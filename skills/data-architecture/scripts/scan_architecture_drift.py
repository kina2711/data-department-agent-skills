#!/usr/bin/env python3
"""Measure structural drift in a codebase as deterministic first-pass evidence.

Agents generate code faster than architecture review can absorb it, so decay shows up as
structure long before it shows up as failing tests: cycles appear, module depth grows, one
module absorbs everything, and near-identical blocks multiply.

This is a regex-based approximation over a fixed set of languages, not a parser. It cannot
resolve dynamic imports, aliases, re-exports or conditional imports, and it does not
understand semantics. Treat its output as a signal that directs review, never as proof that
architecture is sound. Where a real parse is required, use a tree-sitter-based tool such as
Sentrux (`sentrux check`, `sentrux gate`, or its MCP server) and record that as the evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

LANGUAGE_PATTERNS = {
    ".py": [
        re.compile(r"^\s*from\s+([.\w]+)\s+import\b", re.M),
        re.compile(r"^\s*import\s+([.\w]+)", re.M),
    ],
    ".js": [re.compile(r"""(?:from|require\()\s*['"]([^'"]+)['"]""")],
    ".jsx": [re.compile(r"""(?:from|require\()\s*['"]([^'"]+)['"]""")],
    ".ts": [re.compile(r"""(?:from|require\()\s*['"]([^'"]+)['"]""")],
    ".tsx": [re.compile(r"""(?:from|require\()\s*['"]([^'"]+)['"]""")],
    ".sql": [re.compile(r"""\{\{\s*ref\(\s*['"]([^'"]+)['"]\s*\)\s*\}\}""")],
}
SKIP_DIRECTORIES = {
    ".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build",
    ".mypy_cache", ".pytest_cache", ".ruff_cache", "target", "site-packages",
}
REDUNDANCY_WINDOW = 6
MIN_BLOCK_CHARS = 80


def discover(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix not in LANGUAGE_PATTERNS:
            continue
        if any(part in SKIP_DIRECTORIES for part in path.parts):
            continue
        files.append(path)
    return files


def module_name(path: Path, root: Path) -> str:
    return path.relative_to(root).with_suffix("").as_posix()


def resolve(target: str, source: Path, root: Path, modules: set[str]) -> str | None:
    """Map an import string onto a module in this repository, or None if it is external."""
    candidate = target.replace("\\", "/")
    if candidate.startswith("."):
        depth = len(candidate) - len(candidate.lstrip("."))
        base = source.parent
        for _ in range(depth - 1):
            base = base.parent
        tail = candidate[depth:].replace(".", "/")
        try:
            joined = (base / tail).resolve().relative_to(root.resolve()).as_posix()
        except (ValueError, OSError):
            return None
        return joined if joined in modules else None
    dotted = candidate.replace(".", "/")
    for form in (candidate, dotted, f"{candidate}/index", f"{dotted}/index"):
        cleaned = form.strip("/")
        if cleaned in modules:
            return cleaned
    suffix_matches = [name for name in modules if name.endswith(f"/{candidate.strip('/')}")]
    return suffix_matches[0] if len(suffix_matches) == 1 else None


def build_graph(files: list[Path], root: Path) -> dict[str, set[str]]:
    modules = {module_name(path, root) for path in files}
    graph: dict[str, set[str]] = {name: set() for name in modules}
    for path in files:
        name = module_name(path, root)
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for pattern in LANGUAGE_PATTERNS[path.suffix]:
            for match in pattern.findall(text):
                resolved = resolve(str(match), path, root, modules)
                if resolved is not None and resolved != name:
                    graph[name].add(resolved)
    return graph


def find_cycles(graph: dict[str, set[str]]) -> list[list[str]]:
    """Tarjan strongly connected components; any component above size one is a cycle."""
    index_counter = [0]
    stack: list[str] = []
    on_stack: set[str] = set()
    indices: dict[str, int] = {}
    lowlink: dict[str, int] = {}
    cycles: list[list[str]] = []

    def strongconnect(node: str) -> None:
        indices[node] = lowlink[node] = index_counter[0]
        index_counter[0] += 1
        stack.append(node)
        on_stack.add(node)
        for neighbour in sorted(graph.get(node, ())):
            if neighbour not in indices:
                strongconnect(neighbour)
                lowlink[node] = min(lowlink[node], lowlink[neighbour])
            elif neighbour in on_stack:
                lowlink[node] = min(lowlink[node], indices[neighbour])
        if lowlink[node] == indices[node]:
            component: list[str] = []
            while True:
                member = stack.pop()
                on_stack.discard(member)
                component.append(member)
                if member == node:
                    break
            if len(component) > 1 or node in graph.get(node, set()):
                cycles.append(sorted(component))

    previous_limit = sys.getrecursionlimit()
    sys.setrecursionlimit(max(previous_limit, len(graph) * 4 + 1000))
    try:
        for node in sorted(graph):
            if node not in indices:
                strongconnect(node)
    finally:
        sys.setrecursionlimit(previous_limit)
    return sorted(cycles, key=len, reverse=True)


def longest_chain(graph: dict[str, set[str]], cyclic: set[str]) -> int:
    """Longest dependency chain over the acyclic part; cycles are excluded, not traversed."""
    memo: dict[str, int] = {}

    def depth(node: str, seen: frozenset[str]) -> int:
        if node in cyclic or node in seen:
            return 0
        if node in memo:
            return memo[node]
        best = 0
        for neighbour in graph.get(node, ()):
            best = max(best, 1 + depth(neighbour, seen | {node}))
        memo[node] = best
        return best

    return max((depth(node, frozenset()) for node in graph), default=0)


def redundancy(files: list[Path]) -> tuple[float, list[dict[str, object]]]:
    """Count normalized line windows that appear in more than one place."""
    seen: dict[str, list[str]] = defaultdict(list)
    windows = 0
    for path in files:
        try:
            raw = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        lines = [line.strip() for line in raw if line.strip() and not line.strip().startswith(("#", "//", "--"))]
        for start in range(0, max(0, len(lines) - REDUNDANCY_WINDOW + 1)):
            block = "\n".join(lines[start:start + REDUNDANCY_WINDOW])
            if len(block) < MIN_BLOCK_CHARS:
                continue
            windows += 1
            digest = hashlib.sha256(block.encode("utf-8")).hexdigest()
            seen[digest].append(f"{path.as_posix()}:{start + 1}")
    duplicated = {digest: places for digest, places in seen.items() if len(places) > 1}
    duplicate_windows = sum(len(places) - 1 for places in duplicated.values())
    ratio = duplicate_windows / windows if windows else 0.0
    hotspots = [
        {"occurrences": len(places), "locations": sorted(places)[:6]}
        for _, places in sorted(duplicated.items(), key=lambda item: len(item[1]), reverse=True)[:5]
    ]
    return ratio, hotspots


def gini(values: list[int]) -> float:
    """Inequality of module size. 0.0 is perfectly even, 1.0 is one module holding everything."""
    numbers = sorted(value for value in values if value >= 0)
    total = sum(numbers)
    if not numbers or total == 0:
        return 0.0
    cumulative = sum((index + 1) * value for index, value in enumerate(numbers))
    count = len(numbers)
    return max(0.0, min(1.0, (2 * cumulative) / (count * total) - (count + 1) / count))


def score_component(value: float) -> int:
    return int(round(max(0.0, min(1.0, value)) * 2000))


def analyze(root: Path, max_depth: int) -> dict[str, object]:
    files = discover(root)
    if not files:
        return {"error": f"no analyzable source files under {root}"}
    graph = build_graph(files, root)
    cycles = find_cycles(graph)
    cyclic = {member for cycle in cycles for member in cycle}
    chain = longest_chain(graph, cyclic)
    duplication, hotspots = redundancy(files)

    sizes = []
    for path in files:
        try:
            sizes.append(len(path.read_text(encoding="utf-8", errors="replace").splitlines()))
        except OSError:
            sizes.append(0)
    inequality = gini(sizes)

    fan_out = {name: len(targets) for name, targets in graph.items()}
    fan_in: dict[str, int] = defaultdict(int)
    for targets in graph.values():
        for target in targets:
            fan_in[target] += 1
    internal_edges = sum(fan_out.values())
    coupling = internal_edges / len(graph) if graph else 0.0

    metrics = {
        "modularity": max(0.0, 1.0 - min(1.0, coupling / 8.0)),
        "acyclicity": 1.0 if not cycles else max(0.0, 1.0 - len(cyclic) / len(graph)),
        "depth": 1.0 if chain <= max_depth else max(0.0, 1.0 - (chain - max_depth) / max(1, max_depth)),
        "equality": max(0.0, 1.0 - inequality),
        "redundancy": max(0.0, 1.0 - min(1.0, duplication * 5.0)),
    }
    components = {name: score_component(value) for name, value in metrics.items()}
    hubs = sorted(fan_in.items(), key=lambda item: item[1], reverse=True)[:5]

    return {
        "root": root.as_posix(),
        "files_analyzed": len(files),
        "modules": len(graph),
        "internal_edges": internal_edges,
        "score": sum(components.values()),
        "score_max": 10000,
        "components": components,
        "observations": {
            "cycles": len(cycles),
            "modules_in_cycles": len(cyclic),
            "largest_cycle": cycles[0][:8] if cycles else [],
            "longest_dependency_chain": chain,
            "max_depth_budget": max_depth,
            "mean_fan_out": round(coupling, 2),
            "size_inequality_gini": round(inequality, 3),
            "duplicate_block_ratio": round(duplication, 4),
            "top_dependency_hubs": [{"module": name, "fan_in": count} for name, count in hubs],
            "duplication_hotspots": hotspots,
        },
        "method": "regex import extraction; not a parse. Confirm findings against a tree-sitter tool before acting on them.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="repository or package root to scan")
    parser.add_argument("--max-depth", type=int, default=5, help="permitted dependency chain length")
    parser.add_argument("--gate", type=int, help="fail when the score falls below this threshold (0-10000)")
    parser.add_argument("--baseline", type=Path, help="previous report; fail when the score regresses")
    parser.add_argument("--report-out", type=Path, help="write the report as JSON")
    args = parser.parse_args()

    if not args.root.is_dir():
        print(f"ERROR: not a directory: {args.root}")
        sys.exit(1)

    report = analyze(args.root, args.max_depth)
    if "error" in report:
        print(f"ERROR: {report['error']}")
        sys.exit(1)

    print(f"modules: {report['modules']} across {report['files_analyzed']} files")
    for name, value in report["components"].items():
        print(f"  {name:<12} {value:>5} / 2000")
    print(f"SCORE: {report['score']} / {report['score_max']}")
    observations = report["observations"]
    if observations["cycles"]:
        print(f"CYCLES: {observations['cycles']} (largest: {' -> '.join(observations['largest_cycle'])})")
    if observations["longest_dependency_chain"] > args.max_depth:
        print(f"DEPTH: chain of {observations['longest_dependency_chain']} exceeds budget {args.max_depth}")
    if observations["duplicate_block_ratio"] > 0:
        print(f"REDUNDANCY: {observations['duplicate_block_ratio']:.2%} of {REDUNDANCY_WINDOW}-line windows are duplicated")

    if args.report_out is not None:
        args.report_out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"report written: {args.report_out}")

    failed = False
    if args.baseline is not None:
        try:
            previous = json.loads(args.baseline.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"ERROR: unreadable baseline: {exc}")
            sys.exit(1)
        delta = int(report["score"]) - int(previous.get("score", 0))
        print(f"BASELINE: {previous.get('score')} -> {report['score']} ({delta:+d})")
        if delta < 0:
            print("REGRESSION: structural score fell against the recorded baseline")
            failed = True
    if args.gate is not None and int(report["score"]) < args.gate:
        print(f"GATE FAILED: {report['score']} is below the required {args.gate}")
        failed = True

    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
