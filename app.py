# PlatformPulse Streamlit application.
from __future__ import annotations

from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

from platformpulse.data import load_feedback, load_pipeline_metrics, load_services, load_survey
from platformpulse.generator import ServiceConfig, generate_service_zip, generated_paths, sanitize_service_name
from platformpulse.metrics import journey_stage_summary, platform_kpis
from platformpulse.prioritization import opportunity_score, rank_opportunities
from platformpulse.reliability import catalogue_health


st.set_page_config(page_title="PlatformPulse", page_icon="🧭", layout="wide", initial_sidebar_state="expanded")

st.markdown(
    """
    <style>
      .block-container {padding-top: 1.3rem; padding-bottom: 2rem;}
      .pp-hero {padding: 1.3rem 1.5rem; border: 1px solid #d7dde5;
                border-radius: 14px; background: linear-gradient(135deg,#f7f9fc,#ffffff);}
      .pp-kicker {font-size: .82rem; letter-spacing: .08em; font-weight: 700;
                  text-transform: uppercase; color: #52606d;}
      .pp-title {font-size: 2.15rem; line-height: 1.1; font-weight: 750; margin: .25rem 0;}
      .pp-subtitle {font-size: 1.04rem; color: #465362; max-width: 900px;}
      div[data-testid="stMetric"] {border: 1px solid #e3e7ed; padding: .8rem;
                                  border-radius: 12px; background: white;}
    </style>
    """,
    unsafe_allow_html=True,
)

survey = load_survey()
services = load_services()
pipelines = load_pipeline_metrics()
feedback = load_feedback()
health = catalogue_health(services)
ranked = rank_opportunities(feedback)
kpis = platform_kpis(survey, services, pipelines)

