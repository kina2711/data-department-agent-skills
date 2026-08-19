#!/usr/bin/env python3
"""Check that governed assets actually carry the ownership, policy and retention they claim.

A governance register is easy to fill and easy to leave half-filled. The gap is invisible until
someone needs the owner of a restricted dataset and finds an empty field. This counts the gaps
per classification, so an assertion of coverage has to survive arithmetic.

It checks the register against itself. It cannot confirm that a named owner accepted the role,
that a policy is enforced in any system, or that the classification is correct.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CLASSIFICATIONS = ["public", "internal", "confidential", "restricted"]
# Higher classifications require strictly more control, so requirements accumulate.
REQUIRED_BY_CLASSIFICATION = {
    "public": ("owner",),
    "internal": ("owner", "steward"),
    "confidential": ("owner", "steward", "retention", "access_policy"),
    "restricted": ("owner", "steward", "retention", "access_policy", "last_reviewed_at", "lawful_basis"),
}
CERTIFIABLE_REQUIREMENTS = ("owner", "steward", "retention", "access_policy", "last_reviewed_at")
STALE_REVIEW_DAYS = 365


def parse_timestamp(value: Any) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None else parsed.replace(tzinfo=timezone.utc)


def audit(assets: list[Any], as_of: datetime) -> tuple[list[str], list[str], dict[str, Any]]:
    errors: list[str] = []
    gaps: list[str] = []
    by_classification: Counter = Counter()
    missing_fields: dict[str, Counter] = defaultdict(Counter)
    seen: set[str] = set()
    certified_incomplete = 0
    stale = 0

    for index, asset in enumerate(assets):
        label = f"asset[{index}]"
        if not isinstance(asset, dict):
            errors.append(f"{label}: each asset must be an object")
            continue
        name = str(asset.get("asset") or asset.get("name") or "").strip()
        if not name:
            errors.append(f"{label}: asset must be named")
            continue
        label = name
        if name in seen:
            errors.append(f"{label}: duplicate asset entry")
        seen.add(name)

        classification = str(asset.get("classification", "")).strip().lower()
        if classification not in REQUIRED_BY_CLASSIFICATION:
            errors.append(f"{label}: classification {classification!r} is not one of {CLASSIFICATIONS}")
            continue
        by_classification[classification] += 1

        for field in REQUIRED_BY_CLASSIFICATION[classification]:
            if not str(asset.get(field, "")).strip():
                gaps.append(f"{label} ({classification}): missing {field}")
                missing_fields[classification][field] += 1

        reviewed = parse_timestamp(asset.get("last_reviewed_at"))
        if reviewed is not None and (as_of - reviewed).days > STALE_REVIEW_DAYS:
            stale += 1
            gaps.append(
                f"{label} ({classification}): last reviewed {(as_of - reviewed).days} days ago; "
                f"a review older than {STALE_REVIEW_DAYS} days is not current evidence"
            )

        if asset.get("certified") is True:
            absent = [field for field in CERTIFIABLE_REQUIREMENTS if not str(asset.get(field, "")).strip()]
            if absent:
                certified_incomplete += 1
                gaps.append(
                    f"{label}: certified while missing {', '.join(absent)}; "
                    "certification cannot rest on an incomplete register"
                )

    total = sum(by_classification.values())
    summary = {
        "assets": total,
        "by_classification": dict(by_classification),
        "gaps": len(gaps),
        "coverage": round(1 - len(gaps) / total, 4) if total else 0.0,
        "missing_fields": {key: dict(value) for key, value in missing_fields.items()},
        "certified_but_incomplete": certified_incomplete,
        "stale_reviews": stale,
    }
    return errors, gaps, summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("register", type=Path, help="JSON array of governed assets")
    parser.add_argument("--as-of", help="ISO 8601 evaluation time (default: now, UTC)")
    parser.add_argument("--require-classification", choices=CLASSIFICATIONS,
                        help="fail on any gap at or above this classification")
    parser.add_argument("--report-out", type=Path)
    args = parser.parse_args()

    as_of = parse_timestamp(args.as_of) if args.as_of else datetime.now(timezone.utc)
    if as_of is None:
        print("ERROR: --as-of must be an ISO 8601 timestamp")
        sys.exit(1)

    try:
        assets = json.loads(args.register.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: unreadable register: {exc}")
        sys.exit(1)
    if not isinstance(assets, list):
        print("ERROR: register must be an array of assets")
        sys.exit(1)
    if not assets:
        print("EMPTY: the register lists no assets; coverage is unknown, not complete")
        sys.exit(1)

    errors, gaps, summary = audit(assets, as_of)
    for error in errors:
        print(f"ERROR: {error}")
    for gap in gaps:
        print(f"GAP: {gap}")

    print(f"assets: {summary['assets']}  gaps: {summary['gaps']}  coverage: {summary['coverage']:.1%}")
    for classification in CLASSIFICATIONS:
        count = summary["by_classification"].get(classification, 0)
        if count:
            missing = summary["missing_fields"].get(classification, {})
            detail = ", ".join(f"{field}={n}" for field, n in sorted(missing.items())) or "complete"
            print(f"  {classification:<13} {count:>4} asset(s)  {detail}")

    if args.report_out is not None:
        args.report_out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"report written: {args.report_out}")

    if errors:
        print(f"FAILED: {len(errors)} register error(s)")
        sys.exit(1)
    if args.require_classification:
        threshold = CLASSIFICATIONS.index(args.require_classification)
        blocking = [
            gap for gap in gaps
            if any(f"({name})" in gap for name in CLASSIFICATIONS[threshold:])
        ]
        if blocking:
            print(f"BLOCKED: {len(blocking)} gap(s) at or above {args.require_classification}")
            sys.exit(3)
    if gaps:
        print(f"INCOMPLETE: {len(gaps)} coverage gap(s); this is not a certified register")
        sys.exit(2)
    print("PASS: every asset carries the controls its classification requires")


if __name__ == "__main__":
    main()
