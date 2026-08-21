#!/usr/bin/env python3
"""Decide whether a model version may be promoted, against evidence rather than narrative.

Promotion is where the controls quietly fall away. A model beats the baseline on one aggregate
metric while regressing on a segment; the approval was granted for a different artifact hash; the
rollback plan exists as a sentence; monitors are named but not configured. Each of those is
checkable, and each of them is what the postmortem later says went wrong.

It validates a registry/promotion record against the gates it claims to have passed. It cannot
retrain, re-evaluate or deploy anything, and a passing record is authorization to proceed, not
proof the model is good.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REQUIRED_FIELDS = (
    "model_name", "version", "artifact_uri", "artifact_sha256",
    "training_data_ref", "evaluation", "monitoring", "rollback", "approval",
)
REQUIRED_MONITORS = ("prediction-drift", "input-drift", "performance", "availability")
VALID_STAGES = ("dev", "staging", "shadow", "canary", "production")


def check(record: Any, target_stage: str) -> tuple[list[str], list[str], dict[str, Any]]:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(record, dict):
        return ["promotion record must be a JSON object"], [], {}

    for field in REQUIRED_FIELDS:
        if not record.get(field):
            errors.append(f"missing {field}")

    stage = str(record.get("current_stage", "")).strip().lower()
    if stage and stage not in VALID_STAGES:
        warnings.append(f"current_stage {stage!r} is not one of {', '.join(VALID_STAGES)}")
    if target_stage == "production" and stage in {"dev", ""}:
        warnings.append(f"promoting straight from {stage or 'unknown'} to production skips staged exposure")

    evaluation = record.get("evaluation")
    metrics_checked = 0
    regressions: list[str] = []
    if isinstance(evaluation, dict):
        if not evaluation.get("dataset_ref"):
            errors.append("evaluation.dataset_ref is missing; a metric without a named dataset is not reproducible")
        if evaluation.get("evaluated_at") is None:
            warnings.append("evaluation.evaluated_at is missing; freshness of the result cannot be judged")
        metrics = evaluation.get("metrics")
        if not isinstance(metrics, list) or not metrics:
            errors.append("evaluation.metrics must be a non-empty array")
        else:
            for index, metric in enumerate(metrics):
                if not isinstance(metric, dict):
                    errors.append(f"evaluation.metrics[{index}]: must be an object")
                    continue
                name = str(metric.get("name", f"metric[{index}]"))
                value = metric.get("value")
                baseline = metric.get("baseline")
                threshold = metric.get("threshold")
                higher_is_better = metric.get("higher_is_better", True)
                if not isinstance(value, (int, float)) or isinstance(value, bool):
                    errors.append(f"{name}: value must be numeric")
                    continue
                metrics_checked += 1
                if isinstance(threshold, (int, float)) and not isinstance(threshold, bool):
                    fails = value < threshold if higher_is_better else value > threshold
                    if fails:
                        errors.append(f"{name}: {value:g} misses the promotion threshold {threshold:g}")
                if isinstance(baseline, (int, float)) and not isinstance(baseline, bool):
                    worse = value < baseline if higher_is_better else value > baseline
                    if worse:
                        regressions.append(f"{name} ({value:g} against baseline {baseline:g})")

        segments = evaluation.get("segments")
        if not isinstance(segments, list) or not segments:
            warnings.append("no segment results; an aggregate gain can hide a regression on the segment that matters")
        else:
            for segment in segments:
                if not isinstance(segment, dict):
                    continue
                name = str(segment.get("name", "segment"))
                value = segment.get("value")
                baseline = segment.get("baseline")
                if isinstance(value, (int, float)) and isinstance(baseline, (int, float)) and value < baseline:
                    regressions.append(f"segment {name} ({value:g} against {baseline:g})")

    if regressions:
        warnings.append(f"regression against baseline on: {', '.join(regressions)}")

    monitoring = record.get("monitoring")
    configured: list[str] = []
    if isinstance(monitoring, dict):
        monitors = monitoring.get("monitors")
        if isinstance(monitors, list):
            for monitor in monitors:
                if isinstance(monitor, dict) and str(monitor.get("status", "")).lower() in {"configured", "active", "enabled"}:
                    configured.append(str(monitor.get("type", monitor.get("name", ""))).lower())
                elif isinstance(monitor, str):
                    configured.append(monitor.lower())
    missing_monitors = [name for name in REQUIRED_MONITORS if name not in configured]
    if missing_monitors:
        if target_stage in {"production", "canary"}:
            errors.append(f"monitor(s) not configured for {target_stage}: {', '.join(missing_monitors)}")
        else:
            warnings.append(f"monitor(s) not configured: {', '.join(missing_monitors)}")

    rollback = record.get("rollback")
    if isinstance(rollback, dict):
        if not rollback.get("previous_version"):
            errors.append("rollback.previous_version is missing; there is nothing to roll back to")
        if not rollback.get("procedure"):
            errors.append("rollback.procedure is missing")
        if str(rollback.get("tested", "")).lower() not in {"true", "yes", "passed"} and rollback.get("tested") is not True:
            warnings.append("rollback has not been tested; an untested rollback is a plan, not a control")

    approval = record.get("approval")
    if isinstance(approval, dict):
        status = str(approval.get("status", "")).lower()
        if status != "approved":
            errors.append(f"approval status is {status or 'absent'}; promotion requires explicit approval")
        approved_hash = str(approval.get("artifact_sha256", "")).strip().lower()
        actual_hash = str(record.get("artifact_sha256", "")).strip().lower()
        if approved_hash and actual_hash and approved_hash != actual_hash:
            errors.append(
                "approval is bound to a different artifact hash; a changed artifact expires the decision"
            )
        elif not approved_hash:
            errors.append("approval is not bound to an artifact hash; scope cannot be verified")
        scope = str(approval.get("scope_stage", "")).lower()
        if scope and scope != target_stage:
            errors.append(f"approval is scoped to {scope}, not to {target_stage}")

    summary = {
        "model": record.get("model_name"),
        "version": record.get("version"),
        "target_stage": target_stage,
        "metrics_checked": metrics_checked,
        "monitors_configured": len([name for name in REQUIRED_MONITORS if name in configured]),
        "regressions": regressions,
    }
    return errors, warnings, summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("record", type=Path, help="model promotion/registry record as JSON")
    parser.add_argument("--target-stage", choices=VALID_STAGES, default="production")
    parser.add_argument("--strict", action="store_true", help="treat warnings as failures")
    args = parser.parse_args()

    if not args.record.is_file():
        print(f"ERROR: no such file: {args.record}")
        sys.exit(2)
    try:
        record = json.loads(args.record.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"ERROR: invalid JSON: {exc}")
        sys.exit(2)

    errors, warnings, summary = check(record, args.target_stage)
    for error in errors:
        print(f"ERROR: {error}")
    for warning in warnings:
        print(f"WARNING: {warning}")

    if summary:
        print(
            f"model: {summary['model']} v{summary['version']} -> {summary['target_stage']}  "
            f"metrics checked: {summary['metrics_checked']}  monitors configured: "
            f"{summary['monitors_configured']}/{len(REQUIRED_MONITORS)}"
        )

    if errors:
        print(f"BLOCKED: {len(errors)} promotion gate(s) unmet")
        sys.exit(1)
    if warnings and args.strict:
        print(f"BLOCKED: {len(warnings)} warning(s) under --strict")
        sys.exit(1)
    if warnings:
        print(f"PASS WITH WARNINGS: {len(warnings)} item(s) the approver must accept explicitly")
        sys.exit(0)
    print("PASS: evaluation, monitoring, rollback and hash-bound approval are all present for this stage")


if __name__ == "__main__":
    main()
