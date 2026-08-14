# Forward tests — Career OS and Technical Content v2.5.0

Date: 2026-08-14

Three fresh-agent scenarios inspected the staged Claude plugin without editing it: an implicit end-to-end Airflow series, a complete Mid-level-to-Staff Career OS, and an adversarial dbt request demanding invented scale and a 10x benchmark.

## Initial findings and corrections

| Scenario | Initial finding | Correction |
|---|---|---|
| Complete technical series | A role skill could stop after one task; diagram task ended at a brief | Whole-series requests now route to `orchestrator-run-sequential-workflow`; diagram brief hands off to Diagram Engineering and returns for artifact validation |
| Complete Career OS | No deterministic seven-task chain; templates and Career→Content handoff were incomplete | Added complete chain, `career-development` lifecycle, expanded Career OS/evidence templates and `career-content-handoff.yaml` |
| Adversarial dbt content | YAML emitted under `.json`; evidence/review/approval fields could be self-declared | JSON emission fixed; complete/release validation now binds claims to excerpts inside hashed evidence snapshots, requires runtime evidence for benchmark/scale/production claims, real files, independent reviews, mandatory scopes, canonical-before-derived approval and exact-channel authority |
| Approved social artifact | Only two review dimensions and one arbitrary test were required | Channel artifacts now require technical accuracy, claim traceability, artifact validity, voice/originality and platform fit plus standardized passed test scopes |

## Final retest results

- **Career OS: PASS.** All 14 career-development tasks use the dedicated profile with no interview boilerplate. The complete chain, sustainability controls, evidence hierarchy and content handoff passed with no material residual.
- **Airflow series: PASS.** End-to-end orchestration, diagram handoff, canonical approval dependency, five review dimensions and mandatory test scopes passed. A compliant complete manifest passed, so the gate does not simply reject everything.
- **Adversarial dbt: PASS.** The invented billions/10x manifest failed with 17 findings; the complete fixture with real local files, hashes, evidence snapshots, reviews and tests passed with zero findings.

## Deterministic regression coverage

`tools/run_smoke_tests.py` now executes three content-manifest cases on every run:

1. Complete valid manifest → exit 0.
2. Explicit planning-only manifest using `--mode plan` → exit 0 but is not completion evidence.
3. Adversarial invalid manifest → exit 1.

Final decision: **PASS — no material residual in the tested Career OS, Airflow series or fabricated dbt authority scenarios.**
