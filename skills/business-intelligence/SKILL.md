---
name: business-intelligence
description: Design, build, test and govern BI semantic models, KPIs, dashboards, reports, interactions, row-level security, refresh, accessibility and adoption. Use for BI Engineer, reporting or dashboard work.
---

# Business Intelligence

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

## Dashboard experience routing

- Read-only critique of an existing dashboard -> `bi-audit-dashboard-experience`.
- A redesign specification from a completed audit or explicit redesign brief -> `bi-redesign-dashboard-experience`.
- New implementation from an approved dashboard/report specification -> `bi-build-dashboard`.
- Narrow navigation, readability, accessibility or mobile verification -> `bi-test-dashboard-usability`.

Never invent a KPI, benchmark, testimonial or business result to fill a visual slot. Preserve the existing design system unless the redesign scope explicitly changes it.
`bi-redesign-dashboard-experience` ends at an implementation-ready specification. If the user authorizes actual artifact mutation, hand the approved specification to `bi-build-dashboard` as a separate R2 build task.


## Stack-native adapter routing

After selecting the task, detect the real stack/version and read only the matching adapter below plus [the adapter index](references/technology-adapters.md). Do not load every adapter.

- [snowflake](references/adapter-snowflake.md)
- [bigquery](references/adapter-bigquery.md)
- [microsoft-fabric](references/adapter-microsoft-fabric.md)
- [power-bi](references/adapter-power-bi.md)
- [tableau-looker](references/adapter-tableau-looker.md)

## Atomic task routing

- **Plan, define, design, map, specify or create a proposed artifact** (4 tasks): read [references/catalog-plan-design.md](references/catalog-plan-design.md).
- **Build, implement, configure, teach, interview or deliver an artifact — evidence deliverables** (2 tasks): read [references/catalog-build-deliver-evidence.md](references/catalog-build-deliver-evidence.md).
- **Build, implement, configure, teach, interview or deliver an artifact — release deliverables** (2 tasks): read [references/catalog-build-deliver-release.md](references/catalog-build-deliver-release.md).
- **Build, implement, configure, teach, interview or deliver an artifact — remaining deliverables** (11 tasks): read [references/catalog-build-deliver-other.md](references/catalog-build-deliver-other.md).
- **Inspect, analyze, test, review, validate, assess, certify or audit** (8 tasks): read [references/catalog-test-assure.md](references/catalog-test-assure.md).
- **Deploy, release, monitor, recover, migrate, optimize, retire or improve** (5 tasks): read [references/catalog-operate-improve.md](references/catalog-operate-improve.md).

Read only the best-matching catalog. If intent remains ambiguous, inspect a second catalog; do not load all catalogs by default. Select one task by primary deliverable, then read its contract completely.

## Completion response

State the selected task ID, primary deliverable, evidence inspected, validation performed, approval status, residual risks and next owner. A draft or plan is not an executed production outcome.
