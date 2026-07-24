"""Security-conscious self-service golden-path starter-service generator."""
from __future__ import annotations

import io
import json
import re
import textwrap
import zipfile
from dataclasses import dataclass

import yaml

ALLOWED_LANGUAGES = {"Python"}
ALLOWED_VISIBILITIES = {"internal", "private", "public"}
ALLOWED_DATABASES = {"None", "PostgreSQL", "MySQL", "Redis"}
ALLOWED_ENVIRONMENTS = {"development", "staging", "production"}


@dataclass(frozen=True)
class ServiceConfig:
    service_name: str
    team: str
    language: str = "Python"
    visibility: str = "internal"
    database: str = "None"
    environment: str = "development"
    slo_target: float = 99.9


def sanitize_service_name(value: str) -> str:
    cleaned = re.sub(r"[^a-z0-9-]+", "-", str(value).strip().lower().replace("_", "-"))
    cleaned = re.sub(r"-+", "-", cleaned).strip("-")
    if not cleaned:
        raise ValueError("Service name must contain at least one letter or number.")
    return cleaned[:63]


def sanitize_team(value: str) -> str:
    """Return display-safe ownership text and reject control/code-injection characters."""
    team = str(value).strip() or "unassigned-team"
    if len(team) > 80:
        raise ValueError("Owning team must be 80 characters or fewer.")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9 ._/-]*", team):
        raise ValueError("Owning team may contain letters, numbers, spaces, dots, underscores, slashes and hyphens only.")
    return team


def validate_config(config: ServiceConfig) -> ServiceConfig:
    sanitize_service_name(config.service_name)
    sanitize_team(config.team)
    if config.language not in ALLOWED_LANGUAGES:
        raise ValueError("Unsupported language selection.")
    if config.visibility not in ALLOWED_VISIBILITIES:
        raise ValueError("Unsupported repository visibility.")
    if config.database not in ALLOWED_DATABASES:
        raise ValueError("Unsupported database selection.")
    if config.environment not in ALLOWED_ENVIRONMENTS:
        raise ValueError("Unsupported environment selection.")
    if not 90.0 <= float(config.slo_target) <= 99.999:
        raise ValueError("SLO target must be between 90.0 and 99.999.")
    return config


def _files(config: ServiceConfig) -> dict[str, str]:
    validate_config(config)
    name = sanitize_service_name(config.service_name)
    team = sanitize_team(config.team)
    team_literal = json.dumps(team)
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
            "links": {
                "repository": f"https://github.com/example/{name}",
                "documentation": f"https://docs.example.internal/services/{name}",
                "runbook": f"https://runbooks.example.internal/{name}",
            },
        },
    }

    main_py = f'''# Generated FastAPI starter service for {name}.
from fastapi import FastAPI

app = FastAPI(title={json.dumps(name)}, version="0.1.0")

@app.get("/health")
def health() -> dict[str, str]:
    return {{"status": "ok", "service": {json.dumps(name)}}}

@app.get("/")
def root() -> dict[str, str]:
    return {{"message": "Welcome to {name}", "owner": {team_literal}}}
'''

    test_py = f'''from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {{"status": "ok", "service": {json.dumps(name)}}}
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
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: python -m pip install --upgrade pip
      - run: python -m pip install -r requirements.txt
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
        seccompProfile:
          type: RuntimeDefault
      containers:
        - name: {name}
          image: ghcr.io/example/{name}:0.1.0
          imagePullPolicy: IfNotPresent
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop: ["ALL"]
          ports:
            - containerPort: 8000
          readinessProbe:
            httpGet:
              path: /health
              port: 8000
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
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

    readme = f'''# {name}

Generated by PlatformPulse's self-service golden path.

## Ownership
- Team: **{team}**
- Visibility: **{config.visibility}**
- Environment: **{config.environment}**
- SLO target: **{float(config.slo_target)}%**
- Data dependency: **{db_note}**

## Run locally
```bash
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```
Open `http://localhost:8000/health`.

## Test
```bash
python -m pytest -q
```
'''

    dockerfile = textwrap.dedent('''\
        FROM python:3.11-slim
        ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
        RUN useradd --create-home --uid 10001 appuser
        WORKDIR /app
        COPY requirements.txt .
        RUN python -m pip install --no-cache-dir -r requirements.txt
        COPY --chown=appuser:appuser . .
        USER appuser
        EXPOSE 8000
        CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
    ''')

    return {
        f"{name}/app/__init__.py": "",
        f"{name}/app/main.py": main_py,
        f"{name}/tests/test_health.py": test_py,
        f"{name}/requirements.txt": "fastapi==0.116.1\nuvicorn==0.35.0\npytest==8.4.2\nhttpx==0.28.1\n",
        f"{name}/Dockerfile": dockerfile,
        f"{name}/docker-compose.yml": f'services:\n  {name}:\n    build: .\n    ports:\n      - "8000:8000"\n    read_only: true\n    security_opt:\n      - no-new-privileges:true\n',
        f"{name}/.github/workflows/ci.yml": workflow,
        f"{name}/kubernetes/deployment.yaml": deployment,
        f"{name}/kubernetes/service.yaml": service,
        f"{name}/helm/Chart.yaml": f'apiVersion: v2\nname: {name}\ndescription: Generated Helm chart for {name}\ntype: application\nversion: 0.1.0\nappVersion: "0.1.0"\n',
        f"{name}/helm/values.yaml": f'replicaCount: 2\nimage:\n  repository: ghcr.io/example/{name}\n  tag: 0.1.0\nservice:\n  port: 80\nslo:\n  availabilityTarget: {float(config.slo_target)}\nowner: {json.dumps(team)}\n',
        f"{name}/service-catalog.yaml": yaml.safe_dump(catalog, sort_keys=False),
        f"{name}/README.md": readme,
        f"{name}/.gitignore": "__pycache__/\n.pytest_cache/\n.venv/\n.env\n",
    }


def generate_service_zip(config: ServiceConfig) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for path, content in _files(config).items():
            archive.writestr(path, content)
    buffer.seek(0)
    return buffer.getvalue()


def generated_paths(config: ServiceConfig) -> list[str]:
    return sorted(_files(config).keys())
