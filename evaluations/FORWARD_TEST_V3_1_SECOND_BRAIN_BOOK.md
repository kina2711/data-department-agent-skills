# Forward tests — v3.1.0 Second Brain and Book-to-Knowledge

Date: 2026-08-14

Fresh agents received only raw user prompts and the local suite. All tests were read-only; no source was moved, modified or published.

## Personal Second Brain

Prompt: design a reversible migration from Notion export, PDF/transcript folders and Obsidian into `1_Nguon / 2_Wiki / 3_Toi / 4_Ket-Qua`, preserving privacy, source lineage and representative retrieval tests.

Result:

- Correctly selected `personal-second-brain-and-knowledge-os` and `brain-plan-tool-migration` with `design-specification / R1-reviewed / standard-path`.
- Kept source snapshots immutable, separated Wiki synthesis and personal context, blocked cutover until paths/owner/reviewer/rights/privacy thresholds exist, and proposed hash/count/link/lineage/restore gates.
- Included citation, ambiguous-query, conflict, abstention, forbidden-source, freshness and output-lineage retrieval cases.
- The first pass exposed Windows CP1252 output friction. All four new runtimes now explicitly configure UTF-8 stdout/stderr. A fresh PowerShell retest with `PYTHONUTF8` and `PYTHONIOENCODING` unset preserved Vietnamese paths and exited correctly without repository changes.

## Book-to-Knowledge

Prompt: analyze `LIFECYCLE_OPERATING_MODEL.md`, recover its structure and exact framework locators, plan a Second Brain pack and then a Career application handoff with changed-scenario exercises; do not publish or infer rights.

Result:

- Correctly selected `book-to-knowledge-and-action`, captured the source SHA-256 and line locators, treated absent rights as unverified/private-only, and separated source headings from synthesis and future personal application.
- Proposed the exact handoff sequence: source rights/structure/framework cards → `book-build-second-brain-pack` → Second Brain owner → `book-build-career-application-pack` → Career owner → changed-scenario transfer tests.
- The first pass exposed a taxonomy collision: the verb `recover` classified document-structure extraction as production incident recovery (`R3`). The classifier now treats book structure recovery as `build-change / R2-standard / standard-path`; real Second Brain restore remains incident recovery.
- A fresh retest selected `book-extract-frameworks` for the prompt's primary deliverable and preserved the corrected R2 build path. It checked beginning/middle/end structure, heading-derived names, balanced fences and prompt-injection signals, while refusing completion because rights and transfer tests were unresolved.

## Residual boundaries

- A plan is not an imported vault or generated pack.
- Local access is not redistribution or publication authority.
- `3_Toi` remains user-supplied personal context; the agent cannot invent experience or voice evidence.
- Book conversion owns source distillation; Second Brain, Career, Academy and Technical Content own their downstream operating outcomes.
