"""Product and delivery metric calculations."""
from __future__ import annotations
from typing import Any
import pandas as pd

def developer_experience_score(survey: pd.DataFrame) -> float:
    if survey.empty:
        return 0.0
    friction = float(survey["friction_score"].mean())
    minutes = float(survey["minutes_lost"].mean())
    frequency = float(survey["frequency"].mean())
    penalty = (friction * 8.0) + min(minutes / 3.0, 20.0) + (frequency * 2.5)
    return round(max(0.0, min(100.0, 100.0 - penalty)), 1)

def platform_kpis(survey: pd.DataFrame, services: pd.DataFrame, pipelines: pd.DataFrame) -> dict[str, Any]:
    if services.empty or pipelines.empty:
        raise ValueError("Services and pipeline data must not be empty.")
    latest = pipelines.sort_values("date").groupby("service_name", as_index=False).tail(1)
    return {
        "developer_experience_score": developer_experience_score(survey),
        "median_time_to_first_deploy_min": round(float(survey.loc[survey["journey_stage"] == "Deploy", "minutes_lost"].median()), 1),
        "golden_path_adoption_pct": round(float(services["created_via_golden_path"].mean() * 100), 1),
        "pipeline_success_pct": round(float(latest["pipeline_success"].mean() * 100), 1),
        "ownership_coverage_pct": round(float(services["team"].fillna("").str.strip().ne("").mean() * 100), 1),
        "slo_coverage_pct": round(float(services["slo_target"].notna().mean() * 100), 1),
        "documentation_coverage_pct": round(float(services["documentation"].fillna("").str.strip().ne("").mean() * 100), 1),
        "median_pipeline_duration_min": round(float(pipelines["pipeline_duration_min"].median()), 1),
        "deployment_frequency_per_week": round(float(pipelines["deployment_count"].sum()) / max(pipelines["date"].nunique() / 7.0, 1.0), 1),
        "median_lead_time_hours": round(float(pipelines["lead_time_hours"].median()), 1),
        "change_failure_rate_pct": round(float(pipelines["change_failed"].mean() * 100), 1),
        "median_mttr_min": round(float(pipelines.loc[pipelines["mttr_minutes"] > 0, "mttr_minutes"].median()), 1),
        "support_requests": int(pipelines["support_requests"].sum()),
    }

def journey_stage_summary(survey: pd.DataFrame) -> pd.DataFrame:
    summary = survey.groupby("journey_stage", as_index=False).agg(
        respondents=("respondent_id", "nunique"),
        mean_friction=("friction_score", "mean"),
        mean_minutes_lost=("minutes_lost", "mean"),
        mean_frequency=("frequency", "mean"),
    )
    summary["opportunity_score"] = (
        summary["mean_friction"] * summary["mean_frequency"] * (1 + summary["mean_minutes_lost"] / 60.0)
    ).round(2)
    return summary.sort_values(["opportunity_score"], ascending=False).reset_index(drop=True)
