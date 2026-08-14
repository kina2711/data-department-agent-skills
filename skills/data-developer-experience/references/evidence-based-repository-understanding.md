# Evidence-based repository understanding

A repository summary is orientation, not proof of understanding. Build a mental model by tracing one real path end to end and testing predictions against observable behavior.

## Trace protocol

1. Choose one bounded user/business event, job run or source record and name the expected sink/output.
2. Locate the real entry point: scheduler/DAG, command, API, notebook or job configuration.
3. Follow imports, dependencies, schemas, SQL/models, storage writes and downstream consumers. Cite file paths, symbols and configuration rather than describing from memory.
4. At each boundary record input grain/contract, transformation, output grain/contract, side effects, retry/checkpoint behavior and failure route.
5. Before running anything, write a prediction for a deterministic fixture or known record: which stages execute and what output/control totals should appear.
6. Run the narrowest safe test or inspect existing execution evidence. Reconcile prediction versus observed output and update the trace.
7. Inspect one failure path, late/duplicate record or changed assumption. Verify handling rather than inferring it from a happy-path name.
8. End with unknowns, confidence and learning questions. A walkthrough should enable the learner to predict a changed scenario without notes.

Use a metadata lineage task when the primary deliverable is an enterprise lineage graph. Use this method when the deliverable is evidence-based repository understanding and a validated path trace.
