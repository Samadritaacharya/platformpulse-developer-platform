"""Validated data access helpers for PlatformPulse demo datasets."""
from __future__ import annotations

from pathlib import Path
from typing import Final

import pandas as pd

DATA_DIR: Final = Path(__file__).resolve().parent.parent / "data"
_ALLOWED_DATASETS: Final = {
    "survey_results.csv",
    "services.csv",
    "pipeline_metrics.csv",
    "feedback.csv",
    "ab_test_events.csv",
    "ai_use_cases.csv",
}

_SCHEMAS: Final[dict[str, set[str]]] = {
    "survey_results.csv": {
        "respondent_id", "persona", "journey_stage", "friction_score",
        "frequency", "minutes_lost", "comment", "source_type",
    },
    "services.csv": {
        "service_name", "team", "repository", "language", "environment",
        "documentation", "last_deployment", "pipeline_status", "slo_target",
        "slo_actual", "open_incidents", "runbook", "created_via_golden_path",
    },
    "pipeline_metrics.csv": {
        "date", "service_name", "pipeline_success", "pipeline_duration_min",
        "deployment_count", "lead_time_hours", "change_failed", "mttr_minutes",
        "support_requests",
    },
    "feedback.csv": {
        "id", "persona", "journey_stage", "problem", "evidence_count",
        "reach", "impact", "confidence", "effort", "strategic_alignment",
        "reliability_risk", "status",
    },
    "ab_test_events.csv": {
        "participant_id", "variant", "persona", "completed_first_deploy",
        "time_to_first_deploy_min", "support_request", "satisfaction_score",
        "exposure_date",
    },
    "ai_use_cases.csv": {
        "use_case_id", "name", "owner", "stage", "model_type",
        "data_classification", "external_model", "data_residency",
        "personal_data", "automated_decision", "human_oversight",
        "access_control", "audit_logging", "business_purpose",
    },
}


def _validate_dataset_name(filename: str) -> None:
    if filename not in _ALLOWED_DATASETS:
        raise ValueError(f"Unsupported dataset: {filename}")


def _validate_columns(filename: str, frame: pd.DataFrame) -> None:
    missing = _SCHEMAS[filename].difference(frame.columns)
    if missing:
        raise ValueError(f"{filename} is missing required columns: {sorted(missing)}")
    if frame.empty:
        raise ValueError(f"{filename} must not be empty")


def load_csv(filename: str) -> pd.DataFrame:
    """Load a known local CSV with schema checks and no user-controlled path access."""
    _validate_dataset_name(filename)
    path = DATA_DIR / filename
    if not path.is_file():
        raise FileNotFoundError(f"Missing data file: {path}")
    try:
        frame = pd.read_csv(path)
    except (pd.errors.ParserError, UnicodeDecodeError) as exc:
        raise ValueError(f"Could not parse {filename}: {exc}") from exc
    _validate_columns(filename, frame)
    return frame


def load_survey() -> pd.DataFrame:
    frame = load_csv("survey_results.csv")
    numeric = ["friction_score", "frequency", "minutes_lost"]
    frame[numeric] = frame[numeric].apply(pd.to_numeric, errors="raise")
    if not frame["friction_score"].between(1, 5).all():
        raise ValueError("Survey friction scores must be between 1 and 5")
    return frame


def load_services() -> pd.DataFrame:
    frame = load_csv("services.csv")
    frame["last_deployment"] = pd.to_datetime(frame["last_deployment"], errors="raise", utc=True)
    numeric = ["slo_target", "slo_actual", "open_incidents", "created_via_golden_path"]
    frame[numeric] = frame[numeric].apply(pd.to_numeric, errors="raise")
    return frame


def load_pipeline_metrics() -> pd.DataFrame:
    frame = load_csv("pipeline_metrics.csv")
    frame["date"] = pd.to_datetime(frame["date"], errors="raise", utc=True)
    numeric = [
        "pipeline_success", "pipeline_duration_min", "deployment_count",
        "lead_time_hours", "change_failed", "mttr_minutes", "support_requests",
    ]
    frame[numeric] = frame[numeric].apply(pd.to_numeric, errors="raise")
    return frame


def load_feedback() -> pd.DataFrame:
    frame = load_csv("feedback.csv")
    numeric = [
        "evidence_count", "reach", "impact", "confidence", "effort",
        "strategic_alignment", "reliability_risk",
    ]
    frame[numeric] = frame[numeric].apply(pd.to_numeric, errors="raise")
    return frame


def load_ab_test_events() -> pd.DataFrame:
    frame = load_csv("ab_test_events.csv")
    frame["exposure_date"] = pd.to_datetime(frame["exposure_date"], errors="raise", utc=True)
    numeric = [
        "completed_first_deploy", "time_to_first_deploy_min", "support_request",
        "satisfaction_score",
    ]
    frame[numeric] = frame[numeric].apply(pd.to_numeric, errors="raise")
    return frame


def load_ai_use_cases() -> pd.DataFrame:
    frame = load_csv("ai_use_cases.csv")
    binary = [
        "external_model", "personal_data", "automated_decision",
        "human_oversight", "access_control", "audit_logging",
    ]
    frame[binary] = frame[binary].apply(pd.to_numeric, errors="raise")
    return frame
