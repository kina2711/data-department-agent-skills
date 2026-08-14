#!/usr/bin/env python3
"""Validate an executable Data Department workflow without mutating it."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

RISK = {"R0-light": 0, "R1-reviewed": 1, "R2-standard": 2, "R3-controlled": 3, "R4-critical": 4}
TASK_STATES = ["planned", "ready", "in-progress", "blocked", "failed", "implemented", "tested", "approved", "released", "complete"]
EXECUTED_STATES = {"in-progress", "implemented", "tested", "approved", "released", "complete"}
EVIDENCE_STATES = {"tested", "approved", "released", "complete"}
APPROVAL_STATES = {"approved", "released", "complete"}
ALLOWED_TASK_TRANSITIONS = {
    "planned": {"ready", "blocked", "failed"},
    "ready": {"in-progress", "blocked", "failed"},
    "in-progress": {"implemented", "blocked", "failed"},
    "implemented": {"in-progress", "tested", "blocked", "failed"},
    "tested": {"approved", "released", "complete", "failed"},
    "approved": {"released", "failed"},
    "released": {"complete", "failed"},
    "blocked": {"ready", "failed"},
    "failed": {"ready"},
    "complete": set(),
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_records(folder: Path | None, key: str, errors: list[str]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    if folder is None:
        return result
    if not folder.is_dir():
        errors.append(f"record directory does not exist: {folder}")
        return result
    for path in sorted(folder.glob("*.json")):
        try:
            record = load_json(path)
            record_id = str(record.get(key, "")).strip()
            if not record_id:
                errors.append(f"{path}: missing {key}")
            elif record_id in result:
                errors.append(f"duplicate {key}: {record_id}")
            else:
                result[record_id] = record
        except (OSError, json.JSONDecodeError, TypeError) as exc:
            errors.append(f"{path}: invalid JSON: {exc}")
    return result


def detect_cycle(tasks: dict[str, dict[str, Any]]) -> list[str]:
    visiting: set[str] = set()
    visited: set[str] = set()
    path: list[str] = []

    def walk(task_id: str) -> list[str]:
        if task_id in visiting:
            start = path.index(task_id)
            return path[start:] + [task_id]
        if task_id in visited:
            return []
        visiting.add(task_id)
        path.append(task_id)
        for dep in tasks[task_id].get("depends_on", []):
            if dep in tasks:
                cycle = walk(dep)
                if cycle:
                    return cycle
        path.pop()
        visiting.remove(task_id)
        visited.add(task_id)
        return []

    for task_id in tasks:
        cycle = walk(task_id)
        if cycle:
            return cycle
    return []


def validate(args: argparse.Namespace) -> list[str]:
    errors: list[str] = []
    try:
        workflow = load_json(args.workflow)
        catalog_rows = load_json(args.catalog)
    except (OSError, json.JSONDecodeError, TypeError) as exc:
        return [f"invalid workflow/catalog JSON: {exc}"]

    if not isinstance(workflow, dict) or not isinstance(catalog_rows, list):
        return ["workflow must be an object and catalog must be an array"]
    catalog = {row.get("id"): row for row in catalog_rows if isinstance(row, dict)}
    task_rows = workflow.get("tasks")
    if not isinstance(task_rows, list) or not task_rows:
        return ["tasks must be a non-empty array"]

    tasks: dict[str, dict[str, Any]] = {}
    for index, task in enumerate(task_rows):
        if not isinstance(task, dict):
            errors.append(f"tasks[{index}] must be an object")
            continue
        task_id = str(task.get("task_id", "")).strip()
        if not task_id:
            errors.append(f"tasks[{index}].task_id is required")
            continue
        if task_id in tasks:
            errors.append(f"duplicate workflow task: {task_id}")
            continue
        tasks[task_id] = task
        if task_id not in catalog:
            errors.append(f"unknown catalog task: {task_id}")
            continue
        if not str(task.get("owner", "")).strip():
            errors.append(f"{task_id}: owner is required")
        if task.get("status") not in TASK_STATES:
            errors.append(f"{task_id}: invalid status {task.get('status')!r}")
        declared = task.get("risk_tier")
        floor = catalog[task_id].get("risk_tier")
        if declared not in RISK:
            errors.append(f"{task_id}: invalid risk tier {declared!r}")
        elif floor in RISK and RISK[declared] < RISK[floor]:
            errors.append(f"{task_id}: risk downgrade {declared} below catalog floor {floor}")
        for field in ("depends_on", "evidence_refs", "approval_refs"):
            if not isinstance(task.get(field), list):
                errors.append(f"{task_id}: {field} must be an array")

    for task_id, task in tasks.items():
        dependencies = task.get("depends_on", []) if isinstance(task.get("depends_on"), list) else []
        for dependency in dependencies:
            if dependency == task_id:
                errors.append(f"{task_id}: cannot depend on itself")
            elif dependency not in tasks:
                errors.append(f"{task_id}: unknown dependency {dependency}")
        if task.get("status") in EXECUTED_STATES:
            unfinished = [dep for dep in dependencies if dep in tasks and tasks[dep].get("status") not in {"released", "complete"}]
            if unfinished:
                errors.append(f"{task_id}: executed before dependencies complete: {unfinished}")

    cycle = detect_cycle(tasks)
    if cycle:
        errors.append("dependency cycle: " + " -> ".join(cycle))

    current = str(workflow.get("current_task_id", ""))
    if current and current not in tasks:
        errors.append(f"current_task_id is not in tasks: {current}")

    workflow_risk = workflow.get("workflow_risk_tier")
    if workflow_risk not in RISK:
        errors.append(f"invalid workflow_risk_tier: {workflow_risk!r}")
    else:
        child_risks = []
        for task_id, task in tasks.items():
            declared = RISK.get(task.get("risk_tier"), 0)
            floor = RISK.get(catalog.get(task_id, {}).get("risk_tier"), 0)
            child_risks.append(max(declared, floor))
        if child_risks and RISK[workflow_risk] < max(child_risks):
            errors.append(f"workflow risk {workflow_risk} is below highest child-task risk")

    transitions = workflow.get("transitions")
    if not isinstance(transitions, list):
        errors.append("transitions must be an array")
        transitions = []
    transition_state = {task_id: "planned" for task_id in tasks}
    last_occurred_at = ""
    transitioned_tasks: set[str] = set()
    for index, transition in enumerate(transitions):
        if not isinstance(transition, dict):
            errors.append(f"transitions[{index}] must be an object")
            continue
        task_id = str(transition.get("task_id", ""))
        if task_id not in tasks:
            errors.append(f"transitions[{index}]: unknown task {task_id}")
            continue
        source = transition.get("from_status")
        target = transition.get("to_status")
        if source != transition_state[task_id]:
            errors.append(f"{task_id}: transition source {source!r} does not match prior state {transition_state[task_id]!r}")
        if source not in ALLOWED_TASK_TRANSITIONS or target not in ALLOWED_TASK_TRANSITIONS.get(str(source), set()):
            errors.append(f"{task_id}: illegal transition {source!r} -> {target!r}")
        refs = transition.get("evidence_refs")
        if not isinstance(refs, list):
            errors.append(f"{task_id}: transition evidence_refs must be an array")
        elif target in {"tested", "approved", "released", "complete"} and not refs:
            errors.append(f"{task_id}: transition to {target} requires evidence_refs")
        occurred_at = str(transition.get("occurred_at", ""))
        if not occurred_at:
            errors.append(f"{task_id}: transition occurred_at is required")
        elif last_occurred_at and occurred_at < last_occurred_at:
            errors.append(f"{task_id}: transition history is not chronological")
        last_occurred_at = max(last_occurred_at, occurred_at)
        if target in ALLOWED_TASK_TRANSITIONS:
            transition_state[task_id] = target
        transitioned_tasks.add(task_id)
    for task_id, task in tasks.items():
        if task_id in transitioned_tasks and transition_state[task_id] != task.get("status"):
            errors.append(f"{task_id}: transition history ends at {transition_state[task_id]} but task status is {task.get('status')}")
        if (args.mode == "complete" or workflow.get("status") == "complete") and task.get("status") != "planned" and task_id not in transitioned_tasks:
            errors.append(f"{task_id}: complete workflow requires transition history")

    evidence = load_records(args.evidence_dir, "evidence_id", errors)
    approvals = load_records(args.approval_dir, "approval_id", errors)
    for transition in transitions:
        if isinstance(transition, dict):
            for ref in transition.get("evidence_refs", []) if isinstance(transition.get("evidence_refs"), list) else []:
                if ref not in evidence:
                    errors.append(f"transition for {transition.get('task_id')}: unresolved evidence {ref}")
    for task_id, task in tasks.items():
        status = task.get("status")
        evidence_refs = task.get("evidence_refs", []) if isinstance(task.get("evidence_refs"), list) else []
        approval_refs = task.get("approval_refs", []) if isinstance(task.get("approval_refs"), list) else []
        if status in EVIDENCE_STATES and not evidence_refs:
            errors.append(f"{task_id}: {status} requires evidence_refs")
        for ref in evidence_refs:
            record = evidence.get(ref)
            if not record:
                errors.append(f"{task_id}: unresolved evidence {ref}")
            elif record.get("task_id") != task_id:
                errors.append(f"{task_id}: evidence {ref} belongs to {record.get('task_id')}")
        if task.get("risk_tier") in {"R3-controlled", "R4-critical"} and status in EXECUTED_STATES and not approval_refs:
            errors.append(f"{task_id}: controlled execution requires approval_refs")
        if status in APPROVAL_STATES and task.get("risk_tier") != "R0-light" and not approval_refs:
            errors.append(f"{task_id}: {status} requires approval_refs")
        for ref in approval_refs:
            record = approvals.get(ref)
            if not record:
                errors.append(f"{task_id}: unresolved approval {ref}")
                continue
            if record.get("task_id") != task_id or record.get("decision") != "approved":
                errors.append(f"{task_id}: approval {ref} is not an approved record for this task")
            if record.get("artifact_version") != task.get("artifact_version"):
                errors.append(f"{task_id}: approval {ref} version mismatch")
            if str(record.get("artifact_sha256", "")).lower() != str(task.get("artifact_sha256", "")).lower():
                errors.append(f"{task_id}: approval {ref} hash mismatch")

    claims = workflow.get("claims")
    if not isinstance(claims, list):
        errors.append("claims must be an array")
        claims = []
    for claim in claims:
        if not isinstance(claim, dict):
            errors.append("claim must be an object")
            continue
        claim_id = str(claim.get("claim_id", "")).strip()
        task_id = claim.get("task_id")
        refs = claim.get("evidence_refs")
        if not claim_id:
            errors.append("claim_id is required")
        if not str(claim.get("wording", "")).strip():
            errors.append(f"claim {claim_id or '<missing>'}: wording is required")
        if task_id not in tasks:
            errors.append(f"claim {claim.get('claim_id')}: unknown task {task_id}")
        if claim.get("status") not in {"draft", "verified", "rejected"}:
            errors.append(f"claim {claim_id or '<missing>'}: invalid status {claim.get('status')!r}")
        if not isinstance(refs, list):
            errors.append(f"claim {claim_id or '<missing>'}: evidence_refs must be an array")
        if claim.get("status") == "verified" and (not isinstance(refs, list) or not refs):
            errors.append(f"claim {claim.get('claim_id')}: verified claim lacks evidence")
        for ref in refs if isinstance(refs, list) else []:
            if ref not in evidence:
                errors.append(f"claim {claim.get('claim_id')}: unresolved evidence {ref}")

    if args.mode == "complete" or workflow.get("status") == "complete":
        incomplete = [task_id for task_id, task in tasks.items() if task.get("status") not in {"released", "complete"}]
        if incomplete:
            errors.append(f"complete workflow has incomplete tasks: {incomplete}")
        unresolved_claims = [c.get("claim_id") for c in claims if isinstance(c, dict) and c.get("status") not in {"verified", "rejected"}]
        if unresolved_claims:
            errors.append(f"complete workflow has unresolved claims: {unresolved_claims}")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("workflow", type=Path)
    parser.add_argument("--catalog", type=Path, default=Path(__file__).resolve().parents[1] / "assets" / "task-catalog.json")
    parser.add_argument("--evidence-dir", type=Path)
    parser.add_argument("--approval-dir", type=Path)
    parser.add_argument("--mode", choices=("plan", "execute", "complete"), default="execute")
    args = parser.parse_args()
    errors = validate(args)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"FAILED: {len(errors)} workflow validation error(s)")
        sys.exit(1)
    print("PASS: workflow graph, risk, evidence, approval and completion controls are valid")


if __name__ == "__main__":
    main()
