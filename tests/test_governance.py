import pandas as pd

from platformpulse.data import load_ai_use_cases
from platformpulse.governance import assess_inventory, assess_use_case, governance_kpis


def test_uncontrolled_ai_use_case_is_critical() -> None:
    case = pd.Series({
        "data_classification": "Restricted",
        "external_model": 1,
        "data_residency": "Unknown",
        "personal_data": 1,
        "automated_decision": 1,
        "human_oversight": 0,
        "access_control": 0,
        "audit_logging": 0,
        "stage": "Production",
    })
    result = assess_use_case(case)
    assert result.risk_level == "Critical"
    assert "Pause deployment" in result.decision
    assert any("human oversight" in control for control in result.controls)


def test_inventory_has_governance_coverage_metrics() -> None:
    assessed = assess_inventory(load_ai_use_cases())
    metrics = governance_kpis(assessed)
    assert metrics["total_use_cases"] == 6
    assert metrics["high_or_critical"] >= 1
    assert 0 <= metrics["audit_logging_coverage_pct"] <= 100
    assert set(assessed["risk_level"]).issubset({"Low", "Moderate", "High", "Critical"})
