---
name: dd-constitution
description: Establish or enforce the project constitution — locked technology decisions and blocking architecture rules that downstream work may not silently renegotiate.
argument-hint: "[ratify | check <plan text> | amend]"
disable-model-invocation: true
---

Constitution operation: $ARGUMENTS

The failure this prevents: an agent implements a feature and quietly swaps a settled
technology or breaks a settled boundary along the way. A decision changes by amendment, never
as a side effect.

## Ratify

1. Copy `skills/shared-data-core/assets/project-constitution.json` to the project root.
2. Fill it from real decisions already made — ADRs, architecture docs, existing dependency
   manifests. Do not invent principles the team never agreed to; an unratified constitution
   that nobody believes is worse than none.
3. For each technology layer record the version constraint, whether it is `locked`, where it
   was decided (`decided_in`), and which alternatives were rejected. The rejected list is what
   makes drift detectable later.
4. Set `amendment_policy.requires_approval_from` to a named authority. Leave `ratified_by`
   empty until a human ratifies it, and say so.
5. Validate: `python skills/shared-data-core/scripts/validate_constitution.py project-constitution.json`

## Check a plan before building

```
python skills/shared-data-core/scripts/validate_constitution.py project-constitution.json --proposal-file <plan.md>
```

Exit `3` means the plan names a rejected alternative for a locked layer. That is a **blocked**
plan, not a warning to note and proceed past. Either change the plan or open an amendment.

## Amend

```
python skills/shared-data-core/scripts/validate_constitution.py project-constitution.json --previous <ratified-copy.json>
```

An amendment requires a version bump and the named approver. Changing a locked layer,
unlocking one, or removing or downgrading a blocking rule without both is reported as a
violation — report it as such rather than explaining it away.

Return: the locked layers, the blocking rules, whether the current plan conflicts with any of
them, and the exact amendment that would be required to proceed as proposed.
