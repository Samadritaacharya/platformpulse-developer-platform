import io
import zipfile

import pytest

from platformpulse.generator import (
    ServiceConfig,
    generate_service_zip,
    generated_file_preview,
    generated_paths,
    sanitize_service_name,
)


def test_sanitize_service_name() -> None:
    assert sanitize_service_name("Catalog Insights_API") == "catalog-insights-api"


def test_golden_path_zip_contains_operability_and_security_controls() -> None:
    config = ServiceConfig(
        service_name="catalog-insights-api",
        team="marketplace-platform",
        database="PostgreSQL",
        environment="staging",
        slo_target=99.9,
    )
    payload = generate_service_zip(config)
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        names = set(archive.namelist())
        assert "catalog-insights-api/app/main.py" in names
        assert "catalog-insights-api/tests/test_health.py" in names
        assert "catalog-insights-api/.github/workflows/ci.yml" in names
        assert "catalog-insights-api/kubernetes/deployment.yaml" in names
        assert "catalog-insights-api/helm/Chart.yaml" in names
        assert "catalog-insights-api/service-catalog.yaml" in names
        deployment = archive.read("catalog-insights-api/kubernetes/deployment.yaml").decode()
        dockerfile = archive.read("catalog-insights-api/Dockerfile").decode()
        workflow = archive.read("catalog-insights-api/.github/workflows/ci.yml").decode()
        assert "runAsNonRoot: true" in deployment
        assert "allowPrivilegeEscalation: false" in deployment
        assert 'drop: ["ALL"]' in deployment
        assert "USER 10001:10001" in dockerfile
        assert "permissions:\n  contents: read" in workflow
        assert "actions/checkout@11bd719" in workflow


def test_generated_paths_are_stable_and_safe() -> None:
    config = ServiceConfig(service_name="demo", team="team-a")
    paths = generated_paths(config)
    assert paths == sorted(paths)
    assert len(paths) >= 12
    assert all(".." not in path.split("/") for path in paths)


def test_team_injection_is_rejected() -> None:
    with pytest.raises(ValueError):
        ServiceConfig(service_name="demo", team='team\nmalicious: true')


def test_invalid_enum_and_slo_are_rejected() -> None:
    with pytest.raises(ValueError):
        ServiceConfig(service_name="demo", team="team-a", environment="../../prod")
    with pytest.raises(ValueError):
        ServiceConfig(service_name="demo", team="team-a", slo_target=100.0)


def test_preview_returns_one_generated_control() -> None:
    config = ServiceConfig(service_name="demo", team="team-a")
    assert "readOnlyRootFilesystem: true" in generated_file_preview(config, "kubernetes/deployment.yaml")
