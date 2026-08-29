# Context engineering standard

Use context as a governed retrieval layer, not as one oversized prompt or a substitute for live inspection.

## Persistent index versus task package

- A **context index** is a durable map of sources, authority, ownership, scope, freshness and load conditions. It points to knowledge; it does not duplicate every source.
- A **task context package** is a bounded, versioned snapshot for one objective and primary deliverable. Build it from the index and record exact source hashes.

## Required layers

1. Task: objective, decision, primary deliverable and acceptance criteria.
2. Business: domain terms, owners, metric semantics and relevant rules.
3. Data: schemas, grain, keys, lineage, quality and freshness.
4. Implementation: repository paths, runtime, interfaces, environments and current behavior.
5. Evidence: prior findings, decisions, tests, incidents and approved artifacts.
6. Constraints: permissions, sensitivity, policies, budget, deadline and prohibited actions.
7. Output contract: required format, tests, approval and handoff.

## Packaging procedure

1. Start with the smallest set that can change the current decision; do not load sources only because they exist.
2. Prefer authoritative and current sources. Preserve conflicts instead of silently choosing one.
3. Record path or URI, owner, authority, last-verified date, sensitivity and SHA-256 where a local file is used.
4. Deduplicate exact content and summarize only when the original remains linked.
5. Estimate tokens and trim in this order: decorative examples, repeated prose, stale prior findings, noncritical background. Never trim acceptance criteria, safety rules, schema/grain, unresolved conflicts or evidence needed for validation.
6. Scan for secrets and unnecessary sensitive data. Link protected material rather than copying it when permissions may differ.
7. Validate the package by asking whether a fresh agent can identify the task, unknowns, authority, constraints, required tests and output without hidden context.

The package may enable progress with bounded assumptions, but it must never turn missing authority, live state or critical semantics into an assumed fact.

## Session-boundary handoff

Run state records where work stands: phase, current task, gates passed, what blocks it. It records nothing about how the session arrived there — the approach tried and abandoned, the assumption everything else rests on, the reason the obvious solution does not work here. A successor resuming from run state alone re-derives that reasoning, sometimes differently, and sometimes by repeating the abandoned approach.

Write a handoff when a session ends with work unfinished. It carries only what no durable artifact already holds.

- The task and where it actually stands, stated separately from where the plan says it stands.
- What was tried and rejected, with the reason. This is the highest-value content in the document and the only part that disappears completely when the session does.
- The load-bearing assumption: the one that, if wrong, invalidates the rest of the work.
- The next action, and why that one rather than the alternatives already considered.
- Which skills and task IDs the successor should route to, so a routing decision already made is not made again and differently.
- Open questions waiting on a named person.

Leave out anything a spec, plan, ADR, issue, commit, diff or run-state record already holds; reference it by path, hash or URL. A handoff that restates the plan is a second copy of the plan, and it will drift from the first.

Write it to the operating system's temporary directory or a configured scratch location, never into the workspace unless the user asks for it there. A handoff is working scratch, not a deliverable: written into the repository it gets committed, then reviewed, then eventually believed.

A handoff is not evidence, not an approval and not a claim that anything finished. A gate the session did not pass stays unpassed however the document describes it. Redact secrets, credentials and personal data before writing — a scratch file is still a file.
