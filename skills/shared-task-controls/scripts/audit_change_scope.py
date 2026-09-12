#!/usr/bin/env python3
"""Audit Git changes against an explicit, machine-readable scope contract."""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import subprocess
import sys
from pathlib import Path


def run_git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout


def normalize(path: str) -> str:
    return path.strip().replace("\\", "/").removeprefix("./")


def matches(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatchcase(path, normalize(pattern)) for pattern in patterns)


def parse_name_status(raw: str) -> list[dict[str, str]]:
    changes: list[dict[str, str]] = []
    for line in raw.splitlines():
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        status = parts[0]
        path = normalize(parts[-1])
        entry = {"status": status, "path": path}
        if status.startswith(("R", "C")) and len(parts) >= 3:
            entry["from_path"] = normalize(parts[-2])
        changes.append(entry)
    return changes


def collect_changes(repo: Path, base: str, head: str | None) -> list[dict[str, str]]:
    if head:
        comparison = f"{base}...{head}"
        return parse_name_status(run_git(repo, "diff", "--name-status", comparison))

    # Comparing the working tree directly with the baseline preserves the final
    # state when a staged modification is followed by an unstaged deletion.
    changes = parse_name_status(run_git(repo, "diff", "--name-status", base))
    for path in run_git(repo, "ls-files", "--others", "--exclude-standard").splitlines():
        clean = normalize(path)
        changes.append({"status": "??", "path": clean})
    return sorted(changes, key=lambda item: (item["path"], item["status"]))


