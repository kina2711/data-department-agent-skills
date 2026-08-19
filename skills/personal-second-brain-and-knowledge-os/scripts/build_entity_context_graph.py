#!/usr/bin/env python3
"""Index and retrieve memory with no model calls, returning pointers into the original traces.

Summarizing memory with a model costs tokens on every write and loses the evidence: once a
detail is merged away, nothing downstream can recover it. This control follows the structure
Zero-Mem describes (arXiv 2607.29377) -- keep the original traces as the source of record,
organize them as an entity-context graph plus a temporal hierarchy, and retrieve by
deterministic scoring.

Scope, stated plainly: the memory operations here make zero model calls, and retrieval
returns spans of the original trace rather than generated prose. This is a lexical
implementation with no encoder, so it does not reproduce the paper's retrieval quality or its
benchmark results, and reading the retrieved spans still costs tokens in the caller's context.
The claim it supports is narrow: indexing, linking and ranking cost no tokens, and no stored
detail is ever silently rewritten.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TEXT_SUFFIXES = {".md", ".markdown", ".txt", ".rst"}
RECORD_SUFFIXES = {".jsonl", ".ndjson"}
SKIP_DIRECTORIES = {".git", "node_modules", "__pycache__", ".venv", "venv", ".obsidian"}
STOPWORDS = {
    "the", "and", "for", "with", "that", "this", "from", "have", "has", "was", "were",
    "are", "not", "but", "you", "your", "our", "its", "into", "than", "then", "they",
    "them", "when", "what", "which", "will", "would", "can", "could", "should", "about",
}
ENTITY_PATTERNS = [
    re.compile(r"`([A-Za-z0-9_./-]{3,64})`"),
    re.compile(r"\[\[([^\]]{2,64})\]\]"),
    re.compile(r"(?<![\w#])#([A-Za-z][A-Za-z0-9_-]{2,32})"),
    re.compile(r"\b([A-Z][a-zA-Z0-9]{2,}(?:[ ][A-Z][a-zA-Z0-9]{2,}){0,3})\b"),
]
TIMESTAMP_PATTERNS = [
    re.compile(r"\b(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(?::\d{2})?)"),
    re.compile(r"\b(\d{4}-\d{2}-\d{2})\b"),
]


def tokenize(text: str) -> list[str]:
    return [word for word in re.findall(r"[a-z0-9_]{3,}", text.lower()) if word not in STOPWORDS]


def extract_entities(text: str) -> list[str]:
    found: list[str] = []
    for pattern in ENTITY_PATTERNS:
        for match in pattern.findall(text):
            entity = str(match).strip()
            if 2 < len(entity) <= 64:
                found.append(entity)
    seen: set[str] = set()
    ordered: list[str] = []
    for entity in found:
        key = entity.lower()
        if key not in seen:
            seen.add(key)
            ordered.append(entity)
    return ordered


def parse_timestamp(text: str) -> str | None:
    for pattern in TIMESTAMP_PATTERNS:
        match = pattern.search(text)
        if match:
            return match.group(1)
    return None


def timestamp_sort_key(value: str | None) -> str:
    return value or ""


def segment_text(text: str, path: Path, session: str) -> list[dict[str, Any]]:
    """Split a trace into spans without altering a single character of its content."""
    spans: list[dict[str, Any]] = []
    lines = text.splitlines()
    current: list[str] = []
    start_line = 1
    for index, line in enumerate(lines, start=1):
        is_boundary = line.startswith("#") or (not line.strip() and len(current) >= 12)
        if is_boundary and current and any(item.strip() for item in current):
            spans.append({"start_line": start_line, "end_line": index - 1, "text": "\n".join(current)})
            current = []
            start_line = index
        current.append(line)
    if current and any(item.strip() for item in current):
        spans.append({"start_line": start_line, "end_line": len(lines), "text": "\n".join(current)})

    records: list[dict[str, Any]] = []
    for order, span in enumerate(spans):
        body = span["text"]
        records.append({
            "record_id": f"{path.as_posix()}#L{span['start_line']}-{span['end_line']}",
            "source": path.as_posix(),
            "session": session,
            "order": order,
            "start_line": span["start_line"],
            "end_line": span["end_line"],
            "timestamp": parse_timestamp(body),
            "entities": extract_entities(body),
            "tokens": tokenize(body),
            "preview": body.strip().splitlines()[0][:160] if body.strip() else "",
        })
    return records


def load_jsonl(path: Path, session: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for order, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines()):
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(payload, dict):
            continue
        body = " ".join(
            str(payload.get(field, "")) for field in ("text", "content", "message", "body", "summary")
        ).strip() or json.dumps(payload, ensure_ascii=False)
        records.append({
            "record_id": f"{path.as_posix()}#{order}",
            "source": path.as_posix(),
            "session": str(payload.get("session") or session),
            "order": order,
            "start_line": order + 1,
            "end_line": order + 1,
            "timestamp": str(payload.get("timestamp") or payload.get("created_at") or "") or parse_timestamp(body),
            "entities": extract_entities(body),
            "tokens": tokenize(body),
            "preview": body[:160],
        })
    return records


def build_index(root: Path) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or any(part in SKIP_DIRECTORIES for part in path.parts):
            continue
        session = path.parent.relative_to(root).as_posix() or "."
        try:
            if path.suffix.lower() in RECORD_SUFFIXES:
                records.extend(load_jsonl(path, session))
            elif path.suffix.lower() in TEXT_SUFFIXES:
                records.extend(segment_text(path.read_text(encoding="utf-8", errors="replace"), path, session))
        except OSError:
            continue

    entity_graph: dict[str, list[str]] = defaultdict(list)
    for record in records:
        for entity in record["entities"]:
            entity_graph[entity.lower()].append(record["record_id"])

    co_occurrence: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for record in records:
        keys = sorted({entity.lower() for entity in record["entities"]})
        for i, left in enumerate(keys):
            for right in keys[i + 1:]:
                co_occurrence[left][right] += 1
                co_occurrence[right][left] += 1

    temporal: dict[str, list[str]] = defaultdict(list)
    for record in sorted(records, key=lambda item: (item["session"], timestamp_sort_key(item["timestamp"]), item["order"])):
        temporal[record["session"]].append(record["record_id"])

    return {
        "built_at": datetime.now(timezone.utc).isoformat(),
        "root": root.as_posix(),
        "model_calls": 0,
        "records": records,
        "entity_graph": {key: sorted(set(value)) for key, value in sorted(entity_graph.items())},
        "entity_co_occurrence": {
            key: dict(sorted(value.items(), key=lambda item: item[1], reverse=True)[:12])
            for key, value in sorted(co_occurrence.items())
        },
        "temporal_hierarchy": dict(sorted(temporal.items())),
    }


def retrieve(index: dict[str, Any], query: str, limit: int, expand: bool) -> list[dict[str, Any]]:
    """Rank records by entity overlap, lexical overlap, recency and session locality."""
    query_entities = {entity.lower() for entity in extract_entities(query)}
    query_tokens = set(tokenize(query))
    entity_graph = index.get("entity_graph", {})
    co_occurrence = index.get("entity_co_occurrence", {})

    if expand:
        neighbours: set[str] = set()
        for entity in query_entities:
            neighbours.update(co_occurrence.get(entity, {}))
        query_entities |= neighbours

    records = index.get("records", [])
    timestamps = sorted({record["timestamp"] for record in records if record.get("timestamp")})
    recency_rank = {value: position / max(1, len(timestamps) - 1) for position, value in enumerate(timestamps)}

    direct_hits: set[str] = set()
    for entity in query_entities:
        direct_hits.update(entity_graph.get(entity, []))

    scored: list[dict[str, Any]] = []
    for record in records:
        record_entities = {entity.lower() for entity in record.get("entities", [])}
        entity_overlap = len(record_entities & query_entities)
        token_overlap = len(set(record.get("tokens", [])) & query_tokens)
        if not entity_overlap and not token_overlap:
            continue
        recency = recency_rank.get(record.get("timestamp"), 0.0)
        locality = 0.5 if record["record_id"] in direct_hits else 0.0
        score = (entity_overlap * 3.0) + (token_overlap * 1.0) + (recency * 2.0) + locality
        scored.append({
            "record_id": record["record_id"],
            "source": record["source"],
            "lines": [record["start_line"], record["end_line"]],
            "session": record["session"],
            "timestamp": record.get("timestamp"),
            "score": round(score, 3),
            "matched_entities": sorted(record_entities & query_entities)[:8],
            "preview": record.get("preview", ""),
        })
    scored.sort(key=lambda item: (-item["score"], item["record_id"]))
    return scored[:limit]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="directory of traces, notes or JSONL interaction records")
    parser.add_argument("--index-out", type=Path, help="write the index as JSON")
    parser.add_argument("--index-in", type=Path, help="reuse an existing index instead of rebuilding")
    parser.add_argument("--query", help="retrieve records relevant to this text")
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--expand", action="store_true", help="follow the entity co-occurrence graph one hop")
    args = parser.parse_args()

    if args.index_in is not None:
        try:
            index = json.loads(args.index_in.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"ERROR: unreadable index: {exc}")
            sys.exit(1)
    else:
        if not args.root.is_dir():
            print(f"ERROR: not a directory: {args.root}")
            sys.exit(1)
        index = build_index(args.root)

    if args.index_out is not None:
        args.index_out.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"index written: {args.index_out}")

    print(f"records: {len(index.get('records', []))}")
    print(f"entities: {len(index.get('entity_graph', {}))}")
    print(f"sessions: {len(index.get('temporal_hierarchy', {}))}")
    print(f"model_calls: {index.get('model_calls', 0)}")

    if not args.query:
        if not index.get("records"):
            print("EMPTY: no traces indexed; nothing can be recalled")
            sys.exit(1)
        print("PASS: index built with no model calls; pass --query to retrieve")
        return

    hits = retrieve(index, args.query, args.limit, args.expand)
    if not hits:
        print("NO MATCH: nothing in the indexed traces matches this query")
        print("Report this as unknown. Do not answer from an unindexed assumption.")
        sys.exit(2)
    for hit in hits:
        location = f"{hit['source']}:{hit['lines'][0]}-{hit['lines'][1]}"
        print(f"{hit['score']:>7}  {location}")
        if hit["matched_entities"]:
            print(f"         entities: {', '.join(hit['matched_entities'])}")
        if hit["preview"]:
            print(f"         {hit['preview']}")
    print(f"RETRIEVED: {len(hits)} span(s) with 0 model calls; read the cited spans for evidence")


if __name__ == "__main__":
    main()
