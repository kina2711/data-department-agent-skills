# Agent harness

A harness is everything one agent needs to do one role's work, packaged so it behaves the same way twice and can be handed to somebody else. It is not a bundle of skills. It is a boundary, and most of its value is in what it excludes.

The suite already has the parts — task contracts, a context package, a tool surface, evaluation cases, run state. A harness is the declaration that says which of them apply, and that declaration is the artifact.

## What a harness declares

- **Scope.** The tasks this agent may select, and the ones deliberately left out. "Everything the skill offers" is not a scope; it is the absence of one.
- **Grounding.** The schema index, company context, corpus or registry the agent retrieves from, each pinned to a version. An agent grounded on whatever happened to be current is not reproducible.
- **Tool surface.** What it may reach outside the warehouse, read and write separately, per the external tool access standard.
- **Guardrails.** Permission mode, write ceiling per run, the gates that require named authority, and the risk tier above which it stops and asks.
- **Evaluation.** The cases that decide whether this harness works, and the score it reached on them. Without these, "it works" is an opinion held by whoever built it.
- **Environment.** What must exist for it to run at all: credentials by name not value, services, versions.

## Reproducible, or it cannot be debugged

Two runs of the same harness on the same input should differ only where the model is non-deterministic — never because a prompt, a corpus or a schema moved underneath it. Pin every input that is not the user's request, and record the pinned versions with the run.

When an agent produces something wrong, the first question is what it was working from. A harness that cannot answer that turns every investigation into an archaeology exercise, and the answer is usually that something changed and nobody knows what.

## Version it, because a changed harness is a different agent

Swapping the model, editing the system prompt, adding a tool or widening the scope produces an agent with different behaviour and a stale evaluation. Version the harness, re-run its cases, and record both. An evaluation score attached to a version nobody can reconstruct is decoration.

## Handing one over transfers risk as well as capability

A harness given to another team runs under their credentials, in their environment, against their data. The guardrails travel with it or the harness is not what they received. State plainly what it may write, what it may spend, and what it stops for; a recipient who has to infer the blast radius from reading prompts will infer it wrong.

Name an accountable owner. An unowned harness in production is a set of permissions nobody is watching.

## What the harness does not change

It packages how work is done; it does not lower what the work must clear. Every gate in the lifecycle standard applies inside a harness exactly as outside it: evidence for material claims, named authority for R3 and above, and no claim of production execution without it. A harness that quietly relaxes a gate has not made the agent more capable, only less accountable.

Nor does packaging make an agent correct. A harness with a clean evaluation on ten cases is an agent that passed ten cases.
