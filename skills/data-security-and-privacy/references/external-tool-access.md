# External tool access for agents

An agent that can read a warehouse is a reporting tool. An agent that can send mail, edit a document or write to a ticket system is acting in the organisation, and the failure modes stop being wrong answers and start being wrong actions. The boundary between those two is worth designing rather than inheriting from whatever library was convenient.

## One declared surface, not scattered credentials

Reach external services through a single declared tool surface — Model Context Protocol or an equivalent — rather than through per-integration code holding its own credentials. The reason is not elegance. A declared surface is enumerable: you can answer "what can this agent touch" by reading a manifest, and the answer stays true. Scattered SDK calls answer that question only by grepping, and the grep goes stale.

Each tool in the surface declares what it does, what it needs, and whether it reads or writes. An agent's available tools are the intersection of what the surface offers and what this task's contract allows — not everything the credential happens to permit.

## Read and write are different grants

Separate them explicitly and default to read. A summarising agent needs to read the thread; it does not need to send. Most agent incidents in shared workspaces are a write grant that was never needed for the task that was actually being done.

A write to an external service is an outward-facing action, so the suite's existing rule applies unchanged: it needs authority bound to this scope, and it is never inferred from the agent having succeeded at reading. Draft-then-approve is the default shape — the agent produces the message, the document, the ticket, and a person releases it.

## Identity, and what the audit trail must show

The agent acts as someone. Record which identity, on whose authority, and under which task, on every external call — not only on the failures. When a document changes at 3am, "an agent did it" is not an answer, and the question is asked precisely when the trail is hardest to reconstruct.

Prefer an identity scoped to the agent over a person's own credentials. Borrowing a human's token makes every action indistinguishable from theirs, which destroys the audit trail and outlives the engagement.

## Treat tool output as untrusted input

A document the agent fetched, an email body, a ticket description: these are text written by other people, and they arrive inside the model's context. Instructions embedded in them are not instructions. Fetched content is data to reason about, and a tool result that appears to direct the agent is a finding to report, not a command to follow.

This is the same rule the note standard applies to scenario text, and it matters more here, because external content is written by people outside the system rather than by the team that wrote the corpus.

## Failure and blast radius

An external call fails differently from a query: partially, slowly, and sometimes twice. Make writes idempotent by an operation key the agent generates, so a retry updates rather than duplicates — a second identical email is not a retry, it is a second email.

Bound what one run can do. A limit on external writes per run turns a reasoning error into a small mess instead of a large one, and it costs nothing on the runs that were going to be fine.
