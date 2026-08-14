#!/usr/bin/env python3
"""Delegate to the shared Data Engineering execution-plan inspector."""

from __future__ import annotations

import runpy
from pathlib import Path


shared = Path(__file__).resolve().parents[2] / "data-engineering" / "scripts" / "inspect_execution_plan.py"
if not shared.is_file():
    raise SystemExit("data-engineering/scripts/inspect_execution_plan.py is required; install the complete suite")
runpy.run_path(str(shared), run_name="__main__")
