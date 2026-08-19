#!/usr/bin/env python3
"""Exercise the executable evidence scripts and the production guard against real fixtures.

Each control is run as a subprocess exactly as a skill would run it, so a control that
cannot enforce its own rule fails here rather than silently passing a user's release.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "skills" / "shared-data-core" / "scripts"
ORCH = ROOT / "skills" / "data-department-orchestrator" / "scripts"
GUARD = ROOT / "hooks" / "guard_production_action.py"
ARCH = ROOT / "skills" / "data-architecture" / "scripts" / "scan_architecture_drift.py"
BRAIN = ROOT / "skills" / "personal-second-brain-and-knowledge-os" / "scripts" / "build_entity_context_graph.py"
CATALOG = ROOT / "task-catalog.json"
CONSTITUTION = CORE / "validate_constitution.py"
CODEINDEX = ROOT / "skills" / "data-developer-experience" / "scripts" / "build_code_index.py"
INSTINCTS = ORCH / "manage_instincts.py"
QUALITY = ORCH / "score_skill_quality.py"
INSTALLER = ROOT / "tools" / "install_agent_harness.py"
SUITE_ROOT_ARG = ROOT
LF = chr(10)


def run(args: list[str], stdin: str | None = None) -> tuple[int, str]:
    completed = subprocess.run(
        [sys.executable, *args],
        input=stdin,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return completed.returncode, completed.stdout + completed.stderr


def write(path: Path, payload: object) -> Path:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def build_fixtures(work: Path) -> dict[str, object]:
    artifacts = work / "artifacts"
    artifacts.mkdir()
    artifact = artifacts / "verification-report.md"
    artifact.write_text("# verification report\n\nrecomputed independently\n", encoding="utf-8")
    digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
    next_task = next(
        entry["id"]
        for entry in json.loads(CATALOG.read_text(encoding="utf-8"))
        if "handoff" in entry["id"]
    )
    return {
        "root": artifacts,
        "digest": digest,
        "result": {
            "task_id": "core-verify-deliverable",
            "status": "complete",
            "lifecycle_profile": "advisory-analysis",
            "risk_tier": "R0-light",
            "execution_path": "fast-path",
            "phase_reached": "handoff",
            "primary_deliverable": "pass/fail verification report",
            "evidence": ["ev-1"],
            "test_results": ["independent recalculation matched"],
            "gate_results": ["definition-of-done: passed"],
            "approval_status": "not-required",
            "residual_risks": ["single-period sample"],
            "next_task": next_task,
            "next_owner": "analytics-engineering",
        },
        "evidence": [
            {
                "evidence_id": "ev-1",
                "task_id": "core-verify-deliverable",
                "claim_ids": ["c1"],
                "artifact": "verification-report.md",
                "artifact_version": "1.0.0",
                "artifact_sha256": digest,
                "environment": {"host": "ci"},
                "method": "independent recalculation",
                "observed_result": "match",
                "status": "passed",
                "captured_at": "2026-08-17T09:00:00Z",
                "captured_by": "control-tests",
                "limitations": "single period",
            }
        ],
        "approval": {
            "approval_id": "ap-1",
            "task_id": "core-verify-deliverable",
            "scope": ["verification-report.md"],
            "artifact_version": "1.0.0",
            "artifact_sha256": digest,
            "risk_tier": "R2-standard",
            "approver": "head-of-data",
            "authority": "data governance council",
            "decision": "approved",
            "conditions": [],
            "decided_at": "2026-08-16T09:00:00Z",
            "expires_at": "2026-09-16T09:00:00Z",
        },
        "state": {
            "workflow_id": "wf-control",
            "status": "complete",
            "lifecycle_profile": "advisory-analysis",
            "risk_tier": "R0-light",
            "execution_path": "fast-path",
            "current_phase": "handoff",
            "current_task": "core-verify-deliverable",
            "completed_tasks": ["core-verify-deliverable"],
            "passed_gates": ["definition-of-done"],
            "failed_tests": [],
            "blocked_by": [],
            "next_permitted_action": "hand off to analytics engineering",
            "updated_at": "2026-08-17T10:00:00Z",
        },
    }


def constitution_fixture() -> dict:
    return {
        "constitution_id": "const-control", "project": "control-suite", "version": "1.0.0",
        "ratified_at": "2026-08-01T09:00:00Z", "ratified_by": "head-of-data",
        "principles": [{"id": "ARCH-1", "statement": "Marts are additive only.",
                        "rationale": "Downstream BI cannot absorb breaking grain changes.",
                        "enforcement": "blocking"}],
        "technology_stack": [{"layer": "warehouse", "technology": "BigQuery",
                              "version_constraint": ">=2026.01", "locked": True,
                              "decided_in": "ADR-004",
                              "alternatives_rejected": ["Snowflake", "Redshift"]}],
        "architecture_rules": [{"id": "DEP-1", "rule": "Marts must not read staging directly.",
                                "enforcement": "blocking", "forbidden_dependencies": ["marts->staging"],
                                "max_module_depth": 4, "allow_cycles": False}],
        "amendment_policy": {"requires_approval_from": "data governance council",
                             "requires_version_bump": True, "supersedes": []},
    }


def check_new_layers(work: Path) -> tuple[int, list[str]]:
    """Constitution, architecture sensor and deterministic memory must each be able to fail."""
    failures: list[str] = []
    checks = 0

    good = write(work / "constitution.json", constitution_fixture())
    drifted_doc = constitution_fixture()
    drifted_doc["technology_stack"][0]["technology"] = "Snowflake"
    drifted = write(work / "constitution-drifted.json", drifted_doc)
    unlocked_doc = constitution_fixture()
    unlocked_doc["technology_stack"][0]["locked"] = False
    unlocked_doc["version"] = "1.1.0"
    unlocked = write(work / "constitution-unlocked.json", unlocked_doc)
    blank = ROOT / "skills" / "shared-data-core" / "assets" / "project-constitution.json"

    cases: list[tuple[str, list[str], int]] = [
        ("a ratified constitution validates", [str(CONSTITUTION), str(good)], 0),
        ("a plan consistent with locked layers passes",
         [str(CONSTITUTION), str(good), "--proposal", "Add incremental dbt models on BigQuery."], 0),
        ("a plan naming a rejected alternative is blocked",
         [str(CONSTITUTION), str(good), "--proposal", "Migrate the warehouse to Snowflake."], 3),
        ("swapping a locked technology without a version bump is blocked",
         [str(CONSTITUTION), str(drifted), "--previous", str(good)], 3),
        ("silently unlocking a locked layer is blocked",
         [str(CONSTITUTION), str(unlocked), "--previous", str(good)], 3),
        ("the blank template is rejected until it is filled in", [str(CONSTITUTION), str(blank)], 1),
    ]
    for label, args, expected in cases:
        checks += 1
        code, output = run(args)
        if code != expected:
            failures.append(label + ": expected exit " + str(expected) + ", got " + str(code) + LF + output.strip())

    healthy = work / "healthy" / "pkg"
    healthy.mkdir(parents=True)
    (healthy / "base.py").write_text("VALUE = 1" + LF, encoding="utf-8")
    (healthy / "app.py").write_text(
        "from pkg.base import VALUE" + LF + LF + "def run():" + LF + "    return VALUE" + LF, encoding="utf-8"
    )

    decayed = work / "decayed" / "pkg"
    decayed.mkdir(parents=True)
    (decayed / "a.py").write_text("from pkg.b import thing" + LF + LF + "def a():" + LF + "    return thing()" + LF, encoding="utf-8")
    (decayed / "b.py").write_text("from pkg.c import other" + LF + LF + "def thing():" + LF + "    return other()" + LF, encoding="utf-8")
    (decayed / "c.py").write_text("from pkg.a import a" + LF + LF + "def other():" + LF + "    return a()" + LF, encoding="utf-8")

    checks += 1
    code, output = run([str(ARCH), str(work / "healthy"), "--max-depth", "5"])
    if code != 0:
        failures.append("a small acyclic package scans clean: expected exit 0, got " + str(code) + LF + output)
    elif "acyclicity    2000" not in output:
        failures.append("a small acyclic package should score full acyclicity" + LF + output)

    checks += 1
    code, output = run([str(ARCH), str(work / "decayed"), "--max-depth", "5"])
    if "CYCLES: 1" not in output:
        failures.append("a three-module import cycle must be detected" + LF + output)

    checks += 1
    code, output = run([str(ARCH), str(work / "decayed"), "--gate", "10000"])
    if code != 1:
        failures.append("a failing score gate must exit 1, got " + str(code))

    vault = work / "vault" / "2026-08"
    vault.mkdir(parents=True)
    (vault / "note.md").write_text(
        "# dbt on BigQuery 2026-08-11" + LF + LF + "Incremental models use `merge` against [[BigQuery]]." + LF,
        encoding="utf-8",
    )
    index = work / "memory-index.json"

    checks += 1
    code, output = run([str(BRAIN), str(work / "vault"), "--index-out", str(index)])
    if code != 0 or "model_calls: 0" not in output:
        failures.append("memory index must build with zero model calls" + LF + output)

    checks += 1
    code, output = run([str(BRAIN), str(work / "vault"), "--index-in", str(index), "--query", "BigQuery incremental"])
    if code != 0 or "RETRIEVED" not in output:
        failures.append("an indexed entity must be retrievable" + LF + output)

    checks += 1
    code, output = run([str(BRAIN), str(work / "vault"), "--index-in", str(index), "--query", "kubernetes helm rollback"])
    if code != 2:
        failures.append("an unmatched query must report unknown with exit 2, got " + str(code) + LF + output)

    return checks, failures


def instinct_fixture(instinct_id: str, scope: str, applied: int, succeeded: int,
                     confirmed: str, status: str = "proposed") -> dict:
    return {
        "instinct_id": instinct_id, "scope": scope,
        "trigger": "A situation that recurs often enough to be worth a rule.",
        "pattern": "The concrete action to take when that situation holds.",
        "rationale": "The failure mode this prevents, observed in recorded runs.",
        "observations": {"applied": applied, "succeeded": succeeded, "failed": applied - succeeded},
        "status": status, "created_at": "2026-01-01T09:00:00Z",
        "last_confirmed_at": confirmed, "evidence": ["ev-1"], "user_content": None,
    }


def telemetry_line(number: int, task: str, outcome: str, route: str = "implicit",
                   overridden: bool = False, verified: bool = True) -> dict:
    return {
        "event_id": "e" + str(number), "occurred_at": "2026-08-11T09:00:00Z",
        "suite_version": "3.5.0", "skill": "shared-data-core", "task_id": task,
        "route_source": "overridden" if overridden else route, "outcome": outcome,
        "duration_ms": 1000, "references_loaded": [], "token_estimate": 4000,
        "failure_codes": ["missing-approval"] if outcome == "failed" else [],
        "user_content": None, "evidence_verified": verified,
    }


def check_v35_layers(work: Path) -> tuple[int, list[str]]:
    """Code index, instincts and contract quality must each refuse to overstate what they know."""
    failures: list[str] = []
    checks = 0

    pkg = work / "codebase" / "pkg"
    pkg.mkdir(parents=True)
    (pkg / "core.py").write_text(
        "def helper():" + LF + "    return 1" + LF + LF + LF
        + "def caller():" + LF + "    return helper()" + LF,
        encoding="utf-8",
    )
    code_index = work / "code-index.json"

    checks += 1
    code, output = run([str(CODEINDEX), str(work / "codebase"), "--index-out", str(code_index)])
    if code != 0 or "symbols: 2" not in output:
        failures.append("code index must find both symbols" + LF + output)

    checks += 1
    code, output = run([str(CODEINDEX), str(work / "codebase"), "--index-in", str(code_index), "--symbol", "helper"])
    if code != 0:
        failures.append("an indexed symbol must resolve, got exit " + str(code) + LF + output)
    elif "CALLERS  caller" not in output:
        failures.append("caller relationship must be reported" + LF + output)
    elif "CONTEXT  returned" not in output:
        failures.append("context saving must be reported" + LF + output)

    checks += 1
    code, output = run([str(CODEINDEX), str(work / "codebase"), "--index-in", str(code_index), "--symbol", "no_such_symbol"])
    if code != 2:
        failures.append("an unindexed symbol must report unknown with exit 2, got " + str(code))

    ledger = write(work / "instincts.json", [
        instinct_fixture("well-evidenced", "analytics-engineering", 9, 9, "2026-08-10T09:00:00Z"),
        instinct_fixture("one-lucky-run", "data-engineering", 2, 1, "2026-08-02T09:00:00Z"),
        instinct_fixture("gone-stale", "business-intelligence", 8, 7, "2026-01-05T09:00:00Z", "active"),
        instinct_fixture("mostly-fails", "mlops", 10, 2, "2026-08-01T09:00:00Z", "active"),
    ])

    checks += 1
    code, output = run([str(INSTINCTS), str(ledger), "--rescore", "--as-of", "2026-08-19T00:00:00Z"])
    if code != 0:
        failures.append("a valid instinct ledger must score, got exit " + str(code) + LF + output)
    else:
        expectations = [
            ("well-evidenced", "active"),
            ("one-lucky-run", "proposed"),
            ("gone-stale", "weakening"),
            ("mostly-fails", "retired"),
        ]
        for instinct_id, expected_status in expectations:
            line = next((row for row in output.splitlines() if instinct_id in row), "")
            if not line.strip().startswith(expected_status):
                failures.append("instinct " + instinct_id + " should be " + expected_status + ", got: " + line)

    leaky = write(work / "instincts-leaky.json", [
        {**instinct_fixture("leaks-a-secret", "global", 6, 6, "2026-08-10T09:00:00Z"),
         "pattern": "Reuse the api_key value recorded from the last run."}
    ])
    checks += 1
    code, output = run([str(INSTINCTS), str(leaky)])
    if code != 1 or "secret" not in output:
        failures.append("an instinct containing a credential must be rejected" + LF + output)

    unearned = write(work / "instincts-unearned.json", [
        instinct_fixture("claims-active-early", "global", 2, 2, "2026-08-10T09:00:00Z", "active")
    ])
    checks += 1
    code, output = run([str(INSTINCTS), str(unearned)])
    if code != 1:
        failures.append("active status on 2 applications must be rejected, got exit " + str(code) + LF + output)

    catalog_ids = [entry["id"] for entry in json.loads(CATALOG.read_text(encoding="utf-8"))]
    healthy_task, failing_task, misrouted_task = catalog_ids[0], catalog_ids[1], catalog_ids[2]
    rows: list[dict] = []
    number = 0
    for _ in range(8):
        number += 1
        rows.append(telemetry_line(number, healthy_task, "complete"))
    for _ in range(7):
        number += 1
        rows.append(telemetry_line(number, failing_task, "failed", verified=False))
    for _ in range(2):
        number += 1
        rows.append(telemetry_line(number, failing_task, "complete"))
    for _ in range(6):
        number += 1
        rows.append(telemetry_line(number, misrouted_task, "complete", overridden=True))
    for _ in range(2):
        number += 1
        rows.append(telemetry_line(number, misrouted_task, "complete"))
    telemetry = work / "telemetry.jsonl"
    telemetry.write_text(LF.join(json.dumps(row) for row in rows) + LF, encoding="utf-8")

    checks += 1
    code, output = run([str(QUALITY), str(telemetry), "--task-catalog", str(CATALOG), "--fail-on-action"])
    if code != 1:
        failures.append("tasks needing action must exit 1, got " + str(code) + LF + output)
    else:
        if "investigate       " + failing_task not in output:
            failures.append("a 22% completion task must be flagged investigate" + LF + output)
        if "fix-routing       " + misrouted_task not in output:
            failures.append("a 75% override task must be flagged fix-routing despite full completion" + LF + output)
        if "healthy           " + healthy_task not in output:
            failures.append("a reliable task must be reported healthy" + LF + output)

    leaky_telemetry = work / "telemetry-leaky.jsonl"
    leaked = telemetry_line(1, healthy_task, "complete")
    leaked["user_content"] = "the user pasted a salary table"
    leaky_telemetry.write_text(json.dumps(leaked) + LF, encoding="utf-8")
    checks += 1
    code, output = run([str(QUALITY), str(leaky_telemetry)])
    if code != 1 or "user_content is forbidden" not in output:
        failures.append("telemetry carrying user content must be rejected" + LF + output)

    empty_telemetry = work / "telemetry-empty.jsonl"
    empty_telemetry.write_text("", encoding="utf-8")
    checks += 1
    code, output = run([str(QUALITY), str(empty_telemetry)])
    if code != 1 or "unknown" not in output:
        failures.append("an empty ledger must report unknown rather than good" + LF + output)

    return checks, failures


def check_harness_install(work: Path) -> tuple[int, list[str]]:
    """The installer must never clobber a path it did not create, and must undo itself."""
    failures: list[str] = []
    checks = 0
    target = work / "target-project"
    target.mkdir()

    checks += 1
    code, output = run([str(INSTALLER), str(target), "--dry-run"])
    if code != 0:
        failures.append("dry run must succeed, got exit " + str(code) + LF + output)
    elif any((target / name).exists() for name in (".codex", ".agents", "AGENTS.md")):
        failures.append("dry run must not create anything on disk")

    checks += 1
    code, output = run([str(INSTALLER), str(target), "--harness", "codex", "--copy"])
    skills_dir = target / ".codex" / "skills"
    if code != 0:
        failures.append("codex install must succeed, got exit " + str(code) + LF + output)
    elif not (skills_dir / "shared-data-core" / "SKILL.md").exists():
        failures.append("codex install must place SKILL.md under .codex/skills/<name>/")
    elif not (target / "AGENTS.md").exists():
        failures.append("codex install must provide AGENTS.md")

    checks += 1
    code, output = run([str(INSTALLER), str(target), "--harness", "antigravity", "--copy"])
    agent_file = target / ".agents" / "agents" / "dd-ae.md"
    if code != 0:
        failures.append("antigravity install must succeed, got exit " + str(code) + LF + output)
    elif not agent_file.exists():
        failures.append("antigravity install must place department agents under .agents/agents/")

    foreign = work / "foreign-project"
    (foreign / ".codex" / "skills").mkdir(parents=True)
    (foreign / ".codex" / "skills" / "shared-data-core").write_text("mine", encoding="utf-8")
    checks += 1
    code, output = run([str(INSTALLER), str(foreign), "--harness", "codex", "--copy"])
    if "REFUSED" not in output:
        failures.append("installing over a path we did not create must be refused" + LF + output)
    elif (foreign / ".codex" / "skills" / "shared-data-core").read_text(encoding="utf-8") != "mine":
        failures.append("a refused path must be left untouched")

    checks += 1
    code, output = run([str(INSTALLER), str(SUITE_ROOT_ARG)])
    if code != 1 or "into itself" not in output:
        failures.append("installing the suite into itself must be refused, got exit " + str(code))

    checks += 1
    code, output = run([str(INSTALLER), str(target), "--uninstall"])
    leftovers = [
        name for name in (".codex/skills", ".agents/agents", "AGENTS.md")
        if (target / name).exists()
    ]
    if code != 0:
        failures.append("uninstall must succeed, got exit " + str(code) + LF + output)
    elif leftovers:
        failures.append("uninstall left paths behind: " + ", ".join(leftovers))

    return checks, failures


def guard_cases() -> list[tuple[str, str, bool]]:
    """(label, command, expect_escalation)"""
    return [
        ("git push", "git push origin main", True),
        ("force push", "git push --force origin main", True),
        ("terraform destroy", "terraform destroy -auto-approve", True),
        ("dbt prod build", "dbt build --target prod", True),
        ("unfiltered delete", 'psql -c "delete from orders"', True),
        ("recursive delete", "rm -rf ./build", True),
        ("release publish", "gh release create v1.0.0", True),
        ("kubectl apply", "kubectl apply -f deploy.yaml", True),
        ("filtered delete", 'psql -c "delete from orders where id = 1"', False),
        ("dbt dev build", "dbt build --target dev", False),
        ("read-only status", "git status", False),
        ("test run", "pytest -q", False),
    ]


def main() -> None:
    failures: list[str] = []
    checks = 0

    with tempfile.TemporaryDirectory() as raw:
        work = Path(raw)
        fixtures = build_fixtures(work)
        root = str(fixtures["root"])
        result = write(work / "result.json", fixtures["result"])
        evidence = write(work / "evidence.json", fixtures["evidence"])
        approval = write(work / "approval.json", fixtures["approval"])
        state = write(work / "state.json", fixtures["state"])

        positive: list[tuple[str, list[str], int]] = [
            ("task result accepts a complete, catalog-linked result",
             [str(CORE / "validate_task_result.py"), str(result), "--task-catalog", str(CATALOG), "--mode", "complete"], 0),
            ("evidence bundle accepts a hash-verified envelope",
             [str(CORE / "validate_evidence_bundle.py"), str(evidence), "--artifact-root", root, "--mode", "complete"], 0),
            ("deliverable verification passes with a verified artifact",
             [str(CORE / "verify_deliverable.py"), str(result), str(evidence), "--artifact-root", root], 0),
            ("approval is valid inside its window",
             [str(ORCH / "validate_approval_record.py"), str(approval), "--task-catalog", str(CATALOG),
              "--as-of", "2026-08-17T00:00:00Z", "--require-approved"], 0),
            ("run state is consistent at completion",
             [str(ORCH / "validate_run_state.py"), str(state), "--task-catalog", str(CATALOG)], 0),
            ("run state template parses as flat YAML",
             [str(ORCH / "validate_run_state.py"), str(ROOT / "skills" / "data-department-orchestrator" / "assets" / "run-state.yaml")], 1),
        ]
        for label, args, expected in positive:
            checks += 1
            code, output = run(args)
            if code != expected:
                failures.append(f"{label}: expected exit {expected}, got {code}\n{output.strip()}")

        # A control that cannot fail is not a control.
        unverified = write(work / "result-unverified.json", {**fixtures["result"], "evidence": []})
        forged = write(work / "evidence-forged.json", [{**fixtures["evidence"][0], "artifact_sha256": "0" * 64}])
        unapproved = write(work / "result-unapproved.json", {
            **fixtures["result"], "risk_tier": "R4-critical", "execution_path": "controlled-path",
            "approval_status": "pending",
        })
        stale_state = write(work / "state-stale.json", {**fixtures["state"], "blocked_by": ["missing access"]})

        negative: list[tuple[str, list[str], int]] = [
            ("a completion claim with no evidence is rejected",
             [str(CORE / "validate_task_result.py"), str(unverified), "--mode", "complete"], 1),
            ("an R4 completion without approval is rejected",
             [str(CORE / "validate_task_result.py"), str(unapproved), "--task-catalog", str(CATALOG), "--mode", "complete"], 1),
            ("a forged artifact hash is rejected",
             [str(CORE / "validate_evidence_bundle.py"), str(forged), "--artifact-root", root, "--mode", "complete"], 1),
            ("verification without an artifact root reports incomplete, not pass",
             [str(CORE / "verify_deliverable.py"), str(result), str(evidence)], 2),
            ("an expired approval cannot authorize action",
             [str(ORCH / "validate_approval_record.py"), str(approval), "--as-of", "2026-10-01T00:00:00Z", "--require-approved"], 1),
            ("a complete run state cannot carry unresolved blockers",
             [str(ORCH / "validate_run_state.py"), str(stale_state)], 1),
        ]
        for label, args, expected in negative:
            checks += 1
            code, output = run(args)
            if code != expected:
                failures.append(f"{label}: expected exit {expected}, got {code}\n{output.strip()}")

        layer_checks, layer_failures = check_new_layers(work)
        checks += layer_checks
        failures.extend(layer_failures)

        v35_checks, v35_failures = check_v35_layers(work)
        checks += v35_checks
        failures.extend(v35_failures)

        harness_checks, harness_failures = check_harness_install(work)
        checks += harness_checks
        failures.extend(harness_failures)

    for label, command, expect_escalation in guard_cases():
        checks += 1
        payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": command}})
        code, output = run([str(GUARD)], stdin=payload)
        if code != 0:
            failures.append(f"guard {label}: guard must always exit 0, got {code}")
            continue
        escalated = '"permissionDecision": "ask"' in output.replace("'", '"')
        if escalated != expect_escalation:
            failures.append(
                f"guard {label}: expected escalation={expect_escalation}, got {escalated} for {command!r}"
            )

    checks += 1
    code, _ = run([str(GUARD)], stdin="not json at all")
    if code != 0:
        failures.append(f"guard fails open on malformed input: expected exit 0, got {code}")

    print(f"control_checks: {checks}")
    print(f"errors: {len(failures)}")
    for failure in failures:
        print(f"ERROR: {failure}")
    if failures:
        sys.exit(1)
    print("Control tests passed")


if __name__ == "__main__":
    main()
