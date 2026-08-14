#!/usr/bin/env python3
"""Produce a deterministic, read-only evidence inventory for repo-first assessment."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

EXCLUDED = {".git", ".venv", "venv", "node_modules", "dist", "build", ".tox", ".mypy_cache", ".pytest_cache", "__pycache__"}
TEXT_EXTENSIONS = {".py", ".sql", ".md", ".yml", ".yaml", ".json", ".toml", ".ini", ".cfg", ".sh", ".ps1", ".js", ".ts", ".java", ".scala", ".go", ".rs", ".xml", ".txt"}
LANGUAGES = {".py": "Python", ".sql": "SQL", ".scala": "Scala", ".java": "Java", ".js": "JavaScript", ".ts": "TypeScript", ".go": "Go", ".rs": "Rust", ".r": "R", ".ipynb": "Notebook"}
SECRET_NAME = re.compile(r"(?i)(secret|token|password|passwd|credential|private[_-]?key|api[_-]?key)")


def git(root: Path, *args: str) -> str:
    try:
        proc = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, timeout=10, check=False)
        return proc.stdout.strip() if proc.returncode == 0 else ""
    except (OSError, subprocess.TimeoutExpired):
        return ""


def files(root: Path) -> list[Path]:
    result: list[Path] = []
    for current, dirs, names in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in EXCLUDED)
        base = Path(current)
        for name in sorted(names):
            path = base / name
            if path.is_file():
                result.append(path)
    return result


def rel(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def find_matches(paths: list[Path], root: Path, patterns: tuple[str, ...]) -> list[str]:
    return sorted(rel(root, p) for p in paths if any(Path(rel(root, p)).match(pattern) for pattern in patterns))


def snapshot(paths: list[Path], root: Path) -> tuple[str, list[str]]:
    aggregate = hashlib.sha256()
    skipped: list[str] = []
    for path in paths:
        relative = rel(root, path)
        try:
            size = path.stat().st_size
            if size > 10 * 1024 * 1024:
                skipped.append(relative)
                continue
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            aggregate.update(relative.encode("utf-8"))
            aggregate.update(str(size).encode("ascii"))
            aggregate.update(digest.encode("ascii"))
        except OSError:
            skipped.append(relative)
    return aggregate.hexdigest(), skipped


def build(root: Path) -> dict[str, Any]:
    paths = files(root)
    relative = [rel(root, p) for p in paths]
    languages = Counter(LANGUAGES[p.suffix.lower()] for p in paths if p.suffix.lower() in LANGUAGES)
    manifest_patterns = ("pyproject.toml", "requirements*.txt", "poetry.lock", "uv.lock", "package*.json", "pom.xml", "build.gradle*", "go.mod", "Cargo.toml", "packages.yml", "dbt_project.yml")
    license_files = find_matches(paths, root, ("LICENSE*", "COPYING*", "NOTICE*"))
    manifests = find_matches(paths, root, manifest_patterns)
    tests = sorted(x for x in relative if re.search(r"(^|/)(tests?|spec)(/|$)|(^|/)test_[^/]+|[^/]+_test\.", x, re.I))
    workflows = sorted(x for x in relative if x.startswith(".github/workflows/") or x in {".gitlab-ci.yml", "Jenkinsfile", "azure-pipelines.yml"})
    containers = find_matches(paths, root, ("Dockerfile*", "docker-compose*.yml", "docker-compose*.yaml", "compose*.yml", "compose*.yaml", "devcontainer.json", ".devcontainer/*"))
    docs = sorted(x for x in relative if x.lower().endswith(".md") or x.startswith("docs/"))
    data_contracts = sorted(x for x in relative if re.search(r"(schema|contract|sources|models|expectation|quality).*(ya?ml|json|sql)$", x, re.I))
    observability = sorted(x for x in relative if re.search(r"(monitor|alert|metric|logging|runbook|incident|slo|sla)", x, re.I))
    infra = sorted(x for x in relative if x.endswith((".tf", ".tfvars")) or x.startswith(("infra/", "terraform/", "k8s/", "helm/")))
    suspicious_names = sorted(x for x in relative if SECRET_NAME.search(Path(x).name) and not re.search(r"example|sample|template|test", x, re.I))
    digest, skipped = snapshot(paths, root)
    status = git(root, "status", "--porcelain=v1")
    remote = git(root, "remote", "get-url", "origin")
    head = git(root, "rev-parse", "HEAD")
    branch = git(root, "branch", "--show-current")
    tags = git(root, "tag", "--points-at", "HEAD").splitlines() if head else []
    last_commit = git(root, "log", "-1", "--format=%cI")

    dimensions = {
        "purpose-and-users": {"evidence": [x for x in relative if x.lower() in {"readme.md", "docs/index.md", "docs/architecture.md"}], "state": "observed" if docs else "unknown"},
        "architecture-and-data-flow": {"evidence": sorted(x for x in relative if re.search(r"architecture|lineage|data[_-]?flow|erd|diagram", x, re.I)), "state": "inventory-only"},
        "runtime-and-reproducibility": {"evidence": manifests + containers, "state": "inventory-only"},
        "data-contracts-and-modeling": {"evidence": data_contracts, "state": "inventory-only"},
        "correctness-and-tests": {"evidence": tests, "state": "inventory-only"},
        "security-secrets-dependencies": {"evidence": manifests, "suspicious_filenames": suspicious_names, "state": "inventory-only"},
        "ci-cd-and-supply-chain": {"evidence": workflows + containers + infra, "state": "inventory-only"},
        "observability-and-reliability": {"evidence": observability, "state": "inventory-only"},
        "performance-and-cost": {"evidence": sorted(x for x in relative if re.search(r"benchmark|performance|load[_-]?test|cost", x, re.I)), "state": "inventory-only"},
        "documentation-and-developer-experience": {"evidence": docs + containers, "state": "inventory-only"},
        "maintainability-and-activity": {"evidence": workflows + manifests, "git_last_commit": last_commit, "state": "inventory-only"},
        "license-and-provenance": {"evidence": license_files, "origin": remote, "commit": head, "state": "observed" if license_files and head else "partial"},
    }
    return {
        "report_type": "read-only-repository-evidence-inventory",
        "root": str(root),
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "git": {"origin": remote, "head": head, "branch": branch, "tags_at_head": tags, "dirty_entries": len(status.splitlines()) if status else 0},
        "snapshot_sha256": digest,
        "snapshot_skipped_files": skipped,
        "inventory": {"files": len(paths), "languages": dict(languages), "licenses": license_files, "manifests": manifests, "tests": tests, "workflows": workflows, "containers": containers, "infrastructure": infra},
        "dimensions": dimensions,
        "limitations": ["No repository code, tests, containers or hooks were executed.", "File presence is evidence for inspection, not proof of correctness or operating effectiveness.", "Suspicious filenames are heuristic findings; file contents and secret validity were not exposed."],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.repository.resolve()
    if not root.is_dir():
        print(f"ERROR: repository directory does not exist: {root}")
        sys.exit(1)
    report = build(root)
    payload = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
        print(f"WROTE: {args.output}")
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
