---
name: dd-instinct
description: Record, score and govern instincts — reusable patterns whose confidence is derived from counted outcomes rather than asserted after a single run.
argument-hint: "[propose | observe <id> success|failure | review] [scope]"
disable-model-invocation: true
---

Instinct operation: $ARGUMENTS

An agent that declares a lesson learned after one lucky run has learned nothing. An instinct
earns its status from counted outcomes, and loses it the same way.

## Propose

Append to the ledger (`skills/data-department-orchestrator/assets/instinct-ledger.json`) with
`status: "proposed"`, `observations` all zero, and `user_content: null`.

Write it as a trigger and an action: *when* this situation holds, *then* do this, *because* of
this failure mode. A pattern you cannot state without quoting the user's data or prompt is not
an instinct — do not record it. Never store transcripts, secrets or data values; the validator
rejects text that looks like a credential.

## Observe

```
python skills/data-department-orchestrator/scripts/manage_instincts.py <ledger> --observe <id> --outcome success|failure --evidence <evidence-id> --write
```

Record the outcome of an actual application, with the evidence that shows it. An observation
without evidence is an opinion.

## Review

```
python skills/data-department-orchestrator/scripts/manage_instincts.py <ledger> --rescore --scope <skill>
```

Confidence is the Wilson lower bound of the success rate, so a small sample scores low by
construction. Status follows from the numbers, not from preference:

- `proposed` — under 5 applications or under 0.70 confidence. A hypothesis. It may inform a
  question; it may not shape a decision.
- `active` — at least 5 applications, confidence at or above 0.70, evidence attached.
- `weakening` — unconfirmed for more than 90 days. Re-test before relying on it; a pattern that
  held in a previous stack version may not hold now.
- `retired` — confidence at or below 0.35 with enough applications to be sure. Leave it in the
  ledger; a recorded dead end stops the same idea being retried.

**Only `active` instincts may shape behavior.** When you apply one, say which, and record the
outcome afterwards — including when it failed. An instinct that only ever gets confirmed is
not being tested.

Return: the instincts relevant to the current scope with status and confidence, which one you
are applying and why, and which weakening ones need a re-test before they can be trusted again.
