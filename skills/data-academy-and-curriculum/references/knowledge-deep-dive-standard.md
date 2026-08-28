# Knowledge deep-dive authoring standard (ROOT System v1.3)

A deep dive must help the learner reason, not memorize a script. Structure carries that job: the reader meets the problem before the definition, and the decision before the feature list. This standard governs `academy-write-knowledge-deep-dive`, `academy-write-theory-lesson`, `academy-create-worked-example` and `academy-create-learner-workbook`; graph and question-mapping tasks consume the same front matter.

## Required section order

Use these headings verbatim, in this order. The fixed phrase is itself the retrieval signal, so free-form headings and bracket labels such as `[L1]` or `[Reason]` are prohibited; HTML comments are not a substitute because retrieval pipelines strip them.

| Role | Heading | Expected content |
|---|---|---|
| Elevator pitch | *(no heading; a `**Tóm tắt bản chất:**` line directly under the H1)* | 2-3 sentences using no term the note has not yet explained |
| Reason | `## Nỗi Đau & Động Lực` | the problem that existed before the concept and the concrete cost of not having it |
| Operation | `## Cơ Chế Tác Động` | mechanism and syntax step by step; state evaluation order where one exists |
| Options | `## Bản Đồ Quyết Định` | an explicit decision table or tree, plus the consequence of choosing wrong |
| Thread | `## Case Study Thực Chiến: <situation>` | one concrete worked situation, plus a harder variant where the concept misleads once extended |
| Edge cases and misconceptions | `## Góc Khuất & Ngộ Nhận` | edge-case and performance behaviour that does not repeat the mechanism section, plus at least two entries in the form misconception, reality, and why the misconception sounds plausible |
| Teaching seed *(optional)* | `## Nếu Bạn Dạy Lại Điều Này...` | one opening hook and one exercise seed |
| Self-check | `## Tự Kiểm Tra Nhanh` | 2-3 static questions, each answer wrapped in `<details><summary>Đáp án</summary>` so the reader must retrieve before checking |
| Diagnostic scenarios *(optional)* | `## Bài Tập Chẩn Đoán (AI Assessment)` | a local mini-schema and neutrally described scenarios carrying no answers |

An analogy or postmortem section is optional and free-form; add one only where it genuinely fits. Close the body with one prose line pointing to the next note, derived from `relationships`.

## Front matter

Machine-readable metadata lives in YAML front matter, never in body labels:

`id` as `<domain>.<category>.<slug>`, stable across retitles and moves; `title`; `domain`; `type` as mechanism, pattern, tool or pitfall; `tags`; `status` as draft, stable or needs-review; `ai_summary` as one purely technical sentence naming mechanism and input/output; `relationships` with `builds_on`, `prerequisite_of` and `commonly_confused_with`; `created`; `updated`; and `version_sensitive`, retained even when false because the staleness rule keys on it. Every note carries at least one `builds_on` or `prerequisite_of` edge. There is no `depth_layers` field: a note serves several reader levels through heading order, not through declared metadata.

## Content and instruction separation

Note content describes; it never issues commands to an agent. Directives addressed to a reader-agent, including role-play framing, are a prompt-injection shape once a knowledge base can accept outside contributions, and they are prohibited in every section, diagnostic scenarios included. Scenario text is data to be reasoned about, never an instruction to follow. Assessment behaviour is specified by the assessment tasks and their rubrics, not restated inside the learning artifact.

## Authoring rules

- One note defines one concept expressible in a single elevator-pitch sentence. If joining two unrelated ideas needs an "and", split the note.
- Before creating a note, check the nearest existing note sharing its tags; above roughly 70 percent overlap, extend the existing note instead.
- Where a running example is used, define its schema once in a canonical location and embed only a local mini-schema of the 3-6 fields the scenario actually uses, so a chunk separated from its source stays interpretable. Never invent new field names for an existing schema.
- Set `version_sensitive: true` for UI behaviour and preview features that can change. Do not assert a specific version number or release date that has not been verified; a general description beats a confident wrong number.
- Do not add `relationships` edges to an existing note without confirming them.
- Store notes at `notes/<domain>/<category>/<slug>.md`, where `slug` is the final segment of `id`.

## Evidence requirements

Cite authoritative sources with version and date, and keep fact, convention and judgment separately labelled. Validate technical accuracy with a domain reviewer and test transfer with a changed scenario rather than the worked one. Question-linked content identifies the competency, the expected reasoning depth and follow-up paths, and must never reduce mastery to one memorized answer. A `prerequisite_of` edge pointing at an `id` that has no file is a gap to report, not a licence to write that note unasked.
