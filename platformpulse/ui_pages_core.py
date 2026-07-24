"""Core Developer Platform product views."""
from __future__ import annotations

import plotly.express as px
import streamlit as st

from platformpulse.generator import (
    ServiceConfig,
    generate_service_zip,
    generated_file_preview,
    generated_paths,
    sanitize_service_name,
)
from platformpulse.metrics import journey_stage_summary
from platformpulse.ui_components import AppContext, chart, metrics, table


def render_overview(context: AppContext) -> None:
    st.subheader("Product outcome overview")
    metrics([
        ("Developer Experience", f"{context.kpis['developer_experience_score']}/100", None),
        ("Golden-path adoption", f"{context.kpis['golden_path_adoption_pct']}%", None),
        ("Pipeline success", f"{context.kpis['pipeline_success_pct']}%", None),
        ("Services at risk", str(int((context.health['health_status'] != 'Green').sum())), None),
    ])
    metrics([
        ("A/B conversion uplift", f"+{context.experiment.absolute_uplift_pp} pp", "Treatment"),
        ("Deploy-time reduction", f"{context.experiment.time_reduction_pct}%", "Treatment"),
        ("AI use cases", str(context.ai_metrics["total_use_cases"]), None),
        ("High/Critical AI risks", str(context.ai_metrics["high_or_critical"]), None),
    ])
    left, right = st.columns([1.15, 1])
    with left:
        stage = journey_stage_summary(context.survey)
        fig = px.bar(
            stage.sort_values("opportunity_score"),
            x="opportunity_score",
            y="journey_stage",
            orientation="h",
            title="Where developer friction is concentrated",
        )
        st.plotly_chart(chart(fig), width="stretch", config={"displayModeBar": False})
    with right:
        counts = context.health["health_status"].value_counts().rename_axis("status").reset_index(name="services")
        fig = px.pie(
            counts,
            values="services",
            names="status",
            hole=.58,
            title="Service catalogue health",
            color="status",
            color_discrete_map={"Green": "#12B76A", "Amber": "#F79009", "Red": "#F04438"},
        )
        st.plotly_chart(chart(fig), width="stretch", config={"displayModeBar": False})
    st.success(context.experiment.decision)
    table(context.ranked[["problem", "priority_score", "roadmap_horizon"]])


def render_discovery(context: AppContext) -> None:
    st.subheader("Developer Experience Discovery")
    st.caption("All evidence is synthetic. Add real interviews only with consent and anonymisation.")
    persona = st.selectbox("Persona", ["All"] + sorted(context.survey["persona"].unique()))
    view = context.survey if persona == "All" else context.survey[context.survey["persona"] == persona]
    metrics([
        ("Respondents", str(view["respondent_id"].nunique()), None),
        ("Average friction", f"{view['friction_score'].mean():.1f}/5", None),
        ("Average time lost", f"{view['minutes_lost'].mean():.0f} min/week", None),
    ])
    stage = journey_stage_summary(view)
    fig = px.scatter(
        stage,
        x="mean_minutes_lost",
        y="mean_friction",
        size="respondents",
        color="journey_stage",
        hover_data=["mean_frequency", "opportunity_score"],
        title="Journey-stage evidence map",
    )
    st.plotly_chart(chart(fig), width="stretch", config={"displayModeBar": False})
    table(view[["persona", "journey_stage", "friction_score", "frequency", "minutes_lost", "comment", "source_type"]])
    st.download_button(
        "Download evidence",
        view.to_csv(index=False).encode(),
        "discovery-evidence.csv",
        "text/csv",
    )


def render_golden_path(_: AppContext) -> None:
    st.subheader("Secure Self-Service Golden Path")
    st.caption("Generate a FastAPI starter with tests, pinned CI, non-root Docker, Kubernetes controls, Helm and ownership metadata.")
    with st.form("golden-path"):
        left, right = st.columns(2)
        name = left.text_input("Service name", "catalog-insights-api")
        team = right.text_input("Owning team", "marketplace-platform")
        visibility = left.selectbox("Repository visibility", ["internal", "private", "public"])
        database = right.selectbox("Database", ["None", "PostgreSQL", "MySQL", "Redis"])
        environment = left.selectbox("Environment", ["development", "staging", "production"])
        slo = right.slider("Availability SLO", 99.0, 99.99, 99.9, .01)
        build = st.form_submit_button("Build secure starter", type="primary", width="stretch")
    if not build:
        return
    try:
        config = ServiceConfig(
            name,
            team,
            visibility=visibility,
            database=database,
            environment=environment,
            slo_target=slo,
        )
        safe_name = sanitize_service_name(name)
        payload = generate_service_zip(config)
        st.success(f"Secure starter generated for {safe_name}.")
        files_tab, preview_tab, acceptance_tab = st.tabs(["Artefacts", "Security preview", "Acceptance criteria"])
        with files_tab:
            st.code("\n".join(generated_paths(config)), language="text")
        with preview_tab:
            preview = st.selectbox(
                "Preview",
                ["kubernetes/deployment.yaml", "Dockerfile", ".github/workflows/ci.yml", "service-catalog.yaml"],
            )
            st.code(generated_file_preview(config, preview), language="yaml")
        with acceptance_tab:
            st.markdown("- health and readiness checks\n- tests and pinned CI\n- non-root container\n- no privilege escalation\n- dropped capabilities\n- owner, SLO and security metadata\n- no generated secrets")
        st.download_button(
            "Download secure starter ZIP",
            payload,
            f"{safe_name}-golden-path.zip",
            "application/zip",
            type="primary",
        )
    except ValueError as exc:
        st.error(str(exc))


def render_service_catalogue(context: AppContext) -> None:
    st.subheader("Internal Service Catalogue")
    choice = st.selectbox(
        "Risk filter",
        ["All", "Missing owner", "Failed pipeline", "Missing documentation", "No runbook", "Below SLO", "Open incidents", "Stale deployment"],
    )
    view = context.health.copy()
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
    table(view[["service_name", "team", "environment", "pipeline_status", "slo_actual", "slo_target", "open_incidents", "health_status", "health_score", "risk_reasons", "recommended_action"]])
    st.download_button("Download health report", view.to_csv(index=False).encode(), "service-health.csv", "text/csv")


def render_platform_metrics(context: AppContext) -> None:
    st.subheader("Developer Platform Metrics")
    metrics([
        ("Ownership coverage", f"{context.kpis['ownership_coverage_pct']}%", None),
        ("Documentation coverage", f"{context.kpis['documentation_coverage_pct']}%", None),
        ("Change-failure rate", f"{context.kpis['change_failure_rate_pct']}%", None),
        ("Median MTTR", f"{context.kpis['median_mttr_min']} min", None),
    ])
    trend = context.pipelines.groupby("date", as_index=False).agg(
        pipeline_success=("pipeline_success", "mean"),
        pipeline_duration_min=("pipeline_duration_min", "median"),
        lead_time_hours=("lead_time_hours", "median"),
        mttr_minutes=("mttr_minutes", "median"),
    )
    trend["pipeline_success_pct"] = trend["pipeline_success"] * 100
    left, right = st.columns(2)
    with left:
        fig = px.line(trend, x="date", y="pipeline_success_pct", markers=True, title="Pipeline success")
        st.plotly_chart(chart(fig), width="stretch", config={"displayModeBar": False})
    with right:
        fig = px.line(
            trend,
            x="date",
            y=["pipeline_duration_min", "lead_time_hours", "mttr_minutes"],
            markers=True,
            title="Flow and recovery",
        )
        st.plotly_chart(chart(fig), width="stretch", config={"displayModeBar": False})
