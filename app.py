"""Streamlit entry point for PlatformPulse."""
from __future__ import annotations

import importlib
import sys

MODULE = "platformpulse.ui"

# Streamlit reruns this entry point in the same Python process. Reloading the UI
# module prevents a cached import from leaving the page blank after interaction.
if MODULE in sys.modules:
    importlib.reload(sys.modules[MODULE])
else:
    importlib.import_module(MODULE)
