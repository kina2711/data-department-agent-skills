# book-test-retrieval-and-application

## Trigger

Use when the user asks to test retrieval and application, requests the stated deliverable, or supplies an artifact that requires this atomic workflow. Do not select by job title alone.

## Contract

- Profile: `advisory-analysis`
- Risk tier: `R0-light`
- Execution path: `fast-path`
- Contract version: `3.0`
- Criticality: `deep`
- Model tier: `standard` per [model selection](../model-selection.md); a lighter model never lowers the bar this output must clear.
- Goal: dùng unseen queries và scenarios để đo routing, citation, abstention và framework application.
- Primary deliverable: **book knowledge evaluation**.

## Inputs and readiness

- Confirm objective, consumer, owner, target/environment, scope, constraints and acceptance criteria.
- Identify relevant systems, data, artifacts, dependencies, authority, evidence and tests.
- For controlled work, establish containment, backup, rollback or recovery before execution.

If an absent input changes semantics, risk, cost, scope or acceptance, classify it as blocking. Otherwise state a bounded assumption and record it.

## Deep execution contract

- Contract version: `3.0`.
- Criticality: `deep`; treat this as a low-freedom protocol for **book knowledge evaluation**.

Mandatory domain inputs:
- Source files, editions and rights.
- Conversion purpose and destinations.
- Content type and structure.
- Token and quality budget.

Invariants that must remain true:
- Named frameworks preserve author precision.
- Quotations stay bounded.
- Derived claims trace to locations.
- Destination packs distinguish author view, synthesis and user application.

Decision and execution sequence:
1. Inventory and fingerprint.
2. Extract and verify structure.
3. Distill frameworks and decisions.
4. Compile destination packs.
5. Test retrieval and application.
6. Scan rights, security and version.

Required proof:
- Source manifest.
- Chapter and locator coverage.
- Framework citation audit.
- Destination validation.
- Retrieval/application results and copyright decision.

Block before mutation or a positive completion decision when a mandatory input, authority, invariant, recovery path or proof source is unresolved. Preserve the failed state and route remediation explicitly; never weaken a test or threshold merely to pass.


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


## Tests and evidence

- Source edition/hash, extraction coverage and framework-to-locator traceability.
- Copyright, quotation, prompt-injection, broken-link and hallucinated-framework audit.
- Unseen retrieval and changed-scenario application test for the selected destination.

Also verify scope and acceptance criteria, test relevant edge/failure paths, store evidence and keep failed mandatory checks visible. Use independent critical acceptance testing when practical.

## Approval and done

Explicit approval is normally not required for read-only work, but becomes mandatory if scope expands to a governed or mutating action. Approval is version- and scope-specific and never waives testing. Finish only when the deliverable meets acceptance criteria, mandatory tests pass, required approval exists, residual risks have owners, and handoff/monitoring is explicit. Stop as `blocked` or `failed` on missing authority, material ambiguity, failed validation or unsafe recovery; never fabricate success.

## Return

Return the task ID, lifecycle profile, risk tier, execution path, phase reached, primary deliverable, evidence links, test results, approvals, assumptions, open risks, affected assets, owner and one explicit next task. Route cross-role work through the department orchestrator.

Report it in the compact shape from [response compression](../response-compression.md): one state line, the deliverable, only the fields that carry content, then one next action. Blocked gates, unrun checks, assumptions, limitations and residual risks are printed in full even here.

Mirror the outcome into `../../assets/atomic-task-output.yaml` alongside the prose. Where the prose and the structured record disagree, the record stands and the task is not complete.
