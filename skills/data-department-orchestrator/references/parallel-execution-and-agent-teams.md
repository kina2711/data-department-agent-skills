# Parallel execution and delegated branches

Use this whenever work fans out — into subagents, an agent-teams runtime, or several passes by one
agent. The branch contract is the invariant; the runtime is not. If the runtime cannot run branches
concurrently, the same contract executes sequentially and the result is identical, only slower.

## When parallelism is legitimate

Branches must be independent in what they **write**, not merely in what they read. Two branches
reading one schema is fine; two branches writing one file is a silent last-writer-wins defect that
no test will show. Declare `write_paths` per branch and keep them disjoint. A branch that reads a
path another branch is rewriting sees a half-written state; either serialize those two or snapshot
the input first.

If a branch depends on another branch's output, the work is sequential. Say so and use the
sequential workflow rather than declaring a dependency inside a parallel wave.

## Branch delegation contract

Each branch is dispatched with `branch-delegation-contract.json`: branch ID, canonical `task_id`,
owner, inherited risk tier, allowed `write_paths` and `read_paths`, forbidden actions, expected
artifacts with hashes, the evidence it must return, and a token budget. Validate the whole wave
with `scripts/validate_branch_plan.py --task-catalog assets/task-catalog.json` before dispatching
anything; without the catalog the check is `incomplete`, not a pass.

**A delegated branch holds no authority.** It never approves, never publishes, never mutates
production, and never raises its own risk tier. Catalog risk is a floor that a branch inherits and
may exceed only by returning a proposal to the supervisor. Any task above the delegation ceiling
stops at a proposal; the supervisor obtains version- and hash-bound approval and executes it in the
main line.

## Fan-in

Merge in a declared deterministic order and record it in `fan-in-merge-record.yaml`. Two branches
that return contradictory findings do not get averaged, reconciled by preference, or resolved by
recency: the contradiction goes to `orchestrator-manage-conflict-register` with both sources
intact. Reconstruct nothing from a branch's narrative — a result exists only as the artifact and
evidence the branch returned, verified against the expected hash.

A failed branch never silently reduces scope. The run is `partial` with the failure visible and
owned; `complete` requires every branch released or complete. The supervisor inherits the highest
child risk tier before claiming completion.

## Runtime note

Concurrent agent execution may be experimental or unavailable in a given harness, and availability
changes. Never make correctness depend on it: the plan, the isolation rules and the merge policy
are what make the result trustworthy, and they hold in either mode.
