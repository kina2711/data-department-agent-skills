# project-audit-originality-and-attribution

## Trigger

Use when the user asks to audit originality and attribution, requests the stated deliverable, or supplies an artifact that requires this atomic workflow. Do not select by job title alone.

## Contract

- Profile: `governance-assurance`
- Risk tier: `R1-reviewed`
- Execution path: `standard-path`
- Contract version: `3.0`
- Criticality: `deep`
- Goal: đối chiếu final artifacts với source origins, license, borrowed elements, differentiators và public claims.
- Primary deliverable: **originality and attribution audit**.

## Inputs and readiness

- Confirm objective, consumer, owner, target/environment, scope, constraints and acceptance criteria.
- Identify relevant systems, data, artifacts, dependencies, authority, evidence and tests.
- For controlled work, establish containment, backup, rollback or recovery before execution.

If an absent input changes semantics, risk, cost, scope or acceptance, classify it as blocking. Otherwise state a bounded assumption and record it.

## Deep execution contract

- Contract version: `3.0`.
- Criticality: `deep`; treat this as a low-freedom protocol for **originality and attribution audit**.

Mandatory domain inputs:
- Starting evidence and provenance.
- Target role/user/outcome.
- Time/data/rights/test constraints.

Invariants that must remain true:
- External sources stay attributed.
- Selection passes hard gates.
- Portfolio claims match implemented/tested evidence.

Decision and execution sequence:
1. Classify mode.
2. Score options.
3. Lock thesis.
4. Audit/transform sources.
5. Blueprint vertical slices.
6. Validate and package proof.

Required proof:
- Origin/license record.
- Option score.
- Thesis/differentiation.
- Tests, failure proof, reproduction and claim audit.

Block before mutation or a positive completion decision when a mandatory input, authority, invariant, recovery path or proof source is unresolved. Preserve the failed state and route remediation explicitly; never weaken a test or threshold merely to pass.


## Procedure

1. Read [the lifecycle standard](../lifecycle-standard.md); apply its stages, gates and risk-adaptive path.
2. Load only applicable company context, then inspect live artifacts when facts may have changed.
3. Load technology or industry references only when they affect this deliverable.
4. Execute the stated goal; keep one primary deliverable and record provenance for material facts.
5. Run the tests below, resolve failures, obtain required approval and complete the lifecycle handoff.

Additional resources:
- Read [the personal-project operating system](../personal-project-operating-system.md) and reuse the matching intake, option-scorecard, thesis, roadmap or evidence-plan asset.
- Read [the repository assessment and originality standard](../repository-assessment-and-originality.md); inspect the exact source/version and license before reuse.
- When a project manifest exists, run `../../scripts/validate_personal_project_manifest.py`; plan mode is not completion evidence.


## Tests and evidence

- Evidence completeness and sampling.
- Control-design and operating-effectiveness test.
- Authority and exception review.

Also verify scope and acceptance criteria, test relevant edge/failure paths, store evidence and keep failed mandatory checks visible. Use independent critical acceptance testing when practical.

## Approval and done

Require named reviewer acceptance before the artifact becomes an organizational baseline. Approval is version- and scope-specific and never waives testing. Finish only when the deliverable meets acceptance criteria, mandatory tests pass, required approval exists, residual risks have owners, and handoff/monitoring is explicit. Stop as `blocked` or `failed` on missing authority, material ambiguity, failed validation or unsafe recovery; never fabricate success.

## Return

Return the task ID, lifecycle profile, risk tier, execution path, phase reached, primary deliverable, evidence links, test results, approvals, assumptions, open risks, affected assets, owner and one explicit next task. Route cross-role work through the department orchestrator.

Report it in the compact shape from [response compression](../response-compression.md): one state line, the deliverable, only the fields that carry content, then one next action. Blocked gates, unrun checks, assumptions, limitations and residual risks are printed in full even here.

Mirror the outcome into `../../assets/atomic-task-output.yaml` alongside the prose. Where the prose and the structured record disagree, the record stands and the task is not complete.
