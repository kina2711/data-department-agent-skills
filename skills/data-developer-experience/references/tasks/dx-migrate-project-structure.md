# dx-migrate-project-structure

## Trigger

Use when the user asks to migrate project structure, requests the stated deliverable, or supplies an artifact that requires this atomic workflow. Do not select by job title alone.

## Contract

- Profile: `build-change`
- Risk tier: `R3-controlled`
- Execution path: `controlled-path`
- Contract version: `3.0`
- Criticality: `enforced`
- Goal: chuyển layout/config có compatibility plan và verification.
- Primary deliverable: **migrated repository**.

## Inputs and readiness

- Confirm objective, consumer, owner, target/environment, scope, constraints and acceptance criteria.
- Identify relevant systems, data, artifacts, dependencies, authority, evidence and tests.
- For controlled work, establish containment, backup, rollback or recovery before execution.

If an absent input changes semantics, risk, cost, scope or acceptance, classify it as blocking. Otherwise state a bounded assumption and record it.

## Deep execution contract

- Contract version: `3.0`.
- Criticality: `enforced`; treat this as a low-freedom protocol for **migrated repository**.

Mandatory domain inputs:
- Developer journey and baseline friction.
- Repository/toolchain constraints.
- Target golden path.

Invariants that must remain true:
- Dx controls do not bypass security/quality.
- Templates are reproducible.
- Adoption is measured.

Decision and execution sequence:
1. Observe journey.
2. Trace a real path.
3. Design golden path.
4. Automate feedback.
5. Test clean setup and adoption.

Required proof:
- Time-to-first-success.
- Clean-room setup.
- Template/ci tests and developer feedback.

Block before mutation or a positive completion decision when a mandatory input, authority, invariant, recovery path or proof source is unresolved. Preserve the failed state and route remediation explicitly; never weaken a test or threshold merely to pass.


## Procedure

1. Read [the lifecycle standard](../lifecycle-standard.md); apply its stages, gates and risk-adaptive path.
2. Load only applicable company context, then inspect live artifacts when facts may have changed.
3. Load technology or industry references only when they affect this deliverable.
4. Execute the stated goal; keep one primary deliverable and record provenance for material facts.
5. Run the tests below, resolve failures, obtain required approval and complete the lifecycle handoff.

Additional resources:
- Read [the Workflow Runtime and Evidence OS](../workflow-runtime-and-evidence-os.md); validate workflow, evidence and version-bound approvals instead of relying on narrative gate claims.
- Read [the execution discipline standard](../execution-discipline-standard.md).
- Before Git-backed mutation, require a verified success contract and pre-change scope contract. After the final change, run `core-audit-change-scope` and `core-verify-deliverable`; release remains blocked if either control is absent or failed.


## Tests and evidence

- Static/unit/contract tests.
- Integration and data reconciliation.
- Security/performance/regression checks.

Also verify scope and acceptance criteria, test relevant edge/failure paths, store evidence and keep failed mandatory checks visible. Use independent critical acceptance testing when practical.

## Approval and done

Require explicit, scoped, version-specific human approval before execution and preserve rollback authority. Approval is version- and scope-specific and never waives testing. Finish only when the deliverable meets acceptance criteria, mandatory tests pass, required approval exists, residual risks have owners, and handoff/monitoring is explicit. Stop as `blocked` or `failed` on missing authority, material ambiguity, failed validation or unsafe recovery; never fabricate success.

## Return

Return the task ID, lifecycle profile, risk tier, execution path, phase reached, primary deliverable, evidence links, test results, approvals, assumptions, open risks, affected assets, owner and one explicit next task. Route cross-role work through the department orchestrator.

Return the full contract; [response compression](../response-compression.md) governs wording, never coverage. Never soften `blocked` or `failed`, and never report an unrun check as a pass.

Mirror the outcome into `../../assets/atomic-task-output.yaml` alongside the prose. Where the prose and the structured record disagree, the record stands and the task is not complete.
