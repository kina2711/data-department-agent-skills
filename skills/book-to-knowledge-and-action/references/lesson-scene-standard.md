# Lesson scenes, and where each one came from

Build a lesson from a document and two failure modes appear, identical from the outside. It can
cover material the document does not contain, and it can quietly drop the part that mattered. Both
produce a plausible lesson. The defence against both is the same: every beat carries the passage it
came from, and the passages nobody used are listed.

## Two stages, not one

First comes the outline, and only the outline: an ordered list of beats, each with a type, a claim
it teaches, and a span of the source it rests on. Nothing is written yet. That is the point —
the cheapest moment to notice that a lesson has four beats on setup and none on the failure mode is
before any of them has been drafted.

Scenes come second. Each beat becomes exactly one scene of its declared type. Two scenes out of one beat means it was two beats all along. None means a gap, not a shortcut.

## The scene types, and what each one owes

| Type | Does | Must carry |
|---|---|---|
| `explain` | states a mental model or mechanism | the source span, and the misconception it displaces |
| `check` | asks one retrieval question | an answer, and what a wrong answer reveals |
| `practice` | gives a task the learner performs | the success condition, checkable by someone else |
| `decide` | poses a situation with no single right answer | the trade-off, and what makes each choice defensible |
| `apply` | a longer task combining earlier beats | the beats it assumes, by id |

Five types is the whole vocabulary, and the table above is the complete list. Any sixth is nearly always one of these five renamed, and each extra doubles what an instructor
must hold in their head.

Watch the ratio rather than legislating it. All `explain` gives you a document with slide breaks. All `check` tests before teaching anything. If a whole module has no
`decide` beat, either the topic genuinely has no judgment in it — rare — or the judgment was left
out because it is the hard part to write.

## Source spans are the contract

Each beat names the passage it rests on: the file, plus a locator precise enough to find it — a
page, a heading, a line range. "Chapter 3" is not a span; "p. 47, the paragraph beginning "Idempotency"" is. Test it by having a second person open the source and land on the same passage without guessing.

Two consequences follow, and both are the point of doing this at all. Where no span exists, the beat is teaching something the source does not say. That may still be
correct. It is certainly not sourced, and it stays marked that way. And the spans nobody used get listed at the end of the outline, because
the material a lesson skips is a decision, and an undocumented decision is indistinguishable from
an oversight.

## What the package does not decide

Until somebody has run the session, duration estimates are guesses, and they are labelled as
estimates. Whether the lesson works is measured by the assessment tasks, not asserted here. And a
package is not a curriculum: it covers one source, and how it fits a role's learning path is
decided by the curriculum map, which knows about the other sources.
