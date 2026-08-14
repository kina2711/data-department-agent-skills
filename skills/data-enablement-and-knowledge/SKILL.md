---
name: data-enablement-and-knowledge
description: Enable data teams through technical onboarding, learning plans, explanations, walkthroughs, pairing, knowledge checks, articles and knowledge-base curation. Use for internal data enablement or knowledge-transfer work.
---

# Data Enablement and Knowledge

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

## Knowledge-library routing

- One standalone note → `enable-create-knowledge-article`.
- One concept and its relationships → `enable-build-concept-knowledge-map`.
- Multiple entries with canonical IDs, taxonomy, backlinks, owners, versions and freshness → `enable-build-versioned-knowledge-library`.
- Publish an already reviewed artifact to Notion/Confluence/portal → `enable-publish-knowledge`.

For a linked/versioned library request, select the library task even when the user also asks for a design or publishing plan. Treat publication as a downstream handoff.


## Atomic task routing

- **Plan, define, design, map, specify or create a proposed artifact** (5 tasks): read [references/catalog-plan-design.md](references/catalog-plan-design.md).
- **Build, implement, configure, teach, interview or deliver an artifact** (10 tasks): read [references/catalog-build-deliver.md](references/catalog-build-deliver.md).
- **Inspect, analyze, test, review, validate, assess, certify or audit** (1 task): read [references/catalog-test-assure.md](references/catalog-test-assure.md).
- **Deploy, release, monitor, recover, migrate, optimize, retire or improve** (1 task): read [references/catalog-operate-improve.md](references/catalog-operate-improve.md).

Read only the best-matching catalog. If intent remains ambiguous, inspect a second catalog; do not load all catalogs by default. Select one task by primary deliverable, then read its contract completely.

## Completion response

State the selected task ID, primary deliverable, evidence inspected, validation performed, approval status, residual risks and next owner. A draft or plan is not an executed production outcome.
