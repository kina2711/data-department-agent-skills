# Universal professional-series rules

Use this contract for technical series planning, episode authoring, channel adaptation and release. Optimize for reader capability and verifiability, not posting frequency, jargon density, length or inspiration.

## Input and assumption contract

Collect series name, topic, audience, starting and target levels, business context, recurring narrative case, platforms, channel languages, technical baseline, sources, brand voice, visual system and publishing constraints. Record low-risk assumptions explicitly. Use placeholders for owner-confirmed facts; never invent versions, metrics, customers, outcomes, architectures or experience.

## Capability journey and coverage

Design a progression from mental model to basic execution, distinctions, failure handling, purposeful design, review and independent operation. Organize episodes across the layers actually needed: problem/mental model, core mechanics, correctness/reliability, operations/governance and design/capstone. Do not claim beginner-to-advanced coverage when the series contains only APIs and happy-path operations.

Assign each episode exactly one primary type: `FOUNDATION`, `DISTINCTION`, `MECHANISM`, `IMPLEMENTATION`, `DECISION`, `FAILURE`, `OPERATIONS`, `REVIEW` or `CAPSTONE`. Avoid long runs of implementation-only episodes. Maintain a coverage matrix with topic, owning episode, prerequisite, depth, code, failure mode and status; use it to expose gaps, duplication, premature dependencies and unverifiable scope.

Prefer one clearly synthetic recurring case with organization context, result consumer, inputs/outputs, reference workflow, service expectation, failure scenarios and data/resource/security constraints. Reveal only the case detail needed by the current episode.

## Teaching contract per episode

Do not draft the caption until the brief names: learning objective, reader starting point, misconception, concrete scenario, one-sentence core claim, core mechanism, decision, failure mode, evidence and intentional boundary. Every section must advance the core claim.

Prefer `situation → consequence → mental model → concept name → mechanism → example → code → failure → trade-off → decision`. Explain why code exists before asking the reader to inspect it. Select only depth questions relevant to the objective: responsibility and non-responsibility, state/data change, applicability, non-applicability, trade-off, observable failure, verification, assumptions, version sensitivity and context-bounded conclusions.

## Human professional voice

Write calmly, precisely and concretely. Respect the reader; do not lecture, perform expertise, imitate a press release or add sales language without a sales purpose. Prefer a concrete actor, action, object, condition and consequence over abstract claims.

Do not fabricate first-person experience, projects, customers, testimonials or dialogue. Label synthetic scenarios. Avoid formulaic openings, fake excitement, engagement bait, repeated slogan fragments, adjective triplets, excessive em dashes and repeated constructions such as “not only... but also...”. Do not use jargon when plain language preserves the meaning; retain exact API, class, component and official-documentation terminology.

After drafting, remove title repetition and empty transitions, replace abstractions with observable detail, qualify absolutes, cut roughly 10–20% when meaning is preserved, inspect paragraph-opening logic and vary sentence rhythm naturally. The conclusion must support a decision: when to use, when not to use, what to verify, the main boundary or the next action.

## Evidence and overclaim controls

Distinguish sourced technical fact, context-bound design judgment, conditional recommendation, prediction and accountable experience. Prefer specifications/standards, official product documentation, source/release notes, primary research and direct vendor material; use community sources for experience or perspective. Map disputed claims to source, version/date, valid scope, conditions/exceptions and confidence. Recheck current version, lifecycle status, links, APIs, pricing, law, standard and policy immediately before publishing.

Avoid `always`, `never`, `best`, `perfect`, `guaranteed`, `production-ready` and `enterprise-grade` unless evidence and scope make the statement defensible. State applicability conditions, residual verification and what the method does not guarantee.

## Mandatory visual evidence contract

Each published social episode must include three functional asset roles in the default order `REAL → ILLUSTRATION → CODE`; record an editorial exception when changing order, and block release when omitting a role without an approved reason.

- `REAL`: use an authentic screenshot, interface, dashboard, terminal output, log, device, process, document, measurement or work artifact. Point to what the practitioner observes. Never label AI-generated UI or a mock-up as real. Preserve meaningful errors and limitations. Record source and rights; redact secrets, credentials, PII, internal URLs/IPs, private repositories, customer/project names and confidential data in the exported pixels, not only a removable overlay.
- `ILLUSTRATION`: explain one mechanism, relationship, state transition, decision, failure path, architecture, timeline or responsibility boundary. Complete “after viewing this, the reader understands...” before designing. Choose layout from the actual relationship; do not use cards for a flow. Keep one idea per node, mobile-readable text, semantic colors and alt text. Do not use generative-image models to render important code, logos, exact UI, tables, dense labels or long typography; use a controlled renderer.
- `CODE`: prove a declaration, dependency, validation, error path, configuration, query, test, command, contract or policy. Label it `runnable-example`, `code-reference` or `pseudocode`; declare baseline/dependencies and actual validation. Code must be syntactically appropriate, scoped to the objective, secret-free and mobile-readable. Never present unvalidated pseudocode as runnable or production-ready.

The caption must bridge all three layers: where the real signal appears, which mental model explains it and how code implements or verifies the mechanism. Captions such as “see image for details” fail. Every asset needs specific alt text.

## Channel and CTA contract

Write each channel separately from the approved canonical evidence pack. Adapt assumed knowledge, entry speed, length, line breaks, terminology explanation, CTA, hashtags and caption-image relationship. Do not translate sentence by sentence.

- Facebook: Vietnamese, beginner-friendly without false simplification, 500–700 words by default, headings for scanning, emoji only as navigation, four to six hashtags and one specific technical question.
- LinkedIn: English, 200–260 words by default, focused on decision/trade-off/operational consequence, no emoji, sparse functional headings, no self-help voice, three to five hashtags.
- Substack: English and long-form according to the platform playbook.

Use CTA to ask about a decision, failure, risk control, trade-off or small verification. Reject generic “What do you think?”, “Agree?”, “Comment YES”, tagging requests and unrelated engagement bait.

## Release gates

Run independent editorial, human-voice, depth, evidence, REAL-image, illustration, code and platform gates. Do not release when the objective is missing, a material claim lacks evidence, a mandatory asset role lacks an approved exception, REAL media leaks sensitive data, runnable code does not parse, experimental behavior is called stable, prose is promotional/template-like, the article is a feature list, media is decorative, alt text is missing or the conclusion exceeds the evidence.
