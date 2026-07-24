from pathlib import Path


def test_streamlit_security_controls_are_enabled() -> None:
    config = Path(".streamlit/config.toml").read_text(encoding="utf-8")
    assert "enableCORS = true" in config
    assert "enableXsrfProtection = true" in config


def test_container_runs_non_root() -> None:
    dockerfile = Path("Dockerfile").read_text(encoding="utf-8")
    compose = Path("docker-compose.yml").read_text(encoding="utf-8")
    assert "USER 10001:10001" in dockerfile
    assert "no-new-privileges:true" in compose
    assert "cap_drop" in compose


def test_ci_is_least_privilege_and_runs_security_checks() -> None:
    workflow = Path(".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "permissions:\n  contents: read" in workflow
    assert "bandit" in workflow
    assert "pip-audit" in workflow
    assert "actions/checkout@11bd719" in workflow
