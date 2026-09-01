#!/usr/bin/env python3
"""Send the routing cases to a model and score what comes back.

Every other check in this repo reads files. Validation proves the contracts agree with each other,
the twelve properties prove they obey the stated rules, and both stay green regardless of whether
an agent handed a live request would ever find the right one. Internal coherence is what they
establish. Whether any of it works is a separate question, open here for a while.

The answer costs money and arrives sampled rather than fixed, which shapes two decisions.

Nothing is sent without `--execute`; the default prints an estimate to read first. Replies are
cached under a hash of the exact prompt and model, so re-running an unchanged case is free, and an
edited prompt can never be scored against yesterday's reply.

Per case it asks three things. Did the model choose the expected skill? Did it name the tasks the
case lists? And on confusion pairs, where the near miss is the entire point, did it stay off the
named rival? Skill accuracy is the headline worth quoting. Recall flatters a model that lists
everything, so precision sits next to it and neither appears alone.

A single run tells you about that sample. `--repeat` fires each case n times and reports where the
verdicts disagreed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import statistics
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from eval_harness import SUITES, load_cases  # noqa: E402

CASES = ROOT / "evaluations"
CACHE = ROOT / ".cache" / "behavioural"
BEHAVIOURAL_SUITES = ("routing", "confusion")
RETRIES = 3
BACKOFF_SECONDS = 4


class CallFailed(RuntimeError):
    """The model was never reached. Distinct from a reply that came back wrong."""


def skill_menu() -> str:
    lines = []
    for skill_md in sorted((ROOT / "skills").glob("*/SKILL.md")):
        text = skill_md.read_text(encoding="utf-8")
        name = re.search(r"^name:\s*(.+)$", text, re.M)
        desc = re.search(r"^description:\s*(.+)$", text, re.M)
        if name and desc:
            lines.append(f"- {name.group(1).strip()}: {desc.group(1).strip()}")
    return "\n".join(lines)


# The first measurement gave the model the skill menu and nothing else, and scored it against cases
# written for an agent that also has the routing policy loaded. It missed the orchestrator cases,
# which was the policy's absence showing up as a suite failure. The policy below is the one this
# repo actually ships in CLAUDE.md; leaving it out measured a system nobody runs.
POLICY = """Routing policy for this department:
- A request that needs more than one role, or whose scope is not yet clear, goes to
  data-department-orchestrator. It decomposes the work; it does not do the work.
- A request naming one deliverable inside one role goes straight to that role's skill.
- Pick the skill by the primary deliverable asked for, not by the job title mentioned."""

SKILL_PROMPT = """You are routing a request inside a data department. Here are the available skills:

{menu}

{policy}

Request:
{query}

Answer with JSON only, no prose and no code fence:
{{"skill": "<exactly one skill name from the list>", "why": "<one sentence>"}}"""

# Task ids were never in the first prompt, so task recall of 2.9% measured whether a model can
# invent identifiers it has not been shown. Routing here happens in two steps -- choose the skill,
# then read that skill's task list -- so the measurement now does the same.
TASK_PROMPT = """A request has been routed to the `{skill}` skill. Its tasks are:

{tasks}

Request:
{query}

Answer with JSON only, no prose and no code fence:
{{"tasks": ["<task id>", ...]}}

