# dbt adapter

## Detect and bind the version

Inspect `dbt_project.yml`, `packages.yml`/lock, profiles indirection, adapters, macros, state artifacts and orchestrator integration. Capture dbt Core/Cloud and adapter versions from the target environment. Treat manifest schema and command behavior as version-sensitive.

## Read-only preflight

Run version/debug/parse or equivalent without publishing. Inspect sources, exposures, semantic models/metrics, contracts, snapshots, seeds, incremental predicates, grants and selectors. Never expose profile secrets.

## Execution and proof

Compile first; build a bounded selector with upstream/downstream scope made explicit. Test uniqueness/not-null/relationships/accepted values, custom business invariants, source freshness, contracts and reconciliation. For incremental models compare clean full-refresh output with incremental/rerun behavior, late updates and schema changes. Preserve `manifest.json`, `run_results.json`, compiled SQL, invocation ID and warehouse query evidence.

## Release traps

Block on grain-changing joins, ungoverned metric semantics, state comparison from incompatible manifests, destructive full refresh without approval, silent schema evolution, tests with no failure action or passing only because rows are excluded.
