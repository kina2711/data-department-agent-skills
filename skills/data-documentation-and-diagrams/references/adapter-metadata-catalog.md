# DataHub and OpenMetadata adapter

## Detect and bind the version

Capture platform/server and ingestion framework versions, metadata model, auth method, source connector recipe and target environment. Inspect custom entities/aspects, lineage sources, ownership/tag/domain policies and search configuration.

## Safe execution

Validate recipes/config and secrets indirection before ingestion. Start with bounded sources/assets and dry-run or isolated target when supported. Distinguish harvested, declared and inferred metadata and retain source/run timestamps.

## Tests and proof

Reconcile expected versus ingested assets/columns/owners/lineage edges, sample field values and confidence, search/findability, stale deletion behavior, schema history and policy effects. Capture run ID, recipe hash, connector logs, coverage/freshness and representative lineage/search tests.

## Release traps

Block broad destructive cleanup, inferred lineage presented as observed, connector credentials in files, unstable identifiers, ownership overwritten without authority, silent stale metadata or coverage claims from only successful connector status.
