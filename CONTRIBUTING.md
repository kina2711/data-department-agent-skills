# Contributing

## The one rule that breaks everything else

`skills/` is **generated**. Never edit a file under `skills/` by hand — the next build
overwrites it and your change disappears without a trace.

Change the source instead:

| To change | Edit |
|---|---|
| A task's goal, deliverable or ownership | [docs/skill-map.md](docs/skill-map.md) — the canonical taxonomy |
| How contracts, catalogs or SKILL.md files are rendered | [tools/build_suite.py](tools/build_suite.py) |
| A slash command for a department | `ROLE_COMMANDS` in `tools/build_suite.py` |
| A hand-written control command | `commands/dd-*.md` (the ones without a generated marker) |
| An evidence script | `skills/<role>/scripts/` — these are hand-written and are **not** regenerated |
| The Vietnamese task catalog | [tools/generate_user_docs.py](tools/generate_user_docs.py) |

## Before opening a pull request

All seven must pass:

```bash
python tools/build_suite.py
python tools/generate_user_docs.py
python tools/validate_suite.py
python tools/validate_claude_skills.py
python tools/run_smoke_tests.py
python tools/run_benchmark_tests.py
python tools/run_control_tests.py
python tools/audit_skills.py
```

Then confirm the build is deterministic — CI runs `git diff --exit-code` after rebuilding,
so an unbuilt change fails:

```bash
python tools/build_suite.py && git diff --exit-code
```

Requirements: Python 3.10+ and PyYAML. Everything else is standard library on purpose —
evidence scripts run on a user's machine and must not need an install step.

## Adding an atomic task

1. Add the line to `docs/skill-map.md` in the existing format:
   `` - `task-id` — goal; output: deliverable. ``
2. The `task-id` prefix decides ownership; see `PREFIX_TO_SKILL` in `tools/build_suite.py`.
3. Rebuild. The contract, catalog entry and routing are generated for you.
4. If the task needs a script, template or adapter, add it to `task_specific_resources()`.
   A contract with no task-specific resource shows up in the audit.
5. Add a routing case to `evaluations/routing-cases.yaml` so the task is reachable from
   natural language, and a confusion-pair case if a sibling role could plausibly claim it.

## Adding an evidence script

Evidence scripts are the part of this suite that cannot bluff, so they are held to a
higher standard than the prose around them.

- **Standard library only.** No third-party imports.
- **Exit codes carry meaning**: `0` passed, `1` failed, `2` incomplete or unknown because a
  check could not run, `3` blocked by policy. `2` is never a pass.
- **A control that cannot fail is not a control.** Add cases to
  `tools/run_control_tests.py` asserting both the pass path and the refusal paths.
- **State the limits in the docstring** — what the script checks, and specifically what it
  cannot confirm. A script that overstates its reach is worse than no script.
- **Never store user content**, prompts, secrets or data values in any artefact a script
  writes.
- Register the script in `tools/validate_suite.py` so it cannot silently disappear.

## Writing style for contracts and commands

Say what is true and what is not verified. `not-run`, `incomplete` and `unknown` are
honest statuses and must never be reported as success. A high failure rate triggers
investigation, never a weaker gate.

## Reporting a problem

Include what you ran, the full output, and which of the eight checks failed. For a routing
complaint, include the exact request text and the task it selected — that is what makes a
confusion-pair case reproducible.
