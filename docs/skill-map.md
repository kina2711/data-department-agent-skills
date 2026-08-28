# Data Department Skill Map

## 1. Mục tiêu thiết kế

Xây một bộ Claude Agent Skills có thể phục vụ toàn bộ vòng đời dữ liệu, từ chiến lược, kiến trúc, thu thập, biến đổi, phân tích, quản trị đến Machine Learning và vận hành production.

Nguyên tắc phân rã:

- Một role là một top-level skill có khả năng nhận diện và điều phối công việc thuộc role đó.
- Một nhiệm vụ tạo ra một deliverable chính và có một tiêu chí hoàn thành rõ ràng là một atomic sub-skill.
- Một atomic sub-skill không đồng nghĩa với một bước thao tác nhỏ. Ví dụ `viết một câu SQL` chỉ là thao tác; `trả lời một business question bằng SQL đã kiểm chứng` mới là một nhiệm vụ hoàn chỉnh.
- Skill dùng chung không được copy vào nhiều role. Role skill gọi shared skill hoặc áp dụng shared contract.
- Mọi thao tác ghi production, cấp quyền, xử lý PII, xóa dữ liệu, chứng nhận KPI và triển khai model phải có approval gate.

## 2. Kiến trúc phân tầng

```text
data-department-orchestrator
├── shared-data-core
├── company-data-context
├── head-of-data-and-data-product
├── data-business-analysis
├── data-architecture
├── data-governance-and-stewardship
├── metadata-engineering-and-catalog
├── data-platform-and-dataops
├── data-developer-experience
├── data-engineering
├── analytics-engineering
├── data-analysis
├── business-intelligence
├── product-analytics-and-experimentation
├── data-science
├── machine-learning-engineering
├── mlops
├── data-quality-and-reliability
├── data-security-and-privacy
├── master-data-management
├── generative-ai-engineering
├── data-documentation-and-diagrams
├── data-enablement-and-knowledge
├── data-academy-and-curriculum
├── data-onboarding-and-integration
├── data-talent-acquisition-and-interview
└── data-career-and-interview-coach
```

Mỗi role skill nên có cấu trúc:

```text
role-skill/
├── SKILL.md
├── tasks/
│   ├── task-a.md
│   ├── task-b.md
│   └── task-c.md
├── scripts/
└── assets/
```

`SKILL.md` chỉ làm routing và quy định workflow chung. Mỗi file trực tiếp trong `tasks/` là một atomic sub-skill để giữ progressive disclosure ở một tầng tham chiếu.

## 3. Contract bắt buộc của một atomic sub-skill

Mỗi task module phải khai báo đủ:

1. **Trigger**: người dùng nói gì hoặc artifact nào xuất hiện thì task được chọn.
2. **Goal**: một kết quả duy nhất cần đạt.
3. **Required inputs**: đầu vào tối thiểu; thiếu gì thì phải phát hiện.
4. **Context to load**: schema, glossary, policy, codebase hoặc runbook cần đọc.
5. **Workflow**: các bước thực hiện và decision points.
6. **Deliverable**: một artifact chính có schema/template rõ ràng.
7. **Validation**: kiểm tra kỹ thuật và nghiệp vụ trước khi hoàn thành.
8. **Approval gate**: hành động nào bắt buộc con người duyệt.
9. **Failure mode**: khi nào phải dừng, rollback hoặc chuyển role.
10. **Handoff**: role/sub-skill tiếp theo và dữ liệu bàn giao.

## 4. Shared Data Core — năng lực dùng chung

Đây là các task dùng lại bởi mọi role; không gắn ownership vào một role chuyên môn.

### P0 — bắt buộc

- `core-classify-data-request` — phân loại intent, domain, độ rủi ro và role owner; output: routing decision.
- `core-discover-data-assets` — tìm source, table, metric, dashboard và owner liên quan; output: evidence-backed asset shortlist.
- `core-read-business-glossary` — ánh xạ thuật ngữ người dùng sang định nghĩa chuẩn; output: resolved terminology.
- `core-inspect-dataset-schema` — đọc schema, khóa, partition và quan hệ; output: schema assessment.
- `core-profile-dataset` — đo null, distinct, distribution, outlier và freshness; output: profile report.
- `core-check-data-access` — xác định quyền cần thiết và giới hạn sử dụng; output: access decision hoặc request.
- `core-handle-sensitive-data` — nhận diện PII/confidential data và áp dụng handling rule; output: safe processing plan.
- `core-validate-sql-safely` — lint, dry-run/explain, kiểm tra scan cost và read/write risk; output: validated SQL.
- `core-estimate-change-impact` — tìm downstream dependency và stakeholder bị ảnh hưởng; output: impact report.
- `core-create-data-work-ticket` — chuyển yêu cầu thành scope, acceptance criteria, dependency và estimate; output: implementation-ready ticket.
- `core-define-success-contract` — chuyển mục tiêu mơ hồ thành outcome quan sát được, tiêu chí pass/fail, evidence, non-goals và điều kiện dừng; output: verifiable success contract.
- `core-audit-change-scope` — đối chiếu thay đổi thực tế với yêu cầu, allowlist, planned deletions và task-to-file traceability để phát hiện scope creep; output: surgical change-scope audit.
- `core-document-data-deliverable` — tạo tài liệu theo template chuẩn; output: linked documentation.
- `core-record-data-decision` — ghi decision, alternatives, evidence và consequences; output: decision record.
- `core-request-human-approval` — tạo approval package đúng owner; output: auditable approval request.
- `core-handoff-data-work` — đóng gói context, artifacts, open risks và next action; output: lossless handoff package.
- `core-verify-deliverable` — chạy checklist theo loại artifact và thu evidence; output: pass/fail verification report.
- `core-build-task-context-package` — gom task, business, schema, lineage, constraints và evidence thành context bundle có manifest, provenance, freshness và token budget; output: prompt-ready task context package.

## 4A. Company Data Context — bộ nhớ có quản trị của phòng Data

Ranh giới: pack này quản lý context ổn định và có provenance của công ty; không thay thế việc kiểm tra live system khi thông tin có thể đã thay đổi.

- `ctx-initialize-company-data-context` — tạo cấu trúc context chuẩn cho business, data, platform, policy và ownership; output: initialized context pack.
- `ctx-register-source-system` — ghi purpose, owner, interface, cadence, keys và constraints của source; output: source-system entry.
- `ctx-register-dataset-schema` — ghi schema, grain, keys, partitions, relationships và examples; output: dataset-schema entry.
- `ctx-register-business-metric` — ghi definition, formula, grain, dimensions, exclusions và owner; output: metric entry.
- `ctx-register-data-owner` — ghi accountability, stewardship, escalation và contact channel; output: ownership entry.
- `ctx-register-data-policy` — ghi rule, scope, enforcement, exception và authority; output: policy entry.
- `ctx-record-platform-environment` — ghi tools, environments, endpoints, deployment và operational constraints; output: platform-context entry.
- `ctx-validate-context-pack` — kiểm tra completeness, conflicts, staleness, provenance và broken references; output: context validation report.
- `ctx-build-context-index` — tạo index phân tầng chỉ rõ nguồn context, authority, scope, trigger đọc, owner và freshness cho Claude/agent sessions; output: governed context index.

## 5. Head of Data / Data Product / Data PM

Ranh giới: role này quyết định outcome, priority, capacity và stakeholder alignment; không tự quyết định implementation detail thay Architect/DE/AE.

### P0 — vận hành cơ bản

- `hod-assess-data-maturity` — đánh giá maturity theo people/process/technology/governance; output: maturity baseline.
- `hod-define-data-strategy` — chuyển business strategy thành data themes và measurable outcomes; output: data strategy.
- `hod-build-data-roadmap` — sắp xếp initiative theo value, risk và dependency; output: phased roadmap.
- `hod-define-data-okrs` — xây objective, key result, baseline và owner; output: approved OKR set.
- `dpm-intake-data-request` — chuẩn hóa problem, requester, urgency và expected decision; output: intake record.
- `dpm-frame-data-product-opportunity` — xác định user, job-to-be-done, value hypothesis và constraints; output: opportunity brief.
- `dpm-prioritize-data-backlog` — chấm điểm value, effort, risk và dependency; output: ranked backlog.
- `dpm-write-data-product-requirements` — định nghĩa scope, user story, NFR và acceptance criteria; output: PRD.
- `dpm-plan-data-release` — xác định milestones, dependency, rollout và communication; output: release plan.
- `dpm-accept-data-deliverable` — kiểm chứng acceptance criteria và business usability; output: acceptance decision.

### P1 — scale organization

- `hod-design-data-operating-model` — xác định centralized/federated/mesh, ownership và interaction model; output: operating model.
- `hod-plan-data-capacity` — dự báo demand, capacity, bottleneck và hiring/outsourcing; output: capacity plan.
- `hod-manage-data-portfolio` — theo dõi value, cost, risk và status của initiatives; output: portfolio review.
- `hod-define-data-service-slas` — xác định service catalog, priority và response/resolution target; output: SLA policy.
- `hod-evaluate-data-vendor` — so sánh fit, TCO, lock-in, security và exit path; output: vendor decision memo.
- `hod-measure-data-product-adoption` — theo dõi usage, satisfaction, decision impact và retirement signal; output: adoption report.
- `hod-run-data-steering-review` — chuẩn bị decisions, escalations và commitments; output: steering decision log.

### P2 — organization development

- `hod-design-data-team-topology` — xác định team boundaries và cognitive load; output: target topology.
- `hod-define-data-role-competencies` — tạo competency matrix theo level; output: role framework.
- `hod-create-data-hiring-scorecard` — định nghĩa outcomes, signals và interview rubric; output: hiring scorecard.
- `hod-build-data-training-roadmap` — gap assessment và learning path; output: capability plan.

## 6. Data Architect

Ranh giới: Architect quyết định principles, target state, standards và cross-system trade-offs; engineering role hiện thực và vận hành.

### P0 — kiến trúc nền tảng

- `arch-assess-current-data-architecture` — lập inventory, bottleneck, risk và technical debt; output: current-state assessment.
- `arch-define-target-data-architecture` — mô tả target state, boundaries, flows và quality attributes; output: target architecture.
- `arch-select-data-platform-pattern` — đánh giá warehouse/lake/lakehouse/mesh theo workload; output: pattern decision.
- `arch-design-data-domain-boundaries` — xác định domain, bounded context, owner và shared concepts; output: domain map.
- `arch-design-data-flow` — mô tả source-to-consumption flow, latency và control points; output: data-flow design.
- `arch-choose-integration-pattern` — chọn batch/API/CDC/event/stream và trade-off; output: integration decision.
- `arch-define-data-contract-standard` — quy định schema, semantics, SLO, compatibility và ownership; output: contract standard.
- `arch-define-modeling-standard` — chọn dimensional/Data Vault/domain model conventions; output: modeling standard.
- `arch-write-architecture-decision-record` — ghi context, options, decision và consequence; output: ADR.
- `arch-review-solution-design` — kiểm tra consistency, scalability, operability và governance; output: review decision.

### P1 — resilience và scale

- `arch-design-batch-architecture` — thiết kế batch topology, scheduling, recovery và backfill; output: batch design.
- `arch-design-streaming-architecture` — thiết kế event model, ordering, delivery semantics và replay; output: streaming design.
- `arch-design-metadata-lineage-architecture` — thiết kế metadata collection, lineage và catalog integration; output: metadata architecture.
- `arch-design-data-security-architecture` — thiết kế trust boundaries, IAM, encryption và policy enforcement; output: security architecture.
- `arch-design-disaster-recovery` — xác định RTO/RPO, backup, failover và test plan; output: DR architecture.
- `arch-plan-data-platform-capacity` — dự báo throughput, concurrency, storage và headroom; output: capacity model.
- `arch-design-multi-environment-strategy` — phân tách dev/test/prod và promotion flow; output: environment architecture.
- `arch-plan-legacy-data-migration` — waves, coexistence, reconciliation và rollback; output: migration roadmap.

### P2 — enterprise architecture

- `arch-evaluate-technology-option` — proof-of-fit theo weighted criteria; output: technology recommendation.
- `arch-assess-architecture-compliance` — đối chiếu implementation với standards và waiver; output: compliance report.
- `arch-manage-architecture-technical-debt` — lượng hóa debt, risk và remediation sequence; output: debt register.
- `arch-design-data-sharing-architecture` — thiết kế clean room/exchange/API/share có governance; output: sharing architecture.

## 7. Data Governance / Data Stewardship

Ranh giới: DG định nghĩa policy, accountability và certification; không trực tiếp triển khai enforcement kỹ thuật thay Security/Platform/Engineering.

### P0 — nền quản trị

- `dg-define-data-domain` — xác định scope, assets, owner và stewardship boundary; output: domain charter.
- `dg-assign-data-ownership` — thiết lập accountable owner, steward và custodian; output: ownership matrix.
- `dg-create-business-term` — định nghĩa term, synonyms, rules, examples và owner; output: glossary entry.
- `dg-resolve-business-term-conflict` — phân tích định nghĩa cạnh tranh và điều phối quyết định; output: resolved term.
- `dg-classify-data-asset` — gắn sensitivity, criticality, regulatory và lifecycle class; output: classification record.
- `dg-define-data-policy` — viết policy gồm scope, rule, roles, exceptions và evidence; output: approved policy draft.
- `dg-define-data-retention-rule` — xác định retention, legal hold và disposal trigger; output: retention schedule.
- `dg-certify-data-asset` — kiểm tra owner, definition, quality, lineage và controls; output: certification decision.
- `dg-certify-business-metric` — phê duyệt definition, formula, grain, filters và source; output: certified metric.
- `dg-manage-data-issue` — ghi nhận, phân loại, assign, track remediation và closure evidence; output: governed issue record.

### P1 — workflow và compliance

- `dg-review-data-access-request` — đánh giá purpose, minimization, sensitivity và duration; output: governance recommendation.
- `dg-review-data-sharing-request` — đánh giá recipient, purpose, contract, controls và revocation; output: sharing decision package.
- `dg-define-data-quality-policy` — xác định dimensions, thresholds, owners và escalation; output: DQ policy.
- `dg-define-metadata-requirements` — xác định metadata bắt buộc theo asset type; output: metadata standard.
- `dg-review-lineage-completeness` — kiểm tra coverage cho critical data element; output: lineage gap report.
- `dg-manage-policy-exception` — đánh giá compensating controls, expiry và approver; output: time-bound exception.
- `dg-collect-compliance-evidence` — gom policy, access, quality, lineage và approval artifacts; output: evidence package.
- `dg-run-governance-council` — chuẩn bị agenda, decisions, owners và deadlines; output: council decision log.

### P2 — maturity và assurance

- `dg-assess-governance-maturity` — chấm maturity và xác định improvement backlog; output: governance assessment.
- `dg-measure-governance-kpis` — đo ownership, glossary, certification, issue aging và compliance; output: governance scorecard.
- `dg-plan-data-asset-retirement` — xác định consumers, archive, replacement và deletion approvals; output: retirement plan.
- `dg-audit-policy-conformance` — lấy mẫu evidence và ghi exceptions/remediation; output: conformance audit.

## 8. Data Platform Engineer / DataOps

Ranh giới: role này cung cấp paved road, runtime, automation và reliability của platform; không sở hữu business transformation logic.

### P0 — platform foundation

