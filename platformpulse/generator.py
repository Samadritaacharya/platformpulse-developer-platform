"""Secure-by-default self-service golden-path starter-service generator."""
from __future__ import annotations

import io
import json
import re
import textwrap
import zipfile
from dataclasses import dataclass
from typing import Final

import yaml

_ALLOWED_LANGUAGES: Final = {"Python"}
_ALLOWED_VISIBILITY: Final = {"internal", "private", "public"}
_ALLOWED_DATABASES: Final = {"None", "PostgreSQL", "MySQL", "Redis"}
_ALLOWED_ENVIRONMENTS: Final = {"development", "staging", "production"}
_SAFE_TEXT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 ._/-]{0,79}$")
_GENERATED_REQUIREMENTS: Final = """fastapi==0.139.2
starlette==1.3.1
uvicorn==0.35.0
pytest==9.0.3
httpx==0.28.1
"""


@dataclass(frozen=True)
class ServiceConfig:
    service_name: str
    team: str
    language: str = "Python"
    visibility: str = "internal"
    database: str = "None"
    environment: str = "development"
    slo_target: float = 99.9

    def __post_init__(self) -> None:
        sanitize_service_name(self.service_name)
        sanitize_team_name(self.team)
        if self.language not in _ALLOWED_LANGUAGES:
            raise ValueError(f"Unsupported language: {self.language}")
        if self.visibility not in _ALLOWED_VISIBILITY:
            raise ValueError(f"Unsupported repository visibility: {self.visibility}")
        if self.database not in _ALLOWED_DATABASES:
            raise ValueError(f"Unsupported database: {self.database}")
        if self.environment not in _ALLOWED_ENVIRONMENTS:
            raise ValueError(f"Unsupported environment: {self.environment}")
        if not 99.0 <= float(self.slo_target) <= 99.99:
            raise ValueError("SLO target must be between 99.0 and 99.99")


def sanitize_service_name(value: str) -> str:
    cleaned = re.sub(r"[^a-z0-9-]+", "-", value.strip().lower().replace("_", "-"))
    cleaned = re.sub(r"-+", "-", cleaned).strip("-")
    if not cleaned or not re.search(r"[a-z0-9]", cleaned):
        raise ValueError("Service name must contain at least one letter or number.")
    return cleaned[:63]


