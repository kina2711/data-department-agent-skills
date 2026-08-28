#!/usr/bin/env python3
"""Compute when each topic in a learner memory is due for review.

`review_due_at` is read by the transition builder to decide whether knowledge is fresh, and it
was previously a hand-entered date. A date somebody typed six months ago is not a freshness
signal; it is a guess that has since been treated as evidence.

The interval comes from how the topic was actually demonstrated. A topic proved once by
explanation decays faster than one proved twice by independent application; a topic whose
subject matter changes underneath it decays faster than a stable one; and a topic that other
topics depend on is worth refreshing before the things built on it are needed.

It schedules review. It cannot tell whether the underlying evidence was any good, and a topic
that is not yet due is not thereby proven — it is only not yet known to have decayed.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

# Base interval in days by topic state. `mastered` earns the longest, and nothing below
# `practiced` earns a long one, because there is nothing yet to retain.
BASE_INTERVAL = {
    "unseen": 0,
    "exposed": 14,
    "practiced": 30,
    "demonstrated": 60,
    "mastered": 120,
    "stale": 0,
    "conflicted": 0,
    "retired": 0,
}
# Each independent piece of evidence beyond the first extends the interval, with diminishing
# effect: the second demonstration says much more than the fifth.
EVIDENCE_STEP = [1.0, 1.4, 1.7, 1.9, 2.0]
# Subject matter that moves invalidates knowledge on its own schedule, not the learner's.
VERSION_SENSITIVE_FACTOR = 0.5
# Something several topics are built on is refreshed before the dependents need it.
DEPENDENCY_FACTOR = 0.8
MAX_INTERVAL_DAYS = 365
IMMEDIATE_STATES = {"stale", "conflicted"}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_date(value: Any) -> date | None:
    try:
        return datetime.strptime(str(value).strip(), "%Y-%m-%d").date()
    except (ValueError, AttributeError, TypeError):
        return None


def evidence_multiplier(count: int) -> float:
    if count <= 0:
        return 0.6  # a state claimed with no evidence reference is reviewed sooner, not later
    return EVIDENCE_STEP[min(count, len(EVIDENCE_STEP)) - 1]


def compute(memory: Any, today: date) -> tuple[list[dict[str, Any]], list[str]]:
    notes: list[str] = []
    topics = memory.get("topics") if isinstance(memory, dict) else None
    if not isinstance(topics, list):
        return [], ["memory has no topics list"]

    dependents: dict[str, int] = {}
    for topic in topics:
        if not isinstance(topic, dict):
            continue
        for prerequisite in topic.get("prerequisites") or []:
            key = str(prerequisite).strip()
            if key:
                dependents[key] = dependents.get(key, 0) + 1

    results: list[dict[str, Any]] = []
    for topic in topics:
        if not isinstance(topic, dict):
            continue
        topic_id = str(topic.get("topic_id", "")).strip()
        if not topic_id:
            notes.append("a topic has no topic_id and was skipped")
            continue
        status = str(topic.get("status", "")).strip()
        if status not in BASE_INTERVAL:
            notes.append(f"{topic_id}: unknown status {status or '(empty)'}; treated as due now")
            status = "conflicted"

        anchor = parse_date(topic.get("last_demonstrated_at")) or parse_date(topic.get("last_learned_at"))
        if anchor is None and status not in IMMEDIATE_STATES and BASE_INTERVAL[status] > 0:
            notes.append(f"{topic_id}: no readable demonstration date; treated as due now")

        base = BASE_INTERVAL[status]
        if status in IMMEDIATE_STATES or base == 0 or anchor is None:
            due = today
            interval = 0
            reason = f"{status or 'unknown'}: review now"
        else:
            factor = evidence_multiplier(len(topic.get("evidence_refs") or []))
            reason_parts = [f"{status} base {base}d", f"evidence x{factor:.2g}"]
            if topic.get("version_sensitive") or str(topic.get("source_version", "")).strip():
                factor *= VERSION_SENSITIVE_FACTOR
                reason_parts.append(f"version-sensitive x{VERSION_SENSITIVE_FACTOR}")
            if dependents.get(topic_id, 0) >= 2:
                factor *= DEPENDENCY_FACTOR
                reason_parts.append(f"{dependents[topic_id]} dependents x{DEPENDENCY_FACTOR}")
            interval = min(int(round(base * factor)), MAX_INTERVAL_DAYS)
            due = anchor + timedelta(days=interval)
            reason = ", ".join(reason_parts)

        existing = parse_date(topic.get("review_due_at"))
        results.append({
            "topic_id": topic_id,
            "status": status,
            "anchor_date": anchor.isoformat() if anchor else "",
            "interval_days": interval,
            "review_due_at": due.isoformat(),
            "previous_review_due_at": existing.isoformat() if existing else "",
            "changed": existing != due,
            "overdue_days": max((today - due).days, 0),
            "basis": reason,
        })
    return results, notes


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("memory", type=Path, help="learner-memory.json")
    parser.add_argument("--today", type=str, help="override today's date as YYYY-MM-DD")
    parser.add_argument("--apply", type=Path, help="write an updated memory file to this path")
    parser.add_argument("--report-out", type=Path)
    args = parser.parse_args()

    try:
        memory = load(args.memory)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: unreadable memory: {exc}")
        sys.exit(1)

    today = parse_date(args.today) if args.today else date.today()
    if today is None:
        print("ERROR: --today must be YYYY-MM-DD")
        sys.exit(1)

    results, notes = compute(memory, today)
    for note in notes:
        print(f"NOTE: {note}")
    if not results:
        print("FAILED: nothing to schedule")
        sys.exit(1)

    overdue = [r for r in results if r["overdue_days"] > 0]
    changed = [r for r in results if r["changed"]]
    for row in sorted(results, key=lambda r: (-r["overdue_days"], r["review_due_at"])):
        flag = f"OVERDUE {row['overdue_days']}d" if row["overdue_days"] else "due"
        print(f"{row['topic_id']}: {flag} {row['review_due_at']}  ({row['basis']})")

    print(f"topics: {len(results)}  overdue: {len(overdue)}  rescheduled: {len(changed)}")

    if args.report_out is not None:
        args.report_out.write_text(
            json.dumps({"computed_at": today.isoformat(), "topics": results}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"report written: {args.report_out}")

    if args.apply is not None:
        by_id = {r["topic_id"]: r for r in results}
        for topic in memory.get("topics", []):
            row = by_id.get(str(topic.get("topic_id", "")).strip())
            if row:
                topic["review_due_at"] = row["review_due_at"]
        args.apply.write_text(json.dumps(memory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"updated memory written: {args.apply}")
        print("A computed date is a scheduling decision, not evidence; mastery state is unchanged.")


if __name__ == "__main__":
    main()
