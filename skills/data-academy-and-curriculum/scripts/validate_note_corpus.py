#!/usr/bin/env python3
"""Check a note corpus for the structural faults that only appear at scale.

A single note can be reviewed by reading it. A corpus of two hundred cannot, and the failures
that matter there are relational rather than editorial: an ID claimed twice, a `builds_on` edge
pointing at a note nobody ever wrote, a prerequisite cycle that makes the reading order
impossible, a note planned months ago and quietly never built, a file on disk that no manifest
entry knows about. Each is cheap to find mechanically and expensive to find by reading.

It also reports near-duplicate candidates by tag overlap, because the rule of extending an
existing note instead of creating a twin cannot be applied by hand once the corpus is large.

It also flags a short list of filler phrasings, always as warnings and never as failures, because
style is a judgment a regular expression does not get to make.

It reads structure. It cannot tell whether a note is correct, well written, pitched at the right
level, or worth keeping; a corpus can pass every check here and still teach the wrong things.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path
from typing import Any

VALID_STATUS = {"planned", "drafted", "reviewed", "stale"}
BUILT_STATUS = {"drafted", "reviewed"}
# Overlap above this share of the smaller tag set is reported as a possible duplicate.
TAG_OVERLAP_THRESHOLD = 0.70
STALE_AFTER_DAYS = 183

REQUIRED_HEADINGS = [
    "## Nỗi Đau & Động Lực",
    "## Cơ Chế Tác Động",
    "## Bản Đồ Quyết Định",
    "## Góc Khuất & Ngộ Nhận",
    "## Tự Kiểm Tra Nhanh",
]
CASE_STUDY_PREFIX = "## Case Study Thực Chiến:"
PITCH_MARKER = "**Tóm tắt bản chất:**"

# Phrasings that are almost always connective filler in explanatory prose. Each is reported with
# what replaces it, because a bare ban list produces avoidance rather than better writing. These
# are warnings at every note status: style is judgment, and a checker gets a vote, not a veto.
PROSE_TELLS = [
    (r"[Tt]rong (thế giới|bối cảnh|kỷ nguyên)[^.]{0,40}(ngày nay|hiện nay)", "scene-setting opener; lead with the claim"),
    (r"[Ii]n today'?s [a-z ]{0,30}(world|landscape|era)", "scene-setting opener; lead with the claim"),
    (r"[Kk]hông chỉ [^.]{1,60} mà còn", "'không chỉ … mà còn'; split it or cut the weaker half"),
    (r"\bnot only\b[^.]{1,60}\bbut also\b", "'not only … but also'; split it or cut the weaker half"),
    (r"[Đđ]iều (quan trọng|đáng) (cần )?(lưu ý|chú ý) là", "delete the frame, keep the noting"),
    (r"[Ii]t'?s worth noting that", "delete the frame, keep the noting"),
    (r"([Bb]ài viết|[Pp]hần|[Nn]ote) này sẽ (trình bày|giới thiệu|đề cập|khám phá)", "structure announcement; the headings already do this"),
    (r"[Ll]et'?s (explore|dive|take a look)", "structure announcement; the headings already do this"),
    (r"[Tt]óm lại,? (có thể thấy|ta thấy|chúng ta)", "closing recap; end on the consequence or next decision"),
    (r"[Hh]ãy cùng (tìm hiểu|khám phá|đi sâu)", "structure announcement; the headings already do this"),
]
# One hedge is precision; three stacked is avoidance.
HEDGE_WORDS = r"(có thể|có lẽ|thường|đôi khi|dường như|khá là|might|maybe|possibly|potentially|somewhat)"
EM_DASH_PER_1000_LIMIT = 4.0
# Uniform sentence length is the strongest structural tell of generated prose, and unlike a word
# list it cannot be evaded by swapping vocabulary. Calibrated against 260 documents of this repo's
# own prose, whose coefficient of variation runs 0.32 to 0.66; the floor sits below the most even
# of them so real writing is never flagged.
SENTENCE_VARIATION_FLOOR = 0.29
MIN_SENTENCES_FOR_VARIATION = 12
# Intensifiers that sound concrete and cannot be checked.
UNFALSIFIABLE = (
    r"\b(đáng kể|rất nhiều|vô cùng|hàng loạt|tối ưu hơn nhiều)\b",
    r"\b(significantly|substantially|a wide range of|a variety of|greatly improves)\b",
)
# Balanced construction where reality is usually lopsided.
SYMMETRY = (r"\b(mặt khác|một mặt.{0,40}mặt khác)\b", r"\bon the one hand\b.{0,80}\bon the other hand\b")


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_date(value: str) -> date | None:
    try:
        return datetime.strptime(value.strip(), "%Y-%m-%d").date()
    except (ValueError, AttributeError):
        return None


def find_cycles(edges: dict[str, list[str]]) -> list[list[str]]:
    """Depth-first search for prerequisite cycles; no reading order exists inside one."""
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


def section_body(text: str, heading: str) -> str:
    """Text between a heading and the next one, so an empty section is distinguishable."""
    start = text.find(heading)
    if start == -1:
        return ""
    start += len(heading)
    nxt = re.search(r"^## ", text[start:], re.MULTILINE)
    body = text[start:start + nxt.start()] if nxt else text[start:]
    return body.strip()


def check_prose_tells(text: str) -> list[str]:
    """Filler phrasings a structural check cannot see. Advisory only, never a failure."""
    tells: list[str] = []
    body = text.split("---\n", 2)[-1] if text.startswith("---\n") else text
    # Tables and headings legitimately carry dashes and have no sentence terminators, so a run
    # of table rows would otherwise read as one enormous sentence.
    prose_only = "\n".join(
        line for line in body.splitlines()
        if not line.lstrip().startswith(("|", "#"))
    )
    # A bulleted list is uniform by design and says nothing about prose rhythm; measuring its
    # variation measures the list format. Sentence statistics run on paragraphs only.
    paragraphs_only = "\n".join(
        line for line in body.splitlines()
        if not line.lstrip().startswith(("|", "#", "-", "*", ">"))
        and not re.match(r"^\s*\d+[.)]\s", line)
    )
    for pattern, advice in PROSE_TELLS:
        found = re.search(pattern, body)
        if found:
            tells.append(f"prose: {found.group(0).strip()!r} — {advice}")

    prose_chars = len(re.sub(r"```.*?```", "", prose_only, flags=re.DOTALL))
    dashes = prose_only.count("—")
    if prose_chars > 400 and dashes / (prose_chars / 1000) > EM_DASH_PER_1000_LIMIT:
        tells.append(
            f"prose: {dashes} em dashes in {prose_chars} chars; vary the clause breaks"
        )

    # Density over a whole note misses the pattern that actually reads badly: one sentence
    # strung together entirely on dashes.
    for sentence in re.split(r"(?<=[.!?])\s+|\n", prose_only):
        if sentence.count("—") >= 3:
            tells.append(f"prose: {sentence.count('—')} em dashes in one sentence — {sentence.strip()[:60]!r}")
            break

    for sentence in re.split(r"(?<=[.!?])\s+|\n", prose_only):
        if len(re.findall(HEDGE_WORDS, sentence, re.IGNORECASE)) >= 3:
            tells.append(f"prose: three hedges in one sentence — {sentence.strip()[:70]!r}")
            break

    for pattern in UNFALSIFIABLE:
        found = re.search(pattern, prose_only, re.IGNORECASE)
        if found:
            tells.append(f"prose: {found.group(0)!r} sounds concrete and cannot be checked — give a number, a version or a case")
            break
    for pattern in SYMMETRY:
        if re.search(pattern, prose_only, re.IGNORECASE | re.DOTALL):
            tells.append("prose: balanced two-handed construction; most trade-offs have a side that usually wins — say which, and the condition where it does not")
            break

    # Length variation, measured rather than judged.
    lengths = [
        len(s.split()) for s in re.split(r"(?<=[.!?])\s+", paragraphs_only)
        if len(s.split()) >= 4
    ]
    if len(lengths) >= MIN_SENTENCES_FOR_VARIATION:
        mean = sum(lengths) / len(lengths)
        variance = sum((x - mean) ** 2 for x in lengths) / (len(lengths) - 1)
        cv = (variance ** 0.5) / mean if mean else 0
        if cv < SENTENCE_VARIATION_FLOOR:
            tells.append(
                f"prose: sentence lengths vary by {cv:.2f}, below {SENTENCE_VARIATION_FLOOR} — "
                "let each point take the space it needs rather than adding variation for its own sake"
            )
    return tells


def check_note_file(path: Path) -> list[str]:
    """Structural faults inside one note file, not a judgment about its content."""
    faults: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return [f"unreadable: {exc}"]

    if not text.startswith("---\n"):
        faults.append("no YAML front matter")
    else:
        front = text.split("---\n", 2)[1] if text.count("---\n") >= 2 else ""
        for field in ("id:", "ai_summary:", "relationships:", "version_sensitive:"):
            if not re.search(rf"^{re.escape(field)}", front, re.MULTILINE):
                faults.append(f"front matter has no {field.rstrip(':')}")
        summary = re.search(r"^ai_summary:\s*(.*)$", front, re.MULTILINE)
        if summary and not summary.group(1).strip().strip('"\''):
            faults.append("ai_summary is empty")
    if PITCH_MARKER not in text:
        faults.append(f"missing `{PITCH_MARKER}` line")
    for heading in REQUIRED_HEADINGS:
        if heading not in text:
            faults.append(f"missing heading `{heading}`")
    if CASE_STUDY_PREFIX not in text:
        faults.append(f"missing heading `{CASE_STUDY_PREFIX} <situation>`")
    if "## Tự Kiểm Tra Nhanh" in text and "<details>" not in text:
        faults.append("self-check answers are not wrapped in <details>")

    # A heading that is present but empty passes a presence check and teaches nothing.
    decision = section_body(text, "## Bản Đồ Quyết Định")
    if "## Bản Đồ Quyết Định" in text:
        rows = [
            line for line in decision.splitlines()
            if line.strip().startswith("|") and not re.match(r"^\s*\|[\s|:-]+\|\s*$", line)
        ]
        # header row plus at least one case; a table with only a header decides nothing.
        if len(rows) < 2 and "- " not in decision:
            faults.append("decision map has no cases, only a heading or an empty table")
    misc = section_body(text, "## Góc Khuất & Ngộ Nhận")
    if "## Góc Khuất & Ngộ Nhận" in text and misc.count("**Hiểu lầm:**") < 2:
        faults.append(f"fewer than 2 misconception entries ({misc.count('**Hiểu lầm:**')} found)")
    check = section_body(text, "## Tự Kiểm Tra Nhanh")
    if "## Tự Kiểm Tra Nhanh" in text:
        if check.count("<details>") < 2:
            faults.append(f"fewer than 2 self-check questions ({check.count('<details>')} found)")
        if re.search(r"<details>\s*<summary>[^<]*</summary>\s*</details>", check):
            faults.append("a self-check answer is empty")
    case_heading = next((line for line in text.splitlines() if line.startswith(CASE_STUDY_PREFIX)), None)
    if case_heading and len(section_body(text, case_heading)) < 40:
        faults.append("case study section is empty or a stub")
    pitch = ""
    if PITCH_MARKER in text:
        pitch = text.split(PITCH_MARKER, 1)[1].split("\n\n", 1)[0].strip()
        if len(pitch) < 30:
            faults.append("elevator pitch is a stub")
    # Bracket labels are the pattern the fixed-phrase headings exist to replace.
    if re.search(r"^#{1,6}\s*\[(L\d|Reason|Operation|Options|Thread)\]", text, re.MULTILINE):
        faults.append("uses a bracket label heading instead of a fixed phrase")
    return faults


def validate(manifest: Any, note_root: Path | None) -> tuple[list[str], list[str], dict[str, Any]]:
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(manifest, dict):
        return ["manifest is not an object"], [], {}
    notes = manifest.get("notes")
    if not isinstance(notes, list) or not notes:
        return ["manifest has no notes list"], [], {}

    by_id: dict[str, dict[str, Any]] = {}
    for index, note in enumerate(notes):
        if not isinstance(note, dict):
            errors.append(f"notes[{index}] is not an object")
            continue
        note_id = str(note.get("id", "")).strip()
        if not note_id:
            errors.append(f"notes[{index}] has no id")
            continue
        if note_id in by_id:
            errors.append(f"duplicate note id: {note_id}")
            continue
        status = str(note.get("status", "")).strip()
        if status not in VALID_STATUS:
            errors.append(f"{note_id}: status {status or '(empty)'} is not one of {sorted(VALID_STATUS)}")
        by_id[note_id] = note

    # Relationship edges must land on a note that at least exists as a plan.
    prereq_edges: dict[str, list[str]] = {}
    for note_id, note in by_id.items():
        for field in ("builds_on", "prerequisite_of"):
            targets = note.get(field) or []
            if not isinstance(targets, list):
                errors.append(f"{note_id}: {field} is not a list")
                continue
            for target in targets:
                if str(target).strip() not in by_id:
                    errors.append(f"{note_id}: {field} points at unknown id {target}")
        if not (note.get("builds_on") or note.get("prerequisite_of")):
            warnings.append(f"{note_id}: no builds_on or prerequisite_of edge")
        prereq_edges[note_id] = [
            str(t).strip() for t in (note.get("builds_on") or []) if str(t).strip() in by_id
        ]

    for cycle in find_cycles(prereq_edges):
        errors.append("prerequisite cycle: " + " -> ".join(cycle))

    # Near-duplicates, resolved before writing rather than discovered later.
    tagged = [(nid, {str(t).strip().lower() for t in (n.get("tags") or [])}) for nid, n in by_id.items()]
    duplicate_candidates: list[str] = []
    for i, (left_id, left) in enumerate(tagged):
        for right_id, right in tagged[i + 1:]:
            if len(left) < 2 or len(right) < 2:
                continue
            overlap = len(left & right) / min(len(left), len(right))
            if overlap >= TAG_OVERLAP_THRESHOLD:
                duplicate_candidates.append(f"{left_id} ~ {right_id} ({overlap:.0%} tag overlap)")
    for candidate in duplicate_candidates:
        warnings.append(f"possible duplicate: {candidate}")

    # Staleness applies only where the note itself declared it could go out of date.
    today = date.today()
    stale_notes: list[str] = []
    for note_id, note in by_id.items():
        if not note.get("version_sensitive"):
            continue
        updated = parse_date(str(note.get("updated", "")))
        if updated is None:
            warnings.append(f"{note_id}: version_sensitive with no readable updated date")
            continue
        age = (today - updated).days
        if age > STALE_AFTER_DAYS:
            stale_notes.append(f"{note_id} ({age} days)")
            warnings.append(f"{note_id}: version_sensitive and last updated {age} days ago")

    planned_missing: list[str] = []
    unmanifested: list[str] = []
    file_faults: dict[str, list[str]] = {}
    if note_root is not None:
        if not note_root.is_dir():
            errors.append(f"note root is not a directory: {note_root}")
        else:
            declared: set[Path] = set()
            for note_id, note in by_id.items():
                rel = str(note.get("path", "")).strip()
                status = str(note.get("status", "")).strip()
                if not rel:
                    if status in BUILT_STATUS:
                        errors.append(f"{note_id}: status {status} but no path")
                    continue
                kind = str(note.get("kind", "deep-dive")).strip() or "deep-dive"
                target = (note_root / rel).resolve()
                declared.add(target)
                if status in BUILT_STATUS and not target.is_file():
                    planned_missing.append(note_id)
                    errors.append(f"{note_id}: status {status} but no file at {rel}")
                elif target.is_file() and kind == "reference":
                    # The authoring standard requires a canonical location for a running example's
                    # schema, and such a file is not a deep dive. Checking it against the deep-dive
                    # headings reported six missing sections for a file that must not have them.
                    for tell in check_prose_tells(target.read_text(encoding="utf-8")):
                        warnings.append(f"{note_id}: {tell}")
                elif target.is_file():
                    faults = check_note_file(target)
                    if faults:
                        file_faults[note_id] = faults
                        for fault in faults:
                            (errors if status == "reviewed" else warnings).append(f"{note_id}: {fault}")
                    for tell in check_prose_tells(target.read_text(encoding="utf-8")):
                        warnings.append(f"{note_id}: {tell}")
            for found in sorted(note_root.rglob("*.md")):
                if found.resolve() not in declared:
                    unmanifested.append(str(found.relative_to(note_root)))
                    warnings.append(f"file not in manifest: {found.relative_to(note_root)}")

    built = [n for n in by_id.values() if str(n.get("status", "")) in BUILT_STATUS]
    reviewed = [n for n in by_id.values() if str(n.get("status", "")) == "reviewed"]
    # Supporting files belong to no module; counting them made a corpus of five modules report six.
    deep_dives = [n for n in by_id.values() if str(n.get("kind", "deep-dive")) != "reference"]
    modules = {str(n.get("module_id", "")).strip() for n in deep_dives if n.get("module_id")}
    modules_done = {
        module
        for module in modules
        if all(
            str(n.get("status", "")) in BUILT_STATUS
            for n in deep_dives
            if str(n.get("module_id", "")).strip() == module
        )
    }
    summary = {
        "corpus_id": manifest.get("corpus_id", ""),
        "notes_planned": len(by_id),
        "notes_built": len(built),
        "notes_reviewed": len(reviewed),
        "modules": len(modules),
        "modules_complete": len(modules_done),
        "build_coverage": round(len(built) / len(by_id), 4) if by_id else 0.0,
        "review_coverage": round(len(reviewed) / len(by_id), 4) if by_id else 0.0,
        "duplicate_candidates": duplicate_candidates,
        "stale_notes": stale_notes,
        "planned_missing_files": planned_missing,
        "files_not_in_manifest": unmanifested,
        "note_faults": file_faults,
        "errors": len(errors),
        "warnings": len(warnings),
    }
    return errors, warnings, summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, help="note-corpus-manifest.json")
    parser.add_argument("--note-root", type=Path, help="directory the manifest paths are relative to")
    parser.add_argument("--strict", action="store_true", help="treat warnings as failures")
    parser.add_argument("--report-out", type=Path)
    args = parser.parse_args()

    try:
        manifest = load(args.manifest)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: unreadable manifest: {exc}")
        sys.exit(1)

    errors, warnings, summary = validate(manifest, args.note_root)
    for error in errors:
        print(f"ERROR: {error}")
    for warning in warnings:
        print(f"WARNING: {warning}")

    if summary:
        print(
            f"notes: {summary['notes_planned']}  built: {summary['notes_built']}  "
            f"reviewed: {summary['notes_reviewed']}  modules complete: "
            f"{summary['modules_complete']}/{summary['modules']}  "
            f"build coverage: {summary['build_coverage']:.0%}"
        )
    if args.report_out is not None and summary:
        args.report_out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"report written: {args.report_out}")

    if errors:
        print(f"FAILED: {len(errors)} corpus error(s)")
        sys.exit(1)
    if warnings and args.strict:
        print(f"FAILED: {len(warnings)} warning(s) under --strict")
        sys.exit(1)
    if warnings:
        print(f"PASS WITH WARNINGS: {len(warnings)} item(s) to resolve before the corpus is cited as complete")
        sys.exit(0)
    print("PASS: structure is sound; this says nothing about whether the notes are any good")


if __name__ == "__main__":
    main()
