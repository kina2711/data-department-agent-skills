---
name: dd-status
description: Report the current Data Department workflow state from the real run-state and workflow manifest files, including blockers, gates and the next permitted action.
argument-hint: "[path to run-state or workflow manifest]"
disable-model-invocation: true
---

Report workflow status. Optional path argument: $ARGUMENTS

1. Locate the state files. Use the supplied path if given; otherwise search the working directory for `run-state.json`, `run-state.yaml` or `workflow-manifest.json`. If none exists, say so and state that no workflow is in progress — do not reconstruct state from this conversation.
2. Validate before reporting. State that fails validation is not a status report:

```
python skills/data-department-orchestrator/scripts/validate_run_state.py <state-file> --task-catalog task-catalog.json
python skills/data-department-orchestrator/scripts/validate_workflow.py <manifest> --mode plan
```

3. Report from the validated file only: workflow ID, status, lifecycle profile, risk tier, execution path, current phase, current task, completed tasks, passed gates, failed tests, blockers, next permitted action and the age of `updated_at`.
4. Flag drift explicitly. If the working tree, the run state and the recorded evidence disagree, report the disagreement rather than picking the optimistic reading.
5. If validation fails, print the validator output verbatim and stop. Do not explain away a validator failure.

Return the next permitted action as one concrete task ID, and name what must happen before any gated action becomes permitted.
