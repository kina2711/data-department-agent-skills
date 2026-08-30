# Marts an agent can consume

A mart designed for a human analyst and a mart designed for an agent differ in one respect that decides everything else: the analyst knows what the columns mean and the agent does not. The analyst joins four tables without noticing; the agent writes a join it half-understands and produces a number nobody can trace.

## Shape follows the consumer

Neither shape is correct in general. Choose by who reads it and what they ask:

| Consumer and question | Shape | Why |
|---|---|---|
| An agent answering open questions about one entity | One big table | Every attribute reachable without a join, so a wrong join is not a failure mode that exists |
| Slice-and-dice across shared dimensions, many facts | Star schema | Conformed dimensions are what make two facts comparable; flattening destroys that |
| A fixed dashboard with known questions | Purpose-built aggregate | Neither general shape earns its cost when the questions do not change |

One big table trades storage and update cost for join safety. That trade is worth making where a wrong join produces a plausible wrong number, and not worth making where the attributes change independently and the table becomes a rewrite on every change.

## Compute the derived measure once, in the mart

A rate, a ratio, a flag or a score that an agent would otherwise compute in generated SQL belongs in the mart with a name and a definition. Bounce rate computed by three different agents produces three different numbers, all defensible, none reconcilable.

This is the difference between a mart and a view over raw tables: the mart carries the judgment. Where the definition is contested, the mart holds the agreed one and names it precisely enough that the disagreement is visible — `is_bounce_single_pageview_session`, not `is_bounce`.

## Publish the description with the data

A mart an agent can consume has its schema published where retrieval can reach it: column names, types, grain, the meaning of each derived measure, the partition and cluster keys, and the values a categorical column actually takes. A column called `status` with six undocumented values is a mart the agent will guess about.

State the grain in one sentence at the top of the model and make it true. Most agent-generated aggregation errors are grain errors, and a stated grain converts them from silent to checkable.

## Physical layout is part of the contract

Partition and cluster keys are not tuning applied afterwards. An agent writes the query it was grounded on, so a mart whose partition key is absent from its published description will be queried without it, and the first sign will be the bill. Publish them, and make the common query path the cheap one.

## What this does not solve

An AI-ready mart makes an agent's query more likely to be answerable and cheaper to run. It does not make the answer right, and a pre-computed measure is only as good as the definition it froze — a mart is the most durable place to embed a wrong definition, because everything downstream then agrees with it. Version the definitions, and treat changing one as a breaking change to every consumer rather than a model edit.
