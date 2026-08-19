#!/usr/bin/env python3
"""Validate structure, contracts, links, metadata, manifests and task coverage."""

from __future__ import annotations

import json
import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"


def canonical_text_sha256(path: Path) -> str:
    """Hash canonical UTF-8/LF text so validation is OS-independent."""
    normalized = path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
REQUIRED_TASK_SECTIONS = [
    "Trigger",
    "Contract",
    "Inputs and readiness",
    "Procedure",
    "Tests and evidence",
    "Approval and done",
    "Return",
]
PEOPLE_RESOURCES = {
    "data-enablement-and-knowledge": {
        "references": ["linked-knowledge-library.md"],
        "assets": ["concept-knowledge-map.yaml", "knowledge-library.yaml"],
    },
    "data-academy-and-curriculum": {
        "references": ["role-curricula.md", "assessment-and-certification.md", "knowledge-deep-dive-standard.md"],
        "assets": ["curriculum-spec.yaml", "lesson-plan.yaml", "assessment-blueprint.yaml", "learner-evidence.yaml", "concept-knowledge-graph.yaml", "knowledge-deep-dive.yaml", "question-learning-traceability.yaml"],
        "scripts": ["validate_curriculum_coverage.py"],
    },
    "data-onboarding-and-integration": {
        "references": ["role-onboarding-tracks.md"],
        "assets": ["onboarding-plan.yaml", "access-readiness.yaml", "checkpoint.yaml"],
    },
    "data-talent-acquisition-and-interview": {
        "references": ["role-interview-architecture.md", "question-knowledge-validity.md"],
        "assets": ["hiring-workflow-state.yaml", "role-scorecard.yaml", "interview-loop.yaml", "candidate-packet.yaml", "assessment-rubric.yaml", "interviewer-guide.yaml", "calibration-record.yaml", "interview-evidence.yaml", "debrief.yaml", "fairness-validity-audit.yaml", "question-competency-evidence.yaml", "answer-anchor-pack.yaml", "question-bank-coverage-audit.yaml"],
    },
    "data-career-and-interview-coach": {
        "references": ["coaching-ethics-and-method.md", "role-curricula.md", "interview-knowledge-system.md", "career-operating-system.md", "career-learning-memory.md"],
        "assets": ["readiness-profile.yaml", "mock-assessment.yaml", "remediation-plan.yaml", "interview-question-dossier.yaml", "question-knowledge-map.yaml", "interview-knowledge-library.yaml", "career-operating-system.yaml", "career-evidence-portfolio.yaml", "career-review.yaml", "career-content-handoff.yaml", "learner-memory.json", "learning-event.yaml", "cross-skill-prerequisite-map.yaml", "skill-transition-context.json", "learner-memory.schema.json"],
        "scripts": ["validate_learning_memory.py", "build_skill_transition_context.py"],
    },
    "data-technical-content-and-social": {
        "references": ["technical-series-method.md", "platform-format-playbooks.md", "technical-content-quality-standard.md"],
        "assets": ["technical-series-plan.yaml", "episode-brief.yaml", "source-pack.yaml", "content-manifest.json", "editorial-calendar.yaml", "content-quality-review.yaml"],
        "scripts": ["validate_content_manifest.py"],
    },
    "personal-second-brain-and-knowledge-os": {
        "references": ["second-brain-operating-system.md", "knowledge-note-and-lineage-standard.md", "retrieval-and-output-grounding.md", "migration-and-tool-interop.md", "second-brain-quality-and-safety.md"],
        "assets": ["second-brain-manifest.json", "source-record.yaml", "wiki-note.yaml", "personal-context.yaml", "output-record.yaml", "migration-plan.yaml", "retrieval-evaluation.yaml", "knowledge-review.yaml", "second-brain-manifest.schema.json"],
        "scripts": ["build_brain_index.py", "validate_second_brain.py"],
    },
    "book-to-knowledge-and-action": {
        "references": ["book-conversion-operating-system.md", "source-extraction-and-structure.md", "knowledge-distillation-and-application.md", "destination-packs.md", "copyright-security-and-quality.md"],
        "assets": ["book-conversion-manifest.json", "book-source-manifest.yaml", "framework-card.yaml", "chapter-note.yaml", "destination-plan.yaml", "application-experiment.yaml", "conversion-evidence.yaml", "book-conversion-manifest.schema.json"],
        "scripts": ["extract_book_sources.py", "validate_book_conversion.py"],
    },
}

