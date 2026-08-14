# Forward test: Interview Knowledge Deep-Dive System v2.2

Date: 2026-08-13

## Scope

Fresh agents tested the new cross-role capability without being shown the implementation rationale:

1. Convert one interview question into a complete learning dossier.
2. Validate whether a question measures the intended competency without leaking a model answer.
3. Convert multiple approved dossiers into a linked, versioned, Notion-ready knowledge library.

## Results

| Scenario | Expected route | Result | Status |
|---|---|---|---|
| One RTM interview question | `career-build-question-deep-dive` | Selected the dossier task after boundary refinement; rejected the multi-dossier library task | PASS |
| Question validity and evidence | `talent-map-question-to-competency-evidence` | Produced outcome-to-competency-to-question-to-evidence traceability, anchored scoring, standardized probes and leakage/fairness controls | PASS |
| Multiple linked and versioned dossiers | `enable-build-versioned-knowledge-library` | Selected the governed library task; rejected a standalone article; kept publication downstream | PASS |

## Defects found and corrected

- The first single-question test selected `career-build-interview-knowledge-library`. The career skill now states that one complete question dossier routes to `career-build-question-deep-dive`; the library task requires multiple approved dossiers plus taxonomy, backlinks and version metadata.
- The first multi-entry knowledge-library test selected `enable-create-knowledge-article`. The enablement skill now distinguishes one standalone note from a governed, linked and versioned collection.

## Acceptance evidence

- Single-question versus multi-dossier boundary: PASS.
- Standalone article versus governed library boundary: PASS.
- Publishing is treated as a reviewed downstream handoff: PASS.
- Authentic evidence is required; hypothetical STAR examples must be labeled and cannot be presented as candidate history: PASS.
- Memorized answer reproduction is not accepted as competency evidence; novel transfer/retest is required: PASS.

No production data, hiring decisions or external knowledge platform were changed during these tests.
