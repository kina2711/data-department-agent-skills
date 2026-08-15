# Claude-native validation

Date: 2026-08-14

## Static and package validation

- `tools/validate_claude_skills.py`: 32 Claude skills, 809 atomic workflows, zero errors.
- `tools/validate_suite.py`: 32 skills, 809 task files, 809 task links, zero errors.
- `tools/run_smoke_tests.py`: 35 routing cases, 37 confusion-pair cases, 13 lifecycle cases, 41 catalog-routing cases, Workflow/Evidence OS, content-manifest, personal-project, Second Brain, Book-to-Knowledge and Learning Memory regressions, zero errors.
- `tools/run_benchmark_tests.py`: 34 deterministic adapter/control tests passed, including SQL/data-contract checks, bounded context, strict scope validation, repository/context/stack detection, portfolio/telemetry proof, privacy-minimized brain indexing, four-layer validation, book conversion gates, mastery-evidence rejection, invalid-memory blocking and Airflow-to-dbt context compression/decay/version-shift behavior.
- `claude plugin validate --strict`: passed on the staged plugin.
- Project/plugin stage audit: 32 `SKILL.md`, 809 task contracts and zero `agents/openai.yaml` files.
- Claude plugin ZIP audit: one plugin manifest, 32 skills, 809 task contracts, no root `CLAUDE.md`, no Python cache and no cross-client UI metadata.
- Deterministic source build, generated documentation and strict native plugin validation all passed for v3.2.0.

## Native Claude Code invocation

The current staged v3.2.0 plugin passed `claude plugin validate --strict` with 32 skills. A prior native invocation loaded the staged v2.3.0 plugin with `claude --plugin-dir` and invoked `/data-department-agent-skills:data-engineering` for a read-only Spark execution-plan diagnosis.

Claude selected:

- Task: `de-analyze-execution-plan`
- Lifecycle: `advisory-analysis`
- Risk: `R0-light`
- Path: `fast-path`

Result: pass. Claude refused to infer a bottleneck from operator names alone and requested the actual plan, provenance and workload metrics. Plugin discovery, namespace invocation and atomic-task routing worked in Claude Code 2.1.206.

## Token optimization audit

Measured with `claude --plugin-dir <stage> plugin details data-department-agent-skills` and a local progressive-loading audit:

- Always-on discovery remains compact: 940 words / 7,482 characters across all 32 skill descriptions, roughly 1,900 tokens before client/plugin framing overhead.
- Role `SKILL.md` entrypoints range from 321 to 557 words; only the selected role entrypoint is loaded.
- Conservative largest sharded path (`SKILL.md` + one catalog + one task contract + Workflow/Evidence OS + one stack adapter) is 2,043 words. Most paths omit the runtime or adapter and are smaller.
- Atomic task contracts: 361,388 whitespace-delimited words across 809 files, maximum 692 words per file; they remain sharded and are never loaded together.
- Task discovery is sharded into `plan-design`, `build-deliver`, `test-assure` and `operate-improve`; Claude reads one matching catalog by default.
- Catalog shards max at 265 words; 98 role-scoped stack adapters range from 112 to 169 words. Runtime, adapter and specialist references remain conditional, so unrelated material is not injected.

A native post-optimization invocation read only `catalog-plan-design.md`, selected `de-design-ingestion-pipeline`, preserved `design-specification / R2-standard / standard-path`, and correctly reported that no approval had been granted.

A prior v2.2.0 native invocation of `/data-department-agent-skills:data-career-and-interview-coach` for exactly one RTM interview question selected `career-build-question-deep-dive` with the primary deliverable `complete interview-question dossier`. It did not route to the multi-dossier knowledge-library task.

## v3.2.0 Cross-skill Learning Memory

