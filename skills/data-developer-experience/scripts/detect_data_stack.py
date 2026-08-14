#!/usr/bin/env python3
"""Detect candidate Data stack adapters from repository evidence only."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

EXCLUDED = {".git", ".venv", "venv", "node_modules", "dist", "build", "__pycache__"}
RULES = {
    "airflow": {"names": {"airflow.cfg", "astro-project.yaml"}, "paths": {"dags"}, "contains": ("apache-airflow",)},
    "dbt": {"names": {"dbt_project.yml", "packages.yml"}, "paths": {"models", "macros"}, "contains": ("dbt-core", "dbt-")},
    "spark": {"names": {"spark-defaults.conf"}, "paths": set(), "contains": ("pyspark", "spark-submit", "SparkSession")},
    "kafka-flink": {"names": set(), "paths": set(), "contains": ("confluent-kafka", "kafka-python", "apache-flink", "pyflink")},
    "snowflake": {"names": {"snowflake.yml"}, "paths": set(), "contains": ("snowflake-connector", "snowflake.snowpark", "SNOWFLAKE_")},
    "bigquery": {"names": set(), "paths": set(), "contains": ("google-cloud-bigquery", "bigquery", "INFORMATION_SCHEMA.JOBS")},
    "databricks": {"names": {"databricks.yml", "databricks.yaml"}, "paths": {"resources"}, "contains": ("databricks-sdk", "DATABRICKS_")},
    "microsoft-fabric": {"names": set(), "paths": set(), "contains": ("onelake", "fabric-rest-api", "mssparkutils")},
    "power-bi": {"names": set(), "paths": set(), "contains": (".pbip", ".tmdl", "dataset.pbix")},
    "metadata-catalog": {"names": {"metadata_ingestion.yml"}, "paths": set(), "contains": ("datahub", "openmetadata")},
    "mlflow-kubeflow": {"names": {"pipeline.yaml"}, "paths": set(), "contains": ("mlflow", "kubeflow", "kfp")},
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository", type=Path)
    args = parser.parse_args()
    root = args.repository.resolve()
    if not root.is_dir():
        print(f"ERROR: repository directory does not exist: {root}")
        sys.exit(1)
    evidence = {name: [] for name in RULES}
    for current, dirs, names in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in EXCLUDED)
        base = Path(current)
        rel_dir = base.relative_to(root).as_posix()
        for adapter, rule in RULES.items():
            if base.name in rule["paths"]:
                evidence[adapter].append(f"directory:{rel_dir}")
        for name in sorted(names):
            path = base / name
            relative = path.relative_to(root).as_posix()
            for adapter, rule in RULES.items():
                if name in rule["names"] or any(token.lower() in relative.lower() for token in rule["contains"] if token.startswith(".")):
                    evidence[adapter].append(f"file:{relative}")
            if path.suffix.lower() not in {".txt", ".toml", ".yml", ".yaml", ".json", ".py", ".sql"} or path.stat().st_size > 1_000_000:
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for adapter, rule in RULES.items():
                hits = [token for token in rule["contains"] if token and token.lower() in text.lower()]
                if hits:
                    evidence[adapter].append(f"content:{relative}:{','.join(sorted(set(hits)))}")
    detected = []
    for adapter, hits in evidence.items():
        unique = sorted(set(hits))
        if unique:
            detected.append({"adapter": adapter, "confidence": "high" if len(unique) >= 2 else "candidate", "evidence": unique[:20]})
    print(json.dumps({"repository": str(root), "detected": detected, "limitations": ["Detection selects candidate adapters; bind exact runtime/provider versions before execution.", "No repository code was executed."]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
