---
name: data-department-orchestrator
description: Route ambiguous, organizational or multi-role Data Department requests and compose governed workflows with owners, dependencies, gates and handoffs. Use for cross-role repository rebuilds or end-to-end initiatives combining discovery, implementation and proof; route personal learning or portfolio projects to Personal Data Project Engineering.
---

# Data Department Orchestrator

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

## Role routing

Read [references/role-routing.md](references/role-routing.md) to select the primary role by deliverable ownership. Keep one accountable role per atomic task. Use shared core controls as dependencies, not as substitute owners.

Route personal learning, capstone or portfolio projects—including repo-first, dataset-first and external-idea-first requests—to `data-personal-project-engineering`. Keep organizational repository rebuilds and governed cross-role delivery in this orchestrator.

## Workflow state

For multi-step work, initialize `assets/workflow-manifest.json` and update it after every completed task or gate. Every `task_id` must be an exact canonical ID from `assets/task-catalog.json`; use optional `instance_id` only as a human-friendly occurrence label. Claim status is limited to `draft`, `verified` or `rejected`. Run `scripts/validate_workflow.py` before execution, after transitions and in complete mode before the final claim. Read-only work must still validate a temporary manifest outside the target repository. Use `assets/approval-record.json` for version/hash-bound authority. Resume from the latest verified state; never redo an approved artifact without a change request.

Record optional improvement telemetry only through `scripts/record_skill_telemetry.py` and `assets/telemetry-event.json`; never store user content, prompts, secrets or data values. Aggregate it with `scripts/analyze_skill_telemetry.py`; high failure or override rates trigger investigation, never weaker gates.


## Atomic task routing

- **Build, implement, configure, teach, interview or deliver an artifact** (17 tasks): read [references/catalog-build-deliver.md](references/catalog-build-deliver.md).
- **Inspect, analyze, test, review, validate, assess, certify or audit** (2 tasks): read [references/catalog-test-assure.md](references/catalog-test-assure.md).

Read only the best-matching catalog. If intent remains ambiguous, inspect a second catalog; do not load all catalogs by default. Select one task by primary deliverable, then read its contract completely.

## Completion response

State the selected task ID, primary deliverable, evidence inspected, validation performed, approval status, residual risks and next owner. A draft or plan is not an executed production outcome.