def sanitize_team_name(value: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError("Owning team is required")
    if any(ord(char) < 32 for char in cleaned):
        raise ValueError("Owning team must not contain control characters")
    if not _SAFE_TEXT.fullmatch(cleaned):
        raise ValueError("Owning team contains unsupported characters or is too long")
    return cleaned


def _python_literal(value: str) -> str:
    return json.dumps(value, ensure_ascii=True)


def _files(config: ServiceConfig) -> dict[str, str]:
    name = sanitize_service_name(config.service_name)
    team = sanitize_team_name(config.team)
    db_note = config.database if config.database != "None" else "No database"
    catalog = {
        "apiVersion": "platformpulse.dev/v1",
        "kind": "Service",
        "metadata": {"name": name, "visibility": config.visibility, "owner": team},
        "spec": {
            "language": config.language,
            "environment": config.environment,
            "database": config.database,
            "slo": {"availabilityTarget": float(config.slo_target)},
            "security": {
                "runAsNonRoot": True,
                "readOnlyRootFilesystem": True,
                "leastPrivilege": True,
                "auditLogging": True,
            },
            "links": {
                "repository": f"https://github.com/example/{name}",
                "documentation": f"https://docs.example.internal/services/{name}",
                "runbook": f"https://runbooks.example.internal/{name}",
            },
        },
    }

    main_py = f'''"""Generated FastAPI starter service for {name}."""
from fastapi import FastAPI

app = FastAPI(title={_python_literal(name)}, version="0.1.0", docs_url="/docs")

@app.get("/health", include_in_schema=False)
def health() -> dict[str, str]:
    return {{"status": "ok", "service": {_python_literal(name)}}}

@app.get("/ready", include_in_schema=False)
def ready() -> dict[str, str]:
    return {{"status": "ready", "service": {_python_literal(name)}}}

@app.get("/")
def root() -> dict[str, str]:
    return {{"message": "Welcome", "service": {_python_literal(name)}, "owner": {_python_literal(team)}}}
'''
    test_py = f'''from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {{"status": "ok", "service": {_python_literal(name)}}}


def test_readiness() -> None:
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"
'''
    workflow = f'''name: {name} CI

on:
  push:
    branches: [main]
  pull_request:

permissions:
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2
      - uses: actions/setup-python@42375524e23c412d93fb67b49958b491fce71c38 # v5.4.0
        with:
          python-version: "3.11"
          cache: pip
      - run: python -m pip install --upgrade pip
      - run: python -m pip install -r requirements.txt
      - run: python -m pip check
      - run: python -m pytest -q
'''
    deployment = f'''apiVersion: apps/v1
kind: Deployment
metadata:
  name: {name}
spec:
  replicas: 2
  selector:
    matchLabels:
      app: {name}
  template:
    metadata:
      labels:
        app: {name}
    spec:
      automountServiceAccountToken: false
      securityContext:
        runAsNonRoot: true
        runAsUser: 10001
        runAsGroup: 10001
        fsGroup: 10001
        seccompProfile:
          type: RuntimeDefault
      containers:
        - name: {name}
          image: ghcr.io/example/{name}:0.1.0
          imagePullPolicy: IfNotPresent
          ports:
            - containerPort: 8000
          readinessProbe:
            httpGet:
              path: /ready
              port: 8000
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop: ["ALL"]
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 500m
              memory: 512Mi
'''
    service = f'''apiVersion: v1
kind: Service
metadata:
  name: {name}
spec:
  selector:
    app: {name}
  ports:
    - port: 80
      targetPort: 8000
'''
    dockerfile = textwrap.dedent('''\
        FROM python:3.11-slim
        ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
        RUN groupadd --system --gid 10001 appgroup && useradd --system --uid 10001 --gid appgroup --create-home appuser
        WORKDIR /app
        COPY requirements.txt .
        RUN python -m pip install --no-cache-dir -r requirements.txt && python -m pip check
        COPY --chown=appuser:appgroup . .
        USER 10001:10001
        EXPOSE 8000
        HEALTHCHECK CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)"
        CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]
    ''')
    readme = f'''# {name}

Generated by PlatformPulse's secure-by-default golden path.

- Team: **{team}**
- Visibility: **{config.visibility}**
- Environment: **{config.environment}**
- SLO target: **{float(config.slo_target)}%**
- Data dependency: **{db_note}**

```bash
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
python -m pytest -q
```

Before production, replace example URLs, pin images by digest, add endpoint authentication, use external secret management, and run vulnerability scans.
'''
    compose = f'''services:
  {name}:
    build: .
    ports:
      - "8000:8000"
    read_only: true
    tmpfs: [/tmp]
    security_opt: [no-new-privileges:true]
    cap_drop: [ALL]
'''
    files = {
        f"{name}/app/__init__.py": "",
        f"{name}/app/main.py": main_py,
        f"{name}/tests/test_health.py": test_py,
        f"{name}/requirements.txt": _GENERATED_REQUIREMENTS,
        f"{name}/Dockerfile": dockerfile,
        f"{name}/docker-compose.yml": compose,
        f"{name}/.dockerignore": ".git\n.venv\n__pycache__\n.pytest_cache\n.env\n",
        f"{name}/.github/workflows/ci.yml": workflow,
        f"{name}/kubernetes/deployment.yaml": deployment,
        f"{name}/kubernetes/service.yaml": service,
        f"{name}/helm/Chart.yaml": f"apiVersion: v2\nname: {name}\ndescription: Generated Helm chart\ntype: application\nversion: 0.1.0\nappVersion: \"0.1.0\"\n",
        f"{name}/helm/values.yaml": f"replicaCount: 2\nimage:\n  repository: ghcr.io/example/{name}\n  tag: 0.1.0\nservice:\n  port: 80\nslo:\n  availabilityTarget: {float(config.slo_target)}\nowner: {json.dumps(team)}\n",
        f"{name}/service-catalog.yaml": yaml.safe_dump(catalog, sort_keys=False),
        f"{name}/README.md": readme,
        f"{name}/.gitignore": "__pycache__/\n.pytest_cache/\n.venv/\n.env\n",
    }
    if any(".." in path.split("/") for path in files):
        raise ValueError("Generated archive contains an unsafe path")
    return files


def generate_service_zip(config: ServiceConfig) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED, strict_timestamps=False) as archive:
        for path, content in _files(config).items():
            archive.writestr(path, content)
    return buffer.getvalue()


def generated_paths(config: ServiceConfig) -> list[str]:
    return sorted(_files(config).keys())


def generated_file_preview(config: ServiceConfig, path_suffix: str) -> str:
    matches = [content for path, content in _files(config).items() if path.endswith(path_suffix)]
    if len(matches) != 1:
        raise ValueError(f"Expected one generated file ending with {path_suffix}")
    return matches[0]
