# Canonical concept registry

Four ID spaces describe the same knowledge and none of them join: the system-design canon's `sd.*` IDs, note IDs in a corpus, `topic_id` in learner memory, and `concept_id` in a concept graph. A note about idempotency and a canon entry about idempotency are the same concept wearing two names, so coverage cannot be measured, a note cannot prove it teaches a competency, and mastery cannot point at what taught it. The registry is the layer above all four. It owns no content; it owns identity.

## The key

A registry entry is a **concept key** of the form `ck.<domain>.<slug>` — `ck.proc.idempotency`, `ck.sql.window-function`. Each key carries a one-sentence definition, and that sentence is the entry's real work: without it two notes cannot tell whether they are claiming the same concept or two different ones that share a word.

Every key records what it binds to: canon IDs, note IDs, learner-memory topic IDs, competency IDs and question IDs. Bindings point outward from the registry. Nothing in the canon, a note or a memory file is rewritten to accommodate a key, and `sd.*` IDs keep their meaning unchanged.

## Propose early, register before counting

A key may be coined and bound to the moment a note needs one; work does not stop for an acceptance cycle. A new key enters as `proposed` carrying its definition sentence, domain and owner, and notes bind to it immediately.

What `proposed` does not buy is coverage. Only `registered` keys count, so a corpus can be written entirely against proposed keys and still report honestly that none of it is verified coverage yet. Acceptance is a batch review, not a gate in front of every key.

The risk this trades away is real and worth naming: two modules coining different keys for one concept, found only after both have notes. It is contained mechanically rather than by rule. The validator reports proposed keys whose names or definitions closely resemble each other or an existing key in the same domain, and that report is resolved before a batch is accepted. Merging two proposed keys is cheap; merging two registered keys that already carry bindings is not.

## One primary note per key

A key may bind to several notes — the same concept taught at different levels legitimately appears more than once. Exactly one of those notes is the key's **primary** teaching note. This is what makes duplication decidable: two notes both claiming primary on one key is a duplicate, reported mechanically, rather than a judgment about how similar their tags look. A near-duplicate that is genuinely a second view of the concept keeps its binding and drops its primary claim.

Aliases resolve to exactly one key. The same alias registered against two keys is an error, because a lookup would then depend on which entry was read first.

## What coverage now means

A canon ID or competency counts as covered only when a key bound to it has a primary note whose status is `reviewed`. A note that exists is not coverage; a note that is drafted is not coverage; a key with three notes and no primary is not coverage. Report uncovered keys, keys whose primary note is stale, and bindings that point at IDs no longer present, separately — they call for different work.

Run `../../scripts/validate_concept_registry.py` for the mechanical checks: unregistered keys in use, duplicate primaries, alias collisions, dangling bindings, cycles in `parents`, and canon or competency IDs with no registered key.

## Retiring a key

Supersede; do not delete. A superseded key names its successor and keeps its bindings readable until every referring artifact has been repointed. Deleting a key silently breaks the crosswalk that made a coverage number meaningful, and the number keeps rendering.

## What the registry is not

It is not study content and holds no explanations — those live in notes. It is not a competency framework and does not say what a role must know. It is not evidence of learning: a key bound to a mastered topic records that the two refer to the same concept, never that the concept was mastered because a note exists. Mastery semantics stay with the learner-memory contract.
