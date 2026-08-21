#!/usr/bin/env python3
"""Audit an interview question bank for coverage, balance, redundancy and selection risk.

A question bank drifts quietly. Competencies that are easy to write questions for get five, the
one that actually predicts the job gets none; two questions differ only in wording and double-count
the same signal; difficulty piles up at one end; a question that leaked keeps being scored as if it
still measured something. Where outcome data exists, the bank also carries adverse-impact risk.

It audits the bank's structure and, when pass/fail outcomes by monitored group are supplied,
computes the selection-rate ratio as a screening signal. A ratio below 0.80 is a trigger to
investigate, never a finding of discrimination, and never proof of fairness when above it.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ADVERSE_IMPACT_RATIO = 0.80
MIN_GROUP_SIZE = 30
DIFFICULTY_ORDER = ("easy", "medium", "hard")
STOPWORDS = {
    "the", "a", "an", "of", "to", "in", "on", "for", "and", "or", "is", "are", "how", "what",
    "why", "would", "you", "your", "do", "does", "can", "with", "that", "this", "it", "if",
}


def normalize(text: str) -> set[str]:
    words = re.findall(r"[a-z0-9]+", text.lower())
    return {word for word in words if word not in STOPWORDS and len(word) > 2}


def jaccard(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def audit(bank: Any, similarity: float) -> tuple[list[str], list[str], dict[str, Any]]:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(bank, dict):
        return ["question bank must be a JSON object"], [], {}

    required_competencies = bank.get("required_competencies")
    required_competencies = [str(item) for item in required_competencies] if isinstance(required_competencies, list) else []

    questions = bank.get("questions")
    if not isinstance(questions, list) or not questions:
        errors.append("questions must be a non-empty array")
        return errors, warnings, {}

    seen_ids: set[str] = set()
    competency_counts: Counter[str] = Counter()
    difficulty_counts: Counter[str] = Counter()
    tokens: dict[str, set[str]] = {}
    leaked: list[str] = []
    unanchored: list[str] = []
    outcomes: defaultdict[str, dict[str, int]] = defaultdict(lambda: {"assessed": 0, "passed": 0})

    for index, question in enumerate(questions):
        label = f"questions[{index}]"
        if not isinstance(question, dict):
            errors.append(f"{label}: must be an object")
            continue
        question_id = str(question.get("id", "")).strip()
        if not question_id:
            errors.append(f"{label}: missing id")
            continue
        if question_id in seen_ids:
            errors.append(f"{question_id}: duplicate id")
        seen_ids.add(question_id)

        text = str(question.get("text", "")).strip()
        if not text:
            errors.append(f"{question_id}: missing question text")
        else:
            tokens[question_id] = normalize(text)

        competencies = question.get("competencies")
        competencies = [str(item) for item in competencies] if isinstance(competencies, list) else []
        if not competencies:
            errors.append(f"{question_id}: no competency; a question measuring nothing named cannot be scored")
        for competency in competencies:
            competency_counts[competency] += 1

        difficulty = str(question.get("difficulty", "")).strip().lower()
        if difficulty not in DIFFICULTY_ORDER:
            warnings.append(f"{question_id}: difficulty {difficulty or '(missing)'!r} is not one of {', '.join(DIFFICULTY_ORDER)}")
        else:
            difficulty_counts[difficulty] += 1

        anchors = question.get("answer_anchors")
        if not isinstance(anchors, list) or len(anchors) < 2:
            unanchored.append(question_id)

        if question.get("leaked") or str(question.get("status", "")).lower() == "leaked":
            leaked.append(question_id)

        results = question.get("outcomes")
        if isinstance(results, list):
            for row in results:
                if not isinstance(row, dict):
                    continue
                group = str(row.get("group", "")).strip()
                assessed = row.get("assessed")
                passed = row.get("passed")
                if not group or not isinstance(assessed, int) or not isinstance(passed, int):
                    continue
                if passed > assessed:
                    errors.append(f"{question_id}: group {group} has more passes than assessments")
                    continue
                outcomes[group]["assessed"] += assessed
                outcomes[group]["passed"] += passed

    missing_competencies = [name for name in required_competencies if competency_counts[name] == 0]
    for name in missing_competencies:
        errors.append(f"required competency has no question: {name}")

    if unanchored:
        errors.append(
            f"{len(unanchored)} question(s) carry fewer than two answer anchors: {', '.join(unanchored[:6])}"
        )
    if leaked:
        warnings.append(f"{len(leaked)} question(s) flagged leaked and still in the bank: {', '.join(leaked[:6])}")

    total_scored = sum(difficulty_counts.values())
    if total_scored:
        for level in DIFFICULTY_ORDER:
            share = difficulty_counts[level] / total_scored
            if share > 0.60:
                warnings.append(f"difficulty is unbalanced: {share:.0%} of questions are {level}")

    if competency_counts:
        heaviest, count = competency_counts.most_common(1)[0]
        if count / len(questions) > 0.50:
            warnings.append(f"{heaviest} carries {count / len(questions):.0%} of the bank; the interview measures one thing repeatedly")

    duplicates: list[tuple[str, str, float]] = []
    ids = sorted(tokens)
    for left_index, left in enumerate(ids):
        for right in ids[left_index + 1:]:
            score = jaccard(tokens[left], tokens[right])
            if score >= similarity:
                duplicates.append((left, right, round(score, 2)))
    for left, right, score in duplicates[:10]:
        warnings.append(f"{left} and {right} overlap {score:.0%}; they may double-count one signal")

    impact: dict[str, Any] = {}
    if outcomes:
        rates = {
            group: (values["passed"] / values["assessed"], values["assessed"])
            for group, values in outcomes.items()
            if values["assessed"] > 0
        }
        if rates:
            best_group = max(rates, key=lambda name: rates[name][0])
            best_rate = rates[best_group][0]
            impact = {"reference_group": best_group, "reference_rate": round(best_rate, 3), "groups": {}}
            for group, (rate, assessed) in sorted(rates.items()):
                ratio = round(rate / best_rate, 2) if best_rate else float("nan")
                impact["groups"][group] = {"rate": round(rate, 3), "assessed": assessed, "ratio": ratio}
                if assessed < MIN_GROUP_SIZE:
                    warnings.append(f"group {group} has {assessed} assessments; below {MIN_GROUP_SIZE} the ratio is too noisy to act on")
                elif ratio < ADVERSE_IMPACT_RATIO:
                    warnings.append(
                        f"group {group} selection-rate ratio is {ratio:.2f} against {best_group}; "
                        f"below {ADVERSE_IMPACT_RATIO:.2f} this is a signal to investigate the questions, not a finding"
                    )

    summary = {
        "questions": len(questions),
        "competencies": dict(competency_counts),
        "difficulty": dict(difficulty_counts),
        "duplicates": len(duplicates),
        "leaked": len(leaked),
        "adverse_impact": impact,
    }
    return errors, warnings, summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("bank", type=Path, help="question bank as JSON")
    parser.add_argument("--similarity", type=float, default=0.60, help="token overlap that counts as redundant (default 0.60)")
    parser.add_argument("--strict", action="store_true", help="treat warnings as failures")
    args = parser.parse_args()

    if not args.bank.is_file():
        print(f"ERROR: no such file: {args.bank}")
        sys.exit(2)
    try:
        bank = json.loads(args.bank.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"ERROR: invalid JSON: {exc}")
        sys.exit(2)

    errors, warnings, summary = audit(bank, args.similarity)
    for error in errors:
        print(f"ERROR: {error}")
    for warning in warnings:
        print(f"WARNING: {warning}")

    if summary:
        print(f"questions: {summary['questions']}  competencies covered: {len(summary['competencies'])}  redundant pairs: {summary['duplicates']}")
        if summary["difficulty"]:
            print("difficulty: " + ", ".join(f"{level}={summary['difficulty'].get(level, 0)}" for level in DIFFICULTY_ORDER))
        impact = summary["adverse_impact"]
        if impact:
            print(f"selection rates against {impact['reference_group']} ({impact['reference_rate']:.1%}):")
            for group, values in impact["groups"].items():
                print(f"  {group}: {values['rate']:.1%} of {values['assessed']} assessed, ratio {values['ratio']:.2f}")
            print("NOTE: the ratio is a screening signal only. It is not proof of discrimination, and a ratio above 0.80 is not proof of fairness.")

    if errors:
        print(f"FAILED: {len(errors)} bank error(s)")
        sys.exit(1)
    if warnings and args.strict:
        print(f"FAILED: {len(warnings)} warning(s) under --strict")
        sys.exit(1)
    if warnings:
        print(f"PASS WITH WARNINGS: {len(warnings)} item(s) to review before the bank goes live")
        sys.exit(0)
    print("PASS: the bank covers every required competency, is anchored, and shows no structural imbalance")


if __name__ == "__main__":
    main()
