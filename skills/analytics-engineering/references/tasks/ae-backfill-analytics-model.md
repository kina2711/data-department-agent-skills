# ae-backfill-analytics-model

## Trigger

Use when the user asks to backfill analytics model, requests the stated deliverable, or supplies an artifact that requires this atomic workflow. Do not select by job title alone.

## Contract

- Profile: `advisory-analysis`
- Risk tier: `R3-controlled`
- Execution path: `controlled-path`
- Contract version: `3.0`
- Criticality: `enforced`
- Goal: chạy history rebuild và reconcile metrics.
- Primary deliverable: **verified backfill**.

## Inputs and readiness

- Confirm objective, consumer, owner, target/environment, scope, constraints and acceptance criteria.
- Identify relevant systems, data, artifacts, dependencies, authority, evidence and tests.
- For controlled work, establish containment, backup, rollback or recovery before execution.

If an absent input changes semantics, risk, cost, scope or acceptance, classify it as blocking. Otherwise state a bounded assumption and record it.

## Deep execution contract

- Contract version: `3.0`.
- Criticality: `enforced`; treat this as a low-freedom protocol for **verified backfill**.

Mandatory domain inputs:
- Metric semantics and grain.
- Source contracts and lineage.
- Materialization and change strategy.

Invariants that must remain true:
- Joins preserve intended grain.
- Business definitions need authority.
- Incremental logic equals full refresh.

Decision and execution sequence:
1. Model layers.
2. Encode contracts.
3. Implement tests.
4. Compare incremental/full.
5. Document lineage and release impact.

Required proof:
- Compiled model/sql.
- Contract and reconciliation results.
- Lineage, performance and metric approval.

Block before mutation or a positive completion decision when a mandatory input, authority, invariant, recovery path or proof source is unresolved. Preserve the failed state and route remediation explicitly; never weaken a test or threshold merely to pass.


## Procedure

1. Read [the lifecycle standard](../lifecycle-standard.md); apply its stages, gates and risk-adaptive path.
2. Load only applicable company context, then inspect live artifacts when facts may have changed.
3. Load technology or industry references only when they affect this deliverable.
4. Execute the stated goal; keep one primary deliverable and record provenance for material facts.
5. Run the tests below, resolve failures, obtain required approval and complete the lifecycle handoff.

Additional resources:
- Read [the Workflow Runtime and Evidence OS](../workflow-runtime-and-evidence-os.md); validate workflow, evidence and version-bound approvals instead of relying on narrative gate claims.


## Tests and evidence

- Independent calculation or alternate method.
- Assumption and sensitivity challenge.
- Domain-semantic review.

Also verify scope and acceptance criteria, test relevant edge/failure paths, store evidence and keep failed mandatory checks visible. Use independent critical acceptance testing when practical.

## Approval and done

Require explicit, scoped, version-specific human approval before execution and preserve rollback authority. Approval is version- and scope-specific and never waives testing. Finish only when the deliverable meets acceptance criteria, mandatory tests pass, required approval exists, residual risks have owners, and handoff/monitoring is explicit. Stop as `blocked` or `failed` on missing authority, material ambiguity, failed validation or unsafe recovery; never fabricate success.

## Return

Return the task ID, lifecycle profile, risk tier, execution path, phase reached, primary deliverable, evidence links, test results, approvals, assumptions, open risks, affected assets, owner and one explicit next task. Route cross-role work through the department orchestrator.

Return the full contract; [response compression](../response-compression.md) governs wording, never coverage. Never soften `blocked` or `failed`, and never report an unrun check as a pass.

Mirror the outcome into `../../assets/atomic-task-output.yaml` alongside the prose. Where the prose and the structured record disagree, the record stands and the task is not complete.
