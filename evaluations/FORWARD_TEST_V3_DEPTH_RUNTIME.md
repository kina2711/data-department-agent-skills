# Forward tests — v3.0.0 Depth, Runtime and Stack Adapters

Date: 2026-08-14

Fresh agents received realistic user requests and the routed skill artifacts. They were not given expected answers or evaluation fixtures. All target-repository work was read-only.

## 1. Cross-role workflow runtime

The initial Finance reporting rebuild test selected `orchestrator-compose-workflow` and produced a sensible cross-role graph, but used invented workflow-instance labels as `task_id`, used the invalid claim status `pending`, and skipped deterministic validation because the request was read-only.

The release was tightened without weakening the test:

- Compose, maintain-state, resume and completion-assessment tasks became `enforced`.
- `task_id` is reserved for exact IDs in `task-catalog.json`; optional `instance_id` is only a display label.
- Claim status is restricted to `draft`, `verified` or `rejected`, and the validator now rejects other values in every mode.
- Read-only planning explicitly permits and requires a temporary manifest outside the target repository.

Fresh retest from the raw request selected `orchestrator-compose-workflow`, generated a temporary manifest with 33 exact canonical task IDs and 53 dependency edges, set workflow risk floor to `R3-controlled`, and kept all claims `draft`. The first plan validation correctly rejected a missing claim `wording`; the agent repaired the manifest rather than explaining away or weakening the rule. Final `validate_workflow.py --mode plan` returned exit code 0. An independent topology/risk/role/state check also passed. The temporary manifest hash was `a3e0fc02b27f506db6ed4f8c437bf4e9ebd4515777ab276fdd88bd00f5f7bcb3`; it was deleted after validation and confirmed absent.

Result: **PASS after one contract-hardening iteration.**

## 2. Repo-first personal project

A fresh repo-first assessment against `C:\PROJECT\e-commerce_dwh` selected `project-audit-reference-repository` and performed a read-only evidence audit. It distinguished the parent Git root from a standalone repository, identified missing dataset provenance/rights, verified existing dbt artifacts and bounded local checks, preserved synthetic-versus-real-source limitations, and separated implemented, locally tested, released and operationally proven states.

The agent produced a 12-dimension assessment, `reuse/adapt/replace/drop/build-new` matrix, differentiated user-owned thesis, prioritized reliability/governance roadmap, honest interview claims, and exact next task. It ran only bounded checks, verified the repository snapshot hash before/after, and did not mutate the target.

Result: **PASS.**

## 3. Airflow stack adapter

A fresh Data Engineering review against `C:\PROJECT\i-learn-airflow` selected `de-review-data-engineering-change` and loaded only the Airflow adapter plus routed task references. It separated AST/static evidence from Airflow runtime evidence, challenged README claims, and inspected idempotency, backfill safety, reconciliation, dependency pinning and reproducibility.

The result correctly classified the repository as `static-review passed, runtime certification blocked`, proposed the smallest evidence-building sequence, and did not equate syntax parsing or local adapter tests with scheduler/executor correctness.

Result: **PASS.**

## Release conclusion

The tests show that v3 routing is not only broad but operationally constrained: exact task identity, risk floors, legal state transitions, evidence-bound claims, stack-specific review and read-only validation behavior survive fresh-agent pressure. The workflow test found a material loophole before release; the retest closed it without task inflation or relaxed acceptance criteria.
