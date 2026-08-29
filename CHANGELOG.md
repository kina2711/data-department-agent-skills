# Changelog

## v3.9.0

Three standards for things the suite could check structurally but never judged: whether prose is
worth reading, whether a diagram was derived from anything, and what a session loses when it ends.

32 role skills - 827 atomic task contracts - 45 slash commands - 32 Antigravity agents -
52 executable evidence scripts - 12 JSON Schemas

### Prose voice reaches the skills that write prose

The suite already had good voice rules, trapped in one skill. Academy, Career, Enablement and
Documentation — the four that produce the most explanatory prose — had none, so a note could pass
every structural check and still open with a scene-setting paragraph restating its own title.

- New shared reference `authored-prose-voice.md`, shipped to those four skills and to
  `shared-data-core`. It resolves the tension the ROOT note format creates: the summary line
  answers immediately, the reason section then starts from the problem — both rules hold, on
  different parts of the document.
- Named tells, each paired with what replaces it, in the language the corpus is written in.
  A ban list produces avoidance; a replacement produces writing.
- Register matching rather than voice imitation: producing text in a named person's voice for
  others to read is impersonation regardless of framing.
- It states its own limit. Fluent prose can be confidently wrong, and no qualifier is removed for
  reading weak when the claim genuinely is qualified.
- `validate_note_corpus.py` now flags filler phrasings, always as warnings and never as failures,
  because style is a judgment a regular expression does not get to make. Measured against 606
  repo documents it flags six, five of which are the standard itself listing its own examples.

### Diagrams say where they came from

`validate_diagram_source.py` stated in its own docstring that it cannot confirm a diagram is true.
Nothing else did either, and the skill owned no reference of its own across thirteen diagram tasks.

- New reference `diagram-fidelity-standard.md`. Every diagram declares itself `observed`,
  `proposed` or `illustrative` on the rendering rather than only in metadata, because a reader
  seeing it in a slide has no access to the file.
- Another diagram, a README, a ticket or recall is not inspection. A diagram derived from a
  diagram inherits its errors and none of its freshness.
- An observed diagram names the commit, tag or extraction timestamp it was read at; without one,
  "is this still true" has no answer and the diagram does not announce when it stops being true.
- Omission is a claim: what was excluded and why is recorded.
- `validate_diagram_source.py --provenance` cross-checks parsed node ids against
  `diagram-provenance.yaml` — unsourced nodes, missing version anchors, entries naming nodes the
  source does not contain, and elements sourced from another diagram. Its pass message now says
  what it did not verify.

### A session handoff carries what run state cannot

`run-state.yaml` records phase, current task, gates and blockers. It records nothing about how the
session arrived there, so a successor re-derives the reasoning, sometimes differently and
sometimes by repeating the approach already abandoned.

- New section in `context-engineering-standard.md`, and new task
  `orchestrator-write-session-handoff` with `session-handoff.yaml`.
- The document carries only what no spec, plan, ADR, issue, commit, diff or run-state record
  already holds; everything else is referenced by path or hash. A handoff that restates the plan
  is a second copy of the plan and will drift from it.
- What was tried and rejected, and the load-bearing assumption, are the fields that matter: they
  are the only content that disappears completely when the session does.
- It is written to the OS temporary directory, never into the workspace unless asked. A handoff
  written into the repository gets committed, then reviewed, then eventually believed.
- It is not evidence and not an approval. Gates the session left unpassed are listed as unpassed.

### Elsewhere

- `context-engineering-standard.md` now also ships to the orchestrator, which referenced it
  without having it; every `../*.md` link across all 827 contracts resolves.
- The suite grows from 826 to 827 atomic tasks.

## v3.8.0

A note-corpus pipeline for Academy, a concept registry that finally joins Career's canon to it,
and a Socratic diagnostic loop that proposes evidence without ever claiming mastery.

32 role skills - 826 atomic task contracts - 45 slash commands - 32 Antigravity agents -
52 executable evidence scripts - 12 JSON Schemas

### Note authoring moves to a fixed-phrase structure

- `knowledge-deep-dive-standard.md` is rewritten as a structural contract: a required section
  order with verbatim headings, a YAML front-matter contract carrying `ai_summary` and
  `relationships`, collapsible self-check answers, and strict content/instruction separation —
  note content describes and never issues commands to an agent. Bracket labels such as `[L1]`
  are prohibited; the fixed phrase is itself the retrieval signal.
