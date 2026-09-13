# Agent harness

A harness is everything one agent needs to do one role's work, packaged so it behaves the same way twice and can be handed to somebody else. It is not a bundle of skills. It is a boundary, and most of its value is in what it excludes.

The suite already has the parts — task contracts, a context package, a tool surface, evaluation cases, run state. What a harness adds is the declaration of which ones apply, and that declaration is the artifact `orchestrator-define-agent-harness` produces.

## Agent = model + harness

A model is a text predictor that stands still and forgets. It cannot run a command, cannot see a file, and remembers nothing between calls. Everything an agent does that a model cannot, the harness does — which is why the same model, wrapped in two different harnesses, produces an agent that finishes a project and an agent that flails.

Four parts, and every one of them already exists somewhere in this suite. Naming them together is the point: a harness missing one of the four fails in a way that looks like the model being bad at its job.

**The loop.** Think, call a tool, read what came back, think again, one step at a time until the work is done. [The harness delivery loop](harness-delivery-loop.md) is this suite's version, and the reason a loop is a design decision rather than a detail is that the stopping condition is part of it: a loop with no stated finish runs until something else stops it.

**Tools and the environment.** Hands. Run a command, read a file, call an API. [The external tool access standard](external-tool-access.md) governs what may be reached and separates reading from writing, because the sharper the tool and the smaller the environment, the more real work a model gets done and the less of it is guessing.

**State and memory.** After every call the model has forgotten. What persists is whatever the harness wrote down: history, notes, checkpoints. [The workflow runtime and evidence OS](workflow-runtime-and-evidence-os.md) holds run state so an agent survives past one context window and wakes up in the right place, and [the context budget standard](context-budget-standard.md) governs what stays in the window while it is still running.

**Safety rails.** An agent will trip. A command errors, a permission is wider than the task needed, an answer is confidently wrong. Risk tiers, approval gates, the production guard hook and [safety and approvals](safety-and-approvals.md) are the floor it lands on: bound the permission, catch the error, retry what is safe to retry, and ask a person for the rest. Trip without falling.

The strongest models are trained for the harness they run inside; the two are designed to fit. That is the whole reason the same model behaves differently in two harnesses, and the reason a harness is worth declaring rather than assuming.

## What a harness declares

- **Scope.** The tasks this agent may select, and the ones deliberately left out. "Everything the skill offers" is not a scope; it is the absence of one.
- **Grounding.** The schema index, company context, corpus or registry the agent retrieves from, each pinned to a version. An agent grounded on whatever happened to be current is not reproducible.
- **Tool surface.** What it may reach outside the warehouse, read and write separately, per the external tool access standard.
- **Guardrails.** Permission mode, write ceiling per run, the gates that require named authority, and the risk tier above which it stops and asks.
- **Evaluation.** The cases that decide whether this harness works, and the score it reached on them. Without these, "it works" is an opinion held by whoever built it.
- **Environment.** What must exist for it to run at all: credentials by name not value, services, versions.

## Reproducible, or it cannot be debugged

Two runs of the same harness on the same input should differ only where the model is non-deterministic — never because a prompt, a corpus or a schema moved underneath it. Pin every input that is not the user's request, and record the pinned versions with the run.

When an agent produces something wrong, the first question is what it was working from — the model, the prompt, the corpus, the schema, each at the version it had that day. Unable to answer that, a harness turns every investigation into an archaeology exercise, and the answer is usually that something changed and nobody knows what.

## Version it, because a changed harness is a different agent

Swap the model. Edit the system prompt, add a tool, widen the scope — each one produces an agent with different behaviour and an evaluation that no longer describes it. Version the harness, re-run its cases, and record both; `orchestrator-audit-agent-harness` exists to compare a running agent against the declaration it claims to follow. An evaluation score attached to a version nobody can reconstruct is decoration.

## Handing one over transfers risk as well as capability

Handed to another team, a harness runs under their credentials, in their environment, against their data. The guardrails travel with it or the harness is not what they received. State plainly what it may write, what it may spend, and what it stops for; a recipient who has to infer the blast radius from reading prompts will infer it wrong.

Name an accountable owner. An unowned harness in production is a set of permissions nobody is watching.

## What the harness does not change

It packages how work is done; it does not lower what the work must clear. Every gate in the lifecycle standard applies inside a harness exactly as outside it: evidence for material claims, named authority for R3 and above, and no claim of production execution without it. Quietly relax a gate and the agent is not more capable, only less accountable.

Nor does packaging make an agent correct. A harness with a clean evaluation on ten cases is an agent that passed ten cases.
