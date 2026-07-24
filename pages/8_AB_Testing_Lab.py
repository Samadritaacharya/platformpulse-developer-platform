"""Interactive, privacy-safe A/B testing lab for PlatformPulse."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from platformpulse.ab_testing import demo_experiment_data, sample_size_warning, two_proportion_test

st.set_page_config(page_title="PlatformPulse A/B Testing Lab", page_icon="🧪", layout="wide")

st.markdown(
    """
    <style>
      .block-container {max-width: 1240px; padding-top: 1.5rem;}
      .ab-hero {padding: 1.35rem 1.5rem; border-radius: 16px; border: 1px solid #d9e2ec;
                background: linear-gradient(135deg,#f4f8ff,#ffffff); margin-bottom: 1rem;}
      .ab-title {font-size: 2rem; font-weight: 750; margin-bottom: .3rem;}
      .ab-note {color:#52606d; max-width: 920px;}
      div[data-testid="stMetric"] {border:1px solid #e3e8ef; border-radius:12px; padding:.75rem; background:#fff;}
    </style>
    <div class="ab-hero">
      <div class="ab-title">A/B Testing Lab</div>
      <div class="ab-note">Evaluate whether a guided golden path improves first-deployment success. All included data is synthetic, aggregate and privacy-safe.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.info("Experiment guardrail: do not collect names, emails, repository secrets, source code, or employee identifiers. Use aggregated product events only.")

mode = st.radio("Data mode", ["Recruiter-ready demo", "Custom aggregate experiment"], horizontal=True)

if mode == "Recruiter-ready demo":
    data = demo_experiment_data()
    st.dataframe(data, use_container_width=True, hide_index=True)
    control = data.iloc[0]
    treatment = data.iloc[1]
    cv, cc = int(control["visitors"]), int(control["successful_first_deployments"])
    tv, tc = int(treatment["visitors"]), int(treatment["successful_first_deployments"])
else:
    st.caption("Enter aggregate counts only. No personal or sensitive data is required.")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Variant A — Current flow")
        cv = st.number_input("A participants", min_value=1, max_value=1_000_000, value=300, step=10)
        cc = st.number_input("A successful first deployments", min_value=0, max_value=int(cv), value=min(165, int(cv)), step=1)
    with c2:
        st.markdown("#### Variant B — Guided golden path")
        tv = st.number_input("B participants", min_value=1, max_value=1_000_000, value=300, step=10)
        tc = st.number_input("B successful first deployments", min_value=0, max_value=int(tv), value=min(201, int(tv)), step=1)

alpha = st.select_slider("Significance threshold", options=[0.10, 0.05, 0.01], value=0.05, format_func=lambda x: f"α = {x}")
result = two_proportion_test(int(cv), int(cc), int(tv), int(tc), alpha=float(alpha))

warning = sample_size_warning(int(cv), int(tv))
if warning:
    st.warning(warning)

cols = st.columns(5)
cols[0].metric("A conversion", f"{result.control_rate * 100:.1f}%")
cols[1].metric("B conversion", f"{result.treatment_rate * 100:.1f}%")
cols[2].metric("Absolute uplift", f"{result.absolute_uplift * 100:+.1f} pp")
cols[3].metric("Relative uplift", f"{result.relative_uplift_pct:+.1f}%")
cols[4].metric("p-value", f"{result.p_value:.4f}")

chart_data = pd.DataFrame(
    {
        "Variant": ["A — Current flow", "B — Guided golden path"],
        "Successful first deployment (%)": [result.control_rate * 100, result.treatment_rate * 100],
    }
)
fig = px.bar(chart_data, x="Variant", y="Successful first deployment (%)", text_auto=".1f", range_y=[0, 100], title="Primary outcome comparison")
st.plotly_chart(fig, use_container_width=True)

if result.significant and result.absolute_uplift > 0:
    st.success(result.recommendation)
elif result.significant:
    st.error(result.recommendation)
else:
    st.warning(result.recommendation)

st.markdown("### Decision record")
decision = pd.DataFrame(
    [
        ["Hypothesis", "A guided golden path increases successful first deployments."],
        ["Primary metric", "Successful first deployment rate."],
        ["Guardrails", "Support requests, setup duration, failed pipelines, rollback events."],
        ["Result", "Statistically significant" if result.significant else "Not statistically significant"],
        ["Recommended action", result.recommendation],
    ],
    columns=["Field", "Value"],
)
st.dataframe(decision, use_container_width=True, hide_index=True)

st.markdown("### Responsible experimentation checklist")
st.markdown(
    """
    - Predefine the hypothesis, primary metric, guardrails, duration and stop conditions.
    - Use random allocation where operationally safe; do not disadvantage protected groups.
    - Collect the minimum aggregate telemetry needed and define a retention period.
    - Do not use AI-generated scores to make employment, disciplinary or access decisions.
    - Monitor reliability and security guardrails; keep a tested rollback path.
    - Record inconclusive and negative results to reduce repeated experimentation risk.
    """
)

st.download_button(
    "Download experiment decision as CSV",
    data=decision.to_csv(index=False).encode("utf-8"),
    file_name="platformpulse_ab_test_decision.csv",
    mime="text/csv",
)

st.caption("Portfolio demonstration only · synthetic aggregate data · no production or employer information")
