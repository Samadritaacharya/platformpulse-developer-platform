from platformpulse.data import (
    load_ab_test_events,
    load_ai_use_cases,
    load_feedback,
    load_pipeline_metrics,
    load_services,
    load_survey,
)
from platformpulse.metrics import journey_stage_summary, platform_kpis
from platformpulse.reliability import catalogue_health, demo_reference_time


def test_all_demo_datasets_load_and_validate() -> None:
    survey = load_survey()
    services = load_services()
    pipelines = load_pipeline_metrics()
    feedback = load_feedback()
    experiments = load_ab_test_events()
    ai_inventory = load_ai_use_cases()
    assert not any(frame.empty for frame in (survey, services, pipelines, feedback, experiments, ai_inventory))


def test_platform_metrics_and_health_are_stable() -> None:
    survey = load_survey()
    services = load_services()
    pipelines = load_pipeline_metrics()
    kpis = platform_kpis(survey, services, pipelines)
    reference = demo_reference_time(services, pipelines)
    health = catalogue_health(services, now=reference)
    assert 0 <= kpis["developer_experience_score"] <= 100
    assert kpis["median_mttr_min"] > 0
    assert len(journey_stage_summary(survey)) > 0
    assert set(health["health_status"]).issubset({"Green", "Amber", "Red"})
    assert health["deployment_age_days"].min() >= 0
