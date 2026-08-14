# Technical-series method

Build one governed content system, not disconnected posts.

## Series architecture

1. Define audience, decisions/problems, prior knowledge, promised outcomes, exclusions and success signals.
2. Map prerequisite concepts and design the arc: why → mental model → internal mechanics → guided example → hands-on use → production failure → trade-offs → integration/capstone.
3. Create one episode brief per central question. Each brief declares material claims, versions, sources, code, diagram, failure mode, limitations and platform adaptations.
4. Produce a canonical technical article as the source of truth. Social variants derive from its approved evidence pack, not from each other.
5. Schedule only evidence-ready episodes. Include research, technical review, editorial review, correction and recovery buffers.

For an Airflow or dbt series, avoid a feature-tour sequence. Teach the problem the tool solves, its execution/compilation model, state and dependency semantics, local runnable behavior, production operations, common failure patterns, boundaries versus alternatives, and a capstone that integrates earlier concepts.

## Episode gate

An episode may enter adaptation only when the central question is answered, version assumptions are explicit, material claims are traceable, code/tests have actual status, diagrams match the explanation, failure/trade-off analysis exists, sensitive information is removed and limitations are visible. Missing proof blocks factual publication; it does not invite invented examples.

Repository packaging keeps `research/`, canonical article, `examples/`, tests, diagrams, platform variants, reviews, status and changelog linked by stable series/episode/artifact IDs.
