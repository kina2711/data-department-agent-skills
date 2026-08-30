#!/usr/bin/env python3
"""Audit skill descriptions as the routing surface they actually are.

A skill's `description` is not documentation. It is the text a router reads to decide which skill
handles a request, so two descriptions that share vocabulary compete for the same requests, and a
description that never says what it is *not* for cannot lose that competition on purpose.

Three things are checked. Every description needs a trigger clause, because a feature list gives
a router nothing to match an intent against. Pairs whose vocabulary overlaps heavily are the
routing failures waiting to happen, and each of those pairs should have a confusion-pair
evaluation case pinning the intended winner. Descriptions that never name a boundary or redirect
are reported, since a skill that only advertises cannot decline.

It measures word overlap. It cannot tell whether the routing a description produces is the
routing anyone wanted; only an evaluation case can assert that.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
CASES = ROOT / "evaluations" / "confusion-pair-cases.yaml"

# Words carried by nearly every description in a data suite; counting them as shared vocabulary
# would make every pair look confusable and hide the pairs that really are.
STOPWORDS = set(
    """data with when work that this from into your which their using these those other where
    while being there about under after before claude should across through more than what them
    also only such very over each both same then they will been have has for the and use uses""".split()
)
OVERLAP_REPORT_THRESHOLD = 0.09
TRIGGER = re.compile(r"\bUse (for|when|whenever|it for|this for)\b", re.I)
BOUNDARY = re.compile(r"\b(never|not for|instead|route|rather than|belongs to|hand off|defer)\b", re.I)


def read_descriptions() -> dict[str, str]:
    out: dict[str, str] = {}
    for path in sorted(SKILLS.glob("*/SKILL.md")):
        text = path.read_text(encoding="utf-8")
        name = re.search(r"^name:\s*(.+)$", text, re.M)
        desc = re.search(r"^description:\s*(.+)$", text, re.M)
        if name and desc:
            out[name.group(1).strip()] = desc.group(1).strip()
    return out


def guarded_pairs() -> set[frozenset[str]]:
    """Pairs a confusion-pair case already pins to an intended winner."""
    try:
        text = CASES.read_text(encoding="utf-8")
    except OSError:
        return set()
    found = re.findall(r"expected_primary_skill:\s*(\S+)\s*\n\s*rejected_skill:\s*(\S+)", text)
    return {frozenset(pair) for pair in found}


def claim_span(description: str) -> str:
    """The part of a description that competes for requests.

    A sentence whose job is "this is not mine, it belongs to X" necessarily contains X's
    vocabulary, and scoring it as shared vocabulary punishes the one construct that actually
    prevents the confusion. Overlap is measured on what a description claims, not on what it
    disclaims.
    """
    keep = []
    for sentence in re.split(r"(?<=[.;])\s+", description):
        if BOUNDARY.search(sentence):
            continue
        keep.append(sentence)
    return " ".join(keep) or description


def vocabulary(description: str) -> set[str]:
    return set(re.findall(r"[a-z]{4,}", claim_span(description).lower())) - STOPWORDS


def audit(descriptions: dict[str, str], guarded: set[frozenset[str]]) -> tuple[list[str], list[str], dict]:
    errors: list[str] = []
    warnings: list[str] = []

    no_trigger = [n for n, d in descriptions.items() if not TRIGGER.search(d)]
    for name in no_trigger:
        errors.append(f"{name}: description has no trigger clause; a router cannot match an intent to a feature list")

    no_boundary = sorted(n for n, d in descriptions.items() if not BOUNDARY.search(d))

    names = sorted(descriptions)
    overlaps = []
    for i, left in enumerate(names):
        for right in names[i + 1:]:
            a, b = vocabulary(descriptions[left]), vocabulary(descriptions[right])
            union = a | b
            if not union:
                continue
            score = len(a & b) / len(union)
            if score >= OVERLAP_REPORT_THRESHOLD:
                overlaps.append({
                    "pair": [left, right],
                    "overlap": round(score, 3),
                    "shared": sorted(a & b),
                    "guarded": frozenset({left, right}) in guarded,
                })
    overlaps.sort(key=lambda o: -o["overlap"])

    for item in overlaps:
        if not item["guarded"]:
            warnings.append(
                f"{item['pair'][0]} ~ {item['pair'][1]} overlap {item['overlap']:.0%} "
                f"({', '.join(item['shared'][:5])}) with no confusion-pair case"
            )

    summary = {
        "skills": len(descriptions),
        "scored_on": "claim span only; redirect sentences are excluded from overlap",
        "median_length": sorted(len(d) for d in descriptions.values())[len(descriptions) // 2],
        "without_trigger": no_trigger,
        "without_boundary": no_boundary,
        "boundary_coverage": round(1 - len(no_boundary) / len(descriptions), 3) if descriptions else 0.0,
        "overlapping_pairs": overlaps,
        "unguarded_pairs": [o["pair"] for o in overlaps if not o["guarded"]],
        "errors": len(errors),
        "warnings": len(warnings),
    }
    return errors, warnings, summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--strict", action="store_true", help="treat warnings as failures")
    parser.add_argument("--report-out", type=Path)
    args = parser.parse_args()

    descriptions = read_descriptions()
    if not descriptions:
        print("ERROR: no SKILL.md descriptions found")
        sys.exit(1)

    errors, warnings, summary = audit(descriptions, guarded_pairs())
    for error in errors:
        print(f"ERROR: {error}")
    for warning in warnings:
        print(f"WARNING: {warning}")

    print(
        f"skills: {summary['skills']}  median description: {summary['median_length']} chars  "
        f"boundary coverage: {summary['boundary_coverage']:.0%}  "
        f"overlapping pairs: {len(summary['overlapping_pairs'])}  "
        f"unguarded: {len(summary['unguarded_pairs'])}"
    )
    if args.report_out:
        args.report_out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"report written: {args.report_out}")

    if errors:
        print(f"FAILED: {len(errors)} description error(s)")
        sys.exit(1)
    if warnings and args.strict:
        print(f"FAILED: {len(warnings)} warning(s) under --strict")
        sys.exit(1)
    if warnings:
        print(f"PASS WITH WARNINGS: {len(warnings)} pair(s) compete for requests with nothing pinning the winner")
        sys.exit(0)
    print("PASS: every description triggers, and every overlapping pair has a case pinning the winner")


if __name__ == "__main__":
    main()
