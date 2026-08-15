# Source Integration Audit

## Source

`C:/Users/Vmt/Downloads/skill`

Audit date: 2026-08-12

## Packages inspected

| Package | Inventory | Decision |
|---|---:|---|
| `data-os (1)` | 160 files, 153 Markdown files | Adopt selected control-plane, project, metadata, platform, standards and domain patterns |
| `data-project-agent-system` | 39 files, 27 Markdown files | Adopt project entry modes, layer contracts, repository analysis and project scaffolding concepts |
| `BI REPORT PLATFORM` | 3 ZIP packages and 1 DOCX guide | Adopt governed BI lifecycle, evidence/approval artifacts and platform adapters |
| `diagram-skills-package` | 107 files, 11 Claude skills | Adopt diagram-selection and diagram-generation tasks as a shared documentation role pack |

## Adopted additions

### New role packs

- `data-business-analysis`
- `metadata-engineering-and-catalog`
- `data-developer-experience`
- `data-documentation-and-diagrams`
- `data-enablement-and-knowledge`

### New control-plane capabilities

- Repo-first, idea-first and dataset-first project entry modes
- Sequential, parallel, conditional and fan-out/fan-in orchestration
- Persisted run state and workflow resume
- Question, assumption, conflict, approval and evidence ledgers
- Information-sufficiency and phase-gate enforcement

### BI lifecycle additions

- Adaptive discovery dialogue
- Information-sufficiency classification
- Business-domain brief
- Source-authority matrix
- Evidence ledger
- Reversible and idempotent cleaning plan
- Platform-neutral report specification
- Section-level approval
- Independent UAT
- Dashboard/report reconciliation
- Release approval and maintenance workflows

### Project engineering additions

- Repository audit and reverse engineering
- Project scaffolding and template selection
- Local environment bootstrap
- Synthetic datasets and deterministic fixtures
- Dependency, pre-commit and CI baselines
- Enterprise benchmark and production-readiness assessment

### Diagram capabilities

- Mermaid activity, ERD, sequence and state
- PlantUML use case and swimlane activity
- BPMN 2.0 process modeling
- D2 architecture, activity and ERD
- DBML schema and SQL handoff
- Diagram-selection and semantic-validation tasks

### Adapter layer

- Airflow, BigQuery, dbt, Spark, Docker and Kubernetes
- Terraform and Pulumi
- DataHub/OpenMetadata
- Power BI, Tableau, Superset, Metabase, Looker Studio and HTML/JavaScript
- Mermaid, PlantUML, BPMN, D2 and DBML

### Knowledge packs

- Automotive, Ecommerce, EdTech, Energy and FinTech
- Gaming, Healthcare, Logistics and Manufacturing
- Media/Entertainment, Real Estate, Retail and SaaS B2B
- Telecom and Travel/Hospitality
- Core, Finance, Sales, Marketing, Product, Retention, SaaS, Operations and People metrics

## Merged rather than duplicated

| Source capability | Existing target |
|---|---|
| Data Analyst, Analytics Engineer, Data Engineer | Existing role packs; only missing atomic tasks are added |
| Data Governance | Existing DG role; catalog implementation moved to Metadata role |
| Architecture review | Existing Architect review tasks |
| SQL/Python/dbt review | Existing role review plus Data Developer Experience quality gates |
| Data profiling | Shared core, DA, DS and DQ tasks retain distinct deliverables |
| BI semantic model | Existing BI/AE tasks; added platform-neutral contract and evidence lifecycle |
| Monitoring and alerting | Existing Platform/DRE/MLOps tasks |
| FinOps | Existing Platform and ML cost-optimization tasks |

## Intentionally not imported into the Data Department core

- Generic job hunting, salary negotiation and self-promotion automation. Evidence-based career development, ethical professional visibility and technical publishing are now retained under explicit Career and Technical Content owners.
- General marketing/sales automation unrelated to data delivery.
- Generic company performance-review workflows outside data-team enablement.
- Duplicate README, installation guides and changelogs as skill runtime content.
- Tool-specific capabilities as new business tasks; they remain adapters.

## Safety changes required before reuse

