#!/usr/bin/env python3
"""Validate cross-skill learner memory without mutating it."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

TOPIC_STATUSES = {"unseen", "exposed", "practiced", "demonstrated", "mastered", "stale", "conflicted", "retired"}
EVIDENCE_STATUSES = {"unverified", "verified", "expired", "rejected"}
EVIDENCE_TYPES = {"learning", "practice", "project", "assessment", "production", "teaching", "review", "reflection"}
TRANSFER_SCOPES = {"not-applicable", "same-context", "changed-scenario"}
EVENT_TYPES = {"learned", "practiced", "applied", "assessed", "reviewed", "forgotten", "version-changed"}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def valid_date(value: Any) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


def unique_id_records(records: Any, key: str, label: str, errors: list[str]) -> tuple[list[dict], set[str]]:
    if not isinstance(records, list):
        errors.append(f"{label} must be an array")
        return [], set()
    valid: list[dict] = []
    identifiers: set[str] = set()
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            errors.append(f"{label}[{index}] must be an object")
            continue
        identifier = str(record.get(key, "")).strip()
        if not identifier:
            errors.append(f"{label}[{index}].{key} is required")
        elif identifier in identifiers:
            errors.append(f"{label}: duplicate {key} {identifier}")
        else:
            identifiers.add(identifier)
        valid.append(record)
    return valid, identifiers


def validate(memory: Any, mode: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(memory, dict):
        return ["memory must be an object"]
    for field in ("memory_id", "person_id", "version", "updated_at"):
        if not str(memory.get(field, "")).strip():
            errors.append(f"{field} is required")
    if memory.get("privacy_classification") not in {"private", "confidential", "restricted"}:
        errors.append("invalid privacy_classification")
    if memory.get("status") not in {"draft", "active", "conflicted", "archived"}:
        errors.append("invalid status")
    if not valid_date(memory.get("updated_at")):
        errors.append("updated_at must be an ISO date/time")

    authority = memory.get("authority")
    if not isinstance(authority, dict):
        errors.append("authority must be an object")
    else:
        for field in ("owner", "canonical_path", "storage_scope"):
            if not str(authority.get(field, "")).strip():
                errors.append(f"authority.{field} is required")
        if authority.get("storage_scope") not in {"project", "user", "second-brain"}:
            errors.append("invalid authority.storage_scope")

    evidence, evidence_ids = unique_id_records(memory.get("evidence_registry"), "evidence_id", "evidence_registry", errors)
    evidence_by_id = {str(item.get("evidence_id")): item for item in evidence}
    for index, item in enumerate(evidence):
        label = f"evidence_registry[{index}]"
        if item.get("type") not in EVIDENCE_TYPES:
            errors.append(f"{label}: invalid type")
        if item.get("validity_status") not in EVIDENCE_STATUSES:
            errors.append(f"{label}: invalid validity_status")
        if item.get("transfer_scope") not in TRANSFER_SCOPES:
            errors.append(f"{label}: invalid transfer_scope")
        if not str(item.get("locator", "")).strip() or not str(item.get("scope", "")).strip():
            errors.append(f"{label}: locator and scope are required")
        digest = str(item.get("sha256", ""))
        if digest and not re.fullmatch(r"[a-fA-F0-9]{64}", digest):
            errors.append(f"{label}.sha256 is invalid")
        if item.get("validity_status") == "verified" and not valid_date(item.get("validated_at")):
            errors.append(f"{label}: verified evidence needs validated_at")

    topics, topic_ids = unique_id_records(memory.get("topics"), "topic_id", "topics", errors)
    for index, topic in enumerate(topics):
        label = f"topics[{index}]"
        for field in ("topic_id", "display_name", "compact_summary", "last_learned_at", "last_demonstrated_at", "review_due_at", "source_version"):
            if field not in topic:
                errors.append(f"{label}.{field} is required")
        status = topic.get("status")
        if status not in TOPIC_STATUSES:
            errors.append(f"{label}: invalid status")
        level = topic.get("mastery_level")
        confidence = topic.get("confidence")
        if not isinstance(level, int) or not 0 <= level <= 6:
            errors.append(f"{label}.mastery_level must be 0..6")
        if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
            errors.append(f"{label}.confidence must be 0..1")
        for field in ("skill_ids", "concepts", "decision_rules", "interfaces", "failure_modes", "prerequisites", "relevance_to", "evidence_refs", "limitations"):
            if not isinstance(topic.get(field), list):
                errors.append(f"{label}.{field} must be an array")
        unknown_evidence = sorted(set(map(str, topic.get("evidence_refs", []))) - evidence_ids)
        if unknown_evidence:
            errors.append(f"{label}: unknown evidence_refs {unknown_evidence}")
        unknown_prerequisites = sorted(set(map(str, topic.get("prerequisites", []))) - topic_ids)
        if unknown_prerequisites:
            errors.append(f"{label}: unknown prerequisites {unknown_prerequisites}")
        if status == "mastered":
            verified = [ref for ref in topic.get("evidence_refs", []) if evidence_by_id.get(str(ref), {}).get("validity_status") == "verified"]
            applied = [ref for ref in verified if evidence_by_id[str(ref)].get("type") in {"project", "production", "teaching"}]
            transfer = [ref for ref in verified if evidence_by_id[str(ref)].get("transfer_scope") == "changed-scenario"]
            if not isinstance(level, int) or level < 4:
                errors.append(f"{label}: mastered requires mastery_level >= 4")
            if not isinstance(confidence, (int, float)) or confidence < 0.7:
                errors.append(f"{label}: mastered requires confidence >= 0.7")
            if not verified:
                errors.append(f"{label}: mastered requires verified evidence")
            if not applied:
                errors.append(f"{label}: mastered requires verified project, production or teaching evidence")
            if not transfer:
                errors.append(f"{label}: mastered requires verified changed-scenario transfer evidence")
            if not str(topic.get("compact_summary", "")).strip():
                errors.append(f"{label}: mastered requires compact_summary")
            if not valid_date(topic.get("last_demonstrated_at")) or not valid_date(topic.get("review_due_at")):
                errors.append(f"{label}: mastered requires demonstration and review dates")

    events, _ = unique_id_records(memory.get("learning_events"), "event_id", "learning_events", errors)
    for index, event in enumerate(events):
        label = f"learning_events[{index}]"
        if event.get("event_type") not in EVENT_TYPES:
            errors.append(f"{label}: invalid event_type")
        if event.get("topic_id") not in topic_ids:
            errors.append(f"{label}: unknown topic_id {event.get('topic_id')!r}")
        unknown = sorted(set(map(str, event.get("evidence_refs", []))) - evidence_ids)
        if unknown:
            errors.append(f"{label}: unknown evidence_refs {unknown}")
        if not valid_date(event.get("occurred_at")) or not valid_date(event.get("recorded_at")):
            errors.append(f"{label}: occurred_at and recorded_at must be ISO date/time")

    focus = memory.get("current_focus")
    if not isinstance(focus, list):
        errors.append("current_focus must be an array")
    else:
        unknown_focus = sorted(set(map(str, focus)) - topic_ids)
        if unknown_focus:
            errors.append(f"current_focus contains unknown topics {unknown_focus}")
    if mode == "complete":
        if memory.get("status") != "active":
            errors.append("complete mode requires status active")
        if not topics:
            errors.append("complete mode requires at least one topic")
        if any(topic.get("status") == "conflicted" for topic in topics):
            errors.append("complete mode cannot contain unresolved conflicted topics")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("memory", type=Path)
    parser.add_argument("--mode", choices=("plan", "complete"), default="plan")
    args = parser.parse_args()
    try:
        memory = load_json(args.memory)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: invalid memory JSON: {exc}")
        raise SystemExit(1)
    errors = validate(memory, args.mode)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"FAILED: {len(errors)} learner-memory validation error(s)")
        raise SystemExit(1)
    print("PASS: learner identity, topics, mastery evidence, events, freshness and cross-skill references are valid")


if __name__ == "__main__":
    main()
