# talent-map-question-to-competency-evidence

## Trigger

Use when the user asks to map question to competency evidence, requests the stated deliverable, or supplies an artifact that requires this atomic workflow. Do not select by job title alone.

## Contract

- Profile: `hiring`
- Risk tier: `R2-standard`
- Execution path: `standard-path`
- Contract version: `3.0`
- Criticality: `standard`
- Model tier: `standard` per [model selection](../model-selection.md); a lighter model never lowers the bar this output must clear.
- Goal: phân tích intent, competency, depth, expected evidence, probes và red flags của từng question.
- Primary deliverable: **question-competency-evidence matrix**.

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
- Read [role interview architecture](../role-interview-architecture.md) for methods, fairness, calibration and evidence rules.
- Reuse the workflow, scorecard, loop, candidate, rubric, calibration, evidence, debrief and audit templates from `../../assets/`.
- Read [question-to-competency validity controls](../question-knowledge-validity.md).
- Reuse the question traceability, answer-anchor or question-bank audit template from `../../assets/`.
- Read [solution option framing](../solution-option-framing.md); frame three to five materially different approaches in `../../assets/design-option-set.yaml`, select one against the stated constraints in at most forty words, and derive the deliverable structure from that selection. Where this role already owns a scored selection artifact, use it instead of duplicating the decision.

- A bundled hiring request is a composed workflow: select the primary artifact, then name the scorecard, assessment, calibration, evidence, debrief, decision and audit tasks in dependency order.
- Upgrade live hiring decisions, employment-impacting automation and jurisdiction-sensitive workflows to R3-controlled with HR/legal/accessibility review and a named hiring owner.
- Upgrade fairness, validity or quality-of-hire analysis to R3-controlled whenever it processes protected, sensitive or individual-level candidate/employee data.
- Do not claim fairness, validity or predictive usefulness from a small pilot; report sample size, uncertainty, missing data and subgroup privacy constraints.

## Tests and evidence

- Role-outcome, competency and construct-alignment review.
- Independent anchor scoring and interviewer calibration.
- Difficulty, redundancy, bias, leakage and candidate-burden audit.

Also verify scope and acceptance criteria, test relevant edge/failure paths, store evidence and keep failed mandatory checks visible. Use independent critical acceptance testing when practical.

## Approval and done

Require owner approval before production, sensitive, externally visible or materially costly execution. Approval is version- and scope-specific and never waives testing. Finish only when the deliverable meets acceptance criteria, mandatory tests pass, required approval exists, residual risks have owners, and handoff/monitoring is explicit. Stop as `blocked` or `failed` on missing authority, material ambiguity, failed validation or unsafe recovery; never fabricate success.

## Return

Return the task ID, lifecycle profile, risk tier, execution path, phase reached, primary deliverable, evidence links, test results, approvals, assumptions, open risks, affected assets, owner and one explicit next task. Route cross-role work through the department orchestrator.

Return the full contract; [response compression](../response-compression.md) governs wording, never coverage. Never soften `blocked` or `failed`, and never report an unrun check as a pass.
