---
name: master-data-management
description: Design and operate master entities, identity matching, survivorship, golden records, reference data, hierarchies, stewardship and synchronization. Use for MDM, entity resolution or reference-data work.
---

# Master Data Management

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

## Ownership

Own only deliverables listed in this role catalog. When the requested deliverable belongs to another role, produce a handoff instead of silently taking ownership. Use the department orchestrator for multi-role work.


## Atomic task routing

- **Plan, define, design, map, specify or create a proposed artifact** (3 tasks): read [references/catalog-plan-design.md](references/catalog-plan-design.md).
- **Build, implement, configure, teach, interview or deliver an artifact** (6 tasks): read [references/catalog-build-deliver.md](references/catalog-build-deliver.md).
- **Inspect, analyze, test, review, validate, assess, certify or audit** (2 tasks): read [references/catalog-test-assure.md](references/catalog-test-assure.md).
- **Deploy, release, monitor, recover, migrate, optimize, retire or improve** (2 tasks): read [references/catalog-operate-improve.md](references/catalog-operate-improve.md).

Read only the best-matching catalog. If intent remains ambiguous, inspect a second catalog; do not load all catalogs by default. Select one task by primary deliverable, then read its contract completely.

## Completion response

State the selected task ID, primary deliverable, evidence inspected, validation performed, approval status, residual risks and next owner. A draft or plan is not an executed production outcome.
