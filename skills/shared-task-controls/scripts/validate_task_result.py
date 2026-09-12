#!/usr/bin/env python3
"""Validate an atomic task result and its completion consistency without mutating it."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

STATUSES = ["draft", "blocked", "failed", "validated", "approved", "released", "monitored", "complete"]
PROFILES = {
    "advisory-analysis", "design-specification", "build-change", "production-release",
    "incident-recovery", "governance-assurance", "learning", "onboarding", "hiring",
    "career-coaching", "career-development",
}
RISKS = {"R0-light", "R1-reviewed", "R2-standard", "R3-controlled", "R4-critical"}
PATHS = {"fast-path": {"R0-light"}, "standard-path": {"R1-reviewed", "R2-standard"}, "controlled-path": {"R3-controlled", "R4-critical"}}
APPROVALS = {"not-required", "pending", "approved", "rejected", "expired"}
EVIDENCE_STATES = {"validated", "approved", "released", "monitored", "complete"}
APPROVED_STATES = {"approved", "released", "monitored", "complete"}
STRING_ARRAYS = ("evidence", "test_results", "gate_results", "assumptions", "limitations", "residual_risks")
REQUIRED = (
    "task_id", "status", "lifecycle_profile", "risk_tier", "execution_path", "phase_reached",
    "primary_deliverable", "evidence", "test_results", "gate_results", "approval_status",
    "residual_risks", "next_task", "next_owner",
)
ALLOWED = set(REQUIRED) | {"assumptions", "limitations"}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_record(record: Any, source: str, catalog: set[str] | None, complete: bool) -> list[str]:
    errors: list[str] = []
    if not isinstance(record, dict):
        return [f"{source}: task result must be an object"]
    for field in REQUIRED:
        if field not in record:
            errors.append(f"{source}: missing {field}")
    unknown = sorted(set(record) - ALLOWED)
    if unknown:
        errors.append(f"{source}: unsupported fields {unknown}")
    for field in STRING_ARRAYS:
        value = record.get(field)
        if field in record and (not isinstance(value, list) or any(not isinstance(item, str) for item in value)):
            errors.append(f"{source}: {field} must be an array of strings")

    status = record.get("status")
    if status not in STATUSES:
        errors.append(f"{source}: invalid status {status!r}")
    if record.get("lifecycle_profile") not in PROFILES:
        errors.append(f"{source}: invalid lifecycle_profile {record.get('lifecycle_profile')!r}")
    risk = record.get("risk_tier")
    if risk not in RISKS:
        errors.append(f"{source}: invalid risk_tier {risk!r}")
    path = record.get("execution_path")
    if path not in PATHS:
        errors.append(f"{source}: invalid execution_path {path!r}")
    elif risk in RISKS and risk not in PATHS[path]:
        errors.append(f"{source}: execution_path {path!r} does not match risk_tier {risk!r}")
    approval = record.get("approval_status")
    if approval not in APPROVALS:
        errors.append(f"{source}: invalid approval_status {approval!r}")
    if not str(record.get("primary_deliverable", "")).strip():
        errors.append(f"{source}: primary_deliverable must name one artifact")

    task_id = str(record.get("task_id", ""))
    if catalog is not None and task_id and task_id not in catalog:
        errors.append(f"{source}: task_id is not a canonical catalog ID: {task_id}")
    next_task = str(record.get("next_task", ""))
    if catalog is not None and next_task and next_task not in catalog:
        errors.append(f"{source}: next_task is not a canonical catalog ID: {next_task}")

    if status in EVIDENCE_STATES and not record.get("evidence"):
        errors.append(f"{source}: status {status!r} requires at least one evidence reference")
    if status in EVIDENCE_STATES and not record.get("test_results"):
        errors.append(f"{source}: status {status!r} requires recorded test results")
    if status in APPROVED_STATES and approval not in {"approved", "not-required"}:
        errors.append(f"{source}: status {status!r} conflicts with approval_status {approval!r}")
    if risk in {"R3-controlled", "R4-critical"} and status in APPROVED_STATES and approval != "approved":
        errors.append(f"{source}: {risk} completion requires an explicit approval record")
    if status in {"blocked", "failed"} and not (record.get("residual_risks") or record.get("limitations")):
        errors.append(f"{source}: status {status!r} must state what blocks or failed")
    if complete:
        if status not in {"complete", "released", "monitored"}:
            errors.append(f"{source}: complete mode rejects status {status!r}")
        if not str(record.get("next_owner", "")).strip():
            errors.append(f"{source}: complete result requires an explicit next_owner")
        if not record.get("gate_results"):
            errors.append(f"{source}: complete result requires recorded gate results")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("result", type=Path, help="JSON task result object or array")
    parser.add_argument("--task-catalog", type=Path, help="task-catalog.json used to check canonical task IDs")
    parser.add_argument("--mode", choices=("plan", "complete"), default="plan")
    args = parser.parse_args()

    try:
        data = load(args.result)
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
    for index, record in enumerate(records):
        errors.extend(validate_record(record, f"{args.result}#{index}", catalog, args.mode == "complete"))

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"FAILED: {len(errors)} task-result validation error(s)")
        sys.exit(1)
    print(f"PASS: {len(records)} atomic task result(s) are structurally and logically consistent")


if __name__ == "__main__":
    main()