- `platform-provision-data-environment` — tạo dev/test/prod resources theo baseline; output: usable environment.
- `platform-configure-data-iam` — triển khai role/service account/least privilege; output: access configuration.
- `platform-manage-data-secrets` — tạo, rotate và audit secrets; output: managed secret lifecycle.
- `platform-provision-data-storage` — cấu hình bucket/database/schema, lifecycle và encryption; output: storage resource.
- `platform-provision-data-compute` — cấu hình compute, workload isolation và autoscaling; output: compute resource.
- `platform-deploy-orchestrator` — cài đặt, cấu hình và kiểm tra orchestration runtime; output: operational orchestrator.
- `platform-build-data-ci-pipeline` — lint, unit test, security scan và artifact build; output: CI workflow.
- `platform-build-data-cd-pipeline` — promotion, approval, deploy, smoke test và rollback; output: CD workflow.
- `platform-configure-platform-observability` — logs, metrics, traces, dashboards và alerts; output: observability baseline.
- `platform-backup-data-platform` — triển khai backup policy và verification; output: verified backups.

### P1 — operations at scale

- `platform-test-disaster-recovery` — diễn tập restore/failover và đo RTO/RPO; output: DR test report.
- `platform-upgrade-data-service` — compatibility assessment, staged rollout và rollback; output: upgraded service.
- `platform-manage-network-connectivity` — private endpoints, firewall và routing; output: validated connectivity.
- `platform-create-self-service-template` — tạo golden path cho pipeline/model/environment; output: reusable template.
- `platform-enforce-policy-as-code` — mã hóa guardrails và exception flow; output: enforced controls.
- `platform-troubleshoot-platform-incident` — triage infrastructure/runtime fault; output: restored platform and incident record.
- `platform-measure-platform-slos` — tính availability, latency và failure budget; output: SLO report.
- `platform-optimize-platform-cost` — phân bổ cost, rightsizing và schedule; output: savings plan.

### P2 — ecosystem evolution

- `platform-evaluate-platform-capacity` — stress test concurrency, throughput và saturation; output: capacity report.
- `platform-migrate-platform-workload` — di chuyển workload có dual-run và rollback; output: migrated workload.
- `platform-deprecate-platform-component` — inventory consumers, transition và removal; output: safe deprecation.

## 9. Data Engineer

Ranh giới: DE sở hữu ingestion, transformation kỹ thuật, orchestration và delivery reliability; business mart và metric semantics thuộc AE.

### P0 — ingestion và pipeline

- `de-profile-source-system` — xác định schema, keys, volume, change pattern và limits; output: source profile.
- `de-design-ingestion-pipeline` — chọn method, cadence, watermark, recovery và controls; output: ingestion design.
- `de-build-batch-ingestion` — nạp batch có checkpoint, audit và retry; output: production-ready batch pipeline.
- `de-build-api-ingestion` — xử lý auth, pagination, rate limit và incremental sync; output: API pipeline.
- `de-build-file-ingestion` — xử lý arrival, naming, encoding, schema và duplicate files; output: file pipeline.
- `de-build-cdc-ingestion` — capture insert/update/delete và checkpoint; output: CDC pipeline.
- `de-build-streaming-ingestion` — xử lý partition, ordering, delivery semantics và dead-letter; output: stream pipeline.
- `de-normalize-raw-data` — chuẩn hóa type, metadata, timestamp và malformed records; output: conformed raw layer.
- `de-build-incremental-load` — triển khai watermark/merge và late-arriving handling; output: incremental pipeline.
- `de-make-pipeline-idempotent` — đảm bảo rerun không tạo duplicate hoặc corruption; output: idempotency guarantees.
- `de-orchestrate-data-workflow` — cấu hình dependencies, schedule, timeout, retry và SLA; output: orchestrated DAG.
- `de-add-pipeline-data-checks` — kiểm tra schema, count, duplicate và reconciliation; output: guarded pipeline.

### P1 — reliability và lifecycle

- `de-handle-schema-evolution` — đánh giá compatible/breaking change và migration; output: schema-change implementation.
- `de-backfill-data-range` — ước lượng scope/cost, chạy chunked backfill và reconcile; output: verified backfill.
- `de-replay-stream-events` — xác định offset, deduplicate và validate replay; output: verified replay.
- `de-reconcile-source-target` — so sánh counts, totals, hashes và sample records; output: reconciliation report.
- `de-analyze-execution-plan` — đọc SQL/Spark execution plan trước khi tối ưu để xác định scan, join, shuffle, skew, partition và bottleneck có evidence; output: execution-plan diagnosis.
- `de-optimize-pipeline-performance` — tìm bottleneck I/O/compute/shuffle và tune; output: benchmarked improvement.
- `de-write-pipeline-tests` — unit, contract, integration và failure-path tests; output: automated test suite.
- `de-deploy-data-pipeline` — promote config/code, smoke test và monitor; output: deployed pipeline.
- `de-troubleshoot-failed-pipeline` — isolate source/code/platform/data cause; output: restored pipeline and diagnosis.
- `de-create-pipeline-runbook` — viết operations, alerts, recovery và ownership; output: runbook.

### P2 — migration và optimization

- `de-migrate-data-pipeline` — dual-run, reconcile, cutover và rollback; output: migrated pipeline.
- `de-retire-data-pipeline` — confirm consumers, archive và disable safely; output: retired pipeline.
- `de-review-data-engineering-change` — review correctness, resilience, cost, security và operability; output: review findings.

## 10. Analytics Engineer

Ranh giới: AE biến raw/conformed data thành trusted analytical models và semantic metrics; không thay DA kết luận insight, không thay DE sở hữu source ingestion.

### P0 — analytical modeling

- `ae-translate-business-logic` — chuyển rule nghiệp vụ thành transformation specification; output: logic spec.
- `ae-design-dimensional-model` — xác định grain, facts, dimensions và keys; output: dimensional design.
- `ae-build-staging-model` — rename, cast và standardize source-aligned data; output: staging model.
- `ae-build-intermediate-model` — đóng gói reusable business transformations; output: intermediate model.
- `ae-build-analytics-mart` — tạo subject-area fact/dimension/wide mart; output: consumable mart.
- `ae-implement-incremental-model` — định nghĩa unique key, filter và merge behavior; output: incremental model.
- `ae-implement-slowly-changing-dimension` — quản lý lịch sử dimension theo SCD strategy; output: historical dimension.
- `ae-create-analytics-snapshot` — lưu point-in-time state có valid-from/to; output: snapshot model.
- `ae-write-model-tests` — kiểm tra key, relationship, accepted values và business assertions; output: model test suite.
- `ae-document-analytics-model` — mô tả grain, columns, caveats, lineage và owner; output: model documentation.
- `ae-implement-semantic-metric` — mã hóa formula, grain, dimensions và time semantics; output: semantic metric.
- `ae-certify-analytics-dataset` — thu test, freshness, documentation và ownership evidence; output: certification package.

### P1 — lifecycle và scale

- `ae-assess-model-change-impact` — tìm consumers, metric changes và migration needs; output: impact assessment.
- `ae-refactor-analytics-model` — giảm duplication/complexity mà giữ contract; output: refactored model.
- `ae-optimize-analytics-query` — tune joins, pruning, materialization và compute; output: measured performance gain.
- `ae-backfill-analytics-model` — chạy history rebuild và reconcile metrics; output: verified backfill.
- `ae-troubleshoot-model-failure` — phân biệt source, logic, dependency và warehouse faults; output: restored model.
- `ae-review-analytics-pull-request` — review grain, logic, tests, style và downstream impact; output: review decision.
- `ae-manage-metric-version` — xử lý breaking formula change, dual-run và communication; output: versioned metric.

### P2 — semantic governance

- `ae-detect-duplicate-metrics` — so sánh definitions và usage để đề xuất consolidation; output: duplication report.
- `ae-deprecate-analytics-model` — migrate consumers, preserve history và remove safely; output: retired model.
- `ae-design-self-service-data-product` — đóng gói discoverability, contract, examples và SLO; output: analytical data product.

## 11. Data Analyst

Ranh giới: DA sở hữu business question, analytical method, interpretation và communication; production transformation thuộc AE/DE, dashboard engineering phức tạp thuộc BI Engineer.

### P0 — analysis lifecycle

- `da-clarify-business-question` — chuyển yêu cầu mơ hồ thành decision, population, period và success criteria; output: analysis brief.
- `da-write-analysis-plan` — xác định hypotheses, metrics, dimensions, method và limitations; output: analysis plan.
- `da-discover-analysis-data` — tìm datasets/metrics phù hợp và đánh giá fitness; output: selected data sources.
- `da-define-metric-requirement` — định nghĩa business intent, formula, grain, filters và examples; output: metric requirement.
- `da-write-analysis-query` — tạo SQL đúng grain và logic cho question; output: validated query.
- `da-validate-analysis-result` — kiểm tra totals, edge cases, benchmark và alternate query; output: validation evidence.
- `da-run-programmatic-eda` — profile grain, types, missingness, duplicates, distributions, outliers, cardinality và data fitness trước phân tích sâu; output: reproducible EDA report.
- `da-run-descriptive-analysis` — tóm tắt level, trend, distribution và composition; output: descriptive findings.
- `da-analyze-kpi-variance` — tách change theo volume/rate/mix/time/segment; output: variance decomposition.
- `da-diagnose-metric-change` — kiểm tra instrumentation, data quality và business drivers; output: ranked root causes.
- `da-segment-entities` — tạo meaningful customer/product/account segments; output: segment profile.
- `da-analyze-funnel` — tính stage conversion, drop-off và segment differences; output: funnel findings.
- `da-analyze-cohort` — xây cohort matrix và so sánh behavior theo start period; output: cohort findings.
- `da-analyze-retention-churn` — định nghĩa retained/churned và xác định patterns; output: retention analysis.
- `da-answer-ad-hoc-question` — thực hiện analysis nhỏ có query, evidence và caveats; output: decision-ready answer.

### P1 — communication và monitoring

- `da-design-dashboard-requirement` — xác định audience, decisions, KPIs, cuts và interactions; output: dashboard spec.
- `da-review-dashboard-accuracy` — kiểm tra numbers, filters, grain, labels và edge cases; output: QA report.
- `da-create-analysis-visualization` — chọn chart và encoding đúng analytical message; output: visualization artifact.
- `da-write-insight-narrative` — trình bày what/so-what/why/now-what với evidence; output: insight memo.
- `da-present-analysis` — cấu trúc narrative, anticipated objections và decision ask; output: presentation package.
- `da-monitor-business-metric` — theo dõi threshold/trend và giải thích biến động; output: monitoring update.
- `da-document-analysis` — lưu question, logic, queries, results, caveats và reproducibility; output: analysis record.
- `da-explain-sql-business-logic` — chuyển sources, joins, filters, grain, aggregations và output columns của SQL thành logic nghiệp vụ kèm validation questions; output: query logic explanation.
- `da-explain-analysis-methodology` — giải thích data, method, assumptions, uncertainty và limitations theo audience tier; output: audience-calibrated methodology note.
- `da-run-analysis-peer-review` — review question-method alignment, data fitness, SQL/code, statistics, assumptions, narrative và reproducibility; output: analysis peer-review decision.
- `da-run-analysis-retrospective` — so sánh plan với thực tế, tìm nguyên nhân rework và chuyển lessons thành actions/templates/standards có owner; output: analysis retrospective and improvement actions.

### P2 — advanced analysis

- `da-build-business-forecast` — tạo forecast phục vụ planning kèm uncertainty; output: forecast and assumptions.
- `da-analyze-root-cause` — dùng issue tree và decomposition để tìm driver; output: causal hypothesis tree.
- `da-estimate-business-opportunity` — ước lượng population, uplift, cost và uncertainty; output: opportunity sizing.

## 12. BI Engineer / BI Developer

Ranh giới: BI Engineer sở hữu implementation, performance, security và lifecycle của semantic BI/dashboard; DA sở hữu câu hỏi và insight.

### P0 — dashboard delivery

- `bi-translate-dashboard-spec` — chuyển requirement thành dataset, measures, pages và interactions; output: BI design.
- `bi-build-semantic-model` — cấu hình relationships, measures, hierarchies và date logic; output: BI semantic model.
- `bi-build-dashboard` — hiện thực pages, visuals, filters và navigation; output: working dashboard.
- `bi-implement-dashboard-measures` — tạo measures đúng context và aggregation; output: tested measures.
- `bi-implement-row-level-security` — ánh xạ identity tới access filters; output: tested RLS.
- `bi-validate-dashboard-data` — reconcile dashboard với certified source; output: validation report.
- `bi-test-dashboard-usability` — kiểm tra navigation, readability, accessibility và mobile; output: usability findings.
- `bi-audit-dashboard-experience` — đánh giá read-only decision fit, hierarchy, metric truth, information density, interaction states, accessibility, responsiveness và dấu hiệu dashboard generic; output: prioritized dashboard experience audit.
- `bi-redesign-dashboard-experience` — chuyển audit và dashboard spec thành redesign có traceability, design-system fit, truthful content, test matrix và migration scope; output: implementation-ready dashboard redesign specification.
- `bi-optimize-dashboard-performance` — giảm query/render time và model size; output: benchmarked improvement.
- `bi-publish-dashboard` — deploy workspace/app, permissions và refresh; output: published dashboard.
- `bi-configure-dashboard-refresh` — thiết lập schedule, credential và failure alert; output: reliable refresh.

### P1 — lifecycle

- `bi-monitor-dashboard-usage` — đo viewers, frequency, latency và unused content; output: usage report.
- `bi-troubleshoot-dashboard` — xử lý data, refresh, permission hoặc visual issue; output: restored dashboard.
- `bi-certify-dashboard` — kiểm tra source, owner, quality, documentation và access; output: certification package.
- `bi-version-dashboard-change` — quản lý breaking change, release note và rollback; output: versioned release.
- `bi-retire-dashboard` — tìm consumers, cung cấp replacement và archive; output: retired dashboard.

## 13. Product Analyst / Experimentation

Ranh giới: role này sở hữu event/behavior analysis và experiment readout; instrumentation engineering do Product Engineering/DE triển khai.

### P0 — product measurement

- `pa-define-product-event` — định nghĩa event, properties, trigger, identity và validation; output: tracking spec entry.
- `pa-design-event-taxonomy` — chuẩn hóa naming, entities và lifecycle; output: event taxonomy.
- `pa-qa-product-instrumentation` — kiểm tra firing, payload, identity và duplication; output: instrumentation QA report.
- `pa-define-product-north-star` — xác định value event, frequency, breadth và guardrails; output: north-star framework.
- `pa-analyze-user-journey` — map paths, transitions và friction points; output: journey findings.
- `pa-analyze-activation` — định nghĩa activation và xác định actions liên quan value; output: activation analysis.
- `pa-analyze-feature-adoption` — đo exposure, trial, repeat và depth; output: adoption report.
- `pa-analyze-product-retention` — đo logo/user/activity retention theo cohorts; output: retention report.
- `pa-analyze-product-churn` — tìm patterns trước churn và affected segments; output: churn findings.
- `pa-build-growth-accounting` — phân rã new/reactivated/retained/resurrected/churned; output: growth accounting.

### P1 — experimentation

- `exp-frame-experiment-hypothesis` — định nghĩa intervention, mechanism, outcome và guardrail; output: testable hypothesis.
- `exp-design-ab-test` — chọn unit, randomization, variants, duration và analysis plan; output: experiment design.
- `exp-calculate-sample-size` — tính MDE, power, alpha và traffic duration; output: sample-size plan.
- `exp-check-randomization` — kiểm tra sample ratio mismatch và balance; output: randomization report.
- `exp-analyze-experiment` — ước lượng effect, interval, guardrails và heterogeneity; output: experiment readout.
- `exp-handle-experiment-peeking` — áp dụng sequential/correction rule; output: valid stopping decision.
- `exp-register-experiment` — lưu hypothesis, setup, result và decision; output: experiment registry entry.

