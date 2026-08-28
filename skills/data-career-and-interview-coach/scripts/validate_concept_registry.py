#!/usr/bin/env python3
"""Check that a concept registry actually joins the ID spaces it claims to join.

A crosswalk fails quietly. A key referenced before it was registered, an alias claimed by two
keys, a binding to a note that was renamed, two notes both calling themselves the primary
teaching note for one concept — none of these raise anything at read time. They simply make the
coverage number wrong, and it keeps rendering as though it were right.

Coverage here has one meaning: a canon or competency ID is covered when a registered key bound
to it has a primary note marked `reviewed`. A note that exists is not coverage, and neither is a
key with three notes and no primary.

It checks identity structure. It cannot tell whether a definition is a good one, whether two keys
that look distinct are really the same concept, or whether the primary note teaches it well.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

KEY_PATTERN = re.compile(r"^ck\.[a-z0-9-]+\.[a-z0-9-]+$")
VALID_STATUS = {"proposed", "registered", "superseded"}
COUNTABLE_NOTE_STATUS = "reviewed"
# Two keys in one domain this similar are probably one concept coined twice.
NAME_SIMILARITY_THRESHOLD = 0.82
DEFINITION_SIMILARITY_THRESHOLD = 0.75


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def find_cycles(edges: dict[str, list[str]]) -> list[list[str]]:
    colour: dict[str, int] = defaultdict(int)
    cycles: list[list[str]] = []
    stack: list[str] = []

    def visit(node: str) -> None:
        colour[node] = 1
        stack.append(node)
        for nxt in edges.get(node, []):
            if colour[nxt] == 0:
                visit(nxt)
            elif colour[nxt] == 1:
                cycles.append(stack[stack.index(nxt):] + [nxt])
        stack.pop()
        colour[node] = 2

    for node in list(edges):
        if colour[node] == 0:
            visit(node)
    return cycles


def collect_note_status(manifest: Any) -> dict[str, str]:
    """Note ID to status, from a corpus manifest; absent manifest means status unknown."""
    if not isinstance(manifest, dict):
        return {}
    notes = manifest.get("notes")
    if not isinstance(notes, list):
        return {}
    return {
        str(n.get("id", "")).strip(): str(n.get("status", "")).strip()
        for n in notes
        if isinstance(n, dict) and str(n.get("id", "")).strip()
    }


def collect_note_keys(manifest: Any) -> dict[str, list[str]]:
    """Note ID to the concept keys it claims, so bindings can be checked in both directions."""
    if not isinstance(manifest, dict):
        return {}
    notes = manifest.get("notes")
    if not isinstance(notes, list):
        return {}
    return {
        str(n.get("id", "")).strip(): [str(k).strip() for k in (n.get("concept_keys") or [])]
        for n in notes
        if isinstance(n, dict) and str(n.get("id", "")).strip()
    }


def validate(registry: Any, note_status: dict[str, str], note_keys: dict[str, list[str]], canon_ids: set[str]) -> tuple[list[str], list[str], dict[str, Any]]:
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(registry, dict):
        return ["registry is not an object"], [], {}
    keys = registry.get("keys")
    if not isinstance(keys, list) or not keys:
        return ["registry has no keys list"], [], {}

    by_key: dict[str, dict[str, Any]] = {}
    alias_owner: dict[str, str] = {}
    for index, entry in enumerate(keys):
        if not isinstance(entry, dict):
            errors.append(f"keys[{index}] is not an object")
            continue
        key = str(entry.get("concept_key", "")).strip()
        if not key:
            errors.append(f"keys[{index}] has no concept_key")
            continue
        if not KEY_PATTERN.match(key):
            errors.append(f"{key}: not of the form ck.<domain>.<slug>")
        if key in by_key:
            errors.append(f"duplicate concept_key: {key}")
            continue
        by_key[key] = entry

        status = str(entry.get("status", "")).strip()
        if status not in VALID_STATUS:
            errors.append(f"{key}: status {status or '(empty)'} is not one of {sorted(VALID_STATUS)}")
        if not str(entry.get("definition", "")).strip():
            errors.append(f"{key}: no definition sentence, so it cannot disambiguate anything")
        if not str(entry.get("owner", "") or registry.get("owner", "")).strip():
            warnings.append(f"{key}: no owner")
        if status == "superseded" and not str(entry.get("superseded_by", "")).strip():
            errors.append(f"{key}: superseded with no successor named")

        for alias in entry.get("aliases") or []:
            alias_norm = str(alias).strip().lower()
            if not alias_norm:
                continue
            if alias_norm in alias_owner and alias_owner[alias_norm] != key:
                errors.append(f"alias {alias_norm!r} claimed by both {alias_owner[alias_norm]} and {key}")
            else:
                alias_owner[alias_norm] = key

    # Hierarchy edges must resolve, and must not loop.
    parent_edges: dict[str, list[str]] = {}
    for key, entry in by_key.items():
        parents = [str(x).strip() for x in (entry.get("parents") or [])]
        for parent in parents:
            if parent not in by_key:
                errors.append(f"{key}: parent {parent} is not registered")
        parent_edges[key] = [x for x in parents if x in by_key]
        for related in entry.get("related") or []:
            if str(related).strip() not in by_key:
                warnings.append(f"{key}: related {related} is not registered")
    for cycle in find_cycles(parent_edges):
        errors.append("parent cycle: " + " -> ".join(cycle))

    # Primary claims: exactly one note per key, and the note must be bound to it.
    primary_claims: dict[str, list[str]] = defaultdict(list)
    covered: list[str] = []
    keys_without_primary: list[str] = []
    unreviewed_primary: list[str] = []
    dangling_bindings: list[str] = []

    for key, entry in by_key.items():
        binds = entry.get("binds") or {}
        if not isinstance(binds, dict):
            errors.append(f"{key}: binds is not an object")
            binds = {}
        note_ids = [str(x).strip() for x in (binds.get("note_ids") or [])]
        if note_status:
            for note_id in note_ids:
                if note_id not in note_status:
                    dangling_bindings.append(f"{key} -> note {note_id}")
                    errors.append(f"{key}: bound note {note_id} is not in the corpus manifest")
        for canon_id in binds.get("canon_ids") or []:
            if canon_ids and str(canon_id).strip() not in canon_ids:
                warnings.append(f"{key}: canon id {canon_id} not found in the canon reference")

        primary = str(entry.get("primary_note_id", "")).strip()
        status = str(entry.get("status", "")).strip()
        if not primary:
            if status == "registered":
                keys_without_primary.append(key)
                warnings.append(f"{key}: registered with no primary note, so it counts as uncovered")
            continue
        primary_claims[primary].append(key)
        if note_ids and primary not in note_ids:
            errors.append(f"{key}: primary note {primary} is not among its bound note_ids")
        if note_status:
            actual = note_status.get(primary)
            if actual is None:
                errors.append(f"{key}: primary note {primary} is not in the corpus manifest")
            elif actual != COUNTABLE_NOTE_STATUS:
                unreviewed_primary.append(f"{key} ({primary} is {actual})")
                warnings.append(f"{key}: primary note {primary} is {actual}, not {COUNTABLE_NOTE_STATUS}; uncovered")
            elif status == "registered":
                covered.append(key)
        elif status == "registered":
            covered.append(key)

    # One note may be primary for several keys only if it genuinely teaches them; two keys
    # sharing a primary is reported so the choice is deliberate rather than accidental.
    duplicate_primary = [
        f"{note_id} is primary for {sorted(claim_keys)}"
        for note_id, claim_keys in primary_claims.items()
        if len(claim_keys) > 1
    ]
    for item in duplicate_primary:
        warnings.append(f"shared primary: {item}")

    # Binding to a proposed key is allowed, so duplicate coining is the risk that replaces it.
    # Cheap to fix while both are proposed; expensive once either carries registered bindings.
    near_duplicates: list[str] = []
    entries = sorted(by_key.items())
    for i, (left_key, left) in enumerate(entries):
        for right_key, right in entries[i + 1:]:
            if str(left.get("domain", "")).strip() != str(right.get("domain", "")).strip():
                continue
            if "proposed" not in {str(left.get("status", "")), str(right.get("status", ""))}:
                continue
            name_sim = SequenceMatcher(
                None,
                str(left.get("display_name", "")).lower(),
                str(right.get("display_name", "")).lower(),
            ).ratio()
            def_sim = SequenceMatcher(
                None,
                str(left.get("definition", "")).lower(),
                str(right.get("definition", "")).lower(),
            ).ratio()
            if name_sim >= NAME_SIMILARITY_THRESHOLD or def_sim >= DEFINITION_SIMILARITY_THRESHOLD:
                near_duplicates.append(
                    f"{left_key} ~ {right_key} (name {name_sim:.0%}, definition {def_sim:.0%})"
                )
    for item in near_duplicates:
        warnings.append(f"possible duplicate key: {item}")

    # The reverse direction: a note claiming a key the registry never heard of.
    unregistered_in_use: list[str] = []
    for note_id, keys_claimed in note_keys.items():
        for key in keys_claimed:
            if key and key not in by_key:
                unregistered_in_use.append(f"{note_id} -> {key}")
                errors.append(f"note {note_id} binds to unregistered key {key}")

    registered = [k for k, e in by_key.items() if str(e.get("status", "")) == "registered"]
    bound_canon = {
        str(c).strip()
        for e in by_key.values()
        for c in ((e.get("binds") or {}).get("canon_ids") or [])
        if str(c).strip()
    }
    canon_without_key = sorted(canon_ids - bound_canon) if canon_ids else []
    for canon_id in canon_without_key:
        warnings.append(f"canon id {canon_id} has no registered key")

    summary = {
        "registry_id": registry.get("registry_id", ""),
        "keys_total": len(by_key),
        "keys_registered": len(registered),
        "keys_covered": len(covered),
        "coverage": round(len(covered) / len(registered), 4) if registered else 0.0,
        "keys_without_primary": keys_without_primary,
        "primary_not_reviewed": unreviewed_primary,
        "shared_primary": duplicate_primary,
        "dangling_bindings": dangling_bindings,
        "canon_ids_without_key": canon_without_key,
        "near_duplicate_keys": near_duplicates,
        "unregistered_keys_in_use": unregistered_in_use,
        "keys_proposed": len([k for k, e in by_key.items() if str(e.get("status", "")) == "proposed"]),
        "errors": len(errors),
        "warnings": len(warnings),
    }
    return errors, warnings, summary


def read_canon_ids(path: Path) -> set[str]:
    """Pull sd.* IDs out of the canon reference; a missing file simply disables the check."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return set()
    return set(re.findall(r"`(sd\.[a-z0-9.-]+)`", text))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("registry", type=Path, help="concept-registry.json")
    parser.add_argument("--corpus-manifest", type=Path, help="note-corpus-manifest.json to resolve note bindings")
    parser.add_argument("--canon", type=Path, help="system-design-canon.md to check canon bindings against")
    parser.add_argument("--strict", action="store_true", help="treat warnings as failures")
    parser.add_argument("--report-out", type=Path)
    args = parser.parse_args()

    try:
        registry = load(args.registry)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"ERROR: unreadable registry: {exc}")
        sys.exit(1)

    note_status: dict[str, str] = {}
    note_keys: dict[str, list[str]] = {}
    if args.corpus_manifest is not None:
        try:
            corpus = load(args.corpus_manifest)
            note_status = collect_note_status(corpus)
            note_keys = collect_note_keys(corpus)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            print(f"ERROR: unreadable corpus manifest: {exc}")
            sys.exit(1)
        if not note_status:
            print("WARNING: corpus manifest has no readable notes; note bindings unchecked")

    canon_ids = read_canon_ids(args.canon) if args.canon is not None else set()

    errors, warnings, summary = validate(registry, note_status, note_keys, canon_ids)
    for error in errors:
        print(f"ERROR: {error}")
    for warning in warnings:
        print(f"WARNING: {warning}")

    if summary:
        print(
            f"keys: {summary['keys_total']}  registered: {summary['keys_registered']}  "
            f"proposed: {summary['keys_proposed']}  "
            f"covered: {summary['keys_covered']}  coverage: {summary['coverage']:.0%}"
        )
    if args.report_out is not None and summary:
        args.report_out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"report written: {args.report_out}")

    if errors:
        print(f"FAILED: {len(errors)} registry error(s)")
        sys.exit(1)
    if warnings and args.strict:
        print(f"FAILED: {len(warnings)} warning(s) under --strict")
        sys.exit(1)
    if warnings:
        print(f"PASS WITH WARNINGS: {len(warnings)} item(s) to resolve before citing a coverage number")
        sys.exit(0)
    print("PASS: the crosswalk resolves; this says nothing about whether the concepts are well chosen")


if __name__ == "__main__":
    main()
