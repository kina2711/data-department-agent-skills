# Data Department Agent Skills v3.2.0

This release adds persistent, evidence-bound Learning Memory across all 32 Claude skills. The suite now contains 809 atomic workflows.

## What changed

- Career now owns seven new workflows for learner-memory initialization, cross-skill prerequisite mapping, bounded transition context, append-only learning events, mastery assessment, decay detection and memory reconciliation.
- Every role skill receives a lightweight interoperability contract so it can reuse verified prior knowledge without loading or repeating the full learning history.
- `mastered` cannot be inferred from reading, attendance or chat history. It requires verified evidence, sufficient confidence, a demonstrated transfer and a valid review date.
- Fresh mastered prerequisites are compressed according to relevance. Stale, conflicted, version-shifted or safety-critical prerequisites are expanded and retested.
- A Draft 2020-12 learner-memory schema, templates, validator and token-bounded transition-context builder are included.

## Airflow → dbt behavior

When Airflow is fresh and evidence-backed, a dbt learning task receives only the orchestration/transformation boundary, invocation interface, retry/idempotency decisions and relevant failure modes. DAG fundamentals are not taught again. If the Airflow review is overdue or the relevant interface changed version, it moves into the refresh/retest set.

## Validation

- 32 Claude skills and 809 linked task contracts.
- 35 natural-language routing cases.
- 37 role-confusion cases.
- 41 catalog-routing cases.
- 13 lifecycle cases.
- 34 deterministic benchmark/control tests.
- 94 enforced, 163 deep and 552 standard task contracts.

The release remains local-first and requires no external memory API, note application or MCP server.
