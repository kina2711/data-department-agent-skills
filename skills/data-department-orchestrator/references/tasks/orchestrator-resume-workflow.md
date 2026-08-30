# orchestrator-resume-workflow

## Trigger

Use when the user asks to resume workflow, requests the stated deliverable, or supplies an artifact that requires this atomic workflow. Do not select by job title alone.

## Contract

- Profile: `advisory-analysis`
- Risk tier: `R2-standard`
- Execution path: `standard-path`
- Contract version: `3.0`
- Criticality: `enforced`
- Model tier: `standard` per [model selection](../model-selection.md); a lighter model never lowers the bar this output must clear.
- Goal: phục hồi context từ run state và ledgers mà không làm lại approved work.
- Primary deliverable: **resumed execution plan**.

## Inputs and readiness

- Confirm objective, consumer, owner, target/environment, scope, constraints and acceptance criteria.
- Identify relevant systems, data, artifacts, dependencies, authority, evidence and tests.
- For controlled work, establish containment, backup, rollback or recovery before execution.

If an absent input changes semantics, risk, cost, scope or acceptance, classify it as blocking. Otherwise state a bounded assumption and record it.

## Deep execution contract

- Contract version: `3.0`.
- Criticality: `enforced`; treat this as a low-freedom protocol for **resumed execution plan**.

Mandatory domain inputs:
- Objective and success contract.
- Task graph with owners.
- Current state and authority.

Invariants that must remain true:
- One accountable owner per task.
- No dependency or gate bypass.
- Child risk sets the workflow risk floor.

Decision and execution sequence:
1. Classify and bound.
2. Compose acyclic graph.
3. Validate readiness.
4. Execute one ready task.
5. Gate and hand off.

Required proof:
- Validated workflow graph.
- Version-bound approvals.
- Claim-to-evidence completion record.

Block before mutation or a positive completion decision when a mandatory input, authority, invariant, recovery path or proof source is unresolved. Preserve the failed state and route remediation explicitly; never weaken a test or threshold merely to pass.


## Procedure

1. Read [the lifecycle standard](../lifecycle-standard.md); apply its stages, gates and risk-adaptive path.
2. Load only applicable company context, then inspect live artifacts when facts may have changed.
3. Load technology or industry references only when they affect this deliverable.
4. Execute the stated goal; keep one primary deliverable and record provenance for material facts.
5. Run the tests below, resolve failures, obtain required approval and complete the lifecycle handoff.

Additional resources:
- Read [the execution discipline standard](../execution-discipline-standard.md).
- Use the success, scope, hypothesis or verification ledger from `../../assets/` that matches the current failure risk; do not load all templates by default.
- When the project root has a `project-constitution.json`, check the plan against it with `../../scripts/validate_constitution.py --proposal-file`; exit status 3 is a blocked plan, not a warning. A locked technology or blocking architecture rule changes only by versioned, approved amendment.
- Use exact canonical `task_id` values from `../../assets/task-catalog.json`; put any human-friendly occurrence label in optional `instance_id`. Initialize from `../../assets/workflow-manifest.json` and run `../../scripts/validate_workflow.py --mode plan`, `execute` or `complete` as appropriate. A read-only request still permits creating and validating a temporary manifest outside the target repository. Claim status must be exactly `draft`, `verified` or `rejected`.
- Keep `../../assets/run-state.yaml` synchronized with the manifest and validate it with `../../scripts/validate_run_state.py --task-catalog ../../assets/task-catalog.json`. A resumed run inherits validated state only; never reconstruct progress from conversation history.
- Read [the Workflow Runtime and Evidence OS](../workflow-runtime-and-evidence-os.md); validate workflow, evidence and version-bound approvals instead of relying on narrative gate claims.
- Before Git-backed mutation, require a verified success contract and pre-change scope contract. After the final change, run `core-audit-change-scope` and `core-verify-deliverable`; release remains blocked if either control is absent or failed.

- The declared risk tier is a minimum floor. Before each child task and before completion, inherit the highest current child-task risk tier and its approval, recovery and evidence requirements.

## Tests and evidence

- Independent calculation or alternate method.
- Assumption and sensitivity challenge.
- Domain-semantic review.

Also verify scope and acceptance criteria, test relevant edge/failure paths, store evidence and keep failed mandatory checks visible. Use independent critical acceptance testing when practical.

## Approval and done

Require owner approval before production, sensitive, externally visible or materially costly execution. Approval is version- and scope-specific and never waives testing. Finish only when the deliverable meets acceptance criteria, mandatory tests pass, required approval exists, residual risks have owners, and handoff/monitoring is explicit. Stop as `blocked` or `failed` on missing authority, material ambiguity, failed validation or unsafe recovery; never fabricate success.

## Return

Return the task ID, lifecycle profile, risk tier, execution path, phase reached, primary deliverable, evidence links, test results, approvals, assumptions, open risks, affected assets, owner and one explicit next task. Route cross-role work through the department orchestrator.

Return the full contract; [response compression](../response-compression.md) governs wording, never coverage. Never soften `blocked` or `failed`, and never report an unrun check as a pass.

Mirror the outcome into `../../assets/atomic-task-output.yaml` alongside the prose. Where the prose and the structured record disagree, the record stands and the task is not complete.
