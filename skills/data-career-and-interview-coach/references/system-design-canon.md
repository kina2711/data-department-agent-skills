# Data system-design canon

Use this as the shared concept registry for interview knowledge work, not as study content. Every entry is a canonical concept ID that a question dossier, knowledge map, case study or visual explainer links to. Write each explanation yourself from primary sources.

## Concept domains and canonical IDs

| Domain | Canonical concept IDs |
|---|---|
| Ingestion | `sd.ingest.batch-extract`, `sd.ingest.cdc-log`, `sd.ingest.cdc-query`, `sd.ingest.api-pagination`, `sd.ingest.backpressure` |
| Streaming | `sd.stream.delivery-semantics`, `sd.stream.ordering-and-keys`, `sd.stream.windowing`, `sd.stream.watermark-and-late-data`, `sd.stream.replay` |
| Storage | `sd.store.row-vs-columnar`, `sd.store.file-layout-and-size`, `sd.store.table-format-acid`, `sd.store.partitioning`, `sd.store.clustering-and-sort`, `sd.store.compaction` |
| Distribution | `sd.dist.sharding-key`, `sd.dist.replication`, `sd.dist.consistency-model`, `sd.dist.quorum`, `sd.dist.partition-tolerance-tradeoff` |
| Processing | `sd.proc.shuffle-and-skew`, `sd.proc.join-strategy`, `sd.proc.incremental-vs-full`, `sd.proc.idempotency`, `sd.proc.backfill-and-restatement` |
| Serving | `sd.serve.cache-strategy`, `sd.serve.cache-invalidation`, `sd.serve.precompute-vs-query-time`, `sd.serve.concurrency-and-isolation` |
| Reliability | `sd.rel.slo-freshness`, `sd.rel.retry-and-dlq`, `sd.rel.schema-evolution`, `sd.rel.lineage-and-impact`, `sd.rel.failure-domain` |
| Governance and cost | `sd.gov.access-model`, `sd.gov.pii-boundary`, `sd.gov.retention`, `sd.cost.storage-vs-compute`, `sd.cost.scan-reduction` |

Add a domain or ID only with an explicit definition and owner. Never mint an ID inside a single deliverable; register it here first so dossiers, maps, case studies and explainers stay joinable.

## Design answer frame

Move `Clarify → Constrain → Contract → Component → Consistency → Cost → Collapse`:

1. **Clarify** the decision the system serves, its users and the read/write pattern.
2. **Constrain** with explicit numbers — event rate, rows per day, retention, freshness target, concurrency, budget — and mark every number you assumed rather than were given.
3. **Contract** the data: grain, keys, schema-evolution policy, delivery semantics and ownership.
4. **Component** the flow source → ingest → store → process → serve, naming one rejected alternative per hop and why it lost.
5. **Consistency**: what may be stale, what must be exact, and how duplicates, late data and replays are handled.
6. **Cost and operations**: scan/compute profile, failure domains, on-call surface, SLO and its recovery path.
7. **Collapse** into trade-offs: the two or three decisions you would revisit first and the signal that would force the change.

Depth rises with level: Foundation names the components; Practitioner defends the contract and failure handling; Advanced quantifies trade-offs and migration; Lead argues the operating and cost model. A named reference architecture recited without constraints is not an answer.

## Visual mental model rule

Each concept carries at most one diagram, and that diagram must show the mechanism rather than decorate it. Specify elements, relationships, the single takeaway, what the reader should observe, the common misreading and alt text. Specification belongs to `career-design-concept-visual-explainer`; rendering belongs to `data-documentation-and-diagrams`.

## Source policy

Prefer primary sources: project and vendor documentation for the exact version, papers, and first-party engineering blogs. Record source URL, version or date, accessed date, and whether each claim is documented, measured or inferred.

Curated third-party collections — public system-design cheat-sheet repositories, course notes, summary threads — are navigation aids only. Cite them as a pointer and verify the underlying primary source. Material under `NonCommercial` or `NoDerivatives` terms may be linked and quoted briefly with attribution, but never copied, translated, redrawn or adapted into a deliverable.
