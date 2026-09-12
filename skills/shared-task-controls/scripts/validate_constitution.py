#!/usr/bin/env python3
"""Validate a project constitution and check proposed work against its locked decisions.

Spec-driven development fails when an agent quietly renegotiates a settled decision. This
control makes that renegotiation detectable: a locked technology or a blocking architecture
rule can only change through an explicit, approved amendment, never as a side effect of
implementing a feature.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ENFORCEMENT = {"blocking", "review-required", "advisory"}
ID_RE = re.compile(r"^[A-Z]+-[0-9]+$")
SEMVER_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
REQUIRED = (
    "constitution_id", "project", "version", "ratified_at", "ratified_by",
    "principles", "technology_stack", "architecture_rules", "amendment_policy",
)


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_document(doc: Any, source: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(doc, dict):
        return [f"{source}: constitution must be an object"]
    for field in REQUIRED:
        if field not in doc:
            errors.append(f"{source}: missing {field}")
    unknown = sorted(set(doc) - set(REQUIRED))
    if unknown:
        errors.append(f"{source}: unsupported fields {unknown}")
    if not SEMVER_RE.fullmatch(str(doc.get("version", ""))):
        errors.append(f"{source}: version must be semantic (MAJOR.MINOR.PATCH)")
    for field in ("constitution_id", "project", "ratified_at", "ratified_by"):
        if not str(doc.get(field, "")).strip():
            errors.append(f"{source}: {field} must not be empty")

    seen_ids: set[str] = set()
    principles = doc.get("principles")
    if not isinstance(principles, list) or not principles:
        errors.append(f"{source}: principles must be a non-empty array")
    else:
        for index, item in enumerate(principles):
            label = f"{source}: principles[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{label}: must be an object")
                continue
            if not ID_RE.fullmatch(str(item.get("id", ""))):
                errors.append(f"{label}: id must look like 'ARCH-1'")
            elif item["id"] in seen_ids:
                errors.append(f"{label}: duplicate id {item['id']}")
            else:
                seen_ids.add(item["id"])
            if item.get("enforcement") not in ENFORCEMENT:
                errors.append(f"{label}: invalid enforcement {item.get('enforcement')!r}")
            for field in ("statement", "rationale"):
                if not str(item.get(field, "")).strip():
                    errors.append(f"{label}: {field} must not be empty")

    stack = doc.get("technology_stack")
    if not isinstance(stack, list) or not stack:
        errors.append(f"{source}: technology_stack must be a non-empty array")
    else:
        layers: set[str] = set()
        for index, item in enumerate(stack):
            label = f"{source}: technology_stack[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{label}: must be an object")
                continue
            layer = str(item.get("layer", "")).strip().lower()
            if not layer:
                errors.append(f"{label}: layer must not be empty")
            elif layer in layers:
                errors.append(f"{label}: duplicate layer {layer!r}; one layer holds one decision")
            else:
                layers.add(layer)
            if not isinstance(item.get("locked"), bool):
                errors.append(f"{label}: locked must be true or false")
            for field in ("technology", "version_constraint", "decided_in"):
                if not str(item.get(field, "")).strip():
                    errors.append(f"{label}: {field} must not be empty")

    rules = doc.get("architecture_rules")
    if not isinstance(rules, list) or not rules:
        errors.append(f"{source}: architecture_rules must be a non-empty array")
    else:
        for index, item in enumerate(rules):
            label = f"{source}: architecture_rules[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{label}: must be an object")
                continue
            if not ID_RE.fullmatch(str(item.get("id", ""))):
                errors.append(f"{label}: id must look like 'DEP-1'")
            elif item["id"] in seen_ids:
                errors.append(f"{label}: duplicate id {item['id']}")
            else:
                seen_ids.add(item["id"])
            if item.get("enforcement") not in ENFORCEMENT:
                errors.append(f"{label}: invalid enforcement {item.get('enforcement')!r}")
            if not str(item.get("rule", "")).strip():
                errors.append(f"{label}: rule must not be empty")

    policy = doc.get("amendment_policy")
    if not isinstance(policy, dict):
        errors.append(f"{source}: amendment_policy must be an object")
    else:
        if not str(policy.get("requires_approval_from", "")).strip():
            errors.append(f"{source}: amendment_policy must name an approving authority")
        if policy.get("requires_version_bump") is not True:
            errors.append(
                f"{source}: amendment_policy must require a version bump; "
                "silent amendment is the failure this control prevents"
            )
    return errors


def compare_versions(previous: dict[str, Any], current: dict[str, Any]) -> list[str]:
    """An amendment that changes a locked decision must be explicit and versioned."""
    findings: list[str] = []
    if str(previous.get("version")) == str(current.get("version")):
        same_stack = previous.get("technology_stack") == current.get("technology_stack")
        same_rules = previous.get("architecture_rules") == current.get("architecture_rules")
        if not (same_stack and same_rules):
            findings.append(
                f"constitution changed without a version bump (still {current.get('version')}); "
                "an amendment requires a new version and named approval"
            )
    locked_before = {
        str(item.get("layer", "")).lower(): item
        for item in previous.get("technology_stack", [])
        if isinstance(item, dict) and item.get("locked")
    }
    current_by_layer = {
        str(item.get("layer", "")).lower(): item
        for item in current.get("technology_stack", [])
        if isinstance(item, dict)
    }
    for layer, before in locked_before.items():
        after = current_by_layer.get(layer)
        if after is None:
            findings.append(f"locked layer {layer!r} was removed from the constitution")
            continue
        if str(after.get("technology")) != str(before.get("technology")):
            findings.append(
                f"locked layer {layer!r} changed technology "
                f"{before.get('technology')!r} -> {after.get('technology')!r}"
            )
        if str(after.get("version_constraint")) != str(before.get("version_constraint")):
            findings.append(
                f"locked layer {layer!r} changed version constraint "
                f"{before.get('version_constraint')!r} -> {after.get('version_constraint')!r}"
            )
        if not after.get("locked"):
            findings.append(f"locked layer {layer!r} was silently unlocked")
    blocking_before = {
        str(item.get("id")): item
        for item in previous.get("architecture_rules", [])
        if isinstance(item, dict) and item.get("enforcement") == "blocking"
    }
    current_rules = {
        str(item.get("id")): item
        for item in current.get("architecture_rules", [])
        if isinstance(item, dict)
    }
    for rule_id, before in blocking_before.items():
        after = current_rules.get(rule_id)
        if after is None:
            findings.append(f"blocking architecture rule {rule_id} was removed")
        elif str(after.get("rule")) != str(before.get("rule")):
            findings.append(f"blocking architecture rule {rule_id} was reworded")
        elif after.get("enforcement") != "blocking":
            findings.append(
                f"blocking architecture rule {rule_id} was downgraded to {after.get('enforcement')!r}"
            )
    return findings


def check_proposal(doc: dict[str, Any], proposal: str) -> list[str]:
    """Flag a proposed technology that competes with a locked layer."""
    findings: list[str] = []
    text = proposal.lower()
    for item in doc.get("technology_stack", []):
        if not isinstance(item, dict) or not item.get("locked"):
            continue
        technology = str(item.get("technology", "")).lower()
        layer = str(item.get("layer", ""))
        for rejected in item.get("alternatives_rejected", []):
            candidate = str(rejected).lower()
            if not candidate:
                continue
            if re.search(rf"\b{re.escape(candidate)}\b", text) and technology not in text:
                findings.append(
                    f"proposal names {rejected!r} for locked layer {layer!r}, which is decided as "
                    f"{item.get('technology')!r} in {item.get('decided_in')}"
                )
    return findings


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("constitution", type=Path, help="project-constitution.json")
    parser.add_argument("--previous", type=Path, help="prior ratified version, to detect silent amendment")
    parser.add_argument("--proposal", help="proposed plan or change text to check against locked decisions")
    parser.add_argument("--proposal-file", type=Path, help="read the proposal text from a file")
    args = parser.parse_args()

    try:
        doc = load(args.constitution)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: invalid constitution JSON: {exc}")
        sys.exit(1)

    errors = validate_document(doc, str(args.constitution))
    violations: list[str] = []

    if args.previous is not None and not errors:
        try:
            previous = load(args.previous)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"ERROR: invalid previous constitution JSON: {exc}")
            sys.exit(1)
        violations.extend(compare_versions(previous, doc))

    proposal_text = args.proposal or ""
    if args.proposal_file is not None:
        try:
            proposal_text = f"{proposal_text}\n{args.proposal_file.read_text(encoding='utf-8')}"
        except OSError as exc:
            print(f"ERROR: unreadable proposal: {exc}")
            sys.exit(1)
    if proposal_text.strip() and not errors:
        violations.extend(check_proposal(doc, proposal_text))

    for error in errors:
        print(f"ERROR: {error}")
    for violation in violations:
        print(f"VIOLATION: {violation}")

    if errors:
        print(f"FAILED: {len(errors)} constitution validation error(s)")
        sys.exit(1)
    if violations:
        print(f"BLOCKED: {len(violations)} constitution violation(s); amend explicitly or change the plan")
        sys.exit(3)
    principles = len(doc.get("principles", []))
    locked = sum(1 for item in doc.get("technology_stack", []) if isinstance(item, dict) and item.get("locked"))
    print(
        f"PASS: constitution {doc.get('project')!r} v{doc.get('version')} is valid "
        f"({principles} principles, {locked} locked layers)"
    )


if __name__ == "__main__":
    main()
