# academy-build-concept-knowledge-graph

## Trigger

Use when the user asks to build concept knowledge graph, requests the stated deliverable, or supplies an artifact that requires this atomic workflow. Do not select by job title alone.

## Contract

- Profile: `learning`
- Risk tier: `R2-standard`
- Execution path: `standard-path`
- Contract version: `3.0`
- Criticality: `deep`
- Goal: mô hình hóa concepts, prerequisites, dependencies, misconceptions và transfer paths.
- Primary deliverable: **concept knowledge graph**.

## Inputs and readiness

- Confirm objective, consumer, owner, target/environment, scope, constraints and acceptance criteria.
- Identify relevant systems, data, artifacts, dependencies, authority, evidence and tests.
- For controlled work, establish containment, backup, rollback or recovery before execution.

If an absent input changes semantics, risk, cost, scope or acceptance, classify it as blocking. Otherwise state a bounded assumption and record it.

## Deep execution contract

- Contract version: `3.0`.
- Criticality: `deep`; treat this as a low-freedom protocol for **concept knowledge graph**.

Mandatory domain inputs:
- Role-level outcomes.
- Prerequisites and learner baseline.
- Delivery constraints and transfer target.

Invariants that must remain true:
- Assessment aligns to outcomes.
- Attendance is not mastery.
- Certification scope matches demonstrated evidence.

Decision and execution sequence:
1. Map outcomes.
2. Sequence theory/practice.
3. Design authentic assessment.
4. Teach.
5. Calibrate.
6. Retest transfer and improve.

Required proof:
- Blueprint traceability.
- Learner artifacts.
- Calibrated scores.
- Remediation, retention and workplace-transfer evidence.

Block before mutation or a positive completion decision when a mandatory input, authority, invariant, recovery path or proof source is unresolved. Preserve the failed state and route remediation explicitly; never weaken a test or threshold merely to pass.


## Procedure

1. Read [the lifecycle standard](../lifecycle-standard.md); apply its stages, gates and risk-adaptive path.
2. Load only applicable company context, then inspect live artifacts when facts may have changed.
3. Load technology or industry references only when they affect this deliverable.
4. Execute the stated goal; keep one primary deliverable and record provenance for material facts.
5. Run the tests below, resolve failures, obtain required approval and complete the lifecycle handoff.

Additional resources:
- Read [role curricula](../role-curricula.md) and [assessment rules](../assessment-and-certification.md).
- Reuse the applicable curriculum, lesson, assessment or evidence template from `../../assets/`.
- Read [the knowledge deep-dive authoring standard](../knowledge-deep-dive-standard.md).
- Reuse the concept-graph, deep-dive or question-learning traceability template from `../../assets/`.

- Certification proves only the named, versioned competencies demonstrated by evidence; it never proves tenure, job title, automatic promotion or general seniority.
- Upgrade to R3-controlled and require People/HR plus accountable business approval when certification affects employment, promotion, compensation, regulation or external claims.
- For a curriculum bundle, select one primary artifact and chain `academy-write-theory-lesson` → `academy-design-hands-on-lab` → `academy-design-summative-exam` → `academy-write-answer-key` → `academy-write-assessment-rubric` → `academy-calibrate-assessors` → `academy-certify-role-competency` → `academy-measure-training-effectiveness` as applicable.

## Tests and evidence

- Authoritative-source and domain-review verification.
- Prerequisite, graph-cycle, misconception and coverage checks.
- Novel-scenario application and learning-transfer test.

Also verify scope and acceptance criteria, test relevant edge/failure paths, store evidence and keep failed mandatory checks visible. Use independent critical acceptance testing when practical.

## Approval and done

Require owner approval before production, sensitive, externally visible or materially costly execution. Approval is version- and scope-specific and never waives testing. Finish only when the deliverable meets acceptance criteria, mandatory tests pass, required approval exists, residual risks have owners, and handoff/monitoring is explicit. Stop as `blocked` or `failed` on missing authority, material ambiguity, failed validation or unsafe recovery; never fabricate success.

## Return

Return the task ID, lifecycle profile, risk tier, execution path, phase reached, primary deliverable, evidence links, test results, approvals, assumptions, open risks, affected assets, owner and one explicit next task. Route cross-role work through the department orchestrator.

Return the full contract; [response compression](../response-compression.md) governs wording, never coverage. Never soften `blocked` or `failed`, and never report an unrun check as a pass.

Mirror the outcome into `../../assets/atomic-task-output.yaml` alongside the prose. Where the prose and the structured record disagree, the record stands and the task is not complete.
