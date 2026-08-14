#!/usr/bin/env python3
"""Build a privacy-minimized context-source index from a local project tree."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

EXCLUDED = {".git", ".venv", "venv", "node_modules", "dist", "build", "__pycache__"}
CONTEXT_EXTENSIONS = {".md", ".yml", ".yaml", ".json", ".toml", ".sql", ".dbml", ".bpmn", ".puml"}
SENSITIVE = re.compile(r"(?i)(secret|credential|password|token|private[_-]?key|\.env($|\.)|customer|candidate|employee|payroll)")


def classify(path: str) -> str:
    lower = path.lower()
    if any(word in lower for word in ("glossary", "metric", "kpi", "semantic")):
        return "business-semantics"
    if any(word in lower for word in ("schema", "model", "contract", "lineage", "catalog")):
        return "data-metadata"
    if any(word in lower for word in ("policy", "governance", "privacy", "security", "retention")):
        return "policy-control"
    if any(word in lower for word in ("architecture", "adr", "diagram", "system")):
        return "architecture-system"
    if any(word in lower for word in ("runbook", "incident", "slo", "operat")):
        return "operations"
    return "project-documentation"


def authority(path: str) -> str:
    lower = path.lower()
    if any(word in lower for word in ("approved", "canonical", "certified", "policy")):
        return "declared-authoritative-unverified"
    if any(word in lower for word in ("draft", "example", "sample", "template")):
        return "non-authoritative"
    return "unknown-requires-owner"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--max-bytes", type=int, default=5_000_000)
    args = parser.parse_args()
    root = args.root.resolve()
    if not root.is_dir():
        print(f"ERROR: root directory does not exist: {root}")
        sys.exit(1)
    entries = []
    excluded_sensitive = []
    for current, dirs, names in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in EXCLUDED)
        for name in sorted(names):
            path = Path(current) / name
            if path.suffix.lower() not in CONTEXT_EXTENSIONS or not path.is_file():
                continue
            relative = path.relative_to(root).as_posix()
            if SENSITIVE.search(relative):
                excluded_sensitive.append(relative)
                continue
            stat = path.stat()
            if stat.st_size > args.max_bytes:
                continue
            entries.append({
                "context_id": hashlib.sha256(relative.encode("utf-8")).hexdigest()[:16],
                "path": relative,
                "kind": classify(relative),
                "authority": authority(relative),
                "owner": "unresolved",
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "size_bytes": stat.st_size,
                "last_modified_at": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
                "last_verified_at": "",
                "freshness_status": "unverified",
                "retrieval_triggers": [],
                "conflicts_with": [],
            })
    result = {
        "index_version": "3.0",
        "root": str(root),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "entries": entries,
        "excluded_sensitive_paths": excluded_sensitive,
        "limitations": ["Content values were not copied into the index.", "Authority and ownership are hypotheses until confirmed by accountable owners.", "Live systems override stale local documentation."],
    }
    payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
        print(f"WROTE: {args.output} ({len(entries)} entries)")
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
