# Personal-project operating system

Build a personal project as evidence of problem solving, engineering judgment and verified execution—not as a technology checklist or a renamed clone.

## Mode selection

Choose the mode from the strongest available evidence and the user's actual objective:

| Strongest starting evidence | Primary mode | Required first proof |
|---|---|---|
| Pain/consequence | problem-first | actor, current workaround, measurable consequence |
| Repeated workflow | user-workflow-first | observed steps, friction, errors and handoffs |
| Decision/KPI | decision-first | owner, action, uncertainty and decision latency |
| User's own idea | idea-first | problem/user/feasibility validation |
| External idea/demo/article/product | inspiration-first | provenance, rights and transformation thesis |
| Dataset | dataset-first | actual inspection, profiling, fitness and limitations |
| Repository | repo-first | exact commit/license, audit, baseline run and improvement matrix |
| Target role/gap | role-competency-first | required evidence mapped to capabilities |
| Technology | technology-first | problem fit and non-toy outcome; tools are not value |
| Business domain | domain-first | entity/event/process/decision map and bounded problem |
| Architecture question | architecture-first | workload, quality attributes, alternatives and failure proof |
| API/source/target | integration-first | contracts, reliability, security and reconciliation |
| OSS issue | open-source-issue-first | maintainer intent, reproduction and contribution rules |
| Paper | paper-replication-first | hypothesis, environment, reproduction criteria and extension |
| Tutorial/course | tutorial-course-first | removed scaffold plus changed data/constraints and new tests |
| Incident/failure | incident-failure-first | reproduction, detection, diagnosis, recovery and prevention |
| Binding constraint | constraint-first | measurable constraint and acceptable trade space |
| Performance/cost question | benchmark-first | controlled baseline, variables, repetitions and limitations |
| Policy/control | governance-compliance-first | control objective, evidence and failure consequence |
| Multiple strong inputs | hybrid-input | one primary thesis; secondary inputs remain provenance/constraints |

Do not create a separate “repo plus idea” mode. Prefer repo-first when code exists, then transform the repo into a differentiated thesis. Prefer inspiration-first when only someone else's concept exists. If intent is contribution rather than ownership, use open-source-issue-first.

## Selection system

Apply hard gates before scoring: rights/license, data/privacy, safety/ethics, feasible minimum slice and observable success. A failed hard gate blocks selection regardless of weighted score.

Score viable options out of 100 using the reusable scorecard: problem value 12, target-role fit 14, evidence strength 12, differentiation 12, feasibility 10, data readiness 8, testability 8, operations depth 6, deployability/demo 5, maintainability/evolution 4, security/privacy/legal 5, and cost/time sustainability 4. Attach evidence and confidence to each score; subtract an explicit risk penalty rather than hiding uncertainty in optimistic scores.

Select for a balanced proof portfolio. A smaller project with real failure handling, tests, deployment evidence and clear decisions can outrank a broad architecture that never runs. Do not choose solely by trend, repository stars, tool count, dataset size or apparent complexity.

## Common execution loop

1. Classify inputs, provenance, access and uncertainty.
2. Generate two to five bounded theses; reject duplicates and tool-only demos.
3. Apply hard gates, weighted scoring and confidence/risk review.
4. Lock one thesis: problem, user, outcome, hypothesis, contribution, non-claims, scope and success evidence.
5. For external sources, complete the attribution/originality transformation before implementation.
6. Build an implementation-ready blueprint and vertical-slice roadmap.
7. Handoff each slice to the accountable Data role; preserve project IDs and evidence contracts.
8. Test correctness, integration, reconciliation, security/privacy, performance/cost, failure/recovery, usability and reproducibility as applicable.
9. Classify status truthfully: planned → implemented → tested → demonstrated → released → maintained.
10. Audit portfolio claims and plan maintenance/evolution from real gaps and feedback.

## Borrowed-source default

An external repository or idea is a source, not the finished project. Record one of `inspired-by`, `adapted-from`, `forked-from`, `replicated-from` or `contributed-to`; never silently relabel it `self-originated`. Preserve author/owner, locator, version/commit, license/terms, permitted use, borrowed elements and attribution text.

Create a user-owned build thesis by changing the problem framing and delivering substantive proof. Require meaningful differentiation on at least three axes unless the declared purpose is exact replication or upstream contribution: problem/user, data/domain, architecture, reliability, governance, performance/cost, operations, evaluation or experience. Renaming, UI restyling, framework substitution, prompt rewriting or documentation alone does not satisfy originality.

If a public repository has no license, default copyright applies: inspect and learn, but do not reproduce, distribute or publish derivative code without permission. Never convert provenance honesty into a claim that the user invented the external source.

## Research basis

- GitHub licensing: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository
- GitHub repository practices: https://docs.github.com/en/repositories/creating-and-managing-repositories/best-practices-for-repositories
- GitHub open-source contribution: https://docs.github.com/en/get-started/exploring-projects-on-github/contributing-to-open-source
- NIST SSDF: https://csrc.nist.gov/pubs/sp/800/218/final
- OpenSSF Scorecard: https://scorecard.dev/
- SLSA provenance levels: https://slsa.dev/spec/v1.0/levels
- DORA capabilities: https://docs.cloud.google.com/architecture/devops
- NIST AI RMF: https://airc.nist.gov/airmf-resources/airmf/5-sec-core/
- FAIR data principles: https://www.go-fair.org/fair-principles/
