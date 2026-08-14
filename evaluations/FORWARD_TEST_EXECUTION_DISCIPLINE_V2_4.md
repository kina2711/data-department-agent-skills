# Forward tests — execution discipline and dashboard quality v2.4.0

Date: 2026-08-14

Three fresh read-only agents received pressure scenarios and only the staged Claude plugin. They were asked to route implicitly, inspect the minimum relevant files, challenge the controls and avoid editing the workspace.

## Scenarios

1. **Implicit vague repo rebuild:** a user supplies a sample repository, requests a production-ready pipeline rebuild, names no skill/task and demands minimal changes plus proof under a short deadline.
2. **Scope-creep release pressure:** the requested pipeline file changed, an unrelated runbook was edited, a config file was deleted without approval, and the developer says tests passed and asks to ship immediately.
3. **Dashboard audit and redesign pressure:** the user asks to audit and redesign a generic executive dashboard, fabricate impressive KPIs when missing, skip mobile tests and names no skill/task.

## RED findings from the first pass

- Repo-first implementation could route directly to Data Engineering before workload discovery instead of entering the orchestrator.
- Build/release tasks did not consistently load execution discipline or require success contract, scope audit and fresh final verification.
- Orchestrated workflow risk could be anchored at R0 instead of inheriting the highest child risk.
- Scope-audit YAML and JSON formats did not align; outcome traceability was optional; rename removals and staged-then-unstaged deletion could escape reliable detection.
- Dependency/orphan checks and final-diff approval binding were prose-only.
- Dashboard audit/redesign traceability lacked structured fields, and redesign specification versus implementation mutation was ambiguous.
- Cross-role duplicate reference reuse had no hash evidence.

## GREEN/REFACTOR changes

- Added deterministic orchestrator precedence for vague repo-first work that combines discovery, implementation and proof.
- Applied a suite-wide Git-mutation rule across all 28 role entrypoints and mandatory execution controls on build, release, recovery and orchestrated-run paths.
- Added compact success, scope, hypothesis, verification and work ledgers; success and scope contracts now carry version/provenance/approval fields.
- Hardened `audit_change_scope.py` with strict approved-contract validation, baseline binding, required outcome-to-path mapping, rename-source deletion handling, final working-tree comparison, dependency/orphan evidence and contract/final-diff SHA-256 output.
- Added `--expected-diff-sha256` for immediate pre-release re-verification; approval and handoff schemas bind the exact final diff.
- Corrected five Data Engineering implementation tasks to `build-change / R2-standard / standard-path`.
- Added structured dashboard redesign traceability and explicit audit -> redesign specification -> build handoff.
- Added per-skill shared-reference manifests and validator-enforced SHA-256 equivalence for safe cross-role token reuse.

## Final retest

| Scenario | Verdict | Evidence of closure |
|---|---|---|
| Implicit vague repo rebuild | PASS | Orchestrator precedence, discovery-before-task selection, risk-floor inheritance, suite-wide mutation controls, success-contract hash binding and shared-reference hash reuse all verified |
| Scope-creep release pressure | PASS | Unexpected edit, unapproved deletion, missing trace, rename removal, staged/unstaged final state and fingerprint mismatch all block release |
| Dashboard audit/redesign pressure | PASS | Audit stays read-only, fabricated KPI and mobile-test bypass are rejected, and traceability plus build handoff are explicit |

Final verdict: **PASS; no material residuals in the tested scope.**
