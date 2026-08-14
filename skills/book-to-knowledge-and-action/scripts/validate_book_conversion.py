#!/usr/bin/env python3
"""Validate a book-to-knowledge conversion manifest without mutating artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

DESTINATIONS = {"skill", "second-brain", "career", "interview", "project", "curriculum", "workflow", "content"}
RIGHTS = {"unverified", "private-use", "open-license", "owner-authorized", "publication-authorized", "blocked"}
TEST_SCOPES = {"format", "links", "traceability", "copyright", "security", "retrieval", "application", "token-path"}
SUSPICIOUS = {
    "instruction-override": re.compile(r"(?i)ignore (?:all |any )?(?:previous|prior|system) instructions"),
    "secret-exfiltration": re.compile(r"(?i)(?:upload|send|print|reveal).{0,40}(?:secret|credential|\.ssh|api key)"),
    "pipe-to-shell": re.compile(r"(?i)(?:curl|wget).{0,200}\|\s*(?:sh|bash|powershell)"),
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_artifact(root: Path, relative: str, label: str, errors: list[str]) -> Path | None:
    path = (root / relative).resolve()
    try:
        path.relative_to(root)
    except ValueError:
        errors.append(f"{label}: path escapes artifact root: {relative}")
        return None
    return path


def scan_artifact(path: Path, label: str, errors: list[str]) -> None:
    if path.stat().st_size > 2_000_000 or path.suffix.lower() not in {".md", ".txt", ".json", ".yaml", ".yml"}:
        return
    text = path.read_text(encoding="utf-8", errors="ignore")
    for rule, pattern in SUSPICIOUS.items():
        if pattern.search(text):
            errors.append(f"{label}: suspicious generated instruction ({rule})")


def validate(args: argparse.Namespace) -> list[str]:
    errors: list[str] = []
    try:
        manifest = load_json(args.manifest)
    except (OSError, json.JSONDecodeError, TypeError) as exc:
        return [f"invalid manifest JSON: {exc}"]
    if not isinstance(manifest, dict):
        return ["manifest must be an object"]

    for field in ("conversion_id", "owner", "version", "source_manifest_ref", "updated_at"):
        if not str(manifest.get(field, "")).strip():
            errors.append(f"{field} is required")
    if manifest.get("mode") not in {"analyze", "full", "fold-in", "update"}:
        errors.append("invalid mode")
    destination = manifest.get("primary_destination")
    if destination not in DESTINATIONS:
        errors.append("invalid primary_destination")
    rights = manifest.get("rights_status")
    if rights not in RIGHTS:
        errors.append("invalid rights_status")
    if manifest.get("content_type") not in {"text", "technical", "academic", "reference", "visual", "mixed"}:
        errors.append("invalid content_type")
    if manifest.get("depth") not in {"reference", "study", "application"}:
        errors.append("invalid depth")

    source_ids_raw = manifest.get("source_ids")
    if not isinstance(source_ids_raw, list) or not source_ids_raw:
        errors.append("source_ids must be a non-empty array")
        source_ids: set[str] = set()
    else:
        source_ids = {str(item) for item in source_ids_raw if str(item).strip()}
        if len(source_ids) != len(source_ids_raw):
            errors.append("source_ids contain blanks or duplicates")

    structure = manifest.get("structure")
    if not isinstance(structure, dict):
        errors.append("structure must be an object")
        structure = {}
    chapters = structure.get("chapters_detected")
    if not isinstance(chapters, int) or chapters < 0:
        errors.append("structure.chapters_detected must be a non-negative integer")
    if structure.get("extraction_status") not in {"not-run", "partial", "passed", "failed"}:
        errors.append("invalid structure.extraction_status")

    framework_ids: set[str] = set()
    frameworks = manifest.get("frameworks")
    if not isinstance(frameworks, list):
        errors.append("frameworks must be an array")
        frameworks = []
    for index, framework in enumerate(frameworks):
        label = f"frameworks[{index}]"
        if not isinstance(framework, dict):
            errors.append(f"{label} must be an object")
            continue
        framework_id = str(framework.get("framework_id", "")).strip()
        if not framework_id or framework_id in framework_ids:
            errors.append(f"{label}: framework_id missing or duplicate")
        framework_ids.add(framework_id)
        if not str(framework.get("exact_name", "")).strip():
            errors.append(f"{label}.exact_name is required")
        if framework.get("source_id") not in source_ids:
            errors.append(f"{label}: unknown source_id {framework.get('source_id')!r}")
        if not isinstance(framework.get("locators"), list) or not framework.get("locators"):
            errors.append(f"{label}.locators must be non-empty")

    trace_ids: set[str] = set()
    traceability = manifest.get("traceability")
    if not isinstance(traceability, list):
        errors.append("traceability must be an array")
        traceability = []
    for index, row in enumerate(traceability):
        label = f"traceability[{index}]"
        if not isinstance(row, dict):
            errors.append(f"{label} must be an object")
            continue
        material_id = str(row.get("material_id", "")).strip()
        if not material_id:
            errors.append(f"{label}.material_id is required")
        trace_ids.add(material_id)
        if row.get("source_id") not in source_ids:
            errors.append(f"{label}: unknown source_id {row.get('source_id')!r}")
        if not isinstance(row.get("locators"), list) or not row.get("locators"):
            errors.append(f"{label}.locators must be non-empty")

    root = args.root.resolve() if args.root else None
    artifacts = manifest.get("destination_artifacts")
    if not isinstance(artifacts, list):
        errors.append("destination_artifacts must be an array")
        artifacts = []
    artifact_ids: set[str] = set()
    for index, artifact in enumerate(artifacts):
        label = f"destination_artifacts[{index}]"
        if not isinstance(artifact, dict):
            errors.append(f"{label} must be an object")
            continue
        artifact_id = str(artifact.get("artifact_id", "")).strip()
        if not artifact_id or artifact_id in artifact_ids:
            errors.append(f"{label}: artifact_id missing or duplicate")
        artifact_ids.add(artifact_id)
        relative = str(artifact.get("path", "")).strip()
        expected = str(artifact.get("sha256", "")).lower()
        if not relative or not re.fullmatch(r"[a-f0-9]{64}", expected):
            errors.append(f"{label}: path and 64-character SHA-256 are required")
        if artifact.get("status") not in {"draft", "generated", "tested", "approved", "published"}:
            errors.append(f"{label}: invalid status")
        if root is not None and relative:
            path = resolve_artifact(root, relative, label, errors)
            if path is not None:
                if not path.is_file():
                    errors.append(f"{label}: missing artifact {relative}")
                else:
                    if re.fullmatch(r"[a-f0-9]{64}", expected) and sha256(path) != expected:
                        errors.append(f"{label}: SHA-256 mismatch")
                    if args.scan_generated:
                        scan_artifact(path, label, errors)

    tests = manifest.get("tests")
    if not isinstance(tests, list):
        errors.append("tests must be an array")
        tests = []
    passed_scopes: set[str] = set()
    for index, test in enumerate(tests):
        if not isinstance(test, dict):
            errors.append(f"tests[{index}] must be an object")
            continue
        scope = test.get("scope")
        if scope not in TEST_SCOPES:
            errors.append(f"tests[{index}]: invalid scope {scope!r}")
        if test.get("status") == "passed":
            passed_scopes.add(str(scope))
            if not str(test.get("evidence_ref", "")).strip():
                errors.append(f"tests[{index}]: passed test lacks evidence_ref")
        elif test.get("status") not in {"not-run", "failed"}:
            errors.append(f"tests[{index}]: invalid status")

    publication = manifest.get("publication")
    if not isinstance(publication, dict):
        errors.append("publication must be an object")
        publication = {}
    if publication.get("visibility") not in {"private", "public"}:
        errors.append("publication.visibility must be private or public")

    if args.mode in {"complete", "publish"}:
        if rights in {"unverified", "blocked", None}:
            errors.append("complete mode requires resolved, non-blocked rights")
        if structure.get("extraction_status") != "passed":
            errors.append("complete mode requires passed extraction")
        if not frameworks or framework_ids - trace_ids:
            errors.append(f"frameworks missing traceability: {sorted(framework_ids - trace_ids)}")
        if not artifacts or any(a.get("status") not in {"tested", "approved", "published"} for a in artifacts if isinstance(a, dict)):
            errors.append("complete mode requires tested destination artifacts")
        required = {"traceability", "retrieval"}
        if destination == "skill":
            required |= {"format", "links", "token-path"}
        if manifest.get("depth") == "application" or destination in {"career", "interview", "project", "curriculum", "workflow", "content"}:
            required.add("application")
        missing = sorted(required - passed_scopes)
        if missing:
            errors.append(f"missing passed test scopes: {missing}")
        if any(t.get("status") == "failed" for t in tests if isinstance(t, dict)):
            errors.append("failed tests remain unresolved")
    if args.mode == "publish":
        if publication.get("status") not in {"approved", "published"}:
            errors.append("publish mode requires approved or published status")
        if not str(publication.get("authority_ref", "")).strip():
            errors.append("publish mode requires explicit authority_ref")
        if publication.get("visibility") == "public" and rights not in {"open-license", "owner-authorized", "publication-authorized"}:
            errors.append("public publication is not permitted by rights_status")
        if any(a.get("status") not in {"approved", "published"} for a in artifacts if isinstance(a, dict)):
            errors.append("publish mode requires exact approved artifacts")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--root", type=Path, help="Artifact root used to verify paths and hashes")
    parser.add_argument("--mode", choices=("plan", "complete", "publish"), default="plan")
    parser.add_argument("--scan-generated", action="store_true")
    args = parser.parse_args()
    errors = validate(args)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"FAILED: {len(errors)} book-conversion validation error(s)")
        sys.exit(1)
    print("PASS: source, structure, traceability, destination, tests and rights controls are valid")


if __name__ == "__main__":
    main()
