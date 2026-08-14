# Structured interview architecture by role

Use multiple independent methods. No single conversation should decide the hire.

| Role family | Required evidence methods |
|---|---|
| DA/Product Analyst | SQL work sample, ambiguous analytics case, visualization critique, stakeholder behavioral interview |
| AE/BI | Data-modeling case, semantic/KPI scenario, SQL review, dashboard or model critique |
| DE/Platform | Coding, pipeline design, failure recovery, operations/security scenario |
| DS | Statistics/experiment case, modeling design, leakage/validation critique, business communication |
| MLE/MLOps | Software/ML system design, deployment/rollback scenario, monitoring incident and code review |
| Architect | Architecture case, ADR trade-offs, migration scenario and influence evidence |
| DG/Metadata/Security | Policy/ownership scenario, classification/access case, lineage/evidence review and conflict handling |
| Manager/Head | Strategy case, prioritization, people leadership, delivery recovery and executive communication |

Lock independent evidence before debrief. Score only assigned competencies using behavioral anchors. Do not use protected characteristics, pedigree proxies or unstructured cultural similarity as evidence.

## Validation and fairness controls

- Map each must-have competency to one primary method and at least one corroborating signal; remove stages that add burden without incremental evidence.
- Pilot prompts with anchor responses before live use. Each interviewer scores independently; a panel is calibrated only when every must-have score is within one point of the agreed anchor and disagreements are resolved against rubric evidence.
- Track rubric completion, missing evidence, interviewer severity, score variance, stage conversion, candidate withdrawal, accommodation delivery and candidate experience.
- Where lawful and sample sizes protect privacy, compare selection rates and score distributions across monitored groups. Flag a selection-rate ratio below 0.80 or a material unexplained gap for investigation; this is a screening signal, not proof of discrimination or fairness.
- Report numerator, denominator, confidence/uncertainty, missingness and cohort window. Do not publish subgroup results that risk re-identification.
- Establish content validity through role-outcome alignment and subject-matter review. Predictive validity and quality-of-hire claims require sufficient longitudinal evidence and cannot be inferred from one hiring cohort.

## Composed hiring workflow

For requests that bundle a complete process, compose in dependency order: role profile → scorecard → structured loop → job-relevant assessment → interviewer guide/training → panel calibration → independent evidence → debrief → recommendation/approval → fairness and validity monitoring. Each step remains its own atomic task and artifact.