- Added seven Career workflows for memory initialization, prerequisite mapping, bounded transition context, append-only learning events, mastery assessment, decay detection and conflict reconciliation; the catalog now contains 809 tasks: 94 `enforced`, 163 `deep` and 552 `standard`.
- Every role skill routes to a compact learner-memory interoperability contract. Career remains the sole mastery-state authority; technical roles are read-only consumers and never infer mastery from chat history, course attendance or an unverified note.
- `learner-memory.schema.json` separates topic state, confidence, evidence, transfer scope, freshness, source version, limitations and append-only events. `mastered` requires level ≥ 4, confidence ≥ 0.7, verified applied evidence, verified changed-scenario transfer, compact summary and demonstration/review dates.
- `build_skill_transition_context.py` validates the canonical memory before use and creates a token-bounded pack. Fresh mastered indirect topics become one-line reuse records; direct prerequisites become bridge summaries with interfaces, decision rules and failure modes; stale, uncertain, explicitly version-shifted or safety-critical topics move to `expand_or_retest`. An over-budget required pack is blocked rather than consumed.
- Deterministic tests prove the Airflow → dbt case does not reteach Airflow, does not leak full evidence descriptions, stays within budget and reopens Airflow when the review date has expired.

## v3.1.0 Second Brain and Book-to-Knowledge

- Added `personal-second-brain-and-knowledge-os` with 46 workflows and `book-to-knowledge-and-action` with 45 workflows; total catalog is 802 tasks: 94 `enforced`, 161 `deep` and 547 `standard`.
- The Second Brain validator enforces the exact four layers, root-contained paths, stable IDs, registry counts, source references, SHA-256, passed retrieval tests and verified backup/restore evidence. Its indexer emits metadata/headings/IDs only and excludes likely secret files.
- Book conversion supports analyze/full/fold-in/update; source extraction for PDF, EPUB, DOCX, HTML, Markdown/text and bounded RTF; source/corpus hashes; structure/framework locators; eight destinations; rights, copyright, security, retrieval, token-path and application gates.
- Deterministic positive and adversarial fixtures passed for both systems. Invalid source IDs, count drift, failed retrieval, unresolved rights, failed extraction, absent framework traceability, draft artifacts and failed tests are rejected.
- Routing tests distinguish personal/local knowledge from governed company context, and source conversion from downstream Academy, Career and Technical Content ownership.

## v3.0.0 Depth and Enforcement

- Task count remains 711: 88 contracts are `enforced`, 131 are `deep` and 492 are `standard`; the upgrade adds domain invariants and proof instead of catalog inflation.
- Workflow Runtime rejects dependency cycles, execution before prerequisites, risk downgrade, unresolved evidence, missing controlled approvals and false completion.
- Evidence OS verifies artifact-root containment and SHA-256 and distinguishes implemented, tested, approved, released and complete.
- Twelve canonical stack adapters generate 98 role-scoped packs, each directly routed from the owning SKILL for progressive loading.
- Read-only repository audit returned all 12 required dimensions; context bootstrap omitted content values; stack detection found Airflow/dbt from evidence; strict portfolio proof resolved one artifact and claim and rejected empty plans.
- Thirty-two confusion-pair fixtures cover DA/BA, DA/Product Analytics, DE/AE, DE/Platform, Architecture/Platform, Governance/Metadata, DQ/DE, DS/MLE, MLE/MLOps, Academy/Career, Hiring/Career, Project/Orchestrator and related boundaries.
- Fresh-agent forward tests passed for Airflow engineering review and repo-first personal-project assessment. The first workflow-runtime pass exposed non-canonical instance IDs and skipped read-only plan validation; v3 now makes compose/maintain/resume/completion tasks `enforced`, reserves `task_id` for exact catalog IDs, constrains claim status and requires temporary deterministic validation even in read-only planning.

## v2.7.0 Personal Project Discovery & Build OS

- Added `data-personal-project-engineering` with 42 workflows and 20 starting modes, while retaining legacy orchestrator tasks for organizational cross-role initiatives.
- Repo-first requires exact source/version/license evidence, an evidence-state-aware audit across 12 dimensions, safe baseline honesty and a `reuse/adapt/replace/drop/build-new` matrix.
- External repositories and ideas become attributed user-owned project theses. Complete-mode validation rejects false `self-originated` claims and normally requires at least three substantive differentiation axes.
- Deterministic regressions cover project option scoring, valid repo-first manifests and adversarial renamed-clone manifests.
- The role entrypoint is 484 words / 3,948 characters; task discovery and the three specialist references remain progressively loaded.
- An independent read-only test against `C:\PROJECT\i-learn-airflow` passed all routing, provenance, 12-dimension audit, baseline-honesty, transformation, differentiation, roadmap and portfolio-proof checks. See `FORWARD_TEST_PERSONAL_PROJECT_V2_7.md`.

