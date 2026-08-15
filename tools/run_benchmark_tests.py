#!/usr/bin/env python3
"""Run deterministic regression checks for benchmark-derived adapters and controls."""

from __future__ import annotations

import json
import hashlib
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "evaluations" / "fixtures" / "benchmark-v2.3"


def invoke(script: Path, *arguments: str, expected_exit: int = 0) -> dict:
    process = subprocess.run(
        [sys.executable, str(script), *arguments, "--json"],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )
    if process.returncode != expected_exit:
        raise AssertionError(
            f"{script.name} exited {process.returncode}, expected {expected_exit}: {process.stderr or process.stdout}"
        )
    return json.loads(process.stdout or process.stderr)


def invoke_plain_json(script: Path, *arguments: str, expected_exit: int = 0) -> dict:
    process = subprocess.run(
        [sys.executable, str(script), *arguments],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )
    if process.returncode != expected_exit:
        raise AssertionError(
            f"{script.name} exited {process.returncode}, expected {expected_exit}: {process.stderr or process.stdout}"
        )
    return json.loads(process.stdout)


def main() -> int:
    da = ROOT / "skills" / "data-analysis" / "scripts"
    de = ROOT / "skills" / "data-engineering" / "scripts"
    ae = ROOT / "skills" / "analytics-engineering" / "scripts"
    dq = ROOT / "skills" / "data-quality-and-reliability" / "scripts"
    core = ROOT / "skills" / "shared-data-core" / "scripts"
    context = ROOT / "skills" / "company-data-context" / "scripts"
    orchestrator = ROOT / "skills" / "data-department-orchestrator" / "scripts"
    project = ROOT / "skills" / "data-personal-project-engineering" / "scripts"
    dx = ROOT / "skills" / "data-developer-experience" / "scripts"
    brain = ROOT / "skills" / "personal-second-brain-and-knowledge-os" / "scripts"
    book = ROOT / "skills" / "book-to-knowledge-and-action" / "scripts"
    career = ROOT / "skills" / "data-career-and-interview-coach" / "scripts"

    eda = invoke(da / "profile_dataset.py", "--input", str(FIXTURE / "sample.csv"))
    assert eda["status"] == "pass" and eda["rows_profiled"] == 4

    sql = invoke(da / "explain_sql.py", "--input", str(FIXTURE / "query.sql"))
    assert sql["filters"] == ["status = 'paid'"]
    assert sql["group_by"] == ["customer_id"]
    assert sql["sources"] == ["raw.orders", "paid_orders"]
    assert any("different effective grains" in risk for risk in sql["risks"])

    join_sql = invoke(da / "explain_sql.py", "--input", str(FIXTURE / "join-query.sql"))
    assert join_sql["joins"] == [{
        "type": "LEFT",
        "source": "dim.customers",
        "alias": "c",
        "condition": "o.customer_id = c.customer_id AND c.is_current = true",
    }]
    assert join_sql["filters"] == ["o.status = 'paid'"]

    plan = invoke(de / "inspect_execution_plan.py", "--input", str(FIXTURE / "spark-plan.txt"), "--engine", "spark")
    plan_ae = invoke(ae / "inspect_execution_plan.py", "--input", str(FIXTURE / "spark-plan.txt"), "--engine", "spark")
    assert plan["engine"] == "spark" and len(plan["findings"]) >= 4
    assert plan_ae["findings"] == plan["findings"]

    valid = invoke(
        dq / "validate_tabular_data.py",
        "--input", str(FIXTURE / "valid.csv"),
        "--contract", str(FIXTURE / "dq-contract.json"),
    )
    invalid = invoke(
        dq / "validate_tabular_data.py",
        "--input", str(FIXTURE / "sample.csv"),
        "--contract", str(FIXTURE / "dq-contract.json"),
        expected_exit=1,
    )
    assert valid["status"] == "pass" and valid["error_count"] == 0
    assert invalid["status"] == "fail" and invalid["error_count"] == 4
    assert invalid["error_counts"] == {
        "duplicate-primary-key": 1,
        "duplicate-unique-value": 1,
        "null-not-allowed": 1,
        "type-mismatch": 1,
    }

    with tempfile.TemporaryDirectory(prefix="data-department-v3.0-") as temporary:
        target = Path(temporary)
        for script, suffix in ((core / "build_context_package.py", "core"), (context / "build_context_package.py", "context")):
            report = invoke(
                script,
                "--manifest", str(FIXTURE / "context-manifest.json"),
                "--output", str(target / f"package-{suffix}.md"),
                "--report", str(target / f"report-{suffix}.json"),
                "--max-tokens", "2000",
            )
            assert report["status"] == "pass" and report["estimated_tokens"] <= 2000
            rendered = (target / f"package-{suffix}.md").read_text(encoding="utf-8")
            assert rendered.index("## Implementation") < rendered.index("## Evidence")

        scope_repo = target / "scope-repo"
        scope_repo.mkdir()
        subprocess.run(["git", "init", "-q", str(scope_repo)], check=True)
        subprocess.run(["git", "-C", str(scope_repo), "config", "user.email", "scope-test@example.invalid"], check=True)
        subprocess.run(["git", "-C", str(scope_repo), "config", "user.name", "Scope Test"], check=True)
        (scope_repo / "src").mkdir()
        (scope_repo / "docs").mkdir()
        (scope_repo / "src" / "pipeline.sql").write_text("select 1;\n", encoding="utf-8")
        (scope_repo / "src" / "dual.sql").write_text("select 1;\n", encoding="utf-8")
        (scope_repo / "docs" / "runbook.md").write_text("baseline\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(scope_repo), "add", "."], check=True)
        subprocess.run(["git", "-C", str(scope_repo), "commit", "-qm", "baseline"], check=True)
        baseline = subprocess.run(["git", "-C", str(scope_repo), "rev-parse", "HEAD"], check=True, text=True, capture_output=True).stdout.strip()

        scope_contract = target / "scope-contract.json"
        scope_contract.write_text(json.dumps({
            "contract_id": "scope-test-1",
            "task_id": "core-audit-change-scope",
            "requested_outcomes": ["update pipeline"],
            "baseline_commit": baseline,
            "allowed_paths": ["src/**"],
            "forbidden_paths": ["secrets/**"],
            "planned_deletions": [],
            "generated_paths": [],
            "task_to_paths": [{"outcome": "update pipeline", "paths": ["src/**"]}],
            "dependency_checks": [{"name": "imports", "status": "pass", "evidence": "static dependency scan"}],
            "orphan_checks": [{"name": "orphan files", "status": "not-applicable", "reason": "no artifact removed"}],
            "approved_by": "test-owner",
            "approved_at": "2026-08-14T00:00:00Z",
        }), encoding="utf-8")
        (scope_repo / "src" / "pipeline.sql").write_text("select 2;\n", encoding="utf-8")
        scope_pass = invoke(core / "audit_change_scope.py", "--repo", str(scope_repo), "--contract", str(scope_contract))
        assert scope_pass["status"] == "pass" and scope_pass["summary"]["changed"] == 1
        approved_diff = scope_pass["contract_binding"]["final_diff_sha256"]
        fingerprint_pass = invoke(core / "audit_change_scope.py", "--repo", str(scope_repo), "--contract", str(scope_contract), "--expected-diff-sha256", approved_diff)
        assert fingerprint_pass["fingerprint_match"] is True
        (scope_repo / "docs" / "runbook.md").write_text("drive-by edit\n", encoding="utf-8")
        scope_fail = invoke(core / "audit_change_scope.py", "--repo", str(scope_repo), "--contract", str(scope_contract), expected_exit=1)
        assert scope_fail["status"] == "fail" and scope_fail["summary"]["unexpected"] == 1
        fingerprint_fail = invoke(core / "audit_change_scope.py", "--repo", str(scope_repo), "--contract", str(scope_contract), "--expected-diff-sha256", approved_diff, expected_exit=1)
        assert fingerprint_fail["fingerprint_match"] is False

        (scope_repo / "src" / "pipeline.sql").rename(scope_repo / "src" / "renamed.sql")
        rename_fail = invoke(core / "audit_change_scope.py", "--repo", str(scope_repo), "--contract", str(scope_contract), expected_exit=1)
        assert rename_fail["summary"]["unapproved_deletions"] >= 1

        (scope_repo / "src" / "dual.sql").write_text("select 2;\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(scope_repo), "add", "src/dual.sql"], check=True)
        (scope_repo / "src" / "dual.sql").unlink()
        staged_then_deleted = invoke(core / "audit_change_scope.py", "--repo", str(scope_repo), "--contract", str(scope_contract), expected_exit=1)
        assert any(item.get("removed_path") == "src/dual.sql" for item in staged_then_deleted["unapproved_deletions"])

        invalid_contract = target / "invalid-scope-contract.json"
        invalid = json.loads(scope_contract.read_text(encoding="utf-8"))
        invalid["task_to_paths"] = []
        invalid_contract.write_text(json.dumps(invalid), encoding="utf-8")
        invalid_trace = invoke(core / "audit_change_scope.py", "--repo", str(scope_repo), "--contract", str(invalid_contract), expected_exit=2)
        assert invalid_trace["status"] == "error" and "non-empty" in invalid_trace["error"]

        (scope_repo / "dbt_project.yml").write_text("name: fixture\nversion: '1.0'\n", encoding="utf-8")
        (scope_repo / "pyproject.toml").write_text("[project]\ndependencies=['apache-airflow','dbt-core']\n", encoding="utf-8")
        repository_report = invoke_plain_json(project / "audit_repository.py", str(scope_repo))
        assert len(repository_report["dimensions"]) == 12
        assert repository_report["git"]["head"] == baseline
        assert len(repository_report["snapshot_sha256"]) == 64

        context_report = invoke_plain_json(context / "bootstrap_context_index.py", str(scope_repo))
        assert context_report["index_version"] == "3.0"
        assert all("content" not in entry for entry in context_report["entries"])

        stack_report = invoke_plain_json(dx / "detect_data_stack.py", str(scope_repo))
        detected = {item["adapter"] for item in stack_report["detected"]}
        assert {"airflow", "dbt"}.issubset(detected)

        portfolio = invoke_plain_json(
            project / "build_portfolio_evidence.py",
            str(ROOT / "evaluations" / "fixtures" / "portfolio-manifest-valid.json"),
            "--project-root", str(ROOT / "evaluations" / "fixtures"),
            "--strict",
        )
        assert portfolio["summary"]["verified_artifacts"] == 1
        assert portfolio["summary"]["verified_claims"] == 1

        telemetry_path = target / "events.jsonl"
        record = subprocess.run(
            [sys.executable, str(orchestrator / "record_skill_telemetry.py"), str(ROOT / "evaluations" / "fixtures" / "telemetry-event-valid.json"), "--output", str(telemetry_path)],
            cwd=ROOT, text=True, encoding="utf-8", capture_output=True, check=False,
        )
        assert record.returncode == 0 and telemetry_path.is_file()
        telemetry = invoke_plain_json(orchestrator / "analyze_skill_telemetry.py", str(telemetry_path))
        assert telemetry["events"] == 1 and telemetry["outcomes"] == {"complete": 1}

        brain_root = target / "second-brain"
        brain_files = {
            "1_Nguon/source.md": "---\nsource_id: src-001\n---\n# Primary source\nImmutable source body.\n",
            "2_Wiki/note.md": "---\nnote_id: note-001\n---\n# Processed note\nA grounded synthesis.\n",
            "3_Toi/rules.md": "---\ncontext_id: me-001\n---\n# My rules\nState uncertainty explicitly.\n",
            "4_Ket-Qua/output.md": "---\noutput_id: out-001\n---\n# Reusable output\nA source-bound artifact.\n",
        }
        for relative, content in brain_files.items():
            path = brain_root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        (brain_root / "1_Nguon" / ".env").write_text("API_KEY=must-not-enter-index\n", encoding="utf-8")
        brain_index = invoke_plain_json(brain / "build_brain_index.py", str(brain_root), "--strict")
        assert brain_index["layer_counts"] == {"1_Nguon": 1, "2_Wiki": 1, "3_Toi": 1, "4_Ket-Qua": 1}
        assert brain_index["sensitive_files_excluded"] == ["1_Nguon/.env"]
        assert all("body" not in entry and "content" not in entry for entry in brain_index["entries"])

        def digest(relative: str) -> str:
            return hashlib.sha256((brain_root / relative).read_bytes()).hexdigest()

        brain_manifest = {
            "brain_id": "brain-test-001", "owner": "fixture-owner", "version": "1.0.0",
            "purpose": "Test grounded reuse", "canonical_root": str(brain_root),
            "privacy_classification": "private", "status": "active", "updated_at": "2026-08-14T00:00:00Z",
            "layers": {
                "1_Nguon": {"path": "1_Nguon", "source_count": 1},
                "2_Wiki": {"path": "2_Wiki", "note_count": 1},
                "3_Toi": {"path": "3_Toi", "rule_count": 1},
                "4_Ket-Qua": {"path": "4_Ket-Qua", "output_count": 1},
            },
            "source_registry": [{"id": "src-001", "path": "1_Nguon/source.md", "sha256": digest("1_Nguon/source.md"), "status": "verified"}],
            "note_registry": [{"id": "note-001", "path": "2_Wiki/note.md", "sha256": digest("2_Wiki/note.md"), "status": "verified", "source_ids": ["src-001"]}],
            "personal_context_registry": [{"id": "me-001", "path": "3_Toi/rules.md", "sha256": digest("3_Toi/rules.md"), "status": "verified", "source_ids": ["src-001"]}],
            "output_registry": [{"id": "out-001", "path": "4_Ket-Qua/output.md", "sha256": digest("4_Ket-Qua/output.md"), "status": "verified", "source_ids": ["src-001"]}],
            "retrieval_test_set": [{"query_id": "q-001", "query": "Find the source-bound rule", "status": "passed"}],
            "backup": {"last_verified_at": "2026-08-14T00:00:00Z", "artifact_sha256": "a" * 64, "restore_tested_at": "2026-08-14T00:00:00Z"},
        }
        brain_manifest_path = target / "second-brain-manifest.json"
        brain_manifest_path.write_text(json.dumps(brain_manifest), encoding="utf-8")
        brain_valid = subprocess.run(
            [sys.executable, str(brain / "validate_second_brain.py"), str(brain_manifest_path), "--root", str(brain_root), "--mode", "complete"],
            cwd=ROOT, text=True, encoding="utf-8", capture_output=True, check=False,
        )
        assert brain_valid.returncode == 0 and "four-layer structure" in brain_valid.stdout
        invalid_brain = json.loads(json.dumps(brain_manifest))
        invalid_brain["layers"]["2_Wiki"]["note_count"] = 7
        invalid_brain["note_registry"][0]["source_ids"] = ["missing-source"]
        invalid_brain["retrieval_test_set"][0]["status"] = "failed"
        invalid_brain_path = target / "second-brain-invalid.json"
        invalid_brain_path.write_text(json.dumps(invalid_brain), encoding="utf-8")
        brain_invalid = subprocess.run(
            [sys.executable, str(brain / "validate_second_brain.py"), str(invalid_brain_path), "--root", str(brain_root), "--mode", "complete"],
            cwd=ROOT, text=True, encoding="utf-8", capture_output=True, check=False,
        )
        assert brain_invalid.returncode == 1
        assert "unknown source_ids" in brain_invalid.stdout and "does not match" in brain_invalid.stdout and "retrieval tests passed" in brain_invalid.stdout

        book_source = target / "book-source.md"
        book_source.write_text("# Part One\n\n## Decision Loop\n\nObserve, decide, act, and review evidence.\n", encoding="utf-8")
        extracted_dir = target / "book-extracted"
        extraction = invoke_plain_json(book / "extract_book_sources.py", str(book_source), "--output-dir", str(extracted_dir), "--mode", "technical")
        metadata = json.loads((extracted_dir / "metadata.json").read_text(encoding="utf-8"))
        assert extraction["sources"] == 1 and metadata["sources"][0]["content_sha256"] == hashlib.sha256(book_source.read_bytes()).hexdigest()
        assert "SOURCE 1: book-source.md" in (extracted_dir / "full_text.txt").read_text(encoding="utf-8")
        destination = target / "career-application.md"
        destination.write_text("# Career application\n\nUse the Decision Loop in weekly review experiments.\n", encoding="utf-8")
        destination_hash = hashlib.sha256(destination.read_bytes()).hexdigest()
        book_manifest = {
            "conversion_id": "book-test-001", "owner": "fixture-owner", "version": "1.0.0", "mode": "full",
            "primary_destination": "career", "source_manifest_ref": str(extracted_dir / "metadata.json"),
            "source_ids": ["source-001"], "rights_status": "private-use", "content_type": "technical", "depth": "application",
            "structure": {"chapters_detected": 1, "chapter_map_ref": "book-source.md#part-one", "extraction_status": "passed"},
            "frameworks": [{"framework_id": "fw-decision-loop", "exact_name": "Decision Loop", "source_id": "source-001", "locators": ["book-source.md#decision-loop"]}],
            "destination_artifacts": [{"artifact_id": "career-pack", "path": "career-application.md", "sha256": destination_hash, "status": "tested"}],
            "traceability": [{"material_id": "fw-decision-loop", "source_id": "source-001", "locators": ["book-source.md#decision-loop"]}],
            "tests": [
                {"test_id": "t-trace", "scope": "traceability", "status": "passed", "evidence_ref": "manual-locator-check"},
                {"test_id": "t-retrieve", "scope": "retrieval", "status": "passed", "evidence_ref": "query-test"},
                {"test_id": "t-apply", "scope": "application", "status": "passed", "evidence_ref": "scenario-test"},
            ],
            "publication": {"status": "not-published", "visibility": "private", "authority_ref": ""},
            "limitations": ["Single synthetic chapter fixture"], "status": "tested", "updated_at": "2026-08-14T00:00:00Z",
        }
        book_manifest_path = target / "book-conversion.json"
        book_manifest_path.write_text(json.dumps(book_manifest), encoding="utf-8")
        book_valid = subprocess.run(
            [sys.executable, str(book / "validate_book_conversion.py"), str(book_manifest_path), "--root", str(target), "--mode", "complete"],
            cwd=ROOT, text=True, encoding="utf-8", capture_output=True, check=False,
        )
        assert book_valid.returncode == 0 and "source, structure, traceability" in book_valid.stdout
        invalid_book = json.loads(json.dumps(book_manifest))
        invalid_book["rights_status"] = "unverified"
        invalid_book["structure"]["extraction_status"] = "failed"
        invalid_book["traceability"] = []
        invalid_book["destination_artifacts"][0]["status"] = "draft"
        invalid_book["tests"][1]["status"] = "failed"
        invalid_book_path = target / "book-conversion-invalid.json"
        invalid_book_path.write_text(json.dumps(invalid_book), encoding="utf-8")
        book_invalid = subprocess.run(
            [sys.executable, str(book / "validate_book_conversion.py"), str(invalid_book_path), "--root", str(target), "--mode", "complete"],
            cwd=ROOT, text=True, encoding="utf-8", capture_output=True, check=False,
        )
        assert book_invalid.returncode == 1
        assert "resolved, non-blocked rights" in book_invalid.stdout and "frameworks missing traceability" in book_invalid.stdout and "failed tests remain unresolved" in book_invalid.stdout

        learner_memory = {
            "memory_id": "learner-memory-test-001",
            "person_id": "fixture-person",
            "version": "1.0.0",
            "privacy_classification": "private",
            "authority": {
                "owner": "fixture-person",
                "canonical_path": str(target / "learner-memory.json"),
                "storage_scope": "user",
            },
            "current_focus": ["dbt"],
            "topics": [
                {
                    "topic_id": "airflow", "display_name": "Apache Airflow", "skill_ids": ["data-engineering"],
                    "status": "mastered", "mastery_level": 5, "confidence": 0.9,
                    "compact_summary": "Can design idempotent DAGs, retries and observable orchestration boundaries.",
                    "concepts": ["DAG", "scheduling", "idempotency"],
                    "decision_rules": ["Keep transformation logic out of the scheduler"],
                    "interfaces": ["Airflow invokes dbt jobs and observes their exit state"],
                    "failure_modes": ["non-idempotent retry", "hidden transformation in operator code"],
                    "prerequisites": [], "relevance_to": ["dbt"],
                    "evidence_refs": ["e-airflow-project", "e-airflow-transfer"],
                    "last_learned_at": "2026-07-01T00:00:00Z", "last_demonstrated_at": "2026-08-01T00:00:00Z",
                    "review_due_at": "2027-02-01T00:00:00Z", "source_version": "Airflow 3.x", "limitations": [],
                },
                {
                    "topic_id": "dbt", "display_name": "dbt", "skill_ids": ["analytics-engineering"],
                    "status": "exposed", "mastery_level": 1, "confidence": 0.3, "compact_summary": "Beginning dbt study.",
                    "concepts": [], "decision_rules": [], "interfaces": [], "failure_modes": [],
                    "prerequisites": ["airflow"], "relevance_to": [], "evidence_refs": [],
                    "last_learned_at": "2026-08-14T00:00:00Z", "last_demonstrated_at": "",
                    "review_due_at": "", "source_version": "dbt Core 1.x", "limitations": [],
                },
            ],
            "evidence_registry": [
                {"evidence_id": "e-airflow-project", "type": "project", "locator": "repo://airflow-project", "scope": "DAG implementation", "result": "passed review", "validated_at": "2026-08-01T00:00:00Z", "validity_status": "verified", "transfer_scope": "same-context", "sha256": "b" * 64},
                {"evidence_id": "e-airflow-transfer", "type": "assessment", "locator": "assessment://airflow-changed-scenario", "scope": "changed-scenario transfer", "result": "passed", "validated_at": "2026-08-02T00:00:00Z", "validity_status": "verified", "transfer_scope": "changed-scenario", "sha256": "c" * 64},
            ],
            "learning_events": [
                {"event_id": "le-airflow-001", "topic_id": "airflow", "event_type": "assessed", "skill_id": "data-career-and-interview-coach", "evidence_refs": ["e-airflow-project", "e-airflow-transfer"], "occurred_at": "2026-08-02T00:00:00Z", "recorded_at": "2026-08-02T01:00:00Z"},
            ],
            "updated_at": "2026-08-14T00:00:00Z",
            "status": "active",
        }
        learner_memory_path = target / "learner-memory.json"
        learner_memory_path.write_text(json.dumps(learner_memory), encoding="utf-8")
        memory_valid = subprocess.run(
            [sys.executable, str(career / "validate_learning_memory.py"), str(learner_memory_path), "--mode", "complete"],
            cwd=ROOT, text=True, encoding="utf-8", capture_output=True, check=False,
        )
        assert memory_valid.returncode == 0 and "mastery evidence" in memory_valid.stdout

        transition = invoke_plain_json(
            career / "build_skill_transition_context.py", str(learner_memory_path),
            "--next-topic", "dbt", "--token-budget", "500",
        )
        assert [item["topic_id"] for item in transition["bridge_summaries"]] == ["airflow"]
        assert transition["expand_or_retest"] == []
        assert transition["estimated_tokens"] <= 500
        assert "DAG implementation" not in json.dumps(transition)

        invalid_memory = json.loads(json.dumps(learner_memory))
        invalid_memory["topics"][0]["evidence_refs"] = []
        invalid_memory["topics"][0]["compact_summary"] = ""
        invalid_memory_path = target / "learner-memory-invalid.json"
        invalid_memory_path.write_text(json.dumps(invalid_memory), encoding="utf-8")
        memory_invalid = subprocess.run(
            [sys.executable, str(career / "validate_learning_memory.py"), str(invalid_memory_path), "--mode", "complete"],
            cwd=ROOT, text=True, encoding="utf-8", capture_output=True, check=False,
        )
        assert memory_invalid.returncode == 1
        assert "verified evidence" in memory_invalid.stdout and "compact_summary" in memory_invalid.stdout

        stale_memory = json.loads(json.dumps(learner_memory))
        stale_memory["topics"][0]["review_due_at"] = "2026-01-01T00:00:00Z"
        stale_memory_path = target / "learner-memory-stale.json"
        stale_memory_path.write_text(json.dumps(stale_memory), encoding="utf-8")
        stale_transition = invoke_plain_json(
            career / "build_skill_transition_context.py", str(stale_memory_path),
            "--next-topic", "dbt", "--token-budget", "500",
        )
        assert stale_transition["bridge_summaries"] == []
        assert [item["topic_id"] for item in stale_transition["expand_or_retest"]] == ["airflow"]
        assert "review is due" in stale_transition["expand_or_retest"][0]["reason"]

        version_transition = invoke_plain_json(
            career / "build_skill_transition_context.py", str(learner_memory_path),
            "--next-topic", "dbt", "--current-version", "airflow=Airflow 4.x", "--token-budget", "500",
        )
        assert version_transition["bridge_summaries"] == []
        assert "source version changed" in version_transition["expand_or_retest"][0]["reason"]

        invalid_transition = subprocess.run(
            [sys.executable, str(career / "build_skill_transition_context.py"), str(invalid_memory_path), "--next-topic", "dbt", "--token-budget", "500"],
            cwd=ROOT, text=True, encoding="utf-8", capture_output=True, check=False,
        )
        assert invalid_transition.returncode == 2
        assert "learner-memory validation failed" in invalid_transition.stderr

    print("benchmark_adapter_tests: 34")
    print("benchmark_fixture_assertions: passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
