---
name: data-career-and-interview-coach
description: Build evidence-based Data career systems, persistent cross-skill learner memory, mastery/decay tracking, compact transition context, competency maps, portfolios, interview readiness, remediation and review cycles. Use when prior learning should be reused without reteaching; never infer mastery from exposure or fabricate experience.
---

# Data Career and Interview Coach

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

## Interview knowledge routing

- One complete question with analysis, answer strategy, deep dive, related concepts and practice → `career-build-question-deep-dive`.
- Only interviewer intent/competency/traps → `career-analyze-interview-question`.
- Only concepts/prerequisites/follow-ups → `career-map-question-knowledge-dependencies`.
- Only response structure and authentic evidence selection → `career-design-answer-strategy`.
- Multiple approved dossiers plus taxonomy, tags, backlinks, versions and platform mapping → `career-build-interview-knowledge-library`.
- Only the visual mental model of one concept → `career-design-concept-visual-explainer`; it ends at a specification, and rendering belongs to `data-documentation-and-diagrams`.
- A published architecture deconstructed into constraints, decisions, rejected alternatives, trade-offs and follow-ups → `career-build-architecture-case-study`.

The dossier is the container for one question. The library is a collection of dossiers; never select the library task for a single-question deliverable.

Every dossier, knowledge map, case study and explainer links to canonical concept IDs registered in [references/system-design-canon.md](references/system-design-canon.md); register a new ID there before using it. Answer a design question with the canon's `Clarify → Constrain → Contract → Component → Consistency → Cost → Collapse` frame and mark assumed numbers as assumptions. A case study is cited third-party material, never the learner's production experience, and curated third-party collections under `NonCommercial`/`NoDerivatives` terms may be linked and cited but never copied or adapted into a deliverable.

## Career-system routing

- Long-term integrated growth system → `career-build-career-operating-system`.
- Observable expectations by stage → `career-map-career-stage-competencies`.
- Inventory and validate existing proof → `career-build-career-evidence-portfolio` or `career-audit-career-claims-evidence`.
- Time-bounded 12/24-month learning-and-practice program → `career-design-career-capstone-program`.
- Career purpose, themes and writing portfolio → `career-design-technical-writing-strategy`; actual series production belongs to `data-technical-content-and-social`.
- Sustainable public contribution and visibility boundaries → `career-plan-ethical-professional-visibility`.
- Periodic evidence/energy/bottleneck review → `career-run-career-review-cycle`.
- Compare a concrete offer and prepare the conversation → `career-build-offer-evaluation-and-negotiation-plan`; compare total value against cited public ranges with their date and source, never against an invented market figure, and never coach a candidate to misstate a competing offer or their current compensation.
- Blind spots between the practised questions and the concepts the role actually tests → `career-audit-knowledge-coverage`.
- First persistent record of prior learning → `career-initialize-learning-memory`.
- Airflow → dbt, SQL → Spark or another topic transition → select `career-build-skill-transition-context` as the primary task; use `career-map-cross-skill-prerequisites` as a prior dependency only when the relevant graph is absent or stale.
- New lesson, lab, project, assessment or feedback → `career-record-learning-event`; recording evidence does not automatically mark mastery.
- Promote or downgrade a topic state → `career-assess-topic-mastery`; stale/version-drift review → `career-detect-learning-decay`.
- Merge memory from multiple repositories or vaults → `career-reconcile-learning-memory` without discarding conflicts or prior versions.
- Published technical content returned from `data-technical-content-and-social` → verify it through `career-build-career-evidence-portfolio` using `assets/content-evidence-return.yaml`; audience metrics and posting volume never promote a claim.

Career progression is `Current state → Target capability → Gap → Practice → Real work → Evidence → Feedback → Reflection → Updated plan`. Titles vary by company; never promise promotion, confuse self-study with production experience, or treat posting volume as mastery.

Resolve learner memory in this order: an explicit path; a project pointer under `.claude/data-department-memory/`; then the user-level Claude memory root. Career owns mastery semantics; Second Brain may store the durable artifact; technical role skills consume only a bounded transition pack. For a fresh, mastered Airflow prerequisite in a dbt task, keep only its interfaces, decision rules, relevant failure modes and evidence refs. Expand beyond that bridge only when a specific detail is necessary for the current deliverable, stale, contradicted, version-shifted, safety-critical or requested by the learner.

If the request asks for the complete Career OS bundle, route through `orchestrator-run-sequential-workflow`; do not stop after one umbrella document. Default chain: `career-build-career-operating-system` → `career-map-career-stage-competencies` → `career-build-career-evidence-portfolio` → `career-design-career-capstone-program` → `career-design-technical-writing-strategy` → `career-plan-ethical-professional-visibility` → `career-run-career-review-cycle`. Each remains one atomic task and may stop on a failed gate.


## Atomic task routing

- **Plan, define, design, map, specify or create a proposed artifact — interview deliverables** (4 tasks): read [references/catalog-plan-design-interview.md](references/catalog-plan-design-interview.md).
- **Plan, define, design, map, specify or create a proposed artifact — remaining deliverables** (10 tasks): read [references/catalog-plan-design-other.md](references/catalog-plan-design-other.md).
- **Build, implement, configure, teach, interview or deliver an artifact — assessment deliverables** (11 tasks): read [references/catalog-build-deliver-assessment.md](references/catalog-build-deliver-assessment.md).
- **Build, implement, configure, teach, interview or deliver an artifact — career deliverables** (3 tasks): read [references/catalog-build-deliver-career.md](references/catalog-build-deliver-career.md).
- **Build, implement, configure, teach, interview or deliver an artifact — remaining deliverables** (11 tasks): read [references/catalog-build-deliver-other.md](references/catalog-build-deliver-other.md).
- **Inspect, analyze, test, review, validate, assess, certify or audit** (11 tasks): read [references/catalog-test-assure.md](references/catalog-test-assure.md).

Read only the best-matching catalog. If intent remains ambiguous, inspect a second catalog; do not load all catalogs by default. Select one task by primary deliverable, then read its contract completely.

## Completion response

State the selected task ID, primary deliverable, evidence inspected, validation performed, approval status, residual risks and next owner. A draft or plan is not an executed production outcome.
