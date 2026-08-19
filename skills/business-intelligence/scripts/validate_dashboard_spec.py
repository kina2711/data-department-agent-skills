#!/usr/bin/env python3
"""Check a dashboard specification before it is built, not after users find the wrong number.

The defects that survive a BI review are structural: a visual bound to no governed metric, a
filter that changes the grain silently, two visuals showing the same measure at different
grains, colour carrying meaning with no non-colour encoding. Each is cheap to catch in the spec
and expensive to catch in production.

It checks the specification against itself and against the metric contract it names. It cannot
confirm the numbers are right, and it does not replace validating the dashboard against source.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

REQUIRED_SPEC = ("dashboard", "audience", "decisions", "grain", "visuals")
REQUIRED_VISUAL = ("id", "title", "type", "metrics", "grain")
COLOUR_ONLY_TYPES = {"heatmap", "choropleth", "treemap", "scatter"}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(spec: Any, metrics: set[str] | None) -> tuple[list[str], list[str], dict[str, Any]]:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(spec, dict):
        return [f"specification must be an object"], [], {}

    for field in REQUIRED_SPEC:
        if not spec.get(field):
            errors.append(f"missing {field}")
    decisions = spec.get("decisions")
    if isinstance(decisions, list) and not decisions:
        errors.append("decisions is empty; a dashboard that supports no named decision has no acceptance criterion")

    visuals = spec.get("visuals")
    if not isinstance(visuals, list) or not visuals:
        errors.append("visuals must be a non-empty array")
        return errors, warnings, {}

    seen_ids: set[str] = set()
    metric_grains: dict[str, set[str]] = defaultdict(set)
    referenced: set[str] = set()
    dashboard_grain = str(spec.get("grain", "")).strip()

    for index, visual in enumerate(visuals):
        label = f"visuals[{index}]"
        if not isinstance(visual, dict):
            errors.append(f"{label}: must be an object")
            continue
        visual_id = str(visual.get("id", "")).strip()
        label = visual_id or label
        for field in REQUIRED_VISUAL:
            if not visual.get(field):
                errors.append(f"{label}: missing {field}")
        if visual_id:
            if visual_id in seen_ids:
                errors.append(f"{label}: duplicate visual id")
            seen_ids.add(visual_id)

        visual_metrics = visual.get("metrics")
        if isinstance(visual_metrics, list):
            for name in visual_metrics:
                referenced.add(str(name))
                metric_grains[str(name)].add(str(visual.get("grain", "")).strip())
                if metrics is not None and str(name) not in metrics:
                    errors.append(
                        f"{label}: metric {name!r} is not in the metric contract; "
                        "a visual may not define its own measure"
                    )

        grain = str(visual.get("grain", "")).strip()
        if grain and dashboard_grain and grain != dashboard_grain and not visual.get("grain_change_reason"):
            errors.append(
                f"{label}: grain {grain!r} differs from the dashboard grain {dashboard_grain!r} "
                "with no grain_change_reason; a silent grain change is how two tiles disagree"
            )

        if str(visual.get("type", "")).lower() in COLOUR_ONLY_TYPES:
            if not visual.get("non_colour_encoding"):
                errors.append(
                    f"{label}: {visual.get('type')} carries meaning in colour alone; "
                    "declare non_colour_encoding (label, size, pattern or ordering)"
                )
        if not visual.get("null_handling"):
            warnings.append(f"{label}: no null_handling stated; blank and zero will look identical")
        if not visual.get("source_of_truth"):
            warnings.append(f"{label}: no source_of_truth recorded for traceability")

    for name, grains in sorted(metric_grains.items()):
        real = {grain for grain in grains if grain}
        if len(real) > 1:
            errors.append(
                f"metric {name!r} is shown at {len(real)} different grains ({', '.join(sorted(real))}); "
                "the same measure at two grains will be read as a contradiction"
            )

    filters = spec.get("filters", [])
    if isinstance(filters, list):
        for index, item in enumerate(filters):
            if isinstance(item, dict) and item.get("affects_grain") and not item.get("documented_effect"):
                errors.append(f"filters[{index}]: changes the grain with no documented_effect")

    unused = sorted(metrics - referenced) if metrics is not None else []
    summary = {
        "visuals": len(visuals),
        "metrics_referenced": len(referenced),
        "metrics_in_contract": len(metrics) if metrics is not None else None,
        "metrics_unused": unused,
        "errors": len(errors),
        "warnings": len(warnings),
    }
    return errors, warnings, summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", type=Path, help="dashboard specification JSON")
    parser.add_argument("--metric-contract", type=Path,
                        help="JSON array of governed metric names, or objects with a 'name' field")
    parser.add_argument("--strict", action="store_true", help="treat warnings as failures")
    args = parser.parse_args()

    try:
        spec = load(args.spec)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: unreadable specification: {exc}")
        sys.exit(1)

    metrics: set[str] | None = None
    if args.metric_contract is not None:
        try:
            payload = load(args.metric_contract)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"ERROR: unreadable metric contract: {exc}")
            sys.exit(1)
        if not isinstance(payload, list):
            print("ERROR: metric contract must be an array")
            sys.exit(1)
        metrics = {
            str(item.get("name")) if isinstance(item, dict) else str(item)
            for item in payload
        }

    errors, warnings, summary = validate(spec, metrics)
    for error in errors:
        print(f"ERROR: {error}")
    for warning in warnings:
        print(f"WARNING: {warning}")

    if summary:
        print(f"visuals: {summary['visuals']}  metrics referenced: {summary['metrics_referenced']}")
        if summary["metrics_unused"]:
            print(f"unused contract metrics: {', '.join(summary['metrics_unused'])}")
    if metrics is None:
        print("NOTE: no metric contract supplied; metric bindings were not verified")

    if errors:
        print(f"FAILED: {len(errors)} specification error(s)")
        sys.exit(1)
    if warnings and args.strict:
        print(f"FAILED: {len(warnings)} warning(s) under --strict")
        sys.exit(1)
    if warnings:
        print(f"PASS WITH WARNINGS: {len(warnings)} item(s) to confirm before build")
        sys.exit(0)
    print("PASS: specification is structurally consistent and every metric is governed")


if __name__ == "__main__":
    main()
