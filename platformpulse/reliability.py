"""Service-health and operational recommendation logic."""
from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd


def demo_reference_time(services: pd.DataFrame, pipelines: pd.DataFrame | None = None) -> datetime:
    candidates: list[pd.Timestamp] = []
    if not services.empty:
        candidates.append(pd.to_datetime(services["last_deployment"], utc=True).max())
    if pipelines is not None and not pipelines.empty:
        candidates.append(pd.to_datetime(pipelines["date"], utc=True).max())
    latest = max(candidates) if candidates else pd.Timestamp.now(tz="UTC")
    return (latest + pd.Timedelta(days=1)).to_pydatetime()


def service_health(row: pd.Series, now: datetime | None = None) -> dict[str, object]:
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    score = 100
    reasons: list[str] = []
    actions: list[str] = []
    team = str(row.get("team", "") or "").strip()
    documentation = str(row.get("documentation", "") or "").strip()
    runbook = str(row.get("runbook", "") or "").strip()
    pipeline_status = str(row.get("pipeline_status", "") or "").lower()
    incidents = max(0, int(row.get("open_incidents", 0) or 0))
    slo_target = float(row.get("slo_target", 0) or 0)
    slo_actual = float(row.get("slo_actual", 0) or 0)
    last_deployment = pd.Timestamp(row.get("last_deployment"))
    if pd.isna(last_deployment):
        raise ValueError("last_deployment is required for reliability scoring")
    if last_deployment.tzinfo is None:
        last_deployment = last_deployment.tz_localize("UTC")
    age_days = max(0, (pd.Timestamp(now) - last_deployment).days)
    if not team:
        score -= 25; reasons.append("missing accountable owner"); actions.append("Assign a named owning team in the service catalogue.")
    if pipeline_status != "passing":
        score -= 25; reasons.append("latest pipeline is not passing"); actions.append("Triage the failed pipeline and restore the supported path.")
    if slo_target and slo_actual < slo_target:
        score -= 20; reasons.append("SLO is below target"); actions.append("Review recent deployments and error/latency signals.")
    if incidents:
        score -= min(20, incidents * 8); reasons.append(f"{incidents} open incident(s)"); actions.append("Confirm incident owner, mitigation and follow-up review.")
    if not documentation:
        score -= 10; reasons.append("documentation is missing"); actions.append("Create a discoverable service overview and operating guide.")
    if not runbook:
        score -= 10; reasons.append("runbook is missing"); actions.append("Document the first-response runbook and escalation path.")
    if age_days > 45:
        score -= 5; reasons.append("deployment is stale"); actions.append("Confirm lifecycle status and whether the service is maintained.")
    score = max(0, score)
    status = "Green" if score >= 80 else "Amber" if score >= 55 else "Red"
    if not actions:
        actions.append("No immediate corrective action; continue monitoring.")
    return {"health_score": score, "status": status, "reasons": reasons or ["no material risk signal"], "recommended_actions": actions, "deployment_age_days": age_days}


def catalogue_health(services: pd.DataFrame, now: datetime | None = None) -> pd.DataFrame:
    if services.empty:
        raise ValueError("Service catalogue must not be empty")
    rows = []
    for _, row in services.iterrows():
        result = service_health(row, now=now)
        rows.append({**row.to_dict(), "health_score": result["health_score"], "health_status": result["status"], "risk_reasons": "; ".join(result["reasons"]), "recommended_action": result["recommended_actions"][0], "deployment_age_days": result["deployment_age_days"]})
    return pd.DataFrame(rows)
