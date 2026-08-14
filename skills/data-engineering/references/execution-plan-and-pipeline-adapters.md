# Execution-plan and pipeline-adapter method

Inspect behavior before recommending a fix. Generated code or framework familiarity is not evidence that the plan is efficient or reliable.

## Plan-first diagnosis

1. Capture engine, version, environment/config, query/job identifier and the exact command used to obtain the plan.
2. Establish baseline duration, input/output size, tasks/partitions, bytes scanned, shuffle, spill, skew, memory/GC and cost when available.
3. For SQL, inspect scan/pruning, estimates versus actuals, join order/type, redistribution, repeated scans, sorts, aggregation and materialization.
4. For Spark, inspect exchanges, wide transformations, stage boundaries, partition count/size, skew, broadcast decisions, cache/recompute, spill and small-file effects.
5. Form a falsifiable hypothesis for each bottleneck. Change one material variable at a time and compare equivalent workloads.
6. Preserve correctness with row counts, control totals, hashes/samples and edge cases. A faster wrong result is failure.

## Orchestrator adapter checklist

For Airflow, Prefect, Dagster or another orchestrator, adapt syntax only after confirming framework/version. Preserve the same semantic controls: stable task IDs, explicit dependencies, bounded retries/backoff, timeouts, concurrency, idempotency, checkpoint/watermark, SLA/alerts, secret references, testability and backfill/catch-up policy.

## Pipeline error handling

Classify transient, permanent, data-quality and code/config failures. Define retry eligibility, attempt budget, quarantine or dead-letter route, alert ownership, replay criteria and reconciliation after recovery. Do not retry deterministic bad data indefinitely or acknowledge records before durable processing when that breaks the required delivery semantics.
