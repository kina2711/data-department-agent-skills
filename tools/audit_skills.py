#!/usr/bin/env python3
"""Score every skill on measurable quality dimensions and rank the weakest ones.

"This skill is good" is an opinion. This produces the numbers an opinion would have to argue
with: always-visible description cost, routing-shard balance, contract depth, executable
evidence coverage, thin contracts that carry no task-specific resource, and description
overlap with sibling skills.

It measures structure, not correctness. A skill can score well here and still give bad advice;
a low score marks a place to look, not a proven defect.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
STOPWORDS = {
    "and", "for", "with", "the", "use", "when", "that", "this", "from", "into", "data",
    "a", "an", "of", "to", "or", "in", "on", "by", "as", "is", "are", "be", "it", "its",
}
# Always-visible cost: every skill description sits in context for every request.
DESCRIPTION_BUDGET = 600
SHARD_IMBALANCE_LIMIT = 0.55
THIN_CONTRACT_LIMIT = 0.60
OVERLAP_LIMIT = 0.35


def tokens(text: str) -> set[str]:
    return {word for word in re.findall(r"[a-z]{3,}", text.lower()) if word not in STOPWORDS}


def frontmatter(text: str) -> dict[str, str]:
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not match:
        return {}
    data: dict[str, str] = {}
    for line in match.group(1).splitlines():
        key, separator, value = line.partition(":")
        if separator:
            data[key.strip()] = value.strip().strip('"')
    return data


def measure(skill_dir: Path) -> dict[str, Any]:
    entry = skill_dir / "SKILL.md"
    text = entry.read_text(encoding="utf-8")
    meta = frontmatter(text)
    description = meta.get("description", "")

    references = skill_dir / "references"
    tasks_dir = references / "tasks"
    task_files = sorted(tasks_dir.glob("*.md")) if tasks_dir.exists() else []
    shards = sorted(references.glob("catalog-*.md")) if references.exists() else []
    shard_counts: dict[str, int] = {}
    for shard in shards:
        found = re.findall(r"\(tasks/([a-z0-9-]+)\.md\)", shard.read_text(encoding="utf-8"))
        shard_counts[shard.stem] = len(found)

    depth = Counter()
    thin = 0
    for path in task_files:
        body = path.read_text(encoding="utf-8")
        criticality = re.search(r"^- Criticality: `([a-z-]+)`", body, re.M)
        depth[criticality.group(1) if criticality else "unknown"] += 1
        # A contract whose only resources are the generic lifecycle lines carries no
        # task-specific control: nothing to run, no template, no adapter.
        if "Additional resources:" not in body:
            thin += 1

    scripts = sorted((skill_dir / "scripts").glob("*.py")) if (skill_dir / "scripts").is_dir() else []
    assets = sorted(p for p in (skill_dir / "assets").glob("*") if p.is_file()) if (skill_dir / "assets").is_dir() else []
    reference_files = [
        path for path in references.glob("*.md")
        if references.exists() and not path.name.startswith("catalog-")
    ]
    adapters = [path for path in reference_files if path.name.startswith("adapter-")]

    total_shard_tasks = sum(shard_counts.values()) or 1
    largest_shard = max(shard_counts.values(), default=0)

    return {
        "skill": skill_dir.name,
        "description_chars": len(description),
        "skill_md_lines": len(text.splitlines()),
        "tasks": len(task_files),
        "shards": shard_counts,
        "largest_shard_share": round(largest_shard / total_shard_tasks, 4),
        "depth": dict(depth),
        "thin_contracts": thin,
        "thin_share": round(thin / len(task_files), 4) if task_files else 0.0,
        "scripts": len(scripts),
        "assets": len(assets),
        "references": len(reference_files),
        "adapters": len(adapters),
        "description_tokens": tokens(description),
    }


def find_overlaps(records: list[dict[str, Any]]) -> dict[str, list[tuple[str, float]]]:
    """Jaccard similarity between descriptions. High overlap means routing can confuse them."""
    overlaps: dict[str, list[tuple[str, float]]] = {}
    for left in records:
        pairs: list[tuple[str, float]] = []
        for right in records:
            if left["skill"] == right["skill"]:
                continue
            a, b = left["description_tokens"], right["description_tokens"]
            union = a | b
            if not union:
                continue
            score = len(a & b) / len(union)
            if score >= OVERLAP_LIMIT:
                pairs.append((right["skill"], round(score, 3)))
        overlaps[left["skill"]] = sorted(pairs, key=lambda item: -item[1])[:3]
    return overlaps


def findings_for(record: dict[str, Any], overlaps: list[tuple[str, float]]) -> list[str]:
    findings: list[str] = []
    if record["description_chars"] > DESCRIPTION_BUDGET:
        findings.append(
            f"description is {record['description_chars']} chars against a {DESCRIPTION_BUDGET} budget; "
            "it is always in context, for every request"
        )
    if record["largest_shard_share"] > SHARD_IMBALANCE_LIMIT and record["tasks"] >= 12:
        biggest = max(record["shards"].items(), key=lambda item: item[1])
        findings.append(
            f"{biggest[0]} holds {record['largest_shard_share']:.0%} of the tasks; "
            "one shard doing most of the routing weakens progressive disclosure"
        )
    if record["thin_share"] > THIN_CONTRACT_LIMIT:
        findings.append(
            f"{record['thin_contracts']}/{record['tasks']} contracts ({record['thin_share']:.0%}) carry no "
            "task-specific resource: no script, template or adapter to run"
        )
    if record["scripts"] == 0 and record["tasks"] >= 20:
        findings.append(f"{record['tasks']} tasks and no executable evidence script")
    if overlaps:
        pairs = ", ".join(f"{name} ({score:.2f})" for name, score in overlaps)
        findings.append(f"description overlaps siblings: {pairs}; confirm role-confusion cases cover these")
    return findings


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report-out", type=Path, help="write the full scorecard as JSON")
    parser.add_argument("--top", type=int, default=10, help="how many weakest skills to detail")
    parser.add_argument("--fail-on-findings", action="store_true",
                        help="exit non-zero when any skill has a finding")
    args = parser.parse_args()

    skill_dirs = sorted(path for path in SKILLS.iterdir() if path.is_dir())
    records = [measure(path) for path in skill_dirs]
    overlaps = find_overlaps(records)

    for record in records:
        record["findings"] = findings_for(record, overlaps[record["skill"]])
        record["overlaps"] = overlaps[record["skill"]]
        del record["description_tokens"]

    ranked = sorted(records, key=lambda record: (-len(record["findings"]), -record["thin_share"]))
    flagged = [record for record in ranked if record["findings"]]

    print(f"skills_audited: {len(records)}")
    print(f"skills_with_findings: {len(flagged)}")
    print(f"total_findings: {sum(len(record['findings']) for record in records)}")
    print(f"mean_thin_share: {sum(r['thin_share'] for r in records) / len(records):.2%}")
    print()

    for record in ranked[: args.top]:
        if not record["findings"]:
            continue
        print(
            f"{record['skill']}  ({record['tasks']} tasks, {record['scripts']} scripts, "
            f"{record['assets']} assets, {record['adapters']} adapters)"
        )
        for finding in record["findings"]:
            print(f"  - {finding}")
        print()

    if args.report_out is not None:
        args.report_out.write_text(
            json.dumps({"skills": records}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(f"report written: {args.report_out}")

    if args.fail_on_findings and flagged:
        sys.exit(1)


if __name__ == "__main__":
    main()
