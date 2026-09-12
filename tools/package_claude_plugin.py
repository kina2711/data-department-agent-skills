#!/usr/bin/env python3
"""Stage and zip the Claude plugin release.

A port of `package_claude_plugin.ps1`, which needs PowerShell and therefore cannot run on the
machine this suite is developed on. Same staging rules, same strict validation gate, same four
archive entries -- so the two produce interchangeable archives and neither is the odd one out.

Two things it does that the PowerShell version does not. The version comes from
`.claude-plugin/plugin.json` rather than a literal in the default argument, because that literal
sat at an old version for four releases and nobody noticed until an archive was named after a
version it did not contain. And every path it deletes is checked to be inside the staging
directory first, which the original also does; that check is not decoration, since the staging
root is built from user-supplied paths.

Only `plugin.json` is staged from `.claude-plugin/`. Copying `marketplace.json` alongside it makes
Claude Code validate the archive as a marketplace rather than as a plugin.

Standard library only.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
COMPONENTS = ("commands", "hooks")
SKILL_RESOURCES = ("references", "assets", "scripts")
ARCHIVE_ENTRIES = (".claude-plugin", "skills", "commands", "hooks")


def plugin_version() -> str:
    data = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    version = str(data.get("version", "")).strip()
    if not version:
        raise SystemExit(".claude-plugin/plugin.json has no version")
    return version


def inside(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
    except ValueError:
        return False
    return True


def purge_caches(stage: Path) -> None:
    """Drop __pycache__ and .pyc, refusing anything that resolves outside the staging root."""
    for cache in sorted(stage.rglob("__pycache__")):
        if not inside(cache, stage):
            raise SystemExit(f"refusing to remove a cache outside the staged plugin: {cache}")
        shutil.rmtree(cache)
    for compiled in sorted(stage.rglob("*.pyc")):
        if not inside(compiled, stage):
            raise SystemExit(f"refusing to remove a file outside the staged plugin: {compiled}")
        compiled.unlink()


def stage_plugin(stage: Path) -> None:
    if stage.exists():
        shutil.rmtree(stage)
    stage.mkdir(parents=True)

    target = stage / ".claude-plugin"
    target.mkdir()
    shutil.copy2(ROOT / ".claude-plugin" / "plugin.json", target / "plugin.json")

    for component in COMPONENTS:
        source = ROOT / component
        if not source.is_dir():
            raise SystemExit(f"plugin component directory is missing: {source}")
        shutil.copytree(source, stage / component)

    skills_target = stage / "skills"
    skills_target.mkdir()
    # The routing index is a file, not a skill directory, so the per-skill loop below skips it.
    # It travels with the plugin because it is the cheapest way in for a harness that does not
    # preload descriptions.
    index = ROOT / "skills" / "llms.txt"
    if index.is_file():
        shutil.copy2(index, skills_target / "llms.txt")
    for skill in sorted(p for p in (ROOT / "skills").iterdir() if p.is_dir()):
        out = skills_target / skill.name
        out.mkdir()
        shutil.copy2(skill / "SKILL.md", out / "SKILL.md")
        for resource in SKILL_RESOURCES:
            source = skill / resource
            if source.is_dir():
                shutil.copytree(source, out / resource)

    purge_caches(stage)


def validate(stage: Path) -> None:
    """The release is validated by Claude Code itself, not by this script's opinion of it."""
    claude = shutil.which("claude")
    if claude is None:
        raise SystemExit("the Claude Code CLI is required to validate the plugin release")
    result = subprocess.run([claude, "plugin", "validate", "--strict", str(stage)], check=False)
    if result.returncode != 0:
        raise SystemExit("Claude Code strict plugin validation failed")


def write_archive(stage: Path, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.unlink(missing_ok=True)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for entry in ARCHIVE_ENTRIES:
            base = stage / entry
            for path in sorted(base.rglob("*")):
                if path.is_file():
                    archive.write(path, path.relative_to(stage))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--output", type=Path, help="archive path; defaults to dist/ named after the plugin version")
    args = ap.parse_args()

    version = plugin_version()
    output = (args.output or DIST / f"data-department-claude-plugin-v{version}.zip").resolve()
    if not inside(output.parent, DIST) and output.parent != DIST:
        raise SystemExit(f"the plugin release must stay inside dist: {output}")

    stage = DIST / "claude-plugin" / "data-department-agent-skills"
    stage_plugin(stage)
    validate(stage)
    write_archive(stage, output)

    size = output.stat().st_size
    print(f"wrote {output.relative_to(ROOT)}  ({size / 1048576:.1f} MB)  plugin v{version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
