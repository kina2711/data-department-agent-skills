# brain-retire-stale-knowledge

## Trigger

Use when the user asks to retire stale knowledge, requests the stated deliverable, or supplies an artifact that requires this atomic workflow. Do not select by job title alone.

## Contract

- Profile: `production-release`
- Risk tier: `R4-critical`
- Execution path: `controlled-path`
- Contract version: `3.0`
- Criticality: `enforced`
- Model tier: `strong` per [model selection](../model-selection.md); a lighter model never lowers the bar this output must clear.
- Goal: deprecate hoặc archive note/source/output với reason, successor, retention và backlink repair.
- Primary deliverable: **knowledge retirement record**.

## Inputs and readiness

- Confirm objective, consumer, owner, target/environment, scope, constraints and acceptance criteria.
- Identify relevant systems, data, artifacts, dependencies, authority, evidence and tests.
- For controlled work, establish containment, backup, rollback or recovery before execution.

If an absent input changes semantics, risk, cost, scope or acceptance, classify it as blocking. Otherwise state a bounded assumption and record it.

## Deep execution contract

- Contract version: `3.0`.
- Criticality: `enforced`; treat this as a low-freedom protocol for **knowledge retirement record**.

Mandatory domain inputs:
- Brain purpose and users.
- Source inventory and rights.
- Privacy boundary.
- Target outputs and retrieval questions.

Invariants that must remain true:
- 1_nguon remains immutable evidence.
- Wiki separates fact/inference.
- 3_toi never masquerades as source fact.
- Every material output traces to source and personal-rule versions.

Decision and execution sequence:
1. Assess current system.
2. Design four layers.
3. Ingest and fingerprint.
4. Distill and link.
5. Retrieve minimum context.
6. Generate and verify output.
7. Review freshness and reuse.

Required proof:
- Source manifest and hashes.
- Note-to-source links.
- Retrieval test set.
- Output claim lineage.
- Privacy, freshness and restore evidence.

Block before mutation or a positive completion decision when a mandatory input, authority, invariant, recovery path or proof source is unresolved. Preserve the failed state and route remediation explicitly; never weaken a test or threshold merely to pass.


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
- Read [the Second Brain quality and safety standard](../second-brain-quality-and-safety.md); run `../../scripts/validate_second_brain.py` when a vault manifest is available.
- Read [the Workflow Runtime and Evidence OS](../workflow-runtime-and-evidence-os.md); validate workflow, evidence and version-bound approvals instead of relying on narrative gate claims.
- Read [the execution discipline standard](../execution-discipline-standard.md).
- Before Git-backed mutation, require a verified success contract and pre-change scope contract. After the final change, run `core-audit-change-scope` and `core-verify-deliverable`; release remains blocked if either control is absent or failed.
- Bind final human approval to the scope-audit `final_diff_sha256`, then rerun the audit immediately before release with that expected fingerprint. Any mismatch invalidates approval and blocks release.


## Tests and evidence

- Layer, stable-ID, source-hash, rights and note-to-source lineage validation.
- Representative retrieval, freshness, citation, forbidden-source and abstention evaluation.
- Privacy, prompt-injection, output-grounding, backup or lifecycle check as applicable.

Also verify scope and acceptance criteria, test relevant edge/failure paths, store evidence and keep failed mandatory checks visible. Use independent critical acceptance testing when practical.

## Approval and done

Require explicit, scoped, version-specific human approval before execution and preserve rollback authority. Approval is version- and scope-specific and never waives testing. Finish only when the deliverable meets acceptance criteria, mandatory tests pass, required approval exists, residual risks have owners, and handoff/monitoring is explicit. Stop as `blocked` or `failed` on missing authority, material ambiguity, failed validation or unsafe recovery; never fabricate success.

## Return

Return the task ID, lifecycle profile, risk tier, execution path, phase reached, primary deliverable, evidence links, test results, approvals, assumptions, open risks, affected assets, owner and one explicit next task. Route cross-role work through the department orchestrator.

Return the full contract; [response compression](../response-compression.md) governs wording, never coverage. Never soften `blocked` or `failed`, and never report an unrun check as a pass.

Mirror the outcome into `../../assets/atomic-task-output.yaml` alongside the prose. Where the prose and the structured record disagree, the record stands and the task is not complete.
