# ctx-build-context-index

## Trigger

Use when the user asks to build context index, requests the stated deliverable, or supplies an artifact that requires this atomic workflow. Do not select by job title alone.

## Contract

- Profile: `design-specification`
- Risk tier: `R2-standard`
- Execution path: `standard-path`
- Contract version: `3.0`
- Criticality: `deep`
- Goal: tạo index phân tầng chỉ rõ nguồn context, authority, scope, trigger đọc, owner và freshness cho Claude/agent sessions.
- Primary deliverable: **governed context index**.

## Inputs and readiness

- Confirm objective, consumer, owner, target/environment, scope, constraints and acceptance criteria.
- Identify relevant systems, data, artifacts, dependencies, authority, evidence and tests.
- For controlled work, establish containment, backup, rollback or recovery before execution.

If an absent input changes semantics, risk, cost, scope or acceptance, classify it as blocking. Otherwise state a bounded assumption and record it.

## Deep execution contract

- Contract version: `3.0`.
- Criticality: `deep`; treat this as a low-freedom protocol for **governed context index**.

Mandatory domain inputs:
- Source inventory and authority.
- Owners and freshness.
- Sensitivity and retrieval triggers.

Invariants that must remain true:
- Live evidence overrides stale context.
- Secrets/raw sensitive records are excluded.
- Conflicts remain explicit.

Decision and execution sequence:
1. Inventory.
2. Classify authority.
3. Redact.
4. Detect conflict.
5. Version and index.
6. Test representative retrieval.

Required proof:
- Context entry provenance.
- Last-verified timestamp.
- Conflict/freshness report and retrieval test.

Block before mutation or a positive completion decision when a mandatory input, authority, invariant, recovery path or proof source is unresolved. Preserve the failed state and route remediation explicitly; never weaken a test or threshold merely to pass.


## Procedure

1. Read [the lifecycle standard](../lifecycle-standard.md); apply its stages, gates and risk-adaptive path.
2. Load only applicable company context, then inspect live artifacts when facts may have changed.
3. Load technology or industry references only when they affect this deliverable.
4. Execute the stated goal; keep one primary deliverable and record provenance for material facts.
5. Run the tests below, resolve failures, obtain required approval and complete the lifecycle handoff.

Additional resources:
- Read [the context-engineering standard](../context-engineering-standard.md).
- Reuse the context-index or task-context-package template from `../../assets/`; for the task package, run `../../scripts/build_context_package.py` when local source files are available.
- Use `../../scripts/bootstrap_context_index.py` for a privacy-minimized source inventory; authority and ownership remain unverified until accountable confirmation.
- Read [solution option framing](../solution-option-framing.md); frame three to five materially different approaches in `../../assets/design-option-set.yaml`, select one against the stated constraints in at most forty words, and derive the deliverable structure from that selection. Where this role already owns a scored selection artifact, use it instead of duplicating the decision.


## Tests and evidence

- Unique-ID, authority and routing-rule validation.
- Broken-link, conflict and stale-entry checks.
- Least-context retrieval test using representative tasks.

Also verify scope and acceptance criteria, test relevant edge/failure paths, store evidence and keep failed mandatory checks visible. Use independent critical acceptance testing when practical.

## Approval and done

Require owner approval before production, sensitive, externally visible or materially costly execution. Approval is version- and scope-specific and never waives testing. Finish only when the deliverable meets acceptance criteria, mandatory tests pass, required approval exists, residual risks have owners, and handoff/monitoring is explicit. Stop as `blocked` or `failed` on missing authority, material ambiguity, failed validation or unsafe recovery; never fabricate success.

## Return

Return the task ID, lifecycle profile, risk tier, execution path, phase reached, primary deliverable, evidence links, test results, approvals, assumptions, open risks, affected assets, owner and one explicit next task. Route cross-role work through the department orchestrator.

Return the full contract; [response compression](../response-compression.md) governs wording, never coverage. Never soften `blocked` or `failed`, and never report an unrun check as a pass.

Mirror the outcome into `../../assets/atomic-task-output.yaml` alongside the prose. Where the prose and the structured record disagree, the record stands and the task is not complete.
