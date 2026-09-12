# Reading less of what a tool returns

Context spends in two directions and only one of them gets attention. Writing shorter answers is
the familiar half. Less familiar, and usually larger, is what comes back from a command: a
test run prints 4,000 lines, `git diff` on a generated suite prints 40,000, and every one of them
is read at full price before the useful three are found.

## Ask for less before trimming more

Cheapest is to reduce at the tool rather than after it. `git diff --stat` before `git diff`.
`npm test 2>&1 | grep -E "^ℹ (pass|fail)"` when the question is whether it passed. `head -3` on a
validator that prints a summary line last is worse than `tail -1`, and knowing which end holds the
answer is most of the skill.

None of that is truncation. Truncation cuts an unknown amount off a known output; asking a
narrower question returns a smaller output that is complete for that question. Truncation hides what it dropped. Narrowing has nothing to hide.

## Shape first, then drill

Anything large goes in one order: how many, then which, then what. Counts come before names, names before stack traces. A failing pipeline gives the failing stage before the log of that stage
before the line that threw. Reading the log first and looking for the shape inside it is the
expensive way round, and it is the default.

Files follow it too. `grep -n` to find where, then read thirty lines around it. Whole
files get read when the task is to change the whole file.

## Say what was cut

Filtered output gets reported as filtered. "Tests passed" after reading only the summary
line is a claim about the summary line; if a warning was printed above it and never read, the
report says the warnings were not read. One clause buys the difference between a compressed read and an incomplete one presented as
complete.

One failure mode makes this concrete. A command exits 0, the tail is green, and the middle
contains a skip. From the last line alone, a run that skipped its most expensive check is indistinguishable from one
that passed it.

## Where this stops

Never compress the thing being judged. Whatever is under review — a diff, an artifact being verified, evidence being read — is the work,
and skimming it to save context is skipping the task. The
budget applies to the noise a tool wraps its answer in, never to the answer.

And never filter an error stream. Read at 20%, a stack trace has been read at 0%, and the line that got cut is disproportionately
the one that mattered.
