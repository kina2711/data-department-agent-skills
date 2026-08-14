# da-validate-analysis-result

## Trigger

Use when the user asks to validate analysis result, requests the stated deliverable, or supplies an artifact that requires this atomic workflow. Do not select by job title alone.

## Contract

- Profile: `advisory-analysis`
- Risk tier: `R0-light`
- Execution path: `fast-path`
- Contract version: `3.0`
- Criticality: `deep`
- Goal: kiểm tra totals, edge cases, benchmark và alternate query.
- Primary deliverable: **validation evidence**.

## Inputs and readiness

- Confirm objective, consumer, owner, target/environment, scope, constraints and acceptance criteria.
- Identify relevant systems, data, artifacts, dependencies, authority, evidence and tests.
- For controlled work, establish containment, backup, rollback or recovery before execution.

If an absent input changes semantics, risk, cost, scope or acceptance, classify it as blocking. Otherwise state a bounded assumption and record it.

## Deep execution contract

- Contract version: `3.0`.
- Criticality: `deep`; treat this as a low-freedom protocol for **validation evidence**.

Mandatory domain inputs:
- Decision question and population.
- Dataset grain/provenance.
- Method assumptions and comparison baseline.

Invariants that must remain true:
- Observation, inference and recommendation are separated.
- Uncertainty is visible.
- Calculations are reproducible.

Decision and execution sequence:
1. Frame.
2. Profile.
3. Calculate with alternate check.
4. Test sensitivity/segments.
5. Interpret for decision and peer review.

Required proof:
- Query/code and data snapshot.
- Result reproduction.
- Assumptions, uncertainty and reviewer findings.

Block before mutation or a positive completion decision when a mandatory input, authority, invariant, recovery path or proof source is unresolved. Preserve the failed state and route remediation explicitly; never weaken a test or threshold merely to pass.


## Procedure

1. Read [the lifecycle standard](../lifecycle-standard.md); apply its stages, gates and risk-adaptive path.
2. Load only applicable company context, then inspect live artifacts when facts may have changed.
3. Load technology or industry references only when they affect this deliverable.
4. Execute the stated goal; keep one primary deliverable and record provenance for material facts.
5. Run the tests below, resolve failures, obtain required approval and complete the lifecycle handoff.

Additional resources:
- Read [the analysis rigor and communication standard](../analysis-rigor-and-communication.md).
- Reuse the matching EDA, SQL explanation, methodology, peer-review, retrospective or impact template from `../../assets/`; use `../../scripts/profile_dataset.py` or `../../scripts/explain_sql.py` when applicable, only as deterministic first-pass evidence.


## Tests and evidence

- Independent calculation or alternate method.
- Assumption and sensitivity challenge.
- Domain-semantic review.

Also verify scope and acceptance criteria, test relevant edge/failure paths, store evidence and keep failed mandatory checks visible. Use independent critical acceptance testing when practical.

## Approval and done

Explicit approval is normally not required for read-only work, but becomes mandatory if scope expands to a governed or mutating action. Approval is version- and scope-specific and never waives testing. Finish only when the deliverable meets acceptance criteria, mandatory tests pass, required approval exists, residual risks have owners, and handoff/monitoring is explicit. Stop as `blocked` or `failed` on missing authority, material ambiguity, failed validation or unsafe recovery; never fabricate success.

## Return

Return the task ID, lifecycle profile, risk tier, execution path, phase reached, primary deliverable, evidence links, test results, approvals, assumptions, open risks, affected assets, owner and one explicit next task. Route cross-role work through the department orchestrator.
