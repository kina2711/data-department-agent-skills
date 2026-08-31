# orchestrator-package-agent-harness

## Trigger

Use when the user asks to package agent harness, requests the stated deliverable, or supplies an artifact that requires this atomic workflow. Do not select by job title alone.

## Contract

- Profile: `build-change`
- Risk tier: `R2-standard`
- Execution path: `standard-path`
- Contract version: `3.0`
- Criticality: `standard`
- Model tier: `standard` per [model selection](../model-selection.md); a lighter model never lowers the bar this output must clear.
- Goal: đóng gói harness đã khai báo thành thứ chạy lại được và bàn giao được, ghim mọi phiên bản đầu vào.
- Primary deliverable: **packaged agent harness**.

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
- Read [the agent harness standard](../agent-harness-standard.md); a harness is a boundary rather than a bundle, and most of its value is in what it excludes. "Everything the skill offers" is the absence of a scope, not a scope.
- Reuse `../../assets/agent-harness.yaml`. Pin every input that is not the user's request — schema index, corpus, registry, prompt — and record the pinned versions with the run; a harness that cannot say what it was working from turns every investigation into archaeology.
- Guardrails travel with the package or the recipient did not receive the harness: state plainly what it may write, what it may spend, and what it stops for, and name an accountable owner. An unowned harness in production is a set of permissions nobody is watching.
- Packaging changes how work is done and never what it must clear. Every lifecycle gate applies inside a harness exactly as outside it, and a clean evaluation on ten cases is an agent that passed ten cases.
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

Return the full contract; [response compression](../response-compression.md) governs wording, never coverage. Never soften `blocked` or `failed`, and never report an unrun check as a pass.
