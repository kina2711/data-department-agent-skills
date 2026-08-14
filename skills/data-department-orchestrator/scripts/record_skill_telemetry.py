#!/usr/bin/env python3
"""Validate and append one privacy-minimized telemetry event as JSONL."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ALLOWED = {"event_id", "occurred_at", "suite_version", "skill", "task_id", "route_source", "outcome", "duration_ms", "references_loaded", "token_estimate", "failure_codes", "user_content"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("event", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        event = json.loads(args.event.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: invalid event JSON: {exc}")
        sys.exit(1)
    errors = []
    extra = set(event) - ALLOWED if isinstance(event, dict) else {"not-an-object"}
    if extra:
        errors.append(f"unexpected fields may contain user content: {sorted(extra)}")
    required = ALLOWED - {"user_content"}
    for field in required:
        if field not in event:
            errors.append(f"missing {field}")
    if event.get("user_content") is not None:
        errors.append("user_content must be null or omitted")
    if not re.fullmatch(r"[a-z0-9-]{1,64}", str(event.get("skill", ""))):
        errors.append("invalid skill")
    if not re.fullmatch(r"[a-z0-9-]{1,64}", str(event.get("task_id", ""))):
        errors.append("invalid task_id")
    if event.get("route_source") not in {"implicit", "explicit", "orchestrated", "overridden"}:
        errors.append("invalid route_source")
    if event.get("outcome") not in {"complete", "blocked", "failed", "abandoned"}:
        errors.append("invalid outcome")
    if not isinstance(event.get("duration_ms"), int) or event.get("duration_ms", -1) < 0:
        errors.append("duration_ms must be a non-negative integer")
    if not isinstance(event.get("token_estimate"), int) or event.get("token_estimate", -1) < 0:
        errors.append("token_estimate must be a non-negative integer")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        sys.exit(1)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
    print(f"APPENDED: {args.output}")


if __name__ == "__main__":
    main()
