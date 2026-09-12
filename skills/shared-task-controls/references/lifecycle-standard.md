# Data work lifecycle standard

## Canonical lifecycle

1. **Plan** — define outcome, scope, owner, consumers, dependencies, acceptance criteria, evidence and test strategy.
2. **Assess** — inspect current state, establish a baseline, validate inputs, classify risk and expose blockers.
3. **Design** — choose the smallest viable approach, alternatives, controls, observability and recovery path.
4. **Execute** — create or change the artifact in the safest suitable environment with versioned checkpoints.
5. **Test** — verify correctness, semantics, quality, integration, security, privacy, performance and recovery as applicable.
6. **Review/Approve** — resolve findings and obtain authority appropriate to risk; approval never replaces testing.
7. **Release/Handoff** — publish, deploy or transfer the exact validated version with evidence and ownership.
8. **Monitor/Improve** — observe outcomes, close residual actions and feed evidence into process improvement.

## Risk-adaptive paths

| Tier | Typical work | Path | Required control |
|---|---|---|---|
| R0 light | Read-only lookup or bounded analysis | Fast | Evidence and self-check |
| R1 reviewed | Design, documentation, learning or advisory baseline | Standard | Peer/domain review |
| R2 standard | Reversible non-production build or people workflow | Standard | Automated/practical test plus owner review |
| R3 controlled | Production, access, sensitive, external or material-cost change | Controlled | Independent tests, explicit approval, rollback and monitoring |
| R4 critical | Destructive, regulatory, breach, certified or high-impact decision | Controlled | Segregated approval, strongest evidence, rehearsed recovery and audit trail |

Never downgrade risk to meet a deadline. Upgrade it when scope or evidence changes.

## Gates

- **G0 Intake:** correct task, role and primary deliverable selected.
- **G1 Ready:** Definition of Ready passed; blockers resolved.
- **G2 Design:** approach, tests, controls and recovery reviewed.
- **G3 Execute:** authority exists for the planned environment and scope.
- **G4 Test:** mandatory tests pass with stored evidence.
- **G5 Approve:** accountable human approves the exact version when required.
- **G6 Release:** smoke/reconciliation succeeds and ownership transfers.
- **G7 Stabilize:** monitoring window closes or improvement actions are assigned.

## Optimization rules

- Select one atomic task at a time; compose multi-role work in the orchestrator.
- Ask only questions whose answers change semantics, risk, scope, test strategy or acceptance.
- Reuse verified context and evidence; do not repeat an approved phase without a change request.
- Run independent checks in parallel when they do not share mutable state.
- Automate deterministic validation; reserve human review for semantics, judgment, authority and exceptions.
- Stop early on a failed mandatory gate. Do not spend build effort on an unready requirement.
- Keep work in progress small and prefer reversible increments over large batches.
- Measure cycle time, rework, escaped defects, approval wait and outcome quality; optimize bottlenecks using evidence.
