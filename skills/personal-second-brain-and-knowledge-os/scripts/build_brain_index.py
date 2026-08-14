#!/usr/bin/env python3
"""Build a privacy-minimized metadata index for a local four-layer vault."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

LAYERS = {"1_Nguon", "2_Wiki", "3_Toi", "4_Ket-Qua"}
EXCLUDED_DIRS = {".git", ".obsidian", ".trash", "node_modules", "__pycache__", ".venv", "venv"}
SENSITIVE_NAMES = {".env", "id_rsa", "id_ed25519", "credentials.json", "secrets.json"}
TEXT_EXTENSIONS = {".md", ".markdown", ".txt", ".rst", ".adoc", ".yaml", ".yml", ".json"}
ID_KEYS = ("id", "source_id", "note_id", "context_id", "output_id")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_metadata(path: Path) -> tuple[str, str]:
    if path.suffix.lower() not in TEXT_EXTENSIONS or path.stat().st_size > 2_000_000:
        return "", ""
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")[:32_000]
    except OSError:
        return "", ""
    title_match = re.search(r"(?m)^#\s+(.+?)\s*$", text)
    title = title_match.group(1).strip() if title_match else ""
    stable_id = ""
    if text.startswith("---"):
        end = text.find("\n---", 3)
        frontmatter = text[3:end] if end != -1 else text[:4000]
        for key in ID_KEYS:
            match = re.search(rf"(?m)^\s*{re.escape(key)}\s*:\s*['\"]?([^\n'\"]+)", frontmatter)
            if match:
                stable_id = match.group(1).strip()
                break
    return title, stable_id


def index_vault(root: Path, output_path: Path | None, strict: bool) -> tuple[dict, list[str]]:
    errors: list[str] = []
    entries: list[dict] = []
    excluded_sensitive: list[str] = []
    layer_counts = {layer: 0 for layer in sorted(LAYERS)}
    observed_layers = {path.name for path in root.iterdir() if path.is_dir() and path.name in LAYERS}
    if strict and observed_layers != LAYERS:
        errors.append(f"expected four layer directories; missing={sorted(LAYERS - observed_layers)}")

    resolved_output = output_path.resolve() if output_path else None
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        relative = path.relative_to(root)
        if any(part in EXCLUDED_DIRS for part in relative.parts):
            continue
        if resolved_output and path.resolve() == resolved_output:
            continue
        if path.name.lower() in SENSITIVE_NAMES:
            excluded_sensitive.append(relative.as_posix())
            continue
        layer = relative.parts[0] if relative.parts and relative.parts[0] in LAYERS else "unclassified"
        if layer in layer_counts:
            layer_counts[layer] += 1
        title, stable_id = read_metadata(path)
        stat = path.stat()
        entries.append(
            {
                "path": relative.as_posix(),
                "layer": layer,
                "stable_id": stable_id,
                "title": title,
                "extension": path.suffix.lower(),
                "size_bytes": stat.st_size,
                "modified_at": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
                "sha256": sha256(path),
            }
        )
    duplicate_ids: dict[str, list[str]] = {}
    for entry in entries:
        if entry["stable_id"]:
            duplicate_ids.setdefault(entry["stable_id"], []).append(entry["path"])
    duplicate_ids = {key: paths for key, paths in duplicate_ids.items() if len(paths) > 1}
    if strict and duplicate_ids:
        errors.append(f"duplicate stable IDs: {sorted(duplicate_ids)}")
    payload = {
        "root": str(root),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "privacy": "Metadata, headings and IDs only; no note bodies or data values are emitted.",
        "layer_counts": layer_counts,
        "unclassified_count": sum(1 for entry in entries if entry["layer"] == "unclassified"),
        "sensitive_files_excluded": excluded_sensitive,
        "duplicate_stable_ids": duplicate_ids,
        "entries": entries,
    }
    return payload, errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    if not root.is_dir():
        print(f"ERROR: vault root is not a directory: {root}")
        sys.exit(1)
    payload, errors = index_vault(root, args.output, args.strict)
    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
        print(f"WROTE: {args.output.resolve()}")
    else:
        print(rendered, end="")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
