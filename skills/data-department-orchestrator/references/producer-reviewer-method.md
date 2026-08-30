# Producer-reviewer method

Use when the cost of a plausible-but-wrong deliverable is higher than the cost of producing it
twice. A reviewer who has already read the producer's reasoning is measuring agreement with that
reasoning, not the work.

## Independence rules

1. Fix the acceptance criteria and the review rubric **before** production starts. A rubric written
   after seeing the artifact describes the artifact.
2. The reviewer receives the artifact, the original requirement and the acceptance criteria. The
   reviewer does not receive the producer's rationale, chain of reasoning, self-assessment or
   confidence until an independent verdict is recorded.
3. The producer and the reviewer are never the same actor, and the reviewer is not a branch the
   producer dispatched.
4. The reviewer's verdict is recorded first and is immutable. Only then are both sides disclosed
   and the disagreement discussed.

## Disagreement

Disagreement is the output, not a failure of the process. Route an unresolved contradiction to
`orchestrator-manage-conflict-register` with both positions and their evidence. Do not split the
difference, do not let the more confident side win, and do not send it back for a third opinion
that merely breaks the tie without new evidence.

A reviewer's acceptance is quality evidence. It is **not** owner approval, and it never satisfies a
gate that requires named authority bound to an artifact version and hash.

## Rounds and the three ways one ends

Cap the loop. Two full rounds without convergence is a signal that the requirement is ambiguous,
not that a third round will help. Record every round in `producer-reviewer-record.yaml`,
including rounds that failed.

Each round ends in exactly one of three verdicts, and the reviewer names which:

- **accept** — the artifact meets the acceptance criteria. Downstream work proceeds. This is
  quality evidence, never owner approval.
- **revise** — the defects are specific, bounded and repairable by the producer. The reviewer
  lists them with severity; the producer returns a revision, not an argument.
- **reject** — the artifact is wrong in a way another revision will not repair: it answers a
  different question, rests on a premise that does not hold, or would need to be rebuilt rather
  than corrected. The loop terminates as `failed` and returns to the requester.

The missing verdict is usually `reject`. Without it, work that should stop instead spends its two
rounds being polished, and arrives late and still wrong. A reviewer who can only say *accept* or
*try again* cannot report that the task itself was misframed.

Set the severity threshold that separates `revise` from `reject` in the rubric, before production,
alongside the acceptance criteria. Deciding it after reading the artifact is deciding it about the
artifact. A single critical defect is a `reject` regardless of how many minor ones were fixed;
counting defects is not a substitute for weighing the worst one.

A `reject` is a terminal state of this loop, not of the work. It returns an unmet requirement to
whoever set it, with both positions intact and the reason the artifact could not be repaired.
