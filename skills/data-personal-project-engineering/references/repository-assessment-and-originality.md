# Repository assessment and originality standard

## Evidence capture and rights gate

Resolve URL/path, owner, exact commit/tag, access date, visibility, license/terms, archived/maintenance state and a bounded source snapshot/hash. Inspect `LICENSE`, notices, README, contribution rules, citation metadata and generated/vendored components. Viewing or forking on GitHub does not itself grant permission to reproduce or distribute derivative work; the license controls reuse.

Do not execute untrusted repository code on the host by default. Inspect manifests, scripts, workflows, containers, hooks, secrets patterns and dependency sources first; use a bounded disposable environment when execution is needed.

## Assessment dimensions

For each dimension, record observed evidence, strength, finding, impact, uncertainty, recommendation and validation:

1. Purpose and users: stated problem, actual consumer, outcome and unsupported claims.
2. Architecture and data flow: components, boundaries, source-to-output path, state and coupling.
3. Runtime and reproducibility: prerequisites, pinned versions, setup, sample data, deterministic commands and cleanup.
4. Data contracts and modeling: grain, keys, schemas, invariants, lineage, quality and evolution.
5. Correctness and tests: unit/contract/integration/E2E coverage, edge cases, reconciliation and test truthfulness.
6. Security, secrets and dependencies: credentials, permissions, input handling, vulnerabilities and dependency trust.
7. CI/CD and supply chain: protected changes, pinned automation, build provenance, artifact integrity and release process.
8. Observability and reliability: logs, metrics, alerts, idempotency, retry, timeout, rollback, recovery and runbook.
9. Performance and cost: baseline workload, bottlenecks, resource use, cost model and benchmark validity.
10. Documentation and developer experience: architecture, setup, commands, decisions, examples, troubleshooting and accessibility.
11. Maintainability and activity: modularity, duplication, ownership, issue/PR/release health, staleness and upgrade path.
12. License and provenance: permissions, obligations, upstream attribution, datasets/models/fonts/assets and incompatible terms.

Run the smallest safe baseline that proves the advertised path. Record environment, commands, inputs, outputs, failures and actual status. Do not infer quality from stars, screenshots, README claims or a green badge alone. OpenSSF Scorecard is a useful security heuristic, not a complete quality verdict.

## Findings and improvement plan

Rate findings `P0` unsafe/invalid, `P1` blocks core outcome, `P2` material quality gap, or `P3` improvement. Every finding needs a concrete locator/evidence, consequence, recommended change and verification method. Separate strengths, limitations and unknowns; do not manufacture defects to justify a rewrite.

Classify every relevant component:

- `reuse`: validated fit; preserve with attribution and regression proof.
- `adapt`: sound core but contract, context or quality differs.
- `replace`: incompatible architecture, risk, correctness or maintainability.
- `drop`: no support for the new thesis.
- `build-new`: required contribution absent upstream.

## Transform reference into a personal project

Write an explicit origin statement and a one-sentence new thesis. Preserve an upstream-to-new trace showing what was borrowed, learned, changed, rejected and created. Require at least three substantive differentiation axes for an inspiration/adaptation/fork project. Each differentiator needs a baseline, planned delta and proof method.

The final assessment must include: executive verdict, verified baseline, architecture/data-flow summary, dimension findings, improvement backlog, reuse matrix, legal/provenance limits, new project thesis, differentiation design, phased roadmap, validation strategy, portfolio evidence and residual risks.
