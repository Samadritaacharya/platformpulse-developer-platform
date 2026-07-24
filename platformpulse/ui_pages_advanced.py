"""Experimentation, governance, prioritisation and reliability views."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from platformpulse.experiments import persona_lift, variant_summary
from platformpulse.prioritization import opportunity_score
from platformpulse.ui_components import AppContext, chart, metrics, table


def render_experiment(context: AppContext) -> None:
    result = context.experiment
    st.subheader("A/B Experiment Lab")
    st.caption("Synthetic Control: manual setup. Treatment: secure golden path.")
    metrics([
        ("Control conversion", f"{result.control_conversion}%", None),
        ("Treatment conversion", f"{result.treatment_conversion}%", f"+{result.absolute_uplift_pp} pp"),
        ("Two-sided p-value", f"{result.p_value:.4f}", "< 0.05"),
        ("95% uplift interval", f"{result.ci_low_pp} to {result.ci_high_pp} pp", None),
    ])
    if result.srm_p_value < .01:
        st.error(f"Sample-ratio mismatch detected (p={result.srm_p_value:.4f}).")
    else:
        st.success(f"Assignment check passed (SRM p={result.srm_p_value:.4f}). {result.decision}.")
    summary = variant_summary(context.experiments)
    left, right = st.columns(2)
    with left:
        fig = px.bar(summary, x="variant", y="conversion_rate", text="conversion_rate", title="Successful first deployment")
        fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        st.plotly_chart(chart(fig), width="stretch", config={"displayModeBar": False})
    with right:
        guardrails = pd.DataFrame({
            "Metric": ["Deploy time (min)", "Support rate (%)", "Satisfaction (/5)"],
            "Control": [result.control_time_min, result.control_support_rate, result.control_satisfaction],
            "Treatment": [result.treatment_time_min, result.treatment_support_rate, result.treatment_satisfaction],
        })
        table(guardrails)
        st.info(f"Treatment reduced deploy time by {result.time_reduction_pct}% and support demand by {result.support_reduction_pp} pp.")
    table(persona_lift(context.experiments))
    st.download_button(
        "Download experiment events",
        context.experiments.to_csv(index=False).encode(),
        "ab-test-events.csv",
        "text/csv",
    )


def render_roadmap(context: AppContext) -> None:
    st.subheader("Feedback-to-Roadmap Workflow")
    table(context.ranked[["id", "problem", "evidence_count", "priority_score", "roadmap_horizon", "status"]])
    options = {
        "Golden-path service creation": (120, 4.5, 85, 8, 5, 4),
        "Faster CI feedback": (180, 3.8, 80, 10, 5, 5),
        "Ownership and documentation": (220, 3.2, 90, 6, 4, 4),
    }
    selected = st.selectbox("Decision scenario", list(options))
    defaults = options[selected]
    left, middle, right = st.columns(3)
    reach = left.number_input("Reach", 1, 1000, defaults[0])
    impact = middle.slider("Impact", 1.0, 5.0, defaults[1], .1)
    confidence = right.slider("Confidence", 10, 100, defaults[2], 5)
    effort = left.slider("Effort", 1, 20, defaults[3])
    alignment = middle.slider("Alignment", 1, 5, defaults[4])
    risk = right.slider("Reliability risk", 1, 5, defaults[5])
    score = opportunity_score(reach, impact, confidence, effort, alignment, risk)
    st.metric("Decision score", score)
    if score >= 70:
        st.info("Prioritise now and validate incrementally.")
    elif score >= 35:
        st.info("Keep in Next and reduce uncertainty.")
    else:
        st.info("Keep in Later.")


def render_ai_governance(context: AppContext) -> None:
    st.subheader("AI Governance & Cybersecurity Control Centre")
    st.caption("Transparent synthetic scoring—not legal advice or a compliance claim.")
    metrics([
        ("AI use cases", str(context.ai_metrics["total_use_cases"]), None),
        ("High/Critical", str(context.ai_metrics["high_or_critical"]), None),
        ("Human oversight", f"{context.ai_metrics['human_oversight_coverage_pct']}%", None),
        ("Audit logging", f"{context.ai_metrics['audit_logging_coverage_pct']}%", None),
    ])
    left, right = st.columns([1, 1.5])
    with left:
        counts = context.assessed_ai["risk_level"].value_counts().rename_axis("risk_level").reset_index(name="use_cases")
        fig = px.bar(
            counts,
            x="risk_level",
            y="use_cases",
            color="risk_level",
            title="AI risk distribution",
            color_discrete_map={"Low": "#12B76A", "Moderate": "#F79009", "High": "#F04438", "Critical": "#7A271A"},
        )
        st.plotly_chart(chart(fig), width="stretch", config={"displayModeBar": False})
    with right:
        table(context.assessed_ai[["use_case_id", "name", "owner", "stage", "risk_level", "risk_score", "governance_decision"]])
    use_case = st.selectbox("Review use case", context.assessed_ai["use_case_id"])
    row = context.assessed_ai[context.assessed_ai["use_case_id"] == use_case].iloc[0]
    st.markdown(f"### {row['name']}")
    st.write(f"**Purpose:** {row['business_purpose']}")
    if row["risk_level"] in {"High", "Critical"}:
        st.warning(str(row["governance_decision"]))
    else:
        st.info(str(row["governance_decision"]))
    for control in str(row["required_controls"]).split(" | "):
        st.markdown(f"- {control}")
    with st.expander("Repository security posture", expanded=True):
        st.markdown("- CORS and XSRF protection enabled\n- non-root read-only containers\n- Kubernetes seccomp and least privilege\n- sanitised allow-listed generator inputs\n- pinned CI actions and least-privilege permissions\n- tests, Bandit and pip-audit")
    st.download_button(
        "Download governance register",
        context.assessed_ai.to_csv(index=False).encode(),
        "ai-governance-register.csv",
        "text/csv",
    )


def render_reliability(context: AppContext) -> None:
    st.subheader("Platform Reliability & Operational Action")
    service = st.selectbox("Service", context.health["service_name"])
    row = context.health[context.health["service_name"] == service].iloc[0]
    metrics([
        ("Health status", str(row["health_status"]), None),
        ("Health score", f"{row['health_score']}/100", None),
        ("SLO", f"{row['slo_actual']}% / {row['slo_target']}%", None),
        ("Open incidents", str(int(row["open_incidents"])), None),
    ])
    st.write(f"**Signals:** {row['risk_reasons']}")
    st.info(str(row["recommended_action"]))
    pipeline = context.pipelines[context.pipelines["service_name"] == service].sort_values("date")
    fig = px.line(
        pipeline,
        x="date",
        y=["pipeline_duration_min", "lead_time_hours", "mttr_minutes"],
        markers=True,
        title=f"{service}: delivery and recovery",
    )
    st.plotly_chart(chart(fig), width="stretch", config={"displayModeBar": False})
