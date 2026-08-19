#!/usr/bin/env python3
"""Validate version-bound approval records, their expiry window and their artifact binding."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

RISKS = {"R1-reviewed", "R2-standard", "R3-controlled", "R4-critical"}
DECISIONS = {"approved", "rejected", "expired", "revoked"}
REQUIRED = (
    "approval_id", "task_id", "scope", "artifact_version", "artifact_sha256",
    "risk_tier", "approver", "authority", "decision", "decided_at", "expires_at",
)
ALLOWED = set(REQUIRED) | {"conditions"}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_timestamp(value: str) -> datetime | None:
    text = str(value).strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None else parsed.replace(tzinfo=timezone.utc)


def validate_record(record: Any, source: str, as_of: datetime, catalog: set[str] | None, root: Path | None, require_approved: bool) -> list[str]:
    errors: list[str] = []
    if not isinstance(record, dict):
        return [f"{source}: approval record must be an object"]
    for field in REQUIRED:
        if field not in record:
            errors.append(f"{source}: missing {field}")
    unknown = sorted(set(record) - ALLOWED)
    if unknown:
        errors.append(f"{source}: unsupported fields {unknown}")

    scope = record.get("scope")
    if not isinstance(scope, list) or not scope or any(not str(item).strip() for item in scope):
        errors.append(f"{source}: scope must be a non-empty array of named boundaries")
    conditions = record.get("conditions", [])
    if not isinstance(conditions, list) or any(not isinstance(item, str) for item in conditions):
        errors.append(f"{source}: conditions must be an array of strings")

    digest = str(record.get("artifact_sha256", ""))
    if len(digest) != 64 or any(char not in "0123456789abcdefABCDEF" for char in digest):
        errors.append(f"{source}: artifact_sha256 must be 64 hexadecimal characters")
    if not str(record.get("artifact_version", "")).strip():
        errors.append(f"{source}: artifact_version must bind the approval to one version")
    for field in ("approval_id", "approver", "authority"):
        if not str(record.get(field, "")).strip():
            errors.append(f"{source}: {field} must not be empty")

    risk = record.get("risk_tier")
    if risk not in RISKS:
        errors.append(f"{source}: invalid risk_tier {risk!r}")
    decision = record.get("decision")
    if decision not in DECISIONS:
        errors.append(f"{source}: invalid decision {decision!r}")

    task_id = str(record.get("task_id", ""))
    if catalog is not None and task_id and task_id not in catalog:
        errors.append(f"{source}: task_id is not a canonical catalog ID: {task_id}")

    decided_at = parse_timestamp(record.get("decided_at", ""))
    expires_at = parse_timestamp(record.get("expires_at", ""))
    if decided_at is None:
        errors.append(f"{source}: decided_at must be an ISO 8601 timestamp")
    if expires_at is None:
        errors.append(f"{source}: expires_at must be an ISO 8601 timestamp")
    if decided_at is not None and expires_at is not None and expires_at <= decided_at:
        errors.append(f"{source}: expires_at must be later than decided_at")
    if decided_at is not None and decided_at > as_of:
        errors.append(f"{source}: decided_at is in the future relative to {as_of.isoformat()}")

    expired = expires_at is not None and expires_at <= as_of
    if expired and decision == "approved":
        errors.append(f"{source}: approval expired at {record.get('expires_at')}; it cannot authorize action at {as_of.isoformat()}")
    if require_approved and decision != "approved":
        errors.append(f"{source}: authority check requires decision 'approved', found {decision!r}")
    if require_approved and conditions and not str(record.get("authority", "")).strip():
        errors.append(f"{source}: conditional approval requires a named authority")

    if root is not None:
        matches = [path for path in root.rglob("*") if path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest().lower() == digest.lower()]
        if digest and not matches:
            errors.append(f"{source}: no artifact under {root} matches artifact_sha256")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", type=Path, help="JSON approval record object or array")
    parser.add_argument("--task-catalog", type=Path, help="task-catalog.json used to check canonical task IDs")
    parser.add_argument("--artifact-root", type=Path, help="root searched for an artifact matching artifact_sha256")
    parser.add_argument("--as-of", help="ISO 8601 evaluation time (default: now, UTC)")
    parser.add_argument("--require-approved", action="store_true", help="fail unless the record currently authorizes action")
    args = parser.parse_args()

    as_of = parse_timestamp(args.as_of) if args.as_of else datetime.now(timezone.utc)
    if as_of is None:
        print("ERROR: --as-of must be an ISO 8601 timestamp")
        sys.exit(1)

    try:
        data = load(args.record)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: invalid JSON: {exc}")
        sys.exit(1)

    catalog: set[str] | None = None
    if args.task_catalog is not None:
        try:
            entries = load(args.task_catalog)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"ERROR: invalid task catalog: {exc}")
            sys.exit(1)
        if not isinstance(entries, list):
            print("ERROR: task catalog must be an array")
            sys.exit(1)
        catalog = {str(entry.get("id")) for entry in entries if isinstance(entry, dict)}

    records = data if isinstance(data, list) else [data]
    errors: list[str] = []
    seen: set[str] = set()
    for index, record in enumerate(records):
        errors.extend(validate_record(record, f"{args.record}#{index}", as_of, catalog, args.artifact_root, args.require_approved))
        if isinstance(record, dict):
            approval_id = str(record.get("approval_id", ""))
            if approval_id and approval_id in seen:
                errors.append(f"duplicate approval_id: {approval_id}")
            seen.add(approval_id)

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"FAILED: {len(errors)} approval validation error(s)")
        sys.exit(1)
    print(f"PASS: {len(records)} approval record(s) valid at {as_of.isoformat()}")


if __name__ == "__main__":
    main()
