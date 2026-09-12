#!/usr/bin/env python3
"""Validate evidence envelopes and optionally verify local artifact hashes."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_record(record: Any, source: Path, root: Path | None, complete: bool) -> list[str]:
    errors: list[str] = []
    if not isinstance(record, dict):
        return [f"{source}: evidence must be an object"]
    required = (
        "evidence_id", "task_id", "claim_ids", "artifact", "artifact_version",
        "artifact_sha256", "environment", "method", "observed_result", "status",
        "captured_at", "captured_by", "limitations",
    )
    for field in required:
        if field not in record:
            errors.append(f"{source}: missing {field}")
    if not isinstance(record.get("claim_ids"), list) or not record.get("claim_ids"):
        errors.append(f"{source}: claim_ids must be a non-empty array")
    digest = str(record.get("artifact_sha256", ""))
    if len(digest) != 64 or any(char not in "0123456789abcdefABCDEF" for char in digest):
        errors.append(f"{source}: artifact_sha256 must be 64 hexadecimal characters")
    if not isinstance(record.get("environment"), dict) or not record.get("environment"):
        errors.append(f"{source}: environment must identify the execution/inspection context")
    if record.get("status") not in {"passed", "failed", "observed", "not-run", "not-applicable"}:
        errors.append(f"{source}: invalid status")
    if complete and record.get("status") not in {"passed", "observed", "not-applicable"}:
        errors.append(f"{source}: complete bundle cannot contain status {record.get('status')!r}")
    if complete and not str(record.get("artifact_version", "")).strip():
        errors.append(f"{source}: complete evidence requires artifact_version")
    artifact = str(record.get("artifact", ""))
    if root is not None and artifact:
        path = (root / artifact).resolve() if not Path(artifact).is_absolute() else Path(artifact).resolve()
        try:
            path.relative_to(root.resolve())
        except ValueError:
            errors.append(f"{source}: artifact escapes permitted root: {path}")
        else:
            if not path.is_file():
                errors.append(f"{source}: artifact does not exist: {path}")
            elif digest and hashlib.sha256(path.read_bytes()).hexdigest().lower() != digest.lower():
                errors.append(f"{source}: artifact hash mismatch: {path}")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle", type=Path, help="JSON evidence object or array")
    parser.add_argument("--artifact-root", type=Path)
    parser.add_argument("--mode", choices=("plan", "complete"), default="plan")
    args = parser.parse_args()
    try:
        data = load(args.bundle)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: invalid JSON: {exc}")
        sys.exit(1)
    records = data if isinstance(data, list) else [data]
    errors: list[str] = []
    seen: set[str] = set()
    for index, record in enumerate(records):
        source = Path(f"{args.bundle}#{index}")
        errors.extend(validate_record(record, source, args.artifact_root, args.mode == "complete"))
        if isinstance(record, dict):
            evidence_id = str(record.get("evidence_id", ""))
            if evidence_id in seen:
                errors.append(f"duplicate evidence_id: {evidence_id}")
            seen.add(evidence_id)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"FAILED: {len(errors)} evidence validation error(s)")
        sys.exit(1)
    print(f"PASS: {len(records)} evidence envelope(s) are structurally and cryptographically valid")


if __name__ == "__main__":
    main()
