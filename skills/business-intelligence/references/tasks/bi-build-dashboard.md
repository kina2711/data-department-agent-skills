# bi-build-dashboard

## Trigger

Use when the user asks to build dashboard, requests the stated deliverable, or supplies an artifact that requires this atomic workflow. Do not select by job title alone.

## Contract

- Profile: `build-change`
- Risk tier: `R2-standard`
- Execution path: `standard-path`
- Contract version: `3.0`
- Criticality: `deep`
- Goal: hiện thực pages, visuals, filters và navigation.
- Primary deliverable: **working dashboard**.

## Inputs and readiness

- Confirm objective, consumer, owner, target/environment, scope, constraints and acceptance criteria.
- Identify relevant systems, data, artifacts, dependencies, authority, evidence and tests.
- For controlled work, establish containment, backup, rollback or recovery before execution.

If an absent input changes semantics, risk, cost, scope or acceptance, classify it as blocking. Otherwise state a bounded assumption and record it.

## Deep execution contract

- Contract version: `3.0`.
- Criticality: `deep`; treat this as a low-freedom protocol for **working dashboard**.

Mandatory domain inputs:
- Audience and decisions.
- Certified metrics and semantic source.
- Interaction/access/refresh constraints.

Invariants that must remain true:
- Display logic does not redefine metrics.
- All states are designed.
- Access and accessibility are tested.

Decision and execution sequence:
1. Discover decisions.
2. Specify semantic/report behavior.
3. Build representative views.
4. Validate data and ux.
5. Publish with uat.

Required proof:
- Metric traceability.
- Viewport/state/accessibility tests.
- Refresh/performance and owner uat.

Block before mutation or a positive completion decision when a mandatory input, authority, invariant, recovery path or proof source is unresolved. Preserve the failed state and route remediation explicitly; never weaken a test or threshold merely to pass.


## Procedure

1. Read [the lifecycle standard](../lifecycle-standard.md); apply its stages, gates and risk-adaptive path.
2. Load only applicable company context, then inspect live artifacts when facts may have changed.
3. Load technology or industry references only when they affect this deliverable.
4. Execute the stated goal; keep one primary deliverable and record provenance for material facts.
5. Run the tests below, resolve failures, obtain required approval and complete the lifecycle handoff.

Additional resources:
- Read [the dashboard experience quality standard](../dashboard-experience-quality.md).
- Reuse `../../assets/dashboard-experience-audit.yaml` for audit/redesign evidence; keep audit read-only and separate observed facts from recommendations.
- Read [the execution discipline standard](../execution-discipline-standard.md).
- Before Git-backed mutation, require a verified success contract and pre-change scope contract. After the final change, run `core-audit-change-scope` and `core-verify-deliverable`; release remains blocked if either control is absent or failed.


## Tests and evidence

- Static/unit/contract tests.
- Integration and data reconciliation.
- Security/performance/regression checks.

Also verify scope and acceptance criteria, test relevant edge/failure paths, store evidence and keep failed mandatory checks visible. Use independent critical acceptance testing when practical.

## Approval and done

Require owner approval before production, sensitive, externally visible or materially costly execution. Approval is version- and scope-specific and never waives testing. Finish only when the deliverable meets acceptance criteria, mandatory tests pass, required approval exists, residual risks have owners, and handoff/monitoring is explicit. Stop as `blocked` or `failed` on missing authority, material ambiguity, failed validation or unsafe recovery; never fabricate success.

## Return

Return the task ID, lifecycle profile, risk tier, execution path, phase reached, primary deliverable, evidence links, test results, approvals, assumptions, open risks, affected assets, owner and one explicit next task. Route cross-role work through the department orchestrator.
