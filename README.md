# Data Department Agent Skills

Claude-native operating system for a complete Data Department: **32 role skills**, **802 atomic workflows**, risk-adaptive lifecycle controls, executable evidence gates and progressive loading.

Current release: **v3.1.0**.

## Start here

- [Chi tiết toàn bộ skill và task](01_CHI_TIET_TOAN_BO_SKILL_VA_TASK.md): ownership, boundaries, resources and all 802 atomic workflows.
- [Hướng dẫn import và sử dụng với Claude Code](02_HUONG_DAN_IMPORT_VA_SU_DUNG_CLAUDE.md): plugin, project-scope and user-scope installation; routing; prompts; validation and troubleshooting.
- [Tổng quan năng lực](02_TONG_QUAN_NANG_LUC_DATA_DEPARTMENT_SKILLS.md).

## Capability map

The suite covers:

- Data leadership/product, Business Analysis, Architecture, Governance, Metadata and Security.
- Data Platform/DataOps, Developer Experience, Data Engineering, Analytics Engineering, BI and Data Quality.
- Data Analysis, Product Analytics, Data Science, ML Engineering, MLOps and Generative AI Engineering.
- Documentation, Enablement, Academy, Onboarding, Hiring, Career/Interview and Technical Content.
- Personal Project Engineering, Personal Second Brain / Knowledge OS and Book-to-Knowledge / Skill / Action Engineering.
- Cross-role orchestration with task dependencies, evidence, approvals, handoffs and completion validation.

Claude may route from an ordinary natural-language request. Users do not need to remember individual task IDs.

## Install from a release

Download `data-department-claude-plugin-v3.1.0.zip` from the GitHub Release and extract it. Validate and start Claude Code from the target project:

```powershell
$pluginRoot = "C:\Tools\data-department-agent-skills-v3.1.0"
Expand-Archive .\data-department-claude-plugin-v3.1.0.zip -DestinationPath $pluginRoot
claude plugin validate --strict $pluginRoot
claude --plugin-dir $pluginRoot
```

The extracted directory must contain `.claude-plugin/plugin.json` and `skills/`.

## Use

Explicit plugin invocation:

```text
/data-department-agent-skills:data-department-orchestrator

Tôi có đề bài và một GitHub repository mẫu. Hãy audit read-only,
chọn workflow phù hợp, lập kế hoạch, build và test local.
Không push hoặc deploy nếu chưa được yêu cầu.
```

Implicit routing is also supported:

```text
Hãy xây Second Brain local từ Notion export, PDF, transcript và Obsidian.
Giữ nguyên nguồn, source lineage, privacy và representative retrieval tests.
```

## Architecture

```text
natural-language request
→ role ownership
→ one canonical atomic task
→ Plan → Assess → Design → Execute → Test
→ Review/Approve → Release/Handoff → Monitor/Improve
```

Only skill metadata is always visible. Claude loads one selected `SKILL.md`, one catalog shard, one task contract and conditional references/scripts as needed. The 802 task contracts are not loaded together.

## Validate from source

Requirements: Python 3.10+, PyYAML, Git and Claude Code for native plugin validation.

```powershell
python tools\build_suite.py
python tools\generate_user_docs.py
python tools\validate_suite.py
python tools\validate_claude_skills.py
python tools\run_smoke_tests.py
python tools\run_benchmark_tests.py
powershell -ExecutionPolicy Bypass -File tools\package_claude_plugin.ps1
```

The current release passes 34 routing cases, 36 role-confusion cases, 34 catalog-routing cases and 28 deterministic benchmark/control tests.

## Repository layout

```text
.claude-plugin/     Claude plugin manifest
skills/             32 progressive-disclosure role skills
schemas/            workflow, evidence and domain manifest schemas
evaluations/        routing, adversarial and forward-test evidence
tools/              deterministic build, validation and packaging scripts
suite-manifest.yaml canonical suite inventory
task-catalog.json   machine-readable atomic task catalog
```

## Safety and licensing

- Production changes, sensitive data, publishing and external actions remain gated by task risk, evidence and authority.
- The plugin manifest declares this release **Proprietary**. No open-source license or redistribution right is granted by publishing the repository. Change the license only through an explicit owner decision.
- Referenced third-party projects remain governed by their own licenses; see [source integration audit](SOURCE_INTEGRATION_AUDIT.md).

