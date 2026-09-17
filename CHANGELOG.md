# Changelog

## v3.26.1 — a selector that collected an answer and changed nothing

Data 2026 asks how far to run, and offers four stages from "rewrite the roadmap prose" through to
"the sources are in, compose the lessons". The template emitted all eight steps whichever was
chosen, so picking the first stage still handed over instructions for extracting sources and
deploying the site. The field was answered and ignored — worse than not asking, because the person
believes they scoped the run.

The template engine gained `neu_la`, which keeps a part only when a parameter holds one of the
named values; `neu` could only ask whether a parameter was filled at all. Both doors use it, since
both compose prompts from the same library.

Stage one is now 1076 characters rather than 4537, and carries the rewrite alone. The last stage
carries extraction, composition and the build commands, and says explicitly that the roadmap and
objectives are already settled and must not be rewritten. Two tests hold it: one on the engine,
one asserting the first stage is shorter than the last and that neither carries the other's steps.

157 app tests.

## v3.26.0 — Data 2026, reordered so the objective comes before the search

The first cut of this workflow had gap analysis drive the source hunt. The author's own ordering is
better and the workflow now follows it: start at the roadmap, rewrite its language, detail it, then
write objectives for the role, each module and each lesson. **Those names and objectives are the
search query.** Looking for material before an objective exists collects reading for a question
nobody has asked.

**The source step is a handover, not an acquisition.** It names each source and how to obtain it —
publisher link, open-access copy, official docs, arXiv, or plainly "buy it" or "borrow it" — and
then stops. The author fetches them, puts them in `ref/`, and says so. Nothing is read in the
meantime, and guessing a book's contents from its title while waiting is called out as the failure
it would be.

**Building the site is now part of the flow, as instructions.** Step 8 walks through `make status`,
`make material`, `make web`, `make preview` and `make deploy` in order, says which file each one
produces, and explains how to find the lesson with the broken front matter when the parser
complains. The run still does not deploy.

38 tasks, 32 waves, nine gates. Two orderings are asserted in code at build time rather than
trusted: the search runs after the objectives exist, and extraction runs after the author confirms.

A green suite is not always good news. After the scope changed from 34 tasks to 38 and two gates
moved, every case still passed — which meant the cases were describing the old flow. Three were
rewritten and added for the two human gates and the objective stage, then verified by removing each
gate and watching a case break. 36/36.

## v3.25.0 — Data 2026, for three curricula that already exist

A second authored workflow. Data Trainer starts from a folder of source material and builds a
corpus; **Data 2026** starts from three curricula already written to disk — Data Analyst, Data
Engineer, Analytics Engineer — and brings them up to standard without starting over. 34 tasks,
26 waves, eight gates that need a named person.

The ordering is the point. The prose already written is rewritten first, and the rewrite may not
add or drop a single fact, number, name or citation — losing a claim while rewriting is a fault,
not concision. Then the reference gaps are **named** at programme, module and lesson level before
anything is searched for, because searching first collects material for a question nobody asked.
Only then does a source hunt run, and every candidate must carry four things or it is not listed:
title and author, version or year, which named gap it fills, and a concrete lawful way to obtain
it. The run stops at a human decision; approved, it packages for the site build and hands over the
commands rather than running them.

**Both harnesses now carry a measured score.** Fourteen new cases for `data-2026` alongside the
existing twenty, verified the same way before anything was recorded: publishing moved into scope,
the approval gate removed, the rights gate removed, an exclusion stripped of its reason, and a
workflow task dropped from the scope. Each broke a case. 34/34.

Two faults caught by checks written in earlier releases rather than by reading: the preset job
collected a field the template never used, and the coverage report had no row for the new harness.

## Data Agent 0.6.1 — the terminal can find the run you left unfinished

The session store moved into `core/` and both doors use it. Until now only the app recorded a run,
so a session started from `data-agent` printed its id once and forgot it — and an id nobody wrote
down is a conversation nobody can reopen after a reboot.

```
data-agent resume                 # what is unfinished, newest first
data-agent resume <id> --go       # continue it
data-agent resume --here --go     # continue whatever was left in this folder
```

The id is written as the run streams rather than when it ends, because a run stopped by Ctrl-C or
a session limit is exactly the one somebody wants back and it never reaches the end.

**Adoption merges every old store instead of picking one.** The first attempt took the most
recently modified, which was a development profile a test run had touched minutes earlier — so it
adopted a fixture and left a real fourteen-turn run from two days before behind. Sessions are keyed
by folder and skill, so there is nothing to choose between: the union is well defined and the newer
record wins on a shared key.

