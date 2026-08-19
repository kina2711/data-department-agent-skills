---
name: dd-handoff
description: Produce a cross-role handoff package that transfers a completed atomic task to the next owner with evidence, assumptions, residual risks and one explicit next task.
argument-hint: "[completed task id] [next role]"
disable-model-invocation: true
---

Prepare the handoff. Optional arguments: $ARGUMENTS

A handoff is a transfer of ownership, not a summary. The receiving role must be able to start without re-deriving your work.

1. Confirm the source task is genuinely finished. Run `/dd-verify` first if the evidence chain has not been validated in this session. Do not hand off an `incomplete` verdict as if it were complete.
2. Resolve the receiving role from `suite-manifest.yaml` and the single next atomic task ID from `task-catalog.json`. An unnamed next owner is not a handoff.
3. Fill `skills/data-department-orchestrator/assets/handoff-package.yaml` with:
   - Source task ID, primary deliverable, artifact paths, artifact versions and SHA-256 hashes.
   - Evidence envelope IDs and their verification status.
   - Approval status and, when required, the approval record ID and its expiry.
   - Assumptions carried forward, with which ones the receiver must re-test.
   - Residual risks, each with a named owner. An unowned risk blocks the handoff.
   - Known limitations and what was explicitly **not** done.
4. State the receiving role's Definition of Ready and which of its inputs you are supplying versus leaving open.

Return: the completed handoff package, the next task ID, the next owner, and the shortest list of blocking gaps the receiver will hit first. If any residual risk has no owner or any mandatory test failed, return the handoff as **blocked** and say what closes it.
