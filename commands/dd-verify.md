---
name: dd-verify
description: Run the executable evidence chain over a task result, its evidence envelopes and its artifacts, and return a machine-checked pass/fail verification report.
argument-hint: "[task result path] [evidence path] [artifact root]"
disable-model-invocation: true
---

Verify the deliverable. Optional paths: $ARGUMENTS

Run the real validators and report their real output. A description of a check is not a check.

1. Resolve inputs: the atomic task result JSON, the evidence bundle JSON and the artifact root. If any is missing, say which, and run the checks that remain possible.
2. Run, in order, and show each command with its actual output:

```
python skills/shared-data-core/scripts/validate_task_result.py <result> --task-catalog task-catalog.json --mode complete
python skills/shared-data-core/scripts/validate_evidence_bundle.py <evidence> --artifact-root <root> --mode complete
python skills/shared-data-core/scripts/verify_deliverable.py <result> <evidence> --artifact-root <root>
```

3. Interpret exit codes honestly: `0` passed, `1` failed, `2` incomplete because a check could not be run. **`incomplete` is not `passed`.** Report `not-run` checks as unproven, never as satisfied.
4. If the task result claims a state of `approved`, `released`, `monitored` or `complete`, also validate the approval record with `/dd-approve` before accepting the claim.
5. List every unsupported claim: any assertion in the result that no evidence envelope with a verified artifact hash supports.

Return: overall verdict (passed / failed / incomplete), the count of verified versus unproven claims, each failed check with its validator message, and the specific next action that would close each gap. Never upgrade an `incomplete` verdict to a pass in prose.
