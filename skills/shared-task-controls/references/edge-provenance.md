# Edge provenance in knowledge graphs

Any graph built from documents mixes two kinds of edge, and the mixing is what ruins it. Some were
written down by a person who knew the relationship was real. Others came out of a rule — co-occurrence,
section ordering, shared vocabulary — and the rule was a guess.
Both look identical once they are arrows on a canvas. So the graph presents a guess with exactly
the confidence of a fact, at whatever scale the pipeline happens to run.

The fix is small. Every edge carries where it came from.

## Three labels

**Extracted.** A person asserted this relationship, or it was read verbatim from a file that
asserts it — a `parents` link in the concept registry, a standard named in a task contract. Such
an edge carries the authority of whoever wrote it. No more, and no less.

**Inferred.** A rule produced this edge. Record the rule beside it, so that a reader can judge the
derivation rather than trust it: a prerequisite between two notes, derived from the registry link
between the concepts those notes teach, is inferred — sound enough, but one step removed from
anything a human actually wrote.

**Ambiguous.** The relationship is asserted, but it means less than the arrow suggests. Workflow
stage precedence is the standing example: it says the earlier stage runs first, and says nothing
whatever about whether one task consumes the other's output. Tasks inside a stage are peers.
Drawing 832 of those as dependencies would be wrong 832 times.

## What the labels are for

Ambiguous edges are excluded from every structural claim — degree, clustering, anything about what
depends on what. They stay in the graph, because deleting them would throw away information that
somebody may want. They stay labelled for the harder reason: unlabelled, they lie.

The same discipline answers the pressure that produces fabricated graphs. When a source has no edge
to give, the output is fewer edges — never a weaker rule, quietly applied to fill the gap. An empty
region is a finding. A region filled in by heuristic is a fiction nobody will be able to detect
later, because by then it looks exactly like everything around it.

## Hubs destroy structure

A node nearly everything connects to tells you nothing about grouping. Worse: by joining every
cluster to every other cluster it collapses them into one, which is precisely how the standards
that all 865 tasks route to behave. Cluster over a graph that still contains them and the result
is one blob plus a handful of orphans.

Exclude ubiquitous nodes before clustering, the way stopwords are dropped before comparing
documents. Their ubiquity is itself worth reporting, separately, as a fact about what the whole
suite leans on.

## Reading a cluster

Clustering finds groups. It does not find meaning; whatever name a person attaches to a community
is a hypothesis, nothing more. So treat a cluster that crosses skill boundaries as a question — do
these two roles share more than the taxonomy admits, or do they merely share boilerplate? — and
answer it by reading the members. Never by trusting the partition.

Run `python3 tools/build_knowledge_graph.py --report` to regenerate the graph and print hubs,
communities and cross-domain edges. `--check` fails when the committed graph is stale.
