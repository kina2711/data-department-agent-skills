# Note-corpus operating system

Use this reference when the deliverable is not one note but a whole body of notes for a role or domain. A corpus is built in one direction only: sourced roadmap, skill tracks, corpus plan, then module batches, then audit and index. Every stage is resumable, because a corpus outlives the session that started it.

## Stage flow

1. `academy-research-role-roadmap` — what a practitioner of this role is actually expected to know, taken from cited public sources rather than from recall.
2. `academy-build-skill-track-map` — each roadmap step becomes a track with an ordered module list and an exit criterion.
3. `academy-plan-note-corpus` — every planned note is enumerated with its ID, module, prerequisites and status before any note is written.
4. `academy-build-note-module` — one module at a time, to completion, updating the manifest as the checkpoint.
5. `academy-audit-note-corpus` — duplication, dangling edges, prerequisite cycles, staleness and coverage.
6. `academy-index-note-corpus` — the durable record of what exists.

Do not begin stage 4 before stage 3 has an accepted plan. Notes written without a planned ID acquire prerequisite edges that point nowhere, and the graph cannot be repaired cheaply once several modules deep.

## Sourcing the roadmap

A roadmap presented as current must name where it came from. Every step carries a source with publisher, URL, publication or update date and access date. Where a step is included on the author's judgment rather than from a source, mark it as judgment and say why. `role-curricula.md` is the suite's own level matrix and may be used as one input, but it is a static table and is never itself evidence of what is current. An uncited step is recorded as an assumption, and the roadmap does not claim currency unless its sources are dated.

Separate three things throughout: what sources state, what is conventional practice without a single authority, and what is the author's judgment. Do not assert version numbers, release dates or tool rankings that have not been verified.

## The manifest is the resume anchor

`note-corpus-manifest.json` holds the corpus state: corpus ID, domain, roadmap and track references, the planned note list and per-note status. Note status is exactly one of `planned`, `drafted`, `reviewed` or `stale`. `drafted` means a file exists at the expected path; it is not a claim that the note is correct. Only `reviewed` records a note as usable, and only after the deep-dive standard's checks have been applied to it.

A session resumes by reading the manifest, never by re-deriving the plan. Rebuilding the plan mid-corpus renumbers IDs that other notes already point at. Where the roadmap genuinely changed, add and supersede entries rather than regenerating the list, and mark superseded notes `stale` with a reason rather than deleting them.

## Module batches

A module is the unit of work because it is the smallest scope whose notes share prerequisites and can be checked against each other for overlap. Build every note in the module to the same depth before moving on: a corpus of uneven notes is worse than a smaller complete one, because the reader cannot tell which gaps are deliberate.

Within a batch, apply the deep-dive standard to each note, then check the batch as a set: no two notes in the module carry the same elevator-pitch claim, each note's `builds_on` targets either exist or are planned, and no note silently redefines a term another note in the module owns.

## Duplication and coverage at corpus scale

The per-note rule of extending a near-duplicate instead of creating one does not survive being applied by hand across hundreds of notes. The concept graph and the manifest are the duplication index: a proposed note whose tags and elevator pitch overlap an existing entry is resolved before it is written, not discovered later. Run `../../scripts/validate_note_corpus.py` for the mechanical checks — duplicate IDs, dangling `builds_on` and `prerequisite_of` targets, prerequisite cycles, planned-but-missing files, files not in the manifest, and notes whose `updated` date is old while `version_sensitive` is true. The script reads structure and cannot judge whether a note is any good.

## One module, one writer

A corpus outlives its sessions, so two of them will eventually run at once. The manifest is a single file and the last write wins, which silently discards whichever module finished first.

Claim a module before building it and release it when the batch closes. Two sessions may work in parallel only on modules that share no notes, and neither rewrites a manifest entry belonging to the other's module. On a collision, the module that has not yet written any note yields; re-running a module that produced nothing is cheap, and reconciling two divergent manifests is not.

Where the corpus spans enough stages to need gates, represent it as `corpus-workflow-manifest.json` and validate it with `data-department-orchestrator/scripts/validate_workflow.py`. The dependency edges are the stage order — research before tracks, tracks before plan, plan before any module — and each module batch is its own task instance so a failure names the module rather than the whole corpus. Resume through `orchestrator-resume-workflow` reading that manifest alongside the corpus manifest.

## What the corpus index does not record

The index records what exists: notes, relationships, coverage against the roadmap, freshness and gaps. It never records what the learner has mastered. A written note is evidence that content exists, not that anyone learned it, and the number of notes built is not a measure of progress. Mastery semantics and learner memory belong to `data-career-and-interview-coach` under the learner-memory interoperability contract; route learning evidence there rather than inferring it here. Where the corpus is stored in a personal knowledge vault, the vault's layer and provenance rules apply on top of this one.
