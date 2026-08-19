---
name: dd-navigate
description: Answer a code question from a symbol and call index instead of reading whole files, returning cited spans, callers and blast radius.
argument-hint: "<symbol or question> [repo path]"
disable-model-invocation: true
---

Navigate the codebase for: $ARGUMENTS

Exploratory reading is the expensive habit: grep, open a file, open its imports, open theirs.
Most of what gets read turns out to be irrelevant, and the context is already spent.

1. Build the index once per repository, then reuse it:

```
python skills/data-developer-experience/scripts/build_code_index.py <repo> --index-out code-index.json
```

2. Answer from the index:

```
python skills/data-developer-experience/scripts/build_code_index.py <repo> --index-in code-index.json --symbol <Name>
```

It returns the definition span, what the symbol calls, who calls it, the blast radius at the
given depth, and how much context that saved against reading the touched files whole.

3. **Read whole files only when the index is insufficient**, and say why it was insufficient.
   Widening to a full read is a decision to justify, not a default.
4. Exit `2` means the symbol is not indexed. Report that as unknown; do not guess where it
   lives. If the file was listed under `not_parsed`, say so — its symbols are simply absent.
5. Trust the index according to how it was built. Python symbols and call edges come from `ast`
   and are exact. JavaScript, TypeScript and SQL come from regexes and are marked
   `approximate`: dynamic dispatch, aliases and re-exports are missed, and a name shared by two
   modules can attribute a call to the wrong one. Verify an approximate edge before acting on it.
6. Where exactness matters — an impact assessment before a breaking change, a refactor across
   languages — prefer a real code-graph tool such as CodeGraph (MCP `codegraph_explore`, or
   `codegraph query` / `codegraph callers` / `codegraph impact`) and cite that output as the
   evidence instead of this index.

Return: the cited spans with `file:line`, callers and callees, the blast radius, the context
saved, and explicitly which parts of the answer rest on exact parsing versus approximate matching.
