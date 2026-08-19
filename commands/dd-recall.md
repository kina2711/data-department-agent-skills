---
name: dd-recall
description: Recall prior work from indexed traces with zero model calls, returning pointers into the original spans rather than a generated summary.
argument-hint: "[vault path] <what to recall>"
disable-model-invocation: true
---

Recall from indexed memory: $ARGUMENTS

Memory that is summarized by a model costs tokens on every write and destroys the evidence —
once a detail is merged away, nothing downstream recovers it. This retrieves spans of the
original trace instead.

1. Build or reuse the index:

```
python skills/personal-second-brain-and-knowledge-os/scripts/build_entity_context_graph.py <vault> --index-out memory-index.json
```

2. Retrieve, following the entity graph one hop when the query is broad:

```
python skills/personal-second-brain-and-knowledge-os/scripts/build_entity_context_graph.py <vault> --index-in memory-index.json --query "<question>" --expand
```

3. **Read the cited spans before asserting anything.** The retrieval output is a set of
   pointers with previews, not an answer. Quoting a preview as if it were the full record is
   the failure this control exists to prevent.
4. Exit `2` means nothing in the indexed traces matches. Report that as unknown. Do not fill
   the gap from conversation history or from a plausible assumption.
5. Attribute every recalled fact to `source:line`. A fact you cannot point at is not recalled,
   it is invented.

Scope, state it when reporting: indexing, linking and ranking make **zero model calls**;
reading the retrieved spans still consumes context tokens. This is a lexical implementation
with no encoder, so recall is weaker than an embedding-based system on paraphrased queries —
if a query returns nothing, try the concrete identifiers and entity names used in the notes.

For learning and skill-transition work this is a retrieval aid only. Mastery state stays owned
by the career skill and still requires verified evidence; a trace mentioning a topic is
exposure, never mastery.

Return: the ranked spans with `source:line`, what each one actually says, what remains
unanswered by the indexed traces, and the next place to look.
