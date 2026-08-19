#!/usr/bin/env python3
"""Validate workflow run state so a resumed run cannot skip gates or invent progress."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATUSES = {
    "planning", "assessing", "designing", "executing", "testing",
    "awaiting-approval", "releasing", "monitoring", "blocked", "failed", "complete",
}
RISKS = {"R0-light", "R1-reviewed", "R2-standard", "R3-controlled", "R4-critical"}
PATHS = {"fast-path": {"R0-light"}, "standard-path": {"R1-reviewed", "R2-standard"}, "controlled-path": {"R3-controlled", "R4-critical"}}
ARRAYS = ("completed_tasks", "passed_gates", "failed_tests", "blocked_by")
REQUIRED = (
    "workflow_id", "status", "lifecycle_profile", "risk_tier", "execution_path",
    "current_phase", "current_task", "completed_tasks", "passed_gates",
    "failed_tests", "blocked_by", "next_permitted_action", "updated_at",
)
TERMINAL_CLEAN = {"complete", "releasing", "monitoring"}


def parse_flat_yaml(text: str) -> dict[str, Any]:
    """Read the flat scalar/list mapping used by run-state.yaml without a YAML dependency."""
    data: dict[str, Any] = {}
    current: str | None = None
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith("  - ") and current is not None:
            data.setdefault(current, [])
            if not isinstance(data[current], list):
                raise ValueError(f"list item under scalar key: {current}")
            data[current].append(line[4:].strip().strip('"'))
            continue
        if line.startswith((" ", "\t")):
            raise ValueError(f"unsupported nested structure: {raw!r}")
        key, separator, value = line.partition(":")
        if not separator:
            raise ValueError(f"unparsable line: {raw!r}")
        key = key.strip()
        value = value.strip()
        current = key
        if value in ("", "[]"):
            data[key] = [] if value == "[]" else ""
        else:
            data[key] = value.strip('"')
    return data


def load_state(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".yaml", ".yml"}:
        return parse_flat_yaml(text)
    return json.loads(text)


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


def validate_state(state: dict[str, Any], source: str, catalog: set[str] | None) -> list[str]:
    errors: list[str] = []
    for field in REQUIRED:
        if field not in state:
            errors.append(f"{source}: missing {field}")
    unknown = sorted(set(state) - set(REQUIRED))
    if unknown:
        errors.append(f"{source}: unsupported fields {unknown}")
    for field in ARRAYS:
        value = state.get(field)
        if field in state and (not isinstance(value, list) or any(not isinstance(item, str) for item in value)):
            errors.append(f"{source}: {field} must be an array of strings")

    status = state.get("status")
    if status not in STATUSES:
        errors.append(f"{source}: invalid status {status!r}")
    risk = state.get("risk_tier")
    if risk not in RISKS:
        errors.append(f"{source}: invalid risk_tier {risk!r}")
    path = state.get("execution_path")
    if path not in PATHS:
        errors.append(f"{source}: invalid execution_path {path!r}")
    elif risk in RISKS and risk not in PATHS[path]:
        errors.append(f"{source}: execution_path {path!r} does not match risk_tier {risk!r}")
    for field in ("workflow_id", "lifecycle_profile", "current_phase", "next_permitted_action"):
        if not str(state.get(field, "")).strip():
            errors.append(f"{source}: {field} must not be empty")
    if parse_timestamp(state.get("updated_at", "")) is None:
        errors.append(f"{source}: updated_at must be an ISO 8601 timestamp")

    completed = state.get("completed_tasks") if isinstance(state.get("completed_tasks"), list) else []
    if len(completed) != len(set(completed)):
        errors.append(f"{source}: completed_tasks contains duplicates")
    current_task = str(state.get("current_task", ""))
    if catalog is not None:
        for task_id in completed:
            if task_id not in catalog:
                errors.append(f"{source}: completed task is not a canonical catalog ID: {task_id}")
        if current_task and current_task not in catalog:
            errors.append(f"{source}: current_task is not a canonical catalog ID: {current_task}")

    blocked_by = state.get("blocked_by") if isinstance(state.get("blocked_by"), list) else []
    failed_tests = state.get("failed_tests") if isinstance(state.get("failed_tests"), list) else []
    if status == "blocked" and not blocked_by:
        errors.append(f"{source}: blocked state must name what blocks it")
    if status == "failed" and not (failed_tests or blocked_by):
        errors.append(f"{source}: failed state must record a failed test or blocker")
    if status in TERMINAL_CLEAN and blocked_by:
        errors.append(f"{source}: status {status!r} cannot carry unresolved blockers {blocked_by}")
    if status in TERMINAL_CLEAN and failed_tests:
        errors.append(f"{source}: status {status!r} cannot carry failed tests {failed_tests}")
    if status == "complete":
        if not completed:
            errors.append(f"{source}: complete state requires at least one completed task")
        if current_task and current_task not in completed:
            errors.append(f"{source}: complete state leaves current_task {current_task!r} unfinished")
        if not state.get("passed_gates"):
            errors.append(f"{source}: complete state requires recorded passed gates")
    if status not in {"planning", "complete"} and not current_task:
        errors.append(f"{source}: status {status!r} requires a current_task")
    if current_task and current_task in completed and status not in {"complete", "monitoring"}:
        errors.append(f"{source}: current_task {current_task!r} is already recorded as completed")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("state", type=Path, help="run state as JSON, or the flat run-state.yaml template")
    parser.add_argument("--task-catalog", type=Path, help="task-catalog.json used to check canonical task IDs")
    args = parser.parse_args()

    try:
        state = load_state(args.state)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: unreadable run state: {exc}")
        sys.exit(1)
    if not isinstance(state, dict):
        print("ERROR: run state must be a mapping")
        sys.exit(1)

    catalog: set[str] | None = None
    if args.task_catalog is not None:
        try:
            entries = json.loads(args.task_catalog.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"ERROR: invalid task catalog: {exc}")
            sys.exit(1)
        if not isinstance(entries, list):
            print("ERROR: task catalog must be an array")
            sys.exit(1)
        catalog = {str(entry.get("id")) for entry in entries if isinstance(entry, dict)}

    errors = validate_state(state, str(args.state), catalog)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"FAILED: {len(errors)} run-state validation error(s)")
        sys.exit(1)
    print(f"PASS: run state {state.get('workflow_id')!r} is consistent at status {state.get('status')!r}")


if __name__ == "__main__":
    main()
