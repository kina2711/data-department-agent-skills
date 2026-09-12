# BigQuery adapter

## Detect and bind the context

Capture project, location, dataset, principal, reservation/edition, client and table/view/model versions. Inspect partitioning/clustering, authorized views, row/column policies, scheduled queries, Dataform/dbt integration and transfer jobs.

## Safe execution

Use dry run/query plan and maximum-bytes-billed controls before material scans. Qualify project/dataset/table names and location. Scope service-account permissions and never expose credentials. Stage mutations into bounded destinations when feasible.

## Tests and proof

Validate partition pruning, bytes processed, slot time, shuffle, join cardinality, approximate functions, timestamp/timezone semantics, streaming/upsert duplication and source-target reconciliation. Capture job IDs, dry-run bytes, plan statistics, object definitions, hashes and cost assumptions.

## Release traps

Block missing partition filters, cross-location assumptions, broad IAM, accidental full-table rewrite, cached-result benchmark, schema relaxation without contract review or cost claims without job/reservation evidence.