## 14. Data Scientist

Ranh giới: DS sở hữu problem formulation, statistical/modeling validity và offline evidence; ML Engineer productionize, MLOps triển khai và vận hành.

### P0 — modeling lifecycle

- `ds-frame-modeling-problem` — chuyển business decision thành target, unit, horizon và constraints; output: modeling brief.
- `ds-design-modeling-dataset` — định nghĩa observation unit, labels, cutoff và sampling; output: dataset specification.
- `ds-prevent-data-leakage` — audit temporal, target, identity và split leakage; output: leakage assessment.
- `ds-run-exploratory-analysis` — đánh giá distribution, missingness, relationship và anomalies; output: EDA report.
- `ds-engineer-features` — tạo features có rationale, availability và reproducibility; output: feature set.
- `ds-build-baseline-model` — thiết lập heuristic/simple model benchmark; output: baseline metrics.
- `ds-train-model` — huấn luyện pipeline reproducible với tracked config; output: trained candidate.
- `ds-tune-hyperparameters` — search có budget và nested validation phù hợp; output: tuned candidate.
- `ds-validate-model` — đánh giá holdout, stability, uncertainty và business metric; output: validation report.
- `ds-select-evaluation-metric` — chọn metric phù hợp cost/error/base rate; output: evaluation protocol.
- `ds-explain-model` — phân tích global/local drivers và limitations; output: explainability report.
- `ds-create-model-card` — ghi intended use, data, metrics, risks và limitations; output: model card.

### P1 — advanced data science

- `ds-build-time-series-forecast` — xử lý seasonality, hierarchy, backtest và intervals; output: forecast model.
- `ds-estimate-causal-effect` — chọn identification strategy, assumptions và robustness tests; output: causal estimate.
- `ds-build-optimization-model` — định nghĩa objective, constraints và scenario evaluation; output: optimization solution.
- `ds-detect-anomalies` — xây expected behavior và calibrated anomaly threshold; output: anomaly model.
- `ds-assess-model-fairness` — đo subgroup performance, disparity và mitigation; output: fairness assessment.
- `ds-design-offline-experiment` — thiết kế validation có power và unbiased comparison; output: evaluation design.
- `ds-reproduce-model-result` — tái tạo dataset, code, environment và metrics; output: reproducibility report.
- `ds-handoff-model-to-engineering` — đóng gói artifact, features, inference contract và acceptance tests; output: production handoff.

### P2 — decision science

- `ds-run-scenario-simulation` — mô phỏng uncertainty và policy alternatives; output: scenario analysis.
- `ds-monitor-model-business-value` — liên kết model usage với outcome và counterfactual baseline; output: value report.

## 15. Machine Learning Engineer

Ranh giới: ML Engineer biến model thành production software có test, serving contract, scale và rollback; platform lifecycle thuộc MLOps.

### P0 — productionization

- `mle-productionize-model-code` — refactor notebook thành package/module deterministic; output: production codebase.
- `mle-build-feature-pipeline` — tạo online/offline consistent feature computation; output: feature pipeline.
- `mle-build-training-pipeline` — tự động hóa extract, train, evaluate và package; output: training pipeline.
- `mle-package-model-artifact` — đóng gói model, dependencies, signature và metadata; output: deployable artifact.
- `mle-define-inference-contract` — định nghĩa request/response, validation, version và error behavior; output: inference contract.
- `mle-build-batch-inference` — triển khai scalable scheduled scoring và result delivery; output: batch inference job.
- `mle-build-online-inference-service` — triển khai API/service có latency, scaling và health checks; output: serving service.
- `mle-write-model-unit-tests` — test preprocessing, features, prediction và edge cases; output: unit test suite.
- `mle-write-model-integration-tests` — test feature/model/service/downstream compatibility; output: integration tests.
- `mle-validate-training-serving-skew` — so sánh feature logic và distributions; output: skew report.
- `mle-optimize-inference-performance` — tune batching, serialization, runtime và hardware; output: latency/cost benchmark.
- `mle-implement-model-fallback` — tạo timeout, default, previous-model và degraded mode; output: resilience behavior.

### P1 — safe release

- `mle-build-shadow-deployment` — chạy model mới không ảnh hưởng decision; output: shadow comparison.
- `mle-build-canary-release` — route small traffic và define abort thresholds; output: canary rollout.
- `mle-validate-model-compatibility` — kiểm tra schema, runtime, feature và consumer compatibility; output: compatibility report.
- `mle-troubleshoot-inference-error` — isolate input, feature, artifact, runtime hoặc dependency cause; output: restored inference.
- `mle-rollback-model-release` — revert artifact/config/traffic và verify; output: restored stable version.
- `mle-document-model-service` — viết contract, limits, SLO, runbook và owner; output: service documentation.

### P2 — optimization

- `mle-compress-model` — quantize/prune/distill và đo quality trade-off; output: optimized model artifact.
- `mle-review-ml-engineering-change` — review correctness, performance, security và operability; output: review findings.

## 16. MLOps / ML Platform Engineer

Ranh giới: MLOps sở hữu ML platform, lifecycle automation, deployment controls và production monitoring; không tự thay đổi modeling objective.

### P0 — lifecycle platform

- `mlops-provision-ml-environment` — tạo reproducible compute, runtime và access; output: ML environment.
- `mlops-configure-experiment-tracking` — chuẩn hóa runs, params, metrics và artifacts; output: tracking workspace.
- `mlops-register-model-version` — lưu artifact, signature, lineage và stage; output: registry version.
- `mlops-build-ml-ci-pipeline` — lint, tests, data checks, security scan và package; output: ML CI workflow.
- `mlops-build-ml-cd-pipeline` — approval, deploy, smoke test và rollback; output: ML CD workflow.
- `mlops-promote-model-stage` — kiểm tra gates từ candidate tới staging/production; output: promotion decision.
- `mlops-deploy-model-version` — triển khai artifact/config và verify endpoints; output: deployed version.
- `mlops-monitor-model-service` — theo dõi availability, latency, errors và saturation; output: service monitoring.
- `mlops-monitor-data-drift` — đo input distribution shift với baseline; output: drift alert/report.
- `mlops-monitor-model-performance` — theo dõi delayed labels và model metrics; output: performance report.
- `mlops-monitor-prediction-quality` — theo dõi confidence, missing features và output anomalies; output: prediction-quality report.
- `mlops-trigger-model-retraining` — đánh giá schedule/drift/performance trigger và launch controlled run; output: retraining run.

### P1 — governance và reliability

- `mlops-validate-retrained-model` — so sánh challenger/champion và policy gates; output: validation decision.
- `mlops-rollback-production-model` — chuyển traffic/version và verify recovery; output: rollback record.
- `mlops-build-model-lineage` — nối data, code, features, run, artifact và deployment; output: lineage graph.
- `mlops-enforce-model-approval-gate` — yêu cầu evidence và approvers theo risk tier; output: auditable gate.
- `mlops-manage-feature-store` — đăng ký, materialize, monitor và deprecate features; output: governed feature lifecycle.
- `mlops-handle-ml-incident` — triage data/model/service issue và coordinate response; output: resolved incident.
- `mlops-create-ml-runbook` — ghi alerts, diagnosis, rollback và contacts; output: runbook.
- `mlops-optimize-ml-infrastructure-cost` — phân tích training/serving utilization và rightsizing; output: cost plan.

### P2 — platform evolution

- `mlops-upgrade-ml-runtime` — compatibility test, staged migration và rollback; output: upgraded runtime.
- `mlops-retire-model-version` — confirm no consumers, archive evidence và delete safely; output: retired version.
- `mlops-audit-model-controls` — thu lineage, approvals, monitoring và incident evidence; output: control audit.

## 17. Data Quality Engineer / Data Reliability Engineer

Ranh giới: DQ/DRE thiết kế quality controls, observability và incident process; domain owner quyết định business threshold, engineering role sửa implementation.

### P0 — preventive quality

- `dq-profile-critical-dataset` — lập baseline completeness, validity, uniqueness và distribution; output: DQ profile.
- `dq-define-data-quality-rule` — chuyển expectation thành executable rule, threshold và owner; output: DQ rule spec.
- `dq-implement-data-quality-test` — mã hóa và tích hợp rule vào pipeline/model; output: automated test.
- `dq-test-data-contract` — kiểm tra schema, semantics, freshness và compatibility; output: contract test report.
- `dq-reconcile-data-systems` — so sánh source/target theo control totals và samples; output: reconciliation evidence.
- `dq-build-data-quality-scorecard` — tổng hợp dimensions, criticality và issue status; output: DQ scorecard.
- `dq-certify-quality-readiness` — kiểm tra coverage, thresholds và open issues; output: quality gate decision.
- `dre-define-data-slo` — xác định freshness, availability, completeness và error budget; output: data SLO.
- `dre-monitor-data-freshness` — phát hiện late/missing updates theo schedule; output: freshness alerts.
- `dre-monitor-data-volume` — phát hiện spike/drop theo baseline và seasonality; output: volume alerts.
- `dre-monitor-schema-change` — phát hiện breaking drift và affected consumers; output: schema alert.
- `dre-monitor-data-distribution` — phát hiện anomaly trên critical columns; output: distribution alert.

### P1 — incident response

- `dre-triage-data-alert` — xác định severity, blast radius, owner và immediate action; output: triage decision.
- `dre-diagnose-data-incident` — trace lineage và evidence để tìm failure point; output: root-cause diagnosis.
- `dre-coordinate-data-incident` — quản lý roles, communication, timeline và mitigation; output: incident log.
- `dre-restore-corrupted-data` — quarantine, restore/reprocess và reconcile; output: recovered dataset.
- `dre-write-data-postmortem` — ghi impact, timeline, root cause, lessons và actions; output: postmortem.
- `dre-track-reliability-actions` — theo dõi corrective/preventive actions đến closure; output: action register.

### P2 — proactive reliability

- `dq-detect-data-quality-anomaly` — xây baseline và calibrated anomaly logic; output: anomaly detector.
- `dre-assess-data-product-reliability` — review SLO, incidents, tests và dependencies; output: reliability assessment.
- `dre-run-data-game-day` — mô phỏng failure và đánh giá detection/recovery; output: resilience test report.

## 18. Data Security / Privacy Engineer

Ranh giới: Security/Privacy thiết kế và kiểm chứng controls; business owner/DPO/legal phê duyệt use case có rủi ro cao.

### P0 — protection controls

- `sec-discover-sensitive-data` — scan và xác minh PII/secrets/confidential fields; output: sensitive-data inventory.
- `sec-classify-sensitive-data` — gắn class theo policy và regulation; output: security classification.
- `sec-threat-model-data-flow` — xác định assets, trust boundaries, threats và mitigations; output: threat model.
- `sec-design-data-access-control` — định nghĩa RBAC/ABAC, segregation và break-glass; output: access-control design.
- `sec-implement-row-column-security` — triển khai filters/masking và test bypass; output: enforced policies.
- `sec-implement-data-masking` — chọn static/dynamic/tokenization theo use case; output: masked data flow.
- `sec-verify-data-encryption` — kiểm tra at-rest/in-transit/key management; output: encryption evidence.
- `sec-audit-data-access` — phân tích grants, usage, dormant access và anomalies; output: access audit.
- `privacy-assess-data-use-case` — đánh giá purpose, minimization, legal basis và risk; output: privacy assessment.
- `privacy-handle-data-subject-request` — discover, verify, export/delete và record evidence; output: completed DSR package.

### P1 — lifecycle và assurance

- `privacy-enforce-retention-deletion` — map assets, execute approved deletion và verify; output: deletion evidence.
- `sec-review-data-sharing-security` — đánh giá recipient, transport, controls và expiry; output: security recommendation.
- `sec-rotate-compromised-credential` — revoke, rotate, update consumers và audit; output: restored credentials.
- `sec-investigate-data-access-anomaly` — correlate identity, query, asset và context; output: investigation report.
- `privacy-prepare-data-breach-assessment` — xác định affected data, subjects, scope và notifications; output: breach assessment.
- `sec-collect-control-evidence` — gom configurations, logs, tests và approvals; output: audit evidence.

## 19. Master Data Management / Reference Data

Ranh giới: MDM sở hữu identity, golden record, hierarchy và stewardship workflow cho core entities.

### P0 — master lifecycle

- `mdm-design-master-entity` — xác định attributes, identifiers, relationships và owners; output: master model.
- `mdm-profile-entity-duplicates` — đo duplicate patterns và root causes; output: duplicate assessment.
- `mdm-define-match-rules` — thiết kế deterministic/probabilistic matching và thresholds; output: match rule set.
- `mdm-define-merge-survivorship` — xác định source priority, recency và field-level rules; output: survivorship policy.
- `mdm-build-golden-record` — match, merge, preserve lineage và publish identity; output: golden dataset.
- `mdm-manage-stewardship-queue` — route ambiguous matches và corrections; output: resolved stewardship cases.
- `mdm-manage-reference-data` — version codes, descriptions, mappings và effective dates; output: governed reference set.
- `mdm-manage-master-hierarchy` — duy trì parent-child, validity và cycle checks; output: valid hierarchy.
- `mdm-monitor-master-data-quality` — đo completeness, uniqueness và consistency; output: MDM scorecard.
- `mdm-synchronize-master-data` — publish changes, acknowledgements và reconciliation; output: synchronized consumers.

### P1 — controlled change

- `mdm-handle-master-data-change` — validate request, approval, effective date và audit; output: approved master change.
- `mdm-resolve-identity-conflict` — điều tra evidence và quyết định split/merge/link; output: identity resolution.
- `mdm-audit-master-data-lineage` — trace attribute về source, rule và steward action; output: lineage evidence.

## 20. Generative AI / AI Engineer

Ranh giới: AI Engineer xây AI data product; DS hỗ trợ evaluation/modeling, DE ingestion, ML Engineer serving, MLOps lifecycle.

### P0 — RAG và agent foundation

- `ai-frame-generative-ai-use-case` — xác định user task, value, risk và non-AI baseline; output: AI use-case brief.
- `ai-design-evaluation-dataset` — tạo representative, adversarial và edge-case examples; output: versioned eval set.
- `ai-ingest-knowledge-source` — extract, clean, version và preserve permissions; output: indexed-ready corpus.
- `ai-design-document-chunking` — chọn boundaries, overlap và metadata theo retrieval need; output: chunking strategy.
- `ai-create-embeddings-index` — embed, store, version và validate coverage; output: searchable index.
- `ai-build-retrieval-pipeline` — query transform, filters, hybrid search và top-k; output: retriever.
- `ai-build-reranking-pipeline` — rerank candidates và tune latency/quality; output: reranker.
- `ai-design-system-prompt` — định nghĩa role, constraints, evidence và refusal behavior; output: versioned prompt.
- `ai-build-rag-answering-flow` — nối retrieval, prompt, citations và fallback; output: RAG workflow.
- `ai-build-tool-using-agent` — định nghĩa tools, permissions, state và termination; output: bounded agent workflow.
- `ai-implement-ai-guardrails` — kiểm tra input/output, tool permission và policy; output: guardrail layer.
- `ai-evaluate-retrieval-quality` — đo recall/precision/ranking theo gold set; output: retrieval evaluation.
- `ai-evaluate-answer-quality` — đo correctness, groundedness, relevance và refusal; output: answer evaluation.

