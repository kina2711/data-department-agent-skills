# Data Department Operating Model v2

## 1. Mục tiêu

Chuẩn hóa toàn bộ Delivery OS và People OS theo một lifecycle có evidence, test và ownership rõ ràng, đồng thời điều chỉnh độ nặng quy trình theo rủi ro.

```text
Intake
  → Plan
  → Assess
  → Design
  → Execute
  → Test
  → Review / Approve
  → Release / Handoff
  → Monitor / Improve
```

Không coi “đã viết xong” là hoàn thành. Một artifact chỉ hoàn thành khi đúng scope, có test evidence, đạt gate cần thiết, có owner tiếp nhận và residual risk được ghi nhận.

## 2. Stage model

| Stage | Câu hỏi phải trả lời | Output tối thiểu | Exit gate |
|---|---|---|---|
| Intake | Đây là nhiệm vụ gì, deliverable nào, role nào sở hữu? | Routing decision | G0 Correct route |
| Plan | Outcome, scope, owner, consumers, deadline và acceptance là gì? | Task/workflow plan | G1 Definition of Ready |
| Assess | Hiện trạng, baseline, evidence, dependency và risk là gì? | Assessment baseline | G2 Evidence sufficient |
| Design | Cách làm nhỏ nhất, reversible, testable là gì? | Versioned design/spec | G3 Design accepted |
| Execute | Artifact được tạo/thay đổi ở đâu và bằng checkpoint nào? | Candidate artifact | G4 Execution complete |
| Test | Correctness, semantics, integration, security và recovery đã chứng minh chưa? | Test evidence | G5 Mandatory tests pass |
| Review/Approve | Ai có authority chấp nhận version/scope này? | Review and approval record | G6 Approved when required |
| Release/Handoff | Kết quả được deploy/publish/chuyển owner an toàn chưa? | Released artifact/handoff | G7 Release verified |
| Monitor/Improve | Outcome có ổn định và bài học đã đóng loop chưa? | Monitoring/improvement record | G8 Stabilized/learned |

## 3. Definition of Ready

Một task không đi vào execution nếu thiếu một yếu tố có thể làm thay đổi semantics, risk, scope, test strategy hoặc acceptance:

- Primary deliverable và consumer rõ ràng.
- Primary owner và approver khi cần.
- Scope in/out và target environment.
- Input, dependency và quyền truy cập tối thiểu.
- Acceptance criteria đo được.
- Lifecycle profile và risk tier.
- Evidence plan và test strategy.
- Rollback/recovery cho controlled work.

Fast-path R0 có thể gộp Plan và Assess trong một bước, nhưng không được bỏ evidence hoặc verification.

## 4. Definition of Done

- Deliverable tồn tại và có version.
- Acceptance criteria được trace tới test results.
- Mandatory tests pass; exception có owner và expiry.
- Approval đúng version/target/scope được ghi nhận.
- Security, privacy, semantic, accessibility, operability và cost checks đã chạy khi áp dụng.
- Controlled work có rollback/recovery và monitoring evidence.
- Documentation, ownership, residual risk và next task đã handoff.
- Trạng thái phân biệt rõ draft, validated, approved, released, monitored, blocked và failed.

## 5. Risk-adaptive execution

| Tier | Ví dụ | Path | Controls |
|---|---|---|---|
| R0 Light | Read-only lookup, bounded analysis | Fast | Evidence + self-check |
| R1 Reviewed | Design, theory lesson, documentation | Standard | Peer/domain review |
| R2 Standard | Non-prod build, assessment, onboarding task | Standard | Automated/practical tests + owner review |
| R3 Controlled | Production deploy, access, PII, external publishing | Controlled | Independent tests + approval + rollback + monitoring |
| R4 Critical | Destructive delete, breach, certified KPI, regulated decision | Controlled | Segregated approval + strongest evidence + rehearsed recovery + audit |

Deadline không được dùng để hạ risk tier. Scope thay đổi phải reclassify trước khi tiếp tục.

## 6. Lifecycle profiles

| Profile | Optimize for | Test focus |
|---|---|---|
| Advisory analysis | Decision quality và uncertainty | Independent calculation, sensitivity, semantic review |
| Design/specification | Completeness và implementability | Traceability, scenarios, failure paths |
| Build/change | Correctness và reversibility | Unit, contract, integration, reconciliation, regression |
| Production release | Safe change | Preflight, live smoke, reconciliation, stabilization |
| Incident/recovery | Time-to-safe-recovery | Health, correctness, recurrence prevention |
| Governance assurance | Authority và evidence | Sampling, control effectiveness, exceptions |
| Learning | Competency transfer | Formative, summative, practical, retention |
| Onboarding | Safe time-to-productivity | Access, knowledge, guided and independent work |
| Hiring | Valid fair signal | Anchored score, job sample, inter-rater and fairness |
| Career coaching | Authentic readiness | Baseline mock, remediation, novel-scenario retest |

