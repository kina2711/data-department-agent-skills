#!/usr/bin/env python3
"""Generate one executable workflow manifest per skill from the map's authored phases.

The dependency edges are not invented. `docs/skill-map.md` already groups each skill's tasks into
ordered phases written by hand — P0 before P1 before P2 — and that ordering is the only structure
in the repository that says which work comes first. This turns it into manifests the canvas can
open and `validate_workflow.py` can check.

What the edges mean is narrower than it looks, and the manifest says so in its objective: an edge
encodes *phase precedence*, not a task-level prerequisite. Each phase has an anchor, the first
task the map lists for it; the phase's other tasks depend on that anchor, and the next phase's
anchor depends on the previous one. Two tasks inside one phase are peers with no claim about
their relative order, because the map does not make one.

It builds a starting graph. It cannot know which tasks a particular engagement needs, and a real
workflow is this file with the irrelevant tasks deleted.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "docs" / "skill-map.md"
SKILLS = ROOT / "skills"
CATALOG = ROOT / "task-catalog.json"
OUT_DIR = ROOT / "workflows"

RISK_ORDER = ["R0-light", "R1-reviewed", "R2-standard", "R3-controlled", "R4-critical"]

# Within one authored phase the suite's own lifecycle semantics still order the work: you analyse
# before you specify, specify before you build, and assure or release after. Ordering by profile
# and then by catalog verb turns two or three phases into ten-odd real stages without inventing a
# single edge — every rank below comes from a field the catalog already carries.
LIFECYCLE_ORDER = [
    "advisory-analysis", "design-specification", "learning", "career-coaching",
    "career-development", "onboarding", "hiring", "build-change",
    "governance-assurance", "production-release", "incident-recovery",
]
GROUP_ORDER = ["plan-design", "build-deliver", "test-assure", "operate-improve"]


def catalog_groups() -> dict[str, str]:
    """Task to its verb group, read from the routing catalogs each skill ships."""
    groups: dict[str, str] = {}
    for path in SKILLS.glob("*/references/catalog-*.md"):
        shard = path.stem.removeprefix("catalog-")
        base = next((g for g in GROUP_ORDER if shard.startswith(g)), shard)
        for task_id in re.findall(r"\(tasks/([a-z0-9-]+)\.md\)", path.read_text(encoding="utf-8")):
            groups[task_id] = base
    return groups


def stage_rank(task: dict, group: str) -> tuple[int, int]:
    life = task.get("lifecycle_profile", "")
    return (
        LIFECYCLE_ORDER.index(life) if life in LIFECYCLE_ORDER else len(LIFECYCLE_ORDER),
        GROUP_ORDER.index(group) if group in GROUP_ORDER else len(GROUP_ORDER),
    )


def parse_phases() -> dict[str, list[dict]]:
    """Skill-map section title to its ordered phases and the tasks each lists."""
    text = MAP.read_text(encoding="utf-8")
    # Section numbers in the map are not uniform — "4A." and an unnumbered heading both appear —
    # so the number is optional. A strict pattern silently merges a section into its predecessor.
    parts = re.split(r"^## (?:[0-9]+[A-Za-z]?\.\s*)?(.+)$", text, flags=re.M)
    sections: dict[str, list[dict]] = {}
    for i in range(1, len(parts), 2):
        title, body = parts[i].strip(), parts[i + 1]
        phases: list[dict] = []
        current = None
        for line in body.splitlines():
            heading = re.match(r"^### (P\d)\s*—\s*(.+)$", line)
            if heading:
                current = {"phase": heading.group(1), "label": heading.group(2).strip(), "tasks": []}
                phases.append(current)
                continue
            task = re.match(r"^- `([a-z0-9-]+)`", line)
            if not task:
                continue
            if current is None:
                current = {"phase": "P0", "label": "", "tasks": []}
                phases.append(current)
            current["tasks"].append(task.group(1))
        if phases:
            sections[title] = phases
    return sections


def tasks_by_skill() -> dict[str, set[str]]:
    """A task belongs to the skill that ships its contract, not to its id prefix."""
    owned: dict[str, set[str]] = {}
    for directory in sorted(SKILLS.glob("*/references/tasks")):
        skill = directory.parent.parent.name
        owned[skill] = {p.stem for p in directory.glob("*.md")}
    return owned


def build(skill: str, phases: list[dict], catalog: dict[str, dict], owned: set[str],
          groups: dict[str, str]) -> dict | None:
    """One manifest for one skill. Returns None when the skill owns nothing the map lists."""
    kept = [
        {**phase, "tasks": [t for t in phase["tasks"] if t in owned and t in catalog]}
        for phase in phases
    ]
    kept = [p for p in kept if p["tasks"]]
    if not kept:
        return None

    # Stages are (phase, lifecycle rank, verb rank). Tasks sharing a stage are peers; the map and
    # the catalog both decline to order them, so neither does this.
    stages: list[dict] = []
    for phase in kept:
        by_rank: dict[tuple[int, int], list[str]] = {}
        for task_id in phase["tasks"]:
            rank = stage_rank(catalog[task_id], groups.get(task_id, ""))
            by_rank.setdefault(rank, []).append(task_id)
        for rank in sorted(by_rank):
            stages.append({
                "phase": phase["phase"],
                "label": phase["label"],
                "lifecycle": LIFECYCLE_ORDER[rank[0]] if rank[0] < len(LIFECYCLE_ORDER) else "other",
                "group": GROUP_ORDER[rank[1]] if rank[1] < len(GROUP_ORDER) else "other",
                "tasks": by_rank[rank],
            })

    tasks: list[dict] = []
    previous_anchor: str | None = None
    highest = 0
    for stage in stages:
        anchor = stage["tasks"][0]
        for index, task_id in enumerate(stage["tasks"]):
            risk = catalog[task_id]["risk_tier"]
            highest = max(highest, RISK_ORDER.index(risk))
            depends = ([previous_anchor] if previous_anchor else []) if index == 0 else [anchor]
            tasks.append({
                "task_id": task_id,
                "owner": "",
                "depends_on": depends,
                "status": "planned",
                "risk_tier": risk,
                "artifact_version": "",
                "artifact_sha256": "",
                "evidence_refs": [],
                "approval_refs": [],
            })
        previous_anchor = anchor

    # Where a stage's risk exceeds everything before it, the work crosses a control boundary and
    # needs authority that earlier stages did not. The schema has nowhere to store a gate node, so
    # the objective names them and the canvas derives the markers from the same risk data.
    gates: list[str] = []
    seen_risk = 0
    for stage in stages:
        top = max(RISK_ORDER.index(catalog[t]["risk_tier"]) for t in stage["tasks"])
        if top > seen_risk:
            seen_risk = top
            if RISK_ORDER[top] in {"R2-standard", "R3-controlled", "R4-critical"}:
                gates.append(f"{stage['tasks'][0]} enters {RISK_ORDER[top]}")

    trail = " → ".join(f"{s['phase']}/{s['lifecycle']}/{s['group']}" for s in stages)
    return {
        "workflow_id": f"{skill}-standard-path",
        "version": "2.0.0",
        "objective": (
            f"Standard path through {skill}, {len(stages)} stages over {len(tasks)} tasks. "
            f"Stages come from the phases in docs/skill-map.md ordered by lifecycle profile and "
            f"then by catalog verb: {trail}. An edge encodes stage precedence, not a task-level "
            f"prerequisite — tasks inside one stage are peers, because nothing in the suite orders "
            f"them. Control boundaries, where risk first rises and authority beyond the previous "
            f"stage is required: {'; '.join(gates) if gates else 'none'}. "
            f"Delete what this engagement does not need before running it."
        ),
        "status": "draft",
        "workflow_risk_tier": RISK_ORDER[highest],
        "current_task_id": stages[0]["tasks"][0],
        "tasks": tasks,
        "transitions": [],
        "claims": [],
        "updated_at": "",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="fail if any file would change")
    args = parser.parse_args()

    catalog = {t["id"]: t for t in json.loads(CATALOG.read_text(encoding="utf-8"))}
    owned = tasks_by_skill()
    phases = parse_phases()
    groups = catalog_groups()

    # Map section titles are prose; resolve them to skills through the tasks they list.
    section_for_skill: dict[str, list[dict]] = {}
    for title, section_phases in phases.items():
        listed = {t for p in section_phases for t in p["tasks"]}
        best, score = None, 0
        for skill, ids in owned.items():
            overlap = len(listed & ids)
            if overlap > score:
                best, score = skill, overlap
        if best:
            section_for_skill.setdefault(best, []).extend(section_phases)

    OUT_DIR.mkdir(exist_ok=True)
    written, changed, skipped = 0, [], []
    covered_tasks: set[str] = set()
    for skill in sorted(owned):
        manifest = build(skill, section_for_skill.get(skill, []), catalog, owned[skill], groups)
        if manifest is None:
            skipped.append(skill)
            continue
        covered_tasks.update(t["task_id"] for t in manifest["tasks"])
        path = OUT_DIR / f"{skill}.workflow.json"
        rendered = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
        if path.exists() and path.read_text(encoding="utf-8") == rendered:
            written += 1
            continue
        changed.append(path.name)
        if not args.check:
            path.write_text(rendered, encoding="utf-8")
        written += 1

    uncovered = sorted({t for ids in owned.values() for t in ids} - covered_tasks)
    print(f"workflows: {written}  skills without map phases: {len(skipped)}  tasks not in any workflow: {len(uncovered)}")
    if skipped:
        print("  no phases: " + ", ".join(skipped))
    if uncovered:
        print(f"  uncovered example: {', '.join(uncovered[:5])}")
    if args.check and changed:
        print("FAILED: out of date: " + ", ".join(changed))
        sys.exit(1)
    if changed:
        print("wrote: " + ", ".join(changed[:6]) + (" …" if len(changed) > 6 else ""))


if __name__ == "__main__":
    main()
