#!/usr/bin/env python3
"""Extract supported local documents into a bounded corpus and source metadata."""

from __future__ import annotations

import argparse
import glob
import hashlib
import html
from html.parser import HTMLParser
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

SUPPORTED = {".pdf", ".epub", ".docx", ".html", ".htm", ".md", ".markdown", ".txt", ".rst", ".adoc", ".rtf"}
MAX_SOURCE_BYTES = 250 * 1024 * 1024
MAX_ZIP_MEMBER_BYTES = 50 * 1024 * 1024
MAX_ZIP_TOTAL_BYTES = 300 * 1024 * 1024


class TextHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() in {"h1", "h2", "h3", "h4", "p", "li", "br", "pre", "tr"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        self.parts.append(data)

    def text(self) -> str:
        return re.sub(r"\n{3,}", "\n\n", html.unescape("".join(self.parts))).strip()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_zip_members(archive: zipfile.ZipFile) -> list[zipfile.ZipInfo]:
    members = archive.infolist()
    total = sum(item.file_size for item in members)
    if total > MAX_ZIP_TOTAL_BYTES:
        raise ValueError(f"archive expands beyond {MAX_ZIP_TOTAL_BYTES} bytes")
    for item in members:
        if item.file_size > MAX_ZIP_MEMBER_BYTES:
            raise ValueError(f"archive member too large: {item.filename}")
        normalized = Path(item.filename.replace("\\", "/"))
        if normalized.is_absolute() or ".." in normalized.parts:
            raise ValueError(f"unsafe archive path: {item.filename}")
    return members


def html_to_text(raw: str) -> str:
    parser = TextHTMLParser()
    parser.feed(raw)
    return parser.text()


def extract_docx(path: Path) -> str:
    with zipfile.ZipFile(path) as archive:
        safe_zip_members(archive)
        raw = archive.read("word/document.xml")
    root = ElementTree.fromstring(raw)
    paragraphs: list[str] = []
    for paragraph in root.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p"):
        text = "".join(node.text or "" for node in paragraph.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t"))
        if text.strip():
            paragraphs.append(text.strip())
    return "\n\n".join(paragraphs)


def extract_epub(path: Path) -> str:
    sections: list[str] = []
    with zipfile.ZipFile(path) as archive:
        members = safe_zip_members(archive)
        names = sorted(item.filename for item in members if Path(item.filename).suffix.lower() in {".xhtml", ".html", ".htm"})
        for name in names:
            raw = archive.read(name).decode("utf-8", errors="ignore")
            text = html_to_text(raw)
            if text:
                sections.append(f"## EPUB SECTION: {name}\n\n{text}")
    return "\n\n".join(sections)


def extract_pdf(path: Path) -> tuple[str, str]:
    pdftotext = shutil.which("pdftotext")
    if pdftotext:
        with tempfile.TemporaryDirectory(prefix="book-extract-") as temp_dir:
            output = Path(temp_dir) / "source.txt"
            result = subprocess.run([pdftotext, "-layout", str(path), str(output)], capture_output=True, text=True, timeout=300)
            if result.returncode == 0 and output.is_file():
                return output.read_text(encoding="utf-8", errors="ignore"), "pdftotext-layout"
    if importlib.util.find_spec("pypdf"):
        from pypdf import PdfReader  # type: ignore

        reader = PdfReader(str(path))
        return "\n\n".join((page.extract_text() or "") for page in reader.pages), "pypdf"
    raise RuntimeError("PDF extractor unavailable; install pdftotext or pypdf explicitly")


def extract_rtf(raw: str) -> str:
    text = re.sub(r"\\'[0-9a-fA-F]{2}", " ", raw)
    text = re.sub(r"\\[a-zA-Z]+-?\d* ?", " ", text)
    text = text.replace("{", " ").replace("}", " ")
    return re.sub(r"\s+", " ", text).strip()


def extract_one(path: Path) -> tuple[str, str]:
    suffix = path.suffix.lower()
    if path.stat().st_size > MAX_SOURCE_BYTES:
        raise ValueError(f"source exceeds {MAX_SOURCE_BYTES} bytes")
    if suffix in {".md", ".markdown", ".txt", ".rst", ".adoc"}:
        return path.read_text(encoding="utf-8", errors="ignore"), "plain-text"
    if suffix in {".html", ".htm"}:
        return html_to_text(path.read_text(encoding="utf-8", errors="ignore")), "stdlib-html"
    if suffix == ".rtf":
        return extract_rtf(path.read_text(encoding="utf-8", errors="ignore")), "bounded-rtf-fallback"
    if suffix == ".docx":
        return extract_docx(path), "stdlib-docx-xml"
    if suffix == ".epub":
        return extract_epub(path), "stdlib-epub-zip"
    if suffix == ".pdf":
        return extract_pdf(path)
    raise ValueError(f"unsupported format: {suffix}")


def expand_inputs(values: list[str]) -> list[Path]:
    found: set[Path] = set()
    for value in values:
        matches = [Path(item) for item in glob.glob(value, recursive=True)] if any(char in value for char in "*?[") else [Path(value)]
        for match in matches:
            if match.is_dir():
                found.update(path.resolve() for path in match.rglob("*") if path.is_file() and path.suffix.lower() in SUPPORTED)
            elif match.is_file() and match.suffix.lower() in SUPPORTED:
                found.add(match.resolve())
    return sorted(found)


def preflight() -> dict:
    return {
        "supported_formats": sorted(SUPPORTED),
        "pdftotext": shutil.which("pdftotext") or "unavailable",
        "pypdf": bool(importlib.util.find_spec("pypdf")),
        "docx_epub_html": "stdlib extractors available",
        "automatic_dependency_install": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="*")
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--mode", choices=("text", "technical"), default="text")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        print(json.dumps(preflight(), indent=2))
        return
    if not args.inputs:
        print("ERROR: at least one file, directory or glob is required", file=sys.stderr)
        sys.exit(1)
    sources = expand_inputs(args.inputs)
    if not sources:
        print("ERROR: no supported source files found", file=sys.stderr)
        sys.exit(1)
    output_dir = (args.output_dir or Path(tempfile.gettempdir()) / "book_knowledge_work").resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    corpus_parts: list[str] = []
    metadata_sources: list[dict] = []
    failures: list[str] = []
    for index, path in enumerate(sources, start=1):
        try:
            text, method = extract_one(path)
        except (OSError, ValueError, RuntimeError, zipfile.BadZipFile, ElementTree.ParseError, subprocess.TimeoutExpired) as exc:
            failures.append(f"{path}: {exc}")
            continue
        words = len(text.split())
        corpus_parts.append(f"\n===== SOURCE {index}: {path.name} | SHA256 {sha256(path)} =====\n\n{text.strip()}\n")
        metadata_sources.append({"source_id": f"source-{index:03d}", "path": str(path), "filename": path.name, "format": path.suffix.lower(), "content_sha256": sha256(path), "size_bytes": path.stat().st_size, "extraction_method": method, "words": words, "estimated_tokens": round(words * 1.33), "limitations": ["Technical structure requires manual sample verification"] if args.mode == "technical" and method != "pdftotext-layout" else []})
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}", file=sys.stderr)
    if not metadata_sources:
        sys.exit(1)
    corpus = "\n".join(corpus_parts)
    corpus_path = output_dir / "full_text.txt"
    corpus_path.write_text(corpus, encoding="utf-8")
    total_words = len(corpus.split())
    metadata = {"generated_at": datetime.now(timezone.utc).isoformat(), "mode": args.mode, "total_sources": len(metadata_sources), "failed_sources": failures, "words": total_words, "estimated_tokens": round(total_words * 1.33), "corpus_path": str(corpus_path), "corpus_sha256": sha256(corpus_path), "sources": metadata_sources}
    metadata_path = output_dir / "metadata.json"
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"corpus": str(corpus_path), "metadata": str(metadata_path), "sources": len(metadata_sources), "failures": len(failures)}, indent=2))
    if failures:
        sys.exit(2)


if __name__ == "__main__":
    main()