## 7. Test architecture

### Data and software delivery

1. Static/schema validation
2. Unit/business-rule tests
3. Contract and compatibility tests
4. Integration/end-to-end tests
5. Data-quality and reconciliation tests
6. Security/privacy/performance/resilience tests
7. UAT, release smoke and monitoring validation

Không phải task nào cũng cần cả bảy lớp. Task contract chọn các lớp theo profile/risk; R3/R4 cần independent verification cho critical acceptance.

### Learning

1. Baseline diagnostic
2. Formative checks trong lúc học
3. Summative theory test
4. Authentic practical assessment
5. Novel-scenario retest sau remediation
6. Workplace transfer check

Attendance không phải competency evidence.

### Onboarding

1. Access/environment check
2. Policy/security knowledge check
3. Domain/tool exercise
4. Guided first-task review
5. Independent work-sample assessment
6. 7/30/60/90 integration checkpoints

### Hiring

1. Scorecard coverage review
2. Structured screen
3. Job-relevant work sample
4. Role-specific technical/behavioral evidence
5. Independent anchored scoring
6. Calibrated debrief
7. Fairness and validity audit

## 8. Approval matrix

| Action | Required authority |
|---|---|
| Internal reversible draft | Artifact owner/peer reviewer |
| Business semantic baseline | Business/data owner |
| Production deployment/publish | Service/product owner |
| Access, secrets, sensitive sharing | Security/privacy/data owner |
| Delete/retire/destructive backfill | Data owner plus governance/privacy authority |
| Certified KPI/policy | Governance authority and business owner |
| Model promotion/high-risk AI | Model/service owner plus risk approver |
| Hiring decision | Hiring manager under HR policy |
| Competency certification | Calibrated assessor and program owner |

Approval không thay thế test và hết hiệu lực khi artifact/scope thay đổi materially.

## 9. Workflow optimization

### Giảm thời gian chờ

- Chạy profiling, security review và dependency discovery song song khi chỉ đọc.
- Chuẩn bị test data, environment và approval package trong lúc build nếu dependencies đã ổn định.
- Tự động hóa deterministic checks; human chỉ tập trung semantics, judgment, exception và authority.
- Reuse verified company context, evidence và approved artifacts bằng version/provenance.

### Giảm rework

- Chặn execution tại Definition of Ready nếu KPI, grain, scope hoặc ownership chưa rõ.
- Test contract và critical business rules trước khi build phần presentation.
- Dùng small batch, feature flag, canary, shadow hoặc dual-run cho controlled change.
- Lock independent interview scores trước debrief; không sửa evidence theo ý kiến nhóm.
- Diagnose learning/onboarding gap trước khi giao thêm nội dung chung chung.

### WIP policy

- Mỗi atomic task có một primary owner và một primary deliverable.
- Mỗi owner không mở thêm controlled task khi task hiện tại chưa qua Test hoặc được handoff chính thức.
- Orchestrator giới hạn parallelism theo shared mutable systems, reviewer capacity và approval bandwidth.
- Blocked work phải ghi blocker, owner và next check; không giữ trạng thái “in progress” giả.

## 10. Status state machine

```text
draft
→ ready
→ assessing
→ designed
→ executing
→ testing
→ validated
→ awaiting-approval
→ approved
→ releasing
→ released
→ monitoring
→ complete

Any stage → blocked | failed | rolled-back
```

## 11. Metrics để tối ưu hệ thống

### Flow

- Lead time và cycle time theo profile/risk
- Queue/approval wait time
- Flow efficiency
- WIP và task aging
- First-pass yield
- Rework rate

### Quality

- Escaped defects/incidents
- Reconciliation failure rate
- Rollback rate
- Test coverage theo criticality
- Exception aging

### Business

- Time-to-decision
- Adoption và decision impact
- Data product SLO và stakeholder satisfaction
- Cost per delivered/maintained outcome

### People OS

- Learning gain, retention và workplace transfer
- Time-to-access, time-to-first-value và onboarding readiness
- Interview reliability, fairness, candidate experience và quality of hire
- Coaching score trend và novel-scenario pass rate

Không tối ưu một metric đơn lẻ. Ví dụ giảm cycle time nhưng tăng escaped defects là thất bại.

## 12. Continuous improvement loop

1. Thu flow, quality, business và people evidence.
2. Xác định bottleneck có impact lớn nhất.
3. Form một hypothesis cải tiến nhỏ.
4. Thử nghiệm trên bounded workflow/cohort.
5. So baseline và guardrails.
6. Standardize khi tốt hơn; rollback khi không tốt.
7. Version lifecycle, templates, curricula và interview loop.
