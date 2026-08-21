#!/usr/bin/env python3
"""Score a 7/30/60/90-day onboarding checkpoint without letting an average hide a blocker.

The failure mode this guards against is arithmetic: four strong dimensions and one unresolved
access or security dimension average to "on track", and the person is sent to independent work
without the entitlement, the escalation path or the review they need. A critical dimension below
the bar blocks the readiness decision regardless of the mean.

It checks a checkpoint record against the rubric. It cannot observe the work itself, so every
score at or above "performs a bounded task" must name evidence.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REQUIRED_DIMENSIONS = (
    "access-readiness",
    "role-clarity",
    "domain-understanding",
    "delivery-readiness",
    "integration",
)
CRITICAL_BY_DEFAULT = {"access-readiness"}
EVIDENCE_REQUIRED_AT = 2
READY_MEAN = 2.0
SCORE_LABELS = {
    0: "not started",
    1: "exposed but still blocked or fully guided",
    2: "performs a bounded task with normal support",
    3: "performs independently and can explain risks and escalation",
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate(record: Any) -> tuple[list[str], list[str], dict[str, Any]]:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(record, dict):
        return ["checkpoint record must be a JSON object"], [], {}

    for field in ("person", "role", "checkpoint"):
        if not str(record.get(field, "")).strip():
            errors.append(f"missing {field}")

    dimensions = record.get("dimensions")
    if not isinstance(dimensions, list) or not dimensions:
        errors.append("dimensions must be a non-empty array")
        return errors, warnings, {}

    seen: dict[str, int] = {}
    blocking: list[str] = []
    unevidenced: list[str] = []
    for index, item in enumerate(dimensions):
        label = f"dimensions[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label}: must be an object")
            continue
        name = str(item.get("name", "")).strip()
        if not name:
            errors.append(f"{label}: missing name")
            continue
        if name in seen:
            errors.append(f"{name}: scored twice")
        score = item.get("score")
        if not isinstance(score, int) or isinstance(score, bool) or not 0 <= score <= 3:
            errors.append(f"{name}: score must be an integer 0-3, got {score!r}")
            continue
        seen[name] = score

        evidence = item.get("evidence")
        evidence = evidence if isinstance(evidence, list) else []
        evidence = [str(entry).strip() for entry in evidence if str(entry).strip()]
        if score >= EVIDENCE_REQUIRED_AT and not evidence:
            unevidenced.append(name)
            errors.append(
                f"{name}: scored {score} ({SCORE_LABELS[score]}) with no evidence; "
                "an unevidenced score is an impression, not a checkpoint"
            )

        critical = item.get("critical")
        critical = name in CRITICAL_BY_DEFAULT if critical is None else bool(critical)
        if critical and score < EVIDENCE_REQUIRED_AT:
            blocking.append(f"{name} ({score})")

    missing = [name for name in REQUIRED_DIMENSIONS if name not in seen]
    for name in missing:
        errors.append(f"required dimension not scored: {name}")

    extra = sorted(set(seen) - set(REQUIRED_DIMENSIONS))
    if extra:
        warnings.append(f"non-standard dimension(s) scored: {', '.join(extra)}")

    scores = list(seen.values())
    mean = round(sum(scores) / len(scores), 2) if scores else 0.0
    zero_dimensions = sorted(name for name, score in seen.items() if score == 0)
    if zero_dimensions:
        warnings.append(f"not started: {', '.join(zero_dimensions)}")

    if blocking:
        decision = "blocked"
    elif missing or errors:
        decision = "incomplete"
    elif mean >= READY_MEAN:
        decision = "ready-for-next-stage"
    else:
        decision = "not-ready"

    summary = {
        "scored": len(seen),
        "mean": mean,
        "blocking": blocking,
        "unevidenced": unevidenced,
        "decision": decision,
    }
    return errors, warnings, summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("checkpoint", type=Path, help="checkpoint record as JSON")
    parser.add_argument("--require-ready", action="store_true", help="exit non-zero unless the decision is ready-for-next-stage")
    args = parser.parse_args()

    if not args.checkpoint.is_file():
        print(f"ERROR: no such file: {args.checkpoint}")
        sys.exit(2)
    try:
        record = load(args.checkpoint)
    except json.JSONDecodeError as exc:
        print(f"ERROR: invalid JSON: {exc}")
        sys.exit(2)

    errors, warnings, summary = evaluate(record)
    for error in errors:
        print(f"ERROR: {error}")
    for warning in warnings:
        print(f"WARNING: {warning}")

    if summary:
        print(f"dimensions scored: {summary['scored']}  mean: {summary['mean']}  decision: {summary['decision']}")
        if summary["blocking"]:
            print(f"critical dimension(s) below the bar: {', '.join(summary['blocking'])}")
            print("NOTE: a critical failure is never averaged away; resolve it before the readiness decision")

    if errors:
        print(f"FAILED: {len(errors)} rubric error(s)")
        sys.exit(1)
    if summary.get("decision") == "blocked":
        print("BLOCKED: a critical dimension is below the bar; the readiness decision cannot be taken")
        sys.exit(1)
    if args.require_ready and summary.get("decision") != "ready-for-next-stage":
        print(f"FAILED: decision is {summary.get('decision')} under --require-ready")
        sys.exit(1)
    if warnings:
        print(f"PASS WITH WARNINGS: {len(warnings)} item(s) to confirm with the manager and buddy")
        sys.exit(0)
    print(f"PASS: checkpoint is complete and evidenced; decision {summary.get('decision')}")


if __name__ == "__main__":
    main()
