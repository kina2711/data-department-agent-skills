# brain-run-knowledge-review-cycle

## Trigger

Use when the user asks to run knowledge review cycle, requests the stated deliverable, or supplies an artifact that requires this atomic workflow. Do not select by job title alone.

## Contract

- Profile: `advisory-analysis`
- Risk tier: `R0-light`
- Execution path: `fast-path`
- Contract version: `3.0`
- Criticality: `standard`
- Goal: review inbox, orphans, conflicts, stale notes, personal rules, outputs và improvement actions theo cadence.
- Primary deliverable: **knowledge review record**.

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
- Read [the Second Brain operating system](../second-brain-operating-system.md); preserve the four-layer boundary and stable source identity.
- Reuse only the matching manifest, source, Wiki-note, personal-context, output, migration or evaluation asset from `../../assets/`.
- Read [the migration and tool-interoperability standard](../migration-and-tool-interop.md); export first, preserve originals and validate representative retrieval before cutover.
- Run `../../scripts/build_brain_index.py` for a privacy-minimized path/hash/title/ID inventory; it intentionally excludes note bodies and likely secret files.


## Tests and evidence

- Layer, stable-ID, source-hash, rights and note-to-source lineage validation.
- Representative retrieval, freshness, citation, forbidden-source and abstention evaluation.
- Privacy, prompt-injection, output-grounding, backup or lifecycle check as applicable.

Also verify scope and acceptance criteria, test relevant edge/failure paths, store evidence and keep failed mandatory checks visible. Use independent critical acceptance testing when practical.

## Approval and done

Explicit approval is normally not required for read-only work, but becomes mandatory if scope expands to a governed or mutating action. Approval is version- and scope-specific and never waives testing. Finish only when the deliverable meets acceptance criteria, mandatory tests pass, required approval exists, residual risks have owners, and handoff/monitoring is explicit. Stop as `blocked` or `failed` on missing authority, material ambiguity, failed validation or unsafe recovery; never fabricate success.

## Return

Return the task ID, lifecycle profile, risk tier, execution path, phase reached, primary deliverable, evidence links, test results, approvals, assumptions, open risks, affected assets, owner and one explicit next task. Route cross-role work through the department orchestrator.
