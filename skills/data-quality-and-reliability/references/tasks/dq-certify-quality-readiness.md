# dq-certify-quality-readiness

## Trigger

Use when the user asks to certify quality readiness, requests the stated deliverable, or supplies an artifact that requires this atomic workflow. Do not select by job title alone.

## Contract

- Profile: `governance-assurance`
- Risk tier: `R1-reviewed`
- Execution path: `standard-path`
- Contract version: `3.0`
- Criticality: `deep`
- Goal: kiểm tra coverage, thresholds và open issues.
- Primary deliverable: **quality gate decision**.

## Inputs and readiness

- Confirm objective, consumer, owner, target/environment, scope, constraints and acceptance criteria.
- Identify relevant systems, data, artifacts, dependencies, authority, evidence and tests.
- For controlled work, establish containment, backup, rollback or recovery before execution.

If an absent input changes semantics, risk, cost, scope or acceptance, classify it as blocking. Otherwise state a bounded assumption and record it.

## Deep execution contract

- Contract version: `3.0`.
- Criticality: `deep`; treat this as a low-freedom protocol for **quality gate decision**.

Mandatory domain inputs:
- Critical data element and consumer.
- Rule/slo and baseline.
- Incident/recovery ownership.

Invariants that must remain true:
- Rules have action and owner.
- Thresholds are not lowered to pass.
- Restored data is independently reconciled.

Decision and execution sequence:
1. Profile.
2. Define expectation.
3. Implement at boundaries.
4. Monitor.
5. Triage/contain/recover.
6. Verify prevention.

Required proof:
- Rule executions.
- Sli/slo history.
- Incident timeline.
- Reconciliation and corrective-action effectiveness.

Block before mutation or a positive completion decision when a mandatory input, authority, invariant, recovery path or proof source is unresolved. Preserve the failed state and route remediation explicitly; never weaken a test or threshold merely to pass.


## Procedure

1. Read [the lifecycle standard](../lifecycle-standard.md); apply its stages, gates and risk-adaptive path.
2. Load only applicable company context, then inspect live artifacts when facts may have changed.
3. Load technology or industry references only when they affect this deliverable.
4. Execute the stated goal; keep one primary deliverable and record provenance for material facts.
5. Run the tests below, resolve failures, obtain required approval and complete the lifecycle handoff.

Additional resources:
- Read [the stage-gated data-validation standard](../stage-gated-data-validation.md).
- Reuse `../../assets/pipeline-validation-plan.yaml`; validate input, transformation, output and monitoring layers with owned failure actions. In the Data Quality skill, `../../scripts/validate_tabular_data.py` can execute bounded CSV/JSONL checks.


## Tests and evidence

- Evidence completeness and sampling.
- Control-design and operating-effectiveness test.
- Authority and exception review.

Also verify scope and acceptance criteria, test relevant edge/failure paths, store evidence and keep failed mandatory checks visible. Use independent critical acceptance testing when practical.

## Approval and done

Require named reviewer acceptance before the artifact becomes an organizational baseline. Approval is version- and scope-specific and never waives testing. Finish only when the deliverable meets acceptance criteria, mandatory tests pass, required approval exists, residual risks have owners, and handoff/monitoring is explicit. Stop as `blocked` or `failed` on missing authority, material ambiguity, failed validation or unsafe recovery; never fabricate success.

## Return

Return the task ID, lifecycle profile, risk tier, execution path, phase reached, primary deliverable, evidence links, test results, approvals, assumptions, open risks, affected assets, owner and one explicit next task. Route cross-role work through the department orchestrator.
