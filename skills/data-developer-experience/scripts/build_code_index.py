#!/usr/bin/env python3
"""Index code symbols and call relationships so an agent can answer questions without reading whole files.

The expensive habit is exploratory reading: grep, open a file, open its imports, open theirs.
Each hop spends context on lines that turn out to be irrelevant. This builds a local symbol and
call index once, then answers "where is X defined, who calls it, what does it touch" from the
index and returns only the cited spans.

Python is parsed with `ast`, so its symbols and call edges are exact. JavaScript, TypeScript
and SQL are matched with regexes, so their edges are approximate: dynamic dispatch, aliases and
re-exports are missed, and a name shared by two modules can attribute a call to the wrong one.
Where exactness matters, prefer a real code-graph tool such as CodeGraph (MCP `codegraph_explore`,
or `codegraph query` / `codegraph callers` / `codegraph impact`) and cite that instead.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

PYTHON_SUFFIXES = {".py"}
REGEX_SUFFIXES = {".js", ".jsx", ".ts", ".tsx"}
SQL_SUFFIXES = {".sql"}
SKIP_DIRECTORIES = {
    ".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build",
    ".mypy_cache", ".pytest_cache", ".ruff_cache", "target", "site-packages",
}
JS_DEFINITION = re.compile(
    r"^\s*(?:export\s+)?(?:async\s+)?(?:function\s+(\w+)|class\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\()",
    re.M,
)
JS_CALL = re.compile(r"\b([A-Za-z_$][\w$]*)\s*\(")
SQL_REF = re.compile(r"""\{\{\s*ref\(\s*['"]([^'"]+)['"]\s*\)\s*\}\}""")
NOISE_CALLS = {
    "if", "for", "while", "switch", "catch", "return", "function", "typeof", "await",
    "print", "len", "str", "int", "list", "dict", "set", "super", "range", "require",
}


def discover(root: Path) -> list[Path]:
    suffixes = PYTHON_SUFFIXES | REGEX_SUFFIXES | SQL_SUFFIXES
    return [
        path
        for path in sorted(root.rglob("*"))
        if path.is_file()
        and path.suffix in suffixes
        and not any(part in SKIP_DIRECTORIES for part in path.parts)
    ]


def index_python(path: Path, relative: str, symbols: dict, calls: dict, errors: list[str]) -> None:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except (OSError, SyntaxError) as exc:
        errors.append(f"{relative}: not parsed ({exc.__class__.__name__})")
        return

    scope: list[str] = []

    def qualified(name: str) -> str:
        return ".".join(scope + [name]) if scope else name

    def record_definition(node: ast.AST, name: str, kind: str) -> None:
        signature = ""
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            arguments = [argument.arg for argument in node.args.args]
            signature = f"({', '.join(arguments)})"
        symbols[qualified(name)].append({
            "file": relative,
            "line": getattr(node, "lineno", 0),
            "end_line": getattr(node, "end_lineno", getattr(node, "lineno", 0)),
            "kind": kind,
            "signature": signature,
            "exact": True,
        })

    def visit(node: ast.AST) -> None:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            record_definition(node, node.name, "method" if scope else "function")
            owner = qualified(node.name)
            scope.append(node.name)
            for child in ast.iter_child_nodes(node):
                visit(child)
            scope.pop()
            for called in collect_calls(node):
                calls[owner].add(called)
            return
        if isinstance(node, ast.ClassDef):
            record_definition(node, node.name, "class")
            scope.append(node.name)
            for child in ast.iter_child_nodes(node):
                visit(child)
            scope.pop()
            return
        for child in ast.iter_child_nodes(node):
            visit(child)

    def collect_calls(node: ast.AST) -> set[str]:
        found: set[str] = set()
        for descendant in ast.walk(node):
            if not isinstance(descendant, ast.Call):
                continue
            target = descendant.func
            if isinstance(target, ast.Name):
                found.add(target.id)
            elif isinstance(target, ast.Attribute):
                found.add(target.attr)
        return {name for name in found if name not in NOISE_CALLS}

    visit(tree)


def index_regex(path: Path, relative: str, symbols: dict, calls: dict) -> None:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return
    lines = text.splitlines()
    definitions: list[tuple[int, str]] = []
    for match in JS_DEFINITION.finditer(text):
        name = next((group for group in match.groups() if group), None)
        if not name:
            continue
        line = text[: match.start()].count("\n") + 1
        definitions.append((line, name))
        symbols[name].append({
            "file": relative,
            "line": line,
            "end_line": line,
            "kind": "function",
            "signature": "",
            "exact": False,
        })
    definitions.sort()
    for index, (line, name) in enumerate(definitions):
        end = definitions[index + 1][0] - 1 if index + 1 < len(definitions) else len(lines)
        body = "\n".join(lines[line:end])
        for called in JS_CALL.findall(body):
            if called not in NOISE_CALLS and called != name:
                calls[name].add(called)


def index_sql(path: Path, relative: str, symbols: dict, calls: dict) -> None:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return
    model = path.stem
    symbols[model].append({
        "file": relative,
        "line": 1,
        "end_line": len(text.splitlines()),
        "kind": "model",
        "signature": "",
        "exact": False,
    })
    for referenced in SQL_REF.findall(text):
        calls[model].add(referenced)


def build(root: Path) -> dict[str, Any]:
    symbols: dict[str, list[dict[str, Any]]] = defaultdict(list)
    calls: dict[str, set[str]] = defaultdict(set)
    errors: list[str] = []
    files = discover(root)
    total_bytes = 0
    for path in files:
        relative = path.relative_to(root).as_posix()
        try:
            total_bytes += path.stat().st_size
        except OSError:
            pass
        if path.suffix in PYTHON_SUFFIXES:
            index_python(path, relative, symbols, calls, errors)
        elif path.suffix in REGEX_SUFFIXES:
            index_regex(path, relative, symbols, calls)
        else:
            index_sql(path, relative, symbols, calls)

    callers: dict[str, set[str]] = defaultdict(set)
    for caller, callees in calls.items():
        for callee in callees:
            if callee in symbols:
                callers[callee].add(caller)

    return {
        "root": root.as_posix(),
        "files_indexed": len(files),
        "indexed_bytes": total_bytes,
        "symbols": {name: entries for name, entries in sorted(symbols.items())},
        "calls": {name: sorted(targets) for name, targets in sorted(calls.items())},
        "callers": {name: sorted(sources) for name, sources in sorted(callers.items())},
        "not_parsed": errors,
        "method": "ast for Python (exact); regex for JS/TS/SQL (approximate)",
    }


def read_span(root: Path, entry: dict[str, Any], context: int) -> str:
    path = root / entry["file"]
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return ""
    start = max(0, int(entry["line"]) - 1)
    end = min(len(lines), int(entry.get("end_line", entry["line"])) + context)
    return "\n".join(lines[start:end])


def blast_radius(index: dict[str, Any], symbol: str, depth: int) -> list[str]:
    """Symbols that would be affected if this one changed, following callers upward."""
    callers = index.get("callers", {})
    seen: set[str] = set()
    frontier = {symbol}
    for _ in range(depth):
        nxt: set[str] = set()
        for name in frontier:
            for caller in callers.get(name, []):
                if caller not in seen and caller != symbol:
                    seen.add(caller)
                    nxt.add(caller)
        frontier = nxt
        if not frontier:
            break
    return sorted(seen)


def explain(index: dict[str, Any], root: Path, symbol: str, context: int, depth: int) -> int:
    entries = index.get("symbols", {}).get(symbol)
    if not entries:
        nearby = sorted(
            name for name in index.get("symbols", {}) if symbol.lower() in name.lower()
        )[:8]
        print(f"NOT FOUND: {symbol!r} is not in the index")
        if nearby:
            print(f"closest indexed names: {', '.join(nearby)}")
        print("Report this as unknown rather than guessing where the symbol lives.")
        return 2

    returned_bytes = 0
    for entry in entries:
        location = f"{entry['file']}:{entry['line']}-{entry.get('end_line', entry['line'])}"
        marker = "" if entry.get("exact") else "  (approximate: regex match, not a parse)"
        print(f"DEFINED  {location}  {entry['kind']}{entry['signature']}{marker}")
        span = read_span(root, entry, context)
        if span:
            returned_bytes += len(span.encode("utf-8"))
            print(span)
            print()

    callees = index.get("calls", {}).get(symbol, [])
    known_callees = [name for name in callees if name in index.get("symbols", {})]
    callers = index.get("callers", {}).get(symbol, [])
    print(f"CALLS    {', '.join(known_callees) if known_callees else '(none indexed)'}")
    print(f"CALLERS  {', '.join(callers) if callers else '(none indexed)'}")
    radius = blast_radius(index, symbol, depth)
    print(f"BLAST RADIUS (depth {depth}): {len(radius)} symbol(s)")
    if radius:
        print(f"  {', '.join(radius[:20])}")

    files_touched = {entry["file"] for entry in entries}
    for name in callers:
        for entry in index.get("symbols", {}).get(name, []):
            files_touched.add(entry["file"])
    naive_bytes = 0
    for relative in files_touched:
        try:
            naive_bytes += (root / relative).stat().st_size
        except OSError:
            pass
    if naive_bytes:
        saved = 100 * (1 - returned_bytes / naive_bytes)
        print(
            f"CONTEXT  returned {returned_bytes} bytes instead of {naive_bytes} bytes "
            f"across {len(files_touched)} file(s): {saved:.1f}% less than reading them whole"
        )
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="repository root to index or query")
    parser.add_argument("--index-out", type=Path, help="write the index as JSON")
    parser.add_argument("--index-in", type=Path, help="reuse an existing index instead of rebuilding")
    parser.add_argument("--symbol", help="explain one symbol: definition, callers, callees, blast radius")
    parser.add_argument("--context", type=int, default=0, help="extra lines to show after a definition")
    parser.add_argument("--depth", type=int, default=2, help="how far to follow callers for blast radius")
    args = parser.parse_args()

    if args.index_in is not None:
        try:
            index = json.loads(args.index_in.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"ERROR: unreadable index: {exc}")
            sys.exit(1)
    else:
        if not args.root.is_dir():
            print(f"ERROR: not a directory: {args.root}")
            sys.exit(1)
        index = build(args.root)

    if args.index_out is not None:
        args.index_out.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"index written: {args.index_out}")

    print(f"files_indexed: {index.get('files_indexed', 0)}")
    print(f"symbols: {len(index.get('symbols', {}))}")
    print(f"call_edges: {sum(len(value) for value in index.get('calls', {}).values())}")
    if index.get("not_parsed"):
        print(f"not_parsed: {len(index['not_parsed'])} file(s); their symbols are absent from the index")

    if not args.symbol:
        if not index.get("symbols"):
            print("EMPTY: no symbols indexed; nothing can be answered from this index")
            sys.exit(1)
        print("PASS: index built; pass --symbol to answer a question without reading whole files")
        return

    sys.exit(explain(index, args.root, args.symbol, args.context, args.depth))


if __name__ == "__main__":
    main()
