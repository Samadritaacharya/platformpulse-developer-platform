"""Reusable Streamlit components and validated application context."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from platformpulse.data import (
    load_ab_test_events,
    load_ai_use_cases,
    load_feedback,
    load_pipeline_metrics,
    load_services,
    load_survey,
)
from platformpulse.experiments import ExperimentResult, analyze_experiment
from platformpulse.governance import assess_inventory, governance_kpis
from platformpulse.metrics import platform_kpis
from platformpulse.prioritization import rank_opportunities
from platformpulse.reliability import catalogue_health, demo_reference_time

PAGES = (
    "Executive Overview",
    "Developer Discovery",
    "Golden Path Generator",
    "Service Catalogue",
    "Platform Metrics",
    "Experiment Lab",
    "Roadmap & Decisions",
    "AI Governance & Security",
    "Reliability",
)


@dataclass(frozen=True)
class AppContext:
    survey: pd.DataFrame
    services: pd.DataFrame
    pipelines: pd.DataFrame
    feedback: pd.DataFrame
    experiments: pd.DataFrame
    ai_inventory: pd.DataFrame
    as_of: datetime
    health: pd.DataFrame
    ranked: pd.DataFrame
    kpis: dict[str, object]
    experiment: ExperimentResult
    assessed_ai: pd.DataFrame
    ai_metrics: dict[str, float | int]


@st.cache_data(show_spinner=False)
def load_context() -> AppContext:
    survey = load_survey()
    services = load_services()
    pipelines = load_pipeline_metrics()
    feedback = load_feedback()
    experiments = load_ab_test_events()
    ai_inventory = load_ai_use_cases()
    as_of = demo_reference_time(services, pipelines)
    assessed_ai = assess_inventory(ai_inventory)
    return AppContext(
        survey=survey,
        services=services,
        pipelines=pipelines,
        feedback=feedback,
        experiments=experiments,
        ai_inventory=ai_inventory,
        as_of=as_of,
        health=catalogue_health(services, now=as_of),
        ranked=rank_opportunities(feedback),
        kpis=platform_kpis(survey, services, pipelines),
        experiment=analyze_experiment(experiments),
        assessed_ai=assessed_ai,
        ai_metrics=governance_kpis(assessed_ai),
    )


def setup_page() -> None:
    st.set_page_config(
        page_title="PlatformPulse",
        page_icon="🧭",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            "Get help": "https://github.com/Samadritaacharya/platformpulse-developer-platform",
            "Report a bug": "https://github.com/Samadritaacharya/platformpulse-developer-platform/issues",
            "About": "Independent Developer Platform portfolio prototype using synthetic data.",
        },
    )
    st.markdown(
        """
<style>
.block-container{padding-top:1rem;padding-bottom:2.5rem;max-width:1500px}
.pp-hero{padding:1.35rem 1.5rem;border:1px solid #d9e0ea;border-radius:18px;background:linear-gradient(120deg,#f7f9ff,#fff);box-shadow:0 8px 28px rgba(23,32,51,.06)}
.pp-kicker{font-size:.78rem;letter-spacing:.1em;font-weight:750;text-transform:uppercase;color:#3b5ccc}
.pp-title{font-size:clamp(2rem,4vw,3rem);font-weight:790;color:#172033;margin:.25rem 0}
.pp-subtitle{font-size:1.02rem;line-height:1.55;color:#566176;max-width:1000px}
.pp-badge{display:inline-block;margin:.7rem .35rem 0 0;padding:.25rem .65rem;border-radius:999px;background:#eef4ff;border:1px solid #c7d7fe;color:#1849a9;font-size:.76rem;font-weight:650}
div[data-testid="stMetric"]{border:1px solid #d9e0ea;padding:.8rem;border-radius:14px;background:#fff}
.pp-table-wrap{overflow:auto;max-height:460px;border:1px solid #d9e0ea;border-radius:12px;background:#fff}
table.pp-table{border-collapse:collapse;width:100%;font-size:.84rem}
table.pp-table th{position:sticky;top:0;background:#f5f7fa;text-align:left;padding:.65rem;border-bottom:1px solid #d9e0ea}
table.pp-table td{padding:.62rem;border-bottom:1px solid #edf0f5;vertical-align:top}
section[data-testid="stSidebar"]{border-right:1px solid #d9e0ea}
.stButton>button,.stDownloadButton>button{border-radius:10px;font-weight:650}
</style>
""",
        unsafe_allow_html=True,
    )


def render_header() -> None:
    st.markdown(
        """
<div class="pp-hero">
  <div class="pp-kicker">Developer Experience · Platform Product Management · Secure Delivery</div>
  <div class="pp-title">PlatformPulse</div>
  <div class="pp-subtitle">An end-to-end Developer Platform product lab connecting discovery, secure self-service, service ownership, CI/CD health, A/B experimentation, AI governance and roadmap decisions.</div>
  <span class="pp-badge">Synthetic demo data</span><span class="pp-badge">Secure by default</span>
  <span class="pp-badge">A/B tested</span><span class="pp-badge">AI governance</span>
</div>
""",
        unsafe_allow_html=True,
    )


def render_sidebar(as_of: datetime) -> str:
    st.sidebar.title("PlatformPulse")
    page = st.sidebar.radio("Explore", PAGES)
    st.sidebar.divider()
    st.sidebar.caption(f"Synthetic data as of {as_of:%d %b %Y}. No employer, client or personal data.")
    st.sidebar.link_button(
        "GitHub repository",
        "https://github.com/Samadritaacharya/platformpulse-developer-platform",
        width="stretch",
    )
    return page


def chart(fig: go.Figure) -> go.Figure:
    fig.update_layout(
        margin=dict(l=16, r=16, t=55, b=16),
        legend_title_text="",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def metrics(items: list[tuple[str, str, str | None]]) -> None:
    columns = st.columns(len(items))
    for column, (label, value, delta) in zip(columns, items):
        column.metric(label, value, delta=delta)


def table(frame: pd.DataFrame) -> None:
    """Render escaped HTML without Arrow/native dataframe serialisation."""
    html = frame.to_html(index=False, escape=True, border=0, classes="pp-table")
    st.markdown(f'<div class="pp-table-wrap">{html}</div>', unsafe_allow_html=True)
