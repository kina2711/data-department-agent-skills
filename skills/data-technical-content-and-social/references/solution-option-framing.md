# Solution option framing

Use before committing to a design, specification, model, plan, architecture or program. A first idea presented as the only idea hides the trade-off the reviewer needs to see.

## Step-back procedure

1. Before drafting, list three to five candidate approaches at the level of approach, not implementation detail. Two variants of the same approach count as one option.
2. For each option record three to five defining points, what it optimizes for, and the condition under which it is the wrong choice.
3. Select one and justify the selection in at most forty words, against the stated constraints rather than preference.
4. Record each rejected option with the reason it lost and the signal that would reopen the decision.
5. Derive the deliverable's structure from the selected approach. An outline that would be identical under any option means the framing was decorative.

Do not manufacture filler options to reach a count: three genuinely different approaches beat five where two are padding. When only one approach is viable, say so and name the constraint that eliminates the others — that is still a recorded decision, not a skipped step.

## Where it applies

Required when the primary deliverable is a specification, design, architecture, model, strategy, plan, curriculum or program. Not required for read-only inspection, mechanical execution of an already approved design, or incident recovery where the recovery path is prescribed. Where the role already owns a scored selection artifact, use that artifact instead of duplicating the decision.

## Result envelope

Return prose and a structured record together. The option set belongs in `design-option-set.yaml`; the task outcome belongs in `atomic-task-output.yaml`, whose fields mirror the return contract — task, status, phase reached, deliverable, evidence, test results, gate results, approval, assumptions, limitations, residual risks and next task/owner. Validate it with `shared-data-core/scripts/validate_task_result.py` when the script is reachable.

The structured record is a mirror of the reported outcome, not a second version of it. If the prose claims a pass that the record does not carry, the record wins and the task is not complete.
