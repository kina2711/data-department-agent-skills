#!/usr/bin/env python3
"""Build a bounded, provenance-aware Markdown context package from a JSON manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


LAYERS = ["task", "business", "data", "implementation", "evidence", "constraints", "output"]
SECRET_PATTERNS = {
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "aws_access_key": re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    "generic_secret": re.compile(r"(?i)\b(?:api[_-]?key|secret|password|token)\s*[:=]\s*['\"]?[A-Za-z0-9_./+=-]{12,}"),
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def estimate_tokens(text: str) -> int:
    return max(1, (len(text) + 3) // 4)


def scan_secrets(text: str) -> list[str]:
    return [name for name, pattern in SECRET_PATTERNS.items() if pattern.search(text)]


CONTEXT_LEVELS = ("full", "summary", "excluded")


def summarise(text: str, budget_chars: int = 1200) -> str:
    """A source reduced to its shape rather than dropped.

    Open Notebook makes this a per-source choice — full content, a summary, or out of context —
    and the third option is the one this builder was missing. Previously a source over budget was
    removed outright, so the package lost the fact that it existed. A reader who knows a source
    said something and roughly what beats a reader who cannot tell it was ever there.

    Deliberately extractive: headings and the opening sentences of the body, taken verbatim. A
    generated abstract would be a claim about the source, and this script has no model to stand
    behind one. Everything here can be checked against the file it came from.
    """
    lines = text.splitlines()
    headings = [line.strip() for line in lines if line.lstrip().startswith("#")]
    body = [line.strip() for line in lines if line.strip() and not line.lstrip().startswith("#")]
    parts: list[str] = []
    if headings:
        parts.append("Headings: " + " · ".join(h.lstrip("# ").strip() for h in headings[:12]))
    opening = " ".join(body[:6])
    if opening:
        parts.append(opening)
    out = "\n\n".join(parts).strip()
    if len(out) > budget_chars:
        out = out[: budget_chars - 1].rsplit(" ", 1)[0] + "…"
    return out or "(nguồn rỗng)"


def load_manifest(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data.get("task"), dict) or not data["task"].get("objective"):
        raise ValueError("manifest.task.objective is required")
    if not isinstance(data.get("sources", []), list):
        raise ValueError("manifest.sources must be a list")
    return data


def build(manifest_path: Path, max_tokens: int) -> tuple[str, dict]:
    manifest = load_manifest(manifest_path)
    base = manifest_path.parent.resolve()
    included: list[dict] = []
    omitted: list[dict] = []
    seen_hashes: set[str] = set()

    for index, source in enumerate(manifest.get("sources", [])):
        raw_path = source.get("path", "")
        layer = source.get("layer", "evidence")
        if layer not in LAYERS:
            raise ValueError(f"source {index}: unsupported layer {layer!r}")
        level = source.get("context_level", "full")
        if level not in CONTEXT_LEVELS:
            raise ValueError(f"source {index}: unsupported context_level {level!r}; "
                             f"expected one of {', '.join(CONTEXT_LEVELS)}")
        if level == "excluded":
            omitted.append({"path": raw_path, "reason": "excluded-by-manifest"})
            continue
        path = Path(raw_path)
        if not path.is_absolute():
            path = (base / path).resolve()
        if not path.is_file():
            if source.get("required", False):
                raise FileNotFoundError(f"required source not found: {path}")
            omitted.append({"path": str(path), "reason": "not-found"})
            continue
        raw = path.read_bytes()
        digest = sha256(raw)
        if digest in seen_hashes:
            omitted.append({"path": str(path), "reason": "duplicate-content", "sha256": digest})
            continue
        text = raw.decode("utf-8", errors="replace")
        findings = scan_secrets(text)
        if findings:
            raise ValueError(f"secret-like content in {path}: {', '.join(findings)}")
        seen_hashes.add(digest)
        included.append(
            {
                "path": str(path),
                "name": source.get("name") or path.name,
                "layer": layer,
                "priority": int(source.get("priority", 50)),
                "required": bool(source.get("required", False)),
                "authority": source.get("authority", "unknown"),
                "owner": source.get("owner", "unknown"),
                "last_verified": source.get("last_verified", "unknown"),
                "sensitivity": source.get("sensitivity", "internal"),
                "sha256": digest,
                "context_level": level,
                "full_chars": len(text.strip()),
                "content": summarise(text) if level == "summary" else text.strip(),
            }
        )

    task = manifest["task"]
    header = [
        "# Task Context Package",
        "",
        f"- Package ID: `{manifest.get('package_id', '')}`",
        f"- Objective: {task['objective']}",
        f"- Primary deliverable: {task.get('primary_deliverable', '')}",
        f"- Acceptance criteria: {json.dumps(task.get('acceptance_criteria', []), ensure_ascii=False)}",
        f"- Generated from manifest: `{manifest_path.resolve()}`",
        "",
    ]

    def render(items: list[dict]) -> str:
        parts = list(header)
        for layer in LAYERS:
            selected = sorted((x for x in items if x["layer"] == layer), key=lambda x: (-x["priority"], x["path"]))
            if not selected:
                continue
            parts.extend([f"## {layer.title()}", ""])
            for item in selected:
                parts.extend(
                    [
                        f"### {item['name']}",
                        f"Source: `{item['path']}` · SHA-256 `{item['sha256']}` · authority `{item['authority']}` · owner `{item['owner']}` · verified `{item['last_verified']}` · sensitivity `{item['sensitivity']}`",
                        "",
                        *(
                            [f"> **Tóm tắt, không phải nguyên văn.** Rút từ {item['full_chars']} ký "
                             f"tự. Trích dẫn thì đọc file gốc ở đường dẫn trên.", ""]
                            if item["context_level"] == "summary" else []
                        ),
                        item["content"],
                        "",
                    ]
                )
        return "\n".join(parts).rstrip() + "\n"

    bundle = render(included)

    # Over budget, demote before dropping. Losing a source entirely loses the fact that it exists,
    # and a reader cannot ask about a gap they cannot see. Summarising the lowest-priority full
    # source first keeps every source represented for as long as the budget allows; only when
    # everything is already a summary does anything leave.
    while estimate_tokens(bundle) > max_tokens:
        demotable = sorted(
            (x for x in included if x["context_level"] == "full" and not x["required"]),
            key=lambda x: (x["priority"], -len(x["content"]), x["path"]),
        )
        if demotable:
            victim = demotable[0]
            victim["context_level"] = "summary"
            victim["content"] = summarise(victim["content"])
            victim["demoted"] = "token-budget"
            bundle = render(included)
            continue
        candidates = sorted((x for x in included if not x["required"]), key=lambda x: (x["priority"], -len(x["content"]), x["path"]))
        if not candidates:
            # Required sources are never demoted behind the caller's back. A summary of a source
            # the task declared it needs is a quieter failure than this one, and the quiet kind is
            # the kind nobody notices until the output is wrong.
            raise ValueError(
                f"required context exceeds token budget: ~{estimate_tokens(bundle)} > {max_tokens}. "
                "Raise --max-tokens, or set context_level to summary on a required source to say "
                "deliberately that a summary of it is enough."
            )
        victim = candidates[0]
        included.remove(victim)
        omitted.append({"path": victim["path"], "reason": "token-budget", "sha256": victim["sha256"]})
        bundle = render(included)

    report = {
        "status": "pass",
        "package_id": manifest.get("package_id", ""),
        "estimated_tokens": estimate_tokens(bundle),
        "max_tokens": max_tokens,
        "included": [{k: v for k, v in item.items() if k != "content"} for item in included],
        "omitted": omitted,
        "assumptions": manifest.get("assumptions", []),
        "conflicts": manifest.get("conflicts", []),
    }
    return bundle, report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path, help="JSON manifest containing task and sources")
    parser.add_argument("--output", required=True, type=Path, help="Markdown bundle output")
    parser.add_argument("--report", type=Path, help="Optional JSON provenance report")
    parser.add_argument("--max-tokens", type=int, default=100_000)
    parser.add_argument("--json", action="store_true", help="Print report as JSON")
    args = parser.parse_args()
    if args.max_tokens <= 0:
        parser.error("--max-tokens must be positive")
    try:
        bundle, report = build(args.manifest, args.max_tokens)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(bundle, encoding="utf-8")
        if args.report:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, ensure_ascii=False) if args.json else f"PASS: {len(report['included'])} sources, ~{report['estimated_tokens']} tokens, {len(report['omitted'])} omitted")
        return 0
    except Exception as exc:
        error = {"status": "error", "message": str(exc)}
        print(json.dumps(error, ensure_ascii=False) if args.json else f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
