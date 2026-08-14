# core-audit-change-scope

## Trigger

Use when the user asks to audit change scope, requests the stated deliverable, or supplies an artifact that requires this atomic workflow. Do not select by job title alone.

## Contract

- Profile: `advisory-analysis`
- Risk tier: `R0-light`
- Execution path: `fast-path`
- Contract version: `3.0`
- Criticality: `deep`
- Goal: đối chiếu thay đổi thực tế với yêu cầu, allowlist, planned deletions và task-to-file traceability để phát hiện scope creep.
- Primary deliverable: **surgical change-scope audit**.

## Inputs and readiness

- Confirm objective, consumer, owner, target/environment, scope, constraints and acceptance criteria.
- Identify relevant systems, data, artifacts, dependencies, authority, evidence and tests.
- For controlled work, establish containment, backup, rollback or recovery before execution.

If an absent input changes semantics, risk, cost, scope or acceptance, classify it as blocking. Otherwise state a bounded assumption and record it.

## Deep execution contract

- Contract version: `3.0`.
- Criticality: `deep`; treat this as a low-freedom protocol for **surgical change-scope audit**.

Mandatory domain inputs:
- Bounded request and consumer.
- Authoritative sources.
- Evidence and sensitivity constraints.

Invariants that must remain true:
- Least context and privilege.
- Provenance on material facts.
- No claim stronger than evidence.

Decision and execution sequence:
1. Classify.
2. Retrieve minimum context.
3. Inspect source.
4. Execute deterministic check.
5. Record evidence and limitation.

Required proof:
- Source identifiers and hashes.
- Method and environment.
- Pass/fail result and residual uncertainty.

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
- Use `../../assets/change-scope-contract.json` as the pre-change approved script input, `../../assets/change-scope-ledger.yaml` for the audit record, and run `../../scripts/audit_change_scope.py` for a Git repository. Missing or invalid traceability blocks the audit.


## Tests and evidence

- Requested-outcome-to-changed-artifact traceability.
- Allowlist, unexpected-file and unapproved-deletion scan.
- Generated-file, dependency and newly orphaned-artifact review.

Also verify scope and acceptance criteria, test relevant edge/failure paths, store evidence and keep failed mandatory checks visible. Use independent critical acceptance testing when practical.

## Approval and done

Explicit approval is normally not required for read-only work, but becomes mandatory if scope expands to a governed or mutating action. Approval is version- and scope-specific and never waives testing. Finish only when the deliverable meets acceptance criteria, mandatory tests pass, required approval exists, residual risks have owners, and handoff/monitoring is explicit. Stop as `blocked` or `failed` on missing authority, material ambiguity, failed validation or unsafe recovery; never fabricate success.

## Return

Return the task ID, lifecycle profile, risk tier, execution path, phase reached, primary deliverable, evidence links, test results, approvals, assumptions, open risks, affected assets, owner and one explicit next task. Route cross-role work through the department orchestrator.