List only the tasks you would actually run, in order. Listing extra tasks is scored against you."""


def build_prompt(case: dict, menu: str) -> str:
    return SKILL_PROMPT.format(menu=menu, policy=POLICY, query=case.get("query", ""))


def task_menu(skill: str) -> str:
    catalog = json.loads((ROOT / "task-catalog.json").read_text(encoding="utf-8"))
    index = json.loads((ROOT / "docs" / "retrieval-index.json").read_text(encoding="utf-8"))
    goals = {t["id"]: t.get("output", "") for t in catalog}
    ids = [t["id"] for t in index["tasks"] if t["skill"] == skill]
    return "\n".join(f"- {i}: {goals.get(i, '')}" for i in ids)


def ask(prompt: str, model: str, timeout: int, attempt: int = 0) -> tuple[dict | None, str, bool]:
    """Return (parsed, raw, from_cache).

    The key covers the prompt, the model and which repeat this is. Leaving the attempt out made
    `--repeat` replay one cached answer n times and report a spread of zero every time -- a
    stability measurement that could not observe instability.
    """
    key = hashlib.sha256(f"{model}\0{attempt}\0{prompt}".encode()).hexdigest()[:32]
    cached = CACHE / f"{key}.json"
    if cached.exists():
        raw = json.loads(cached.read_text(encoding="utf-8"))["raw"]
        return parse(raw), raw, True
    # A burst of concurrent calls gets throttled, and the first version of this returned the
    # failure as an unparseable answer -- 27 rate-limited calls were reported as 27 routing misses,
    # complete with an accuracy figure. An infrastructure failure is not a wrong answer.
    for attempt_number in range(RETRIES):
        result = subprocess.run(
            ["claude", "-p", prompt, "--model", model, "--output-format", "json",
             "--permission-mode", "plan", "--allowed-tools", ""],
            capture_output=True, text=True, timeout=timeout, check=False,
        )
        if result.returncode == 0:
            break
        if attempt_number < RETRIES - 1:
            time.sleep(BACKOFF_SECONDS * (2 ** attempt_number))
    if result.returncode != 0:
        raise CallFailed(f"rc={result.returncode} after {RETRIES} tries: {result.stderr.strip()[:160]}")
    try:
        raw = json.loads(result.stdout)["result"]
    except (json.JSONDecodeError, KeyError):
        raw = result.stdout
    CACHE.mkdir(parents=True, exist_ok=True)
    cached.write_text(json.dumps({"raw": raw}, ensure_ascii=False), encoding="utf-8")
    return parse(raw), raw, False


def parse(raw: str) -> dict | None:
    """Models wrap JSON in fences and prose no matter what the prompt says; take the widest object."""
    match = re.search(r"\{.*\}", raw, re.S)
    if not match:
        return None
    try:
        answer = json.loads(match.group(0))
    except json.JSONDecodeError:
        return None
    return answer if isinstance(answer, dict) else None


def score_case(case: dict, suite: str, answer: dict | None, task_answer: dict | None = None,
               known_skills: frozenset[str] = frozenset()) -> dict:
    expected_skill = case.get("expected_primary_skill")
    expected_tasks = case.get("expected_tasks") or (
        [case["expected_task"]] if case.get("expected_task") else [])
    got_skill = (answer or {}).get("skill")
    got_tasks = [t for t in (task_answer or {}).get("tasks", []) if isinstance(t, str)]

    hit = set(expected_tasks) & set(got_tasks)
    # Without stage two there are no tasks to score, and a recall of 0/n would read as a model that
    # answered wrongly rather than one that was never asked.
    scored_tasks = task_answer is not None
    # An answer naming something that is not a skill is a broken reply, not a routing mistake.
    # Counting the two together would report the prompt's failures as the suite's.
    invalid = answer is not None and bool(got_skill) and known_skills and got_skill not in known_skills
    result = {
        "case": case["id"],
        "suite": suite,
        "expected_skill": expected_skill,
        "got_skill": got_skill,
        "skill_correct": bool(got_skill) and got_skill == expected_skill,
        "task_recall": round(len(hit) / len(expected_tasks), 3) if scored_tasks and expected_tasks else None,
        "task_precision": round(len(hit) / len(got_tasks), 3) if scored_tasks and got_tasks else None,
        "unparseable": answer is None or not got_skill,
        "invalid_skill": bool(invalid),
    }
    if case.get("rejected_skill"):
        result["rejected_skill"] = case["rejected_skill"]
        result["avoided_rival"] = got_skill != case["rejected_skill"]
    return result


def collect(pattern: str | None) -> list[tuple[str, dict]]:
    picked = []
    for suite in BEHAVIOURAL_SUITES:
        path = CASES / SUITES[suite][0]
        if not path.exists():
            continue
        for case in load_cases(path):
            if not case.get("query"):
                continue
            if pattern and not re.search(pattern, case["id"]):
                continue
            picked.append((suite, case))
    return picked


def report(rows: list[dict], repeat: int) -> dict:
    failed = [r for r in rows if r.get("call_failed")]
    rows = [r for r in rows if not r.get("call_failed")]
    by_case: dict[str, list[dict]] = {}
    for row in rows:
        by_case.setdefault(row["case"], []).append(row)

    accuracy = [statistics.mean(1.0 if r["skill_correct"] else 0.0 for r in runs) for runs in by_case.values()]
    recalls = [r["task_recall"] for r in rows if r["task_recall"] is not None]
    precisions = [r["task_precision"] for r in rows if r["task_precision"] is not None]
    rivals = [r["avoided_rival"] for r in rows if "avoided_rival" in r]
    unstable = [c for c, runs in by_case.items() if len({r["skill_correct"] for r in runs}) > 1]

    summary = {
        "cases": len(by_case),
        "runs": len(rows),
        "repeat": repeat,
        "skill_accuracy": round(statistics.mean(accuracy), 3) if accuracy else 0.0,
        "task_recall": round(statistics.mean(recalls), 3) if recalls else None,
        "task_precision": round(statistics.mean(precisions), 3) if precisions else None,
        "rival_avoided": round(sum(rivals) / len(rivals), 3) if rivals else None,
        "unparseable": sum(1 for r in rows if r["unparseable"]),
        "invalid_skill": sum(1 for r in rows if r.get("invalid_skill")),
        "unstable_cases": unstable,
        "call_failures": len(failed),
    }
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--execute", action="store_true", help="actually call the model; without it this only estimates")
    parser.add_argument("--model", default="claude-haiku-4-5-20251001")
    parser.add_argument("--case", help="regex over case ids")
    parser.add_argument("--limit", type=int, help="stop after this many cases")
    parser.add_argument("--tasks", action="store_true",
                        help="also run the second stage: pick tasks inside the chosen skill (doubles the calls)")
    parser.add_argument("--repeat", type=int, default=1, help="runs per case, to see the spread")
    parser.add_argument("--workers", type=int, default=8, help="cases in flight at once")
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--json", help="write the full per-run report here")
    args = parser.parse_args()

    cases = collect(args.case)
    if args.limit:
        cases = cases[: args.limit]
    if not cases:
        print("no cases matched")
        sys.exit(1)

    menu = skill_menu()
    prompts = [(suite, case, build_prompt(case, menu)) for suite, case in cases]
    uncached = sum(
        1 for _, _, p in prompts
        for attempt in range(args.repeat)
        if not (CACHE / f"{hashlib.sha256(f'{args.model}\0{attempt}\0{p}'.encode()).hexdigest()[:32]}.json").exists()
    )

    if not args.execute:
        print(f"{len(cases)} cases x {args.repeat} = {len(cases) * args.repeat} runs against {args.model}")
        print(f"{uncached} would call the model; the rest are cached and free.")
        print(f"prompt size: about {len(prompts[0][2]) // 4} tokens each, {len(menu.splitlines())} skills in the menu")
        print("\nNothing was sent. Re-run with --execute to spend.")
        sys.exit(0)

    # Serially, 106 cases at roughly forty seconds each is an hour, which means nobody runs it.
    # Each case is independent, so they go out together.
    known = frozenset(p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md"))

    def one(job: tuple[int, str, dict, str]) -> list[dict]:
        _, suite, case, prompt = job
        out = []
        for attempt in range(args.repeat):
            try:
                answer, _raw, cached = ask(prompt, args.model, args.timeout, attempt)
            except (CallFailed, subprocess.TimeoutExpired) as exc:
                out.append({"case": case["id"], "suite": suite, "call_failed": str(exc)[:160],
                            "skill_correct": False, "got_skill": None, "expected_skill":
                            case.get("expected_primary_skill"), "task_recall": None,
                            "task_precision": None, "unparseable": False, "invalid_skill": False})
                continue
            task_answer = None
            chosen = (answer or {}).get("skill")
            # Stage two runs against whatever skill the model actually chose, not the expected one.
            # Scoring tasks inside a skill it never picked would flatter the number.
            if args.tasks and chosen and (ROOT / "skills" / chosen / "SKILL.md").exists():
                menu_for_skill = task_menu(chosen)
                if menu_for_skill:
                    task_answer, _, _ = ask(
                        TASK_PROMPT.format(skill=chosen, tasks=menu_for_skill, query=case.get("query", "")),
                        args.model, args.timeout, attempt)
            row = score_case(case, suite, answer, task_answer, known)
            row["cached"] = cached
            out.append(row)
        return out

    rows: list[dict] = []
    started = time.time()
    jobs = [(i, suite, case, prompt) for i, (suite, case, prompt) in enumerate(prompts, 1)]
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for (index, _suite, case, _p), result in zip(jobs, pool.map(one, jobs)):
            rows.extend(result)
            last = result[-1]
            mark = "ERR " if last.get("call_failed") else ("ok " if last["skill_correct"] else "MISS")
            print(f"{mark} {index:3}/{len(prompts)} {case['id'][:44]:44} "
                  f"got {str(last['got_skill'])[:34]}", flush=True)

    summary = report(rows, args.repeat)
    if summary["call_failures"]:
        print(f"\n{summary['call_failures']} of {len(rows)} calls never reached the model and are "
              f"excluded. Throttling is the usual cause; lower --workers and re-run, the rest is cached.")
    if not summary["cases"]:
        print("Every call failed. No accuracy is reported, because none was measured.")
        sys.exit(1)
    print(f"\nskill accuracy   {summary['skill_accuracy']:.1%}  over {summary['cases']} cases, "
          f"{summary['runs']} runs, {time.time() - started:.0f}s")
    if summary["task_recall"] is not None and summary["task_precision"] is not None:
        print(f"task recall      {summary['task_recall']:.1%}   precision {summary['task_precision']:.1%}  "
              f"— recall alone rewards a model that lists everything")
    elif not args.tasks:
        print("task recall      not measured; pass --tasks to run the second stage")
    if summary["rival_avoided"] is not None:
        print(f"rival avoided    {summary['rival_avoided']:.1%}   on confusion pairs")
    broken = summary["unparseable"] + summary["invalid_skill"]
    if broken:
        print(f"broken replies   {broken} of {summary['runs']}: {summary['unparseable']} returned no JSON "
              f"object or no skill, {summary['invalid_skill']} named something that is not a skill. These are prompt "
              f"failures counted against accuracy above; the routing figure excluding them is "
              f"{(summary['skill_accuracy'] * summary['cases']) / max(1, summary['cases'] - broken):.1%}.")
    if summary["unstable_cases"]:
        print(f"unstable         {len(summary['unstable_cases'])} cases answered differently across repeats: "
              f"{', '.join(summary['unstable_cases'][:4])}")
    elif args.repeat > 1:
        print(f"unstable         none; every case gave the same verdict across {args.repeat} runs")

    if args.json:
        Path(args.json).write_text(
            json.dumps({"summary": summary, "runs": rows, "model": args.model}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8")
        print(f"report written: {args.json}")

    print("\nThis measures routing behaviour, not delivery. A model that picks the right skill can "
          "still execute the contract badly, and no number here would notice.")


if __name__ == "__main__":
    main()
