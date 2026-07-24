"""Streamlit user interface for PlatformPulse."""
from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd
import plotly.express as px
import streamlit as st

from platformpulse.data import (
    load_ab_test_events,
    load_ai_use_cases,
    load_feedback,
    load_pipeline_metrics,
    load_services,
    load_survey,
)
from platformpulse.experiments import analyze_experiment, persona_lift, variant_summary
from platformpulse.generator import ServiceConfig, generate_service_zip, generated_file_preview, generated_paths, sanitize_service_name
from platformpulse.governance import assess_inventory, governance_kpis
from platformpulse.metrics import journey_stage_summary, platform_kpis
from platformpulse.prioritization import opportunity_score, rank_opportunities
from platformpulse.reliability import catalogue_health, demo_reference_time

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
.pp-hero{padding:1.35rem 1.5rem;border:1px solid #d9e0ea;border-radius:18px;
background:linear-gradient(120deg,#f7f9ff,#fff);box-shadow:0 8px 28px rgba(23,32,51,.06)}
.pp-kicker{font-size:.78rem;letter-spacing:.1em;font-weight:750;text-transform:uppercase;color:#3b5ccc}
.pp-title{font-size:clamp(2rem,4vw,3rem);font-weight:790;color:#172033;margin:.25rem 0}
.pp-subtitle{font-size:1.02rem;line-height:1.55;color:#566176;max-width:1000px}
.pp-badge{display:inline-block;margin:.7rem .35rem 0 0;padding:.25rem .65rem;border-radius:999px;
background:#eef4ff;border:1px solid #c7d7fe;color:#1849a9;font-size:.76rem;font-weight:650}
div[data-testid="stMetric"]{border:1px solid #d9e0ea;padding:.8rem;border-radius:14px;background:#fff}
div[data-testid="stDataFrame"]{border:1px solid #d9e0ea;border-radius:12px;overflow:hidden}
section[data-testid="stSidebar"]{border-right:1px solid #d9e0ea}
.stButton>button,.stDownloadButton>button{border-radius:10px;font-weight:650}
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def _load() -> tuple[pd.DataFrame, ...]:
    return (
        load_survey(), load_services(), load_pipeline_metrics(), load_feedback(),
        load_ab_test_events(), load_ai_use_cases(),
    )


def _chart(fig):
    fig.update_layout(
        margin=dict(l=16, r=16, t=55, b=16), legend_title_text="",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def _metrics(items: list[tuple[str, str, str | None]]) -> None:
    cols = st.columns(len(items))
    for col, (label, value, delta) in zip(cols, items):
        col.metric(label, value, delta=delta)


try:
    survey, services, pipelines, feedback, experiments, ai_inventory = _load()
    as_of = demo_reference_time(services, pipelines)
    health = catalogue_health(services, now=as_of)
    ranked = rank_opportunities(feedback)
    kpis = platform_kpis(survey, services, pipelines)
    experiment = analyze_experiment(experiments)
    assessed_ai = assess_inventory(ai_inventory)
    ai_metrics = governance_kpis(assessed_ai)
except (FileNotFoundError, ValueError, KeyError, TypeError) as exc:
    st.error("Validated demo data could not be loaded.")
    st.exception(exc)
    st.stop()

st.markdown(
    """
<div class="pp-hero">
  <div class="pp-kicker">Developer Experience · Platform Product Management · Secure Delivery</div>
  <div class="pp-title">PlatformPulse</div>
  <div class="pp-subtitle">An end-to-end Developer Platform product lab connecting discovery,
  secure self-service, service ownership, CI/CD health, A/B experimentation, AI governance and roadmap decisions.</div>
  <span class="pp-badge">Synthetic demo data</span><span class="pp-badge">Secure by default</span>
  <span class="pp-badge">A/B tested</span><span class="pp-badge">AI governance</span>
</div>
""",
    unsafe_allow_html=True,
)

PAGES = [
    "Executive Overview", "Developer Discovery", "Golden Path Generator",
    "Service Catalogue", "Platform Metrics", "Experiment Lab",
    "Roadmap & Decisions", "AI Governance & Security", "Reliability",
]
st.sidebar.title("PlatformPulse")
page = st.sidebar.radio("Explore", PAGES)
st.sidebar.divider()
st.sidebar.caption(f"Synthetic data as of {as_of:%d %b %Y}. No employer, client or personal data.")
st.sidebar.link_button(
    "GitHub repository",
    "https://github.com/Samadritaacharya/platformpulse-developer-platform",
    use_container_width=True,
)

if page == "Executive Overview":
    st.subheader("Product outcome overview")
    _metrics([
        ("Developer Experience", f"{kpis['developer_experience_score']}/100", None),
        ("Golden-path adoption", f"{kpis['golden_path_adoption_pct']}%", None),
        ("Pipeline success", f"{kpis['pipeline_success_pct']}%", None),
        ("Services at risk", str(int((health['health_status'] != 'Green').sum())), None),
    ])
    _metrics([
        ("A/B conversion uplift", f"+{experiment.absolute_uplift_pp} pp", "Treatment"),
        ("Deploy-time reduction", f"{experiment.time_reduction_pct}%", "Treatment"),
        ("AI use cases", str(ai_metrics["total_use_cases"]), None),
        ("High/Critical AI risks", str(ai_metrics["high_or_critical"]), None),
    ])
    left, right = st.columns([1.15, 1])
    with left:
        stage = journey_stage_summary(survey)
        fig = px.bar(stage.sort_values("opportunity_score"), x="opportunity_score", y="journey_stage",
                     orientation="h", title="Where developer friction is concentrated")
        st.plotly_chart(_chart(fig), use_container_width=True, config={"displayModeBar": False})
    with right:
        counts = health["health_status"].value_counts().rename_axis("status").reset_index(name="services")
        fig = px.pie(counts, values="services", names="status", hole=.58, title="Service catalogue health",
                     color="status", color_discrete_map={"Green":"#12B76A","Amber":"#F79009","Red":"#F04438"})
        st.plotly_chart(_chart(fig), use_container_width=True, config={"displayModeBar": False})
    st.success(experiment.decision)
    st.dataframe(ranked[["problem", "priority_score", "roadmap_horizon"]], use_container_width=True, hide_index=True)

elif page == "Developer Discovery":
    st.subheader("Developer Experience Discovery")
    st.caption("All evidence is synthetic. Add real interviews only with consent and anonymisation.")
    persona = st.selectbox("Persona", ["All"] + sorted(survey["persona"].unique()))
    view = survey if persona == "All" else survey[survey["persona"] == persona]
    _metrics([
        ("Respondents", str(view["respondent_id"].nunique()), None),
        ("Average friction", f"{view['friction_score'].mean():.1f}/5", None),
        ("Average time lost", f"{view['minutes_lost'].mean():.0f} min/week", None),
    ])
    stage = journey_stage_summary(view)
    fig = px.scatter(stage, x="mean_minutes_lost", y="mean_friction", size="respondents",
                     color="journey_stage", hover_data=["mean_frequency", "opportunity_score"],
                     title="Journey-stage evidence map")
    st.plotly_chart(_chart(fig), use_container_width=True, config={"displayModeBar": False})
    st.dataframe(view[["persona","journey_stage","friction_score","frequency","minutes_lost","comment","source_type"]],
                 use_container_width=True, hide_index=True)
    st.download_button("Download evidence", view.to_csv(index=False).encode(), "discovery-evidence.csv", "text/csv")

elif page == "Golden Path Generator":
    st.subheader("Secure Self-Service Golden Path")
    st.caption("Generate a FastAPI starter with tests, pinned CI, non-root Docker, Kubernetes controls, Helm and ownership metadata.")
    with st.form("golden-path"):
        c1, c2 = st.columns(2)
        name = c1.text_input("Service name", "catalog-insights-api")
        team = c2.text_input("Owning team", "marketplace-platform")
        visibility = c1.selectbox("Repository visibility", ["internal", "private", "public"])
        database = c2.selectbox("Database", ["None", "PostgreSQL", "MySQL", "Redis"])
        environment = c1.selectbox("Environment", ["development", "staging", "production"])
        slo = c2.slider("Availability SLO", 99.0, 99.99, 99.9, .01)
        build = st.form_submit_button("Build secure starter", type="primary", use_container_width=True)
    if build:
        try:
            config = ServiceConfig(name, team, visibility=visibility, database=database, environment=environment, slo_target=slo)
            safe_name = sanitize_service_name(name)
            payload = generate_service_zip(config)
            st.success(f"Secure starter generated for {safe_name}.")
            tab1, tab2, tab3 = st.tabs(["Artefacts", "Security preview", "Acceptance criteria"])
            with tab1:
                st.code("\n".join(generated_paths(config)), language="text")
            with tab2:
                preview = st.selectbox("Preview", ["kubernetes/deployment.yaml", "Dockerfile", ".github/workflows/ci.yml", "service-catalog.yaml"])
                st.code(generated_file_preview(config, preview), language="yaml")
            with tab3:
                st.markdown("- health and readiness checks\n- tests and pinned CI\n- non-root container\n- no privilege escalation\n- dropped capabilities\n- owner, SLO and security metadata\n- no generated secrets")
            st.download_button("Download secure starter ZIP", payload, f"{safe_name}-golden-path.zip", "application/zip", type="primary")
        except ValueError as exc:
            st.error(str(exc))

elif page == "Service Catalogue":
    st.subheader("Internal Service Catalogue")
    choice = st.selectbox("Risk filter", ["All", "Missing owner", "Failed pipeline", "Missing documentation", "No runbook", "Below SLO", "Open incidents", "Stale deployment"])
    view = health.copy()
    masks = {
        "Missing owner": view["team"].fillna("").str.strip().eq(""),
        "Failed pipeline": view["pipeline_status"].fillna("").str.lower().ne("passing"),
        "Missing documentation": view["documentation"].fillna("").str.strip().eq(""),
        "No runbook": view["runbook"].fillna("").str.strip().eq(""),
        "Below SLO": view["slo_actual"] < view["slo_target"],
        "Open incidents": view["open_incidents"] > 0,
        "Stale deployment": view["deployment_age_days"] > 45,
    }
    if choice != "All":
        view = view[masks[choice]]
    st.dataframe(view[["service_name","team","environment","pipeline_status","slo_actual","slo_target","open_incidents","health_status","health_score","risk_reasons","recommended_action"]],
                 use_container_width=True, hide_index=True)
    st.download_button("Download health report", view.to_csv(index=False).encode(), "service-health.csv", "text/csv")

elif page == "Platform Metrics":
    st.subheader("Developer Platform Metrics")
    _metrics([
        ("Ownership coverage", f"{kpis['ownership_coverage_pct']}%", None),
        ("Documentation coverage", f"{kpis['documentation_coverage_pct']}%", None),
        ("Change-failure rate", f"{kpis['change_failure_rate_pct']}%", None),
        ("Median MTTR", f"{kpis['median_mttr_min']} min", None),
    ])
    trend = pipelines.groupby("date", as_index=False).agg(
        pipeline_success=("pipeline_success","mean"), pipeline_duration_min=("pipeline_duration_min","median"),
        lead_time_hours=("lead_time_hours","median"), mttr_minutes=("mttr_minutes","median"))
    trend["pipeline_success_pct"] = trend["pipeline_success"] * 100
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(_chart(px.line(trend, x="date", y="pipeline_success_pct", markers=True, title="Pipeline success")), use_container_width=True, config={"displayModeBar": False})
    with c2:
        st.plotly_chart(_chart(px.line(trend, x="date", y=["pipeline_duration_min","lead_time_hours","mttr_minutes"], markers=True, title="Flow and recovery")), use_container_width=True, config={"displayModeBar": False})

elif page == "Experiment Lab":
    st.subheader("A/B Experiment Lab")
    st.caption("Synthetic Control: manual setup. Treatment: secure golden path.")
    _metrics([
        ("Control conversion", f"{experiment.control_conversion}%", None),
        ("Treatment conversion", f"{experiment.treatment_conversion}%", f"+{experiment.absolute_uplift_pp} pp"),
        ("Two-sided p-value", f"{experiment.p_value:.4f}", "< 0.05"),
        ("95% uplift interval", f"{experiment.ci_low_pp} to {experiment.ci_high_pp} pp", None),
    ])
    if experiment.srm_p_value < .01:
        st.error(f"Sample-ratio mismatch detected (p={experiment.srm_p_value:.4f}).")
    else:
        st.success(f"Assignment check passed (SRM p={experiment.srm_p_value:.4f}). {experiment.decision}.")
    summary = variant_summary(experiments)
    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(summary, x="variant", y="conversion_rate", text="conversion_rate", title="Successful first deployment")
        fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        st.plotly_chart(_chart(fig), use_container_width=True, config={"displayModeBar": False})
    with c2:
        guardrails = pd.DataFrame({
            "Metric":["Deploy time (min)","Support rate (%)","Satisfaction (/5)"],
            "Control":[experiment.control_time_min,experiment.control_support_rate,experiment.control_satisfaction],
            "Treatment":[experiment.treatment_time_min,experiment.treatment_support_rate,experiment.treatment_satisfaction],
        })
        st.dataframe(guardrails, use_container_width=True, hide_index=True)
        st.info(f"Treatment reduced deploy time by {experiment.time_reduction_pct}% and support demand by {experiment.support_reduction_pp} pp.")
    st.dataframe(persona_lift(experiments), use_container_width=True, hide_index=True)
    st.download_button("Download experiment events", experiments.to_csv(index=False).encode(), "ab-test-events.csv", "text/csv")

elif page == "Roadmap & Decisions":
    st.subheader("Feedback-to-Roadmap Workflow")
    st.dataframe(ranked[["id","problem","evidence_count","priority_score","roadmap_horizon","status"]], use_container_width=True, hide_index=True)
    options = {
        "Golden-path service creation": (120,4.5,85,8,5,4),
        "Faster CI feedback": (180,3.8,80,10,5,5),
        "Ownership and documentation": (220,3.2,90,6,4,4),
    }
    selected = st.selectbox("Decision scenario", list(options))
    defaults = options[selected]
    a,b,c = st.columns(3)
    reach = a.number_input("Reach", 1, 1000, defaults[0])
    impact = b.slider("Impact", 1.0, 5.0, defaults[1], .1)
    confidence = c.slider("Confidence", 10, 100, defaults[2], 5)
    effort = a.slider("Effort", 1, 20, defaults[3])
    alignment = b.slider("Alignment", 1, 5, defaults[4])
    risk = c.slider("Reliability risk", 1, 5, defaults[5])
    score = opportunity_score(reach, impact, confidence, effort, alignment, risk)
    st.metric("Decision score", score)
    st.info("Prioritise now and validate incrementally." if score >= 70 else "Keep in Next and reduce uncertainty." if score >= 35 else "Keep in Later.")

elif page == "AI Governance & Security":
    st.subheader("AI Governance & Cybersecurity Control Centre")
    st.caption("Transparent synthetic scoring—not legal advice or a compliance claim.")
    _metrics([
        ("AI use cases", str(ai_metrics["total_use_cases"]), None),
        ("High/Critical", str(ai_metrics["high_or_critical"]), None),
        ("Human oversight", f"{ai_metrics['human_oversight_coverage_pct']}%", None),
        ("Audit logging", f"{ai_metrics['audit_logging_coverage_pct']}%", None),
    ])
    c1, c2 = st.columns([1,1.5])
    with c1:
        counts = assessed_ai["risk_level"].value_counts().rename_axis("risk_level").reset_index(name="use_cases")
        fig = px.bar(counts, x="risk_level", y="use_cases", color="risk_level", title="AI risk distribution",
                     color_discrete_map={"Low":"#12B76A","Moderate":"#F79009","High":"#F04438","Critical":"#7A271A"})
        st.plotly_chart(_chart(fig), use_container_width=True, config={"displayModeBar": False})
    with c2:
        st.dataframe(assessed_ai[["use_case_id","name","owner","stage","risk_level","risk_score","governance_decision"]], use_container_width=True, hide_index=True)
    use_case = st.selectbox("Review use case", assessed_ai["use_case_id"])
    row = assessed_ai[assessed_ai["use_case_id"] == use_case].iloc[0]
    st.markdown(f"### {row['name']}")
    st.write(f"**Purpose:** {row['business_purpose']}")
    st.warning(str(row["governance_decision"])) if row["risk_level"] in {"High","Critical"} else st.info(str(row["governance_decision"]))
    for control in str(row["required_controls"]).split(" | "):
        st.markdown(f"- {control}")
    with st.expander("Repository security posture", expanded=True):
        st.markdown("- CORS and XSRF protection enabled\n- non-root read-only containers\n- Kubernetes seccomp and least privilege\n- sanitised allow-listed generator inputs\n- pinned CI actions and least-privilege permissions\n- tests, Bandit and pip-audit")
    st.download_button("Download governance register", assessed_ai.to_csv(index=False).encode(), "ai-governance-register.csv", "text/csv")

elif page == "Reliability":
    st.subheader("Platform Reliability & Operational Action")
    service = st.selectbox("Service", health["service_name"])
    row = health[health["service_name"] == service].iloc[0]
    _metrics([
        ("Health status", str(row["health_status"]), None),
        ("Health score", f"{row['health_score']}/100", None),
        ("SLO", f"{row['slo_actual']}% / {row['slo_target']}%", None),
        ("Open incidents", str(int(row["open_incidents"])), None),
    ])
    st.write(f"**Signals:** {row['risk_reasons']}")
    st.info(str(row["recommended_action"]))
    service_pipeline = pipelines[pipelines["service_name"] == service].sort_values("date")
    fig = px.line(service_pipeline, x="date", y=["pipeline_duration_min","lead_time_hours","mttr_minutes"], markers=True, title=f"{service}: delivery and recovery")
    st.plotly_chart(_chart(fig), use_container_width=True, config={"displayModeBar": False})

st.divider()
st.caption(f"PlatformPulse · rendered {datetime.now(timezone.utc):%Y-%m-%d %H:%M UTC} · synthetic data only")
