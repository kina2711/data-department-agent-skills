# Diagram fidelity

`validate_diagram_source.py` says in its own docstring that it cannot confirm a diagram is true. Nothing else in the suite did either. A structurally perfect diagram that is quietly wrong is more dangerous than no diagram, because a reader acts on it: boxes drawn from memory get treated as an inventory, and an arrow someone assumed becomes a dependency in someone else's plan.

## Declare the class, visibly

Every diagram is exactly one of:

- **observed** — every element was read out of an artifact that exists now.
- **proposed** — a design for something that does not exist yet.
- **illustrative** — a teaching example that depicts no particular system.

The class appears on the rendered diagram, not only in its metadata. A reader who sees the image in a slide, a wiki page or a screenshot has no access to the file's front matter, and that is where diagrams do most of their travelling.

Mixing classes silently is the common failure: four services that exist and one that is planned, drawn as five identical boxes. Either render the proposed elements distinctly and say so in the legend, or split them into two diagrams.

## What counts as inspection

Reading the artifact itself: source files, configuration, DDL, catalog or lineage output, an API response, a query plan, a scheduler definition. Each observed element records where it was read — a path with a line or anchor, a table name, a DAG id, a topic name, a config key.

Not inspection: another diagram, a README's description of the system, a ticket, a design document, or recall. A diagram derived from a diagram inherits every error in the original and none of its freshness. Where a prior diagram is the only source available, the new one is `proposed` until an artifact is actually read, however confident the original looked.

## Bind to a version

An observed diagram names the commit, tag, release or extraction timestamp it was read at. Without that, "is this still true" has no answer, and the diagram does not announce the moment it stops being accurate — it just keeps rendering. Treat an observed diagram whose version anchor is gone as `proposed` until re-derived.

## Absence is a claim

Leaving a component out for clarity states that it does not matter to the question the diagram answers. That is often correct, but it is a decision rather than a default: record what was excluded and why. The difference between a simplification and a misrepresentation is whether the omission was declared.

## The check

Record elements in `diagram-provenance.yaml` and run `../../scripts/validate_diagram_source.py --provenance` alongside the structural check. It reports nodes with no provenance entry, entries pointing at nodes the source does not contain, observed diagrams with no version anchor, and observed entries whose source type is another diagram.

It confirms that each element claims a source. It cannot open that source and confirm the claim is honest. Only the person who inspected the artifact can do that, and the point of recording it is that this person is identifiable later.
