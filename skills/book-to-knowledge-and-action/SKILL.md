---
name: book-to-knowledge-and-action
description: Turn books, PDFs, EPUBs, documents or source collections into reusable agent skills, Second Brain packs, career/interview/project systems, curricula, workflows or technical content. Use when structure, frameworks, decisions, citations, copyright controls and progressive loading matter more than a summary.
---

# Book to Knowledge and Action

## Operating contract

1. Identify the requested deliverable, then select exactly one atomic task below.
2. Read that task file completely before acting.
3. Read [references/lifecycle-standard.md](references/lifecycle-standard.md) and use the task's profile, risk tier and execution path.
4. Load only the company context and adapter references needed for the selected task.
5. On a cross-role handoff, compare logical ID and SHA-256 in `references/shared-reference-manifest.json`; reuse an already loaded shared reference when both match instead of loading its duplicate.
6. Inspect real artifacts and systems before making change-sensitive claims.
7. Apply Definition of Ready, stage gates, test strategy, Definition of Done, approval and handoff requirements.
8. Do not invent access, approvals, successful execution, test results or business confirmation.
9. For any Git-backed mutation, regardless of the task's verb or profile, require a pre-change success/scope contract, a post-change `core-audit-change-scope`, and fresh `core-verify-deliverable` evidence before completion.
10. For learning, coaching or skill-transition work, resolve [the learner-memory interoperability contract](references/learning-memory-interoperability.md). Reuse only relevant verified summaries; never infer mastery from exposure, and expand stale, uncertain, changed-version or safety-critical prerequisites.

## Conversion routing

- One or more sources without a requested destination → select `book-classify-conversion-purpose`, then produce one primary destination plan.
- Claude-compatible reusable skill → `book-build-agent-skill` plus progressive chapter pack, traceability and validation tasks.
- Long-lived four-layer vault material → `book-build-second-brain-pack`, then hand off to `personal-second-brain-and-knowledge-os`.
- Career, interview, project, curriculum or technical-series application → select the matching destination compiler and hand off actual downstream operation to the owning role skill.
- New edition or added documents for an existing pack → `book-fold-into-existing-system` or `book-update-from-new-edition`; preserve prior IDs, evidence and conflicts.

The core pipeline is `source rights → fingerprint/extract → structure verification → frameworks/decisions → destination compiler → traceability/security scan → unseen retrieval/application test`. Do not call a chapter summary a skill, copy long passages, invent named frameworks, collapse multiple authors into one voice, or publish third-party/internal derived content without explicit rights and visibility authority.

This implementation adapts the structure-first, progressive-loading, analyze/full/update, cost-preflight and copyright-gate ideas from `virgiliojr94/book-to-skill` under MIT. It extends them with Second Brain, Career, Interview, Project, Academy and Content destination contracts, claim lineage, changed-scenario transfer tests and suite-native lifecycle/evidence controls.

Load only the relevant specialist reference: [conversion OS](references/book-conversion-operating-system.md), [extraction](references/source-extraction-and-structure.md), [distillation](references/knowledge-distillation-and-application.md), [destination packs](references/destination-packs.md), or [copyright/security/quality](references/copyright-security-and-quality.md).


## Atomic task routing

- **Plan, define, design, map, specify or create a proposed artifact** (1 task): read [references/catalog-plan-design.md](references/catalog-plan-design.md).
- **Build, implement, configure, teach, interview or deliver an artifact** (32 tasks): read [references/catalog-build-deliver.md](references/catalog-build-deliver.md).
- **Inspect, analyze, test, review, validate, assess, certify or audit** (8 tasks): read [references/catalog-test-assure.md](references/catalog-test-assure.md).
- **Deploy, release, monitor, recover, migrate, optimize, retire or improve** (4 tasks): read [references/catalog-operate-improve.md](references/catalog-operate-improve.md).

Read only the best-matching catalog. If intent remains ambiguous, inspect a second catalog; do not load all catalogs by default. Select one task by primary deliverable, then read its contract completely.

## Completion response

State the selected task ID, primary deliverable, evidence inspected, validation performed, approval status, residual risks and next owner. A draft or plan is not an executed production outcome.
