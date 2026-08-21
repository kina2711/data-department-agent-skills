---
name: data-technical-content-and-social
description: Build evidence-backed technical series for Facebook in Vietnamese, LinkedIn and Substack in English, and GitHub from research and a canonical article through code, diagrams, channel-native adaptations, QA, publishing and measurement. Use for Airflow, dbt, Spark, Kafka or other technical-content programs.
---

# Technical Content and Social

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

## Canonical-to-channel routing

- Whole series structure and dependency arc → `content-design-technical-series`.
- One episode's scope and evidence contract → `content-create-episode-brief`.
- Source-of-truth explanation → `content-write-canonical-technical-article`.
- Facebook, LinkedIn and Substack are separate atomic adaptations; select the requested channel task, not all three by default.
- Enforce the channel language contract: Facebook prose is Vietnamese (`vi`); LinkedIn and Substack prose is English (`en`). Preserve code, identifiers, product names and established technical terms where translation would reduce precision.
- One approved canonical artifact adapted to multiple channels → `content-repurpose-technical-content`.
- Accuracy, traceability, executable artifacts, voice/originality and platform fit are independent reviews; passing one never waives another.
- A whole/end-to-end series request containing research, code, diagrams and multiple channels must enter `orchestrator-run-sequential-workflow`; one content task must not masquerade as the completed series.
- Which canon concepts the series has actually taught, and where the arc leaves a gap → `content-audit-series-concept-coverage`.
- `content-create-technical-diagram-brief` specifies the visual only. Handoff actual Mermaid/PlantUML/D2/rendered work to `data-documentation-and-diagrams`, then return to `content-test-code-and-diagrams` before adaptation.
- After publication and measurement, return the approved artifact, its claim IDs and review outcome to `data-career-and-interview-coach` through `assets/content-evidence-return.yaml` and `career-build-career-evidence-portfolio`. This skill owns the artifact; Career owns whether it counts as competency evidence.

Do not write a social post before its material technical claims are supported. Do not fabricate production experience, benchmarks, incidents, readership or authority. Clearly label teaching examples, synthetic scenarios, opinions and hypotheses. Publication is an R3 controlled task and requires explicit channel authority plus approval of the exact version.


## Atomic task routing

- **Plan, define, design, map, specify or create a proposed artifact** (10 tasks): read [references/catalog-plan-design.md](references/catalog-plan-design.md).
- **Build, implement, configure, teach, interview or deliver an artifact** (7 tasks): read [references/catalog-build-deliver.md](references/catalog-build-deliver.md).
- **Inspect, analyze, test, review, validate, assess, certify or audit** (8 tasks): read [references/catalog-test-assure.md](references/catalog-test-assure.md).
- **Deploy, release, monitor, recover, migrate, optimize, retire or improve** (2 tasks): read [references/catalog-operate-improve.md](references/catalog-operate-improve.md).

Read only the best-matching catalog. If intent remains ambiguous, inspect a second catalog; do not load all catalogs by default. Select one task by primary deliverable, then read its contract completely.

## Completion response

State the selected task ID, primary deliverable, evidence inspected, validation performed, approval status, residual risks and next owner. A draft or plan is not an executed production outcome.