- The standard now also governs `academy-write-theory-lesson`, `academy-create-worked-example`
  and `academy-create-learner-workbook`, not deep dives alone.
- `knowledge-deep-dive.yaml` is restructured to hold what the standard requires.

### A corpus is a deliverable, not a pile of notes

- New reference `note-corpus-operating-system.md`: sourced roadmap, skill tracks, corpus plan,
  module batches, audit, index — in one direction, resumable across sessions.
- Six new tasks: `academy-research-role-roadmap`, `academy-build-skill-track-map`,
  `academy-plan-note-corpus`, `academy-build-note-module`, `academy-audit-note-corpus`,
  `academy-index-note-corpus`.
- A roadmap presented as current names its sources with dates; `currency_claim` stays
  `not-claimed` while any step is uncited, and `role-curricula.md` is an input, never evidence.
- `note-corpus-manifest.json` is the resume anchor. Regenerating the plan mid-corpus renumbers
  IDs that existing notes point at, so changed roadmaps supersede rather than rewrite.
- One module, one writer: modules are claimed before building, and on a collision the module
  that produced no notes yields. `corpus-workflow-manifest.json` represents the whole flow for
  `validate_workflow.py`.
- New script `validate_note_corpus.py` — duplicate IDs, dangling relationship targets,
  prerequisite cycles, planned-but-missing files, unmanifested files, stale version-sensitive
  notes, tag-overlap duplicate candidates, and hollow sections: an empty decision table, fewer
  than two misconceptions, fewer than two self-check questions, a stub case study.

### One identity across four ID spaces

- New reference `concept-registry-standard.md`, shared by Academy and Career. Concept keys
  `ck.<domain>.<slug>` bind outward to canon IDs, note IDs, learner-memory topics, competencies
  and questions; nothing downstream is rewritten and `sd.*` keeps its meaning.
- Exactly one primary note per key. This makes duplication decidable rather than a judgment
  about tag similarity, and it gives coverage a single meaning: a canon ID is covered when a
  key bound to it has a primary note marked `reviewed`. A note that merely exists is not
  coverage.
- Notes may bind to a `proposed` key immediately so a corpus can start; only `registered` keys
  count, so a corpus built on proposed keys reports zero verified coverage rather than
  borrowing a number it does not have. The duplicate-coining risk this accepts is contained
  mechanically: near-duplicate proposed keys are reported while merging them is still cheap.
- New tasks `career-register-canonical-concept` and `career-bootstrap-concept-registry`.
- New script `validate_concept_registry.py` — unregistered keys in use, duplicate primaries,
  alias collisions, dangling bindings, `parents` cycles, near-duplicate keys, canon IDs with
  no key.
- `concept_keys` crosswalk fields added across six assets and, optionally, to
  `learner-memory.schema.json`; existing memory files stay valid.

### Diagnosis that proposes evidence instead of asserting it

- New reference `diagnostic-session-method.md`: three Socratic rounds per scenario, then teach
  directly, because questioning past productive struggle stops being Socratic. The resolving
  round is the evidence — unaided on an unseen surface proposes `demonstrated`, rounds one and
  two propose `practiced`, round three or direct teaching proposes `exposed`, and a previously
  seen scenario is recall rather than transfer.
- New task `academy-run-note-diagnostic` emits a learning event to Career and never writes
  mastery. Academy proposes; Career reconciles and decides.
- New task `academy-apply-misconception-feedback` closes the loop: the same misconception
  against one concept key in three or more distinct sessions is written back into the key's
  primary note. The edit is append-only and sets `status` to `needs-review`; a pattern from one
  learner is enough to add a warning and nowhere near enough to overturn deliberate content.
- New task `academy-prioritize-corpus-by-gap` ranks modules against a measured gap artifact,
  labelling each `measured`, `self-reported` or `assumed`.

### Freshness stops being a typed date

- New script `schedule_topic_review.py` computes `review_due_at` from demonstrated state,
  independent evidence count with diminishing returns, version sensitivity and dependent count.
  A computed due date is a scheduling decision, never evidence, and a topic that is not yet due
  is only not known to have decayed.

