# Data Department Agent Skills v2 — Operating Guide

The suite is a native Claude Code plugin and also follows the open Agent Skills directory format. Claude discovers only each skill's `name` and `description`, loads `SKILL.md` on activation, then reads atomic task contracts and other resources on demand.

User documentation:

- `installation-and-usage.md` — import, validation, invocation and troubleshooting.
- `capability-overview.md` — complete capability, role, lifecycle, control and template catalog.

## Build and validate

Run from the repository root:

```powershell
python .\tools\build_suite.py
python .\tools\validate_suite.py
python .\tools\validate_claude_skills.py
python .\tools\run_smoke_tests.py
```

`skill-map.md` is the canonical taxonomy. `build_suite.py` regenerates role routers, atomic task contracts, manifests and shared assets from it.

## Install into a Claude Code project

```powershell
.\tools\install_claude_skills.ps1 -Scope Project -ProjectPath C:\path\to\project
```

This copies all top-level skills into `<project>/.claude/skills`. Existing skill directories are not replaced unless `-Force` is supplied.

## Install for the current user

```powershell
.\tools\install_claude_skills.ps1 -Scope User
```

Review globally installed skills before using `-Force` because same-name skill directories will be replaced.

## Use

- Invoke `data-department-orchestrator` for end-to-end, ambiguous or multi-role initiatives.
- Invoke a role skill directly when the primary deliverable and owner are already clear.
- Populate `company-data-context` before expecting company-specific answers.
- Keep tool-specific instructions in adapter references; do not create duplicate business tasks per tool.
- Use run-state and evidence/approval ledgers for multi-session or governed delivery.
- Use `data-academy-and-curriculum`, `data-onboarding-and-integration`, `data-talent-acquisition-and-interview`, and `data-career-and-interview-coach` for the full People OS lifecycle.
- Follow `lifecycle-operating-model.md` for risk-adaptive Plan-Assess-Execute-Test stage gates and optimization metrics.

## Change the taxonomy

1. Add or modify an atomic task in `skill-map.md` using `- \`task-id\` — goal; output: deliverable.`.
2. Map any new prefix in `tools/build_suite.py`.
3. Rebuild and run all validators.
4. Add a routing evaluation for materially new behavior.
5. Forward-test the affected role skill with a fresh Claude session before production use.

## Release

```powershell
.\tools\package_suite.ps1
.\tools\package_claude_plugin.ps1
```

`package_claude_plugin.ps1` creates the clean Claude-native plugin release, excludes cross-client UI metadata, and runs `claude plugin validate --strict` before packaging. Load the staged development plugin with `claude --plugin-dir <staged-plugin-path>` or distribute its ZIP through a Claude Code plugin marketplace.
