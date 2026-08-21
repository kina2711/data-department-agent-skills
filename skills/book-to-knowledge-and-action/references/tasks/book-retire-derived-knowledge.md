# book-retire-derived-knowledge

## Trigger

Use when the user asks to retire derived knowledge, requests the stated deliverable, or supplies an artifact that requires this atomic workflow. Do not select by job title alone.

## Contract

- Profile: `production-release`
- Risk tier: `R4-critical`
- Execution path: `controlled-path`
- Contract version: `3.0`
- Criticality: `enforced`
- Goal: deprecate stale framework hoặc generated pack với reason, successor, archive và backlink repair.
- Primary deliverable: **derived-knowledge retirement record**.

## Inputs and readiness

- Confirm objective, consumer, owner, target/environment, scope, constraints and acceptance criteria.
- Identify relevant systems, data, artifacts, dependencies, authority, evidence and tests.
- For controlled work, establish containment, backup, rollback or recovery before execution.

If an absent input changes semantics, risk, cost, scope or acceptance, classify it as blocking. Otherwise state a bounded assumption and record it.

## Deep execution contract

- Contract version: `3.0`.
- Criticality: `enforced`; treat this as a low-freedom protocol for **derived-knowledge retirement record**.

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
- Read [the Book-to-Knowledge operating system](../book-conversion-operating-system.md); extract actionable structure rather than chapter recap.
- Reuse only the matching source-manifest, framework-card, chapter-note, destination-plan, experiment or evidence asset from `../../assets/`.
- Read [the destination compiler and handoff standard](../destination-packs.md); the book skill owns conversion evidence while Career, Project, Academy, Content or Second Brain owns downstream operation.
- Read [the copyright, security and quality standard](../copyright-security-and-quality.md); run `../../scripts/validate_book_conversion.py` when a conversion manifest is available.
- Read [the Workflow Runtime and Evidence OS](../workflow-runtime-and-evidence-os.md); validate workflow, evidence and version-bound approvals instead of relying on narrative gate claims.
- Read [the execution discipline standard](../execution-discipline-standard.md).
- Before Git-backed mutation, require a verified success contract and pre-change scope contract. After the final change, run `core-audit-change-scope` and `core-verify-deliverable`; release remains blocked if either control is absent or failed.
- Bind final human approval to the scope-audit `final_diff_sha256`, then rerun the audit immediately before release with that expected fingerprint. Any mismatch invalidates approval and blocks release.


## Tests and evidence

- Source edition/hash, extraction coverage and framework-to-locator traceability.
- Copyright, quotation, prompt-injection, broken-link and hallucinated-framework audit.
- Unseen retrieval and changed-scenario application test for the selected destination.

Also verify scope and acceptance criteria, test relevant edge/failure paths, store evidence and keep failed mandatory checks visible. Use independent critical acceptance testing when practical.

## Approval and done

Require explicit, scoped, version-specific human approval before execution and preserve rollback authority. Approval is version- and scope-specific and never waives testing. Finish only when the deliverable meets acceptance criteria, mandatory tests pass, required approval exists, residual risks have owners, and handoff/monitoring is explicit. Stop as `blocked` or `failed` on missing authority, material ambiguity, failed validation or unsafe recovery; never fabricate success.

## Return

Return the task ID, lifecycle profile, risk tier, execution path, phase reached, primary deliverable, evidence links, test results, approvals, assumptions, open risks, affected assets, owner and one explicit next task. Route cross-role work through the department orchestrator.

Return the full contract; [response compression](../response-compression.md) governs wording, never coverage. Never soften `blocked` or `failed`, and never report an unrun check as a pass.

Mirror the outcome into `../../assets/atomic-task-output.yaml` alongside the prose. Where the prose and the structured record disagree, the record stands and the task is not complete.