### P1 — production quality

- `ai-test-prompt-injection-resistance` — chạy attack set và đánh giá containment; output: security test report.
- `ai-monitor-ai-application` — theo dõi quality, latency, cost, safety và feedback; output: AI observability dashboard.
- `ai-analyze-ai-failures` — cluster failure modes và propose fixes; output: failure taxonomy.
- `ai-optimize-ai-cost-latency` — tune model routing, caching, context và batching; output: benchmarked optimization.
- `ai-release-ai-version` — evaluate, approve, canary và rollback; output: controlled release.
- `ai-create-human-review-workflow` — route low-confidence/high-risk cases; output: review queue and policy.
- `ai-document-ai-system` — ghi data, prompts, models, tools, risks và limitations; output: AI system card.

## 21. Business Analyst / Data Business Analyst

Ranh giới: BA sở hữu discovery, process, business requirements và traceability; Data PM quyết định product outcome/priority, DA sở hữu analytical method và insight.

### P0 — discovery và requirements

- `ba-frame-business-problem` — xác định hiện trạng, pain point, affected users và desired outcome; output: problem statement.
- `ba-map-stakeholders` — xác định sponsor, decision maker, users, SMEs và approvers; output: stakeholder map.
- `ba-map-business-decision` — nối decision với evidence, cadence, owner và consequence; output: decision map.
- `ba-define-scope-contract` — ghi in-scope, out-of-scope, constraints và change rule; output: scope contract.
- `ba-plan-discovery-interview` — chọn participants, question sequence và evidence cần thu; output: interview plan.
- `ba-run-discovery-workshop` — điều phối workshop và chốt decisions/open questions; output: workshop record.
- `ba-elicit-business-requirements` — thu thập goal, process, rule, data và acceptance needs; output: requirement set.
- `ba-write-business-requirements-document` — chuẩn hóa context, scope, stakeholders và requirements; output: BRD.
- `ba-write-functional-requirements` — định nghĩa system behavior, inputs, outputs và exceptions; output: functional specification.
- `ba-write-nonfunctional-requirements` — định nghĩa performance, availability, security, audit và usability; output: NFR specification.
- `ba-define-business-rules` — ghi condition, decision, exception, owner và examples; output: business-rule register.
- `ba-write-acceptance-criteria` — chuyển requirement thành testable Given/When/Then hoặc checklist; output: acceptance criteria.

### P1 — process và traceability

- `ba-document-as-is-process` — mô tả actors, events, steps, rules và pain points hiện tại; output: as-is process model.
- `ba-design-to-be-process` — thiết kế future workflow, controls và role changes; output: to-be process model.
- `ba-write-use-case-specification` — mô tả actor, precondition, main flow, alternatives và postcondition; output: use-case specification.
- `ba-map-user-journey` — mô tả stages, touchpoints, needs và friction; output: user-journey map.
- `ba-create-business-persona` — tổng hợp role, goals, behaviors và information needs; output: persona.
- `ba-build-requirement-traceability` — nối requirement tới design, data, test và release; output: traceability matrix.
- `ba-prioritize-requirements` — áp dụng value, urgency, dependency và risk; output: prioritized requirements.
- `ba-validate-requirements` — kiểm tra completeness, consistency, feasibility và testability; output: validation report.
- `ba-manage-requirement-change` — đánh giá impact, approval và baseline version; output: governed change request.
- `ba-assess-solution-feasibility` — đánh giá data, technology, operations, risk và value; output: feasibility report.
- `ba-seed-project-risk-register` — ghi risk, likelihood, impact, mitigation và owner; output: initial risk register.
- `ba-handoff-requirements-to-delivery` — đóng gói baselined requirements, decisions và open questions; output: delivery handoff.

## 22. Metadata Engineer / Data Catalog Manager

Ranh giới: Metadata role triển khai và vận hành catalog/lineage/discovery; DG quy định metadata policy và chứng nhận, DE/AE phát metadata từ implementation.

### P0 — metadata foundation

- `meta-inventory-data-assets` — lập inventory source, table, model, metric, report và owner; output: asset inventory.
- `meta-harvest-technical-metadata` — thu schema, type, keys, jobs và dependencies từ platforms; output: harvested metadata.
- `meta-curate-business-metadata` — nối descriptions, glossary terms, domain và use cases; output: enriched catalog entries.
- `meta-register-data-asset` — tạo catalog entry có identifier, owner, classification và lifecycle; output: registered asset.
- `meta-map-critical-data-elements` — xác định CDE và liên kết system/column/control; output: CDE map.
- `meta-build-data-lineage` — tạo source-to-target lineage ở dataset/column/job level; output: lineage graph.
- `meta-validate-lineage` — đối chiếu parsed lineage với code, queries và owner evidence; output: lineage validation report.
- `meta-index-data-for-discovery` — cấu hình searchable metadata, synonyms và ranking; output: discoverable catalog index.
- `meta-build-source-authority-matrix` — xác định authoritative source theo entity, field và use case; output: authority matrix.
- `meta-synchronize-asset-ownership` — cập nhật owner/steward từ systems of record; output: consistent ownership metadata.

### P1 — catalog operations

- `meta-ingest-usage-metadata` — thu query/report access và popularity signals; output: usage metadata.
- `meta-detect-orphan-data-assets` — tìm assets không owner, không consumer hoặc không refresh; output: orphan report.
- `meta-track-schema-version` — lưu schema history, compatibility và change events; output: schema version history.
- `meta-measure-metadata-completeness` — chấm mandatory fields theo asset type và criticality; output: completeness scorecard.
- `meta-onboard-metadata-connector` — cấu hình extraction, credentials, schedule và validation; output: operational connector.
- `meta-manage-catalog-tags` — chuẩn hóa technical/business/security tags và inheritance; output: governed tag set.
- `meta-publish-metadata-api` — cung cấp searchable metadata contract cho tools/agents; output: metadata API contract.
- `meta-deprecate-catalog-asset` — đánh dấu replacement, notify consumers và archive lineage; output: deprecated catalog record.

## 23. Data Developer Experience / Data Project Engineer

Ranh giới: role này chuẩn hóa repository, project bootstrap, local development và reusable engineering workflow; không sở hữu business logic của pipeline/model.

### P0 — repository và scaffolding

- `dx-audit-data-repository` — phân loại code, configs, tests, docs, data và risks; output: repository assessment.
- `dx-reverse-engineer-data-project` — trace entry points, pipeline, dependencies và outputs; output: evidence-based project map.
- `dx-trace-data-path-end-to-end` — theo một source hoặc job qua code, configuration, transforms và sink; dự đoán hành vi trước khi chạy rồi đối chiếu observed output; output: evidence-based end-to-end data path trace.
- `dx-scaffold-data-project` — sinh cấu trúc repo theo workload và standards; output: runnable project skeleton.
- `dx-select-project-template` — chọn template theo stack, deployment và governance needs; output: template decision.
- `dx-bootstrap-local-environment` — cấu hình runtime, env, credentials placeholders và smoke test; output: working local setup.
- `dx-manage-project-dependencies` — lock, update, vulnerability-check và document dependencies; output: reproducible dependency set.
- `dx-generate-synthetic-dataset` — sinh data giả theo schema, distribution và privacy constraints; output: synthetic dataset.
- `dx-create-test-data-fixture` — tạo deterministic edge-case records cho automated tests; output: test fixture.
- `dx-build-project-task-runner` — chuẩn hóa commands setup/test/lint/build/run; output: task runner.
- `dx-configure-precommit-quality-gates` — cài format, lint, secret scan và file checks; output: pre-commit workflow.

### P1 — project quality và delivery

- `dx-configure-repository-ci` — chạy tests, scans, validation và packaging theo pull request; output: repository CI.
- `dx-review-repository-hygiene` — kiểm tra naming, generated files, data leakage và dead code; output: hygiene report.
- `dx-detect-repository-secrets` — scan current tree/history và tạo remediation plan; output: secret exposure report.
- `dx-package-data-project` — tạo artifact/container/package có version và provenance; output: deployable project artifact.
- `dx-create-project-demo` — tạo safe sample data, scripted walkthrough và expected outputs; output: reproducible demo.
- `dx-benchmark-data-project` — chấm architecture, performance, quality, security, docs và business fit; output: benchmark scorecard.
- `dx-assess-production-readiness` — kiểm tra documentation, tests, deployment, observability và controls; output: readiness decision.
- `dx-migrate-project-structure` — chuyển layout/config có compatibility plan và verification; output: migrated repository.

## 24. Data Enablement / Knowledge Engineer

Ranh giới: role này biến kiến thức nội bộ thành learning/onboarding assets có thể đo lường; không thay domain owner phê duyệt nội dung chuyên môn.

### P0 — onboarding và learning

- `enable-create-role-onboarding` — tạo lộ trình 30/60/90 ngày theo role và access needs; output: role onboarding plan.
- `enable-create-system-onboarding` — giải thích architecture, workflows, environments và runbooks; output: system onboarding guide.
- `enable-create-learning-plan` — chuyển competency gap thành modules, practice và milestones; output: learning plan.
- `enable-explain-data-concept` — giải thích khái niệm theo audience và concrete examples; output: concept lesson.
- `enable-create-code-walkthrough` — dẫn giải data code từ entry point tới output; output: code walkthrough.
- `enable-run-pair-programming-session` — chia task, checkpoints và feedback loop; output: completed guided exercise.
- `enable-generate-practice-exercise` — tạo realistic task, fixtures và success criteria; output: practice assignment.
- `enable-generate-knowledge-check` — tạo quiz/scenario và answer rubric; output: knowledge check.
- `enable-run-skill-assessment` — đánh giá artifact thực tế theo competency rubric; output: skill assessment.

### P1 — knowledge lifecycle

- `enable-summarize-technical-source` — tổng hợp paper/book/documentation thành actionable notes; output: source summary.
- `enable-capture-lessons-learned` — rút decisions, surprises, patterns và anti-patterns từ project; output: lessons-learned record.
- `enable-create-knowledge-article` — chuẩn hóa problem, solution, evidence và applicability; output: knowledge article.
- `enable-build-concept-knowledge-map` — liên kết concept, prerequisite, contrast, application, misconception và related questions; output: linked concept knowledge map.
- `enable-build-versioned-knowledge-library` — tổ chức deep dives, question dossiers, tags, backlinks, owner, freshness và review status; output: governed knowledge library.
- `enable-publish-knowledge` — kiểm tra owner, sensitivity, discoverability và version trước publish; output: published knowledge asset.
- `enable-curate-knowledge-base` — merge duplicates, retire stale content và repair links; output: curated knowledge base.
- `enable-measure-learning-progress` — theo dõi completion, assessment và application evidence; output: learning-progress report.

## 25. Data Academy / Curriculum Engineering

Ranh giới: Academy role thiết kế, giảng dạy, đánh giá và cải tiến chương trình học; domain experts phê duyệt tính đúng chuyên môn, managers xác nhận năng lực áp dụng trong công việc.

### P0 — learning architecture

- `academy-assess-organizational-learning-needs` — phân tích strategy, competency gaps, incidents và delivery demand; output: organizational learning-needs assessment.
- `academy-define-role-learning-outcomes` — chuyển competency theo role/level thành observable learning outcomes; output: role learning-outcome framework.
- `academy-build-competency-curriculum-map` — nối competencies, modules, practice và assessments; output: competency-to-curriculum map.
- `academy-map-learning-prerequisites` — xác định kiến thức tiên quyết và dependency giữa modules; output: learning prerequisite graph.
- `academy-design-role-syllabus` — thiết kế scope, sequence, pacing và evaluation cho một role; output: role syllabus.
- `academy-design-level-learning-path` — tạo pathway Junior/Middle/Senior/Lead có entry/exit criteria; output: level learning pathway.
- `academy-build-role-theory-pack` — đóng gói lý thuyết chuẩn theo role, level và company context; output: role theory knowledge pack.
- `academy-build-concept-knowledge-graph` — mô hình hóa concepts, prerequisites, dependencies, misconceptions và transfer paths; output: concept knowledge graph.
- `academy-research-role-roadmap` — nghiên cứu roadmap hành nghề đang được dùng từ nguồn công khai, mỗi mục kèm nguồn và ngày truy cập; output: sourced role roadmap.
- `academy-build-skill-track-map` — tách mỗi bước roadmap thành skill track có thứ tự học, module và tiêu chí ra; output: skill-track map.
- `academy-plan-note-corpus` — liệt kê toàn bộ note dự kiến theo module kèm id, prerequisite và trạng thái build; output: note corpus plan.
- `academy-prioritize-corpus-by-gap` — xếp thứ tự module theo khoảng cách năng lực đã đo thay vì theo thứ tự roadmap; output: gap-prioritized corpus plan.
- `academy-map-questions-to-learning-objectives` — nối question tới competency, Bloom depth, prerequisites, learning objectives và assessments; output: question-to-learning traceability matrix.
- `academy-design-learning-module` — định nghĩa objectives, concepts, examples, activities và assessment; output: learning-module specification.
- `academy-plan-learning-cohort` — lập audience, schedule, instructors, capacity và support; output: cohort delivery plan.

### P1 — content production

- `academy-write-theory-lesson` — viết lesson có mental model, principles, trade-offs và misconceptions; output: theory lesson.
- `academy-write-knowledge-deep-dive` — giải thích một concept từ definition, mental model, mechanism, trade-offs tới edge cases, examples và sources; output: evidence-backed knowledge deep dive.
- `academy-build-note-module` — dựng trọn bộ note của một module theo cùng một chuẩn rồi cập nhật corpus manifest; output: module note batch.
- `academy-create-lecture-deck` — chuyển lesson thành slide narrative có examples và checks; output: lecture deck.
- `academy-create-instructor-guide` — ghi facilitation flow, timings, prompts, expected questions và interventions; output: instructor guide.
- `academy-create-learner-workbook` — tạo notes, exercises, reflection và progress checks; output: learner workbook.
- `academy-create-worked-example` — giải một bài mẫu từng bước kèm reasoning và checks; output: worked example.
- `academy-design-hands-on-lab` — tạo lab setup, tasks, checkpoints, cleanup và success criteria; output: lab specification.
- `academy-create-business-case-study` — tạo scenario, data, ambiguity, stakeholder context và decision ask; output: case-study package.
- `academy-design-capstone-project` — tạo end-to-end project, milestones, gates và rubric; output: capstone specification.
- `academy-create-learning-sandbox` — tạo môi trường cô lập, reproducible và cost-bounded; output: learning sandbox.
- `academy-generate-training-dataset` — tạo dataset realistic, privacy-safe và có planted issues; output: training dataset.
- `academy-write-assessment-rubric` — định nghĩa criteria, evidence, performance levels và critical failures; output: assessment rubric.
- `academy-write-answer-key` — tạo expected reasoning, alternatives, checks và common errors; output: answer key.
- `academy-design-formative-assessment` — tạo low-stakes checks để điều chỉnh việc học sớm; output: formative assessment.
- `academy-design-summative-exam` — tạo blueprint, questions, practical tasks, scoring và pass rules; output: summative exam package.

### P2 — delivery, testing và certification

