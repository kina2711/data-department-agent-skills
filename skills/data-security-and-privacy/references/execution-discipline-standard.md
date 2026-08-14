# Evidence-driven execution discipline

Load this reference only for change, debugging, completion-verification or workflow-control tasks. It strengthens the lifecycle standard without turning every advisory request into a heavyweight engineering ceremony.

## 1. Choose the work path

- **Probe**: read-only discovery, reproduction or a disposable experiment. It may answer one uncertainty but may not silently become the production solution.
- **Bounded change**: one independently testable outcome with explicit allowed paths, compatibility constraints and rollback.
- **Systemic change**: architecture, multiple components, migrations or material blast radius. Requires a decomposed plan, interface contracts and staged integration.

The path may upgrade when evidence reveals wider scope; never downgrade it merely to meet a deadline. Split work at the smallest independently testable and reviewable boundary, not at arbitrary file counts.

"Production-ready" means evidence says the artifact is eligible for a controlled release; it does not mean deployed, approved, or stable in production. Actual production mutation is a separate R3/R4 release task with explicit authority, live smoke/reconciliation and stabilization evidence.

## 2. Establish a verifiable target

Before execution, record the consumer/decision, observable outcome, pass/fail checks, evidence method, non-goals and stop conditions. Ask only about ambiguities that change semantics, risk, scope, cost or acceptance. Other unknowns become explicit bounded assumptions with an impact-if-wrong and validation step.

For change work, create a scope ledger:

- requested outcome -> planned task -> allowed artifact/path;
- forbidden or unrelated areas;
- expected generated files and approved deletions;
- compatibility, migration and cleanup boundaries.

Every changed artifact must trace to the request, a required test, or newly orphaned cleanup caused by the same change. Existing unrelated cleanup becomes a separate task.

## 3. Diagnose before changing

1. Reproduce or capture the current behavior with environment, version and exact inputs.
2. Trace evidence across component boundaries: what entered, what left and what changed at each boundary.
3. Compare a working case with the failing case and inspect recent relevant changes.
4. State one falsifiable hypothesis and its predicted observation.
5. Change one material variable, run the narrowest decisive test and update the hypothesis ledger.
6. Fix the earliest controllable cause, then add proportionate validation at input, transformation, output and monitoring layers.

Do not stack speculative fixes. After three failed material fix attempts, stop patching and request an architecture or problem-framing review; repeated failure is evidence that the model of the system is wrong.

## 4. Build and integrate in small verified increments

For executable behavior, capture a failing test or deterministic pre-change observation, implement the minimum sufficient change, make the narrow check pass, then refactor only within scope. For analysis, policy, curriculum or design artifacts, use the equivalent cycle: failing example/rubric finding -> minimal artifact change -> independent re-evaluation.

Do not create a framework, abstraction, configuration option or migration layer without a present requirement. Preserve local conventions and public interfaces unless the approved scope changes them.

## 5. Review in two passes

1. **Specification compliance**: compare the exact requested outcomes and acceptance checks with the delivered artifact. Identify missing, excess or untraceable work.
2. **Artifact quality**: inspect correctness, data semantics, failure handling, security/privacy, performance, maintainability and operational readiness as applicable.

Treat review comments as technical hypotheses. Verify them against the requirement, artifact and runtime evidence; resolve valid findings and document reasoned rejection of invalid ones. Re-run the affected review after each material fix.

## 6. Verify claims with fresh evidence

No completion claim is stronger than its evidence. Immediately before handoff:

- run or inspect the command/method that proves each material claim;
- record artifact version, environment, exact command or review method, exit status, observed result and timestamp;
- read the result, not only the exit code;
- keep failed mandatory checks and unsupported claims visible;
- distinguish `implemented`, `tested`, `approved`, `released` and `observed stable`.

Cached results, a prior agent's summary, code appearance and approval are not substitutes for fresh relevant verification. Approval authorizes; it does not prove correctness.

For Git-backed production release, approval must name the exact `final_diff_sha256` produced by the scope audit. Immediately before release, rerun the audit against the approved baseline and expected fingerprint. Any intervening file change invalidates the approval; stop, re-audit and obtain a new approval for the new fingerprint.

## 7. Persist only state needed to resume

For multi-step work, keep a compact work ledger with objective, path, current phase, verified baseline, active hypothesis, completed steps, failed attempts, open findings and next smallest action. Store large evidence by link or hash. This is the resume contract after handoff or context compaction, not a transcript of all reasoning.