- Do not use public PlantUML rendering for sensitive architecture, PII or confidential process names. Prefer local rendering; otherwise require explicit approval and sanitization.
- Do not trust generated BPMN, DBML, PBIR/TMDL or infrastructure artifacts without compilation/schema validation.
- Do not let capabilities call each other directly. Route through the department orchestrator so state, evidence, approvals and handoffs remain auditable.
- Do not copy bundled skills unchanged: normalize frontmatter to the target Claude Agent Skills format and remove nonportable absolute paths.
- Keep role `SKILL.md` concise and load task/tool/domain details progressively.

## Result

The canonical taxonomy is maintained in `DATA_DEPARTMENT_SKILL_MAP.md`. The imported sources are treated as design references and reusable assets, not as the canonical taxonomy.

## External benchmark — 2026-08-13

This release also benchmarked the suite against:

- [`nimrodfisher/data-analytics-skills`](https://github.com/nimrodfisher/data-analytics-skills): atomic analytics workflows, minimum viable context, assumptions log, peer review, retrospective, SQL-to-business explanation and context packaging.
- [`borghei/Claude-Skills` data analytics guidance](https://github.com/borghei/Claude-Skills/blob/main/data-analytics/CLAUDE.md): deterministic local scripts, JSON and human-readable outputs, explicit exit codes and progressive references.
- [`borghei/Claude-Skills` Senior Data Engineer skill](https://github.com/borghei/Claude-Skills/blob/main/engineering/senior-data-engineer/SKILL.md): plan-aware pipeline diagnosis, batch/stream adapters, schema drift, watermarks, DLQ and bounded clarification.
- [Agensi's data-engineering skills article](https://www.agensi.io/learn/best-claude-code-skills-data-engineering): stack-specific SQL conventions, execution-plan inspection, layered ETL and validation at input, transformation, output and monitoring.
- [The referenced Claude Code community discussion](https://www.reddit.com/r/ClaudeCode/comments/1s4pk8i/claude_code_for_data_engineering_data_science/): plan first, persist business/schema/lineage context, trace one real data path and compare predicted with observed behavior before claiming repository understanding.

### Additions accepted

| Gap | Canonical task or resource |
|---|---|
| One-task context bundle with token budget | `core-build-task-context-package`, `build_context_package.py` |
| Persistent context source/routing inventory | `ctx-build-context-index`, `context-index.yaml` |
| Evidence-based one-path repository learning | `dx-trace-data-path-end-to-end`, `data-path-trace.yaml` |
| Plan-first SQL/Spark diagnosis | `de-analyze-execution-plan`, `inspect_execution_plan.py` |
| Reproducible dataset profiling before analysis | `da-run-programmatic-eda`, `profile_dataset.py` |
| SQL-to-business translation | `da-explain-sql-business-logic`, `explain_sql.py` |
| Audience-calibrated method explanation | `da-explain-analysis-methodology` |
| Independent analytical delivery gate | `da-run-analysis-peer-review` |
| Post-delivery process learning | `da-run-analysis-retrospective` |
| Executable bounded contract checks | `validate_tabular_data.py` and stage-gated validation standard |

### Merged instead of duplicated

Existing planning, assumptions, query validation, metric reconciliation, cohort/funnel/segmentation, visualization, executive summary, stakeholder requirements, impact estimation and pipeline design remain under their current canonical owners. External names were not promoted to additional top-level skills because their primary deliverables already exist in the 28-role taxonomy.

### Intellectual-property and evidence boundary

The external repositories and article were used to identify behavior patterns and evaluation gaps. New task contracts, references, assets and scripts were independently authored for this suite; no third-party code or prose is vendored. Community comments are treated as practitioner hypotheses to test, not authoritative standards.

## External benchmark — 2026-08-14

Release 2.4.0 additionally evaluated three skill systems:

- [`obra/superpowers`](https://github.com/obra/superpowers): composable delivery lifecycle, bounded plans, root-cause-first debugging, test-first behavior changes, two-pass review, persistent execution state and fresh verification before completion claims.
- [`multica-ai/andrej-karpathy-skills`](https://github.com/multica-ai/andrej-karpathy-skills): explicit assumptions, simplicity, minimal sufficient solutions, surgical edits and goal-to-check execution loops.
- [`Nutlope/hallmark`](https://github.com/Nutlope/hallmark): project preflight, explicit audit/redesign/build modes, truthful content, structural anti-repetition, design-token discipline and pre-emit/post-emit quality gates.

### Additions accepted

| Gap | Canonical task, control or resource |
|---|---|
| Vague outcomes without executable done criteria | `core-define-success-contract`, `success-contract.yaml` |
| Drive-by edits and untraceable repository changes | `core-audit-change-scope`, `change-scope-ledger.yaml`, `audit_change_scope.py` |
| Speculative multi-fix debugging | `execution-discipline-standard.md`, `debug-hypothesis-ledger.yaml` |
| Completion language stronger than evidence | claim-to-evidence rules and `verification-claims.yaml` |
| Resume after long execution or context compaction | compact `work-ledger.yaml` |
| Generic or misleading dashboard experiences | `bi-audit-dashboard-experience`, `bi-redesign-dashboard-experience`, `dashboard-experience-quality.md` and audit template |

### Adapted rather than copied

- Universal code TDD was adapted to artifact-appropriate evidence cycles. Executable behavior uses fail/pass tests; analysis, governance, learning and design use a failing example or rubric finding followed by independent re-evaluation.
- Hard design approval before every change was not imported. Existing R0-R4 risk tiers determine approval strength; small read-only work remains fast while production, sensitive and destructive work stays controlled.
- Hallmark's website-specific fonts, page themes and component recipes were not imported. Its preflight, honesty, hierarchy, specificity, restraint, accessibility and anti-template principles were translated to governed BI dashboards.
- Existing troubleshooting, verification, orchestration and UAT tasks were strengthened instead of being duplicated under third-party names.

### Intellectual-property and license boundary

The repositories were inspected as behavioral benchmarks. This suite contains independently authored data-domain contracts, references, schemas, tests and code. No upstream source file or prose is vendored. Each upstream project's own repository remains the authority for its license and attribution terms.

## User-provided learning/content prompt benchmark — 2026-08-14

The 1,279-page local PDF `Prompt gen tài liệu học_dạy&content.pdf` was indexed and selectively inspected for career systems, technical writing, research/version controls, evidence policy, mastery rubrics, Facebook/LinkedIn formats, repository packaging and output contracts. The document did not contain a Substack playbook, so newsletter behavior was independently designed for this suite.

### Additions accepted

| Gap | Canonical task, resource or control |
|---|---|
| Career growth fragmented into interview preparation | Career OS, stage competency map, capstone, evidence portfolio, review cycle and claim audit tasks |
| Public visibility disconnected from real capability | `career-design-technical-writing-strategy`, `career-plan-ethical-professional-visibility`, career evidence policy |
| Social posts produced before technical proof | Canonical episode gate: research/version → article/code/diagram → accuracy/traceability tests → channel adaptation |
| Facebook and LinkedIn copied from one draft | Channel-native atomic tasks and `platform-format-playbooks.md` |
| Missing long-form newsletter channel | `content-write-substack-technical-newsletter` with subject/preheader, deep dive, exercise, references and version/correction note |
| Technical series as unordered topic lists | Knowledge map and narrative arc from why/mental model through mechanics, hands-on, failures, trade-offs and capstone |
| Unsupported claims and false completion | `content-manifest.json`, `validate_content_manifest.py`, independent accuracy/traceability/artifact/voice/platform gates |

### Channel language contract — v2.5.1

Facebook reader-facing prose is Vietnamese (`vi`); LinkedIn and Substack reader-facing prose are English (`en`). Code, identifiers, product names and established technical terms may remain unchanged for precision. The rule is encoded in series/episode assets, each social artifact's `language` field, platform playbooks, exact-version `channel-language` test evidence and the manifest validator; literal cross-channel translation is not accepted as adaptation.

## Universal professional-series rules — v2.6.0

The user-supplied `UNIVERSAL PROFESSIONAL SERIES CONTENT RULES` was converted into progressive-disclosure guidance plus executable controls. Accepted additions include the capability journey and five-layer coverage model, nine episode types, per-episode teaching contract, human-voice editing pass, decision-oriented conclusion and CTA rules, primary-source/overclaim controls, and the mandatory `REAL → ILLUSTRATION → CODE` media evidence contract. Series, episode, social-package, manifest and review assets now carry these fields. Complete/release validation requires independent human-voice and media-integrity reviews, editorial-depth/human-voice/media-contract test scopes, safe media provenance/redaction/rights/hash evidence, and all three media roles for every requested social artifact.

### Ownership and intellectual-property boundary

- Career Coach owns career intent, sustainable development, evidence and ethical visibility; Technical Content owns actual series production and publishing; Academy owns curriculum and assessment; Documentation owns specialized diagrams.
- Prompt patterns were translated into new atomic contracts and independently authored references/assets. No long passage, author-specific story or distinctive wording from the PDF is copied into runtime skills.
- Author voice is represented as high-level traits and constraints only. The suite forbids copied phrasing, invented experience, fake benchmarks, title guarantees and engagement-at-any-cost behavior.

## Personal Project Discovery & Build OS — v2.7.0

Release 2.7.0 adds `data-personal-project-engineering`: 42 atomic workflows for selecting, transforming, planning, validating and evolving personal Data projects. It supports 20 entry modes: problem, user workflow, decision, self-authored idea, external inspiration, dataset, repository, role competency, technology, domain, architecture, integration, open-source issue, paper replication, tutorial/course, incident/failure, constraint, benchmark, governance/compliance and hybrid input.

### Selection and execution controls

- Resolve hard gates before scoring: legal/ethical usability, safe access, bounded scope, feasible environment and testability.
- Rank viable options with a 100-point weighted scorecard covering decision value, portfolio signal, differentiation potential, evidence availability, feasibility, learning leverage, operational depth and maintenance burden; record confidence and risk penalty separately.
- Create a versioned personal-project thesis with target user, problem, decision/workflow, build promise, exclusions, success evidence and substantive differentiators before implementation.
- Run a shared lifecycle: intake → evidence inspection → option selection → thesis → architecture/blueprint → bounded milestones → implementation handoff → functional/reproducibility/quality/security/performance tests → portfolio evidence → release review → maintenance/evolution.

### Repo-first assessment standard

Repo-first now resolves repository URL, owner, exact commit/tag, license/terms and intended use before reuse. The evidence-based audit covers 12 dimensions: purpose/users; architecture/data flow; runtime/reproducibility; data contracts/modeling; correctness/tests; security/secrets/dependencies; CI/CD/supply chain; observability/reliability; performance/cost; documentation/DevEx; maintainability/activity; and license/provenance. Findings carry location, evidence state, severity, confidence, consequence and verification method. The transformation matrix decides `reuse`, `adapt`, `replace`, `drop` or `build-new` for each relevant upstream element.

### External-source originality rule

When the starting point is another person's repository, idea, article, demo, video, project list or product, the suite treats it as an attributed source and turns it into a user-owned build thesis. It records what came from the source, what was rejected, what changed and why. A portfolio project normally needs at least three substantive differentiation axes—such as user/problem, data, architecture, behavior, evaluation, operations, governance or integration. Renaming, visual restyling, framework swaps and documentation-only changes do not qualify. The suite never converts external provenance into a false claim that the original idea was self-originated.

### Standards used as design evidence

- GitHub repository licensing and contribution guidance informs provenance, permitted-use and contribution paths.
- NIST Secure Software Development Framework informs lifecycle-integrated security practices.
- OpenSSF Scorecard informs evidence categories for source, dependency, CI and maintenance risk; it remains a heuristic, not a guarantee.
- SLSA provenance informs artifact origin and integrity evidence.
- DORA capability guidance informs delivery, feedback, observability and improvement considerations.
- NIST AI RMF informs Govern/Map/Measure/Manage routing for AI/ML projects.
- FAIR principles inform findability, accessibility, interoperability and reuse considerations for project data and artifacts.

The implementation is independently authored. External standards and repositories are cited as design evidence; their prose and code are not vendored into this suite.

## Depth, Enforcement and Stack-Native Runtime — v3.0.0

Version 3.0.0 intentionally keeps the catalog at 30 skills and 711 atomic workflows. The upgrade addresses execution depth rather than inflating task count.

### Deep task contracts

Every catalog entry now carries contract version and criticality metadata. The build generates 88 `enforced`, 131 `deep` and 492 `standard` contracts. Deep/enforced contracts add role-specific mandatory inputs, invariants, ordered decision/execution sequence, proof requirements and explicit blocking conditions. The domain protocols cover all 30 roles while remaining inside the selected task contract, so they do not increase always-on discovery context.

### Executable Workflow and Evidence OS

New typed schemas cover task metadata, workflow manifests, evidence envelopes, approval records and privacy-minimized telemetry. Deterministic validators enforce acyclic dependencies, catalog risk floors, task ownership, dependency completion, evidence resolution, controlled-work approval, exact artifact version/hash binding and truthful workflow completion. Approval cannot replace evidence and evidence cannot replace authority.

### Stack-native adapters

Ninety-eight role-scoped adapter copies are generated from 12 canonical implementation packs: Airflow, dbt, Spark, Kafka/Flink, Snowflake, BigQuery, Databricks/Delta, Microsoft Fabric, Power BI, Tableau/Looker, DataHub/OpenMetadata and MLflow/Kubeflow. Each pack defines version/context binding, read-only preflight, execution/test proof and platform-specific release traps. A role SKILL links directly to only its relevant packs, and agents load one or two after stack detection.

### Deterministic automation

- `audit_repository.py`: read-only repository evidence and 12-dimension inventory.
- `detect_data_stack.py`: candidate adapter detection without executing repository code.
- `bootstrap_context_index.py`: privacy-minimized context source inventory with authority/freshness hypotheses.
- `validate_workflow.py`: graph, risk, evidence, approval and completion enforcement.
- `validate_evidence_bundle.py`: evidence structure, artifact-root containment and SHA-256 verification.
- `build_portfolio_evidence.py`: artifact/validation/claim resolution for defensible portfolios.
- `record_skill_telemetry.py` and `analyze_skill_telemetry.py`: user-content-free improvement signals.

### Evaluation expansion

The suite now tests 32 natural-language routing cases, 32 role confusion pairs, 30 catalog-routing cases, 13 lifecycle cases, valid/adversarial workflow and evidence fixtures, portfolio claim enforcement, telemetry privacy rejection, adapter routing, 219 deep/enforced contract presence and 20 deterministic benchmark/control paths. Failed gates remain regression signals rather than reasons to weaken thresholds.

## Personal Second Brain and Book-to-Knowledge benchmark — v3.1.0

Version 3.1.0 adds two independently routed systems rather than one overloaded prompt.

### Personal Second Brain / Knowledge OS

- The canonical local-first architecture is `1_Nguon → 2_Wiki → 3_Toi → 4_Ket-Qua`: immutable source material, processed knowledge, personal context and reusable outputs.
- Notion, Google Sheets, LarkSuite, Obsidian and ordinary local files may remain sources or interfaces. Migration is inventory-first, non-destructive, reversible and hash/provenance bound.
- Stable IDs, source locators, fact/inference/personal-context separation, conflict handling, retrieval tests, output grounding, privacy/freshness audits and backup/restore evidence are first-class controls.
- Metadata indexing excludes likely secrets and emits no note bodies or data values.

### Book → Knowledge / Skill / Action Engineering

The public `virgiliojr94/book-to-skill` repository was inspected as a behavioral benchmark. Useful patterns retained are analyze/full/update paths, cost preflight, structure-first extraction, bounded access for large sources, progressive chapter resources, framework/principle/technique extraction and copyright/security gates. This suite extends those patterns with:

- Eight explicit destinations: skill, second brain, career, interview, project, curriculum, workflow and content.
- Exact framework names and source locators; author claims, AI synthesis and user application remain separate records.
- Rights status, version lineage, destination artifact hashes, transfer/application tests and exact-publication authority.
- Multi-book comparison, new-edition merge, fold-in, retirement and changed-scenario transfer evaluation.

No upstream file is vendored. Runtime references, schemas, validators, templates and task contracts are independently authored for this suite. The upstream repository remains the authority for its MIT license and original implementation.

## Cross-skill Learning Memory — v3.2.0

This release adds an independently authored personal learner-memory protocol; it is not copied from an upstream memory product or note-taking system.

- Career owns mastery semantics, evidence review, decay detection and reconciliation. Personal Second Brain may store the canonical artifact, while all technical/academy roles consume it read-only.
- The model distinguishes exposure, practice, demonstration, mastery, staleness and conflict. Course completion and conversation history are insufficient evidence for mastery.
- Cross-skill transition is relevance-aware: fresh mastered knowledge is compressed; direct prerequisites retain only interfaces, decision rules and failure modes; stale, changed-version, conflicted and safety-critical knowledge is expanded and retested.
- Learner-memory identity, authority, privacy, evidence references, dates and append-only learning events are schema-backed. Validation rejects unsupported mastery and broken references.
- The context builder has an explicit token budget and never copies evidence bodies. It returns IDs and bounded summaries so Airflow knowledge can support dbt without reproducing an Airflow course inside the dbt prompt.

Design evidence came from the suite's existing Career, Academy, Second Brain, context engineering and evidence OS boundaries. No external memory service, API or MCP dependency is required.
