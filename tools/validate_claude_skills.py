#!/usr/bin/env python3
"""Validate Claude Code/Agent Skills discovery, progressive disclosure and plugin purity."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
TASK_LINK_RE = re.compile(r"\(tasks/([a-z0-9-]+)\.md\)")


def main() -> None:
    errors: list[str] = []
    skill_dirs = sorted(path for path in SKILLS.iterdir() if path.is_dir())
    total_tasks = 0

    for skill_dir in skill_dirs:
        entry = skill_dir / "SKILL.md"
        if not entry.exists():
            errors.append(f"{skill_dir}: missing SKILL.md")
            continue
        text = entry.read_text(encoding="utf-8")
        match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
        if not match:
            errors.append(f"{entry}: missing YAML frontmatter")
            continue
        try:
            metadata = yaml.safe_load(match.group(1))
        except yaml.YAMLError as exc:
            errors.append(f"{entry}: invalid YAML: {exc}")
            continue
        if not isinstance(metadata, dict):
            errors.append(f"{entry}: frontmatter must be a mapping")
            continue
        name = metadata.get("name")
        description = metadata.get("description")
        allowed_fields = {
            "name", "description", "when_to_use", "disable-model-invocation",
            "user-invocable", "allowed-tools", "context", "agent", "argument-hint",
            "model", "hooks", "license", "compatibility", "metadata",
        }
        unknown = sorted(set(metadata) - allowed_fields)
        if unknown:
            errors.append(f"{entry}: unsupported Claude frontmatter fields {unknown}")
        if name != skill_dir.name or not isinstance(name, str) or not NAME_RE.fullmatch(name):
            errors.append(f"{entry}: invalid or mismatched name {name!r}")
        if not isinstance(description, str) or not description.strip() or len(description) > 1024:
            errors.append(f"{entry}: description must contain 1-1024 characters")
        if not re.search(r"(?:^|\s)use(?:\s|$)", str(description), re.IGNORECASE):
            errors.append(f"{entry}: description does not explain when to use the skill")
        if len(text.splitlines()) >= 500:
            errors.append(f"{entry}: must stay below 500 lines")

        task_dir = skill_dir / "references" / "tasks"
        tasks = sorted(task_dir.glob("*.md")) if task_dir.exists() else []
        catalog_files = sorted((skill_dir / "references").glob("catalog-*.md"))
        catalog_links = set(re.findall(r"\(references/(catalog-[a-z0-9-]+\.md)\)", text))
        if catalog_links != {path.name for path in catalog_files}:
            errors.append(f"{entry}: generated catalog links are incomplete")
        links = [
            task_id
            for catalog_file in catalog_files
            for task_id in TASK_LINK_RE.findall(catalog_file.read_text(encoding="utf-8"))
        ]
        if len(links) != len(set(links)):
            errors.append(f"{entry}: an atomic task appears in multiple catalogs")
        total_tasks += len(tasks)
        if {path.stem for path in tasks} != set(links):
            errors.append(f"{entry}: atomic task links do not exactly match task files")

        for path in skill_dir.rglob("*"):
            if path.is_file() and path.name.lower() in {
                "readme.md", "installation_guide.md", "quick_reference.md", "changelog.md"
            }:
                errors.append(f"{path}: extraneous skill documentation")

    print(f"claude_skills: {len(skill_dirs)}")
    print(f"atomic_tasks: {total_tasks}")
    print(f"errors: {len(errors)}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        sys.exit(1)
    print("Claude skill validation passed")


if __name__ == "__main__":
    main()