BENCHMARK_RESOURCES = {
    "shared-data-core": {
        "references": ["context-engineering-standard.md", "execution-discipline-standard.md"],
        "assets": ["task-context-package.yaml", "success-contract.yaml", "change-scope-ledger.yaml", "change-scope-contract.json", "debug-hypothesis-ledger.yaml", "verification-claims.yaml", "atomic-task-output.yaml", "atomic-task-result.schema.json", "project-constitution.json", "project-constitution.schema.json"],
        "scripts": ["build_context_package.py", "audit_change_scope.py", "validate_evidence_bundle.py", "validate_task_result.py", "verify_deliverable.py", "validate_constitution.py"],
    },
    "data-department-orchestrator": {
        "references": ["lifecycle-standard.md"],
        "assets": ["workflow-manifest.json", "run-state.yaml", "run-state.schema.json", "approval-record.json", "approval-record.schema.json", "task-catalog.json", "instinct-ledger.json", "instinct-record.schema.json"],
        "scripts": ["validate_workflow.py", "validate_approval_record.py", "validate_run_state.py", "manage_instincts.py", "score_skill_quality.py"],
    },
    "company-data-context": {
        "references": ["context-engineering-standard.md"],
        "assets": ["context-index.yaml"],
        "scripts": ["build_context_package.py"],
    },
    "data-developer-experience": {
        "references": ["evidence-based-repository-understanding.md"],
        "assets": ["data-path-trace.yaml"],
        "scripts": ["build_code_index.py"],
    },
    "data-enablement-and-knowledge": {
        "references": ["evidence-based-repository-understanding.md"],
        "assets": ["data-path-trace.yaml"],
        "scripts": [],
    },
    "data-architecture": {
        "references": ["lifecycle-standard.md"],
        "assets": [],
        "scripts": ["scan_architecture_drift.py"],
    },
    "data-engineering": {
        "references": ["execution-plan-and-pipeline-adapters.md", "stage-gated-data-validation.md"],
        "assets": ["execution-plan-review.yaml", "pipeline-validation-plan.yaml"],
        "scripts": ["inspect_execution_plan.py"],
    },
    "analytics-engineering": {
        "references": ["execution-plan-and-pipeline-adapters.md"],
        "assets": ["execution-plan-review.yaml"],
        "scripts": ["inspect_execution_plan.py"],
    },
    "data-analysis": {
        "references": ["analysis-rigor-and-communication.md"],
        "assets": ["eda-report.yaml", "query-logic-explanation.yaml", "methodology-note.yaml", "analysis-peer-review.yaml", "analysis-retrospective.yaml", "impact-estimate.yaml"],
        "scripts": ["profile_dataset.py", "explain_sql.py"],
    },
    "data-quality-and-reliability": {
        "references": ["stage-gated-data-validation.md"],
        "assets": ["pipeline-validation-plan.yaml"],
        "scripts": ["validate_tabular_data.py"],
    },
    "business-intelligence": {
        "references": ["dashboard-experience-quality.md"],
        "assets": ["dashboard-experience-audit.yaml"],
        "scripts": ["validate_dashboard_spec.py"],
    },
    "data-governance-and-stewardship": {
        "references": ["lifecycle-standard.md"],
        "assets": [],
        "scripts": ["validate_policy_coverage.py"],
    },
    "data-business-analysis": {
        "references": ["lifecycle-standard.md"],
        "assets": [],
        "scripts": ["validate_requirements_traceability.py"],
    },
}


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def frontmatter(text: str, source: Path, errors: list[str]) -> dict:
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not match:
        fail(errors, f"{source}: invalid frontmatter")
        return {}
    data: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, separator, value = line.partition(":")
        if not separator or not key.strip() or not value.strip():
            fail(errors, f"{source}: invalid frontmatter line {line!r}")
            continue
        data[key.strip()] = value.strip().strip('"')
    if set(data) != {"name", "description"}:
        fail(errors, f"{source}: frontmatter must contain only name and description")
    name = data.get("name", "")
    description = data.get("description", "")
    if not re.fullmatch(r"[a-z0-9-]{1,64}", str(name)):
        fail(errors, f"{source}: invalid name {name!r}")
    if not isinstance(description, str) or not description or len(description) > 1024:
        fail(errors, f"{source}: invalid description")
    if "<" in str(description) or ">" in str(description):
        fail(errors, f"{source}: description contains angle brackets")
    return data


