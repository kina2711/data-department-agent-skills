# ai-audit-tool-surface

## Trigger

Use when the user asks to audit tool surface, requests the stated deliverable, or supplies an artifact that requires this atomic workflow. Do not select by job title alone.

## Contract

- Profile: `governance-assurance`
- Risk tier: `R1-reviewed`
- Execution path: `standard-path`
- Contract version: `3.0`
- Criticality: `deep`
- Model tier: `strong` per [model selection](../model-selection.md); a lighter model never lowers the bar this output must clear.
- Goal: đối chiếu quyền agent thật sự có với quyền contract cho phép và dấu vết truy cập.
- Primary deliverable: **tool surface access audit**.

## Inputs and readiness

- Confirm objective, consumer, owner, target/environment, scope, constraints and acceptance criteria.
- Identify relevant systems, data, artifacts, dependencies, authority, evidence and tests.
- For controlled work, establish containment, backup, rollback or recovery before execution.

If an absent input changes semantics, risk, cost, scope or acceptance, classify it as blocking. Otherwise state a bounded assumption and record it.

## Deep execution contract

- Contract version: `3.0`.
- Criticality: `deep`; treat this as a low-freedom protocol for **tool surface access audit**.

Mandatory domain inputs:
- Use case and allowed actions.
- Corpus/model/prompt versions.
- Eval set and threat boundary.

Invariants that must remain true:
- Answers/actions are grounded and attributable.
- Prompt injection is assumed.
- Release requires failure-class evidence.

Decision and execution sequence:
1. Frame.
2. Build versioned corpus/eval.
3. Retrieve/compose.
4. Evaluate quality/safety.
5. Red-team.
6. Release with monitoring.

Required proof:
- Dataset/index/prompt hashes.
- Retrieval/answer/tool evals.
- Injection tests.
- Cost/latency and system card.

Block before mutation or a positive completion decision when a mandatory input, authority, invariant, recovery path or proof source is unresolved. Preserve the failed state and route remediation explicitly; never weaken a test or threshold merely to pass.


## Procedure

1. Read [the lifecycle standard](../lifecycle-standard.md); apply its stages, gates and risk-adaptive path.
2. Load only applicable company context, then inspect live artifacts when facts may have changed.
3. Load technology or industry references only when they affect this deliverable.
4. Execute the stated goal; keep one primary deliverable and record provenance for material facts.
5. Run the tests below, resolve failures, obtain required approval and complete the lifecycle handoff.

Additional resources:
- Read [external tool access](../external-tool-access.md); this audit compares what the agent can actually reach against what its contract allows, which are rarely the same set.
- Reuse `../../assets/tool-surface-audit.yaml`. Report excess permissions the credential grants beyond the declared surface, writes taken without approval, calls made under a borrowed human identity, non-idempotent writes and runs with no write ceiling.
- Check the audit trail records identity, authority and task on every external call rather than only on failures. When a document changes at 3am, "an agent did it" is not an answer.


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