Resuming restores the model's memory of the work, not the transcript. Said in that wording
wherever it is offered, because the opposite is what people expect.

155 app tests.

## Data Agent 0.6.0 — the desktop build catches up with the split

The suite is unchanged at v3.24.0. What moved is the app, which now loads its logic from
`app/core/` rather than owning it, and the packaged build had to be told about that.

**The package list would have shipped a broken app.** `build.files` named `src/**/*` and
`package.json`, which was complete when everything lived in `src/`. After the split, a build made
from that list contains a `main.js` whose first line requires `../core/suite` — a module the
archive does not hold, so the window never opens. Caught by listing the built asar instead of
trusting the build to have guessed; `core/**/*` and `cli/**/*` are named now.

Verified on the installed build rather than the source tree: `core/` and `cli/` are present inside
`app.asar`, and loading the packaged `index.html` under Electron resolves `WfGraph` from
`../core/graph.js` — the cross-directory script tag that would otherwise have failed silently and
taken the workflow canvas with it.

## v3.24.0 — a second door, a third context level, and the drafts that were turned down

**`data-agent` is a real command now.** The Electron app and the terminal are two clients of one
library: `core/` owns reading the suite, composing a preset job's prompt, building the argv that
runs Claude, and splitting its JSON stream. Neither door owns the permission mode, so it cannot
mean one thing in each.

```
data-agent find "pipeline chạy lại bị trùng dữ liệu"
data-agent show de-build-batch-ingestion --full
data-agent run de-build-batch-ingestion --dir . --perm plan
```

Every listing command takes `--json`. Widths are measured in display columns rather than code
points, because a Vietnamese combining mark occupies no column and counting it drifted every table
one cell per diacritic.

Three faults the extraction exposed, each a real one:

- **Piped `--json` was truncated.** `console.log` to a pipe is asynchronous and `process.exit()`
  did not wait, so the tail of the array never arrived and what did arrive parsed nowhere. The
  exit code is set instead of forced.
- **The tier was being passed as a model name.** A task declares `strong`, `standard` or `light`,
  and the suite keeps it that way because tiers outlive model ids. Passing it through produced
  `--model standard`, which is not a model. The CLI reports the tier and leaves `--model` to you.
- **The two doors were reading different config files.** The app kept its config under Electron's
  userData, named after the product; the CLI looked in `~/.config/data-agent`. They now share one
  file, and the first read adopts whatever the old location held — including the recent folders,
  which is the part a user would have had to retype.

**A source can now enter context as a summary instead of vanishing.** `build_context_package.py`
was binary: full content, or dropped when the budget ran out. Open Notebook makes this a
per-source choice, and the third state is the one that was missing — losing a source entirely
loses the fact that it existed, and nobody can ask about a gap they cannot see. Over budget, the
lowest-priority source is demoted to a summary before anything is removed; measured on three
sources at a 4k budget, all three survive where two were previously dropped. Summaries are
extractive — headings and opening sentences, verbatim — and labelled in the package, because a
generated abstract would be a claim this script has no model to stand behind. A required source is
never demoted silently; that still fails, and now says what to do about it.

**The rejected drafts are kept, with the reason.** A voice guide describes the target and not the
misses, so an agent still has to guess which defensible sentence would actually have been sent
back. `voice_ledger.py` keeps the approval and the rejection side by side; a rejection without a
reason is refused, since that records that something was wrong and not what. `brief` renders what
a draft should read first, rejections before approvals. It counts recurring reasons and refuses to
promote one into a rule — that judgement belongs to a person, and a ledger that concluded things
would be a second voice guide nobody agreed to.

152 app tests, 17 of them new.

## v3.23.1 — the coverage report disagreed with the harness it reports on

`docs/harness-coverage.json` still called data-trainer unevaluated while the declaration beside it
carried 20/20. The report is generated, nothing regenerated it, and a generated copy nobody
refreshes is a second answer to a question that already had one — the more convincing answer, since
it is the file a reader opens first.

Regenerated, and validation now compares the two. Verified by setting the row back to false and
watching it fail.

## v3.23.0 — the harness has a score now, and the router has an opinion about R2

