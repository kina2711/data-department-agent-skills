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

## Rounds

Cap the loop. Two full rounds without convergence is a signal that the requirement is ambiguous,
not that a third round will help; escalate to the requester with both positions rather than
iterating. Record every round in `producer-reviewer-record.yaml`, including rounds that failed.
