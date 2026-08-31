# Chi tiết toàn bộ Data Department Skills và Atomic Tasks

> Phiên bản `3.10.0` · `33` Claude role skills · `865` atomic workflows.
> Đây là catalog tra cứu đầy đủ được sinh từ `suite-manifest.yaml`, `task-catalog.json` và task contracts; không phải nội dung luôn được nạp vào context của Claude.

## Mục lục

- [1. Bộ skill này là gì](#1-bộ-skill-này-là-gì)
- [2. Cách đọc catalog](#2-cách-đọc-catalog)
- [3. Lifecycle và kiểm soát chung](#3-lifecycle-và-kiểm-soát-chung)
- [4. Bản đồ 33 skills](#4-bản-đồ-33-skills)
- [5. Chi tiết từng skill và toàn bộ task](#5-chi-tiết-từng-skill-và-toàn-bộ-task)
- [6. Cách chọn skill/task](#6-cách-chọn-skilltask)

## 1. Bộ skill này là gì

`data-department-agent-skills` là một operating system theo role cho toàn bộ phòng Data. Claude nhận đề bài bằng ngôn ngữ tự nhiên, chọn role theo ownership của primary deliverable, chọn đúng một atomic task, rồi áp dụng lifecycle và risk controls tương ứng.

```text
User request / đề bài / repository
→ role routing
→ primary deliverable
→ one atomic task
→ Plan → Assess → Design → Execute → Test
→ Review/Approve → Release/Handoff → Monitor/Improve
```

Một atomic task là một đơn vị công việc có một deliverable chính và Definition of Done riêng. Task contract đầy đủ quy định trigger, goal, inputs/readiness, procedure, tests/evidence, approval, failure state và handoff.

## 2. Cách đọc catalog

Mỗi dòng task bên dưới có:

- **Task ID:** định danh ổn định để routing và handoff; bình thường người dùng không cần nhớ.
- **Nhiệm vụ:** outcome mà task phải đạt, không phải một thao tác nhỏ.
- **Deliverable:** artifact chính dùng để chọn task khi nhiều task có từ khóa gần nhau.
- **Lifecycle:** profile điều khiển mức độ planning, execution và verification.
- **Risk / path:** mức kiểm soát và execution path tối thiểu.
- **Contract:** liên kết tới file hướng dẫn đầy đủ Claude sẽ đọc sau khi task được chọn.

Bốn catalog được tải theo nhu cầu để tối ưu token:

| Catalog | Dùng cho |
|---|---|
| Plan / Design | Plan, define, design, map, specify hoặc tạo proposed artifact |
| Build / Deliver | Build, implement, configure, teach, interview hoặc deliver artifact |
| Test / Assure | Inspect, analyze, test, review, validate, assess, certify hoặc audit |
| Operate / Improve | Deploy, release, monitor, recover, migrate, optimize, retire hoặc improve |

## 3. Lifecycle và kiểm soát chung

| Stage | Kết quả bắt buộc |
|---|---|
| Plan | Outcome, scope, owner, consumer, dependency, acceptance criteria và test strategy |
| Assess | Current-state evidence, baseline, validated inputs, risk tier và blockers |
| Design | Approach, alternatives, controls, observability và recovery path |
| Execute | Versioned artifact/change trong môi trường và authority cho phép |
| Test | Correctness, semantics, quality, integration, security/privacy, performance/recovery khi áp dụng |
| Review / Approve | Findings được xử lý và accountable authority duyệt đúng version/scope |
| Release / Handoff | Đúng artifact đã test được publish/deploy/bàn giao kèm evidence và owner |
| Monitor / Improve | Outcome được quan sát; residual actions có owner và feedback quay lại quy trình |

| Risk | Typical work | Control tối thiểu |
|---|---|---|
| R0-light | Read-only lookup, bounded analysis | Evidence và self-check |
| R1-reviewed | Design, documentation, learning/advisory | Peer hoặc domain review |
| R2-standard | Reversible build, people workflow | Practical/automated test và owner review |
| R3-controlled | Production, access, sensitive, external, material cost | Independent test, explicit approval, rollback, monitoring |
| R4-critical | Destructive, regulatory, breach, certified/high-impact decision | Segregated approval, strongest evidence, rehearsed recovery, audit trail |

### Slash commands

Mười ba lệnh điều khiển cộng 32 lệnh phòng ban (mỗi role một lệnh `/dd-<role>`, nhóm theo sprint stage think / plan / build / review / test / ship / reflect). Routing ngầm bằng ngôn ngữ tự nhiên vẫn hoạt động như cũ.

| Lệnh | Dùng để |
|---|---|
| `/dd-route` | Định tuyến một đề bài về đúng một role và một atomic task, chưa thực thi |
| `/dd-catalog` | Tra cứu task ID theo từ khóa, role prefix hoặc deliverable |
| `/dd-task` | Nạp trọn vẹn một task contract và báo cáo readiness, gates, tests, approvals |
| `/dd-status` | Báo cáo run state đã được validate, blockers và next permitted action |
| `/dd-verify` | Chạy chuỗi evidence thực thi và trả verdict passed / failed / incomplete |
| `/dd-approve` | Kiểm tra approval record có thực sự cho phép hành động gated tại thời điểm hiện tại |
| `/dd-handoff` | Sinh handoff package với evidence, assumptions, residual risks và next owner |
| `/dd-constitution` | Chốt và cưỡng chế hiến pháp dự án: tech stack khóa và luật kiến trúc chặn |
| `/dd-scan` | Đo structural drift: cycles, độ sâu phụ thuộc, coupling, trùng lặp |
| `/dd-recall` | Truy hồi trí nhớ tất định, 0 model call, trả về con trỏ source:line |
| `/dd-navigate` | Trả lời câu hỏi code từ symbol index thay vì đọc cả file |
| `/dd-instinct` | Ghi nhận và chấm điểm instinct; confidence tính từ kết quả đếm được |
| `/dd-skill-quality` | Chấm chất lượng task contract theo outcome đã ghi nhận |

### Production guard

`hooks/guard_production_action.py` chặn trước các lệnh shell mang tính production, publishing hoặc phá hủy (push, terraform apply/destroy, kubectl apply, dbt --target prod, drop/truncate, delete không có where, gh release create, rm -rf) và chuyển sang quyết định tường minh của con người.

Guard chỉ trả `ask`, không bao giờ tự `deny`: quyền quyết định thuộc về người dùng. Nếu payload không đọc được hoặc Python không khả dụng, guard thoát im lặng và luồng permission mặc định của Claude Code được giữ nguyên — một lỗi môi trường không bao giờ được âm thầm nới quyền.

## 4. Bản đồ 33 skills

| # | Skill | Role | Tasks |
|---:|---|---|---:|
| 1 | [`data-department-orchestrator`](#skill-data-department-orchestrator) | Data Department Orchestrator | 27 |
| 2 | [`shared-data-core`](#skill-shared-data-core) | Shared Data Core | 18 |
| 3 | [`company-data-context`](#skill-company-data-context) | Company Data Context | 9 |
| 4 | [`head-of-data-and-data-product`](#skill-head-of-data-and-data-product) | Head of Data and Data Product | 21 |
| 5 | [`data-business-analysis`](#skill-data-business-analysis) | Data Business Analysis | 24 |
| 6 | [`data-architecture`](#skill-data-architecture) | Data Architecture | 22 |
| 7 | [`data-governance-and-stewardship`](#skill-data-governance-and-stewardship) | Data Governance and Stewardship | 22 |
| 8 | [`metadata-engineering-and-catalog`](#skill-metadata-engineering-and-catalog) | Metadata Engineering and Catalog | 18 |
| 9 | [`data-platform-and-dataops`](#skill-data-platform-and-dataops) | Data Platform and DataOps | 21 |
| 10 | [`data-developer-experience`](#skill-data-developer-experience) | Data Developer Experience | 20 |
| 11 | [`data-engineering`](#skill-data-engineering) | Data Engineering | 25 |
| 12 | [`analytics-engineering`](#skill-analytics-engineering) | Analytics Engineering | 22 |
| 13 | [`data-analysis`](#skill-data-analysis) | Data Analysis | 29 |
| 14 | [`business-intelligence`](#skill-business-intelligence) | Business Intelligence | 32 |
| 15 | [`product-analytics-and-experimentation`](#skill-product-analytics-and-experimentation) | Product Analytics and Experimentation | 17 |
| 16 | [`data-science`](#skill-data-science) | Data Science | 22 |
| 17 | [`machine-learning-engineering`](#skill-machine-learning-engineering) | Machine Learning Engineering | 20 |
| 18 | [`mlops`](#skill-mlops) | MLOps | 23 |
| 19 | [`data-quality-and-reliability`](#skill-data-quality-and-reliability) | Data Quality and Reliability | 21 |
| 20 | [`data-security-and-privacy`](#skill-data-security-and-privacy) | Data Security and Privacy | 16 |
| 21 | [`technical-translation`](#skill-technical-translation) | Technical Translation | 17 |
| 22 | [`master-data-management`](#skill-master-data-management) | Master Data Management | 13 |
| 23 | [`generative-ai-engineering`](#skill-generative-ai-engineering) | Generative AI Engineering | 24 |
| 24 | [`data-documentation-and-diagrams`](#skill-data-documentation-and-diagrams) | Data Documentation and Diagrams | 20 |
| 25 | [`data-enablement-and-knowledge`](#skill-data-enablement-and-knowledge) | Data Enablement and Knowledge | 17 |
| 26 | [`data-academy-and-curriculum`](#skill-data-academy-and-curriculum) | Data Academy and Curriculum | 49 |
| 27 | [`data-onboarding-and-integration`](#skill-data-onboarding-and-integration) | Data Onboarding and Integration | 34 |
| 28 | [`data-talent-acquisition-and-interview`](#skill-data-talent-acquisition-and-interview) | Data Talent and Interviewing | 41 |
| 29 | [`data-career-and-interview-coach`](#skill-data-career-and-interview-coach) | Data Career and Interview Coach | 57 |
| 30 | [`data-technical-content-and-social`](#skill-data-technical-content-and-social) | Technical Content and Social | 27 |
| 31 | [`data-personal-project-engineering`](#skill-data-personal-project-engineering) | Personal Data Project Engineering | 42 |
| 32 | [`personal-second-brain-and-knowledge-os`](#skill-personal-second-brain-and-knowledge-os) | Personal Second Brain and Knowledge OS | 50 |
| 33 | [`book-to-knowledge-and-action`](#skill-book-to-knowledge-and-action) | Book to Knowledge and Action | 45 |

## 5. Chi tiết từng skill và toàn bộ task

<a id="skill-data-department-orchestrator"></a>

### 1. `data-department-orchestrator` — Data Department Orchestrator

**Claude trigger description:** Route ambiguous, organizational or multi-role Data Department requests and compose governed workflows with owners, dependencies, gates and handoffs. Use for cross-role repository rebuilds or end-to-end initiatives combining discovery, implementation and proof; route personal learning or portfolio projects to Personal Data Project Engineering.

**Ownership:** Điều phối yêu cầu mơ hồ, end-to-end hoặc có nhiều role; phân rã initiative thành chuỗi atomic task có owner, dependency, gate và handoff.

**Khi nên dùng:** Dùng khi đề bài chứa nhiều deliverable, cần dựng lại một repository, hoặc chưa rõ role nào sở hữu kết quả cuối.

**Ranh giới và handoff:** Không thay chuyên môn của các role. Mỗi task chỉ có một accountable owner; orchestrator quản lý workflow state, approval và thứ tự thực thi.

**Quy mô:** 27 tasks — Plan / Design 3; Build / Deliver 20; Test / Assure 4; Operate / Improve 0.

**Domain references tải khi cần:** `agent-harness-standard.md`, `context-engineering-standard.md`, `external-tool-access.md`, `harness-delivery-loop.md`, `learning-memory-interoperability.md`, `model-selection.md`, `parallel-execution-and-agent-teams.md`, `producer-reviewer-method.md`, `response-compression.md`, `solution-option-framing.md`, `workflow-runtime-and-evidence-os.md`.

**Templates/assets có thể tái sử dụng:** `agent-harness.yaml`, `approval-ledger.yaml`, `approval-record.json`, `approval-record.schema.json`, `assumption-register.yaml`, `atomic-task-output.yaml`, `branch-delegation-contract.json`, `change-scope-contract.json`, `change-scope-ledger.yaml`, `conflict-register.yaml`, `debug-hypothesis-ledger.yaml`, `design-option-set.yaml`, `evidence-ledger.yaml`, `fan-in-merge-record.yaml`, `handoff-package.yaml`, `harness-approval.yaml`, `harness-readiness-audit.yaml`, `harness-stop-log.json`, `instinct-ledger.json`, `instinct-record.schema.json`, `producer-reviewer-record.yaml`, `question-register.yaml`, `run-state.schema.json`, `run-state.yaml`, `session-handoff.yaml`, `stage-gate.yaml`, `success-contract.yaml`, `task-catalog.json`, `task-contract.schema.json`, `telemetry-event.json`, `telemetry-event.schema.json`, `test-evidence.yaml`, `verification-claims.yaml`, `work-ledger.yaml`, `workflow-manifest.json`, `workflow-manifest.schema.json`.

**Scripts:** `analyze_skill_telemetry.py`, `manage_instincts.py`, `record_skill_telemetry.py`, `score_skill_quality.py`, `validate_approval_record.py`, `validate_branch_plan.py`, `validate_run_state.py`, `validate_workflow.py`.

#### Plan / Design (3 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`orchestrator-collect-plan-risk`](skills/data-department-orchestrator/references/tasks/orchestrator-collect-plan-risk.md) | gom mọi thao tác rủi ro mà kế hoạch hàm ý để duyệt một lần lúc lập kế hoạch, kèm hạn dùng và số lần | plan-time risk approval set | `advisory-analysis` | `R2-standard` / `standard-path` |
| [`orchestrator-define-agent-harness`](skills/data-department-orchestrator/references/tasks/orchestrator-define-agent-harness.md) | khai báo phạm vi, grounding, tool surface, guardrail, eval và môi trường cho một agent theo vai | agent harness specification | `design-specification` | `R1-reviewed` / `standard-path` |
| [`orchestrator-write-session-handoff`](skills/data-department-orchestrator/references/tasks/orchestrator-write-session-handoff.md) | ghi lại suy luận mà run state không giữ được khi một phiên kết thúc dở dang | session handoff note | `design-specification` | `R1-reviewed` / `standard-path` |

#### Build / Deliver (20 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`orchestrator-compose-workflow`](skills/data-department-orchestrator/references/tasks/orchestrator-compose-workflow.md) | chuyển intent thành steps, dependencies, gates và handoffs | workflow plan | `advisory-analysis` | `R0-light` / `fast-path` |
| [`orchestrator-enforce-phase-gate`](skills/data-department-orchestrator/references/tasks/orchestrator-enforce-phase-gate.md) | ngăn task vượt lifecycle khi prerequisites chưa approved | gate decision | `build-change` | `R2-standard` / `standard-path` |
| [`orchestrator-hydrate-context`](skills/data-department-orchestrator/references/tasks/orchestrator-hydrate-context.md) | nạp project, role, decisions, constraints, stack và permissions | hydrated context | `advisory-analysis` | `R0-light` / `fast-path` |
| [`orchestrator-maintain-run-state`](skills/data-department-orchestrator/references/tasks/orchestrator-maintain-run-state.md) | lưu lifecycle phase, current task, blockers và next permitted action | run-state record | `advisory-analysis` | `R0-light` / `fast-path` |
| [`orchestrator-manage-approval-ledger`](skills/data-department-orchestrator/references/tasks/orchestrator-manage-approval-ledger.md) | lưu gate, scope, approver, version và decision | approval ledger | `advisory-analysis` | `R0-light` / `fast-path` |
| [`orchestrator-manage-assumption-register`](skills/data-department-orchestrator/references/tasks/orchestrator-manage-assumption-register.md) | ghi source, impact, expiry và confirmation status | assumption register | `advisory-analysis` | `R0-light` / `fast-path` |
| [`orchestrator-manage-conflict-register`](skills/data-department-orchestrator/references/tasks/orchestrator-manage-conflict-register.md) | ghi contradictory inputs, owners và resolution | conflict register | `advisory-analysis` | `R0-light` / `fast-path` |
| [`orchestrator-manage-evidence-ledger`](skills/data-department-orchestrator/references/tasks/orchestrator-manage-evidence-ledger.md) | lưu artifact, provenance, claim và validation status | evidence ledger | `advisory-analysis` | `R0-light` / `fast-path` |
| [`orchestrator-manage-question-register`](skills/data-department-orchestrator/references/tasks/orchestrator-manage-question-register.md) | deduplicate, prioritize và close questions bằng evidence | question register | `advisory-analysis` | `R0-light` / `fast-path` |
| [`orchestrator-package-agent-harness`](skills/data-department-orchestrator/references/tasks/orchestrator-package-agent-harness.md) | đóng gói harness đã khai báo thành thứ chạy lại được và bàn giao được, ghim mọi phiên bản đầu vào | packaged agent harness | `build-change` | `R2-standard` / `standard-path` |
| [`orchestrator-resume-workflow`](skills/data-department-orchestrator/references/tasks/orchestrator-resume-workflow.md) | phục hồi context từ run state và ledgers mà không làm lại approved work | resumed execution plan | `advisory-analysis` | `R2-standard` / `standard-path` |
| [`orchestrator-run-conditional-workflow`](skills/data-department-orchestrator/references/tasks/orchestrator-run-conditional-workflow.md) | chọn branch theo evidence/status/threshold | branch decision and execution | `advisory-analysis` | `R2-standard` / `standard-path` |
| [`orchestrator-run-delivery-loop`](skills/data-department-orchestrator/references/tasks/orchestrator-run-delivery-loop.md) | chạy vòng Plan/Work/Review/Ship với cổng chặn giữa mỗi chặng và ghi mọi lần bị chặn | delivery loop record | `advisory-analysis` | `R2-standard` / `standard-path` |
| [`orchestrator-run-fanout-fanin`](skills/data-department-orchestrator/references/tasks/orchestrator-run-fanout-fanin.md) | phân tách một artifact cho nhiều reviewers rồi synthesize | consolidated assessment | `advisory-analysis` | `R2-standard` / `standard-path` |
| [`orchestrator-run-parallel-workflow`](skills/data-department-orchestrator/references/tasks/orchestrator-run-parallel-workflow.md) | chạy independent checks và hợp nhất kết quả | merged result | `advisory-analysis` | `R2-standard` / `standard-path` |
| [`orchestrator-run-producer-reviewer`](skills/data-department-orchestrator/references/tasks/orchestrator-run-producer-reviewer.md) | chạy vòng producer/reviewer độc lập với rubric chốt trước, giữ kín lập luận của producer tới khi reviewer ghi verdict, và đưa bất đồng chưa giải vào conflict register | producer-reviewer verdict record | `advisory-analysis` | `R2-standard` / `standard-path` |
| [`orchestrator-run-sequential-workflow`](skills/data-department-orchestrator/references/tasks/orchestrator-run-sequential-workflow.md) | truyền verified output giữa dependent tasks | completed chain | `advisory-analysis` | `R2-standard` / `standard-path` |
| [`orchestrator-start-dataset-first-project`](skills/data-department-orchestrator/references/tasks/orchestrator-start-dataset-first-project.md) | bắt đầu từ dataset bằng profiling, direction generation và fitness assessment | evidence-grounded project direction | `advisory-analysis` | `R0-light` / `fast-path` |
| [`orchestrator-start-idea-first-project`](skills/data-department-orchestrator/references/tasks/orchestrator-start-idea-first-project.md) | bắt đầu từ business idea qua discovery, product và feasibility gates | baselined project charter | `advisory-analysis` | `R0-light` / `fast-path` |
| [`orchestrator-start-repo-first-project`](skills/data-department-orchestrator/references/tasks/orchestrator-start-repo-first-project.md) | bắt đầu từ repository hiện có bằng audit, learning và redesign diff | repo-grounded project plan | `advisory-analysis` | `R0-light` / `fast-path` |

#### Test / Assure (4 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`orchestrator-audit-agent-harness`](skills/data-department-orchestrator/references/tasks/orchestrator-audit-agent-harness.md) | đối chiếu harness đang chạy với bản khai báo, kiểm quyền thừa, gate bị nới và eval đã cũ | harness readiness audit | `governance-assurance` | `R1-reviewed` / `standard-path` |
| [`orchestrator-audit-runtime-floor`](skills/data-department-orchestrator/references/tasks/orchestrator-audit-runtime-floor.md) | kiểm năm nhóm cấm tuyệt đối còn nguyên và không bị cấu hình nào tắt được | runtime floor audit | `governance-assurance` | `R1-reviewed` / `standard-path` |
| [`orchestrator-check-information-sufficiency`](skills/data-department-orchestrator/references/tasks/orchestrator-check-information-sufficiency.md) | xác định thiếu blocking/nonblocking và conflicts | proceed/ask/stop decision | `advisory-analysis` | `R0-light` / `fast-path` |
| [`orchestrator-evaluate-workflow-completion`](skills/data-department-orchestrator/references/tasks/orchestrator-evaluate-workflow-completion.md) | đối chiếu deliverables, validations, approvals và open risks | completion decision | `advisory-analysis` | `R0-light` / `fast-path` |

<a id="skill-shared-data-core"></a>

### 2. `shared-data-core` — Shared Data Core

**Claude trigger description:** Apply shared data controls for bounded task-context packaging, discovery, schema inspection, profiling, validation, evidence, approvals and handoffs. Use when a data task needs reusable cross-role safeguards, a prompt-ready context bundle or artifact checks.

**Ownership:** Cung cấp các kiểm soát nền dùng chung: phân loại request, tìm tài sản, đọc glossary/schema, profiling, access, evidence, approval và handoff.

**Khi nên dùng:** Dùng như dependency của mọi role khi cần context đáng tin cậy hoặc kiểm tra an toàn trước khi làm việc.

**Ranh giới và handoff:** Không sở hữu deliverable chuyên môn; không được dùng shared controls để né ownership của DA, DE, DG, DS hay role khác.

**Quy mô:** 18 tasks — Plan / Design 3; Build / Deliver 9; Test / Assure 6; Operate / Improve 0.

**Domain references tải khi cần:** `adapter-bigquery.md`, `adapter-snowflake.md`, `authored-prose-voice.md`, `context-engineering-standard.md`, `external-tool-access.md`, `learning-memory-interoperability.md`, `model-selection.md`, `response-compression.md`, `solution-option-framing.md`, `workflow-runtime-and-evidence-os.md`.

**Templates/assets có thể tái sử dụng:** `atomic-task-output.yaml`, `atomic-task-result.schema.json`, `change-scope-contract.json`, `change-scope-ledger.yaml`, `debug-hypothesis-ledger.yaml`, `design-option-set.yaml`, `evidence-envelope.json`, `evidence-envelope.schema.json`, `project-constitution.json`, `project-constitution.schema.json`, `success-contract.yaml`, `task-context-package.yaml`, `verification-claims.yaml`.

**Scripts:** `audit_change_scope.py`, `build_context_package.py`, `validate_constitution.py`, `validate_evidence_bundle.py`, `validate_task_result.py`, `verify_deliverable.py`.

#### Plan / Design (3 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`core-create-data-work-ticket`](skills/shared-data-core/references/tasks/core-create-data-work-ticket.md) | chuyển yêu cầu thành scope, acceptance criteria, dependency và estimate | implementation-ready ticket | `design-specification` | `R1-reviewed` / `standard-path` |
| [`core-define-success-contract`](skills/shared-data-core/references/tasks/core-define-success-contract.md) | chuyển mục tiêu mơ hồ thành outcome quan sát được, tiêu chí pass/fail, evidence, non-goals và điều kiện dừng | verifiable success contract | `design-specification` | `R1-reviewed` / `standard-path` |
| [`core-document-data-deliverable`](skills/shared-data-core/references/tasks/core-document-data-deliverable.md) | tạo tài liệu theo template chuẩn | linked documentation | `advisory-analysis` | `R0-light` / `fast-path` |

#### Build / Deliver (9 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`core-build-task-context-package`](skills/shared-data-core/references/tasks/core-build-task-context-package.md) | gom task, business, schema, lineage, constraints và evidence thành context bundle có manifest, provenance, freshness và token budget | prompt-ready task context package | `build-change` | `R2-standard` / `standard-path` |
| [`core-classify-data-request`](skills/shared-data-core/references/tasks/core-classify-data-request.md) | phân loại intent, domain, độ rủi ro và role owner | routing decision | `advisory-analysis` | `R0-light` / `fast-path` |
| [`core-discover-data-assets`](skills/shared-data-core/references/tasks/core-discover-data-assets.md) | tìm source, table, metric, dashboard và owner liên quan | evidence-backed asset shortlist | `advisory-analysis` | `R0-light` / `fast-path` |
| [`core-estimate-change-impact`](skills/shared-data-core/references/tasks/core-estimate-change-impact.md) | tìm downstream dependency và stakeholder bị ảnh hưởng | impact report | `advisory-analysis` | `R0-light` / `fast-path` |
| [`core-handle-sensitive-data`](skills/shared-data-core/references/tasks/core-handle-sensitive-data.md) | nhận diện PII/confidential data và áp dụng handling rule | safe processing plan | `advisory-analysis` | `R0-light` / `fast-path` |
| [`core-handoff-data-work`](skills/shared-data-core/references/tasks/core-handoff-data-work.md) | đóng gói context, artifacts, open risks và next action | lossless handoff package | `advisory-analysis` | `R0-light` / `fast-path` |
| [`core-read-business-glossary`](skills/shared-data-core/references/tasks/core-read-business-glossary.md) | ánh xạ thuật ngữ người dùng sang định nghĩa chuẩn | resolved terminology | `advisory-analysis` | `R0-light` / `fast-path` |
| [`core-record-data-decision`](skills/shared-data-core/references/tasks/core-record-data-decision.md) | ghi decision, alternatives, evidence và consequences | decision record | `advisory-analysis` | `R0-light` / `fast-path` |
| [`core-request-human-approval`](skills/shared-data-core/references/tasks/core-request-human-approval.md) | tạo approval package đúng owner | auditable approval request | `advisory-analysis` | `R0-light` / `fast-path` |

#### Test / Assure (6 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`core-audit-change-scope`](skills/shared-data-core/references/tasks/core-audit-change-scope.md) | đối chiếu thay đổi thực tế với yêu cầu, allowlist, planned deletions và task-to-file traceability để phát hiện scope creep | surgical change-scope audit | `advisory-analysis` | `R0-light` / `fast-path` |
| [`core-check-data-access`](skills/shared-data-core/references/tasks/core-check-data-access.md) | xác định quyền cần thiết và giới hạn sử dụng | access decision hoặc request | `advisory-analysis` | `R3-controlled` / `controlled-path` |
| [`core-inspect-dataset-schema`](skills/shared-data-core/references/tasks/core-inspect-dataset-schema.md) | đọc schema, khóa, partition và quan hệ | schema assessment | `advisory-analysis` | `R0-light` / `fast-path` |
| [`core-profile-dataset`](skills/shared-data-core/references/tasks/core-profile-dataset.md) | đo null, distinct, distribution, outlier và freshness | profile report | `advisory-analysis` | `R0-light` / `fast-path` |
| [`core-validate-sql-safely`](skills/shared-data-core/references/tasks/core-validate-sql-safely.md) | lint, dry-run/explain, kiểm tra scan cost và read/write risk | validated SQL | `advisory-analysis` | `R0-light` / `fast-path` |
| [`core-verify-deliverable`](skills/shared-data-core/references/tasks/core-verify-deliverable.md) | chạy checklist theo loại artifact và thu evidence | pass/fail verification report | `advisory-analysis` | `R0-light` / `fast-path` |

<a id="skill-company-data-context"></a>

### 3. `company-data-context` — Company Data Context

**Claude trigger description:** Maintain and index company-specific data context including glossary terms, metrics, datasets, systems, owners, policies and platforms. Use when Claude must initialize, route, retrieve or verify organizational context without storing secrets.

**Ownership:** Xây bộ nhớ doanh nghiệp có quản trị cho business terms, metrics, datasets, systems, owners, policies và platform environments.

**Khi nên dùng:** Dùng khi Claude cần company-specific context có provenance, version và ngày xác minh để tránh bịa giả định tổ chức.

**Ranh giới và handoff:** Context pack không thay thế việc kiểm tra live system đối với thông tin có thể thay đổi; không chứa secret hay raw sensitive data.

**Quy mô:** 9 tasks — Plan / Design 1; Build / Deliver 7; Test / Assure 1; Operate / Improve 0.

**Domain references tải khi cần:** `adapter-bigquery.md`, `adapter-databricks.md`, `adapter-metadata-catalog.md`, `adapter-microsoft-fabric.md`, `adapter-snowflake.md`, `context-engineering-standard.md`, `learning-memory-interoperability.md`, `model-selection.md`, `response-compression.md`, `solution-option-framing.md`, `workflow-runtime-and-evidence-os.md`.

**Templates/assets có thể tái sử dụng:** `atomic-task-output.yaml`, `context-index.yaml`, `design-option-set.yaml`.

**Scripts:** `bootstrap_context_index.py`, `build_context_package.py`.

#### Plan / Design (1 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`ctx-build-context-index`](skills/company-data-context/references/tasks/ctx-build-context-index.md) | tạo index phân tầng chỉ rõ nguồn context, authority, scope, trigger đọc, owner và freshness cho Claude/agent sessions | governed context index | `design-specification` | `R2-standard` / `standard-path` |

#### Build / Deliver (7 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`ctx-initialize-company-data-context`](skills/company-data-context/references/tasks/ctx-initialize-company-data-context.md) | tạo cấu trúc context chuẩn cho business, data, platform, policy và ownership | initialized context pack | `advisory-analysis` | `R0-light` / `fast-path` |
| [`ctx-record-platform-environment`](skills/company-data-context/references/tasks/ctx-record-platform-environment.md) | ghi tools, environments, endpoints, deployment và operational constraints | platform-context entry | `advisory-analysis` | `R0-light` / `fast-path` |
| [`ctx-register-business-metric`](skills/company-data-context/references/tasks/ctx-register-business-metric.md) | ghi definition, formula, grain, dimensions, exclusions và owner | metric entry | `advisory-analysis` | `R0-light` / `fast-path` |
| [`ctx-register-data-owner`](skills/company-data-context/references/tasks/ctx-register-data-owner.md) | ghi accountability, stewardship, escalation và contact channel | ownership entry | `advisory-analysis` | `R0-light` / `fast-path` |
| [`ctx-register-data-policy`](skills/company-data-context/references/tasks/ctx-register-data-policy.md) | ghi rule, scope, enforcement, exception và authority | policy entry | `advisory-analysis` | `R0-light` / `fast-path` |
| [`ctx-register-dataset-schema`](skills/company-data-context/references/tasks/ctx-register-dataset-schema.md) | ghi schema, grain, keys, partitions, relationships và examples | dataset-schema entry | `advisory-analysis` | `R0-light` / `fast-path` |
| [`ctx-register-source-system`](skills/company-data-context/references/tasks/ctx-register-source-system.md) | ghi purpose, owner, interface, cadence, keys và constraints của source | source-system entry | `advisory-analysis` | `R0-light` / `fast-path` |

#### Test / Assure (1 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`ctx-validate-context-pack`](skills/company-data-context/references/tasks/ctx-validate-context-pack.md) | kiểm tra completeness, conflicts, staleness, provenance và broken references | context validation report | `advisory-analysis` | `R0-light` / `fast-path` |

<a id="skill-head-of-data-and-data-product"></a>

### 4. `head-of-data-and-data-product` — Head of Data and Data Product

**Claude trigger description:** Lead data strategy, operating model, portfolio, roadmap, service intake, prioritization, value, adoption and executive governance. Use for Head of Data, CDO or Data Product Management deliverables.

**Ownership:** Chuyển chiến lược kinh doanh thành data strategy, operating model, portfolio, roadmap, ưu tiên, service model và cơ chế đo giá trị/adoption.

**Khi nên dùng:** Dùng cho Head of Data, Data Product Manager, Data PM hoặc quyết định cấp portfolio và stakeholder governance.

**Ranh giới và handoff:** Sở hữu outcome, priority và capacity; implementation detail phải handoff cho Architecture, Engineering, Analytics hoặc Governance.

**Quy mô:** 21 tasks — Plan / Design 11; Build / Deliver 7; Test / Assure 3; Operate / Improve 0.

**Domain references tải khi cần:** `external-tool-access.md`, `learning-memory-interoperability.md`, `model-selection.md`, `response-compression.md`, `solution-option-framing.md`, `workflow-runtime-and-evidence-os.md`.

**Templates/assets có thể tái sử dụng:** `atomic-task-output.yaml`, `design-option-set.yaml`.

**Scripts:** `score_portfolio_options.py`.

#### Plan / Design (11 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`dpm-frame-data-product-opportunity`](skills/head-of-data-and-data-product/references/tasks/dpm-frame-data-product-opportunity.md) | xác định user, job-to-be-done, value hypothesis và constraints | opportunity brief | `design-specification` | `R1-reviewed` / `standard-path` |
| [`dpm-plan-data-release`](skills/head-of-data-and-data-product/references/tasks/dpm-plan-data-release.md) | xác định milestones, dependency, rollout và communication | release plan | `production-release` | `R3-controlled` / `controlled-path` |
| [`dpm-write-data-product-requirements`](skills/head-of-data-and-data-product/references/tasks/dpm-write-data-product-requirements.md) | định nghĩa scope, user story, NFR và acceptance criteria | PRD | `design-specification` | `R1-reviewed` / `standard-path` |
| [`hod-create-data-hiring-scorecard`](skills/head-of-data-and-data-product/references/tasks/hod-create-data-hiring-scorecard.md) | định nghĩa outcomes, signals và interview rubric | hiring scorecard | `design-specification` | `R1-reviewed` / `standard-path` |
| [`hod-define-data-okrs`](skills/head-of-data-and-data-product/references/tasks/hod-define-data-okrs.md) | xây objective, key result, baseline và owner | approved OKR set | `design-specification` | `R1-reviewed` / `standard-path` |
| [`hod-define-data-role-competencies`](skills/head-of-data-and-data-product/references/tasks/hod-define-data-role-competencies.md) | tạo competency matrix theo level | role framework | `design-specification` | `R1-reviewed` / `standard-path` |
| [`hod-define-data-service-slas`](skills/head-of-data-and-data-product/references/tasks/hod-define-data-service-slas.md) | xác định service catalog, priority và response/resolution target | SLA policy | `design-specification` | `R1-reviewed` / `standard-path` |
| [`hod-define-data-strategy`](skills/head-of-data-and-data-product/references/tasks/hod-define-data-strategy.md) | chuyển business strategy thành data themes và measurable outcomes | data strategy | `design-specification` | `R1-reviewed` / `standard-path` |
| [`hod-design-data-operating-model`](skills/head-of-data-and-data-product/references/tasks/hod-design-data-operating-model.md) | xác định centralized/federated/mesh, ownership và interaction model | operating model | `design-specification` | `R1-reviewed` / `standard-path` |
| [`hod-design-data-team-topology`](skills/head-of-data-and-data-product/references/tasks/hod-design-data-team-topology.md) | xác định team boundaries và cognitive load | target topology | `design-specification` | `R1-reviewed` / `standard-path` |
| [`hod-plan-data-capacity`](skills/head-of-data-and-data-product/references/tasks/hod-plan-data-capacity.md) | dự báo demand, capacity, bottleneck và hiring/outsourcing | capacity plan | `design-specification` | `R1-reviewed` / `standard-path` |

#### Build / Deliver (7 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`dpm-accept-data-deliverable`](skills/head-of-data-and-data-product/references/tasks/dpm-accept-data-deliverable.md) | kiểm chứng acceptance criteria và business usability | acceptance decision | `advisory-analysis` | `R0-light` / `fast-path` |
| [`dpm-intake-data-request`](skills/head-of-data-and-data-product/references/tasks/dpm-intake-data-request.md) | chuẩn hóa problem, requester, urgency và expected decision | intake record | `advisory-analysis` | `R0-light` / `fast-path` |
| [`dpm-prioritize-data-backlog`](skills/head-of-data-and-data-product/references/tasks/dpm-prioritize-data-backlog.md) | chấm điểm value, effort, risk và dependency | ranked backlog | `advisory-analysis` | `R0-light` / `fast-path` |
| [`hod-build-data-roadmap`](skills/head-of-data-and-data-product/references/tasks/hod-build-data-roadmap.md) | sắp xếp initiative theo value, risk và dependency | phased roadmap | `build-change` | `R2-standard` / `standard-path` |
| [`hod-build-data-training-roadmap`](skills/head-of-data-and-data-product/references/tasks/hod-build-data-training-roadmap.md) | gap assessment và learning path | capability plan | `build-change` | `R2-standard` / `standard-path` |
| [`hod-manage-data-portfolio`](skills/head-of-data-and-data-product/references/tasks/hod-manage-data-portfolio.md) | theo dõi value, cost, risk và status của initiatives | portfolio review | `advisory-analysis` | `R0-light` / `fast-path` |
| [`hod-run-data-steering-review`](skills/head-of-data-and-data-product/references/tasks/hod-run-data-steering-review.md) | chuẩn bị decisions, escalations và commitments | steering decision log | `advisory-analysis` | `R0-light` / `fast-path` |

#### Test / Assure (3 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`hod-assess-data-maturity`](skills/head-of-data-and-data-product/references/tasks/hod-assess-data-maturity.md) | đánh giá maturity theo people/process/technology/governance | maturity baseline | `advisory-analysis` | `R0-light` / `fast-path` |
| [`hod-evaluate-data-vendor`](skills/head-of-data-and-data-product/references/tasks/hod-evaluate-data-vendor.md) | so sánh fit, TCO, lock-in, security và exit path | vendor decision memo | `advisory-analysis` | `R0-light` / `fast-path` |
| [`hod-measure-data-product-adoption`](skills/head-of-data-and-data-product/references/tasks/hod-measure-data-product-adoption.md) | theo dõi usage, satisfaction, decision impact và retirement signal | adoption report | `advisory-analysis` | `R0-light` / `fast-path` |

<a id="skill-data-business-analysis"></a>

### 5. `data-business-analysis` — Data Business Analysis

**Claude trigger description:** Elicit and validate data requirements, business rules, processes, use cases, acceptance criteria and traceability. Use for Data Business Analyst work or when an ambiguous business request must become an implementation-ready specification.

**Ownership:** Khám phá nhu cầu, quy trình, business rules, data/metric requirements, use cases, acceptance criteria, traceability và UAT readiness.

**Khi nên dùng:** Dùng khi business question chưa đủ rõ để thiết kế dữ liệu hoặc khi cần nối requirement tới design, implementation và test evidence.

**Ranh giới và handoff:** Không tự chuẩn hóa metric tranh chấp hay quyết định kiến trúc; chuyển đúng artifact cho Governance, Architecture, AE/DE và BI.

**Quy mô:** 24 tasks — Plan / Design 15; Build / Deliver 7; Test / Assure 2; Operate / Improve 0.

**Domain references tải khi cần:** `learning-memory-interoperability.md`, `model-selection.md`, `response-compression.md`, `solution-option-framing.md`, `workflow-runtime-and-evidence-os.md`.

**Templates/assets có thể tái sử dụng:** `atomic-task-output.yaml`, `design-option-set.yaml`.

**Scripts:** `validate_requirements_traceability.py`.

#### Plan / Design (15 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`ba-create-business-persona`](skills/data-business-analysis/references/tasks/ba-create-business-persona.md) | tổng hợp role, goals, behaviors và information needs | persona | `design-specification` | `R1-reviewed` / `standard-path` |
| [`ba-define-business-rules`](skills/data-business-analysis/references/tasks/ba-define-business-rules.md) | ghi condition, decision, exception, owner và examples | business-rule register | `design-specification` | `R1-reviewed` / `standard-path` |
| [`ba-define-scope-contract`](skills/data-business-analysis/references/tasks/ba-define-scope-contract.md) | ghi in-scope, out-of-scope, constraints và change rule | scope contract | `design-specification` | `R1-reviewed` / `standard-path` |
| [`ba-design-to-be-process`](skills/data-business-analysis/references/tasks/ba-design-to-be-process.md) | thiết kế future workflow, controls và role changes | to-be process model | `design-specification` | `R1-reviewed` / `standard-path` |
| [`ba-document-as-is-process`](skills/data-business-analysis/references/tasks/ba-document-as-is-process.md) | mô tả actors, events, steps, rules và pain points hiện tại | as-is process model | `advisory-analysis` | `R0-light` / `fast-path` |
| [`ba-frame-business-problem`](skills/data-business-analysis/references/tasks/ba-frame-business-problem.md) | xác định hiện trạng, pain point, affected users và desired outcome | problem statement | `design-specification` | `R1-reviewed` / `standard-path` |
| [`ba-map-business-decision`](skills/data-business-analysis/references/tasks/ba-map-business-decision.md) | nối decision với evidence, cadence, owner và consequence | decision map | `advisory-analysis` | `R0-light` / `fast-path` |
| [`ba-map-stakeholders`](skills/data-business-analysis/references/tasks/ba-map-stakeholders.md) | xác định sponsor, decision maker, users, SMEs và approvers | stakeholder map | `advisory-analysis` | `R0-light` / `fast-path` |
| [`ba-map-user-journey`](skills/data-business-analysis/references/tasks/ba-map-user-journey.md) | mô tả stages, touchpoints, needs và friction | user-journey map | `advisory-analysis` | `R0-light` / `fast-path` |
| [`ba-plan-discovery-interview`](skills/data-business-analysis/references/tasks/ba-plan-discovery-interview.md) | chọn participants, question sequence và evidence cần thu | interview plan | `design-specification` | `R1-reviewed` / `standard-path` |
| [`ba-write-acceptance-criteria`](skills/data-business-analysis/references/tasks/ba-write-acceptance-criteria.md) | chuyển requirement thành testable Given/When/Then hoặc checklist | acceptance criteria | `design-specification` | `R1-reviewed` / `standard-path` |
| [`ba-write-business-requirements-document`](skills/data-business-analysis/references/tasks/ba-write-business-requirements-document.md) | chuẩn hóa context, scope, stakeholders và requirements | BRD | `design-specification` | `R1-reviewed` / `standard-path` |
| [`ba-write-functional-requirements`](skills/data-business-analysis/references/tasks/ba-write-functional-requirements.md) | định nghĩa system behavior, inputs, outputs và exceptions | functional specification | `design-specification` | `R1-reviewed` / `standard-path` |
| [`ba-write-nonfunctional-requirements`](skills/data-business-analysis/references/tasks/ba-write-nonfunctional-requirements.md) | định nghĩa performance, availability, security, audit và usability | NFR specification | `design-specification` | `R1-reviewed` / `standard-path` |
| [`ba-write-use-case-specification`](skills/data-business-analysis/references/tasks/ba-write-use-case-specification.md) | mô tả actor, precondition, main flow, alternatives và postcondition | use-case specification | `design-specification` | `R1-reviewed` / `standard-path` |

#### Build / Deliver (7 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`ba-build-requirement-traceability`](skills/data-business-analysis/references/tasks/ba-build-requirement-traceability.md) | nối requirement tới design, data, test và release | traceability matrix | `build-change` | `R2-standard` / `standard-path` |
| [`ba-elicit-business-requirements`](skills/data-business-analysis/references/tasks/ba-elicit-business-requirements.md) | thu thập goal, process, rule, data và acceptance needs | requirement set | `advisory-analysis` | `R0-light` / `fast-path` |
| [`ba-handoff-requirements-to-delivery`](skills/data-business-analysis/references/tasks/ba-handoff-requirements-to-delivery.md) | đóng gói baselined requirements, decisions và open questions | delivery handoff | `advisory-analysis` | `R0-light` / `fast-path` |
| [`ba-manage-requirement-change`](skills/data-business-analysis/references/tasks/ba-manage-requirement-change.md) | đánh giá impact, approval và baseline version | governed change request | `advisory-analysis` | `R0-light` / `fast-path` |
| [`ba-prioritize-requirements`](skills/data-business-analysis/references/tasks/ba-prioritize-requirements.md) | áp dụng value, urgency, dependency và risk | prioritized requirements | `advisory-analysis` | `R0-light` / `fast-path` |
| [`ba-run-discovery-workshop`](skills/data-business-analysis/references/tasks/ba-run-discovery-workshop.md) | điều phối workshop và chốt decisions/open questions | workshop record | `advisory-analysis` | `R0-light` / `fast-path` |
| [`ba-seed-project-risk-register`](skills/data-business-analysis/references/tasks/ba-seed-project-risk-register.md) | ghi risk, likelihood, impact, mitigation và owner | initial risk register | `advisory-analysis` | `R0-light` / `fast-path` |

#### Test / Assure (2 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`ba-assess-solution-feasibility`](skills/data-business-analysis/references/tasks/ba-assess-solution-feasibility.md) | đánh giá data, technology, operations, risk và value | feasibility report | `advisory-analysis` | `R0-light` / `fast-path` |
| [`ba-validate-requirements`](skills/data-business-analysis/references/tasks/ba-validate-requirements.md) | kiểm tra completeness, consistency, feasibility và testability | validation report | `advisory-analysis` | `R0-light` / `fast-path` |

<a id="skill-data-architecture"></a>

### 6. `data-architecture` — Data Architecture

**Claude trigger description:** Design data target states, domains, models, integration patterns, contracts, technology decisions, migrations and architecture reviews. Use for enterprise, solution or data architecture deliverables and ADRs.

**Ownership:** Thiết kế current/target architecture, domain boundaries, data models, integration patterns, contracts, ADR, migration, resilience và guardrails.

**Khi nên dùng:** Dùng cho quyết định cấu trúc hệ thống hoặc thay đổi có nhiều downstream dependency và trade-off dài hạn.

**Ranh giới và handoff:** Không biến architecture thành implementation chưa được phê duyệt; mọi quyết định quan trọng cần alternatives, consequences và migration path.

**Quy mô:** 22 tasks — Plan / Design 17; Build / Deliver 1; Test / Assure 4; Operate / Improve 0.

**Domain references tải khi cần:** `adapter-bigquery.md`, `adapter-databricks.md`, `adapter-kafka-flink.md`, `adapter-microsoft-fabric.md`, `adapter-snowflake.md`, `learning-memory-interoperability.md`, `model-selection.md`, `response-compression.md`, `solution-option-framing.md`, `workflow-runtime-and-evidence-os.md`.

**Templates/assets có thể tái sử dụng:** `atomic-task-output.yaml`, `design-option-set.yaml`.

**Scripts:** `scan_architecture_drift.py`.

#### Plan / Design (17 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`arch-choose-integration-pattern`](skills/data-architecture/references/tasks/arch-choose-integration-pattern.md) | chọn batch/API/CDC/event/stream và trade-off | integration decision | `design-specification` | `R1-reviewed` / `standard-path` |
| [`arch-define-data-contract-standard`](skills/data-architecture/references/tasks/arch-define-data-contract-standard.md) | quy định schema, semantics, SLO, compatibility và ownership | contract standard | `design-specification` | `R1-reviewed` / `standard-path` |
| [`arch-define-modeling-standard`](skills/data-architecture/references/tasks/arch-define-modeling-standard.md) | chọn dimensional/Data Vault/domain model conventions | modeling standard | `design-specification` | `R1-reviewed` / `standard-path` |
| [`arch-define-target-data-architecture`](skills/data-architecture/references/tasks/arch-define-target-data-architecture.md) | mô tả target state, boundaries, flows và quality attributes | target architecture | `design-specification` | `R1-reviewed` / `standard-path` |
| [`arch-design-batch-architecture`](skills/data-architecture/references/tasks/arch-design-batch-architecture.md) | thiết kế batch topology, scheduling, recovery và backfill | batch design | `design-specification` | `R1-reviewed` / `standard-path` |
| [`arch-design-data-domain-boundaries`](skills/data-architecture/references/tasks/arch-design-data-domain-boundaries.md) | xác định domain, bounded context, owner và shared concepts | domain map | `design-specification` | `R1-reviewed` / `standard-path` |
| [`arch-design-data-flow`](skills/data-architecture/references/tasks/arch-design-data-flow.md) | mô tả source-to-consumption flow, latency và control points | data-flow design | `design-specification` | `R1-reviewed` / `standard-path` |
| [`arch-design-data-security-architecture`](skills/data-architecture/references/tasks/arch-design-data-security-architecture.md) | thiết kế trust boundaries, IAM, encryption và policy enforcement | security architecture | `design-specification` | `R3-controlled` / `controlled-path` |
| [`arch-design-data-sharing-architecture`](skills/data-architecture/references/tasks/arch-design-data-sharing-architecture.md) | thiết kế clean room/exchange/API/share có governance | sharing architecture | `design-specification` | `R3-controlled` / `controlled-path` |
| [`arch-design-disaster-recovery`](skills/data-architecture/references/tasks/arch-design-disaster-recovery.md) | xác định RTO/RPO, backup, failover và test plan | DR architecture | `incident-recovery` | `R3-controlled` / `controlled-path` |
| [`arch-design-metadata-lineage-architecture`](skills/data-architecture/references/tasks/arch-design-metadata-lineage-architecture.md) | thiết kế metadata collection, lineage và catalog integration | metadata architecture | `design-specification` | `R1-reviewed` / `standard-path` |
| [`arch-design-multi-environment-strategy`](skills/data-architecture/references/tasks/arch-design-multi-environment-strategy.md) | phân tách dev/test/prod và promotion flow | environment architecture | `design-specification` | `R1-reviewed` / `standard-path` |
| [`arch-design-streaming-architecture`](skills/data-architecture/references/tasks/arch-design-streaming-architecture.md) | thiết kế event model, ordering, delivery semantics và replay | streaming design | `design-specification` | `R1-reviewed` / `standard-path` |
| [`arch-plan-data-platform-capacity`](skills/data-architecture/references/tasks/arch-plan-data-platform-capacity.md) | dự báo throughput, concurrency, storage và headroom | capacity model | `design-specification` | `R1-reviewed` / `standard-path` |
| [`arch-plan-legacy-data-migration`](skills/data-architecture/references/tasks/arch-plan-legacy-data-migration.md) | waves, coexistence, reconciliation và rollback | migration roadmap | `design-specification` | `R1-reviewed` / `standard-path` |
| [`arch-select-data-platform-pattern`](skills/data-architecture/references/tasks/arch-select-data-platform-pattern.md) | đánh giá warehouse/lake/lakehouse/mesh theo workload | pattern decision | `design-specification` | `R1-reviewed` / `standard-path` |
| [`arch-write-architecture-decision-record`](skills/data-architecture/references/tasks/arch-write-architecture-decision-record.md) | ghi context, options, decision và consequence | ADR | `design-specification` | `R1-reviewed` / `standard-path` |

#### Build / Deliver (1 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`arch-manage-architecture-technical-debt`](skills/data-architecture/references/tasks/arch-manage-architecture-technical-debt.md) | lượng hóa debt, risk và remediation sequence | debt register | `advisory-analysis` | `R0-light` / `fast-path` |

#### Test / Assure (4 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`arch-assess-architecture-compliance`](skills/data-architecture/references/tasks/arch-assess-architecture-compliance.md) | đối chiếu implementation với standards và waiver | compliance report | `advisory-analysis` | `R0-light` / `fast-path` |
| [`arch-assess-current-data-architecture`](skills/data-architecture/references/tasks/arch-assess-current-data-architecture.md) | lập inventory, bottleneck, risk và technical debt | current-state assessment | `advisory-analysis` | `R0-light` / `fast-path` |
| [`arch-evaluate-technology-option`](skills/data-architecture/references/tasks/arch-evaluate-technology-option.md) | proof-of-fit theo weighted criteria | technology recommendation | `advisory-analysis` | `R0-light` / `fast-path` |
| [`arch-review-solution-design`](skills/data-architecture/references/tasks/arch-review-solution-design.md) | kiểm tra consistency, scalability, operability và governance | review decision | `advisory-analysis` | `R0-light` / `fast-path` |

<a id="skill-data-governance-and-stewardship"></a>

### 7. `data-governance-and-stewardship` — Data Governance and Stewardship

**Claude trigger description:** Define and operate data ownership, policies, glossary, classification, access governance, retention, certification, stewardship and control evidence. Use for Data Governance, Data Office or Data Steward work.

**Ownership:** Quản trị ownership, stewardship, glossary, classification, policy, retention, access, certification, issues, council workflow và control evidence.

**Khi nên dùng:** Dùng khi cần định nghĩa authority, chuẩn hóa nghĩa dữ liệu, chứng nhận metric/data product hoặc xử lý ngoại lệ governance.

**Ranh giới và handoff:** Không tự cấp quyền, phê duyệt ngoại lệ hay tuyên bố compliance khi thiếu accountable authority và audit evidence.

**Quy mô:** 22 tasks — Plan / Design 8; Build / Deliver 5; Test / Assure 8; Operate / Improve 1.

**Domain references tải khi cần:** `external-tool-access.md`, `learning-memory-interoperability.md`, `model-selection.md`, `response-compression.md`, `solution-option-framing.md`, `workflow-runtime-and-evidence-os.md`.

**Templates/assets có thể tái sử dụng:** `atomic-task-output.yaml`, `design-option-set.yaml`.

**Scripts:** `validate_policy_coverage.py`.

#### Plan / Design (8 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`dg-collect-compliance-evidence`](skills/data-governance-and-stewardship/references/tasks/dg-collect-compliance-evidence.md) | gom policy, access, quality, lineage và approval artifacts | evidence package | `governance-assurance` | `R1-reviewed` / `standard-path` |
| [`dg-create-business-term`](skills/data-governance-and-stewardship/references/tasks/dg-create-business-term.md) | định nghĩa term, synonyms, rules, examples và owner | glossary entry | `governance-assurance` | `R1-reviewed` / `standard-path` |
| [`dg-define-data-domain`](skills/data-governance-and-stewardship/references/tasks/dg-define-data-domain.md) | xác định scope, assets, owner và stewardship boundary | domain charter | `governance-assurance` | `R1-reviewed` / `standard-path` |
| [`dg-define-data-policy`](skills/data-governance-and-stewardship/references/tasks/dg-define-data-policy.md) | viết policy gồm scope, rule, roles, exceptions và evidence | approved policy draft | `governance-assurance` | `R1-reviewed` / `standard-path` |
| [`dg-define-data-quality-policy`](skills/data-governance-and-stewardship/references/tasks/dg-define-data-quality-policy.md) | xác định dimensions, thresholds, owners và escalation | DQ policy | `governance-assurance` | `R1-reviewed` / `standard-path` |
| [`dg-define-data-retention-rule`](skills/data-governance-and-stewardship/references/tasks/dg-define-data-retention-rule.md) | xác định retention, legal hold và disposal trigger | retention schedule | `governance-assurance` | `R1-reviewed` / `standard-path` |
| [`dg-define-metadata-requirements`](skills/data-governance-and-stewardship/references/tasks/dg-define-metadata-requirements.md) | xác định metadata bắt buộc theo asset type | metadata standard | `governance-assurance` | `R1-reviewed` / `standard-path` |
| [`dg-plan-data-asset-retirement`](skills/data-governance-and-stewardship/references/tasks/dg-plan-data-asset-retirement.md) | xác định consumers, archive, replacement và deletion approvals | retirement plan | `production-release` | `R4-critical` / `controlled-path` |

#### Build / Deliver (5 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`dg-assign-data-ownership`](skills/data-governance-and-stewardship/references/tasks/dg-assign-data-ownership.md) | thiết lập accountable owner, steward và custodian | ownership matrix | `governance-assurance` | `R1-reviewed` / `standard-path` |
| [`dg-classify-data-asset`](skills/data-governance-and-stewardship/references/tasks/dg-classify-data-asset.md) | gắn sensitivity, criticality, regulatory và lifecycle class | classification record | `governance-assurance` | `R1-reviewed` / `standard-path` |
| [`dg-manage-data-issue`](skills/data-governance-and-stewardship/references/tasks/dg-manage-data-issue.md) | ghi nhận, phân loại, assign, track remediation và closure evidence | governed issue record | `governance-assurance` | `R1-reviewed` / `standard-path` |
| [`dg-manage-policy-exception`](skills/data-governance-and-stewardship/references/tasks/dg-manage-policy-exception.md) | đánh giá compensating controls, expiry và approver | time-bound exception | `governance-assurance` | `R1-reviewed` / `standard-path` |
| [`dg-run-governance-council`](skills/data-governance-and-stewardship/references/tasks/dg-run-governance-council.md) | chuẩn bị agenda, decisions, owners và deadlines | council decision log | `governance-assurance` | `R1-reviewed` / `standard-path` |

#### Test / Assure (8 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`dg-assess-governance-maturity`](skills/data-governance-and-stewardship/references/tasks/dg-assess-governance-maturity.md) | chấm maturity và xác định improvement backlog | governance assessment | `governance-assurance` | `R1-reviewed` / `standard-path` |
| [`dg-audit-policy-conformance`](skills/data-governance-and-stewardship/references/tasks/dg-audit-policy-conformance.md) | lấy mẫu evidence và ghi exceptions/remediation | conformance audit | `governance-assurance` | `R1-reviewed` / `standard-path` |
| [`dg-certify-business-metric`](skills/data-governance-and-stewardship/references/tasks/dg-certify-business-metric.md) | phê duyệt definition, formula, grain, filters và source | certified metric | `governance-assurance` | `R4-critical` / `controlled-path` |
| [`dg-certify-data-asset`](skills/data-governance-and-stewardship/references/tasks/dg-certify-data-asset.md) | kiểm tra owner, definition, quality, lineage và controls | certification decision | `governance-assurance` | `R1-reviewed` / `standard-path` |
| [`dg-measure-governance-kpis`](skills/data-governance-and-stewardship/references/tasks/dg-measure-governance-kpis.md) | đo ownership, glossary, certification, issue aging và compliance | governance scorecard | `governance-assurance` | `R1-reviewed` / `standard-path` |
| [`dg-review-data-access-request`](skills/data-governance-and-stewardship/references/tasks/dg-review-data-access-request.md) | đánh giá purpose, minimization, sensitivity và duration | governance recommendation | `governance-assurance` | `R3-controlled` / `controlled-path` |
| [`dg-review-data-sharing-request`](skills/data-governance-and-stewardship/references/tasks/dg-review-data-sharing-request.md) | đánh giá recipient, purpose, contract, controls và revocation | sharing decision package | `governance-assurance` | `R3-controlled` / `controlled-path` |
| [`dg-review-lineage-completeness`](skills/data-governance-and-stewardship/references/tasks/dg-review-lineage-completeness.md) | kiểm tra coverage cho critical data element | lineage gap report | `governance-assurance` | `R1-reviewed` / `standard-path` |

#### Operate / Improve (1 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`dg-resolve-business-term-conflict`](skills/data-governance-and-stewardship/references/tasks/dg-resolve-business-term-conflict.md) | phân tích định nghĩa cạnh tranh và điều phối quyết định | resolved term | `governance-assurance` | `R1-reviewed` / `standard-path` |

<a id="skill-metadata-engineering-and-catalog"></a>

### 8. `metadata-engineering-and-catalog` — Metadata Engineering and Catalog

**Claude trigger description:** Build and operate metadata ingestion, catalog, search, lineage, ownership, usage and metadata quality. Use for data catalog, discovery, technical metadata or lineage engineering requests. This skill describes assets rather than building them, so pipeline construction belongs to data-engineering and transformation modelling to analytics-engineering.

**Ownership:** Thu thập và vận hành technical/business metadata, lineage, ownership, search, usage analytics, metadata APIs và chất lượng catalog.

**Khi nên dùng:** Dùng khi cần làm cho tài sản dữ liệu discoverable, traceable và có quan hệ nguồn–đích rõ ràng.

**Ranh giới và handoff:** Không suy diễn lineage hoặc ownership từ tên gọi; phải phân biệt metadata quan sát được, khai báo và đã được xác nhận.

**Quy mô:** 18 tasks — Plan / Design 1; Build / Deliver 13; Test / Assure 3; Operate / Improve 1.

**Domain references tải khi cần:** `adapter-bigquery.md`, `adapter-databricks.md`, `adapter-metadata-catalog.md`, `adapter-microsoft-fabric.md`, `adapter-snowflake.md`, `external-tool-access.md`, `learning-memory-interoperability.md`, `model-selection.md`, `response-compression.md`, `solution-option-framing.md`, `workflow-runtime-and-evidence-os.md`.

**Templates/assets có thể tái sử dụng:** `atomic-task-output.yaml`, `design-option-set.yaml`.

#### Plan / Design (1 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`meta-map-critical-data-elements`](skills/metadata-engineering-and-catalog/references/tasks/meta-map-critical-data-elements.md) | xác định CDE và liên kết system/column/control | CDE map | `advisory-analysis` | `R0-light` / `fast-path` |

#### Build / Deliver (13 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`meta-build-data-lineage`](skills/metadata-engineering-and-catalog/references/tasks/meta-build-data-lineage.md) | tạo source-to-target lineage ở dataset/column/job level | lineage graph | `build-change` | `R2-standard` / `standard-path` |
| [`meta-build-source-authority-matrix`](skills/metadata-engineering-and-catalog/references/tasks/meta-build-source-authority-matrix.md) | xác định authoritative source theo entity, field và use case | authority matrix | `build-change` | `R2-standard` / `standard-path` |
| [`meta-curate-business-metadata`](skills/metadata-engineering-and-catalog/references/tasks/meta-curate-business-metadata.md) | nối descriptions, glossary terms, domain và use cases | enriched catalog entries | `advisory-analysis` | `R0-light` / `fast-path` |
| [`meta-deprecate-catalog-asset`](skills/metadata-engineering-and-catalog/references/tasks/meta-deprecate-catalog-asset.md) | đánh dấu replacement, notify consumers và archive lineage | deprecated catalog record | `advisory-analysis` | `R0-light` / `fast-path` |
| [`meta-harvest-technical-metadata`](skills/metadata-engineering-and-catalog/references/tasks/meta-harvest-technical-metadata.md) | thu schema, type, keys, jobs và dependencies từ platforms | harvested metadata | `advisory-analysis` | `R0-light` / `fast-path` |
| [`meta-index-data-for-discovery`](skills/metadata-engineering-and-catalog/references/tasks/meta-index-data-for-discovery.md) | cấu hình searchable metadata, synonyms và ranking | discoverable catalog index | `advisory-analysis` | `R0-light` / `fast-path` |
| [`meta-ingest-usage-metadata`](skills/metadata-engineering-and-catalog/references/tasks/meta-ingest-usage-metadata.md) | thu query/report access và popularity signals | usage metadata | `build-change` | `R2-standard` / `standard-path` |
| [`meta-inventory-data-assets`](skills/metadata-engineering-and-catalog/references/tasks/meta-inventory-data-assets.md) | lập inventory source, table, model, metric, report và owner | asset inventory | `advisory-analysis` | `R0-light` / `fast-path` |
| [`meta-manage-catalog-tags`](skills/metadata-engineering-and-catalog/references/tasks/meta-manage-catalog-tags.md) | chuẩn hóa technical/business/security tags và inheritance | governed tag set | `advisory-analysis` | `R0-light` / `fast-path` |
| [`meta-onboard-metadata-connector`](skills/metadata-engineering-and-catalog/references/tasks/meta-onboard-metadata-connector.md) | cấu hình extraction, credentials, schedule và validation | operational connector | `advisory-analysis` | `R0-light` / `fast-path` |
| [`meta-register-data-asset`](skills/metadata-engineering-and-catalog/references/tasks/meta-register-data-asset.md) | tạo catalog entry có identifier, owner, classification và lifecycle | registered asset | `advisory-analysis` | `R0-light` / `fast-path` |
| [`meta-synchronize-asset-ownership`](skills/metadata-engineering-and-catalog/references/tasks/meta-synchronize-asset-ownership.md) | cập nhật owner/steward từ systems of record | consistent ownership metadata | `build-change` | `R2-standard` / `standard-path` |
| [`meta-track-schema-version`](skills/metadata-engineering-and-catalog/references/tasks/meta-track-schema-version.md) | lưu schema history, compatibility và change events | schema version history | `advisory-analysis` | `R0-light` / `fast-path` |

#### Test / Assure (3 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`meta-detect-orphan-data-assets`](skills/metadata-engineering-and-catalog/references/tasks/meta-detect-orphan-data-assets.md) | tìm assets không owner, không consumer hoặc không refresh | orphan report | `advisory-analysis` | `R0-light` / `fast-path` |
| [`meta-measure-metadata-completeness`](skills/metadata-engineering-and-catalog/references/tasks/meta-measure-metadata-completeness.md) | chấm mandatory fields theo asset type và criticality | completeness scorecard | `advisory-analysis` | `R0-light` / `fast-path` |
| [`meta-validate-lineage`](skills/metadata-engineering-and-catalog/references/tasks/meta-validate-lineage.md) | đối chiếu parsed lineage với code, queries và owner evidence | lineage validation report | `advisory-analysis` | `R0-light` / `fast-path` |

#### Operate / Improve (1 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`meta-publish-metadata-api`](skills/metadata-engineering-and-catalog/references/tasks/meta-publish-metadata-api.md) | cung cấp searchable metadata contract cho tools/agents | metadata API contract | `production-release` | `R3-controlled` / `controlled-path` |

<a id="skill-data-platform-and-dataops"></a>

### 9. `data-platform-and-dataops` — Data Platform and DataOps

**Claude trigger description:** Design and operate data platforms, environments, orchestration, CI/CD, observability, capacity, reliability, cost and disaster recovery. Use for Data Platform, DataOps or platform operations work. The model lifecycle itself belongs to mlops.

**Ownership:** Thiết kế và vận hành nền tảng dữ liệu: environments, orchestration, CI/CD, secrets, observability, capacity, cost, backup, DR và incidents.

**Khi nên dùng:** Dùng cho platform services, operational readiness và các thay đổi hạ tầng dùng chung cho nhiều workload.

**Ranh giới và handoff:** Production, secrets, access và recovery là controlled work; cần rollback, monitoring và approval đúng scope/version.

**Quy mô:** 21 tasks — Plan / Design 1; Build / Deliver 13; Test / Assure 3; Operate / Improve 4.

**Domain references tải khi cần:** `adapter-airflow.md`, `adapter-bigquery.md`, `adapter-databricks.md`, `adapter-kafka-flink.md`, `adapter-metadata-catalog.md`, `adapter-microsoft-fabric.md`, `adapter-mlflow-kubeflow.md`, `adapter-snowflake.md`, `adapter-spark.md`, `external-tool-access.md`, `learning-memory-interoperability.md`, `model-selection.md`, `response-compression.md`, `solution-option-framing.md`, `workflow-runtime-and-evidence-os.md`.

**Templates/assets có thể tái sử dụng:** `atomic-task-output.yaml`, `design-option-set.yaml`.

**Scripts:** `summarize_terraform_plan.py`.

#### Plan / Design (1 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`platform-create-self-service-template`](skills/data-platform-and-dataops/references/tasks/platform-create-self-service-template.md) | tạo golden path cho pipeline/model/environment | reusable template | `design-specification` | `R1-reviewed` / `standard-path` |

#### Build / Deliver (13 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`platform-backup-data-platform`](skills/data-platform-and-dataops/references/tasks/platform-backup-data-platform.md) | triển khai backup policy và verification | verified backups | `advisory-analysis` | `R0-light` / `fast-path` |
| [`platform-build-data-cd-pipeline`](skills/data-platform-and-dataops/references/tasks/platform-build-data-cd-pipeline.md) | promotion, approval, deploy, smoke test và rollback | CD workflow | `build-change` | `R2-standard` / `standard-path` |
| [`platform-build-data-ci-pipeline`](skills/data-platform-and-dataops/references/tasks/platform-build-data-ci-pipeline.md) | lint, unit test, security scan và artifact build | CI workflow | `build-change` | `R2-standard` / `standard-path` |
| [`platform-configure-data-iam`](skills/data-platform-and-dataops/references/tasks/platform-configure-data-iam.md) | triển khai role/service account/least privilege | access configuration | `build-change` | `R3-controlled` / `controlled-path` |
| [`platform-configure-platform-observability`](skills/data-platform-and-dataops/references/tasks/platform-configure-platform-observability.md) | logs, metrics, traces, dashboards và alerts | observability baseline | `build-change` | `R2-standard` / `standard-path` |
| [`platform-deprecate-platform-component`](skills/data-platform-and-dataops/references/tasks/platform-deprecate-platform-component.md) | inventory consumers, transition và removal | safe deprecation | `advisory-analysis` | `R0-light` / `fast-path` |
| [`platform-enforce-policy-as-code`](skills/data-platform-and-dataops/references/tasks/platform-enforce-policy-as-code.md) | mã hóa guardrails và exception flow | enforced controls | `build-change` | `R2-standard` / `standard-path` |
| [`platform-manage-data-secrets`](skills/data-platform-and-dataops/references/tasks/platform-manage-data-secrets.md) | tạo, rotate và audit secrets | managed secret lifecycle | `advisory-analysis` | `R3-controlled` / `controlled-path` |
| [`platform-manage-network-connectivity`](skills/data-platform-and-dataops/references/tasks/platform-manage-network-connectivity.md) | private endpoints, firewall và routing | validated connectivity | `advisory-analysis` | `R0-light` / `fast-path` |
| [`platform-provision-data-compute`](skills/data-platform-and-dataops/references/tasks/platform-provision-data-compute.md) | cấu hình compute, workload isolation và autoscaling | compute resource | `build-change` | `R2-standard` / `standard-path` |
| [`platform-provision-data-environment`](skills/data-platform-and-dataops/references/tasks/platform-provision-data-environment.md) | tạo dev/test/prod resources theo baseline | usable environment | `build-change` | `R2-standard` / `standard-path` |
| [`platform-provision-data-storage`](skills/data-platform-and-dataops/references/tasks/platform-provision-data-storage.md) | cấu hình bucket/database/schema, lifecycle và encryption | storage resource | `build-change` | `R2-standard` / `standard-path` |
| [`platform-upgrade-data-service`](skills/data-platform-and-dataops/references/tasks/platform-upgrade-data-service.md) | compatibility assessment, staged rollout và rollback | upgraded service | `build-change` | `R2-standard` / `standard-path` |

#### Test / Assure (3 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`platform-evaluate-platform-capacity`](skills/data-platform-and-dataops/references/tasks/platform-evaluate-platform-capacity.md) | stress test concurrency, throughput và saturation | capacity report | `advisory-analysis` | `R0-light` / `fast-path` |
| [`platform-measure-platform-slos`](skills/data-platform-and-dataops/references/tasks/platform-measure-platform-slos.md) | tính availability, latency và failure budget | SLO report | `advisory-analysis` | `R0-light` / `fast-path` |
| [`platform-test-disaster-recovery`](skills/data-platform-and-dataops/references/tasks/platform-test-disaster-recovery.md) | diễn tập restore/failover và đo RTO/RPO | DR test report | `incident-recovery` | `R3-controlled` / `controlled-path` |

#### Operate / Improve (4 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`platform-deploy-orchestrator`](skills/data-platform-and-dataops/references/tasks/platform-deploy-orchestrator.md) | cài đặt, cấu hình và kiểm tra orchestration runtime | operational orchestrator | `production-release` | `R3-controlled` / `controlled-path` |
| [`platform-migrate-platform-workload`](skills/data-platform-and-dataops/references/tasks/platform-migrate-platform-workload.md) | di chuyển workload có dual-run và rollback | migrated workload | `build-change` | `R3-controlled` / `controlled-path` |
| [`platform-optimize-platform-cost`](skills/data-platform-and-dataops/references/tasks/platform-optimize-platform-cost.md) | phân bổ cost, rightsizing và schedule | savings plan | `build-change` | `R2-standard` / `standard-path` |
| [`platform-troubleshoot-platform-incident`](skills/data-platform-and-dataops/references/tasks/platform-troubleshoot-platform-incident.md) | triage infrastructure/runtime fault | restored platform and incident record | `incident-recovery` | `R3-controlled` / `controlled-path` |

<a id="skill-data-developer-experience"></a>

### 10. `data-developer-experience` — Data Developer Experience

**Claude trigger description:** Improve data developer setup, repositories, end-to-end data-path understanding, templates, local environments, CI feedback, standards and inner-loop productivity. Use for Data DevEx, repo reverse engineering, evidence-based walkthroughs or golden paths.

**Ownership:** Tạo golden paths, repository templates, scaffolding, local environments, CI feedback, standards và trải nghiệm tự phục vụ cho data developers.

**Khi nên dùng:** Dùng khi giảm cognitive load, setup time, inconsistency hoặc friction trong vòng đời phát triển dữ liệu.

**Ranh giới và handoff:** Không tối ưu DX bằng cách bỏ security, quality hay governance gates; đo hiệu quả bằng adoption, lead time và escaped defects.

**Quy mô:** 20 tasks — Plan / Design 3; Build / Deliver 11; Test / Assure 5; Operate / Improve 1.

**Domain references tải khi cần:** `adapter-airflow.md`, `adapter-databricks.md`, `adapter-dbt.md`, `adapter-microsoft-fabric.md`, `adapter-spark.md`, `evidence-based-repository-understanding.md`, `learning-memory-interoperability.md`, `model-selection.md`, `response-compression.md`, `solution-option-framing.md`, `workflow-runtime-and-evidence-os.md`.

**Templates/assets có thể tái sử dụng:** `atomic-task-output.yaml`, `data-path-trace.yaml`, `design-option-set.yaml`.

**Scripts:** `build_code_index.py`, `detect_data_stack.py`.

#### Plan / Design (3 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`dx-create-project-demo`](skills/data-developer-experience/references/tasks/dx-create-project-demo.md) | tạo safe sample data, scripted walkthrough và expected outputs | reproducible demo | `design-specification` | `R1-reviewed` / `standard-path` |
| [`dx-create-test-data-fixture`](skills/data-developer-experience/references/tasks/dx-create-test-data-fixture.md) | tạo deterministic edge-case records cho automated tests | test fixture | `design-specification` | `R1-reviewed` / `standard-path` |
| [`dx-select-project-template`](skills/data-developer-experience/references/tasks/dx-select-project-template.md) | chọn template theo stack, deployment và governance needs | template decision | `design-specification` | `R1-reviewed` / `standard-path` |

#### Build / Deliver (11 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`dx-benchmark-data-project`](skills/data-developer-experience/references/tasks/dx-benchmark-data-project.md) | chấm architecture, performance, quality, security, docs và business fit | benchmark scorecard | `advisory-analysis` | `R0-light` / `fast-path` |
| [`dx-bootstrap-local-environment`](skills/data-developer-experience/references/tasks/dx-bootstrap-local-environment.md) | cấu hình runtime, env, credentials placeholders và smoke test | working local setup | `advisory-analysis` | `R0-light` / `fast-path` |
| [`dx-build-project-task-runner`](skills/data-developer-experience/references/tasks/dx-build-project-task-runner.md) | chuẩn hóa commands setup/test/lint/build/run | task runner | `build-change` | `R2-standard` / `standard-path` |
| [`dx-configure-precommit-quality-gates`](skills/data-developer-experience/references/tasks/dx-configure-precommit-quality-gates.md) | cài format, lint, secret scan và file checks | pre-commit workflow | `build-change` | `R2-standard` / `standard-path` |
| [`dx-configure-repository-ci`](skills/data-developer-experience/references/tasks/dx-configure-repository-ci.md) | chạy tests, scans, validation và packaging theo pull request | repository CI | `build-change` | `R2-standard` / `standard-path` |
| [`dx-generate-synthetic-dataset`](skills/data-developer-experience/references/tasks/dx-generate-synthetic-dataset.md) | sinh data giả theo schema, distribution và privacy constraints | synthetic dataset | `advisory-analysis` | `R0-light` / `fast-path` |
| [`dx-manage-project-dependencies`](skills/data-developer-experience/references/tasks/dx-manage-project-dependencies.md) | lock, update, vulnerability-check và document dependencies | reproducible dependency set | `advisory-analysis` | `R0-light` / `fast-path` |
| [`dx-package-data-project`](skills/data-developer-experience/references/tasks/dx-package-data-project.md) | tạo artifact/container/package có version và provenance | deployable project artifact | `build-change` | `R2-standard` / `standard-path` |
| [`dx-recommend-agent-automation`](skills/data-developer-experience/references/tasks/dx-recommend-agent-automation.md) | soi repo data rồi đề xuất hook, subagent, skill và MCP server đáng tự động hoá, chỉ đọc không tạo file | automation recommendation | `advisory-analysis` | `R0-light` / `fast-path` |
| [`dx-reverse-engineer-data-project`](skills/data-developer-experience/references/tasks/dx-reverse-engineer-data-project.md) | trace entry points, pipeline, dependencies và outputs | evidence-based project map | `advisory-analysis` | `R0-light` / `fast-path` |
| [`dx-scaffold-data-project`](skills/data-developer-experience/references/tasks/dx-scaffold-data-project.md) | sinh cấu trúc repo theo workload và standards | runnable project skeleton | `build-change` | `R2-standard` / `standard-path` |

#### Test / Assure (5 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`dx-assess-production-readiness`](skills/data-developer-experience/references/tasks/dx-assess-production-readiness.md) | kiểm tra documentation, tests, deployment, observability và controls | readiness decision | `advisory-analysis` | `R0-light` / `fast-path` |
| [`dx-audit-data-repository`](skills/data-developer-experience/references/tasks/dx-audit-data-repository.md) | phân loại code, configs, tests, docs, data và risks | repository assessment | `governance-assurance` | `R1-reviewed` / `standard-path` |
| [`dx-detect-repository-secrets`](skills/data-developer-experience/references/tasks/dx-detect-repository-secrets.md) | scan current tree/history và tạo remediation plan | secret exposure report | `advisory-analysis` | `R3-controlled` / `controlled-path` |
| [`dx-review-repository-hygiene`](skills/data-developer-experience/references/tasks/dx-review-repository-hygiene.md) | kiểm tra naming, generated files, data leakage và dead code | hygiene report | `advisory-analysis` | `R0-light` / `fast-path` |
| [`dx-trace-data-path-end-to-end`](skills/data-developer-experience/references/tasks/dx-trace-data-path-end-to-end.md) | theo một source hoặc job qua code, configuration, transforms và sink; dự đoán hành vi trước khi chạy rồi đối chiếu observed output | evidence-based end-to-end data path trace | `advisory-analysis` | `R0-light` / `fast-path` |

#### Operate / Improve (1 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`dx-migrate-project-structure`](skills/data-developer-experience/references/tasks/dx-migrate-project-structure.md) | chuyển layout/config có compatibility plan và verification | migrated repository | `build-change` | `R3-controlled` / `controlled-path` |

<a id="skill-data-engineering"></a>

### 11. `data-engineering` — Data Engineering

**Claude trigger description:** Design, build, test, diagnose execution plans and operate batch, API, file, CDC and streaming pipelines with idempotency, schema evolution, reconciliation, recovery and runbooks. Use for Data Engineer ingestion, performance or pipeline work. Route feature pipelines and model serving to machine-learning-engineering, dbt-style modelling to analytics-engineering, and catalog or lineage harvesting to metadata-engineering-and-catalog.

**Ownership:** Thiết kế, xây, kiểm thử và vận hành batch/API/file/CDC/streaming pipelines với idempotency, schema evolution, reconciliation và recovery.

**Khi nên dùng:** Dùng cho ingestion, transformation ở tầng pipeline, orchestration, backfill, replay, troubleshooting và retirement.

**Ranh giới và handoff:** Không mặc định source semantics hoặc successful load; luôn kiểm tra grain, keys, watermark, duplicates, source-target reconciliation và rerun safety.

**Quy mô:** 25 tasks — Plan / Design 3; Build / Deliver 11; Test / Assure 4; Operate / Improve 7.

**Domain references tải khi cần:** `adapter-airflow.md`, `adapter-bigquery.md`, `adapter-databricks.md`, `adapter-dbt.md`, `adapter-kafka-flink.md`, `adapter-microsoft-fabric.md`, `adapter-snowflake.md`, `adapter-spark.md`, `execution-plan-and-pipeline-adapters.md`, `external-tool-access.md`, `learning-memory-interoperability.md`, `model-selection.md`, `response-compression.md`, `solution-option-framing.md`, `stage-gated-data-validation.md`, `workflow-runtime-and-evidence-os.md`, `zero-landing-ingestion.md`.

**Templates/assets có thể tái sử dụng:** `atomic-task-output.yaml`, `design-option-set.yaml`, `execution-plan-review.yaml`, `pipeline-validation-plan.yaml`.

**Scripts:** `inspect_execution_plan.py`.

#### Plan / Design (3 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`de-create-pipeline-runbook`](skills/data-engineering/references/tasks/de-create-pipeline-runbook.md) | viết operations, alerts, recovery và ownership | runbook | `design-specification` | `R2-standard` / `standard-path` |
| [`de-design-ingestion-pipeline`](skills/data-engineering/references/tasks/de-design-ingestion-pipeline.md) | chọn method, cadence, watermark, recovery và controls | ingestion design | `design-specification` | `R2-standard` / `standard-path` |
| [`de-write-pipeline-tests`](skills/data-engineering/references/tasks/de-write-pipeline-tests.md) | unit, contract, integration và failure-path tests | automated test suite | `build-change` | `R2-standard` / `standard-path` |

#### Build / Deliver (11 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`de-add-pipeline-data-checks`](skills/data-engineering/references/tasks/de-add-pipeline-data-checks.md) | kiểm tra schema, count, duplicate và reconciliation | guarded pipeline | `build-change` | `R2-standard` / `standard-path` |
| [`de-build-api-ingestion`](skills/data-engineering/references/tasks/de-build-api-ingestion.md) | xử lý auth, pagination, rate limit và incremental sync | API pipeline | `build-change` | `R2-standard` / `standard-path` |
| [`de-build-batch-ingestion`](skills/data-engineering/references/tasks/de-build-batch-ingestion.md) | nạp batch có checkpoint, audit và retry | production-ready batch pipeline | `build-change` | `R2-standard` / `standard-path` |
| [`de-build-cdc-ingestion`](skills/data-engineering/references/tasks/de-build-cdc-ingestion.md) | capture insert/update/delete và checkpoint | CDC pipeline | `build-change` | `R2-standard` / `standard-path` |
| [`de-build-file-ingestion`](skills/data-engineering/references/tasks/de-build-file-ingestion.md) | xử lý arrival, naming, encoding, schema và duplicate files | file pipeline | `build-change` | `R2-standard` / `standard-path` |
| [`de-build-incremental-load`](skills/data-engineering/references/tasks/de-build-incremental-load.md) | triển khai watermark/merge và late-arriving handling | incremental pipeline | `build-change` | `R2-standard` / `standard-path` |
| [`de-build-streaming-ingestion`](skills/data-engineering/references/tasks/de-build-streaming-ingestion.md) | xử lý partition, ordering, delivery semantics và dead-letter | stream pipeline | `build-change` | `R2-standard` / `standard-path` |
| [`de-handle-schema-evolution`](skills/data-engineering/references/tasks/de-handle-schema-evolution.md) | đánh giá compatible/breaking change và migration | schema-change implementation | `build-change` | `R2-standard` / `standard-path` |
| [`de-make-pipeline-idempotent`](skills/data-engineering/references/tasks/de-make-pipeline-idempotent.md) | đảm bảo rerun không tạo duplicate hoặc corruption | idempotency guarantees | `build-change` | `R2-standard` / `standard-path` |
| [`de-normalize-raw-data`](skills/data-engineering/references/tasks/de-normalize-raw-data.md) | chuẩn hóa type, metadata, timestamp và malformed records | conformed raw layer | `build-change` | `R2-standard` / `standard-path` |
| [`de-orchestrate-data-workflow`](skills/data-engineering/references/tasks/de-orchestrate-data-workflow.md) | cấu hình dependencies, schedule, timeout, retry và SLA | orchestrated DAG | `build-change` | `R2-standard` / `standard-path` |

#### Test / Assure (4 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`de-analyze-execution-plan`](skills/data-engineering/references/tasks/de-analyze-execution-plan.md) | đọc SQL/Spark execution plan trước khi tối ưu để xác định scan, join, shuffle, skew, partition và bottleneck có evidence | execution-plan diagnosis | `advisory-analysis` | `R0-light` / `fast-path` |
| [`de-profile-source-system`](skills/data-engineering/references/tasks/de-profile-source-system.md) | xác định schema, keys, volume, change pattern và limits | source profile | `advisory-analysis` | `R0-light` / `fast-path` |
| [`de-reconcile-source-target`](skills/data-engineering/references/tasks/de-reconcile-source-target.md) | so sánh counts, totals, hashes và sample records | reconciliation report | `advisory-analysis` | `R0-light` / `fast-path` |
| [`de-review-data-engineering-change`](skills/data-engineering/references/tasks/de-review-data-engineering-change.md) | review correctness, resilience, cost, security và operability | review findings | `advisory-analysis` | `R0-light` / `fast-path` |

#### Operate / Improve (7 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`de-backfill-data-range`](skills/data-engineering/references/tasks/de-backfill-data-range.md) | ước lượng scope/cost, chạy chunked backfill và reconcile | verified backfill | `advisory-analysis` | `R3-controlled` / `controlled-path` |
| [`de-deploy-data-pipeline`](skills/data-engineering/references/tasks/de-deploy-data-pipeline.md) | promote config/code, smoke test và monitor | deployed pipeline | `production-release` | `R3-controlled` / `controlled-path` |
| [`de-migrate-data-pipeline`](skills/data-engineering/references/tasks/de-migrate-data-pipeline.md) | dual-run, reconcile, cutover và rollback | migrated pipeline | `build-change` | `R3-controlled` / `controlled-path` |
| [`de-optimize-pipeline-performance`](skills/data-engineering/references/tasks/de-optimize-pipeline-performance.md) | tìm bottleneck I/O/compute/shuffle và tune | benchmarked improvement | `build-change` | `R2-standard` / `standard-path` |
| [`de-replay-stream-events`](skills/data-engineering/references/tasks/de-replay-stream-events.md) | xác định offset, deduplicate và validate replay | verified replay | `advisory-analysis` | `R0-light` / `fast-path` |
| [`de-retire-data-pipeline`](skills/data-engineering/references/tasks/de-retire-data-pipeline.md) | confirm consumers, archive và disable safely | retired pipeline | `production-release` | `R4-critical` / `controlled-path` |
| [`de-troubleshoot-failed-pipeline`](skills/data-engineering/references/tasks/de-troubleshoot-failed-pipeline.md) | isolate source/code/platform/data cause | restored pipeline and diagnosis | `incident-recovery` | `R3-controlled` / `controlled-path` |

<a id="skill-analytics-engineering"></a>

### 12. `analytics-engineering` — Analytics Engineering

**Claude trigger description:** Build governed staging, intermediate, mart, dimensional and semantic models with tests, documentation, lineage, incremental logic and release controls. Use for Analytics Engineering, dbt or analytics-ready dataset work. Route source ingestion to data-engineering and catalog, lineage harvesting or metadata quality to metadata-engineering-and-catalog.

**Ownership:** Chuyển dữ liệu thô thành staging/intermediate/marts, semantic metrics và data products có tests, documentation, lineage và versioning.

**Khi nên dùng:** Dùng cho dimensional modeling, dbt-style workflows, incremental models, snapshots, SCD, metric layer và analytics PR review.

**Ranh giới và handoff:** Không tự chọn business definition đang tranh chấp; metric semantics cần BA/Governance approval trước khi certification hoặc release.

**Quy mô:** 22 tasks — Plan / Design 5; Build / Deliver 10; Test / Assure 4; Operate / Improve 3.

**Domain references tải khi cần:** `adapter-bigquery.md`, `adapter-databricks.md`, `adapter-dbt.md`, `adapter-microsoft-fabric.md`, `adapter-snowflake.md`, `agent-ready-marts.md`, `execution-plan-and-pipeline-adapters.md`, `external-tool-access.md`, `learning-memory-interoperability.md`, `model-selection.md`, `response-compression.md`, `solution-option-framing.md`, `workflow-runtime-and-evidence-os.md`.

**Templates/assets có thể tái sử dụng:** `atomic-task-output.yaml`, `design-option-set.yaml`, `execution-plan-review.yaml`.

**Scripts:** `inspect_execution_plan.py`.

#### Plan / Design (5 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`ae-create-analytics-snapshot`](skills/analytics-engineering/references/tasks/ae-create-analytics-snapshot.md) | lưu point-in-time state có valid-from/to | snapshot model | `design-specification` | `R1-reviewed` / `standard-path` |
| [`ae-design-dimensional-model`](skills/analytics-engineering/references/tasks/ae-design-dimensional-model.md) | xác định grain, facts, dimensions và keys | dimensional design | `design-specification` | `R1-reviewed` / `standard-path` |
| [`ae-design-self-service-data-product`](skills/analytics-engineering/references/tasks/ae-design-self-service-data-product.md) | đóng gói discoverability, contract, examples và SLO | analytical data product | `design-specification` | `R1-reviewed` / `standard-path` |
| [`ae-document-analytics-model`](skills/analytics-engineering/references/tasks/ae-document-analytics-model.md) | mô tả grain, columns, caveats, lineage và owner | model documentation | `advisory-analysis` | `R0-light` / `fast-path` |
| [`ae-write-model-tests`](skills/analytics-engineering/references/tasks/ae-write-model-tests.md) | kiểm tra key, relationship, accepted values và business assertions | model test suite | `design-specification` | `R1-reviewed` / `standard-path` |

#### Build / Deliver (10 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`ae-build-analytics-mart`](skills/analytics-engineering/references/tasks/ae-build-analytics-mart.md) | tạo subject-area fact/dimension/wide mart | consumable mart | `build-change` | `R2-standard` / `standard-path` |
| [`ae-build-intermediate-model`](skills/analytics-engineering/references/tasks/ae-build-intermediate-model.md) | đóng gói reusable business transformations | intermediate model | `build-change` | `R2-standard` / `standard-path` |
| [`ae-build-staging-model`](skills/analytics-engineering/references/tasks/ae-build-staging-model.md) | rename, cast và standardize source-aligned data | staging model | `build-change` | `R2-standard` / `standard-path` |
| [`ae-deprecate-analytics-model`](skills/analytics-engineering/references/tasks/ae-deprecate-analytics-model.md) | migrate consumers, preserve history và remove safely | retired model | `advisory-analysis` | `R0-light` / `fast-path` |
| [`ae-implement-incremental-model`](skills/analytics-engineering/references/tasks/ae-implement-incremental-model.md) | định nghĩa unique key, filter và merge behavior | incremental model | `build-change` | `R2-standard` / `standard-path` |
| [`ae-implement-semantic-metric`](skills/analytics-engineering/references/tasks/ae-implement-semantic-metric.md) | mã hóa formula, grain, dimensions và time semantics | semantic metric | `build-change` | `R2-standard` / `standard-path` |
| [`ae-implement-slowly-changing-dimension`](skills/analytics-engineering/references/tasks/ae-implement-slowly-changing-dimension.md) | quản lý lịch sử dimension theo SCD strategy | historical dimension | `build-change` | `R2-standard` / `standard-path` |
| [`ae-manage-metric-version`](skills/analytics-engineering/references/tasks/ae-manage-metric-version.md) | xử lý breaking formula change, dual-run và communication | versioned metric | `advisory-analysis` | `R0-light` / `fast-path` |
| [`ae-refactor-analytics-model`](skills/analytics-engineering/references/tasks/ae-refactor-analytics-model.md) | giảm duplication/complexity mà giữ contract | refactored model | `build-change` | `R2-standard` / `standard-path` |
| [`ae-translate-business-logic`](skills/analytics-engineering/references/tasks/ae-translate-business-logic.md) | chuyển rule nghiệp vụ thành transformation specification | logic spec | `advisory-analysis` | `R0-light` / `fast-path` |

#### Test / Assure (4 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`ae-assess-model-change-impact`](skills/analytics-engineering/references/tasks/ae-assess-model-change-impact.md) | tìm consumers, metric changes và migration needs | impact assessment | `advisory-analysis` | `R0-light` / `fast-path` |
| [`ae-certify-analytics-dataset`](skills/analytics-engineering/references/tasks/ae-certify-analytics-dataset.md) | thu test, freshness, documentation và ownership evidence | certification package | `governance-assurance` | `R1-reviewed` / `standard-path` |
| [`ae-detect-duplicate-metrics`](skills/analytics-engineering/references/tasks/ae-detect-duplicate-metrics.md) | so sánh definitions và usage để đề xuất consolidation | duplication report | `advisory-analysis` | `R0-light` / `fast-path` |
| [`ae-review-analytics-pull-request`](skills/analytics-engineering/references/tasks/ae-review-analytics-pull-request.md) | review grain, logic, tests, style và downstream impact | review decision | `advisory-analysis` | `R0-light` / `fast-path` |

#### Operate / Improve (3 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`ae-backfill-analytics-model`](skills/analytics-engineering/references/tasks/ae-backfill-analytics-model.md) | chạy history rebuild và reconcile metrics | verified backfill | `advisory-analysis` | `R3-controlled` / `controlled-path` |
| [`ae-optimize-analytics-query`](skills/analytics-engineering/references/tasks/ae-optimize-analytics-query.md) | tune joins, pruning, materialization và compute | measured performance gain | `build-change` | `R2-standard` / `standard-path` |
| [`ae-troubleshoot-model-failure`](skills/analytics-engineering/references/tasks/ae-troubleshoot-model-failure.md) | phân biệt source, logic, dependency và warehouse faults | restored model | `incident-recovery` | `R3-controlled` / `controlled-path` |

<a id="skill-data-analysis"></a>

### 13. `data-analysis` — Data Analysis

**Claude trigger description:** Perform programmatic EDA, reproducible analysis, SQL-to-business explanation, methodology communication, peer review and retrospective. Use for Data Analyst requests involving datasets, SQL, statistics, insights or analytical quality.

**Ownership:** Trả lời business questions bằng analysis plan, SQL/Python, EDA, segmentation, root-cause, forecasting nhẹ và insight có evidence.

**Khi nên dùng:** Dùng khi primary deliverable là câu trả lời phân tích, decision support hoặc analytical narrative thay vì production data product.

**Ranh giới và handoff:** Tách observation, inference và recommendation; không ngụy tạo causal claim, statistical certainty hoặc business confirmation.

**Quy mô:** 29 tasks — Plan / Design 8; Build / Deliver 9; Test / Assure 10; Operate / Improve 2.

**Domain references tải khi cần:** `adapter-bigquery.md`, `adapter-databricks.md`, `adapter-microsoft-fabric.md`, `adapter-snowflake.md`, `analysis-rigor-and-communication.md`, `learning-memory-interoperability.md`, `model-selection.md`, `response-compression.md`, `solution-option-framing.md`, `workflow-runtime-and-evidence-os.md`.

**Templates/assets có thể tái sử dụng:** `analysis-peer-review.yaml`, `analysis-retrospective.yaml`, `atomic-task-output.yaml`, `design-option-set.yaml`, `eda-report.yaml`, `impact-estimate.yaml`, `methodology-note.yaml`, `query-logic-explanation.yaml`.

**Scripts:** `explain_sql.py`, `profile_dataset.py`.

#### Plan / Design (8 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`da-clarify-business-question`](skills/data-analysis/references/tasks/da-clarify-business-question.md) | chuyển yêu cầu mơ hồ thành decision, population, period và success criteria | analysis brief | `advisory-analysis` | `R0-light` / `fast-path` |
| [`da-create-analysis-visualization`](skills/data-analysis/references/tasks/da-create-analysis-visualization.md) | chọn chart và encoding đúng analytical message | visualization artifact | `design-specification` | `R1-reviewed` / `standard-path` |
| [`da-define-metric-requirement`](skills/data-analysis/references/tasks/da-define-metric-requirement.md) | định nghĩa business intent, formula, grain, filters và examples | metric requirement | `design-specification` | `R1-reviewed` / `standard-path` |
| [`da-design-dashboard-requirement`](skills/data-analysis/references/tasks/da-design-dashboard-requirement.md) | xác định audience, decisions, KPIs, cuts và interactions | dashboard spec | `design-specification` | `R1-reviewed` / `standard-path` |
| [`da-document-analysis`](skills/data-analysis/references/tasks/da-document-analysis.md) | lưu question, logic, queries, results, caveats và reproducibility | analysis record | `advisory-analysis` | `R0-light` / `fast-path` |
| [`da-write-analysis-plan`](skills/data-analysis/references/tasks/da-write-analysis-plan.md) | xác định hypotheses, metrics, dimensions, method và limitations | analysis plan | `design-specification` | `R1-reviewed` / `standard-path` |
| [`da-write-analysis-query`](skills/data-analysis/references/tasks/da-write-analysis-query.md) | tạo SQL đúng grain và logic cho question | validated query | `design-specification` | `R1-reviewed` / `standard-path` |
| [`da-write-insight-narrative`](skills/data-analysis/references/tasks/da-write-insight-narrative.md) | trình bày what/so-what/why/now-what với evidence | insight memo | `design-specification` | `R1-reviewed` / `standard-path` |

#### Build / Deliver (9 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`da-answer-ad-hoc-question`](skills/data-analysis/references/tasks/da-answer-ad-hoc-question.md) | thực hiện analysis nhỏ có query, evidence và caveats | decision-ready answer | `advisory-analysis` | `R0-light` / `fast-path` |
| [`da-build-business-forecast`](skills/data-analysis/references/tasks/da-build-business-forecast.md) | tạo forecast phục vụ planning kèm uncertainty | forecast and assumptions | `build-change` | `R2-standard` / `standard-path` |
| [`da-discover-analysis-data`](skills/data-analysis/references/tasks/da-discover-analysis-data.md) | tìm datasets/metrics phù hợp và đánh giá fitness | selected data sources | `advisory-analysis` | `R0-light` / `fast-path` |
| [`da-estimate-business-opportunity`](skills/data-analysis/references/tasks/da-estimate-business-opportunity.md) | ước lượng population, uplift, cost và uncertainty | opportunity sizing | `advisory-analysis` | `R0-light` / `fast-path` |
| [`da-explain-analysis-methodology`](skills/data-analysis/references/tasks/da-explain-analysis-methodology.md) | giải thích data, method, assumptions, uncertainty và limitations theo audience tier | audience-calibrated methodology note | `advisory-analysis` | `R0-light` / `fast-path` |
| [`da-explain-sql-business-logic`](skills/data-analysis/references/tasks/da-explain-sql-business-logic.md) | chuyển sources, joins, filters, grain, aggregations và output columns của SQL thành logic nghiệp vụ kèm validation questions | query logic explanation | `advisory-analysis` | `R0-light` / `fast-path` |
| [`da-present-analysis`](skills/data-analysis/references/tasks/da-present-analysis.md) | cấu trúc narrative, anticipated objections và decision ask | presentation package | `advisory-analysis` | `R0-light` / `fast-path` |
| [`da-run-descriptive-analysis`](skills/data-analysis/references/tasks/da-run-descriptive-analysis.md) | tóm tắt level, trend, distribution và composition | descriptive findings | `advisory-analysis` | `R0-light` / `fast-path` |
| [`da-segment-entities`](skills/data-analysis/references/tasks/da-segment-entities.md) | tạo meaningful customer/product/account segments | segment profile | `advisory-analysis` | `R0-light` / `fast-path` |

#### Test / Assure (10 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`da-analyze-cohort`](skills/data-analysis/references/tasks/da-analyze-cohort.md) | xây cohort matrix và so sánh behavior theo start period | cohort findings | `advisory-analysis` | `R0-light` / `fast-path` |
| [`da-analyze-funnel`](skills/data-analysis/references/tasks/da-analyze-funnel.md) | tính stage conversion, drop-off và segment differences | funnel findings | `advisory-analysis` | `R0-light` / `fast-path` |
| [`da-analyze-kpi-variance`](skills/data-analysis/references/tasks/da-analyze-kpi-variance.md) | tách change theo volume/rate/mix/time/segment | variance decomposition | `advisory-analysis` | `R0-light` / `fast-path` |
| [`da-analyze-retention-churn`](skills/data-analysis/references/tasks/da-analyze-retention-churn.md) | định nghĩa retained/churned và xác định patterns | retention analysis | `advisory-analysis` | `R0-light` / `fast-path` |
| [`da-analyze-root-cause`](skills/data-analysis/references/tasks/da-analyze-root-cause.md) | dùng issue tree và decomposition để tìm driver | causal hypothesis tree | `advisory-analysis` | `R0-light` / `fast-path` |
| [`da-diagnose-metric-change`](skills/data-analysis/references/tasks/da-diagnose-metric-change.md) | kiểm tra instrumentation, data quality và business drivers | ranked root causes | `advisory-analysis` | `R0-light` / `fast-path` |
| [`da-review-dashboard-accuracy`](skills/data-analysis/references/tasks/da-review-dashboard-accuracy.md) | kiểm tra numbers, filters, grain, labels và edge cases | QA report | `advisory-analysis` | `R0-light` / `fast-path` |
| [`da-run-analysis-peer-review`](skills/data-analysis/references/tasks/da-run-analysis-peer-review.md) | review question-method alignment, data fitness, SQL/code, statistics, assumptions, narrative và reproducibility | analysis peer-review decision | `advisory-analysis` | `R0-light` / `fast-path` |
| [`da-run-programmatic-eda`](skills/data-analysis/references/tasks/da-run-programmatic-eda.md) | profile grain, types, missingness, duplicates, distributions, outliers, cardinality và data fitness trước phân tích sâu | reproducible EDA report | `advisory-analysis` | `R0-light` / `fast-path` |
| [`da-validate-analysis-result`](skills/data-analysis/references/tasks/da-validate-analysis-result.md) | kiểm tra totals, edge cases, benchmark và alternate query | validation evidence | `advisory-analysis` | `R0-light` / `fast-path` |

#### Operate / Improve (2 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`da-monitor-business-metric`](skills/data-analysis/references/tasks/da-monitor-business-metric.md) | theo dõi threshold/trend và giải thích biến động | monitoring update | `advisory-analysis` | `R0-light` / `fast-path` |
| [`da-run-analysis-retrospective`](skills/data-analysis/references/tasks/da-run-analysis-retrospective.md) | so sánh plan với thực tế, tìm nguyên nhân rework và chuyển lessons thành actions/templates/standards có owner | analysis retrospective and improvement actions | `advisory-analysis` | `R0-light` / `fast-path` |

<a id="skill-business-intelligence"></a>

### 14. `business-intelligence` — Business Intelligence

**Claude trigger description:** Design, build, test and govern BI semantic models, KPIs, dashboards, reports, interactions, row-level security, refresh, accessibility and adoption. Use for BI Engineer, reporting or dashboard work. This skill owns the semantic layer upward; pipelines belong to data-engineering.

**Ownership:** Thiết kế, xây và vận hành dashboards/reports, semantic presentation, visualization, access, performance, UAT, release và adoption.

**Khi nên dùng:** Dùng khi deliverable chính là trải nghiệm BI cho người dùng hoặc báo cáo vận hành/executive.

**Ranh giới và handoff:** Không nhúng logic metric chưa được quản trị vào dashboard; release phải có data validation, usability/accessibility và owner acceptance.

**Quy mô:** 32 tasks — Plan / Design 4; Build / Deliver 15; Test / Assure 8; Operate / Improve 5.

**Domain references tải khi cần:** `adapter-bigquery.md`, `adapter-microsoft-fabric.md`, `adapter-power-bi.md`, `adapter-snowflake.md`, `adapter-tableau-looker.md`, `dashboard-experience-quality.md`, `dashboards-as-code.md`, `external-tool-access.md`, `learning-memory-interoperability.md`, `model-selection.md`, `response-compression.md`, `solution-option-framing.md`, `workflow-runtime-and-evidence-os.md`.

**Templates/assets có thể tái sử dụng:** `atomic-task-output.yaml`, `dashboard-experience-audit.yaml`, `design-option-set.yaml`.

**Scripts:** `validate_dashboard_spec.py`.

#### Plan / Design (4 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`bi-create-cleaning-transformation-plan`](skills/business-intelligence/references/tasks/bi-create-cleaning-transformation-plan.md) | thiết kế reversible, idempotent cleaning và reconciliation | transformation plan | `design-specification` | `R1-reviewed` / `standard-path` |
| [`bi-create-platform-neutral-report-spec`](skills/business-intelligence/references/tasks/bi-create-platform-neutral-report-spec.md) | định nghĩa pages, visuals, filters, interactions và accessibility | neutral report spec | `design-specification` | `R1-reviewed` / `standard-path` |
| [`bi-prepare-release-approval`](skills/business-intelligence/references/tasks/bi-prepare-release-approval.md) | gom approved gates, open risks, version và target environment | release package | `production-release` | `R3-controlled` / `controlled-path` |
| [`bi-redesign-dashboard-experience`](skills/business-intelligence/references/tasks/bi-redesign-dashboard-experience.md) | chuyển audit và dashboard spec thành redesign có traceability, design-system fit, truthful content, test matrix và migration scope | implementation-ready dashboard redesign specification | `design-specification` | `R1-reviewed` / `standard-path` |

#### Build / Deliver (15 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`bi-author-analytical-report`](skills/business-intelligence/references/tasks/bi-author-analytical-report.md) | viết report có methods, findings, limitations và recommendations | analytical report | `advisory-analysis` | `R0-light` / `fast-path` |
| [`bi-build-business-domain-brief`](skills/business-intelligence/references/tasks/bi-build-business-domain-brief.md) | mô hình hóa process, entity, event, state và policy | domain brief | `build-change` | `R2-standard` / `standard-path` |
| [`bi-build-dashboard`](skills/business-intelligence/references/tasks/bi-build-dashboard.md) | hiện thực pages, visuals, filters và navigation | working dashboard | `build-change` | `R2-standard` / `standard-path` |
| [`bi-build-semantic-model`](skills/business-intelligence/references/tasks/bi-build-semantic-model.md) | cấu hình relationships, measures, hierarchies và date logic | BI semantic model | `build-change` | `R2-standard` / `standard-path` |
| [`bi-build-source-authority-matrix`](skills/business-intelligence/references/tasks/bi-build-source-authority-matrix.md) | chọn nguồn chuẩn theo KPI/dimension/use case | BI authority matrix | `build-change` | `R2-standard` / `standard-path` |
| [`bi-configure-dashboard-refresh`](skills/business-intelligence/references/tasks/bi-configure-dashboard-refresh.md) | thiết lập schedule, credential và failure alert | reliable refresh | `build-change` | `R2-standard` / `standard-path` |
| [`bi-export-analytical-report`](skills/business-intelligence/references/tasks/bi-export-analytical-report.md) | render approved source thành Markdown/PDF có kiểm tra | published report files | `advisory-analysis` | `R0-light` / `fast-path` |
| [`bi-implement-dashboard-measures`](skills/business-intelligence/references/tasks/bi-implement-dashboard-measures.md) | tạo measures đúng context và aggregation | tested measures | `build-change` | `R2-standard` / `standard-path` |
| [`bi-implement-row-level-security`](skills/business-intelligence/references/tasks/bi-implement-row-level-security.md) | ánh xạ identity tới access filters | tested RLS | `build-change` | `R3-controlled` / `controlled-path` |
| [`bi-maintain-evidence-ledger`](skills/business-intelligence/references/tasks/bi-maintain-evidence-ledger.md) | nối claim/metric/visual tới query và evidence status | evidence ledger | `advisory-analysis` | `R0-light` / `fast-path` |
| [`bi-maintain-report-product`](skills/business-intelligence/references/tasks/bi-maintain-report-product.md) | xử lý source/metric/platform change và regression validation | maintained BI release | `advisory-analysis` | `R0-light` / `fast-path` |
| [`bi-run-discovery-dialogue`](skills/business-intelligence/references/tasks/bi-run-discovery-dialogue.md) | hỏi thích ứng, không lặp và ghi question/answer/conflict | discovery register | `advisory-analysis` | `R0-light` / `fast-path` |
| [`bi-run-independent-uat`](skills/business-intelligence/references/tasks/bi-run-independent-uat.md) | kiểm tra numerical, structural, visual, security, accessibility và operations | UAT evidence | `advisory-analysis` | `R0-light` / `fast-path` |
| [`bi-translate-dashboard-spec`](skills/business-intelligence/references/tasks/bi-translate-dashboard-spec.md) | chuyển requirement thành dataset, measures, pages và interactions | BI design | `advisory-analysis` | `R0-light` / `fast-path` |
| [`bi-version-dashboard-change`](skills/business-intelligence/references/tasks/bi-version-dashboard-change.md) | quản lý breaking change, release note và rollback | versioned release | `advisory-analysis` | `R0-light` / `fast-path` |

#### Test / Assure (8 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`bi-assess-information-sufficiency`](skills/business-intelligence/references/tasks/bi-assess-information-sufficiency.md) | phân loại confirmed/inferred/blocking/conflicting | sufficiency decision | `advisory-analysis` | `R0-light` / `fast-path` |
| [`bi-audit-dashboard-experience`](skills/business-intelligence/references/tasks/bi-audit-dashboard-experience.md) | đánh giá read-only decision fit, hierarchy, metric truth, information density, interaction states, accessibility, responsiveness và dấu hiệu dashboard generic | prioritized dashboard experience audit | `advisory-analysis` | `R0-light` / `fast-path` |
| [`bi-certify-dashboard`](skills/business-intelligence/references/tasks/bi-certify-dashboard.md) | kiểm tra source, owner, quality, documentation và access | certification package | `governance-assurance` | `R1-reviewed` / `standard-path` |
| [`bi-reconcile-dashboard-report`](skills/business-intelligence/references/tasks/bi-reconcile-dashboard-report.md) | đảm bảo KPI, filters, claims và limitations nhất quán | reconciliation report | `advisory-analysis` | `R0-light` / `fast-path` |
| [`bi-review-report-section`](skills/business-intelligence/references/tasks/bi-review-report-section.md) | kiểm tra và xin approval theo từng section | section approval status | `advisory-analysis` | `R0-light` / `fast-path` |
| [`bi-test-dashboard-usability`](skills/business-intelligence/references/tasks/bi-test-dashboard-usability.md) | kiểm tra navigation, readability, accessibility và mobile | usability findings | `advisory-analysis` | `R0-light` / `fast-path` |
| [`bi-validate-dashboard-data`](skills/business-intelligence/references/tasks/bi-validate-dashboard-data.md) | reconcile dashboard với certified source | validation report | `advisory-analysis` | `R0-light` / `fast-path` |
| [`bi-validate-report-claims`](skills/business-intelligence/references/tasks/bi-validate-report-claims.md) | phát hiện unsupported claim, semantic drift và missing evidence | report QA findings | `advisory-analysis` | `R0-light` / `fast-path` |

#### Operate / Improve (5 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`bi-monitor-dashboard-usage`](skills/business-intelligence/references/tasks/bi-monitor-dashboard-usage.md) | đo viewers, frequency, latency và unused content | usage report | `advisory-analysis` | `R0-light` / `fast-path` |
| [`bi-optimize-dashboard-performance`](skills/business-intelligence/references/tasks/bi-optimize-dashboard-performance.md) | giảm query/render time và model size | benchmarked improvement | `build-change` | `R2-standard` / `standard-path` |
| [`bi-publish-dashboard`](skills/business-intelligence/references/tasks/bi-publish-dashboard.md) | deploy workspace/app, permissions và refresh | published dashboard | `production-release` | `R3-controlled` / `controlled-path` |
| [`bi-retire-dashboard`](skills/business-intelligence/references/tasks/bi-retire-dashboard.md) | tìm consumers, cung cấp replacement và archive | retired dashboard | `production-release` | `R4-critical` / `controlled-path` |
| [`bi-troubleshoot-dashboard`](skills/business-intelligence/references/tasks/bi-troubleshoot-dashboard.md) | xử lý data, refresh, permission hoặc visual issue | restored dashboard | `incident-recovery` | `R3-controlled` / `controlled-path` |

<a id="skill-product-analytics-and-experimentation"></a>

### 15. `product-analytics-and-experimentation` — Product Analytics and Experimentation

**Claude trigger description:** Define product events and metrics, analyze funnels, activation, retention and growth, and design or evaluate experiments. Use for Product Analyst, growth analytics, instrumentation or A/B testing work.

**Ownership:** Định nghĩa event taxonomy, tracking plans, funnels, cohorts, retention, attribution, A/B tests và product decision evidence.

**Khi nên dùng:** Dùng cho câu hỏi về hành vi sản phẩm, instrumentation hoặc thiết kế/đọc thí nghiệm.

**Ranh giới và handoff:** Không tuyên bố causal effect nếu assignment, exposure, power, guardrails hoặc validity checks không đạt.

**Quy mô:** 17 tasks — Plan / Design 5; Build / Deliver 5; Test / Assure 7; Operate / Improve 0.

**Domain references tải khi cần:** `adapter-bigquery.md`, `adapter-databricks.md`, `adapter-snowflake.md`, `learning-memory-interoperability.md`, `model-selection.md`, `response-compression.md`, `solution-option-framing.md`, `workflow-runtime-and-evidence-os.md`.

**Templates/assets có thể tái sử dụng:** `atomic-task-output.yaml`, `design-option-set.yaml`.

#### Plan / Design (5 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`exp-design-ab-test`](skills/product-analytics-and-experimentation/references/tasks/exp-design-ab-test.md) | chọn unit, randomization, variants, duration và analysis plan | experiment design | `design-specification` | `R1-reviewed` / `standard-path` |
| [`exp-frame-experiment-hypothesis`](skills/product-analytics-and-experimentation/references/tasks/exp-frame-experiment-hypothesis.md) | định nghĩa intervention, mechanism, outcome và guardrail | testable hypothesis | `design-specification` | `R1-reviewed` / `standard-path` |
| [`pa-define-product-event`](skills/product-analytics-and-experimentation/references/tasks/pa-define-product-event.md) | định nghĩa event, properties, trigger, identity và validation | tracking spec entry | `design-specification` | `R1-reviewed` / `standard-path` |
| [`pa-define-product-north-star`](skills/product-analytics-and-experimentation/references/tasks/pa-define-product-north-star.md) | xác định value event, frequency, breadth và guardrails | north-star framework | `design-specification` | `R1-reviewed` / `standard-path` |
| [`pa-design-event-taxonomy`](skills/product-analytics-and-experimentation/references/tasks/pa-design-event-taxonomy.md) | chuẩn hóa naming, entities và lifecycle | event taxonomy | `design-specification` | `R1-reviewed` / `standard-path` |

#### Build / Deliver (5 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`exp-calculate-sample-size`](skills/product-analytics-and-experimentation/references/tasks/exp-calculate-sample-size.md) | tính MDE, power, alpha và traffic duration | sample-size plan | `advisory-analysis` | `R0-light` / `fast-path` |
| [`exp-handle-experiment-peeking`](skills/product-analytics-and-experimentation/references/tasks/exp-handle-experiment-peeking.md) | áp dụng sequential/correction rule | valid stopping decision | `advisory-analysis` | `R0-light` / `fast-path` |
| [`exp-register-experiment`](skills/product-analytics-and-experimentation/references/tasks/exp-register-experiment.md) | lưu hypothesis, setup, result và decision | experiment registry entry | `advisory-analysis` | `R0-light` / `fast-path` |
| [`pa-build-growth-accounting`](skills/product-analytics-and-experimentation/references/tasks/pa-build-growth-accounting.md) | phân rã new/reactivated/retained/resurrected/churned | growth accounting | `build-change` | `R2-standard` / `standard-path` |
| [`pa-qa-product-instrumentation`](skills/product-analytics-and-experimentation/references/tasks/pa-qa-product-instrumentation.md) | kiểm tra firing, payload, identity và duplication | instrumentation QA report | `advisory-analysis` | `R0-light` / `fast-path` |

#### Test / Assure (7 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`exp-analyze-experiment`](skills/product-analytics-and-experimentation/references/tasks/exp-analyze-experiment.md) | ước lượng effect, interval, guardrails và heterogeneity | experiment readout | `advisory-analysis` | `R0-light` / `fast-path` |
| [`exp-check-randomization`](skills/product-analytics-and-experimentation/references/tasks/exp-check-randomization.md) | kiểm tra sample ratio mismatch và balance | randomization report | `advisory-analysis` | `R0-light` / `fast-path` |
| [`pa-analyze-activation`](skills/product-analytics-and-experimentation/references/tasks/pa-analyze-activation.md) | định nghĩa activation và xác định actions liên quan value | activation analysis | `advisory-analysis` | `R0-light` / `fast-path` |
| [`pa-analyze-feature-adoption`](skills/product-analytics-and-experimentation/references/tasks/pa-analyze-feature-adoption.md) | đo exposure, trial, repeat và depth | adoption report | `advisory-analysis` | `R0-light` / `fast-path` |
| [`pa-analyze-product-churn`](skills/product-analytics-and-experimentation/references/tasks/pa-analyze-product-churn.md) | tìm patterns trước churn và affected segments | churn findings | `advisory-analysis` | `R0-light` / `fast-path` |
| [`pa-analyze-product-retention`](skills/product-analytics-and-experimentation/references/tasks/pa-analyze-product-retention.md) | đo logo/user/activity retention theo cohorts | retention report | `advisory-analysis` | `R0-light` / `fast-path` |
| [`pa-analyze-user-journey`](skills/product-analytics-and-experimentation/references/tasks/pa-analyze-user-journey.md) | map paths, transitions và friction points | journey findings | `advisory-analysis` | `R0-light` / `fast-path` |

<a id="skill-data-science"></a>

### 16. `data-science` — Data Science

**Claude trigger description:** Frame and execute statistical, causal, forecasting, optimization and machine-learning studies with leakage controls, validation, explainability and model-risk evidence. Use for Data Scientist or decision-science work.

**Ownership:** Đóng khung bài toán, xây dataset/features, baseline, experiments, statistical/ML models, explainability và model validation.

**Khi nên dùng:** Dùng cho discovery và development của mô hình hoặc nghiên cứu định lượng cần đánh giá ngoài mẫu.

**Ranh giới và handoff:** Không đồng nhất offline metric với business impact; deployment/serving thuộc MLE/MLOps và cần promotion gate riêng.

**Quy mô:** 22 tasks — Plan / Design 5; Build / Deliver 13; Test / Assure 3; Operate / Improve 1.

**Domain references tải khi cần:** `adapter-bigquery.md`, `adapter-databricks.md`, `adapter-mlflow-kubeflow.md`, `adapter-spark.md`, `learning-memory-interoperability.md`, `model-selection.md`, `response-compression.md`, `solution-option-framing.md`, `workflow-runtime-and-evidence-os.md`.

**Templates/assets có thể tái sử dụng:** `atomic-task-output.yaml`, `design-option-set.yaml`.

**Scripts:** `check_experiment_design.py`.

#### Plan / Design (5 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`ds-create-model-card`](skills/data-science/references/tasks/ds-create-model-card.md) | ghi intended use, data, metrics, risks và limitations | model card | `design-specification` | `R1-reviewed` / `standard-path` |
| [`ds-design-modeling-dataset`](skills/data-science/references/tasks/ds-design-modeling-dataset.md) | định nghĩa observation unit, labels, cutoff và sampling | dataset specification | `design-specification` | `R1-reviewed` / `standard-path` |
| [`ds-design-offline-experiment`](skills/data-science/references/tasks/ds-design-offline-experiment.md) | thiết kế validation có power và unbiased comparison | evaluation design | `design-specification` | `R1-reviewed` / `standard-path` |
| [`ds-frame-modeling-problem`](skills/data-science/references/tasks/ds-frame-modeling-problem.md) | chuyển business decision thành target, unit, horizon và constraints | modeling brief | `design-specification` | `R1-reviewed` / `standard-path` |
| [`ds-select-evaluation-metric`](skills/data-science/references/tasks/ds-select-evaluation-metric.md) | chọn metric phù hợp cost/error/base rate | evaluation protocol | `design-specification` | `R1-reviewed` / `standard-path` |

#### Build / Deliver (13 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`ds-build-baseline-model`](skills/data-science/references/tasks/ds-build-baseline-model.md) | thiết lập heuristic/simple model benchmark | baseline metrics | `build-change` | `R2-standard` / `standard-path` |
| [`ds-build-optimization-model`](skills/data-science/references/tasks/ds-build-optimization-model.md) | định nghĩa objective, constraints và scenario evaluation | optimization solution | `build-change` | `R2-standard` / `standard-path` |
| [`ds-build-time-series-forecast`](skills/data-science/references/tasks/ds-build-time-series-forecast.md) | xử lý seasonality, hierarchy, backtest và intervals | forecast model | `build-change` | `R2-standard` / `standard-path` |
| [`ds-engineer-features`](skills/data-science/references/tasks/ds-engineer-features.md) | tạo features có rationale, availability và reproducibility | feature set | `advisory-analysis` | `R0-light` / `fast-path` |
| [`ds-estimate-causal-effect`](skills/data-science/references/tasks/ds-estimate-causal-effect.md) | chọn identification strategy, assumptions và robustness tests | causal estimate | `advisory-analysis` | `R0-light` / `fast-path` |
| [`ds-explain-model`](skills/data-science/references/tasks/ds-explain-model.md) | phân tích global/local drivers và limitations | explainability report | `advisory-analysis` | `R0-light` / `fast-path` |
| [`ds-handoff-model-to-engineering`](skills/data-science/references/tasks/ds-handoff-model-to-engineering.md) | đóng gói artifact, features, inference contract và acceptance tests | production handoff | `advisory-analysis` | `R0-light` / `fast-path` |
| [`ds-prevent-data-leakage`](skills/data-science/references/tasks/ds-prevent-data-leakage.md) | audit temporal, target, identity và split leakage | leakage assessment | `advisory-analysis` | `R0-light` / `fast-path` |
| [`ds-reproduce-model-result`](skills/data-science/references/tasks/ds-reproduce-model-result.md) | tái tạo dataset, code, environment và metrics | reproducibility report | `advisory-analysis` | `R0-light` / `fast-path` |
| [`ds-run-exploratory-analysis`](skills/data-science/references/tasks/ds-run-exploratory-analysis.md) | đánh giá distribution, missingness, relationship và anomalies | EDA report | `advisory-analysis` | `R0-light` / `fast-path` |
| [`ds-run-scenario-simulation`](skills/data-science/references/tasks/ds-run-scenario-simulation.md) | mô phỏng uncertainty và policy alternatives | scenario analysis | `advisory-analysis` | `R0-light` / `fast-path` |
| [`ds-train-model`](skills/data-science/references/tasks/ds-train-model.md) | huấn luyện pipeline reproducible với tracked config | trained candidate | `build-change` | `R2-standard` / `standard-path` |
| [`ds-tune-hyperparameters`](skills/data-science/references/tasks/ds-tune-hyperparameters.md) | search có budget và nested validation phù hợp | tuned candidate | `advisory-analysis` | `R0-light` / `fast-path` |

#### Test / Assure (3 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`ds-assess-model-fairness`](skills/data-science/references/tasks/ds-assess-model-fairness.md) | đo subgroup performance, disparity và mitigation | fairness assessment | `advisory-analysis` | `R0-light` / `fast-path` |
| [`ds-detect-anomalies`](skills/data-science/references/tasks/ds-detect-anomalies.md) | xây expected behavior và calibrated anomaly threshold | anomaly model | `advisory-analysis` | `R0-light` / `fast-path` |
| [`ds-validate-model`](skills/data-science/references/tasks/ds-validate-model.md) | đánh giá holdout, stability, uncertainty và business metric | validation report | `advisory-analysis` | `R0-light` / `fast-path` |

#### Operate / Improve (1 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`ds-monitor-model-business-value`](skills/data-science/references/tasks/ds-monitor-model-business-value.md) | liên kết model usage với outcome và counterfactual baseline | value report | `advisory-analysis` | `R0-light` / `fast-path` |

<a id="skill-machine-learning-engineering"></a>

### 17. `machine-learning-engineering` — Machine Learning Engineering

**Claude trigger description:** Engineer training pipelines, features, model artifacts, batch or online serving, performance, testing, deployment interfaces and resilience. Use for ML Engineer implementation and productionization work. Route general batch, CDC or streaming ingestion to data-engineering, and registry, drift or model rollout operations to mlops.

**Ownership:** Chuyển model thành phần mềm đáng tin cậy: training/inference code, feature pipelines, serving, performance, integration và release artifacts.

**Khi nên dùng:** Dùng khi trọng tâm là engineering của hệ thống ML, batch/online inference hoặc production integration.

**Ranh giới và handoff:** Không tự phê duyệt model quality/fairness; nhận validated model từ DS và handoff deployment/monitoring cho MLOps.

**Quy mô:** 20 tasks — Plan / Design 4; Build / Deliver 10; Test / Assure 3; Operate / Improve 3.

**Domain references tải khi cần:** `adapter-databricks.md`, `adapter-kafka-flink.md`, `adapter-mlflow-kubeflow.md`, `adapter-spark.md`, `external-tool-access.md`, `learning-memory-interoperability.md`, `model-selection.md`, `response-compression.md`, `solution-option-framing.md`, `workflow-runtime-and-evidence-os.md`.

**Templates/assets có thể tái sử dụng:** `atomic-task-output.yaml`, `design-option-set.yaml`.

**Scripts:** `check_training_serving_skew.py`.

#### Plan / Design (4 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`mle-define-inference-contract`](skills/machine-learning-engineering/references/tasks/mle-define-inference-contract.md) | định nghĩa request/response, validation, version và error behavior | inference contract | `design-specification` | `R1-reviewed` / `standard-path` |
| [`mle-document-model-service`](skills/machine-learning-engineering/references/tasks/mle-document-model-service.md) | viết contract, limits, SLO, runbook và owner | service documentation | `advisory-analysis` | `R0-light` / `fast-path` |
| [`mle-write-model-integration-tests`](skills/machine-learning-engineering/references/tasks/mle-write-model-integration-tests.md) | test feature/model/service/downstream compatibility | integration tests | `design-specification` | `R1-reviewed` / `standard-path` |
| [`mle-write-model-unit-tests`](skills/machine-learning-engineering/references/tasks/mle-write-model-unit-tests.md) | test preprocessing, features, prediction và edge cases | unit test suite | `design-specification` | `R1-reviewed` / `standard-path` |

#### Build / Deliver (10 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`mle-build-batch-inference`](skills/machine-learning-engineering/references/tasks/mle-build-batch-inference.md) | triển khai scalable scheduled scoring và result delivery | batch inference job | `build-change` | `R2-standard` / `standard-path` |
| [`mle-build-canary-release`](skills/machine-learning-engineering/references/tasks/mle-build-canary-release.md) | route small traffic và define abort thresholds | canary rollout | `production-release` | `R3-controlled` / `controlled-path` |
| [`mle-build-feature-pipeline`](skills/machine-learning-engineering/references/tasks/mle-build-feature-pipeline.md) | tạo online/offline consistent feature computation | feature pipeline | `build-change` | `R2-standard` / `standard-path` |
| [`mle-build-online-inference-service`](skills/machine-learning-engineering/references/tasks/mle-build-online-inference-service.md) | triển khai API/service có latency, scaling và health checks | serving service | `build-change` | `R2-standard` / `standard-path` |
| [`mle-build-shadow-deployment`](skills/machine-learning-engineering/references/tasks/mle-build-shadow-deployment.md) | chạy model mới không ảnh hưởng decision | shadow comparison | `production-release` | `R3-controlled` / `controlled-path` |
| [`mle-build-training-pipeline`](skills/machine-learning-engineering/references/tasks/mle-build-training-pipeline.md) | tự động hóa extract, train, evaluate và package | training pipeline | `build-change` | `R2-standard` / `standard-path` |
| [`mle-compress-model`](skills/machine-learning-engineering/references/tasks/mle-compress-model.md) | quantize/prune/distill và đo quality trade-off | optimized model artifact | `advisory-analysis` | `R0-light` / `fast-path` |
| [`mle-implement-model-fallback`](skills/machine-learning-engineering/references/tasks/mle-implement-model-fallback.md) | tạo timeout, default, previous-model và degraded mode | resilience behavior | `build-change` | `R2-standard` / `standard-path` |
| [`mle-package-model-artifact`](skills/machine-learning-engineering/references/tasks/mle-package-model-artifact.md) | đóng gói model, dependencies, signature và metadata | deployable artifact | `build-change` | `R2-standard` / `standard-path` |
| [`mle-productionize-model-code`](skills/machine-learning-engineering/references/tasks/mle-productionize-model-code.md) | refactor notebook thành package/module deterministic | production codebase | `advisory-analysis` | `R0-light` / `fast-path` |

#### Test / Assure (3 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`mle-review-ml-engineering-change`](skills/machine-learning-engineering/references/tasks/mle-review-ml-engineering-change.md) | review correctness, performance, security và operability | review findings | `advisory-analysis` | `R0-light` / `fast-path` |
| [`mle-validate-model-compatibility`](skills/machine-learning-engineering/references/tasks/mle-validate-model-compatibility.md) | kiểm tra schema, runtime, feature và consumer compatibility | compatibility report | `advisory-analysis` | `R0-light` / `fast-path` |
| [`mle-validate-training-serving-skew`](skills/machine-learning-engineering/references/tasks/mle-validate-training-serving-skew.md) | so sánh feature logic và distributions | skew report | `build-change` | `R2-standard` / `standard-path` |

#### Operate / Improve (3 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`mle-optimize-inference-performance`](skills/machine-learning-engineering/references/tasks/mle-optimize-inference-performance.md) | tune batching, serialization, runtime và hardware | latency/cost benchmark | `build-change` | `R2-standard` / `standard-path` |
| [`mle-rollback-model-release`](skills/machine-learning-engineering/references/tasks/mle-rollback-model-release.md) | revert artifact/config/traffic và verify | restored stable version | `production-release` | `R3-controlled` / `controlled-path` |
| [`mle-troubleshoot-inference-error`](skills/machine-learning-engineering/references/tasks/mle-troubleshoot-inference-error.md) | isolate input, feature, artifact, runtime hoặc dependency cause | restored inference | `incident-recovery` | `R3-controlled` / `controlled-path` |

<a id="skill-mlops"></a>

### 18. `mlops` — MLOps

**Claude trigger description:** Operate the ML lifecycle through experiment tracking, registry, CI/CD, deployment, monitoring, drift, retraining, rollback, lineage and governance. Use for MLOps, model release or ML platform operations. The underlying platform belongs to data-platform-and-dataops.

**Ownership:** Quản lý ML lifecycle trong production: registry, reproducibility, CI/CD/CT, promotion, deployment, monitoring, drift, incidents và rollback.

**Khi nên dùng:** Dùng khi model/version/environment cần được vận hành có kiểm soát và quan sát sau release.

**Ranh giới và handoff:** Không promote chỉ vì pipeline chạy thành công; cần validation, approval, canary/smoke, rollback và post-release monitoring.

**Quy mô:** 23 tasks — Plan / Design 1; Build / Deliver 12; Test / Assure 2; Operate / Improve 8.

**Domain references tải khi cần:** `adapter-databricks.md`, `adapter-mlflow-kubeflow.md`, `adapter-spark.md`, `external-tool-access.md`, `learning-memory-interoperability.md`, `model-selection.md`, `response-compression.md`, `solution-option-framing.md`, `workflow-runtime-and-evidence-os.md`.

**Templates/assets có thể tái sử dụng:** `atomic-task-output.yaml`, `design-option-set.yaml`.

**Scripts:** `check_model_promotion_readiness.py`.

#### Plan / Design (1 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`mlops-create-ml-runbook`](skills/mlops/references/tasks/mlops-create-ml-runbook.md) | ghi alerts, diagnosis, rollback và contacts | runbook | `design-specification` | `R1-reviewed` / `standard-path` |

#### Build / Deliver (12 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`mlops-build-ml-cd-pipeline`](skills/mlops/references/tasks/mlops-build-ml-cd-pipeline.md) | approval, deploy, smoke test và rollback | ML CD workflow | `build-change` | `R2-standard` / `standard-path` |
| [`mlops-build-ml-ci-pipeline`](skills/mlops/references/tasks/mlops-build-ml-ci-pipeline.md) | lint, tests, data checks, security scan và package | ML CI workflow | `build-change` | `R2-standard` / `standard-path` |
| [`mlops-build-model-lineage`](skills/mlops/references/tasks/mlops-build-model-lineage.md) | nối data, code, features, run, artifact và deployment | lineage graph | `build-change` | `R2-standard` / `standard-path` |
| [`mlops-configure-experiment-tracking`](skills/mlops/references/tasks/mlops-configure-experiment-tracking.md) | chuẩn hóa runs, params, metrics và artifacts | tracking workspace | `build-change` | `R2-standard` / `standard-path` |
| [`mlops-enforce-model-approval-gate`](skills/mlops/references/tasks/mlops-enforce-model-approval-gate.md) | yêu cầu evidence và approvers theo risk tier | auditable gate | `governance-assurance` | `R1-reviewed` / `standard-path` |
| [`mlops-handle-ml-incident`](skills/mlops/references/tasks/mlops-handle-ml-incident.md) | triage data/model/service issue và coordinate response | resolved incident | `incident-recovery` | `R3-controlled` / `controlled-path` |
| [`mlops-manage-feature-store`](skills/mlops/references/tasks/mlops-manage-feature-store.md) | đăng ký, materialize, monitor và deprecate features | governed feature lifecycle | `advisory-analysis` | `R0-light` / `fast-path` |
| [`mlops-promote-model-stage`](skills/mlops/references/tasks/mlops-promote-model-stage.md) | kiểm tra gates từ candidate tới staging/production | promotion decision | `production-release` | `R3-controlled` / `controlled-path` |
| [`mlops-provision-ml-environment`](skills/mlops/references/tasks/mlops-provision-ml-environment.md) | tạo reproducible compute, runtime và access | ML environment | `build-change` | `R2-standard` / `standard-path` |
| [`mlops-register-model-version`](skills/mlops/references/tasks/mlops-register-model-version.md) | lưu artifact, signature, lineage và stage | registry version | `advisory-analysis` | `R0-light` / `fast-path` |
| [`mlops-trigger-model-retraining`](skills/mlops/references/tasks/mlops-trigger-model-retraining.md) | đánh giá schedule/drift/performance trigger và launch controlled run | retraining run | `build-change` | `R2-standard` / `standard-path` |
| [`mlops-upgrade-ml-runtime`](skills/mlops/references/tasks/mlops-upgrade-ml-runtime.md) | compatibility test, staged migration và rollback | upgraded runtime | `build-change` | `R2-standard` / `standard-path` |

#### Test / Assure (2 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`mlops-audit-model-controls`](skills/mlops/references/tasks/mlops-audit-model-controls.md) | thu lineage, approvals, monitoring và incident evidence | control audit | `governance-assurance` | `R1-reviewed` / `standard-path` |
| [`mlops-validate-retrained-model`](skills/mlops/references/tasks/mlops-validate-retrained-model.md) | so sánh challenger/champion và policy gates | validation decision | `build-change` | `R2-standard` / `standard-path` |

#### Operate / Improve (8 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`mlops-deploy-model-version`](skills/mlops/references/tasks/mlops-deploy-model-version.md) | triển khai artifact/config và verify endpoints | deployed version | `production-release` | `R3-controlled` / `controlled-path` |
| [`mlops-monitor-data-drift`](skills/mlops/references/tasks/mlops-monitor-data-drift.md) | đo input distribution shift với baseline | drift alert/report | `advisory-analysis` | `R0-light` / `fast-path` |
| [`mlops-monitor-model-performance`](skills/mlops/references/tasks/mlops-monitor-model-performance.md) | theo dõi delayed labels và model metrics | performance report | `advisory-analysis` | `R0-light` / `fast-path` |
| [`mlops-monitor-model-service`](skills/mlops/references/tasks/mlops-monitor-model-service.md) | theo dõi availability, latency, errors và saturation | service monitoring | `advisory-analysis` | `R0-light` / `fast-path` |
| [`mlops-monitor-prediction-quality`](skills/mlops/references/tasks/mlops-monitor-prediction-quality.md) | theo dõi confidence, missing features và output anomalies | prediction-quality report | `advisory-analysis` | `R0-light` / `fast-path` |
| [`mlops-optimize-ml-infrastructure-cost`](skills/mlops/references/tasks/mlops-optimize-ml-infrastructure-cost.md) | phân tích training/serving utilization và rightsizing | cost plan | `build-change` | `R2-standard` / `standard-path` |
| [`mlops-retire-model-version`](skills/mlops/references/tasks/mlops-retire-model-version.md) | confirm no consumers, archive evidence và delete safely | retired version | `production-release` | `R4-critical` / `controlled-path` |
| [`mlops-rollback-production-model`](skills/mlops/references/tasks/mlops-rollback-production-model.md) | chuyển traffic/version và verify recovery | rollback record | `production-release` | `R4-critical` / `controlled-path` |

<a id="skill-data-quality-and-reliability"></a>

### 19. `data-quality-and-reliability` — Data Quality and Reliability

**Claude trigger description:** Define data quality rules and SLOs, implement observability, reconcile data, triage incidents, run game days and prevent recurrence. Use for Data Quality, Data Reliability or data incident work.

**Ownership:** Thiết kế rules, expectations, SLIs/SLOs, monitoring, anomaly detection, incident response, RCA, reconciliation và reliability improvement.

**Khi nên dùng:** Dùng cho assurance độc lập hoặc khi chất lượng/freshness/completeness gây ảnh hưởng downstream.

**Ranh giới và handoff:** Không che failed checks hoặc tự hạ threshold để pass; exceptions cần owner, expiry và residual-risk record.

**Quy mô:** 21 tasks — Plan / Design 3; Build / Deliver 5; Test / Assure 8; Operate / Improve 5.

**Domain references tải khi cần:** `adapter-airflow.md`, `adapter-bigquery.md`, `adapter-databricks.md`, `adapter-dbt.md`, `adapter-microsoft-fabric.md`, `adapter-snowflake.md`, `adapter-spark.md`, `external-tool-access.md`, `learning-memory-interoperability.md`, `model-selection.md`, `response-compression.md`, `solution-option-framing.md`, `stage-gated-data-validation.md`, `workflow-runtime-and-evidence-os.md`.

**Templates/assets có thể tái sử dụng:** `atomic-task-output.yaml`, `design-option-set.yaml`, `pipeline-validation-plan.yaml`.

**Scripts:** `validate_tabular_data.py`.

#### Plan / Design (3 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`dq-define-data-quality-rule`](skills/data-quality-and-reliability/references/tasks/dq-define-data-quality-rule.md) | chuyển expectation thành executable rule, threshold và owner | DQ rule spec | `design-specification` | `R1-reviewed` / `standard-path` |
| [`dre-define-data-slo`](skills/data-quality-and-reliability/references/tasks/dre-define-data-slo.md) | xác định freshness, availability, completeness và error budget | data SLO | `design-specification` | `R1-reviewed` / `standard-path` |
| [`dre-write-data-postmortem`](skills/data-quality-and-reliability/references/tasks/dre-write-data-postmortem.md) | ghi impact, timeline, root cause, lessons và actions | postmortem | `design-specification` | `R1-reviewed` / `standard-path` |

#### Build / Deliver (5 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`dq-build-data-quality-scorecard`](skills/data-quality-and-reliability/references/tasks/dq-build-data-quality-scorecard.md) | tổng hợp dimensions, criticality và issue status | DQ scorecard | `build-change` | `R2-standard` / `standard-path` |
| [`dq-implement-data-quality-test`](skills/data-quality-and-reliability/references/tasks/dq-implement-data-quality-test.md) | mã hóa và tích hợp rule vào pipeline/model | automated test | `build-change` | `R2-standard` / `standard-path` |
| [`dre-coordinate-data-incident`](skills/data-quality-and-reliability/references/tasks/dre-coordinate-data-incident.md) | quản lý roles, communication, timeline và mitigation | incident log | `incident-recovery` | `R3-controlled` / `controlled-path` |
| [`dre-run-data-game-day`](skills/data-quality-and-reliability/references/tasks/dre-run-data-game-day.md) | mô phỏng failure và đánh giá detection/recovery | resilience test report | `advisory-analysis` | `R0-light` / `fast-path` |
| [`dre-track-reliability-actions`](skills/data-quality-and-reliability/references/tasks/dre-track-reliability-actions.md) | theo dõi corrective/preventive actions đến closure | action register | `advisory-analysis` | `R0-light` / `fast-path` |

#### Test / Assure (8 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`dq-certify-quality-readiness`](skills/data-quality-and-reliability/references/tasks/dq-certify-quality-readiness.md) | kiểm tra coverage, thresholds và open issues | quality gate decision | `governance-assurance` | `R1-reviewed` / `standard-path` |
| [`dq-detect-data-quality-anomaly`](skills/data-quality-and-reliability/references/tasks/dq-detect-data-quality-anomaly.md) | xây baseline và calibrated anomaly logic | anomaly detector | `advisory-analysis` | `R0-light` / `fast-path` |
| [`dq-profile-critical-dataset`](skills/data-quality-and-reliability/references/tasks/dq-profile-critical-dataset.md) | lập baseline completeness, validity, uniqueness và distribution | DQ profile | `advisory-analysis` | `R0-light` / `fast-path` |
| [`dq-reconcile-data-systems`](skills/data-quality-and-reliability/references/tasks/dq-reconcile-data-systems.md) | so sánh source/target theo control totals và samples | reconciliation evidence | `advisory-analysis` | `R0-light` / `fast-path` |
| [`dq-test-data-contract`](skills/data-quality-and-reliability/references/tasks/dq-test-data-contract.md) | kiểm tra schema, semantics, freshness và compatibility | contract test report | `advisory-analysis` | `R0-light` / `fast-path` |
| [`dre-assess-data-product-reliability`](skills/data-quality-and-reliability/references/tasks/dre-assess-data-product-reliability.md) | review SLO, incidents, tests và dependencies | reliability assessment | `advisory-analysis` | `R0-light` / `fast-path` |
| [`dre-diagnose-data-incident`](skills/data-quality-and-reliability/references/tasks/dre-diagnose-data-incident.md) | trace lineage và evidence để tìm failure point | root-cause diagnosis | `incident-recovery` | `R3-controlled` / `controlled-path` |
| [`dre-triage-data-alert`](skills/data-quality-and-reliability/references/tasks/dre-triage-data-alert.md) | xác định severity, blast radius, owner và immediate action | triage decision | `advisory-analysis` | `R0-light` / `fast-path` |

#### Operate / Improve (5 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`dre-monitor-data-distribution`](skills/data-quality-and-reliability/references/tasks/dre-monitor-data-distribution.md) | phát hiện anomaly trên critical columns | distribution alert | `advisory-analysis` | `R0-light` / `fast-path` |
| [`dre-monitor-data-freshness`](skills/data-quality-and-reliability/references/tasks/dre-monitor-data-freshness.md) | phát hiện late/missing updates theo schedule | freshness alerts | `advisory-analysis` | `R0-light` / `fast-path` |
| [`dre-monitor-data-volume`](skills/data-quality-and-reliability/references/tasks/dre-monitor-data-volume.md) | phát hiện spike/drop theo baseline và seasonality | volume alerts | `advisory-analysis` | `R0-light` / `fast-path` |
| [`dre-monitor-schema-change`](skills/data-quality-and-reliability/references/tasks/dre-monitor-schema-change.md) | phát hiện breaking drift và affected consumers | schema alert | `advisory-analysis` | `R0-light` / `fast-path` |
| [`dre-restore-corrupted-data`](skills/data-quality-and-reliability/references/tasks/dre-restore-corrupted-data.md) | quarantine, restore/reprocess và reconcile | recovered dataset | `incident-recovery` | `R3-controlled` / `controlled-path` |

<a id="skill-data-security-and-privacy"></a>

### 20. `data-security-and-privacy` — Data Security and Privacy

**Claude trigger description:** Protect data through classification, threat modeling, least privilege, encryption, masking, audit, privacy workflows and incident response. Use for Data Security, Privacy, DSR or sensitive-data risk work.

**Ownership:** Thực hiện classification, threat/risk assessment, least privilege, encryption, privacy controls, audits, incidents và data-subject workflows.

**Khi nên dùng:** Dùng khi scope liên quan PII/confidential data, access, sharing, retention, deletion hoặc security posture.

**Ranh giới và handoff:** Không tự cấp quyền, xóa dữ liệu hay tuyên bố pháp lý; R3/R4 cần authority, segregation, evidence và recoverability thích hợp.

**Quy mô:** 16 tasks — Plan / Design 3; Build / Deliver 9; Test / Assure 4; Operate / Improve 0.

**Domain references tải khi cần:** `adapter-bigquery.md`, `adapter-databricks.md`, `adapter-metadata-catalog.md`, `adapter-microsoft-fabric.md`, `adapter-power-bi.md`, `adapter-snowflake.md`, `external-tool-access.md`, `learning-memory-interoperability.md`, `model-selection.md`, `response-compression.md`, `solution-option-framing.md`, `workflow-runtime-and-evidence-os.md`.

**Templates/assets có thể tái sử dụng:** `atomic-task-output.yaml`, `design-option-set.yaml`.

#### Plan / Design (3 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`privacy-prepare-data-breach-assessment`](skills/data-security-and-privacy/references/tasks/privacy-prepare-data-breach-assessment.md) | xác định affected data, subjects, scope và notifications | breach assessment | `incident-recovery` | `R4-critical` / `controlled-path` |
| [`sec-collect-control-evidence`](skills/data-security-and-privacy/references/tasks/sec-collect-control-evidence.md) | gom configurations, logs, tests và approvals | audit evidence | `governance-assurance` | `R1-reviewed` / `standard-path` |
| [`sec-design-data-access-control`](skills/data-security-and-privacy/references/tasks/sec-design-data-access-control.md) | định nghĩa RBAC/ABAC, segregation và break-glass | access-control design | `governance-assurance` | `R3-controlled` / `controlled-path` |

#### Build / Deliver (9 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`privacy-enforce-retention-deletion`](skills/data-security-and-privacy/references/tasks/privacy-enforce-retention-deletion.md) | map assets, execute approved deletion và verify | deletion evidence | `production-release` | `R4-critical` / `controlled-path` |
| [`privacy-handle-data-subject-request`](skills/data-security-and-privacy/references/tasks/privacy-handle-data-subject-request.md) | discover, verify, export/delete và record evidence | completed DSR package | `governance-assurance` | `R4-critical` / `controlled-path` |
| [`sec-classify-sensitive-data`](skills/data-security-and-privacy/references/tasks/sec-classify-sensitive-data.md) | gắn class theo policy và regulation | security classification | `governance-assurance` | `R1-reviewed` / `standard-path` |
| [`sec-discover-sensitive-data`](skills/data-security-and-privacy/references/tasks/sec-discover-sensitive-data.md) | scan và xác minh PII/secrets/confidential fields | sensitive-data inventory | `governance-assurance` | `R1-reviewed` / `standard-path` |
| [`sec-implement-data-masking`](skills/data-security-and-privacy/references/tasks/sec-implement-data-masking.md) | chọn static/dynamic/tokenization theo use case | masked data flow | `governance-assurance` | `R2-standard` / `standard-path` |
| [`sec-implement-row-column-security`](skills/data-security-and-privacy/references/tasks/sec-implement-row-column-security.md) | triển khai filters/masking và test bypass | enforced policies | `governance-assurance` | `R3-controlled` / `controlled-path` |
| [`sec-investigate-data-access-anomaly`](skills/data-security-and-privacy/references/tasks/sec-investigate-data-access-anomaly.md) | correlate identity, query, asset và context | investigation report | `governance-assurance` | `R3-controlled` / `controlled-path` |
| [`sec-rotate-compromised-credential`](skills/data-security-and-privacy/references/tasks/sec-rotate-compromised-credential.md) | revoke, rotate, update consumers và audit | restored credentials | `incident-recovery` | `R4-critical` / `controlled-path` |
| [`sec-threat-model-data-flow`](skills/data-security-and-privacy/references/tasks/sec-threat-model-data-flow.md) | xác định assets, trust boundaries, threats và mitigations | threat model | `governance-assurance` | `R1-reviewed` / `standard-path` |

#### Test / Assure (4 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`privacy-assess-data-use-case`](skills/data-security-and-privacy/references/tasks/privacy-assess-data-use-case.md) | đánh giá purpose, minimization, legal basis và risk | privacy assessment | `governance-assurance` | `R3-controlled` / `controlled-path` |
| [`sec-audit-data-access`](skills/data-security-and-privacy/references/tasks/sec-audit-data-access.md) | phân tích grants, usage, dormant access và anomalies | access audit | `governance-assurance` | `R3-controlled` / `controlled-path` |
| [`sec-review-data-sharing-security`](skills/data-security-and-privacy/references/tasks/sec-review-data-sharing-security.md) | đánh giá recipient, transport, controls và expiry | security recommendation | `governance-assurance` | `R3-controlled` / `controlled-path` |
| [`sec-verify-data-encryption`](skills/data-security-and-privacy/references/tasks/sec-verify-data-encryption.md) | kiểm tra at-rest/in-transit/key management | encryption evidence | `governance-assurance` | `R1-reviewed` / `standard-path` |

<a id="skill-technical-translation"></a>

### 21. `technical-translation` — Technical Translation

**Claude trigger description:** Translate foreign-language books, documentation, web content and technical material into Vietnamese that reads as a domain expert wrote it, with a fixed glossary, style guide, fidelity review and translation memory. Use for translation or localisation into Vietnamese; route the authoring of new Vietnamese technical content to data-technical-content-and-social.

**Ownership:** Dịch sách, tài liệu kỹ thuật, nội dung web và tài liệu mã nguồn nước ngoài sang tiếng Việt đúng ngữ cảnh chuyên ngành.

**Khi nên dùng:** Dùng khi cần chuyển ngữ, chốt glossary và style guide trước, rồi kiểm trung thành theo từng khẳng định.

**Ranh giới và handoff:** Đơn vị trung thành là khẳng định chứ không phải câu; không dịch định danh mã, tên API và tên sản phẩm; không sửa bản gốc trong lúc dịch.

**Quy mô:** 17 tasks — Plan / Design 4; Build / Deliver 7; Test / Assure 5; Operate / Improve 1.

**Domain references tải khi cần:** `learning-memory-interoperability.md`, `model-selection.md`, `response-compression.md`, `solution-option-framing.md`, `vietnamese-technical-translation.md`, `workflow-runtime-and-evidence-os.md`.

**Templates/assets có thể tái sử dụng:** `atomic-task-output.yaml`, `design-option-set.yaml`, `fidelity-review.yaml`, `terminology-glossary.yaml`, `translation-brief.yaml`, `translation-memory.yaml`, `translationese-report.yaml`, `vietnamese-style-guide.yaml`.

#### Plan / Design (4 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`trans-build-terminology-glossary`](skills/technical-translation/references/tasks/trans-build-terminology-glossary.md) | chốt thuật ngữ chuyên ngành và thuật ngữ nào giữ nguyên tiếng Anh | bilingual terminology glossary | `build-change` | `R2-standard` / `standard-path` |
| [`trans-clarify-translation-brief`](skills/technical-translation/references/tasks/trans-clarify-translation-brief.md) | chốt người đọc, mục đích, mức trang trọng và "trung thành" ở đây nghĩa là gì | translation brief | `advisory-analysis` | `R0-light` / `fast-path` |
| [`trans-define-vietnamese-style-guide`](skills/technical-translation/references/tasks/trans-define-vietnamese-style-guide.md) | xưng hô, mức trang trọng, quy ước số, đơn vị, ngày tháng và tên riêng | Vietnamese style guide | `design-specification` | `R1-reviewed` / `standard-path` |
| [`trans-plan-long-form-translation`](skills/technical-translation/references/tasks/trans-plan-long-form-translation.md) | chia tập, thứ tự, điểm kiểm nhất quán cho sách hoặc tài liệu dài | long-form translation plan | `design-specification` | `R1-reviewed` / `standard-path` |

#### Build / Deliver (7 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`trans-localize-culture-bound-content`](skills/technical-translation/references/tasks/trans-localize-culture-bound-content.md) | xử lý ví dụ, ẩn dụ, đơn vị và tham chiếu văn hoá không chuyển thẳng được | localised content | `advisory-analysis` | `R1-reviewed` / `standard-path` |
| [`trans-maintain-translation-memory`](skills/technical-translation/references/tasks/trans-maintain-translation-memory.md) | giữ cặp câu đã duyệt để tái dùng và giữ nhất quán giữa các tài liệu | translation memory | `advisory-analysis` | `R0-light` / `fast-path` |
| [`trans-transcreate-persuasive-copy`](skills/technical-translation/references/tasks/trans-transcreate-persuasive-copy.md) | viết lại nội dung thuyết phục khi dịch sát nghĩa làm hỏng mục đích | transcreated copy | `advisory-analysis` | `R1-reviewed` / `standard-path` |
| [`trans-translate-code-documentation`](skills/technical-translation/references/tasks/trans-translate-code-documentation.md) | dịch tài liệu kỹ thuật giữ nguyên định danh mã, API và output mẫu | translated code documentation | `advisory-analysis` | `R1-reviewed` / `standard-path` |
| [`trans-translate-document`](skills/technical-translation/references/tasks/trans-translate-document.md) | dịch một tài liệu theo brief, glossary và style guide | translated document | `advisory-analysis` | `R1-reviewed` / `standard-path` |
| [`trans-translate-technical-book`](skills/technical-translation/references/tasks/trans-translate-technical-book.md) | dịch sách kỹ thuật giữ nhất quán thuật ngữ và giọng xuyên chương | translated book manuscript | `advisory-analysis` | `R1-reviewed` / `standard-path` |
| [`trans-translate-web-content`](skills/technical-translation/references/tasks/trans-translate-web-content.md) | dịch trang web giữ nguyên markup, link, alt text và cấu trúc | translated web content | `advisory-analysis` | `R1-reviewed` / `standard-path` |

#### Test / Assure (5 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`trans-analyze-source-document`](skills/technical-translation/references/tasks/trans-analyze-source-document.md) | đọc thể loại, cấu trúc, giọng, và các bẫy dịch trước khi dịch câu nào | source analysis | `advisory-analysis` | `R0-light` / `fast-path` |
| [`trans-audit-terminology-consistency`](skills/technical-translation/references/tasks/trans-audit-terminology-consistency.md) | soát một thuật ngữ có bị dịch nhiều kiểu trong cùng tài liệu không | terminology consistency audit | `governance-assurance` | `R1-reviewed` / `standard-path` |
| [`trans-detect-translationese`](skills/technical-translation/references/tasks/trans-detect-translationese.md) | tìm cú pháp dịch máy, sai mức trang trọng và thành ngữ dịch sát chữ | translationese report | `advisory-analysis` | `R0-light` / `fast-path` |
| [`trans-review-translation-fidelity`](skills/technical-translation/references/tasks/trans-review-translation-fidelity.md) | đối chiếu ngược từng khẳng định với bản gốc, không đối chiếu từng câu | fidelity review | `advisory-analysis` | `R0-light` / `fast-path` |
| [`trans-test-reader-comprehension`](skills/technical-translation/references/tasks/trans-test-reader-comprehension.md) | kiểm người đọc đích hiểu đúng, không chỉ đọc trôi | comprehension test result | `advisory-analysis` | `R0-light` / `fast-path` |

#### Operate / Improve (1 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`trans-refresh-translation-on-source-change`](skills/technical-translation/references/tasks/trans-refresh-translation-on-source-change.md) | cập nhật bản dịch khi bản gốc đổi, chỉ dịch lại phần đã đổi | refreshed translation | `advisory-analysis` | `R1-reviewed` / `standard-path` |

<a id="skill-master-data-management"></a>

### 22. `master-data-management` — Master Data Management

**Claude trigger description:** Design and operate master entities, identity matching, survivorship, golden records, reference data, hierarchies, stewardship and synchronization. Use for MDM, entity resolution or reference-data work.

**Ownership:** Thiết kế và vận hành master/reference data, match-merge, survivorship, golden records, hierarchies, stewardship và distribution.

**Khi nên dùng:** Dùng khi nhiều source mô tả cùng entity và tổ chức cần bản ghi chuẩn có lineage và governance.

**Ranh giới và handoff:** Merge/survivorship phải giải thích được, reversible khi cần và không phá vỡ source-of-record authority.

**Quy mô:** 13 tasks — Plan / Design 3; Build / Deliver 6; Test / Assure 2; Operate / Improve 2.

**Domain references tải khi cần:** `external-tool-access.md`, `learning-memory-interoperability.md`, `model-selection.md`, `response-compression.md`, `solution-option-framing.md`, `workflow-runtime-and-evidence-os.md`.

**Templates/assets có thể tái sử dụng:** `atomic-task-output.yaml`, `design-option-set.yaml`.

#### Plan / Design (3 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`mdm-define-match-rules`](skills/master-data-management/references/tasks/mdm-define-match-rules.md) | thiết kế deterministic/probabilistic matching và thresholds | match rule set | `design-specification` | `R1-reviewed` / `standard-path` |
| [`mdm-define-merge-survivorship`](skills/master-data-management/references/tasks/mdm-define-merge-survivorship.md) | xác định source priority, recency và field-level rules | survivorship policy | `design-specification` | `R1-reviewed` / `standard-path` |
| [`mdm-design-master-entity`](skills/master-data-management/references/tasks/mdm-design-master-entity.md) | xác định attributes, identifiers, relationships và owners | master model | `design-specification` | `R1-reviewed` / `standard-path` |

#### Build / Deliver (6 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`mdm-build-golden-record`](skills/master-data-management/references/tasks/mdm-build-golden-record.md) | match, merge, preserve lineage và publish identity | golden dataset | `build-change` | `R2-standard` / `standard-path` |
| [`mdm-handle-master-data-change`](skills/master-data-management/references/tasks/mdm-handle-master-data-change.md) | validate request, approval, effective date và audit | approved master change | `advisory-analysis` | `R0-light` / `fast-path` |
| [`mdm-manage-master-hierarchy`](skills/master-data-management/references/tasks/mdm-manage-master-hierarchy.md) | duy trì parent-child, validity và cycle checks | valid hierarchy | `advisory-analysis` | `R0-light` / `fast-path` |
| [`mdm-manage-reference-data`](skills/master-data-management/references/tasks/mdm-manage-reference-data.md) | version codes, descriptions, mappings và effective dates | governed reference set | `advisory-analysis` | `R0-light` / `fast-path` |
| [`mdm-manage-stewardship-queue`](skills/master-data-management/references/tasks/mdm-manage-stewardship-queue.md) | route ambiguous matches và corrections | resolved stewardship cases | `advisory-analysis` | `R0-light` / `fast-path` |
| [`mdm-synchronize-master-data`](skills/master-data-management/references/tasks/mdm-synchronize-master-data.md) | publish changes, acknowledgements và reconciliation | synchronized consumers | `build-change` | `R2-standard` / `standard-path` |

#### Test / Assure (2 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`mdm-audit-master-data-lineage`](skills/master-data-management/references/tasks/mdm-audit-master-data-lineage.md) | trace attribute về source, rule và steward action | lineage evidence | `governance-assurance` | `R1-reviewed` / `standard-path` |
| [`mdm-profile-entity-duplicates`](skills/master-data-management/references/tasks/mdm-profile-entity-duplicates.md) | đo duplicate patterns và root causes | duplicate assessment | `advisory-analysis` | `R0-light` / `fast-path` |

#### Operate / Improve (2 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`mdm-monitor-master-data-quality`](skills/master-data-management/references/tasks/mdm-monitor-master-data-quality.md) | đo completeness, uniqueness và consistency | MDM scorecard | `advisory-analysis` | `R0-light` / `fast-path` |
| [`mdm-resolve-identity-conflict`](skills/master-data-management/references/tasks/mdm-resolve-identity-conflict.md) | điều tra evidence và quyết định split/merge/link | identity resolution | `advisory-analysis` | `R0-light` / `fast-path` |

<a id="skill-generative-ai-engineering"></a>

### 23. `generative-ai-engineering` — Generative AI Engineering

**Claude trigger description:** Build and evaluate governed RAG, retrieval, prompt, tool-using agent and GenAI systems with guardrails, injection testing, monitoring and system cards. Use for production GenAI data products or agents.

**Ownership:** Thiết kế và xây RAG/LLM applications, prompts, retrieval, evaluations, guardrails, observability, cost và release controls.

**Khi nên dùng:** Dùng khi deliverable là hệ thống GenAI hoặc quy trình đánh giá chất lượng, safety và groundedness.

**Ranh giới và handoff:** Không đánh giá bằng demo đẹp hoặc một vài câu hỏi; cần eval set, failure taxonomy, red-team và production monitoring phù hợp.

**Quy mô:** 24 tasks — Plan / Design 8; Build / Deliver 8; Test / Assure 5; Operate / Improve 3.

**Domain references tải khi cần:** `adapter-databricks.md`, `adapter-mlflow-kubeflow.md`, `adapter-spark.md`, `external-tool-access.md`, `grounded-generation-and-agent-economics.md`, `learning-memory-interoperability.md`, `model-selection.md`, `response-compression.md`, `solution-option-framing.md`, `workflow-runtime-and-evidence-os.md`.

**Templates/assets có thể tái sử dụng:** `atomic-task-output.yaml`, `design-option-set.yaml`, `schema-retrieval-index.yaml`, `semantic-cache.yaml`, `tool-surface-audit.yaml`, `tool-surface.yaml`.

**Scripts:** `summarize_eval_run.py`.

#### Plan / Design (8 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`ai-create-embeddings-index`](skills/generative-ai-engineering/references/tasks/ai-create-embeddings-index.md) | embed, store, version và validate coverage | searchable index | `design-specification` | `R1-reviewed` / `standard-path` |
| [`ai-create-human-review-workflow`](skills/generative-ai-engineering/references/tasks/ai-create-human-review-workflow.md) | route low-confidence/high-risk cases | review queue and policy | `design-specification` | `R1-reviewed` / `standard-path` |
| [`ai-declare-tool-surface`](skills/generative-ai-engineering/references/tasks/ai-declare-tool-surface.md) | khai báo một bề mặt tool liệt kê được cho dịch vụ ngoài, tách quyền đọc và ghi | declared tool surface | `advisory-analysis` | `R2-standard` / `standard-path` |
| [`ai-design-document-chunking`](skills/generative-ai-engineering/references/tasks/ai-design-document-chunking.md) | chọn boundaries, overlap và metadata theo retrieval need | chunking strategy | `design-specification` | `R1-reviewed` / `standard-path` |
| [`ai-design-evaluation-dataset`](skills/generative-ai-engineering/references/tasks/ai-design-evaluation-dataset.md) | tạo representative, adversarial và edge-case examples | versioned eval set | `design-specification` | `R1-reviewed` / `standard-path` |
| [`ai-design-system-prompt`](skills/generative-ai-engineering/references/tasks/ai-design-system-prompt.md) | định nghĩa role, constraints, evidence và refusal behavior | versioned prompt | `design-specification` | `R1-reviewed` / `standard-path` |
| [`ai-document-ai-system`](skills/generative-ai-engineering/references/tasks/ai-document-ai-system.md) | ghi data, prompts, models, tools, risks và limitations | AI system card | `advisory-analysis` | `R0-light` / `fast-path` |
| [`ai-frame-generative-ai-use-case`](skills/generative-ai-engineering/references/tasks/ai-frame-generative-ai-use-case.md) | xác định user task, value, risk và non-AI baseline | AI use-case brief | `design-specification` | `R1-reviewed` / `standard-path` |

#### Build / Deliver (8 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`ai-build-rag-answering-flow`](skills/generative-ai-engineering/references/tasks/ai-build-rag-answering-flow.md) | nối retrieval, prompt, citations và fallback | RAG workflow | `build-change` | `R2-standard` / `standard-path` |
| [`ai-build-reranking-pipeline`](skills/generative-ai-engineering/references/tasks/ai-build-reranking-pipeline.md) | rerank candidates và tune latency/quality | reranker | `build-change` | `R2-standard` / `standard-path` |
| [`ai-build-retrieval-pipeline`](skills/generative-ai-engineering/references/tasks/ai-build-retrieval-pipeline.md) | query transform, filters, hybrid search và top-k | retriever | `build-change` | `R2-standard` / `standard-path` |
| [`ai-build-schema-retrieval-index`](skills/generative-ai-engineering/references/tasks/ai-build-schema-retrieval-index.md) | index cấu trúc bảng, cột, grain và partition key để agent lấy schema thật ngay trước khi sinh SQL | schema retrieval index | `build-change` | `R2-standard` / `standard-path` |
| [`ai-build-semantic-cache`](skills/generative-ai-engineering/references/tasks/ai-build-semantic-cache.md) | cache câu trả lời theo khoảng cách vector kèm khoá phiên bản dữ liệu và đo tỷ lệ hit sai | semantic answer cache | `build-change` | `R2-standard` / `standard-path` |
| [`ai-build-tool-using-agent`](skills/generative-ai-engineering/references/tasks/ai-build-tool-using-agent.md) | định nghĩa tools, permissions, state và termination | bounded agent workflow | `build-change` | `R2-standard` / `standard-path` |
| [`ai-implement-ai-guardrails`](skills/generative-ai-engineering/references/tasks/ai-implement-ai-guardrails.md) | kiểm tra input/output, tool permission và policy | guardrail layer | `build-change` | `R2-standard` / `standard-path` |
| [`ai-ingest-knowledge-source`](skills/generative-ai-engineering/references/tasks/ai-ingest-knowledge-source.md) | extract, clean, version và preserve permissions | indexed-ready corpus | `build-change` | `R2-standard` / `standard-path` |

#### Test / Assure (5 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`ai-analyze-ai-failures`](skills/generative-ai-engineering/references/tasks/ai-analyze-ai-failures.md) | cluster failure modes và propose fixes | failure taxonomy | `advisory-analysis` | `R0-light` / `fast-path` |
| [`ai-audit-tool-surface`](skills/generative-ai-engineering/references/tasks/ai-audit-tool-surface.md) | đối chiếu quyền agent thật sự có với quyền contract cho phép và dấu vết truy cập | tool surface access audit | `governance-assurance` | `R1-reviewed` / `standard-path` |
| [`ai-evaluate-answer-quality`](skills/generative-ai-engineering/references/tasks/ai-evaluate-answer-quality.md) | đo correctness, groundedness, relevance và refusal | answer evaluation | `advisory-analysis` | `R0-light` / `fast-path` |
| [`ai-evaluate-retrieval-quality`](skills/generative-ai-engineering/references/tasks/ai-evaluate-retrieval-quality.md) | đo recall/precision/ranking theo gold set | retrieval evaluation | `advisory-analysis` | `R0-light` / `fast-path` |
| [`ai-test-prompt-injection-resistance`](skills/generative-ai-engineering/references/tasks/ai-test-prompt-injection-resistance.md) | chạy attack set và đánh giá containment | security test report | `advisory-analysis` | `R0-light` / `fast-path` |

#### Operate / Improve (3 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`ai-monitor-ai-application`](skills/generative-ai-engineering/references/tasks/ai-monitor-ai-application.md) | theo dõi quality, latency, cost, safety và feedback | AI observability dashboard | `advisory-analysis` | `R0-light` / `fast-path` |
| [`ai-optimize-ai-cost-latency`](skills/generative-ai-engineering/references/tasks/ai-optimize-ai-cost-latency.md) | tune model routing, caching, context và batching | benchmarked optimization | `build-change` | `R2-standard` / `standard-path` |
| [`ai-release-ai-version`](skills/generative-ai-engineering/references/tasks/ai-release-ai-version.md) | evaluate, approve, canary và rollback | controlled release | `production-release` | `R3-controlled` / `controlled-path` |

<a id="skill-data-documentation-and-diagrams"></a>

### 24. `data-documentation-and-diagrams` — Data Documentation and Diagrams

**Claude trigger description:** Create validated data documentation, ADRs, runbooks, postmortems, ERDs, BPMN, sequence, state, lineage and architecture diagrams. Use when the primary deliverable is a data document or technical diagram.

**Ownership:** Tạo và duy trì architecture diagrams, data flows, lineage views, runbooks, SOPs, dictionaries và documentation packages.

**Khi nên dùng:** Dùng khi primary deliverable là tài liệu/diagram có audience, scope, source và review cycle rõ ràng.

**Ranh giới và handoff:** Không vẽ quan hệ không có evidence; mọi tài liệu cần owner, version, freshness và liên kết tới artifact thực.

**Quy mô:** 20 tasks — Plan / Design 18; Build / Deliver 1; Test / Assure 1; Operate / Improve 0.

**Domain references tải khi cần:** `adapter-dbt.md`, `adapter-metadata-catalog.md`, `adapter-power-bi.md`, `adapter-tableau-looker.md`, `authored-prose-voice.md`, `diagram-fidelity-standard.md`, `external-tool-access.md`, `learning-memory-interoperability.md`, `model-selection.md`, `response-compression.md`, `solution-option-framing.md`, `workflow-runtime-and-evidence-os.md`.

**Templates/assets có thể tái sử dụng:** `atomic-task-output.yaml`, `design-option-set.yaml`, `diagram-provenance.yaml`.

**Scripts:** `validate_diagram_source.py`.

#### Plan / Design (18 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`docs-create-architecture-diagram`](skills/data-documentation-and-diagrams/references/tasks/docs-create-architecture-diagram.md) | mô tả systems, services, stores và flows bằng D2 | architecture diagram | `design-specification` | `R1-reviewed` / `standard-path` |
| [`docs-create-bpmn-process`](skills/data-documentation-and-diagrams/references/tasks/docs-create-bpmn-process.md) | tạo BPMN 2.0 có pools, lanes, events, gateways và semantic validation | valid BPMN artifact | `design-specification` | `R1-reviewed` / `standard-path` |
| [`docs-create-d2-activity-diagram`](skills/data-documentation-and-diagrams/references/tasks/docs-create-d2-activity-diagram.md) | tạo standalone activity diagram bằng D2 | D2 source and rendered image | `design-specification` | `R1-reviewed` / `standard-path` |
| [`docs-create-d2-erd`](skills/data-documentation-and-diagrams/references/tasks/docs-create-d2-erd.md) | tạo standalone ERD dễ đọc cho model phức tạp | D2 ERD | `design-specification` | `R1-reviewed` / `standard-path` |
| [`docs-create-dbml-schema`](skills/data-documentation-and-diagrams/references/tasks/docs-create-dbml-schema.md) | tạo DBML có types, keys, indexes và exportable SQL | validated DBML schema | `design-specification` | `R1-reviewed` / `standard-path` |
| [`docs-create-mermaid-activity-diagram`](skills/data-documentation-and-diagrams/references/tasks/docs-create-mermaid-activity-diagram.md) | mô hình hóa flow có branches/loops nhỏ | validated Mermaid activity diagram | `design-specification` | `R1-reviewed` / `standard-path` |
| [`docs-create-mermaid-erd`](skills/data-documentation-and-diagrams/references/tasks/docs-create-mermaid-erd.md) | tạo inline ERD cho model nhỏ/trung bình | Mermaid ERD | `design-specification` | `R1-reviewed` / `standard-path` |
| [`docs-create-sequence-diagram`](skills/data-documentation-and-diagrams/references/tasks/docs-create-sequence-diagram.md) | mô tả actors/services/messages/alternatives theo thời gian | sequence diagram | `design-specification` | `R1-reviewed` / `standard-path` |
| [`docs-create-state-diagram`](skills/data-documentation-and-diagrams/references/tasks/docs-create-state-diagram.md) | mô tả states, triggers, valid và invalid transitions | state model | `design-specification` | `R1-reviewed` / `standard-path` |
| [`docs-create-swimlane-activity-diagram`](skills/data-documentation-and-diagrams/references/tasks/docs-create-swimlane-activity-diagram.md) | mô hình hóa multi-role process bằng PlantUML lanes | rendered swimlane diagram | `design-specification` | `R1-reviewed` / `standard-path` |
| [`docs-create-usecase-diagram`](skills/data-documentation-and-diagrams/references/tasks/docs-create-usecase-diagram.md) | mô tả actors, system boundary và include/extend | use-case diagram | `design-specification` | `R1-reviewed` / `standard-path` |
| [`docs-select-diagram-type`](skills/data-documentation-and-diagrams/references/tasks/docs-select-diagram-type.md) | chọn ERD, sequence, state, activity, swimlane, BPMN, use case hoặc architecture theo question | diagram decision | `design-specification` | `R1-reviewed` / `standard-path` |
| [`docs-write-api-documentation`](skills/data-documentation-and-diagrams/references/tasks/docs-write-api-documentation.md) | ghi contract, auth, examples, errors và versioning | API documentation | `design-specification` | `R1-reviewed` / `standard-path` |
| [`docs-write-architecture-document`](skills/data-documentation-and-diagrams/references/tasks/docs-write-architecture-document.md) | ghi context, components, flows, qualities và decisions | architecture document | `design-specification` | `R1-reviewed` / `standard-path` |
| [`docs-write-data-documentation`](skills/data-documentation-and-diagrams/references/tasks/docs-write-data-documentation.md) | ghi sources, models, metrics, lineage và caveats | data documentation | `design-specification` | `R1-reviewed` / `standard-path` |
| [`docs-write-operational-runbook`](skills/data-documentation-and-diagrams/references/tasks/docs-write-operational-runbook.md) | ghi symptoms, diagnosis, recovery, escalation và verification | runbook | `design-specification` | `R1-reviewed` / `standard-path` |
| [`docs-write-postmortem`](skills/data-documentation-and-diagrams/references/tasks/docs-write-postmortem.md) | ghi impact, timeline, root cause và actions | postmortem | `design-specification` | `R1-reviewed` / `standard-path` |
| [`docs-write-release-notes`](skills/data-documentation-and-diagrams/references/tasks/docs-write-release-notes.md) | tóm tắt changes, impact, migration và known issues | release notes | `production-release` | `R3-controlled` / `controlled-path` |

#### Build / Deliver (1 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`docs-maintain-changelog`](skills/data-documentation-and-diagrams/references/tasks/docs-maintain-changelog.md) | cập nhật versioned change history từ release evidence | changelog | `advisory-analysis` | `R0-light` / `fast-path` |

#### Test / Assure (1 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`docs-validate-diagram-semantics`](skills/data-documentation-and-diagrams/references/tasks/docs-validate-diagram-semantics.md) | kiểm tra missing node, dead end, cardinality, direction và domain correctness | diagram QA report | `advisory-analysis` | `R0-light` / `fast-path` |

<a id="skill-data-enablement-and-knowledge"></a>

### 25. `data-enablement-and-knowledge` — Data Enablement and Knowledge

**Claude trigger description:** Enable data teams through technical onboarding, learning plans, explanations, walkthroughs, pairing, knowledge checks, articles and knowledge-base curation. Use for internal data enablement or knowledge-transfer work.

**Ownership:** Xây knowledge articles, concept maps, linked/versioned libraries, office hours, communities, adoption và publishing workflows.

**Khi nên dùng:** Dùng khi tri thức đã được duyệt cần tổ chức để tìm kiếm, học, tái sử dụng hoặc xuất bản sang Notion/knowledge platform.

**Ranh giới và handoff:** Một note đơn lẻ khác với governed library; publishing là downstream handoff, còn source of truth phải có stable IDs, provenance và version.

**Quy mô:** 17 tasks — Plan / Design 5; Build / Deliver 10; Test / Assure 1; Operate / Improve 1.

**Domain references tải khi cần:** `authored-prose-voice.md`, `evidence-based-repository-understanding.md`, `learning-memory-interoperability.md`, `linked-knowledge-library.md`, `model-selection.md`, `response-compression.md`, `solution-option-framing.md`, `workflow-runtime-and-evidence-os.md`.

**Templates/assets có thể tái sử dụng:** `atomic-task-output.yaml`, `concept-knowledge-map.yaml`, `data-path-trace.yaml`, `design-option-set.yaml`, `knowledge-library.yaml`.

#### Plan / Design (5 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`enable-create-code-walkthrough`](skills/data-enablement-and-knowledge/references/tasks/enable-create-code-walkthrough.md) | dẫn giải data code từ entry point tới output | code walkthrough | `design-specification` | `R1-reviewed` / `standard-path` |
| [`enable-create-knowledge-article`](skills/data-enablement-and-knowledge/references/tasks/enable-create-knowledge-article.md) | chuẩn hóa problem, solution, evidence và applicability | knowledge article | `design-specification` | `R1-reviewed` / `standard-path` |
| [`enable-create-learning-plan`](skills/data-enablement-and-knowledge/references/tasks/enable-create-learning-plan.md) | chuyển competency gap thành modules, practice và milestones | learning plan | `design-specification` | `R1-reviewed` / `standard-path` |
| [`enable-create-role-onboarding`](skills/data-enablement-and-knowledge/references/tasks/enable-create-role-onboarding.md) | tạo lộ trình 30/60/90 ngày theo role và access needs | role onboarding plan | `design-specification` | `R1-reviewed` / `standard-path` |
| [`enable-create-system-onboarding`](skills/data-enablement-and-knowledge/references/tasks/enable-create-system-onboarding.md) | giải thích architecture, workflows, environments và runbooks | system onboarding guide | `design-specification` | `R1-reviewed` / `standard-path` |

#### Build / Deliver (10 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`enable-build-concept-knowledge-map`](skills/data-enablement-and-knowledge/references/tasks/enable-build-concept-knowledge-map.md) | liên kết concept, prerequisite, contrast, application, misconception và related questions | linked concept knowledge map | `build-change` | `R2-standard` / `standard-path` |
| [`enable-build-versioned-knowledge-library`](skills/data-enablement-and-knowledge/references/tasks/enable-build-versioned-knowledge-library.md) | tổ chức deep dives, question dossiers, tags, backlinks, owner, freshness và review status | governed knowledge library | `build-change` | `R2-standard` / `standard-path` |
| [`enable-capture-lessons-learned`](skills/data-enablement-and-knowledge/references/tasks/enable-capture-lessons-learned.md) | rút decisions, surprises, patterns và anti-patterns từ project | lessons-learned record | `advisory-analysis` | `R0-light` / `fast-path` |
| [`enable-curate-knowledge-base`](skills/data-enablement-and-knowledge/references/tasks/enable-curate-knowledge-base.md) | merge duplicates, retire stale content và repair links | curated knowledge base | `advisory-analysis` | `R0-light` / `fast-path` |
| [`enable-explain-data-concept`](skills/data-enablement-and-knowledge/references/tasks/enable-explain-data-concept.md) | giải thích khái niệm theo audience và concrete examples | concept lesson | `advisory-analysis` | `R0-light` / `fast-path` |
| [`enable-generate-knowledge-check`](skills/data-enablement-and-knowledge/references/tasks/enable-generate-knowledge-check.md) | tạo quiz/scenario và answer rubric | knowledge check | `advisory-analysis` | `R0-light` / `fast-path` |
| [`enable-generate-practice-exercise`](skills/data-enablement-and-knowledge/references/tasks/enable-generate-practice-exercise.md) | tạo realistic task, fixtures và success criteria | practice assignment | `advisory-analysis` | `R0-light` / `fast-path` |
| [`enable-run-pair-programming-session`](skills/data-enablement-and-knowledge/references/tasks/enable-run-pair-programming-session.md) | chia task, checkpoints và feedback loop | completed guided exercise | `advisory-analysis` | `R0-light` / `fast-path` |
| [`enable-run-skill-assessment`](skills/data-enablement-and-knowledge/references/tasks/enable-run-skill-assessment.md) | đánh giá artifact thực tế theo competency rubric | skill assessment | `advisory-analysis` | `R2-standard` / `standard-path` |
| [`enable-summarize-technical-source`](skills/data-enablement-and-knowledge/references/tasks/enable-summarize-technical-source.md) | tổng hợp paper/book/documentation thành actionable notes | source summary | `advisory-analysis` | `R0-light` / `fast-path` |

#### Test / Assure (1 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`enable-measure-learning-progress`](skills/data-enablement-and-knowledge/references/tasks/enable-measure-learning-progress.md) | theo dõi completion, assessment và application evidence | learning-progress report | `advisory-analysis` | `R0-light` / `fast-path` |

#### Operate / Improve (1 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`enable-publish-knowledge`](skills/data-enablement-and-knowledge/references/tasks/enable-publish-knowledge.md) | kiểm tra owner, sensitivity, discoverability và version trước publish | published knowledge asset | `production-release` | `R3-controlled` / `controlled-path` |

<a id="skill-data-academy-and-curriculum"></a>

### 26. `data-academy-and-curriculum` — Data Academy and Curriculum

**Claude trigger description:** Design and deliver role-based Data Academy curricula with theory, labs, capstones, assessments, remediation, certification and effectiveness measurement. Use for structured learning programs across Data roles and levels. Route hiring loops, scorecards and candidate evaluation to data-talent-acquisition-and-interview; this skill teaches, never selects.

**Ownership:** Thiết kế curriculum theo role/level, theory, labs, capstones, assessment, remediation, certification và knowledge deep dives.

**Khi nên dùng:** Dùng cho đào tạo có learning objectives, prerequisites, evidence of mastery và transfer sang tình huống mới.

**Ranh giới và handoff:** Không coi attendance hay đáp án học thuộc là competency; certification cần rubric, critical failures, calibration và retention/transfer evidence.

**Quy mô:** 49 tasks — Plan / Design 29; Build / Deliver 11; Test / Assure 8; Operate / Improve 1.

**Domain references tải khi cần:** `assessment-and-certification.md`, `authored-prose-voice.md`, `concept-registry-standard.md`, `diagnostic-session-method.md`, `knowledge-deep-dive-standard.md`, `learning-memory-interoperability.md`, `model-selection.md`, `note-corpus-operating-system.md`, `response-compression.md`, `role-curricula.md`, `solution-option-framing.md`, `workflow-runtime-and-evidence-os.md`.

**Templates/assets có thể tái sử dụng:** `assessment-blueprint.yaml`, `atomic-task-output.yaml`, `concept-knowledge-graph.yaml`, `concept-registry.json`, `corpus-priority-plan.yaml`, `corpus-workflow-manifest.json`, `curriculum-spec.yaml`, `design-option-set.yaml`, `knowledge-deep-dive.yaml`, `learner-evidence.yaml`, `lesson-plan.yaml`, `misconception-feedback.yaml`, `note-corpus-audit.yaml`, `note-corpus-manifest.json`, `note-diagnostic-session.yaml`, `prior-knowledge-profile.yaml`, `question-learning-traceability.yaml`, `role-roadmap.yaml`, `skill-track-map.yaml`.

**Scripts:** `validate_curriculum_coverage.py`, `validate_note_corpus.py`.

#### Plan / Design (29 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`academy-build-competency-curriculum-map`](skills/data-academy-and-curriculum/references/tasks/academy-build-competency-curriculum-map.md) | nối competencies, modules, practice và assessments | competency-to-curriculum map | `learning` | `R2-standard` / `standard-path` |
| [`academy-build-role-theory-pack`](skills/data-academy-and-curriculum/references/tasks/academy-build-role-theory-pack.md) | đóng gói lý thuyết chuẩn theo role, level và company context | role theory knowledge pack | `learning` | `R2-standard` / `standard-path` |
| [`academy-build-skill-track-map`](skills/data-academy-and-curriculum/references/tasks/academy-build-skill-track-map.md) | tách mỗi bước roadmap thành skill track có thứ tự học, module và tiêu chí ra | skill-track map | `learning` | `R2-standard` / `standard-path` |
| [`academy-create-business-case-study`](skills/data-academy-and-curriculum/references/tasks/academy-create-business-case-study.md) | tạo scenario, data, ambiguity, stakeholder context và decision ask | case-study package | `learning` | `R1-reviewed` / `standard-path` |
| [`academy-create-instructor-guide`](skills/data-academy-and-curriculum/references/tasks/academy-create-instructor-guide.md) | ghi facilitation flow, timings, prompts, expected questions và interventions | instructor guide | `learning` | `R1-reviewed` / `standard-path` |
| [`academy-create-learner-workbook`](skills/data-academy-and-curriculum/references/tasks/academy-create-learner-workbook.md) | tạo notes, exercises, reflection và progress checks | learner workbook | `learning` | `R1-reviewed` / `standard-path` |
| [`academy-create-learning-sandbox`](skills/data-academy-and-curriculum/references/tasks/academy-create-learning-sandbox.md) | tạo môi trường cô lập, reproducible và cost-bounded | learning sandbox | `learning` | `R1-reviewed` / `standard-path` |
| [`academy-create-lecture-deck`](skills/data-academy-and-curriculum/references/tasks/academy-create-lecture-deck.md) | chuyển lesson thành slide narrative có examples và checks | lecture deck | `learning` | `R1-reviewed` / `standard-path` |
| [`academy-create-remediation-plan`](skills/data-academy-and-curriculum/references/tasks/academy-create-remediation-plan.md) | thiết kế targeted theory, practice, coaching và retest | learner remediation plan | `learning` | `R1-reviewed` / `standard-path` |
| [`academy-create-worked-example`](skills/data-academy-and-curriculum/references/tasks/academy-create-worked-example.md) | giải một bài mẫu từng bước kèm reasoning và checks | worked example | `learning` | `R1-reviewed` / `standard-path` |
| [`academy-define-role-learning-outcomes`](skills/data-academy-and-curriculum/references/tasks/academy-define-role-learning-outcomes.md) | chuyển competency theo role/level thành observable learning outcomes | role learning-outcome framework | `learning` | `R1-reviewed` / `standard-path` |
| [`academy-design-capstone-project`](skills/data-academy-and-curriculum/references/tasks/academy-design-capstone-project.md) | tạo end-to-end project, milestones, gates và rubric | capstone specification | `learning` | `R1-reviewed` / `standard-path` |
| [`academy-design-formative-assessment`](skills/data-academy-and-curriculum/references/tasks/academy-design-formative-assessment.md) | tạo low-stakes checks để điều chỉnh việc học sớm | formative assessment | `learning` | `R2-standard` / `standard-path` |
| [`academy-design-hands-on-lab`](skills/data-academy-and-curriculum/references/tasks/academy-design-hands-on-lab.md) | tạo lab setup, tasks, checkpoints, cleanup và success criteria | lab specification | `learning` | `R1-reviewed` / `standard-path` |
| [`academy-design-learning-module`](skills/data-academy-and-curriculum/references/tasks/academy-design-learning-module.md) | định nghĩa objectives, concepts, examples, activities và assessment | learning-module specification | `learning` | `R1-reviewed` / `standard-path` |
| [`academy-design-level-learning-path`](skills/data-academy-and-curriculum/references/tasks/academy-design-level-learning-path.md) | tạo pathway Junior/Middle/Senior/Lead có entry/exit criteria | level learning pathway | `learning` | `R1-reviewed` / `standard-path` |
| [`academy-design-role-syllabus`](skills/data-academy-and-curriculum/references/tasks/academy-design-role-syllabus.md) | thiết kế scope, sequence, pacing và evaluation cho một role | role syllabus | `learning` | `R1-reviewed` / `standard-path` |
| [`academy-design-summative-exam`](skills/data-academy-and-curriculum/references/tasks/academy-design-summative-exam.md) | tạo blueprint, questions, practical tasks, scoring và pass rules | summative exam package | `learning` | `R1-reviewed` / `standard-path` |
| [`academy-elicit-prior-knowledge`](skills/data-academy-and-curriculum/references/tasks/academy-elicit-prior-knowledge.md) | hỏi người học đã nắm được gì và giải quyết learner memory trước khi lập kế hoạch corpus | prior-knowledge profile | `learning` | `R1-reviewed` / `standard-path` |
| [`academy-map-learning-prerequisites`](skills/data-academy-and-curriculum/references/tasks/academy-map-learning-prerequisites.md) | xác định kiến thức tiên quyết và dependency giữa modules | learning prerequisite graph | `learning` | `R1-reviewed` / `standard-path` |
| [`academy-map-questions-to-learning-objectives`](skills/data-academy-and-curriculum/references/tasks/academy-map-questions-to-learning-objectives.md) | nối question tới competency, Bloom depth, prerequisites, learning objectives và assessments | question-to-learning traceability matrix | `learning` | `R1-reviewed` / `standard-path` |
| [`academy-plan-learning-cohort`](skills/data-academy-and-curriculum/references/tasks/academy-plan-learning-cohort.md) | lập audience, schedule, instructors, capacity và support | cohort delivery plan | `learning` | `R1-reviewed` / `standard-path` |
| [`academy-plan-note-corpus`](skills/data-academy-and-curriculum/references/tasks/academy-plan-note-corpus.md) | liệt kê toàn bộ note dự kiến theo module kèm id, prerequisite và trạng thái build | note corpus plan | `learning` | `R1-reviewed` / `standard-path` |
| [`academy-prioritize-corpus-by-gap`](skills/data-academy-and-curriculum/references/tasks/academy-prioritize-corpus-by-gap.md) | xếp thứ tự module theo khoảng cách năng lực đã đo thay vì theo thứ tự roadmap | gap-prioritized corpus plan | `learning` | `R1-reviewed` / `standard-path` |
| [`academy-research-role-roadmap`](skills/data-academy-and-curriculum/references/tasks/academy-research-role-roadmap.md) | nghiên cứu roadmap hành nghề đang được dùng từ nguồn công khai, mỗi mục kèm nguồn và ngày truy cập | sourced role roadmap | `learning` | `R1-reviewed` / `standard-path` |
| [`academy-write-answer-key`](skills/data-academy-and-curriculum/references/tasks/academy-write-answer-key.md) | tạo expected reasoning, alternatives, checks và common errors | answer key | `learning` | `R1-reviewed` / `standard-path` |
| [`academy-write-assessment-rubric`](skills/data-academy-and-curriculum/references/tasks/academy-write-assessment-rubric.md) | định nghĩa criteria, evidence, performance levels và critical failures | assessment rubric | `learning` | `R2-standard` / `standard-path` |
| [`academy-write-knowledge-deep-dive`](skills/data-academy-and-curriculum/references/tasks/academy-write-knowledge-deep-dive.md) | giải thích một concept từ definition, mental model, mechanism, trade-offs tới edge cases, examples và sources | evidence-backed knowledge deep dive | `learning` | `R1-reviewed` / `standard-path` |
| [`academy-write-theory-lesson`](skills/data-academy-and-curriculum/references/tasks/academy-write-theory-lesson.md) | viết lesson có mental model, principles, trade-offs và misconceptions | theory lesson | `learning` | `R1-reviewed` / `standard-path` |

#### Build / Deliver (11 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`academy-apply-misconception-feedback`](skills/data-academy-and-curriculum/references/tasks/academy-apply-misconception-feedback.md) | gom ngộ nhận lặp lại theo concept key rồi bổ sung vào chính note dạy sai mô hình đó | revised note batch | `learning` | `R1-reviewed` / `standard-path` |
| [`academy-build-concept-knowledge-graph`](skills/data-academy-and-curriculum/references/tasks/academy-build-concept-knowledge-graph.md) | mô hình hóa concepts, prerequisites, dependencies, misconceptions và transfer paths | concept knowledge graph | `learning` | `R2-standard` / `standard-path` |
| [`academy-build-note-module`](skills/data-academy-and-curriculum/references/tasks/academy-build-note-module.md) | dựng trọn bộ note của một module theo cùng một chuẩn rồi cập nhật corpus manifest | module note batch | `learning` | `R2-standard` / `standard-path` |
| [`academy-deliver-theory-session`](skills/data-academy-and-curriculum/references/tasks/academy-deliver-theory-session.md) | thực hiện lesson có knowledge checks và participation evidence | delivered-session record | `learning` | `R1-reviewed` / `standard-path` |
| [`academy-facilitate-learning-workshop`](skills/data-academy-and-curriculum/references/tasks/academy-facilitate-learning-workshop.md) | điều phối collaborative problem solving và peer feedback | workshop outcome record | `learning` | `R1-reviewed` / `standard-path` |
| [`academy-generate-training-dataset`](skills/data-academy-and-curriculum/references/tasks/academy-generate-training-dataset.md) | tạo dataset realistic, privacy-safe và có planted issues | training dataset | `learning` | `R1-reviewed` / `standard-path` |
| [`academy-index-note-corpus`](skills/data-academy-and-curriculum/references/tasks/academy-index-note-corpus.md) | hợp nhất corpus thành index tra cứu bền vững ghi lại cái gì tồn tại, không suy ra mastery | note corpus index | `learning` | `R1-reviewed` / `standard-path` |
| [`academy-run-knowledge-diagnostic`](skills/data-academy-and-curriculum/references/tasks/academy-run-knowledge-diagnostic.md) | đo baseline theory, practical skills và misconceptions | learner diagnostic report | `learning` | `R1-reviewed` / `standard-path` |
| [`academy-run-lab-session`](skills/data-academy-and-curriculum/references/tasks/academy-run-lab-session.md) | giám sát hands-on execution, safety, checkpoints và recovery | lab completion evidence | `learning` | `R1-reviewed` / `standard-path` |
| [`academy-run-learning-office-hours`](skills/data-academy-and-curriculum/references/tasks/academy-run-learning-office-hours.md) | xử lý blockers, misconceptions và follow-up actions | office-hours support log | `learning` | `R1-reviewed` / `standard-path` |
| [`academy-run-note-diagnostic`](skills/data-academy-and-curriculum/references/tasks/academy-run-note-diagnostic.md) | chạy kịch bản chẩn đoán của corpus theo vòng Socratic có giới hạn rồi đề xuất hạng bằng chứng | note diagnostic session record | `learning` | `R1-reviewed` / `standard-path` |

#### Test / Assure (8 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`academy-analyze-learning-gaps`](skills/data-academy-and-curriculum/references/tasks/academy-analyze-learning-gaps.md) | tổng hợp item, cohort và role-level failure patterns | learning-gap analysis | `learning` | `R1-reviewed` / `standard-path` |
| [`academy-assess-learner-submission`](skills/data-academy-and-curriculum/references/tasks/academy-assess-learner-submission.md) | chấm artifact theo rubric với evidence và actionable feedback | assessed submission | `learning` | `R1-reviewed` / `standard-path` |
| [`academy-assess-organizational-learning-needs`](skills/data-academy-and-curriculum/references/tasks/academy-assess-organizational-learning-needs.md) | phân tích strategy, competency gaps, incidents và delivery demand | organizational learning-needs assessment | `learning` | `R1-reviewed` / `standard-path` |
| [`academy-audit-curriculum-quality`](skills/data-academy-and-curriculum/references/tasks/academy-audit-curriculum-quality.md) | kiểm tra accuracy, coverage, accessibility, bias và assessment validity | curriculum quality audit | `learning` | `R1-reviewed` / `standard-path` |
| [`academy-audit-note-corpus`](skills/data-academy-and-curriculum/references/tasks/academy-audit-note-corpus.md) | kiểm tra trùng lặp, cạnh quan hệ treo, chu trình prerequisite, độ cũ và độ phủ của corpus | note corpus audit | `learning` | `R1-reviewed` / `standard-path` |
| [`academy-calibrate-assessors`](skills/data-academy-and-curriculum/references/tasks/academy-calibrate-assessors.md) | chuẩn hóa cách chấm bằng anchor examples và disagreement resolution | assessor-calibration record | `learning` | `R1-reviewed` / `standard-path` |
| [`academy-certify-role-competency`](skills/data-academy-and-curriculum/references/tasks/academy-certify-role-competency.md) | đối chiếu evidence với pass rules và scope chứng nhận | competency certification decision | `learning` | `R1-reviewed` / `standard-path` |
| [`academy-measure-training-effectiveness`](skills/data-academy-and-curriculum/references/tasks/academy-measure-training-effectiveness.md) | đo reaction, learning, behavior transfer và business impact | training-effectiveness report | `learning` | `R1-reviewed` / `standard-path` |

#### Operate / Improve (1 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`academy-refresh-curriculum`](skills/data-academy-and-curriculum/references/tasks/academy-refresh-curriculum.md) | cập nhật theo stack, policy, incidents và learner evidence | versioned curriculum release | `learning` | `R1-reviewed` / `standard-path` |

<a id="skill-data-onboarding-and-integration"></a>

### 27. `data-onboarding-and-integration` — Data Onboarding and Integration

**Claude trigger description:** Plan and operate Data Department preboarding, access readiness, orientation, shadowing, first work, checkpoints, crossboarding, reboarding and offboarding. Use for new-hire or role-transition integration.

**Ownership:** Đưa nhân sự mới vào môi trường qua preboarding, access, context, role plan, buddy, checkpoints, readiness và knowledge transfer/offboarding.

**Khi nên dùng:** Dùng cho hành trình 7/30/60/90 ngày hoặc thay đổi role/team cần kiểm soát quyền và năng lực.

**Ranh giới và handoff:** Không xác nhận readiness chỉ dựa trên checklist; access dùng least privilege và completion cần evidence theo role.

**Quy mô:** 34 tasks — Plan / Design 8; Build / Deliver 18; Test / Assure 4; Operate / Improve 4.

**Domain references tải khi cần:** `external-tool-access.md`, `learning-memory-interoperability.md`, `model-selection.md`, `response-compression.md`, `role-onboarding-tracks.md`, `solution-option-framing.md`, `workflow-runtime-and-evidence-os.md`.

**Templates/assets có thể tái sử dụng:** `access-readiness.yaml`, `atomic-task-output.yaml`, `checkpoint.yaml`, `design-option-set.yaml`, `onboarding-plan.yaml`.

**Scripts:** `score_onboarding_checkpoint.py`.

#### Plan / Design (8 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`onboard-collect-new-hire-context`](skills/data-onboarding-and-integration/references/tasks/onboard-collect-new-hire-context.md) | thu background, strengths, gaps, accessibility và support needs | new-hire context profile | `onboarding` | `R2-standard` / `standard-path` |
| [`onboard-create-first-week-plan`](skills/data-onboarding-and-integration/references/tasks/onboard-create-first-week-plan.md) | sắp xếp learning, meetings, setup, shadowing và small wins | first-week schedule | `onboarding` | `R2-standard` / `standard-path` |
| [`onboard-create-preboarding-checklist`](skills/data-onboarding-and-integration/references/tasks/onboard-create-preboarding-checklist.md) | chuẩn bị contract dependencies, equipment, accounts, schedule và contacts | preboarding checklist | `onboarding` | `R2-standard` / `standard-path` |
| [`onboard-define-data-onboarding-standard`](skills/data-onboarding-and-integration/references/tasks/onboard-define-data-onboarding-standard.md) | định nghĩa lifecycle, mandatory content, gates, owners và SLAs | data onboarding standard | `onboarding` | `R2-standard` / `standard-path` |
| [`onboard-plan-access-provisioning`](skills/data-onboarding-and-integration/references/tasks/onboard-plan-access-provisioning.md) | map role tới least-privilege access và approvers | access provisioning plan | `onboarding` | `R3-controlled` / `controlled-path` |
| [`onboard-plan-new-hire-onboarding`](skills/data-onboarding-and-integration/references/tasks/onboard-plan-new-hire-onboarding.md) | cá nhân hóa theo role, level, location, employment type và start date | individual onboarding plan | `onboarding` | `R2-standard` / `standard-path` |
| [`onboard-plan-stakeholder-introductions`](skills/data-onboarding-and-integration/references/tasks/onboard-plan-stakeholder-introductions.md) | sắp xếp sponsor, SMEs, consumers và partner teams theo relevance | stakeholder introduction plan | `onboarding` | `R2-standard` / `standard-path` |
| [`onboard-prepare-workstation-environment`](skills/data-onboarding-and-integration/references/tasks/onboard-prepare-workstation-environment.md) | thiết lập approved tools, runtime, configs và security baseline | workstation readiness evidence | `onboarding` | `R2-standard` / `standard-path` |

#### Build / Deliver (18 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`onboard-assign-onboarding-buddy`](skills/data-onboarding-and-integration/references/tasks/onboard-assign-onboarding-buddy.md) | chọn buddy, expectations, cadence và escalation path | buddy agreement | `onboarding` | `R2-standard` / `standard-path` |
| [`onboard-capture-onboarding-feedback`](skills/data-onboarding-and-integration/references/tasks/onboard-capture-onboarding-feedback.md) | thu anonymous và attributable feedback có action routing | onboarding feedback report | `onboarding` | `R2-standard` / `standard-path` |
| [`onboard-deliver-business-domain-orientation`](skills/data-onboarding-and-integration/references/tasks/onboard-deliver-business-domain-orientation.md) | dạy processes, entities, KPIs, rules và stakeholders | domain-orientation record | `onboarding` | `R2-standard` / `standard-path` |
| [`onboard-deliver-company-orientation`](skills/data-onboarding-and-integration/references/tasks/onboard-deliver-company-orientation.md) | giới thiệu strategy, products, customers, culture và operating norms | company-orientation completion record | `onboarding` | `R2-standard` / `standard-path` |
| [`onboard-deliver-data-architecture-orientation`](skills/data-onboarding-and-integration/references/tasks/onboard-deliver-data-architecture-orientation.md) | hướng dẫn systems, flows, models, environments và critical dependencies | architecture-orientation record | `onboarding` | `R2-standard` / `standard-path` |
| [`onboard-deliver-data-organization-orientation`](skills/data-onboarding-and-integration/references/tasks/onboard-deliver-data-organization-orientation.md) | giải thích team topology, services, ownership và interaction model | data-organization orientation record | `onboarding` | `R2-standard` / `standard-path` |
| [`onboard-deliver-governance-security-orientation`](skills/data-onboarding-and-integration/references/tasks/onboard-deliver-governance-security-orientation.md) | dạy policies, classifications, access, privacy và incident duties | governance-security training record | `onboarding` | `R3-controlled` / `controlled-path` |
| [`onboard-deliver-role-orientation`](skills/data-onboarding-and-integration/references/tasks/onboard-deliver-role-orientation.md) | làm rõ outcomes, responsibilities, boundaries và success measures | role-orientation record | `onboarding` | `R2-standard` / `standard-path` |
| [`onboard-deliver-toolchain-orientation`](skills/data-onboarding-and-integration/references/tasks/onboard-deliver-toolchain-orientation.md) | hướng dẫn local setup, Git, orchestration, warehouse, BI/ML và support paths | toolchain-orientation record | `onboarding` | `R2-standard` / `standard-path` |
| [`onboard-guide-documentation-discovery`](skills/data-onboarding-and-integration/references/tasks/onboard-guide-documentation-discovery.md) | hướng dẫn tìm glossary, catalog, runbooks, ADRs và standards | documentation-discovery exercise | `onboarding` | `R2-standard` / `standard-path` |
| [`onboard-onboard-data-contractor`](skills/data-onboarding-and-integration/references/tasks/onboard-onboard-data-contractor.md) | áp dụng bounded access, scope, deliverables và exit controls | contractor onboarding package | `onboarding` | `R2-standard` / `standard-path` |
| [`onboard-run-first-independent-task`](skills/data-onboarding-and-integration/references/tasks/onboard-run-first-independent-task.md) | giao task bounded để đánh giá khả năng tự chủ | first-independent-task assessment | `onboarding` | `R2-standard` / `standard-path` |
| [`onboard-run-guided-first-task`](skills/data-onboarding-and-integration/references/tasks/onboard-run-guided-first-task.md) | thực hiện task nhỏ với coach, gates và feedback | guided-task completion record | `onboarding` | `R2-standard` / `standard-path` |
| [`onboard-run-ninety-day-checkpoint`](skills/data-onboarding-and-integration/references/tasks/onboard-run-ninety-day-checkpoint.md) | đánh giá role readiness, outcomes, gaps và next development plan | ninety-day onboarding review | `onboarding` | `R2-standard` / `standard-path` |
| [`onboard-run-role-shadowing`](skills/data-onboarding-and-integration/references/tasks/onboard-run-role-shadowing.md) | theo dõi work thật có observation goals và debrief | shadowing evidence | `onboarding` | `R2-standard` / `standard-path` |
| [`onboard-run-seven-day-checkpoint`](skills/data-onboarding-and-integration/references/tasks/onboard-run-seven-day-checkpoint.md) | kiểm tra access, clarity, belonging, workload và blockers | seven-day checkpoint record | `onboarding` | `R2-standard` / `standard-path` |
| [`onboard-run-sixty-day-checkpoint`](skills/data-onboarding-and-integration/references/tasks/onboard-run-sixty-day-checkpoint.md) | đánh giá autonomy, quality, collaboration và domain growth | sixty-day checkpoint record | `onboarding` | `R2-standard` / `standard-path` |
| [`onboard-run-thirty-day-checkpoint`](skills/data-onboarding-and-integration/references/tasks/onboard-run-thirty-day-checkpoint.md) | đánh giá foundations, first contributions và support needs | thirty-day checkpoint record | `onboarding` | `R2-standard` / `standard-path` |

#### Test / Assure (4 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`onboard-assess-integration-health`](skills/data-onboarding-and-integration/references/tasks/onboard-assess-integration-health.md) | đo role clarity, access, network, learning, contribution và belonging | integration-health assessment | `onboarding` | `R2-standard` / `standard-path` |
| [`onboard-certify-onboarding-completion`](skills/data-onboarding-and-integration/references/tasks/onboard-certify-onboarding-completion.md) | kiểm tra mandatory evidence và manager/new-hire signoff | onboarding completion decision | `onboarding` | `R2-standard` / `standard-path` |
| [`onboard-measure-onboarding-effectiveness`](skills/data-onboarding-and-integration/references/tasks/onboard-measure-onboarding-effectiveness.md) | đo time-to-access, time-to-first-value, retention và readiness | onboarding effectiveness report | `onboarding` | `R2-standard` / `standard-path` |
| [`onboard-verify-access-readiness`](skills/data-onboarding-and-integration/references/tasks/onboard-verify-access-readiness.md) | test accounts, MFA, environments, repositories và data permissions | access-readiness report | `onboarding` | `R3-controlled` / `controlled-path` |

#### Operate / Improve (4 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`onboard-crossboard-role-transfer`](skills/data-onboarding-and-integration/references/tasks/onboard-crossboard-role-transfer.md) | tái định hướng khi đổi role/team/domain và giữ transferable context | crossboarding plan | `onboarding` | `R2-standard` / `standard-path` |
| [`onboard-offboard-and-transfer-knowledge`](skills/data-onboarding-and-integration/references/tasks/onboard-offboard-and-transfer-knowledge.md) | thu hồi access, bàn giao ownership, knowledge và open risks | offboarding evidence package | `onboarding` | `R4-critical` / `controlled-path` |
| [`onboard-reboard-returning-employee`](skills/data-onboarding-and-integration/references/tasks/onboard-reboard-returning-employee.md) | xác định thay đổi trong thời gian vắng mặt và rebuild readiness | reboarding plan | `onboarding` | `R2-standard` / `standard-path` |
| [`onboard-resolve-onboarding-blocker`](skills/data-onboarding-and-integration/references/tasks/onboard-resolve-onboarding-blocker.md) | triage owner, impact, workaround và permanent fix | resolved onboarding issue | `onboarding` | `R2-standard` / `standard-path` |

<a id="skill-data-talent-acquisition-and-interview"></a>

### 28. `data-talent-acquisition-and-interview` — Data Talent and Interviewing

**Claude trigger description:** Design and run structured Data hiring with role profiles, scorecards, interview loops, work samples, rubrics, calibration, debriefs, fairness and validity controls. Use for recruiting or interviewing Data roles. Route curriculum, labs and certification of existing staff to data-academy-and-curriculum; this skill decides who to hire, never how to train.

**Ownership:** Thiết kế hiring scorecards, sourcing/screening, structured interviews, role-specific rounds, rubrics, calibration, debrief và fairness audits.

**Khi nên dùng:** Dùng cho quy trình tuyển Data roles hoặc kiểm tra question bank đo đúng competency và evidence.

**Ranh giới và handoff:** Không leak answer anchors, không dùng protected traits, pedigree hay một câu hỏi làm single-point decision; quyết định cuối thuộc panel có thẩm quyền.

**Quy mô:** 41 tasks — Plan / Design 11; Build / Deliver 21; Test / Assure 8; Operate / Improve 1.

**Domain references tải khi cần:** `learning-memory-interoperability.md`, `model-selection.md`, `question-knowledge-validity.md`, `response-compression.md`, `role-interview-architecture.md`, `solution-option-framing.md`, `workflow-runtime-and-evidence-os.md`.

**Templates/assets có thể tái sử dụng:** `answer-anchor-pack.yaml`, `assessment-rubric.yaml`, `atomic-task-output.yaml`, `calibration-record.yaml`, `candidate-packet.yaml`, `debrief.yaml`, `design-option-set.yaml`, `fairness-validity-audit.yaml`, `hiring-workflow-state.yaml`, `interview-evidence.yaml`, `interview-loop.yaml`, `interviewer-guide.yaml`, `question-bank-coverage-audit.yaml`, `question-competency-evidence.yaml`, `role-scorecard.yaml`.

**Scripts:** `audit_question_bank.py`.

#### Plan / Design (11 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`talent-build-role-hiring-scorecard`](skills/data-talent-acquisition-and-interview/references/tasks/talent-build-role-hiring-scorecard.md) | chuyển outcomes/competencies thành observable signals và scoring anchors | role hiring scorecard | `hiring` | `R2-standard` / `standard-path` |
| [`talent-build-role-question-bank`](skills/data-talent-acquisition-and-interview/references/tasks/talent-build-role-question-bank.md) | tạo behavioral, technical và scenario questions theo role/level | versioned interview question bank | `hiring` | `R2-standard` / `standard-path` |
| [`talent-create-candidate-feedback`](skills/data-talent-acquisition-and-interview/references/tasks/talent-create-candidate-feedback.md) | tạo feedback lawful, respectful và evidence-grounded | candidate feedback package | `hiring` | `R3-controlled` / `controlled-path` |
| [`talent-create-interviewer-guide`](skills/data-talent-acquisition-and-interview/references/tasks/talent-create-interviewer-guide.md) | ghi conduct, probing, evidence capture, prohibited topics và timing | interviewer guide | `hiring` | `R2-standard` / `standard-path` |
| [`talent-define-data-role-profile`](skills/data-talent-acquisition-and-interview/references/tasks/talent-define-data-role-profile.md) | định nghĩa mission, outcomes, responsibilities, boundaries và level | role profile | `hiring` | `R2-standard` / `standard-path` |
| [`talent-design-structured-interview-loop`](skills/data-talent-acquisition-and-interview/references/tasks/talent-design-structured-interview-loop.md) | sắp xếp stages, competencies, interviewers và decision rules | interview-loop design | `hiring` | `R2-standard` / `standard-path` |
| [`talent-design-take-home-assignment`](skills/data-talent-acquisition-and-interview/references/tasks/talent-design-take-home-assignment.md) | tạo bounded realistic artifact, dataset, rubric và timebox | take-home assignment package | `hiring` | `R2-standard` / `standard-path` |
| [`talent-map-question-to-competency-evidence`](skills/data-talent-acquisition-and-interview/references/tasks/talent-map-question-to-competency-evidence.md) | phân tích intent, competency, depth, expected evidence, probes và red flags của từng question | question-competency-evidence matrix | `hiring` | `R2-standard` / `standard-path` |
| [`talent-plan-hiring-campaign`](skills/data-talent-acquisition-and-interview/references/tasks/talent-plan-hiring-campaign.md) | xác định funnel, channels, timeline, owners, SLAs và capacity | hiring campaign plan | `hiring` | `R2-standard` / `standard-path` |
| [`talent-write-data-job-description`](skills/data-talent-acquisition-and-interview/references/tasks/talent-write-data-job-description.md) | viết JD rõ scope, competencies, conditions và inclusive requirements | job description | `hiring` | `R2-standard` / `standard-path` |
| [`talent-write-interview-answer-anchors`](skills/data-talent-acquisition-and-interview/references/tasks/talent-write-interview-answer-anchors.md) | định nghĩa behavioral anchors và evidence của câu trả lời yếu/đạt/mạnh mà không tạo script học thuộc | calibrated answer-anchor pack | `hiring` | `R2-standard` / `standard-path` |

#### Build / Deliver (21 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`talent-make-hiring-recommendation`](skills/data-talent-acquisition-and-interview/references/tasks/talent-make-hiring-recommendation.md) | cân must-have evidence, risks và development assumptions | hiring recommendation | `hiring` | `R3-controlled` / `controlled-path` |
| [`talent-run-analytics-case-interview`](skills/data-talent-acquisition-and-interview/references/tasks/talent-run-analytics-case-interview.md) | đánh giá framing, metrics, analysis, insight và decision communication | analytics-case assessment | `hiring` | `R3-controlled` / `controlled-path` |
| [`talent-run-behavioral-interview`](skills/data-talent-acquisition-and-interview/references/tasks/talent-run-behavioral-interview.md) | đánh giá past evidence về ownership, collaboration, learning và conflict | behavioral assessment | `hiring` | `R3-controlled` / `controlled-path` |
| [`talent-run-bi-product-sense-interview`](skills/data-talent-acquisition-and-interview/references/tasks/talent-run-bi-product-sense-interview.md) | đánh giá audience, decision, semantic model và dashboard trade-offs | BI product-sense assessment | `hiring` | `R3-controlled` / `controlled-path` |
| [`talent-run-candidate-question-session`](skills/data-talent-acquisition-and-interview/references/tasks/talent-run-candidate-question-session.md) | cung cấp consistent, honest role/team context và ghi concerns | candidate-question record | `hiring` | `R3-controlled` / `controlled-path` |
| [`talent-run-data-architecture-interview`](skills/data-talent-acquisition-and-interview/references/tasks/talent-run-data-architecture-interview.md) | đánh giá boundaries, patterns, qualities, governance và migration | architecture-interview assessment | `hiring` | `R3-controlled` / `controlled-path` |
| [`talent-run-data-engineering-interview`](skills/data-talent-acquisition-and-interview/references/tasks/talent-run-data-engineering-interview.md) | đánh giá ingestion, reliability, scale, recovery và cost | data-engineering assessment | `hiring` | `R3-controlled` / `controlled-path` |
| [`talent-run-data-modeling-interview`](skills/data-talent-acquisition-and-interview/references/tasks/talent-run-data-modeling-interview.md) | đánh giá grain, entities, dimensions, history và trade-offs | data-modeling assessment | `hiring` | `R3-controlled` / `controlled-path` |
| [`talent-run-data-science-interview`](skills/data-talent-acquisition-and-interview/references/tasks/talent-run-data-science-interview.md) | đánh giá statistics, experiment/model validity, leakage và business fit | data-science assessment | `hiring` | `R3-controlled` / `controlled-path` |
| [`talent-run-governance-privacy-interview`](skills/data-talent-acquisition-and-interview/references/tasks/talent-run-governance-privacy-interview.md) | đánh giá policy, ownership, classification, access và risk scenarios | governance-privacy assessment | `hiring` | `R3-controlled` / `controlled-path` |
| [`talent-run-hiring-debrief`](skills/data-talent-acquisition-and-interview/references/tasks/talent-run-hiring-debrief.md) | tổng hợp independent evidence, resolve conflicts và avoid groupthink | hiring debrief record | `hiring` | `R3-controlled` / `controlled-path` |
| [`talent-run-leadership-interview`](skills/data-talent-acquisition-and-interview/references/tasks/talent-run-leadership-interview.md) | đánh giá strategy, people, execution, influence và judgment | leadership assessment | `hiring` | `R3-controlled` / `controlled-path` |
| [`talent-run-mlops-interview`](skills/data-talent-acquisition-and-interview/references/tasks/talent-run-mlops-interview.md) | đánh giá lifecycle, deployment, monitoring, rollback và governance | MLOps interview assessment | `hiring` | `R3-controlled` / `controlled-path` |
| [`talent-run-python-interview`](skills/data-talent-acquisition-and-interview/references/tasks/talent-run-python-interview.md) | đánh giá data manipulation, design, testing và maintainability | Python interview assessment | `hiring` | `R3-controlled` / `controlled-path` |
| [`talent-run-recruiter-screen`](skills/data-talent-acquisition-and-interview/references/tasks/talent-run-recruiter-screen.md) | xác minh motivation, logistics, expectations và baseline fit | recruiter-screen record | `hiring` | `R3-controlled` / `controlled-path` |
| [`talent-run-reference-check`](skills/data-talent-acquisition-and-interview/references/tasks/talent-run-reference-check.md) | xác minh role-relevant evidence với consent và consistent questions | reference-check record | `hiring` | `R3-controlled` / `controlled-path` |
| [`talent-run-sql-interview`](skills/data-talent-acquisition-and-interview/references/tasks/talent-run-sql-interview.md) | đánh giá correctness, grain, edge cases, debugging và communication | SQL interview assessment | `hiring` | `R3-controlled` / `controlled-path` |
| [`talent-run-technical-screen`](skills/data-talent-acquisition-and-interview/references/tasks/talent-run-technical-screen.md) | kiểm tra fundamentals và problem-solving theo role | technical-screen assessment | `hiring` | `R3-controlled` / `controlled-path` |
| [`talent-screen-data-resume`](skills/data-talent-acquisition-and-interview/references/tasks/talent-screen-data-resume.md) | đối chiếu evidence với must-have outcomes thay vì keyword matching | resume-screen decision | `hiring` | `R3-controlled` / `controlled-path` |
| [`talent-source-data-candidates`](skills/data-talent-acquisition-and-interview/references/tasks/talent-source-data-candidates.md) | xây search strategy, outreach criteria và source tracking | qualified candidate slate | `hiring` | `R3-controlled` / `controlled-path` |
| [`talent-train-data-interviewer`](skills/data-talent-acquisition-and-interview/references/tasks/talent-train-data-interviewer.md) | đào tạo structured assessment, bias control và candidate experience | interviewer training record | `hiring` | `R2-standard` / `standard-path` |

#### Test / Assure (8 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`talent-audit-assessment-validity`](skills/data-talent-acquisition-and-interview/references/tasks/talent-audit-assessment-validity.md) | đo alignment, reliability và predictive usefulness của assessments | assessment-validity report | `hiring` | `R2-standard` / `standard-path` |
| [`talent-audit-interview-fairness`](skills/data-talent-acquisition-and-interview/references/tasks/talent-audit-interview-fairness.md) | kiểm tra adverse patterns, inconsistent scoring và prohibited signals | interview fairness audit | `hiring` | `R2-standard` / `standard-path` |
| [`talent-audit-question-bank-coverage`](skills/data-talent-acquisition-and-interview/references/tasks/talent-audit-question-bank-coverage.md) | kiểm tra coverage, redundancy, difficulty, bias, leakage và validity của question bank | question-bank coverage audit | `hiring` | `R2-standard` / `standard-path` |
| [`talent-calibrate-interview-panel`](skills/data-talent-acquisition-and-interview/references/tasks/talent-calibrate-interview-panel.md) | dùng anchor responses để chuẩn hóa scoring và probing | panel calibration record | `hiring` | `R2-standard` / `standard-path` |
| [`talent-evaluate-take-home-assignment`](skills/data-talent-acquisition-and-interview/references/tasks/talent-evaluate-take-home-assignment.md) | chấm correctness, reasoning, trade-offs, testing và authorship discussion | take-home assessment | `hiring` | `R3-controlled` / `controlled-path` |
| [`talent-measure-quality-of-hire`](skills/data-talent-acquisition-and-interview/references/tasks/talent-measure-quality-of-hire.md) | liên kết hiring evidence với ramp-up, performance và retention | quality-of-hire report | `hiring` | `R2-standard` / `standard-path` |
| [`talent-score-interview-evidence`](skills/data-talent-acquisition-and-interview/references/tasks/talent-score-interview-evidence.md) | map independent notes tới scorecard trước debrief | evidence-based interview score | `hiring` | `R3-controlled` / `controlled-path` |
| [`talent-validate-workforce-need`](skills/data-talent-acquisition-and-interview/references/tasks/talent-validate-workforce-need.md) | kiểm tra outcome, capacity gap, alternatives, budget và urgency | validated hiring request | `hiring` | `R2-standard` / `standard-path` |

#### Operate / Improve (1 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`talent-optimize-interview-funnel`](skills/data-talent-acquisition-and-interview/references/tasks/talent-optimize-interview-funnel.md) | cải thiện conversion, time, candidate experience và signal quality | optimized interview process | `hiring` | `R2-standard` / `standard-path` |

<a id="skill-data-career-and-interview-coach"></a>

### 29. `data-career-and-interview-coach` — Data Career and Interview Coach

**Claude trigger description:** Build evidence-based Data career systems, persistent cross-skill learner memory, mastery/decay tracking, compact transition context, competency maps, portfolios, interview readiness, remediation and review cycles. Use when prior learning should be reused without reteaching; never infer mastery from exposure or fabricate experience.

**Ownership:** Xây Career OS, career-stage competency map, evidence portfolio, capstone roadmap, technical-writing strategy, ethical visibility, interview readiness, remediation và review cycles.

**Khi nên dùng:** Dùng cho phát triển sự nghiệp Data bền vững, chuẩn bị interview, kiểm chứng career claims hoặc biến learning thành evidence có thể bảo vệ.

**Ranh giới và handoff:** Không bịa kinh nghiệm, hứa title/promotion, đánh đồng self-study với production hay biến public visibility thành proxy cho năng lực.

**Quy mô:** 57 tasks — Plan / Design 16; Build / Deliver 29; Test / Assure 12; Operate / Improve 0.

**Domain references tải khi cần:** `authored-prose-voice.md`, `career-learning-memory.md`, `career-operating-system.md`, `coaching-ethics-and-method.md`, `concept-registry-standard.md`, `interview-knowledge-system.md`, `learning-memory-interoperability.md`, `model-selection.md`, `response-compression.md`, `role-curricula.md`, `solution-option-framing.md`, `system-design-canon.md`, `workflow-runtime-and-evidence-os.md`.

**Templates/assets có thể tái sử dụng:** `architecture-case-study.yaml`, `atomic-task-output.yaml`, `career-content-handoff.yaml`, `career-evidence-portfolio.yaml`, `career-operating-system.yaml`, `career-review.yaml`, `concept-registry.json`, `concept-visual-explainer.yaml`, `content-evidence-return.yaml`, `cross-skill-prerequisite-map.yaml`, `design-option-set.yaml`, `impact-score.yaml`, `interview-knowledge-library.yaml`, `interview-question-dossier.yaml`, `knowledge-coverage-audit.yaml`, `learner-memory.json`, `learner-memory.schema.json`, `learning-event.yaml`, `mock-assessment.yaml`, `offer-evaluation.yaml`, `question-knowledge-map.yaml`, `readiness-profile.yaml`, `remediation-plan.yaml`, `skill-transition-context.json`, `work-entities.yaml`, `work-log-entry.yaml`.

**Scripts:** `build_skill_transition_context.py`, `schedule_topic_review.py`, `validate_concept_registry.py`, `validate_learning_memory.py`.

#### Plan / Design (16 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`career-bootstrap-concept-registry`](skills/data-career-and-interview-coach/references/tasks/career-bootstrap-concept-registry.md) | sinh lô concept key ứng viên từ track map và canon để corpus có chỗ bind ngay | proposed concept key batch | `career-coaching` | `R1-reviewed` / `standard-path` |
| [`career-build-competency-gap-plan`](skills/data-career-and-interview-coach/references/tasks/career-build-competency-gap-plan.md) | ưu tiên gap theo hiring impact, prerequisites và available time | competency-gap plan | `career-development` | `R1-reviewed` / `standard-path` |
| [`career-build-project-story`](skills/data-career-and-interview-coach/references/tasks/career-build-project-story.md) | chuyển project thật thành problem/action/evidence/impact narrative | project story bank | `career-development` | `R1-reviewed` / `standard-path` |
| [`career-build-question-deep-dive`](skills/data-career-and-interview-coach/references/tasks/career-build-question-deep-dive.md) | tạo hồ sơ gồm question analysis, concept theory, practical examples, trade-offs, failure modes, sources và related knowledge | interview question deep-dive dossier | `career-coaching` | `R2-standard` / `standard-path` |
| [`career-clarify-target-data-role`](skills/data-career-and-interview-coach/references/tasks/career-clarify-target-data-role.md) | xác định role, level, company context và timeline mục tiêu | target-role brief | `career-development` | `R1-reviewed` / `standard-path` |
| [`career-create-interview-preparation-plan`](skills/data-career-and-interview-coach/references/tasks/career-create-interview-preparation-plan.md) | lập lịch theory, practice, mocks, feedback và retests | interview preparation plan | `career-coaching` | `R1-reviewed` / `standard-path` |
| [`career-create-targeted-remediation`](skills/data-career-and-interview-coach/references/tasks/career-create-targeted-remediation.md) | giao theory/practice đúng failure pattern | interview remediation plan | `career-coaching` | `R1-reviewed` / `standard-path` |
| [`career-design-answer-strategy`](skills/data-career-and-interview-coach/references/tasks/career-design-answer-strategy.md) | chọn structure, opening, reasoning flow, evidence, STAR/system-design pattern, checks và follow-up handling | interview answer strategy | `career-coaching` | `R1-reviewed` / `standard-path` |
| [`career-design-career-capstone-program`](skills/data-career-and-interview-coach/references/tasks/career-design-career-capstone-program.md) | thiết kế chương trình 12/24 tháng có prerequisites, labs, projects, reviews, recovery buffers và evidence milestones | career capstone program | `career-development` | `R1-reviewed` / `standard-path` |
| [`career-design-concept-visual-explainer`](skills/data-career-and-interview-coach/references/tasks/career-design-concept-visual-explainer.md) | đặc tả visual mental model cho một concept gồm elements, relationships, annotation, common misreading, takeaway và alt text | concept visual explainer spec | `career-coaching` | `R1-reviewed` / `standard-path` |
| [`career-design-technical-writing-strategy`](skills/data-career-and-interview-coach/references/tasks/career-design-technical-writing-strategy.md) | chọn audience, writing formats, themes, cadence và evidence policy để technical writing phục vụ mastery và reputation thật | career technical-writing strategy | `career-development` | `R1-reviewed` / `standard-path` |
| [`career-map-career-stage-competencies`](skills/data-career-and-interview-coach/references/tasks/career-map-career-stage-competencies.md) | mô tả competency, scope, autonomy, judgment, impact và influence theo từng career stage mà không đồng nhất title giữa công ty | career-stage competency map | `career-development` | `R1-reviewed` / `standard-path` |
| [`career-map-cross-skill-prerequisites`](skills/data-career-and-interview-coach/references/tasks/career-map-cross-skill-prerequisites.md) | nối concept, interface, decision rule và failure mode giữa skill đã học với skill kế tiếp | cross-skill prerequisite map | `career-development` | `R1-reviewed` / `standard-path` |
| [`career-map-question-knowledge-dependencies`](skills/data-career-and-interview-coach/references/tasks/career-map-question-knowledge-dependencies.md) | nối question tới core concepts, prerequisites, related concepts, contrasts và follow-up paths | question knowledge dependency map | `career-coaching` | `R1-reviewed` / `standard-path` |
| [`career-plan-ethical-professional-visibility`](skills/data-career-and-interview-coach/references/tasks/career-plan-ethical-professional-visibility.md) | xây kế hoạch contribution, community, mentoring và public expertise không khoe title hoặc biến self-promotion thành proxy cho năng lực | ethical professional-visibility plan | `career-development` | `R1-reviewed` / `standard-path` |
| [`career-register-canonical-concept`](skills/data-career-and-interview-coach/references/tasks/career-register-canonical-concept.md) | cấp và quản lý concept key nối canon, note, topic và competency về một danh tính | canonical concept registry entry | `career-coaching` | `R1-reviewed` / `standard-path` |

#### Build / Deliver (29 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`career-build-architecture-case-study`](skills/data-career-and-interview-coach/references/tasks/career-build-architecture-case-study.md) | bóc tách một kiến trúc public thành constraints, decisions, rejected alternatives, consistency, cost, failure modes và follow-up questions có trích dẫn nguồn | architecture case-study dossier | `career-coaching` | `R2-standard` / `standard-path` |
| [`career-build-career-evidence-portfolio`](skills/data-career-and-interview-coach/references/tasks/career-build-career-evidence-portfolio.md) | lập evidence inventory theo learning, practice, project, production, leadership, business và organizational impact | career evidence portfolio | `career-development` | `R1-reviewed` / `standard-path` |
| [`career-build-career-operating-system`](skills/data-career-and-interview-coach/references/tasks/career-build-career-operating-system.md) | nối current state, target capability, gaps, practice, real work, evidence, feedback và review cadence thành hệ thống phát triển bền vững | career operating system | `career-development` | `R1-reviewed` / `standard-path` |
| [`career-build-interview-knowledge-library`](skills/data-career-and-interview-coach/references/tasks/career-build-interview-knowledge-library.md) | tổ chức question dossiers thành linked, tagged, versioned và Notion-ready knowledge library | interview knowledge library | `career-coaching` | `R2-standard` / `standard-path` |
| [`career-build-offer-evaluation-and-negotiation-plan`](skills/data-career-and-interview-coach/references/tasks/career-build-offer-evaluation-and-negotiation-plan.md) | định giá từng cấu phần offer, đối chiếu market range có trích dẫn, chuẩn bị asks, fallback và walk-away position mà không hứa kết quả lương | offer evaluation and negotiation plan | `career-coaching` | `R2-standard` / `standard-path` |
| [`career-build-skill-transition-context`](skills/data-career-and-interview-coach/references/tasks/career-build-skill-transition-context.md) | nén phần đã mastered thành bridge summary và chỉ mở rộng phần stale, uncertain hoặc trực tiếp cần cho skill mới | bounded skill-transition context pack | `career-development` | `R1-reviewed` / `standard-path` |
| [`career-coach-star-story`](skills/data-career-and-interview-coach/references/tasks/career-coach-star-story.md) | cải thiện situation/task/action/result mà không bịa evidence | refined STAR story | `career-coaching` | `R1-reviewed` / `standard-path` |
| [`career-coach-technical-communication`](skills/data-career-and-interview-coach/references/tasks/career-coach-technical-communication.md) | luyện clarification, assumptions, trade-offs và concise explanation | communication coaching record | `career-coaching` | `R1-reviewed` / `standard-path` |
| [`career-extract-log-entities`](skills/data-career-and-interview-coach/references/tasks/career-extract-log-entities.md) | trích project, tool, skill, metric và outcome từ nhật ký thô, đánh dấu cái nào là suy đoán | extracted work entities | `career-coaching` | `R1-reviewed` / `standard-path` |
| [`career-generate-role-question-set`](skills/data-career-and-interview-coach/references/tasks/career-generate-role-question-set.md) | tạo question set theo role, level, company style và gaps | personalized question set | `career-coaching` | `R1-reviewed` / `standard-path` |
| [`career-initialize-learning-memory`](skills/data-career-and-interview-coach/references/tasks/career-initialize-learning-memory.md) | tạo learner identity, topic taxonomy, baseline, storage pointer, privacy và evidence policy dùng xuyên các role skill | versioned learner-memory baseline | `career-development` | `R1-reviewed` / `standard-path` |
| [`career-log-work-day`](skills/data-career-and-interview-coach/references/tasks/career-log-work-day.md) | ghi nhật ký một ngày làm việc theo mẫu: việc đã làm, vấn đề gặp, cách giải, output và điều học được | daily work log entry | `career-coaching` | `R1-reviewed` / `standard-path` |
| [`career-query-own-history`](skills/data-career-and-interview-coach/references/tasks/career-query-own-history.md) | trả lời câu hỏi về chính công việc đã làm bằng nhật ký và knowledge base của mình, có trích dẫn ngày | grounded history answer | `career-coaching` | `R1-reviewed` / `standard-path` |
| [`career-record-learning-event`](skills/data-career-and-interview-coach/references/tasks/career-record-learning-event.md) | ghi append-only nội dung đã học, practice, artifact, feedback, assessment và source/version mà không tự nâng mastery | learning event record | `career-development` | `R1-reviewed` / `standard-path` |
| [`career-roll-up-work-period`](skills/data-career-and-interview-coach/references/tasks/career-roll-up-work-period.md) | tổng hợp nhật ký một tuần hoặc một tháng thành tường thuật tiến bộ có bằng chứng | work period roll-up | `career-coaching` | `R1-reviewed` / `standard-path` |
| [`career-run-career-review-cycle`](skills/data-career-and-interview-coach/references/tasks/career-run-career-review-cycle.md) | review tuần/tháng/quý/năm dựa trên evidence, feedback, energy, bottleneck và thay đổi bối cảnh | career review record | `career-development` | `R1-reviewed` / `standard-path` |
| [`career-run-interview-retest`](skills/data-career-and-interview-coach/references/tasks/career-run-interview-retest.md) | kiểm tra lại cùng competency bằng scenario mới | retest assessment | `career-coaching` | `R1-reviewed` / `standard-path` |
| [`career-run-mock-analytics-case`](skills/data-career-and-interview-coach/references/tasks/career-run-mock-analytics-case.md) | mô phỏng ambiguous business case từ framing tới recommendation | analytics-case mock assessment | `career-coaching` | `R1-reviewed` / `standard-path` |
| [`career-run-mock-behavioral-interview`](skills/data-career-and-interview-coach/references/tasks/career-run-mock-behavioral-interview.md) | mô phỏng evidence-based behavioral probing | behavioral mock assessment | `career-coaching` | `R1-reviewed` / `standard-path` |
| [`career-run-mock-data-engineering-design`](skills/data-career-and-interview-coach/references/tasks/career-run-mock-data-engineering-design.md) | mô phỏng pipeline/system design, failure và scale questions | DE design mock assessment | `career-coaching` | `R1-reviewed` / `standard-path` |
| [`career-run-mock-data-modeling-interview`](skills/data-career-and-interview-coach/references/tasks/career-run-mock-data-modeling-interview.md) | mô phỏng model design và trade-off defense | data-modeling mock assessment | `career-coaching` | `R1-reviewed` / `standard-path` |
| [`career-run-mock-data-science-interview`](skills/data-career-and-interview-coach/references/tasks/career-run-mock-data-science-interview.md) | mô phỏng statistics, experiment, modeling và validation questions | DS mock assessment | `career-coaching` | `R1-reviewed` / `standard-path` |
| [`career-run-mock-governance-architecture-interview`](skills/data-career-and-interview-coach/references/tasks/career-run-mock-governance-architecture-interview.md) | mô phỏng policy, ownership, architecture và risk trade-offs | DG-architecture mock assessment | `career-coaching` | `R1-reviewed` / `standard-path` |
| [`career-run-mock-leadership-interview`](skills/data-career-and-interview-coach/references/tasks/career-run-mock-leadership-interview.md) | mô phỏng strategy, prioritization, people và conflict scenarios | leadership mock assessment | `career-coaching` | `R1-reviewed` / `standard-path` |
| [`career-run-mock-mlops-interview`](skills/data-career-and-interview-coach/references/tasks/career-run-mock-mlops-interview.md) | mô phỏng deployment, drift, monitoring và incident scenarios | MLOps mock assessment | `career-coaching` | `R1-reviewed` / `standard-path` |
| [`career-run-mock-python-interview`](skills/data-career-and-interview-coach/references/tasks/career-run-mock-python-interview.md) | mô phỏng data coding, testing và code explanation | Python mock assessment | `career-coaching` | `R1-reviewed` / `standard-path` |
| [`career-run-mock-recruiter-screen`](skills/data-career-and-interview-coach/references/tasks/career-run-mock-recruiter-screen.md) | mô phỏng motivation, background, logistics và concise pitch | recruiter-screen mock report | `career-coaching` | `R1-reviewed` / `standard-path` |
| [`career-run-mock-sql-interview`](skills/data-career-and-interview-coach/references/tasks/career-run-mock-sql-interview.md) | mô phỏng SQL live có probing, edge cases và feedback | SQL mock assessment | `career-coaching` | `R1-reviewed` / `standard-path` |
| [`career-track-preparation-progress`](skills/data-career-and-interview-coach/references/tasks/career-track-preparation-progress.md) | theo dõi evidence, scores, consistency và remaining risks | preparation progress report | `career-coaching` | `R1-reviewed` / `standard-path` |

#### Test / Assure (12 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`career-analyze-interview-question`](skills/data-career-and-interview-coach/references/tasks/career-analyze-interview-question.md) | bóc tách interviewer intent, competency, scope, ambiguity, expected depth và failure traps | interview question analysis | `career-coaching` | `R1-reviewed` / `standard-path` |
| [`career-assess-role-readiness`](skills/data-career-and-interview-coach/references/tasks/career-assess-role-readiness.md) | đánh giá theory, practical evidence, communication và gaps theo scorecard | readiness assessment | `career-development` | `R1-reviewed` / `standard-path` |
| [`career-assess-topic-mastery`](skills/data-career-and-interview-coach/references/tasks/career-assess-topic-mastery.md) | đánh giá recall, application, changed-scenario transfer, failure handling, evidence và freshness trước khi đổi mastery state | topic mastery assessment | `career-development` | `R1-reviewed` / `standard-path` |
| [`career-audit-career-claims-evidence`](skills/data-career-and-interview-coach/references/tasks/career-audit-career-claims-evidence.md) | đối chiếu resume, portfolio, promotion hoặc public claims với evidence thật và gắn nhãn self-study/hypothetical đúng mức | career-claim evidence audit | `career-development` | `R1-reviewed` / `standard-path` |
| [`career-audit-knowledge-coverage`](skills/data-career-and-interview-coach/references/tasks/career-audit-knowledge-coverage.md) | đối chiếu question library với canonical concept ID để tìm concept chưa có dossier, prerequisite gap, entry stale và vùng luyện thừa | interview knowledge coverage audit | `career-coaching` | `R1-reviewed` / `standard-path` |
| [`career-certify-interview-readiness`](skills/data-career-and-interview-coach/references/tasks/career-certify-interview-readiness.md) | tổng hợp multi-format evidence và residual gaps | interview-readiness decision | `career-coaching` | `R1-reviewed` / `standard-path` |
| [`career-detect-learning-decay`](skills/data-career-and-interview-coach/references/tasks/career-detect-learning-decay.md) | phát hiện knowledge stale, ít dùng, version drift, evidence hết hạn hoặc confidence giảm và chọn refresh tối thiểu | learning-decay and refresh report | `career-development` | `R1-reviewed` / `standard-path` |
| [`career-evaluate-interview-answer`](skills/data-career-and-interview-coach/references/tasks/career-evaluate-interview-answer.md) | chấm correctness, structure, evidence, depth và communication | answer evaluation | `career-coaching` | `R1-reviewed` / `standard-path` |
| [`career-reconcile-learning-memory`](skills/data-career-and-interview-coach/references/tasks/career-reconcile-learning-memory.md) | hợp nhất learning history từ nhiều repo/skill, giữ lineage, xử lý conflict và ngăn silent status regression | reconciled learner-memory version | `career-development` | `R1-reviewed` / `standard-path` |
| [`career-review-data-portfolio`](skills/data-career-and-interview-coach/references/tasks/career-review-data-portfolio.md) | đánh giá project depth, reproducibility, decisions, impact và presentation | portfolio review | `career-development` | `R1-reviewed` / `standard-path` |
| [`career-review-data-resume`](skills/data-career-and-interview-coach/references/tasks/career-review-data-resume.md) | kiểm tra relevance, evidence, clarity, claims và role alignment | resume review | `career-development` | `R1-reviewed` / `standard-path` |
| [`career-score-work-impact`](skills/data-career-and-interview-coach/references/tasks/career-score-work-impact.md) | chấm mức ảnh hưởng của một mục nhật ký dựa trên chỉ số định lượng và phạm vi người bị ảnh hưởng | impact score record | `career-coaching` | `R1-reviewed` / `standard-path` |

<a id="skill-data-technical-content-and-social"></a>

### 30. `data-technical-content-and-social` — Technical Content and Social

**Claude trigger description:** Build evidence-backed technical series for Facebook in Vietnamese, LinkedIn and Substack in English, and GitHub from research and a canonical article through code, diagrams, channel-native adaptations, QA, publishing and measurement. Use for Airflow, dbt, Spark, Kafka or other technical-content programs.

**Ownership:** Thiết kế và vận hành technical series từ research, knowledge map và canonical article tới code, diagrams, Facebook, LinkedIn, Substack, publishing và measurement.

**Khi nên dùng:** Dùng cho Airflow, dbt, Spark, Kafka hoặc chủ đề kỹ thuật cần một chuỗi nhất quán, có evidence và adaptation riêng theo kênh.

**Ranh giới và handoff:** Không viết social trước technical validation, copy một bài sang mọi kênh, hoặc bịa production experience, benchmark, authority và reader outcomes.

**Quy mô:** 27 tasks — Plan / Design 10; Build / Deliver 7; Test / Assure 8; Operate / Improve 2.

**Domain references tải khi cần:** `demand-driven-content.md`, `external-tool-access.md`, `learning-memory-interoperability.md`, `model-selection.md`, `platform-format-playbooks.md`, `response-compression.md`, `solution-option-framing.md`, `technical-content-quality-standard.md`, `technical-series-method.md`, `universal-professional-series-rules.md`, `workflow-runtime-and-evidence-os.md`.

**Templates/assets có thể tái sử dụng:** `atomic-task-output.yaml`, `content-evidence-return.yaml`, `content-manifest.json`, `content-quality-review.yaml`, `design-option-set.yaml`, `editorial-calendar.yaml`, `episode-brief.yaml`, `series-concept-coverage.yaml`, `social-episode-package.yaml`, `source-pack.yaml`, `technical-series-plan.yaml`.

**Scripts:** `validate_content_manifest.py`.

#### Plan / Design (10 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`content-create-episode-brief`](skills/data-technical-content-and-social/references/tasks/content-create-episode-brief.md) | khóa central question, audience promise, evidence, example, code, diagram, failure và platform adaptations cho một episode | episode content brief | `design-specification` | `R1-reviewed` / `standard-path` |
| [`content-create-technical-carousel-script`](skills/data-technical-content-and-social/references/tasks/content-create-technical-carousel-script.md) | chuyển một mental model thành slide sequence có hook, progressive explanation, visual direction, alt text và takeaway | technical carousel script | `design-specification` | `R1-reviewed` / `standard-path` |
| [`content-create-technical-diagram-brief`](skills/data-technical-content-and-social/references/tasks/content-create-technical-diagram-brief.md) | mô tả message, entities, flow, evidence, labels, alt text và validation cho visual/diagram | technical diagram brief | `design-specification` | `R1-reviewed` / `standard-path` |
| [`content-define-author-voice`](skills/data-technical-content-and-social/references/tasks/content-define-author-voice.md) | rút ra voice traits, rhythm, vocabulary, boundaries và anti-patterns mà không copy câu/ví dụ mẫu | author-voice guide | `design-specification` | `R1-reviewed` / `standard-path` |
| [`content-define-technical-content-strategy`](skills/data-technical-content-and-social/references/tasks/content-define-technical-content-strategy.md) | xác định audience, problem space, positioning, outcomes, channels, constraints và success signals | technical-content strategy brief | `design-specification` | `R1-reviewed` / `standard-path` |
| [`content-design-technical-series`](skills/data-technical-content-and-social/references/tasks/content-design-technical-series.md) | thiết kế narrative arc từ why và mental model tới mechanics, hands-on, production, trade-offs và capstone | technical-series architecture | `design-specification` | `R1-reviewed` / `standard-path` |
| [`content-write-canonical-technical-article`](skills/data-technical-content-and-social/references/tasks/content-write-canonical-technical-article.md) | viết source-of-truth article có first principles, mechanisms, code, trade-offs, failures, limitations và references | canonical technical article | `design-specification` | `R1-reviewed` / `standard-path` |
| [`content-write-facebook-technical-post`](skills/data-technical-content-and-social/references/tasks/content-write-facebook-technical-post.md) | chuyển canonical evidence thành bài tiếng Việt dài, tự nhiên, giàu context, failure/trade-off và câu hỏi thảo luận, đồng thời giữ nguyên technical terms cần độ chính xác | Vietnamese Facebook technical post | `design-specification` | `R1-reviewed` / `standard-path` |
| [`content-write-linkedin-technical-post`](skills/data-technical-content-and-social/references/tasks/content-write-linkedin-technical-post.md) | chuyển một insight kỹ thuật thành bài tiếng Anh chuyên nghiệp, cô đọng, scannable, có evidence và takeaway | English LinkedIn technical post | `design-specification` | `R1-reviewed` / `standard-path` |
| [`content-write-substack-technical-newsletter`](skills/data-technical-content-and-social/references/tasks/content-write-substack-technical-newsletter.md) | viết newsletter tiếng Anh chuyên sâu có subject, preheader, editorial opening, technical walkthrough, exercise, references và next-episode bridge | English Substack technical newsletter | `design-specification` | `R1-reviewed` / `standard-path` |

#### Build / Deliver (7 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`content-build-code-example-package`](skills/data-technical-content-and-social/references/tasks/content-build-code-example-package.md) | tạo runnable teaching/production-oriented examples, tests, setup, expected output và safety notes | validated code example package | `build-change` | `R2-standard` / `standard-path` |
| [`content-build-editorial-calendar`](skills/data-technical-content-and-social/references/tasks/content-build-editorial-calendar.md) | xếp episode, channel, cadence, dependency, review, buffer và publish window | editorial calendar | `build-change` | `R1-reviewed` / `standard-path` |
| [`content-build-series-knowledge-map`](skills/data-technical-content-and-social/references/tasks/content-build-series-knowledge-map.md) | nối prerequisites, core concepts, mechanisms, contrasts, failure modes và follow-on topics | series knowledge map | `build-change` | `R1-reviewed` / `standard-path` |
| [`content-manage-content-backlog`](skills/data-technical-content-and-social/references/tasks/content-manage-content-backlog.md) | ưu tiên topic theo audience value, evidence readiness, dependency, effort, freshness và strategic fit | governed content backlog | `advisory-analysis` | `R0-light` / `fast-path` |
| [`content-package-technical-series-repository`](skills/data-technical-content-and-social/references/tasks/content-package-technical-series-repository.md) | tổ chức roadmap, articles, research, code, tests, diagrams, social variants, status và contribution guidance | technical-series repository package | `build-change` | `R2-standard` / `standard-path` |
| [`content-repurpose-technical-content`](skills/data-technical-content-and-social/references/tasks/content-repurpose-technical-content.md) | biến canonical article thành channel-native variants mà không copy nguyên văn hoặc làm sai claim | cross-channel adaptation package | `advisory-analysis` | `R0-light` / `fast-path` |
| [`content-research-technical-topic`](skills/data-technical-content-and-social/references/tasks/content-research-technical-topic.md) | thu thập official sources, versioned facts, examples, controversies, failure modes và source limitations | technical-topic research pack | `advisory-analysis` | `R0-light` / `fast-path` |

#### Test / Assure (8 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`content-audit-author-voice-and-originality`](skills/data-technical-content-and-social/references/tasks/content-audit-author-voice-and-originality.md) | kiểm tra consistency, AI tells, cliché, copied phrasing, invented authority và channel duplication | voice and originality audit | `governance-assurance` | `R1-reviewed` / `standard-path` |
| [`content-audit-claim-source-traceability`](skills/data-technical-content-and-social/references/tasks/content-audit-claim-source-traceability.md) | nối từng material claim tới source, test, runtime evidence hoặc nhãn opinion/hypothesis | content claim-traceability audit | `governance-assurance` | `R1-reviewed` / `standard-path` |
| [`content-audit-series-concept-coverage`](skills/data-technical-content-and-social/references/tasks/content-audit-series-concept-coverage.md) | map episode đã publish tới canonical concept ID để tách concept đã dạy khỏi concept chỉ nhắc tới, tìm prerequisite hở và trùng lặp | series concept coverage audit | `governance-assurance` | `R1-reviewed` / `standard-path` |
| [`content-measure-series-performance`](skills/data-technical-content-and-social/references/tasks/content-measure-series-performance.md) | đánh giá qualified readership, saves, discussion quality, completion, subscriptions và learning outcomes không chạy theo vanity metrics | series performance review | `advisory-analysis` | `R0-light` / `fast-path` |
| [`content-review-platform-fit`](skills/data-technical-content-and-social/references/tasks/content-review-platform-fit.md) | kiểm tra length, structure, accessibility, CTA, hashtags, links, formatting và native-reader experience theo channel | platform-fit review | `advisory-analysis` | `R0-light` / `fast-path` |
| [`content-review-technical-accuracy`](skills/data-technical-content-and-social/references/tasks/content-review-technical-accuracy.md) | kiểm tra facts, mechanisms, version specificity, abstraction/implementation boundary, examples và limitations | technical accuracy review | `advisory-analysis` | `R0-light` / `fast-path` |
| [`content-test-code-and-diagrams`](skills/data-technical-content-and-social/references/tasks/content-test-code-and-diagrams.md) | chạy code/tests và đối chiếu diagram với implementation hoặc evidence đã khai báo | content artifact validation report | `advisory-analysis` | `R0-light` / `fast-path` |
| [`content-verify-technical-versions`](skills/data-technical-content-and-social/references/tasks/content-verify-technical-versions.md) | xác minh version, environment, behavior khác biệt và ngày hiệu lực trước khi viết claim phụ thuộc thời gian | technical version matrix | `advisory-analysis` | `R0-light` / `fast-path` |

#### Operate / Improve (2 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`content-publish-technical-content`](skills/data-technical-content-and-social/references/tasks/content-publish-technical-content.md) | phát hành đúng approved version, metadata, links, alt text và schedule lên kênh đã được ủy quyền | technical-content publication record | `production-release` | `R3-controlled` / `controlled-path` |
| [`content-refresh-technical-series`](skills/data-technical-content-and-social/references/tasks/content-refresh-technical-series.md) | cập nhật version drift, broken examples, stale claims, links và cross-channel variants rồi ghi changelog | refreshed technical-series release | `advisory-analysis` | `R0-light` / `fast-path` |

<a id="skill-data-personal-project-engineering"></a>

### 31. `data-personal-project-engineering` — Personal Data Project Engineering

**Claude trigger description:** Create differentiated personal Data projects for portfolios, learning or capstones from a problem, dataset, repository, role gap, technology, paper, course, open-source issue, incident, constraint or mixed evidence. Use when Claude must select a project mode, assess a reference repo, transform borrowed inspiration into an attributed user-owned thesis, plan execution, or evaluate portfolio proof.

**Ownership:** Biến vấn đề, user workflow, decision, ý tưởng, nguồn cảm hứng, dataset, repository, role gap, công nghệ, domain, kiến trúc, paper, course, incident hoặc constraints thành một personal data project có thesis và bằng chứng rõ ràng.

**Khi nên dùng:** Dùng khi xây learning/portfolio project, đặc biệt repo-first hoặc inspiration-first: kiểm tra provenance/license, audit hiện trạng, chọn reuse/adapt/replace/drop/build-new, thiết kế khác biệt và lập roadmap/test/evidence.

**Ranh giới và handoff:** Nguồn của người khác phải được attribution trung thực; biến nó thành luận đề và implementation của người dùng bằng khác biệt thực chất, không đổi tên/cosmetic clone hoặc tuyên bố sai rằng ý tưởng gốc hoàn toàn do mình nghĩ ra.

**Quy mô:** 42 tasks — Plan / Design 10; Build / Deliver 26; Test / Assure 6; Operate / Improve 0.

**Domain references tải khi cần:** `adapter-airflow.md`, `adapter-bigquery.md`, `adapter-databricks.md`, `adapter-dbt.md`, `adapter-kafka-flink.md`, `adapter-metadata-catalog.md`, `adapter-microsoft-fabric.md`, `adapter-mlflow-kubeflow.md`, `adapter-power-bi.md`, `adapter-snowflake.md`, `adapter-spark.md`, `external-tool-access.md`, `learning-memory-interoperability.md`, `model-selection.md`, `personal-project-operating-system.md`, `personal-project-quality-standard.md`, `repository-assessment-and-originality.md`, `response-compression.md`, `solution-option-framing.md`, `workflow-runtime-and-evidence-os.md`.

**Templates/assets có thể tái sử dụng:** `atomic-task-output.yaml`, `borrowed-source-transformation.yaml`, `design-option-set.yaml`, `personal-project-manifest.json`, `project-evidence-plan.yaml`, `project-intake.yaml`, `project-option-scorecard.json`, `project-release-review.yaml`, `project-roadmap.yaml`, `project-thesis.yaml`, `repository-assessment.yaml`.

**Scripts:** `audit_repository.py`, `build_portfolio_evidence.py`, `score_project_options.py`, `validate_personal_project_manifest.py`.

#### Plan / Design (10 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`project-define-success-evidence`](skills/data-personal-project-engineering/references/tasks/project-define-success-evidence.md) | nối outcome tới observable proof, tests, demo, artifacts và portfolio claims được phép | project success-evidence contract | `design-specification` | `R1-reviewed` / `standard-path` |
| [`project-design-next-version-evolution`](skills/data-personal-project-engineering/references/tasks/project-design-next-version-evolution.md) | chọn next version từ real gaps/feedback thay vì feature accumulation và giữ backward evidence | evidence-driven project evolution plan | `design-specification` | `R1-reviewed` / `standard-path` |
| [`project-design-project-differentiation`](skills/data-personal-project-engineering/references/tasks/project-design-project-differentiation.md) | tạo khác biệt có ý nghĩa theo problem/user, data/domain, architecture, reliability, governance, performance, operations, evaluation hoặc experience | project differentiation design | `design-specification` | `R1-reviewed` / `standard-path` |
| [`project-plan-execution-and-milestones`](skills/data-personal-project-engineering/references/tasks/project-plan-execution-and-milestones.md) | chuyển thesis thành vertical slices, milestones, task graph, test gates, demo checkpoints và recovery buffers | executable project milestone plan | `design-specification` | `R1-reviewed` / `standard-path` |
| [`project-plan-originality-and-attribution`](skills/data-personal-project-engineering/references/tasks/project-plan-originality-and-attribution.md) | phân loại self-originated/inspired/adapted/forked/replicated/contributed, attribution và giới hạn claim | originality and attribution plan | `design-specification` | `R1-reviewed` / `standard-path` |
| [`project-plan-portfolio-evidence`](skills/data-personal-project-engineering/references/tasks/project-plan-portfolio-evidence.md) | chọn decisions, artifacts, tests, failures, trade-offs và narrative proof cần lưu | portfolio evidence plan | `design-specification` | `R1-reviewed` / `standard-path` |
| [`project-plan-project-maintenance`](skills/data-personal-project-engineering/references/tasks/project-plan-project-maintenance.md) | thiết kế dependency updates, data/version drift, cost monitoring, issue handling, refresh và archival | personal-project maintenance plan | `design-specification` | `R1-reviewed` / `standard-path` |
| [`project-plan-project-roadmap`](skills/data-personal-project-engineering/references/tasks/project-plan-project-roadmap.md) | thiết kế phases, dependencies, milestones, gates, buffers và stop conditions | personal-project roadmap | `design-specification` | `R1-reviewed` / `standard-path` |
| [`project-plan-project-validation-strategy`](skills/data-personal-project-engineering/references/tasks/project-plan-project-validation-strategy.md) | thiết kế static, unit, contract, integration, reconciliation, security, performance, failure, usability và portfolio-proof checks | project validation strategy | `design-specification` | `R1-reviewed` / `standard-path` |
| [`project-select-project-mode`](skills/data-personal-project-engineering/references/tasks/project-select-project-mode.md) | chọn một primary mode và secondary inputs bằng routing rules có giải thích | personal-project mode decision | `design-specification` | `R1-reviewed` / `standard-path` |

#### Build / Deliver (26 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`project-bound-scope-and-constraints`](skills/data-personal-project-engineering/references/tasks/project-bound-scope-and-constraints.md) | khóa time, cost, compute, data access, privacy, license, deployment và maintenance boundary | project scope and constraint contract | `build-change` | `R2-standard` / `standard-path` |
| [`project-build-personal-project-thesis`](skills/data-personal-project-engineering/references/tasks/project-build-personal-project-thesis.md) | khóa problem, target user, decision/outcome, hypothesis, contribution riêng và non-claims | personal-project thesis | `build-change` | `R2-standard` / `standard-path` |
| [`project-build-project-blueprint`](skills/data-personal-project-engineering/references/tasks/project-build-project-blueprint.md) | hợp nhất requirements, architecture, data contracts, interfaces, environments, risks, tests và handoffs trước implementation | implementation-ready project blueprint | `build-change` | `R2-standard` / `standard-path` |
| [`project-build-reuse-adapt-replace-matrix`](skills/data-personal-project-engineering/references/tasks/project-build-reuse-adapt-replace-matrix.md) | phân loại từng component thành reuse/adapt/replace/drop/build-new kèm evidence, reason, risk và validation | repository transformation matrix | `build-change` | `R2-standard` / `standard-path` |
| [`project-classify-starting-point`](skills/data-personal-project-engineering/references/tasks/project-classify-starting-point.md) | phân loại evidence đầu vào, mức sở hữu, độ chắc chắn và project entry mode phù hợp | project starting-point classification | `advisory-analysis` | `R0-light` / `fast-path` |
| [`project-start-architecture-first`](skills/data-personal-project-engineering/references/tasks/project-start-architecture-first.md) | bắt đầu từ architecture pattern hoặc system design question và khóa quality attributes, workload, alternatives, failure và proof | architecture-grounded project charter | `advisory-analysis` | `R0-light` / `fast-path` |
| [`project-start-benchmark-first`](skills/data-personal-project-engineering/references/tasks/project-start-benchmark-first.md) | bắt đầu từ performance/cost/correctness question với baseline, controlled variables, repetitions và limitations | benchmark-driven project plan | `advisory-analysis` | `R0-light` / `fast-path` |
| [`project-start-constraint-first`](skills/data-personal-project-engineering/references/tasks/project-start-constraint-first.md) | bắt đầu từ cost, privacy, latency, offline, scale, resource hoặc regulatory constraint | constraint-driven project direction | `build-change` | `R2-standard` / `standard-path` |
| [`project-start-dataset-first`](skills/data-personal-project-engineering/references/tasks/project-start-dataset-first.md) | bắt đầu từ dataset bằng inspection, profiling, fitness, limitations và viable decision/use-case generation | evidence-grounded project direction | `advisory-analysis` | `R0-light` / `fast-path` |
| [`project-start-decision-first`](skills/data-personal-project-engineering/references/tasks/project-start-decision-first.md) | bắt đầu từ quyết định cần cải thiện, xác định decision owner, inputs, uncertainty, latency và action | decision-grounded project direction | `advisory-analysis` | `R0-light` / `fast-path` |
| [`project-start-domain-first`](skills/data-personal-project-engineering/references/tasks/project-start-domain-first.md) | bắt đầu từ business domain, lập entity/event/process/decision map rồi chọn bounded problem | domain-grounded project direction | `advisory-analysis` | `R0-light` / `fast-path` |
| [`project-start-governance-compliance-first`](skills/data-personal-project-engineering/references/tasks/project-start-governance-compliance-first.md) | bắt đầu từ policy/control/lineage/privacy/quality requirement và biến nó thành verifiable data control | governance-driven project charter | `advisory-analysis` | `R0-light` / `fast-path` |
| [`project-start-hybrid-input-project`](skills/data-personal-project-engineering/references/tasks/project-start-hybrid-input-project.md) | hợp nhất nhiều input nhưng chọn một primary thesis, resolve conflicts và giữ provenance của từng input | hybrid-input project charter | `advisory-analysis` | `R0-light` / `fast-path` |
| [`project-start-idea-first`](skills/data-personal-project-engineering/references/tasks/project-start-idea-first.md) | bắt đầu từ ý tưởng do người dùng tự đề xuất rồi kiểm tra problem, user, feasibility và evidence value | self-idea project charter | `advisory-analysis` | `R0-light` / `fast-path` |
| [`project-start-incident-failure-first`](skills/data-personal-project-engineering/references/tasks/project-start-incident-failure-first.md) | bắt đầu từ failure scenario, tạo reproduction, detection, diagnosis, recovery và prevention evidence | reliability project charter | `incident-recovery` | `R3-controlled` / `controlled-path` |
| [`project-start-inspiration-first`](skills/data-personal-project-engineering/references/tasks/project-start-inspiration-first.md) | bắt đầu từ ý tưởng, bài viết, video, demo hoặc sản phẩm của người khác và chuyển thành thesis riêng có attribution | inspiration-derived project charter | `advisory-analysis` | `R0-light` / `fast-path` |
| [`project-start-integration-first`](skills/data-personal-project-engineering/references/tasks/project-start-integration-first.md) | bắt đầu từ API, event, source/target hoặc interoperability gap và xác định contract, reliability, security, reconciliation | integration-grounded project direction | `advisory-analysis` | `R0-light` / `fast-path` |
| [`project-start-open-source-issue-first`](skills/data-personal-project-engineering/references/tasks/project-start-open-source-issue-first.md) | bắt đầu từ issue thật, kiểm tra maintainer intent, contribution rules, reproducibility và contribution scope | contribution-grounded project plan | `advisory-analysis` | `R0-light` / `fast-path` |
| [`project-start-paper-replication-first`](skills/data-personal-project-engineering/references/tasks/project-start-paper-replication-first.md) | bắt đầu từ paper/experiment bằng hypothesis, environment, dataset, reproduction criteria và extension question | replication-and-extension project plan | `advisory-analysis` | `R0-light` / `fast-path` |
| [`project-start-problem-first`](skills/data-personal-project-engineering/references/tasks/project-start-problem-first.md) | bắt đầu từ pain point có thật, xác minh actor, consequence, current workaround và measurable outcome | problem-grounded project direction | `advisory-analysis` | `R0-light` / `fast-path` |
| [`project-start-repo-first`](skills/data-personal-project-engineering/references/tasks/project-start-repo-first.md) | bắt đầu từ repository bằng provenance/license check, evidence-based audit, baseline execution, improvement matrix và thesis riêng | assessed and differentiated repo-first plan | `advisory-analysis` | `R0-light` / `fast-path` |
| [`project-start-role-competency-first`](skills/data-personal-project-engineering/references/tasks/project-start-role-competency-first.md) | bắt đầu từ target role/gap, chọn project tạo đúng technical, judgment, operations và communication evidence | competency-evidence project direction | `advisory-analysis` | `R0-light` / `fast-path` |
| [`project-start-technology-first`](skills/data-personal-project-engineering/references/tasks/project-start-technology-first.md) | bắt đầu từ công nghệ nhưng buộc chứng minh problem fit, learning value, alternatives và non-toy outcome | technology-grounded project charter | `advisory-analysis` | `R0-light` / `fast-path` |
| [`project-start-tutorial-course-first`](skills/data-personal-project-engineering/references/tasks/project-start-tutorial-course-first.md) | chuyển tutorial/course thành project độc lập bằng cách bỏ scaffold, thay constraints/data và thêm tests, failures, operations | tutorial-to-independent-project plan | `advisory-analysis` | `R0-light` / `fast-path` |
| [`project-start-user-workflow-first`](skills/data-personal-project-engineering/references/tasks/project-start-user-workflow-first.md) | bắt đầu từ workflow của người dùng, tìm friction, handoff, error và automation opportunity | workflow-grounded project direction | `advisory-analysis` | `R0-light` / `fast-path` |
| [`project-transform-borrowed-source-to-original-thesis`](skills/data-personal-project-engineering/references/tasks/project-transform-borrowed-source-to-original-thesis.md) | biến repo hoặc ý tưởng ngoài thành thesis do người dùng sở hữu nhưng vẫn giữ attribution và giới hạn provenance claim | attributed differentiated project thesis | `advisory-analysis` | `R0-light` / `fast-path` |

#### Test / Assure (6 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`project-audit-originality-and-attribution`](skills/data-personal-project-engineering/references/tasks/project-audit-originality-and-attribution.md) | đối chiếu final artifacts với source origins, license, borrowed elements, differentiators và public claims | originality and attribution audit | `governance-assurance` | `R1-reviewed` / `standard-path` |
| [`project-audit-reference-repository`](skills/data-personal-project-engineering/references/tasks/project-audit-reference-repository.md) | nhận xét và đánh giá repo theo purpose, architecture, data flow, runtime, correctness, tests, security, dependencies, CI/CD, observability, performance, cost, documentation, maintainability, activity và license | evidence-backed repository assessment | `governance-assurance` | `R1-reviewed` / `standard-path` |
| [`project-evaluate-portfolio-strength`](skills/data-personal-project-engineering/references/tasks/project-evaluate-portfolio-strength.md) | đánh giá depth, reproducibility, decisions, failures, trade-offs, operations, communication và role evidence | project portfolio-strength assessment | `advisory-analysis` | `R0-light` / `fast-path` |
| [`project-evaluate-project-completion`](skills/data-personal-project-engineering/references/tasks/project-evaluate-project-completion.md) | phân biệt planned, implemented, tested, demonstrated, released và maintained rồi kiểm tra Definition of Done | personal-project completion decision | `advisory-analysis` | `R0-light` / `fast-path` |
| [`project-review-project-readiness`](skills/data-personal-project-engineering/references/tasks/project-review-project-readiness.md) | kiểm tra thesis, rights, data, scope, architecture, dependencies, success evidence, cost và next owner trước build | project readiness decision | `advisory-analysis` | `R0-light` / `fast-path` |
| [`project-score-project-options`](skills/data-personal-project-engineering/references/tasks/project-score-project-options.md) | chấm các phương án theo value, role fit, evidence, differentiation, feasibility, data, testability, operations, risk, cost và sustainability | weighted project option scorecard | `advisory-analysis` | `R0-light` / `fast-path` |

<a id="skill-personal-second-brain-and-knowledge-os"></a>

### 32. `personal-second-brain-and-knowledge-os` — Personal Second Brain and Knowledge OS

**Claude trigger description:** Build or operate a local-first AI Second Brain with 1_Nguon, 2_Wiki, 3_Toi and 4_Ket-Qua layers. Use for Obsidian or local-file knowledge systems, migration from Notion/Sheets/Lark, source ingestion, linked notes, personal context, grounded retrieval, reusable outputs, privacy, backup and freshness.

**Ownership:** Xây và vận hành Bộ Não2 local-first theo 1_Nguon, 2_Wiki, 3_Toi và 4_Ket-Qua, từ migration/capture tới linked knowledge, personal context, retrieval, output, backup và reuse measurement.

**Khi nên dùng:** Dùng khi cần gom tài liệu từ Notion, Sheets, Lark, Obsidian hoặc file local thành hệ thống AI đọc được, tìm lại được và tạo output đúng nguồn lẫn chất riêng.

**Ranh giới và handoff:** Không trộn nguồn với suy luận hoặc chất riêng, không nạp secret mặc định, không coi output AI là Wiki fact và không đánh giá thành công bằng số lượng note.

**Quy mô:** 50 tasks — Plan / Design 12; Build / Deliver 30; Test / Assure 4; Operate / Improve 4.

**Domain references tải khi cần:** `external-tool-access.md`, `knowledge-note-and-lineage-standard.md`, `learning-memory-interoperability.md`, `migration-and-tool-interop.md`, `model-selection.md`, `response-compression.md`, `retrieval-and-output-grounding.md`, `second-brain-operating-system.md`, `second-brain-quality-and-safety.md`, `solution-option-framing.md`, `workflow-runtime-and-evidence-os.md`.

**Templates/assets có thể tái sử dụng:** `atomic-task-output.yaml`, `design-option-set.yaml`, `knowledge-review.yaml`, `migration-plan.yaml`, `output-record.yaml`, `personal-context.yaml`, `retrieval-evaluation.yaml`, `second-brain-manifest.json`, `second-brain-manifest.schema.json`, `source-record.yaml`, `wiki-note.yaml`.

**Scripts:** `build_brain_index.py`, `build_entity_context_graph.py`, `validate_second_brain.py`.

#### Plan / Design (12 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`brain-create-content-from-brain`](skills/personal-second-brain-and-knowledge-os/references/tasks/brain-create-content-from-brain.md) | tạo content từ Wiki và 3_Toi rồi handoff sang content skill khi cần production đa kênh | source-and-voice-grounded content draft | `design-specification` | `R1-reviewed` / `standard-path` |
| [`brain-create-learning-plan-from-brain`](skills/personal-second-brain-and-knowledge-os/references/tasks/brain-create-learning-plan-from-brain.md) | map known/unknown, prerequisites, sources, practice và retrieval checks thành learning plan | second-brain learning plan | `design-specification` | `R1-reviewed` / `standard-path` |
| [`brain-create-project-plan-from-brain`](skills/personal-second-brain-and-knowledge-os/references/tasks/brain-create-project-plan-from-brain.md) | biến prior knowledge, constraints, decisions và evidence gaps thành project direction rồi handoff sang project skill | knowledge-grounded project plan | `design-specification` | `R1-reviewed` / `standard-path` |
| [`brain-create-report-from-brain`](skills/personal-second-brain-and-knowledge-os/references/tasks/brain-create-report-from-brain.md) | tổng hợp report có evidence, limitations, conflicts và next actions từ knowledge vault | grounded report | `design-specification` | `R1-reviewed` / `standard-path` |
| [`brain-define-output-contracts`](skills/personal-second-brain-and-knowledge-os/references/tasks/brain-define-output-contracts.md) | định nghĩa schema, audience, evidence, review, channel, version và done criteria theo từng output | second-brain output contracts | `design-specification` | `R1-reviewed` / `standard-path` |
| [`brain-define-personal-context-contract`](skills/personal-second-brain-and-knowledge-os/references/tasks/brain-define-personal-context-contract.md) | định nghĩa kinh nghiệm, preferences, voice, audiences và work rules được phép dùng cùng provenance | personal-context contract | `design-specification` | `R1-reviewed` / `standard-path` |
| [`brain-define-second-brain-purpose`](skills/personal-second-brain-and-knowledge-os/references/tasks/brain-define-second-brain-purpose.md) | khóa users, decisions, recurring jobs, desired outputs, non-goals và success signals | second-brain purpose contract | `design-specification` | `R1-reviewed` / `standard-path` |
| [`brain-define-source-rights-policy`](skills/personal-second-brain-and-knowledge-os/references/tasks/brain-define-source-rights-policy.md) | định nghĩa ownership, license, allowed processing, quotation, redistribution, retention và deletion | source-rights policy | `design-specification` | `R1-reviewed` / `standard-path` |
| [`brain-design-four-layer-architecture`](skills/personal-second-brain-and-knowledge-os/references/tasks/brain-design-four-layer-architecture.md) | thiết kế 1_Nguon, 2_Wiki, 3_Toi và 4_Ket-Qua với identity, flow và invariants | four-layer brain architecture | `design-specification` | `R1-reviewed` / `standard-path` |
| [`brain-design-retrieval-routing`](skills/personal-second-brain-and-knowledge-os/references/tasks/brain-design-retrieval-routing.md) | map intents và queries tới note types, scopes, freshness, ranking và fallback | retrieval-routing design | `design-specification` | `R1-reviewed` / `standard-path` |
| [`brain-design-vault-taxonomy`](skills/personal-second-brain-and-knowledge-os/references/tasks/brain-design-vault-taxonomy.md) | thiết kế folders, note types, tags, links, IDs, status và naming mà không tạo taxonomy quá sâu | vault taxonomy | `design-specification` | `R1-reviewed` / `standard-path` |
| [`brain-plan-tool-migration`](skills/personal-second-brain-and-knowledge-os/references/tasks/brain-plan-tool-migration.md) | lập kế hoạch export, inventory, transform, verify và cutover từ Notion, Sheets, Lark hoặc tool khác sang local-first vault | reversible knowledge migration plan | `design-specification` | `R1-reviewed` / `standard-path` |

#### Build / Deliver (30 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`brain-backup-second-brain`](skills/personal-second-brain-and-knowledge-os/references/tasks/brain-backup-second-brain.md) | tạo versioned encrypted backup, integrity hashes và recovery instructions cho vault | second-brain backup record | `build-change` | `R2-standard` / `standard-path` |
| [`brain-build-atomic-knowledge-note`](skills/personal-second-brain-and-knowledge-os/references/tasks/brain-build-atomic-knowledge-note.md) | tạo một note cho một concept hoặc decision có stable ID, aliases, status, source links và related notes | atomic knowledge note | `build-change` | `R2-standard` / `standard-path` |
| [`brain-build-audience-context`](skills/personal-second-brain-and-knowledge-os/references/tasks/brain-build-audience-context.md) | ghi audience problems, sophistication, language, objections, desired outcomes và sensitive boundaries | audience-context pack | `build-change` | `R2-standard` / `standard-path` |
| [`brain-build-author-voice-profile`](skills/personal-second-brain-and-knowledge-os/references/tasks/brain-build-author-voice-profile.md) | mô hình hóa tone, rhythm, vocabulary, evidence style, prohibited patterns và channel variations mà không copy mẫu | author-voice profile | `build-change` | `R2-standard` / `standard-path` |
| [`brain-build-canvas-view`](skills/personal-second-brain-and-knowledge-os/references/tasks/brain-build-canvas-view.md) | dựng canvas không gian cho một chủ đề khi quan hệ giữa các note quan trọng hơn thứ tự đọc | canvas view | `build-change` | `R2-standard` / `standard-path` |
| [`brain-build-concept-map`](skills/personal-second-brain-and-knowledge-os/references/tasks/brain-build-concept-map.md) | nối prerequisites, concepts, mechanisms, contrasts, failures và applications | concept map | `build-change` | `R2-standard` / `standard-path` |
| [`brain-build-domain-second-brain`](skills/personal-second-brain-and-knowledge-os/references/tasks/brain-build-domain-second-brain.md) | cấu hình four-layer system cho một domain cụ thể và chỉ nạp rules/references phù hợp | domain-specific second-brain package | `build-change` | `R2-standard` / `standard-path` |
| [`brain-build-grounded-context-pack`](skills/personal-second-brain-and-knowledge-os/references/tasks/brain-build-grounded-context-pack.md) | đóng gói context có source locators, facts, inferences, personal rules, conflicts, omissions và expiry | prompt-ready grounded context pack | `build-change` | `R2-standard` / `standard-path` |
| [`brain-build-map-of-content`](skills/personal-second-brain-and-knowledge-os/references/tasks/brain-build-map-of-content.md) | dựng trang MOC điều hướng một chủ đề thay vì để người đọc dò thư mục | map of content | `build-change` | `R2-standard` / `standard-path` |
| [`brain-build-source-provenance-record`](skills/personal-second-brain-and-knowledge-os/references/tasks/brain-build-source-provenance-record.md) | nối source ID tới origin, locator, snapshot hash, rights, ingestion method và transformations | source provenance record | `build-change` | `R2-standard` / `standard-path` |
| [`brain-build-topic-map`](skills/personal-second-brain-and-knowledge-os/references/tasks/brain-build-topic-map.md) | tạo map-of-content điều hướng một domain bằng questions và relationships thay vì folder dump | topic map | `build-change` | `R2-standard` / `standard-path` |
| [`brain-build-work-rule-library`](skills/personal-second-brain-and-knowledge-os/references/tasks/brain-build-work-rule-library.md) | mã hóa preferences, quality bars, decision rules, templates, exceptions và escalation | personal work-rule library | `build-change` | `R2-standard` / `standard-path` |
| [`brain-capture-source-material`](skills/personal-second-brain-and-knowledge-os/references/tasks/brain-capture-source-material.md) | đưa nguồn mới vào 1_Nguon với stable ID, snapshot, checksum, origin, captured-at và rights | captured source record | `build-change` | `R2-standard` / `standard-path` |
| [`brain-classify-knowledge-domain`](skills/personal-second-brain-and-knowledge-os/references/tasks/brain-classify-knowledge-domain.md) | xác định personal, career, technical, business, marketing, medical, creator hoặc mixed domain cùng risk boundary | knowledge-domain classification | `advisory-analysis` | `R0-light` / `fast-path` |
| [`brain-curate-personal-principles`](skills/personal-second-brain-and-knowledge-os/references/tasks/brain-curate-personal-principles.md) | rút ra principles từ kinh nghiệm thật và gắn scope, counterexample, confidence, review date | personal-principle library | `advisory-analysis` | `R0-light` / `fast-path` |
| [`brain-deduplicate-source-library`](skills/personal-second-brain-and-knowledge-os/references/tasks/brain-deduplicate-source-library.md) | phát hiện exact, near-duplicate, revised và syndicated sources mà không xóa evidence tùy tiện | source deduplication decision | `build-change` | `R2-standard` / `standard-path` |
| [`brain-distill-source-to-wiki-note`](skills/personal-second-brain-and-knowledge-os/references/tasks/brain-distill-source-to-wiki-note.md) | chuyển nguồn thành Wiki note tách source facts, synthesis, inference, uncertainty, applications và citations | source-grounded Wiki note | `build-change` | `R2-standard` / `standard-path` |
| [`brain-extract-multiformat-content`](skills/personal-second-brain-and-knowledge-os/references/tasks/brain-extract-multiformat-content.md) | trích text và structure từ PDF, EPUB, DOCX, HTML, Markdown, CSV và plain text bằng trusted local tools | normalized source extraction | `build-change` | `R2-standard` / `standard-path` |
| [`brain-generate-grounded-output`](skills/personal-second-brain-and-knowledge-os/references/tasks/brain-generate-grounded-output.md) | tạo output từ context pack và gắn material claims tới source hoặc personal-rule IDs | grounded second-brain output | `build-change` | `R2-standard` / `standard-path` |
| [`brain-import-exported-workspace`](skills/personal-second-brain-and-knowledge-os/references/tasks/brain-import-exported-workspace.md) | import bounded exports từ Notion, Google Drive, Sheets, Lark hoặc bookmarks mà giữ links, attachments và source identity | imported workspace package | `build-change` | `R2-standard` / `standard-path` |
| [`brain-inventory-distributed-sources`](skills/personal-second-brain-and-knowledge-os/references/tasks/brain-inventory-distributed-sources.md) | inventory file, URL, export, note, image, video, transcript và spreadsheet theo owner, format, sensitivity, authority và last-used | distributed-source inventory | `advisory-analysis` | `R0-light` / `fast-path` |
| [`brain-link-knowledge-graph`](skills/personal-second-brain-and-knowledge-os/references/tasks/brain-link-knowledge-graph.md) | tạo typed links giữa source, concept, person, project, decision và output đồng thời phát hiện orphan links | linked knowledge graph | `build-change` | `R2-standard` / `standard-path` |
| [`brain-maintain-wikilink-graph`](skills/personal-second-brain-and-knowledge-os/references/tasks/brain-maintain-wikilink-graph.md) | giữ wikilink và backlink hai chiều đúng, phát hiện link chết và trang mồ côi | wikilink graph report | `advisory-analysis` | `R0-light` / `fast-path` |
| [`brain-normalize-source-metadata`](skills/personal-second-brain-and-knowledge-os/references/tasks/brain-normalize-source-metadata.md) | chuẩn hóa title, author, date, source type, canonical URL, edition, tags, sensitivity và authority | normalized source metadata | `build-change` | `R2-standard` / `standard-path` |
| [`brain-process-image-and-diagram-source`](skills/personal-second-brain-and-knowledge-os/references/tasks/brain-process-image-and-diagram-source.md) | mô tả OCR, labels, relationships, uncertainty và link về ảnh gốc thay vì coi visual inference là fact | image knowledge record | `build-change` | `R2-standard` / `standard-path` |
| [`brain-retrieve-task-context`](skills/personal-second-brain-and-knowledge-os/references/tasks/brain-retrieve-task-context.md) | lấy minimum sufficient sources, Wiki notes và 3_Toi rules cho một task với authority, freshness và token budget | routed task context | `advisory-analysis` | `R0-light` / `fast-path` |
| [`brain-reuse-prior-work`](skills/personal-second-brain-and-knowledge-os/references/tasks/brain-reuse-prior-work.md) | tìm, đánh giá freshness và tái sử dụng decisions, templates, examples hoặc artifacts trước khi làm lại | prior-work reuse decision | `build-change` | `R2-standard` / `standard-path` |
| [`brain-run-knowledge-review-cycle`](skills/personal-second-brain-and-knowledge-os/references/tasks/brain-run-knowledge-review-cycle.md) | review inbox, orphans, conflicts, stale notes, personal rules, outputs và improvement actions theo cadence | knowledge review record | `advisory-analysis` | `R0-light` / `fast-path` |
| [`brain-run-privacy-freshness-audit`](skills/personal-second-brain-and-knowledge-os/references/tasks/brain-run-privacy-freshness-audit.md) | kiểm tra secrets, sensitive personal data, permissions, stale notes, broken links, rights và retention | privacy-and-freshness audit | `governance-assurance` | `R3-controlled` / `controlled-path` |
| [`brain-transcribe-audio-video-source`](skills/personal-second-brain-and-knowledge-os/references/tasks/brain-transcribe-audio-video-source.md) | tạo transcript có timestamps, speaker uncertainty, language và media provenance | source-grounded transcript | `build-change` | `R2-standard` / `standard-path` |

#### Test / Assure (4 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`brain-assess-current-knowledge-system`](skills/personal-second-brain-and-knowledge-os/references/tasks/brain-assess-current-knowledge-system.md) | đánh giá nơi lưu, retrieval friction, duplication, portability, AI access, privacy và reuse baseline | current knowledge-system assessment | `advisory-analysis` | `R0-light` / `fast-path` |
| [`brain-audit-output-grounding`](skills/personal-second-brain-and-knowledge-os/references/tasks/brain-audit-output-grounding.md) | kiểm tra mỗi material claim là sourced, inferred, personal hoặc unsupported và xác minh citations | output-grounding audit | `governance-assurance` | `R1-reviewed` / `standard-path` |
| [`brain-measure-reuse-value`](skills/personal-second-brain-and-knowledge-os/references/tasks/brain-measure-reuse-value.md) | đo time-to-find, reuse rate, grounded-output rate, search failure và avoided rework mà không chạy theo note count | second-brain value review | `advisory-analysis` | `R0-light` / `fast-path` |
| [`brain-test-retrieval-quality`](skills/personal-second-brain-and-knowledge-os/references/tasks/brain-test-retrieval-quality.md) | đo relevance, coverage, source authority, freshness, context precision và abstention trên representative query set | retrieval evaluation | `advisory-analysis` | `R0-light` / `fast-path` |

#### Operate / Improve (4 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`brain-operate-capture-inbox`](skills/personal-second-brain-and-knowledge-os/references/tasks/brain-operate-capture-inbox.md) | nhận mọi thứ mới vào một inbox chỉ-đọc và giữ bản gốc bất biến trước khi tổng hợp | capture inbox record | `advisory-analysis` | `R0-light` / `fast-path` |
| [`brain-resolve-knowledge-conflict`](skills/personal-second-brain-and-knowledge-os/references/tasks/brain-resolve-knowledge-conflict.md) | giữ lại competing claims, editions, authority, dates và resolution owner thay vì silent overwrite | knowledge-conflict record | `build-change` | `R2-standard` / `standard-path` |
| [`brain-restore-second-brain`](skills/personal-second-brain-and-knowledge-os/references/tasks/brain-restore-second-brain.md) | phục hồi vào location tách biệt, kiểm tra integrity, links, indexes và representative retrieval trước cutover | verified restore record | `incident-recovery` | `R3-controlled` / `controlled-path` |
| [`brain-retire-stale-knowledge`](skills/personal-second-brain-and-knowledge-os/references/tasks/brain-retire-stale-knowledge.md) | deprecate hoặc archive note/source/output với reason, successor, retention và backlink repair | knowledge retirement record | `production-release` | `R4-critical` / `controlled-path` |

<a id="skill-book-to-knowledge-and-action"></a>

### 33. `book-to-knowledge-and-action` — Book to Knowledge and Action

**Claude trigger description:** Turn books, PDFs, EPUBs, documents or source collections into reusable agent skills, Second Brain packs, career/interview/project systems, curricula, workflows or technical content. Use when structure, frameworks, decisions, citations, copyright controls and progressive loading matter more than a summary.

**Ownership:** Chuyển sách, PDF, EPUB, tài liệu hoặc source collection thành skill, Second Brain pack, Career/Interview/Project system, curriculum, workflow hoặc technical-content blueprint.

**Khi nên dùng:** Dùng khi cần extract frameworks, mental models, principles, techniques, anti-patterns, decision rules và applications với progressive loading và source traceability.

**Ranh giới và handoff:** Không chỉ tóm tắt chương, không bịa tên framework, không copy dài, không biến việc đọc thành production evidence và không publish derived content khi thiếu rights/authority.

**Quy mô:** 45 tasks — Plan / Design 1; Build / Deliver 32; Test / Assure 8; Operate / Improve 4.

**Domain references tải khi cần:** `book-conversion-operating-system.md`, `copyright-security-and-quality.md`, `destination-packs.md`, `knowledge-distillation-and-application.md`, `learning-memory-interoperability.md`, `model-selection.md`, `response-compression.md`, `solution-option-framing.md`, `source-extraction-and-structure.md`, `workflow-runtime-and-evidence-os.md`.

**Templates/assets có thể tái sử dụng:** `application-experiment.yaml`, `atomic-task-output.yaml`, `book-conversion-manifest.json`, `book-conversion-manifest.schema.json`, `book-source-manifest.yaml`, `chapter-note.yaml`, `conversion-evidence.yaml`, `design-option-set.yaml`, `destination-plan.yaml`, `framework-card.yaml`.

**Scripts:** `extract_book_sources.py`, `validate_book_conversion.py`.

#### Plan / Design (1 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`book-map-chapters-and-sections`](skills/book-to-knowledge-and-action/references/tasks/book-map-chapters-and-sections.md) | map table of contents, chapter boundaries, themes, source offsets và destination slices | chapter-source map | `advisory-analysis` | `R0-light` / `fast-path` |

#### Build / Deliver (32 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`book-build-action-experiment-plan`](skills/book-to-knowledge-and-action/references/tasks/book-build-action-experiment-plan.md) | chọn behaviors hoặc decisions để thử, baseline, cadence, observation, stop rule và review | book application experiment | `build-change` | `R2-standard` / `standard-path` |
| [`book-build-agent-skill`](skills/book-to-knowledge-and-action/references/tasks/book-build-agent-skill.md) | compile frameworks, routing, progressive references, assets và guardrails thành Claude-compatible skill | validated book-derived agent skill | `build-change` | `R2-standard` / `standard-path` |
| [`book-build-career-application-pack`](skills/book-to-knowledge-and-action/references/tasks/book-build-career-application-pack.md) | map book concepts tới competencies, deliberate practice, authentic evidence, reflection và career review | book-to-career application pack | `build-change` | `R2-standard` / `standard-path` |
| [`book-build-concept-glossary`](skills/book-to-knowledge-and-action/references/tasks/book-build-concept-glossary.md) | tạo glossary chuẩn hóa aliases, definitions, chapter locators và related concepts | source-linked concept glossary | `build-change` | `R2-standard` / `standard-path` |
| [`book-build-curriculum-pack`](skills/book-to-knowledge-and-action/references/tasks/book-build-curriculum-pack.md) | tạo objectives, prerequisites, theory, examples, labs, assessments, remediation và capstone từ book evidence | book-to-curriculum package | `build-change` | `R2-standard` / `standard-path` |
| [`book-build-decision-cheatsheet`](skills/book-to-knowledge-and-action/references/tasks/book-build-decision-cheatsheet.md) | compile decision trees, trade-off matrices, thresholds, defaults và smells thay vì glossary rút gọn | decision cheatsheet | `build-change` | `R2-standard` / `standard-path` |
| [`book-build-interview-knowledge-pack`](skills/book-to-knowledge-and-action/references/tasks/book-build-interview-knowledge-pack.md) | chuyển frameworks thành question dependencies, answer strategies, examples, trade-offs và novel retests | book-to-interview knowledge pack | `build-change` | `R2-standard` / `standard-path` |
| [`book-build-knowledge-graph`](skills/book-to-knowledge-and-action/references/tasks/book-build-knowledge-graph.md) | nối chapters, prerequisites, concepts, frameworks, techniques, conflicts và applications | book knowledge graph | `build-change` | `R2-standard` / `standard-path` |
| [`book-build-progressive-chapter-pack`](skills/book-to-knowledge-and-action/references/tasks/book-build-progressive-chapter-pack.md) | tạo chapter files on-demand có core idea, frameworks, worked examples, failures, takeaways và links | progressive chapter pack | `build-change` | `R2-standard` / `standard-path` |
| [`book-build-project-application-pack`](skills/book-to-knowledge-and-action/references/tasks/book-build-project-application-pack.md) | biến frameworks thành project hypotheses, decisions, constraints, experiments, artifacts và portfolio proof | book-to-project application pack | `build-change` | `R2-standard` / `standard-path` |
| [`book-build-second-brain-pack`](skills/book-to-knowledge-and-action/references/tasks/book-build-second-brain-pack.md) | đưa source vào 1_Nguon, distilled notes vào 2_Wiki, giữ chỗ cho 3_Toi và output contracts cho 4_Ket-Qua | book-to-second-brain package | `build-change` | `R2-standard` / `standard-path` |
| [`book-build-source-manifest`](skills/book-to-knowledge-and-action/references/tasks/book-build-source-manifest.md) | ghi source/edition hash, rights, extraction method, locators, transformations và limitations | book source manifest | `build-change` | `R2-standard` / `standard-path` |
| [`book-build-technical-content-series`](skills/book-to-knowledge-and-action/references/tasks/book-build-technical-content-series.md) | chuyển source map thành canonical technical series và handoff evidence-bound production sang content skill | book-to-content series blueprint | `build-change` | `R2-standard` / `standard-path` |
| [`book-build-topic-index`](skills/book-to-knowledge-and-action/references/tasks/book-build-topic-index.md) | map natural-language topics và questions tới chapter, framework và destination files | progressive topic index | `build-change` | `R2-standard` / `standard-path` |
| [`book-build-workflow-checklists`](skills/book-to-knowledge-and-action/references/tasks/book-build-workflow-checklists.md) | compile procedures, gates, exceptions, checklists và evidence requirements cho công việc lặp lại | book-derived workflow pack | `build-change` | `R2-standard` / `standard-path` |
| [`book-classify-conversion-purpose`](skills/book-to-knowledge-and-action/references/tasks/book-classify-conversion-purpose.md) | chọn primary destination là skill, second brain, career, interview, project, curriculum, workflow, content hoặc mixed có one primary output | book-conversion purpose decision | `advisory-analysis` | `R0-light` / `fast-path` |
| [`book-compare-multiple-books`](skills/book-to-knowledge-and-action/references/tasks/book-compare-multiple-books.md) | so sánh terminology, assumptions, frameworks, agreements, contradictions và applicability qua nhiều nguồn | multi-book comparison | `advisory-analysis` | `R0-light` / `fast-path` |
| [`book-estimate-conversion-budget`](skills/book-to-knowledge-and-action/references/tasks/book-estimate-conversion-budget.md) | ước tính extraction quality, token/time/cost, chapter budget, destination files và stop conditions | conversion budget estimate | `advisory-analysis` | `R0-light` / `fast-path` |
| [`book-extract-antipatterns`](skills/book-to-knowledge-and-action/references/tasks/book-extract-antipatterns.md) | trích what-not-to-do, detection signals, why-it-fails, exceptions và remedies | anti-pattern library | `build-change` | `R2-standard` / `standard-path` |
| [`book-extract-decision-rules`](skills/book-to-knowledge-and-action/references/tasks/book-extract-decision-rules.md) | trích if/then/because logic, thresholds, defaults, tells và escalation | decision-rule library | `build-change` | `R2-standard` / `standard-path` |
| [`book-extract-examples-and-cases`](skills/book-to-knowledge-and-action/references/tasks/book-extract-examples-and-cases.md) | synthesize worked examples, context, decision, outcome và limitation với bounded quotation | example-and-case pack | `build-change` | `R2-standard` / `standard-path` |
| [`book-extract-frameworks`](skills/book-to-knowledge-and-action/references/tasks/book-extract-frameworks.md) | trích named frameworks với exact name, purpose, conditions, steps, failure modes và source locators | framework cards | `build-change` | `R2-standard` / `standard-path` |
| [`book-extract-mental-models`](skills/book-to-knowledge-and-action/references/tasks/book-extract-mental-models.md) | trích thinking models và nêu when-to-use, limits, contrasts và source evidence | mental-model library | `build-change` | `R2-standard` / `standard-path` |
| [`book-extract-principles`](skills/book-to-knowledge-and-action/references/tasks/book-extract-principles.md) | chuyển principles thành decision-guiding rules mà không làm mất qualifier hoặc scope | principle library | `build-change` | `R2-standard` / `standard-path` |
| [`book-extract-source-text`](skills/book-to-knowledge-and-action/references/tasks/book-extract-source-text.md) | trích text local-first bằng format-aware tools, giữ source boundaries và không cài dependency ngoài khi chưa được phép | extracted source corpus | `build-change` | `R2-standard` / `standard-path` |
| [`book-extract-technical-artifacts`](skills/book-to-knowledge-and-action/references/tasks/book-extract-technical-artifacts.md) | trích code, commands, formulas, schemas và tables với syntax/version/source verification | technical-artifact pack | `build-change` | `R2-standard` / `standard-path` |
| [`book-extract-techniques`](skills/book-to-knowledge-and-action/references/tasks/book-extract-techniques.md) | trích repeatable techniques, inputs, procedure, outputs, trade-offs và evidence | technique library | `build-change` | `R2-standard` / `standard-path` |
| [`book-fold-into-existing-system`](skills/book-to-knowledge-and-action/references/tasks/book-fold-into-existing-system.md) | merge source/version mới vào skill hoặc Second Brain mà preserve IDs, backlinks, conflicts và prior evidence | governed fold-in release | `build-change` | `R2-standard` / `standard-path` |
| [`book-identify-content-type`](skills/book-to-knowledge-and-action/references/tasks/book-identify-content-type.md) | phân loại technical, text-heavy, academic, reference, visual hoặc mixed để chọn extraction và depth | content-type decision | `advisory-analysis` | `R0-light` / `fast-path` |
| [`book-inventory-source-collection`](skills/book-to-knowledge-and-action/references/tasks/book-inventory-source-collection.md) | inventory books, chapters, PDFs, EPUBs, notes và companion artifacts theo source identity và edition | book-source inventory | `advisory-analysis` | `R0-light` / `fast-path` |
| [`book-merge-source-versions`](skills/book-to-knowledge-and-action/references/tasks/book-merge-source-versions.md) | reconcile duplicate, revised, translated và companion sources theo authority và stable identity | source-version merge decision | `build-change` | `R2-standard` / `standard-path` |
| [`book-update-from-new-edition`](skills/book-to-knowledge-and-action/references/tasks/book-update-from-new-edition.md) | diff editions, classify changed/added/removed claims, update impacted packs và retain prior version | new-edition update release | `build-change` | `R2-standard` / `standard-path` |

#### Test / Assure (8 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`book-assess-source-rights`](skills/book-to-knowledge-and-action/references/tasks/book-assess-source-rights.md) | kiểm tra ownership, license, edition, quotation, processing, storage và publication rights trước conversion | source-rights decision | `advisory-analysis` | `R0-light` / `fast-path` |
| [`book-audit-copyright-and-privacy`](skills/book-to-knowledge-and-action/references/tasks/book-audit-copyright-and-privacy.md) | kiểm tra quotation length, redistribution, internal/confidential content, personal data và public/private boundary | copyright-and-privacy audit | `governance-assurance` | `R3-controlled` / `controlled-path` |
| [`book-audit-source-traceability`](skills/book-to-knowledge-and-action/references/tasks/book-audit-source-traceability.md) | sample và đối chiếu frameworks, rules, examples, technical artifacts với source locators và hashes | book traceability audit | `governance-assurance` | `R1-reviewed` / `standard-path` |
| [`book-detect-hallucinated-frameworks`](skills/book-to-knowledge-and-action/references/tasks/book-detect-hallucinated-frameworks.md) | phát hiện invented names, merged concepts, missing qualifiers, false quotations và unsupported author voice | hallucination findings | `advisory-analysis` | `R0-light` / `fast-path` |
| [`book-measure-knowledge-transfer`](skills/book-to-knowledge-and-action/references/tasks/book-measure-knowledge-transfer.md) | đo recall, application, decision quality, artifact quality và changed-scenario transfer thay vì file count | knowledge-transfer review | `advisory-analysis` | `R0-light` / `fast-path` |
| [`book-test-retrieval-and-application`](skills/book-to-knowledge-and-action/references/tasks/book-test-retrieval-and-application.md) | dùng unseen queries và scenarios để đo routing, citation, abstention và framework application | book knowledge evaluation | `advisory-analysis` | `R0-light` / `fast-path` |
| [`book-validate-derived-skill`](skills/book-to-knowledge-and-action/references/tasks/book-validate-derived-skill.md) | kiểm tra Claude format, triggering, progressive disclosure, broken links, token path và task behavior | derived-skill validation report | `advisory-analysis` | `R0-light` / `fast-path` |
| [`book-verify-extraction-quality`](skills/book-to-knowledge-and-action/references/tasks/book-verify-extraction-quality.md) | sample đầu/giữa/cuối, chapter boundaries, OCR, code/tables và missing-page signals | extraction quality report | `advisory-analysis` | `R0-light` / `fast-path` |

#### Operate / Improve (4 tasks)

| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |
|---|---|---|---|---|
| [`book-publish-derived-skill`](skills/book-to-knowledge-and-action/references/tasks/book-publish-derived-skill.md) | publish exact scanned version chỉ khi rights và explicit public/private authority hợp lệ | derived-skill publication record | `production-release` | `R3-controlled` / `controlled-path` |
| [`book-recover-document-structure`](skills/book-to-knowledge-and-action/references/tasks/book-recover-document-structure.md) | phục hồi headings, chapters, code, tables, formula, figure references và page/section locators | recovered document structure | `build-change` | `R2-standard` / `standard-path` |
| [`book-resolve-author-claims`](skills/book-to-knowledge-and-action/references/tasks/book-resolve-author-claims.md) | phân biệt author claim, cited evidence, illustrative example, synthesis, disagreement và uncertainty | author-claim evidence map | `build-change` | `R2-standard` / `standard-path` |
| [`book-retire-derived-knowledge`](skills/book-to-knowledge-and-action/references/tasks/book-retire-derived-knowledge.md) | deprecate stale framework hoặc generated pack với reason, successor, archive và backlink repair | derived-knowledge retirement record | `production-release` | `R4-critical` / `controlled-path` |

## 6. Cách chọn skill/task

Người dùng chỉ cần mô tả outcome. Claude tự route theo các quy tắc:

1. Nếu yêu cầu có nhiều role/deliverable hoặc cần dựng lại repository, dùng `data-department-orchestrator`.
2. Nếu deliverable đã rõ, chọn role sở hữu deliverable đó; không chọn chỉ vì job title xuất hiện trong prompt.
3. Chọn catalog theo intent hiện tại: design khác build, test khác deploy.
4. Chọn đúng một atomic task theo primary deliverable và đọc contract đầy đủ.
5. Hoàn thành hoặc handoff task hiện tại trước khi chuyển sang task tiếp theo.
6. Không tuyên bố execution/test/approval thành công nếu chưa có evidence.

Prompt kiểm tra routing:

```text
Hãy phân tích yêu cầu và báo trước khi làm:
- primary role skill
- current atomic task ID
- primary deliverable
- lifecycle profile, risk tier và execution path
- blockers/assumptions và acceptance criteria.
Sau đó thực hiện task hiện tại, test, báo evidence, approval status, residual risks và next owner.
```

Tổng kiểm: **33 skills / 865 tasks** đã được liệt kê, không thiếu và không trùng ownership trong catalog này.
