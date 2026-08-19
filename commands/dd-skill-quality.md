---
name: dd-skill-quality
description: Score task contracts against recorded outcomes — routing, completion, fallback and evidence rates — and produce controlled improvement recommendations.
argument-hint: "[telemetry ledger] [skill]"
disable-model-invocation: true
---

Score contract quality from: $ARGUMENTS

This scores the **suite's own task contracts**, not the data they operate on. For data quality
work, use `/dd-quality`, which opens the Data Quality and Reliability department.

809 contracts are not uniformly good. Without recorded outcomes, an unreliable task and a
dependable one look identical, and the same failure repeats because no feedback ever reaches
the contract that caused it.

1. Score the ledger:

```
python skills/data-department-orchestrator/scripts/score_skill_quality.py <telemetry.jsonl> --task-catalog task-catalog.json --report-out skill-quality.json
```

2. Read the recommendation per task and what drives it:

| Action | Meaning |
|---|---|
| `observe` | Fewer than 5 runs. Too few to judge — keep collecting, draw no conclusion |
| `healthy` | Completing reliably at the recorded sample size |
| `fix-routing` | Over 25% of runs overrode the routed task; the trigger wording is attracting work this contract does not own |
| `investigate` | Under 60% completion. Find the cause |
| `derive-variant` | Over 25% of runs needed a fallback; a variant contract for that path may be missing |
| `tighten-evidence` | Completions are being claimed without verified evidence |

Note that `fix-routing` can fire on a task with 100% completion. Completion alone hides a
routing defect: the work succeeds, but the wrong contract was doing it.

3. **A high failure rate triggers investigation, never a weaker gate.** If the change you are
   about to propose is "relax the approval" or "drop the test that keeps failing", stop — the
   gate is doing its job and the cause is upstream of it.
4. Recommendations are change requests, not edits. Do not rewrite a contract off the back of
   this report. Open the change with the quality record attached as evidence and let it be
   reviewed like any other change.
5. Telemetry carrying `user_content` is rejected outright and the run fails. Never add prompts,
   data values or transcripts to make a signal richer.
6. An empty ledger exits `1`: quality is **unknown**, which is not the same as good. Say so.

Return: the tasks needing action ranked worst-completion first, the specific defect behind
each, the change request you would open for the top one, and which tasks have too few runs to
judge at all.
