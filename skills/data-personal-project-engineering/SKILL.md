---
name: data-personal-project-engineering
description: Create differentiated personal Data projects for portfolios, learning or capstones from a problem, dataset, repository, role gap, technology, paper, course, open-source issue, incident, constraint or mixed evidence. Use when Claude must select a project mode, assess a reference repo, transform borrowed inspiration into an attributed user-owned thesis, plan execution, or evaluate portfolio proof.
---

# Personal Data Project Engineering

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

## Personal-project routing

- First identify the strongest starting evidence; do not select a mode from the requested technology name alone.
- Personal project with an existing repository → `project-start-repo-first`, followed by `project-audit-reference-repository` and `project-transform-borrowed-source-to-original-thesis` when the repository is external.
- Someone else's idea, article, demo, video, project list or product → `project-start-inspiration-first`; treat it as a cited source, never as the user's original idea.
- Multiple credible inputs → `project-start-hybrid-input-project`; choose one primary mode and record the others as constraints/evidence.
- Target role or competency gap without a project thesis → `project-start-role-competency-first`; career strategy remains in `data-career-and-interview-coach`.
- Actual code scaffolding and repository implementation hand off to `data-developer-experience` and the relevant DA/AE/DE/DS/ML/BI role after the project thesis, scope and success evidence are ready.

Default borrowed-source policy: transform repositories and external ideas into an attributed, user-owned build thesis. Record origin, license/terms, exact source version, borrowed elements, rejected elements and substantive differentiators. Never hide provenance, claim an external idea as self-originated, or treat renaming, restyling, framework swaps or documentation-only changes as originality.

For repo-first work run `scripts/audit_repository.py` before qualitative assessment. Before portfolio completion run `scripts/build_portfolio_evidence.py --strict`; a README or screenshot alone cannot verify a claim.


## Stack-native adapter routing

After selecting the task, detect the real stack/version and read only the matching adapter below plus [the adapter index](references/technology-adapters.md). Do not load every adapter.

- [airflow](references/adapter-airflow.md)
- [dbt](references/adapter-dbt.md)
- [spark](references/adapter-spark.md)
- [kafka-flink](references/adapter-kafka-flink.md)
- [snowflake](references/adapter-snowflake.md)
- [bigquery](references/adapter-bigquery.md)
- [databricks](references/adapter-databricks.md)
- [microsoft-fabric](references/adapter-microsoft-fabric.md)
- [power-bi](references/adapter-power-bi.md)
- [metadata-catalog](references/adapter-metadata-catalog.md)
- [mlflow-kubeflow](references/adapter-mlflow-kubeflow.md)

## Atomic task routing

- **Plan, define, design, map, specify or create a proposed artifact** (10 tasks): read [references/catalog-plan-design.md](references/catalog-plan-design.md).
- **Build, implement, configure, teach, interview or deliver an artifact — project deliverables** (11 tasks): read [references/catalog-build-deliver-project.md](references/catalog-build-deliver-project.md).
- **Build, implement, configure, teach, interview or deliver an artifact — grounded deliverables** (4 tasks): read [references/catalog-build-deliver-grounded.md](references/catalog-build-deliver-grounded.md).
- **Build, implement, configure, teach, interview or deliver an artifact — remaining deliverables** (11 tasks): read [references/catalog-build-deliver-other.md](references/catalog-build-deliver-other.md).
- **Inspect, analyze, test, review, validate, assess, certify or audit** (6 tasks): read [references/catalog-test-assure.md](references/catalog-test-assure.md).

Read only the best-matching catalog. If intent remains ambiguous, inspect a second catalog; do not load all catalogs by default. Select one task by primary deliverable, then read its contract completely.

## Completion response

State the selected task ID, primary deliverable, evidence inspected, validation performed, approval status, residual risks and next owner. A draft or plan is not an executed production outcome.
