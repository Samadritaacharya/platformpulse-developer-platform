"""Data access helpers for PlatformPulse."""
from __future__ import annotations
from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

def load_csv(filename: str) -> pd.DataFrame:
    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Missing data file: {path}")
    return pd.read_csv(path)

def load_survey() -> pd.DataFrame:
    return load_csv("survey_results.csv")

def load_services() -> pd.DataFrame:
    df = load_csv("services.csv")
    df["last_deployment"] = pd.to_datetime(df["last_deployment"])
    return df

def load_pipeline_metrics() -> pd.DataFrame:
    df = load_csv("pipeline_metrics.csv")
    df["date"] = pd.to_datetime(df["date"])
    return df

def load_feedback() -> pd.DataFrame:
    return load_csv("feedback.csv")
