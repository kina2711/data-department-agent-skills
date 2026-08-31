# Dashboards as code

Drag a chart into place and it exists in one tool, in one workspace, in whatever state the last person left it. Nobody can review that as a diff. Nobody can rebuild it after someone deletes it, and moving it to staging means doing the whole thing again by hand. Writing the dashboard as a specification and creating it through the platform's API fixes all three — and adds one failure mode that did not exist before.

## Specification first, API second

What goes in version control is the specification: layout, and per chart its dataset, metric, dimensions, filters, chart type, and the question it answers. Review happens there, before anything is created. Diffs happen there too. Calling the API is the mechanical step afterwards, and it is the least interesting part.

One rule decides whether this helps or hurts: write the specification against the semantic layer, never against raw tables. Reach past the governed metric definitions and you have just written a second definition of revenue — and no viewer can tell which one they are looking at.

## What the API will not catch

Platform APIs accept anything that renders. Superset will build you a time series across a dimension with four hundred distinct values; it will build a pie chart of a continuous measure; it will apply a filter that quietly drops 80% of the rows. None of that returns an error. Generate dashboards ten times faster and you generate these ten times faster.

So the specification carries the checks a person would otherwise apply by looking at the thing: expected cardinality per dimension, the grain each chart aggregates to, and what the chart is for. That last field does most of the work. When a chart's stated question cannot be answered by its own configuration, a reviewer catches it while it is still three lines of YAML.

## Idempotency and ownership

Run the same specification twice and you should have one dashboard, updated. Key each chart on a stable identifier derived from the specification — never on its title, because titles get renamed and then you have two.

Ownership is the quieter problem. Every generated dashboard still needs a named human owner, recorded in the specification itself. Nobody feels responsible for something that appeared from an API call, and that is what a catalog is full of two years later: four hundred dashboards, no owners, nobody willing to delete any of them.

## Publication is still a gate

Generating is not publishing. When a dashboard reaches an audience it is a release, so the numbers get verified against a known-good query, the access model gets checked against who can now see the data, and someone named approves it. Construction got faster. Trust did not, and it stops exactly where someone else starts relying on the output.
