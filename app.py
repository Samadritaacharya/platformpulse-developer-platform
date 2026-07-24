"""Streamlit entry point for PlatformPulse."""
from __future__ import annotations

import importlib.util
from pathlib import Path

UI_PATH = Path(__file__).resolve().parent / "platformpulse" / "ui.py"
SPEC = importlib.util.spec_from_file_location("_platformpulse_ui_runtime", UI_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Unable to load the PlatformPulse UI module")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
