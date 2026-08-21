# Data Department Agent Skills

A governed operating system for an entire Data Department, packaged as a Claude Code plugin.
**32 role skills**, **815 atomic task contracts**, **45 slash commands**, **49 executable
evidence scripts**, **12 JSON Schemas**, and a production guard hook.

[![Validate](https://github.com/kina2711/data-department-agent-skills/actions/workflows/validate.yml/badge.svg)](https://github.com/kina2711/data-department-agent-skills/actions/workflows/validate.yml)

Current release: **v3.7.0** · Works with **Claude Code**, **OpenAI Codex** and **Google Antigravity**

🇻🇳 [Đọc bản tiếng Việt](README.vi.md)

---

## What problem this solves

An agent with 800 workflows and no controls is worse than an agent with ten, because it will
confidently claim work it never did. Three failures show up over and over:

1. **Invented completion.** "Deployed to production", "tests passed", "the stakeholder
   approved" — asserted, never evidenced.
2. **Structural decay.** Code is generated faster than architecture review absorbs it. Tests
   stay green while cycles appear and settled decisions get quietly renegotiated.
3. **Ownership drift.** Ambiguous requests get answered by whichever role sounds closest, so
   nobody owns the outcome and the handoff never happens.

Every mechanism here exists to make one of those three detectable rather than deniable.

**Design position:** `not-run`, `incomplete` and `unknown` are honest statuses, and none of
them may be reported as success. A high failure rate triggers investigation, never a weaker
gate. Nothing here claims production execution, publishing, access change, deletion,
certification or model promotion without evidence and named human approval.

---

## Table of contents

- [Installation](#installation)
- [Other agent harnesses](#other-agent-harnesses)
- [Quick start](#quick-start)
- [How routing works](#how-routing-works)
- [The 32 departments](#the-32-departments)
- [Slash commands](#slash-commands)
- [Governance controls](#governance-controls)
- [Executable evidence](#executable-evidence)
- [Repository layout](#repository-layout)
- [Building and validating from source](#building-and-validating-from-source)
- [Documentation](#documentation)
- [Licence](#licence)

---

## Installation

Requires **Claude Code** and **Python 3.10+** on `PATH` as `python` (the guard hook and every
evidence script need it; both fail open if it is missing).

### Option 1 — from a release archive (recommended)

```powershell
# Windows
$pluginRoot = "C:\Tools\data-department-agent-skills-v3.7.0"
Expand-Archive .\data-department-claude-plugin-v3.7.0.zip -DestinationPath $pluginRoot
claude plugin validate --strict $pluginRoot
claude --plugin-dir $pluginRoot
```

```bash
# macOS / Linux
pluginRoot=~/tools/data-department-agent-skills-v3.7.0
unzip data-department-claude-plugin-v3.7.0.zip -d "$pluginRoot"
claude plugin validate --strict "$pluginRoot"
claude --plugin-dir "$pluginRoot"
```

The extracted directory must contain `.claude-plugin/plugin.json`, `skills/`, `commands/`
and `hooks/`. If any is missing the plugin loads a subset of itself, silently.

### Option 2 — from the marketplace manifest

The repository publishes itself as a single-plugin marketplace
(`.claude-plugin/marketplace.json`):

```
/plugin marketplace add kina2711/data-department-agent-skills
/plugin install data-department-agent-skills
```

### Option 3 — from source, for development

```bash
git clone https://github.com/kina2711/data-department-agent-skills.git
cd data-department-agent-skills
python -m pip install PyYAML
python tools/build_suite.py
python tools/validate_claude_skills.py
claude --plugin-dir .
```

### Verifying the install

```
/dd-catalog profiling
```

It should return matching task IDs from the 815-task catalog. If it answers from general
knowledge instead of the catalog, the plugin is not loaded.

---

## Other agent harnesses

The suite is not Claude-only. Codex uses the same `name` + `description` SKILL.md frontmatter,
so there is no translation layer — the installer links the same directories rather than
duplicating them.

| Harness | Reads | Surface |
|---|---|---|
| **Claude Code** | `.claude-plugin/`, `skills/`, `commands/`, `hooks/` | Full: 45 commands, production guard hook |
| **OpenAI Codex** | `AGENTS.md`, `.codex/skills/<name>/SKILL.md` | 32 skills, routed implicitly or by name |
| **Google Antigravity** | `AGENTS.md`, `.agents/agents/<name>.md`, `.agents/skills/` | 32 custom agents, one per department |
| Any AGENTS.md harness | `AGENTS.md`, `skills/<name>/SKILL.md` | 32 skills |

```bash
# install into a target project
python tools/install_agent_harness.py /path/to/project --harness codex
python tools/install_agent_harness.py /path/to/project --harness antigravity
python tools/install_agent_harness.py /path/to/project            # all three

python tools/install_agent_harness.py /path/to/project --dry-run  # show every action first
python tools/install_agent_harness.py /path/to/project --uninstall
```

**It links rather than copies**, so one rebuild of the suite updates every installed harness at
once. Where symlinks are unavailable — Windows without Developer Mode — it falls back to
copying and **says so**, because a silent copy that later goes stale is worse than a loud one.
Use `--copy` to force that, and re-run after every rebuild.

**It refuses to overwrite anything it did not create.** An install record at
`.data-department-install.json` tracks what belongs to it; `--force` overrides, `--uninstall`
removes exactly what it added and nothing else.

### Antigravity specifics

`.agents/agents/` holds one custom agent per department, generated by the build. Each pins
`commandExecutionPolicy: sandbox` — this suite never claims production execution without
evidence and named approval, and the agent definition should not quietly grant it. `tools` is
deliberately left unset so the harness default applies rather than freezing a tool list that
will age.

### Codex specifics

Codex reads `AGENTS.md` from the Codex home directory first, then walks from the repository
root down to your working directory, with closer files overriding earlier ones. Skills land at
`.codex/skills/<name>/SKILL.md` for repo scope, or `~/.codex/skills/` for user scope.

> Codex **custom prompts are deprecated** in favour of skills, so this suite ships no
> `~/.codex/prompts/` files. The 13 control commands remain Claude Code-only; under Codex and
> Antigravity, ask for the same thing in natural language.


---

## Quick start

**You do not need to memorise task IDs.** Ask in plain language, in any language:

```
Hai dashboard đang ra hai con số khác nhau cho cùng một KPI doanh thu. Tìm nguyên nhân.
```

Claude resolves the owning role, selects one atomic task, reads its contract completely, and
applies that contract's lifecycle profile, risk tier and execution path.

When you want explicit control, drive it with commands:

```
/dd-route Build an incremental dbt model for order events on BigQuery
/dd-task ae-build-incremental-model
/dd-verify task-result.json evidence.json ./artifacts
/dd-handoff ae-build-incremental-model data-quality-and-reliability
```

A typical governed session:

```
/dd-constitution ratify          # lock the tech stack and architecture rules first
/dd-scan .                       # baseline the structure before changing anything
/dd-ae Add an incremental model for order events
/dd-verify                       # machine-checked evidence, not a summary
/dd-approve                      # does an approval actually authorise this?
/dd-handoff                      # transfer ownership with evidence attached
```

---

## How routing works

```
natural-language request
   ↓  route by primary deliverable, never by job title
one owning role skill                    (32 candidates)
   ↓  read ONE catalog shard, not all of them
one canonical atomic task                (815 contracts)
   ↓  read that contract completely
Plan → Assess → Design → Execute → Test → Review/Approve → Release/Handoff → Monitor/Improve
```

**Progressive disclosure is the point.** Only skill descriptions sit in context permanently.
Claude then loads one `SKILL.md`, one catalog shard, one task contract, and only the
references that contract names. The 815 contracts and 98 stack adapters are never loaded
together.

Catalogs shard by intent — plan/design, build/deliver, test/assure, operate/improve — and any
shard that would exceed 11 tasks splits again by deliverable topic
(`catalog-plan-design-diagram.md`), so no single file carries most of the routing.

### Risk tiers decide how much control applies

| Tier | Typical work | Minimum control |
|---|---|---|
| `R0-light` | Read-only lookup, bounded analysis | Evidence and self-check |
| `R1-reviewed` | Design, documentation, advisory | Peer or domain review |
| `R2-standard` | Reversible build, people workflow | Automated test and owner review |
| `R3-controlled` | Production, access, sensitive data, material cost | Independent test, explicit approval, rollback, monitoring |
| `R4-critical` | Destructive, regulatory, certified decision | Segregated approval, strongest evidence, rehearsed recovery, audit trail |

The `R0` fast path is for genuinely read-only work. Risk is never downgraded to meet a
deadline.

---

## The 32 departments

Each department is one slash command, grouped by sprint stage. The count is that role's
atomic tasks.

### Think — understand before building

| Command | Department | Tasks |
|---|---|---|
| `/dd-hod` | Head of Data and Data Product | 21 |
| `/dd-ba` | Data Business Analysis | 24 |
| `/dd-analysis` | Data Analysis | 29 |
| `/dd-onboard` | Data Onboarding and Integration | 34 |
| `/dd-context` | Company Data Context | 9 |

### Plan — decide structure and sequence

| Command | Department | Tasks |
|---|---|---|
| `/dd-arch` | Data Architecture | 22 |
| `/dd-orchestrate` | Data Department Orchestrator | 20 |

### Build — produce the artefact

| Command | Department | Tasks |
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

### Review — authority and safety

| Command | Department | Tasks |
|---|---|---|
| `/dd-govern` | Data Governance and Stewardship | 22 |
| `/dd-security` | Data Security and Privacy | 16 |

### Test — prove it works

| Command | Department | Tasks |
|---|---|---|
| `/dd-quality` | Data Quality and Reliability | 21 |
| `/dd-experiment` | Product Analytics and Experimentation | 17 |

### Ship — release and operate

| Command | Department | Tasks |
|---|---|---|
| `/dd-platform` | Data Platform and DataOps | 21 |
| `/dd-mlops` | MLOps | 23 |
| `/dd-content` | Technical Content and Social | 27 |

### Reflect — learn, teach, grow

| Command | Department | Tasks |
|---|---|---|
| `/dd-career` | Data Career and Interview Coach | 50 |
| `/dd-brain` | Personal Second Brain and Knowledge OS | 46 |
| `/dd-book` | Book to Knowledge and Action | 45 |
| `/dd-hire` | Data Talent and Interviewing | 41 |
| `/dd-academy` | Data Academy and Curriculum | 39 |
| `/dd-docs` | Data Documentation and Diagrams | 20 |
| `/dd-enable` | Data Enablement and Knowledge | 17 |

Full detail — ownership, boundaries, resources and all 815 workflows — is in
[docs/skill-and-task-catalog.md](docs/skill-and-task-catalog.md).

---

## Slash commands

Thirteen control commands sit alongside the 32 departments. All are user-invoked; they do not
fire on their own.

### Routing and navigation

| Command | Does |
|---|---|
| `/dd-route <request>` | Resolves one owning role and one canonical task **without executing** |
| `/dd-catalog <keyword>` | Searches the 815-task catalog by keyword, role prefix or deliverable |
| `/dd-task <task-id>` | Loads one contract completely; reports readiness, gates, tests, approvals |
| `/dd-navigate <symbol>` | Answers code questions from a symbol index instead of reading whole files |
| `/dd-recall <question>` | Retrieves prior work from indexed traces with **zero model calls** |

### Execution and evidence

| Command | Does |
|---|---|
| `/dd-status` | Reports validated run state, blockers, next permitted action |
| `/dd-verify` | Runs the evidence chain; returns passed / failed / **incomplete** |
| `/dd-approve` | Checks whether an approval record actually authorises a gated action |
| `/dd-handoff` | Produces a handoff package with evidence, residual risks, next owner |

### Governance and improvement

| Command | Does |
|---|---|
| `/dd-constitution` | Ratifies and enforces locked technology and blocking architecture rules |
| `/dd-scan [path]` | Measures structural drift: cycles, depth, coupling, inequality, duplication |
| `/dd-instinct` | Records and scores reusable patterns; confidence derived from counted outcomes |
| `/dd-skill-quality` | Scores task contracts against recorded outcomes and opens change requests |

> `/dd-quality` opens the **Data Quality** department (quality of your data).
> `/dd-skill-quality` scores **this suite's own contracts**. Different things.

---

## Governance controls

### Project constitution — stop silent renegotiation

The failure: an agent implements a feature and quietly swaps a settled technology along the
way. A constitution records principles, a technology stack with per-layer `locked` flags and
`alternatives_rejected`, blocking architecture rules, and an amendment policy.

```bash
python skills/shared-data-core/scripts/validate_constitution.py project-constitution.json \
  --proposal-file plan.md
```

```
VIOLATION: proposal names 'Snowflake' for locked layer 'warehouse',
           which is decided as 'BigQuery' in ADR-004
BLOCKED: 1 constitution violation(s); amend explicitly or change the plan
```

Exit `3` is **blocked**, not a warning to note and walk past. Changing a locked layer,
unlocking one, or removing a blocking rule without a version bump and a named approver is a
violation.

### Production guard hook

`hooks/guard_production_action.py` intercepts shell commands before they run: git pushes and
force pushes, `terraform`/`pulumi` apply and destroy, Kubernetes and Helm mutations, cloud and
object-storage deletion, `DROP`/`TRUNCATE`, `DELETE` without a `WHERE`, dbt runs against a
production target, orchestrator backfills, package and release publication, and `rm -rf`.

It returns **only `ask`** — never `deny`. The approval it demands can only come from a human,
so the decision stays with you. An unreadable payload or a missing interpreter exits silently
into the normal permission flow, so an environment failure can never silently widen access.

### Architecture drift sensor

```bash
python skills/data-architecture/scripts/scan_architecture_drift.py . --max-depth 5 --gate 8000
```

Five components out of 2000 each — modularity, acyclicity, depth, equality, redundancy — with
cycles (Tarjan SCC), longest dependency chain, module size inequality (Gini), and duplicated
line windows reported with file and line. `--baseline` fails on regression.

**Stated limit:** regex import extraction, not a parse. It misses dynamic imports, aliases and
re-exports, and understands no semantics. A high score is not proof the architecture is sound.
For an exact answer use a tree-sitter tool such as Sentrux and cite that instead.

### Confidence-scored instincts

A pattern is not a rule because it worked once. Confidence is the **Wilson lower bound** of the
observed success rate, so a small sample scores low by construction:

| Observations | Confidence | Status |
|---|---|---|
| 9 applied, 9 succeeded | 0.70 | `active` |
| 2 applied, 1 succeeded | 0.09 | `proposed` — one lucky run |
| 8 applied, 7 succeeded, unconfirmed 7 months | 0.53 | `weakening` — re-test first |
| 10 applied, 2 succeeded | 0.06 | `retired` |

Only `active` instincts may shape behaviour. Recording a single failure against a 9/9 instinct
demotes it. Instincts store a trigger, an action, a rationale and a count — never transcripts,
prompts, secrets or data values.

### Contract quality loop

`/dd-skill-quality` scores the suite's own contracts from privacy-minimised telemetry and
recommends `observe`, `healthy`, `fix-routing`, `investigate`, `derive-variant` or
`tighten-evidence`.

`fix-routing` fires on tasks with **100% completion and 75% override** — completion alone hides
a routing defect where the work succeeded but the wrong contract did it. Recommendations are
change requests with evidence attached, never direct edits. Telemetry carrying `user_content`
is rejected outright.

### Token-free recall and navigation

`/dd-recall` indexes notes and traces into an entity-context graph plus a temporal hierarchy,
then retrieves by deterministic scoring — returning `source:line` pointers into the original
spans, never generated prose. A query with no match exits `2` and reports unknown.

`/dd-navigate` answers "where is this defined, who calls it, what breaks if it changes" from a
symbol index. Explaining one function in this repository's `tools/` returned **1169 bytes
instead of 425360** — 99.7% less than reading the seven files involved.

Both state their scope honestly: indexing and ranking make zero model calls, but reading the
returned spans still costs context, and the lexical implementation has no encoder.

### Cross-skill learning memory

`mastered` cannot be inferred from reading, attendance or chat history. It requires verified
evidence, sufficient confidence, a demonstrated transfer and a valid review date. Fresh
prerequisites are compressed; stale, conflicted, version-shifted or safety-critical ones are
expanded and retested.

```
Tôi đã hoàn thành Airflow với project và bài test. Giờ học dbt.
```

The dbt task receives only the orchestration/transformation boundary, the invocation
interface, retry/idempotency decisions and relevant failure modes. DAG fundamentals are not
taught again — unless the Airflow review is overdue, in which case they move into the retest
set.

---

## Executable evidence

49 scripts across the skills. **Standard library only** — they run on your machine with no
install step. Exit codes carry meaning everywhere:

| Exit | Meaning |
|---|---|
| `0` | Passed |
| `1` | Failed |
| `2` | Incomplete or unknown — a check could not run. **Not a pass** |
| `3` | Blocked by policy (constitution violation, must-have UAT gap) |

### The core chain

```bash
python skills/shared-data-core/scripts/validate_task_result.py result.json \
  --task-catalog task-catalog.json --mode complete
python skills/shared-data-core/scripts/validate_evidence_bundle.py evidence.json \
  --artifact-root ./artifacts --mode complete
python skills/shared-data-core/scripts/verify_deliverable.py result.json evidence.json \
  --artifact-root ./artifacts
```

`verify_deliverable.py` joins claims to evidence to artefact hashes and lists every claim no
verified evidence supports.

### Workflow and authority

| Script | Refuses |
|---|---|
| `validate_workflow.py` | Invalid state transitions, non-canonical task IDs |
| `validate_run_state.py` | A "complete" run carrying blockers or failed tests |
| `validate_approval_record.py` | Expired, out-of-scope or hash-mismatched approval |
| `validate_branch_plan.py` | Branches writing the same path, a dependency inside a parallel wave, a branch above the delegation ceiling, an undeclared merge policy |

### Domain controls

| Script | Catches |
|---|---|
| `validate_policy_coverage.py` | Assets missing owner/steward/retention for their classification; certification on an incomplete register; reviews over a year old |
| `validate_dashboard_spec.py` | Visuals bound to ungoverned metrics; silent grain changes; one measure at two grains; colour-only encodings |
| `validate_curriculum_coverage.py` | Objectives never assessed; prerequisite cycles; recall items claiming to verify an `apply` objective |
| `validate_requirements_traceability.py` | Acceptance criteria with no passing test; must-have gaps blocking UAT |
| `validate_tabular_data.py` | Bounded CSV/JSONL quality checks |
| `audit_change_scope.py` | Git changes outside the approved scope contract |
| `audit_repository.py` | Deterministic read-only inventory before qualitative judgement |
| `profile_dataset.py`, `explain_sql.py` | First-pass analysis evidence |
| `detect_data_stack.py` | Stack detection before binding an adapter |
| `validate_diagram_source.py` | Diagram sources with orphan nodes, duplicate ids, unbalanced blocks or no text equivalent |
| `score_onboarding_checkpoint.py` | A critical onboarding dimension averaged away into an "on track" mean |
| `summarize_terraform_plan.py` | Destroy and replace hidden inside a plan summary; stateful resources called out separately |
| `check_experiment_design.py` | Underpowered designs, uncorrected multiple testing, effects the traffic cannot detect |
| `audit_question_bank.py` | Uncovered competencies, redundant questions, unanchored scoring, selection-rate ratio below 0.80 |
| `summarize_eval_run.py` | Pass rates without an interval; runs too small to separate a fix from noise; unvalidated judges |
| `score_portfolio_options.py` | Hard gates traded off inside the arithmetic; rank differences that are noise |
| `check_training_serving_skew.py` | Features missing at serving, dtype changes, unseen categories carrying real traffic |
| `check_model_promotion_readiness.py` | Approval bound to a different artifact hash or stage; named-but-unconfigured monitors; untested rollback |

Plus schema validators for learner memory, second-brain vaults, book conversions, content
manifests, personal-project manifests, and portfolio evidence.

### Stack-native adapters

98 adapter packs. After a task is selected, Claude detects the real stack and version and reads
**only the matching adapter** — dbt, Snowflake, BigQuery, Databricks, Microsoft Fabric,
Airflow, Spark, Kafka, Power BI, Tableau, Looker, Metabase, Superset and more.

---

## Repository layout

```
.
├── .claude-plugin/       plugin manifest and marketplace entry
├── .github/workflows/    CI: build, validate, regress, audit, determinism check
├── .agents/agents/       Antigravity custom agents, one per department  ← GENERATED
├── commands/             45 slash commands (13 controls + 32 generated departments)
├── hooks/                production, publishing and destructive-action guard
├── skills/               32 progressive-disclosure role skills  ← GENERATED
│   └── <role>/
│       ├── SKILL.md              entry point, always-visible metadata only
│       ├── references/
│       │   ├── catalog-*.md      routing shards, loaded one at a time
│       │   ├── tasks/*.md        the 815 atomic task contracts
│       │   └── adapter-*.md      stack-native adapter packs
│       ├── assets/               record templates and JSON Schemas
│       └── scripts/              executable evidence  ← hand-written
├── schemas/              12 canonical Draft 2020-12 schemas
├── evaluations/          routing, lifecycle, confusion-pair and contract cases
├── tools/                deterministic build, validation, audit and packaging
├── docs/                 long-form documentation
├── suite-manifest.yaml   canonical role inventory
├── task-catalog.json     canonical machine-readable task catalog
├── AGENTS.md             cross-agent entry point
├── CLAUDE.md             Claude Code project instructions
└── CHANGELOG.md
```

> **`skills/` is generated.** Editing it by hand is overwritten by the next build. Change
> [docs/skill-map.md](docs/skill-map.md) or [tools/build_suite.py](tools/build_suite.py)
> instead — see [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Building and validating from source

Requirements: Python 3.10+, PyYAML, Git, and Claude Code for native plugin validation.

```bash
python tools/build_suite.py            # regenerate skills, commands, manifests, plugin
python tools/generate_user_docs.py     # regenerate the Vietnamese task catalog
python tools/validate_suite.py         # structure, contracts, links, required resources
python tools/validate_claude_skills.py # frontmatter, disclosure, commands, hooks, manifest
python tools/run_smoke_tests.py        # routing, lifecycle, catalog and confusion cases
python tools/run_benchmark_tests.py    # deterministic adapter and fixture assertions
python tools/run_control_tests.py      # every evidence script and guard rule, both directions
python tools/audit_skills.py           # per-skill structural scorecard
python tools/install_agent_harness.py <project> --dry-run   # multi-harness install
```

### What the current release passes

| Suite | Result |
|---|---|
| Skills / contracts / commands / agents | 32 / 815 / 45 / 32, 0 errors |
| Natural-language routing | 35 cases |
| Role-confusion pairs | 37 cases |
| Catalog routing | 41 cases |
| Lifecycle | 13 cases |
| Benchmark adapters | 34 tests |
| **Control tests** | **52 checks** |
| Plugin validation | `claude plugin validate --strict` passes |
| Determinism | a second build is a no-op |

`run_control_tests.py` asserts the **refusal** paths, not just the happy ones: a completion
claim with no evidence, an R4 completion without approval, a forged artefact hash, an expired
approval, a constitution violation, an unindexed symbol, telemetry carrying user content, and
an empty ledger reporting unknown rather than good.

### The audit is honest about what is unfinished

`audit_skills.py` reports **0 findings across 32 skills**. v3.6.0 carried 13 openly: nine
skills with 20+ contracts and no executable evidence script, and four catalog shards over the
55% concentration threshold. All 13 closed in v3.7.0 — nine new scripts, and share-aware
sharding.

What remains unfinished is narrower and named in the release notes: the nine new scripts were
verified against hand-built fixtures on both the passing and the failing path, but have no unit
suite of their own and CI does not exercise them beyond import.

`mean_thin_share` is **0.00%**: every one of the 815 contracts carries at least one
task-specific resource.

---

## Documentation

| Document | Contents | Language |
|---|---|---|
| [docs/skill-and-task-catalog.md](docs/skill-and-task-catalog.md) | All 32 skills and 815 workflows: ownership, boundaries, resources | Vietnamese |
| [docs/installation-and-usage.md](docs/installation-and-usage.md) | Plugin, project-scope and user-scope install; routing; prompts; troubleshooting | Vietnamese |
| [docs/capability-overview.md](docs/capability-overview.md) | Capability summary | Vietnamese |
| [docs/skill-map.md](docs/skill-map.md) | **Canonical taxonomy** — the source the build reads | English |
| [docs/lifecycle-operating-model.md](docs/lifecycle-operating-model.md) | Stage gates, risk tiers, execution paths | English |
| [docs/operating-guide.md](docs/operating-guide.md) | Maintainer guide to the build pipeline | English |
| [docs/source-integration-audit.md](docs/source-integration-audit.md) | Third-party sources referenced and their licences | English |
| [AGENTS.md](AGENTS.md) | Entry point for agents other than Claude Code | English |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to change the suite without breaking the build | English |
| [CHANGELOG.md](CHANGELOG.md) | Release history | English |

---

## Licence

**Proprietary - all rights reserved.** Publishing this repository grants no licence to use,
copy, modify or redistribute it. See [LICENSE](LICENSE).

Relicensing requires an explicit decision by the copyright holder. Referenced third-party
projects remain governed by their own licences; this repository incorporates no third-party
source code. See [docs/source-integration-audit.md](docs/source-integration-audit.md).
