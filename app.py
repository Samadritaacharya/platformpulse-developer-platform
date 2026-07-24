"""Streamlit entry point for PlatformPulse."""
from __future__ import annotations

import runpy

# Streamlit reruns this file in the same process. run_module executes the UI in
# a fresh namespace on each interaction without reloading native extensions.
runpy.run_module("platformpulse.ui", run_name="__main__")
