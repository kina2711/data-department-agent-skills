#!/usr/bin/env python3
"""Produce a heuristic structural and business-review scaffold for SELECT SQL."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def compact(sql: str) -> str:
    sql = re.sub(r"/\*.*?\*/", " ", sql, flags=re.S)
    sql = re.sub(r"--[^\n]*", " ", sql)
    return re.sub(r"\s+", " ", sql).strip().rstrip(";")


def split_expressions(text: str) -> list[str]:
    result, start, depth, quote = [], 0, 0, None
    for index, char in enumerate(text):
        if quote:
            if char == quote and (index == 0 or text[index - 1] != "\\"):
                quote = None
        elif char in "'\"`":
            quote = char
        elif char == "(":
            depth += 1
        elif char == ")":
            depth = max(0, depth - 1)
        elif char == "," and depth == 0:
            result.append(text[start:index].strip())
            start = index + 1
    tail = text[start:].strip()
    if tail:
        result.append(tail)
    return result


def sql_tokens(sql: str) -> list[tuple[str, int, int, int]]:
    """Return unquoted word tokens with source spans and parenthesis depth."""
    tokens: list[tuple[str, int, int, int]] = []
    index, depth, quote = 0, 0, None
    while index < len(sql):
        char = sql[index]
        if quote:
            if char == quote:
                if index + 1 < len(sql) and sql[index + 1] == quote:
                    index += 2
                    continue
                quote = None
            index += 1
            continue
        if char in "'\"`":
            quote = char
            index += 1
            continue
        if char == "[":
            quote = "]"
            index += 1
            continue
        if char == "(":
            depth += 1
            index += 1
            continue
        if char == ")":
            depth = max(0, depth - 1)
            index += 1
            continue
        match = re.match(r"[A-Za-z_][A-Za-z0-9_$]*", sql[index:])
        if match:
            end = index + len(match.group(0))
            tokens.append((match.group(0).upper(), index, end, depth))
            index = end
            continue
        index += 1
    return tokens


def sequence_at(tokens: list[tuple[str, int, int, int]], index: int, words: tuple[str, ...]) -> bool:
    if index + len(words) > len(tokens):
        return False
    depth = tokens[index][3]
    return all(tokens[index + offset][0] == word and tokens[index + offset][3] == depth for offset, word in enumerate(words))


def closing_scope_position(sql: str, start: int, scope_depth: int) -> int:
    """Find the closing parenthesis of the current SQL scope, if any."""
    depth, quote, index = scope_depth, None, start
    while index < len(sql):
        char = sql[index]
        if quote:
            if char == quote:
                if index + 1 < len(sql) and sql[index + 1] == quote:
                    index += 2
                    continue
                quote = None
            index += 1
            continue
        if char in "'\"`":
            quote = char
        elif char == "[":
            quote = "]"
        elif char == "(":
            depth += 1
        elif char == ")":
            if depth == scope_depth:
                return index
            depth -= 1
        index += 1
    return len(sql)


def clauses(sql: str, start_words: tuple[str, ...], end_sequences: tuple[tuple[str, ...], ...]) -> list[tuple[int, str]]:
    """Extract clauses while respecting query scope and nested expressions."""
    tokens = sql_tokens(sql)
    results: list[tuple[int, str]] = []
    for index, token in enumerate(tokens):
        if not sequence_at(tokens, index, start_words):
            continue
        scope_depth = token[3]
        content_start = tokens[index + len(start_words) - 1][2]
        content_end = closing_scope_position(sql, content_start, scope_depth)
        for later in range(index + len(start_words), len(tokens)):
            if tokens[later][3] < scope_depth:
                break
            if tokens[later][3] != scope_depth:
                continue
            if any(sequence_at(tokens, later, sequence) for sequence in end_sequences):
                content_end = min(content_end, tokens[later][1])
                break
        value = sql[content_start:content_end].strip()
        if value:
            results.append((scope_depth, value))
    return results


def extract_joins(sql: str) -> list[dict[str, str]]:
    tokens = sql_tokens(sql)
    joins: list[dict[str, str]] = []
    pattern = re.compile(
        r"\b(?:(LEFT|RIGHT|FULL(?:\s+OUTER)?|INNER|CROSS)\s+)?JOIN\s+"
        r"([`\"\[]?[A-Za-z_][\w$.-]*(?:[`\"\]]?)?)"
        r"(?:\s+(?:AS\s+)?(?!ON\b|WHERE\b|GROUP\b|HAVING\b|QUALIFY\b|ORDER\b|LIMIT\b)([A-Za-z_]\w*))?",
        flags=re.I,
    )
    for match in pattern.finditer(sql):
        join_index = next(
            (index for index, token in enumerate(tokens) if token[0] == "JOIN" and match.start() <= token[1] < match.end()),
            None,
        )
        condition = ""
        if join_index is not None:
            depth = tokens[join_index][3]
            on_index = next(
                (
                    index
                    for index in range(join_index + 1, len(tokens))
                    if tokens[index][3] == depth and tokens[index][0] == "ON"
                ),
                None,
            )
            if on_index is not None:
                end = closing_scope_position(sql, tokens[on_index][2], depth)
                for later in range(on_index + 1, len(tokens)):
                    if tokens[later][3] < depth:
                        break
                    if tokens[later][3] != depth:
                        continue
                    if tokens[later][0] in {"JOIN", "WHERE", "HAVING", "QUALIFY", "LIMIT", "UNION", "EXCEPT", "INTERSECT"} or sequence_at(tokens, later, ("GROUP", "BY")) or sequence_at(tokens, later, ("ORDER", "BY")):
                        end = min(end, tokens[later][1])
                        break
                condition = sql[tokens[on_index][2]:end].strip()
        joins.append(
            {
                "type": (match.group(1) or "INNER").upper(),
                "source": match.group(2),
                "alias": match.group(3) or "",
                "condition": condition,
            }
        )
    return joins


def analyze(raw: str, dialect: str) -> dict:
    sql = compact(raw)
    if not re.search(r"\bSELECT\b", sql, flags=re.I):
        raise ValueError("only SELECT/CTE query explanation is supported")
    ctes = re.findall(r"(?:\bWITH\b|,)\s*([A-Za-z_][\w$]*)\s+AS\s*\(", sql, flags=re.I)
    sources = re.findall(r"\b(?:FROM|JOIN)\s+([`\"\[]?[A-Za-z_][\w$.-]*(?:[`\"\]]?)?)", sql, flags=re.I)
    joins = extract_joins(sql)
    where_clauses = clauses(sql, ("WHERE",), (("GROUP", "BY"), ("HAVING",), ("QUALIFY",), ("ORDER", "BY"), ("LIMIT",), ("UNION",), ("EXCEPT",), ("INTERSECT",)))
    group_clauses = clauses(sql, ("GROUP", "BY"), (("HAVING",), ("QUALIFY",), ("ORDER", "BY"), ("LIMIT",), ("UNION",), ("EXCEPT",), ("INTERSECT",)))
    select_clauses = clauses(sql, ("SELECT",), (("FROM",),))
    outer_depth = min((depth for depth, _ in select_clauses), default=0)
    outer_select = next((value for depth, value in select_clauses if depth == outer_depth), "")
    outer_group = next((value for depth, value in group_clauses if depth == outer_depth), "")
    select_items = split_expressions(outer_select)
    aggregates = [item for item in select_items if re.search(r"\b(COUNT|SUM|AVG|MIN|MAX|STDDEV|VARIANCE)\s*\(", item, flags=re.I)]
    windows = [item for item in select_items if re.search(r"\bOVER\s*\(", item, flags=re.I)]
    risks = []
    if any(item.strip() == "*" or item.strip().endswith(".*") for item in select_items):
        risks.append("SELECT * makes the output contract and sensitive-column exposure unstable")
    if any(join["type"].startswith("CROSS") for join in joins):
        risks.append("CROSS JOIN can create a Cartesian expansion")
    if joins and not outer_group:
        risks.append("Confirm join cardinality and output grain; joins may fan out measures")
    if re.search(r"\bNOT\s+IN\s*\(", sql, flags=re.I):
        risks.append("NOT IN may behave unexpectedly when the subquery contains NULL")
    if aggregates and not re.search(r"\bCOALESCE\s*\(", sql, flags=re.I):
        risks.append("Confirm intended NULL behavior in aggregations")
    if any(re.search(r"\bCOUNT\s*\(\s*DISTINCT\b", item, flags=re.I) for item in aggregates) and any(re.search(r"\bSUM\s*\(", item, flags=re.I) for item in aggregates):
        risks.append("COUNT(DISTINCT ...) and row-level SUM(...) may use different effective grains when duplicate entity rows exist")
    if re.search(r"'\d{4}-\d{2}-\d{2}'", sql) and not re.search(r"(?:parameter|var|\{\{)", sql, flags=re.I):
        risks.append("Hard-coded date literals may make the query non-reusable or stale")
    questions = [
        "What business entity and period should one output row represent?",
        "Are source tables and metric definitions authoritative for this decision?",
        "What are the expected join cardinalities and how is fan-out detected?",
        "How should NULL, late-arriving records, time zones, currencies and duplicates be handled?",
        "Which control totals or alternate query will validate the result?",
    ]
    return {
        "status": "heuristic-review",
        "dialect": dialect,
        "ctes": ctes,
        "sources": list(dict.fromkeys(sources)),
        "joins": joins,
        "filters": [value for _, value in where_clauses],
        "group_by": split_expressions(outer_group),
        "output_expressions": select_items,
        "aggregations": aggregates,
        "window_expressions": windows,
        "risks": risks,
        "validation_questions": questions,
        "limitations": ["Regex-based structure extraction is not a dialect parser.", "Business meaning requires schema, glossary, metric definitions and owner review.", "Run engine-native parse/EXPLAIN or a dry run before relying on correctness or cost claims."],
    }


def human(result: dict) -> str:
    lines = [f"Status: {result['status']}", f"Dialect: {result['dialect']}", f"Sources: {', '.join(result['sources']) or 'unknown'}", f"CTEs: {', '.join(result['ctes']) or 'none'}", "Output expressions:"]
    lines += [f"- {item}" for item in result["output_expressions"]]
    lines.append("Risks:")
    lines += [f"- {item}" for item in result["risks"]] or ["- None detected by heuristic checks"]
    lines.append("Validation questions:")
    lines += [f"- {item}" for item in result["validation_questions"]]
    lines += [f"LIMITATION: {item}" for item in result["limitations"]]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--input", type=Path)
    source.add_argument("--sql")
    parser.add_argument("--dialect", default="unknown")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        raw = args.input.read_text(encoding="utf-8") if args.input else args.sql
        result = analyze(raw, args.dialect)
        rendered = json.dumps(result, ensure_ascii=False, indent=2) if args.json or args.output else human(result)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(rendered)
        return 0
    except Exception as exc:
        print(json.dumps({"status": "error", "message": str(exc)}, ensure_ascii=False) if args.json else f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
