#!/usr/bin/env python3
"""Check a diagram source before it is published as documentation.

A diagram fails a reader for structural reasons long before it fails for aesthetic ones: a node
declared and never connected, two nodes sharing an identifier, an edge pointing at something that
does not exist, a canvas so dense nobody reads it, or no alt text at all. Those are cheap to catch
in the source and expensive to catch after the page ships.

It reads Mermaid, PlantUML or D2 source and checks it against itself. It does not render anything.

With `--provenance` it also checks that every node claims a source: an entry in a provenance
record naming the artifact it was read out of, plus a version anchor for the diagram as a whole.
That closes the gap between a diagram being well-formed and a diagram being derived from
anything. It still cannot open those artifacts and confirm the claims are honest — only the
person who inspected them can, and recording provenance is what makes that person identifiable.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

MERMAID_HEADERS = (
    "flowchart", "graph", "sequenceDiagram", "erDiagram", "classDiagram",
    "stateDiagram", "journey", "gantt", "pie", "mindmap", "timeline",
)
DENSITY_WARNING = 25

MERMAID_NODE = re.compile(r"\b([A-Za-z_][\w-]*)\s*(?:\[\[|\[\(|\(\(|\[|\(|\{\{|\{|>)([^\]\)\}]*)")
MERMAID_EDGE = re.compile(
    r"([A-Za-z_][\w-]*)\s*(?:-\.->|-\.-|-{2,3}>|-{2,3}|={2,3}>|<-{2,3}>)"
    r"(?:\|[^|]*\|)?\s*([A-Za-z_][\w-]*)"
)
# Node labels carry the same characters as edges; drop them before matching relationships.
MERMAID_LABEL = re.compile(
    r"([A-Za-z_][\w-]*)\s*(?:\[\[.*?\]\]|\[\(.*?\)\]|\(\(.*?\)\)|\{\{.*?\}\}|\[.*?\]|\(.*?\)|\{.*?\}|>.*?\])"
)
D2_EDGE = re.compile(r"^\s*([\w.-]+)\s*(?:->|<-|--|<->)\s*([\w.-]+)")
PLANTUML_EDGE = re.compile(r"^\s*(\w+)\s*(?:-+>|<-+|\.+>|-+)\s*(\w+)")


def detect_notation(text: str) -> str:
    stripped = "\n".join(
        line for line in text.splitlines() if not line.strip().startswith(("%%", "//", "'"))
    )
    if "@startuml" in stripped or "@startmindmap" in stripped:
        return "plantuml"
    for line in stripped.splitlines():
        head = line.strip()
        if head.startswith(MERMAID_HEADERS):
            return "mermaid"
    if D2_EDGE.search(stripped) or ":" in stripped:
        return "d2"
    return "unknown"


def parse_mermaid(text: str) -> tuple[set[str], list[tuple[str, str]], list[str]]:
    declared: set[str] = set()
    edges: list[tuple[str, str]] = []
    errors: list[str] = []
    labels: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.split("%%", 1)[0].strip()
        if not line or line.startswith(MERMAID_HEADERS) or line.startswith(("subgraph", "end", "click", "style", "classDef", "linkStyle")):
            continue
        for node_id, label in MERMAID_NODE.findall(line):
            declared.add(node_id)
            label = label.strip().strip('"')
            if label:
                if node_id in labels and labels[node_id] != label:
                    errors.append(
                        f"node `{node_id}` is declared twice with different labels: "
                        f"{labels[node_id]!r} then {label!r}"
                    )
                labels[node_id] = label
        for left, right in MERMAID_EDGE.findall(MERMAID_LABEL.sub(r"\1", line)):
            edges.append((left, right))
    for node_id, label in labels.items():
        if not label:
            errors.append(f"node `{node_id}` has an empty label")
    return declared | {n for edge in edges for n in edge}, edges, errors


def parse_simple(text: str, pattern: re.Pattern[str]) -> tuple[set[str], list[tuple[str, str]], list[str]]:
    nodes: set[str] = set()
    edges: list[tuple[str, str]] = []
    for raw in text.splitlines():
        line = raw.split("#", 1)[0]
        match = pattern.search(line)
        if match:
            left, right = match.group(1), match.group(2)
            edges.append((left, right))
            nodes.update((left, right))
    return nodes, edges, []


def check_balance(text: str, notation: str) -> list[str]:
    errors: list[str] = []
    if notation == "plantuml":
        starts = text.count("@startuml") + text.count("@startmindmap")
        ends = text.count("@enduml") + text.count("@endmindmap")
        if starts != ends:
            errors.append(f"unbalanced PlantUML block: {starts} start(s) against {ends} end(s)")
        if starts == 0:
            errors.append("PlantUML source has no @startuml block")
    if notation == "mermaid":
        opens = sum(text.count(char) for char in "([{")
        closes = sum(text.count(char) for char in ")]}")
        if opens != closes:
            errors.append(f"unbalanced brackets: {opens} opening against {closes} closing")
        subgraphs = len(re.findall(r"^\s*subgraph\b", text, re.MULTILINE))
        ends = len(re.findall(r"^\s*end\s*$", text, re.MULTILINE))
        if subgraphs > ends:
            errors.append(f"{subgraphs} subgraph(s) but only {ends} matching `end`")
    return errors


VALID_CLASSES = {"observed", "proposed", "illustrative"}
# A diagram read out of another diagram inherits its errors and none of its freshness.
DERIVED_SOURCE_TYPES = {"diagram", "readme", "ticket", "design-doc", "recall"}


def check_provenance(record: Any, nodes: set[str]) -> tuple[list[str], list[str]]:
    """Cross-check a provenance record against the node ids actually present in the source."""
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(record, dict):
        return ["provenance record is not an object"], []

    diagram_class = str(record.get("diagram_class", "")).strip()
    if diagram_class not in VALID_CLASSES:
        errors.append(f"diagram_class {diagram_class or '(empty)'} is not one of {sorted(VALID_CLASSES)}")

    elements = record.get("elements")
    if not isinstance(elements, list):
        return errors + ["provenance record has no elements list"], warnings

    by_node: dict[str, dict[str, Any]] = {}
    for element in elements:
        if not isinstance(element, dict):
            errors.append("an element entry is not an object")
            continue
        node_id = str(element.get("node_id", "")).strip()
        if not node_id:
            errors.append("an element entry has no node_id")
            continue
        by_node[node_id] = element

    # Only an observed diagram makes a claim about a system that exists, so only it needs sources.
    if diagram_class == "observed":
        unsourced = sorted(nodes - set(by_node))
        for node_id in unsourced:
            errors.append(f"node {node_id} has no provenance entry")
        anchor = record.get("version_anchor") or {}
        if not str(anchor.get("value", "")).strip():
            errors.append("observed diagram has no version anchor; 'is this still true' has no answer")
        if str(record.get("derived_from_diagram", "")).strip():
            errors.append(
                "observed diagram is derived from another diagram; it is proposed until an artifact is read"
            )
        for node_id, element in sorted(by_node.items()):
            source_type = str(element.get("source_type", "")).strip().lower()
            if source_type in DERIVED_SOURCE_TYPES:
                errors.append(f"node {node_id}: source_type {source_type} is not an inspected artifact")
            elif not source_type:
                errors.append(f"node {node_id}: no source_type")
            if not str(element.get("locator", "")).strip():
                errors.append(f"node {node_id}: no locator saying where it was read")

    # An element the source no longer contains is a rename or a deletion nobody propagated.
    for node_id in sorted(set(by_node) - nodes):
        warnings.append(f"provenance names {node_id}, which the diagram source does not contain")

    mixed = {
        str(e.get("element_class", "")).strip()
        for e in by_node.values()
        if str(e.get("element_class", "")).strip()
    }
    if len(mixed) > 1:
        warnings.append(
            f"elements mix classes ({', '.join(sorted(mixed))}); render them distinctly or split the diagram"
        )
    if not record.get("excluded"):
        warnings.append("nothing recorded as excluded; a silent omission reads as a claim that nothing was left out")
    return errors, warnings


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("source", type=Path, help="diagram source file (.mmd, .puml, .d2 or .md fence)")
    parser.add_argument("--alt-text", help="alt text for the rendered diagram; required unless --no-alt-text-required")
    parser.add_argument("--alt-text-file", type=Path, help="read alt text from a file instead")
    parser.add_argument("--no-alt-text-required", action="store_true", help="the diagram is decorative and carries no information")
    parser.add_argument("--max-nodes", type=int, default=DENSITY_WARNING, help=f"density warning threshold (default {DENSITY_WARNING})")
    parser.add_argument("--provenance", type=Path, help="diagram-provenance JSON record to check the source against")
    parser.add_argument("--strict", action="store_true", help="treat warnings as failures")
    args = parser.parse_args()

    if not args.source.is_file():
        print(f"ERROR: no such file: {args.source}")
        sys.exit(2)

    text = args.source.read_text(encoding="utf-8")
    fence = re.search(r"```(?:mermaid|d2|plantuml)?\s*\n(.*?)```", text, re.DOTALL)
    if fence:
        text = fence.group(1)
    if not text.strip():
        print("ERROR: diagram source is empty")
        sys.exit(1)

    notation = detect_notation(text)
    errors: list[str] = []
    warnings: list[str] = []

    if notation == "unknown":
        print("ERROR: could not detect Mermaid, PlantUML or D2 notation")
        sys.exit(1)

    errors.extend(check_balance(text, notation))
    if notation == "mermaid":
        nodes, edges, parse_errors = parse_mermaid(text)
    elif notation == "plantuml":
        nodes, edges, parse_errors = parse_simple(text, PLANTUML_EDGE)
    else:
        nodes, edges, parse_errors = parse_simple(text, D2_EDGE)
    errors.extend(parse_errors)

    if not edges:
        warnings.append("no relationships were parsed; a diagram with no edges usually shows a list, not a mechanism")

    connected = {node for edge in edges for node in edge}
    orphans = sorted(nodes - connected)
    if orphans and len(nodes) > 1:
        warnings.append(f"{len(orphans)} node(s) never appear in a relationship: {', '.join(orphans[:8])}")

    self_loops = [left for left, right in edges if left == right]
    if self_loops:
        warnings.append(f"{len(self_loops)} self-referencing edge(s): {', '.join(sorted(set(self_loops))[:8])}")

    if len(nodes) > args.max_nodes:
        warnings.append(
            f"{len(nodes)} nodes exceeds the {args.max_nodes}-node readability threshold; "
            "split the diagram or raise its abstraction level"
        )

    if args.provenance is not None:
        if not args.provenance.is_file():
            errors.append(f"provenance record not found: {args.provenance}")
        else:
            try:
                record = json.loads(args.provenance.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                errors.append(f"unreadable provenance record: {exc}")
            else:
                provenance_errors, provenance_warnings = check_provenance(record, nodes)
                errors.extend(provenance_errors)
                warnings.extend(provenance_warnings)

    alt_text = args.alt_text
    if args.alt_text_file:
        if not args.alt_text_file.is_file():
            errors.append(f"alt-text file not found: {args.alt_text_file}")
        else:
            alt_text = args.alt_text_file.read_text(encoding="utf-8").strip()
    if not args.no_alt_text_required:
        if not alt_text or not alt_text.strip():
            errors.append("no alt text supplied; a diagram carrying information needs a text equivalent")
        elif len(alt_text.strip()) < 20:
            warnings.append(f"alt text is {len(alt_text.strip())} characters; that rarely describes a mechanism")

    for error in errors:
        print(f"ERROR: {error}")
    for warning in warnings:
        print(f"WARNING: {warning}")
    print(f"notation: {notation}  nodes: {len(nodes)}  edges: {len(edges)}")

    if errors:
        print(f"FAILED: {len(errors)} structural error(s)")
        sys.exit(1)
    if warnings and args.strict:
        print(f"FAILED: {len(warnings)} warning(s) under --strict")
        sys.exit(1)
    if warnings:
        print(f"PASS WITH WARNINGS: {len(warnings)} item(s) to confirm before publishing")
        sys.exit(0)
    if args.provenance is not None:
        print(
            "PASS: structurally consistent, has a text equivalent, and every node claims an "
            "inspected source. Whether those sources say what the diagram says is not checked here."
        )
    else:
        print("PASS: diagram source is structurally consistent and has a text equivalent")


if __name__ == "__main__":
    main()
