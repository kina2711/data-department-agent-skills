#!/usr/bin/env python3
"""Which workflows run under a declared harness, and which run under none.

A harness is the boundary a run is supposed to stay inside: what it may select, what it is
grounded on, where it stops, and who it hands to. Declaring one for a flow is cheap; the thing
that is not cheap is knowing which flows have one, because a flow without a harness looks exactly
like a flow with a good one until something goes wrong.

This reports coverage rather than asserting it. Generating a harness for every workflow would make
the number 100% and mean nothing — a declaration nobody wrote is not a boundary anybody chose,
which is the same failure as a pass rate over cases nobody wrote. So the shipped skill workflows
are counted separately from the authored ones, and the report says plainly that a template is not
a harnessed flow.

Standard library only.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS = ROOT / "workflows"
HARNESSES = ROOT / "harnesses"
SKILLS = ROOT / "skills"


def load(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", type=Path, help="write the report as JSON")
    ap.add_argument("--require", nargs="*", default=[],
                    help="workflow ids that must have a harness; exit 1 if any does not")
    args = ap.parse_args()

    skill_names = {d.name for d in SKILLS.iterdir() if d.is_dir()} if SKILLS.is_dir() else set()

    harnesses = {}
    for path in sorted(HARNESSES.glob("*.harness.json")) if HARNESSES.is_dir() else []:
        doc = load(path)
        if doc.get("harness_id"):
            harnesses[doc["harness_id"]] = doc

    rows = []
    for path in sorted(WORKFLOWS.glob("*.workflow.json")):
        doc = load(path)
        wid = doc.get("workflow_id") or path.stem.replace(".workflow", "")
        tasks = [t.get("task_id") for t in doc.get("tasks", []) if t.get("task_id")]
        h = harnesses.get(wid)
        # A per-skill workflow is generated scaffolding for one role; an authored flow is one
        # somebody composed. Only the second kind is a candidate for a harness of its own.
        # Generated ids carry the execution path as a suffix — analytics-engineering-standard-path —
        # so a bare name comparison classified all thirty-five as authored and reported 1/35 for a
        # gap that is really 1/2.
        base = wid
        for suffix in ("-standard-path", "-fast-path", "-controlled-path"):
            if base.endswith(suffix):
                base = base[: -len(suffix)]
                break
        kind = "template" if base in skill_names else "authored"
        covered = set(h["scope"]["tasks_in"]) if h else set()
        missing = sorted(set(tasks) - covered) if h else []
        rows.append({
            "workflow": wid, "kind": kind, "tasks": len(tasks),
            "harness": h["harness_id"] if h else None,
            "harness_status": (h or {}).get("status"),
            "evaluated": bool((h or {}).get("evaluation", {}).get("cases_total")),
            "tasks_outside_harness": missing,
        })

    authored = [r for r in rows if r["kind"] == "authored"]
    with_h = [r for r in authored if r["harness"]]
    orphans = [h for h in harnesses if h not in {r["workflow"] for r in rows}]

    print(f"workflows: {len(rows)}  ({len(authored)} authored, {len(rows) - len(authored)} per-skill templates)")
    print(f"authored flows with a declared harness: {len(with_h)}/{len(authored)}")
    print(f"harness declarations: {len(harnesses)}"
          + (f"  · not matching any workflow: {', '.join(orphans)}" if orphans else ""))
    print()
    for r in authored:
        mark = "✓" if r["harness"] else "—"
        note = ""
        if r["harness"]:
            note = f"  status={r['harness_status']}"
            note += "  evaluated" if r["evaluated"] else "  UNEVALUATED"
            if r["tasks_outside_harness"]:
                note += f"  · {len(r['tasks_outside_harness'])} task(s) outside its scope"
        print(f"  {mark} {r['workflow']:34s} {r['tasks']:3d} task{note}")

    if rows and len(authored) != len(rows):
        print(f"\nThe {len(rows) - len(authored)} per-skill workflows are templates with no owner "
              "and no harness by design. Counting them as covered would report a boundary nobody drew.")

    if args.json:
        args.json.write_text(json.dumps({"workflows": rows, "harnesses": sorted(harnesses)},
                                        ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"\nwrote {args.json}")

    failed = [w for w in args.require if w not in harnesses]
    if failed:
        for w in failed:
            print(f"ERROR: {w} has no harness declaration", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
