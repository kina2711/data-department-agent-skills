# Databricks and Delta adapter

## Detect and bind the context

Capture workspace/cloud, runtime, Spark/Delta/Unity Catalog, cluster or SQL warehouse policy, job/bundle and library versions. Inspect catalogs/schemas, external locations, volumes, secrets references, repos/bundles and table protocols/features.

## Safe execution

Prefer bundle/config validation, SQL explain and isolated catalog/schema. Review cluster policy and service-principal permissions. Treat notebook output as evidence only when source/version, parameters and run ID are bound.

## Tests and proof

Test Delta constraints/schema evolution, merge keys and duplicate matches, time travel/vacuum boundary, streaming checkpoints, change data feed, expectations, job repair/retry, cluster termination and Unity Catalog access. Capture run/query IDs, table versions, plans, metrics, lineage and cost/runtime context.

## Release traps

Block unpinned runtimes/libraries, personal-token automation, unmanaged mounts, merge ambiguity, vacuum that removes recovery, checkpoint reuse across incompatible code or notebook success without data reconciliation.
