# Dashboard experience quality standard

Use this reference for BI dashboard build, audit, redesign, usability testing and independent UAT. It applies design discipline to analytical decision products; it does not replace metric governance, semantic-model tests or platform-specific validation.

## Mode and boundary

- **Audit** is read-only: report observed evidence, location, severity, decision impact and a concrete fix. Do not edit or quietly redesign.
- **Redesign** starts from a completed audit or explicit redesign brief and returns a traceable specification before implementation.
- **Build** implements an approved specification while preserving the repository's framework, component boundaries and design system.

Never invent a KPI value, target, comparison, benchmark, customer quote or business outcome to fill a layout. Use a visibly labelled pending placeholder, request the missing fact, or remove the unsupported visual slot.

## Preflight

Inspect the dashboard requirement, audience and decisions; certified metric definitions; source authority; current pages and interactions; design tokens/theme; component/chart libraries; responsive conventions; accessibility requirements; platform constraints; and prior audit or usage evidence. Separate observed facts, stakeholder statements, inference and recommendation.

For redesign, list the expected file/page scope and planned removals. Preserve filters, drill paths, bookmarks, RLS behavior, export behavior and metric semantics unless the approved change explicitly replaces them.

## Six-axis pre-emit critique

Score 1-5 and revise any axis below 3 before handoff:

1. **Decision fit**: each page and visual supports a named user decision or monitoring action.
2. **Hierarchy**: primary signal, context, diagnosis and detail are distinguishable within seconds.
3. **Specificity**: structure and vocabulary fit this domain rather than a generic executive template.
4. **Restraint**: every visual, color, label and interaction earns its place.
5. **Truth**: claims, numbers, units, time windows and status language trace to governed evidence.
6. **Accessibility**: keyboard, focus, contrast, text alternatives, non-color cues and responsive use are designed, not deferred.

## Quality gates

### Truth and analytical integrity

- Metric name, formula, grain, owner, unit, timezone, period, filters and freshness are visible or discoverable.
- Totals reconcile with an authoritative source; cross-filtering does not silently change denominator semantics.
- Missing, delayed, suppressed and zero values remain distinguishable.
- Forecasts, uncertainty and thresholds disclose method and limitations.
- Every narrative claim maps to a query, model, approved metric or clearly labelled hypothesis.

### Information architecture and visual encoding

- Avoid the generic sequence of logo/header -> equal KPI-card row -> repeated equal chart cards -> decorative footer when it does not match the decision flow.
- Avoid card-inside-card nesting, redundant borders, rainbow category palettes, donut/gauge walls, decorative gradients and repeated visual types with no comparative purpose.
- Choose visual form from the analytical question: comparison, trend, distribution, relationship, composition, flow, geography or detailed lookup.
- Use semantic tokens consistently; do not improvise one-off colors or fonts mid-build. Keep numbers aligned and units/scales comparable.
- Prefer progressive disclosure: overview -> explanation -> detail. Dense is acceptable when intentional, aligned and scannable.

### Interaction, state and responsive behavior

- Define default, hover, focus-visible, active/selected, loading, empty, partial-data, error, disabled and stale states where applicable.
- Every hover behavior has keyboard and touch access. Filters expose current scope, reset behavior, dependencies and no-result state.
- Test at representative desktop, tablet and narrow widths; critical metric labels, controls and values must not truncate ambiguously or require horizontal page scrolling.
- Preserve a logical focus order, visible focus, adequate contrast, text alternatives, non-color status cues and reduced-motion behavior.

### Operational fit

- Show owner, refresh/freshness, certification status, data caveats and support route in proportion to risk.
- Validate RLS/OLS with representative roles, performance with realistic data volume, exports/subscriptions, refresh failure and monitoring.
- Reconcile redesigned output against the previous approved baseline and document intentional changes.

## Audit output and redesign handoff

Group findings by actual severity: critical means wrong decision, data/security exposure or unusable access; major means material friction or misleading hierarchy; minor means polish. For each finding cite the exact page/visual/file and observed evidence. End with counts, decision readiness, top remediation order and anything not tested.

A redesign specification maps audit finding -> design decision -> affected page/component -> preserved behavior -> acceptance test. Implementation begins only after scope and semantic decisions are clear; visual approval never waives metric, RLS, performance or accessibility testing.
