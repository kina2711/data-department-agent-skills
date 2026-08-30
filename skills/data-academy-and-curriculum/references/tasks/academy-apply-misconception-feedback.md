# academy-apply-misconception-feedback

## Trigger

Use when the user asks to apply misconception feedback, requests the stated deliverable, or supplies an artifact that requires this atomic workflow. Do not select by job title alone.

## Contract

- Profile: `learning`
- Risk tier: `R1-reviewed`
- Execution path: `standard-path`
- Contract version: `3.0`
- Criticality: `standard`
- Model tier: `standard` per [model selection](../model-selection.md); a lighter model never lowers the bar this output must clear.
- Goal: gom ngộ nhận lặp lại theo concept key rồi bổ sung vào chính note dạy sai mô hình đó.
- Primary deliverable: **revised note batch**.

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
- Read [role curricula](../role-curricula.md) and [assessment rules](../assessment-and-certification.md).
- Reuse the applicable curriculum, lesson, assessment or evidence template from `../../assets/`.
- Read [the note-corpus operating system](../note-corpus-operating-system.md); the stages run in one direction, and `note-corpus-manifest.json` is the resume anchor rather than something to re-derive each session.
- Read [the canonical concept registry](../concept-registry-standard.md); bind every note, module and scenario to a `ck.` key, coining it as `proposed` when none fits, and claim exactly one primary note per key. Only `registered` keys count toward coverage, so never report a corpus built on proposed keys as covered.
- Reuse the role-roadmap, skill-track-map, note-corpus-manifest or note-corpus-audit asset from `../../assets/` that matches this stage.
- Read [the diagnostic session method](../diagnostic-session-method.md); the same misconception against one concept key in three or more distinct sessions is the threshold, and one observation is noise.
- Reuse `../../assets/misconception-feedback.yaml`. The edit is append-only: add the entry to the note's misconception section, set `status` to `needs-review` and `updated` to today, and never rewrite, reorder or delete existing content on the strength of a pattern drawn from one learner.
- Verify the corpus is under version control or backed up before editing, and record each edit with the sessions that justified it so it can be read back and reverted. Report rather than edit a note whose primary key is unregistered or whose status is not `reviewed`.

- Certification proves only the named, versioned competencies demonstrated by evidence; it never proves tenure, job title, automatic promotion or general seniority.
- Upgrade to R3-controlled and require People/HR plus accountable business approval when certification affects employment, promotion, compensation, regulation or external claims.
- For a curriculum bundle, select one primary artifact and chain `academy-write-theory-lesson` → `academy-design-hands-on-lab` → `academy-design-summative-exam` → `academy-write-answer-key` → `academy-write-assessment-rubric` → `academy-calibrate-assessors` → `academy-certify-role-competency` → `academy-measure-training-effectiveness` as applicable.

## Tests and evidence

- Authoritative-source and domain-review verification.
- Prerequisite, graph-cycle, misconception and coverage checks.
- Novel-scenario application and learning-transfer test.

Also verify scope and acceptance criteria, test relevant edge/failure paths, store evidence and keep failed mandatory checks visible. Use independent critical acceptance testing when practical.

## Approval and done

Require named reviewer acceptance before the artifact becomes an organizational baseline. Approval is version- and scope-specific and never waives testing. Finish only when the deliverable meets acceptance criteria, mandatory tests pass, required approval exists, residual risks have owners, and handoff/monitoring is explicit. Stop as `blocked` or `failed` on missing authority, material ambiguity, failed validation or unsafe recovery; never fabricate success.

## Return

Return the task ID, lifecycle profile, risk tier, execution path, phase reached, primary deliverable, evidence links, test results, approvals, assumptions, open risks, affected assets, owner and one explicit next task. Route cross-role work through the department orchestrator.

Report it in the compact shape from [response compression](../response-compression.md): one state line, the deliverable, only the fields that carry content, then one next action. Blocked gates, unrun checks, assumptions, limitations and residual risks are printed in full even here.
