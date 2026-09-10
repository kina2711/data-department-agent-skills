#!/usr/bin/env python3
"""Write a captured source and its distilled notes into a local vault as one reversible operation.

The chain that produces the content already exists as atomic tasks: capture the source, normalize
its metadata, distill it into a Wiki note, split out atomic notes, link the graph. What was missing
is the last step -- getting the result into the vault without a half-finished write.

Two phases, because a vault is somebody's own work and a partial write is worse than no write:

    plan   read every target, hash what is already there, and print exactly what would change
    apply  re-read those targets, refuse if anything moved since the plan, then write all or none

The plan carries a digest over the target paths and their current hashes. Apply recomputes it and
stops when it differs, so an edit made in Obsidian between planning and applying aborts the write
instead of silently overwriting it. Files that already exist are backed up into a journal directory
before being replaced, and any failure mid-way restores every file the run had touched.

Reads a bundle on stdin or from --bundle:

    {"source": {...source-record fields...},
     "notes": [{...wiki-note fields...}, ...]}

Field names follow assets/source-record.yaml and assets/wiki-note.yaml. Standard library only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import unicodedata
import tempfile
from datetime import datetime, timezone
from pathlib import Path

SOURCE_LAYER = "1_Nguon"
WIKI_LAYER = "2_Wiki"
JOURNAL = ".dd-journal"

# A vault is identified by its layers, not by a marker file, so an existing four-layer vault works
# without being adopted first.
REQUIRED_LAYERS = (SOURCE_LAYER, WIKI_LAYER)


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    """Hash of a file, or the empty marker when it does not exist yet."""
    if not path.exists():
        return ""
    return sha256_bytes(path.read_bytes())


def slug(text: str, fallback: str = "khong-ten") -> str:
    """A filename that stays readable in a file manager and stable across runs.

    Normalised to NFC first. Vietnamese text can arrive composed or decomposed, and the two forms
    look identical while comparing unequal -- an id written in one form and linked in the other is
    a dead wikilink that nothing in the file reveals.
    """
    text = unicodedata.normalize("NFC", (text or "")).strip().lower()
    # Keep Vietnamese words legible rather than stripping to ASCII: the vault is read by a person.
    text = re.sub(r"[\s/\\]+", "-", text)
    text = re.sub(r"[^0-9a-zA-Zà-ỹÀ-ỸđĐ_-]+", "", text)
    text = re.sub(r"-{2,}", "-", text).strip("-")
    return text[:80] or fallback


def yaml_scalar(value) -> str:
    if value is None:
        return '""'
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    text = str(value)
    if text == "" or re.search(r'[:#\[\]{}",\n]', text) or text.strip() != text:
        return json.dumps(text, ensure_ascii=False)
    return text


def yaml_block(data: dict, indent: int = 0) -> list[str]:
    """Enough YAML for frontmatter. Not a general emitter -- it covers scalars, lists and maps."""
    pad = " " * indent
    lines: list[str] = []
    for key, value in data.items():
        if isinstance(value, dict):
            if not value:
                lines.append(f"{pad}{key}: {{}}")
                continue
            lines.append(f"{pad}{key}:")
            lines.extend(yaml_block(value, indent + 2))
        elif isinstance(value, (list, tuple)):
            if not value:
                lines.append(f"{pad}{key}: []")
                continue
            lines.append(f"{pad}{key}:")
            for item in value:
                if isinstance(item, dict):
                    inner = yaml_block(item, indent + 4)
                    inner[0] = f"{pad}  - " + inner[0].lstrip()
                    lines.extend(inner)
                else:
                    lines.append(f"{pad}  - {yaml_scalar(item)}")
        else:
            lines.append(f"{pad}{key}: {yaml_scalar(value)}")
    return lines


def frontmatter(data: dict) -> str:
    return "---\n" + "\n".join(yaml_block(data)) + "\n---\n"


def bullets(title: str, items, known_ids: set[str] | None = None) -> str:
    """A section, or nothing. An empty heading reads as an answered question that was not."""
    if not items:
        return ""
    lines = [f"## {title}", ""]
    for item in items:
        if isinstance(item, dict):
            claim = item.get("claim") or item.get("text") or json.dumps(item, ensure_ascii=False)
            locator = item.get("locator") or ""
            source_id = item.get("source_id") or ""
            # A claim without a locator is still a claim; the citation is appended when there is one.
            # Only link an id this bundle actually writes. A [[link]] to an id that does not
            # exist looks like a citation and resolves to nothing, which is worse than plain text
            # because the reader believes there is a source behind it.
            source_id = unicodedata.normalize("NFC", source_id)
            linkable = known_ids is not None and source_id in known_ids
            shown = f"[[{source_id}]]" if linkable else source_id
            cite = ""
            if source_id and locator:
                cite = f" ({shown} — {locator})"
            elif source_id:
                cite = f" ({shown})"
            elif locator:
                cite = f" ({locator})"
            lines.append(f"- {claim}{cite}")
        else:
            lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines) + "\n"


def render_source(source: dict) -> str:
    meta = {
        "source_id": source.get("source_id", ""),
        "title": source.get("title", ""),
        "source_type": source.get("source_type", ""),
        "origin": source.get("origin", ""),
        "author_or_owner": source.get("author_or_owner", ""),
        "captured_at": source.get("captured_at") or now(),
        "canonical_locator": source.get("canonical_locator", ""),
        "snapshot_path": source.get("snapshot_path", ""),
        "content_sha256": source.get("content_sha256", ""),
        "rights": source.get("rights", {"ownership": "unknown", "processing_allowed": "unknown"}),
        "sensitivity": source.get("sensitivity", "private"),
        "authority": source.get("authority", "unknown"),
        "status": source.get("status", "captured"),
        "tags": source.get("tags", []),
    }
    body = [frontmatter(meta), f"# {source.get('title') or source.get('source_id') or 'Nguồn'}\n"]
    locator = source.get("canonical_locator")
    if locator:
        body.append(f"Nguồn gốc: <{locator}>\n")
    if source.get("summary"):
        body.append(f"\n{source['summary']}\n")
    body.append(bullets("Giới hạn của nguồn", source.get("limitations")))
    # An empty snapshot is a fact about the record, not a detail to leave the reader guessing at.
    if not source.get("snapshot_path"):
        body.append("\n> Chưa có snapshot cục bộ. Nội dung có thể đổi hoặc biến mất ở đầu nguồn.\n")
    return "".join(body)


def render_note(note: dict, source_id: str) -> str:
    known = {source_id}
    meta = {
        "note_id": note.get("note_id", ""),
        "title": note.get("title", ""),
        "note_type": note.get("note_type", "concept"),
        "aliases": note.get("aliases", []),
        "status": note.get("status", "draft"),
        "source_ids": note.get("source_ids") or ([source_id] if source_id else []),
        "related_note_ids": note.get("related_note_ids", []),
        "last_verified_at": note.get("last_verified_at", ""),
        "tags": note.get("tags", []),
    }
    parts = [frontmatter(meta), f"# {note.get('title') or note.get('note_id') or 'Note'}\n\n"]
    # The four sections stay separate on purpose: what the source said, what was worked out from it,
    # what was guessed, and what is still open. Merged, a guess reads like a quotation.
    parts.append(bullets("Nguồn nói gì", note.get("source_facts"), known))
    parts.append(bullets("Tổng hợp", note.get("synthesis")))
    parts.append(bullets("Suy luận (chưa có trong nguồn)", note.get("inferences")))
    parts.append(bullets("Còn chưa chắc", note.get("uncertainties")))
    parts.append(bullets("Mâu thuẫn", note.get("conflicts")))
    parts.append(bullets("Dùng được vào đâu", note.get("applications")))
    links = note.get("related_note_ids") or []
    if links:
        parts.append("## Liên quan\n\n" + "".join(f"- [[{x}]]\n" for x in links) + "\n")
    if source_id:
        parts.append(f"\nNguồn: [[{source_id}]]\n")
    return "".join(parts)


def targets_for(bundle: dict, vault: Path) -> list[tuple[Path, str]]:
    """Every file the bundle would write, as (path, content). Order is stable for hashing."""
    source = bundle.get("source") or {}
    source_id = source.get("source_id") or slug(source.get("title", ""), "nguon")
    source["source_id"] = source_id

    out: list[tuple[Path, str]] = []
    out.append((vault / SOURCE_LAYER / filename(source_id, source.get("title", "")), render_source(source)))

    for note in bundle.get("notes") or []:
        note_id = note.get("note_id") or slug(note.get("title", ""), "note")
        note["note_id"] = note_id
        out.append((vault / WIKI_LAYER / filename(note_id, note.get("title", "")), render_note(note, source_id)))

    return out


def filename(item_id: str, title: str) -> str:
    """`id--title.md`, or just `id.md` when the id was derived from that same title."""
    tail = slug(title, "")
    return f"{item_id}--{tail}.md" if tail and tail != item_id else f"{item_id}.md"


def plan_for(bundle: dict, vault: Path) -> dict:
    entries = []
    for path, content in targets_for(bundle, vault):
        before = sha256_file(path)
        after = sha256_bytes(content.encode("utf-8"))
        entries.append({
            "path": str(path.relative_to(vault)),
            "action": "overwrite" if before else "create",
            "unchanged": before == after,
            "sha256_before": before,
            "sha256_after": after,
        })
    digest = sha256_bytes(
        json.dumps([(e["path"], e["sha256_before"]) for e in entries], ensure_ascii=False).encode("utf-8")
    )
    return {
        "vault": str(vault),
        "planned_at": now(),
        "expect": digest,
        "files": entries,
        "overwrites": [e["path"] for e in entries if e["action"] == "overwrite" and not e["unchanged"]],
    }


def check_vault(vault: Path, allow_init: bool) -> None:
    missing = [layer for layer in REQUIRED_LAYERS if not (vault / layer).is_dir()]
    if not missing:
        return
    if not allow_init:
        raise SystemExit(
            f"{vault} thiếu {', '.join(missing)}. Đây có thể không phải vault bốn lớp — "
            "chạy lại với --init nếu thật sự muốn tạo mới."
        )
    for layer in missing:
        (vault / layer).mkdir(parents=True, exist_ok=True)


def apply_bundle(bundle: dict, vault: Path, expect: str | None) -> dict:
    plan = plan_for(bundle, vault)
    if expect and expect != plan["expect"]:
        raise SystemExit(
            "Vault đã đổi kể từ lúc lập plan — không ghi đè. "
            f"Plan chờ {expect[:12]}…, hiện tại {plan['expect'][:12]}…. Lập plan lại rồi xem diff."
        )

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    journal = vault / JOURNAL / stamp
    journal.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    restored: list[tuple[Path, Path]] = []

    try:
        for path, content in targets_for(bundle, vault):
            path.parent.mkdir(parents=True, exist_ok=True)
            if path.exists():
                backup = journal / path.relative_to(vault)
                backup.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, backup)
                restored.append((path, backup))
            # Write beside the target and rename: a reader never sees a half-written note.
            tmp = tempfile.NamedTemporaryFile(
                "w", encoding="utf-8", dir=path.parent, prefix=".dd-", suffix=".tmp", delete=False
            )
            with tmp as handle:
                handle.write(content)
            os.replace(tmp.name, path)
            written.append(path)
    except Exception as err:  # noqa: BLE001 -- any failure must leave the vault as it was
        for path in written:
            path.unlink(missing_ok=True)
        for path, backup in restored:
            shutil.copy2(backup, path)
        raise SystemExit(f"Ghi thất bại, đã hoàn nguyên vault: {err}") from err

    (journal / "manifest.json").write_text(
        json.dumps({"plan": plan, "written": [str(p) for p in written]}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return {
        "ok": True,
        "vault": str(vault),
        "written": [str(p.relative_to(vault)) for p in written],
        "journal": str(journal.relative_to(vault)),
        "expect": plan["expect"],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--vault", required=True, type=Path, help="thư mục vault (chứa 1_Nguon, 2_Wiki)")
    ap.add_argument("--bundle", type=Path, help="file JSON; mặc định đọc stdin")
    ap.add_argument("--apply", action="store_true", help="ghi thật; mặc định chỉ lập plan")
    ap.add_argument("--expect", help="digest từ plan trước đó; apply sẽ dừng nếu vault đã đổi")
    ap.add_argument("--init", action="store_true", help="tạo các lớp còn thiếu thay vì dừng")
    args = ap.parse_args()

    raw = args.bundle.read_text(encoding="utf-8") if args.bundle else sys.stdin.read()
    try:
        bundle = json.loads(raw)
    except json.JSONDecodeError as err:
        print(f"bundle không phải JSON hợp lệ: {err}", file=sys.stderr)
        return 2
    if not isinstance(bundle, dict) or not bundle.get("source"):
        print("bundle cần có khóa 'source'; 'notes' là danh sách Wiki note.", file=sys.stderr)
        return 2

    vault = args.vault.expanduser().resolve()
    check_vault(vault, allow_init=args.init)

    if args.apply:
        result = apply_bundle(bundle, vault, args.expect)
    else:
        result = plan_for(bundle, vault)
        result["note"] = "Chưa ghi gì. Xem lại rồi chạy --apply --expect <expect> để ghi."

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
