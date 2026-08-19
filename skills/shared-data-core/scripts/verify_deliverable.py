#!/usr/bin/env python3
"""Join a task result to its evidence bundle and emit a deterministic pass/fail verification report."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ACCEPTED_EVIDENCE = {"passed", "observed", "not-applicable"}
COMPLETION_STATES = {"validated", "approved", "released", "monitored", "complete"}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def artifact_check(record: dict[str, Any], root: Path | None) -> tuple[str, str]:
    """Return (status, detail) for the artifact bound to one evidence envelope."""
    artifact = str(record.get("artifact", ""))
    digest = str(record.get("artifact_sha256", "")).lower()
    if root is None:
        return "not-run", "no artifact root supplied"
    if not artifact:
        return "failed", "evidence has no artifact path"
    candidate = Path(artifact)
    resolved = candidate.resolve() if candidate.is_absolute() else (root / candidate).resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError:
        return "failed", f"artifact escapes permitted root: {resolved}"
    if not resolved.is_file():
        return "failed", f"artifact does not exist: {resolved}"
    actual = hashlib.sha256(resolved.read_bytes()).hexdigest()
    if digest and actual != digest:
        return "failed", f"artifact hash mismatch: {resolved}"
    if not digest:
        return "failed", f"evidence records no artifact_sha256 for {resolved}"
    return "passed", f"hash verified: {resolved}"


def verify(result: dict[str, Any], bundle: list[Any], root: Path | None) -> dict[str, Any]:
    envelopes: dict[str, dict[str, Any]] = {}
    findings: list[dict[str, str]] = []
    for index, record in enumerate(bundle):
        if not isinstance(record, dict):
            findings.append({"check": f"evidence#{index}", "status": "failed", "detail": "evidence must be an object"})
            continue
        evidence_id = str(record.get("evidence_id", ""))
        if not evidence_id:
            findings.append({"check": f"evidence#{index}", "status": "failed", "detail": "missing evidence_id"})
            continue
        if evidence_id in envelopes:
            findings.append({"check": evidence_id, "status": "failed", "detail": "duplicate evidence_id"})
        envelopes[evidence_id] = record

    task_id = str(result.get("task_id", ""))
    referenced = [str(item) for item in result.get("evidence", []) if isinstance(item, str)]
    if not referenced:
        findings.append({"check": "evidence-coverage", "status": "failed", "detail": "task result references no evidence"})

    for reference in referenced:
        record = envelopes.get(reference)
        if record is None:
            findings.append({"check": reference, "status": "failed", "detail": "referenced evidence is not present in the bundle"})
            continue
        status = str(record.get("status", ""))
        if status not in ACCEPTED_EVIDENCE:
            findings.append({"check": reference, "status": "failed", "detail": f"evidence status {status!r} cannot support a claim"})
        else:
            findings.append({"check": reference, "status": "passed", "detail": f"evidence status {status}"})
        if task_id and str(record.get("task_id", "")) != task_id:
            findings.append({"check": reference, "status": "failed", "detail": f"evidence belongs to task {record.get('task_id')!r}, not {task_id!r}"})
        if not record.get("claim_ids"):
            findings.append({"check": reference, "status": "failed", "detail": "evidence carries no claim_ids"})
        artifact_status, detail = artifact_check(record, root)
        findings.append({"check": f"{reference}:artifact", "status": artifact_status, "detail": detail})

    orphans = sorted(set(envelopes) - set(referenced))
    for orphan in orphans:
        findings.append({"check": orphan, "status": "not-applicable", "detail": "evidence is not referenced by this task result"})

    if str(result.get("status", "")) in COMPLETION_STATES and not result.get("test_results"):
        findings.append({"check": "test-results", "status": "failed", "detail": "completion state without recorded test results"})

    failed = [item for item in findings if item["status"] == "failed"]
    not_run = [item for item in findings if item["status"] == "not-run"]
    if failed:
        overall = "failed"
    elif not_run:
        overall = "incomplete"
    else:
        overall = "passed"
    return {
        "task_id": task_id,
        "primary_deliverable": result.get("primary_deliverable", ""),
        "result_status": result.get("status", ""),
        "approval_status": result.get("approval_status", ""),
        "evidence_referenced": len(referenced),
        "evidence_available": len(envelopes),
        "overall": overall,
        "findings": findings,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("result", type=Path, help="JSON atomic task result")
    parser.add_argument("evidence", type=Path, help="JSON evidence envelope object or array")
    parser.add_argument("--artifact-root", type=Path, help="root under which evidence artifacts must exist")
    parser.add_argument("--report-out", type=Path, help="write the verification report as JSON")
    args = parser.parse_args()

    try:
        result = load(args.result)
        bundle = load(args.evidence)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: invalid JSON: {exc}")
        sys.exit(1)
    if not isinstance(result, dict):
        print("ERROR: task result must be an object")
        sys.exit(1)

    report = verify(result, bundle if isinstance(bundle, list) else [bundle], args.artifact_root)
    for finding in report["findings"]:
        print(f"{finding['status'].upper()}: {finding['check']}: {finding['detail']}")
    if args.report_out is not None:
        args.report_out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"report written: {args.report_out}")

    print(f"OVERALL: {report['overall']} ({report['evidence_referenced']} referenced / {report['evidence_available']} available)")
    if report["overall"] == "failed":
        sys.exit(1)
    if report["overall"] == "incomplete":
        sys.exit(2)


if __name__ == "__main__":
    main()
