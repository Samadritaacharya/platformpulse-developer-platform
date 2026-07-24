"""Stable Streamlit application composition for PlatformPulse."""
from __future__ import annotations

from datetime import datetime, timezone
from collections.abc import Callable

import streamlit as st

from platformpulse.ui_components import (
    AppContext,
    load_context,
    render_header,
    render_sidebar,
    setup_page,
)
from platformpulse.ui_pages_advanced import (
    render_ai_governance,
    render_experiment,
    render_reliability,
    render_roadmap,
)
from platformpulse.ui_pages_core import (
    render_discovery,
    render_golden_path,
    render_overview,
    render_platform_metrics,
    render_service_catalogue,
)

_RENDERERS: dict[str, Callable[[AppContext], None]] = {
    "Executive Overview": render_overview,
    "Developer Discovery": render_discovery,
    "Golden Path Generator": render_golden_path,
    "Service Catalogue": render_service_catalogue,
    "Platform Metrics": render_platform_metrics,
    "Experiment Lab": render_experiment,
    "Roadmap & Decisions": render_roadmap,
    "AI Governance & Security": render_ai_governance,
    "Reliability": render_reliability,
}


def render_app() -> None:
    setup_page()
    try:
        context = load_context()
    except (FileNotFoundError, ValueError, KeyError, TypeError) as exc:
        st.error("Validated demo data could not be loaded.")
        st.exception(exc)
        st.stop()
        return
    render_header()
    page = render_sidebar(context.as_of)
    _RENDERERS[page](context)
    st.divider()
    st.caption(
        f"PlatformPulse · rendered {datetime.now(timezone.utc):%Y-%m-%d %H:%M UTC} · synthetic data only"
    )
