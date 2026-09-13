# Reviewing what a model produced, before anyone relies on it

Every artifact in this suite can now be written by a model, and a model writes what is likely
rather than what is true. That is not a reason to distrust the output; it is a reason to know what
the failure looks like in each medium, because it looks different in prose, in code, and in a
picture — and in all three it looks like competence.

This gate runs before an artifact is shipped, published, merged or filed as evidence. It is not a
quality review; it asks one question. **Is anything here true only because it was likely?**

## Prose

[The humanizer skill](https://github.com/blader/humanizer) is the pattern catalogue and this
standard does not duplicate it: staged contrasts, one-line closers, forced triads, dashes as the
universal joint, inflated significance, bold as decoration. Install it and use it. Absent it,
`authored-prose-voice.md` in this suite covers the same ground more briefly, and the review says
which one it used.

What a rewrite must not do is the part a style pass gets wrong. Rewriting for voice may not add or
remove a fact, number, name, date, quotation or citation. A claim lost while tightening a sentence
is an error, not concision, and it is the likeliest damage a humanizing pass causes — the sentence
reads better precisely because the qualifier that made it true is gone.

Two prose tells this suite cares about more than a general reader would. A hedge that hedges
nothing — *may sometimes potentially* — reads as caution and carries none. And a citation that
points at a real document which does not say the thing: it survives the one check most readers
perform, which is that the link resolves.

## Code

Humanizer explicitly leaves code alone, and code needs its own list. The generated-code tells,
strongest first:

- **An API that does not exist.** A method, flag or parameter with exactly the right name for what
  was wanted. This is the most common and the most confidently written. Check it against the
  installed version, not against recall.
- **No evidence it ran.** The strongest tell is negative: consistent style, plausible names, and
  nothing anywhere showing the code was executed. Run it, or say it was not run.
- **Handling for impossible states, none for likely ones.** A null check on a value that cannot be
  null, and no handling of the timeout that happens weekly.
- **An abstraction with one caller.** A base class, an interface, a strategy — introduced for a
  second case nobody asked for.
- **Tests that assert the implementation.** They mirror the code's structure and pass whatever the
  code does; they fail only when the code changes, never when it is wrong. A test that does not
  fail without the change under test is not covering it.
- **Comments restating the line.** `# increment the counter` above `counter += 1`. Comments should
  hold what the code cannot: why, and what was rejected.
- **Symmetric treatment of asymmetric cases.** Three branches written in parallel when one of them
  is genuinely different, because parallel prose is what the model reaches for.
- **Configuration nobody sets.** Options, thresholds and feature flags with defaults that are the
  only value ever used.

For SQL specifically, the failure is grain rather than syntax: a query that runs, returns a tidy
table, and multiplies rows through a join. Correctness here is a row count, not a review opinion.

## Images and video

Generated media is where the strongest claim gets made with the least evidence, because a picture
is read as a record.

- **A screenshot must be captured, never generated.** A screenshot asserts that something ran and
  looked like this. Producing one from a description manufactures that evidence. Where a real
  capture is not available, leave the slot empty and say so; an empty slot is honest and a
  fabricated one is not.
- **Numbers in a chart come from a query, and the query is named.** A plausible bar chart is the
  easiest false claim to make and the hardest for a reader to challenge.
- **Diagram labels name real things.** A box called `orders_enriched` asserts that table exists.
  Check the names against the schema, and mark anything illustrative as illustrative.
- **Rendered text is still a claim.** Text inside an image escapes every prose check that runs over
  the document around it, which is exactly why an unsupported claim tends to end up there.
- **Say what made the file.** Rendered from a spec, captured from a screen, drawn by hand, or
  produced by a generative model — each carries different weight, and a reader cannot tell them
  apart by looking.

## What the gate returns

A verdict per artifact, and for anything that fails, what specifically is unsupported. Passing is
not a claim that the artifact is good; it is a claim that nothing in it is true only because it was
likely.

Never soften a fail. An artifact that ships with a known unsupported claim ships with it whether or
not the review said so politely, and the review exists to make that visible while it is still cheap
to fix.
