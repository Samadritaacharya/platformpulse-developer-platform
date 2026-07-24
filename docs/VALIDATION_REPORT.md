# Validation Report

## Automated validation

The repository contains tests for:

- safe service-name normalisation;
- golden-path ZIP structure;
- inclusion of CI, Docker, Kubernetes, Helm, ownership and SLO artefacts;
- stable generated path preview;
- weighted prioritisation behaviour;
- effort validation;
- roadmap assignment;
- Developer Experience Score bounds;
- journey-stage aggregation;
- service-health risk classification.

GitHub Actions runs:

```bash
python -m pytest -q
python -m compileall app.py platformpulse
```

## Local result

`9 passed`

## Manual validation checklist

- [ ] Streamlit application starts locally.
- [ ] All navigation pages render.
- [ ] Synthetic-data disclaimer is visible.
- [ ] Persona filtering works.
- [ ] Golden-path ZIP downloads and opens.
- [ ] Generated FastAPI service contains the documented artefacts.
- [ ] Service-catalogue risk filters work.
- [ ] Decision Simulator updates the score and recommendation.
- [ ] Reliability view changes by selected service.
- [ ] Docker image builds and health endpoint responds.
- [ ] No secrets, tokens or confidential data are present.

## Known limitations

- A live Streamlit URL must be added after deployment.
- No production system or cloud account is connected.
