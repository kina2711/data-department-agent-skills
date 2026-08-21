#!/usr/bin/env python3
"""Summarize a Terraform plan and separate the destructive changes from the rest.

`terraform plan` output is read by a human under time pressure, and a single `-/+` on a stateful
resource scrolls past between forty additions. This reads the machine-readable plan
(`terraform show -json plan.tfplan`) and reports what would be destroyed or replaced, with
stateful resource types called out separately, so the approval decision is made against the
destructive set rather than against a diff summary line.

It reads the plan only. It never runs Terraform, never touches state, and cannot tell you whether
a destroy is safe — only that one is present and what it would take with it.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

# Types whose replacement destroys data rather than re-creating an interchangeable resource.
STATEFUL_HINTS = (
    "db_instance", "rds_cluster", "database", "bucket", "storage_account", "disk", "volume",
    "table", "dataset", "warehouse", "filesystem", "snapshot", "backup", "topic", "stream",
    "kinesis", "elasticache", "redshift", "bigquery", "snowflake", "efs", "fsx",
)
DESTRUCTIVE = {"delete", "replace"}


def classify(actions: list[str]) -> str:
    actions = [str(action) for action in actions]
    if actions == ["no-op"] or actions == []:
        return "no-op"
    if "create" in actions and "delete" in actions:
        return "replace"
    if actions == ["delete"]:
        return "delete"
    if actions == ["create"]:
        return "create"
    if actions == ["update"]:
        return "update"
    if actions == ["read"]:
        return "read"
    return "+".join(actions)


def is_stateful(resource_type: str) -> bool:
    lowered = resource_type.lower()
    return any(hint in lowered for hint in STATEFUL_HINTS)


def summarize(plan: Any) -> tuple[list[str], dict[str, Any]]:
    errors: list[str] = []
    if not isinstance(plan, dict):
        return ["plan must be a JSON object; pass the output of `terraform show -json`"], {}
    changes = plan.get("resource_changes")
    if changes is None:
        errors.append("no resource_changes key; this does not look like a `terraform show -json` plan")
        return errors, {}
    if not isinstance(changes, list):
        errors.append("resource_changes must be an array")
        return errors, {}

    counts: Counter[str] = Counter()
    by_type: defaultdict[str, Counter[str]] = defaultdict(Counter)
    destructive: list[dict[str, Any]] = []

    for entry in changes:
        if not isinstance(entry, dict):
            errors.append("resource_changes entry is not an object")
            continue
        address = str(entry.get("address", "<unknown>"))
        resource_type = str(entry.get("type", "<unknown>"))
        change = entry.get("change")
        actions = change.get("actions", []) if isinstance(change, dict) else []
        action = classify(list(actions) if isinstance(actions, list) else [])
        counts[action] += 1
        by_type[resource_type][action] += 1
        if action in DESTRUCTIVE:
            reasons = change.get("replace_paths") if isinstance(change, dict) else None
            destructive.append({
                "address": address,
                "type": resource_type,
                "action": action,
                "stateful": is_stateful(resource_type),
                "replace_paths": reasons if isinstance(reasons, list) else [],
            })

    stateful = [item for item in destructive if item["stateful"]]
    summary = {
        "total": len(changes),
        "counts": dict(counts),
        "destructive": destructive,
        "stateful_destructive": stateful,
        "types": {name: dict(actions) for name, actions in sorted(by_type.items())},
        "terraform_version": plan.get("terraform_version", "unknown"),
    }
    return errors, summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("plan", type=Path, help="plan JSON from `terraform show -json plan.tfplan`")
    parser.add_argument("--allow-destroy", action="store_true", help="a destroy or replace is expected and approved for this run")
    parser.add_argument("--show-types", action="store_true", help="print the per-resource-type breakdown")
    args = parser.parse_args()

    if not args.plan.is_file():
        print(f"ERROR: no such file: {args.plan}")
        sys.exit(2)
    try:
        plan = json.loads(args.plan.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"ERROR: invalid JSON: {exc}")
        sys.exit(2)

    errors, summary = summarize(plan)
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"FAILED: {len(errors)} plan error(s)")
        sys.exit(1)

    counts = summary["counts"]
    ordered = ", ".join(f"{action}={counts[action]}" for action in sorted(counts)) or "no changes"
    print(f"terraform {summary['terraform_version']}  resources: {summary['total']}  {ordered}")

    if args.show_types:
        for name, actions in summary["types"].items():
            rendered = ", ".join(f"{action}={count}" for action, count in sorted(actions.items()))
            print(f"  {name}: {rendered}")

    destructive = summary["destructive"]
    stateful = summary["stateful_destructive"]
    for item in destructive:
        marker = "STATEFUL " if item["stateful"] else ""
        paths = f" (forced by {', '.join(str(p) for p in item['replace_paths'])})" if item["replace_paths"] else ""
        print(f"{marker}{item['action'].upper()}: {item['address']}{paths}")

    if not destructive:
        print("PASS: no destroy or replace in this plan")
        return

    print(f"destructive changes: {len(destructive)} ({len(stateful)} on stateful resource types)")
    if not args.allow_destroy:
        print(
            "FAILED: the plan destroys or replaces resources and --allow-destroy was not given. "
            "Bind explicit, scoped, version-specific approval to this plan before applying."
        )
        sys.exit(1)
    if stateful:
        print(
            "PASS WITH WARNINGS: destroy is authorized, but stateful resources are in scope. "
            "Confirm a restorable backup and a tested recovery path before apply."
        )
        return
    print("PASS: destructive changes are authorized and no stateful resource type is affected")


if __name__ == "__main__":
    main()
