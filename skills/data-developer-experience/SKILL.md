---
name: data-developer-experience
description: Improve data developer setup, repositories, end-to-end data-path understanding, templates, local environments, CI feedback, standards and inner-loop productivity. Use for Data DevEx, repo reverse engineering, evidence-based walkthroughs or golden paths.
---

# Data Developer Experience

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

## Repository-understanding routing

- Broad project structure, entry points, components, dependencies and outputs -> `dx-reverse-engineer-data-project`.
- One source/job-to-sink path, with a prediction checkpoint and comparison to observed output -> `dx-trace-data-path-end-to-end`.

Do not claim understanding from summaries alone. Trace a real path through code, configuration and a deterministic or observed run when feasible. Run `scripts/detect_data_stack.py` before choosing adapters; detection is a candidate signal, not version proof.


## Stack-native adapter routing

After selecting the task, detect the real stack/version and read only the matching adapter below plus [the adapter index](references/technology-adapters.md). Do not load every adapter.

- [airflow](references/adapter-airflow.md)
- [dbt](references/adapter-dbt.md)
- [spark](references/adapter-spark.md)
- [databricks](references/adapter-databricks.md)
- [microsoft-fabric](references/adapter-microsoft-fabric.md)

## Atomic task routing

- **Plan, define, design, map, specify or create a proposed artifact** (3 tasks): read [references/catalog-plan-design.md](references/catalog-plan-design.md).
- **Build, implement, configure, teach, interview or deliver an artifact** (10 tasks): read [references/catalog-build-deliver.md](references/catalog-build-deliver.md).
- **Inspect, analyze, test, review, validate, assess, certify or audit** (5 tasks): read [references/catalog-test-assure.md](references/catalog-test-assure.md).
- **Deploy, release, monitor, recover, migrate, optimize, retire or improve** (1 task): read [references/catalog-operate-improve.md](references/catalog-operate-improve.md).

Read only the best-matching catalog. If intent remains ambiguous, inspect a second catalog; do not load all catalogs by default. Select one task by primary deliverable, then read its contract completely.

## Completion response

State the selected task ID, primary deliverable, evidence inspected, validation performed, approval status, residual risks and next owner. A draft or plan is not an executed production outcome.
