# docs-validate-diagram-semantics

## Trigger

Use when the user asks to validate diagram semantics, requests the stated deliverable, or supplies an artifact that requires this atomic workflow. Do not select by job title alone.

## Contract

- Profile: `advisory-analysis`
- Risk tier: `R0-light`
- Execution path: `fast-path`
- Contract version: `3.0`
- Criticality: `deep`
- Model tier: `strong` per [model selection](../model-selection.md); a lighter model never lowers the bar this output must clear.
- Goal: kiểm tra missing node, dead end, cardinality, direction và domain correctness.
- Primary deliverable: **diagram QA report**.

## Inputs and readiness

- Confirm objective, consumer, owner, target/environment, scope, constraints and acceptance criteria.
- Identify relevant systems, data, artifacts, dependencies, authority, evidence and tests.
- For controlled work, establish containment, backup, rollback or recovery before execution.

If an absent input changes semantics, risk, cost, scope or acceptance, classify it as blocking. Otherwise state a bounded assumption and record it.

## Deep execution contract

- Contract version: `3.0`.
- Criticality: `deep`; treat this as a low-freedom protocol for **diagram QA report**.

Mandatory domain inputs:
- Audience and question.
- Verified source artifacts.
- Notation/rendering and sensitivity constraints.

Invariants that must remain true:
- Relationships are evidence-backed.
- Diagram scope and confidence are explicit.
- Source remains editable/versioned.

Decision and execution sequence:
1. Inspect sources.
2. Choose view/notation.
3. Draft.
4. Validate nodes/edges and readability.
5. Render safely and review freshness.

Required proof:
- Source links.
- Syntax/render result.
- Reviewer corrections.
- Owner/version/freshness metadata.

Block before mutation or a positive completion decision when a mandatory input, authority, invariant, recovery path or proof source is unresolved. Preserve the failed state and route remediation explicitly; never weaken a test or threshold merely to pass.


## Procedure

1. Read [the lifecycle standard](../lifecycle-standard.md); apply its stages, gates and risk-adaptive path.
2. Load only applicable company context, then inspect live artifacts when facts may have changed.
3. Load technology or industry references only when they affect this deliverable.
4. Execute the stated goal; keep one primary deliverable and record provenance for material facts.
5. Run the tests below, resolve failures, obtain required approval and complete the lifecycle handoff.

Additional resources:
- Read [the diagram fidelity standard](../diagram-fidelity-standard.md); declare the diagram `observed`, `proposed` or `illustrative` on the rendering itself, because a reader who sees the image in a slide has no access to its metadata.
- Record each element in `../../assets/diagram-provenance.yaml` with the artifact it was read out of and a locator. Another diagram, a README, a ticket or recall is not inspection: a diagram derived from a diagram inherits its errors and none of its freshness.
- An observed diagram names the commit, tag or extraction timestamp it was read at; without one, whether it is still true has no answer. Record what was excluded and why — a silent omission reads as a claim that nothing was left out.
- Run `../../scripts/validate_diagram_source.py --provenance` before publishing; an unconnected node, a duplicated identifier, a missing text equivalent or a node with no inspected source is a defect, not a style choice. It confirms each element claims a source and never opens that source to confirm the claim.


## Tests and evidence

- Independent calculation or alternate method.
- Assumption and sensitivity challenge.
- Domain-semantic review.

Also verify scope and acceptance criteria, test relevant edge/failure paths, store evidence and keep failed mandatory checks visible. Use independent critical acceptance testing when practical.

## Approval and done

Explicit approval is normally not required for read-only work, but becomes mandatory if scope expands to a governed or mutating action. Approval is version- and scope-specific and never waives testing. Finish only when the deliverable meets acceptance criteria, mandatory tests pass, required approval exists, residual risks have owners, and handoff/monitoring is explicit. Stop as `blocked` or `failed` on missing authority, material ambiguity, failed validation or unsafe recovery; never fabricate success.

## Return

Return the task ID, lifecycle profile, risk tier, execution path, phase reached, primary deliverable, evidence links, test results, approvals, assumptions, open risks, affected assets, owner and one explicit next task. Route cross-role work through the department orchestrator.

Report it in the compact shape from [response compression](../response-compression.md): one state line, the deliverable, only the fields that carry content, then one next action. Blocked gates, unrun checks, assumptions, limitations and residual risks are printed in full even here.

Mirror the outcome into `../../assets/atomic-task-output.yaml` alongside the prose. Where the prose and the structured record disagree, the record stands and the task is not complete.
