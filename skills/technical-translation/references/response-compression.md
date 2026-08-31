# Response compression

This standard governs how a result is *reported*. It never changes what the task requires. Compression may not remove a gate, a test, an approval, a residual risk or an evidence pointer; a shorter answer that hides an unmet control is a failed task, not a concise one.

## Compact return for R0 and R1

For `R0-light` and `R1-reviewed` work, return in this order:

1. One state line: task ID, phase reached, status.
2. The deliverable itself, or the path to it.
3. Only the return fields that carry content. An empty field is omitted, not printed as empty.
4. Exactly one next action, named as a task ID with its owner.

Lead with what changed or what to do, not with what was asked. No preamble, no restatement of the request, no closing summary of the text above it. Number steps only when order matters. Cap any list at five items; when more exist, show the five that change the decision and state how many remain.

## What never compresses

`R2-standard`, `R3-controlled` and `R4-critical` work returns the full contract. At every tier, these print in full regardless of length: blocked or failed status, unmet gates, unrun checks, assumptions, limitations, residual risks with owners, approval status, and any label that separates a draft from an executed outcome or self-study from production evidence.

A task that runs for minutes and shows nothing is indistinguishable from a task that has hung. The reader's only options are to wait or to kill it, and both are decisions made without information. Streaming what is happening as it happens removes that, and introduces one hazard worth naming.

## Show the reasoning, not a spinner

What is worth surfacing while work runs: the step being attempted, the query or command being issued, the artifact being read or written, and what just failed. These are the things a person would ask about if they were watching over your shoulder, and they are the same things that make a run reviewable afterwards.

A progress bar with no content answers "is it alive" and nothing else. The generated SQL, shown as it is written, answers "is it doing the right thing" — which is the question the reader actually has, and it lets them stop a wrong run at second ten instead of minute four.

## An intermediate number is not an answer

The hazard: a figure streamed before validation looks exactly like a result. When it changes after reconciliation, the reader saw the answer change, and that costs more trust than the wait would have.

Label partial output as partial, and keep unvalidated numbers out of the stream unless they are marked as such. Stream the *shape* of the work freely — steps, queries, tools, failures — and gate the *figures* behind whatever check the contract requires. A number that has not passed its test is progress, not a result.

## Failures stream too

The strongest reason to stream is that failure becomes visible at the moment it happens rather than in a summary that may round it away. A failed step, a retry, a fallback taken: each appears, and none is quietly absorbed. Silence about a failure is worse in a stream than in a report, because the reader has been given the impression they are seeing everything.

## What the stream is not

It is not the record. A transcript scrolling past is not evidence, does not persist, and cannot be cited; the run's evidence, state and claims are written where the contract says regardless of what was displayed. Nor does streaming change any gate: a reader watching a run has not approved it, and unapproved work that was visible while it happened is still unapproved.

## What never compresses, continued

Silence is not a pass. An unrun check is reported as unrun. Never merge two claims into one sentence to save a line, never drop the evidence reference of a material claim, and never soften `blocked` or `failed` into narrative phrasing.

## Standing state

When work spans turns or resumes from saved state, open with the current task, the last verified gate and what remains open — read from the validated run state, never reconstructed from conversation history.
