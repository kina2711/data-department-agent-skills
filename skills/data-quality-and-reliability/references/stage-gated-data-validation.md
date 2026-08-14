# Stage-gated data-validation standard

Validate the pipeline at four layers; do not rely on a final row count as the only control.

| Layer | Typical controls | Failure action |
|---|---|---|
| Input | Schema/type, required fields, source freshness, file/API metadata, duplicates and volume bounds | Reject, quarantine or pause before transformation |
| Transformation | Grain/key preservation, row-count deltas, value ranges, business invariants and deterministic/idempotent behavior | Fail the stage and retain diagnostic evidence |
| Output | Referential integrity, uniqueness, control totals, source-target reconciliation, partition completeness and consumer contract | Block publish/promotion or mark dataset unavailable |
| Monitoring | Freshness, volume/distribution anomaly, SLA/SLO, repeated quarantine, schema drift and alert delivery | Page/route to owner and start incident workflow |

Every rule needs an owner, severity, threshold rationale, evaluation scope, evidence location and explicit action. Calibrate anomaly thresholds on representative history; keep missing data distinct from valid zeros. Test the tests with known-bad fixtures and failure injection. Exceptions require scope, approver, expiry and compensating control.
