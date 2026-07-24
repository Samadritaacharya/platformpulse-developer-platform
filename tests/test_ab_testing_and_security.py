from __future__ import annotations

import io
import zipfile

import pytest

from platformpulse.ab_testing import demo_experiment_data, two_proportion_test
from platformpulse.generator import ServiceConfig, generate_service_zip, sanitize_service_name, sanitize_team


def test_demo_ab_result_favours_guided_path() -> None:
    data = demo_experiment_data()
    result = two_proportion_test(
        int(data.iloc[0]["visitors"]),
        int(data.iloc[0]["successful_first_deployments"]),
        int(data.iloc[1]["visitors"]),
        int(data.iloc[1]["successful_first_deployments"]),
    )
    assert result.treatment_rate > result.control_rate
    assert result.significant is True
    assert result.p_value < 0.05


def test_ab_test_rejects_impossible_counts() -> None:
    with pytest.raises(ValueError):
        two_proportion_test(10, 11, 10, 5)
    with pytest.raises(ValueError):
        two_proportion_test(0, 0, 10, 5)


def test_service_name_blocks_path_traversal() -> None:
    assert sanitize_service_name("../../Unsafe Service") == "unsafe-service"
    assert "/" not in sanitize_service_name("../../Unsafe Service")


def test_team_rejects_code_injection_and_controls() -> None:
    assert sanitize_team("marketplace-platform") == "marketplace-platform"
    with pytest.raises(ValueError):
        sanitize_team('team"; import os; #')
    with pytest.raises(ValueError):
        sanitize_team("team\nmalicious")


def test_generated_zip_has_safe_paths_and_hardened_runtime() -> None:
    config = ServiceConfig(service_name="Catalog API", team="Platform Team", environment="production", slo_target=99.9)
    payload = generate_service_zip(config)
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        names = archive.namelist()
        assert names
        assert all(not name.startswith(("/", "\\")) for name in names)
        assert all(".." not in name.split("/") for name in names)
        dockerfile = archive.read("catalog-api/Dockerfile").decode()
        deployment = archive.read("catalog-api/kubernetes/deployment.yaml").decode()
        workflow = archive.read("catalog-api/.github/workflows/ci.yml").decode()
        assert "USER appuser" in dockerfile
        assert "allowPrivilegeEscalation: false" in deployment
        assert "readOnlyRootFilesystem: true" in deployment
        assert "automountServiceAccountToken: false" in deployment
        assert "permissions:\n  contents: read" in workflow


def test_generated_zip_rejects_invalid_enum_values() -> None:
    with pytest.raises(ValueError):
        generate_service_zip(ServiceConfig(service_name="safe", team="team", visibility="unknown"))
