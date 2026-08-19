#!/usr/bin/env python3
"""Check that a curriculum teaches what it assesses and assesses what it teaches.

Two failures survive most curriculum reviews. An objective with no assessment item is taught
and never verified, so nobody knows whether it landed. An assessment item with no objective
tests something the course never covered. A third, quieter one: prerequisites that form a
cycle, which makes the ordering impossible to satisfy no matter where a learner starts.

It checks the curriculum's internal consistency. It cannot judge whether an assessment item is
a good test of its objective, or whether the difficulty is right for the audience.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

BLOOM_LEVELS = ["remember", "understand", "apply", "analyze", "evaluate", "create"]
# An objective at 'apply' or above cannot be verified by recall alone.
PERFORMANCE_LEVELS = set(BLOOM_LEVELS[2:])
RECALL_ITEM_TYPES = {"multiple-choice", "true-false", "fill-in-blank", "recall"}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def find_cycles(edges: dict[str, list[str]]) -> list[list[str]]:
    """Depth-first search for prerequisite cycles; an ordering cannot exist inside one."""
    colour: dict[str, int] = defaultdict(int)
    cycles: list[list[str]] = []
    stack: list[str] = []

    def visit(node: str) -> None:
        colour[node] = 1
        stack.append(node)
        for neighbour in edges.get(node, []):
            if colour[neighbour] == 0:
                visit(neighbour)
            elif colour[neighbour] == 1 and neighbour in stack:
                cycles.append(stack[stack.index(neighbour):] + [neighbour])
        stack.pop()
        colour[node] = 2

    for node in sorted(edges):
        if colour[node] == 0:
            visit(node)
    return cycles


def validate(curriculum: Any) -> tuple[list[str], list[str], dict[str, Any]]:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(curriculum, dict):
        return ["curriculum must be an object"], [], {}

    objectives = curriculum.get("objectives")
    assessments = curriculum.get("assessments")
    if not isinstance(objectives, list) or not objectives:
        errors.append("objectives must be a non-empty array")
    if not isinstance(assessments, list) or not assessments:
        errors.append("assessments must be a non-empty array")
    if errors:
        return errors, warnings, {}

    objective_by_id: dict[str, dict[str, Any]] = {}
    prerequisites: dict[str, list[str]] = {}
    for index, objective in enumerate(objectives):
        label = f"objectives[{index}]"
        if not isinstance(objective, dict):
            errors.append(f"{label}: must be an object")
            continue
        objective_id = str(objective.get("id", "")).strip()
        if not objective_id:
            errors.append(f"{label}: missing id")
            continue
        if objective_id in objective_by_id:
            errors.append(f"{objective_id}: duplicate objective id")
        objective_by_id[objective_id] = objective
        if not str(objective.get("statement", "")).strip():
            errors.append(f"{objective_id}: missing statement")
        level = str(objective.get("level", "")).strip().lower()
        if level not in BLOOM_LEVELS:
            errors.append(f"{objective_id}: level {level!r} is not one of {BLOOM_LEVELS}")
        prerequisites[objective_id] = [str(item) for item in objective.get("prerequisites", [])]

    for objective_id, required in prerequisites.items():
        for prerequisite in required:
            if prerequisite not in objective_by_id:
                errors.append(f"{objective_id}: prerequisite {prerequisite!r} is not a declared objective")

    for cycle in find_cycles({k: [p for p in v if p in objective_by_id] for k, v in prerequisites.items()}):
        errors.append(f"prerequisite cycle: {' -> '.join(cycle)}; no learner ordering can satisfy it")

    assessed: dict[str, list[str]] = defaultdict(list)
    for index, item in enumerate(assessments):
        label = f"assessments[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label}: must be an object")
            continue
        item_id = str(item.get("id", "")).strip() or label
        targets = item.get("objectives")
        if not isinstance(targets, list) or not targets:
            errors.append(f"{item_id}: assesses no objective; it tests something the curriculum never declared")
            continue
        item_type = str(item.get("type", "")).strip().lower()
        for target in targets:
            target_id = str(target)
            if target_id not in objective_by_id:
                errors.append(f"{item_id}: targets undeclared objective {target_id!r}")
                continue
            assessed[target_id].append(item_id)
            level = str(objective_by_id[target_id].get("level", "")).lower()
            if level in PERFORMANCE_LEVELS and item_type in RECALL_ITEM_TYPES:
                errors.append(
                    f"{item_id}: {item_type} cannot verify a '{level}' objective ({target_id}); "
                    "recall does not demonstrate application"
                )
        if not item.get("passing_criterion"):
            warnings.append(f"{item_id}: no passing_criterion; the result cannot be judged")

    unassessed = sorted(set(objective_by_id) - set(assessed))
    for objective_id in unassessed:
        errors.append(f"{objective_id}: taught but never assessed; its outcome is unknown")

    orphan_levels = [
        objective_id for objective_id, objective in objective_by_id.items()
        if not objective.get("evidence_of_mastery")
    ]
    for objective_id in orphan_levels:
        warnings.append(f"{objective_id}: no evidence_of_mastery stated; attendance is not mastery")

    summary = {
        "objectives": len(objective_by_id),
        "assessments": len(assessments),
        "assessed_objectives": len(assessed),
        "coverage": round(len(assessed) / len(objective_by_id), 4) if objective_by_id else 0.0,
        "unassessed": unassessed,
        "errors": len(errors),
        "warnings": len(warnings),
    }
    return errors, warnings, summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("curriculum", type=Path, help="curriculum JSON with objectives and assessments")
    parser.add_argument("--strict", action="store_true", help="treat warnings as failures")
    parser.add_argument("--report-out", type=Path)
    args = parser.parse_args()

    try:
        curriculum = load(args.curriculum)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: unreadable curriculum: {exc}")
        sys.exit(1)

    errors, warnings, summary = validate(curriculum)
    for error in errors:
        print(f"ERROR: {error}")
    for warning in warnings:
        print(f"WARNING: {warning}")

    if summary:
        print(
            f"objectives: {summary['objectives']}  assessments: {summary['assessments']}  "
            f"coverage: {summary['coverage']:.0%}"
        )
    if args.report_out is not None and summary:
        args.report_out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"report written: {args.report_out}")

    if errors:
        print(f"FAILED: {len(errors)} curriculum error(s)")
        sys.exit(1)
    if warnings and args.strict:
        print(f"FAILED: {len(warnings)} warning(s) under --strict")
        sys.exit(1)
    if warnings:
        print(f"PASS WITH WARNINGS: {len(warnings)} item(s) to resolve before delivery")
        sys.exit(0)
    print("PASS: every objective is assessed at a level that can verify it")


if __name__ == "__main__":
    main()
