---
name: dd-review
description: Review completed work against the acceptance criteria fixed during Plan, independently of whoever implemented it.
argument-hint: "[task id or plan reference]"
disable-model-invocation: true
---

Review stage of the harness delivery loop. Target: $ARGUMENTS

Read `skills/data-department-orchestrator/references/producer-reviewer-method.md` alongside the delivery loop.

1. Review against the criteria fixed at Plan time, not against what was built. If the criteria were never written down, the review cannot proceed — say so.
2. Do not read the producer's rationale before recording a verdict. A reviewer who has read it is measuring agreement with it.
3. Return exactly one verdict: **accept**, **revise** with specific bounded defects and their severity, or **reject** when another revision will not repair it.
4. Compare planned against actual and surface the drift rather than reconciling it silently.

**Gate.** Significant findings block completion. Reviewer acceptance is quality evidence and never owner approval.
