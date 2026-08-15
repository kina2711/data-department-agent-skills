#!/usr/bin/env python3
"""Build a bounded, read-only context pack for moving to the next skill."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from validate_learning_memory import validate

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


def parse_date(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def trim(value: Any, limit: int = 500) -> str:
    text = str(value or "").strip()
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def compact(topic: dict, direct: bool) -> dict:
    payload = {
        "topic_id": topic.get("topic_id"),
        "status": topic.get("status"),
        "mastery_level": topic.get("mastery_level"),
        "summary": trim(topic.get("compact_summary")),
        "evidence_refs": list(topic.get("evidence_refs", []))[:8],
        "source_version": topic.get("source_version", ""),
    }
    if direct:
        payload.update({
            "interfaces": list(topic.get("interfaces", []))[:6],
            "decision_rules": list(topic.get("decision_rules", []))[:6],
            "failure_modes": list(topic.get("failure_modes", []))[:6],
        })
    return payload


def estimate_tokens(payload: dict) -> int:
    return round(len(json.dumps(payload, ensure_ascii=False).split()) * 1.33)


def build(memory: dict, next_topic_id: str, required: set[str], budget: int, current_versions: dict[str, str]) -> dict:
    topics = {str(item.get("topic_id")): item for item in memory.get("topics", []) if isinstance(item, dict)}
    next_topic = topics.get(next_topic_id, {})
    direct = set(map(str, next_topic.get("prerequisites", []))) | required
    selected = [
        item for topic_id, item in topics.items()
        if topic_id in direct or next_topic_id in set(map(str, item.get("relevance_to", [])))
    ]
    now = datetime.now(timezone.utc)
    result = {
        "memory_id": memory.get("memory_id", ""),
        "memory_version": memory.get("version", ""),
        "next_topic": next_topic_id,
        "generated_at": now.isoformat(),
        "token_budget": budget,
        "reuse_without_reteaching": [],
        "bridge_summaries": [],
        "expand_or_retest": [],
        "unknown_or_conflicted": [],
        "evidence_refs": [],
        "limitations": [],
        "status": "ready",
    }
    for topic in sorted(selected, key=lambda item: str(item.get("topic_id"))):
        topic_id = str(topic.get("topic_id"))
        status = topic.get("status")
        review_due = parse_date(topic.get("review_due_at"))
        fresh = review_due is not None and review_due >= now
        is_direct = topic_id in direct
        safety_critical = bool(topic.get("safety_critical", False))
        expected_version = current_versions.get(topic_id)
        version_shifted = bool(expected_version and expected_version != str(topic.get("source_version", "")))
        entry = compact(topic, is_direct or safety_critical)
        result["evidence_refs"].extend(entry.get("evidence_refs", []))
        if status == "mastered" and fresh and not safety_critical and not version_shifted:
            target = "bridge_summaries" if is_direct else "reuse_without_reteaching"
            result[target].append(entry)
        elif status in {"conflicted", "unseen", "retired"}:
            entry["reason"] = "unknown, conflicted or retired memory cannot be reused"
            result["unknown_or_conflicted"].append(entry)
        else:
            reasons = []
            if status != "mastered":
                reasons.append(f"status={status}")
            if not fresh:
                reasons.append("review is due or missing")
            if safety_critical:
                reasons.append("safety-critical prerequisite")
            if version_shifted:
                reasons.append(f"source version changed to {expected_version}")
            entry["reason"] = "; ".join(reasons)
            result["expand_or_retest"].append(entry)
    if not selected:
        result["limitations"].append("No relevant prior topics were found; do not infer prior mastery.")
    result["evidence_refs"] = sorted(set(map(str, result["evidence_refs"])))
    while estimate_tokens(result) > budget and result["reuse_without_reteaching"]:
        result["reuse_without_reteaching"].pop()
        if "Indirect mastered summaries were trimmed to meet the token budget." not in result["limitations"]:
            result["limitations"].append("Indirect mastered summaries were trimmed to meet the token budget.")
    result["estimated_tokens"] = estimate_tokens(result)
    if result["estimated_tokens"] > budget:
        result["status"] = "blocked"
        result["limitations"].append("Required bridge/retest material exceeds the requested budget; increase it or narrow scope. No over-budget context may be consumed.")
    return result


def parse_versions(values: list[str]) -> dict[str, str]:
    versions: dict[str, str] = {}
    for value in values:
        topic, separator, version = value.partition("=")
        if not separator or not topic.strip() or not version.strip():
            raise ValueError(f"invalid --current-version {value!r}; expected topic=version")
        versions[topic.strip()] = version.strip()
    return versions


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("memory", type=Path)
    parser.add_argument("--next-topic", required=True)
    parser.add_argument("--required-topic", action="append", default=[])
    parser.add_argument("--current-version", action="append", default=[], metavar="TOPIC=VERSION")
    parser.add_argument("--token-budget", type=int, default=1000)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.token_budget < 200:
        print("ERROR: token budget must be at least 200", file=sys.stderr)
        raise SystemExit(1)
    try:
        memory = json.loads(args.memory.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: invalid memory JSON: {exc}", file=sys.stderr)
        raise SystemExit(1)
    memory_errors = validate(memory, "complete")
    if memory_errors:
        print(json.dumps({"status": "blocked", "reason": "learner-memory validation failed", "errors": memory_errors}, ensure_ascii=False, indent=2), file=sys.stderr)
        raise SystemExit(2)
    try:
        current_versions = parse_versions(args.current_version)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
    result = build(memory, args.next_topic, set(args.required_topic), args.token_budget, current_versions)
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
        print(f"WROTE: {args.output.resolve()}")
    else:
        print(rendered, end="")
    if result["status"] == "blocked":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
