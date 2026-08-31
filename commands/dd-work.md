---
name: dd-work
description: Implement one approved task with its required tests, stopping at the test gate rather than continuing into the next task.
argument-hint: "[task id] or 'all' for the whole approved plan"
disable-model-invocation: true
---

Work stage of the harness delivery loop. Target: $ARGUMENTS

1. Refuse to start if the plan is unapproved. Check the approval record covers this task, is inside its expiry, and has uses remaining.
2. Implement **one** task. A session that implements four tasks produces one reviewable unit instead of four; with `all`, run them sequentially and gate each one separately rather than batching.
3. Write the tests the contract requires before calling the task done. Where the contract requires none, say so explicitly instead of leaving it ambiguous.
4. Log every blocked operation to `harness-stop-log.json` with its rule, category and verdict. Never edit that log to make the run look clean.

**Gate.** Tests pass, or the task stays open. A failing test reported as a caveat is a failing test.
