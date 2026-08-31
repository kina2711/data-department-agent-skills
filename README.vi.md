# Data Department Agent Skills

Hệ điều hành có kiểm soát cho toàn bộ một phòng Data, đóng gói dưới dạng plugin Claude Code.
**32 role skill**, **827 atomic task contract**, **49 slash command**, **52 script evidence
chạy được**, **12 JSON Schema**, và một production guard hook.

[![Validate](https://github.com/kina2711/data-department-agent-skills/actions/workflows/validate.yml/badge.svg)](https://github.com/kina2711/data-department-agent-skills/actions/workflows/validate.yml)

Bản hiện tại: **v3.10.0** · Chạy được với **Claude Code**, **OpenAI Codex** và **Google Antigravity**

🇬🇧 [Read in English](README.md)

---

## Bộ này giải quyết vấn đề gì

Một agent có 800 workflow mà không có kiểm soát thì tệ hơn agent chỉ có mười, vì nó sẽ tự tin
tuyên bố những việc nó chưa từng làm. Ba kiểu hỏng lặp đi lặp lại:

1. **Bịa hoàn thành.** "Đã deploy lên production", "test đã pass", "stakeholder đã duyệt" —
   nói ra mà không có bằng chứng.
2. **Suy thoái cấu trúc.** Code sinh ra nhanh hơn tốc độ review kiến trúc hấp thụ được. Test
   vẫn xanh trong khi cycle xuất hiện và những quyết định đã chốt bị lặng lẽ đổi.
3. **Trôi quyền sở hữu.** Yêu cầu mơ hồ được trả lời bởi role nào nghe gần nhất, nên không ai
   sở hữu kết quả và việc bàn giao không bao giờ xảy ra.

Mọi cơ chế ở đây tồn tại để làm một trong ba thứ đó **phát hiện được** thay vì chối được.

**Lập trường thiết kế:** `not-run`, `incomplete` và `unknown` là các trạng thái trung thực, và
không cái nào được phép báo cáo như thành công. Tỷ lệ thất bại cao kích hoạt điều tra, **không
bao giờ** nới lỏng gate. Không có gì ở đây tuyên bố đã thực thi production, publish, đổi quyền
truy cập, xóa dữ liệu, chứng nhận hay promote model mà thiếu bằng chứng và phê duyệt đích danh
của con người.

---

## Mục lục

- [Cài đặt](#cài-đặt)
- [Các harness khác](#các-harness-khác)
- [Bắt đầu nhanh](#bắt-đầu-nhanh)
- [Cơ chế routing](#cơ-chế-routing)
- [32 phòng ban](#32-phòng-ban)
- [Slash command](#slash-command)
- [Các tầng kiểm soát](#các-tầng-kiểm-soát)
- [Evidence chạy được](#evidence-chạy-được)
- [Cấu trúc repo](#cấu-trúc-repo)
- [Build và kiểm chứng từ source](#build-và-kiểm-chứng-từ-source)
- [Tài liệu](#tài-liệu)
- [Giấy phép](#giấy-phép)

---

## Cài đặt

Yêu cầu **Claude Code** và **Python 3.10+** nằm trên `PATH` với tên `python` (guard hook và mọi
script evidence đều cần; cả hai fail-open nếu thiếu).

### Cách 1 — từ file release (khuyến nghị)

```powershell
# Windows
$pluginRoot = "C:\Tools\data-department-agent-skills-v3.10.0"
Expand-Archive .\data-department-claude-plugin-v3.10.0.zip -DestinationPath $pluginRoot
claude plugin validate --strict $pluginRoot
claude --plugin-dir $pluginRoot
```

```bash
# macOS / Linux
pluginRoot=~/tools/data-department-agent-skills-v3.10.0
unzip data-department-claude-plugin-v3.10.0.zip -d "$pluginRoot"
claude plugin validate --strict "$pluginRoot"
claude --plugin-dir "$pluginRoot"
```

Thư mục giải nén phải chứa `.claude-plugin/plugin.json`, `skills/`, `commands/` và `hooks/`.
Thiếu bất kỳ cái nào thì plugin sẽ nạp **một phần** của chính nó mà không báo gì.

### Cách 2 — qua marketplace manifest

Repo tự publish như một marketplace một-plugin (`.claude-plugin/marketplace.json`):

```
/plugin marketplace add kina2711/data-department-agent-skills
/plugin install data-department-agent-skills
```

### Cách 3 — từ source, để phát triển

```bash
git clone https://github.com/kina2711/data-department-agent-skills.git
cd data-department-agent-skills
python -m pip install PyYAML
python tools/build_suite.py
python tools/validate_claude_skills.py
claude --plugin-dir .
```

### Kiểm tra đã cài đúng chưa

```
/dd-catalog profiling
```

Phải trả về các task ID khớp từ catalog 827 task. Nếu nó trả lời bằng kiến thức chung thay vì
từ catalog, nghĩa là plugin **chưa** được nạp.

---

## Các harness khác

Bộ này không chỉ dành cho Claude. Codex dùng đúng frontmatter `name` + `description` của
SKILL.md, nên không có tầng chuyển đổi nào — installer **link** cùng thư mục chứ không nhân bản.

| Harness | Đọc gì | Bề mặt |
|---|---|---|
| **Claude Code** | `.claude-plugin/`, `skills/`, `commands/`, `hooks/` | Đầy đủ: 45 command, production guard hook |
| **OpenAI Codex** | `AGENTS.md`, `.codex/skills/<name>/SKILL.md` | 32 skill, route ngầm hoặc gọi tên |
| **Google Antigravity** | `AGENTS.md`, `.agents/agents/<name>.md`, `.agents/skills/` | 32 custom agent, mỗi phòng ban một cái |
| Harness AGENTS.md khác | `AGENTS.md`, `skills/<name>/SKILL.md` | 32 skill |

```bash
# cài vào một project đích
python tools/install_agent_harness.py /path/to/project --harness codex
python tools/install_agent_harness.py /path/to/project --harness antigravity
python tools/install_agent_harness.py /path/to/project            # cả ba

python tools/install_agent_harness.py /path/to/project --dry-run  # xem trước mọi thao tác
python tools/install_agent_harness.py /path/to/project --uninstall
```

**Nó link chứ không copy**, nên một lần rebuild là mọi harness đã cài đều cập nhật theo. Chỗ
nào không tạo được symlink — Windows chưa bật Developer Mode — nó chuyển sang copy và **nói rõ
ra**, vì một bản copy âm thầm rồi cũ đi thì tệ hơn một bản copy được cảnh báo. Dùng `--copy`
để ép, và nhớ chạy lại sau mỗi lần rebuild.

**Nó từ chối ghi đè bất cứ thứ gì không phải do nó tạo.** File `.data-department-install.json`
ghi lại những gì thuộc về nó; `--force` để ghi đè, `--uninstall` gỡ đúng những gì đã thêm và
không đụng gì khác.

### Riêng với Antigravity

`.agents/agents/` chứa mỗi phòng ban một custom agent, sinh từ build. Mỗi agent đều ghim
`commandExecutionPolicy: sandbox` — bộ này không bao giờ tuyên bố đã thực thi production mà
thiếu bằng chứng và phê duyệt, nên định nghĩa agent cũng không được lặng lẽ cấp quyền đó.
Trường `tools` cố ý để trống để harness dùng mặc định, thay vì đóng băng một danh sách tool sẽ
lỗi thời.

### Riêng với Codex

Codex đọc `AGENTS.md` ở thư mục home của Codex trước, rồi đi từ gốc repo xuống thư mục làm việc
hiện tại, file gần hơn ghi đè file xa hơn. Skill nằm ở `.codex/skills/<name>/SKILL.md` cho
phạm vi repo, hoặc `~/.codex/skills/` cho phạm vi người dùng.

> Custom prompt của Codex **đã deprecated**, skill là đường thay thế, nên bộ này không ship file
> `~/.codex/prompts/` nào. 13 control command vẫn chỉ có ở Claude Code; với Codex và
> Antigravity, cứ yêu cầu điều tương tự bằng ngôn ngữ tự nhiên.

---

## Bắt đầu nhanh

**Bạn không cần nhớ task ID.** Cứ hỏi bằng ngôn ngữ tự nhiên:

```
Hai dashboard đang ra hai con số khác nhau cho cùng một KPI doanh thu. Tìm nguyên nhân.
```

Claude sẽ xác định role sở hữu, chọn đúng một atomic task, đọc trọn vẹn contract của task đó,
rồi áp dụng lifecycle profile, risk tier và execution path của chính contract ấy.

Khi muốn điều khiển tường minh:

```
/dd-route Xây incremental dbt model cho order events trên BigQuery
/dd-task ae-build-incremental-model
/dd-verify task-result.json evidence.json ./artifacts
/dd-handoff ae-build-incremental-model data-quality-and-reliability
```

Một phiên làm việc có kiểm soát điển hình:

```
/dd-constitution ratify          # chốt tech stack và luật kiến trúc trước
/dd-scan .                       # đo baseline cấu trúc trước khi đụng vào
/dd-ae Thêm incremental model cho order events
/dd-verify                       # bằng chứng máy kiểm, không phải bản tóm tắt
/dd-approve                      # approval có thực sự cho phép việc này không?
/dd-handoff                      # bàn giao kèm evidence
```

---

## Cơ chế routing

```
yêu cầu bằng ngôn ngữ tự nhiên
   ↓  route theo primary deliverable, không bao giờ theo chức danh
một role skill sở hữu                    (32 ứng viên)
   ↓  đọc MỘT catalog shard, không phải tất cả
một atomic task chuẩn                    (827 contract)
   ↓  đọc trọn vẹn contract đó
Plan → Assess → Design → Execute → Test → Review/Approve → Release/Handoff → Monitor/Improve
```

**Progressive disclosure chính là điểm mấu chốt.** Chỉ description của skill nằm thường trực
trong context. Sau đó Claude nạp một `SKILL.md`, một catalog shard, một task contract, và chỉ
những reference mà contract đó nêu tên. 827 contract và 98 stack adapter **không bao giờ** được
nạp cùng lúc.

Catalog chia theo intent — plan/design, build/deliver, test/assure, operate/improve — và shard
nào vượt 11 task sẽ tự tách tiếp theo chủ đề deliverable (`catalog-plan-design-diagram.md`),
nên không file nào ôm phần lớn việc routing.

### Risk tier quyết định mức kiểm soát

| Tier | Loại việc | Kiểm soát tối thiểu |
|---|---|---|
| `R0-light` | Tra cứu read-only, phân tích có giới hạn | Evidence và tự kiểm |
| `R1-reviewed` | Thiết kế, tài liệu, tư vấn | Peer hoặc domain review |
| `R2-standard` | Build có thể đảo ngược, quy trình con người | Test tự động và owner review |
| `R3-controlled` | Production, quyền truy cập, dữ liệu nhạy cảm, chi phí lớn | Test độc lập, phê duyệt tường minh, rollback, monitoring |
| `R4-critical` | Phá hủy, pháp lý, quyết định đã chứng nhận | Phê duyệt tách biệt, evidence mạnh nhất, recovery đã diễn tập, audit trail |

Fast path `R0` chỉ dành cho việc **thực sự** read-only. Không bao giờ hạ risk để kịp deadline.

---

## 32 phòng ban

Mỗi phòng ban là một slash command, nhóm theo sprint stage. Con số là số atomic task của role đó.

### Think — hiểu trước khi làm

| Command | Phòng ban | Task |
|---|---|---|
| `/dd-hod` | Head of Data and Data Product | 21 |
| `/dd-ba` | Data Business Analysis | 24 |
| `/dd-analysis` | Data Analysis | 29 |
| `/dd-onboard` | Data Onboarding and Integration | 34 |
| `/dd-context` | Company Data Context | 9 |

### Plan — quyết cấu trúc và thứ tự

| Command | Phòng ban | Task |
|---|---|---|
| `/dd-arch` | Data Architecture | 22 |
| `/dd-orchestrate` | Data Department Orchestrator | 20 |

### Build — tạo ra artifact

| Command | Phòng ban | Task |
|---|---|---|
| `/dd-de` | Data Engineering | 25 |
| `/dd-ae` | Analytics Engineering | 22 |
| `/dd-bi` | Business Intelligence | 32 |
| `/dd-ds` | Data Science | 22 |
| `/dd-mle` | Machine Learning Engineering | 20 |
| `/dd-genai` | Generative AI Engineering | 20 |
| `/dd-metadata` | Metadata Engineering and Catalog | 18 |
| `/dd-mdm` | Master Data Management | 13 |
| `/dd-devex` | Data Developer Experience | 19 |
| `/dd-project` | Personal Data Project Engineering | 42 |
| `/dd-core` | Shared Data Core | 18 |

### Review — thẩm quyền và an toàn

| Command | Phòng ban | Task |
|---|---|---|
| `/dd-govern` | Data Governance and Stewardship | 22 |
| `/dd-security` | Data Security and Privacy | 16 |

### Test — chứng minh nó chạy

| Command | Phòng ban | Task |
|---|---|---|
| `/dd-quality` | Data Quality and Reliability | 21 |
| `/dd-experiment` | Product Analytics and Experimentation | 17 |

### Ship — phát hành và vận hành

| Command | Phòng ban | Task |
|---|---|---|
| `/dd-platform` | Data Platform and DataOps | 21 |
| `/dd-mlops` | MLOps | 23 |
| `/dd-content` | Technical Content and Social | 27 |

### Reflect — học, dạy, phát triển

| Command | Phòng ban | Task |
|---|---|---|
| `/dd-career` | Data Career and Interview Coach | 50 |
| `/dd-brain` | Personal Second Brain and Knowledge OS | 46 |
| `/dd-book` | Book to Knowledge and Action | 45 |
| `/dd-hire` | Data Talent and Interviewing | 41 |
| `/dd-academy` | Data Academy and Curriculum | 39 |
| `/dd-docs` | Data Documentation and Diagrams | 20 |
| `/dd-enable` | Data Enablement and Knowledge | 17 |

Chi tiết đầy đủ — ownership, ranh giới, resource và toàn bộ 827 workflow — nằm ở
[docs/skill-and-task-catalog.md](docs/skill-and-task-catalog.md).

---

## Slash command

13 control command đứng cạnh 32 phòng ban. Tất cả đều do người dùng gọi; chúng không tự chạy.

### Routing và điều hướng

| Command | Làm gì |
|---|---|
| `/dd-route <yêu cầu>` | Xác định một role sở hữu và một task chuẩn, **chưa thực thi** |
| `/dd-catalog <từ khóa>` | Tra catalog 827 task theo từ khóa, role prefix hoặc deliverable |
| `/dd-task <task-id>` | Nạp trọn một contract; báo readiness, gate, test, approval |
| `/dd-navigate <symbol>` | Trả lời câu hỏi code từ symbol index thay vì đọc cả file |
| `/dd-recall <câu hỏi>` | Truy hồi việc cũ từ trace đã index, **0 model call** |

### Thực thi và bằng chứng

| Command | Làm gì |
|---|---|
| `/dd-status` | Báo run state đã validate, blocker, hành động kế tiếp được phép |
| `/dd-verify` | Chạy chuỗi evidence; trả passed / failed / **incomplete** |
| `/dd-approve` | Kiểm approval record có thực sự cho phép hành động gated không |
| `/dd-handoff` | Sinh handoff package kèm evidence, residual risk, next owner |

### Quản trị và cải tiến

| Command | Làm gì |
|---|---|
| `/dd-constitution` | Chốt và cưỡng chế tech stack khóa cùng luật kiến trúc chặn |
| `/dd-scan [path]` | Đo structural drift: cycle, độ sâu, coupling, bất cân xứng, trùng lặp |
| `/dd-instinct` | Ghi và chấm điểm pattern tái dùng; confidence tính từ kết quả đếm được |
| `/dd-skill-quality` | Chấm task contract theo outcome đã ghi nhận và mở change request |

> `/dd-quality` mở **phòng ban Data Quality** (chất lượng dữ liệu của bạn).
> `/dd-skill-quality` chấm **chính contract của bộ skill này**. Hai thứ khác nhau.

---

## Các tầng kiểm soát

### Project constitution — chặn việc âm thầm đổi quyết định

Kiểu hỏng: agent làm một tính năng rồi tiện tay đổi luôn một công nghệ đã chốt. Constitution
ghi lại nguyên tắc, tech stack với cờ `locked` từng layer và `alternatives_rejected`, luật
kiến trúc chặn, và chính sách sửa đổi.

```bash
python skills/shared-data-core/scripts/validate_constitution.py project-constitution.json \
  --proposal-file plan.md
```

```
VIOLATION: proposal names 'Snowflake' for locked layer 'warehouse',
           which is decided as 'BigQuery' in ADR-004
BLOCKED: 1 constitution violation(s); amend explicitly or change the plan
```

Exit `3` nghĩa là **bị chặn**, không phải cảnh báo để ghi nhận rồi đi tiếp. Đổi layer đã khóa,
mở khóa nó, hoặc bỏ một luật blocking mà không bump version và không có người duyệt đích danh
đều là vi phạm.

### Production guard hook

`hooks/guard_production_action.py` chặn trước các lệnh shell: git push và force push,
`terraform`/`pulumi` apply và destroy, thay đổi Kubernetes và Helm, xóa tài nguyên cloud và
object storage, `DROP`/`TRUNCATE`, `DELETE` không có `WHERE`, dbt chạy vào target production,
backfill orchestrator, publish package và release, và `rm -rf`.

Nó **chỉ trả `ask`** — không bao giờ `deny`. Phê duyệt mà nó đòi chỉ con người mới cấp được,
nên quyền quyết định vẫn thuộc về bạn. Payload không đọc được hoặc thiếu interpreter thì nó
thoát im lặng về luồng permission mặc định, để một lỗi môi trường **không bao giờ** âm thầm nới
quyền.

### Architecture drift sensor

```bash
python skills/data-architecture/scripts/scan_architecture_drift.py . --max-depth 5 --gate 8000
```

Năm thành phần, mỗi cái 2000 điểm — modularity, acyclicity, depth, equality, redundancy — kèm
cycle (Tarjan SCC), chuỗi phụ thuộc dài nhất, độ bất cân xứng kích thước module (Gini), và các
đoạn trùng lặp báo kèm file và dòng. `--baseline` fail khi điểm tụt so với lần trước.

**Giới hạn được nói rõ:** đây là trích import bằng regex, **không phải parse**. Nó bỏ sót
dynamic import, alias và re-export, và không hiểu ngữ nghĩa. Điểm cao **không** chứng minh kiến
trúc lành mạnh. Cần câu trả lời chính xác thì dùng công cụ tree-sitter như Sentrux và trích dẫn
kết quả đó.

### Instinct có confidence

Một pattern không thành quy luật chỉ vì nó đúng một lần. Confidence là **Wilson lower bound**
của tỷ lệ thành công quan sát được, nên mẫu nhỏ tự động điểm thấp:

| Quan sát | Confidence | Trạng thái |
|---|---|---|
| 9 lần áp dụng, 9 thành công | 0.70 | `active` |
| 2 lần áp dụng, 1 thành công | 0.09 | `proposed` — một lần may mắn |
| 8 lần, 7 thành công, 7 tháng chưa xác nhận lại | 0.53 | `weakening` — phải test lại trước |
| 10 lần áp dụng, 2 thành công | 0.06 | `retired` |

Chỉ instinct `active` mới được phép định hình hành vi. Ghi **một** lần thất bại vào instinct
9/9 là nó bị giáng cấp. Instinct lưu trigger, hành động, lý do và số đếm — **không bao giờ**
lưu transcript, prompt, secret hay giá trị dữ liệu.

### Vòng lặp chất lượng contract

`/dd-skill-quality` chấm chính contract của bộ này từ telemetry đã tối giản hóa dữ liệu cá
nhân, rồi khuyến nghị `observe`, `healthy`, `fix-routing`, `investigate`, `derive-variant` hoặc
`tighten-evidence`.

`fix-routing` fire trên task có **100% completion nhưng 75% override** — chỉ nhìn completion sẽ
che mất lỗi routing: việc thành công nhưng sai contract đang làm. Khuyến nghị là change request
kèm evidence, **không phải** sửa trực tiếp. Telemetry có `user_content` bị từ chối thẳng.

### Recall và navigation không tốn token

`/dd-recall` index note và trace thành entity-context graph cùng temporal hierarchy, rồi truy
hồi bằng chấm điểm tất định — trả về con trỏ `source:line` vào đoạn gốc, **không** phải văn bản
sinh ra. Query không khớp gì thì exit `2` và báo unknown.

`/dd-navigate` trả lời "định nghĩa ở đâu, ai gọi, đổi thì vỡ gì" từ symbol index. Giải thích
một hàm trong `tools/` của repo này trả về **1169 byte thay vì 425360** — ít hơn 99,7% so với
đọc cả 7 file liên quan.

Cả hai đều nói rõ phạm vi: index và ranking **0 model call**, nhưng đọc các đoạn trả về vẫn tốn
context, và bản cài đặt này thuần lexical, không có encoder.

### Learning memory xuyên skill

`mastered` **không** suy ra được từ việc đã đọc, đã dự lớp hay lịch sử chat. Nó đòi bằng chứng
đã kiểm chứng, đủ confidence, một lần chuyển giao được thể hiện, và ngày review còn hiệu lực.
Prerequisite còn tươi thì được nén lại; cái nào cũ, mâu thuẫn, lệch version hay thuộc diện an
toàn thì được mở ra và test lại.

```
Tôi đã hoàn thành Airflow với project và bài test. Giờ học dbt.
```

Task dbt chỉ nhận ranh giới orchestration/transformation, interface gọi, quyết định
retry/idempotency và các failure mode liên quan. DAG cơ bản **không** bị dạy lại — trừ khi
review Airflow đã quá hạn, lúc đó nó chuyển vào nhóm cần test lại.

---

## Evidence chạy được

52 script trải khắp các skill. **Chỉ dùng thư viện chuẩn** — chạy trên máy bạn không cần cài gì
thêm. Exit code mang ý nghĩa thống nhất ở mọi nơi:

| Exit | Nghĩa |
|---|---|
| `0` | Passed |
| `1` | Failed |
| `2` | Incomplete hoặc unknown — có kiểm tra không chạy được. **Không phải pass** |
| `3` | Bị chặn bởi chính sách (vi phạm constitution, thiếu must-have khi UAT) |

### Chuỗi lõi

```bash
python skills/shared-data-core/scripts/validate_task_result.py result.json \
  --task-catalog task-catalog.json --mode complete
python skills/shared-data-core/scripts/validate_evidence_bundle.py evidence.json \
  --artifact-root ./artifacts --mode complete
python skills/shared-data-core/scripts/verify_deliverable.py result.json evidence.json \
  --artifact-root ./artifacts
```

`verify_deliverable.py` nối claim → evidence → hash artifact và liệt kê mọi claim không có
evidence đã kiểm chứng nào chống lưng.

### Workflow và thẩm quyền

| Script | Từ chối cái gì |
|---|---|
| `validate_workflow.py` | Chuyển trạng thái không hợp lệ, task ID không chuẩn |
| `validate_run_state.py` | Một run "complete" mà còn blocker hoặc test fail |
| `validate_approval_record.py` | Approval hết hạn, sai scope, lệch hash |
| `validate_branch_plan.py` | Hai branch cùng ghi một path, phụ thuộc nằm trong cùng một wave, branch vượt trần uỷ quyền, thiếu merge policy |

### Kiểm soát theo lĩnh vực

| Script | Bắt được |
|---|---|
| `validate_policy_coverage.py` | Asset thiếu owner/steward/retention theo classification; certified trên register chưa đủ; review quá một năm |
| `validate_dashboard_spec.py` | Visual bind metric ngoài contract; đổi grain âm thầm; một measure ở hai grain; mã hóa chỉ bằng màu |
| `validate_curriculum_coverage.py` | Objective không bao giờ được assess; cycle prerequisite; câu hỏi recall đòi verify objective mức `apply` |
| `validate_requirements_traceability.py` | Acceptance criteria không có test pass; must-have hở chặn UAT |
| `validate_tabular_data.py` | Kiểm chất lượng CSV/JSONL có giới hạn |
| `audit_change_scope.py` | Thay đổi Git nằm ngoài scope contract đã duyệt |
| `audit_repository.py` | Kiểm kê read-only tất định trước khi đánh giá định tính |
| `profile_dataset.py`, `explain_sql.py` | Evidence phân tích lượt đầu |
| `detect_data_stack.py` | Nhận diện stack trước khi chọn adapter |
| `validate_diagram_source.py` | Diagram có node mồ côi, id trùng, block lệch hoặc không có text equivalent |
| `score_onboarding_checkpoint.py` | Một dimension onboarding critical bị trung bình hoá thành "đang đúng tiến độ" |
| `summarize_terraform_plan.py` | Destroy/replace bị lấp trong dòng tóm tắt plan; resource stateful được tách riêng |
| `check_experiment_design.py` | Thiết kế thiếu power, không hiệu chỉnh multiple testing, effect vượt khả năng phát hiện của traffic |
| `audit_question_bank.py` | Competency chưa phủ, câu hỏi trùng tín hiệu, thiếu answer anchor, selection-rate ratio dưới 0.80 |
| `summarize_eval_run.py` | Pass rate không kèm khoảng tin cậy; run quá nhỏ; judge chưa được validate bằng nhãn người |
| `score_portfolio_options.py` | Hard gate bị đánh đổi trong công thức; chênh lệch thứ hạng chỉ là nhiễu |
| `check_training_serving_skew.py` | Feature thiếu khi serving, đổi dtype, category chưa từng thấy chiếm traffic thật |
| `check_model_promotion_readiness.py` | Approval gắn sai artifact hash hoặc sai stage; monitor chỉ được nêu tên; rollback chưa test |

Cộng thêm các validator schema cho learner memory, second-brain vault, chuyển đổi sách, content
manifest, personal-project manifest và portfolio evidence.

### Stack-native adapter

98 gói adapter. Sau khi chọn task, Claude nhận diện stack và version thật rồi chỉ đọc **đúng
adapter khớp** — dbt, Snowflake, BigQuery, Databricks, Microsoft Fabric, Airflow, Spark, Kafka,
Power BI, Tableau, Looker, Metabase, Superset và nhiều hơn.

---

## Cấu trúc repo

```
.
├── .claude-plugin/       plugin manifest và marketplace entry
├── .agents/agents/       Antigravity custom agent, mỗi phòng ban một cái  ← SINH RA
├── .github/workflows/    CI: build, validate, regress, audit, kiểm determinism
├── commands/             45 slash command (13 control + 32 phòng ban sinh ra)
├── hooks/                guard cho production, publishing và hành động phá hủy
├── skills/               32 role skill progressive-disclosure  ← SINH RA
│   └── <role>/
│       ├── SKILL.md              entry point, chỉ metadata luôn hiển thị
│       ├── references/
│       │   ├── catalog-*.md      routing shard, nạp từng cái một
│       │   ├── tasks/*.md        827 atomic task contract
│       │   └── adapter-*.md      gói adapter theo stack
│       ├── assets/               template bản ghi và JSON Schema
│       └── scripts/              evidence chạy được  ← viết tay
├── workflows/            một manifest chạy được cho mỗi skill  ← SINH RA
├── app/                  Data Agent — app desktop chọn skill và canvas workflow
├── schemas/              12 JSON Schema Draft 2020-12
├── evaluations/          case routing, lifecycle, confusion-pair và contract
├── tools/                build, validate, audit và đóng gói tất định
├── docs/                 tài liệu dài
├── suite-manifest.yaml   danh mục role chuẩn
├── task-catalog.json     catalog task máy đọc được
├── AGENTS.md             entry point cho agent không phải Claude Code
├── CLAUDE.md             hướng dẫn project cho Claude Code
└── CHANGELOG.md
```

> **`skills/` là nội dung sinh ra.** Sửa tay sẽ bị lần build kế tiếp ghi đè. Hãy sửa
> [docs/skill-map.md](docs/skill-map.md) hoặc [tools/build_suite.py](tools/build_suite.py)
> — xem [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Build và kiểm chứng từ source

Yêu cầu: Python 3.10+, PyYAML, Git, và Claude Code để validate plugin native.

```bash
python tools/build_suite.py            # sinh lại skill, command, agent, manifest, plugin
python tools/generate_user_docs.py     # sinh lại catalog task tiếng Việt
python tools/validate_suite.py         # cấu trúc, contract, link, resource bắt buộc
python tools/validate_claude_skills.py # frontmatter, disclosure, command, hook, agent, manifest
python tools/run_smoke_tests.py        # case routing, lifecycle, catalog và confusion
python tools/run_benchmark_tests.py    # assertion adapter và fixture tất định
python tools/run_control_tests.py      # mọi script evidence và guard, cả hai chiều
python tools/audit_skills.py           # bảng điểm cấu trúc từng skill
```

### Bản hiện tại pass những gì

| Bộ kiểm | Kết quả |
|---|---|
| Skill / contract / command / agent | 32 / 827 / 49 / 32, 0 lỗi |
| Routing ngôn ngữ tự nhiên | 35 case |
| Role-confusion pair | 37 case |
| Catalog routing | 41 case |
| Lifecycle | 13 case |
| Benchmark adapter | 34 test |
| **Control test** | **52 check** |
| Validate plugin | `claude plugin validate --strict` pass |
| Determinism | build lần hai là no-op |

`run_control_tests.py` assert cả **đường từ chối**, không chỉ đường thuận: claim hoàn thành mà
không có evidence, hoàn thành R4 mà không có approval, hash artifact giả, approval hết hạn, vi
phạm constitution, symbol không có trong index, telemetry lẫn user content, ledger rỗng báo
unknown thay vì good, và installer từ chối ghi đè file không phải của nó.

### Audit nói thật về những gì chưa xong

`audit_skills.py` báo **0 finding trên 32 skill**. v3.6.0 mang 13 finding một cách công khai:
chín skill có 20+ contract mà không có script evidence, và bốn catalog shard vượt ngưỡng tập
trung 55%. Cả 13 đã đóng ở v3.7.0 — chín script mới, và sharding theo tỷ trọng.

Phần còn chưa xong hẹp hơn và được nêu rõ trong release notes: chín script mới đã được kiểm
bằng fixture tự dựng cho cả đường pass lẫn đường fail, nhưng chưa có unit test riêng và CI mới
chỉ import chứ chưa chạy chúng.

`mean_thin_share` là **0.00%**: cả 827 contract đều mang ít nhất một resource riêng của task.

---

## Tài liệu

| Tài liệu | Nội dung | Ngôn ngữ |
|---|---|---|
| [docs/skill-and-task-catalog.md](docs/skill-and-task-catalog.md) | Toàn bộ 32 skill và 827 workflow: ownership, ranh giới, resource | Tiếng Việt |
| [docs/installation-and-usage.md](docs/installation-and-usage.md) | Cài plugin, project-scope, user-scope; routing; prompt; xử lý sự cố | Tiếng Việt |
| [docs/capability-overview.md](docs/capability-overview.md) | Tóm tắt năng lực | Tiếng Việt |
| [docs/skill-map.md](docs/skill-map.md) | **Taxonomy chuẩn** — nguồn mà build đọc vào | Tiếng Anh |
| [docs/lifecycle-operating-model.md](docs/lifecycle-operating-model.md) | Stage gate, risk tier, execution path | Tiếng Anh |
| [docs/operating-guide.md](docs/operating-guide.md) | Hướng dẫn maintainer về build pipeline | Tiếng Anh |
| [docs/source-integration-audit.md](docs/source-integration-audit.md) | Nguồn bên thứ ba được tham chiếu và giấy phép của chúng | Tiếng Anh |
| [AGENTS.md](AGENTS.md) | Entry point cho agent không phải Claude Code | Tiếng Anh |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Cách sửa bộ skill mà không làm vỡ build | Tiếng Anh |
| [CHANGELOG.md](CHANGELOG.md) | Lịch sử release | Tiếng Anh |

---

## Giấy phép

**Proprietary — bảo lưu mọi quyền.** Việc publish repo này **không** cấp bất kỳ quyền sử dụng,
sao chép, sửa đổi hay phân phối lại nào. Xem [LICENSE](LICENSE).

Đổi sang giấy phép mã nguồn mở là quyết định phải do chủ sở hữu bản quyền đưa ra tường minh.
Các dự án bên thứ ba được tham chiếu vẫn chịu giấy phép riêng của chúng; repo này **không** nhúng
mã nguồn bên thứ ba nào. Xem [docs/source-integration-audit.md](docs/source-integration-audit.md).
