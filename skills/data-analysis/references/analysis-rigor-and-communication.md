# Analysis rigor and communication standard

Apply this reference to analysis planning, EDA, query explanation, review, delivery and learning. Automated scripts provide first-pass evidence only; they do not prove business semantics or statistical validity.

## Programmatic EDA

Confirm row grain and scope before interpreting distributions. Inspect schema/types, missingness by field and segment, exact and key duplicates, cardinality, numeric ranges, quantiles/outliers, categorical concentration and date coverage. For large data, document pushdown or sampling strategy, sample frame, seed and what could be missed. Skip or mask sensitive columns unless authorized.

## SQL to business logic

Trace CTEs and sources, join type/cardinality, filters, time logic, grouping grain, aggregations, window functions and output columns. Flag fan-out, implicit null handling, hard-coded periods, currency/time-zone ambiguity and dialect-specific behavior. A structural parser is heuristic; confirm against schema, business definitions and an EXPLAIN/dry run when available.

## Assumptions and impact

Record data, business-rule and statistical assumptions with source, confidence, impact-if-wrong and validation plan. Quantify action impact as low/base/high rather than one number; include baseline, affected population, change mechanism, time horizon, sensitivity and double-counting checks.

## Methodology explanation

Calibrate depth by audience: executive = decision, why the method is credible and limitation; business = data, logic and interpretation; technical = full design, assumptions, diagnostics and reproducibility. Preserve decision-critical caveats when simplifying.

## Peer review and pre-delivery QA

Check question-method alignment, source authority, grain and joins, alternate calculations, statistical assumptions, reproducibility, narrative-to-evidence traceability and actionability. Categorize findings as must-fix, should-fix or optional. The author records a disposition; a reviewer closes must-fix items before decision use.

## Retrospective

Compare plan with actual scope, cycle time, rework and acceptance outcome. Find causes rather than symptoms. Convert durable learning into a specific template, reference, check, test or team rule with owner, due date and effectiveness measure.
