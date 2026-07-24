"""Safe, deterministic A/B testing utilities for product experiments."""
from __future__ import annotations

from dataclasses import dataclass
from math import erf, sqrt

import pandas as pd


@dataclass(frozen=True)
class ExperimentResult:
    control_rate: float
    treatment_rate: float
    absolute_uplift: float
    relative_uplift_pct: float
    z_score: float
    p_value: float
    significant: bool
    recommendation: str


def _validate_counts(visitors: int, conversions: int, label: str) -> None:
    if visitors < 1:
        raise ValueError(f"{label} visitors must be at least 1.")
    if conversions < 0 or conversions > visitors:
        raise ValueError(f"{label} conversions must be between 0 and visitors.")


def two_proportion_test(
    control_visitors: int,
    control_conversions: int,
    treatment_visitors: int,
    treatment_conversions: int,
    alpha: float = 0.05,
) -> ExperimentResult:
    """Return a two-sided pooled two-proportion z-test without external dependencies."""
    _validate_counts(control_visitors, control_conversions, "Control")
    _validate_counts(treatment_visitors, treatment_conversions, "Treatment")
    if not 0 < alpha < 1:
        raise ValueError("Alpha must be between 0 and 1.")

    control_rate = control_conversions / control_visitors
    treatment_rate = treatment_conversions / treatment_visitors
    pooled = (control_conversions + treatment_conversions) / (control_visitors + treatment_visitors)
    standard_error = sqrt(pooled * (1 - pooled) * ((1 / control_visitors) + (1 / treatment_visitors)))
    z_score = 0.0 if standard_error == 0 else (treatment_rate - control_rate) / standard_error
    normal_cdf = 0.5 * (1 + erf(abs(z_score) / sqrt(2)))
    p_value = max(0.0, min(1.0, 2 * (1 - normal_cdf)))
    absolute_uplift = treatment_rate - control_rate
    relative_uplift = 0.0 if control_rate == 0 else (absolute_uplift / control_rate) * 100
    significant = p_value < alpha

    if significant and absolute_uplift > 0:
        recommendation = "Treatment wins: roll out gradually with monitoring and a rollback plan."
    elif significant and absolute_uplift < 0:
        recommendation = "Control wins: stop the treatment and document the learning."
    else:
        recommendation = "Inconclusive: continue safely, increase sample size, or reduce experiment scope."

    return ExperimentResult(
        control_rate=round(control_rate, 6),
        treatment_rate=round(treatment_rate, 6),
        absolute_uplift=round(absolute_uplift, 6),
        relative_uplift_pct=round(relative_uplift, 2),
        z_score=round(z_score, 4),
        p_value=round(p_value, 6),
        significant=significant,
        recommendation=recommendation,
    )


def demo_experiment_data() -> pd.DataFrame:
    """Synthetic demo data. It contains no user identifiers or employer data."""
    return pd.DataFrame(
        [
            {"variant": "A — Existing setup flow", "visitors": 420, "successful_first_deployments": 239, "median_setup_minutes": 38, "support_requests": 64},
            {"variant": "B — Guided golden path", "visitors": 435, "successful_first_deployments": 301, "median_setup_minutes": 21, "support_requests": 31},
        ]
    )


def sample_size_warning(control_visitors: int, treatment_visitors: int) -> str | None:
    if min(control_visitors, treatment_visitors) < 100:
        return "Small sample: treat the result as directional, not as a rollout decision."
    return None