- `academy-run-knowledge-diagnostic` — đo baseline theory, practical skills và misconceptions; output: learner diagnostic report.
- `academy-run-note-diagnostic` — chạy kịch bản chẩn đoán của corpus theo vòng Socratic có giới hạn rồi đề xuất hạng bằng chứng; output: note diagnostic session record.
- `academy-apply-misconception-feedback` — gom ngộ nhận lặp lại theo concept key rồi bổ sung vào chính note dạy sai mô hình đó; output: revised note batch.
- `academy-deliver-theory-session` — thực hiện lesson có knowledge checks và participation evidence; output: delivered-session record.
- `academy-facilitate-learning-workshop` — điều phối collaborative problem solving và peer feedback; output: workshop outcome record.
- `academy-run-lab-session` — giám sát hands-on execution, safety, checkpoints và recovery; output: lab completion evidence.
- `academy-run-learning-office-hours` — xử lý blockers, misconceptions và follow-up actions; output: office-hours support log.
- `academy-assess-learner-submission` — chấm artifact theo rubric với evidence và actionable feedback; output: assessed submission.
- `academy-analyze-learning-gaps` — tổng hợp item, cohort và role-level failure patterns; output: learning-gap analysis.
- `academy-create-remediation-plan` — thiết kế targeted theory, practice, coaching và retest; output: learner remediation plan.
- `academy-certify-role-competency` — đối chiếu evidence với pass rules và scope chứng nhận; output: competency certification decision.
- `academy-calibrate-assessors` — chuẩn hóa cách chấm bằng anchor examples và disagreement resolution; output: assessor-calibration record.
- `academy-audit-curriculum-quality` — kiểm tra accuracy, coverage, accessibility, bias và assessment validity; output: curriculum quality audit.
- `academy-audit-note-corpus` — kiểm tra trùng lặp, cạnh quan hệ treo, chu trình prerequisite, độ cũ và độ phủ của corpus; output: note corpus audit.
- `academy-index-note-corpus` — hợp nhất corpus thành index tra cứu bền vững ghi lại cái gì tồn tại, không suy ra mastery; output: note corpus index.
- `academy-measure-training-effectiveness` — đo reaction, learning, behavior transfer và business impact; output: training-effectiveness report.
- `academy-refresh-curriculum` — cập nhật theo stack, policy, incidents và learner evidence; output: versioned curriculum release.

## 26. Data Onboarding / Environment Integration

Ranh giới: Onboarding role điều phối sự sẵn sàng và hòa nhập; Platform/Security thực thi access, manager xác nhận performance, domain owners xác nhận kiến thức nghiệp vụ.

### P0 — framework và preboarding

- `onboard-define-data-onboarding-standard` — định nghĩa lifecycle, mandatory content, gates, owners và SLAs; output: data onboarding standard.
- `onboard-plan-new-hire-onboarding` — cá nhân hóa theo role, level, location, employment type và start date; output: individual onboarding plan.
- `onboard-collect-new-hire-context` — thu background, strengths, gaps, accessibility và support needs; output: new-hire context profile.
- `onboard-create-preboarding-checklist` — chuẩn bị contract dependencies, equipment, accounts, schedule và contacts; output: preboarding checklist.
- `onboard-plan-access-provisioning` — map role tới least-privilege access và approvers; output: access provisioning plan.
- `onboard-verify-access-readiness` — test accounts, MFA, environments, repositories và data permissions; output: access-readiness report.
- `onboard-prepare-workstation-environment` — thiết lập approved tools, runtime, configs và security baseline; output: workstation readiness evidence.
- `onboard-assign-onboarding-buddy` — chọn buddy, expectations, cadence và escalation path; output: buddy agreement.
- `onboard-plan-stakeholder-introductions` — sắp xếp sponsor, SMEs, consumers và partner teams theo relevance; output: stakeholder introduction plan.

### P1 — orientation và guided integration

- `onboard-deliver-company-orientation` — giới thiệu strategy, products, customers, culture và operating norms; output: company-orientation completion record.
- `onboard-deliver-data-organization-orientation` — giải thích team topology, services, ownership và interaction model; output: data-organization orientation record.
- `onboard-deliver-role-orientation` — làm rõ outcomes, responsibilities, boundaries và success measures; output: role-orientation record.
- `onboard-deliver-business-domain-orientation` — dạy processes, entities, KPIs, rules và stakeholders; output: domain-orientation record.
- `onboard-deliver-data-architecture-orientation` — hướng dẫn systems, flows, models, environments và critical dependencies; output: architecture-orientation record.
- `onboard-deliver-governance-security-orientation` — dạy policies, classifications, access, privacy và incident duties; output: governance-security training record.
- `onboard-deliver-toolchain-orientation` — hướng dẫn local setup, Git, orchestration, warehouse, BI/ML và support paths; output: toolchain-orientation record.
- `onboard-guide-documentation-discovery` — hướng dẫn tìm glossary, catalog, runbooks, ADRs và standards; output: documentation-discovery exercise.
- `onboard-create-first-week-plan` — sắp xếp learning, meetings, setup, shadowing và small wins; output: first-week schedule.
- `onboard-run-role-shadowing` — theo dõi work thật có observation goals và debrief; output: shadowing evidence.
- `onboard-run-guided-first-task` — thực hiện task nhỏ với coach, gates và feedback; output: guided-task completion record.
- `onboard-run-first-independent-task` — giao task bounded để đánh giá khả năng tự chủ; output: first-independent-task assessment.

### P2 — checkpoints, certification và transitions

- `onboard-run-seven-day-checkpoint` — kiểm tra access, clarity, belonging, workload và blockers; output: seven-day checkpoint record.
- `onboard-run-thirty-day-checkpoint` — đánh giá foundations, first contributions và support needs; output: thirty-day checkpoint record.
- `onboard-run-sixty-day-checkpoint` — đánh giá autonomy, quality, collaboration và domain growth; output: sixty-day checkpoint record.
- `onboard-run-ninety-day-checkpoint` — đánh giá role readiness, outcomes, gaps và next development plan; output: ninety-day onboarding review.
- `onboard-resolve-onboarding-blocker` — triage owner, impact, workaround và permanent fix; output: resolved onboarding issue.
- `onboard-assess-integration-health` — đo role clarity, access, network, learning, contribution và belonging; output: integration-health assessment.
- `onboard-certify-onboarding-completion` — kiểm tra mandatory evidence và manager/new-hire signoff; output: onboarding completion decision.
- `onboard-capture-onboarding-feedback` — thu anonymous và attributable feedback có action routing; output: onboarding feedback report.
- `onboard-measure-onboarding-effectiveness` — đo time-to-access, time-to-first-value, retention và readiness; output: onboarding effectiveness report.
- `onboard-crossboard-role-transfer` — tái định hướng khi đổi role/team/domain và giữ transferable context; output: crossboarding plan.
- `onboard-reboard-returning-employee` — xác định thay đổi trong thời gian vắng mặt và rebuild readiness; output: reboarding plan.
- `onboard-onboard-data-contractor` — áp dụng bounded access, scope, deliverables và exit controls; output: contractor onboarding package.
- `onboard-offboard-and-transfer-knowledge` — thu hồi access, bàn giao ownership, knowledge và open risks; output: offboarding evidence package.

## 27. Data Talent Acquisition / Structured Interviewing

Ranh giới: Talent role thiết kế và vận hành tuyển dụng có cấu trúc; hiring manager chịu trách nhiệm quyết định, HR/Legal quản lý employment policy, interviewers chỉ chấm evidence thuộc competency được giao.

### P0 — hiring architecture

- `talent-validate-workforce-need` — kiểm tra outcome, capacity gap, alternatives, budget và urgency; output: validated hiring request.
- `talent-define-data-role-profile` — định nghĩa mission, outcomes, responsibilities, boundaries và level; output: role profile.
- `talent-write-data-job-description` — viết JD rõ scope, competencies, conditions và inclusive requirements; output: job description.
- `talent-build-role-hiring-scorecard` — chuyển outcomes/competencies thành observable signals và scoring anchors; output: role hiring scorecard.
- `talent-plan-hiring-campaign` — xác định funnel, channels, timeline, owners, SLAs và capacity; output: hiring campaign plan.
- `talent-design-structured-interview-loop` — sắp xếp stages, competencies, interviewers và decision rules; output: interview-loop design.
- `talent-build-role-question-bank` — tạo behavioral, technical và scenario questions theo role/level; output: versioned interview question bank.
- `talent-map-question-to-competency-evidence` — phân tích intent, competency, depth, expected evidence, probes và red flags của từng question; output: question-competency-evidence matrix.
- `talent-write-interview-answer-anchors` — định nghĩa behavioral anchors và evidence của câu trả lời yếu/đạt/mạnh mà không tạo script học thuộc; output: calibrated answer-anchor pack.
- `talent-audit-question-bank-coverage` — kiểm tra coverage, redundancy, difficulty, bias, leakage và validity của question bank; output: question-bank coverage audit.
- `talent-create-interviewer-guide` — ghi conduct, probing, evidence capture, prohibited topics và timing; output: interviewer guide.
- `talent-train-data-interviewer` — đào tạo structured assessment, bias control và candidate experience; output: interviewer training record.
- `talent-calibrate-interview-panel` — dùng anchor responses để chuẩn hóa scoring và probing; output: panel calibration record.

### P1 — sourcing và assessment execution

- `talent-source-data-candidates` — xây search strategy, outreach criteria và source tracking; output: qualified candidate slate.
- `talent-screen-data-resume` — đối chiếu evidence với must-have outcomes thay vì keyword matching; output: resume-screen decision.
- `talent-run-recruiter-screen` — xác minh motivation, logistics, expectations và baseline fit; output: recruiter-screen record.
- `talent-run-technical-screen` — kiểm tra fundamentals và problem-solving theo role; output: technical-screen assessment.
- `talent-run-sql-interview` — đánh giá correctness, grain, edge cases, debugging và communication; output: SQL interview assessment.
- `talent-run-python-interview` — đánh giá data manipulation, design, testing và maintainability; output: Python interview assessment.
- `talent-run-analytics-case-interview` — đánh giá framing, metrics, analysis, insight và decision communication; output: analytics-case assessment.
- `talent-run-data-modeling-interview` — đánh giá grain, entities, dimensions, history và trade-offs; output: data-modeling assessment.
- `talent-run-data-engineering-interview` — đánh giá ingestion, reliability, scale, recovery và cost; output: data-engineering assessment.
- `talent-run-data-architecture-interview` — đánh giá boundaries, patterns, qualities, governance và migration; output: architecture-interview assessment.
- `talent-run-data-science-interview` — đánh giá statistics, experiment/model validity, leakage và business fit; output: data-science assessment.
- `talent-run-mlops-interview` — đánh giá lifecycle, deployment, monitoring, rollback và governance; output: MLOps interview assessment.
- `talent-run-governance-privacy-interview` — đánh giá policy, ownership, classification, access và risk scenarios; output: governance-privacy assessment.
- `talent-run-bi-product-sense-interview` — đánh giá audience, decision, semantic model và dashboard trade-offs; output: BI product-sense assessment.
- `talent-design-take-home-assignment` — tạo bounded realistic artifact, dataset, rubric và timebox; output: take-home assignment package.
- `talent-evaluate-take-home-assignment` — chấm correctness, reasoning, trade-offs, testing và authorship discussion; output: take-home assessment.
- `talent-run-behavioral-interview` — đánh giá past evidence về ownership, collaboration, learning và conflict; output: behavioral assessment.
- `talent-run-leadership-interview` — đánh giá strategy, people, execution, influence và judgment; output: leadership assessment.
- `talent-run-candidate-question-session` — cung cấp consistent, honest role/team context và ghi concerns; output: candidate-question record.

### P2 — decision, fairness và optimization

- `talent-score-interview-evidence` — map independent notes tới scorecard trước debrief; output: evidence-based interview score.
- `talent-run-hiring-debrief` — tổng hợp independent evidence, resolve conflicts và avoid groupthink; output: hiring debrief record.
- `talent-make-hiring-recommendation` — cân must-have evidence, risks và development assumptions; output: hiring recommendation.
- `talent-run-reference-check` — xác minh role-relevant evidence với consent và consistent questions; output: reference-check record.
- `talent-create-candidate-feedback` — tạo feedback lawful, respectful và evidence-grounded; output: candidate feedback package.
- `talent-audit-interview-fairness` — kiểm tra adverse patterns, inconsistent scoring và prohibited signals; output: interview fairness audit.
- `talent-audit-assessment-validity` — đo alignment, reliability và predictive usefulness của assessments; output: assessment-validity report.
- `talent-measure-quality-of-hire` — liên kết hiring evidence với ramp-up, performance và retention; output: quality-of-hire report.
- `talent-optimize-interview-funnel` — cải thiện conversion, time, candidate experience và signal quality; output: optimized interview process.

## 28. Data Career Development / Interview Coach

Ranh giới: Coach hỗ trợ nhân viên hoặc ứng viên chuẩn bị và phát triển; không giả mạo kinh nghiệm, làm hộ bài tuyển dụng hoặc can thiệp vào quyết định hiring.

### P0 — readiness và planning

- `career-clarify-target-data-role` — xác định role, level, company context và timeline mục tiêu; output: target-role brief.
- `career-assess-role-readiness` — đánh giá theory, practical evidence, communication và gaps theo scorecard; output: readiness assessment.
- `career-build-competency-gap-plan` — ưu tiên gap theo hiring impact, prerequisites và available time; output: competency-gap plan.
- `career-create-interview-preparation-plan` — lập lịch theory, practice, mocks, feedback và retests; output: interview preparation plan.
- `career-review-data-resume` — kiểm tra relevance, evidence, clarity, claims và role alignment; output: resume review.
- `career-review-data-portfolio` — đánh giá project depth, reproducibility, decisions, impact và presentation; output: portfolio review.
- `career-build-project-story` — chuyển project thật thành problem/action/evidence/impact narrative; output: project story bank.
- `career-build-career-operating-system` — nối current state, target capability, gaps, practice, real work, evidence, feedback và review cadence thành hệ thống phát triển bền vững; output: career operating system.
- `career-initialize-learning-memory` — tạo learner identity, topic taxonomy, baseline, storage pointer, privacy và evidence policy dùng xuyên các role skill; output: versioned learner-memory baseline.
- `career-map-cross-skill-prerequisites` — nối concept, interface, decision rule và failure mode giữa skill đã học với skill kế tiếp; output: cross-skill prerequisite map.
- `career-build-skill-transition-context` — nén phần đã mastered thành bridge summary và chỉ mở rộng phần stale, uncertain hoặc trực tiếp cần cho skill mới; output: bounded skill-transition context pack.
- `career-map-career-stage-competencies` — mô tả competency, scope, autonomy, judgment, impact và influence theo từng career stage mà không đồng nhất title giữa công ty; output: career-stage competency map.
- `career-build-career-evidence-portfolio` — lập evidence inventory theo learning, practice, project, production, leadership, business và organizational impact; output: career evidence portfolio.
- `career-design-career-capstone-program` — thiết kế chương trình 12/24 tháng có prerequisites, labs, projects, reviews, recovery buffers và evidence milestones; output: career capstone program.
- `career-design-technical-writing-strategy` — chọn audience, writing formats, themes, cadence và evidence policy để technical writing phục vụ mastery và reputation thật; output: career technical-writing strategy.
- `career-plan-ethical-professional-visibility` — xây kế hoạch contribution, community, mentoring và public expertise không khoe title hoặc biến self-promotion thành proxy cho năng lực; output: ethical professional-visibility plan.
- `career-generate-role-question-set` — tạo question set theo role, level, company style và gaps; output: personalized question set.
- `career-analyze-interview-question` — bóc tách interviewer intent, competency, scope, ambiguity, expected depth và failure traps; output: interview question analysis.
- `career-map-question-knowledge-dependencies` — nối question tới core concepts, prerequisites, related concepts, contrasts và follow-up paths; output: question knowledge dependency map.
- `career-build-question-deep-dive` — tạo hồ sơ gồm question analysis, concept theory, practical examples, trade-offs, failure modes, sources và related knowledge; output: interview question deep-dive dossier.
- `career-design-answer-strategy` — chọn structure, opening, reasoning flow, evidence, STAR/system-design pattern, checks và follow-up handling; output: interview answer strategy.
- `career-build-interview-knowledge-library` — tổ chức question dossiers thành linked, tagged, versioned và Notion-ready knowledge library; output: interview knowledge library.
- `career-design-concept-visual-explainer` — đặc tả visual mental model cho một concept gồm elements, relationships, annotation, common misreading, takeaway và alt text; output: concept visual explainer spec.
- `career-build-architecture-case-study` — bóc tách một kiến trúc public thành constraints, decisions, rejected alternatives, consistency, cost, failure modes và follow-up questions có trích dẫn nguồn; output: architecture case-study dossier.
- `career-build-offer-evaluation-and-negotiation-plan` — định giá từng cấu phần offer, đối chiếu market range có trích dẫn, chuẩn bị asks, fallback và walk-away position mà không hứa kết quả lương; output: offer evaluation and negotiation plan.

