# Discovery Report

## Research question

Where does the internal developer journey create repeated friction, and which platform capability would produce the strongest combination of user value, reliability improvement and reusable leverage?

## Method

The public demo uses synthetic responses across three personas. Evidence is intentionally labelled `Synthetic`. It demonstrates the discovery workflow and does not claim real Kaufland, SAP, IBM, Kyndryl or customer research.

A future primary-research iteration would use:
- 5-10 consented, anonymous interviews;
- a short quantitative survey;
- support-ticket and pipeline evidence;
- journey-stage observation;
- follow-up validation after an incremental release.

## Main findings from the synthetic dataset

1. **Service creation** has high friction because engineers reconstruct repository, CI and ownership controls.
2. **Build and test** generates repeated support demand when pipeline patterns and failure messages are inconsistent.
3. **Deploy** extends time to first value through manual configuration and clarification loops.
4. **Service ownership** gaps make incident and lifecycle decisions slower.
5. **Monitoring** signals are available but are not always connected to an accountable action.

## Opportunity framing

The leading hypothesis is a self-service golden path with minimum operability metadata. This is not only a code template. It bundles health, tests, CI, Docker, Kubernetes, Helm, ownership, SLO, documentation and runbook metadata.

## Limitations

- No production platform integrations.
- No real internal engineering interviews in the public repository.
- The metric model is illustrative and requires calibration against real baselines.
- Generated Kubernetes/Helm artefacts require engineering review before production use.
