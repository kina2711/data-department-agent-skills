#!/usr/bin/env python3
"""Scan SQL or Spark execution-plan text for evidence-backed review prompts."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


PATTERNS = {
    "sql": [
        ("sequential-scan", r"\bSeq Scan\b|\bTable Scan\b|\bFULL SCAN\b", "Check pruning, selectivity and whether an index/partition strategy matches the workload."),
        ("cartesian-join", r"\bCartesian\b|\bCROSS JOIN\b", "Verify that Cartesian expansion is intentional and bounded."),
        ("nested-loop", r"\bNested Loop\b", "Compare estimated/actual cardinality; nested loops can amplify cost on large inputs."),
        ("sort", r"\bSort\b", "Check rows, memory/spill and whether ordering is required."),
        ("repartition", r"\bRepartition\b|\bExchange\b", "Inspect redistribution volume, keys and partition balance."),
        ("estimate-mismatch", r"rows=\d+.*actual.*rows=\d+", "Compare estimated and actual rows; material mismatch can change join choices."),
    ],
    "spark": [
        ("exchange", r"\bExchange\b|\bShuffleExchange\b", "Wide dependency/shuffle: measure bytes, partitions, spill and skew."),
        ("sort-merge-join", r"\bSortMergeJoin\b", "Check input size, partitioning and whether a broadcast join is safe and supported by evidence."),
        ("cartesian", r"\bCartesianProduct\b|\bBroadcastNestedLoopJoin\b", "Inspect join predicate and boundedness; this may create large expansion."),
        ("single-partition", r"SinglePartition|numPartitions\s*=\s*1", "A single partition can serialize work and become a bottleneck."),
        ("python-udf", r"BatchEvalPython|ArrowEvalPython|PythonUDF", "Measure serialization/vectorization cost and consider native expressions."),
        ("adaptive-plan", r"AdaptiveSparkPlan", "Record whether the displayed plan is initial or final after adaptive execution."),
        ("file-scan", r"FileScan|BatchScan|Scan parquet|Scan csv", "Check pushed filters, partition filters, selected columns and small-file count."),
    ],
}


def detect_engine(text: str) -> str:
    return "spark" if re.search(r"SparkPlan|AdaptiveSparkPlan|Exchange|FileScan", text, flags=re.I) else "sql"


def inspect(text: str, engine: str) -> dict:
    selected = detect_engine(text) if engine == "auto" else engine
    findings = []
    for finding_id, pattern, question in PATTERNS[selected]:
        matches = list(re.finditer(pattern, text, flags=re.I))
        if matches:
            snippets = []
            lines = text.splitlines()
            for match in matches[:5]:
                line_number = text[: match.start()].count("\n") + 1
                snippets.append({"line": line_number, "text": lines[line_number - 1].strip()[:300]})
            findings.append({"id": finding_id, "occurrences": len(matches), "evidence": snippets, "review_question": question})
    return {
        "status": "heuristic-review",
        "engine": selected,
        "findings": findings,
        "required_baseline": ["runtime", "input/output rows and bytes", "partitions/tasks", "shuffle/spill/skew", "environment and configuration", "cost when applicable"],
        "next_steps": ["Confirm every finding against engine-native metrics and actual cardinalities.", "Form one falsifiable bottleneck hypothesis.", "Benchmark one controlled change against an equivalent workload.", "Reconcile correctness and control totals before accepting a speedup."],
        "limitations": ["Pattern matching does not interpret the complete optimizer model.", "Absence of a pattern is not evidence of an efficient plan.", "Recommendations require engine version, configuration, workload metrics and data distribution."],
    }


def human(result: dict) -> str:
    lines = [f"Status: {result['status']}", f"Engine: {result['engine']}", f"Findings: {len(result['findings'])}"]
    for finding in result["findings"]:
        lines.append(f"- {finding['id']} ({finding['occurrences']}): {finding['review_question']}")
        lines.extend(f"  line {e['line']}: {e['text']}" for e in finding["evidence"])
    lines.extend(f"NEXT: {item}" for item in result["next_steps"])
    lines.extend(f"LIMITATION: {item}" for item in result["limitations"])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--engine", choices=["auto", "sql", "spark"], default="auto")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        result = inspect(args.input.read_text(encoding="utf-8", errors="replace"), args.engine)
        rendered = json.dumps(result, ensure_ascii=False, indent=2) if args.json or args.output else human(result)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(rendered)
        return 0
    except Exception as exc:
        print(json.dumps({"status": "error", "message": str(exc)}, ensure_ascii=False) if args.json else f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
