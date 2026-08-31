---
name: dd-plan
description: Turn intent into an approved specification and task list before anything is built, collecting the plan's risky operations for one approval instead of interrupting the run later.
argument-hint: "[what you want built]"
disable-model-invocation: true
---

Plan stage of the harness delivery loop. Intent: $ARGUMENTS

Read `skills/data-department-orchestrator/references/harness-delivery-loop.md` first.

1. Select the atomic tasks this work needs by primary deliverable, and name the ones you are deliberately leaving out. A plan without exclusions is a plan whose scope will surprise someone later.
2. Write the specification and the acceptance criteria **now**, before any implementation. Criteria written after seeing the artifact describe the artifact.
3. Run `orchestrator-collect-plan-risk`: enumerate every operation this plan implies that touches billing, network egress, secrets, production or anything outside the working tree. Present them together in `harness-approval.yaml` with a scope, an expiry and a use count.
4. Record the plan as a workflow manifest so Work and Review have something to check against.

**Gate.** Nothing is built until a named human approves the contract. You cannot approve it yourself, and "the plan was obvious" is not approval. State plainly that the plan is **unapproved** and stop.
