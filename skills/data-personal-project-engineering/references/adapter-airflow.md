# Airflow adapter

## Detect and bind the version

Inspect `pyproject.toml`, requirement/constraint files, Docker/Astro configuration, DAG folders, provider packages and deployment metadata. Capture Airflow, Python and provider versions from the intended environment; never infer runtime support from DAG syntax alone. Verify version-sensitive commands and public interfaces against current official Airflow or managed-service documentation.

## Read-only preflight

Inspect imports, DAG discovery paths, timetable/schedule semantics, connections/variables references, datasets/assets, pools, executors, serialization and secrets backends. Scan plugins, startup hooks and container scripts before executing untrusted code. Prefer a disposable environment.

## Execution and proof

Use the environment-native parse/import-error command, targeted DAG/task test and a bounded representative run. Test logical date/data interval, retries, timeout-after-side-effect, idempotency, backfill/catchup, late data, partial mapping, trigger rules and cleanup. Record exact image/constraints, command, run ID, task logs, emitted data and reconciliation. A successful parse is not scheduler/executor or data correctness proof.

## Release traps

Block on unpinned Airflow/providers, hidden connection assumptions, top-level side effects, non-idempotent writes, ambiguous timezone/data interval, unsafe backfill, missing alert ownership or absent recovery evidence.