### Elsewhere

- The book skill gains a note-corpus destination: it supplies structure, locators and claim
  classification while Academy owns the manifest, coverage and any diagnostic use.
- Evaluation coverage for every new task — catalog routing, lifecycle profiles, two end-to-end
  routing scenarios and six confusion pairs — plus five fixtures, with all three new scripts
  exercised from the smoke suite. The first run caught a real defect:
  `academy-prioritize-corpus-by-gap` was routing to the wrong catalog group.
- The suite grows from 815 to 826 atomic tasks and from 49 to 52 evidence scripts.

## v3.7.0

System-design knowledge for Career, two cross-cutting reporting and design standards, a zero-finding
skill audit, and execution patterns the orchestrator could name but not run.

32 role skills - 815 atomic task contracts - 45 slash commands - 32 Antigravity agents -
49 executable evidence scripts - 12 JSON Schemas

System-design knowledge layer for Data Career, and a return path from published content.

- New reference `system-design-canon.md` in `data-career-and-interview-coach`: a registry of
  canonical concept IDs across ingestion, streaming, storage, distribution, processing, serving,
  reliability, governance and cost; the `Clarify -> Constrain -> Contract -> Component ->
  Consistency -> Cost -> Collapse` answer frame; and a source policy that treats curated
  third-party collections as pointers to primary sources, never as content to copy or adapt.
- New task `career-build-architecture-case-study` — deconstructs a public architecture into
  constraints, decisions, rejected alternatives, consistency, cost, failure modes and follow-up
  questions, with per-claim classification and an explicit third-party study label.
- New task `career-design-concept-visual-explainer` — specifies one visual mental model per
  concept and hands rendering to `data-documentation-and-diagrams`; it never reports a brief as
  a finished diagram.
- `career-build-question-deep-dive` now requires a visual mental model section in the dossier,
  and dossier concept links resolve against the system-design canon.
- Published content now returns to Career as a candidate claim through
  `content-evidence-return.yaml`, verified by `career-build-career-evidence-portfolio`. Reach,
  reactions and posting volume remain audience signals, never mastery evidence.
- Career grows from 46 to 48 atomic tasks; the suite from 809 to 811.

Two cross-cutting standards, applied to all 32 skills and all 811 contracts.

- New shared reference `response-compression.md`: `R0-light` and `R1-reviewed` results are
  reported in a compact shape — one state line, the deliverable, only the fields that carry
  content, one named next action, lists capped at five. It governs presentation only. Blocked
  gates, unrun checks, assumptions, limitations, residual risks and draft-versus-executed labels
  print in full at every risk tier, and `R2`+ still returns the full contract.
- New shared reference `solution-option-framing.md`: plan/design tasks step back and frame three
  to five materially different approaches in the new `design-option-set.yaml` asset, select one
  against the stated constraints in at most forty words, record why each rejected option lost and
  what would reopen the decision, then derive the deliverable structure from that selection.
  Roles that already own a scored selection artifact reuse it instead of duplicating the decision.
- `atomic-task-output.yaml` is now distributed to every skill, and `deep`/`enforced` contracts
  mirror their outcome into it. Where prose and the structured record disagree, the record stands.
- Both references join the shared-reference manifest, so a cross-role handoff deduplicates them
  by logical ID and SHA-256 instead of loading a second copy.

Deep upgrade: the audit closes at zero findings.

`tools/audit_skills.py` reported 13 findings across 13 skills. All 13 are now closed.

- Nine new executable evidence scripts, standard library only, for the nine skills that carried
  20+ contracts and no runnable check: `validate_diagram_source.py` (documentation),
  `score_onboarding_checkpoint.py` (onboarding), `summarize_terraform_plan.py` (platform),
  `check_experiment_design.py` (data science), `audit_question_bank.py` (talent),
  `summarize_eval_run.py` (generative AI), `score_portfolio_options.py` (head of data),
  `check_training_serving_skew.py` (ML engineering) and
  `check_model_promotion_readiness.py` (MLOps). Each is wired into the contracts that need it,
  and each states in its own docstring what it cannot verify.
