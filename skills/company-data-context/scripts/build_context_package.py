#!/usr/bin/env python3
"""Delegate to the shared context packager copied with this standalone skill."""

from __future__ import annotations

import runpy
from pathlib import Path


shared = Path(__file__).resolve().parents[2] / "shared-data-core" / "scripts" / "build_context_package.py"
if not shared.is_file():
    raise SystemExit("shared-data-core/scripts/build_context_package.py is required; install the complete suite")
runpy.run_path(str(shared), run_name="__main__")