### P1 — simulations

- `career-run-mock-recruiter-screen` — mô phỏng motivation, background, logistics và concise pitch; output: recruiter-screen mock report.
- `career-run-mock-sql-interview` — mô phỏng SQL live có probing, edge cases và feedback; output: SQL mock assessment.
- `career-run-mock-python-interview` — mô phỏng data coding, testing và code explanation; output: Python mock assessment.
- `career-run-mock-analytics-case` — mô phỏng ambiguous business case từ framing tới recommendation; output: analytics-case mock assessment.
- `career-run-mock-data-modeling-interview` — mô phỏng model design và trade-off defense; output: data-modeling mock assessment.
- `career-run-mock-data-engineering-design` — mô phỏng pipeline/system design, failure và scale questions; output: DE design mock assessment.
- `career-run-mock-data-science-interview` — mô phỏng statistics, experiment, modeling và validation questions; output: DS mock assessment.
- `career-run-mock-mlops-interview` — mô phỏng deployment, drift, monitoring và incident scenarios; output: MLOps mock assessment.
- `career-run-mock-governance-architecture-interview` — mô phỏng policy, ownership, architecture và risk trade-offs; output: DG-architecture mock assessment.
- `career-run-mock-behavioral-interview` — mô phỏng evidence-based behavioral probing; output: behavioral mock assessment.
- `career-run-mock-leadership-interview` — mô phỏng strategy, prioritization, people và conflict scenarios; output: leadership mock assessment.

### P2 — feedback và mastery

- `career-evaluate-interview-answer` — chấm correctness, structure, evidence, depth và communication; output: answer evaluation.
- `career-coach-star-story` — cải thiện situation/task/action/result mà không bịa evidence; output: refined STAR story.
- `career-coach-technical-communication` — luyện clarification, assumptions, trade-offs và concise explanation; output: communication coaching record.
- `career-create-targeted-remediation` — giao theory/practice đúng failure pattern; output: interview remediation plan.
- `career-run-interview-retest` — kiểm tra lại cùng competency bằng scenario mới; output: retest assessment.
- `career-track-preparation-progress` — theo dõi evidence, scores, consistency và remaining risks; output: preparation progress report.
- `career-record-learning-event` — ghi append-only nội dung đã học, practice, artifact, feedback, assessment và source/version mà không tự nâng mastery; output: learning event record.
- `career-assess-topic-mastery` — đánh giá recall, application, changed-scenario transfer, failure handling, evidence và freshness trước khi đổi mastery state; output: topic mastery assessment.
- `career-detect-learning-decay` — phát hiện knowledge stale, ít dùng, version drift, evidence hết hạn hoặc confidence giảm và chọn refresh tối thiểu; output: learning-decay and refresh report.
- `career-reconcile-learning-memory` — hợp nhất learning history từ nhiều repo/skill, giữ lineage, xử lý conflict và ngăn silent status regression; output: reconciled learner-memory version.
- `career-run-career-review-cycle` — review tuần/tháng/quý/năm dựa trên evidence, feedback, energy, bottleneck và thay đổi bối cảnh; output: career review record.
- `career-audit-career-claims-evidence` — đối chiếu resume, portfolio, promotion hoặc public claims với evidence thật và gắn nhãn self-study/hypothetical đúng mức; output: career-claim evidence audit.
- `career-certify-interview-readiness` — tổng hợp multi-format evidence và residual gaps; output: interview-readiness decision.
- `career-audit-knowledge-coverage` — đối chiếu question library với canonical concept ID để tìm concept chưa có dossier, prerequisite gap, entry stale và vùng luyện thừa; output: interview knowledge coverage audit.
- `career-register-canonical-concept` — cấp và quản lý concept key nối canon, note, topic và competency về một danh tính; output: canonical concept registry entry.
- `career-bootstrap-concept-registry` — sinh lô concept key ứng viên từ track map và canon để corpus có chỗ bind ngay; output: proposed concept key batch.

## 29. Technical Content / Social Series Engineering

Ranh giới: skill này sở hữu strategy, research, production, QA, publishing và learning loop của technical content series. Career Coach sở hữu mục tiêu nghề nghiệp và ethical visibility; Academy sở hữu curriculum/assessment; Documentation sở hữu diagram artifact chuyên biệt. Không phát minh trải nghiệm, số liệu, benchmark hoặc production evidence để làm nội dung hấp dẫn hơn.

### P0 — strategy, research và series architecture

- `content-define-technical-content-strategy` — xác định audience, problem space, positioning, outcomes, channels, constraints và success signals; output: technical-content strategy brief.
- `content-research-technical-topic` — thu thập official sources, versioned facts, examples, controversies, failure modes và source limitations; output: technical-topic research pack.
- `content-verify-technical-versions` — xác minh version, environment, behavior khác biệt và ngày hiệu lực trước khi viết claim phụ thuộc thời gian; output: technical version matrix.
- `content-build-series-knowledge-map` — nối prerequisites, core concepts, mechanisms, contrasts, failure modes và follow-on topics; output: series knowledge map.
- `content-design-technical-series` — thiết kế narrative arc từ why và mental model tới mechanics, hands-on, production, trade-offs và capstone; output: technical-series architecture.
- `content-build-editorial-calendar` — xếp episode, channel, cadence, dependency, review, buffer và publish window; output: editorial calendar.
- `content-define-author-voice` — rút ra voice traits, rhythm, vocabulary, boundaries và anti-patterns mà không copy câu/ví dụ mẫu; output: author-voice guide.
- `content-create-episode-brief` — khóa central question, audience promise, evidence, example, code, diagram, failure và platform adaptations cho một episode; output: episode content brief.

### P1 — canonical production và channel adaptation

- `content-write-canonical-technical-article` — viết source-of-truth article có first principles, mechanisms, code, trade-offs, failures, limitations và references; output: canonical technical article.
- `content-build-code-example-package` — tạo runnable teaching/production-oriented examples, tests, setup, expected output và safety notes; output: validated code example package.
- `content-create-technical-diagram-brief` — mô tả message, entities, flow, evidence, labels, alt text và validation cho visual/diagram; output: technical diagram brief.
- `content-write-facebook-technical-post` — chuyển canonical evidence thành bài tiếng Việt dài, tự nhiên, giàu context, failure/trade-off và câu hỏi thảo luận, đồng thời giữ nguyên technical terms cần độ chính xác; output: Vietnamese Facebook technical post.
- `content-write-linkedin-technical-post` — chuyển một insight kỹ thuật thành bài tiếng Anh chuyên nghiệp, cô đọng, scannable, có evidence và takeaway; output: English LinkedIn technical post.
- `content-write-substack-technical-newsletter` — viết newsletter tiếng Anh chuyên sâu có subject, preheader, editorial opening, technical walkthrough, exercise, references và next-episode bridge; output: English Substack technical newsletter.
- `content-create-technical-carousel-script` — chuyển một mental model thành slide sequence có hook, progressive explanation, visual direction, alt text và takeaway; output: technical carousel script.
- `content-repurpose-technical-content` — biến canonical article thành channel-native variants mà không copy nguyên văn hoặc làm sai claim; output: cross-channel adaptation package.
- `content-package-technical-series-repository` — tổ chức roadmap, articles, research, code, tests, diagrams, social variants, status và contribution guidance; output: technical-series repository package.

### P2 — quality, release và continuous improvement

- `content-review-technical-accuracy` — kiểm tra facts, mechanisms, version specificity, abstraction/implementation boundary, examples và limitations; output: technical accuracy review.
- `content-audit-claim-source-traceability` — nối từng material claim tới source, test, runtime evidence hoặc nhãn opinion/hypothesis; output: content claim-traceability audit.
- `content-test-code-and-diagrams` — chạy code/tests và đối chiếu diagram với implementation hoặc evidence đã khai báo; output: content artifact validation report.
- `content-audit-series-concept-coverage` — map episode đã publish tới canonical concept ID để tách concept đã dạy khỏi concept chỉ nhắc tới, tìm prerequisite hở và trùng lặp; output: series concept coverage audit.
- `content-audit-author-voice-and-originality` — kiểm tra consistency, AI tells, cliché, copied phrasing, invented authority và channel duplication; output: voice and originality audit.
- `content-review-platform-fit` — kiểm tra length, structure, accessibility, CTA, hashtags, links, formatting và native-reader experience theo channel; output: platform-fit review.
- `content-publish-technical-content` — phát hành đúng approved version, metadata, links, alt text và schedule lên kênh đã được ủy quyền; output: technical-content publication record.
- `content-measure-series-performance` — đánh giá qualified readership, saves, discussion quality, completion, subscriptions và learning outcomes không chạy theo vanity metrics; output: series performance review.
- `content-refresh-technical-series` — cập nhật version drift, broken examples, stale claims, links và cross-channel variants rồi ghi changelog; output: refreshed technical-series release.
- `content-manage-content-backlog` — ưu tiên topic theo audience value, evidence readiness, dependency, effort, freshness và strategic fit; output: governed content backlog.

## Personal Data Project Engineering

Ranh giới: skill này sở hữu việc khám phá, lựa chọn, biến đổi nguồn cảm hứng, lập thesis, đánh giá repo tham chiếu, thiết kế khác biệt, roadmap và bằng chứng portfolio cho project cá nhân. Implementation chuyên môn phải handoff sang DA/AE/DE/DS/ML/BI/Platform/Architecture tương ứng. Repository hoặc ý tưởng của người khác luôn là nguồn có provenance; không được clone, đổi tên rồi tuyên bố là ý tưởng nguyên bản.

### P0 — intake, selection và project thesis

- `project-classify-starting-point` — phân loại evidence đầu vào, mức sở hữu, độ chắc chắn và project entry mode phù hợp; output: project starting-point classification.
- `project-select-project-mode` — chọn một primary mode và secondary inputs bằng routing rules có giải thích; output: personal-project mode decision.
- `project-score-project-options` — chấm các phương án theo value, role fit, evidence, differentiation, feasibility, data, testability, operations, risk, cost và sustainability; output: weighted project option scorecard.
- `project-build-personal-project-thesis` — khóa problem, target user, decision/outcome, hypothesis, contribution riêng và non-claims; output: personal-project thesis.
- `project-define-success-evidence` — nối outcome tới observable proof, tests, demo, artifacts và portfolio claims được phép; output: project success-evidence contract.
- `project-plan-originality-and-attribution` — phân loại self-originated/inspired/adapted/forked/replicated/contributed, attribution và giới hạn claim; output: originality and attribution plan.
- `project-plan-project-roadmap` — thiết kế phases, dependencies, milestones, gates, buffers và stop conditions; output: personal-project roadmap.
- `project-plan-portfolio-evidence` — chọn decisions, artifacts, tests, failures, trade-offs và narrative proof cần lưu; output: portfolio evidence plan.
- `project-bound-scope-and-constraints` — khóa time, cost, compute, data access, privacy, license, deployment và maintenance boundary; output: project scope and constraint contract.

### P0 — starting modes

- `project-start-problem-first` — bắt đầu từ pain point có thật, xác minh actor, consequence, current workaround và measurable outcome; output: problem-grounded project direction.
- `project-start-user-workflow-first` — bắt đầu từ workflow của người dùng, tìm friction, handoff, error và automation opportunity; output: workflow-grounded project direction.
- `project-start-decision-first` — bắt đầu từ quyết định cần cải thiện, xác định decision owner, inputs, uncertainty, latency và action; output: decision-grounded project direction.
- `project-start-idea-first` — bắt đầu từ ý tưởng do người dùng tự đề xuất rồi kiểm tra problem, user, feasibility và evidence value; output: self-idea project charter.
- `project-start-inspiration-first` — bắt đầu từ ý tưởng, bài viết, video, demo hoặc sản phẩm của người khác và chuyển thành thesis riêng có attribution; output: inspiration-derived project charter.
- `project-start-dataset-first` — bắt đầu từ dataset bằng inspection, profiling, fitness, limitations và viable decision/use-case generation; output: evidence-grounded project direction.
- `project-start-repo-first` — bắt đầu từ repository bằng provenance/license check, evidence-based audit, baseline execution, improvement matrix và thesis riêng; output: assessed and differentiated repo-first plan.
- `project-start-role-competency-first` — bắt đầu từ target role/gap, chọn project tạo đúng technical, judgment, operations và communication evidence; output: competency-evidence project direction.
- `project-start-technology-first` — bắt đầu từ công nghệ nhưng buộc chứng minh problem fit, learning value, alternatives và non-toy outcome; output: technology-grounded project charter.
- `project-start-domain-first` — bắt đầu từ business domain, lập entity/event/process/decision map rồi chọn bounded problem; output: domain-grounded project direction.
- `project-start-architecture-first` — bắt đầu từ architecture pattern hoặc system design question và khóa quality attributes, workload, alternatives, failure và proof; output: architecture-grounded project charter.
- `project-start-integration-first` — bắt đầu từ API, event, source/target hoặc interoperability gap và xác định contract, reliability, security, reconciliation; output: integration-grounded project direction.
- `project-start-open-source-issue-first` — bắt đầu từ issue thật, kiểm tra maintainer intent, contribution rules, reproducibility và contribution scope; output: contribution-grounded project plan.
- `project-start-paper-replication-first` — bắt đầu từ paper/experiment bằng hypothesis, environment, dataset, reproduction criteria và extension question; output: replication-and-extension project plan.
- `project-start-tutorial-course-first` — chuyển tutorial/course thành project độc lập bằng cách bỏ scaffold, thay constraints/data và thêm tests, failures, operations; output: tutorial-to-independent-project plan.
- `project-start-incident-failure-first` — bắt đầu từ failure scenario, tạo reproduction, detection, diagnosis, recovery và prevention evidence; output: reliability project charter.
- `project-start-constraint-first` — bắt đầu từ cost, privacy, latency, offline, scale, resource hoặc regulatory constraint; output: constraint-driven project direction.
- `project-start-benchmark-first` — bắt đầu từ performance/cost/correctness question với baseline, controlled variables, repetitions và limitations; output: benchmark-driven project plan.
- `project-start-governance-compliance-first` — bắt đầu từ policy/control/lineage/privacy/quality requirement và biến nó thành verifiable data control; output: governance-driven project charter.
- `project-start-hybrid-input-project` — hợp nhất nhiều input nhưng chọn một primary thesis, resolve conflicts và giữ provenance của từng input; output: hybrid-input project charter.

