#!/usr/bin/env python3
"""Write skills/llms.txt: one compact page that routes without opening 33 SKILL.md files.

The suite ships 33 skills and 868 task contracts. Choosing among them by reading them is the
expensive way, and the expense is paid on every request. This index is the cheap layer: what each
skill owns, what it produces, and where it hands off, in a file small enough to load whole.

Every line comes from authored data already in the suite -- descriptions from SKILL.md, task
counts and deliverables from the atlas. Nothing here is a keyword somebody guessed at, because a
routing index that invents its own triggers routes by its own invention.

Honest about what it saves. Claude Code already puts every skill description in context, so this
buys nothing there for picking a skill; it earns its place choosing among the tasks inside one,
and in harnesses that do not preload descriptions at all.

Standard library only.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ATLAS = ROOT / "docs" / "skill-atlas.json"
OUT = ROOT / "skills" / "llms.txt"

# A deliverable naming its own skill adds nothing to a line already under that skill's heading.
STOP = {"plan", "record", "report", "review", "decision", "package", "note", "spec"}


def purpose(description: str) -> str:
    """The first sentence, which is where the authored description states what the skill is for."""
    first = re.split(r"(?<=[.!?])\s+", description.strip())[0]
    return first.rstrip(".")


def handoff(description: str) -> str:
    """The authored 'Route X to Y' clause, when the description carries one."""
    for sentence in re.split(r"(?<=[.!?])\s+", description):
        if re.search(r"\bRoute\b.*\bto\b", sentence):
            return sentence.strip()
    return ""


def deliverables(skill: dict, limit: int = 6) -> list[str]:
    """The most common distinct outputs, which is what a request actually names."""
    counts: Counter[str] = Counter()
    for shard in skill.get("shards", []):
        for task in shard.get("tasks", []):
            out = str(task.get("output", "")).strip().lower()
            if out and out not in STOP:
                counts[out] += 1
    return [name for name, _ in counts.most_common(limit)]


def render(atlas: dict) -> str:
    lines = [
        "# Data Department Agent Skills — routing index",
        "",
        f"{atlas['skill_count']} skills, {atlas['task_count']} atomic task contracts, "
        f"{len(atlas['waves'])} waves. Suite version in `.claude-plugin/plugin.json`.",
        "",
        "Read this to pick a skill and narrow to a task group. Then open that skill's SKILL.md and",
        "the one catalog shard you need — never the whole catalog. Selection is by primary",
        "deliverable, not by job title: the work standing in front of the request decides the owner,",
        "not the noun the request ends with.",
        "",
        "Ambiguous, multi-role, or a request to resume or hand over work goes to",
        "`data-department-orchestrator` first.",
        "",
    ]
    for wave in atlas["waves"]:
        skills = wave.get("skills") or []
        if not skills:
            continue
        lines.append(f"## {wave['wave']} — {wave['title']}")
        lines.append("")
        for skill in sorted(skills, key=lambda s: s["skill"]):
            shards = ", ".join(
                f"{s['shard']} ({s['task_count']})" for s in skill.get("shards", [])
            )
            lines.append(f"{skill['skill']}  ·  {skill['task_count']} tasks  ·  max {skill['highest_risk']}")
            lines.append(f"  {purpose(skill['description'])}.")
            produces = deliverables(skill)
            if produces:
                lines.append(f"  Produces: {'; '.join(produces)}.")
            if shards:
                lines.append(f"  Task groups: {shards}.")
            route = handoff(skill["description"])
            if route:
                lines.append(f"  {route}")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="fail when the file on disk is stale")
    args = ap.parse_args()

    if not ATLAS.exists():
        print(f"missing {ATLAS.relative_to(ROOT)}; run tools/build_skill_atlas.py first", file=sys.stderr)
        return 2
    text = render(json.loads(ATLAS.read_text(encoding="utf-8")))

    if args.check:
        current = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if current != text:
            print(f"{OUT.relative_to(ROOT)} is stale; regenerate with tools/build_skill_index.py", file=sys.stderr)
            return 1
        print(f"{OUT.relative_to(ROOT)} is current")
        return 0

    OUT.write_text(text, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}  ({len(text.encode('utf-8')) / 1024:.1f} KB, {len(text.splitlines())} lines)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
