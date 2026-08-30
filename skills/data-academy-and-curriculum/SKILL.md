---
name: data-academy-and-curriculum
description: Design and deliver role-based Data Academy curricula with theory, labs, capstones, assessments, remediation, certification and effectiveness measurement. Use for structured learning programs across Data roles and levels. Route hiring loops, scorecards and candidate evaluation to data-talent-acquisition-and-interview; this skill teaches, never selects.
---

# Data Academy and Curriculum

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

## Deep-dive routing

- Concept relationships and prerequisites → `academy-build-concept-knowledge-graph`.
- One evidence-backed concept explanation → `academy-write-knowledge-deep-dive`.
- Question-to-competency/objective/assessment coverage → `academy-map-questions-to-learning-objectives`.

For a bundle, select the artifact needed first and state the other two tasks as ordered handoffs.

## Note-corpus routing

A request for a whole body of notes for a role or domain rather than one artifact runs [the note-corpus operating system](references/note-corpus-operating-system.md), one stage at a time:

- What the role is expected to know, from cited sources → `academy-research-role-roadmap`.
- Roadmap steps into ordered tracks and modules → `academy-build-skill-track-map`.
- Every planned note with its ID, module and prerequisites → `academy-plan-note-corpus`.
- One module built to completion → `academy-build-note-module`.
- Duplication, dangling edges, cycles, staleness and coverage → `academy-audit-note-corpus`.
- The durable record of what exists → `academy-index-note-corpus`.
- Which modules to build first, against a measured gap → `academy-prioritize-corpus-by-gap`.
- Running a corpus scenario against a learner → `academy-run-note-diagnostic`.

Every note, module and scenario binds to a registered `ck.` concept key from [the canonical concept registry](references/concept-registry-standard.md); keys are minted by `career-register-canonical-concept` before anything references them. A diagnostic session proposes an evidence class and hands it to Career, which decides whether mastery changed.

Resume from `note-corpus-manifest.json` rather than re-deriving the plan; regenerating it renumbers IDs that existing notes already point at. Never claim the corpus is current without dated sources, and never read a built note as evidence that anyone learned it.


## Atomic task routing

- **Plan, define, design, map, specify or create a proposed artifact — learning deliverables** (6 tasks): read [references/catalog-plan-design-learning.md](references/catalog-plan-design-learning.md).
- **Plan, define, design, map, specify or create a proposed artifact — role deliverables** (3 tasks): read [references/catalog-plan-design-role.md](references/catalog-plan-design-role.md).
- **Plan, define, design, map, specify or create a proposed artifact — specification deliverables** (2 tasks): read [references/catalog-plan-design-specification.md](references/catalog-plan-design-specification.md).
- **Plan, define, design, map, specify or create a proposed artifact — assessment deliverables** (2 tasks): read [references/catalog-plan-design-assessment.md](references/catalog-plan-design-assessment.md).
- **Plan, define, design, map, specify or create a proposed artifact — corpus deliverables** (2 tasks): read [references/catalog-plan-design-corpus.md](references/catalog-plan-design-corpus.md).
- **Plan, define, design, map, specify or create a proposed artifact — learner deliverables** (2 tasks): read [references/catalog-plan-design-learner.md](references/catalog-plan-design-learner.md).
- **Plan, define, design, map, specify or create a proposed artifact — remaining deliverables** (11 tasks): read [references/catalog-plan-design-other.md](references/catalog-plan-design-other.md).
- **Build, implement, configure, teach, interview or deliver an artifact** (11 tasks): read [references/catalog-build-deliver.md](references/catalog-build-deliver.md).
- **Inspect, analyze, test, review, validate, assess, certify or audit** (8 tasks): read [references/catalog-test-assure.md](references/catalog-test-assure.md).
- **Deploy, release, monitor, recover, migrate, optimize, retire or improve** (1 task): read [references/catalog-operate-improve.md](references/catalog-operate-improve.md).

Read only the best-matching catalog. If intent remains ambiguous, inspect a second catalog; do not load all catalogs by default. Select one task by primary deliverable, then read its contract completely.

## Completion response

State the selected task ID, primary deliverable, evidence inspected, validation performed, approval status, residual risks and next owner. A draft or plan is not an executed production outcome.
