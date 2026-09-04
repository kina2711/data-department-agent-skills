# brain-design-retrieval-routing

## Trigger

Use when the user asks to design retrieval routing, requests the stated deliverable, or supplies an artifact that requires this atomic workflow. Do not select by job title alone.

## Contract

- Profile: `design-specification`
- Risk tier: `R1-reviewed`
- Execution path: `standard-path`
- Contract version: `3.0`
- Criticality: `standard`
- Model tier: `standard` per [model selection](../model-selection.md); a lighter model never lowers the bar this output must clear.
- Goal: map intents và queries tới note types, scopes, freshness, ranking và fallback.
- Primary deliverable: **retrieval-routing design**.

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
- Read [answering from a closed set of sources](../bounded-source-answering.md). Name the set before the first question — which documents, which versions, when each was added — and announce anything that arrives mid-session, because the same answer half an hour later may rest on different ground.
- Three answers, and the middle one is the point. Grounded, with a locator precise enough to land on the passage. Not in the set, said plainly and then stopped — naming which documents were searched, since `I do not have enough information` tells a reader nothing and invites a rephrase that fails the same way. Or grounded but contradicted, reporting both sides rather than picking whichever reads better.
- Synthesis is the useful work and stays labelled as synthesis, carrying the passages it rests on. A conclusion needing one unstated fact from outside the set is an outside answer wearing citations. Widening the set is a decision made out loud by adding a document, never a thing that happens at the moment a question turns hard.
- Read [solution option framing](../solution-option-framing.md); frame three to five materially different approaches in `../../assets/design-option-set.yaml`, select one against the stated constraints in at most forty words, and derive the deliverable structure from that selection. Where this role already owns a scored selection artifact, use it instead of duplicating the decision.


## Tests and evidence

- Layer, stable-ID, source-hash, rights and note-to-source lineage validation.
- Representative retrieval, freshness, citation, forbidden-source and abstention evaluation.
- Privacy, prompt-injection, output-grounding, backup or lifecycle check as applicable.

Also verify scope and acceptance criteria, test relevant edge/failure paths, store evidence and keep failed mandatory checks visible. Use independent critical acceptance testing when practical.

## Approval and done

Require named reviewer acceptance before the artifact becomes an organizational baseline. Approval is version- and scope-specific and never waives testing. Finish only when the deliverable meets acceptance criteria, mandatory tests pass, required approval exists, residual risks have owners, and handoff/monitoring is explicit. Stop as `blocked` or `failed` on missing authority, material ambiguity, failed validation or unsafe recovery; never fabricate success.

## Return

Return the task ID, lifecycle profile, risk tier, execution path, phase reached, primary deliverable, evidence links, test results, approvals, assumptions, open risks, affected assets, owner and one explicit next task. Route cross-role work through the department orchestrator.

Report it in the compact shape from [response compression](../response-compression.md): one state line, the deliverable, only the fields that carry content, then one next action. Blocked gates, unrun checks, assumptions, limitations and residual risks are printed in full even here.
