#!/usr/bin/env python3
"""Score personal-project options with hard gates, evidence confidence and risk penalties."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def score(document: object) -> tuple[dict[str, object], list[str]]:
    errors: list[str] = []
    if not isinstance(document, dict):
        return {}, ["scorecard root must be an object"]
    weights = document.get("criteria_weights")
    if not isinstance(weights, dict) or not weights:
        return {}, ["criteria_weights must be a non-empty object"]
    if any(not isinstance(value, (int, float)) or value <= 0 for value in weights.values()):
        errors.append("every criterion weight must be positive")
    if abs(sum(float(value) for value in weights.values()) - 100.0) > 1e-9:
        errors.append("criteria weights must sum to 100")
    hard_gates = document.get("hard_gates")
    if not isinstance(hard_gates, list) or not hard_gates or not all(isinstance(item, str) and item for item in hard_gates):
        errors.append("hard_gates must contain non-empty names")
        hard_gates = []
    options = document.get("options")
    if not isinstance(options, list) or not options:
        errors.append("options must contain at least one option")
        options = []

    ranked: list[dict[str, object]] = []
    seen: set[str] = set()
    for index, option in enumerate(options):
        if not isinstance(option, dict):
            errors.append(f"options[{index}] must be an object")
            continue
        option_id = option.get("option_id")
        if not isinstance(option_id, str) or not option_id.strip():
            errors.append(f"options[{index}].option_id must be non-empty")
            continue
        if option_id in seen:
            errors.append(f"duplicate option_id: {option_id}")
            continue
        seen.add(option_id)
        values = option.get("scores")
        if not isinstance(values, dict):
            errors.append(f"option {option_id}.scores must be an object")
            values = {}
        missing = sorted(set(weights) - set(values))
        extra = sorted(set(values) - set(weights))
        if missing:
            errors.append(f"option {option_id} lacks scores: {missing}")
        if extra:
            errors.append(f"option {option_id} has unknown scores: {extra}")
        invalid = [key for key, value in values.items() if not isinstance(value, (int, float)) or not 0 <= value <= 10]
        if invalid:
            errors.append(f"option {option_id} scores must be in 0..10: {sorted(invalid)}")
        gate_results = option.get("hard_gate_results")
        if not isinstance(gate_results, dict):
            errors.append(f"option {option_id}.hard_gate_results must be an object")
            gate_results = {}
        missing_gates = sorted(set(hard_gates) - set(gate_results))
        if missing_gates:
            errors.append(f"option {option_id} lacks hard gates: {missing_gates}")
        invalid_gates = [name for name, value in gate_results.items() if value not in {True, False, "pass", "fail"}]
        if invalid_gates:
            errors.append(f"option {option_id} hard gates must be pass/fail: {sorted(invalid_gates)}")
        confidence = option.get("confidence")
        risk_penalty = option.get("risk_penalty")
        if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
            errors.append(f"option {option_id}.confidence must be in 0..1")
            confidence = 0
        if not isinstance(risk_penalty, (int, float)) or not 0 <= risk_penalty <= 100:
            errors.append(f"option {option_id}.risk_penalty must be in 0..100")
            risk_penalty = 0
        raw = sum(float(weights[key]) * float(values.get(key, 0)) / 10 for key in weights)
        eligible = all(gate_results.get(name) in {True, "pass"} for name in hard_gates)
        conservative = max(0.0, raw * (0.5 + 0.5 * float(confidence)) - float(risk_penalty)) if eligible else 0.0
        ranked.append({
            "option_id": option_id,
            "mode": option.get("mode", ""),
            "eligible": eligible,
            "raw_score": round(raw, 2),
            "confidence": float(confidence),
            "risk_penalty": float(risk_penalty),
            "conservative_score": round(conservative, 2),
        })
    ranked.sort(key=lambda item: (-float(item["conservative_score"]), -float(item["raw_score"]), str(item["option_id"])))
    return {"ranked_options": ranked, "recommended_option_id": next((item["option_id"] for item in ranked if item["eligible"]), None)}, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scorecard", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        document = json.loads(args.scorecard.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    result, errors = score(document)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
