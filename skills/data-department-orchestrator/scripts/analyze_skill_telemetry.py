#!/usr/bin/env python3
"""Aggregate privacy-minimized telemetry into routing and reliability signals."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("events", type=Path)
    args = parser.parse_args()
    counts = Counter()
    outcomes = Counter()
    route_sources = Counter()
    failures = Counter()
    references = Counter()
    task_outcomes: dict[str, Counter] = defaultdict(Counter)
    task_tokens: dict[str, list[int]] = defaultdict(list)
    errors = []
    for line_no, line in enumerate(args.events.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"line {line_no}: {exc}")
            continue
        if event.get("user_content") is not None:
            errors.append(f"line {line_no}: user_content is forbidden")
            continue
        task = str(event.get("task_id", ""))
        skill = str(event.get("skill", ""))
        outcome = str(event.get("outcome", ""))
        counts[(skill, task)] += 1
        outcomes[outcome] += 1
        route_sources[str(event.get("route_source", ""))] += 1
        task_outcomes[task][outcome] += 1
        token = event.get("token_estimate")
        if isinstance(token, int) and token >= 0:
            task_tokens[task].append(token)
        failures.update(str(x) for x in event.get("failure_codes", []))
        references.update(str(x) for x in event.get("references_loaded", []))
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        sys.exit(1)
    task_signals = []
    for (skill, task), count in counts.most_common():
        failed = task_outcomes[task]["failed"] + task_outcomes[task]["blocked"]
        tokens = task_tokens.get(task, [])
        task_signals.append({"skill": skill, "task_id": task, "runs": count, "blocked_or_failed_rate": round(failed / count, 4), "average_token_estimate": round(sum(tokens) / len(tokens), 1) if tokens else 0})
    result = {
        "events": sum(counts.values()),
        "outcomes": dict(outcomes),
        "route_sources": dict(route_sources),
        "top_failure_codes": failures.most_common(20),
        "top_references": references.most_common(20),
        "task_signals": task_signals,
        "interpretation_rules": ["High blocked/failed rate indicates a contract, readiness or environment investigation—not an automatic threshold reduction.", "High override rate requires confusion-pair routing tests.", "High token use requires progressive-disclosure review before content deletion.", "Unused tasks require usage observation and ownership review before merge/removal."],
    }
    print(json.dumps(result, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
