#!/usr/bin/env python3
"""Run static smoke tests over evaluation scenarios and generated artifacts."""

from __future__ import annotations

import json
import re
import subprocess
import tempfile
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"


def parse_simple_eval(path: Path) -> list[dict[str, object]]:
    cases: list[dict[str, object]] = []
    current: dict[str, object] | None = None
    list_key: str | None = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        case_match = re.match(r"^  - id:\s*(.+)$", line)
        if case_match:
            if current:
                cases.append(current)
            current = {"id": case_match.group(1).strip()}
            list_key = None
            continue
        if current is None:
            continue
        field_match = re.match(r"^    ([a-z_]+):\s*(.*)$", line)
        if field_match:
            key, value = field_match.groups()
            if value:
                current[key] = value.strip()
                list_key = None
            else:
                current[key] = []
                list_key = key
            continue
        item_match = re.match(r"^      -\s*(.+)$", line)
        if item_match and list_key:
            cast = current[list_key]
            if isinstance(cast, list):
                cast.append(item_match.group(1).strip())
    if current:
        cases.append(current)
    return cases


def main() -> None:
    errors: list[str] = []
    catalog = json.loads((ROOT / "task-catalog.json").read_text(encoding="utf-8"))
    task_ids = {item["id"] for item in catalog}
    task_by_id = {item["id"]: item for item in catalog}
    skill_ids = {path.name for path in SKILLS.iterdir() if path.is_dir()}
    cases = parse_simple_eval(ROOT / "evaluations" / "routing-cases.yaml")
    for case in cases:
        primary = str(case.get("expected_primary_skill", ""))
        if primary not in skill_ids:
            errors.append(f"{case['id']}: unknown primary skill {primary}")
        for task_id in case.get("expected_tasks", []):
            if task_id not in task_ids:
                errors.append(f"{case['id']}: unknown expected task {task_id}")
    lifecycle_cases = parse_simple_eval(ROOT / "evaluations" / "lifecycle-cases.yaml")
    for case in lifecycle_cases:
        task_id = str(case.get("task", ""))
        item = task_by_id.get(task_id)
        if not item:
            errors.append(f"{case['id']}: unknown lifecycle task {task_id}")
            continue
        if item.get("lifecycle_profile") != case.get("expected_profile"):
            errors.append(f"{case['id']}: profile {item.get('lifecycle_profile')} != {case.get('expected_profile')}")
        if item.get("execution_path") != case.get("expected_path"):
            errors.append(f"{case['id']}: path {item.get('execution_path')} != {case.get('expected_path')}")
    catalog_cases = parse_simple_eval(ROOT / "evaluations" / "catalog-routing-cases.yaml")
    catalog_location: dict[str, str] = {}
    for path in SKILLS.glob("*/references/catalog-*.md"):
        group = path.stem.removeprefix("catalog-")
        for task_id in re.findall(r"\(tasks/([a-z0-9-]+)\.md\)", path.read_text(encoding="utf-8")):
            if task_id in catalog_location:
                errors.append(f"{task_id}: appears in multiple routing catalogs")
            catalog_location[task_id] = group
    for case in catalog_cases:
        task_id = str(case.get("task", ""))
        expected = str(case.get("expected_catalog", ""))
        # A catalog may be split into topic sub-shards (`plan-design-diagram`). The case still
        # asserts the verb group; the sub-shard suffix is an implementation detail.
        actual = catalog_location.get(task_id)
        if actual != expected and not (actual or "").startswith(f"{expected}-"):
            errors.append(f"{case['id']}: catalog {actual} is not in the {expected} group")
    if set(catalog_location) != task_ids:
        errors.append("Catalog shards do not cover every atomic task exactly once")
    confusion_cases = parse_simple_eval(ROOT / "evaluations" / "confusion-pair-cases.yaml")
    for case in confusion_cases:
        primary = str(case.get("expected_primary_skill", ""))
        rejected = str(case.get("rejected_skill", ""))
        task_id = str(case.get("expected_task", ""))
        if primary not in skill_ids:
            errors.append(f"{case['id']}: unknown confusion-pair primary skill {primary}")
        if rejected not in skill_ids or rejected == primary:
            errors.append(f"{case['id']}: invalid rejected skill {rejected}")
        if task_id not in task_ids:
            errors.append(f"{case['id']}: unknown confusion-pair task {task_id}")
    required_assets = [
        "run-state.yaml",
        "question-register.yaml",
        "assumption-register.yaml",
        "conflict-register.yaml",
        "approval-ledger.yaml",
        "evidence-ledger.yaml",
        "handoff-package.yaml",
        "work-ledger.yaml",
        "success-contract.yaml",
        "change-scope-ledger.yaml",
        "change-scope-contract.json",
        "verification-claims.yaml",
        "workflow-manifest.json",
        "approval-record.json",
        "telemetry-event.json",
    ]
    asset_root = SKILLS / "data-department-orchestrator" / "assets"
    for asset in required_assets:
        if not (asset_root / asset).exists():
            errors.append(f"Missing orchestrator asset {asset}")
    content_validator = SKILLS / "data-technical-content-and-social" / "scripts" / "validate_content_manifest.py"
    content_cases = [
        (ROOT / "evaluations" / "fixtures" / "content-complete" / "content-manifest.json", [], 0, []),
        (ROOT / "evaluations" / "fixtures" / "content-manifest-valid.json", ["--mode", "plan"], 0, []),
        (
            ROOT / "evaluations" / "fixtures" / "content-manifest-invalid.json",
            [],
            1,
            ["language must be en for linkedin", "lacks mandatory media roles"],
        ),
    ]
    for manifest_path, extra, expected_exit, expected_texts in content_cases:
        result = subprocess.run(
            [sys.executable, str(content_validator), str(manifest_path), *extra],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != expected_exit:
            errors.append(f"content validator {manifest_path.name}: exit {result.returncode} != {expected_exit}")
        for expected_text in expected_texts:
            if expected_text not in result.stdout:
                errors.append(f"content validator {manifest_path.name}: missing regression signal {expected_text!r}")
    # Generated per-skill workflows: check the structure the generator is responsible for.
    # `owner` is deliberately empty in the shipped templates — nobody owns a template — so it is
    # stubbed in a throwaway copy rather than written into the file to make a validator pass.
    # The eval files are parsed here by a hand-rolled reader that tolerates unquoted colons, so a
    # file can be valid to this suite and invalid to every other YAML consumer. Check them as YAML.
    try:
        import yaml as _yaml
    except ImportError:
        _yaml = None
    if _yaml is not None:
        for case_file in sorted((ROOT / "evaluations").glob("*.yaml")):
            try:
                _yaml.safe_load(case_file.read_text(encoding="utf-8"))
            except _yaml.YAMLError as exc:
                mark = getattr(exc, "problem_mark", None)
                where = f" line {mark.line + 1}" if mark else ""
                errors.append(f"{case_file.name}: not valid YAML{where}")

    # Asset templates must parse as the format their extension promises.
    for asset in sorted(SKILLS.glob("*/assets/*.json")):
        try:
            json.loads(asset.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{asset.parent.parent.name}/{asset.name}: not valid JSON ({exc.msg})")

    # The registry and the corpus plans are generated; a stale plan points at keys that moved.
    for tool, label in [("build_concept_registry.py", "concept registry"),
                        ("build_corpus_plans.py", "corpus plans")]:
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools" / tool), "--check"],
            capture_output=True, text=True, check=False,
        )
        if result.returncode != 0:
            errors.append(f"{label} out of date; regenerate with tools/{tool}")

    # Every planned note must bind to a key the registry actually has.
    registry_path = ROOT / "docs" / "concept-registry.json"
    if registry_path.exists():
        known = {k["concept_key"] for k in json.loads(registry_path.read_text(encoding="utf-8"))["keys"]}
        for plan_path in sorted((ROOT / "docs" / "corpus-plans").glob("*.corpus.json")):
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            for note in plan.get("notes", []):
                unknown = [k for k in note.get("concept_keys", []) if k not in known]
                if unknown:
                    errors.append(f"{plan_path.name}: {note['id']} binds unregistered {unknown[0]}")
                    break
            if any(n.get("status") != "planned" for n in plan.get("notes", [])):
                errors.append(f"{plan_path.name}: a generated plan must contain only planned notes")

    # The prose tells are advisory in the corpus validator, so nothing else would notice if the
    # detector stopped detecting. Exercise it against a deliberately machine-shaped fixture.
    sys.path.insert(0, str(SKILLS / "data-academy-and-curriculum" / "scripts"))
    try:
        import importlib.util as _ilu
        _spec = _ilu.spec_from_file_location(
            "_corpus_validator", SKILLS / "data-academy-and-curriculum" / "scripts" / "validate_note_corpus.py")
        _mod = _ilu.module_from_spec(_spec)
        _spec.loader.exec_module(_mod)
        _sample = (ROOT / "evaluations" / "fixtures" / "prose-machine" / "machine.md").read_text(encoding="utf-8")
        _tells = _mod.check_prose_tells(_sample)
        for _want in ("structure announcement", "cannot be checked", "two-handed", "sentence lengths vary"):
            if not any(_want in t for t in _tells):
                errors.append(f"prose detector no longer reports {_want!r}")
    except Exception as exc:  # a detector that cannot run is a detector that reports nothing
        errors.append(f"prose detector failed to run: {exc}")

    # The eval harness owns case correctness; smoke only checks it still runs and stays green,
    # so the two do not drift into separate opinions about the same files.
    harness_run = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "eval_harness.py"), "run"],
        capture_output=True, text=True, check=False,
    )
    if harness_run.returncode != 0:
        first = next((l for l in harness_run.stdout.splitlines() if l.startswith("FAIL")), "unknown")
        errors.append(f"eval harness: {first}")

    # The retrieval index is generated; a stale one sends readers to contracts that moved.
    index_path = ROOT / "docs" / "retrieval-index.json"
    if not index_path.exists():
        errors.append("missing docs/retrieval-index.json")
    else:
        index = json.loads(index_path.read_text(encoding="utf-8"))
        indexed = {t["id"] for t in index.get("tasks", [])}
        if indexed != task_ids:
            errors.append(
                f"retrieval index covers {len(indexed)} of {len(task_ids)} tasks; "
                f"missing {sorted(task_ids - indexed)[:3]}"
            )
        for entry in index.get("tasks", []):
            if not entry.get("keywords"):
                errors.append(f"retrieval index: {entry['id']} has no keywords")
                break

    workflow_validator = SKILLS / "data-department-orchestrator" / "scripts" / "validate_workflow.py"
    workflow_files = sorted((ROOT / "workflows").glob("*.workflow.json"))
    if not workflow_files:
        errors.append("no generated workflows in workflows/")
    skill_dirs = {d.name for d in SKILLS.iterdir() if d.is_dir()}
    for path in workflow_files:
        manifest = json.loads(path.read_text(encoding="utf-8"))
        if any(t.get("owner") for t in manifest.get("tasks", [])):
            errors.append(f"{path.name}: a template must not claim an owner")
        probe = json.loads(json.dumps(manifest))
        for task in probe["tasks"]:
            task["owner"] = "probe"
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as tmp:
            json.dump(probe, tmp, ensure_ascii=False)
            probe_path = tmp.name
        result = subprocess.run(
            [sys.executable, str(workflow_validator), probe_path,
             "--catalog", str(ROOT / "task-catalog.json"), "--mode", "plan"],
            capture_output=True, text=True, check=False,
        )
        Path(probe_path).unlink(missing_ok=True)
        if result.returncode != 0:
            first = next((l for l in result.stdout.splitlines() if l.startswith("ERROR")), "unknown")
            errors.append(f"{path.name}: {first}")
    covered = {t["task_id"] for p in workflow_files
               for t in json.loads(p.read_text(encoding="utf-8"))["tasks"]}
    if covered != task_ids:
        errors.append(
            f"workflows cover {len(covered)} of {len(task_ids)} tasks; "
            f"missing {sorted(task_ids - covered)[:3]}"
        )
    named = {p.name.removesuffix(".workflow.json") for p in workflow_files}
    for missing in sorted(skill_dirs - named):
        errors.append(f"no workflow for skill {missing}")

    diagram_validator = SKILLS / "data-documentation-and-diagrams" / "scripts" / "validate_diagram_source.py"
    diagram_dir = ROOT / "evaluations" / "fixtures" / "diagram-provenance"
    diagram_cases = [
        (
            diagram_validator,
            [str(diagram_dir / "pipeline.mmd"), "--provenance", str(diagram_dir / "good.json"), "--no-alt-text-required"],
            0,
            ["every node claims an inspected source"],
        ),
        (
            diagram_validator,
            [str(diagram_dir / "pipeline.mmd"), "--provenance", str(diagram_dir / "bad.json"), "--no-alt-text-required"],
            1,
            [
                "has no provenance entry",
                "has no version anchor",
                "derived from another diagram",
                "is not an inspected artifact",
            ],
        ),
    ]
    for validator, argv, expected_exit, expected_texts in diagram_cases:
        result = subprocess.run([sys.executable, str(validator), *argv], capture_output=True, text=True, check=False)
        if result.returncode != expected_exit:
            errors.append(f"{validator.name} provenance: exit {result.returncode} != {expected_exit}")
        for expected_text in expected_texts:
            if expected_text not in result.stdout:
                errors.append(f"{validator.name} provenance: missing regression signal {expected_text!r}")
    corpus_validator = SKILLS / "data-academy-and-curriculum" / "scripts" / "validate_note_corpus.py"
    registry_validator = SKILLS / "data-career-and-interview-coach" / "scripts" / "validate_concept_registry.py"
    fixtures = ROOT / "evaluations" / "fixtures"
    learning_cases = [
        (corpus_validator, [str(fixtures / "note-corpus-manifest-valid.json")], 0, []),
        (
            corpus_validator,
            [
                str(fixtures / "note-corpus-slop" / "manifest.json"),
                "--note-root",
                str(fixtures / "note-corpus-slop" / "notes"),
            ],
            0,
            [
                "scene-setting opener",
                "delete the frame, keep the noting",
                "structure announcement",
                "three hedges in one sentence",
                "em dashes in one sentence",
            ],
        ),
        (
            registry_validator,
            [str(fixtures / "concept-registry-valid.json"), "--corpus-manifest", str(fixtures / "note-corpus-manifest-valid.json")],
            0,
            [],
        ),
        (
            SKILLS / "data-career-and-interview-coach" / "scripts" / "schedule_topic_review.py",
            [str(fixtures / "learner-memory-schedule.json"), "--today", "2026-08-28"],
            0,
            ["t.spark: due 2026-08-28  (stale: review now)", "version-sensitive x0.5", "3 dependents x0.8"],
        ),
        (
            registry_validator,
            [str(fixtures / "concept-registry-proposed.json")],
            0,
            ["possible duplicate key: ck.proc.idempotency ~ ck.proc.idempotent-write"],
        ),
        (
            registry_validator,
            [str(fixtures / "concept-registry-invalid.json")],
            1,
            [
                "not of the form ck.<domain>.<slug>",
                "no definition sentence",
                "claimed by both",
                "superseded with no successor named",
            ],
        ),
    ]
    for validator, argv, expected_exit, expected_texts in learning_cases:
        result = subprocess.run(
            [sys.executable, str(validator), *argv],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != expected_exit:
            errors.append(f"{validator.name}: exit {result.returncode} != {expected_exit}")
        for expected_text in expected_texts:
            if expected_text not in result.stdout:
                errors.append(f"{validator.name}: missing regression signal {expected_text!r}")
    project_skill = SKILLS / "data-personal-project-engineering"
    project_validator = project_skill / "scripts" / "validate_personal_project_manifest.py"
    project_cases = [
        (ROOT / "evaluations" / "fixtures" / "personal-project-manifest-valid.json", ["--mode", "plan"], 0, []),
        (
            ROOT / "evaluations" / "fixtures" / "personal-project-manifest-invalid.json",
            ["--mode", "plan"],
            1,
            ["cannot be represented as self-originated", "requires at least 3 substantive differentiation", "repo assessment lacks dimensions"],
        ),
    ]
    for manifest_path, extra, expected_exit, expected_texts in project_cases:
        result = subprocess.run(
            [sys.executable, str(project_validator), str(manifest_path), *extra],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != expected_exit:
            errors.append(f"project validator {manifest_path.name}: exit {result.returncode} != {expected_exit}")
        for expected_text in expected_texts:
            if expected_text not in result.stdout:
                errors.append(f"project validator {manifest_path.name}: missing regression signal {expected_text!r}")
    project_scorer = project_skill / "scripts" / "score_project_options.py"
    score_result = subprocess.run(
        [sys.executable, str(project_scorer), str(ROOT / "evaluations" / "fixtures" / "project-option-scorecard-valid.json")],
        capture_output=True,
        text=True,
        check=False,
    )
    if score_result.returncode != 0 or '"recommended_option_id": "repo-transform"' not in score_result.stdout:
        errors.append("project option scorer did not select the expected eligible option")
    workflow_validator = SKILLS / "data-department-orchestrator" / "scripts" / "validate_workflow.py"
    workflow_cases = [
        (
            ROOT / "evaluations" / "fixtures" / "workflow-valid.json",
            0,
            ["PASS: workflow graph"],
        ),
        (
            ROOT / "evaluations" / "fixtures" / "workflow-invalid.json",
            1,
            ["risk downgrade", "dependency cycle", "verified claim lacks evidence", "invalid status 'pending'"],
        ),
    ]
    for workflow_path, expected_exit, expected_texts in workflow_cases:
        result = subprocess.run(
            [sys.executable, str(workflow_validator), str(workflow_path), "--catalog", str(ROOT / "task-catalog.json"), "--evidence-dir", str(ROOT / "evaluations" / "fixtures" / "workflow-evidence"), "--mode", "complete"],
            capture_output=True, text=True, check=False,
        )
        if result.returncode != expected_exit:
            errors.append(f"workflow validator {workflow_path.name}: exit {result.returncode} != {expected_exit}")
        for expected_text in expected_texts:
            if expected_text not in result.stdout:
                errors.append(f"workflow validator {workflow_path.name}: missing regression signal {expected_text!r}")
    evidence_validator = SKILLS / "shared-data-core" / "scripts" / "validate_evidence_bundle.py"
    evidence_cases = [
        (ROOT / "evaluations" / "fixtures" / "evidence-envelope-valid.json", 0, ["cryptographically valid"]),
        (ROOT / "evaluations" / "fixtures" / "evidence-envelope-invalid.json", 1, ["artifact_sha256", "complete bundle cannot contain status 'not-run'", "artifact does not exist"]),
    ]
    for evidence_path, expected_exit, expected_texts in evidence_cases:
        result = subprocess.run(
            [sys.executable, str(evidence_validator), str(evidence_path), "--artifact-root", str(ROOT / "evaluations" / "fixtures"), "--mode", "complete"],
            capture_output=True, text=True, check=False,
        )
        if result.returncode != expected_exit:
            errors.append(f"evidence validator {evidence_path.name}: exit {result.returncode} != {expected_exit}")
        for expected_text in expected_texts:
            if expected_text not in result.stdout:
                errors.append(f"evidence validator {evidence_path.name}: missing regression signal {expected_text!r}")
    portfolio_builder = project_skill / "scripts" / "build_portfolio_evidence.py"
    portfolio_cases = [
        (ROOT / "evaluations" / "fixtures" / "portfolio-manifest-valid.json", 0, ["\"verified_claims\": 1"]),
        (ROOT / "evaluations" / "fixtures" / "personal-project-manifest-valid.json", 1, ["strict portfolio evidence requires at least one artifact", "strict portfolio evidence requires at least one structured claim"]),
    ]
    for manifest_path, expected_exit, expected_texts in portfolio_cases:
        result = subprocess.run(
            [sys.executable, str(portfolio_builder), str(manifest_path), "--project-root", str(ROOT / "evaluations" / "fixtures"), "--strict"],
            capture_output=True, text=True, check=False,
        )
        if result.returncode != expected_exit:
            errors.append(f"portfolio builder {manifest_path.name}: exit {result.returncode} != {expected_exit}")
        for expected_text in expected_texts:
            if expected_text not in result.stdout:
                errors.append(f"portfolio builder {manifest_path.name}: missing regression signal {expected_text!r}")
    telemetry_recorder = SKILLS / "data-department-orchestrator" / "scripts" / "record_skill_telemetry.py"
    telemetry_result = subprocess.run(
        [sys.executable, str(telemetry_recorder), str(ROOT / "evaluations" / "fixtures" / "telemetry-event-invalid.json"), "--output", str(ROOT / "evaluations" / "fixtures" / "must-not-be-created.jsonl")],
        capture_output=True, text=True, check=False,
    )
    if telemetry_result.returncode != 1 or "user_content must be null" not in telemetry_result.stdout:
        errors.append("telemetry recorder did not reject user content")
    if (ROOT / "evaluations" / "fixtures" / "must-not-be-created.jsonl").exists():
        errors.append("invalid telemetry unexpectedly created an output file")
    criticality = {name: sum(item.get("criticality") == name for item in catalog) for name in ("standard", "deep", "enforced")}
    adapter_count = len(list(SKILLS.glob("*/references/adapter-*.md")))
    print(f"routing_cases: {len(cases)}")
    print(f"lifecycle_cases: {len(lifecycle_cases)}")
    print(f"catalog_routing_cases: {len(catalog_cases)}")
    print(f"confusion_pair_cases: {len(confusion_cases)}")
    print(f"catalog_tasks: {len(task_ids)}")
    print(f"skills: {len(skill_ids)}")
    print(f"deep_contracts: {criticality['deep']}")
    print(f"enforced_contracts: {criticality['enforced']}")
    print(f"stack_adapter_packs: {adapter_count}")
    print(f"errors: {len(errors)}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        sys.exit(1)
    print("Smoke tests passed")


if __name__ == "__main__":
    main()
