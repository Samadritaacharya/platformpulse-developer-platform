"""A/B experiment validation and statistical decision helpers."""
from __future__ import annotations

from dataclasses import dataclass
from math import erfc, sqrt
from typing import Final

import pandas as pd

_REQUIRED: Final = {
    "participant_id", "variant", "persona", "completed_first_deploy",
    "time_to_first_deploy_min", "support_request", "satisfaction_score",
    "exposure_date",
}
_ALLOWED_VARIANTS: Final = {"Control", "Treatment"}


@dataclass(frozen=True)
class ExperimentResult:
    control_n: int
    treatment_n: int
    control_conversion: float
    treatment_conversion: float
    absolute_uplift_pp: float
    relative_uplift_pct: float
    z_score: float
    p_value: float
    ci_low_pp: float
    ci_high_pp: float
    srm_p_value: float
    control_time_min: float
    treatment_time_min: float
    time_reduction_pct: float
    control_support_rate: float
    treatment_support_rate: float
    support_reduction_pp: float
    control_satisfaction: float
    treatment_satisfaction: float
    decision: str


def validate_experiment_data(frame: pd.DataFrame) -> None:
    missing = _REQUIRED.difference(frame.columns)
    if missing:
        raise ValueError(f"Experiment data is missing columns: {sorted(missing)}")
    if frame.empty:
        raise ValueError("Experiment data must not be empty")
    if frame["participant_id"].duplicated().any():
        raise ValueError("participant_id values must be unique")
    variants = set(frame["variant"].dropna().astype(str))
    if variants != _ALLOWED_VARIANTS:
        raise ValueError("Experiment must contain exactly Control and Treatment variants")
    for column in ("completed_first_deploy", "support_request"):
        values = set(pd.to_numeric(frame[column], errors="raise").astype(int).unique())
        if not values.issubset({0, 1}):
            raise ValueError(f"{column} must contain only 0 or 1")
    if (pd.to_numeric(frame["time_to_first_deploy_min"], errors="raise") <= 0).any():
        raise ValueError("time_to_first_deploy_min must be positive")
    satisfaction = pd.to_numeric(frame["satisfaction_score"], errors="raise")
    if not satisfaction.between(1, 5).all():
        raise ValueError("satisfaction_score must be between 1 and 5")


def _normal_two_sided_p(z_score: float) -> float:
    return float(erfc(abs(z_score) / sqrt(2.0)))


def _difference_ci(p_control: float, n_control: int, p_treatment: float, n_treatment: int) -> tuple[float, float]:
    standard_error = sqrt(
        (p_control * (1.0 - p_control) / n_control)
        + (p_treatment * (1.0 - p_treatment) / n_treatment)
    )
    difference = p_treatment - p_control
    margin = 1.96 * standard_error
    return difference - margin, difference + margin


def sample_ratio_mismatch_p_value(control_n: int, treatment_n: int) -> float:
    total = control_n + treatment_n
    if total <= 0:
        raise ValueError("Experiment sample size must be positive")
    expected = total / 2.0
    standard_error = sqrt(total * 0.5 * 0.5)
    z_score = (treatment_n - expected) / standard_error
    return _normal_two_sided_p(z_score)


