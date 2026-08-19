---
name: dd-approve
description: Check whether a version- and scope-bound approval record currently authorizes a gated action, and state exactly what is still missing.
argument-hint: "[approval record path] [artifact root]"
disable-model-invocation: true
---

Check approval authority. Optional paths: $ARGUMENTS

You cannot grant approval. You can only report whether a valid approval record exists.

1. Locate the approval record. If none exists, initialize one from `skills/data-department-orchestrator/assets/approval-record.json`, leave it unsigned, and state that the action remains **unauthorized** until a named human approver completes it.
2. Validate it against the current time:

```
python skills/data-department-orchestrator/scripts/validate_approval_record.py <record> --task-catalog task-catalog.json --artifact-root <root> --require-approved
```

3. Report each binding explicitly:
   - **Version binding** — does `artifact_version` match the artifact about to change?
   - **Hash binding** — does `artifact_sha256` match the current artifact bytes? A changed artifact voids the approval.
   - **Scope binding** — does every target of the intended action fall inside `scope`?
   - **Time binding** — is the record inside its `decided_at` / `expires_at` window right now?
   - **Authority binding** — is `approver` a named person with stated `authority` at this `risk_tier`?
   - **Conditions** — are all `conditions` satisfied, and by what evidence?
4. If any binding fails, the action is not approved. Say so plainly and name the single thing required to close it.

Return: authorized yes/no, the failing bindings, the risk tier, and the exact scope the record does authorize. Approval never waives testing, and an expired or hash-mismatched record is the same as no approval.
