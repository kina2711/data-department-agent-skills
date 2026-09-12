# Safety and approval matrix

Require explicit, scoped, version-specific human approval for:

- Production writes, deployment, publishing, promotion or traffic changes.
- Grants, roles, row or column security, secrets and credential rotation.
- PII or confidential-data exposure, extraction, sharing or external rendering.
- Backfills that can overwrite data; deletion, retirement or irreversible migration.
- Certified metric, glossary, policy, retention or business-rule changes.
- Material spend, reserved capacity, vendor commitment or external coordination.
- Model promotion, retraining policy, automated decision logic or high-risk AI release.

Approval does not waive validation. Preserve evidence and rollback instructions.
