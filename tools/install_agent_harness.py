#!/usr/bin/env python3
"""Install this suite into a target project for Codex, Antigravity or Claude Code.

The three harnesses read different paths but the same content. Claude Code loads the plugin
directly; Codex discovers skills at `.codex/skills/<name>/SKILL.md`, which is the same
`name` + `description` frontmatter this suite already uses; Antigravity reads `AGENTS.md`
plus custom agents at `.agents/agents/<name>.md`.

Nothing is duplicated where a link will do. Symlinks keep one source of truth, so a rebuild of
the suite updates every installed harness at once. Where symlinks are unavailable — Windows
without Developer Mode, or a filesystem that cannot make them — the installer falls back to
copying and says so, because a silent copy that later goes stale is worse than a loud one.

It refuses to overwrite anything it did not create, and `--dry-run` shows every action first.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

SUITE_ROOT = Path(__file__).resolve().parents[1]
MARKER_NAME = ".data-department-install.json"
HARNESSES = ("codex", "antigravity", "claude")


class Planner:
    """Collects actions so --dry-run and the real run cannot diverge."""

    def __init__(self, dry_run: bool) -> None:
        self.dry_run = dry_run
        self.actions: list[str] = []
        self.copied_instead_of_linked = 0

    def record(self, message: str) -> None:
        self.actions.append(message)
        print(("would " if self.dry_run else "") + message)

    def link_or_copy(self, source: Path, target: Path, prefer_copy: bool) -> None:
        relation = "copy" if prefer_copy else "link"
        self.record(f"{relation} {target} -> {source}")
        if self.dry_run:
            return
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.is_symlink() or target.exists():
            remove(target)
        if not prefer_copy:
            try:
                target.symlink_to(source, target_is_directory=source.is_dir())
                return
            except (OSError, NotImplementedError):
                self.copied_instead_of_linked += 1
                print(f"  symlink unavailable, copying instead: {target}")
        if source.is_dir():
            shutil.copytree(source, target)
        else:
            shutil.copy2(source, target)


def remove(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def read_marker(root: Path) -> dict:
    marker = root / MARKER_NAME
    if not marker.exists():
        return {}
    try:
        return json.loads(marker.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def owned_by_us(root: Path, target: Path) -> bool:
    installed = set(read_marker(root).get("installed", []))
    try:
        return target.relative_to(root).as_posix() in installed
    except ValueError:
        return False


def guard_existing(root: Path, target: Path, force: bool) -> bool:
    """Return True when it is safe to write. Never clobber a path we did not create."""
    if not (target.exists() or target.is_symlink()):
        return True
    if owned_by_us(root, target) or force:
        return True
    print(f"REFUSED: {target} already exists and was not created by this installer")
    print("         move it aside, or re-run with --force to replace it")
    return False


def skill_names() -> list[str]:
    return sorted(
        path.name for path in (SUITE_ROOT / "skills").iterdir()
        if path.is_dir() and (path / "SKILL.md").exists()
    )


def install_codex(root: Path, planner: Planner, prefer_copy: bool, force: bool) -> list[str]:
    """Codex reads .codex/skills/<name>/SKILL.md and AGENTS.md from the project root."""
    written: list[str] = []
    for name in skill_names():
        target = root / ".codex" / "skills" / name
        if not guard_existing(root, target, force):
            continue
        planner.link_or_copy(SUITE_ROOT / "skills" / name, target, prefer_copy)
        written.append(target.relative_to(root).as_posix())

    agents = root / "AGENTS.md"
    if guard_existing(root, agents, force):
        planner.link_or_copy(SUITE_ROOT / "AGENTS.md", agents, prefer_copy)
        written.append("AGENTS.md")
    return written


def install_antigravity(root: Path, planner: Planner, prefer_copy: bool, force: bool) -> list[str]:
    """Antigravity reads AGENTS.md plus custom agents at .agents/agents/<name>.md."""
    written: list[str] = []
    target = root / ".agents" / "agents"
    if guard_existing(root, target, force):
        planner.link_or_copy(SUITE_ROOT / ".agents" / "agents", target, prefer_copy)
        written.append(".agents/agents")

    skills_target = root / ".agents" / "skills"
    if guard_existing(root, skills_target, force):
        planner.link_or_copy(SUITE_ROOT / "skills", skills_target, prefer_copy)
        written.append(".agents/skills")

    agents = root / "AGENTS.md"
    if guard_existing(root, agents, force):
        planner.link_or_copy(SUITE_ROOT / "AGENTS.md", agents, prefer_copy)
        written.append("AGENTS.md")
    return written


def install_claude(root: Path, planner: Planner, prefer_copy: bool, force: bool) -> list[str]:
    """Claude Code loads the plugin directly; this only wires project-scope skills."""
    written: list[str] = []
    target = root / ".claude" / "skills"
    if guard_existing(root, target, force):
        planner.link_or_copy(SUITE_ROOT / "skills", target, prefer_copy)
        written.append(".claude/skills")
    print()
    print("For the full Claude Code surface (45 slash commands and the production guard hook)")
    print(f'load the plugin instead:  claude --plugin-dir "{SUITE_ROOT}"')
    return written


def uninstall(root: Path, planner: Planner) -> None:
    marker = read_marker(root)
    installed = marker.get("installed", [])
    if not installed:
        print(f"nothing to uninstall: no {MARKER_NAME} in {root}")
        return
    for relative in installed:
        target = root / relative
        if target.exists() or target.is_symlink():
            planner.record(f"remove {target}")
            if not planner.dry_run:
                remove(target)
    if not planner.dry_run:
        (root / MARKER_NAME).unlink(missing_ok=True)
        for directory in (".codex/skills", ".codex", ".agents"):
            path = root / directory
            if path.is_dir() and not any(path.iterdir()):
                path.rmdir()
    print(f"uninstalled {len(installed)} path(s)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("target", type=Path, nargs="?", default=Path.cwd(),
                        help="project to install into (default: current directory)")
    parser.add_argument("--harness", choices=(*HARNESSES, "all"), default="all")
    parser.add_argument("--copy", action="store_true",
                        help="copy instead of linking; the copy will not track suite updates")
    parser.add_argument("--force", action="store_true", help="replace paths this installer did not create")
    parser.add_argument("--dry-run", action="store_true", help="show every action without making changes")
    parser.add_argument("--uninstall", action="store_true", help="remove what this installer created")
    args = parser.parse_args()

    root = args.target.resolve()
    if not root.is_dir():
        print(f"ERROR: not a directory: {root}")
        sys.exit(1)
    if root == SUITE_ROOT:
        print("ERROR: refusing to install the suite into itself")
        sys.exit(1)

    planner = Planner(args.dry_run)
    if args.uninstall:
        uninstall(root, planner)
        return

    selected = HARNESSES if args.harness == "all" else (args.harness,)
    installers = {"codex": install_codex, "antigravity": install_antigravity, "claude": install_claude}

    written: list[str] = []
    for harness in selected:
        print(f"--- {harness} ---")
        written.extend(installers[harness](root, planner, args.copy, args.force))
        print()

    if not written:
        print("nothing installed; every target already existed and was not ours")
        sys.exit(1)

    if not args.dry_run:
        marker = root / MARKER_NAME
        previous = set(read_marker(root).get("installed", []))
        payload = {
            "suite_root": SUITE_ROOT.as_posix(),
            "harnesses": list(selected),
            "mode": "copy" if args.copy else "link",
            "installed": sorted(previous | set(written)),
        }
        marker.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"install record: {marker}")

    print(f"{'planned' if args.dry_run else 'installed'}: {len(written)} path(s) for {', '.join(selected)}")
    if planner.copied_instead_of_linked:
        print(
            f"WARNING: {planner.copied_instead_of_linked} path(s) were copied because symlinks were "
            "unavailable. They will NOT pick up suite updates; re-run this installer after a rebuild."
        )
    if args.copy:
        print("NOTE: --copy was requested. Re-run this installer after every suite rebuild.")


if __name__ == "__main__":
    main()