### P1 — deep assessment và execution design

- `project-audit-reference-repository` — nhận xét và đánh giá repo theo purpose, architecture, data flow, runtime, correctness, tests, security, dependencies, CI/CD, observability, performance, cost, documentation, maintainability, activity và license; output: evidence-backed repository assessment.
- `project-build-reuse-adapt-replace-matrix` — phân loại từng component thành reuse/adapt/replace/drop/build-new kèm evidence, reason, risk và validation; output: repository transformation matrix.
- `project-transform-borrowed-source-to-original-thesis` — biến repo hoặc ý tưởng ngoài thành thesis do người dùng sở hữu nhưng vẫn giữ attribution và giới hạn provenance claim; output: attributed differentiated project thesis.
- `project-design-project-differentiation` — tạo khác biệt có ý nghĩa theo problem/user, data/domain, architecture, reliability, governance, performance, operations, evaluation hoặc experience; output: project differentiation design.
- `project-plan-execution-and-milestones` — chuyển thesis thành vertical slices, milestones, task graph, test gates, demo checkpoints và recovery buffers; output: executable project milestone plan.
- `project-build-project-blueprint` — hợp nhất requirements, architecture, data contracts, interfaces, environments, risks, tests và handoffs trước implementation; output: implementation-ready project blueprint.
- `project-plan-project-validation-strategy` — thiết kế static, unit, contract, integration, reconciliation, security, performance, failure, usability và portfolio-proof checks; output: project validation strategy.

### P2 — assurance, portfolio và evolution

- `project-review-project-readiness` — kiểm tra thesis, rights, data, scope, architecture, dependencies, success evidence, cost và next owner trước build; output: project readiness decision.
- `project-audit-originality-and-attribution` — đối chiếu final artifacts với source origins, license, borrowed elements, differentiators và public claims; output: originality and attribution audit.
- `project-evaluate-portfolio-strength` — đánh giá depth, reproducibility, decisions, failures, trade-offs, operations, communication và role evidence; output: project portfolio-strength assessment.
- `project-evaluate-project-completion` — phân biệt planned, implemented, tested, demonstrated, released và maintained rồi kiểm tra Definition of Done; output: personal-project completion decision.
- `project-plan-project-maintenance` — thiết kế dependency updates, data/version drift, cost monitoring, issue handling, refresh và archival; output: personal-project maintenance plan.
- `project-design-next-version-evolution` — chọn next version từ real gaps/feedback thay vì feature accumulation và giữ backward evidence; output: evidence-driven project evolution plan.

## 30. Personal Second Brain / Knowledge OS

### P0 — purpose, architecture và migration

- `brain-assess-current-knowledge-system` — đánh giá nơi lưu, retrieval friction, duplication, portability, AI access, privacy và reuse baseline; output: current knowledge-system assessment.
- `brain-define-second-brain-purpose` — khóa users, decisions, recurring jobs, desired outputs, non-goals và success signals; output: second-brain purpose contract.
- `brain-classify-knowledge-domain` — xác định personal, career, technical, business, marketing, medical, creator hoặc mixed domain cùng risk boundary; output: knowledge-domain classification.
- `brain-design-four-layer-architecture` — thiết kế 1_Nguon, 2_Wiki, 3_Toi và 4_Ket-Qua với identity, flow và invariants; output: four-layer brain architecture.
- `brain-design-vault-taxonomy` — thiết kế folders, note types, tags, links, IDs, status và naming mà không tạo taxonomy quá sâu; output: vault taxonomy.
- `brain-define-source-rights-policy` — định nghĩa ownership, license, allowed processing, quotation, redistribution, retention và deletion; output: source-rights policy.
- `brain-define-personal-context-contract` — định nghĩa kinh nghiệm, preferences, voice, audiences và work rules được phép dùng cùng provenance; output: personal-context contract.
- `brain-define-output-contracts` — định nghĩa schema, audience, evidence, review, channel, version và done criteria theo từng output; output: second-brain output contracts.
- `brain-design-retrieval-routing` — map intents và queries tới note types, scopes, freshness, ranking và fallback; output: retrieval-routing design.
- `brain-plan-tool-migration` — lập kế hoạch export, inventory, transform, verify và cutover từ Notion, Sheets, Lark hoặc tool khác sang local-first vault; output: reversible knowledge migration plan.

### P1 — source ingestion và Wiki distillation

- `brain-inventory-distributed-sources` — inventory file, URL, export, note, image, video, transcript và spreadsheet theo owner, format, sensitivity, authority và last-used; output: distributed-source inventory.
- `brain-capture-source-material` — đưa nguồn mới vào 1_Nguon với stable ID, snapshot, checksum, origin, captured-at và rights; output: captured source record.
- `brain-import-exported-workspace` — import bounded exports từ Notion, Google Drive, Sheets, Lark hoặc bookmarks mà giữ links, attachments và source identity; output: imported workspace package.
- `brain-extract-multiformat-content` — trích text và structure từ PDF, EPUB, DOCX, HTML, Markdown, CSV và plain text bằng trusted local tools; output: normalized source extraction.
- `brain-transcribe-audio-video-source` — tạo transcript có timestamps, speaker uncertainty, language và media provenance; output: source-grounded transcript.
- `brain-process-image-and-diagram-source` — mô tả OCR, labels, relationships, uncertainty và link về ảnh gốc thay vì coi visual inference là fact; output: image knowledge record.
- `brain-normalize-source-metadata` — chuẩn hóa title, author, date, source type, canonical URL, edition, tags, sensitivity và authority; output: normalized source metadata.
- `brain-deduplicate-source-library` — phát hiện exact, near-duplicate, revised và syndicated sources mà không xóa evidence tùy tiện; output: source deduplication decision.
- `brain-build-source-provenance-record` — nối source ID tới origin, locator, snapshot hash, rights, ingestion method và transformations; output: source provenance record.
- `brain-distill-source-to-wiki-note` — chuyển nguồn thành Wiki note tách source facts, synthesis, inference, uncertainty, applications và citations; output: source-grounded Wiki note.
- `brain-build-atomic-knowledge-note` — tạo một note cho một concept hoặc decision có stable ID, aliases, status, source links và related notes; output: atomic knowledge note.
- `brain-build-concept-map` — nối prerequisites, concepts, mechanisms, contrasts, failures và applications; output: concept map.
- `brain-build-topic-map` — tạo map-of-content điều hướng một domain bằng questions và relationships thay vì folder dump; output: topic map.
- `brain-link-knowledge-graph` — tạo typed links giữa source, concept, person, project, decision và output đồng thời phát hiện orphan links; output: linked knowledge graph.
- `brain-resolve-knowledge-conflict` — giữ lại competing claims, editions, authority, dates và resolution owner thay vì silent overwrite; output: knowledge-conflict record.

### P1 — 3_Toi và khả năng tái sử dụng

- `brain-curate-personal-principles` — rút ra principles từ kinh nghiệm thật và gắn scope, counterexample, confidence, review date; output: personal-principle library.
- `brain-build-author-voice-profile` — mô hình hóa tone, rhythm, vocabulary, evidence style, prohibited patterns và channel variations mà không copy mẫu; output: author-voice profile.
- `brain-build-audience-context` — ghi audience problems, sophistication, language, objections, desired outcomes và sensitive boundaries; output: audience-context pack.
- `brain-build-work-rule-library` — mã hóa preferences, quality bars, decision rules, templates, exceptions và escalation; output: personal work-rule library.
- `brain-build-domain-second-brain` — cấu hình four-layer system cho một domain cụ thể và chỉ nạp rules/references phù hợp; output: domain-specific second-brain package.

### P2 — retrieval, output và reuse

- `brain-retrieve-task-context` — lấy minimum sufficient sources, Wiki notes và 3_Toi rules cho một task với authority, freshness và token budget; output: routed task context.
- `brain-build-grounded-context-pack` — đóng gói context có source locators, facts, inferences, personal rules, conflicts, omissions và expiry; output: prompt-ready grounded context pack.
- `brain-generate-grounded-output` — tạo output từ context pack và gắn material claims tới source hoặc personal-rule IDs; output: grounded second-brain output.
- `brain-reuse-prior-work` — tìm, đánh giá freshness và tái sử dụng decisions, templates, examples hoặc artifacts trước khi làm lại; output: prior-work reuse decision.
- `brain-create-content-from-brain` — tạo content từ Wiki và 3_Toi rồi handoff sang content skill khi cần production đa kênh; output: source-and-voice-grounded content draft.
- `brain-create-report-from-brain` — tổng hợp report có evidence, limitations, conflicts và next actions từ knowledge vault; output: grounded report.
- `brain-create-learning-plan-from-brain` — map known/unknown, prerequisites, sources, practice và retrieval checks thành learning plan; output: second-brain learning plan.
- `brain-create-project-plan-from-brain` — biến prior knowledge, constraints, decisions và evidence gaps thành project direction rồi handoff sang project skill; output: knowledge-grounded project plan.

### P2 — assurance và lifecycle

- `brain-test-retrieval-quality` — đo relevance, coverage, source authority, freshness, context precision và abstention trên representative query set; output: retrieval evaluation.
- `brain-audit-output-grounding` — kiểm tra mỗi material claim là sourced, inferred, personal hoặc unsupported và xác minh citations; output: output-grounding audit.
- `brain-run-privacy-freshness-audit` — kiểm tra secrets, sensitive personal data, permissions, stale notes, broken links, rights và retention; output: privacy-and-freshness audit.
- `brain-backup-second-brain` — tạo versioned encrypted backup, integrity hashes và recovery instructions cho vault; output: second-brain backup record.
- `brain-restore-second-brain` — phục hồi vào location tách biệt, kiểm tra integrity, links, indexes và representative retrieval trước cutover; output: verified restore record.
- `brain-run-knowledge-review-cycle` — review inbox, orphans, conflicts, stale notes, personal rules, outputs và improvement actions theo cadence; output: knowledge review record.
- `brain-retire-stale-knowledge` — deprecate hoặc archive note/source/output với reason, successor, retention và backlink repair; output: knowledge retirement record.
- `brain-measure-reuse-value` — đo time-to-find, reuse rate, grounded-output rate, search failure và avoided rework mà không chạy theo note count; output: second-brain value review.

## 31. Book to Knowledge / Skill / Action Engineering

### P0 — intake, rights và extraction

- `book-classify-conversion-purpose` — chọn primary destination là skill, second brain, career, interview, project, curriculum, workflow, content hoặc mixed có one primary output; output: book-conversion purpose decision.
- `book-assess-source-rights` — kiểm tra ownership, license, edition, quotation, processing, storage và publication rights trước conversion; output: source-rights decision.
- `book-inventory-source-collection` — inventory books, chapters, PDFs, EPUBs, notes và companion artifacts theo source identity và edition; output: book-source inventory.
- `book-identify-content-type` — phân loại technical, text-heavy, academic, reference, visual hoặc mixed để chọn extraction và depth; output: content-type decision.
- `book-estimate-conversion-budget` — ước tính extraction quality, token/time/cost, chapter budget, destination files và stop conditions; output: conversion budget estimate.
- `book-extract-source-text` — trích text local-first bằng format-aware tools, giữ source boundaries và không cài dependency ngoài khi chưa được phép; output: extracted source corpus.
- `book-recover-document-structure` — phục hồi headings, chapters, code, tables, formula, figure references và page/section locators; output: recovered document structure.
- `book-map-chapters-and-sections` — map table of contents, chapter boundaries, themes, source offsets và destination slices; output: chapter-source map.
- `book-verify-extraction-quality` — sample đầu/giữa/cuối, chapter boundaries, OCR, code/tables và missing-page signals; output: extraction quality report.
- `book-build-source-manifest` — ghi source/edition hash, rights, extraction method, locators, transformations và limitations; output: book source manifest.

### P1 — structural knowledge distillation

- `book-extract-frameworks` — trích named frameworks với exact name, purpose, conditions, steps, failure modes và source locators; output: framework cards.
- `book-extract-mental-models` — trích thinking models và nêu when-to-use, limits, contrasts và source evidence; output: mental-model library.
- `book-extract-principles` — chuyển principles thành decision-guiding rules mà không làm mất qualifier hoặc scope; output: principle library.
- `book-extract-techniques` — trích repeatable techniques, inputs, procedure, outputs, trade-offs và evidence; output: technique library.
- `book-extract-antipatterns` — trích what-not-to-do, detection signals, why-it-fails, exceptions và remedies; output: anti-pattern library.
- `book-extract-decision-rules` — trích if/then/because logic, thresholds, defaults, tells và escalation; output: decision-rule library.
- `book-extract-examples-and-cases` — synthesize worked examples, context, decision, outcome và limitation với bounded quotation; output: example-and-case pack.
- `book-extract-technical-artifacts` — trích code, commands, formulas, schemas và tables với syntax/version/source verification; output: technical-artifact pack.
- `book-build-concept-glossary` — tạo glossary chuẩn hóa aliases, definitions, chapter locators và related concepts; output: source-linked concept glossary.
- `book-build-topic-index` — map natural-language topics và questions tới chapter, framework và destination files; output: progressive topic index.
- `book-build-knowledge-graph` — nối chapters, prerequisites, concepts, frameworks, techniques, conflicts và applications; output: book knowledge graph.
- `book-resolve-author-claims` — phân biệt author claim, cited evidence, illustrative example, synthesis, disagreement và uncertainty; output: author-claim evidence map.
- `book-compare-multiple-books` — so sánh terminology, assumptions, frameworks, agreements, contradictions và applicability qua nhiều nguồn; output: multi-book comparison.

### P1 — destination compilers

- `book-build-agent-skill` — compile frameworks, routing, progressive references, assets và guardrails thành Claude-compatible skill; output: validated book-derived agent skill.
- `book-build-progressive-chapter-pack` — tạo chapter files on-demand có core idea, frameworks, worked examples, failures, takeaways và links; output: progressive chapter pack.
- `book-build-decision-cheatsheet` — compile decision trees, trade-off matrices, thresholds, defaults và smells thay vì glossary rút gọn; output: decision cheatsheet.
- `book-build-second-brain-pack` — đưa source vào 1_Nguon, distilled notes vào 2_Wiki, giữ chỗ cho 3_Toi và output contracts cho 4_Ket-Qua; output: book-to-second-brain package.
- `book-build-career-application-pack` — map book concepts tới competencies, deliberate practice, authentic evidence, reflection và career review; output: book-to-career application pack.
- `book-build-interview-knowledge-pack` — chuyển frameworks thành question dependencies, answer strategies, examples, trade-offs và novel retests; output: book-to-interview knowledge pack.
- `book-build-project-application-pack` — biến frameworks thành project hypotheses, decisions, constraints, experiments, artifacts và portfolio proof; output: book-to-project application pack.
- `book-build-curriculum-pack` — tạo objectives, prerequisites, theory, examples, labs, assessments, remediation và capstone từ book evidence; output: book-to-curriculum package.
- `book-build-technical-content-series` — chuyển source map thành canonical technical series và handoff evidence-bound production sang content skill; output: book-to-content series blueprint.
- `book-build-action-experiment-plan` — chọn behaviors hoặc decisions để thử, baseline, cadence, observation, stop rule và review; output: book application experiment.
- `book-build-workflow-checklists` — compile procedures, gates, exceptions, checklists và evidence requirements cho công việc lặp lại; output: book-derived workflow pack.
- `book-fold-into-existing-system` — merge source/version mới vào skill hoặc Second Brain mà preserve IDs, backlinks, conflicts và prior evidence; output: governed fold-in release.

