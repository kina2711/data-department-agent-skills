# Career learner memory and skill-transition method

Career owns the learner's semantic state; role skills consume it, and Personal Second Brain may store it. Use one versioned canonical memory rather than relying on chat history.

## State and evidence

Track each topic as `unseen`, `exposed`, `practiced`, `demonstrated`, `mastered`, `stale`, `conflicted` or `retired`. Recording a course, explanation or event never promotes mastery by itself. `mastered` requires independent application, a changed-scenario transfer check, evidence references, limitations, a compact reusable summary and a freshness date. Production experience remains a separate evidence class.

Store durable concepts, interfaces, decision rules, failure modes and evidence pointers; do not store raw secrets, unnecessary personal data or full lesson transcripts. Append learning events and derive the current topic state. Preserve prior versions and conflicts rather than silently overwriting them.

## Transition policy

For the next skill, classify prior topics:

- `mastered` + fresh + indirect: reuse without reteaching; one-line summary and evidence pointer.
- `mastered` + fresh + direct prerequisite: compact bridge containing only relevant interfaces, decision rules and failure modes.
- `practiced` or weak evidence: concise recap plus one diagnostic or transfer exercise.
- `stale`, `conflicted`, version-shifted or safety/semantic critical: expand and retest before dependency-sensitive work.
- unknown: ask or abstain; never infer completion from conversation history.

Example: after verified Airflow mastery, a dbt transition should summarize orchestration boundaries, scheduling interfaces, retries/idempotency and how dbt jobs are invoked. It should not reteach DAG syntax unless the new task depends on it, the evidence is stale or the learner asks.

Resolve memory from an explicit locator first, then a project pointer under `.claude/data-department-memory/`, then the configured user-level Claude memory root. Use `validate_learning_memory.py` before relying on mastery and `build_skill_transition_context.py` to produce the bounded pack. Memory mutation is an explicit Career task; ordinary role skills remain read-only consumers.
