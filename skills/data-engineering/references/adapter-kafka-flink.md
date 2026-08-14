# Kafka and Flink adapter

## Detect and bind the version

Capture broker/client or Flink runtime/connectors, serialization/schema registry, topic/partition settings, consumer groups, checkpoints/savepoints, delivery semantics and deployment mode. Verify version-sensitive APIs in official documentation.

## Read-only preflight

Inspect topic metadata, retention/compaction, ACL references, partition/key strategy, offsets, lag, watermark/event-time logic, state backend, restart strategy and sink transaction support without consuming or resetting production state.

## Execution and proof

Use isolated topics/groups or replayable fixtures. Test ordering by key, duplicate delivery, poison record, schema compatibility, rebalance/restart, backpressure, late events, checkpoint restoration and sink idempotency/transactions. Record offsets/checkpoints/savepoints, input/output counts, lag, state size, recovery point/time and reconciliation.

## Release traps

Block consumer-group reuse, unapproved offset reset, incompatible schema, insufficient partitions/key skew, unbounded state, misleading exactly-once claims or recovery that was not tested end to end.
