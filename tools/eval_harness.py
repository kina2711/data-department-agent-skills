#!/usr/bin/env python3
"""List, validate and run the suite's evaluation cases, and report what they do not cover.

The cases already exist as data. What was missing was a way to ask anything of them: which cases
exist, what they assert, which pass, and — the question that matters most — which of the 838
contracts nothing checks at all. Smoke tests answered "did anything break"; they could not answer
"how much of this is actually evaluated".

Three subcommands, after lm-evaluation-harness: `ls` lists the suites and their coverage,
`validate` checks every case is well formed and points at things that exist, and `run` executes
them and scores each suite.

What it runs is deterministic: these cases assert facts about the catalog — that a task routes to
the group it should, that a lifecycle profile is what the contract says, that a confusion pair
names two real skills. That is worth automating and cheap to run. It is **not** a model
evaluation: nothing here sends a prompt anywhere, so a green score means the suite is internally
consistent, not that an agent routes well in practice. Behavioural evaluation needs a harness that
actually calls a model, and `--show-prompt` exists so the text such a harness would send can be
read before anyone pays to send it.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
CASES = ROOT / "evaluations"

SUITES = {
    "routing": ("routing-cases.yaml", "query routes to a skill and an ordered set of tasks"),
    "catalog": ("catalog-routing-cases.yaml", "task lands in the right verb catalog"),
    "confusion": ("confusion-pair-cases.yaml", "the right skill wins against a named rival"),
    "lifecycle": ("lifecycle-cases.yaml", "task carries the expected profile and execution path"),
    "contract": ("contract-cases.yaml", "contract shape holds"),
}


def load_cases(path: Path) -> list[dict]:
    """Read the case files without a YAML dependency; they are a flat, known shape."""
    cases: list[dict] = []
    current: dict | None = None
    key: str | None = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        if not line.strip() or line.strip().startswith("#"):
            continue
        start = re.match(r"^\s*-\s+id:\s*(.+)$", line)
        if start:
            current = {"id": start.group(1).strip().strip('"\'')}
            cases.append(current)
            key = None
            continue
        if current is None:
            continue
        field = re.match(r"^\s{4}([a-z_]+):\s*(.*)$", line)
        if field:
            key = field.group(1)
            value = field.group(2).strip()
            current[key] = value.strip('"\'') if value else []
            continue
        item = re.match(r"^\s{6,}-\s+(.*)$", line)
        if item and key:
            current.setdefault(key, [])
            if isinstance(current[key], list):
                current[key].append(item.group(1).strip().strip('"\''))
    return cases


def catalog() -> tuple[dict[str, dict], set[str], dict[str, str]]:
    entries = {t["id"]: t for t in json.loads((ROOT / "task-catalog.json").read_text(encoding="utf-8"))}
    skills = {d.name for d in SKILLS.iterdir() if d.is_dir()}
    group: dict[str, str] = {}
    for path in SKILLS.glob("*/references/catalog-*.md"):
        shard = path.stem.removeprefix("catalog-")
        for task_id in re.findall(r"\(tasks/([a-z0-9-]+)\.md\)", path.read_text(encoding="utf-8")):
            group[task_id] = shard
    return entries, skills, group


def check(case: dict, suite: str, entries: dict, skills: set[str], group: dict[str, str]) -> list[str]:
    """What this one case asserts, and which of those assertions fail."""
    problems: list[str] = []
    referenced = []
    for field in ("task", "expected_task"):
        if case.get(field):
            referenced.append(case[field])
    referenced += [t for t in (case.get("expected_tasks") or []) if t]
    for task_id in referenced:
        if task_id not in entries:
            problems.append(f"unknown task {task_id}")
    for field in ("expected_primary_skill", "rejected_skill"):
        if case.get(field) and case[field] not in skills:
            problems.append(f"unknown skill {case[field]}")
    if suite == "confusion" and case.get("expected_primary_skill") == case.get("rejected_skill"):
        problems.append("rival skill is the same as the winner")
    if suite == "catalog" and case.get("task") in entries:
        actual = group.get(case["task"], "")
        expected = case.get("expected_catalog", "")
        if actual != expected and not actual.startswith(f"{expected}-"):
            problems.append(f"catalog {actual or '(none)'} is not in the {expected} group")
    if suite == "lifecycle" and case.get("task") in entries:
        entry = entries[case["task"]]
        if case.get("expected_profile") and entry["lifecycle_profile"] != case["expected_profile"]:
            problems.append(f"profile {entry['lifecycle_profile']} != {case['expected_profile']}")
        if case.get("expected_path") and entry["execution_path"] != case["expected_path"]:
            problems.append(f"path {entry['execution_path']} != {case['expected_path']}")
    return problems


def coverage(entries: dict, all_cases: dict[str, list[dict]]) -> dict:
    """Which contracts and skills any case mentions — the number a pass rate cannot show."""
    seen_tasks: set[str] = set()
    seen_skills: set[str] = set()
    for cases in all_cases.values():
        for case in cases:
            for field in ("task", "expected_task"):
                if case.get(field):
                    seen_tasks.add(case[field])
            seen_tasks.update(t for t in (case.get("expected_tasks") or []) if t)
            for field in ("expected_primary_skill", "rejected_skill"):
                if case.get(field):
                    seen_skills.add(case[field])
    by_skill: dict[str, int] = defaultdict(int)
    for task_id in seen_tasks:
        entry = entries.get(task_id)
        if entry:
            by_skill[task_id.split("-", 1)[0]] += 1
    return {
        "tasks_covered": len(seen_tasks & set(entries)),
        "tasks_total": len(entries),
        "task_coverage": round(len(seen_tasks & set(entries)) / len(entries), 4) if entries else 0.0,
        "skills_named": len(seen_skills),
        "uncovered_sample": sorted(set(entries) - seen_tasks)[:10],
        "per_prefix": dict(sorted(by_skill.items())),
    }


def read_all() -> dict[str, list[dict]]:
    return {name: load_cases(CASES / f) for name, (f, _) in SUITES.items() if (CASES / f).exists()}


def cmd_ls(args: argparse.Namespace) -> int:
    entries, _, _ = catalog()
    all_cases = read_all()
    cov = coverage(entries, all_cases)
    for name, cases in all_cases.items():
        print(f"{name:11} {len(cases):4} cases  — {SUITES[name][1]}")
    print(f"\ntasks referenced by at least one case: {cov['tasks_covered']}/{cov['tasks_total']} "
          f"({cov['task_coverage']:.1%})")
    if cov["uncovered_sample"]:
        print("uncovered, first ten: " + ", ".join(cov["uncovered_sample"]))
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    entries, skills, group = catalog()
    all_cases = read_all()
    seen: set[str] = set()
    problems = 0
    for name, cases in all_cases.items():
        for case in cases:
            if case["id"] in seen:
                print(f"ERROR: duplicate case id {case['id']}")
                problems += 1
            seen.add(case["id"])
            for issue in check(case, name, entries, skills, group):
                print(f"ERROR: {name}/{case['id']}: {issue}")
                problems += 1
    print(f"cases: {sum(len(c) for c in all_cases.values())}  problems: {problems}")
    return 1 if problems else 0


def cmd_run(args: argparse.Namespace) -> int:
    entries, skills, group = catalog()
    all_cases = read_all()
    report: dict[str, Any] = {"suites": {}, "cases": []}
    failed_total = 0
    for name, cases in all_cases.items():
        if args.suite and name != args.suite:
            continue
        selected = [c for c in cases if not args.case or re.search(args.case, c["id"])]
        failed = []
        for case in selected:
            issues = check(case, name, entries, skills, group)
            report["cases"].append({"suite": name, "id": case["id"], "passed": not issues, "issues": issues})
            if issues:
                failed.append((case["id"], issues))
        score = 1.0 if not selected else round((len(selected) - len(failed)) / len(selected), 4)
        report["suites"][name] = {"cases": len(selected), "failed": len(failed), "score": score}
        failed_total += len(failed)
        mark = "PASS" if not failed else "FAIL"
        print(f"{mark} {name:11} {len(selected) - len(failed):4}/{len(selected):<4} score {score:.0%}")
        for case_id, issues in failed[:5]:
            print(f"       {case_id}: {issues[0]}")
    cov = coverage(entries, all_cases)
    report["coverage"] = cov
    print(f"\ncoverage: {cov['tasks_covered']}/{cov['tasks_total']} contracts referenced "
          f"({cov['task_coverage']:.1%}) — a pass rate over cases nobody wrote is not coverage")
    if args.json:
        Path(args.json).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"report written: {args.json}")
    if args.min_coverage and cov["task_coverage"] < args.min_coverage:
        print(f"FAILED: coverage {cov['task_coverage']:.1%} below --min-coverage {args.min_coverage:.1%}")
        return 1
    return 1 if failed_total else 0


def cmd_show_prompt(args: argparse.Namespace) -> int:
    """Print what a behavioural harness would send, so it can be read before it is paid for."""
    all_cases = read_all()
    for name, cases in all_cases.items():
        for case in cases:
            if args.case and not re.search(args.case, case["id"]):
                continue
            query = case.get("query") or case.get("goal") or ""
            if not query:
                continue
            print(f"--- {name}/{case['id']}")
            print(query)
            expected = case.get("expected_tasks") or ([case["expected_task"]] if case.get("expected_task") else [])
            if expected:
                print(f"    expected tasks: {', '.join(expected)}")
            if case.get("expected_behavior"):
                for line in case["expected_behavior"]:
                    print(f"    expects: {line}")
            print()
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("ls", help="list case suites and contract coverage")
    sub.add_parser("validate", help="check every case is well formed and points at things that exist")
    run = sub.add_parser("run", help="execute the deterministic cases and score each suite")
    run.add_argument("--suite", choices=sorted(SUITES))
    run.add_argument("--case", help="regex over case ids")
    run.add_argument("--json", help="write the full report here")
    run.add_argument("--min-coverage", type=float, help="fail below this contract coverage, 0..1")
    show = sub.add_parser("show-prompt", help="print the text a behavioural harness would send")
    show.add_argument("--case", help="regex over case ids")
    args = parser.parse_args()
    sys.exit({"ls": cmd_ls, "validate": cmd_validate, "run": cmd_run, "show-prompt": cmd_show_prompt}[args.command](args))


if __name__ == "__main__":
    main()
