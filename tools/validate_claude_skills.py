#!/usr/bin/env python3
"""Validate Claude Code/Agent Skills discovery, progressive disclosure and plugin purity."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
COMMANDS = ROOT / "commands"
HOOKS = ROOT / "hooks"
PLUGIN = ROOT / ".claude-plugin" / "plugin.json"
ANTIGRAVITY = ROOT / ".agents" / "agents"
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
TASK_LINK_RE = re.compile(r"\(tasks/([a-z0-9-]+)\.md\)")
COMMAND_FIELDS = {
    "name", "description", "argument-hint", "disable-model-invocation",
    "allowed-tools", "model", "context", "agent",
}
HOOK_EVENTS = {
    "PreToolUse", "PostToolUse", "PostToolUseFailure", "PermissionRequest", "PermissionDenied",
    "PostToolBatch", "SessionStart", "SessionEnd", "Setup", "UserPromptSubmit",
    "Stop", "StopFailure", "SubagentStop", "Notification", "PreCompact", "PostCompact",
}


def validate_commands(errors: list[str]) -> int:
    """Commands are user entry points; a broken one is invisible until someone types it."""
    if not COMMANDS.is_dir():
        errors.append(f"{COMMANDS}: missing commands directory")
        return 0
    stray = sorted(path for path in COMMANDS.iterdir() if path.is_dir())
    for path in stray:
        errors.append(f"{path}: commands must be flat .md files, not subdirectories")
    files = sorted(COMMANDS.glob("*.md"))
    if not files:
        errors.append(f"{COMMANDS}: no command files found")
    for path in files:
        text = path.read_text(encoding="utf-8")
        match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
        if not match:
            errors.append(f"{path}: missing YAML frontmatter")
            continue
        try:
            metadata = yaml.safe_load(match.group(1))
        except yaml.YAMLError as exc:
            errors.append(f"{path}: invalid YAML: {exc}")
            continue
        if not isinstance(metadata, dict):
            errors.append(f"{path}: frontmatter must be a mapping")
            continue
        unknown = sorted(set(metadata) - COMMAND_FIELDS)
        if unknown:
            errors.append(f"{path}: unsupported command frontmatter fields {unknown}")
        name = metadata.get("name")
        if name != path.stem or not isinstance(name, str) or not NAME_RE.fullmatch(str(name)):
            errors.append(f"{path}: invalid or mismatched name {name!r}")
        description = metadata.get("description")
        if not isinstance(description, str) or not description.strip() or len(description) > 1024:
            errors.append(f"{path}: description must contain 1-1024 characters")
        body = text[match.end():]
        if not body.strip():
            errors.append(f"{path}: command body is empty")
    return len(files)


def validate_hooks(errors: list[str]) -> int:
    """A hook that cannot start silently stops enforcing anything, so check the wiring."""
    config = HOOKS / "hooks.json"
    if not config.exists():
        errors.append(f"{config}: missing hooks configuration")
        return 0
    try:
        data = json.loads(config.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{config}: invalid JSON: {exc}")
        return 0
    events = data.get("hooks")
    if not isinstance(events, dict) or not events:
        errors.append(f"{config}: hooks must be a non-empty object of event names")
        return 0
    count = 0
    for event, entries in events.items():
        if event not in HOOK_EVENTS:
            errors.append(f"{config}: unknown hook event {event!r}")
        if not isinstance(entries, list):
            errors.append(f"{config}: event {event!r} must map to an array")
            continue
        for entry in entries:
            for hook in entry.get("hooks", []) if isinstance(entry, dict) else []:
                count += 1
                if not isinstance(hook, dict) or hook.get("type") != "command":
                    errors.append(f"{config}: event {event!r} supports only bundled command hooks")
                    continue
                for argument in hook.get("args", []):
                    if "${CLAUDE_PLUGIN_ROOT}" not in str(argument):
                        continue
                    relative = str(argument).split("${CLAUDE_PLUGIN_ROOT}/", 1)[-1]
                    if not (ROOT / relative).exists():
                        errors.append(f"{config}: hook script does not exist: {relative}")
    if count == 0:
        errors.append(f"{config}: no hook handlers declared")
    return count



ANTIGRAVITY_FIELDS = {
    "name", "description", "tools", "mainAgent", "subagent", "model",
    "commandExecutionPolicy", "mcpServers", "skills", "plugins",
}
ANTIGRAVITY_MODELS = {"inherit", "flash", "pro"}
ANTIGRAVITY_POLICIES = {"off", "auto", "eager", "sandbox"}


def validate_antigravity_agents(errors: list[str]) -> int:
    """A department that points at a missing skill loads as an empty agent, silently."""
    if not ANTIGRAVITY.is_dir():
        errors.append(f"{ANTIGRAVITY}: missing Antigravity agent directory")
        return 0
    files = sorted(ANTIGRAVITY.glob("*.md"))
    if not files:
        errors.append(f"{ANTIGRAVITY}: no agent definitions found")
    for path in files:
        text = path.read_text(encoding="utf-8")
        match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
        if not match:
            errors.append(f"{path}: missing YAML frontmatter")
            continue
        try:
            metadata = yaml.safe_load(match.group(1))
        except yaml.YAMLError as exc:
            errors.append(f"{path}: invalid YAML: {exc}")
            continue
        if not isinstance(metadata, dict):
            errors.append(f"{path}: frontmatter must be a mapping")
            continue
        unknown = sorted(set(metadata) - ANTIGRAVITY_FIELDS)
        if unknown:
            errors.append(f"{path}: unsupported Antigravity fields {unknown}")
        if metadata.get("name") != path.stem:
            errors.append(f"{path}: name {metadata.get('name')!r} does not match the filename")
        description = metadata.get("description")
        if not isinstance(description, str) or not description.strip():
            errors.append(f"{path}: description is required for planner delegation")
        if metadata.get("model") not in ANTIGRAVITY_MODELS:
            errors.append(f"{path}: model must be one of {sorted(ANTIGRAVITY_MODELS)}")
        if metadata.get("commandExecutionPolicy") not in ANTIGRAVITY_POLICIES:
            errors.append(f"{path}: commandExecutionPolicy must be one of {sorted(ANTIGRAVITY_POLICIES)}")
        for reference in metadata.get("skills", []) or []:
            if not (ROOT / str(reference)).is_dir():
                errors.append(f"{path}: skills entry does not exist: {reference}")
    return len(files)


def validate_plugin_manifest(errors: list[str]) -> None:
    """Every path the manifest declares must exist, or the plugin loads a subset of itself."""
    if not PLUGIN.exists():
        errors.append(f"{PLUGIN}: missing plugin manifest")
        return
    try:
        manifest = json.loads(PLUGIN.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{PLUGIN}: invalid JSON: {exc}")
        return
    for field in ("name", "version", "description"):
        if not str(manifest.get(field, "")).strip():
            errors.append(f"{PLUGIN}: missing {field}")
    declared: list[str] = []
    for field in ("commands", "agents", "hooks", "skills"):
        value = manifest.get(field)
        if isinstance(value, str):
            declared.append(value)
        elif isinstance(value, list):
            declared.extend(str(item) for item in value)
    for entry in declared:
        if not entry.startswith("./"):
            errors.append(f"{PLUGIN}: declared path must start with './': {entry}")
        elif not (ROOT / entry[2:]).exists():
            errors.append(f"{PLUGIN}: declared path does not exist: {entry}")


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

    command_count = validate_commands(errors)
    hook_count = validate_hooks(errors)
    validate_plugin_manifest(errors)
    antigravity_agents = validate_antigravity_agents(errors)

    print(f"claude_skills: {len(skill_dirs)}")
    print(f"atomic_tasks: {total_tasks}")
    print(f"slash_commands: {command_count}")
    print(f"hook_handlers: {hook_count}")
    print(f"antigravity_agents: {antigravity_agents}")
    print(f"errors: {len(errors)}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        sys.exit(1)
    print("Claude skill validation passed")


if __name__ == "__main__":
    main()
