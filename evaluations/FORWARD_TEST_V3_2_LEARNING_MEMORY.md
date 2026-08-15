# Forward test — v3.2.0 Cross-skill Learning Memory

## Raw prompt

> Tôi đã học xong Airflow và có project cùng bài test. Giờ chuyển sang dbt. Đừng dạy lại Airflow; chỉ tóm tắt phần liên quan và phát hiện phần nào cần ôn/kiểm tra lại.

The evaluator received the raw prompt and inspected the generated Claude skills read-only. It was not given the expected route or assertions.

## Routing result

- Primary skill: `data-career-and-interview-coach`.
- Primary task: `career-build-skill-transition-context`.
- `career-map-cross-skill-prerequisites` is a prior dependency only when the graph is absent/stale.
- `career-detect-learning-decay` is a separate dependency/handoff when freshness or version evidence is unresolved.
- The sentence claiming a completed project/test was correctly treated as an unverified claim until canonical memory and evidence are resolved.

## Expected compression

For verified, fresh Airflow mastery, the dbt transition retains only orchestration-versus-transformation responsibility, invocation/status interfaces, retries/idempotency, failure propagation/rerun behavior, evidence references and the source version. DAG syntax, operators, executors, catchup and backfill are omitted unless directly necessary, stale or explicitly requested.

Expansion/retest is required for practiced/demonstrated-only state, missing or invalid evidence, overdue review, conflict, retirement, version shift, safety-critical prerequisites, absent changed-scenario transfer or unproven failure handling.

## Findings and remediation

The first pass identified these defects:

1. A generic verified learning record could satisfy the old mastery check.
2. The transition builder trusted memory state without validating it.
3. Version drift was carried as metadata but not compared automatically.
4. The token budget could be exceeded with only a warning.
5. Routing wording could imply multiple primary tasks despite the one-task selection rule.

The implementation was tightened before release:

- Mastery now requires verified applied evidence plus verified `changed-scenario` transfer evidence.
- The builder runs complete learner-memory validation and blocks invalid input.
- `--current-version TOPIC=VERSION` sends mismatches to `expand_or_retest`.
- Required over-budget context is blocked and cannot be consumed.
- `career-build-skill-transition-context` is explicitly primary; mapping/decay are dependencies only when needed.

Deterministic regressions cover fresh compression, overdue review, version shift, unsupported mastery and invalid-memory blocking.
