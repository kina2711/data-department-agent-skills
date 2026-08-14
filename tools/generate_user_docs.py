from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "01_CHI_TIET_TOAN_BO_SKILL_VA_TASK.md"
CATALOG_ORDER = ["plan-design", "build-deliver", "test-assure", "operate-improve"]
CATALOG_LABELS = {
    "plan-design": "Plan / Design",
    "build-deliver": "Build / Deliver",
    "test-assure": "Test / Assure",
    "operate-improve": "Operate / Improve",
}
GENERIC_REFERENCES = {
    "lifecycle-standard.md",
    "safety-and-approvals.md",
    "technology-adapters.md",
    "industry-and-metrics.md",
    "role-routing.md",
    "execution-discipline-standard.md",
    "shared-reference-manifest.json",
}


ROLE_GUIDANCE = {
    "data-department-orchestrator": (
        "Điều phối yêu cầu mơ hồ, end-to-end hoặc có nhiều role; phân rã initiative thành chuỗi atomic task có owner, dependency, gate và handoff.",
        "Dùng khi đề bài chứa nhiều deliverable, cần dựng lại một repository, hoặc chưa rõ role nào sở hữu kết quả cuối.",
        "Không thay chuyên môn của các role. Mỗi task chỉ có một accountable owner; orchestrator quản lý workflow state, approval và thứ tự thực thi.",
    ),
    "shared-data-core": (
        "Cung cấp các kiểm soát nền dùng chung: phân loại request, tìm tài sản, đọc glossary/schema, profiling, access, evidence, approval và handoff.",
        "Dùng như dependency của mọi role khi cần context đáng tin cậy hoặc kiểm tra an toàn trước khi làm việc.",
        "Không sở hữu deliverable chuyên môn; không được dùng shared controls để né ownership của DA, DE, DG, DS hay role khác.",
    ),
    "company-data-context": (
        "Xây bộ nhớ doanh nghiệp có quản trị cho business terms, metrics, datasets, systems, owners, policies và platform environments.",
        "Dùng khi Claude cần company-specific context có provenance, version và ngày xác minh để tránh bịa giả định tổ chức.",
        "Context pack không thay thế việc kiểm tra live system đối với thông tin có thể thay đổi; không chứa secret hay raw sensitive data.",
    ),
    "head-of-data-and-data-product": (
        "Chuyển chiến lược kinh doanh thành data strategy, operating model, portfolio, roadmap, ưu tiên, service model và cơ chế đo giá trị/adoption.",
        "Dùng cho Head of Data, Data Product Manager, Data PM hoặc quyết định cấp portfolio và stakeholder governance.",
        "Sở hữu outcome, priority và capacity; implementation detail phải handoff cho Architecture, Engineering, Analytics hoặc Governance.",
    ),
    "data-business-analysis": (
        "Khám phá nhu cầu, quy trình, business rules, data/metric requirements, use cases, acceptance criteria, traceability và UAT readiness.",
        "Dùng khi business question chưa đủ rõ để thiết kế dữ liệu hoặc khi cần nối requirement tới design, implementation và test evidence.",
        "Không tự chuẩn hóa metric tranh chấp hay quyết định kiến trúc; chuyển đúng artifact cho Governance, Architecture, AE/DE và BI.",
    ),
    "data-architecture": (
        "Thiết kế current/target architecture, domain boundaries, data models, integration patterns, contracts, ADR, migration, resilience và guardrails.",
        "Dùng cho quyết định cấu trúc hệ thống hoặc thay đổi có nhiều downstream dependency và trade-off dài hạn.",
        "Không biến architecture thành implementation chưa được phê duyệt; mọi quyết định quan trọng cần alternatives, consequences và migration path.",
    ),
    "data-governance-and-stewardship": (
        "Quản trị ownership, stewardship, glossary, classification, policy, retention, access, certification, issues, council workflow và control evidence.",
        "Dùng khi cần định nghĩa authority, chuẩn hóa nghĩa dữ liệu, chứng nhận metric/data product hoặc xử lý ngoại lệ governance.",
        "Không tự cấp quyền, phê duyệt ngoại lệ hay tuyên bố compliance khi thiếu accountable authority và audit evidence.",
    ),
    "metadata-engineering-and-catalog": (
        "Thu thập và vận hành technical/business metadata, lineage, ownership, search, usage analytics, metadata APIs và chất lượng catalog.",
        "Dùng khi cần làm cho tài sản dữ liệu discoverable, traceable và có quan hệ nguồn–đích rõ ràng.",
        "Không suy diễn lineage hoặc ownership từ tên gọi; phải phân biệt metadata quan sát được, khai báo và đã được xác nhận.",
    ),
    "data-platform-and-dataops": (
        "Thiết kế và vận hành nền tảng dữ liệu: environments, orchestration, CI/CD, secrets, observability, capacity, cost, backup, DR và incidents.",
        "Dùng cho platform services, operational readiness và các thay đổi hạ tầng dùng chung cho nhiều workload.",
        "Production, secrets, access và recovery là controlled work; cần rollback, monitoring và approval đúng scope/version.",
    ),
    "data-developer-experience": (
        "Tạo golden paths, repository templates, scaffolding, local environments, CI feedback, standards và trải nghiệm tự phục vụ cho data developers.",
        "Dùng khi giảm cognitive load, setup time, inconsistency hoặc friction trong vòng đời phát triển dữ liệu.",
        "Không tối ưu DX bằng cách bỏ security, quality hay governance gates; đo hiệu quả bằng adoption, lead time và escaped defects.",
    ),
    "data-engineering": (
        "Thiết kế, xây, kiểm thử và vận hành batch/API/file/CDC/streaming pipelines với idempotency, schema evolution, reconciliation và recovery.",
        "Dùng cho ingestion, transformation ở tầng pipeline, orchestration, backfill, replay, troubleshooting và retirement.",
        "Không mặc định source semantics hoặc successful load; luôn kiểm tra grain, keys, watermark, duplicates, source-target reconciliation và rerun safety.",
    ),
    "analytics-engineering": (
        "Chuyển dữ liệu thô thành staging/intermediate/marts, semantic metrics và data products có tests, documentation, lineage và versioning.",
        "Dùng cho dimensional modeling, dbt-style workflows, incremental models, snapshots, SCD, metric layer và analytics PR review.",
        "Không tự chọn business definition đang tranh chấp; metric semantics cần BA/Governance approval trước khi certification hoặc release.",
    ),
    "data-analysis": (
        "Trả lời business questions bằng analysis plan, SQL/Python, EDA, segmentation, root-cause, forecasting nhẹ và insight có evidence.",
        "Dùng khi primary deliverable là câu trả lời phân tích, decision support hoặc analytical narrative thay vì production data product.",
        "Tách observation, inference và recommendation; không ngụy tạo causal claim, statistical certainty hoặc business confirmation.",
    ),
    "business-intelligence": (
        "Thiết kế, xây và vận hành dashboards/reports, semantic presentation, visualization, access, performance, UAT, release và adoption.",
        "Dùng khi deliverable chính là trải nghiệm BI cho người dùng hoặc báo cáo vận hành/executive.",
        "Không nhúng logic metric chưa được quản trị vào dashboard; release phải có data validation, usability/accessibility và owner acceptance.",
    ),
    "product-analytics-and-experimentation": (
        "Định nghĩa event taxonomy, tracking plans, funnels, cohorts, retention, attribution, A/B tests và product decision evidence.",
        "Dùng cho câu hỏi về hành vi sản phẩm, instrumentation hoặc thiết kế/đọc thí nghiệm.",
        "Không tuyên bố causal effect nếu assignment, exposure, power, guardrails hoặc validity checks không đạt.",
    ),
    "data-science": (
        "Đóng khung bài toán, xây dataset/features, baseline, experiments, statistical/ML models, explainability và model validation.",
        "Dùng cho discovery và development của mô hình hoặc nghiên cứu định lượng cần đánh giá ngoài mẫu.",
        "Không đồng nhất offline metric với business impact; deployment/serving thuộc MLE/MLOps và cần promotion gate riêng.",
    ),
    "machine-learning-engineering": (
        "Chuyển model thành phần mềm đáng tin cậy: training/inference code, feature pipelines, serving, performance, integration và release artifacts.",
        "Dùng khi trọng tâm là engineering của hệ thống ML, batch/online inference hoặc production integration.",
        "Không tự phê duyệt model quality/fairness; nhận validated model từ DS và handoff deployment/monitoring cho MLOps.",
    ),
    "mlops": (
        "Quản lý ML lifecycle trong production: registry, reproducibility, CI/CD/CT, promotion, deployment, monitoring, drift, incidents và rollback.",
        "Dùng khi model/version/environment cần được vận hành có kiểm soát và quan sát sau release.",
        "Không promote chỉ vì pipeline chạy thành công; cần validation, approval, canary/smoke, rollback và post-release monitoring.",
    ),
    "data-quality-and-reliability": (
        "Thiết kế rules, expectations, SLIs/SLOs, monitoring, anomaly detection, incident response, RCA, reconciliation và reliability improvement.",
        "Dùng cho assurance độc lập hoặc khi chất lượng/freshness/completeness gây ảnh hưởng downstream.",
        "Không che failed checks hoặc tự hạ threshold để pass; exceptions cần owner, expiry và residual-risk record.",
    ),
    "data-security-and-privacy": (
        "Thực hiện classification, threat/risk assessment, least privilege, encryption, privacy controls, audits, incidents và data-subject workflows.",
        "Dùng khi scope liên quan PII/confidential data, access, sharing, retention, deletion hoặc security posture.",
        "Không tự cấp quyền, xóa dữ liệu hay tuyên bố pháp lý; R3/R4 cần authority, segregation, evidence và recoverability thích hợp.",
    ),
    "master-data-management": (
        "Thiết kế và vận hành master/reference data, match-merge, survivorship, golden records, hierarchies, stewardship và distribution.",
        "Dùng khi nhiều source mô tả cùng entity và tổ chức cần bản ghi chuẩn có lineage và governance.",
        "Merge/survivorship phải giải thích được, reversible khi cần và không phá vỡ source-of-record authority.",
    ),
    "generative-ai-engineering": (
        "Thiết kế và xây RAG/LLM applications, prompts, retrieval, evaluations, guardrails, observability, cost và release controls.",
        "Dùng khi deliverable là hệ thống GenAI hoặc quy trình đánh giá chất lượng, safety và groundedness.",
        "Không đánh giá bằng demo đẹp hoặc một vài câu hỏi; cần eval set, failure taxonomy, red-team và production monitoring phù hợp.",
    ),
    "data-documentation-and-diagrams": (
        "Tạo và duy trì architecture diagrams, data flows, lineage views, runbooks, SOPs, dictionaries và documentation packages.",
        "Dùng khi primary deliverable là tài liệu/diagram có audience, scope, source và review cycle rõ ràng.",
        "Không vẽ quan hệ không có evidence; mọi tài liệu cần owner, version, freshness và liên kết tới artifact thực.",
    ),
    "data-enablement-and-knowledge": (
        "Xây knowledge articles, concept maps, linked/versioned libraries, office hours, communities, adoption và publishing workflows.",
        "Dùng khi tri thức đã được duyệt cần tổ chức để tìm kiếm, học, tái sử dụng hoặc xuất bản sang Notion/knowledge platform.",
        "Một note đơn lẻ khác với governed library; publishing là downstream handoff, còn source of truth phải có stable IDs, provenance và version.",
    ),
    "data-academy-and-curriculum": (
        "Thiết kế curriculum theo role/level, theory, labs, capstones, assessment, remediation, certification và knowledge deep dives.",
        "Dùng cho đào tạo có learning objectives, prerequisites, evidence of mastery và transfer sang tình huống mới.",
        "Không coi attendance hay đáp án học thuộc là competency; certification cần rubric, critical failures, calibration và retention/transfer evidence.",
    ),
    "data-onboarding-and-integration": (
        "Đưa nhân sự mới vào môi trường qua preboarding, access, context, role plan, buddy, checkpoints, readiness và knowledge transfer/offboarding.",
        "Dùng cho hành trình 7/30/60/90 ngày hoặc thay đổi role/team cần kiểm soát quyền và năng lực.",
        "Không xác nhận readiness chỉ dựa trên checklist; access dùng least privilege và completion cần evidence theo role.",
    ),
    "data-talent-acquisition-and-interview": (
        "Thiết kế hiring scorecards, sourcing/screening, structured interviews, role-specific rounds, rubrics, calibration, debrief và fairness audits.",
        "Dùng cho quy trình tuyển Data roles hoặc kiểm tra question bank đo đúng competency và evidence.",
        "Không leak answer anchors, không dùng protected traits, pedigree hay một câu hỏi làm single-point decision; quyết định cuối thuộc panel có thẩm quyền.",
    ),
    "data-career-and-interview-coach": (
        "Xây Career OS, career-stage competency map, evidence portfolio, capstone roadmap, technical-writing strategy, ethical visibility, interview readiness, remediation và review cycles.",
        "Dùng cho phát triển sự nghiệp Data bền vững, chuẩn bị interview, kiểm chứng career claims hoặc biến learning thành evidence có thể bảo vệ.",
        "Không bịa kinh nghiệm, hứa title/promotion, đánh đồng self-study với production hay biến public visibility thành proxy cho năng lực.",
    ),
    "data-personal-project-engineering": (
        "Biến vấn đề, user workflow, decision, ý tưởng, nguồn cảm hứng, dataset, repository, role gap, công nghệ, domain, kiến trúc, paper, course, incident hoặc constraints thành một personal data project có thesis và bằng chứng rõ ràng.",
        "Dùng khi xây learning/portfolio project, đặc biệt repo-first hoặc inspiration-first: kiểm tra provenance/license, audit hiện trạng, chọn reuse/adapt/replace/drop/build-new, thiết kế khác biệt và lập roadmap/test/evidence.",
        "Nguồn của người khác phải được attribution trung thực; biến nó thành luận đề và implementation của người dùng bằng khác biệt thực chất, không đổi tên/cosmetic clone hoặc tuyên bố sai rằng ý tưởng gốc hoàn toàn do mình nghĩ ra.",
    ),
    "data-technical-content-and-social": (
        "Thiết kế và vận hành technical series từ research, knowledge map và canonical article tới code, diagrams, Facebook, LinkedIn, Substack, publishing và measurement.",
        "Dùng cho Airflow, dbt, Spark, Kafka hoặc chủ đề kỹ thuật cần một chuỗi nhất quán, có evidence và adaptation riêng theo kênh.",
        "Không viết social trước technical validation, copy một bài sang mọi kênh, hoặc bịa production experience, benchmark, authority và reader outcomes.",
    ),
    "personal-second-brain-and-knowledge-os": (
        "Xây và vận hành Bộ Não2 local-first theo 1_Nguon, 2_Wiki, 3_Toi và 4_Ket-Qua, từ migration/capture tới linked knowledge, personal context, retrieval, output, backup và reuse measurement.",
        "Dùng khi cần gom tài liệu từ Notion, Sheets, Lark, Obsidian hoặc file local thành hệ thống AI đọc được, tìm lại được và tạo output đúng nguồn lẫn chất riêng.",
        "Không trộn nguồn với suy luận hoặc chất riêng, không nạp secret mặc định, không coi output AI là Wiki fact và không đánh giá thành công bằng số lượng note.",
    ),
    "book-to-knowledge-and-action": (
        "Chuyển sách, PDF, EPUB, tài liệu hoặc source collection thành skill, Second Brain pack, Career/Interview/Project system, curriculum, workflow hoặc technical-content blueprint.",
        "Dùng khi cần extract frameworks, mental models, principles, techniques, anti-patterns, decision rules và applications với progressive loading và source traceability.",
        "Không chỉ tóm tắt chương, không bịa tên framework, không copy dài, không biến việc đọc thành production evidence và không publish derived content khi thiếu rights/authority.",
    ),
}