def validate() -> tuple[list[str], dict[str, int]]:
    errors: list[str] = []
    skill_dirs = sorted(path for path in SKILLS.iterdir() if path.is_dir())
    task_ids: list[str] = []
    linked_tasks: list[str] = []

    for skill_dir in skill_dirs:
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            fail(errors, f"{skill_dir}: missing SKILL.md")
            continue
        text = skill_md.read_text(encoding="utf-8")
        data = frontmatter(text, skill_md, errors)
        if data.get("name") != skill_dir.name:
            fail(errors, f"{skill_md}: name does not match directory")
        if len(text.splitlines()) >= 500:
            fail(errors, f"{skill_md}: must stay below 500 lines")
        if "TODO" in text:
            fail(errors, f"{skill_md}: unresolved TODO")

        shared_manifest_path = skill_dir / "references" / "shared-reference-manifest.json"
        if not shared_manifest_path.exists():
            fail(errors, f"{skill_dir}: missing shared-reference-manifest.json")
        else:
            try:
                shared_manifest = json.loads(shared_manifest_path.read_text(encoding="utf-8"))
                for entry in shared_manifest.get("references", []):
                    reference = skill_dir / "references" / entry["filename"]
                    if not reference.is_file():
                        fail(errors, f"{shared_manifest_path}: missing {entry['filename']}")
                        continue
                    observed = canonical_text_sha256(reference)
                    if observed != entry.get("sha256"):
                        fail(errors, f"{shared_manifest_path}: hash mismatch for {entry['filename']}")
            except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
                fail(errors, f"{shared_manifest_path}: invalid manifest: {exc}")

        # Cross-client UI metadata is optional and excluded from Claude-native releases.
        openai_yaml = skill_dir / "agents" / "openai.yaml"
        if openai_yaml.exists():
            try:
                openai_text = openai_yaml.read_text(encoding="utf-8")
                short_match = re.search(r'^\s*short_description:\s*"(.*)"\s*$', openai_text, re.M)
                prompt_match = re.search(r'^\s*default_prompt:\s*"(.*)"\s*$', openai_text, re.M)
                if not short_match or not prompt_match:
                    raise ValueError("missing interface fields")
                short = short_match.group(1)
                prompt = prompt_match.group(1)
                if not 25 <= len(short) <= 64:
                    fail(errors, f"{openai_yaml}: short_description must be 25-64 chars")
                if f"${skill_dir.name}" not in prompt:
                    fail(errors, f"{openai_yaml}: default_prompt must mention ${skill_dir.name}")
            except (TypeError, ValueError) as exc:
                fail(errors, f"{openai_yaml}: invalid interface: {exc}")

        catalog_links = re.findall(
            r"\(references/(catalog-[a-z0-9-]+\.md)\)", text
        )
        catalog_files = sorted((skill_dir / "references").glob("catalog-*.md"))
        if set(catalog_links) != {path.name for path in catalog_files}:
            fail(errors, f"{skill_md}: catalog links do not match generated catalogs")
        for catalog_file in catalog_files:
            catalog_text = catalog_file.read_text(encoding="utf-8")
            linked_tasks.extend(
                re.findall(r"\(tasks/([a-z0-9-]+)\.md\)", catalog_text)
            )

        tasks_dir = skill_dir / "references" / "tasks"
        if not tasks_dir.exists():
            fail(errors, f"{skill_dir}: missing references/tasks")
            continue
        for task_file in sorted(tasks_dir.glob("*.md")):
            task_id = task_file.stem
            task_ids.append(task_id)
            task_text = task_file.read_text(encoding="utf-8")
            if not re.fullmatch(r"[a-z0-9-]{1,64}", task_id):
                fail(errors, f"{task_file}: invalid task ID")
            if not task_text.startswith(f"# {task_id}\n"):
                fail(errors, f"{task_file}: heading must match filename")
            for section in REQUIRED_TASK_SECTIONS:
                if f"## {section}\n" not in task_text:
                    fail(errors, f"{task_file}: missing section {section}")

        for ref in ("lifecycle-standard.md", "technology-adapters.md", "industry-and-metrics.md", "safety-and-approvals.md", "workflow-runtime-and-evidence-os.md"):
            if not (skill_dir / "references" / ref).exists():
                fail(errors, f"{skill_dir}: missing references/{ref}")
        memory_interop = skill_dir / "references" / "learning-memory-interoperability.md"
        if not memory_interop.exists():
            fail(errors, f"{skill_dir}: missing references/learning-memory-interoperability.md")
        elif "learning-memory-interoperability.md" not in text:
            fail(errors, f"{skill_md}: learner-memory interoperability is not routed")

        people_resources = PEOPLE_RESOURCES.get(skill_dir.name)
        if people_resources:
            for ref in people_resources["references"]:
                if not (skill_dir / "references" / ref).exists():
                    fail(errors, f"{skill_dir}: missing references/{ref}")
                if ref not in "\n".join(
                    path.read_text(encoding="utf-8") for path in sorted(tasks_dir.glob("*.md"))
                ):
                    fail(errors, f"{skill_dir}: tasks do not route to references/{ref}")
            for asset in people_resources["assets"]:
                if not (skill_dir / "assets" / asset).exists():
                    fail(errors, f"{skill_dir}: missing assets/{asset}")
            for script in people_resources.get("scripts", []):
                if not (skill_dir / "scripts" / script).exists():
                    fail(errors, f"{skill_dir}: missing scripts/{script}")

        benchmark_resources = BENCHMARK_RESOURCES.get(skill_dir.name)
        if benchmark_resources:
            task_corpus = "\n".join(
                path.read_text(encoding="utf-8") for path in sorted(tasks_dir.glob("*.md"))
            )
            for ref in benchmark_resources["references"]:
                if not (skill_dir / "references" / ref).exists():
                    fail(errors, f"{skill_dir}: missing references/{ref}")
                if ref not in task_corpus:
                    fail(errors, f"{skill_dir}: tasks do not route to references/{ref}")
            for asset in benchmark_resources["assets"]:
                if not (skill_dir / "assets" / asset).exists():
                    fail(errors, f"{skill_dir}: missing assets/{asset}")
            for script in benchmark_resources["scripts"]:
                if not (skill_dir / "scripts" / script).exists():
                    fail(errors, f"{skill_dir}: missing scripts/{script}")

    if len(task_ids) != len(set(task_ids)):
        duplicates = sorted({item for item in task_ids if task_ids.count(item) > 1})
        fail(errors, f"Duplicate task IDs: {duplicates}")
    if set(task_ids) != set(linked_tasks):
        missing_links = sorted(set(task_ids) - set(linked_tasks))
        broken_links = sorted(set(linked_tasks) - set(task_ids))
        if missing_links:
            fail(errors, f"Unlinked task files: {missing_links[:10]}")
        if broken_links:
            fail(errors, f"Broken task links: {broken_links[:10]}")

    catalog_path = ROOT / "task-catalog.json"
    manifest_path = ROOT / "suite-manifest.yaml"
    try:
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        manifest_text = manifest_path.read_text(encoding="utf-8")
        top_match = re.search(r'^top_level_skills:\s*(\d+)\s*$', manifest_text, re.M)
        task_match = re.search(r'^atomic_tasks:\s*(\d+)\s*$', manifest_text, re.M)
        if not top_match or not task_match:
            raise ValueError("missing manifest counts")
        manifest = {"top_level_skills": int(top_match.group(1)), "atomic_tasks": int(task_match.group(1))}
        if len(catalog) != len(task_ids):
            fail(errors, "task-catalog.json count does not match task files")
        valid_profiles = {"advisory-analysis", "design-specification", "build-change", "production-release", "incident-recovery", "governance-assurance", "learning", "onboarding", "hiring", "career-coaching", "career-development"}
        valid_risks = {"R0-light", "R1-reviewed", "R2-standard", "R3-controlled", "R4-critical"}
        valid_paths = {"fast-path", "standard-path", "controlled-path"}
        valid_criticality = {"standard", "deep", "enforced"}
        deep_count = 0
        for item in catalog:
            if item.get("lifecycle_profile") not in valid_profiles:
                fail(errors, f"{item.get('id')}: invalid lifecycle profile")
            if item.get("risk_tier") not in valid_risks:
                fail(errors, f"{item.get('id')}: invalid risk tier")
            if item.get("execution_path") not in valid_paths:
                fail(errors, f"{item.get('id')}: invalid execution path")
            if item.get("contract_version") != "3.0":
                fail(errors, f"{item.get('id')}: task contract must be v3.0")
            if item.get("criticality") not in valid_criticality:
                fail(errors, f"{item.get('id')}: invalid criticality")
            if item.get("criticality") in {"deep", "enforced"}:
                deep_count += 1
                prefix = str(item.get("id", "")).split("-", 1)[0]
                task_path = next(SKILLS.glob(f"*/references/tasks/{item.get('id')}.md"), None)
                if not task_path or "## Deep execution contract\n" not in task_path.read_text(encoding="utf-8"):
                    fail(errors, f"{item.get('id')}: deep/enforced task lacks deep execution contract")
        if deep_count < 100:
            fail(errors, f"v3 requires at least 100 deep/enforced task contracts; found {deep_count}")
        if manifest["top_level_skills"] != len(skill_dirs):
            fail(errors, "suite-manifest top_level_skills count mismatch")
        if manifest["atomic_tasks"] != len(task_ids):
            fail(errors, "suite-manifest atomic_tasks count mismatch")
    except (FileNotFoundError, json.JSONDecodeError, KeyError, ValueError) as exc:
        fail(errors, f"Invalid suite manifest/catalog: {exc}")

    plugin = ROOT / ".claude-plugin" / "plugin.json"
    try:
        plugin_data = json.loads(plugin.read_text(encoding="utf-8"))
        if plugin_data.get("name") != "data-department-agent-skills":
            fail(errors, f"{plugin}: unexpected name")
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        fail(errors, f"Invalid plugin manifest: {exc}")

    required_schemas = {
        "task-contract.schema.json", "workflow-manifest.schema.json", "evidence-envelope.schema.json",
        "approval-record.schema.json", "telemetry-event.schema.json", "run-state.schema.json",
        "atomic-task-result.schema.json", "second-brain-manifest.schema.json",
        "book-conversion-manifest.schema.json",
        "learner-memory.schema.json",
    }
    observed_schemas = {path.name for path in (ROOT / "schemas").glob("*.json")}
    if not required_schemas.issubset(observed_schemas):
        fail(errors, f"Missing v3 schemas: {sorted(required_schemas - observed_schemas)}")
    for schema_name in required_schemas & observed_schemas:
        try:
            schema = json.loads((ROOT / "schemas" / schema_name).read_text(encoding="utf-8"))
            if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
                fail(errors, f"{schema_name}: schema draft must be 2020-12")
        except (OSError, json.JSONDecodeError, TypeError) as exc:
            fail(errors, f"{schema_name}: invalid schema JSON: {exc}")
    required_runtime = [
        SKILLS / "data-department-orchestrator" / "scripts" / "validate_workflow.py",
        SKILLS / "data-department-orchestrator" / "assets" / "workflow-manifest.json",
        SKILLS / "data-department-orchestrator" / "assets" / "approval-record.json",
        SKILLS / "data-department-orchestrator" / "assets" / "task-catalog.json",
        SKILLS / "data-department-orchestrator" / "assets" / "workflow-manifest.schema.json",
        SKILLS / "data-department-orchestrator" / "assets" / "approval-record.schema.json",
        SKILLS / "data-department-orchestrator" / "assets" / "telemetry-event.schema.json",
        SKILLS / "data-department-orchestrator" / "assets" / "task-contract.schema.json",
        SKILLS / "shared-data-core" / "scripts" / "validate_evidence_bundle.py",
        SKILLS / "shared-data-core" / "assets" / "evidence-envelope.json",
        SKILLS / "shared-data-core" / "assets" / "evidence-envelope.schema.json",
        SKILLS / "shared-data-core" / "assets" / "atomic-task-result.schema.json",
        SKILLS / "company-data-context" / "scripts" / "bootstrap_context_index.py",
        SKILLS / "data-developer-experience" / "scripts" / "detect_data_stack.py",
        SKILLS / "data-personal-project-engineering" / "scripts" / "audit_repository.py",
        SKILLS / "data-personal-project-engineering" / "scripts" / "build_portfolio_evidence.py",
        SKILLS / "data-department-orchestrator" / "scripts" / "record_skill_telemetry.py",
        SKILLS / "data-department-orchestrator" / "scripts" / "analyze_skill_telemetry.py",
        SKILLS / "personal-second-brain-and-knowledge-os" / "scripts" / "build_brain_index.py",
        SKILLS / "personal-second-brain-and-knowledge-os" / "scripts" / "validate_second_brain.py",
        SKILLS / "book-to-knowledge-and-action" / "scripts" / "extract_book_sources.py",
        SKILLS / "book-to-knowledge-and-action" / "scripts" / "validate_book_conversion.py",
        SKILLS / "data-career-and-interview-coach" / "scripts" / "validate_learning_memory.py",
        SKILLS / "data-career-and-interview-coach" / "scripts" / "build_skill_transition_context.py",
    ]
    for path in required_runtime:
        if not path.is_file():
            fail(errors, f"Missing v3 runtime resource: {path}")
    catalog_asset = SKILLS / "data-department-orchestrator" / "assets" / "task-catalog.json"
    if catalog_asset.is_file() and catalog_asset.read_bytes() != (ROOT / "task-catalog.json").read_bytes():
        fail(errors, "Orchestrator task-catalog asset is stale")
    adapter_files = list(SKILLS.glob("*/references/adapter-*.md"))
    if len(adapter_files) < 90:
        fail(errors, f"Expected role-scoped stack-native adapters; found only {len(adapter_files)}")
    for path in adapter_files:
        skill_dir = path.parents[1]
        skill_text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        if f"references/{path.name}" not in skill_text:
            fail(errors, f"{path}: adapter is not directly routed from SKILL.md")

    stats = {
        "skills": len(skill_dirs),
        "tasks": len(task_ids),
        "task_links": len(linked_tasks),
        "errors": len(errors),
    }
    return errors, stats


def main() -> None:
    errors, stats = validate()
    for key, value in stats.items():
        print(f"{key}: {value}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        sys.exit(1)
    print("Suite validation passed")


if __name__ == "__main__":
    main()
