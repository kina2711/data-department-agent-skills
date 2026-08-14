# Workflow Runtime and Evidence OS

Use this reference when work spans multiple tasks, carries `deep` or `enforced` criticality, crosses an approval gate, resumes from saved state, or makes a completion/release claim.

## Executable workflow contract

Represent the workflow with `workflow-manifest.json`. Every `task_id` must exactly match an ID in the canonical `task-catalog.json`; use optional `instance_id` only for a human-friendly occurrence label. Keep one accountable owner per task, explicit dependencies, catalog risk as a non-downgradable floor, artifact version/hash, evidence references and approval references. Claim status must be exactly `draft`, `verified` or `rejected`. The graph must be acyclic. A task may execute only after every dependency is `released` or `complete`.

Run `data-department-orchestrator/scripts/validate_workflow.py` with the canonical `task-catalog.json`. Use `plan` while composing, `execute` before or after a transition, and `complete` before the final claim. Read-only work still requires deterministic validation using a temporary manifest outside the target repository; it does not authorize target-repository changes. Do not manually explain away a validator failure.

## Evidence envelope

Bind each material claim to a versioned artifact and a structured envelope containing task, claims, SHA-256, environment, method/command, expected and observed results, exit status, timestamp, actor and limitations. `not-run` is an honest status, never completion proof. Run `shared-data-core/scripts/validate_evidence_bundle.py`; in complete mode, verify local artifact existence and hash when an artifact root is available.

## Approval binding

Approval binds to task, scope, risk, artifact version and artifact SHA-256. R3/R4 execution requires explicit authority before mutation. Any change to scope/version/hash expires the decision. Approval never substitutes for evidence, and evidence never substitutes for accountable authority.

## State and claim rules

- `implemented` means an artifact exists, not that it passed.
- `tested` requires resolved evidence envelopes.
- `approved` requires evidence plus a valid version-bound approval when risk is above R0.
- `released` requires the exact approved artifact and live smoke/reconciliation evidence.
- `complete` requires all tasks released/complete and every public/material claim verified or rejected.
- Failed tests, blocked dependencies and rejected approvals remain visible; do not erase history on retry.

## Privacy-minimized telemetry

Record only routing/task metadata, outcome, duration, references loaded, token estimate and non-sensitive failure codes. Never store prompts, dataset values, secrets, candidate/employee content or other user material in telemetry.
