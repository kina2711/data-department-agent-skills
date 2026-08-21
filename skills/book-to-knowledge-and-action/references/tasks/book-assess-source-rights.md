# book-assess-source-rights

## Trigger

Use when the user asks to assess source rights, requests the stated deliverable, or supplies an artifact that requires this atomic workflow. Do not select by job title alone.

## Contract

- Profile: `advisory-analysis`
- Risk tier: `R0-light`
- Execution path: `fast-path`
- Contract version: `3.0`
- Criticality: `standard`
- Goal: kiểm tra ownership, license, edition, quotation, processing, storage và publication rights trước conversion.
- Primary deliverable: **source-rights decision**.

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
- Read [the Book-to-Knowledge operating system](../book-conversion-operating-system.md); extract actionable structure rather than chapter recap.
- Reuse only the matching source-manifest, framework-card, chapter-note, destination-plan, experiment or evidence asset from `../../assets/`.
- Read [the source extraction and structure standard](../source-extraction-and-structure.md); fingerprint editions, retain locators and verify representative boundaries/artifacts.
- Read [the copyright, security and quality standard](../copyright-security-and-quality.md); run `../../scripts/validate_book_conversion.py` when a conversion manifest is available.
- Preflight or extract supported local files with `../../scripts/extract_book_sources.py`; it never auto-installs dependencies or uploads source material, and technical-mode output still requires structure sampling.


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
