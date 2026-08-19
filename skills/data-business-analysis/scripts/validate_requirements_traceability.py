#!/usr/bin/env python3
"""Trace requirements to acceptance criteria to tests, and report what is unverified.

The failure this catches is a requirement that everyone agreed to and nobody verified. It shows
up at UAT as "we thought that was covered". Tracing the chain in both directions also catches
the opposite defect: work built and tested that no stated requirement asked for.

It checks the traceability matrix, not the system. A requirement traced to a passing test is
covered on paper; whether the test actually exercises the requirement is a review judgement.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

PRIORITIES = ["must", "should", "could", "wont"]
TEST_RESULTS = {"passed", "failed", "blocked", "not-run"}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(matrix: Any) -> tuple[list[str], list[str], dict[str, Any]]:
    errors: list[str] = []
    findings: list[str] = []
    if not isinstance(matrix, dict):
        return ["matrix must be an object"], [], {}

    requirements = matrix.get("requirements")
    tests = matrix.get("tests", [])
    if not isinstance(requirements, list) or not requirements:
        return ["requirements must be a non-empty array"], [], {}
    if not isinstance(tests, list):
        return ["tests must be an array"], [], {}

    requirement_by_id: dict[str, dict[str, Any]] = {}
    criteria_by_requirement: dict[str, list[str]] = defaultdict(list)
    all_criteria: set[str] = set()

    for index, requirement in enumerate(requirements):
        label = f"requirements[{index}]"
        if not isinstance(requirement, dict):
            errors.append(f"{label}: must be an object")
            continue
        requirement_id = str(requirement.get("id", "")).strip()
        if not requirement_id:
            errors.append(f"{label}: missing id")
            continue
        if requirement_id in requirement_by_id:
            errors.append(f"{requirement_id}: duplicate requirement id")
        requirement_by_id[requirement_id] = requirement

        if not str(requirement.get("statement", "")).strip():
            errors.append(f"{requirement_id}: missing statement")
        priority = str(requirement.get("priority", "")).strip().lower()
        if priority not in PRIORITIES:
            errors.append(f"{requirement_id}: priority {priority!r} is not one of {PRIORITIES}")
        if not str(requirement.get("requested_by", "")).strip():
            findings.append(f"{requirement_id}: no requested_by; an unattributed requirement has no one to confirm it")

        criteria = requirement.get("acceptance_criteria")
        if not isinstance(criteria, list) or not criteria:
            errors.append(f"{requirement_id}: no acceptance criteria; it cannot be accepted or rejected")
            continue
        for criterion in criteria:
            criterion_id = str(criterion.get("id", "")) if isinstance(criterion, dict) else str(criterion)
            if not criterion_id:
                errors.append(f"{requirement_id}: an acceptance criterion has no id")
                continue
            if criterion_id in all_criteria:
                errors.append(f"{criterion_id}: acceptance criterion id is reused across requirements")
            all_criteria.add(criterion_id)
            criteria_by_requirement[requirement_id].append(criterion_id)

    covered: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for index, test in enumerate(tests):
        label = f"tests[{index}]"
        if not isinstance(test, dict):
            errors.append(f"{label}: must be an object")
            continue
        test_id = str(test.get("id", "")).strip() or label
        result = str(test.get("result", "")).strip().lower()
        if result not in TEST_RESULTS:
            errors.append(f"{test_id}: result {result!r} is not one of {sorted(TEST_RESULTS)}")
        targets = test.get("covers")
        if not isinstance(targets, list) or not targets:
            findings.append(f"{test_id}: covers no acceptance criterion; it verifies nothing that was asked for")
            continue
        for target in targets:
            criterion_id = str(target)
            if criterion_id not in all_criteria:
                errors.append(f"{test_id}: covers unknown acceptance criterion {criterion_id!r}")
                continue
            covered[criterion_id].append((test_id, result))

    unverified: list[str] = []
    failing: list[str] = []
    for requirement_id, criteria in criteria_by_requirement.items():
        priority = str(requirement_by_id[requirement_id].get("priority", "")).lower()
        for criterion_id in criteria:
            results = covered.get(criterion_id, [])
            if not results:
                unverified.append(criterion_id)
                severity = "ERROR" if priority == "must" else "OPEN"
                findings.append(
                    f"{severity} {requirement_id}/{criterion_id} ({priority}): no test covers this criterion"
                )
                continue
            passing = [test_id for test_id, result in results if result == "passed"]
            if not passing:
                states = ", ".join(f"{test_id}={result}" for test_id, result in results)
                failing.append(criterion_id)
                findings.append(
                    f"OPEN {requirement_id}/{criterion_id} ({priority}): covered but not passing ({states})"
                )

    must_unverified = [
        criterion_id
        for requirement_id, criteria in criteria_by_requirement.items()
        if str(requirement_by_id[requirement_id].get("priority", "")).lower() == "must"
        for criterion_id in criteria
        if criterion_id in unverified or criterion_id in failing
    ]

    summary = {
        "requirements": len(requirement_by_id),
        "acceptance_criteria": len(all_criteria),
        "tests": len(tests),
        "criteria_covered": len(covered),
        "coverage": round(len(covered) / len(all_criteria), 4) if all_criteria else 0.0,
        "unverified_criteria": sorted(unverified),
        "covered_but_not_passing": sorted(failing),
        "must_have_gaps": sorted(set(must_unverified)),
    }
    return errors, findings, summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("matrix", type=Path, help="traceability matrix JSON")
    parser.add_argument("--uat-ready", action="store_true",
                        help="fail unless every must-have criterion is covered by a passing test")
    parser.add_argument("--report-out", type=Path)
    args = parser.parse_args()

    try:
        matrix = load(args.matrix)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: unreadable matrix: {exc}")
        sys.exit(1)

    errors, findings, summary = validate(matrix)
    for error in errors:
        print(f"ERROR: {error}")
    for finding in findings:
        print(finding)

    if summary:
        print(
            f"requirements: {summary['requirements']}  criteria: {summary['acceptance_criteria']}  "
            f"tests: {summary['tests']}  coverage: {summary['coverage']:.0%}"
        )
        if args.report_out is not None:
            args.report_out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(f"report written: {args.report_out}")

    if errors:
        print(f"FAILED: {len(errors)} matrix error(s)")
        sys.exit(1)
    if args.uat_ready and summary.get("must_have_gaps"):
        gaps = ", ".join(summary["must_have_gaps"])
        print(f"BLOCKED: must-have criteria without a passing test: {gaps}")
        sys.exit(3)
    if summary.get("unverified_criteria") or summary.get("covered_but_not_passing"):
        print("INCOMPLETE: some criteria are unverified; this is not UAT-ready")
        sys.exit(2)
    print("PASS: every acceptance criterion is covered by a passing test")


if __name__ == "__main__":
    main()
