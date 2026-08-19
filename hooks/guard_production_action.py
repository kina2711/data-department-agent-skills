#!/usr/bin/env python3
"""Escalate production, publishing and destructive shell actions to an explicit human decision.

Read a Claude Code PreToolUse payload on stdin and emit a permission decision on stdout.
The guard never denies on its own: the suite requires evidence and named authority before a
gated action, and only a human can supply that. Anything unrecognized is left to the normal
permission flow, so a parsing or environment failure can never silently widen access.
"""

from __future__ import annotations

import json
import re
import sys

# (label, pattern) pairs. Patterns are matched case-insensitively against the full command.
GATED_PATTERNS: list[tuple[str, str]] = [
    ("git history rewrite or force push", r"\bgit\s+push\b[^\n]*(--force\b|--force-with-lease\b|-f\b)"),
    ("git push to a remote", r"\bgit\s+push\b"),
    ("git branch or tag deletion on a remote", r"\bgit\s+push\b[^\n]*--delete\b"),
    ("infrastructure apply or destroy", r"\b(terraform|tofu)\s+(apply|destroy)\b|\bpulumi\s+(up|destroy)\b"),
    ("Kubernetes cluster mutation", r"\bkubectl\s+(apply|delete|replace|scale|rollout)\b|\bhelm\s+(install|upgrade|uninstall|rollback)\b"),
    ("cloud resource mutation", r"\baws\s+\w+\s+(rm|delete|put|create|update)\b|\bgcloud\s+[\w-]+\s+(delete|create|update|deploy)\b|\baz\s+[\w-]+\s+(delete|create|update)\b"),
    ("object storage deletion or overwrite", r"\baws\s+s3\s+(rm|sync|mv)\b|\bgsutil\s+(rm|mv|rsync)\b"),
    ("warehouse object drop or truncate", r"\b(drop|truncate)\s+(table|schema|database|view|dataset)\b"),
    ("unfiltered delete statement", r"\bdelete\s+from\b(?![^\n]*\bwhere\b)"),
    ("BigQuery resource removal", r"\bbq\s+(rm|mk\s+--force)\b"),
    ("dbt run against a production target", r"\bdbt\s+(run|build|seed|snapshot|run-operation)\b[^\n]*--target[= ]\s*(prod|production)\b"),
    ("orchestrator backfill or trigger", r"\bairflow\s+(dags\s+)?(trigger|backfill)\b|\bdagster\s+job\s+launch\b|\bprefect\s+deployment\s+run\b"),
    ("package or release publication", r"\bnpm\s+publish\b|\btwine\s+upload\b|\bgh\s+release\s+create\b|\bpoetry\s+publish\b|\bdocker\s+push\b"),
    ("recursive filesystem deletion", r"\brm\s+(-\w*r\w*f|-\w*f\w*r)\b"),
]

MUTATING_TOOLS = {"Bash", "PowerShell"}


def emit(decision: str, reason: str) -> None:
    payload = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decision,
            "permissionDecisionReason": reason,
        }
    }
    json.dump(payload, sys.stdout)
    sys.stdout.write("\n")


def match_gates(command: str) -> list[str]:
    return [label for label, pattern in GATED_PATTERNS if re.search(pattern, command, re.IGNORECASE)]


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0
    if not isinstance(payload, dict):
        return 0
    if payload.get("tool_name") not in MUTATING_TOOLS:
        return 0
    tool_input = payload.get("tool_input")
    command = str(tool_input.get("command", "")) if isinstance(tool_input, dict) else ""
    if not command.strip():
        return 0

    gates = match_gates(command)
    if not gates:
        return 0

    labels = "; ".join(dict.fromkeys(gates))
    emit(
        "ask",
        "Data Department gate: this command performs "
        f"{labels}. The suite requires a named approver, a version- and scope-bound approval record "
        "and fresh evidence before a production, publishing or destructive action. "
        "Confirm the approval exists, or run the read-only equivalent first.",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
