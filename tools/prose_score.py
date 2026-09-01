#!/usr/bin/env python3
"""Score prose on the properties that separate written text from generated text.

AI detectors mostly estimate two things: how predictable the next word is, and how much that
predictability varies across the piece. Neither needs a detector to approximate. Sentence-length
variation, opener diversity, lexical diversity, concrete-detail density and paragraph variation
are all measurable locally, they move in the same direction, and — this is the point — every one
of them is also a property of good writing. Text that scores well here is text that varies its
rhythm, does not start every sentence the same way, uses words the topic actually requires, and
contains details a reader could check.

Thresholds are percentiles of this repository's own prose: 220 hand-written reference documents,
so "good" means "like writing that exists here" rather than a number chosen to look strict.

What it is not: a detector. It cannot tell you what any classifier will report, and it never
reads a piece as authored or generated — it reports properties, and those properties are worth
having whoever wrote the text. Chasing the score by inserting randomness satisfies the metric and
degrades the writing, which is the failure this tool makes easy to commit and does not prevent.
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from pathlib import Path

# (name, p10, median, weight, direction) measured over 220 reference documents.
BANDS = [
    ("sentence_variation", 0.434, 0.515, 0.30, "higher"),
    ("opener_diversity", 0.667, 0.793, 0.25, "higher"),
    ("lexical_diversity", 0.656, 0.728, 0.20, "higher"),
    ("paragraph_variation", 0.200, 0.254, 0.15, "higher"),
    ("concrete_density", 2.0, 11.4, 0.10, "higher"),
]

ADVICE = {
    "sentence_variation": "Sentences are too even. Let a point that needs six clauses have them, and let the next one be four words.",
    "opener_diversity": "Too many sentences begin the same way. Vary what comes first — a subject, a condition, a consequence — because the opener is where monotony is heard.",
    "lexical_diversity": "Vocabulary repeats. Usually this means the text restates rather than advances: cut the restatement instead of reaching for synonyms.",
    "paragraph_variation": "Paragraphs are uniform. A paragraph earns its length from the argument, and some arguments are one line.",
    "concrete_density": "Almost nothing here is checkable. Add a number, a version, a named tool, a date — a claim a reader could verify or dispute.",
}


def python_prose(text: str) -> str:
    """Docstrings and full-line comments only.

    The bands were calibrated on 220 markdown documents. Run them over a .py file whole and every
    identifier counts as a word, so `parser.add_argument` repeated eleven times reads as a writer
    who restates — which is a fact about Python, not about the writing. Take the prose a person
    actually composed and leave the code alone.
    """
    import ast

    parts: list[str] = []
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return text
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            doc = ast.get_docstring(node)
            if doc:
                parts.append(doc)
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# ") and not stripped.startswith("#!"):
            parts.append(stripped[2:])
    return "\n\n".join(parts)


def prose_only(text: str) -> str:
    body = text.split("---\n", 2)[-1] if text.startswith("---\n") else text
    return "\n".join(
        line for line in body.splitlines()
        if not line.lstrip().startswith(("|", "#", "-", "*", ">"))
        and not re.match(r"^\s*\d+[.)]\s", line)
    )


def measure(text: str) -> dict | None:
    body = prose_only(text)
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", body) if len(s.split()) >= 4]
    if len(sentences) < 12:
        return None
    lengths = [len(s.split()) for s in sentences]
    mean = sum(lengths) / len(lengths)
    openers = [s.split()[0].lower().strip(",.;:") for s in sentences]
    words = [w.lower() for w in re.findall(r"[\wÀ-ỹ']+", body)]

    window = 100
    ratios = [len(set(words[i:i + window])) / window for i in range(0, max(1, len(words) - window), 50)] or [0.0]

    paragraphs = [len(p.split()) for p in re.split(r"\n\s*\n", body) if len(p.split()) >= 15]

    return {
        "sentence_variation": statistics.stdev(lengths) / mean if mean else 0.0,
        "opener_diversity": len(set(openers)) / len(openers),
        "lexical_diversity": sum(ratios) / len(ratios),
        "paragraph_variation": (statistics.stdev(paragraphs) / (sum(paragraphs) / len(paragraphs)))
        if len(paragraphs) > 2 else 0.0,
        "concrete_density": len(re.findall(r"\b\d[\d.,%]*\b|`[^`]+`|\bv\d", body)) / max(1, len(words)) * 1000,
        "_sentences": len(sentences),
        "_words": len(words),
    }


def score(values: dict) -> tuple[float, list[tuple[str, float, str]]]:
    """0..1 against the repository's own distribution; at or above median scores full."""
    total = 0.0
    rows = []
    for name, p10, median, weight, _ in BANDS:
        value = values[name]
        if value >= median:
            band = 1.0
        elif value >= p10:
            band = 0.5 + 0.5 * (value - p10) / (median - p10)
        else:
            band = max(0.0, 0.5 * value / p10) if p10 else 0.0
        total += band * weight
        rows.append((name, value, "ok" if band >= 0.9 else ("weak" if band >= 0.5 else "poor")))
    return round(total, 3), rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--min", type=float, help="exit 1 below this score")
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()

    report = []
    worst = 1.0
    for path in args.paths:
        if not path.is_file():
            print(f"SKIP {path}: not a file")
            continue
        raw = path.read_text(encoding="utf-8")
        values = measure(python_prose(raw) if path.suffix == ".py" else raw)
        if values is None:
            print(f"SKIP {path.name}: under twelve sentences of prose, nothing to measure")
            continue
        total, rows = score(values)
        worst = min(worst, total)
        print(f"{total:.2f}  {path.name}  ({values['_sentences']} sentences)")
        for name, value, verdict in rows:
            if verdict != "ok":
                print(f"      {verdict:4} {name} {value:.3f} — {ADVICE[name]}")
        report.append({"file": path.as_posix(), "score": total,
                       "metrics": {k: v for k, v in values.items() if not k.startswith("_")}})

    if args.json:
        args.json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"report written: {args.json}")
    if args.min and worst < args.min:
        print(f"FAILED: lowest score {worst:.2f} below --min {args.min}")
        sys.exit(1)


if __name__ == "__main__":
    main()
