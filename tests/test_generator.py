import io
import zipfile

from platformpulse.generator import ServiceConfig, generate_service_zip, generated_paths, sanitize_service_name


def test_sanitize_service_name() -> None:
    assert sanitize_service_name("Catalog Insights_API") == "catalog-insights-api"


def test_golden_path_zip_contains_operability_controls() -> None:
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


def test_generated_paths_are_stable() -> None:
    config = ServiceConfig(service_name="demo", team="team-a")
    paths = generated_paths(config)
    assert paths == sorted(paths)
    assert len(paths) >= 10
