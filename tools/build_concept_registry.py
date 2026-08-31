#!/usr/bin/env python3
"""Author the canonical concept registry: one key, one sentence that disambiguates it.

The registry is the identity layer the corpus, the schema index and learner memory all bind to.
Its value is entirely in the definitions: a key called `ck.sql.grain` with no sentence cannot tell
two notes whether they mean the same thing, and the whole crosswalk collapses into name matching.

Keys enter as `proposed`. A batch is reviewed and promoted deliberately; nothing here is
`registered`, because nobody has read it yet.

This file is the source. Edit it and regenerate; do not edit the JSON.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "concept-registry.json"

# (key suffix, display name, one-sentence definition, aliases, parents)
DOMAINS: dict[str, list[tuple]] = {
    "sql": [
        ("grain", "Grain", "What exactly one row of a table represents, stated as a sentence.", ["hạt", "granularity"], []),
        ("join-semantics", "Join semantics", "Which rows survive a join and how many copies each produces, decided by key cardinality rather than by join keyword.", ["join"], []),
        ("fan-out", "Join fan-out", "Row multiplication caused by joining to a table whose key is not unique, silently inflating every downstream sum.", ["duplicate join"], ["ck.sql.join-semantics"]),
        ("null-semantics", "Null semantics", "Null is unknown rather than empty, so it propagates through arithmetic and is never equal to anything including itself.", [], []),
        ("cte-vs-subquery", "CTE versus subquery", "A named intermediate result that may or may not be materialised, changing readability always and performance sometimes.", [], []),
        ("window-function", "Window function", "A calculation over a set of rows related to the current row, without collapsing them into one.", ["hàm cửa sổ"], []),
        ("aggregation-grain-error", "Aggregation grain error", "Aggregating at a grain finer or coarser than the question asked, producing a number that is arithmetically correct and answers nothing.", [], ["ck.sql.grain"]),
        ("set-operations", "Set operations", "Union, intersect and except treat rows as members of a set, which is why union removes duplicates and union all does not.", [], []),
        ("index-and-scan", "Index and scan", "Whether the engine reads a targeted subset or every row, decided by predicates and physical layout rather than by query length.", [], []),
        ("query-plan", "Query plan", "The engine's chosen execution strategy, which is what to read when a query is slow rather than the SQL text.", ["execution plan"], []),
        ("transaction-isolation", "Transaction isolation", "What one transaction may see of another's uncommitted work, and the anomalies each level permits.", ["isolation level"], []),
        ("normalization", "Normalization", "Removing redundancy so a fact is stored once, trading write simplicity for join cost at read time.", ["chuẩn hoá"], []),
        ("idempotent-write", "Idempotent write", "A write that produces the same end state when repeated, which is what makes a retry safe.", [], []),
    ],
    "python": [
        ("data-model", "Python data model", "The protocol methods that make an object behave like a builtin, which is why duck typing works.", ["dunder"], []),
        ("mutability-aliasing", "Mutability and aliasing", "Two names can refer to one mutable object, so a change through one is visible through the other.", [], []),
        ("iterator-generator", "Iterator and generator", "Producing values one at a time rather than building a list, bounding memory by the item instead of the collection.", [], []),
        ("comprehension", "Comprehension", "Expression-level construction of a collection, readable at small scale and unreadable past two clauses.", [], []),
        ("typing-and-hints", "Typing and hints", "Annotations checked by a separate tool rather than at runtime, so they document intent and catch a class of error before execution.", [], []),
        ("packaging-environment", "Packaging and environment", "Which interpreter and which dependency versions the code actually runs against, and how that is reproduced elsewhere.", ["venv"], []),
        ("exception-flow", "Exception flow", "Errors as control flow that unwinds to a handler, and the cost of catching too broadly.", [], []),
        ("pandas-semantics", "Pandas semantics", "Index alignment, copy-versus-view and dtype coercion, which is where most silent wrong answers in pandas come from.", [], []),
        ("vectorisation", "Vectorisation", "Expressing a loop as an array operation so the work happens in compiled code rather than in the interpreter.", [], []),
        ("async-concurrency", "Async concurrency", "Interleaving on waiting rather than running in parallel, which helps IO-bound work and not CPU-bound work.", ["asyncio"], []),
        ("testing-pyramid", "Testing in Python", "Fast isolated tests as the base, with slower integrated ones above, and fixtures that make failures reproducible.", [], []),
    ],
    "rust": [
        ("ownership", "Ownership", "Each value has exactly one owner, and it is dropped when the owner goes out of scope.", ["sở hữu"], []),
        ("borrowing", "Borrowing", "Taking a reference without taking ownership, with either many readers or one writer but never both.", ["mượn"], ["ck.rust.ownership"]),
        ("lifetime", "Lifetime", "The compiler's proof that a reference cannot outlive what it points at.", [], ["ck.rust.borrowing"]),
        ("trait", "Trait", "Shared behaviour a type opts into, resolved statically by default so abstraction costs nothing at runtime.", [], []),
        ("error-handling", "Error handling", "Errors as values in Result rather than as exceptions, making the failure path part of the signature.", ["result"], []),
        ("fearless-concurrency", "Fearless concurrency", "Data races prevented at compile time by the same ownership rules that manage memory.", [], ["ck.rust.ownership"]),
        ("zero-cost-abstraction", "Zero-cost abstraction", "Abstractions that compile to what hand-written code would produce, so structure does not cost speed.", [], []),
    ],
    "modelling": [
        ("dimensional-model", "Dimensional model", "Facts measured at a grain, described by conformed dimensions, arranged so a business question maps to a join path.", ["star schema"], []),
        ("conformed-dimension", "Conformed dimension", "One dimension shared by several facts, which is what makes two facts comparable at all.", [], ["ck.modelling.dimensional-model"]),
        ("slowly-changing-dimension", "Slowly changing dimension", "How a dimension records change over time, and whether history is overwritten, versioned or kept alongside.", ["SCD"], []),
        ("one-big-table", "One big table", "A denormalised table where every attribute is reachable without a join, trading storage and update cost for join safety.", ["OBT"], []),
        ("fact-grain", "Fact grain", "The event or state one fact row records, fixed before any measure is added to it.", [], ["ck.sql.grain"]),
        ("semantic-layer", "Semantic layer", "The single governed definition of a metric, so two dashboards asking the same question get the same number.", [], []),
        ("surrogate-key", "Surrogate key", "A key owned by the warehouse rather than the source, so identity survives a source system changing its own.", [], []),
    ],
    "pipeline": [
        ("idempotency", "Pipeline idempotency", "Re-running a step produces the same end state rather than additional rows, which is what makes retry safe.", [], ["ck.sql.idempotent-write"]),
        ("cdc", "Change data capture", "Reading a source's changes from its log or its timestamps rather than re-reading the whole table.", [], []),
        ("watermark", "Watermark", "The boundary declaring which data is considered complete, and therefore what late arrivals will do to yesterday's numbers.", [], []),
        ("backfill", "Backfill", "Reprocessing a historical window, which restates numbers people have already seen and acted on.", [], []),
        ("delivery-semantics", "Delivery semantics", "At-most-once, at-least-once and exactly-once, and which of the three the pipeline can actually claim.", [], []),
        ("schema-evolution", "Schema evolution", "How the pipeline behaves when the source adds, renames or retypes a column, decided before it happens.", [], []),
        ("reconciliation", "Reconciliation", "Comparing source and destination at a key level for the same window, which is the only evidence a load worked.", ["đối soát"], []),
        ("orchestration", "Orchestration", "Declaring dependencies between steps so order, retry and failure behaviour are properties of the graph rather than of a script.", [], []),
        ("dead-letter", "Dead letter", "A terminal destination for records that will never succeed, so a bad record does not stop the stream forever.", [], []),
    ],
    "warehouse": [
        ("columnar-storage", "Columnar storage", "Storing values of one column together, so a query reading three columns of two hundred pays for three.", [], []),
        ("partitioning", "Partitioning", "Splitting a table by a column so a filtered query reads fewer files, and the reason a missing predicate costs a full scan.", [], []),
        ("clustering", "Clustering", "Ordering data within partitions so related rows sit together, reducing the bytes a selective query touches.", ["sort key"], ["ck.warehouse.partitioning"]),
        ("file-layout", "File layout and size", "How many files of what size a table is stored as, which decides scan overhead more often than total volume does.", ["small files"], []),
        ("compute-storage-separation", "Compute and storage separation", "Paying for scan and for storage independently, which changes what optimisation is worth doing.", [], []),
        ("scan-cost", "Scan cost", "What a query costs is bytes read, not rows returned, which is why select star on a wide table is expensive.", [], []),
    ],
    "analytics": [
        ("cohort", "Cohort analysis", "Grouping users by when they started so behaviour is compared at the same age rather than on the same date.", [], []),
        ("funnel", "Funnel analysis", "Ordered steps with drop-off between them, where the definition of a step decides the conversion rate.", [], []),
        ("retention-curve", "Retention curve", "The share of a cohort still active at each period, and whether it flattens or goes to zero.", [], ["ck.analytics.cohort"]),
        ("survivorship-bias", "Survivorship bias", "Measuring only the entities that remained, which makes any average look better than the population.", [], []),
        ("simpson-paradox", "Simpson's paradox", "A trend present in every subgroup that reverses when the groups are pooled, caused by uneven group sizes.", [], []),
        ("statistical-power", "Statistical power", "The chance of detecting an effect that is really there, fixed by sample size before the test runs.", [], []),
        ("sampling-bias", "Sampling bias", "A sample whose selection is related to the outcome, which no sample size fixes.", [], []),
        ("metric-definition-drift", "Metric definition drift", "The same metric name computed differently over time, making a trend an artefact of its own definition.", [], []),
    ],
    "ml": [
        ("leakage", "Data leakage", "Information in training that would not exist at prediction time, producing validation scores the model cannot reproduce.", ["rò rỉ dữ liệu"], []),
        ("train-serve-skew", "Training-serving skew", "Features computed differently in training and in serving, so the model in production is not the model that was evaluated.", [], []),
        ("validation-split", "Validation strategy", "How data is split so the estimate generalises, which for time series means splitting by time and never at random.", [], []),
        ("overfitting", "Overfitting", "Fitting noise in the training data, visible as a gap between training and held-out performance.", [], []),
        ("feature-store", "Feature store", "One definition of a feature served to both training and inference, which is how skew is prevented rather than detected.", [], ["ck.ml.train-serve-skew"]),
        ("drift", "Drift", "The world moving away from the data the model was fitted on, in the inputs or in the relationship itself.", [], []),
        ("explainability", "Explainability", "An account of why this prediction, at the fidelity the decision requires rather than at the fidelity available.", [], []),
    ],
    "arch": [
        ("data-contract", "Data contract", "An agreement about schema, grain, semantics and delivery between a producer and its consumers, versioned like an API.", [], []),
        ("coupling", "Coupling", "How much one component must know about another's internals, which decides what a change costs.", [], []),
        ("consistency-model", "Consistency model", "What a reader may see after a write, and therefore which questions the system can answer correctly.", [], []),
        ("idempotent-interface", "Idempotent interface", "An operation safe to repeat, which is what makes retry a strategy rather than a risk.", [], ["ck.pipeline.idempotency"]),
        ("failure-domain", "Failure domain", "The blast radius of one component failing, and what continues working when it does.", [], []),
        ("lineage", "Lineage", "Which upstream data produced which downstream artifact, generated from the systems rather than drawn by hand.", [], []),
    ],
    "swe": [
        ("version-control-hygiene", "Version control hygiene", "Commits that isolate one change and messages that say why, so history stays a usable record.", [], []),
        ("code-review", "Code review", "A second reader checking against stated criteria, done before the author explains their reasoning.", [], []),
        ("test-isolation", "Test isolation", "A test whose result depends on nothing outside itself, which is what makes a failure informative.", [], []),
        ("ci-feedback-loop", "CI feedback loop", "How long between a mistake and knowing about it, which decides whether tests get run or worked around.", [], []),
        ("technical-debt", "Technical debt", "Deliberately deferred work with an interest cost, distinguished from code that is merely unfamiliar.", [], []),
        ("observability", "Observability", "Whether the running system can answer a question nobody thought to ask before deploying it.", [], []),
    ],
    "product": [
        ("opportunity-sizing", "Opportunity sizing", "An estimate of what a change is worth, with its assumptions stated so the estimate can be argued with.", [], []),
        ("prioritisation-gate", "Prioritisation gate", "A hard constraint that removes an option from ranking rather than being traded off inside a score.", [], []),
        ("discovery-versus-delivery", "Discovery versus delivery", "Deciding what to build against building it, and the cost of running them as one activity.", [], []),
        ("acceptance-criteria", "Acceptance criteria", "Conditions checkable by someone who did not write them, fixed before implementation starts.", [], []),
        ("stakeholder-decision", "Stakeholder decision", "The decision a piece of analysis or a product change actually serves, named before work begins.", [], []),
        ("requirement-traceability", "Requirement traceability", "The chain from a stated need to the thing built and the test proving it, readable in both directions.", [], []),
    ],
}


def build() -> dict:
    keys = []
    for domain, entries in DOMAINS.items():
        for suffix, name, definition, aliases, parents in entries:
            keys.append({
                "concept_key": f"ck.{domain}.{suffix}",
                "display_name": name,
                "definition": definition,
                "domain": domain,
                "aliases": aliases,
                "parents": parents,
                "related": [],
                "binds": {"canon_ids": [], "note_ids": [], "topic_ids": [], "competency_ids": [], "question_ids": []},
                "primary_note_id": "",
                "status": "proposed",
                "superseded_by": "",
                "registered_at": "",
                "registered_by": "",
            })
    return {
        "registry_id": "dd-data-concepts",
        "version": "0.1.0",
        "owner": "data-department",
        "_": ("Source of truth is tools/build_concept_registry.py; regenerate rather than edit. "
              "Every key is `proposed`: a batch is promoted deliberately after review, and only "
              "`registered` keys count toward coverage."),
        "keys": keys,
        "status": "draft",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    registry = build()
    rendered = json.dumps(registry, ensure_ascii=False, indent=1) + "\n"
    by_domain: dict[str, int] = {}
    for key in registry["keys"]:
        by_domain[key["domain"]] = by_domain.get(key["domain"], 0) + 1
    print(f"keys: {len(registry['keys'])}  domains: {len(by_domain)}")
    print("  " + "  ".join(f"{d}:{n}" for d, n in sorted(by_domain.items())))
    if OUT.exists() and OUT.read_text(encoding="utf-8") == rendered:
        return
    if args.check:
        print("FAILED: concept registry is out of date")
        sys.exit(1)
    OUT.write_text(rendered, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
