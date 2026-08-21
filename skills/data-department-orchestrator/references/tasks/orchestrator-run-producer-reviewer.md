# orchestrator-run-producer-reviewer

## Trigger

Use when the user asks to run producer reviewer, requests the stated deliverable, or supplies an artifact that requires this atomic workflow. Do not select by job title alone.

## Contract

- Profile: `advisory-analysis`
- Risk tier: `R2-standard`
- Execution path: `standard-path`
- Contract version: `3.0`
- Criticality: `standard`
- Goal: chạy vòng producer/reviewer độc lập với rubric chốt trước, giữ kín lập luận của producer tới khi reviewer ghi verdict, và đưa bất đồng chưa giải vào conflict register.
- Primary deliverable: **producer-reviewer verdict record**.

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
- Read [the producer-reviewer method](../producer-reviewer-method.md); fix the acceptance criteria and rubric before production, and withhold the rationale behind the artifact until the reviewer has recorded an independent verdict.
- Reuse `../../assets/producer-reviewer-record.yaml`. The producer and reviewer are never the same actor, the reviewer is not a branch the producer dispatched, and every round is recorded including the ones that failed.
- Reviewer acceptance is quality evidence, never owner approval; a gate requiring named authority bound to artifact version and hash stays unmet until that approval exists.
- Cap the loop at two full rounds. Escalate an unresolved disagreement to the requester through `orchestrator-manage-conflict-register` with both positions; never split the difference or let the more confident side win.
- Read [the execution discipline standard](../execution-discipline-standard.md).
- Before Git-backed mutation, require a verified success contract and pre-change scope contract. After the final change, run `core-audit-change-scope` and `core-verify-deliverable`; release remains blocked if either control is absent or failed.

- The declared risk tier is a minimum floor. Before each child task and before completion, inherit the highest current child-task risk tier and its approval, recovery and evidence requirements.

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