**data-trainer stops reading UNEVALUATED.** Twenty cases ask the harness what it does when a run
requests a particular task, and get one of three answers: allowed, gated, or refused. Sixteen name
a task; four state an invariant a widened harness would break. The expectations are written from
what the flow is meant to be, never read back out of the declaration they check — a case computed
from its own subject passes by construction and measures nothing.

Teeth were verified before the score was recorded. Publishing was moved into scope, a gate was
removed, an exclusion lost its reason, a gate was pointed at a task that does not exist, and a
workflow task was dropped from the scope. Each broke a case. 20/20 for suite 3.23.0.

**A score can no longer outlive the thing it measured.** `score_is_for_version` was free to name an
older release, which reads exactly like a fresh measurement. Validation now compares it against the
suite version, and it caught this release's own bump before the re-run.

**R2 evaluation coverage goes from 28.4% to 44.9%.** The 161 uncovered R2 contracts were not worth
a case each; the 37 that share most of their name with a task in another skill were, because that
similarity is the shape a router confuses. The first pair is a literal collision —
`bi-build-source-authority-matrix` and `meta-build-source-authority-matrix` differ by prefix alone.

Those 37 were then sent to a model rather than left as structure. **78.4% skill accuracy, and 97.3%
rival avoidance** — which is the interesting part: on the seven misses the model almost never picks
the rival the case names, it picks a third skill. The pairs designed here are not the confusion
that occurs. Each miss carries a note above it saying what the model answered and why the case
still expects what it expects, and one case was wrong rather than the model: it listed eight
cross-role concerns, which makes the orchestrator the correct answer. That query is narrower now.

## v3.22.1 — the install note named the wrong directory

The permission entry v3.22.0 documented pointed at the marketplace checkout. `${CLAUDE_PLUGIN_ROOT}`
resolves to the cache instead — `cache/<marketplace>/<plugin>/<version>/` — so the entry granted a
directory the commands never read. A run from an empty folder still answered 873 by finding a copy
in the marketplace directory and saying it could not confirm the two matched, which is a correct
report of a wrong setup.

Both READMEs now name the cache root, which also covers the next upgrade. Verified after the
correction: `/dd-catalog` and `/dd-de` both run from an empty directory, and the paths they report
reading are inside the installed version.

## v3.22.0 — the plugin only worked in the directory it was built in

Running `/dd-brain` from an empty folder found nothing. The command said to read
`skills/personal-second-brain-and-knowledge-os/SKILL.md`, that path resolved against the user's
project rather than the plugin, and no such directory was there. Every version since the command
surface was introduced shipped this way. It went unnoticed because the only place it was ever run
was the checkout it was built in, where the relative path happens to be correct.

**The skills are now registered.** `plugin.json` gained `"skills": ["./skills/"]`, so Claude Code
loads them through the Skill tool from any working directory, and the department commands ask for
the skill by name instead of by path. Loading a skill this way costs no permission prompt, which
is why it beats the alternative of pointing the same path somewhere absolute.

**Thirty-four remaining paths now say which root they mean.** Task contracts, catalog shards,
`task-catalog.json`, `suite-manifest.yaml` and every `python skills/...` invocation carry
`${CLAUDE_PLUGIN_ROOT}/`. Seventeen of those were script invocations inside fenced code blocks
that the first pass missed entirely; the check found them. Paths that belong to the user's own
project — `project-constitution.json` above all — deliberately stay relative, because rewriting
those would point every project at one shipped template.

**Two checks so it cannot drift back.** `check_command_paths` refuses a command that addresses a
plugin directory as a project directory. `check_pipeline_counts` compares the summary at the top
of `/dd-pipeline` against the workflow and harness it describes; it was claiming 50 tasks, 31
waves and 3 gates for a flow holding 56 tasks, 35 waves and 7 gates. Both were verified by
breaking them on purpose and watching validation fail.

**Installing now has a documented second step.** Skills load free, but the files they cite are
reads outside the working directory, so Claude Code asks each time. One `additionalDirectories`
entry settles it, and both READMEs now say so.

Measured, not assumed: `${CLAUDE_PLUGIN_ROOT}` expansion in command and SKILL.md bodies, skill
registration, and the permission behaviour were each established with a throwaway plugin before
anything here was written. An earlier probe of the same question failed because it edited the
marketplace source rather than the installed copy, and reading that as "substitution does not
work" would have sent this release down the wrong path.

## Data Agent 0.4.1 — two things the reply box exposed

Replying made a session long enough for two faults to show.

