# career-assess-topic-mastery

## Trigger

Use when the user asks to assess topic mastery, requests the stated deliverable, or supplies an artifact that requires this atomic workflow. Do not select by job title alone.

## Contract

- Profile: `career-development`
- Risk tier: `R1-reviewed`
- Execution path: `standard-path`
- Contract version: `3.0`
- Criticality: `standard`
- Goal: đánh giá recall, application, changed-scenario transfer, failure handling, evidence và freshness trước khi đổi mastery state.
- Primary deliverable: **topic mastery assessment**.

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
- Read [the career operating-system and evidence method](../career-operating-system.md).
- Reuse the career operating-system, career evidence or career review template from `../../assets/` that matches the deliverable.
- Read [the Career learner-memory and transition method](../career-learning-memory.md); preserve event lineage and keep mastery, exposure and production evidence distinct.
- Reuse the learner-memory, learning-event, prerequisite-map or transition-context asset from `../../assets/` that matches the deliverable.
- Run `../../scripts/validate_learning_memory.py` for plan/complete validation; use `../../scripts/build_skill_transition_context.py` to create a bounded read-only context pack for the next topic.
- Compute freshness with `../../scripts/schedule_topic_review.py` rather than typing a date; the interval follows demonstrated state, independent evidence count, version sensitivity and how many topics depend on this one. A computed due date is a scheduling decision, never evidence, and a topic that is not yet due is only not known to have decayed.

- Never guarantee title, promotion, compensation or timeline; distinguish portable capability from company-specific level mapping.
- Never relabel self-study or hypothetical work as production evidence, and never prescribe sustained overtime as ownership.

## Tests and evidence

- Career claim-to-evidence traceability and authorship check.
- Capability, prerequisite and real-work opportunity coverage review.
- Sustainable workload, recovery buffer and changed-constraint review.

Also verify scope and acceptance criteria, test relevant edge/failure paths, store evidence and keep failed mandatory checks visible. Use independent critical acceptance testing when practical.

## Approval and done

Require named reviewer acceptance before the artifact becomes an organizational baseline. Approval is version- and scope-specific and never waives testing. Finish only when the deliverable meets acceptance criteria, mandatory tests pass, required approval exists, residual risks have owners, and handoff/monitoring is explicit. Stop as `blocked` or `failed` on missing authority, material ambiguity, failed validation or unsafe recovery; never fabricate success.

## Return

Return the task ID, lifecycle profile, risk tier, execution path, phase reached, primary deliverable, evidence links, test results, approvals, assumptions, open risks, affected assets, owner and one explicit next task. Route cross-role work through the department orchestrator.

Report it in the compact shape from [response compression](../response-compression.md): one state line, the deliverable, only the fields that carry content, then one next action. Blocked gates, unrun checks, assumptions, limitations and residual risks are printed in full even here.
