import pandas as pd
import pytest

from platformpulse.prioritization import opportunity_score, rank_opportunities


def test_opportunity_score_rewards_reach_and_evidence() -> None:
    high = opportunity_score(200, 4.5, 90, 8, 5, 5)
    low = opportunity_score(50, 2.0, 40, 8, 2, 2)
    assert high > low


def test_effort_must_be_positive() -> None:
    with pytest.raises(ValueError):
        opportunity_score(100, 4, 80, 0)


def test_rank_assigns_now_to_top_opportunity() -> None:
    df = pd.DataFrame([
        {"problem": "A", "reach": 200, "impact": 5, "confidence": 90, "effort": 5, "strategic_alignment": 5, "reliability_risk": 5},
        {"problem": "B", "reach": 50, "impact": 2, "confidence": 50, "effort": 10, "strategic_alignment": 2, "reliability_risk": 2},
    ])
    ranked = rank_opportunities(df)
    assert ranked.iloc[0]["problem"] == "A"
    assert ranked.iloc[0]["roadmap_horizon"] == "Now"
