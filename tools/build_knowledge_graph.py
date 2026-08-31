#!/usr/bin/env python3
"""Build one graph over everything this suite already knows, with every edge labelled by origin.

Four structures here carry relationships and none of them talk to each other: the concept
registry's parent links, the corpus plans' prerequisites, the workflows' stage dependencies, and
the standards each contract routes to. Joined, they answer questions no single file can — which
concept sits under the most work, which standards hold the suite together, whether the clusters
that emerge match the skill boundaries somebody drew.

Every edge carries where it came from, which is the part worth insisting on:

  extracted  a person wrote this relationship down, or it was read verbatim from a file
  inferred   this tool derived it from a rule, and the rule is recorded with the edge
  ambiguous  the relationship is asserted but its meaning is weaker than the edge implies

That last category is not decoration. The 832 workflow edges encode *phase precedence*, not task
prerequisites — two tasks in one stage are peers — and a graph that presented them as
dependencies would be lying at scale. They are labelled ambiguous and excluded from any claim
about what depends on what.

Communities come from label propagation, implemented here because the suite ships standard
library only. It is non-deterministic in general, so the seed is fixed and the run is repeatable.

It reads structure. Clustering finds groups, not meaning: a community is a question worth asking,
never an answer.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "knowledge-graph.json"
SEED = 20260831


def collect() -> tuple[dict[str, dict], list[dict]]:
    nodes: dict[str, dict] = {}
    edges: list[dict] = []

    def node(nid: str, kind: str, **extra) -> None:
        if nid not in nodes:
            nodes[nid] = {"id": nid, "kind": kind, **extra}

    registry = json.loads((ROOT / "docs" / "concept-registry.json").read_text(encoding="utf-8"))
    for key in registry["keys"]:
        node(key["concept_key"], "concept", domain=key["domain"], label=key["display_name"])
    for key in registry["keys"]:
        for parent in key["parents"]:
            if parent in nodes:
                edges.append({"from": parent, "to": key["concept_key"], "type": "prerequisite",
                              "provenance": "extracted",
                              "basis": "authored parent link in the concept registry"})

    for plan_path in sorted((ROOT / "docs" / "corpus-plans").glob("*.corpus.json")):
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        for note in plan["notes"]:
            node(note["id"], "note", domain=plan["corpus_id"], label=note["title"])
            for key in note["concept_keys"]:
                if key in nodes:
                    edges.append({"from": note["id"], "to": key, "type": "teaches",
                                  "provenance": "extracted",
                                  "basis": "concept_keys declared on the planned note"})
            for parent in note["builds_on"]:
                edges.append({"from": parent, "to": note["id"], "type": "prerequisite",
                              "provenance": "inferred",
                              "basis": "derived from the registry parent link between the notes' concepts"})

    catalog = {t["id"]: t for t in json.loads((ROOT / "task-catalog.json").read_text(encoding="utf-8"))}
    index = json.loads((ROOT / "docs" / "retrieval-index.json").read_text(encoding="utf-8"))
    for task in index["tasks"]:
        node(task["id"], "task", domain=task["skill"], label=task["output"])
        for standard in task["standards"]:
            node(standard, "standard", domain="reference", label=standard)
            edges.append({"from": task["id"], "to": standard, "type": "routes-to",
                          "provenance": "extracted",
                          "basis": "link present in the task contract"})

    for wf_path in sorted((ROOT / "workflows").glob("*.workflow.json")):
        manifest = json.loads(wf_path.read_text(encoding="utf-8"))
        for task in manifest["tasks"]:
            for dep in task["depends_on"]:
                if dep in catalog and task["task_id"] in catalog:
                    edges.append({"from": dep, "to": task["task_id"], "type": "stage-precedence",
                                  "provenance": "ambiguous",
                                  "basis": "phase order from docs/skill-map.md; tasks inside a stage are peers, "
                                           "so this is not a task-level prerequisite"})
    return nodes, edges


# A standard nearly every task routes to connects everything to everything and destroys the
# community structure entirely — the first run put 923 of 1215 nodes in one blob. Same reasoning
# as stopwords: a link carried by almost every node discriminates nothing.
UBIQUITY_THRESHOLD = 0.5


def hub_standards(nodes: dict, edges: list[dict]) -> set[str]:
    task_count = sum(1 for n in nodes.values() if n["kind"] == "task") or 1
    reached: Counter = Counter()
    for edge in edges:
        if edge["type"] == "routes-to":
            reached[edge["to"]] += 1
    return {sid for sid, n in reached.items() if n / task_count >= UBIQUITY_THRESHOLD}


def communities(nodes: dict, edges: list[dict], ignore: set[str] | None = None,
                trustworthy_only: bool = True) -> dict[str, int]:
    """Label propagation over the edges whose meaning supports a structural claim."""
    ignore = ignore or set()
    adjacency: dict[str, set[str]] = defaultdict(set)
    for edge in edges:
        if trustworthy_only and edge["provenance"] == "ambiguous":
            continue
        if edge["from"] in ignore or edge["to"] in ignore:
            continue
        adjacency[edge["from"]].add(edge["to"])
        adjacency[edge["to"]].add(edge["from"])

    label = {nid: i for i, nid in enumerate(sorted(nodes))}
    order = sorted(nodes)
    rng = random.Random(SEED)
    for _ in range(30):
        rng.shuffle(order)
        changed = 0
        for nid in order:
            neighbours = adjacency.get(nid)
            if not neighbours:
                continue
            counts = Counter(label[n] for n in neighbours if n in label)
            if not counts:
                continue
            best = min(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:1])[0]
            if label[nid] != best:
                label[nid] = best
                changed += 1
        if not changed:
            break
    return label


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--report", action="store_true", help="print hubs, communities and cross-domain edges")
    args = parser.parse_args()

    nodes, edges = collect()
    ubiquitous = hub_standards(nodes, edges)
    label = communities(nodes, edges, ignore=ubiquitous)

    by_provenance = Counter(e["provenance"] for e in edges)
    degree: Counter = Counter()
    for edge in edges:
        if edge["provenance"] == "ambiguous":
            continue
        degree[edge["from"]] += 1
        degree[edge["to"]] += 1

    groups: dict[int, list[str]] = defaultdict(list)
    for nid, lbl in label.items():
        groups[lbl].append(nid)
    real = {k: v for k, v in groups.items() if len(v) > 1}

    cross = [
        e for e in edges
        if e["provenance"] != "ambiguous"
        and nodes.get(e["from"], {}).get("domain") != nodes.get(e["to"], {}).get("domain")
        and nodes.get(e["from"], {}).get("kind") == nodes.get(e["to"], {}).get("kind")
    ]

    graph = {
        "_": ("Every edge carries its provenance. `ambiguous` edges — workflow stage precedence — "
              "are excluded from degree, clustering and any claim about what depends on what."),
        "seed": SEED,
        "node_count": len(nodes),
        "edge_count": len(edges),
        "edges_by_provenance": dict(by_provenance),
        "community_count": len(real),
        "ubiquitous_standards_excluded": sorted(ubiquitous),
        "nodes": [{**n, "community": label[n["id"]], "degree": degree[n["id"]]} for n in nodes.values()],
        "edges": edges,
    }

    rendered = json.dumps(graph, ensure_ascii=False, indent=1) + "\n"
    print(f"nodes: {len(nodes)}  edges: {len(edges)}  "
          f"({', '.join(f'{k} {v}' for k, v in sorted(by_provenance.items()))})")
    print(f"communities over non-ambiguous edges: {len(real)}"
          f"  (excluding {len(ubiquitous)} standards every task routes to)")

    if args.report:
        print("\nhubs — what the most work routes through:")
        for nid, deg in degree.most_common(8):
            print(f"  {deg:5}  {nodes[nid]['kind']:8} {nid}")
        print("\nlargest communities:")
        for lbl, members in sorted(real.items(), key=lambda kv: -len(kv[1]))[:5]:
            kinds = Counter(nodes[m]["kind"] for m in members)
            domains = Counter(nodes[m].get("domain", "") for m in members).most_common(2)
            print(f"  {len(members):4} nodes  {dict(kinds)}  top domains: {domains}")
        print(f"\ncross-domain edges between nodes of the same kind: {len(cross)}")
        for edge in cross[:5]:
            print(f"  {edge['from']} → {edge['to']}  ({edge['type']}, {edge['provenance']})")

    if OUT.exists() and OUT.read_text(encoding="utf-8") == rendered:
        return
    if args.check:
        print("FAILED: knowledge graph is out of date")
        sys.exit(1)
    OUT.write_text(rendered, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
