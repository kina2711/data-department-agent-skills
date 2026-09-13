#!/usr/bin/env python3
"""Check an agent harness declaration against the standard it claims to follow.

A harness is a boundary written down, and a boundary nobody checks is a boundary that drifts. The
faults worth catching are the ones that make a harness look complete while saying nothing:

- a scope that lists what is in and never what is deliberately left out, which is the absence of a
  scope wearing the shape of one;
- a task id that does not exist in the catalog, so the boundary names work nobody can run;
- an evaluation score attached to no version, no date and no case count — the number that makes
  "it works" look measured when it was asserted;
- grounding with no version pinned, which is a harness that cannot say what it was working from;
- a handover with a blast radius nobody stated, given to a recipient who then has to infer it.

It reads the declaration and the catalog. It cannot tell whether the harness is a good idea, only
whether it says what a harness has to say. Standard library only.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CATALOG = ROOT / "task-catalog.json"

REQUIRED_TOP = ["harness_id", "role", "version", "scope", "grounding", "tool_surface_ref",
                "guardrails", "evaluation", "environment", "reproducible", "handover", "status"]
RISK_ORDER = ["R0-light", "R1-reviewed", "R2-standard", "R3-controlled", "R4-critical"]


def load_catalog() -> set[str]:
    if not CATALOG.exists():
        return set()
    return {t["id"] for t in json.loads(CATALOG.read_text(encoding="utf-8"))}


def check(doc: dict, known: set[str], strict: bool) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    for key in REQUIRED_TOP:
        if key not in doc:
            errors.append(f"missing required field: {key}")
    if errors:
        return errors, warnings

    scope = doc["scope"] or {}
    tasks_in = [t for t in (scope.get("tasks_in") or []) if t]
    tasks_out = [t for t in (scope.get("tasks_out") or []) if t]
    if not tasks_in:
        errors.append("scope.tasks_in is empty; a harness that selects anything has no scope")
    if not tasks_out:
        errors.append('scope.tasks_out is empty; "everything the skill offers" is the absence of a '
                      "scope, not a scope")
    if tasks_out and not str(scope.get("out_reason") or "").strip():
        errors.append("scope.out_reason is empty; an exclusion without a reason cannot be reviewed")
    if known:
        for task in tasks_in + tasks_out:
            if task not in known:
                errors.append(f"scope names a task the catalog does not have: {task}")
    overlap = sorted(set(tasks_in) & set(tasks_out))
    if overlap:
        errors.append(f"tasks both in and out of scope: {', '.join(overlap)}")

    grounding = doc.get("grounding") or []
    if not grounding:
        errors.append("grounding is empty; an agent grounded on whatever was current is not reproducible")
    for i, g in enumerate(grounding):
        if not str(g.get("source") or "").strip():
            errors.append(f"grounding[{i}] has no source")
        if not str(g.get("version") or "").strip():
            errors.append(f"grounding[{i}] pins no version: {g.get('source', '?')}")

    guards = doc.get("guardrails") or {}
    tier = str(guards.get("stops_at_risk_tier") or "")
    if tier not in RISK_ORDER:
        errors.append(f"guardrails.stops_at_risk_tier is not a known tier: {tier or '(empty)'}")
    if not (guards.get("gates_requiring_authority") or []):
        warnings.append("guardrails.gates_requiring_authority is empty; a harness that stops for "
                        "nothing has named no gate")

    ev = doc.get("evaluation") or {}
    score = float(ev.get("score") or 0)
    total = int(ev.get("cases_total") or 0)
    passed = int(ev.get("cases_passed") or 0)
    if score and not str(ev.get("score_is_for_version") or "").strip():
        errors.append("evaluation.score is set but score_is_for_version is empty; a score attached "
                      "to a version nobody can reconstruct is decoration")
    if score and not str(ev.get("run_at") or "").strip():
        errors.append("evaluation.score is set but run_at is empty")
    if total and passed > total:
        errors.append(f"evaluation.cases_passed {passed} exceeds cases_total {total}")
    if score and not total:
        errors.append("evaluation.score is set with cases_total 0; a rate over no cases is not a rate")
    if not score and not total:
        warnings.append("evaluation has not run; the harness is unmeasured, which is honest only "
                        'while nothing claims otherwise — "it works" here is an opinion')

    hand = doc.get("handover") or {}
    if not str(hand.get("blast_radius_stated") or "").strip():
        errors.append("handover.blast_radius_stated is empty; a recipient who has to infer the "
                      "blast radius has been given a risk, not a harness")
    if not (hand.get("may_write") or []):
        warnings.append("handover.may_write is empty; state it even when the answer is nothing")

    if doc.get("status") == "active":
        if not str(doc.get("owner") or "").strip():
            errors.append("status is active with no owner; an unowned harness in production is a "
                          "set of permissions nobody is watching")
        if not total:
            errors.append("status is active with no evaluation run")
        repro = doc.get("reproducible") or {}
        if not repro.get("inputs_pinned"):
            errors.append("status is active but reproducible.inputs_pinned is false")
    elif strict and not str(doc.get("owner") or "").strip():
        errors.append("--strict: owner is required")

    return errors, warnings


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("harness", type=Path)
    ap.add_argument("--strict", action="store_true", help="also require an owner on a draft")
    args = ap.parse_args()

    try:
        doc = json.loads(args.harness.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as err:
        print(f"cannot read {args.harness}: {err}", file=sys.stderr)
        return 2

    errors, warnings = check(doc, load_catalog(), args.strict)
    print(f"harness: {doc.get('harness_id', '(unnamed)')}  status: {doc.get('status', '?')}  "
          f"in: {len((doc.get('scope') or {}).get('tasks_in') or [])}  "
          f"out: {len((doc.get('scope') or {}).get('tasks_out') or [])}")
    for w in warnings:
        print(f"WARNING: {w}")
    for e in errors:
        print(f"ERROR: {e}")
    if errors:
        print(f"FAILED: {len(errors)} harness declaration error(s)")
        return 1
    print("PASS: scope, grounding, guardrails, evaluation and handover are declared as the standard requires")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