## v2.5.0 Career OS and Technical Content controls

- Added 14 `career-development` and retained 25 interview-specific `career-coaching` tasks, eliminating interview-simulation boilerplate from career-system work.
- Added a 26-task Technical Content role covering research, version verification, knowledge maps, series architecture, canonical articles, code, diagram handoffs, Facebook, LinkedIn, Substack, repository packaging, five independent quality dimensions, publishing and measurement.
- The content role entrypoint is 474 words; its largest catalog is 101 words and largest task contract is 483 words. Only the selected lifecycle and one or two specialist references load, so the 26 tasks and all platform playbooks are not injected together.
- `validate_content_manifest.py` has explicit `plan`, default `complete` and `release` modes. Complete/release bind claims to excerpts in hashed evidence snapshots, require runtime evidence for benchmark/scale/production claims, real artifacts and hashes, independent reviews, standardized test scopes, canonical-before-derived approval and exact-channel authority.
- Three fresh-agent pressure tests initially exposed bundle-routing, template, JSON emission, evidence-resolution, review/test and publication-authority gaps. After iterative correction, Career OS, Airflow series and adversarial dbt tests passed with no material residual. See `FORWARD_TEST_CAREER_CONTENT_V2_5.md`.

## v2.4.0 discipline and dashboard controls

- New task boundaries: `core-define-success-contract`, `core-audit-change-scope`, `bi-audit-dashboard-experience` and `bi-redesign-dashboard-experience`.
- New deterministic control: `audit_change_scope.py` passed an allowed single-file change and failed a drive-by documentation edit under the same Git scope contract.
- New conditional resources: evidence-driven work paths, one-hypothesis debugging, two-pass review, fresh claim verification, dashboard preflight, truthful metric content and responsive/accessibility gates.
- New state schemas: success contract, change scope, debug hypothesis, verification claims, compact work ledger and dashboard experience audit.
- Upstream patterns were adapted to the suite's R0-R4 lifecycle rather than imposing universal code-only TDD or mandatory approval on every advisory task.
- Three fresh-agent pressure tests initially exposed routing, coverage, contract, rename/deletion, final-diff and BI handoff loopholes. After two refactor/retest cycles, implicit repo-first routing, scope/release enforcement and BI audit/redesign all passed with no material residuals. See `FORWARD_TEST_EXECUTION_DISCIPLINE_V2_4.md`.

## v2.3.0 benchmark forward tests

Fresh-agent tests received only the user request and the skill artifact:

- Data Analysis selected `da-explain-sql-business-logic`, separated physical and derived sources, established customer grain, challenged duplicate/null/time/currency semantics and ran an independent SQLite edge-case check.
- Data Developer Experience selected `dx-trace-data-path-end-to-end`, predicted the context-package sections before execution, reconciled ordered headings and source hashes, then tested the required-context-over-budget failure path.
- Data Engineering selected `de-analyze-execution-plan`, treated the two exchanges and sort-merge join as a falsifiable hypothesis rather than proof, challenged non-final AQE state and query-to-plan provenance, and designed a correctness-preserving benchmark.

The first Data Analysis pass exposed a CTE boundary error in the deterministic SQL helper. The parser was changed to track quote and parenthesis depth; a fresh retest extracted `status = 'paid'` without leaking the outer query, and a join regression fixture now verifies join source, alias, condition, filter and group scope.

## Interview knowledge-system forward tests

Fresh-agent tests covered the earlier interview routing boundaries and deliverables:

- One RTM interview question selected `career-build-question-deep-dive`, produced analysis, answer strategy, authentic or explicitly hypothetical evidence, knowledge deep dive, related concepts and a novel retest. It did not select the multi-dossier library task.
- A multi-entry, linked, versioned, Notion-ready request selected `enable-build-versioned-knowledge-library`; standalone article creation was rejected and publication remained a downstream reviewed handoff.
- A Senior BA/Data Governance RTM assessment selected `talent-map-question-to-competency-evidence` and produced role-outcome traceability, observable evidence anchors, standardized probes, critical failures, validity controls and answer-leakage protections.

The first interview forward-test pass exposed two routing ambiguities: single-question versus library, and standalone article versus linked/versioned library. Explicit decision boundaries were added to the affected `SKILL.md` generators; targeted retests passed.
