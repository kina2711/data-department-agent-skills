#!/usr/bin/env python3
"""Compare training and serving feature statistics before a model is blamed for the gap.

Training-serving skew is rarely exotic. A feature is missing at inference, a string column arrives
as an integer, a category the model never saw dominates traffic, or a mean has drifted far enough
that the learned thresholds no longer apply. Offline metrics stay excellent while online
performance decays, and the model gets the blame.

It compares two feature-statistics files and reports structural mismatches as errors and
distribution movement as warnings. It compares statistics, not raw data: it cannot see a leaked
label or a broken join, and it never reads production records.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

DEFAULT_MEAN_SHIFT = 0.25   # standard deviations
DEFAULT_MISSING_SHIFT = 0.05
DEFAULT_UNSEEN_SHARE = 0.01


def load(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and isinstance(data.get("features"), dict):
        return data["features"]
    if isinstance(data, dict) and isinstance(data.get("features"), list):
        return {str(item.get("name")): item for item in data["features"] if isinstance(item, dict) and item.get("name")}
    if not isinstance(data, dict):
        raise ValueError("expected an object of feature statistics")
    return data


def as_float(value: Any) -> float | None:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    return None


def compare(train: dict[str, Any], serve: dict[str, Any], mean_shift: float, missing_shift: float, unseen_share: float) -> tuple[list[str], list[str], dict[str, Any]]:
    errors: list[str] = []
    warnings: list[str] = []

    missing_at_serving = sorted(set(train) - set(serve))
    extra_at_serving = sorted(set(serve) - set(train))
    for name in missing_at_serving:
        errors.append(f"{name}: present in training, absent at serving; the model will impute or crash")
    for name in extra_at_serving:
        warnings.append(f"{name}: present at serving, absent in training; it is being computed and discarded")

    drifted: list[str] = []
    for name in sorted(set(train) & set(serve)):
        left = train[name] if isinstance(train[name], dict) else {}
        right = serve[name] if isinstance(serve[name], dict) else {}
        if not left or not right:
            warnings.append(f"{name}: statistics are not objects; skipped")
            continue

        left_type = str(left.get("dtype", left.get("type", ""))).lower()
        right_type = str(right.get("dtype", right.get("type", ""))).lower()
        if left_type and right_type and left_type != right_type:
            errors.append(f"{name}: dtype {left_type} in training against {right_type} at serving")

        left_missing = as_float(left.get("missing_rate"))
        right_missing = as_float(right.get("missing_rate"))
        if left_missing is not None and right_missing is not None:
            delta = right_missing - left_missing
            if abs(delta) > missing_shift:
                warnings.append(
                    f"{name}: missing rate moved {left_missing:.1%} -> {right_missing:.1%} ({delta:+.1%})"
                )

        left_mean, right_mean = as_float(left.get("mean")), as_float(right.get("mean"))
        left_std = as_float(left.get("std")) or as_float(left.get("stddev"))
        if left_mean is not None and right_mean is not None and left_std:
            shift = abs(right_mean - left_mean) / left_std
            if shift > mean_shift:
                drifted.append(name)
                warnings.append(
                    f"{name}: mean moved {shift:.2f} standard deviations ({left_mean:g} -> {right_mean:g})"
                )

        left_categories = left.get("categories")
        right_categories = right.get("categories")
        if isinstance(left_categories, (list, dict)) and isinstance(right_categories, (list, dict)):
            left_set = set(left_categories if isinstance(left_categories, list) else left_categories.keys())
            right_items = right_categories if isinstance(right_categories, dict) else {value: None for value in right_categories}
            unseen = sorted(set(right_items) - left_set)
            if unseen:
                if isinstance(right_categories, dict):
                    total = sum(value for value in right_categories.values() if isinstance(value, (int, float)))
                    unseen_weight = sum(
                        right_categories[value] for value in unseen if isinstance(right_categories.get(value), (int, float))
                    )
                    share = unseen_weight / total if total else 0.0
                    if share > unseen_share:
                        errors.append(
                            f"{name}: {len(unseen)} unseen category value(s) cover {share:.1%} of serving traffic: "
                            f"{', '.join(str(value) for value in unseen[:5])}"
                        )
                    else:
                        warnings.append(f"{name}: {len(unseen)} unseen category value(s), {share:.1%} of traffic")
                else:
                    warnings.append(f"{name}: {len(unseen)} category value(s) unseen in training: {', '.join(str(v) for v in unseen[:5])}")

    summary = {
        "compared": len(set(train) & set(serve)),
        "missing_at_serving": missing_at_serving,
        "extra_at_serving": extra_at_serving,
        "drifted": drifted,
    }
    return errors, warnings, summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("training", type=Path, help="training feature statistics as JSON")
    parser.add_argument("serving", type=Path, help="serving feature statistics as JSON")
    parser.add_argument("--mean-shift", type=float, default=DEFAULT_MEAN_SHIFT, help=f"standard deviations of mean movement to warn at (default {DEFAULT_MEAN_SHIFT})")
    parser.add_argument("--missing-shift", type=float, default=DEFAULT_MISSING_SHIFT, help=f"absolute missing-rate movement to warn at (default {DEFAULT_MISSING_SHIFT})")
    parser.add_argument("--unseen-share", type=float, default=DEFAULT_UNSEEN_SHARE, help=f"share of serving traffic in unseen categories that fails (default {DEFAULT_UNSEEN_SHARE})")
    parser.add_argument("--strict", action="store_true", help="treat warnings as failures")
    args = parser.parse_args()

    for path in (args.training, args.serving):
        if not path.is_file():
            print(f"ERROR: no such file: {path}")
            sys.exit(2)
    try:
        train = load(args.training)
        serve = load(args.serving)
    except (json.JSONDecodeError, ValueError) as exc:
        print(f"ERROR: could not read feature statistics: {exc}")
        sys.exit(2)

    errors, warnings, summary = compare(train, serve, args.mean_shift, args.missing_shift, args.unseen_share)
    for error in errors:
        print(f"ERROR: {error}")
    for warning in warnings:
        print(f"WARNING: {warning}")

    print(
        f"features compared: {summary['compared']}  missing at serving: {len(summary['missing_at_serving'])}  "
        f"unused at serving: {len(summary['extra_at_serving'])}  drifted means: {len(summary['drifted'])}"
    )

    if errors:
        print(f"FAILED: {len(errors)} structural mismatch(es) between training and serving")
        sys.exit(1)
    if warnings and args.strict:
        print(f"FAILED: {len(warnings)} warning(s) under --strict")
        sys.exit(1)
    if warnings:
        print(f"PASS WITH WARNINGS: {len(warnings)} distribution difference(s) to explain before or during rollout")
        sys.exit(0)
    print("PASS: the serving feature surface matches training in shape, type and distribution")


if __name__ == "__main__":
    main()
