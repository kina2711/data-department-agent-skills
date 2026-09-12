# Snowflake adapter

## Detect and bind the context

Capture account/region, role, database/schema, warehouse, client/driver and object versions. Inspect role hierarchy, masking/row-access policies, streams/tasks/dynamic tables, stages, shares and resource monitors. Never print credentials or session tokens.

## Safe execution

Start with metadata, query profile and bounded read-only SQL. Use explicit role/database/schema/warehouse and query tags. For changes, generate/review DDL, scope grants, clone/backup where appropriate and bind approval to exact statements/objects.

## Tests and proof

Validate grain, null/duplicate behavior, time travel/retention assumptions, incremental state, stream consumption, task dependencies, policy enforcement, query plan/bytes/spill, warehouse size and credit impact. Reconcile source/target and capture query IDs, object definitions, result hashes and role evidence.

## Release traps

Block implicit context, broad ownership/grants, destructive replacement, consumed stream without recovery, warehouse scaling without cost bound, zero-copy clone mistaken for backup or query improvement measured without identical cache/workload conditions.
