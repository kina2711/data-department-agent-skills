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

Silence is not a pass. An unrun check is reported as unrun. Never merge two claims into one sentence to save a line, never drop the evidence reference of a material claim, and never soften `blocked` or `failed` into narrative phrasing.

## Standing state

When work spans turns or resumes from saved state, open with the current task, the last verified gate and what remains open — read from the validated run state, never reconstructed from conversation history.
