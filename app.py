"""Streamlit entry point for PlatformPulse."""
from __future__ import annotations

import importlib
import sys

MODULE_NAME = "platformpulse.ui"
importlib.import_module(MODULE_NAME)
# Streamlit executes this entry point again for every interaction. Removing only
# the UI module from the cache allows a normal fresh import on the next rerun
# while leaving native dependencies such as pandas and pyarrow untouched.
sys.modules.pop(MODULE_NAME, None)
