---
name: dd-task
description: Load one canonical atomic task contract completely and report its readiness, gates, tests, approvals and evidence requirements before execution.
argument-hint: "<task-id>"
disable-model-invocation: true
---

Load the atomic task contract for: $ARGUMENTS

1. Resolve the task ID against `task-catalog.json`. If it is not an exact canonical ID, stop and offer the closest real IDs — never proceed on a guessed ID.
2. Read the contract file completely at `skills/<owning-skill>/references/tasks/<task-id>.md`. Partial reads are not permitted.
3. Read `skills/<owning-skill>/references/lifecycle-standard.md` and apply the contract's profile, risk tier and execution path.
4. Load only the company context, technology adapter and industry references the contract actually names. Do not preload every adapter.

Report:

- Contract: goal, primary deliverable, lifecycle profile, risk tier, execution path, criticality.
- Definition of Ready: which inputs are present, which are missing, and which missing inputs are blocking.
- Procedure: the concrete steps for this specific request.
- Tests and evidence: what must be executed or inspected, and which script under `skills/<owning-skill>/scripts/` produces machine-checkable proof.
- Approval and done: who must approve, at what risk tier, and what makes this task complete.

End with an explicit statement of what you will do first and what you will not do without approval. Do not begin executing until the user confirms.