def load_contract(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    for field in ("contract_id", "task_id", "baseline_commit", "approved_by", "approved_at"):
        if not isinstance(data.get(field), str) or not data[field].strip():
            raise ValueError(f"contract.{field} is required")
    outcomes = data.get("requested_outcomes")
    if not isinstance(outcomes, list) or not outcomes or not all(isinstance(item, str) and item for item in outcomes):
        raise ValueError("contract.requested_outcomes must be a non-empty string list")
    allowed = data.get("allowed_paths")
    if not isinstance(allowed, list) or not allowed or not all(isinstance(item, str) for item in allowed):
        raise ValueError("contract.allowed_paths must be a non-empty string list")
    for field in ("forbidden_paths", "planned_deletions", "generated_paths"):
        value = data.get(field, [])
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            raise ValueError(f"contract.{field} must be a string list")
    traces = data.get("task_to_paths")
    if not isinstance(traces, list) or not traces:
        raise ValueError("contract.task_to_paths must be a non-empty list")
    for index, trace in enumerate(traces):
        if not isinstance(trace, dict) or not trace.get("outcome") or not trace.get("paths"):
            raise ValueError(f"contract.task_to_paths[{index}] needs outcome and paths")
        if not isinstance(trace["paths"], list) or not all(isinstance(item, str) for item in trace["paths"]):
            raise ValueError(f"contract.task_to_paths[{index}].paths must be a string list")
        if trace["outcome"] not in outcomes:
            raise ValueError(f"contract.task_to_paths[{index}].outcome is not in requested_outcomes")
    for field in ("dependency_checks", "orphan_checks"):
        checks = data.get(field)
        if not isinstance(checks, list) or not checks:
            raise ValueError(f"contract.{field} must be a non-empty list")
        for index, check in enumerate(checks):
            if not isinstance(check, dict) or not check.get("name") or not check.get("status"):
                raise ValueError(f"contract.{field}[{index}] needs name and status")
    return data


def check_control_evidence(contract: dict) -> list[dict[str, str]]:
    failures: list[dict[str, str]] = []
    for field in ("dependency_checks", "orphan_checks"):
        for check in contract[field]:
            status = check["status"]
            evidence = str(check.get("evidence", "")).strip()
            reason = str(check.get("reason", "")).strip()
            if status == "pass" and evidence:
                continue
            if status == "not-applicable" and reason:
                continue
            failures.append({"control": field, "name": check["name"], "status": status, "reason": "pass needs evidence; not-applicable needs reason"})
    return failures


def diff_fingerprint(repo: Path, base: str, head: str | None, changes: list[dict[str, str]]) -> str:
    comparison = f"{base}...{head}" if head else base
    payload = run_git(repo, "diff", "--binary", comparison).encode("utf-8", errors="replace")
    digest = hashlib.sha256(payload)
    if not head:
        for change in changes:
            if change["status"] != "??":
                continue
            path = repo / change["path"]
            digest.update(change["path"].encode("utf-8"))
            digest.update(path.read_bytes())
    return digest.hexdigest()


def audit(contract: dict, changes: list[dict[str, str]], fingerprint: str) -> dict:
    allowed = contract["allowed_paths"]
    forbidden = contract.get("forbidden_paths", [])
    generated = contract.get("generated_paths", [])
    planned_deletions = contract.get("planned_deletions", [])
    traces = contract.get("task_to_paths", [])

    unexpected: list[dict[str, str]] = []
    forbidden_changes: list[dict[str, str]] = []
    unapproved_deletions: list[dict[str, str]] = []
    untraced: list[dict[str, str]] = []
    mapped: list[dict[str, object]] = []
    control_failures = check_control_evidence(contract)

    for change in changes:
        path = change["path"]
        inspected_paths = [path]
        removed_paths: list[str] = []
        if change["status"].startswith("D"):
            removed_paths.append(path)
        if change["status"].startswith("R") and change.get("from_path"):
            inspected_paths.append(change["from_path"])
            removed_paths.append(change["from_path"])

        for inspected in inspected_paths:
            finding = {**change, "inspected_path": inspected}
            if matches(inspected, forbidden):
                forbidden_changes.append(finding)
            if not matches(inspected, [*allowed, *generated]):
                unexpected.append(finding)
        for removed in removed_paths:
            if not matches(removed, planned_deletions):
                unapproved_deletions.append({**change, "removed_path": removed})

        outcomes = sorted({trace["outcome"] for trace in traces if any(matches(inspected, trace["paths"]) for inspected in inspected_paths)})
        if not outcomes and not all(matches(inspected, generated) for inspected in inspected_paths):
            untraced.append({**change, "inspected_paths": inspected_paths})
        mapped.append({**change, "outcomes": outcomes, "generated": matches(path, generated)})

    violations = len(unexpected) + len(forbidden_changes) + len(unapproved_deletions) + len(untraced) + len(control_failures)
    return {
        "status": "pass" if violations == 0 else "fail",
        "summary": {
            "changed": len(changes),
            "unexpected": len(unexpected),
            "forbidden": len(forbidden_changes),
            "unapproved_deletions": len(unapproved_deletions),
            "untraced": len(untraced),
            "failed_dependency_or_orphan_checks": len(control_failures),
        },
        "contract_binding": {
            "contract_id": contract["contract_id"],
            "task_id": contract["task_id"],
            "baseline_commit": contract["baseline_commit"],
            "approved_by": contract["approved_by"],
            "approved_at": contract["approved_at"],
            "contract_sha256": hashlib.sha256(json.dumps(contract, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest(),
            "final_diff_sha256": fingerprint,
        },
        "changes": mapped,
        "unexpected_changes": unexpected,
        "forbidden_changes": forbidden_changes,
        "unapproved_deletions": unapproved_deletions,
        "untraced_changes": untraced,
        "failed_dependency_or_orphan_checks": control_failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd(), help="Git repository to inspect")
    parser.add_argument("--contract", type=Path, required=True, help="JSON scope contract")
    parser.add_argument("--base", help="Base revision; defaults to HEAD for working-tree audit")
    parser.add_argument("--head", help="Head revision; when supplied, audit base...head only")
    parser.add_argument("--expected-diff-sha256", help="Approved final-diff fingerprint to recheck immediately before release")
    parser.add_argument("--output", type=Path, help="Optional JSON report path")
    parser.add_argument("--json", action="store_true", help="Compatibility flag; output is always JSON")
    args = parser.parse_args()

    try:
        repo = args.repo.resolve()
        if run_git(repo, "rev-parse", "--is-inside-work-tree").strip() != "true":
            raise ValueError(f"not a Git working tree: {repo}")
        contract = load_contract(args.contract.resolve())
        base = args.base or contract["baseline_commit"]
        if args.base and args.base != contract["baseline_commit"]:
            raise ValueError("--base must match contract.baseline_commit")
        run_git(repo, "rev-parse", "--verify", f"{base}^{{commit}}")
        changes = collect_changes(repo, base, args.head)
        report = audit(contract, changes, diff_fingerprint(repo, base, args.head, changes))
        if args.expected_diff_sha256:
            observed = report["contract_binding"]["final_diff_sha256"]
            expected = args.expected_diff_sha256.lower()
            report["expected_final_diff_sha256"] = expected
            report["fingerprint_match"] = observed == expected
            if observed != expected:
                report["status"] = "fail"
                report["summary"]["fingerprint_mismatch"] = 1
        rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            args.output.resolve().write_text(rendered, encoding="utf-8")
        print(rendered, end="")
        return 0 if report["status"] == "pass" else 1
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
