#!/usr/bin/env python3
"""Stream-profile CSV or JSONL data with deterministic, dependency-free checks."""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
import statistics
import sys
from collections import Counter
from pathlib import Path


NULLS = {"", "null", "none", "na", "n/a", "nan"}


class Column:
    def __init__(self, name: str, sample_size: int, seed: int) -> None:
        self.name = name
        self.total = 0
        self.nulls = 0
        self.numeric = 0
        self.minimum: float | None = None
        self.maximum: float | None = None
        self.mean = 0.0
        self.m2 = 0.0
        self.values: Counter[str] = Counter()
        self.unique_overflow = False
        self.sample: list[float] = []
        self.sample_size = sample_size
        self.random = random.Random(f"{seed}:{name}")

    def add(self, raw: object) -> None:
        self.total += 1
        text = "" if raw is None else str(raw).strip()
        if text.lower() in NULLS:
            self.nulls += 1
            return
        if len(self.values) < 10_000 or text in self.values:
            self.values[text] += 1
        else:
            self.unique_overflow = True
        try:
            value = float(text)
            if not math.isfinite(value):
                return
        except ValueError:
            return
        self.numeric += 1
        delta = value - self.mean
        self.mean += delta / self.numeric
        self.m2 += delta * (value - self.mean)
        self.minimum = value if self.minimum is None else min(self.minimum, value)
        self.maximum = value if self.maximum is None else max(self.maximum, value)
        if len(self.sample) < self.sample_size:
            self.sample.append(value)
        else:
            index = self.random.randrange(self.numeric)
            if index < self.sample_size:
                self.sample[index] = value

    def report(self) -> dict:
        non_null = self.total - self.nulls
        numeric_ratio = self.numeric / non_null if non_null else 0.0
        ordered = sorted(self.sample)

        def quantile(p: float) -> float | None:
            if not ordered:
                return None
            pos = (len(ordered) - 1) * p
            lower, upper = math.floor(pos), math.ceil(pos)
            if lower == upper:
                return ordered[lower]
            return ordered[lower] + (ordered[upper] - ordered[lower]) * (pos - lower)

        q1, q3 = quantile(0.25), quantile(0.75)
        outlier_bounds = None
        if q1 is not None and q3 is not None:
            iqr = q3 - q1
            outlier_bounds = {"lower": q1 - 1.5 * iqr, "upper": q3 + 1.5 * iqr}
        result = {
            "name": self.name,
            "total": self.total,
            "null_count": self.nulls,
            "null_ratio": round(self.nulls / self.total, 6) if self.total else 0,
            "observed_unique": len(self.values),
            "unique_count_capped": self.unique_overflow,
            "top_values": self.values.most_common(10),
            "inferred_type": "numeric" if numeric_ratio >= 0.95 else "string_or_mixed",
        }
        if self.numeric:
            result["numeric"] = {
                "count": self.numeric,
                "min": self.minimum,
                "max": self.maximum,
                "mean": self.mean,
                "stddev": math.sqrt(self.m2 / (self.numeric - 1)) if self.numeric > 1 else 0.0,
                "p25": q1,
                "median": quantile(0.5),
                "p75": q3,
                "outlier_bounds_iqr": outlier_bounds,
                "quantiles_from_sample": len(self.sample),
            }
        return result


def rows(path: Path, kind: str):
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        if kind == "csv":
            yield from csv.DictReader(handle)
        else:
            for line_number, line in enumerate(handle, 1):
                if not line.strip():
                    continue
                value = json.loads(line)
                if not isinstance(value, dict):
                    raise ValueError(f"JSONL line {line_number} is not an object")
                yield value


def profile(path: Path, kind: str, max_rows: int, sample_size: int, seed: int, skip: set[str]) -> dict:
    columns: dict[str, Column] = {}
    row_count = 0
    duplicate_count = 0
    seen_rows: set[str] = set()
    duplicate_cap = False
    for record in rows(path, kind):
        row_count += 1
        if max_rows and row_count > max_rows:
            break
        normalized = json.dumps(record, sort_keys=True, ensure_ascii=False, default=str)
        if len(seen_rows) < 200_000:
            if normalized in seen_rows:
                duplicate_count += 1
            else:
                seen_rows.add(normalized)
        else:
            duplicate_cap = True
        for name in record:
            if name not in skip and name not in columns:
                columns[name] = Column(name, sample_size, seed)
        for name, column in columns.items():
            column.add(record.get(name))
    if max_rows and row_count > max_rows:
        row_count = max_rows
    return {
        "status": "pass" if row_count else "fail",
        "file": str(path.resolve()),
        "format": kind,
        "rows_profiled": row_count,
        "max_rows": max_rows or None,
        "duplicate_rows_observed": duplicate_count,
        "duplicate_tracking_capped": duplicate_cap,
        "skipped_columns": sorted(skip),
        "columns": [columns[name].report() for name in sorted(columns)],
        "limitations": [
            "Type inference is value-based and must be checked against the authoritative schema.",
            "Quantiles and IQR bounds use deterministic reservoir samples when a column exceeds the sample size.",
            "This profile does not establish business correctness, representativeness or causal validity.",
        ],
    }


def human(report: dict) -> str:
    lines = [f"Status: {report['status']}", f"Rows profiled: {report['rows_profiled']}", f"Duplicate rows observed: {report['duplicate_rows_observed']}"]
    for col in report["columns"]:
        lines.append(f"- {col['name']}: {col['inferred_type']}; null={col['null_ratio']:.2%}; observed_unique={col['observed_unique']}")
    lines.extend(f"LIMITATION: {item}" for item in report["limitations"])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--format", choices=["csv", "jsonl"], help="Defaults from extension")
    parser.add_argument("--max-rows", type=int, default=0, help="0 means all rows")
    parser.add_argument("--sample-size", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument("--skip-columns", default="", help="Comma-separated sensitive or irrelevant columns")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        kind = args.format or ("jsonl" if args.input.suffix.lower() in {".jsonl", ".ndjson"} else "csv")
        result = profile(args.input, kind, args.max_rows, args.sample_size, args.seed, {x.strip() for x in args.skip_columns.split(",") if x.strip()})
        rendered = json.dumps(result, ensure_ascii=False, indent=2) if args.json or args.output else human(result)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(rendered)
        return 0 if result["status"] == "pass" else 1
    except Exception as exc:
        print(json.dumps({"status": "error", "message": str(exc)}, ensure_ascii=False) if args.json else f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
