from datetime import datetime, timezone

import pandas as pd

from platformpulse.metrics import developer_experience_score, journey_stage_summary
from platformpulse.reliability import service_health


def test_developer_experience_score_is_bounded() -> None:
    survey = pd.DataFrame({"friction_score": [1, 2, 3], "minutes_lost": [10, 20, 30], "frequency": [1, 2, 3]})
    score = developer_experience_score(survey)
    assert 0 <= score <= 100


def test_journey_summary_prioritises_high_friction() -> None:
    survey = pd.DataFrame({
        "respondent_id": ["A", "B", "C"],
        "journey_stage": ["Deploy", "Deploy", "Access"],
        "friction_score": [5, 4, 2],
        "minutes_lost": [100, 80, 20],
        "frequency": [5, 4, 2],
    })
    summary = journey_stage_summary(survey)
    assert summary.iloc[0]["journey_stage"] == "Deploy"


def test_service_health_detects_operational_risk() -> None:
    row = pd.Series({
        "team": "",
        "documentation": "",
        "runbook": "",
        "pipeline_status": "failing",
        "open_incidents": 2,
        "slo_target": 99.9,
        "slo_actual": 98.0,
        "last_deployment": "2026-01-01",
    })
    result = service_health(row, now=datetime(2026, 7, 24, tzinfo=timezone.utc))
    assert result["status"] == "Red"
    assert result["health_score"] < 55
    assert result["recommended_actions"]
