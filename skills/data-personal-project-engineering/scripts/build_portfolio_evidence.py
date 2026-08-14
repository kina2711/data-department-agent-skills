#!/usr/bin/env python3
"""Verify project artifacts and generate a claim-to-evidence portfolio index."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    try:
        manifest: dict[str, Any] = json.loads(args.manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError) as exc:
        print(f"ERROR: invalid manifest: {exc}")
        sys.exit(1)
    root = args.project_root.resolve()
    artifacts: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    if args.strict and not manifest.get("artifacts"):
        errors.append("strict portfolio evidence requires at least one artifact")
    for item in manifest.get("artifacts", []):
        artifact_id = str(item.get("artifact_id", ""))
        raw_path = Path(str(item.get("path", "")))
        path = raw_path.resolve() if raw_path.is_absolute() else (root / raw_path).resolve()
        try:
            path.relative_to(root)
        except ValueError:
            errors.append(f"{artifact_id}: path escapes project root")
            continue
        exists = path.is_file()
        observed_hash = hashlib.sha256(path.read_bytes()).hexdigest() if exists else ""
        expected_hash = str(item.get("sha256", ""))
        verified = exists and bool(expected_hash) and observed_hash.lower() == expected_hash.lower()
        artifacts[artifact_id] = {"path": str(path), "version": item.get("version", ""), "status": item.get("status", ""), "exists": exists, "expected_sha256": expected_hash, "observed_sha256": observed_hash, "verified": verified}
        if args.strict and not verified:
            errors.append(f"{artifact_id}: missing artifact or SHA-256 mismatch")
    validations = {str(v.get("validation_id", "")): v for v in manifest.get("validations", [])}
    claims = []
    if args.strict and not manifest.get("portfolio_claims"):
        errors.append("strict portfolio evidence requires at least one structured claim")
    for claim in manifest.get("portfolio_claims", []):
        if isinstance(claim, str):
            claims.append({"claim": claim, "status": "unstructured", "artifact_refs": [], "validation_refs": []})
            if args.strict:
                errors.append(f"unstructured portfolio claim cannot be verified: {claim[:80]}")
            continue
        artifact_refs = claim.get("artifact_refs", [])
        validation_refs = claim.get("validation_refs", [])
        unresolved_artifacts = [ref for ref in artifact_refs if ref not in artifacts or not artifacts[ref]["verified"]]
        unresolved_validations = [ref for ref in validation_refs if ref not in validations or validations[ref].get("status") != "passed"]
        status = "verified" if artifact_refs and validation_refs and not unresolved_artifacts and not unresolved_validations else "unverified"
        claims.append({**claim, "status": status, "unresolved_artifact_refs": unresolved_artifacts, "unresolved_validation_refs": unresolved_validations})
        if args.strict and status != "verified":
            errors.append(f"claim {claim.get('claim_id', '<missing>')}: unresolved evidence")
    result = {"project_id": manifest.get("project_id", ""), "manifest": str(args.manifest), "artifacts": artifacts, "validations": validations, "claims": claims, "summary": {"artifacts": len(artifacts), "verified_artifacts": sum(x["verified"] for x in artifacts.values()), "claims": len(claims), "verified_claims": sum(x.get("status") == "verified" for x in claims)}, "errors": errors}
    payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
        print(f"WROTE: {args.output}")
    else:
        print(payload, end="")
    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