st.markdown(
    """
    <div class="pp-hero">
      <div class="pp-kicker">Developer Experience & Internal Platform Product Lab</div>
      <div class="pp-title">PlatformPulse</div>
      <div class="pp-subtitle">
        A working product prototype connecting developer discovery, self-service
        golden paths, service ownership, CI/CD health, platform metrics and
        evidence-based roadmap decisions.
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.title("PlatformPulse")
page = st.sidebar.radio(
    "Explore",
    [
        "Executive Overview",
        "Discovery Hub",
        "Golden Path Generator",
        "Service Catalogue",
        "Platform Metrics",
        "Roadmap & Decisions",
        "Reliability",
    ],
)
st.sidebar.divider()
st.sidebar.caption("Independent portfolio project. All data is synthetic and contains no employer or client information.")

if page == "Executive Overview":
    st.subheader("Product outcome overview")
    cols = st.columns(4)
    cols[0].metric("Developer Experience Score", f"{kpis['developer_experience_score']}/100")
    cols[1].metric("Golden-path adoption", f"{kpis['golden_path_adoption_pct']}%")
    cols[2].metric("Pipeline success", f"{kpis['pipeline_success_pct']}%")
    cols[3].metric("Services at risk", int((health["health_status"] != "Green").sum()))

    cols = st.columns(4)
    cols[0].metric("Median pipeline duration", f"{kpis['median_pipeline_duration_min']} min")
    cols[1].metric("Median lead time", f"{kpis['median_lead_time_hours']} h")
    cols[2].metric("Change-failure rate", f"{kpis['change_failure_rate_pct']}%")
    cols[3].metric("Median MTTR", f"{kpis['median_mttr_min']} min")

    st.markdown("### Product hypothesis")
    st.info(
        "A developer platform creates measurable value when the supported path is "
        "easier than the unsupported path, ownership is visible, feedback is fast, "
        "and product decisions are tied to developer and reliability outcomes."
    )

    c1, c2 = st.columns([1.15, 1])
    with c1:
        stage = journey_stage_summary(survey)
        fig = px.bar(
            stage.sort_values("opportunity_score"),
            x="opportunity_score",
            y="journey_stage",
            orientation="h",
            labels={"opportunity_score": "Opportunity score", "journey_stage": "Journey stage"},
            title="Where platform friction is concentrated",
        )
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        status_counts = health["health_status"].value_counts().reset_index()
        status_counts.columns = ["status", "services"]
        fig = px.pie(status_counts, values="services", names="status", hole=0.55, title="Current catalogue health")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Recommended Now / Next / Later roadmap")
    st.dataframe(ranked[["problem", "priority_score", "roadmap_horizon", "journey_stage"]], use_container_width=True, hide_index=True)

elif page == "Discovery Hub":
    st.subheader("Developer Experience Discovery Hub")
    st.caption("Synthetic research evidence is clearly labelled. Add anonymous primary research only when real consented interviews are available.")
    persona = st.selectbox("Persona", ["All"] + sorted(survey["persona"].unique().tolist()))
    filtered = survey if persona == "All" else survey[survey["persona"] == persona]
    cols = st.columns(3)
    cols[0].metric("Responses", filtered["respondent_id"].nunique())
    cols[1].metric("Average friction", f"{filtered['friction_score'].mean():.1f}/5")
    cols[2].metric("Average time lost", f"{filtered['minutes_lost'].mean():.0f} min/week")

    stage = journey_stage_summary(filtered)
    fig = px.scatter(
        stage,
        x="mean_minutes_lost",
        y="mean_friction",
        size="respondents",
        color="journey_stage",
        hover_data=["mean_frequency", "opportunity_score"],
        labels={"mean_minutes_lost": "Average minutes lost per week", "mean_friction": "Average friction (1-5)"},
        title="Journey-stage evidence map",
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("### Evidence and synthetic comments")
    st.dataframe(
        filtered[["persona", "journey_stage", "friction_score", "frequency", "minutes_lost", "comment", "source_type"]],
        use_container_width=True,
        hide_index=True,
    )
    st.markdown("### Discovery questions")
    st.markdown(
        """
        - Where do developers lose the most time?
        - Which steps require avoidable manual configuration?
        - Which documentation or ownership signals are missing?
        - Which pipeline failures recur and create support demand?
        - Which change would improve the largest part of the journey?
        """
    )

elif page == "Golden Path Generator":
    st.subheader("Self-Service Golden Path Generator")
    st.caption("Generate a safe, vendor-neutral FastAPI starter service with health checks, tests, CI, Docker, Kubernetes, Helm, ownership and SLO metadata.")
    c1, c2 = st.columns(2)
    service_name = c1.text_input("Service name", "catalog-insights-api")
    team = c2.text_input("Owning team", "marketplace-platform")
    language = c1.selectbox("Language", ["Python"])
    visibility = c2.selectbox("Repository visibility", ["internal", "private", "public"])
    database = c1.selectbox("Database", ["None", "PostgreSQL", "MySQL", "Redis"])
    environment = c2.selectbox("Target environment", ["development", "staging", "production"])
    slo = st.slider("Availability SLO target", 99.0, 99.99, 99.9, 0.01)
    try:
        config = ServiceConfig(service_name=service_name, team=team, language=language, visibility=visibility, database=database, environment=environment, slo_target=slo)
        safe_name = sanitize_service_name(service_name)
        zip_bytes = generate_service_zip(config)
        st.success(f"Golden path ready: {safe_name}. The ZIP includes ownership, operability and delivery controls rather than only application code.")
        p1, p2 = st.columns([1.2, 1])
        with p1:
            st.markdown("#### Generated artefacts")
            st.code("\n".join(generated_paths(config)), language="text")
        with p2:
            st.markdown("#### Acceptance criteria")
            st.markdown(
                """
                - `/health` returns HTTP 200
                - automated test included
                - GitHub Actions workflow included
                - Docker packaging included
                - Kubernetes and Helm metadata included
                - owner, environment and SLO registered
                - local setup documented
                """
            )
            st.download_button("Download generated starter service", data=zip_bytes, file_name=f"{safe_name}-golden-path.zip", mime="application/zip", use_container_width=True)
    except ValueError as exc:
        st.error(str(exc))

elif page == "Service Catalogue":
    st.subheader("Internal Service Catalogue")
    st.caption("Catalogue signals make ownership, documentation, pipeline health and operability discoverable.")
    filter_option = st.selectbox("Risk filter", ["All services", "Missing owner", "Failed pipeline", "Missing documentation", "No runbook", "Below SLO", "Open incidents", "Stale deployment"])
    view = health.copy()
    if filter_option == "Missing owner":
        view = view[view["team"].fillna("").str.strip().eq("")]
    elif filter_option == "Failed pipeline":
        view = view[view["pipeline_status"].str.lower().ne("passing")]
    elif filter_option == "Missing documentation":
        view = view[view["documentation"].fillna("").str.strip().eq("")]
    elif filter_option == "No runbook":
        view = view[view["runbook"].fillna("").str.strip().eq("")]
    elif filter_option == "Below SLO":
        view = view[view["slo_actual"] < view["slo_target"]]
    elif filter_option == "Open incidents":
        view = view[view["open_incidents"] > 0]
    elif filter_option == "Stale deployment":
        view = view[view["deployment_age_days"] > 45]
    st.dataframe(
        view[["service_name", "team", "language", "environment", "pipeline_status", "slo_target", "slo_actual", "open_incidents", "health_status", "health_score", "risk_reasons", "recommended_action"]],
        use_container_width=True,
        hide_index=True,
    )

elif page == "Platform Metrics":
    st.subheader("Developer Platform Metrics")
    st.caption("The metrics connect user experience, platform adoption, delivery flow and reliability.")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Developer Experience", f"{kpis['developer_experience_score']}/100")
    c2.metric("Ownership coverage", f"{kpis['ownership_coverage_pct']}%")
    c3.metric("Documentation coverage", f"{kpis['documentation_coverage_pct']}%")
    c4.metric("SLO coverage", f"{kpis['slo_coverage_pct']}%")

    trend = pipelines.groupby("date", as_index=False).agg(
        pipeline_success=("pipeline_success", "mean"),
        pipeline_duration_min=("pipeline_duration_min", "median"),
        lead_time_hours=("lead_time_hours", "median"),
        mttr_minutes=("mttr_minutes", "median"),
    ).sort_values("date")
    trend["pipeline_success_pct"] = trend["pipeline_success"] * 100
    c1, c2 = st.columns(2)
    with c1:
        fig = px.line(trend, x="date", y="pipeline_success_pct", markers=True, labels={"pipeline_success_pct": "Pipeline success (%)", "date": "Date"}, title="Delivery reliability trend")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.line(trend, x="date", y=["pipeline_duration_min", "lead_time_hours", "mttr_minutes"], markers=True, title="Flow and recovery indicators")
        st.plotly_chart(fig, use_container_width=True)

    definitions = pd.DataFrame(
        [
            ["Time to first deployment", "Onboarding friction", "Median minutes lost at deploy stage"],
            ["Golden-path adoption", "Self-service usage", "% services created through supported template"],
            ["Pipeline success", "Delivery reliability", "% latest pipelines passing"],
            ["Change lead time", "Delivery flow", "Median hours from change to delivery"],
            ["Change-failure rate", "Release quality", "% changes associated with failure"],
            ["MTTR", "Recovery capability", "Median incident recovery time"],
            ["Developer Experience Score", "User outcome", "Composite friction, time-loss and frequency score"],
        ],
        columns=["Metric", "Outcome", "Prototype calculation"],
    )
    st.markdown("### Metric definitions")
    st.dataframe(definitions, use_container_width=True, hide_index=True)

elif page == "Roadmap & Decisions":
    st.subheader("Feedback-to-Roadmap Workflow")
    st.caption("Evidence is clustered, scored, translated into a product decision and tied to a success metric.")
    st.dataframe(ranked[["id", "problem", "journey_stage", "evidence_count", "priority_score", "roadmap_horizon", "status"]], use_container_width=True, hide_index=True)

    st.markdown("### Product Decision Simulator")
    opportunities = {
        "Golden-path service creation": {"reach": 120, "impact": 4.5, "confidence": 85, "effort": 8, "alignment": 5, "risk": 4},
        "Faster CI pipeline feedback": {"reach": 180, "impact": 3.8, "confidence": 80, "effort": 10, "alignment": 5, "risk": 5},
        "Ownership and documentation coverage": {"reach": 220, "impact": 3.2, "confidence": 90, "effort": 6, "alignment": 4, "risk": 4},
    }
    selected = st.selectbox("Opportunity", list(opportunities))
    defaults = opportunities[selected]
    col1, col2, col3 = st.columns(3)
    reach = col1.number_input("Affected engineers / quarter", 1, 1000, defaults["reach"])
    impact = col2.slider("User impact", 1.0, 5.0, defaults["impact"], 0.1)
    confidence = col3.slider("Evidence confidence (%)", 10, 100, defaults["confidence"], 5)
    effort = col1.slider("Relative effort", 1, 20, defaults["effort"])
    alignment = col2.slider("Strategic alignment", 1, 5, defaults["alignment"])
    risk = col3.slider("Reliability risk addressed", 1, 5, defaults["risk"])
    score = opportunity_score(reach, impact, confidence, effort, alignment, risk)
    st.metric("Decision score", score)
    recommendation = "Prioritise now and validate through an incremental release." if score >= 70 else "Keep in Next; reduce uncertainty or break delivery into smaller slices." if score >= 35 else "Keep in Later unless new evidence materially changes the trade-off."
    st.info(recommendation)
    selected_row = ranked.iloc[0]
    st.markdown("### Example product slice")
    st.markdown(
        f"""
        **Problem:** {selected_row['problem']}

        **User story:** As an internal engineer, I want a supported platform workflow so
        that I can deliver and operate a service without rebuilding standard controls.

        **Acceptance criteria**
        - supported starter artefacts are generated in one flow;
        - ownership and SLO metadata are included;
        - automated tests and CI are included;
        - the developer can complete the demo path in under ten minutes;
        - adoption and support-demand metrics can be measured.
        """
    )

elif page == "Reliability":
    st.subheader("Platform Reliability & Operational Action")
    service = st.selectbox("Service", health["service_name"].tolist())
    row = health[health["service_name"] == service].iloc[0]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Health status", row["health_status"])
    c2.metric("Health score", f"{row['health_score']}/100")
    c3.metric("SLO", f"{row['slo_actual']}% / {row['slo_target']}%")
    c4.metric("Open incidents", int(row["open_incidents"]))
    st.markdown("### Signals")
    st.write(row["risk_reasons"])
    st.markdown("### Recommended first action")
    st.info(row["recommended_action"])
    service_pipeline = pipelines[pipelines["service_name"] == service].sort_values("date")
    fig = px.line(service_pipeline, x="date", y=["pipeline_duration_min", "lead_time_hours", "mttr_minutes"], markers=True, title=f"{service}: delivery and recovery trend")
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("### Operational review checklist")
    st.markdown(
        """
        1. Confirm owner and customer impact.
        2. Review latest deployment and pipeline evidence.
        3. Check SLO, incidents and repeated support signals.
        4. Select or create the appropriate runbook.
        5. Record decision, action owner and due date.
        6. Validate whether the product metric improved after the change.
        """
    )

st.divider()
st.caption(f"PlatformPulse prototype · generated view {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')} · synthetic data only")
