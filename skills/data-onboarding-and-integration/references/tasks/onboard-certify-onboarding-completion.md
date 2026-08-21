# onboard-certify-onboarding-completion

## Trigger

Use when the user asks to certify onboarding completion, requests the stated deliverable, or supplies an artifact that requires this atomic workflow. Do not select by job title alone.

## Contract

- Profile: `onboarding`
- Risk tier: `R2-standard`
- Execution path: `standard-path`
- Contract version: `3.0`
- Criticality: `deep`
- Goal: kiểm tra mandatory evidence và manager/new-hire signoff.
- Primary deliverable: **onboarding completion decision**.

## Inputs and readiness

- Confirm objective, consumer, owner, target/environment, scope, constraints and acceptance criteria.
- Identify relevant systems, data, artifacts, dependencies, authority, evidence and tests.
- For controlled work, establish containment, backup, rollback or recovery before execution.

If an absent input changes semantics, risk, cost, scope or acceptance, classify it as blocking. Otherwise state a bounded assumption and record it.

## Deep execution contract

- Contract version: `3.0`.
- Criticality: `deep`; treat this as a low-freedom protocol for **onboarding completion decision**.

Mandatory domain inputs:
- Role outcomes and prior experience.
- Access/policy requirements.
- 7/30/60/90 owners and evidence.

Invariants that must remain true:
- Least privilege precedes productivity.
- Checklist completion is not readiness.
- Access removal is independently verified.

Decision and execution sequence:
1. Plan.
2. Prepare access/context.
3. Orient and shadow.
4. Guided then independent task.
5. Checkpoint and handoff.

Required proof:
- Access verification.
- Role work samples.
- Checkpoint rubric.
- Remaining gaps and offboarding proof.

Block before mutation or a positive completion decision when a mandatory input, authority, invariant, recovery path or proof source is unresolved. Preserve the failed state and route remediation explicitly; never weaken a test or threshold merely to pass.


## Procedure

1. Read [the lifecycle standard](../lifecycle-standard.md); apply its stages, gates and risk-adaptive path.
2. Load only applicable company context, then inspect live artifacts when facts may have changed.
3. Load technology or industry references only when they affect this deliverable.
4. Execute the stated goal; keep one primary deliverable and record provenance for material facts.
5. Run the tests below, resolve failures, obtain required approval and complete the lifecycle handoff.

Additional resources:
- Read [role onboarding tracks](../role-onboarding-tracks.md) and tailor by role and level.
- Reuse `../../assets/onboarding-plan.yaml`, `../../assets/access-readiness.yaml` and `../../assets/checkpoint.yaml`.
- Score the checkpoint with `../../scripts/score_onboarding_checkpoint.py`; a critical dimension below the bar blocks the readiness decision and is never averaged away, and any score above exposure must name evidence.

- When readiness inputs are incomplete, a bounded assumption-based draft is allowed, but mark failed gates and never represent planned access, training or contribution as completed.
- Treat actual access provisioning or sensitive-data enablement as R3-controlled; treat offboarding and access revocation as R4-critical with independent verification.
- Score every checkpoint against observable evidence and hand unresolved gaps to a named owner with a due date.

## Tests and evidence

- Access and environment verification.
- Policy/domain knowledge check.
- Guided then independent work-sample assessment.

Also verify scope and acceptance criteria, test relevant edge/failure paths, store evidence and keep failed mandatory checks visible. Use independent critical acceptance testing when practical.

## Approval and done

Require owner approval before production, sensitive, externally visible or materially costly execution. Approval is version- and scope-specific and never waives testing. Finish only when the deliverable meets acceptance criteria, mandatory tests pass, required approval exists, residual risks have owners, and handoff/monitoring is explicit. Stop as `blocked` or `failed` on missing authority, material ambiguity, failed validation or unsafe recovery; never fabricate success.

## Return

Return the task ID, lifecycle profile, risk tier, execution path, phase reached, primary deliverable, evidence links, test results, approvals, assumptions, open risks, affected assets, owner and one explicit next task. Route cross-role work through the department orchestrator.

Return the full contract; [response compression](../response-compression.md) governs wording, never coverage. Never soften `blocked` or `failed`, and never report an unrun check as a pass.

Mirror the outcome into `../../assets/atomic-task-output.yaml` alongside the prose. Where the prose and the structured record disagree, the record stands and the task is not complete.