- Catalog sharding is now share-aware: a group that would hold more than 55% of a skill's routing
  gets a tighter budget even when it fits the absolute one, and leftover tasks are distributed
  evenly instead of leaving a one-task orphan shard beside a full one. This closed the imbalance
  in the orchestrator, enablement, security/privacy and metadata catalogs.
- Career gains `career-build-offer-evaluation-and-negotiation-plan` — components valued
  separately, equity as a scenario rather than expected money, market ranges only from cited
  sources with date/region/level, an explicit walk-away position, and a standing refusal to coach
  a misstatement of current or competing compensation — and `career-audit-knowledge-coverage`,
  which measures preparation against registered canon concept IDs rather than questions practised.
- Content gains `content-audit-series-concept-coverage`: a mention is not coverage, and only a
  concept with an explanation, a worked artifact and a stated failure mode counts as taught.
- Career grows to 50 tasks, Content to 27, the suite to 814. Evidence scripts: 39 to 48.

Execution patterns: an independent reviewer, and a real path for parallel work.

- New task `orchestrator-run-producer-reviewer` with `producer-reviewer-method.md`. The rubric is
  fixed before production, the reviewer never receives the rationale behind the artifact until an
  independent verdict is recorded, producer and reviewer are never the same actor, and the loop
  caps at two rounds. Disagreement routes to the conflict register with both positions rather than
  being split, out-argued or broken by a tie-breaking third opinion. Reviewer acceptance is quality
  evidence and never owner approval.
- New reference `parallel-execution-and-agent-teams.md` gives the parallel and fan-out workflows an
  execution path they previously described but did not have. Branches must be disjoint in what they
  write, not merely in what they read; a dependency between branches means the work is sequential;
  a delegated branch never approves, publishes, mutates production or raises its own risk tier, and
  anything above the delegation ceiling stops at a proposal. Fan-in verifies each returned artifact
  against its expected hash, and a failed branch reports `partial` instead of quietly reducing
  scope. Correctness never depends on whether a harness can actually run branches concurrently.
- New script `validate_branch_plan.py` checks a wave before dispatch: write-path collisions,
  read-write hazards, in-wave dependencies, risk floors and the delegation ceiling against the
  canonical catalog, and an explicit merge policy. Without the catalog it exits `incomplete` (2)
  rather than passing.
- New assets `branch-delegation-contract.json`, `fan-in-merge-record.yaml` and
  `producer-reviewer-record.yaml`. The orchestrator SKILL.md now routes by execution pattern.
- Orchestrator grows to 20 tasks, the suite to 815. Evidence scripts: 48 to 49.

## v3.6.0

Multi-harness support and a Vietnamese README.

### Codex, Antigravity and any AGENTS.md harness

Codex reads skills at `.codex/skills/<name>/SKILL.md` using the same `name` + `description`
frontmatter this suite already uses, so no translation layer was needed. Antigravity reads
`AGENTS.md` plus custom agents at `.agents/agents/<name>.md`.

- `.agents/agents/` is now generated by `tools/build_suite.py` — one Antigravity custom agent
  per department, carrying the operating contract, the claims policy and a constitution check.
  Each pins `commandExecutionPolicy: sandbox`; `tools` is left unset so the harness default
  applies rather than freezing a list that will age. A collision guard refuses to generate over
  a hand-written agent.
- `tools/install_agent_harness.py` installs the suite into a target project for `codex`,
  `antigravity`, `claude` or all three. It **links rather than copies** so one rebuild updates
  every installed harness, falls back to copying with a warning where symlinks are unavailable,
  refuses to overwrite any path it did not create, records what it installed in
  `.data-department-install.json`, and can uninstall exactly that and nothing else.
- `validate_claude_skills.py` now validates the Antigravity surface: frontmatter fields against
  the documented schema, `model` and `commandExecutionPolicy` enums, name/filename agreement,
  and that every `skills:` reference resolves to a real directory.
- `AGENTS.md` gained a supported-harness table.

Codex custom prompts are deprecated in favour of skills, so no `~/.codex/prompts/` files are
shipped. The 13 control commands remain Claude Code-only; under Codex and Antigravity the same
work is requested in natural language.

### Documentation

- `README.md` rewritten earlier in this cycle now carries an "Other agent harnesses" section.
- **`README.vi.md`** added: a full Vietnamese edition, cross-linked from the English README.
  Every figure was diffed against the English version — version, control-test count, audit
  findings, `mean_thin_share`, the context-saving measurement and all 32 department task
  counts match.