**The last paragraph was printed twice.** The stream sends the final
assistant message, then a closing event that repeats it as `result`, and
both were rendered. Now the closing text appears only when it says
something the transcript does not.

**A session in plan mode refuses every write, and the app never said so.**
Claude's own advice is to press Shift+Tab, which is true in a terminal and
meaningless here, so a run could sit blocked while the control that
governs it was three inches away and unmentioned. The reply area now names
the mode the next turn will use and marks plan mode in warning colour.

Resuming does carry a new mode — verified before building anything by
starting a run under plan, resuming it under acceptEdits, and watching the
file appear. Nothing about the mechanism needed changing; only the silence
around it did.

107 app tests.

## Data Agent 0.4.0 — desktop app only

The suite is unchanged at v3.11.0. No skill, task contract, command, hook or schema moved, so the
plugin has nothing new to install. What follows happened in the app that ships beside it.

**You can write your own request.** The app had three prompt sources and
none of them was the person: a preset job, a selected task, or a generic
fallback. Presets cover work that recurs. Nothing covered the thing nobody templated. A box now sits between
the presets and the task list, and what you type wins: somebody who wrote a sentence has said
something more specific than any template covers. A selected task still travels with it, as routing
rather than as instruction.

**And the prompt is visible before it is sent.** Pressing run used to dispatch a prompt nobody had seen, assembled from a template or a task id.
Beside the button there is now a disclosure showing exactly what will go, updated on every
keystroke.

**The conversation continues.** `claude -p` answers once and exits, so
when a skill asked what you already know — which is the first task of the
Academy skill — the transcript ended there with nowhere to reply. Every event already carried a session id, and the CLI resumes headlessly. A reply now resumes that
session instead of opening a new conversation wearing the old transcript. The box appears only after a run exits zero with a
session to resume.

Two test defects surfaced with it. A spy assigned to `window.studio` records nothing: the context bridge freezes that object, so an
existing assertion was passing regardless of what the app did. Stubs record in the main process
now. Proving the repaired assertion could fail exposed something worse. With the folder guard removed a
run proceeded and wrote `in-progress` into the repository's own workflow file, because the save
channel was unstubbed too. Both are stubbed. A test suite able to modify the tree it tests will do
so on a day nobody reads the diff.

102 app tests.

## v3.11.0

The first notes the corpus ever produced, a map the suite draws of itself, and a desktop app with
tests that can fail.

33 role skills - 867 atomic task contracts - 51 slash commands - 33 Antigravity agents -
52 executable evidence scripts - 12 JSON Schemas - 23 authored notes - 88 app tests

### The corpus stopped being a plan

86 concept keys, 10 role plans, 206 planned notes — and not one note written. The Data Analyst
corpus exists now: 22 deep dives plus a canonical running schema, 42,000 words, none scoring below
0.96 on the prose gate. Writing them found four defects reading could not. A marker the validator counts was never named
by the authoring standard, so five notes written to that standard exactly failed the check. The
standard demanded a canonical schema file, while neither the manifest nor the validator had any
concept of a file that is not a deep dive. Tags ran domain plus module and came out identical for
every note in a module — all 47 pairs of the SQL module reported at 100% overlap, detecting
nothing. And `</details>` counted as a sentence opener, penalising every note for a repetition the
standard itself mandates.

Every note is `drafted`. None is `reviewed`. The files exist and clear every structural and prose
check there is; nobody with the domain has read one.

### The suite draws itself

One tree of this suite existed, hand-drawn in the canonical skill-map, and it had drifted to 28
skills against 33 on disk. `tools/build_skill_atlas.py` generates it instead. Four levels, each from a source somebody wrote,
rewritten between generated markers. It cannot drift again. Its first finding is about itself. Five skills are named in no rollout wave and carry 181 tasks —
21% of the suite sitting outside every band. Unplaced, and reported as such rather than filed
somewhere plausible.

Four structures here never talked to each other. `tools/build_knowledge_graph.py` joins them: 1215
nodes, 5013 edges, each edge labelled `extracted`, `inferred` or `ambiguous`. Phase precedence is what the 832 workflow edges encode, not task prerequisites, so they are
excluded from every structural claim rather than drawn as dependencies 832 times.

### Evaluation that covers everything, and evaluation that costs money

Only 205 of 867 contracts had a named eval case. `tools/eval_properties.py` adds 12 invariants covering all 867, each carrying a mutation it must
reject. Three rules that seemed obvious turned out false against the catalog. Those are recorded
as non-properties.
Sending the 106 routing cases to a real model, `tools/eval_behavioural.py` reports 76.4% skill
accuracy and 94.9% rival avoidance, with one concentrated weakness at the orchestrator. Building it
was mostly discovering that its own measurements were wrong.

