import pandas as pd
import pytest

from platformpulse.data import load_ab_test_events
from platformpulse.experiments import analyze_experiment, persona_lift, validate_experiment_data, variant_summary


def test_demo_experiment_is_valid_and_actionable() -> None:
    frame = load_ab_test_events()
    result = analyze_experiment(frame)
    assert result.control_n == result.treatment_n == 30
    assert result.treatment_conversion > result.control_conversion
    assert result.absolute_uplift_pp > 0
    assert result.p_value < 0.05
    assert result.srm_p_value > 0.01
    assert result.treatment_time_min < result.control_time_min
    assert result.treatment_support_rate < result.control_support_rate
    assert result.decision.startswith("Ship Treatment")


def test_variant_and_persona_summaries_are_complete() -> None:
    frame = load_ab_test_events()
    assert set(variant_summary(frame)["variant"]) == {"Control", "Treatment"}
    segmented = persona_lift(frame)
    assert len(segmented) == 3
    assert segmented["control_n"].sum() == 30
    assert segmented["treatment_n"].sum() == 30


def test_duplicate_participant_is_rejected() -> None:
    frame = load_ab_test_events()
    invalid = pd.concat([frame, frame.iloc[[0]]], ignore_index=True)
    with pytest.raises(ValueError, match="unique"):
        validate_experiment_data(invalid)
