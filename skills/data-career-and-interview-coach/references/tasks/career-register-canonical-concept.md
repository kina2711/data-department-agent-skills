# career-register-canonical-concept

## Trigger

Use when the user asks to register canonical concept, requests the stated deliverable, or supplies an artifact that requires this atomic workflow. Do not select by job title alone.

## Contract

- Profile: `career-coaching`
- Risk tier: `R1-reviewed`
- Execution path: `standard-path`
- Contract version: `3.0`
- Criticality: `standard`
- Model tier: `standard` per [model selection](../model-selection.md); a lighter model never lowers the bar this output must clear.
- Goal: cấp và quản lý concept key nối canon, note, topic và competency về một danh tính.
- Primary deliverable: **canonical concept registry entry**.

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
- Read [coaching ethics](../coaching-ethics-and-method.md) and [role curricula](../role-curricula.md).
- Reuse the readiness, mock-assessment and remediation templates from `../../assets/`.
- Read [the canonical concept registry](../concept-registry-standard.md); the registry owns identity, never content, and it is not a competency framework.
- Reuse `../../assets/concept-registry.json`. A key carries its one-sentence definition, domain and owner from the moment it is coined; that sentence is what lets two artifacts tell whether they mean the same concept. Notes may bind to a `proposed` key immediately, but only `registered` keys count toward coverage.
- Bindings point outward from the registry: record canon, note, topic, competency and question IDs on the key and rewrite none of them. Exactly one primary note per key, one key per alias, and supersede rather than delete — a deleted key breaks a crosswalk that keeps rendering a coverage number.
- Run `../../scripts/validate_concept_registry.py` before accepting a batch; resolve its near-duplicate report first, because merging two proposed keys is cheap and merging two registered keys that already carry bindings is not. It also reports duplicate primaries, alias collisions, dangling bindings, `parents` cycles and canon IDs with no key, and it cannot judge whether a definition is a good one.
- Read [solution option framing](../solution-option-framing.md); frame three to five materially different approaches in `../../assets/design-option-set.yaml`, select one against the stated constraints in at most forty words, and derive the deliverable structure from that selection. Where this role already owns a scored selection artifact, use it instead of duplicating the decision.

- Assess before teaching, teach before simulation, score before revealing a model answer, and retest the same competency with a novel scenario.
- Never fabricate candidate experience, complete a live assessment, impersonate the candidate or treat a single mock as proof of readiness.

## Tests and evidence

- Factual and source verification.
- Authentic-evidence and no-fabrication review.
- Unseen follow-up and changed-constraint retest without notes.

Also verify scope and acceptance criteria, test relevant edge/failure paths, store evidence and keep failed mandatory checks visible. Use independent critical acceptance testing when practical.

## Approval and done

Require named reviewer acceptance before the artifact becomes an organizational baseline. Approval is version- and scope-specific and never waives testing. Finish only when the deliverable meets acceptance criteria, mandatory tests pass, required approval exists, residual risks have owners, and handoff/monitoring is explicit. Stop as `blocked` or `failed` on missing authority, material ambiguity, failed validation or unsafe recovery; never fabricate success.

## Return

Return the task ID, lifecycle profile, risk tier, execution path, phase reached, primary deliverable, evidence links, test results, approvals, assumptions, open risks, affected assets, owner and one explicit next task. Route cross-role work through the department orchestrator.

Report it in the compact shape from [response compression](../response-compression.md): one state line, the deliverable, only the fields that carry content, then one next action. Blocked gates, unrun checks, assumptions, limitations and residual risks are printed in full even here.
