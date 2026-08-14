#!/usr/bin/env python3
"""Validate CSV or JSONL records against a small, explicit JSON data contract."""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


NULLS = {"", "null", "none", "na", "n/a", "nan"}


def load_contract(path: Path) -> dict[str, Any]:
    contract = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(contract, dict):
        raise ValueError("contract must be a JSON object")
    columns = contract.get("columns", {})
    if isinstance(columns, list):
        columns = {item["name"]: {key: value for key, value in item.items() if key != "name"} for item in columns}
    if not isinstance(columns, dict) or not columns:
        raise ValueError("contract.columns must define at least one column")
    contract["columns"] = columns
    return contract


def read_rows(path: Path, kind: str) -> Iterable[tuple[int, dict[str, Any]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        if kind == "csv":
            for line_number, row in enumerate(csv.DictReader(handle), start=2):
                yield line_number, dict(row)
            return
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"JSONL line {line_number} is not an object")
            yield line_number, value


def is_null(value: Any) -> bool:
    return value is None or (isinstance(value, str) and value.strip().lower() in NULLS)


def parse_value(value: Any, kind: str) -> Any:
    if kind == "string":
        return str(value)
    if kind == "integer":
        if isinstance(value, bool):
            raise ValueError("boolean is not an integer")
        number = float(value)
        if not number.is_integer():
            raise ValueError("not an integer")
        return int(number)
    if kind == "float":
        if isinstance(value, bool):
            raise ValueError("boolean is not a float")
        return float(value)
    if kind == "boolean":
        if isinstance(value, bool):
            return value
        normalized = str(value).strip().lower()
        if normalized in {"true", "1", "yes", "y"}:
            return True
        if normalized in {"false", "0", "no", "n"}:
            return False
        raise ValueError("not a boolean")
    if kind == "date":
        return dt.date.fromisoformat(str(value).strip())
    if kind == "datetime":
        return dt.datetime.fromisoformat(str(value).strip().replace("Z", "+00:00"))
    raise ValueError(f"unsupported type {kind!r}")


def validate(input_path: Path, kind: str, contract: dict[str, Any], max_errors: int) -> dict[str, Any]:
    columns: dict[str, dict[str, Any]] = contract["columns"]
    errors: list[dict[str, Any]] = []
    counts: Counter[str] = Counter()
    unique_seen: dict[str, set[str]] = {name: set() for name, rule in columns.items() if rule.get("unique")}
    primary_key = contract.get("primary_key", [])
    if isinstance(primary_key, str):
        primary_key = [primary_key]
    key_seen: set[tuple[str, ...]] = set()
    row_count = 0

    def add_error(code: str, line: int | None, column: str | None, message: str, value: Any = None) -> None:
        counts[code] += 1
        if len(errors) < max_errors:
            item: dict[str, Any] = {"code": code, "line": line, "column": column, "message": message}
            if value is not None:
                item["value"] = str(value)[:200]
            errors.append(item)

    for line_number, row in read_rows(input_path, kind):
        row_count += 1
        for name, rule in columns.items():
            exists = name in row
            value = row.get(name)
            if rule.get("required", False) and not exists:
                add_error("required-column-missing", line_number, name, "required column is absent")
                continue
            if not exists:
                continue
            if is_null(value):
                if rule.get("nullable", True) is False:
                    add_error("null-not-allowed", line_number, name, "null value is not allowed")
                continue
            raw_text = str(value)
            parsed: Any = value
            expected_type = rule.get("type")
            if expected_type:
                try:
                    parsed = parse_value(value, expected_type)
                except (TypeError, ValueError) as exc:
                    add_error("type-mismatch", line_number, name, str(exc), value)
                    continue
            if "allowed_values" in rule and value not in rule["allowed_values"] and parsed not in rule["allowed_values"]:
                add_error("value-not-allowed", line_number, name, "value is outside allowed_values", value)
            if "pattern" in rule and not re.fullmatch(str(rule["pattern"]), raw_text):
                add_error("pattern-mismatch", line_number, name, "value does not match the full regex pattern", value)
            if "min_length" in rule and len(raw_text) < int(rule["min_length"]):
                add_error("below-min-length", line_number, name, "value is shorter than min_length", value)
            if "max_length" in rule and len(raw_text) > int(rule["max_length"]):
                add_error("above-max-length", line_number, name, "value is longer than max_length", value)
            if "min" in rule:
                try:
                    if parsed < rule["min"]:
                        add_error("below-minimum", line_number, name, "value is below minimum", value)
                except TypeError:
                    add_error("invalid-minimum-rule", line_number, name, "minimum cannot be compared to parsed value", value)
            if "max" in rule:
                try:
                    if parsed > rule["max"]:
                        add_error("above-maximum", line_number, name, "value is above maximum", value)
                except TypeError:
                    add_error("invalid-maximum-rule", line_number, name, "maximum cannot be compared to parsed value", value)
            if name in unique_seen:
                normalized = json.dumps(parsed, sort_keys=True, ensure_ascii=False, default=str)
                if normalized in unique_seen[name]:
                    add_error("duplicate-unique-value", line_number, name, "value violates unique constraint", value)
                unique_seen[name].add(normalized)

        if primary_key:
            missing_key = [name for name in primary_key if is_null(row.get(name))]
            if missing_key:
                add_error("primary-key-null", line_number, ",".join(missing_key), "primary key contains null or missing values")
            else:
                key = tuple(str(row.get(name)) for name in primary_key)
                if key in key_seen:
                    add_error("duplicate-primary-key", line_number, ",".join(primary_key), "primary key is duplicated", key)
                key_seen.add(key)

    minimum = contract.get("row_count_min")
    maximum = contract.get("row_count_max")
    if minimum is not None and row_count < int(minimum):
        add_error("row-count-below-minimum", None, None, f"{row_count} rows is below {minimum}")
    if maximum is not None and row_count > int(maximum):
        add_error("row-count-above-maximum", None, None, f"{row_count} rows is above {maximum}")

    return {
        "status": "pass" if not counts else "fail",
        "input": str(input_path.resolve()),
        "format": kind,
        "rows_checked": row_count,
        "contract_name": contract.get("name", "unnamed"),
        "error_count": sum(counts.values()),
        "error_counts": dict(sorted(counts.items())),
        "errors": errors,
        "errors_truncated": sum(counts.values()) > len(errors),
        "limitations": [
            "This validates declared structural rules, not business correctness or source-to-target reconciliation.",
            "Regex, date and numeric semantics must be aligned with the authoritative producer contract.",
            "For production-scale uniqueness, use an engine-native distributed check instead of this local validator.",
        ],
    }


def human(report: dict[str, Any]) -> str:
    lines = [
        f"Status: {report['status']}",
        f"Rows checked: {report['rows_checked']}",
        f"Errors: {report['error_count']}",
    ]
    lines.extend(f"- {name}: {count}" for name, count in report["error_counts"].items())
    lines.extend(
        f"  line {item['line'] or '-'} / {item['column'] or '-'}: {item['code']} - {item['message']}"
        for item in report["errors"]
    )
    lines.extend(f"LIMITATION: {item}" for item in report["limitations"])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--contract", required=True, type=Path)
    parser.add_argument("--format", choices=["csv", "jsonl"], help="Defaults from input extension")
    parser.add_argument("--max-errors", type=int, default=100)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if args.max_errors <= 0:
        parser.error("--max-errors must be positive")
    try:
        kind = args.format or ("jsonl" if args.input.suffix.lower() in {".jsonl", ".ndjson"} else "csv")
        report = validate(args.input, kind, load_contract(args.contract), args.max_errors)
        rendered = json.dumps(report, ensure_ascii=False, indent=2) if args.json or args.output else human(report)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(rendered)
        return 0 if report["status"] == "pass" else 1
    except Exception as exc:
        print(json.dumps({"status": "error", "message": str(exc)}, ensure_ascii=False) if args.json else f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
