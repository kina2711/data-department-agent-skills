#!/usr/bin/env python3
"""Invariants that must hold for every task, and the mutations that prove each one has teeth.

Named eval cases cover 205 of 865 contracts. Closing that gap by hand would mean writing 660 cases
whose expected values were copied out of the generator that produced the contracts — 660 restatements
that assert nothing and fail only when someone changes both halves inconsistently, which is the one
case they were supposed to catch.

A property covers every task instead of one, and it says something the generator does not: not "this
task is R3" but "no task reaches production without a controlled path". Each was checked against the
catalog before being written down, and three rules that seemed obvious turned out to be false — model
tier is independent of risk tier, `enforce` names building a control rather than performing a write,
and the deep execution contract tracks `deep` *or* `enforced` criticality. Those are recorded below
as non-properties, because a rule the data refuses is worth as much as one it accepts.

Every property carries a mutation: an edit to one task that it must reject. A property nothing can
break is decoration, and `--self-test` fails the run if any property accepts its own mutation.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]

SELF_TEST_SAMPLES = 12

WRITE_VERB = re.compile(r"^\w+-(deploy|publish|promote|delete|retire|backfill|grant|revoke|migrate|rollback)-")


@dataclass(frozen=True)
class Property:
    id: str
    statement: str
    scope: Callable[[dict], bool]
    holds: Callable[[dict, str], bool]
    mutation: Callable[[dict, str], tuple[dict, str]]


def _t(task: dict, **over) -> Callable[[dict, str], tuple[dict, str]]:
    return lambda task_, body: ({**task_, **over}, body)


PROPERTIES: list[Property] = [
    Property(
        "path-matches-risk",
        "Execution path and risk tier agree exactly: fast is R0, standard is R1 or R2, controlled is R3 or R4. "
        "A tier can be argued about; a tier that does not change how the work runs cannot.",
        lambda t: True,
        lambda t, b: {
            "fast-path": t["risk_tier"] == "R0-light",
            "standard-path": t["risk_tier"] in ("R1-reviewed", "R2-standard"),
            "controlled-path": t["risk_tier"] in ("R3-controlled", "R4-critical"),
        }[t["execution_path"]],
        lambda t, b: ({**t, "risk_tier": "R3-controlled" if t["risk_tier"] != "R3-controlled" else "R0-light"}, b),
    ),
    Property(
        "production-write-is-controlled",
        "A task that deploys, publishes, promotes, deletes, retires, backfills, grants, revokes, migrates or "
        "rolls back runs on the controlled path. This is the rule the whole risk model exists to enforce.",
        lambda t: bool(WRITE_VERB.match(t["id"])),
        lambda t, b: t["execution_path"] == "controlled-path",
        _t({}, execution_path="standard-path"),
    ),
    Property(
        "critical-is-enforced",
        "Every R4 task carries enforced criticality. Nothing at the top tier runs on a contract that may be skipped.",
        lambda t: t["risk_tier"] == "R4-critical",
        lambda t, b: t["criticality"] == "enforced",
        _t({}, criticality="standard"),
    ),
    Property(
        "deep-contract-presence",
        "The deep execution contract appears when criticality is deep or enforced, and only then. Present elsewhere "
        "it is filler; absent here the contract is missing the part that governs how the work is actually done.",
        lambda t: True,
        lambda t, b: ("## Deep execution contract" in b) == (t["criticality"] in ("deep", "enforced")),
        lambda t, b: ({**t, "criticality": "standard" if t["criticality"] in ("deep", "enforced") else "deep"}, b),
    ),
    Property(
        "shared-standards-reachable",
        "Every contract links the three standards that apply regardless of role: lifecycle, model selection, "
        "response compression. An agent that cannot reach them from the task it was given will not go looking.",
        lambda t: True,
        lambda t, b: all(s in b for s in ("lifecycle-standard.md", "model-selection.md", "response-compression.md")),
        lambda t, b: (t, b.replace("model-selection.md", "gone.md")),
    ),
    Property(
        "classification-stated-in-body",
        "The contract states its own risk tier, lifecycle profile and execution path in words. Classification that "
        "lives only in the catalog is invisible to whoever is reading the contract and deciding what to do.",
        lambda t: True,
        lambda t, b: all(t[f] in b for f in ("risk_tier", "lifecycle_profile", "execution_path")),
        lambda t, b: (t, b.replace(t["execution_path"], "somewhere")),
    ),
    Property(
        "controlled-names-a-human",
        "A controlled-path contract names a human approver. An approval gate with no person behind it is a step "
        "an agent will mark complete on its own.",
        lambda t: t["execution_path"] == "controlled-path",
        lambda t, b: re.search(r"named human|human approv|approver", b, re.I) is not None,
        lambda t, b: (t, re.sub(r"named human|human approv|approver", "sign-off", b, flags=re.I)),
    ),
    Property(
        "fast-path-claims-no-gate",
        "A fast-path contract does not carry an approval gate. Read-only work that demands approval trains everyone "
        "to route around the gates that matter.",
        lambda t: t["execution_path"] == "fast-path",
        lambda t, b: "Approval gate" not in b,
        lambda t, b: (t, b + "\n\n## Approval gate\n"),
    ),
    Property(
        "evidence-sections-present",
        "Every contract keeps its Tests and evidence, Approval and done, and Return sections. These are where a "
        "claim becomes checkable, and a contract missing one can be satisfied by assertion.",
        lambda t: True,
        lambda t, b: all(f"## {h}" in b for h in ("Tests and evidence", "Approval and done", "Return")),
        lambda t, b: (t, b.replace("## Tests and evidence", "## Notes")),
    ),
    Property(
        "return-section-substantive",
        "The Return section says what comes back. Left near-empty it becomes the place an agent stops early.",
        lambda t: True,
        lambda t, b: len(b.split("## Return")[-1].strip()) > 40,
        lambda t, b: (t, b.split("## Return")[0] + "## Return\n\nDone.\n"),
    ),
    Property(
        "no-placeholders",
        "No contract ships a TODO, TBD or placeholder. Generated text hides an unfinished thought better than "
        "handwritten text does.",
        lambda t: True,
        lambda t, b: not re.search(r"\bTODO\b|\bTBD\b|\bXXX\b|FIXME|lorem ipsum", b),
        lambda t, b: (t, b + "\n\nTODO: finish this.\n"),
    ),
    Property(
        "title-is-the-id",
        "The first heading is the task id. Contracts are loaded by id, and a title that has drifted from it means "
        "the file being read is not the file that was routed to.",
        lambda t: True,
        lambda t, b: b.splitlines()[0].strip() == "# " + t["id"],
        lambda t, b: (t, "# renamed\n" + b.split("\n", 1)[1]),
    ),
]

# Rules the catalog refused. Each looked obvious and each is false, so none of them is a property.
NON_PROPERTIES = [
    ("model tier follows risk tier",
     "75 R0 tasks run on a strong model. Low risk is not low judgment — validating SQL safely is cheap to run "
     "and expensive to get wrong. Model tier is chosen independently and stays that way."),
    ("`enforce` is a production write",
     "The three enforce- tasks build or check a control; they do not write to production. The verb list was too "
     "broad and was cut, rather than the three tasks being reclassified to fit it."),
    ("deep criticality implies a strong model",
     "128 deep tasks run on a standard model. Depth describes the contract the work follows, not the model the "
     "work needs."),
    ("enforced criticality implies R2 or above",
     "Three orchestrator tasks are R0 and enforced: composing a workflow reads and writes nothing, and still has "
     "to follow its contract exactly."),
]


def load() -> list[tuple[dict, str]]:
    catalog = json.load(open(ROOT / "task-catalog.json", encoding="utf-8"))
    bodies = {p.stem: p for p in (ROOT / "skills").glob("*/references/tasks/*.md")}
    missing = [t["id"] for t in catalog if t["id"] not in bodies]
    if missing:
        raise SystemExit(f"no contract on disk for: {missing[:5]}")
    return [(t, bodies[t["id"]].read_text(encoding="utf-8")) for t in catalog]


def evaluate(pairs: list[tuple[dict, str]]) -> list[dict]:
    results = []
    for prop in PROPERTIES:
        scoped = [(t, b) for t, b in pairs if prop.scope(t)]
        failures = [t["id"] for t, b in scoped if not prop.holds(t, b)]
        results.append({"id": prop.id, "scope": len(scoped), "failures": failures,
                        "statement": prop.statement})
    return results


def self_test(pairs: list[tuple[dict, str]]) -> list[str]:
    """A property that cannot reject anything is not testing anything."""
    toothless = []
    for prop in PROPERTIES:
        scoped = [(t, b) for t, b in pairs if prop.scope(t)]
        if not scoped:
            toothless.append(f"{prop.id}: scope matches no task")
            continue
        # One sample can pass by luck — a mutation that happens to be a no-op on the first task in
        # the catalog looked fine until this sampled across the scope.
        step = max(1, len(scoped) // SELF_TEST_SAMPLES)
        accepted = [
            task["id"]
            for task, body in scoped[::step][:SELF_TEST_SAMPLES]
            for mutated_task, mutated_body in [prop.mutation(task, body)]
            if prop.scope(mutated_task) and prop.holds(mutated_task, mutated_body)
        ]
        if accepted:
            toothless.append(f"{prop.id}: accepts its own mutation on {len(accepted)} sampled tasks "
                             f"({', '.join(accepted[:3])})")
    return toothless
