# orchestrator-run-parallel-workflow

## Trigger

Use when the user asks to run parallel workflow, requests the stated deliverable, or supplies an artifact that requires this atomic workflow. Do not select by job title alone.

## Contract

- Profile: `advisory-analysis`
- Risk tier: `R2-standard`
- Execution path: `standard-path`
- Contract version: `3.0`
- Criticality: `standard`
- Model tier: `standard` per [model selection](../model-selection.md); a lighter model never lowers the bar this output must clear.
- Goal: chạy independent checks và hợp nhất kết quả.
- Primary deliverable: **merged result**.

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
- Read [parallel execution and delegated branches](../parallel-execution-and-agent-teams.md); branches must be disjoint in what they write, not merely in what they read.
- Declare every branch in `../../assets/branch-delegation-contract.json` and validate the wave with `../../scripts/validate_branch_plan.py --task-catalog ../../assets/task-catalog.json` before dispatching anything. Without the catalog the check exits `incomplete`; that is not a pass.
- A delegated branch holds no authority: it never approves, publishes, mutates production or raises its own risk tier. Any task above the delegation ceiling stops at a proposal and returns it to the supervisor.
- Record fan-in in `../../assets/fan-in-merge-record.yaml`. Verify each returned artifact against its expected hash, route contradictions to `orchestrator-manage-conflict-register` with both positions intact, inherit the highest child risk tier, and report a failed branch as `partial` rather than reducing scope.
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
