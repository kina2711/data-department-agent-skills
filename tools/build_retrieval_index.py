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



# A whole contract is 60 lines and a whole standard can be 50; returning either as a "result"
# makes the reader do the finding. Sections are the unit a retrieval answer should be.
SECTION_RE = re.compile(r"^(#{2,3})\s+(.+?)\s*$", re.M)


def sections_of(path: Path, kind: str, skill: str, owner_id: str) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    marks = list(SECTION_RE.finditer(text))
    out: list[dict] = []
    for i, m in enumerate(marks):
        start = m.end()
        end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        body = text[start:end].strip()
        if len(body) < 40:
            continue
        heading = m.group(2)
        out.append({
            "kind": kind,
            "skill": skill,
            "owner": owner_id,
            "heading": heading,
            "anchor": re.sub(r"[^a-z0-9]+", "-", heading.lower()).strip("-"),
            "excerpt": body[:320],
            "keywords": keywords(heading, body[:600]),
        })
    return out



# Which real systems a skill touches is already recorded: its adapter packs name them. That turns
# "declare a tool surface" from an abstract instruction into a concrete list per skill.
def tool_surfaces() -> dict[str, dict]:
    surfaces: dict[str, dict] = {}
    for directory in sorted(SKILLS.glob("*/references")):
        skill = directory.parent.name
        platforms = sorted(p.stem.removeprefix("adapter-") for p in directory.glob("adapter-*.md"))
        if not platforms:
            continue
        outward = sorted(
            t.stem for t in (directory / "tasks").glob("*.md")
            if any(w in t.stem.split("-", 1)[1] for w in OUTWARD_WORDS)
        )
        surfaces[skill] = {
            "platforms": platforms,
            "outward_tasks": outward,
            "needs_declared_surface": bool(outward),
        }
    return surfaces


OUTWARD_WORDS = (
    "publish", "deploy", "send", "notify", "sync", "connector", "integrat",
    "provision", "access", "iam", "ticket", "export", "release", "onboard", "offboard",
)


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

    # Section-level passages, so a retrieval answer can point at "the Tests and evidence section
    # of task X" rather than at the whole file.
    passages: list[dict] = []
    for skill, ids in sorted(owned.items()):
        for task_id in sorted(ids):
            contract = SKILLS / skill / "references" / "tasks" / f"{task_id}.md"
            if contract.exists():
                passages.extend(sections_of(contract, "contract", skill, task_id))
    seen_ref: set[str] = set()
    for path in sorted(SKILLS.glob("*/references/*.md")):
        if path.name.startswith(("catalog-", "adapter-")) or path.name in seen_ref:
            continue
        seen_ref.add(path.name)
        passages.extend(sections_of(path, "standard", path.parent.parent.name, path.name))

    # Two thirds of contract sections are identical boilerplate — "Inputs and readiness" is the
    # same paragraph 832 times. Indexed separately they return 832 identical results for one
    # query, which is worse than not indexing them. One entry, listing every owner.
    merged: dict[str, dict] = {}
    for passage in passages:
        digest = hashlib.sha256((passage["heading"] + passage["excerpt"]).encode("utf-8")).hexdigest()[:16]
        entry = merged.get(digest)
        if entry is None:
            entry = dict(passage)
            entry["owners"] = []
            entry.pop("owner", None)
            merged[digest] = entry
        entry["owners"].append(passage["owner"])
    passages = []
    for entry in merged.values():
        entry["owners"].sort()
        entry["shared"] = len(entry["owners"]) > 1
        if entry["shared"]:
            # Boilerplate carries no retrieval signal beyond its heading; keep the entry, drop the
            # per-owner list past a handful so the index stays a lookup surface, not a transcript.
            entry["owner_count"] = len(entry["owners"])
            entry["owners"] = entry["owners"][:5]
        passages.append(entry)
    passages.sort(key=lambda x: (x["kind"], x["heading"]))

    return {
        "_": ("Retrieval surface over the suite's own contracts and standards. Generated by "
              "tools/build_retrieval_index.py; edit the source, never this file. A keyword match "
              "is a candidate, not an answer."),
        "task_count": len(tasks),
        "reference_count": len(references),
        "passage_count": len(passages),
        "skills": sorted(owned),
        "guides": guides,
        "tool_surfaces": tool_surfaces(),
        "tasks": tasks,
        "references": references,
        "passages": passages,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="fail if the index is out of date")
    args = parser.parse_args()

    index = build()
    rendered = json.dumps(index, ensure_ascii=False, indent=1) + "\n"
    current = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
    print(f"tasks: {index['task_count']}  references: {index['reference_count']}  "
          f"passages: {index['passage_count']}  skills: {len(index['skills'])}  "
          f"tool surfaces: {len(index['tool_surfaces'])}")
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
