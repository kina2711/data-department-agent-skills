#!/usr/bin/env python3
"""Plan one note corpus per role from the concept registry.

A corpus plan enumerates every note before any note is written, which is what stops a note
acquiring a prerequisite edge that points nowhere. This produces those plans: for each role, the
concept keys that role has to hold, arranged into modules, with prerequisite edges taken from the
registry's own parent relationships rather than invented here.

Everything it emits is `planned`. No note exists yet, and the plan says so; the corpus manifest is
the resume anchor a session picks up, one module at a time.

It plans coverage. It cannot judge whether a role really needs a concept, and the module ordering
is a starting sequence rather than a curriculum somebody validated.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "docs" / "concept-registry.json"
OUT_DIR = ROOT / "docs" / "corpus-plans"

# role -> ordered modules, each naming the registry domains or explicit keys it covers.
# Order is the reading order; a module depends on the one before it.
ROLES: dict[str, tuple[str, list[tuple[str, list[str]]]]] = {
    "data-analyst": ("Data Analyst", [
        ("sql-foundation", ["ck.sql.grain", "ck.sql.null-semantics", "ck.sql.join-semantics", "ck.sql.fan-out", "ck.sql.set-operations"]),
        ("sql-analysis", ["ck.sql.window-function", "ck.sql.cte-vs-subquery", "ck.sql.aggregation-grain-error"]),
        ("analysis-method", ["domain:analytics"]),
        ("reading-the-model", ["ck.modelling.dimensional-model", "ck.modelling.conformed-dimension", "ck.modelling.semantic-layer"]),
        ("stakeholder-work", ["ck.product.stakeholder-decision", "ck.product.opportunity-sizing", "ck.product.acceptance-criteria"]),
    ]),
    "data-engineer": ("Data Engineer", [
        ("sql-and-storage", ["ck.sql.grain", "ck.sql.join-semantics", "ck.sql.index-and-scan", "ck.sql.query-plan", "ck.sql.transaction-isolation", "ck.sql.idempotent-write"]),
        ("python-for-pipelines", ["ck.python.iterator-generator", "ck.python.exception-flow", "ck.python.packaging-environment", "ck.python.testing-pyramid"]),
        ("pipeline-core", ["domain:pipeline"]),
        ("warehouse-physics", ["domain:warehouse"]),
        ("engineering-practice", ["domain:swe"]),
    ]),
    "analytics-engineer": ("Analytics Engineer", [
        ("sql-depth", ["ck.sql.grain", "ck.sql.fan-out", "ck.sql.window-function", "ck.sql.aggregation-grain-error", "ck.sql.normalization"]),
        ("modelling", ["domain:modelling"]),
        ("incremental-and-cost", ["ck.pipeline.idempotency", "ck.pipeline.backfill", "ck.warehouse.partitioning", "ck.warehouse.clustering", "ck.warehouse.scan-cost"]),
        ("release-discipline", ["ck.swe.version-control-hygiene", "ck.swe.code-review", "ck.swe.test-isolation", "ck.swe.ci-feedback-loop"]),
    ]),
    "business-data-analyst": ("Business Data Analyst", [
        ("sql-working-level", ["ck.sql.grain", "ck.sql.join-semantics", "ck.sql.fan-out", "ck.sql.null-semantics"]),
        ("requirements", ["domain:product"]),
        ("analysis-traps", ["ck.analytics.simpson-paradox", "ck.analytics.survivorship-bias", "ck.analytics.sampling-bias", "ck.analytics.metric-definition-drift"]),
        ("semantics-and-contracts", ["ck.modelling.semantic-layer", "ck.arch.data-contract"]),
    ]),
    "data-scientist": ("Data Scientist", [
        ("python-core", ["domain:python"]),
        ("statistics-traps", ["ck.analytics.statistical-power", "ck.analytics.sampling-bias", "ck.analytics.simpson-paradox", "ck.analytics.survivorship-bias"]),
        ("modelling-discipline", ["domain:ml"]),
        ("data-access", ["ck.sql.grain", "ck.sql.join-semantics", "ck.sql.fan-out"]),
    ]),
    "ml-engineer": ("ML Engineer", [
        ("python-production", ["ck.python.packaging-environment", "ck.python.typing-and-hints", "ck.python.testing-pyramid", "ck.python.async-concurrency", "ck.python.vectorisation"]),
        ("ml-serving", ["ck.ml.train-serve-skew", "ck.ml.feature-store", "ck.ml.drift", "ck.ml.leakage"]),
        ("pipeline-and-contracts", ["ck.pipeline.idempotency", "ck.pipeline.schema-evolution", "ck.arch.idempotent-interface", "ck.arch.data-contract"]),
        ("engineering-practice", ["domain:swe"]),
    ]),
    "data-architect": ("Data Architect", [
        ("architecture-core", ["domain:arch"]),
        ("modelling-decisions", ["ck.modelling.dimensional-model", "ck.modelling.one-big-table", "ck.modelling.conformed-dimension", "ck.modelling.slowly-changing-dimension"]),
        ("platform-physics", ["domain:warehouse"]),
        ("integration-semantics", ["ck.pipeline.delivery-semantics", "ck.pipeline.cdc", "ck.pipeline.schema-evolution", "ck.pipeline.watermark"]),
    ]),
    "product-manager": ("Product Owner / Manager", [
        ("product-core", ["domain:product"]),
        ("measurement", ["ck.analytics.funnel", "ck.analytics.cohort", "ck.analytics.retention-curve", "ck.analytics.metric-definition-drift"]),
        ("evidence-limits", ["ck.analytics.statistical-power", "ck.analytics.sampling-bias", "ck.analytics.survivorship-bias"]),
    ]),
    "bridge-se": ("Bridge SE", [
        ("requirements-and-traceability", ["ck.product.acceptance-criteria", "ck.product.requirement-traceability", "ck.product.stakeholder-decision"]),
        ("engineering-vocabulary", ["ck.swe.version-control-hygiene", "ck.swe.code-review", "ck.swe.ci-feedback-loop", "ck.swe.technical-debt"]),
        ("data-vocabulary", ["ck.sql.grain", "ck.modelling.semantic-layer", "ck.arch.data-contract", "ck.arch.coupling"]),
    ]),
    "software-engineer": ("Software Engineer", [
        ("practice", ["domain:swe"]),
        ("python", ["domain:python"]),
        ("rust", ["domain:rust"]),
        ("systems-thinking", ["ck.arch.coupling", "ck.arch.consistency-model", "ck.arch.failure-domain", "ck.arch.idempotent-interface"]),
    ]),
}


def load_registry() -> dict[str, dict]:
    doc = json.loads(REGISTRY.read_text(encoding="utf-8"))
    return {k["concept_key"]: k for k in doc["keys"]}


def expand(spec: list[str], registry: dict[str, dict]) -> list[str]:
    out: list[str] = []
    for item in spec:
        if item.startswith("domain:"):
            domain = item.split(":", 1)[1]
            out += [k for k, v in registry.items() if v["domain"] == domain]
        elif item in registry:
            out.append(item)
    seen: set[str] = set()
    return [k for k in out if not (k in seen or seen.add(k))]


def note_id(role: str, key: str) -> str:
    return f"{role}.{key.split('.', 1)[1]}"


def build(role: str, display: str, modules: list, registry: dict[str, dict]) -> dict:
    notes = []
    placed: dict[str, str] = {}
    for module_id, spec in modules:
        keys = expand(spec, registry)
        if not keys:
            continue
        for key in keys:
            entry = registry[key]
            nid = note_id(role, key)
            placed[key] = nid
            # Prerequisites come from the registry's parent edges and from nowhere else. Module
            # order is reading order, which `module_id` already carries; writing it into
            # `builds_on` would claim that Rust ownership depends on the Python data model
            # because one module happens to precede the other.
            depends = [placed[p] for p in entry["parents"] if p in placed]
            notes.append({
                "id": nid,
                "title": entry["display_name"],
                "module_id": module_id,
                "path": f"{role}/{module_id}/{key.split('.', 1)[1]}.md",
                "tags": [entry["domain"], module_id],
                "concept_keys": [key],
                "primary_for_keys": [key],
                "builds_on": [d for d in depends if d],
                "prerequisite_of": [],
                "status": "planned",
                "version_sensitive": False,
                "updated": "",
            })

    by_id = {n["id"]: n for n in notes}
    for note in notes:
        for parent in note["builds_on"]:
            if parent in by_id:
                by_id[parent]["prerequisite_of"].append(note["id"])

    return {
        "corpus_id": f"{role}-corpus",
        "domain": display,
        "roadmap_ref": "",
        "track_map_ref": "",
        "note_root": "notes",
        "standard": "knowledge-deep-dive-standard.md",
        "concept_registry_ref": "docs/concept-registry.json",
        "_": ("Planned only: no note exists yet. Run academy-elicit-prior-knowledge before "
              "building, then academy-build-note-module one module at a time, checkpointing here."),
        "notes": notes,
        "modules_completed": [],
        "next_module": modules[0][0] if modules else "",
        "open_gaps": [],
        "owner": "",
        "version": "0.1.0",
        "status": "draft",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    registry = load_registry()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    total_notes = 0
    changed = []
    covered: set[str] = set()
    for role, (display, modules) in sorted(ROLES.items()):
        plan = build(role, display, modules, registry)
        total_notes += len(plan["notes"])
        covered.update(k for n in plan["notes"] for k in n["concept_keys"])
        path = OUT_DIR / f"{role}.corpus.json"
        rendered = json.dumps(plan, ensure_ascii=False, indent=1) + "\n"
        if not path.exists() or path.read_text(encoding="utf-8") != rendered:
            changed.append(path.name)
            if not args.check:
                path.write_text(rendered, encoding="utf-8")
    unused = sorted(set(registry) - covered)
    print(f"roles: {len(ROLES)}  planned notes: {total_notes}  "
          f"registry keys used: {len(covered)}/{len(registry)}")
    if unused:
        print(f"  keys no role plans: {', '.join(unused)}")
    if args.check and changed:
        print("FAILED: corpus plans are out of date")
        sys.exit(1)
    if changed:
        print("wrote: " + ", ".join(changed))


if __name__ == "__main__":
    main()
