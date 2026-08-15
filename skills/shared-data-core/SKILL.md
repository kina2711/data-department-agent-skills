---
name: shared-data-core
description: Apply shared data controls for bounded task-context packaging, discovery, schema inspection, profiling, validation, evidence, approvals and handoffs. Use when a data task needs reusable cross-role safeguards, a prompt-ready context bundle or artifact checks.
---

# Shared Data Core

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
10. For learning, coaching or skill-transition work, resolve [the learner-memory interoperability contract](references/learning-memory-interoperability.md). Reuse only relevant verified summaries; never infer mastery from exposure, and expand stale, uncertain, changed-version or safety-critical prerequisites.

## Context-package routing

- A bounded bundle for one concrete task, with selected files, provenance, hashes, freshness and token budget -> `core-build-task-context-package`.
- A durable catalog of company context sources, authority, owners, retrieval triggers and freshness -> hand off to `ctx-build-context-index` in Company Data Context.

Package the least context needed for the current deliverable. Do not treat a task package as a new source of truth.

Use `assets/evidence-envelope.json` and `scripts/validate_evidence_bundle.py` for material claims, tested/approved/released states and artifact-hash verification.


## Stack-native adapter routing

After selecting the task, detect the real stack/version and read only the matching adapter below plus [the adapter index](references/technology-adapters.md). Do not load every adapter.

- [snowflake](references/adapter-snowflake.md)
- [bigquery](references/adapter-bigquery.md)

## Atomic task routing

- **Plan, define, design, map, specify or create a proposed artifact** (3 tasks): read [references/catalog-plan-design.md](references/catalog-plan-design.md).
- **Build, implement, configure, teach, interview or deliver an artifact** (9 tasks): read [references/catalog-build-deliver.md](references/catalog-build-deliver.md).
- **Inspect, analyze, test, review, validate, assess, certify or audit** (6 tasks): read [references/catalog-test-assure.md](references/catalog-test-assure.md).

Read only the best-matching catalog. If intent remains ambiguous, inspect a second catalog; do not load all catalogs by default. Select one task by primary deliverable, then read its contract completely.

## Completion response

State the selected task ID, primary deliverable, evidence inspected, validation performed, approval status, residual risks and next owner. A draft or plan is not an executed production outcome.
