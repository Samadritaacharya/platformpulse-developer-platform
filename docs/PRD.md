# Product Requirements Document

## Product

PlatformPulse Developer Platform Product Lab

## Objective

Demonstrate an end-to-end product approach for reducing developer friction through discovery, self-service, ownership, platform metrics and evidence-based prioritisation.

## In scope

- Discovery evidence analysis
- Developer personas and journey
- Golden-path starter-service generation
- Service catalogue and risk filters
- Product and delivery metrics
- Feedback clustering and weighted RICE scoring
- Now / Next / Later roadmap
- Reliability scoring and recommended action
- Automated tests, CI and Docker packaging

## Out of scope

- Real cloud resource provisioning
- Production identity and access management
- Integration with proprietary engineering systems
- Automated changes to external repositories
- Claims about any company's internal tooling or metrics

## Functional requirements

1. The user can filter discovery evidence by persona.
2. The user can see journey friction and time-loss evidence.
3. The user can configure and download a generated starter service.
4. The generated service includes health, tests, CI, Docker, Kubernetes, Helm and ownership metadata.
5. The user can filter services by operational risk.
6. The user can view user-centric and technical platform KPIs.
7. The user can rank opportunities and simulate decision trade-offs.
8. The user can see service-health reasoning and a recommended first action.

## Non-functional requirements

- No login or secrets required.
- Synthetic data only.
- Deterministic demo behaviour.
- Local and Docker execution.
- Automated test coverage for core business logic.
- Clear distinction between implemented capability and future product hypothesis.
- Responsive enough for a three-minute recruiter demo.

## Success criteria

- Test suite passes in GitHub Actions.
- A generated ZIP contains at least ten expected platform artefacts.
- The README enables local execution without hidden steps.
- A reviewer can complete the discovery-to-decision demo in under three minutes.
