#!/usr/bin/env python3
"""Check a parallel branch plan before any branch is dispatched.

Parallel execution fails in ways sequential execution cannot: two branches write the same file and
the last one wins silently, a branch reads a path another branch is still rewriting, a delegated
branch carries a risk tier its supervisor was never authorized for, or branches are declared
parallel while one actually depends on another's output. None of that is visible in the result —
it is visible in the plan.

It checks the plan's structure, path isolation and risk ceiling against the canonical task
catalog. It dispatches nothing, and a valid plan is not evidence that the work was done.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import PurePosixPath
from pathlib import Path
from typing import Any

RISK_ORDER = ("R0-light", "R1-reviewed", "R2-standard", "R3-controlled", "R4-critical")
DELEGABLE_CEILING = "R2-standard"


def rank(tier: str) -> int:
    try:
        return RISK_ORDER.index(tier)
    except ValueError:
        return -1


def normalize(path: str) -> PurePosixPath:
    cleaned = str(path).replace("\\", "/").strip()
    while cleaned.startswith("./"):
        cleaned = cleaned[2:]
    return PurePosixPath(cleaned.rstrip("/") or ".")


def overlaps(left: PurePosixPath, right: PurePosixPath) -> bool:
    """True when one path contains the other, which is enough for two writers to collide."""
    return left == right or str(left).startswith(str(right) + "/") or str(right).startswith(str(left) + "/")


def load_catalog(path: Path) -> dict[str, str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    tasks = data.get("tasks") if isinstance(data, dict) else data
    if not isinstance(tasks, list):
        raise ValueError("task catalog must be a list of tasks or an object with a tasks array")
    return {
        str(task["id"]): str(task.get("risk_tier", ""))
        for task in tasks
        if isinstance(task, dict) and task.get("id")
    }


def validate(plan: Any, catalog: dict[str, str] | None, ceiling: str) -> tuple[list[str], list[str], dict[str, Any]]:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(plan, dict):
        return ["branch plan must be a JSON object"], [], {}

    if not str(plan.get("workflow_id", "")).strip():
        errors.append("missing workflow_id; a branch plan that names no workflow cannot be merged back into one")

    branches = plan.get("branches")
    if not isinstance(branches, list) or not branches:
        errors.append("branches must be a non-empty array")
        return errors, warnings, {}
    if len(branches) == 1:
        warnings.append("a single branch is sequential work; the parallel contract adds cost without adding concurrency")

    plan_ceiling = str(plan.get("supervisor_risk_ceiling", ceiling)).strip() or ceiling
    if rank(plan_ceiling) < 0:
        errors.append(f"supervisor_risk_ceiling {plan_ceiling!r} is not one of {', '.join(RISK_ORDER)}")
        plan_ceiling = ceiling

    seen: set[str] = set()
    writes: dict[str, list[PurePosixPath]] = {}
    reads: dict[str, list[PurePosixPath]] = {}
    branch_ids: set[str] = set()

    for index, branch in enumerate(branches):
        label = f"branches[{index}]"
        if not isinstance(branch, dict):
            errors.append(f"{label}: must be an object")
            continue
        branch_id = str(branch.get("branch_id", "")).strip()
        if not branch_id:
            errors.append(f"{label}: missing branch_id")
            continue
        if branch_id in seen:
            errors.append(f"{branch_id}: duplicate branch_id")
        seen.add(branch_id)
        branch_ids.add(branch_id)

        task_id = str(branch.get("task_id", "")).strip()
        if not task_id:
            errors.append(f"{branch_id}: missing task_id")
        elif catalog is not None:
            if task_id not in catalog:
                errors.append(f"{branch_id}: task_id {task_id!r} is not in the canonical catalog")
            else:
                catalog_tier = catalog[task_id]
                declared = str(branch.get("risk_tier", "")).strip() or catalog_tier
                if rank(declared) < rank(catalog_tier):
                    errors.append(
                        f"{branch_id}: declared risk {declared} is below the catalog floor {catalog_tier}; "
                        "a branch may not downgrade its own tier"
                    )
                if rank(catalog_tier) > rank(plan_ceiling):
                    errors.append(
                        f"{branch_id}: {task_id} is {catalog_tier}, above the {plan_ceiling} delegation ceiling. "
                        "A delegated branch holds no approval authority; it must stop at a proposal and return it."
                    )

        if not str(branch.get("owner", "")).strip():
            warnings.append(f"{branch_id}: no owner named for the returned result")

        depends_on = branch.get("depends_on")
        depends_on = [str(item) for item in depends_on] if isinstance(depends_on, list) else []
        in_wave = [item for item in depends_on if item in {str(other.get("branch_id", "")) for other in branches if isinstance(other, dict)}]
        if in_wave:
            errors.append(
                f"{branch_id}: depends on {', '.join(in_wave)} inside the same wave; "
                "a dependency makes this sequential, not parallel"
            )

        branch_writes = branch.get("write_paths")
        branch_writes = [normalize(item) for item in branch_writes] if isinstance(branch_writes, list) else []
        if not branch_writes:
            warnings.append(f"{branch_id}: declares no write_paths; an undeclared write cannot be isolated")
        writes[branch_id] = branch_writes

        branch_reads = branch.get("read_paths")
        reads[branch_id] = [normalize(item) for item in branch_reads] if isinstance(branch_reads, list) else []

        if not branch.get("expected_artifacts"):
            errors.append(f"{branch_id}: no expected_artifacts; there is nothing to verify on return")
        if not branch.get("evidence_required"):
            errors.append(f"{branch_id}: no evidence_required; the merge would rest on the branch's own narrative")
        if not branch.get("token_budget"):
            warnings.append(f"{branch_id}: no token_budget; an unbounded branch cannot be scheduled honestly")

    collisions: list[str] = []
    ordered = sorted(writes)
    for position, left in enumerate(ordered):
        for right in ordered[position + 1:]:
            for left_path in writes[left]:
                for right_path in writes[right]:
                    if overlaps(left_path, right_path):
                        collisions.append(f"{left} and {right} both write {left_path} / {right_path}")
    for collision in collisions:
        errors.append(f"write collision: {collision}; last writer would win silently")

    hazards: list[str] = []
    for reader in ordered:
        for writer in ordered:
            if reader == writer:
                continue
            for read_path in reads[reader]:
                for write_path in writes[writer]:
                    if overlaps(read_path, write_path):
                        hazards.append(f"{reader} reads {read_path} while {writer} writes {write_path}")
    for hazard in sorted(set(hazards)):
        warnings.append(f"read-write hazard: {hazard}; the reader may see a half-written state")

    merge = plan.get("merge")
    if not isinstance(merge, dict):
        errors.append("missing merge policy; fan-in needs a deterministic order and a conflict rule")
    else:
        order = merge.get("order")
        if not isinstance(order, list) or not order:
            errors.append("merge.order must list branch ids in the order results are folded in")
        else:
            unknown = [item for item in order if item not in branch_ids]
            missing = [item for item in sorted(branch_ids) if item not in order]
            if unknown:
                errors.append(f"merge.order names unknown branch(es): {', '.join(str(item) for item in unknown)}")
            if missing:
                errors.append(f"merge.order omits branch(es): {', '.join(missing)}")
        if str(merge.get("on_conflict", "")).strip().lower() not in {"conflict-register", "block", "escalate"}:
            errors.append(
                "merge.on_conflict must be conflict-register, block or escalate; "
                "contradictory branch results are never averaged or silently overwritten"
            )
        if str(merge.get("on_branch_failure", "")).strip().lower() not in {"partial", "block", "retry-then-block"}:
            errors.append(
                "merge.on_branch_failure must be partial, block or retry-then-block; "
                "a failed branch never silently reduces scope to keep the run green"
            )

    summary = {
        "branches": len(branches),
        "ceiling": plan_ceiling,
        "write_collisions": len(collisions),
        "read_write_hazards": len(set(hazards)),
        "catalog_checked": catalog is not None,
    }
    return errors, warnings, summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("plan", type=Path, help="branch plan as JSON")
    parser.add_argument("--task-catalog", type=Path, help="canonical task-catalog.json; without it task ids and risk floors are unchecked")
    parser.add_argument("--ceiling", default=DELEGABLE_CEILING, choices=RISK_ORDER, help=f"highest risk tier a branch may execute (default {DELEGABLE_CEILING})")
    parser.add_argument("--strict", action="store_true", help="treat warnings as failures")
    args = parser.parse_args()

    if not args.plan.is_file():
        print(f"ERROR: no such file: {args.plan}")
        sys.exit(2)
    try:
        plan = json.loads(args.plan.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"ERROR: invalid JSON: {exc}")
        sys.exit(2)

    catalog = None
    if args.task_catalog:
        if not args.task_catalog.is_file():
            print(f"ERROR: no such task catalog: {args.task_catalog}")
            sys.exit(2)
        try:
            catalog = load_catalog(args.task_catalog)
        except (json.JSONDecodeError, ValueError) as exc:
            print(f"ERROR: could not read task catalog: {exc}")
            sys.exit(2)

    errors, warnings, summary = validate(plan, catalog, args.ceiling)
    for error in errors:
        print(f"ERROR: {error}")
    for warning in warnings:
        print(f"WARNING: {warning}")

    if summary:
        print(
            f"branches: {summary['branches']}  delegation ceiling: {summary['ceiling']}  "
            f"write collisions: {summary['write_collisions']}  read-write hazards: {summary['read_write_hazards']}"
        )
    if catalog is None:
        print("NOTE: no task catalog supplied; task ids and risk floors were NOT verified. This is incomplete, not a pass.")
        if not errors:
            sys.exit(2)

    if errors:
        print(f"FAILED: {len(errors)} plan error(s); do not dispatch")
        sys.exit(1)
    if warnings and args.strict:
        print(f"FAILED: {len(warnings)} warning(s) under --strict")
        sys.exit(1)
    if warnings:
        print(f"PASS WITH WARNINGS: {len(warnings)} item(s) to resolve before dispatch")
        sys.exit(0)
    print("PASS: branches are isolated, within the delegation ceiling, and the merge policy is explicit")


if __name__ == "__main__":
    main()
