# Hướng dẫn import và sử dụng Data Department Skills với Claude Code

> Áp dụng cho `data-department-agent-skills` v3.1.0 · 32 role skills · 802 atomic workflows · Windows PowerShell.

## Mục lục

- [1. Chọn hình thức import](#1-chọn-hình-thức-import)
- [2. Điều kiện và file phát hành](#2-điều-kiện-và-file-phát-hành)
- [3. Cách A — thử bằng local plugin](#3-cách-a--thử-bằng-local-plugin)
- [4. Cách B — import vào một project](#4-cách-b--import-vào-một-project)
- [5. Cách C — import cho user](#5-cách-c--import-cho-user)
- [6. Xác minh cài đặt](#6-xác-minh-cài-đặt)
- [7. Cơ chế sử dụng và routing](#7-cơ-chế-sử-dụng-và-routing)
- [8. Prompt mẫu](#8-prompt-mẫu)
- [9. Quy trình chuẩn khi có đề bài và repository mẫu](#9-quy-trình-chuẩn-khi-có-đề-bài-và-repository-mẫu)
- [10. Company context và quyền](#10-company-context-và-quyền)
- [11. Cập nhật, gỡ và phục hồi](#11-cập-nhật-gỡ-và-phục-hồi)
- [12. Troubleshooting](#12-troubleshooting)

## 1. Chọn hình thức import

| Hình thức | Phạm vi | Skill command | Nên dùng khi |
|---|---|---|---|
| Local plugin | Phiên Claude được mở với `--plugin-dir` | `/data-department-agent-skills:data-engineering` | Thử nghiệm bản phát hành mà không chép vào project/user skills |
| Project skills | Một repository | `/data-engineering` | Team muốn commit và dùng chung skill theo project |
| User skills | Mọi project của user | `/data-engineering` | Cá nhân dùng bộ skill thường xuyên trên nhiều repository |

Khuyến nghị:

1. Thử **local plugin** trước.
2. Khi đã xác nhận routing đúng, dùng **Project skills** cho dự án thật.
3. Chỉ dùng **User skills** nếu muốn toàn bộ 32 skills khả dụng ở mọi project.

Claude Code tìm skill theo các vị trí chuẩn:

```text
Project: <repo>\.claude\skills\<skill-name>\SKILL.md
User:    %USERPROFILE%\.claude\skills\<skill-name>\SKILL.md
Plugin:  <plugin-root>\skills\<skill-name>\SKILL.md
```

Lưu ý precedence: managed/enterprise có ưu tiên cao nhất; personal skill có thể che project skill cùng tên. Plugin skill luôn có namespace nên không xung đột trực tiếp với project/user skill.

## 2. Điều kiện và file phát hành

### 2.1 Kiểm tra Claude Code

```powershell
claude --version
```

Bản này đã được native-test với Claude Code `2.1.206`. Claude Code thay đổi nhanh; nếu dùng phiên bản khác, hãy chạy lại các bước validation ở phần 6.

### 2.2 Các file cần biết

```text
C:\PROJECT\data-department\
├── dist\data-department-claude-plugin-v3.1.0.zip
├── dist\claude-plugin\data-department-agent-skills\
├── skills\
├── tools\install_claude_skills.ps1
├── tools\validate_claude_skills.py
├── 01_CHI_TIET_TOAN_BO_SKILL_VA_TASK.md
└── 02_HUONG_DAN_IMPORT_VA_SU_DUNG_CLAUDE.md
```

### 2.3 Kiểm tra checksum plugin ZIP

```powershell
Get-FileHash `
  "C:\PROJECT\data-department\dist\data-department-claude-plugin-v3.1.0.zip" `
  -Algorithm SHA256
```

SHA-256 bản v3.1.0:

```text
8D95F1342CAD38E3B5E501EC26DE2B667073E81F8214BA38106BE995C43433D0
```

Nếu hash khác, không mặc định file là cùng bản phát hành; xác minh lại nguồn hoặc build lại package.

## 3. Cách A — thử bằng local plugin

`--plugin-dir` cần trỏ tới **thư mục plugin đã giải nén**, không trỏ thẳng tới ZIP.

### 3.1 Dùng thư mục staged có sẵn

```powershell
$pluginRoot = "C:\PROJECT\data-department\dist\claude-plugin\data-department-agent-skills"
$workRepo = "C:\path\to\your-project"

Set-Location $workRepo
claude --plugin-dir $pluginRoot
```

### 3.2 Dùng ZIP được chuyển sang máy khác

```powershell
$zipPath = "C:\Downloads\data-department-claude-plugin-v3.1.0.zip"
$pluginRoot = "C:\Tools\data-department-agent-skills-v3.1.0"

Expand-Archive `
  -LiteralPath $zipPath `
  -DestinationPath $pluginRoot

claude plugin validate --strict $pluginRoot

Set-Location "C:\path\to\your-project"
claude --plugin-dir $pluginRoot
```

Sau khi giải nén, cấu trúc đúng là:

```text
data-department-agent-skills-v3.1.0\
├── .claude-plugin\plugin.json
└── skills\
    ├── data-department-orchestrator\SKILL.md
    ├── data-engineering\SKILL.md
    └── ...
```

### 3.3 Gọi plugin skill

Plugin skill luôn có namespace:

```text
/data-department-agent-skills:data-department-orchestrator
/data-department-agent-skills:data-engineering
/data-department-agent-skills:analytics-engineering
/data-department-agent-skills:data-academy-and-curriculum
/data-department-agent-skills:personal-second-brain-and-knowledge-os
/data-department-agent-skills:book-to-knowledge-and-action
```

Ví dụ:

```text
/data-department-agent-skills:data-engineering

Build pipeline lấy orders từ API có pagination và rate limit,
chạy incremental mỗi giờ, rerun không duplicate và có reconciliation.
```

## 4. Cách B — import vào một project

Project scope là lựa chọn phù hợp nhất khi skill là một phần của cách team phát triển repository.

### 4.1 Cài đặt

```powershell
Set-Location "C:\PROJECT\data-department"

.\tools\install_claude_skills.ps1 `
  -Scope Project `
  -ProjectPath "C:\path\to\your-project"
```

Installer chép từng skill vào:

```text
C:\path\to\your-project\.claude\skills\<skill-name>\
```

Sau đó mở Claude từ repository hoặc thư mục con:

```powershell
Set-Location "C:\path\to\your-project"
claude
```

### 4.2 Gọi project skill

Không dùng plugin namespace:

```text
/data-department-orchestrator
/data-engineering
/business-intelligence
/data-career-and-interview-coach
```

### 4.3 Commit cho team

Sau khi review, có thể version-control `.claude/skills/` cùng repository. Trước khi commit:

```powershell
git status --short
git diff -- .claude/skills
```

Không commit secrets, credentials, raw PII hoặc company context không được phép chia sẻ.

## 5. Cách C — import cho user

User scope cài vào `%USERPROFILE%\.claude\skills`:

```powershell
Set-Location "C:\PROJECT\data-department"
.\tools\install_claude_skills.ps1 -Scope User
```

Sau đó mở Claude ở bất kỳ project nào:

```powershell
Set-Location "C:\path\to\any-project"
claude
```

Gọi skill không có namespace:

```text
/data-analysis
/data-science
/mlops
```

Không nên cài User scope nếu project đang có các skill cùng tên nhưng khác policy, vì personal skill có thể được ưu tiên hơn project skill.

## 6. Xác minh cài đặt

### 6.1 Validate source suite

```powershell
Set-Location "C:\PROJECT\data-department"

python .\tools\validate_suite.py
python .\tools\validate_claude_skills.py
python .\tools\run_smoke_tests.py
```

Kỳ vọng:

```text
skills: 28
tasks: 669
task_links: 669
errors: 0
```

### 6.2 Validate local plugin

```powershell
$pluginRoot = "C:\PROJECT\data-department\dist\claude-plugin\data-department-agent-skills"

claude plugin validate --strict $pluginRoot
claude --plugin-dir $pluginRoot plugin details data-department-agent-skills
```

Kỳ vọng inventory có `Skills (32)` và version `3.1.0`.

### 6.3 Kiểm tra Project/User skills

Project:

```powershell
$skillRoot = "C:\path\to\your-project\.claude\skills"

(Get-ChildItem -LiteralPath $skillRoot -Directory).Count
(Get-ChildItem -LiteralPath $skillRoot -Recurse -Filter SKILL.md -File).Count
```

User:

```powershell
$skillRoot = Join-Path $env:USERPROFILE ".claude\skills"

(Get-ChildItem -LiteralPath $skillRoot -Directory).Count
(Get-ChildItem -LiteralPath $skillRoot -Recurse -Filter SKILL.md -File).Count
```

Nếu thư mục chỉ chứa bộ này, hai kết quả phải là `28`. Nếu đã có skill khác, hãy kiểm tra tên 28 folder theo `suite-manifest.yaml` thay vì dựa vào tổng số.

### 6.4 Runtime routing smoke test

Mở Claude với plugin và nhập:

```text
/data-department-agent-skills:data-career-and-interview-coach

Tôi có đúng một câu hỏi phỏng vấn về Requirements Traceability Matrix.
Hãy chọn current atomic task để tạo một question dossier hoàn chỉnh,
không tạo multi-dossier knowledge library.
Trước tiên chỉ trả task ID và primary deliverable.
```

Kỳ vọng:

```text
career-build-question-deep-dive
interview question deep-dive dossier
```

## 7. Cơ chế sử dụng và routing

### 7.1 Có bắt buộc gọi skill cụ thể không?

**Không.** Bạn có thể chỉ đưa đề bài và repository. Claude dựa trên `description` của 29 role skills để tự kích hoạt skill phù hợp.

Ví dụ tối thiểu:

```text
Đề bài:
Xây hệ thống ELT cho orders, có incremental load, data quality,
analytics mart và dashboard vận hành.

Repository mẫu:
https://github.com/example/sample-data-platform

Hãy phân tích, lập kế hoạch, triển khai, test và bàn giao.
Không deploy hoặc push nếu tôi chưa yêu cầu.
```

Yêu cầu này có nhiều role nên `data-department-orchestrator` là entry point hợp lý.

### 7.2 Khi nào gọi orchestrator?

Gọi orchestrator khi:

- Đề bài mơ hồ hoặc chưa rõ deliverable chính.
- Có từ hai role trở lên.
- Cần rebuild/adapt một repository mẫu.
- Muốn quy trình end-to-end từ discovery đến handoff.
- Cần quản lý dependency, approval gate và trạng thái qua nhiều task.

Plugin:

```text
/data-department-agent-skills:data-department-orchestrator
```

Project/User:

```text
/data-department-orchestrator
```

### 7.3 Khi nào gọi role skill trực tiếp?

Gọi role khi primary deliverable đã rõ:

```text
/data-engineering
Build API ingestion pipeline và test rerun/idempotency.
```

```text
/analytics-engineering
Thiết kế dimensional model; chỉ tạo design specification, chưa build.
```

```text
/data-talent-acquisition-and-interview
Audit bộ câu hỏi Senior DE theo competency coverage, fairness và answer leakage.
```

### 7.4 Có gọi atomic task bằng slash command không?

Không. 802 atomic tasks là task contracts nằm trong `references/tasks/`; chúng không phải 802 top-level slash commands.

Bạn gọi role skill hoặc chỉ mô tả yêu cầu. Role skill sẽ:

```text
chọn catalog phù hợp
→ chọn đúng một task ID
→ đọc task contract
→ thực hiện lifecycle
→ bàn giao next task/role
```

Nếu muốn ép routing, hãy nêu task ID trong prompt:

```text
/data-engineering
Hãy dùng task `de-build-api-ingestion` cho yêu cầu sau: ...
Xác minh task vẫn phù hợp trước khi thực hiện.
```

### 7.5 Bắt Claude công khai routing trước khi làm

Dùng khi cần auditability:

```text
Trước khi thực hiện, hãy báo:
1. Primary role skill.
2. Current atomic task ID.
3. Primary deliverable.
4. Lifecycle profile, risk tier và execution path.
5. Inputs còn thiếu, bounded assumptions và blockers.
6. Acceptance criteria và test strategy.

Sau đó mới thực hiện task hiện tại.
```

### 7.6 Plan-only, build hay full lifecycle

Nêu rõ phase để tránh Claude build khi bạn chỉ muốn thiết kế:

```text
Chỉ Plan/Assess/Design. Không sửa file, không chạy migration, không deploy.
```

```text
Được phép sửa repository trong scope đã nêu. Build và chạy test local.
Không push, tạo PR hoặc deploy.
```

```text
Thực hiện đầy đủ tới release candidate. Dừng trước production approval gate.
```

### 7.7 Các control của v2.4.0–v3.1.0

Bộ skill tự kích hoạt các control này theo task; bạn không cần gọi từng file template:

| Tình huống | Task/control chính | Kết quả |
|---|---|---|
| Đề bài mơ hồ nhưng cần build | `core-define-success-contract` | Outcome quan sát được, pass/fail checks, non-goals, evidence và stop conditions |
| Review repository change | `core-audit-change-scope` + `audit_change_scope.py` | Phát hiện file ngoài allowlist, deletion chưa duyệt và thay đổi không trace tới outcome |
| Debug pipeline/model/platform | `execution-discipline-standard.md` + hypothesis ledger | Reproduce, boundary evidence, một giả thuyết/một biến và dừng để review kiến trúc sau ba fix thất bại |
| Tuyên bố đã hoàn thành | verification-claims ledger | Mỗi claim có command/method, environment, artifact version, result, exit status và timestamp mới |
| Audit dashboard | `bi-audit-dashboard-experience` | Audit read-only về decision fit, hierarchy, metric truth, density, states, accessibility, responsive và generic patterns |
| Redesign dashboard | `bi-redesign-dashboard-experience` | Finding-to-change-to-test traceability, giữ metric semantics và design-system boundary |
| Xây Career OS | `career-build-career-operating-system` | Current state → capability → practice → real work → evidence → feedback → review, có recovery buffer và không hứa title |
| Xây technical series | `content-design-technical-series` | Knowledge map, episode arc, canonical evidence pack, Facebook tiếng Việt, LinkedIn/Substack tiếng Anh và quality gates |
| Kiểm chứng nội dung | `content-audit-claim-source-traceability` + `validate_content_manifest.py` | Chặn factual claim thiếu source, artifact mất lineage, sai channel-language contract hoặc publication thiếu approval |
| Professional-series contract | Mọi `content-*` task | Capability journey, coverage matrix, teaching contract, human voice, decision-oriented CTA và editing pass |
| Media evidence contract | `REAL → ILLUSTRATION → CODE` | Chặn release nếu thiếu artifact thật, mental-model visual hoặc code proof; kiểm tra source, rights, redaction, alt text, baseline, validation và SHA-256 |
| Chọn personal project | `project-classify-starting-point` + `project-score-project-options` | Chọn trong 20 entry mode bằng hard gates, weighted score, confidence và risk penalty |
| Repo-first personal project | `project-start-repo-first` + `project-audit-reference-repository` | Audit 12 chiều, chạy baseline an toàn, lập reuse/adapt/replace/drop/build-new matrix và finding có evidence |
| Ý tưởng/repo của người khác | `project-plan-originality-and-attribution` + `project-transform-borrowed-source-to-original-thesis` | Giữ attribution/license, tạo thesis riêng và ít nhất ba trục khác biệt thực chất; chặn renamed/cosmetic clone |
| Xây Second Brain local | `brain-design-four-layer-architecture` + `brain-plan-tool-migration` | Tách nguồn bất biến, Wiki đã xử lý, chất riêng và kết quả; giữ stable ID, source lineage, privacy, retrieval test và restore proof |
| Chuyển sách thành hệ thống dùng được | `book-recover-document-structure` + một destination task | Bóc cấu trúc/framework đúng locator, tách tác giả–synthesis–application, kiểm quyền và kiểm thử khả năng áp dụng trước publish |

Token vẫn được tối ưu bằng progressive disclosure: Claude chỉ đọc một role catalog, một atomic task contract và reference/template đúng với failure risk hiện tại. Bốn ledger của execution discipline không được tải đồng thời nếu task chỉ cần một loại evidence.

### 7.8 Workflow Runtime, Evidence OS và stack adapters — v3

Với workflow nhiều task hoặc task `enforced`, Claude phải tạo `workflow-manifest.json`, dùng task ID canonical, owner, dependencies, risk floor, artifact version/hash, evidence và approval references. Chạy validator trước execution, sau transition và ở `complete` mode trước claim cuối:

```powershell
python skills\data-department-orchestrator\scripts\validate_workflow.py `
  workflow-manifest.json `
  --catalog task-catalog.json `
  --evidence-dir evidence `
  --approval-dir approvals `
  --mode complete
```

Mỗi claim quan trọng phải bind vào evidence envelope. Khi artifact ở local, dùng complete mode để kiểm tra tồn tại và SHA-256:

```powershell
python skills\shared-data-core\scripts\validate_evidence_bundle.py `
  evidence.json `
  --artifact-root . `
  --mode complete
```

Sau khi chọn task, Claude detect stack thật và chỉ đọc một hoặc hai adapter phù hợp. Adapter không thay đổi ownership, metric semantics, risk hoặc approval. Parse/syntax pass không được coi là runtime hoặc end-to-end correctness.

Các automation read-only chính:

- `audit_repository.py`: inventory repo-first trên 12 chiều, không chạy code của repo.
- `detect_data_stack.py`: phát hiện adapter candidate từ manifest và source evidence.
- `bootstrap_context_index.py`: tạo context-source index mà không sao chép content values.
- `build_portfolio_evidence.py --strict`: kiểm tra artifact/hash/validation trước portfolio claims.
- `record_skill_telemetry.py` và `analyze_skill_telemetry.py`: telemetry không chứa prompt, secrets hoặc dữ liệu người dùng.

### 7.9 Personal Project Discovery & Build OS

Bạn không cần biết tên task. Chỉ cần đưa những gì đang có: vấn đề, user workflow, quyết định cần hỗ trợ, ý tưởng, link bài/video, dataset, GitHub repo, role mục tiêu, công nghệ, domain, architecture pattern, paper, course, incident, constraint hoặc nhiều đầu vào cùng lúc. Claude sẽ tự phân loại entry mode và chỉ hỏi khi thiếu thông tin có thể làm thay đổi đáng kể lựa chọn.

Với repo-first, quy trình mặc định là:

```text
provenance + license + exact version
→ evidence-based audit 12 chiều
→ safe baseline / reproducibility check
→ reuse | adapt | replace | drop | build-new
→ personal project thesis
→ substantive differentiation
→ blueprint + milestones + implementation handoff
→ functional + reproducibility + quality + security + performance tests
→ portfolio evidence + release review + maintenance/evolution
```

Nếu repo hoặc ý tưởng đến từ người khác, kết quả được coi là project do bạn chủ động thiết kế và xây theo thesis riêng, nhưng nguồn cảm hứng vẫn phải được ghi đúng. Bộ skill không biến nguồn ngoài thành tuyên bố sai rằng ý tưởng gốc hoàn toàn do bạn nghĩ ra.

### 7.10 Personal Second Brain / Knowledge OS

Chỉ cần mô tả nơi dữ liệu đang nằm và kết quả bạn muốn AI tạo. Claude sẽ route vào `personal-second-brain-and-knowledge-os`, không bắt buộc bạn gọi slash command hay cài MCP. Kiến trúc canonical:

```text
1_Nguon   = file gốc, export, PDF, transcript, ảnh, bảng tính; giữ bất biến và ghi quyền/provenance
2_Wiki    = note đã xử lý, concept map, liên kết, conflict và source locator
3_Toi     = kinh nghiệm, nguyên tắc, giọng viết, audience và work rules của bạn
4_Ket-Qua = bài viết, báo cáo, kế hoạch, slide, project hoặc artifact có lineage
```

Luồng chuẩn là `Assess → Design → Import → Normalize → Distill → Link → Retrieve → Generate → Grounding test → Backup/restore → Review`. Notion, Google Sheets, LarkSuite và Obsidian có thể tiếp tục là nguồn hoặc giao diện; hệ thống local là lớp kiến thức canonical để AI đọc theo task. Không đưa secret/raw sensitive values vào metadata index và không coi `3_Toi` là sự thật khách quan.

Prompt tối thiểu:

```text
Tôi có export Notion ở <path>, PDF/transcript ở <path> và Obsidian vault ở <path>.
Hãy audit read-only, thiết kế Não2 theo 1_Nguon/2_Wiki/3_Toi/4_Ket-Qua,
lập migration plan có rollback, source lineage, privacy, retrieval tests và backup/restore.
Chưa di chuyển hay xóa file nguồn.
```

### 7.11 Book → Knowledge / Skill / Action

Skill này không chỉ tóm tắt sách. Nó hỗ trợ bốn mode: `analyze`, `full`, `fold-in`, `update`; kiểm tra quyền sử dụng, format/extractor và token/cost preflight; khôi phục cấu trúc; bóc framework, principle, technique, anti-pattern, mental model, example và technical artifact; sau đó biên dịch vào **một primary destination**:

- Agent skill, progressive chapter pack hoặc decision cheatsheet.
- Second Brain pack có source locator và knowledge graph.
- Career/interview/project application pack.
- Curriculum, workflow, technical-content series hoặc action experiment.

Các downstream owner vẫn giữ đúng ranh giới: Career sở hữu career evidence; Academy sở hữu curriculum/assessment; Technical Content sở hữu publication; Second Brain sở hữu vault/lineage. Publication bị chặn nếu quyền, traceability, exact artifact approval hoặc copyright/security test chưa đạt.

```text
Đọc các sách ở <path>. Chạy analyze trước, không sửa nguồn.
Giữ đúng tên framework và chapter/page/section locator; phân biệt author claim,
synthesis của AI và cách áp dụng của tôi. Primary destination là second-brain.
Sau đó đề xuất một career application pack và action experiments dưới dạng handoff,
không publish công khai.
```

## 8. Prompt mẫu

### 8.1 Đề bài + GitHub repository mẫu

```text
Tôi có đề bài sau:
<business outcome, users, constraints, acceptance criteria>

Repository mẫu:
<GitHub URL hoặc local path>

Hãy dùng Data Department Orchestrator để:
1. Inspect đề bài và repo thực tế.
2. Lập ma trận reuse / adapt / replace / build-new.
3. Xác định role owners, atomic tasks, dependencies và gates.
4. Đề xuất target architecture và implementation plan.
5. Thực thi trong repository hiện tại.
6. Chạy unit/contract/integration/data-quality/security/performance tests phù hợp.
7. Bàn giao evidence, assumptions, residual risks và next owner.

Không bịa việc đã chạy/test/approve.
Không push, tạo PR, deploy hoặc thay đổi production nếu chưa được phép.
```

### 8.1A Personal project từ một repository có sẵn

```text
/data-personal-project-engineering

Tôi muốn dùng repository sau làm điểm xuất phát cho một personal portfolio project:
<GitHub URL, commit/tag hoặc local path>

Hãy tự route theo repo-first. Kiểm tra provenance/license, đánh giá repo chi tiết
bằng evidence, thử baseline an toàn nếu khả thi, chỉ rõ strengths/weaknesses và
đề xuất cải tiến. Lập ma trận reuse/adapt/replace/drop/build-new, sau đó thiết kế
một project thesis của tôi với ít nhất ba khác biệt thực chất, roadmap, test plan,
portfolio evidence và tiêu chí hoàn thành. Ghi nguồn trung thực; không cosmetic clone.

Hiện chỉ Plan/Assess/Design, chưa sửa repository.
```

Bạn cũng có thể bỏ dòng `/data-personal-project-engineering`; natural-language routing vẫn phải chọn skill này khi primary deliverable là personal learning/capstone/portfolio project.

### 8.2 Data Engineering

```text
/data-engineering

Build ingestion từ REST API có OAuth, pagination, rate limit,
incremental watermark và late-arriving updates.
Rerun phải idempotent. Bổ sung reconciliation, retry policy,
failure recovery, tests và runbook.
```

### 8.3 Data Analysis

```text
/data-analysis

Phân tích nguyên nhân conversion giảm trong 4 tuần gần đây.
Tách observation, inference và recommendation.
Kiểm tra data quality, seasonality, mix shift và statistical uncertainty.
Không tuyên bố causal nếu evidence chỉ là observational.
```

### 8.4 Data Architecture

```text
/data-architecture

Thiết kế target architecture cho customer-360.
So sánh ít nhất hai phương án, xác định domain boundaries,
source of truth, data contracts, security, resilience,
migration waves và Architecture Decision Records.
Chỉ design, chưa triển khai.
```

### 8.5 Academy và đào tạo

```text
/data-academy-and-curriculum

Thiết kế curriculum Data Engineer từ Foundation đến Senior.
Mỗi module cần prerequisites, learning objectives, theory,
hands-on lab, assessment rubric, critical failures,
remediation và retention/transfer test.
```

### 8.6 Onboarding

```text
/data-onboarding-and-integration

Tạo lộ trình onboarding 7/30/60/90 ngày cho Analytics Engineer.
Bao gồm role outcomes, company context, least-privilege access,
buddy plan, practical evidence, checkpoint rubric và readiness gate.
```

### 8.7 Tuyển dụng và phỏng vấn

```text
/data-talent-acquisition-and-interview

Thiết kế structured interview loop cho Senior Data Engineer.
Trace role outcomes → competencies → questions → observable evidence → score.
Tạo standardized probes, Weak/Meets/Strong anchors,
critical failures, calibration plan và fairness/leakage audit.
```

### 8.8 Interview Knowledge Deep Dive

Một câu hỏi:

```text
/data-career-and-interview-coach

Biến câu hỏi RTM này thành một dossier gồm:
question analysis, knowledge dependencies, answer strategy,
authentic STAR hoặc hypothetical example có gắn nhãn,
knowledge deep dive, related concepts, follow-up questions,
practice và novel retest.
```

Nhiều dossier thành library:

```text
/data-enablement-and-knowledge

Tổ chức các dossier đã duyệt thành linked/versioned knowledge library:
stable IDs, taxonomy, concept relations, backlinks, source provenance,
owners, review status, freshness, release manifest và Notion-ready view.
Publication là downstream handoff sau approval.
```

### 8.9 Career Operating System

```text
/data-career-and-interview-coach

Tôi đang là Mid-level Data Engineer và muốn phát triển năng lực Staff.
Hãy đánh giá current state, map competency/scope/impact/influence,
xây Career OS 12 tháng có real-work practice, evidence milestones,
feedback, recovery buffers và quarterly review.
Không hứa promotion; phân biệt self-study, project và production evidence.
```

### 8.10 Technical series cho Facebook, LinkedIn và Substack

```text
/data-technical-content-and-social

Thiết kế series Apache Airflow từ mental model tới production operations.
Bắt đầu bằng research/version matrix, knowledge map và series architecture.
Mỗi episode phải có canonical article, runnable example, diagram brief,
failure/trade-off, claim-source traceability; sau validation mới adaptation
riêng cho Facebook bằng tiếng Việt, LinkedIn bằng tiếng Anh và Substack
bằng tiếng Anh. Giữ code, identifier, product name và technical term cần độ
chính xác; không copy hoặc dịch máy móc giữa các kênh. Ghi `language` trên
từng artifact và chỉ approve khi test scope `channel-language` đã pass cho
đúng version/SHA-256.

Mỗi social episode còn phải có teaching contract trước khi viết: learning
objective, starting point, misconception, scenario, core claim, mechanism,
decision, failure mode, evidence và boundary. Bộ ảnh mặc định theo thứ tự
`REAL → ILLUSTRATION → CODE`; thiếu một vai trò phải có ngoại lệ biên tập được
phê duyệt. Complete/release mode yêu cầu thêm review `human-voice`,
`media-integrity` và test scope `editorial-depth`, `human-voice`,
`media-contract` trên đúng artifact.
```

## 9. Quy trình chuẩn khi có đề bài và repository mẫu

### 9.1 Intake

Cung cấp tối thiểu:

- Business outcome và target users.
- Repository URL hoặc local path.
- Scope được phép thay đổi.
- Constraints: stack, deadline, cloud, data volume, compliance.
- Acceptance criteria biết trước.
- Quyền được phép: read, edit, test, install dependency, network, push/deploy.

Thiếu thông tin không làm thay đổi semantics/risk thì Claude có thể dùng bounded assumption. Thiếu thông tin làm thay đổi scope, cost, safety hoặc acceptance phải được coi là blocker.

### 9.2 Repository assessment

Claude cần inspect artifact thực trước khi kết luận:

```text
Repository structure
→ runtime/dependencies
→ architecture and data flow
→ schemas/contracts
→ tests and CI
→ security/config/secrets handling
→ documentation/runbooks
→ gaps versus requested outcome
```

Đầu ra nên có ma trận:

| Component | Decision | Lý do | Validation |
|---|---|---|---|
| Có thể dùng nguyên | Reuse | Phù hợp requirement và test pass | Regression test |
| Cần sửa | Adapt | Ý tưởng đúng nhưng contract/quality thiếu | Targeted + integration test |
| Không phù hợp | Replace | Architecture/risk không đáp ứng | Migration/compatibility test |
| Còn thiếu | Build new | Không có component đáp ứng | Full task-specific tests |

### 9.3 Planning và task graph

Orchestrator phân rã theo primary deliverables, ví dụ:

```text
BA requirements
→ Architecture design/ADR
→ DE ingestion
→ AE model/mart
→ DQ assurance
→ Governance certification
→ BI product
→ UAT/release/handoff
```

Mỗi thời điểm chỉ có một current atomic task; những task còn lại là ordered handoffs. Điều này giữ ownership rõ và tránh Claude tải toàn bộ 669 contracts vào context.

### 9.4 Execute và test

Test strategy phụ thuộc artifact, nhưng có thể gồm:

- Static/lint/schema checks.
- Unit và contract tests.
- Integration và end-to-end tests.
- Source-target reconciliation.
- Data-quality/freshness/completeness checks.
- Security/privacy/access review.
- Performance/cost/regression tests.
- Rollback/recovery hoặc novel transfer/retest cho People OS.

Claude phải phân biệt rõ `planned`, `implemented`, `tested`, `approved`, `released` và `monitored`. Không được biến plan thành production outcome trong báo cáo.

### 9.5 Completion response

Yêu cầu response cuối theo mẫu:

```text
- Selected skill và task ID
- Lifecycle/risk/path
- Phase reached
- Primary deliverable và files/artifacts
- Evidence inspected
- Tests run, pass/fail và limitations
- Approval status
- Assumptions/blockers
- Residual risks và owner
- Next atomic task / handoff
```

## 10. Company context và quyền

### 10.1 Context nên cung cấp

- Business glossary và metric registry.
- Dataset/source/system inventory.
- Grain, keys, schemas, owners và SLAs/SLOs.
- Platforms, environments, deployment rules và cost constraints.
- Security, privacy, retention, classification và access policies.
- Role/level/competency framework.
- Change, release, incident và approval policies.

Khởi tạo context có quản trị bằng `company-data-context`; ghi provenance, version, owner và last-verified date.

### 10.2 Context không nên lưu trong skill

- Password, API token, private key hoặc cloud credentials.
- Raw sensitive records hoặc unnecessary PII.
- Unapproved interview answer keys.
- Thông tin không có provenance nhưng được trình bày như fact.

### 10.3 Import không tự cấp quyền

Skill chỉ là instructions và resources. Nó không tự cấp repository, terminal, cloud, database, MCP hay production permissions cho Claude.

Các hành động sau cần authority rõ ràng:

- Push/merge/create PR nếu ngoài scope đã giao.
- Deploy/publish production.
- Migration hoặc destructive data change.
- Cấp/thu hồi access.
- Xử lý privacy deletion/request.
- Certify metric/data product/model.
- Promote model hoặc thay đổi traffic.
- Hiring/certification decision ảnh hưởng con người.

## 11. Cập nhật, gỡ và phục hồi

### 11.1 Cập nhật Project/User skills

Installer từ chối ghi đè mặc định. Kiểm tra thay đổi cục bộ trước:

```powershell
git diff -- .claude/skills
```

Sau khi backup/review, cập nhật Project scope:

```powershell
Set-Location "C:\PROJECT\data-department"

.\tools\install_claude_skills.ps1 `
  -Scope Project `
  -ProjectPath "C:\path\to\your-project" `
  -Force
```

User scope:

```powershell
.\tools\install_claude_skills.ps1 -Scope User -Force
```

`-Force` thay toàn bộ folder skill trùng tên. Không dùng nếu có custom changes chưa sao lưu.

### 11.2 Cập nhật local plugin

Giải nén bản mới vào thư mục version mới, validate, rồi đổi `--plugin-dir`. Không giải nén đè lên folder đang dùng nếu cần rollback nhanh.

Trong phiên Claude Code đang mở, dùng `/reload-plugins` khi cập nhật plugin files. Với project/user skill, Claude Code theo dõi file changes; nếu top-level skills directory chưa tồn tại lúc mở session, khởi động lại để đảm bảo discovery.

### 11.3 Gỡ cài đặt

Local plugin: đóng session được mở bằng `--plugin-dir`; không có cài đặt persistent cần xóa.

Project/User: chỉ xóa đúng 28 folder được liệt kê trong `suite-manifest.yaml` sau khi đã xác nhận target path và backup custom changes. Không xóa toàn bộ `.claude\skills` nếu có skill khác.

## 12. Troubleshooting

### 12.1 Claude không thấy skill

Kiểm tra:

1. File phải là `SKILL.md` đúng chữ hoa.
2. Folder phải ở đúng `.claude\skills\<name>` hoặc `<plugin-root>\skills\<name>`.
3. Claude được mở từ project hoặc thư mục con của project.
4. Nếu vừa tạo top-level skills directory, khởi động lại Claude.
5. Dùng `/help` để kiểm tra command discovery.

### 12.2 Plugin không load

```powershell
claude plugin validate --strict "C:\path\to\plugin-root"
claude --debug --plugin-dir "C:\path\to\plugin-root"
```

Các lỗi thường gặp:

- Trỏ `--plugin-dir` vào ZIP thay vì folder đã giải nén.
- `.claude-plugin\plugin.json` không nằm ở plugin root.
- `skills\` bị đặt bên trong `.claude-plugin\`.
- Skill frontmatter hoặc plugin manifest không hợp lệ.

### 12.3 Slash command sai tên

Plugin:

```text
/data-department-agent-skills:<skill-name>
```

Project/User:

```text
/<skill-name>
```

Không gọi atomic task ID như slash command.

### 12.4 Claude chọn sai role hoặc task

Nêu primary deliverable và phase rõ hơn:

```text
Primary deliverable tôi cần là <artifact>.
Hiện tại chỉ <Plan/Build/Test/Operate>.
Hãy báo role skill và task ID trước khi làm.
Nếu task không thuộc role này, hãy handoff thay vì nhận ownership.
```

### 12.5 Claude nói đã test hoặc deploy nhưng không có evidence

Yêu cầu dừng và trả:

```text
Liệt kê chính xác command/tool đã chạy, exit code, artifact/log evidence,
test nào chưa chạy, approval nào chưa có và phase thực sự đạt được.
Không suy diễn planned work thành executed outcome.
```

### 12.6 Kết quả quá dài hoặc tốn token

- Gọi đúng role thay vì orchestrator nếu deliverable đơn role.
- Nêu phase hiện tại và một primary deliverable.
- Yêu cầu đọc đúng một task contract.
- Không yêu cầu Claude load toàn bộ catalogs/references.
- Tái sử dụng verified context thay vì gửi lại lịch sử dài.

## Tài liệu đối chiếu

- [Claude Code — Extend Claude with skills](https://code.claude.com/docs/en/slash-commands)
- [Claude Code — Create plugins](https://code.claude.com/docs/en/plugins)
- [Claude Code — Plugins reference](https://code.claude.com/docs/en/plugins-reference)
- [Agent Skills specification](https://agentskills.io/specification)
- [Catalog đầy đủ 32 skills và 802 tasks](01_CHI_TIET_TOAN_BO_SKILL_VA_TASK.md)