def analyze_experiment(frame: pd.DataFrame) -> ExperimentResult:
    validate_experiment_data(frame)
    control = frame.loc[frame["variant"] == "Control"].copy()
    treatment = frame.loc[frame["variant"] == "Treatment"].copy()
    control_n, treatment_n = len(control), len(treatment)
    if min(control_n, treatment_n) < 20:
        raise ValueError("Each experiment variant needs at least 20 participants")

    c_success = int(control["completed_first_deploy"].sum())
    t_success = int(treatment["completed_first_deploy"].sum())
    p_control = c_success / control_n
    p_treatment = t_success / treatment_n
    pooled = (c_success + t_success) / (control_n + treatment_n)
    pooled_se = sqrt(pooled * (1.0 - pooled) * ((1.0 / control_n) + (1.0 / treatment_n)))
    z_score = 0.0 if pooled_se == 0 else (p_treatment - p_control) / pooled_se
    p_value = _normal_two_sided_p(z_score)
    ci_low, ci_high = _difference_ci(p_control, control_n, p_treatment, treatment_n)

    control_time = float(control["time_to_first_deploy_min"].mean())
    treatment_time = float(treatment["time_to_first_deploy_min"].mean())
    time_reduction = 0.0 if control_time == 0 else ((control_time - treatment_time) / control_time) * 100.0
    control_support = float(control["support_request"].mean())
    treatment_support = float(treatment["support_request"].mean())
    control_satisfaction = float(control["satisfaction_score"].mean())
    treatment_satisfaction = float(treatment["satisfaction_score"].mean())
    no_guardrail_regression = (
        treatment_time <= control_time
        and treatment_support <= control_support
        and treatment_satisfaction >= control_satisfaction
    )

    if p_value < 0.05 and p_treatment > p_control and no_guardrail_regression:
        decision = "Ship Treatment with staged rollout and continued monitoring"
    elif p_value < 0.10 and p_treatment > p_control:
        decision = "Continue experiment to reduce uncertainty"
    else:
        decision = "Do not ship yet; investigate segments and experiment design"

    relative_uplift = 0.0 if p_control == 0 else ((p_treatment - p_control) / p_control) * 100.0
    return ExperimentResult(
        control_n=control_n,
        treatment_n=treatment_n,
        control_conversion=round(p_control * 100.0, 2),
        treatment_conversion=round(p_treatment * 100.0, 2),
        absolute_uplift_pp=round((p_treatment - p_control) * 100.0, 2),
        relative_uplift_pct=round(relative_uplift, 2),
        z_score=round(z_score, 4),
        p_value=round(p_value, 6),
        ci_low_pp=round(ci_low * 100.0, 2),
        ci_high_pp=round(ci_high * 100.0, 2),
        srm_p_value=round(sample_ratio_mismatch_p_value(control_n, treatment_n), 6),
        control_time_min=round(control_time, 1),
        treatment_time_min=round(treatment_time, 1),
        time_reduction_pct=round(time_reduction, 1),
        control_support_rate=round(control_support * 100.0, 1),
        treatment_support_rate=round(treatment_support * 100.0, 1),
        support_reduction_pp=round((control_support - treatment_support) * 100.0, 1),
        control_satisfaction=round(control_satisfaction, 2),
        treatment_satisfaction=round(treatment_satisfaction, 2),
        decision=decision,
    )


def variant_summary(frame: pd.DataFrame) -> pd.DataFrame:
    validate_experiment_data(frame)
    summary = frame.groupby("variant", as_index=False).agg(
        participants=("participant_id", "count"),
        conversion_rate=("completed_first_deploy", "mean"),
        average_time_to_first_deploy=("time_to_first_deploy_min", "mean"),
        support_request_rate=("support_request", "mean"),
        average_satisfaction=("satisfaction_score", "mean"),
    )
    summary["conversion_rate"] = (summary["conversion_rate"] * 100).round(1)
    summary["support_request_rate"] = (summary["support_request_rate"] * 100).round(1)
    summary["average_time_to_first_deploy"] = summary["average_time_to_first_deploy"].round(1)
    summary["average_satisfaction"] = summary["average_satisfaction"].round(2)
    return summary


def persona_lift(frame: pd.DataFrame) -> pd.DataFrame:
    validate_experiment_data(frame)
    grouped = frame.groupby(["persona", "variant"], as_index=False).agg(
        participants=("participant_id", "count"),
        conversion=("completed_first_deploy", "mean"),
        time_min=("time_to_first_deploy_min", "mean"),
    )
    pivot = grouped.pivot(index="persona", columns="variant", values=["participants", "conversion", "time_min"])
    rows: list[dict[str, object]] = []
    for persona in pivot.index:
        c_conversion = float(pivot.loc[persona, ("conversion", "Control")])
        t_conversion = float(pivot.loc[persona, ("conversion", "Treatment")])
        rows.append({
            "persona": persona,
            "control_n": int(pivot.loc[persona, ("participants", "Control")]),
            "treatment_n": int(pivot.loc[persona, ("participants", "Treatment")]),
            "control_conversion_pct": round(c_conversion * 100, 1),
            "treatment_conversion_pct": round(t_conversion * 100, 1),
            "uplift_pp": round((t_conversion - c_conversion) * 100, 1),
            "control_time_min": round(float(pivot.loc[persona, ("time_min", "Control")]), 1),
            "treatment_time_min": round(float(pivot.loc[persona, ("time_min", "Treatment")]), 1),
        })
    return pd.DataFrame(rows).sort_values("uplift_pp", ascending=False).reset_index(drop=True)
