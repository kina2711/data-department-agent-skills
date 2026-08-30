# Dashboards as code

A dashboard assembled by dragging is a dashboard that exists only in the tool. It cannot be reviewed as a diff, reproduced in another environment, or rebuilt after someone deletes it. Defining it as a specification and creating it through the platform's API changes all three, and introduces one failure mode of its own.

## Specification first, API second

The specification is the artifact: layout, each chart's dataset, metric, dimensions, filters, chart type, and the question the chart answers. It is reviewable before anything is created, diffable when it changes, and the thing kept in version control. The API call is the mechanical step that realises it.

Write the specification against the semantic layer, not against raw tables. A dashboard-as-code that reaches past the governed metric definitions reproduces them, and then two definitions of the same number exist with no indication which the viewer is looking at.

## What the API does not check

Platform APIs accept a chart that renders and says nothing. They will happily create a time series over a dimension with four hundred values, a pie chart of a continuous measure, or a filter that silently excludes most of the data. Generating dashboards faster generates these faster.

The specification therefore carries the checks a person would otherwise apply by looking: expected cardinality per dimension, the grain each chart aggregates to, and what the chart is for. A chart whose stated question cannot be answered by its own configuration is a defect the reviewer can catch in the specification, before it is built.

## Idempotency and ownership

Creating the same specification twice must update the dashboard, not produce a second one. Key each chart and the dashboard on a stable identifier derived from the specification rather than on its title, which people rename.

A generated dashboard still has a human owner, and the specification names them. Nobody owns a dashboard that appeared from an API call, and unowned dashboards are what a catalog is full of two years later.

## Publication is still a gate

Generating is not publishing. A dashboard reaching an audience is a release: it needs the numbers verified against a known-good query, the access model checked against who can now see the data, and named approval. The speed gain is in construction and it stops at the point where someone else starts trusting the output.
