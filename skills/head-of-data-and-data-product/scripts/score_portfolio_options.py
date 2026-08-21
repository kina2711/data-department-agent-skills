#!/usr/bin/env python3
"""Score a data portfolio and show where the ranking is real and where it is noise.

Weighted scoring gives prioritisation the appearance of arithmetic. The appearance is the risk:
two initiatives separated by 0.3 points are presented as first and second, weights are tuned until
the preferred item wins, and a hard gate that should have removed an item is quietly averaged into
its score. This keeps gates outside the arithmetic and reports which rank differences survive a
plausible change in weights.

It scores what you give it. It cannot tell you the weights are right, and a ranking is an input to
a portfolio decision, not the decision.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

TIE_THRESHOLD = 0.05  # share of the total scale within which two ranks are not distinguishable


def score(portfolio: Any, tie_threshold: float) -> tuple[list[str], list[str], dict[str, Any]]:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(portfolio, dict):
        return ["portfolio must be a JSON object"], [], {}

    weights = portfolio.get("criteria_weights")
    if not isinstance(weights, dict) or not weights:
        errors.append("criteria_weights must be a non-empty object")
        return errors, warnings, {}
    numeric_weights: dict[str, float] = {}
    for name, value in weights.items():
        if not isinstance(value, (int, float)) or isinstance(value, bool) or value < 0:
            errors.append(f"weight {name} must be a non-negative number, got {value!r}")
            continue
        numeric_weights[str(name)] = float(value)
    total_weight = sum(numeric_weights.values())
    if total_weight <= 0:
        errors.append("criteria weights sum to zero")
        return errors, warnings, {}
    if abs(total_weight - 100) > 0.01 and abs(total_weight - 1) > 0.01:
        warnings.append(f"weights sum to {total_weight:g}; normalising, but a non-standard total usually means a criterion was dropped")

    scale = portfolio.get("scale_max")
    scale = float(scale) if isinstance(scale, (int, float)) and scale > 0 else 5.0

    gates = portfolio.get("hard_gates")
    gates = [str(gate) for gate in gates] if isinstance(gates, list) else []

    items = portfolio.get("initiatives", portfolio.get("options"))
    if not isinstance(items, list) or not items:
        errors.append("initiatives must be a non-empty array")
        return errors, warnings, {}

    scored: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, item in enumerate(items):
        label = f"initiatives[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label}: must be an object")
            continue
        item_id = str(item.get("id", "")).strip()
        if not item_id:
            errors.append(f"{label}: missing id")
            continue
        if item_id in seen:
            errors.append(f"{item_id}: duplicate id")
        seen.add(item_id)

        gate_results = item.get("hard_gate_results")
        gate_results = gate_results if isinstance(gate_results, dict) else {}
        failed_gates = [gate for gate in gates if str(gate_results.get(gate, "unknown")).lower() not in {"pass", "passed", "true"}]
        unknown_gates = [gate for gate in gates if gate not in gate_results]
        if unknown_gates:
            warnings.append(f"{item_id}: gate(s) not evaluated: {', '.join(unknown_gates)}")

        scores = item.get("scores")
        scores = scores if isinstance(scores, dict) else {}
        missing = [name for name in numeric_weights if name not in scores]
        if missing:
            errors.append(f"{item_id}: not scored on {', '.join(missing)}")
            continue

        weighted = 0.0
        out_of_range = []
        for name, weight in numeric_weights.items():
            value = scores.get(name)
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                errors.append(f"{item_id}: score for {name} must be numeric, got {value!r}")
                weighted = float("nan")
                break
            if not 0 <= value <= scale:
                out_of_range.append(f"{name}={value}")
            weighted += (float(value) / scale) * (weight / total_weight)
        if out_of_range:
            errors.append(f"{item_id}: score(s) outside 0-{scale:g}: {', '.join(out_of_range)}")
            continue
        if weighted != weighted:  # NaN
            continue

        scored.append({
            "id": item_id,
            "title": str(item.get("title", "")).strip(),
            "score": round(weighted * 100, 2),
            "blocked": bool(failed_gates),
            "failed_gates": failed_gates,
            "confidence": item.get("confidence"),
            "evidence_refs": item.get("evidence_refs") if isinstance(item.get("evidence_refs"), list) else [],
        })

    for item in scored:
        if not item["evidence_refs"] and not item["blocked"]:
            warnings.append(f"{item['id']}: scored with no evidence reference; the ranking rests on opinion")

    eligible = sorted((item for item in scored if not item["blocked"]), key=lambda entry: -entry["score"])
    blocked = [item for item in scored if item["blocked"]]

    ties: list[tuple[str, str, float]] = []
    for position in range(len(eligible) - 1):
        gap = eligible[position]["score"] - eligible[position + 1]["score"]
        if gap <= tie_threshold * 100:
            ties.append((eligible[position]["id"], eligible[position + 1]["id"], round(gap, 2)))

    summary = {
        "scored": len(scored),
        "eligible": eligible,
        "blocked": blocked,
        "ties": ties,
        "weight_total": total_weight,
    }
    return errors, warnings, summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("portfolio", type=Path, help="portfolio scoring input as JSON")
    parser.add_argument("--tie-threshold", type=float, default=TIE_THRESHOLD, help=f"score gap treated as indistinguishable, as a share of scale (default {TIE_THRESHOLD})")
    parser.add_argument("--top", type=int, default=10, help="how many ranked initiatives to print")
    args = parser.parse_args()

    if not args.portfolio.is_file():
        print(f"ERROR: no such file: {args.portfolio}")
        sys.exit(2)
    try:
        portfolio = json.loads(args.portfolio.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"ERROR: invalid JSON: {exc}")
        sys.exit(2)

    errors, warnings, summary = score(portfolio, args.tie_threshold)
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"FAILED: {len(errors)} scoring error(s)")
        sys.exit(1)

    eligible = summary["eligible"]
    print(f"scored: {summary['scored']}  eligible: {len(eligible)}  gate-blocked: {len(summary['blocked'])}")
    for rank, item in enumerate(eligible[: args.top], 1):
        title = f" - {item['title']}" if item["title"] else ""
        confidence = f"  confidence {item['confidence']}" if item["confidence"] is not None else ""
        print(f"  {rank}. {item['id']}{title}: {item['score']:.2f}{confidence}")
    for item in summary["blocked"]:
        print(f"  BLOCKED {item['id']}: failed {', '.join(item['failed_gates'])}")
    if summary["blocked"]:
        print("NOTE: a failed hard gate removes an initiative from the ranking; it is never traded off against a high score.")

    for left, right, gap in summary["ties"]:
        warnings.append(f"{left} and {right} differ by {gap:.2f} points; that ordering will not survive a small change in weights")

    for warning in warnings:
        print(f"WARNING: {warning}")

    if warnings:
        print(f"PASS WITH WARNINGS: {len(warnings)} item(s) to settle before the portfolio decision")
        sys.exit(0)
    print("PASS: every initiative is fully scored, gates were evaluated, and the ranking separates cleanly")


if __name__ == "__main__":
    main()
