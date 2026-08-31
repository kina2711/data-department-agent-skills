# orchestrator-collect-plan-risk

## Trigger

Use when the user asks to collect plan risk, requests the stated deliverable, or supplies an artifact that requires this atomic workflow. Do not select by job title alone.

## Contract

- Profile: `advisory-analysis`
- Risk tier: `R2-standard`
- Execution path: `standard-path`
- Contract version: `3.0`
- Criticality: `standard`
- Model tier: `standard` per [model selection](../model-selection.md); a lighter model never lowers the bar this output must clear.
- Goal: gom mọi thao tác rủi ro mà kế hoạch hàm ý để duyệt một lần lúc lập kế hoạch, kèm hạn dùng và số lần.
- Primary deliverable: **plan-time risk approval set**.

## Inputs and readiness

- Confirm objective, consumer, owner, target/environment, scope, constraints and acceptance criteria.
- Identify relevant systems, data, artifacts, dependencies, authority, evidence and tests.
- For controlled work, establish containment, backup, rollback or recovery before execution.

If an absent input changes semantics, risk, cost, scope or acceptance, classify it as blocking. Otherwise state a bounded assumption and record it.


## Procedure

1. Read [the lifecycle standard](../lifecycle-standard.md); apply its stages, gates and risk-adaptive path.
2. Load only applicable company context, then inspect live artifacts when facts may have changed.
3. Load technology or industry references only when they affect this deliverable.
4. Execute the stated goal; keep one primary deliverable and record provenance for material facts.
5. Run the tests below, resolve failures, obtain required approval and complete the lifecycle handoff.

Additional resources:
- Read [the harness delivery loop](../harness-delivery-loop.md); Plan, Work, Review and Ship each end at a gate, and Review is done by someone who did not do the work.
- Reuse `../../assets/harness-approval.yaml`. Gather the risky operations the plan implies and present them together at approval time; a guardrail that interrupts a running agent trains the operator to approve without reading.
- Every approval carries scope, an expiry and a use count. An approval without an expiry is a permanent grant issued by someone who thought they were approving one thing.
- Passing the gates means those things were checked. A specification wrong at Plan produces a defect that reaches Ship with a clean record behind it, and a task at R3 still needs named authority whether or not the loop's gates passed.
- Read [solution option framing](../solution-option-framing.md); frame three to five materially different approaches in `../../assets/design-option-set.yaml`, select one against the stated constraints in at most forty words, and derive the deliverable structure from that selection. Where this role already owns a scored selection artifact, use it instead of duplicating the decision.


## Tests and evidence

- Independent calculation or alternate method.
- Assumption and sensitivity challenge.
- Domain-semantic review.

Also verify scope and acceptance criteria, test relevant edge/failure paths, store evidence and keep failed mandatory checks visible. Use independent critical acceptance testing when practical.

## Approval and done

Require owner approval before production, sensitive, externally visible or materially costly execution. Approval is version- and scope-specific and never waives testing. Finish only when the deliverable meets acceptance criteria, mandatory tests pass, required approval exists, residual risks have owners, and handoff/monitoring is explicit. Stop as `blocked` or `failed` on missing authority, material ambiguity, failed validation or unsafe recovery; never fabricate success.

## Return

Return the task ID, lifecycle profile, risk tier, execution path, phase reached, primary deliverable, evidence links, test results, approvals, assumptions, open risks, affected assets, owner and one explicit next task. Route cross-role work through the department orchestrator.

Return the full contract; [response compression](../response-compression.md) governs wording, never coverage. Never soften `blocked` or `failed`, and never report an unrun check as a pass.