### Validation

- 32 skills, 809 contracts, 45 commands, **32 Antigravity agents**, 0 errors.
- **52 control tests** (was 46). The 6 new ones cover the installer: a dry run that touches
  nothing, Codex and Antigravity installs landing in the right paths, a refusal to overwrite a
  path the installer did not create, a refusal to install the suite into itself, and an
  uninstall that leaves nothing behind.

## v3.5.0

This release adds the three capabilities identified in the v3.4.0 source review: navigating
code without reading it, learning patterns that have to earn their confidence, and closing the
feedback loop between recorded outcomes and the contracts that produced them.

The 32 role skills and 809 atomic workflows are unchanged. 45 slash commands (was 42).

## Code navigation without whole-file reads

`skills/data-developer-experience/scripts/build_code_index.py` and `/dd-navigate`.

Builds a symbol and call index, then answers "where is this defined, who calls it, what breaks
if it changes" from the index, returning only the cited spans plus a blast radius. It reports
how much context that saved: explaining `build_marketplace` in this repository's `tools/`
returned 1169 bytes instead of the 425360 bytes of the seven files involved — 99.7% less.

Python is parsed with `ast`, so its symbols and call edges are exact and marked as such.
JavaScript, TypeScript and dbt SQL are matched with regexes and marked `approximate`: dynamic
dispatch, aliases and re-exports are missed. An unindexed symbol exits `2` and reports unknown
rather than guessing. Where exactness matters, `/dd-navigate` directs the work to a real
code-graph tool such as CodeGraph (MCP `codegraph_explore`) and says to cite that instead.

## Confidence-scored instincts

`skills/data-department-orchestrator/scripts/manage_instincts.py`,
`schemas/instinct-record.schema.json`, a ledger template, and `/dd-instinct`.

An instinct is a trigger, an action, a rationale and a count — never a transcript. Confidence
is the **Wilson lower bound** of the observed success rate, so a small sample scores low by
construction and cannot pass itself off as a rule:

| Observations | Confidence | Status |
|---|---|---|
| 9 applied, 9 succeeded | 0.70 | `active` |
| 2 applied, 1 succeeded | 0.09 | `proposed` — one lucky run is not a pattern |
| 8 applied, 7 succeeded, unconfirmed since January | 0.53 | `weakening` — re-test before relying on it |
| 10 applied, 2 succeeded | 0.06 | `retired` |

Recording one failure against the 9/9 instinct drops it to 0.60 and demotes it out of `active`.
Only `active` instincts may shape behavior. The validator rejects `active` status below 5
applications, rejects any record whose text looks like a credential, and rejects any record
carrying `user_content`.

## Contract quality loop

`skills/data-department-orchestrator/scripts/score_skill_quality.py` and `/dd-skill-quality`,
built on the existing privacy-minimized telemetry ledger. Three optional fields were added to
`telemetry-event.schema.json` (`fallback_used`, `superseded_by_task`, `evidence_verified`);
existing events remain valid because none are required.

Per task it derives completion, blocked, failed, abandoned, override and fallback rates plus
evidence verification, then recommends `observe`, `healthy`, `fix-routing`, `investigate`,
`derive-variant` or `tighten-evidence`. `fix-routing` fires on a task with 100% completion and
75% override — completion alone hides a routing defect where the work succeeds but the wrong
contract was doing it.

Two rules are enforced rather than documented: a high failure rate produces `investigate` and
the tool will not emit a recommendation that weakens a gate; and an empty ledger exits `1`
reporting quality as **unknown**, which is not the same as good.

## Command surface guard

`build_commands` now refuses to generate a department command over a hand-written control
command. This fired for real during the release: `/dd-quality` was written as a contract-quality
control and silently overwritten by the generated Data Quality department command. The control
is now `/dd-skill-quality`, the department keeps `/dd-quality`, and the collision is a build
failure rather than a deleted file.

## Validation

