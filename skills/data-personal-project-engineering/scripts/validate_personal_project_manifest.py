#!/usr/bin/env python3
"""Validate personal-project provenance, selection, differentiation, artifacts and evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


ENTRY_MODES = {
    "problem-first", "user-workflow-first", "decision-first", "idea-first", "inspiration-first",
    "dataset-first", "repo-first", "role-competency-first", "technology-first", "domain-first",
    "architecture-first", "integration-first", "open-source-issue-first", "paper-replication-first",
    "tutorial-course-first", "incident-failure-first", "constraint-first", "benchmark-first",
    "governance-compliance-first", "hybrid-input",
}
ORIGIN_TYPES = {"self-originated", "inspired-by", "adapted-from", "forked-from", "replicated-from", "contributed-to"}
EXTERNAL_ORIGINS = ORIGIN_TYPES - {"self-originated"}
HARD_GATES = {"rights-and-license", "data-and-privacy", "safe-and-ethical", "feasible-minimum-slice", "observable-success"}
REPO_DIMENSIONS = {
    "purpose-and-users", "architecture-and-data-flow", "runtime-and-reproducibility",
    "data-contracts-and-modeling", "correctness-and-tests", "security-secrets-dependencies",
    "ci-cd-and-supply-chain", "observability-and-reliability", "performance-and-cost",
    "documentation-and-developer-experience", "maintainability-and-activity", "license-and-provenance",
}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def nonempty(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(document: object, root: Path, mode: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(document, dict):
        return ["manifest root must be an object"]
    for field in ("project_id", "owner", "purpose", "entry_mode"):
        if not nonempty(document.get(field)):
            errors.append(f"{field} must be non-empty")
    entry_mode = document.get("entry_mode")
    if entry_mode not in ENTRY_MODES:
        errors.append(f"entry_mode must be one of {sorted(ENTRY_MODES)}")

    origins = document.get("source_origins")
    if not isinstance(origins, list) or not origins:
        errors.append("source_origins must contain at least one source")
        origins = []
    source_ids: set[str] = set()
    external_ids: set[str] = set()
    for index, source in enumerate(origins):
        if not isinstance(source, dict):
            errors.append(f"source_origins[{index}] must be an object")
            continue
        source_id = source.get("source_id")
        if not nonempty(source_id):
            errors.append(f"source_origins[{index}].source_id must be non-empty")
            continue
        if source_id in source_ids:
            errors.append(f"duplicate source_id: {source_id}")
        source_ids.add(str(source_id))
        origin_type = source.get("origin_type")
        if origin_type not in ORIGIN_TYPES:
            errors.append(f"source {source_id}.origin_type is invalid")
        if origin_type in EXTERNAL_ORIGINS:
            external_ids.add(str(source_id))
            for field in ("locator", "author_or_owner", "version_or_commit", "license_or_terms", "allowed_use", "attribution_text"):
                if not nonempty(source.get(field)):
                    errors.append(f"external source {source_id}.{field} must be non-empty")
        digest = str(source.get("content_sha256", "")).lower()
        if mode == "complete" and not SHA256_RE.fullmatch(digest):
            errors.append(f"source {source_id}.content_sha256 must be a full SHA-256 in complete mode")

    thesis = document.get("thesis")
    if not isinstance(thesis, dict):
        errors.append("thesis must be an object")
        thesis = {}
    for field in ("problem", "target_user", "decision_or_outcome", "original_contribution", "origin_statement"):
        if not nonempty(thesis.get(field)):
            errors.append(f"thesis.{field} must be non-empty")
    non_claims = thesis.get("non_claims")
    if not isinstance(non_claims, list) or not all(nonempty(item) for item in non_claims):
        errors.append("thesis.non_claims must contain explicit limitations")
    if external_ids and "self-originated" in str(thesis.get("origin_statement", "")).lower():
        errors.append("external sources cannot be represented as self-originated")

    axes = document.get("differentiation_axes")
    if not isinstance(axes, list):
        errors.append("differentiation_axes must be an array")
        axes = []
    valid_axes: set[str] = set()
    for index, axis in enumerate(axes):
        if not isinstance(axis, dict):
            errors.append(f"differentiation_axes[{index}] must be an object")
            continue
        for field in ("axis", "reference_baseline", "planned_delta", "proof"):
            if not nonempty(axis.get(field)):
                errors.append(f"differentiation_axes[{index}].{field} must be non-empty")
        if nonempty(axis.get("axis")):
            valid_axes.add(str(axis["axis"]))
    minimum_axes = 1 if entry_mode in {"open-source-issue-first", "paper-replication-first"} else 3
    if external_ids and len(valid_axes) < minimum_axes:
        errors.append(f"external-source project requires at least {minimum_axes} substantive differentiation axis/axes")

    selection = document.get("selection")
    if not isinstance(selection, dict):
        errors.append("selection must be an object")
        selection = {}
    gates = selection.get("hard_gates")
    if not isinstance(gates, dict):
        errors.append("selection.hard_gates must be an object")
        gates = {}
    missing_gates = HARD_GATES - set(gates)
    if missing_gates:
        errors.append(f"selection lacks hard gates: {sorted(missing_gates)}")
    if mode == "complete" and any(gates.get(gate) not in {True, "pass"} for gate in HARD_GATES):
        errors.append("all hard gates must pass in complete mode")
    score = selection.get("weighted_score")
    confidence = selection.get("confidence")
    if not isinstance(score, (int, float)) or not 0 <= score <= 100:
        errors.append("selection.weighted_score must be in 0..100")
    if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
        errors.append("selection.confidence must be in 0..1")

    repo_assessment = document.get("repo_assessment")
    if entry_mode == "repo-first":
        if not isinstance(repo_assessment, dict):
            errors.append("repo-first requires repo_assessment")
        else:
            if repo_assessment.get("source_id") not in source_ids:
                errors.append("repo_assessment.source_id must resolve to source_origins")
            reviewed = repo_assessment.get("dimensions_reviewed")
            if not isinstance(reviewed, list):
                errors.append("repo_assessment.dimensions_reviewed must be an array")
                reviewed = []
            missing_dimensions = REPO_DIMENSIONS - set(reviewed)
            if missing_dimensions:
                errors.append(f"repo assessment lacks dimensions: {sorted(missing_dimensions)}")
            if not nonempty(repo_assessment.get("transformation_matrix_ref")):
                errors.append("repo_assessment.transformation_matrix_ref must be non-empty")
            if mode == "complete" and repo_assessment.get("baseline_status") != "passed":
                errors.append("repo-first baseline must pass in complete mode")

    artifacts = document.get("artifacts")
    if not isinstance(artifacts, list):
        errors.append("artifacts must be an array")
        artifacts = []
    artifact_ids: set[str] = set()
    for index, artifact in enumerate(artifacts):
        if not isinstance(artifact, dict) or not nonempty(artifact.get("artifact_id")):
            errors.append(f"artifacts[{index}] is invalid")
            continue
        artifact_id = str(artifact["artifact_id"])
        artifact_ids.add(artifact_id)
        if mode == "complete":
            path_text = artifact.get("path")
            digest = str(artifact.get("sha256", "")).lower()
            if artifact.get("status") not in {"tested", "demonstrated", "released", "maintained"}:
                errors.append(f"artifact {artifact_id} lacks completion status")
            if not nonempty(path_text) or not nonempty(artifact.get("version")) or not SHA256_RE.fullmatch(digest):
                errors.append(f"artifact {artifact_id} requires path, version and SHA-256")
                continue
            path = (root / str(path_text)).resolve()
            try:
                path.relative_to(root.resolve())
            except ValueError:
                errors.append(f"artifact {artifact_id}.path escapes artifact root")
            else:
                if not path.is_file():
                    errors.append(f"artifact {artifact_id} file does not exist")
                elif sha256(path) != digest:
                    errors.append(f"artifact {artifact_id}.sha256 does not match file")

    validations = document.get("validations")
    if not isinstance(validations, list):
        errors.append("validations must be an array")
        validations = []
    passed_scopes: set[str] = set()
    for index, check in enumerate(validations):
        if not isinstance(check, dict) or not nonempty(check.get("validation_id")) or not nonempty(check.get("scope")):
            errors.append(f"validations[{index}] is invalid")
            continue
        if check.get("artifact_id") not in artifact_ids:
            errors.append(f"validation {check.get('validation_id')} references unknown artifact")
        if check.get("status") == "passed" and nonempty(check.get("evidence_ref")):
            passed_scopes.add(str(check["scope"]))
    if mode == "complete":
        required_scopes = {"functional", "reproducibility", "originality-attribution"}
        missing_scopes = required_scopes - passed_scopes
        if missing_scopes:
            errors.append(f"complete project lacks passed validations: {sorted(missing_scopes)}")
        claims = document.get("portfolio_claims")
        if not isinstance(claims, list) or not claims:
            errors.append("complete project requires portfolio_claims")
        elif any(not isinstance(claim, dict) or not nonempty(claim.get("claim")) or not claim.get("evidence_refs") for claim in claims):
            errors.append("every portfolio claim requires wording and evidence_refs")
        if document.get("status") not in {"demonstrated", "released", "maintained"}:
            errors.append("complete mode requires demonstrated, released or maintained status")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--mode", choices=("plan", "complete"), default="complete")
    parser.add_argument("--artifact-root", type=Path)
    args = parser.parse_args()
    try:
        document = json.loads(args.manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    root = (args.artifact_root or args.manifest.parent).resolve()
    errors = validate(document, root, args.mode)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"FAILED: {len(errors)} validation error(s)")
        return 1
    print("PASS: personal-project provenance, selection, differentiation and evidence are valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
