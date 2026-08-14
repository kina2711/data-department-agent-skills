#!/usr/bin/env python3
"""Validate a four-layer local Second Brain without mutating it."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

LAYERS = ("1_Nguon", "2_Wiki", "3_Toi", "4_Ket-Qua")
REGISTRIES = {
    "source_registry": ("1_Nguon", "source_count"),
    "note_registry": ("2_Wiki", "note_count"),
    "personal_context_registry": ("3_Toi", "rule_count"),
    "output_registry": ("4_Ket-Qua", "output_count"),
}
STATUSES = {"draft", "active", "deprecated", "archived"}
ITEM_STATUSES = {"draft", "verified", "deprecated", "archived"}
SENSITIVE_NAMES = {".env", "id_rsa", "id_ed25519", "credentials.json", "secrets.json"}
SENSITIVE_PATTERNS = {
    "aws-access-key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "private-key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "generic-secret-assignment": re.compile(r"(?i)\b(?:api[_-]?key|client[_-]?secret|password)\s*[:=]\s*['\"]?[^\s'\"]{12,}"),
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_inside(root: Path, relative: str, label: str, errors: list[str]) -> Path | None:
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        errors.append(f"{label}: path escapes vault root: {relative}")
        return None
    return candidate


def validate_registry(
    name: str,
    records: Any,
    root: Path | None,
    source_ids: set[str],
    errors: list[str],
) -> set[str]:
    if not isinstance(records, list):
        errors.append(f"{name} must be an array")
        return set()
    ids: set[str] = set()
    for index, record in enumerate(records):
        label = f"{name}[{index}]"
        if not isinstance(record, dict):
            errors.append(f"{label} must be an object")
            continue
        item_id = str(record.get("id", "")).strip()
        if not item_id:
            errors.append(f"{label}.id is required")
        elif item_id in ids:
            errors.append(f"{name}: duplicate id {item_id}")
        else:
            ids.add(item_id)
        relative = str(record.get("path", "")).strip()
        expected_hash = str(record.get("sha256", "")).lower()
        if not relative:
            errors.append(f"{label}.path is required")
        if not re.fullmatch(r"[a-f0-9]{64}", expected_hash):
            errors.append(f"{label}.sha256 must be 64 lowercase hex characters")
        if record.get("status") not in ITEM_STATUSES:
            errors.append(f"{label}.status is invalid")
        refs = record.get("source_ids", [])
        if not isinstance(refs, list):
            errors.append(f"{label}.source_ids must be an array")
        elif name != "source_registry":
            unknown = sorted(set(map(str, refs)) - source_ids)
            if unknown:
                errors.append(f"{label}: unknown source_ids {unknown}")
        if root is not None and relative:
            path = resolve_inside(root, relative, label, errors)
            if path is not None:
                if not path.is_file():
                    errors.append(f"{label}: missing file {relative}")
                elif re.fullmatch(r"[a-f0-9]{64}", expected_hash) and sha256(path) != expected_hash:
                    errors.append(f"{label}: SHA-256 mismatch for {relative}")
    return ids


def scan_sensitive(root: Path, errors: list[str]) -> None:
    scanned = 0
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        scanned += 1
        if scanned > 50_000:
            errors.append("sensitive scan stopped after 50,000 files")
            return
        if path.name.lower() in SENSITIVE_NAMES:
            errors.append(f"sensitive filename present: {path.relative_to(root)}")
        if path.stat().st_size > 2_000_000 or path.suffix.lower() not in {".md", ".txt", ".json", ".yaml", ".yml"}:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for rule, pattern in SENSITIVE_PATTERNS.items():
            if pattern.search(text):
                errors.append(f"potential {rule} in {path.relative_to(root)}")


def validate(args: argparse.Namespace) -> list[str]:
    errors: list[str] = []
    try:
        manifest = load_json(args.manifest)
    except (OSError, json.JSONDecodeError, TypeError) as exc:
        return [f"invalid manifest JSON: {exc}"]
    if not isinstance(manifest, dict):
        return ["manifest must be an object"]

    for field in ("brain_id", "owner", "version", "purpose", "updated_at"):
        if not str(manifest.get(field, "")).strip():
            errors.append(f"{field} is required")
    if manifest.get("privacy_classification") not in {"private", "confidential", "restricted", "public"}:
        errors.append("invalid privacy_classification")
    if manifest.get("status") not in STATUSES:
        errors.append("invalid status")

    root = args.root.resolve() if args.root else None
    layers = manifest.get("layers")
    if not isinstance(layers, dict) or set(layers) != set(LAYERS):
        errors.append("layers must contain exactly 1_Nguon, 2_Wiki, 3_Toi and 4_Ket-Qua")
        layers = {}
    for layer in LAYERS:
        config = layers.get(layer, {})
        if not isinstance(config, dict) or not str(config.get("path", "")).strip():
            errors.append(f"{layer}.path is required")
            continue
        if root is not None:
            layer_path = resolve_inside(root, str(config["path"]), layer, errors)
            if layer_path is not None and not layer_path.is_dir():
                errors.append(f"{layer}: missing layer directory {config['path']}")

    source_records = manifest.get("source_registry", [])
    source_ids = validate_registry("source_registry", source_records, root, set(), errors)
    observed_counts: dict[str, int] = {"source_registry": len(source_ids)}
    for registry in ("note_registry", "personal_context_registry", "output_registry"):
        ids = validate_registry(registry, manifest.get(registry), root, source_ids, errors)
        observed_counts[registry] = len(ids)

    for registry, (layer, count_field) in REGISTRIES.items():
        declared = layers.get(layer, {}).get(count_field) if isinstance(layers.get(layer), dict) else None
        if not isinstance(declared, int) or declared < 0:
            errors.append(f"{layer}.{count_field} must be a non-negative integer")
        elif declared != observed_counts.get(registry, 0):
            errors.append(f"{layer}.{count_field}={declared} does not match {registry} count {observed_counts.get(registry, 0)}")

    tests = manifest.get("retrieval_test_set")
    if not isinstance(tests, list):
        errors.append("retrieval_test_set must be an array")
        tests = []
    test_ids: set[str] = set()
    for index, test in enumerate(tests):
        if not isinstance(test, dict):
            errors.append(f"retrieval_test_set[{index}] must be an object")
            continue
        query_id = str(test.get("query_id", "")).strip()
        if not query_id or query_id in test_ids:
            errors.append(f"retrieval_test_set[{index}]: query_id missing or duplicate")
        test_ids.add(query_id)
        if not str(test.get("query", "")).strip():
            errors.append(f"retrieval_test_set[{index}].query is required")
        if test.get("status", "not-run") not in {"not-run", "passed", "failed"}:
            errors.append(f"retrieval_test_set[{index}].status is invalid")

    backup = manifest.get("backup")
    if not isinstance(backup, dict):
        errors.append("backup must be an object")
        backup = {}
    backup_hash = str(backup.get("artifact_sha256", ""))
    if backup_hash and not re.fullmatch(r"[a-fA-F0-9]{64}", backup_hash):
        errors.append("backup.artifact_sha256 is invalid")

    if args.mode == "complete":
        if manifest.get("status") != "active":
            errors.append("complete mode requires status active")
        if not source_ids:
            errors.append("complete mode requires at least one verified source")
        if not tests or any(t.get("status") != "passed" for t in tests if isinstance(t, dict)):
            errors.append("complete mode requires all retrieval tests passed")
        if not backup_hash or not backup.get("last_verified_at") or not backup.get("restore_tested_at"):
            errors.append("complete mode requires a hash-bound backup and restore test")
    if args.scan_sensitive and root is not None:
        scan_sensitive(root, errors)
    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--root", type=Path, help="Vault root used to verify paths and hashes")
    parser.add_argument("--mode", choices=("plan", "complete"), default="plan")
    parser.add_argument("--scan-sensitive", action="store_true")
    args = parser.parse_args()
    errors = validate(args)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"FAILED: {len(errors)} second-brain validation error(s)")
        sys.exit(1)
    print("PASS: four-layer structure, registries, lineage, retrieval and lifecycle controls are valid")


if __name__ == "__main__":
    main()
