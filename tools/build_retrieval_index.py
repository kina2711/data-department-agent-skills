#!/usr/bin/env python3
"""Build a retrieval index over the suite's own contracts and standards.

The suite routes by reading catalog shards in order. That works for an agent walking the
hierarchy and works badly for anything else: an app searching 832 tasks, an external agent asking
which contract covers a situation, or a person who knows the deliverable but not the role. Those
readers need one file they can search, not a tree they must walk.

Each entry carries what a retrieval decision needs — the deliverable, the Vietnamese goal, the
risk and model tier, the stage the workflow places it in, and the standards its contract routes
to — plus a keyword set built from the id and goal. It is a lookup surface over material that
already exists; it invents nothing and is regenerated rather than edited.

It indexes structure and wording. It cannot rank by relevance, and a keyword match is a candidate
rather than an answer.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
OUT = ROOT / "docs" / "retrieval-index.json"

# Words too common across a data suite to narrow anything down.
STOPWORDS = set(
    """data and the for with from into that this than then when what which their there here
    một các và của cho theo khi thì với từ trong ra vào là được có không những này đó nếu
    build create design define make run write read use""".split()
)


def owned_tasks() -> dict[str, set[str]]:
    return {
        d.parent.parent.name: {p.stem for p in d.glob("*.md")}
        for d in SKILLS.glob("*/references/tasks")
    }


def contract_references(path: Path) -> list[str]:
    """The standards a contract tells its reader to load."""
    text = path.read_text(encoding="utf-8")
    return sorted({m for m in re.findall(r"\]\(\.\./([a-z0-9-]+\.md)\)", text)})


def workflow_stages() -> dict[str, dict]:
    """Where each task sits in its skill's generated workflow, when one covers it."""
    placement: dict[str, dict] = {}
    for path in sorted((ROOT / "workflows").glob("*.workflow.json")):
        try:
            manifest = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        order = {t["task_id"]: i for i, t in enumerate(manifest.get("tasks", []))}
        for task in manifest.get("tasks", []):
            placement[task["task_id"]] = {
                "workflow": manifest.get("workflow_id", ""),
                "position": order[task["task_id"]],
                "depends_on": task.get("depends_on", []),
            }
    return placement


def keywords(*parts: str) -> list[str]:
    words = set()
    for part in parts:
        for word in re.findall(r"[\wÀ-ỹ]{3,}", part.lower()):
            if word not in STOPWORDS and not word.isdigit():
                words.add(word)
    return sorted(words)


def build() -> dict:
    catalog = {t["id"]: t for t in json.loads((ROOT / "task-catalog.json").read_text(encoding="utf-8"))}
    owned = owned_tasks()
    placement = workflow_stages()

    guides, jobs = {}, []
    for name, key, target in [("huong-dan-skill.vi.json", "skills", "guides"),
                              ("cong-viec.vi.json", "cong_viec", "jobs")]:
        try:
            doc = json.loads((ROOT / "docs" / name).read_text(encoding="utf-8"))
            if target == "guides":
                guides = doc.get(key, {})
            else:
                jobs = doc.get(key, [])
        except (OSError, json.JSONDecodeError):
            pass

    jobs_by_task: dict[str, list[str]] = {}
    for job in jobs:
        jobs_by_task.setdefault(job.get("task_id", ""), []).append(job.get("ten", ""))

    tasks = []
    for skill, ids in sorted(owned.items()):
        for task_id in sorted(ids):
            entry = catalog.get(task_id)
            if not entry:
                continue
            contract = SKILLS / skill / "references" / "tasks" / f"{task_id}.md"
            tasks.append({
                "id": task_id,
                "skill": skill,
                "goal": entry.get("goal", ""),
                "output": entry.get("output", ""),
                "lifecycle_profile": entry.get("lifecycle_profile", ""),
                "risk_tier": entry.get("risk_tier", ""),
                "model_tier": entry.get("model_tier", ""),
                "criticality": entry.get("criticality", ""),
                "standards": contract_references(contract),
                "workflow": placement.get(task_id, {}),
                "preset_jobs": jobs_by_task.get(task_id, []),
                "keywords": keywords(task_id.replace("-", " "), entry.get("goal", ""), entry.get("output", "")),
            })

    # A shared standard ships into every skill that needs it, so the same file appears dozens of
    # times on disk. Retrieval wants one entry per distinct standard, listing where it is loadable.
    by_content: dict[str, dict] = {}
    for path in sorted(SKILLS.glob("*/references/*.md")):
        if path.name.startswith(("catalog-", "adapter-")):
            continue
        text = path.read_text(encoding="utf-8")
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
        head = text.split("\n\n", 2)
        title = head[0].lstrip("# ").strip() if head else path.stem
        summary = head[1].strip() if len(head) > 1 else ""
        entry = by_content.setdefault(digest, {
            "file": path.name,
            "title": title,
            "summary": summary[:400],
            "shipped_to": [],
            "keywords": keywords(title, summary),
        })
        entry["shipped_to"].append(path.parent.parent.name)
    references = sorted(by_content.values(), key=lambda r: (r["file"], r["title"]))
    for entry in references:
        entry["shipped_to"].sort()
        entry["shared"] = len(entry["shipped_to"]) > 1

    return {
        "_": ("Retrieval surface over the suite's own contracts and standards. Generated by "
              "tools/build_retrieval_index.py; edit the source, never this file. A keyword match "
              "is a candidate, not an answer."),
        "task_count": len(tasks),
        "reference_count": len(references),
        "skills": sorted(owned),
        "guides": guides,
        "tasks": tasks,
        "references": references,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="fail if the index is out of date")
    args = parser.parse_args()

    index = build()
    rendered = json.dumps(index, ensure_ascii=False, indent=1) + "\n"
    current = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
    print(f"tasks: {index['task_count']}  references: {index['reference_count']}  skills: {len(index['skills'])}")
    if rendered == current:
        return
    if args.check:
        print("FAILED: retrieval index is out of date; run tools/build_retrieval_index.py")
        sys.exit(1)
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(rendered, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
