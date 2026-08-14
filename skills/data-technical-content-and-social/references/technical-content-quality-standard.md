# Technical-content quality standard

## Research and claims

Prefer current official documentation, standards/specifications, primary research and executable runtime evidence. Record product/runtime version, environment, source date and verification date. Reconcile conflicting sources explicitly. Classify each material statement as verified fact, implementation-specific behavior, convention, opinion, hypothesis or teaching simplification.

Every factual material claim has at least one evidence reference. Benchmarks include hardware, dataset, configuration, method, repetitions and limitations. Production incidents, scale, outcomes and personal experience must be authentic; otherwise use a clearly labelled synthetic scenario. Never invent metrics, quotes, adoption, reader results or test execution.

Store a bounded evidence snapshot or executable report with SHA-256, concrete version/date, verification timestamp and an independent verifier. `validate_content_manifest.py` defaults to `complete` mode, which requires real snapshots/artifacts, exact hashes, independent reviews and passed mandatory scopes. Use `--mode plan` only for an explicitly incomplete planning manifest; it is not completion or publication evidence. Use `--mode release` for exact-channel publication authority.

## Artifact gates

- Code declares setup, versions, safety scope, expected output and whether it is teaching-only or production-oriented. Run available formatter, static checks and tests; report actual status and failures.
- Diagrams identify whether conceptual or implementation-derived, preserve direction and boundaries, and include accessible alt text. Validate against code/config/evidence.
- Examples include error/failure behavior, not only the happy path. Explain trade-offs and when the technique should not be used.
- Content excludes secrets, proprietary interview material, private logs, customer data and unapproved company details.

Run independent reviews for technical accuracy, claim/source traceability, code/diagram validity, voice/originality and platform fit. A pass in one dimension does not compensate for a critical failure in another. Corrections update canonical and all affected channel variants through stable artifact links and a changelog.

For social variants, enforce Facebook=`vi`, LinkedIn=`en`, and Substack=`en`. The language check covers all reader-facing prose while allowing code, identifiers, product names and established technical terms to remain unchanged. A declared language without a passed exact-version `channel-language` test is insufficient for approval.
