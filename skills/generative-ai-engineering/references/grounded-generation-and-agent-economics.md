# Grounded generation and agent economics

An agent that writes SQL from the table names it remembers will produce syntactically perfect queries against columns that do not exist. An agent that skips the model when a question looks familiar will answer a new question with an old answer. Both failures are cheap to prevent and expensive to notice, because both produce output that looks exactly like success.

## Retrieve the schema before writing the query

A generation step that touches a warehouse retrieves the schema for the tables it intends to use, from a metadata index, immediately before generating. Not from the system prompt, which goes stale the moment a column is renamed; not from the conversation, which may be describing a different environment; and not from recall.

What the retrieval must return is the grain, the column names and types, the partition and cluster keys, and whatever the warehouse enforces about them. A query written without the partition key on a partitioned table is not slow — it is a full scan the finance team notices before the analyst does.

Record which schema version grounded which query. When a query later turns out to be wrong, the first question is whether the schema it was written against still describes the table, and that question needs an answer rather than an investigation.

## Semantic cache, and the question it cannot answer

Caching answers by vector distance to previous questions is the largest single cost reduction available to a reporting agent, because the expensive part is the reasoning and most reporting questions repeat. It is also the one optimisation that fails silently.

Two things must hold before a hit is served:

- **The question is the same question.** Vector distance measures phrasing, and two questions can be phrased almost identically while differing in the one clause that matters — last month versus this month, gross versus net, including refunds or not. Set the threshold from labelled pairs you have checked, and treat every near-threshold hit as a miss.
- **The data has not moved underneath it.** A cached report is valid only for a warehouse state. Key the cache on the underlying table versions, partitions or a freshness watermark as well as on the question, and invalidate on load rather than on a timer that has no relationship to when the data changed.

Serve a cached answer labelled as cached, with the timestamp it was produced. A user who can see that a number is four hours old will ask for a refresh when it matters; a user shown a stale number as if it were live will not.

Measure the hit rate and the false-hit rate separately. A rising hit rate with no false-hit measurement is not a saving that has been demonstrated — it is one that has been assumed.

## Interrupt points are part of the design

A long agent graph that runs to completion and then asks for approval has already spent the tokens and already made the decisions. Name the points where it stops instead: after the plan, before anything is written, before anything is published. Each interrupt states what was decided, what happens next, and what the human is being asked to change.

An interrupt is not a confirmation dialog. It exists so the plan can be edited and the graph resumed from that point, which means the state at each interrupt is serialisable and the resume path is tested. An interrupt that can only be approved is a delay with extra steps.

## What observability has to answer

Per-agent tracing on a multi-agent graph exists to answer three questions, and a trace that cannot answer them is decoration:

- Which step spent the time, and which spent the tokens. These are rarely the same step, and the intuition about which is which is usually wrong.
- What context was actually sent. Prompt bloat accumulates invisibly; the only way to find a supervisor forwarding the entire history to every child is to look at what left the process.
- Whether a change helped. Compare prompt versions against the same recorded inputs, and report the difference with its uncertainty rather than the better single run.

Attribute cost per session and per agent, not per call. A cheap agent invoked forty times is the expensive one, and per-call figures hide that completely.

## What none of this makes true

Grounded retrieval reduces invented columns; it does not make the query correct. A cache hit is not a verified answer. A trace shows what happened, not whether it should have. Every claim an agent makes about a business number still needs the evidence and approval the lifecycle standard requires — the agent economics here change what it costs to produce an answer, never what it takes to trust one.
