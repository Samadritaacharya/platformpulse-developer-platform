"""Evidence-based opportunity prioritisation."""
from __future__ import annotations

import pandas as pd

REQUIRED_COLUMNS = {"reach", "impact", "confidence", "effort", "strategic_alignment", "reliability_risk"}


def opportunity_score(reach: float, impact: float, confidence: float, effort: float, strategic_alignment: float = 3.0, reliability_risk: float = 3.0) -> float:
    if reach < 0 or impact < 0:
        raise ValueError("Reach and impact must not be negative")
    if effort <= 0:
        raise ValueError("Effort must be greater than zero.")
    if not 1 <= float(strategic_alignment) <= 5 or not 1 <= float(reliability_risk) <= 5:
        raise ValueError("Alignment and reliability risk must be between 1 and 5")
    confidence_factor = max(0.0, min(float(confidence), 100.0)) / 100.0
    modifier = 0.6 + (0.08 * float(strategic_alignment)) + (0.05 * float(reliability_risk))
    return round((float(reach) * float(impact) * confidence_factor * modifier) / float(effort), 2)


def rank_opportunities(feedback: pd.DataFrame) -> pd.DataFrame:
    missing = REQUIRED_COLUMNS.difference(feedback.columns)
    if missing:
        raise ValueError(f"Missing prioritisation columns: {sorted(missing)}")
    if feedback.empty:
        raise ValueError("Feedback opportunities must not be empty")
    ranked = feedback.copy()
    ranked["priority_score"] = ranked.apply(lambda row: opportunity_score(row["reach"], row["impact"], row["confidence"], row["effort"], row["strategic_alignment"], row["reliability_risk"]), axis=1)
    ranked = ranked.sort_values("priority_score", ascending=False).reset_index(drop=True)
    ranked["roadmap_horizon"] = ["Now" if i == 0 else "Next" if i <= 2 else "Later" for i in range(len(ranked))]
    return ranked
