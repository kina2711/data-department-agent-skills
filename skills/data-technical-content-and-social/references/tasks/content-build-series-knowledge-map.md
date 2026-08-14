# content-build-series-knowledge-map

## Trigger

Use when the user asks to build series knowledge map, requests the stated deliverable, or supplies an artifact that requires this atomic workflow. Do not select by job title alone.

## Contract

- Profile: `build-change`
- Risk tier: `R1-reviewed`
- Execution path: `standard-path`
- Contract version: `3.0`
- Criticality: `deep`
- Goal: nối prerequisites, core concepts, mechanisms, contrasts, failure modes và follow-on topics.
- Primary deliverable: **series knowledge map**.

## Inputs and readiness

- Confirm objective, consumer, owner, target/environment, scope, constraints and acceptance criteria.
- Identify relevant systems, data, artifacts, dependencies, authority, evidence and tests.
- For controlled work, establish containment, backup, rollback or recovery before execution.

If an absent input changes semantics, risk, cost, scope or acceptance, classify it as blocking. Otherwise state a bounded assumption and record it.

## Deep execution contract

- Contract version: `3.0`.
- Criticality: `deep`; treat this as a low-freedom protocol for **series knowledge map**.

Mandatory domain inputs:
- Audience and capability journey.
- Canonical sources/runtime evidence.
- Channel/language/rights constraints.

Invariants that must remain true:
- Canonical evidence precedes social variants.
- Claims and media remain traceable.
- Experience/benchmarks are not invented.

Decision and execution sequence:
1. Research/version.
2. Build canonical artifact/code/diagram.
3. Validate.
4. Adapt by channel.
5. Review voice/platform.
6. Approve and measure.

Required proof:
- Source/claim manifest.
- Code/media hashes.
- Technical/editorial/platform reviews and publication authority.

Block before mutation or a positive completion decision when a mandatory input, authority, invariant, recovery path or proof source is unresolved. Preserve the failed state and route remediation explicitly; never weaken a test or threshold merely to pass.


## Procedure

1. Read [the lifecycle standard](../lifecycle-standard.md); apply its stages, gates and risk-adaptive path.
2. Load only applicable company context, then inspect live artifacts when facts may have changed.
3. Load technology or industry references only when they affect this deliverable.
4. Execute the stated goal; keep one primary deliverable and record provenance for material facts.
5. Run the tests below, resolve failures, obtain required approval and complete the lifecycle handoff.

Additional resources:
- Read [the universal professional-series rules](../universal-professional-series-rules.md) for the capability journey, teaching contract, human voice, REAL/ILLUSTRATION/CODE asset contract and non-publication gates.
- Read [the technical-series method](../technical-series-method.md) and reuse the series-plan, episode-brief or editorial-calendar asset that matches the deliverable.
- Reuse only the matching template from `../../assets/`; run `../../scripts/validate_content_manifest.py` when a content manifest is available.
- Read [the execution discipline standard](../execution-discipline-standard.md).
- Before Git-backed mutation, require a verified success contract and pre-change scope contract. After the final change, run `core-audit-change-scope` and `core-verify-deliverable`; release remains blocked if either control is absent or failed.


## Tests and evidence

- Material claim-to-source, runtime evidence or explicit opinion/hypothesis traceability.
- Version, code, diagram, failure-path and limitation validation as applicable.
- Channel fit, accessibility, originality and cross-variant consistency review.

Also verify scope and acceptance criteria, test relevant edge/failure paths, store evidence and keep failed mandatory checks visible. Use independent critical acceptance testing when practical.

## Approval and done

Require named reviewer acceptance before the artifact becomes an organizational baseline. Approval is version- and scope-specific and never waives testing. Finish only when the deliverable meets acceptance criteria, mandatory tests pass, required approval exists, residual risks have owners, and handoff/monitoring is explicit. Stop as `blocked` or `failed` on missing authority, material ambiguity, failed validation or unsafe recovery; never fabricate success.

## Return

Return the task ID, lifecycle profile, risk tier, execution path, phase reached, primary deliverable, evidence links, test results, approvals, assumptions, open risks, affected assets, owner and one explicit next task. Route cross-role work through the department orchestrator.