def escape_cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ").strip()


def parse_frontmatter(skill_file: Path) -> dict:
    text = skill_file.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, flags=re.S)
    if not match:
        raise ValueError(f"Missing frontmatter: {skill_file}")
    return yaml.safe_load(match.group(1))


def load_catalog_membership(skill_dir: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for catalog in CATALOG_ORDER:
        path = skill_dir / "references" / f"catalog-{catalog}.md"
        if not path.exists():
            continue
        for task_id in re.findall(r"^- `([^`]+)`", path.read_text(encoding="utf-8"), flags=re.M):
            result[task_id] = catalog
    return result


def main() -> None:
    manifest = yaml.safe_load((ROOT / "suite-manifest.yaml").read_text(encoding="utf-8"))
    tasks = json.loads((ROOT / "task-catalog.json").read_text(encoding="utf-8"))
    task_by_id = {task["id"]: task for task in tasks}
    task_total = sum(role["task_count"] for role in manifest["roles"])
    if task_total != len(tasks):
        raise ValueError(f"Manifest/catalog mismatch: {task_total} != {len(tasks)}")
    if set(ROLE_GUIDANCE) != {role["skill"] for role in manifest["roles"]}:
        raise ValueError("ROLE_GUIDANCE must describe every manifest role exactly once")

    lines: list[str] = [
        "# Chi tiết toàn bộ Data Department Skills và Atomic Tasks",
        "",
        f"> Phiên bản `{manifest['version']}` · `{manifest['top_level_skills']}` Claude role skills · `{manifest['atomic_tasks']}` atomic workflows.",
        "> Đây là catalog tra cứu đầy đủ được sinh từ `suite-manifest.yaml`, `task-catalog.json` và task contracts; không phải nội dung luôn được nạp vào context của Claude.",
        "",
        "## Mục lục",
        "",
        "- [1. Bộ skill này là gì](#1-bộ-skill-này-là-gì)",
        "- [2. Cách đọc catalog](#2-cách-đọc-catalog)",
        "- [3. Lifecycle và kiểm soát chung](#3-lifecycle-và-kiểm-soát-chung)",
        f"- [4. Bản đồ {manifest['top_level_skills']} skills](#4-bản-đồ-{manifest['top_level_skills']}-skills)",
        "- [5. Chi tiết từng skill và toàn bộ task](#5-chi-tiết-từng-skill-và-toàn-bộ-task)",
        "- [6. Cách chọn skill/task](#6-cách-chọn-skilltask)",
        "",
        "## 1. Bộ skill này là gì",
        "",
        "`data-department-agent-skills` là một operating system theo role cho toàn bộ phòng Data. Claude nhận đề bài bằng ngôn ngữ tự nhiên, chọn role theo ownership của primary deliverable, chọn đúng một atomic task, rồi áp dụng lifecycle và risk controls tương ứng.",
        "",
        "```text",
        "User request / đề bài / repository",
        "→ role routing",
        "→ primary deliverable",
        "→ one atomic task",
        "→ Plan → Assess → Design → Execute → Test",
        "→ Review/Approve → Release/Handoff → Monitor/Improve",
        "```",
        "",
        "Một atomic task là một đơn vị công việc có một deliverable chính và Definition of Done riêng. Task contract đầy đủ quy định trigger, goal, inputs/readiness, procedure, tests/evidence, approval, failure state và handoff.",
        "",
        "## 2. Cách đọc catalog",
        "",
        "Mỗi dòng task bên dưới có:",
        "",
        "- **Task ID:** định danh ổn định để routing và handoff; bình thường người dùng không cần nhớ.",
        "- **Nhiệm vụ:** outcome mà task phải đạt, không phải một thao tác nhỏ.",
        "- **Deliverable:** artifact chính dùng để chọn task khi nhiều task có từ khóa gần nhau.",
        "- **Lifecycle:** profile điều khiển mức độ planning, execution và verification.",
        "- **Risk / path:** mức kiểm soát và execution path tối thiểu.",
        "- **Contract:** liên kết tới file hướng dẫn đầy đủ Claude sẽ đọc sau khi task được chọn.",
        "",
        "Bốn catalog được tải theo nhu cầu để tối ưu token:",
        "",
        "| Catalog | Dùng cho |",
        "|---|---|",
        "| Plan / Design | Plan, define, design, map, specify hoặc tạo proposed artifact |",
        "| Build / Deliver | Build, implement, configure, teach, interview hoặc deliver artifact |",
        "| Test / Assure | Inspect, analyze, test, review, validate, assess, certify hoặc audit |",
        "| Operate / Improve | Deploy, release, monitor, recover, migrate, optimize, retire hoặc improve |",
        "",
        "## 3. Lifecycle và kiểm soát chung",
        "",
        "| Stage | Kết quả bắt buộc |",
        "|---|---|",
        "| Plan | Outcome, scope, owner, consumer, dependency, acceptance criteria và test strategy |",
        "| Assess | Current-state evidence, baseline, validated inputs, risk tier và blockers |",
        "| Design | Approach, alternatives, controls, observability và recovery path |",
        "| Execute | Versioned artifact/change trong môi trường và authority cho phép |",
        "| Test | Correctness, semantics, quality, integration, security/privacy, performance/recovery khi áp dụng |",
        "| Review / Approve | Findings được xử lý và accountable authority duyệt đúng version/scope |",
        "| Release / Handoff | Đúng artifact đã test được publish/deploy/bàn giao kèm evidence và owner |",
        "| Monitor / Improve | Outcome được quan sát; residual actions có owner và feedback quay lại quy trình |",
        "",
        "| Risk | Typical work | Control tối thiểu |",
        "|---|---|---|",
        "| R0-light | Read-only lookup, bounded analysis | Evidence và self-check |",
        "| R1-reviewed | Design, documentation, learning/advisory | Peer hoặc domain review |",
        "| R2-standard | Reversible build, people workflow | Practical/automated test và owner review |",
        "| R3-controlled | Production, access, sensitive, external, material cost | Independent test, explicit approval, rollback, monitoring |",
        "| R4-critical | Destructive, regulatory, breach, certified/high-impact decision | Segregated approval, strongest evidence, rehearsed recovery, audit trail |",
        "",
        f"## 4. Bản đồ {manifest['top_level_skills']} skills",
        "",
        "| # | Skill | Role | Tasks |",
        "|---:|---|---|---:|",
    ]

    for index, role in enumerate(manifest["roles"], start=1):
        anchor = role["skill"]
        lines.append(
            f"| {index} | [`{anchor}`](#skill-{anchor}) | {escape_cell(role['display_name'])} | {role['task_count']} |"
        )

    lines.extend(["", "## 5. Chi tiết từng skill và toàn bộ task", ""])

    seen_tasks: set[str] = set()
    for index, role in enumerate(manifest["roles"], start=1):
        slug = role["skill"]
        display = role["display_name"]
        skill_dir = ROOT / "skills" / slug
        metadata = parse_frontmatter(skill_dir / "SKILL.md")
        ownership, use_when, boundary = ROLE_GUIDANCE[slug]
        membership = load_catalog_membership(skill_dir)
        task_ids = sorted(path.stem for path in (skill_dir / "references" / "tasks").glob("*.md"))
        if len(task_ids) != role["task_count"]:
            raise ValueError(f"Task count mismatch for {slug}: {len(task_ids)} != {role['task_count']}")
        missing = set(task_ids) - set(task_by_id)
        uncataloged = set(task_ids) - set(membership)
        if missing or uncataloged:
            raise ValueError(f"Incomplete task metadata for {slug}: missing={missing}, uncataloged={uncataloged}")
        seen_tasks.update(task_ids)
        distribution = Counter(membership[task_id] for task_id in task_ids)
        references = sorted(
            path.name
            for path in (skill_dir / "references").glob("*.md")
            if not path.name.startswith("catalog-") and path.name not in GENERIC_REFERENCES
        )
        assets = sorted(path.name for path in (skill_dir / "assets").glob("*") if path.is_file())
        scripts = sorted(path.name for path in (skill_dir / "scripts").glob("*") if path.is_file())

        lines.extend(
            [
                f'<a id="skill-{slug}"></a>',
                "",
                f"### {index}. `{slug}` — {display}",
                "",
                f"**Claude trigger description:** {metadata['description']}",
                "",
                f"**Ownership:** {ownership}",
                "",
                f"**Khi nên dùng:** {use_when}",
                "",
                f"**Ranh giới và handoff:** {boundary}",
                "",
                f"**Quy mô:** {len(task_ids)} tasks — "
                + "; ".join(
                    f"{CATALOG_LABELS[catalog]} {distribution.get(catalog, 0)}" for catalog in CATALOG_ORDER
                )
                + ".",
                "",
            ]
        )
        if references:
            lines.append("**Domain references tải khi cần:** " + ", ".join(f"`{name}`" for name in references) + ".")
            lines.append("")
        if assets:
            lines.append("**Templates/assets có thể tái sử dụng:** " + ", ".join(f"`{name}`" for name in assets) + ".")
            lines.append("")
        if scripts:
            lines.append("**Scripts:** " + ", ".join(f"`{name}`" for name in scripts) + ".")
            lines.append("")

        for catalog in CATALOG_ORDER:
            ids = [task_id for task_id in task_ids if membership[task_id] == catalog]
            if not ids:
                continue
            lines.extend(
                [
                    f"#### {CATALOG_LABELS[catalog]} ({len(ids)} tasks)",
                    "",
                    "| Task | Nhiệm vụ | Primary deliverable | Lifecycle | Risk / path |",
                    "|---|---|---|---|---|",
                ]
            )
            for task_id in ids:
                task = task_by_id[task_id]
                contract = f"skills/{slug}/references/tasks/{task_id}.md"
                lines.append(
                    "| "
                    + f"[`{task_id}`]({contract}) | "
                    + f"{escape_cell(task['goal'])} | "
                    + f"{escape_cell(task['output'])} | "
                    + f"`{escape_cell(task['lifecycle_profile'])}` | "
                    + f"`{escape_cell(task['risk_tier'])}` / `{escape_cell(task['execution_path'])}` |"
                )
            lines.append("")

    if seen_tasks != set(task_by_id):
        raise ValueError(f"Not all catalog tasks documented: {set(task_by_id) - seen_tasks}")

    lines.extend(
        [
            "## 6. Cách chọn skill/task",
            "",
            "Người dùng chỉ cần mô tả outcome. Claude tự route theo các quy tắc:",
            "",
            "1. Nếu yêu cầu có nhiều role/deliverable hoặc cần dựng lại repository, dùng `data-department-orchestrator`.",
            "2. Nếu deliverable đã rõ, chọn role sở hữu deliverable đó; không chọn chỉ vì job title xuất hiện trong prompt.",
            "3. Chọn catalog theo intent hiện tại: design khác build, test khác deploy.",
            "4. Chọn đúng một atomic task theo primary deliverable và đọc contract đầy đủ.",
            "5. Hoàn thành hoặc handoff task hiện tại trước khi chuyển sang task tiếp theo.",
            "6. Không tuyên bố execution/test/approval thành công nếu chưa có evidence.",
            "",
            "Prompt kiểm tra routing:",
            "",
            "```text",
            "Hãy phân tích yêu cầu và báo trước khi làm:",
            "- primary role skill",
            "- current atomic task ID",
            "- primary deliverable",
            "- lifecycle profile, risk tier và execution path",
            "- blockers/assumptions và acceptance criteria.",
            "Sau đó thực hiện task hiện tại, test, báo evidence, approval status, residual risks và next owner.",
            "```",
            "",
            f"Tổng kiểm: **{len(manifest['roles'])} skills / {len(seen_tasks)} tasks** đã được liệt kê, không thiếu và không trùng ownership trong catalog này.",
        ]
    )

    OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Generated {OUTPUT.name}: {len(manifest['roles'])} skills, {len(seen_tasks)} tasks")


if __name__ == "__main__":
    main()
