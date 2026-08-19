---
name: dd-route
description: Route a Data Department request to exactly one owning role skill and one canonical atomic task, without executing it yet.
argument-hint: "<request in any language>"
disable-model-invocation: true
---

Route this request: $ARGUMENTS

Do not execute the work yet. Produce a routing decision only.

1. Restate the request as a **primary deliverable**, not a job title. If the request names several deliverables, list them and say which one is first.
2. Identify the owning role skill from `suite-manifest.yaml`. If two roles plausibly own it, name both and state the tie-break reason.
3. Search `task-catalog.json` for the single best-matching atomic task ID. Never invent an ID. If nothing matches within one role, route to `data-department-orchestrator`.
4. Read that task contract completely from `skills/<role>/references/tasks/<task-id>.md` and report its lifecycle profile, risk tier and execution path.
5. State what inputs are missing and whether each missing input is **blocking** (changes semantics, risk, cost, scope or acceptance) or a **bounded assumption**.
6. Name the approvals and evidence the contract requires before completion.

Return: primary deliverable, owning skill, task ID, profile, risk tier, execution path, blocking gaps, bounded assumptions, and the single next action. If the request spans multiple roles, return the orchestrator task ID and the ordered task chain instead.