### P2 — validation, publication và evolution

- `book-validate-derived-skill` — kiểm tra Claude format, triggering, progressive disclosure, broken links, token path và task behavior; output: derived-skill validation report.
- `book-audit-source-traceability` — sample và đối chiếu frameworks, rules, examples, technical artifacts với source locators và hashes; output: book traceability audit.
- `book-audit-copyright-and-privacy` — kiểm tra quotation length, redistribution, internal/confidential content, personal data và public/private boundary; output: copyright-and-privacy audit.
- `book-test-retrieval-and-application` — dùng unseen queries và scenarios để đo routing, citation, abstention và framework application; output: book knowledge evaluation.
- `book-detect-hallucinated-frameworks` — phát hiện invented names, merged concepts, missing qualifiers, false quotations và unsupported author voice; output: hallucination findings.
- `book-measure-knowledge-transfer` — đo recall, application, decision quality, artifact quality và changed-scenario transfer thay vì file count; output: knowledge-transfer review.
- `book-update-from-new-edition` — diff editions, classify changed/added/removed claims, update impacted packs và retain prior version; output: new-edition update release.
- `book-merge-source-versions` — reconcile duplicate, revised, translated và companion sources theo authority và stable identity; output: source-version merge decision.
- `book-publish-derived-skill` — publish exact scanned version chỉ khi rights và explicit public/private authority hợp lệ; output: derived-skill publication record.
- `book-retire-derived-knowledge` — deprecate stale framework hoặc generated pack với reason, successor, archive và backlink repair; output: derived-knowledge retirement record.

## 32. Data Documentation / Diagram Engineering

Ranh giới: đây là shared service cho BA, Architect, DE, AE, BI và ML; source of truth vẫn thuộc role tạo ra nghiệp vụ/thiết kế.

### P0 — diagram selection và modeling

- `docs-select-diagram-type` — chọn ERD, sequence, state, activity, swimlane, BPMN, use case hoặc architecture theo question; output: diagram decision.
- `docs-create-mermaid-activity-diagram` — mô hình hóa flow có branches/loops nhỏ; output: validated Mermaid activity diagram.
- `docs-create-swimlane-activity-diagram` — mô hình hóa multi-role process bằng PlantUML lanes; output: rendered swimlane diagram.
- `docs-create-bpmn-process` — tạo BPMN 2.0 có pools, lanes, events, gateways và semantic validation; output: valid BPMN artifact.
- `docs-create-d2-activity-diagram` — tạo standalone activity diagram bằng D2; output: D2 source and rendered image.
- `docs-create-architecture-diagram` — mô tả systems, services, stores và flows bằng D2; output: architecture diagram.
- `docs-create-mermaid-erd` — tạo inline ERD cho model nhỏ/trung bình; output: Mermaid ERD.
- `docs-create-d2-erd` — tạo standalone ERD dễ đọc cho model phức tạp; output: D2 ERD.
- `docs-create-dbml-schema` — tạo DBML có types, keys, indexes và exportable SQL; output: validated DBML schema.
- `docs-create-sequence-diagram` — mô tả actors/services/messages/alternatives theo thời gian; output: sequence diagram.
- `docs-create-state-diagram` — mô tả states, triggers, valid và invalid transitions; output: state model.
- `docs-create-usecase-diagram` — mô tả actors, system boundary và include/extend; output: use-case diagram.
- `docs-validate-diagram-semantics` — kiểm tra missing node, dead end, cardinality, direction và domain correctness; output: diagram QA report.

### P1 — document artifacts

- `docs-write-architecture-document` — ghi context, components, flows, qualities và decisions; output: architecture document.
- `docs-write-api-documentation` — ghi contract, auth, examples, errors và versioning; output: API documentation.
- `docs-write-data-documentation` — ghi sources, models, metrics, lineage và caveats; output: data documentation.
- `docs-write-operational-runbook` — ghi symptoms, diagnosis, recovery, escalation và verification; output: runbook.
- `docs-write-postmortem` — ghi impact, timeline, root cause và actions; output: postmortem.
- `docs-write-release-notes` — tóm tắt changes, impact, migration và known issues; output: release notes.
- `docs-maintain-changelog` — cập nhật versioned change history từ release evidence; output: changelog.

## 33. Bổ sung BI delivery lifecycle từ BI Report Platform

Các task dưới đây mở rộng role BI/DA/DG hiện có bằng control-plane và evidence artifacts còn thiếu.

- `bi-run-discovery-dialogue` — hỏi thích ứng, không lặp và ghi question/answer/conflict; output: discovery register.
- `bi-assess-information-sufficiency` — phân loại confirmed/inferred/blocking/conflicting; output: sufficiency decision.
- `bi-build-business-domain-brief` — mô hình hóa process, entity, event, state và policy; output: domain brief.
- `bi-build-source-authority-matrix` — chọn nguồn chuẩn theo KPI/dimension/use case; output: BI authority matrix.
- `bi-maintain-evidence-ledger` — nối claim/metric/visual tới query và evidence status; output: evidence ledger.
- `bi-create-cleaning-transformation-plan` — thiết kế reversible, idempotent cleaning và reconciliation; output: transformation plan.
- `bi-create-platform-neutral-report-spec` — định nghĩa pages, visuals, filters, interactions và accessibility; output: neutral report spec.
- `bi-author-analytical-report` — viết report có methods, findings, limitations và recommendations; output: analytical report.
- `bi-review-report-section` — kiểm tra và xin approval theo từng section; output: section approval status.
- `bi-validate-report-claims` — phát hiện unsupported claim, semantic drift và missing evidence; output: report QA findings.
- `bi-export-analytical-report` — render approved source thành Markdown/PDF có kiểm tra; output: published report files.
- `bi-run-independent-uat` — kiểm tra numerical, structural, visual, security, accessibility và operations; output: UAT evidence.
- `bi-prepare-release-approval` — gom approved gates, open risks, version và target environment; output: release package.
- `bi-maintain-report-product` — xử lý source/metric/platform change và regression validation; output: maintained BI release.
- `bi-reconcile-dashboard-report` — đảm bảo KPI, filters, claims và limitations nhất quán; output: reconciliation report.

## 34. Orchestration, state và evidence control plane

Đây là task modules của `data-department-orchestrator`, bổ sung từ Data OS và BI Report Platform.

- `orchestrator-hydrate-context` — nạp project, role, decisions, constraints, stack và permissions; output: hydrated context.
- `orchestrator-start-repo-first-project` — bắt đầu từ repository hiện có bằng audit, learning và redesign diff; output: repo-grounded project plan.
- `orchestrator-start-idea-first-project` — bắt đầu từ business idea qua discovery, product và feasibility gates; output: baselined project charter.
- `orchestrator-start-dataset-first-project` — bắt đầu từ dataset bằng profiling, direction generation và fitness assessment; output: evidence-grounded project direction.
- `orchestrator-compose-workflow` — chuyển intent thành steps, dependencies, gates và handoffs; output: workflow plan.
- `orchestrator-run-sequential-workflow` — truyền verified output giữa dependent tasks; output: completed chain.
- `orchestrator-run-parallel-workflow` — chạy independent checks và hợp nhất kết quả; output: merged result.
- `orchestrator-run-conditional-workflow` — chọn branch theo evidence/status/threshold; output: branch decision and execution.
- `orchestrator-run-fanout-fanin` — phân tách một artifact cho nhiều reviewers rồi synthesize; output: consolidated assessment.
- `orchestrator-run-producer-reviewer` — chạy vòng producer/reviewer độc lập với rubric chốt trước, giữ kín lập luận của producer tới khi reviewer ghi verdict, và đưa bất đồng chưa giải vào conflict register; output: producer-reviewer verdict record.
- `orchestrator-maintain-run-state` — lưu lifecycle phase, current task, blockers và next permitted action; output: run-state record.
- `orchestrator-resume-workflow` — phục hồi context từ run state và ledgers mà không làm lại approved work; output: resumed execution plan.
- `orchestrator-check-information-sufficiency` — xác định thiếu blocking/nonblocking và conflicts; output: proceed/ask/stop decision.
- `orchestrator-manage-question-register` — deduplicate, prioritize và close questions bằng evidence; output: question register.
- `orchestrator-manage-assumption-register` — ghi source, impact, expiry và confirmation status; output: assumption register.
- `orchestrator-manage-conflict-register` — ghi contradictory inputs, owners và resolution; output: conflict register.
- `orchestrator-manage-approval-ledger` — lưu gate, scope, approver, version và decision; output: approval ledger.
- `orchestrator-manage-evidence-ledger` — lưu artifact, provenance, claim và validation status; output: evidence ledger.
- `orchestrator-enforce-phase-gate` — ngăn task vượt lifecycle khi prerequisites chưa approved; output: gate decision.
- `orchestrator-evaluate-workflow-completion` — đối chiếu deliverables, validations, approvals và open risks; output: completion decision.

## 35. Adapter layer — công cụ không phải nhiệm vụ

Adapter chỉ chứa cách thực hiện một task trên công cụ cụ thể. Không tạo lại task business với tên công cụ.

### Data platform adapters

- Airflow: DAG, connections, sensors, backfill và deployment.
- BigQuery: datasets, partition/clustering, IAM, reservations và cost controls.
- dbt: project structure, models, tests, docs, artifacts và deployment.
- Spark: batch/stream transformations, partitioning, shuffle và tuning.
- Docker: reproducible runtime và image security.
- Kubernetes: workload, autoscaling, secrets và operations.
- Terraform/Pulumi: infrastructure modules, state và policy checks.
- DataHub/OpenMetadata: harvesting, lineage, ownership và search.

### BI platform adapters

- Power BI: PBIP/PBIR/TMDL, DAX, RLS, validation và publish gates.
- Tableau: data sources, calculations, workbooks và supported deployment interfaces.
- Superset: datasets, charts, dashboards, permissions và import bundles.
- Metabase: models, questions, dashboards, collections và APIs.
- Looker Studio: connectors, calculated fields, pages và deployment plan.
- HTML/JavaScript: testable dashboard scaffold, data adapters và ECharts.

### Diagram adapters

- Mermaid: inline ERD, sequence, state và activity.
- PlantUML: use case và true swimlane activity.
- BPMN 2.0: standards-compliant process exchange.
- D2: standalone architecture, activity và ERD rendering.
- DBML: database schema handoff và SQL export.

## 36. Industry và metric knowledge packs

Các pack này là references được role skill tải theo domain, không phải role hoặc workflow mới.

### Industry packs

- Automotive
- Ecommerce
- EdTech
- Energy
- FinTech/Banking
- Gaming
- Healthcare
- Logistics
- Manufacturing
- Media and Entertainment
- Real Estate
- Retail
- SaaS B2B
- Telecom
- Travel and Hospitality

### Metric packs

- Core business metrics
- Finance metrics
- Sales and pipeline metrics
- Marketing and attribution metrics
- Product and growth metrics
- Retention and churn metrics
- SaaS metrics
- Operations and supply-chain metrics
- People analytics metrics

## 37. Handoff chuẩn giữa các role

### Business Intelligence lifecycle

```text
DPM intake
→ DA clarify question and define metric requirement
→ DG resolve term and ownership
→ Architect approve cross-system design when needed
→ DE ingest/conform source data
→ AE build mart and semantic metric
→ DQ validate and certify quality readiness
→ DG certify metric/data asset
→ BI Engineer build and publish dashboard
→ DA validate insight and communicate decision
→ DRE monitor reliability
```

### Machine Learning lifecycle

```text
DPM frame opportunity
→ DS frame problem, build and validate candidate
→ DG/Privacy/Security assess data and model risk
→ ML Engineer productionize and test serving
→ MLOps register, approve and deploy
→ MLOps/DRE monitor service, drift and performance
→ DS evaluate business/model degradation
→ MLOps retrain, promote or rollback
```

## 38. Ranh giới ownership quan trọng

| Artifact | Responsible | Accountable/Approver | Consulted |
|---|---|---|---|
| Business question | DA | Business owner | DPM |
| Metric requirement | DA | Business owner | DG, AE |
| Semantic metric code | AE | Data product owner | DA, DG |
| Metric certification | DG | Business/data owner | DA, AE, DQ |
| Source ingestion | DE | Data engineering owner | Architect, Platform, DQ |
| Analytical mart | AE | Analytics engineering owner | DA, DG, DQ |
| Dashboard implementation | BI Engineer | BI/Data product owner | DA, AE |
| Architecture decision | Data Architect | Architecture authority | DE, AE, Platform, Security |
| Data policy | DG | Governance council/DPO | Security, Legal, role owners |
| Model candidate | DS | DS lead/business owner | DG, ML Engineer |
| Production model service | ML Engineer | ML engineering owner | DS, MLOps, Security |
| Model deployment | MLOps | ML platform/model risk approver | ML Engineer, DS |
| Data/ML incident | DRE or MLOps | Service owner | DE/AE/DS/Security |

## 39. Quy tắc chống skill explosion

Chỉ tách một task thành sub-skill độc lập khi đáp ứng ít nhất ba điều kiện:

- Có trigger riêng biệt.
- Có deliverable riêng biệt.
- Có validation riêng biệt.
- Có thể được gọi lại trong nhiều workflow.
- Có risk/approval gate riêng.
- Cần script, template hoặc reference riêng.

Không tách các bước như `mở file`, `viết SQL`, `chạy test`, `tạo chart` thành skill độc lập nếu chúng chỉ là thao tác bên trong một nhiệm vụ hoàn chỉnh.

## 40. Thứ tự triển khai khuyến nghị

### Wave 0 — control plane

1. `data-department-orchestrator`
2. `shared-data-core`
3. Company context pack: glossary, schemas, metrics, owners, policies, stack và environments

### Wave 1 — đường đi từ request đến trusted analytics

1. `data-business-analysis`
2. `data-analysis`
3. `data-engineering`
4. `analytics-engineering`
5. `data-quality-and-reliability`
6. `data-governance-and-stewardship`
7. `metadata-engineering-and-catalog`
8. `business-intelligence`

### Wave 2 — production platform

1. `data-architecture`
2. `data-platform-and-dataops`
3. `data-security-and-privacy`
4. `head-of-data-and-data-product`
5. `data-developer-experience`
6. `data-documentation-and-diagrams`

### Wave 3 — AI/ML

1. `data-science`
2. `machine-learning-engineering`
3. `mlops`
4. `generative-ai-engineering`

### Wave 4 — specialized enterprise capabilities

1. `product-analytics-and-experimentation`
2. `master-data-management`
3. `data-enablement-and-knowledge`
4. `data-academy-and-curriculum`
5. `data-onboarding-and-integration`
6. `data-talent-acquisition-and-interview`
7. `data-career-and-interview-coach`
8. Các industry, metric và technology adapter packs

## 41. Tiêu chí hoàn thành giai đoạn taxonomy

- Mọi nhiệm vụ quan trọng của mỗi role có đúng một primary owner.
- Không có hai sub-skill trùng deliverable và validation.
- Mọi handoff có artifact rõ ràng.
- Mọi production mutation và sensitive-data action có approval gate.
- Mỗi role có một P0 end-to-end workflow có thể test bằng tình huống thật.
- Có thể thêm tech stack cụ thể mà không phải thay đổi taxonomy nghiệp vụ.
