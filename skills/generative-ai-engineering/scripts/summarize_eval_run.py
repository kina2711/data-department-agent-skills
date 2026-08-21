#!/usr/bin/env python3
"""Summarize an LLM evaluation run and say whether the result can carry a decision.

A pass rate on its own is a number without an error bar. Eighteen out of twenty is 90% and also
compatible with a true rate near 70%; a ten-case suite cannot distinguish a fix from noise; and a
judge model that agrees with human labels 60% of the time is scoring its own opinion. This reports
the interval, not just the point estimate, and refuses to call a small run decisive.

It reads JSONL results and computes Wilson intervals, per-category rates, and judge-human
agreement when human labels are present. It does not run the model or grade anything itself.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

Z_95 = 1.96
MIN_DECISIVE_CASES = 30


def wilson(passed: int, total: int, z: float = Z_95) -> tuple[float, float, float]:
    """Point estimate with a Wilson score interval, which stays sane at small n and rates near 0/1."""
    if total == 0:
        return (float("nan"), float("nan"), float("nan"))
    rate = passed / total
    denominator = 1 + z**2 / total
    centre = (rate + z**2 / (2 * total)) / denominator
    margin = (z * math.sqrt(rate * (1 - rate) / total + z**2 / (4 * total**2))) / denominator
    return rate, max(0.0, centre - margin), min(1.0, centre + margin)


def read_records(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    records: list[dict[str, Any]] = []
    errors: list[str] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"line {number}: invalid JSON ({exc.msg})")
            continue
        if not isinstance(record, dict):
            errors.append(f"line {number}: record is not an object")
            continue
        records.append(record)
    return records, errors


def as_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)) and value in (0, 1):
        return bool(value)
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"pass", "true", "yes", "1"}:
            return True
        if lowered in {"fail", "false", "no", "0"}:
            return False
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("results", type=Path, help="evaluation results as JSONL, one case per line")
    parser.add_argument("--baseline", type=float, help="pass rate of the version being compared against, 0-1")
    parser.add_argument("--threshold", type=float, help="minimum acceptable pass rate, 0-1")
    parser.add_argument("--require-decisive", action="store_true", help=f"fail when the run has fewer than {MIN_DECISIVE_CASES} cases")
    args = parser.parse_args()

    if not args.results.is_file():
        print(f"ERROR: no such file: {args.results}")
        sys.exit(2)

    records, parse_errors = read_records(args.results)
    for error in parse_errors:
        print(f"ERROR: {error}")
    if not records:
        print("ERROR: no usable records")
        sys.exit(1)

    warnings: list[str] = []
    errors: list[str] = list(parse_errors)

    passed = 0
    scored = 0
    missing_verdict = 0
    seen_ids: set[str] = set()
    duplicates = 0
    by_category: defaultdict[str, list[bool]] = defaultdict(list)
    judge_agreements: list[bool] = []
    latencies: list[float] = []
    costs: list[float] = []

    for record in records:
        case_id = str(record.get("id", "")).strip()
        if case_id:
            if case_id in seen_ids:
                duplicates += 1
            seen_ids.add(case_id)

        verdict = as_bool(record.get("passed", record.get("verdict", record.get("result"))))
        if verdict is None:
            missing_verdict += 1
        else:
            scored += 1
            passed += int(verdict)
            by_category[str(record.get("category", "uncategorized"))].append(verdict)
            human = as_bool(record.get("human_label", record.get("human_passed")))
            if human is not None:
                judge_agreements.append(human == verdict)

        latency = record.get("latency_ms")
        if isinstance(latency, (int, float)):
            latencies.append(float(latency))
        cost = record.get("cost_usd")
        if isinstance(cost, (int, float)):
            costs.append(float(cost))

    if missing_verdict:
        errors.append(f"{missing_verdict} record(s) carry no pass/fail verdict; an ungraded case is not a passing case")
    if duplicates:
        warnings.append(f"{duplicates} duplicate case id(s); a repeated case is weighted twice in the rate")

    rate, low, high = wilson(passed, scored)
    print(f"cases: {len(records)}  scored: {scored}  passed: {passed}")
    print(f"pass rate: {rate:.1%}  95% CI: [{low:.1%}, {high:.1%}]  width: {high - low:.1%}")

    if scored < MIN_DECISIVE_CASES:
        message = (
            f"{scored} scored cases cannot separate a real change from noise; "
            f"the interval spans {high - low:.0%}"
        )
        if args.require_decisive:
            errors.append(message)
        else:
            warnings.append(message)

    if by_category and len(by_category) > 1:
        print("by category:")
        rates = {name: wilson(sum(values), len(values))[0] for name, values in by_category.items()}
        lowest = min(rates.values())
        unique_low = sum(1 for value in rates.values() if value == lowest) == 1
        for category, verdicts in sorted(by_category.items()):
            category_rate, category_low, category_high = wilson(sum(verdicts), len(verdicts))
            flag = "  <- weakest" if unique_low and category_rate == lowest else ""
            print(f"  {category}: {category_rate:.1%} of {len(verdicts)} [{category_low:.0%}, {category_high:.0%}]{flag}")

    if judge_agreements:
        agreement = sum(judge_agreements) / len(judge_agreements)
        print(f"judge-human agreement: {agreement:.1%} over {len(judge_agreements)} labelled case(s)")
        if agreement < 0.80:
            warnings.append(
                f"judge agrees with human labels {agreement:.0%} of the time; below that the pass rate "
                "measures the judge, not the system"
            )
    else:
        warnings.append("no human labels present; the judge's grading is unvalidated for this run")

    if latencies:
        latencies.sort()
        p50 = latencies[len(latencies) // 2]
        p95 = latencies[min(len(latencies) - 1, int(len(latencies) * 0.95))]
        print(f"latency ms: p50 {p50:.0f}  p95 {p95:.0f}")
    if costs:
        print(f"cost: total ${sum(costs):.4f}  mean ${sum(costs) / len(costs):.4f} per case")

    if args.baseline is not None:
        delta = rate - args.baseline
        print(f"baseline: {args.baseline:.1%}  delta: {delta:+.1%}")
        if low <= args.baseline <= high:
            warnings.append(
                f"the baseline {args.baseline:.1%} sits inside the confidence interval; "
                "this run does not demonstrate a difference"
            )

    if args.threshold is not None:
        print(f"threshold: {args.threshold:.1%}")
        if low < args.threshold <= high:
            warnings.append(f"the interval straddles the threshold; the run neither meets nor misses it decisively")
        elif high < args.threshold:
            errors.append(f"pass rate is below the {args.threshold:.1%} threshold with 95% confidence")

    for error in errors[len(parse_errors):]:
        print(f"ERROR: {error}")
    for warning in warnings:
        print(f"WARNING: {warning}")

    if errors:
        print(f"FAILED: {len(errors)} blocking issue(s)")
        sys.exit(1)
    if warnings:
        print(f"PASS WITH WARNINGS: {len(warnings)} item(s) that limit what this run can support")
        sys.exit(0)
    print("PASS: the run is large enough, judged consistently, and meets the stated bar")


if __name__ == "__main__":
    main()
