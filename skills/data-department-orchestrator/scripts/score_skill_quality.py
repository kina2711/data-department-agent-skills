#!/usr/bin/env python3
"""Turn recorded outcomes into per-task quality evidence and a controlled improvement decision.

A suite of 809 contracts is not uniformly good, and nothing in the catalog tells you which
tasks routed badly, failed often or needed a fallback. Without that, unreliable tasks and
dependable ones look identical, and the same mistake is repeated because no feedback reaches
the contract that caused it.

This reads the privacy-minimized telemetry ledger and produces a quality record per task:
routing quality, completion quality, fallback rate and evidence verification rate, plus a
recommended action. It recommends only; it never edits a contract. Improvement is a change
request with evidence attached, reviewed like any other change.

One rule is not negotiable and is enforced here: a high failure rate triggers investigation,
never a weaker gate. If the recommendation you want is "relax the approval", this tool will
not produce it.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

MIN_RUNS_FOR_JUDGEMENT = 5
POOR_COMPLETION = 0.60
HIGH_OVERRIDE = 0.25
HIGH_FALLBACK = 0.25
SUCCESS_OUTCOMES = {"complete"}


def load_events(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    events: list[dict[str, Any]] = []
    errors: list[str] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"line {number}: {exc}")
            continue
        if not isinstance(event, dict):
            errors.append(f"line {number}: event must be an object")
            continue
        if event.get("user_content") is not None:
            errors.append(f"line {number}: user_content is forbidden in telemetry")
            continue
        events.append(event)
    return events, errors


def recommend(record: dict[str, Any]) -> tuple[str, str]:
    """Return (action, reason). Actions never include weakening a control."""
    runs = record["runs"]
    if runs < MIN_RUNS_FOR_JUDGEMENT:
        return "observe", f"only {runs} run(s); too few to judge, keep collecting"
    if record["override_rate"] > HIGH_OVERRIDE:
        return "fix-routing", (
            f"{record['override_rate']:.0%} of runs overrode the routed task; the trigger or "
            "deliverable wording is selecting this contract for work it does not own"
        )
    if record["completion_rate"] < POOR_COMPLETION:
        codes = ", ".join(record["top_failure_codes"]) or "no failure codes recorded"
        return "investigate", (
            f"{record['completion_rate']:.0%} completion across {runs} runs ({codes}). "
            "Investigate the cause; do not lower the gate that is catching it"
        )
    if record["fallback_rate"] > HIGH_FALLBACK:
        return "derive-variant", (
            f"{record['fallback_rate']:.0%} of runs needed a fallback; a variant contract for "
            "that path may be missing"
        )
    if record["evidence_verified_rate"] is not None and record["evidence_verified_rate"] < 0.5:
        return "tighten-evidence", (
            f"only {record['evidence_verified_rate']:.0%} of completions carried verified "
            "evidence; completion is being claimed without proof"
        )
    return "healthy", f"{record['completion_rate']:.0%} completion across {runs} runs"


def build_records(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_task: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for event in events:
        by_task[str(event.get("task_id", ""))].append(event)

    records: list[dict[str, Any]] = []
    for task_id, task_events in sorted(by_task.items()):
        runs = len(task_events)
        outcomes = Counter(str(event.get("outcome", "")) for event in task_events)
        routes = Counter(str(event.get("route_source", "")) for event in task_events)
        failures = Counter(
            str(code)
            for event in task_events
            for code in event.get("failure_codes", [])
        )
        fallbacks = sum(1 for event in task_events if event.get("fallback_used") is True)
        superseded = Counter(
            str(event["superseded_by_task"])
            for event in task_events
            if event.get("superseded_by_task")
        )
        completed = [event for event in task_events if str(event.get("outcome")) in SUCCESS_OUTCOMES]
        verified_flags = [
            event.get("evidence_verified")
            for event in completed
            if isinstance(event.get("evidence_verified"), bool)
        ]
        tokens = [
            event["token_estimate"]
            for event in task_events
            if isinstance(event.get("token_estimate"), int)
        ]

        record = {
            "task_id": task_id,
            "skill": str(task_events[0].get("skill", "")),
            "runs": runs,
            "completion_rate": round(len(completed) / runs, 4),
            "blocked_rate": round(outcomes["blocked"] / runs, 4),
            "failed_rate": round(outcomes["failed"] / runs, 4),
            "abandoned_rate": round(outcomes["abandoned"] / runs, 4),
            "override_rate": round(routes["overridden"] / runs, 4),
            "fallback_rate": round(fallbacks / runs, 4),
            "evidence_verified_rate": round(sum(verified_flags) / len(verified_flags), 4) if verified_flags else None,
            "median_token_estimate": sorted(tokens)[len(tokens) // 2] if tokens else 0,
            "top_failure_codes": [code for code, _ in failures.most_common(3)],
            "most_common_replacement": superseded.most_common(1)[0][0] if superseded else None,
        }
        action, reason = recommend(record)
        record["recommended_action"] = action
        record["reason"] = reason
        records.append(record)
    return records


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("events", type=Path, help="telemetry JSONL ledger")
    parser.add_argument("--task-catalog", type=Path, help="task-catalog.json used to check canonical task IDs")
    parser.add_argument("--skill", help="report only this skill")
    parser.add_argument("--report-out", type=Path, help="write the quality records as JSON")
    parser.add_argument("--fail-on-action", action="store_true",
                        help="exit non-zero when any task needs investigation or a routing fix")
    args = parser.parse_args()

    try:
        events, errors = load_events(args.events)
    except OSError as exc:
        print(f"ERROR: unreadable telemetry: {exc}")
        sys.exit(1)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"FAILED: {len(errors)} telemetry error(s)")
        sys.exit(1)
    if not events:
        print("EMPTY: no telemetry events; skill quality is unknown, not good")
        sys.exit(1)

    records = build_records(events)

    if args.task_catalog is not None:
        try:
            catalog = {
                str(entry.get("id"))
                for entry in json.loads(args.task_catalog.read_text(encoding="utf-8"))
                if isinstance(entry, dict)
            }
        except (OSError, json.JSONDecodeError) as exc:
            print(f"ERROR: invalid task catalog: {exc}")
            sys.exit(1)
        unknown = sorted({record["task_id"] for record in records} - catalog)
        if unknown:
            for task_id in unknown:
                print(f"ERROR: telemetry references a non-canonical task ID: {task_id}")
            print(f"FAILED: {len(unknown)} unknown task ID(s)")
            sys.exit(1)

    shown = [record for record in records if not args.skill or record["skill"] == args.skill]
    shown.sort(key=lambda record: (record["completion_rate"], -record["runs"]))

    for record in shown:
        print(
            f"{record['recommended_action']:<17} {record['task_id']}  "
            f"({record['runs']} runs, {record['completion_rate']:.0%} complete)"
        )
        print(f"                  {record['reason']}")
        if record["most_common_replacement"]:
            print(f"                  most often replaced by: {record['most_common_replacement']}")

    if args.report_out is not None:
        payload = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "events": len(events),
            "tasks": len(records),
            "records": records,
            "policy": "A high failure rate triggers investigation, never a weaker gate.",
        }
        args.report_out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"report written: {args.report_out}")

    actions = Counter(record["recommended_action"] for record in records)
    summary = ", ".join(f"{count} {action}" for action, count in sorted(actions.items()))
    print(f"SUMMARY: {len(records)} task(s) over {len(events)} event(s): {summary}")
    print("Recommendations are change requests, not edits. Improve a contract through review, with evidence attached.")

    needs_work = actions["investigate"] + actions["fix-routing"] + actions["tighten-evidence"]
    if args.fail_on_action and needs_work:
        print(f"ACTION REQUIRED: {needs_work} task(s) need investigation or a routing/evidence fix")
        sys.exit(1)


if __name__ == "__main__":
    main()