### Techniques taken from elsewhere

From OpenMAIC, two academy tasks for the outline-then-scene pipeline, where source spans make an
unsourced beat visible. From PaperBanana, a caption-first discipline for figures — deliberately a reference and not a task,
since it fails the distinct-deliverable test. From Caveman, a budget for what a tool returns: the half of context spending nobody watches. And from NotebookLM, whose method survived where its API does not exist, a boundary for answering
from a closed set — where saying "not in the set" plainly is the whole point.

### Interoperability

`.agents/skills` is a relative symlink to `skills`, so Google Antigravity loads all 33 without a
second copy to drift. `.mcp.json` declares the Perplexity server, and only that one, because it is
the only one whose package and interface were read from the provider's documentation.

### The desktop app

Zero tests became 88, screenshots included, compared against baselines by diffing raw bitmaps out
of Electron. A dry run computes the waves a workflow would take before anything is called. A cockpit strip names
what the run is waiting on. It has no control that clears an approval gate, and no play button for
the whole graph. Evidence drafted from the run actually observed, leaving
blank what the app did not see. Tasks run on the model their tier declared — on one workflow, 20 of 29 runs had been using
something heavier than the suite asked for.

Grouped by rollout wave, the grid carries the Vietnamese summary instead of the English routing
description and shows the risk mix the catalog has always held. Every skill has a generated walkthrough. Every line of it names a real task.

## v3.10.0

Which model a task needs, a reviewer verdict that can stop work, and skill descriptions audited
as the routing surface they actually are.

32 role skills - 827 atomic task contracts - 45 slash commands - 32 Antigravity agents -
52 executable evidence scripts - 12 JSON Schemas

### Model tier per task

Every contract declared a risk tier and a criticality; none said which model should run it, so the
choice fell to whatever was open at the time.

- New shared reference `model-selection.md` in all 32 skills. The variable is not importance but
  what catches an error before someone acts on it: a validator (light), a reviewer (standard), or
  nothing at all before a decision, approval or judgment about a person (strong).
- Two rules override the table. Evaluating another artifact runs strong regardless of risk tier,
  because a grade is what everyone downstream trusts and is the least likely thing to be checked;
  a reviewer never runs lighter than the producer it reviews. `R3-controlled` and above run strong.
- `model_tier` is now emitted per task in `task-catalog.json` and printed in every contract:
  238 strong, 409 standard, 180 light.
- Model choice is not a control. It never satisfies a gate, and a lighter model never lowers the
  bar an output must clear. Where budget forces a lighter model on judgment work, that is recorded
  as a limitation rather than decided silently.

### A reviewer can now say stop

Producer-reviewer had two ways out: converge, or exhaust two rounds and escalate.

- Each round ends in exactly one of `accept`, `revise` or `reject`. The missing verdict was
  `reject` — without it, work that should stop instead spends its rounds being polished and
  arrives late and still wrong.
- The severity threshold separating revise from reject is fixed in the rubric before production.
  One critical defect is a reject however many minor ones were repaired.

### Descriptions audited as a routing surface

A skill's `description` is the text a router matches an intent against, not documentation.

- New `tools/audit_skill_descriptions.py`. It found six of the eight highest-overlap skill pairs
  had no confusion-pair case pinning the intended winner; ten cases now cover them, taking the
  suite to 54.
- Nine descriptions gained an explicit boundary naming where competing work belongs. That first
  made the measurement worse — naming a neighbour imports the neighbour's vocabulary — so overlap
  is now scored on the claim span with redirect sentences excluded. A sentence whose job is to
  decline a request should not be counted as competing for it.

### Corrections to v3.8.0

- `corpus-workflow-manifest.json` hardcoded `R1-reviewed` for every task while two of them are
  `R2-standard` in the catalog: a risk downgrade of exactly the kind `validate_workflow.py` exists
  to catch. Risk tiers are now derived from the catalog at build time, so the template cannot
  drift when a task's tier changes.
- The note-corpus operating system claimed each module batch could be its own task instance. The
  validator keys tasks by `task_id` and rejects duplicates, so that was impossible; one workflow
  carries one `academy-build-note-module` entry that advances, and `instance_id` labels which
  module it is currently on.

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
