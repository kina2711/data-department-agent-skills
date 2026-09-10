# Milestone execution against a spec of record

A corpus plan enumerates every note. A milestone is the slice of that plan delivered as one piece of work — five notes and the dataset they all query, or one track's worth of modules — and it is where a corpus either stays coherent or quietly stops matching its own specification. What follows covers the stretch between an accepted plan and a closed milestone. It assumes `academy-plan-note-corpus` has already run, and replaces nothing in that stage.

## Two documents govern, and they are not the same document

The **spec of record** says what each note contains: outline, traps, exercises, pass criteria. It was written once and reviewed once, and amending it costs one line where amending the notes derived from it costs six hundred.

The **standing contract** says how every note is written regardless of subject: voice, section structure, the forbidden list, the evidence rules, and the mistakes already made once and not to be repeated. It accumulates across milestones. Cite both by section number in the plan, because a constraint referenced as "the style rules" is a constraint nobody can check.

Neither of them is the milestone plan. That is the third document, and it holds only what the other two cannot: the order this slice gets built in, what blocks what, and what must be true before authoring starts.

## Survey the bench before planning, not during

Where notes carry runnable output — query results, error text, timings — the output came from a machine, and that machine either exists or does not. Find out first. `psql --version` and `pg_isready` answer in under a second, and the answer changes the plan: a milestone whose evidence needs a database and has no database stalls at the third note, after approval, when the cost of replanning is highest.

Keep the bench separate from the taught environment in the plan's own wording. A corpus teaching PostgreSQL 16 on Windows 11 through DBeaver can be verified against a Linux container of `postgres:16-alpine`, and that container appears in no note. Collapse the two and the result is a set of instructions nobody can follow on the machine they actually own.

Evidence has a shelf life. Row counts printed in a note are true of the dataset that produced them, so a generator without a fixed seed makes every published count unreproducible the moment someone reloads. Fix that before the counts are quoted, not after.

## Reconcile the spec before writing anything

Specs drift against themselves. A table list grows from nine entries to ten while four sentences elsewhere still say nine; a file is renamed in one section and called by its old name in three others; a prerequisite points at a note scheduled to be written later than the note requiring it.

Cross-read the spec of record, the standing contract and the corpus index against each other on the specific names and numbers this milestone touches. Report each contradiction with file and line, say which side is right and why, and propose the amendment. Then check whether the notes already built repeat the error, since that is the difference between a four-line fix and a forty-line one.

Amend the spec. Do not quietly write something else instead: a note that disagrees with its own specification is indistinguishable from a note that is wrong, and a reviewer has no way to tell which of the two happened.

## The promise ledger

Notes written early make forward references. "The four delete behaviours are covered in `J01`" is a promise, and `J01` does not know it exists.

Extract those references mechanically and keep the result as an artifact — one row per target note, naming which notes promised what. Regenerate it at every milestone close rather than maintaining it by hand, because a scan across the built corpus costs a second and does not forget. The ledger then becomes an acceptance condition rather than a courtesy: read the exact promising sentences before writing a target note, and confirm each one kept afterwards.

Targets load unevenly. One note carries six promises from six different notes while its neighbours carry none, and that count predicts how long the note takes better than its outline length does. Sequence the milestone around it.

## Assumptions go in one block, at the top

Assumptions buried inside steps get approved without being read. Collect every one into a single section placed before the work breakdown: the verification environment, each spec contradiction found, every place the standing structure does not fit this slice, and each external resource nobody has checked yet.

Write each as a decision the reader can reverse — what was assumed, on what basis, what changes if it turns out wrong. Four such items is an ordinary count for a milestone. Zero means nobody looked.

External dependencies deserve particular suspicion. A note that tells a learner to open a named web sandbox, download a specific installer or click a labelled button asserts the current state of something outside the corpus entirely. Verify it inside the milestone, name the alternatives tried, and record the date it was checked.

## Closing the milestone

A milestone closes when its work is verifiable, not when the files exist.

- Every runnable block extracted and executed in order against a clean environment, with printed results matching what the notes claim, row counts included.
- The forbidden-list scan clean across the whole corpus rather than only the new notes.
- Reference and prerequisite checks passing: every cited note ID exists in the spec, and no prerequisite points forward.
- The promise ledger regenerated, and the promises this milestone was meant to keep confirmed kept.
- Status updated in the corpus index and the standing contract, so the next session opens on a true statement of what exists.

Report each check as it actually ran. A check that could not run is `not-run` and prints as `not-run`. A milestone with one failing gate and an honest report is in better shape than one reported clean, because the first can be finished and the second has to be re-audited from the start.

Then stop. The next milestone begins from the closed state of this one, and a session that half-finishes two of them leaves neither verifiable.
