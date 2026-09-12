# Model selection

Every task in this suite already declares a risk tier and a criticality. Neither says which model should run it, so the choice has been made by whatever was open at the time. That is the wrong variable to leave to chance in both directions: a weak model on a judgment task produces confident wrong answers that a reviewer then has to catch, and the strongest model on a mechanical task burns budget that the deadline will later reclaim from somewhere that mattered.

## Choose by what catches the error, not by importance

Everything in a governed suite feels important. The question that actually separates the tiers is what happens to a mistake between the model making it and someone acting on it.

| What catches an error here | Tier | Typical work |
|---|---|---|
| A deterministic check — a script, a schema, a test, a validator | **light** | Formatting to a template, extracting fields, filling a manifest, mechanical rewriting, listing what exists |
| A human reviewer reading the output | **standard** | Drafting a specification, writing an explanation, proposing a design, summarizing findings |
| Nothing before it reaches a decision, an approval, a release, or a judgment about a person | **strong** | Grading, auditing, reviewing another artifact, root-cause diagnosis, risk assessment, certification, anything at `R3-controlled` or above |

The reasoning is that a mistake a validator will reject costs one retry, a mistake a reviewer will catch costs their attention, and a mistake nothing catches becomes a decision. Spend where nothing else is watching.

## Two rules that override the table

A task whose output is the **evaluation of another artifact** runs on the strong tier regardless of its risk tier. Grading is where a weak model is most confidently wrong and least likely to be checked, because the grade itself is what everyone downstream trusts. The same applies to a reviewer in a producer-reviewer pair: the reviewer never runs on a lighter tier than the producer, or the review is theatre.

A task at `R3-controlled` or `R4-critical` runs on the strong tier. These are the tiers where execution is irreversible or affects access, employment, money or published claims.

## What model choice is not

It is not a control. A strong model does not satisfy a gate, replace a review, raise an evidence level or license a claim the evidence does not support; a light model does not lower the bar the output must clear. Every gate in the lifecycle standard applies identically at every tier.

Do not downgrade a tier to save budget or time on work the table places higher, for the same reason risk tiers are never downgraded to meet a deadline. If budget genuinely forces a lighter model on judgment work, that is a constraint to state in the deliverable, not a decision to make silently — record it as a limitation so the reader knows the grade they are reading was produced under one.

Record the model actually used alongside the output whenever the task produced a judgment, a score or an approval input. Six months later, "which model graded this" is a question with consequences, and it has no answer unless it was written down.
