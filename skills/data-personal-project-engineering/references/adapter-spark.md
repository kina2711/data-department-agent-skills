# Spark adapter

## Detect and bind the version

Capture Spark distribution/runtime, language, JVM, connector/table-format and cluster configuration. Inspect submit configuration, dependencies, adaptive execution, serialization, partitioning and catalog bindings. Do not compare plans across materially different configs as if equivalent.

## Read-only preflight

Inspect logical/physical plans and input statistics before tuning. Record whether the adaptive plan is final. Check file counts/sizes, partition columns, join keys, skew, shuffles, exchanges, spills, cache/checkpoint use and UDF boundaries.

## Execution and proof

Build a representative bounded fixture and correctness baseline. Change one hypothesis-controlled variable at a time. Compare outputs/checksums, stages/tasks, shuffle read/write, spill, skew, executor utilization, duration and cost envelope over repeated runs. Test empty/skewed/late/duplicate/schema-evolution cases and rerun safety.

## Release traps

Block syntax-only optimization, blind repartition/coalesce/cache, broadcast without size evidence, benchmark on nonrepresentative data, ignored adaptive-plan state or a faster result whose semantics changed.
