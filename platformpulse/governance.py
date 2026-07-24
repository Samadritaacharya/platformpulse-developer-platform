"""AI governance and security risk evaluation for synthetic use-case inventory."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Final

import pandas as pd

_REQUIRED: Final = {
    "use_case_id", "name", "owner", "stage", "model_type",
    "data_classification", "external_model", "data_residency",
    "personal_data", "automated_decision", "human_oversight",
    "access_control", "audit_logging", "business_purpose",
}
_DATA_WEIGHT: Final = {"Public": 0, "Internal": 1, "Confidential": 3, "Restricted": 5}


@dataclass(frozen=True)
class GovernanceAssessment:
    risk_score: int
    risk_level: str
    controls: tuple[str, ...]
    decision: str


def validate_ai_inventory(frame: pd.DataFrame) -> None:
    missing = _REQUIRED.difference(frame.columns)
    if missing:
        raise ValueError(f"AI inventory is missing columns: {sorted(missing)}")
    if frame.empty:
        raise ValueError("AI inventory must not be empty")
    if frame["use_case_id"].duplicated().any():
        raise ValueError("AI use_case_id values must be unique")
    unknown = set(frame["data_classification"]) - set(_DATA_WEIGHT)
    if unknown:
        raise ValueError(f"Unknown data classifications: {sorted(unknown)}")
    for column in (
        "external_model", "personal_data", "automated_decision",
        "human_oversight", "access_control", "audit_logging",
    ):
        values = set(pd.to_numeric(frame[column], errors="raise").astype(int).unique())
        if not values.issubset({0, 1}):
            raise ValueError(f"{column} must contain only 0 or 1")


def assess_use_case(row: pd.Series | dict[str, object]) -> GovernanceAssessment:
    values = dict(row)
    classification = str(values.get("data_classification", "Internal"))
    if classification not in _DATA_WEIGHT:
        raise ValueError(f"Unsupported data classification: {classification}")

    score = _DATA_WEIGHT[classification]
    controls: list[str] = []
    external_model = int(values.get("external_model", 0)) == 1
    personal_data = int(values.get("personal_data", 0)) == 1
    automated_decision = int(values.get("automated_decision", 0)) == 1
    human_oversight = int(values.get("human_oversight", 0)) == 1
    access_control = int(values.get("access_control", 0)) == 1
    audit_logging = int(values.get("audit_logging", 0)) == 1
    residency = str(values.get("data_residency", "Unknown"))
    stage = str(values.get("stage", "Discovery"))

    if external_model:
        score += 2
        controls.append("Complete vendor security, privacy, retention and model-use review.")
    if personal_data:
        score += 3
        controls.append("Document lawful purpose, minimisation, retention and privacy review.")
    if automated_decision:
        score += 4
        controls.append("Define decision boundaries, contestability and human escalation.")
    if not human_oversight:
        score += 4
        controls.append("Add accountable human oversight and a tested override path.")
    if not access_control:
        score += 3
        controls.append("Implement least-privilege access and periodic entitlement review.")
    if not audit_logging:
        score += 2
        controls.append("Enable tamper-resistant logging for prompts, outputs and decisions.")
    if residency.lower() in {"unknown", "global/unknown", "not assessed"}:
        score += 2
        controls.append("Confirm data residency and cross-border processing before rollout.")
    if stage.lower() == "production":
        score += 1
        controls.append("Monitor production incidents, drift, misuse and control effectiveness.")

    if not controls:
        controls.append("Maintain periodic review, user guidance and incident monitoring.")

    if score >= 15:
        level = "Critical"
        decision = "Pause deployment until mandatory controls and accountable approval are complete"
    elif score >= 10:
        level = "High"
        decision = "Conditional approval only after control gaps are remediated"
    elif score >= 5:
        level = "Moderate"
        decision = "Proceed with documented controls, owner and scheduled review"
    else:
        level = "Low"
        decision = "Proceed with standard monitoring and periodic review"
    return GovernanceAssessment(score, level, tuple(controls), decision)


def assess_inventory(frame: pd.DataFrame) -> pd.DataFrame:
    validate_ai_inventory(frame)
    rows: list[dict[str, object]] = []
    for _, row in frame.iterrows():
        assessment = assess_use_case(row)
        rows.append({
            **row.to_dict(),
            "risk_score": assessment.risk_score,
            "risk_level": assessment.risk_level,
            "governance_decision": assessment.decision,
            "required_controls": " | ".join(assessment.controls),
        })
    return pd.DataFrame(rows).sort_values(["risk_score", "use_case_id"], ascending=[False, True]).reset_index(drop=True)


def governance_kpis(assessed: pd.DataFrame) -> dict[str, float | int]:
    if assessed.empty:
        raise ValueError("Assessed AI inventory must not be empty")
    return {
        "total_use_cases": int(len(assessed)),
        "high_or_critical": int(assessed["risk_level"].isin(["High", "Critical"]).sum()),
        "human_oversight_coverage_pct": round(float(assessed["human_oversight"].mean() * 100), 1),
        "access_control_coverage_pct": round(float(assessed["access_control"].mean() * 100), 1),
        "audit_logging_coverage_pct": round(float(assessed["audit_logging"].mean() * 100), 1),
        "known_residency_pct": round(float((~assessed["data_residency"].str.lower().isin(["unknown", "global/unknown", "not assessed"])).mean() * 100), 1),
    }
