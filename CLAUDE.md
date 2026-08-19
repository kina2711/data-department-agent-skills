# Data Department Agent Skills

Use the role-based skills in `skills/` for Data Department work. Route multi-role or ambiguous requests through `data-department-orchestrator`. Select atomic tasks by primary deliverable rather than job title. Read the selected task contract completely and load only relevant company context, technology adapters and industry references.

Classify every task by lifecycle profile, risk tier and execution path. Apply Plan, Assess, Design, Execute, Test, Review/Approve, Release/Handoff and Monitor/Improve stages as specified by the selected contract. Use the R0 fast path only for genuinely light read-only work; never downgrade risk to meet a deadline.

Never claim production execution, publishing, access changes, deletion, certification or model promotion without evidence and required human approval. Preserve the user's existing work, inspect live artifacts before making change-sensitive claims, and record assumptions, validation, residual risks and handoffs.

Treat `docs/skill-map.md` as the canonical taxonomy. Rebuild generated skill content with `tools/build_suite.py`, then run `tools/validate_suite.py`.