- 32 skills, 809 contracts, 45 slash commands, 1 hook handler.
- 35 routing, 37 role-confusion, 41 catalog-routing, 13 lifecycle, 34 benchmark cases.
- **46 control tests** (was 37), wired into CI. The 9 new ones assert the refusals: an
  unindexed symbol reporting unknown, each of the four instinct status transitions, an instinct
  containing a credential, `active` claimed on 2 applications, telemetry carrying user content,
  and an empty ledger reporting unknown rather than good.
- `claude plugin validate --strict` passes for plugin and marketplace.
- Rebuild is deterministic.

## Per-skill audit and structural repair

`tools/audit_skills.py` scores every skill on measurable dimensions — always-visible
description cost, routing-shard balance, contract depth, executable evidence coverage, thin
contracts and description overlap with siblings — and is wired into CI. It measures structure,
not correctness: a low score marks a place to look, not a proven defect.

The first run found 26 findings across 21 skills. Two were fixed:

- **Routing shards were unbalanced in 14 skills**, one shard holding 56–90% of the tasks, which
  defeats progressive disclosure: reading the Documentation `plan-design` catalog loaded 90% of
  its tasks anyway. Oversized catalogs now split into deterministic topic sub-shards capped at
  11 tasks, named after the dominant deliverable token
  (`catalog-plan-design-diagram.md`). Shard-imbalance findings fell from 14 to 2.
- **Four large skills had no executable evidence script.** Added:
  `validate_policy_coverage.py` (governance register coverage by classification, certification
  claimed on an incomplete register, stale reviews), `validate_dashboard_spec.py` (metric
  bindings against the contract, silent grain changes, the same measure at two grains,
  colour-only encodings), `validate_curriculum_coverage.py` (objectives never assessed,
  prerequisite cycles, recall items claiming to verify an `apply` objective) and
  `validate_requirements_traceability.py` (acceptance criteria with no passing test, must-have
  gaps blocking UAT).

Findings are down to 13. **Nine skills still have no evidence script** — talent acquisition
(41 tasks), onboarding (34), mlops (23), data science (22), head of data (21), platform (21),
ML engineering (20), generative AI (20), documentation (20) — and two shards sit just over the
55% threshold. These are tracked by the audit, not fixed.

`mean_thin_share` is 0.00%: every one of the 809 contracts carries at least one task-specific
resource.

## Repository cleanup

Old plugin archives, `__pycache__` and stray `.pyc` files removed; `dist/` went from 34 MB to
2.3 MB holding only the current release. Release notes and forward-test records before v3.5.0
were retired, the v2-era import redirect stub was deleted, `docs/operating-guide.md` was repointed
at the canonical guide, three now-dangling `See FORWARD_TEST_*.md` pointers in
`CLAUDE_NATIVE_VALIDATION.md` were rewritten, and stale `suite_version` values in three test
fixtures were corrected.

## Repository structure

The tree was standardised for publication. Long-form documents moved out of the root into
`docs/` with English kebab-case filenames; release notes became `CHANGELOG.md`. Added
`LICENSE` (proprietary, matching what `plugin.json` already declared) and `CONTRIBUTING.md`.
`README.md` was rewritten as a full feature, installation and usage reference.

| Was | Now |
|---|---|
| `01_CHI_TIET_TOAN_BO_SKILL_VA_TASK.md` | `docs/skill-and-task-catalog.md` |
| `02_HUONG_DAN_IMPORT_VA_SU_DUNG_CLAUDE.md` | `docs/installation-and-usage.md` |
| `02_TONG_QUAN_NANG_LUC_DATA_DEPARTMENT_SKILLS.md` | `docs/capability-overview.md` |
| `DATA_DEPARTMENT_SKILL_MAP.md` | `docs/skill-map.md` |
| `LIFECYCLE_OPERATING_MODEL.md` | `docs/lifecycle-operating-model.md` |
| `OPERATING_GUIDE.md` | `docs/operating-guide.md` |
| `SOURCE_INTEGRATION_AUDIT.md` | `docs/source-integration-audit.md` |
| `RELEASE_NOTES_v3.5.0.md` | `CHANGELOG.md` |

Build inputs and outputs were repointed (`build_suite.py` reads `docs/skill-map.md`,
`generate_user_docs.py` writes `docs/skill-and-task-catalog.md`), the source packaging script
was updated, and every cross-reference in the moved documents was rewritten. A link sweep
across all Markdown reports zero broken links.
