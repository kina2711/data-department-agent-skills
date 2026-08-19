---
name: dd-catalog
description: Search the canonical atomic task catalog by keyword, role prefix or deliverable and return matching task IDs with their contracts.
argument-hint: "<keyword, role prefix or deliverable>"
disable-model-invocation: true
---

Search the atomic task catalog for: $ARGUMENTS

1. Read `task-catalog.json` (the canonical machine-readable inventory). Do not answer from memory or from the skill map prose.
2. Match on task ID, deliverable and description. Treat a bare role prefix (`ae`, `de`, `bi`, `mlops`, `career`, …) as a request for that role's tasks.
3. Return at most 15 matches as a table: task ID, owning skill, primary deliverable.
4. If more than 15 match, say how many were found and narrow by the most specific deliverable.
5. If nothing matches, say so plainly and suggest the two closest role catalogs to inspect — do not fabricate a task ID.

Then name the single best candidate and the exact path to its contract file. Do not start the work; use `/dd-task` to load one contract or `/dd-route` for a full routing decision.
