#!/usr/bin/env python3
"""Score and govern instincts: reusable patterns whose confidence comes from recorded outcomes.

An agent that "learns" by asserting a lesson after one lucky run has learned nothing. This
control stores a pattern only as a proposal, then moves it toward `active` on the strength of
counted outcomes, using the Wilson lower bound so a small sample cannot masquerade as
certainty. Failures pull confidence back down, and an instinct nobody has confirmed in a long
time weakens on its own rather than sitting at its best historical score forever.

It stores no transcripts, prompts, secrets or data values. An instinct is a trigger, an action,
a rationale and a count. If a pattern cannot be written without quoting user content, it is not
an instinct and must not be recorded here.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ID_RE = re.compile(r"^[a-z0-9-]{3,64}$")
STATUSES = {"proposed", "active", "weakening", "retired"}
REQUIRED = (
    "instinct_id", "scope", "trigger", "pattern", "rationale",
    "observations", "status", "created_at", "last_confirmed_at", "evidence", "user_content",
)
OPTIONAL = {"confidence", "counter_indications", "review_by", "superseded_by"}
PROMOTION_MIN_APPLIED = 5
PROMOTION_MIN_CONFIDENCE = 0.70
RETIREMENT_MAX_CONFIDENCE = 0.35
STALE_AFTER_DAYS = 90
SECRET_HINTS = re.compile(
    r"(?i)\b(password|passwd|secret|api[_-]?key|token|bearer|private[_-]?key|credential)\b"
)


def wilson_lower_bound(successes: int, trials: int, z: float = 1.96) -> float:
    """Lower bound of the success rate. Few observations means a low bound, by construction."""
    if trials <= 0:
        return 0.0
    phat = successes / trials
    denominator = 1 + z * z / trials
    centre = phat + z * z / (2 * trials)
    margin = z * math.sqrt((phat * (1 - phat) + z * z / (4 * trials)) / trials)
    return max(0.0, min(1.0, (centre - margin) / denominator))


def parse_timestamp(value: str) -> datetime | None:
    text = str(value).strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None else parsed.replace(tzinfo=timezone.utc)


def load_ledger(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".jsonl", ".ndjson"}:
        records = []
        for line in text.splitlines():
            if line.strip():
                records.append(json.loads(line))
        return records
    data = json.loads(text)
    return data if isinstance(data, list) else [data]


def save_ledger(path: Path, records: list[dict[str, Any]]) -> None:
    if path.suffix.lower() in {".jsonl", ".ndjson"}:
        body = "\n".join(json.dumps(record, ensure_ascii=False) for record in records) + "\n"
    else:
        body = json.dumps(records, ensure_ascii=False, indent=2) + "\n"
    path.write_text(body, encoding="utf-8")


def validate_record(record: Any, source: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(record, dict):
        return [f"{source}: instinct must be an object"]
    for field in REQUIRED:
        if field not in record:
            errors.append(f"{source}: missing {field}")
    unknown = sorted(set(record) - set(REQUIRED) - OPTIONAL)
    if unknown:
        errors.append(f"{source}: unsupported fields {unknown}")
    if not ID_RE.fullmatch(str(record.get("instinct_id", ""))):
        errors.append(f"{source}: instinct_id must be lowercase kebab-case")
    if not ID_RE.fullmatch(str(record.get("scope", ""))):
        errors.append(f"{source}: scope must name a skill or 'global'")
    if record.get("status") not in STATUSES:
        errors.append(f"{source}: invalid status {record.get('status')!r}")
    if record.get("user_content") is not None:
        errors.append(f"{source}: user_content must be null; instincts never store transcripts")

    for field in ("trigger", "pattern", "rationale"):
        value = str(record.get(field, ""))
        if len(value.strip()) < 8:
            errors.append(f"{source}: {field} must be a real sentence, not a stub")
        if SECRET_HINTS.search(value):
            errors.append(f"{source}: {field} looks like it contains a secret; instincts store patterns, not values")

    observations = record.get("observations")
    if not isinstance(observations, dict):
        errors.append(f"{source}: observations must be an object")
    else:
        applied = observations.get("applied")
        succeeded = observations.get("succeeded")
        failed = observations.get("failed")
        if not all(isinstance(value, int) and value >= 0 for value in (applied, succeeded, failed)):
            errors.append(f"{source}: observation counts must be non-negative integers")
        elif succeeded + failed > applied:
            errors.append(f"{source}: succeeded + failed ({succeeded + failed}) exceeds applied ({applied})")

    for field in ("created_at", "last_confirmed_at"):
        if parse_timestamp(record.get(field, "")) is None:
            errors.append(f"{source}: {field} must be an ISO 8601 timestamp")

    if record.get("status") == "active":
        if not record.get("evidence"):
            errors.append(f"{source}: an active instinct requires evidence references")
        if isinstance(observations, dict) and isinstance(observations.get("applied"), int):
            if observations["applied"] < PROMOTION_MIN_APPLIED:
                errors.append(
                    f"{source}: active requires at least {PROMOTION_MIN_APPLIED} applications, "
                    f"found {observations['applied']}"
                )
    return errors


def score(record: dict[str, Any], as_of: datetime) -> dict[str, Any]:
    observations = record.get("observations", {})
    applied = int(observations.get("applied", 0))
    succeeded = int(observations.get("succeeded", 0))
    confidence = wilson_lower_bound(succeeded, applied)

    confirmed = parse_timestamp(record.get("last_confirmed_at", ""))
    stale_days = (as_of - confirmed).days if confirmed else None
    status = record.get("status")

    if status != "retired":
        if confidence <= RETIREMENT_MAX_CONFIDENCE and applied >= PROMOTION_MIN_APPLIED:
            status = "retired"
        elif stale_days is not None and stale_days > STALE_AFTER_DAYS:
            status = "weakening"
        elif applied >= PROMOTION_MIN_APPLIED and confidence >= PROMOTION_MIN_CONFIDENCE:
            status = "active"
        else:
            status = "proposed"

    updated = dict(record)
    updated["confidence"] = round(confidence, 4)
    updated["status"] = status
    if confirmed is not None:
        updated["review_by"] = (confirmed + timedelta(days=STALE_AFTER_DAYS)).date().isoformat()
    return updated


def observe(record: dict[str, Any], outcome: str, evidence: str | None, now: datetime) -> dict[str, Any]:
    updated = dict(record)
    observations = dict(updated.get("observations", {"applied": 0, "succeeded": 0, "failed": 0}))
    observations["applied"] = int(observations.get("applied", 0)) + 1
    if outcome == "success":
        observations["succeeded"] = int(observations.get("succeeded", 0)) + 1
        updated["last_confirmed_at"] = now.isoformat()
    else:
        observations["failed"] = int(observations.get("failed", 0)) + 1
    updated["observations"] = observations
    if evidence:
        updated["evidence"] = sorted(set(list(updated.get("evidence", [])) + [evidence]))
    return updated


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger", type=Path, help="instinct ledger (.json or .jsonl)")
    parser.add_argument("--observe", help="instinct_id to record an application against")
    parser.add_argument("--outcome", choices=("success", "failure"), help="result of that application")
    parser.add_argument("--evidence", help="evidence or telemetry ID supporting this observation")
    parser.add_argument("--rescore", action="store_true", help="recompute confidence and status for every instinct")
    parser.add_argument("--scope", help="report only instincts in this scope")
    parser.add_argument("--as-of", help="ISO 8601 evaluation time (default: now, UTC)")
    parser.add_argument("--write", action="store_true", help="persist changes back to the ledger")
    args = parser.parse_args()

    as_of = parse_timestamp(args.as_of) if args.as_of else datetime.now(timezone.utc)
    if as_of is None:
        print("ERROR: --as-of must be an ISO 8601 timestamp")
        sys.exit(1)

    try:
        records = load_ledger(args.ledger)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: unreadable ledger: {exc}")
        sys.exit(1)

    errors: list[str] = []
    seen: set[str] = set()
    for index, record in enumerate(records):
        errors.extend(validate_record(record, f"{args.ledger}#{index}"))
        if isinstance(record, dict):
            instinct_id = str(record.get("instinct_id", ""))
            if instinct_id and instinct_id in seen:
                errors.append(f"duplicate instinct_id: {instinct_id}")
            seen.add(instinct_id)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"FAILED: {len(errors)} instinct validation error(s)")
        sys.exit(1)

    if args.observe:
        if not args.outcome:
            print("ERROR: --observe requires --outcome")
            sys.exit(1)
        matched = False
        for index, record in enumerate(records):
            if str(record.get("instinct_id")) == args.observe:
                records[index] = observe(record, args.outcome, args.evidence, as_of)
                matched = True
                break
        if not matched:
            print(f"ERROR: no instinct with id {args.observe!r}")
            sys.exit(1)

    if args.rescore or args.observe:
        records = [score(record, as_of) for record in records]

    shown = [
        record for record in records
        if not args.scope or str(record.get("scope")) == args.scope
    ]
    shown.sort(key=lambda record: (-float(record.get("confidence", 0)), str(record.get("instinct_id"))))

    for record in shown:
        observations = record.get("observations", {})
        print(
            f"{record.get('status', ''):<10} {float(record.get('confidence', 0)):.2f}  "
            f"{record.get('instinct_id')}  [{record.get('scope')}]  "
            f"{observations.get('succeeded', 0)}/{observations.get('applied', 0)} applied"
        )
        print(f"           when: {record.get('trigger')}")
        print(f"           then: {record.get('pattern')}")
        if record.get("status") == "weakening":
            print(f"           unconfirmed since {record.get('last_confirmed_at')}; re-test before relying on it")

    active = [record for record in records if record.get("status") == "active"]
    proposed = [record for record in records if record.get("status") == "proposed"]
    weakening = [record for record in records if record.get("status") == "weakening"]
    retired = [record for record in records if record.get("status") == "retired"]

    if args.write:
        save_ledger(args.ledger, records)
        print(f"ledger written: {args.ledger}")

    print(
        f"SUMMARY: {len(active)} active, {len(proposed)} proposed, "
        f"{len(weakening)} weakening, {len(retired)} retired"
    )
    print("Only 'active' instincts may shape behavior. Proposed and weakening ones are hypotheses.")


if __name__ == "__main__":
    main()
