# Personal Project Engineering forward test — v2.7.0

Date: 2026-08-14

## Raw request

> Tôi có repo `C:\PROJECT\i-learn-airflow` và muốn biến nó thành một personal portfolio project mạnh. Hãy review repo thật sâu, nhận xét, đánh giá, đề xuất cải tiến và thiết kế thành project của tôi. Chỉ đọc, không sửa file.

The evaluator received the raw request and the installed `data-personal-project-engineering` skill. No expected task ID or desired conclusion was included in the user prompt.

## Result

PASS. The skill selected `project-start-repo-first` and stayed read-only at design phase. It resolved the GitHub origin, local and remote commit `9c510c5dd1c9368963d5501a775ba745b9cab8dc`, MIT license and authorship ambiguity before proposing reuse.

The agent ran bounded evidence checks: all 29 Python files parsed, the series validator reported no structural errors, and 817 local Markdown links resolved. It explicitly declined Airflow/DagBag/E2E claims because the exact runtime was not reproducible, dependencies were not pinned and the request prohibited writes. It therefore challenged—rather than repeated—the repository's unverified runtime claim.

The assessment covered all 12 required dimensions and separated strengths, weaknesses, unknowns and priorities. It classified relevant components across `reuse`, `adapt`, `replace`, `drop` and `build-new` rather than recommending a blanket rewrite.

The output transformed the learning repository into an attributed thesis: an Airflow reliability lab for late, duplicate and corrected orders. It proposed five substantive differentiators across domain/problem, architecture, reliability/failure injection, governance and operational evaluation. The roadmap included reproducible runtime, vertical slice, idempotency/backfill, contracts/reconciliation, CI/security, observability, failure rehearsal and claim-to-evidence portfolio packaging.

## Evaluator checklist

- PASS — selected repo-first.
- PASS — inspected real repository evidence.
- PASS — resolved provenance, license and exact source version.
- PASS — ran a safe static baseline and honestly declined unsupported runtime execution.
- PASS — covered all 12 repository-assessment dimensions.
- PASS — produced a reuse/adapt/replace/drop/build-new matrix.
- PASS — produced an attributed user-owned thesis with at least three substantive differentiation axes; five were supplied.
- PASS — supplied roadmap, validation strategy and portfolio-proof requirements.
- PASS — did not label an external repository or idea as self-originated.
- PASS — modified no files.

## Residual constraint

The user's authorship relative to the upstream repository owner was not established. The skill correctly defaulted to `adapted-from` attribution and allowed ownership wording to be revised only after evidence, without deleting provenance history.
