---
name: company-data-context
description: Maintain and index company-specific data context including glossary terms, metrics, datasets, systems, owners, policies and platforms. Use when Claude must initialize, route, retrieve or verify organizational context without storing secrets.
---

# Company Data Context

## Operating contract

1. Identify the requested deliverable, then select exactly one atomic task below.
2. Read that task file completely before acting.
3. Read [references/lifecycle-standard.md](references/lifecycle-standard.md) and use the task's profile, risk tier and execution path.
4. Load only the company context and adapter references needed for the selected task.
5. On a cross-role handoff, compare logical ID and SHA-256 in `references/shared-reference-manifest.json`; reuse an already loaded shared reference when both match instead of loading its duplicate.
6. Inspect real artifacts and systems before making change-sensitive claims.
7. Apply Definition of Ready, stage gates, test strategy, Definition of Done, approval and handoff requirements.
8. Do not invent access, approvals, successful execution, test results or business confirmation.
9. For any Git-backed mutation, regardless of the task's verb or profile, require a pre-change success/scope contract, a post-change `core-audit-change-scope`, and fresh `core-verify-deliverable` evidence before completion.

## Context policy

Initialize a project context from the templates in `assets/company-context/`. Never store secrets or raw sensitive records. Every entry needs owner, provenance, effective date, last verified date and status. Live inspection overrides stale reference content.

## Context routing

- Persistent source inventory, authority, owner, routing trigger and freshness -> `ctx-build-context-index`.
- Prompt-ready context bundle for exactly one task and token budget -> hand off to `core-build-task-context-package` in Shared Data Core.

Use `scripts/bootstrap_context_index.py` to inventory local context without copying content values. Its authority and owner classifications remain hypotheses until accountable confirmation.


## Stack-native adapter routing

After selecting the task, detect the real stack/version and read only the matching adapter below plus [the adapter index](references/technology-adapters.md). Do not load every adapter.

- [snowflake](references/adapter-snowflake.md)
- [bigquery](references/adapter-bigquery.md)
- [databricks](references/adapter-databricks.md)
- [microsoft-fabric](references/adapter-microsoft-fabric.md)
- [metadata-catalog](references/adapter-metadata-catalog.md)

## Atomic task routing

- **Plan, define, design, map, specify or create a proposed artifact** (1 task): read [references/catalog-plan-design.md](references/catalog-plan-design.md).
- **Build, implement, configure, teach, interview or deliver an artifact** (7 tasks): read [references/catalog-build-deliver.md](references/catalog-build-deliver.md).
- **Inspect, analyze, test, review, validate, assess, certify or audit** (1 task): read [references/catalog-test-assure.md](references/catalog-test-assure.md).

Read only the best-matching catalog. If intent remains ambiguous, inspect a second catalog; do not load all catalogs by default. Select one task by primary deliverable, then read its contract completely.

## Completion response

State the selected task ID, primary deliverable, evidence inspected, validation performed, approval status, residual risks and next owner. A draft or plan is not an executed production outcome.
