# A/B Testing Design

## Product question

Does a secure self-service golden path improve the probability that an engineer completes a first deployment while reducing time and support demand?

## Variants

- **Control:** manual onboarding and service setup.
- **Treatment:** PlatformPulse secure golden path.

## Metrics

**Primary:** successful first deployment.  
**Guardrails:** time to first deployment, support-request rate and developer satisfaction.  
**Integrity check:** sample-ratio mismatch (SRM).

## Decision rule

Ship the Treatment only when:

1. conversion uplift is positive;
2. the two-sided normal-approximation p-value is below 0.05;
3. assignment shows no material SRM signal;
4. no guardrail regresses;
5. rollout remains staged and monitored.

## Demo result

The committed dataset is deterministic and synthetic. It is designed to exercise the complete analysis flow, including assignment validation, conversion inference, confidence interval, guardrails and persona segmentation.

## Limitations

- The data is synthetic and must not be presented as user research.
- The statistical model uses a normal approximation.
- The prototype does not model seasonality, repeated exposure, network effects or long-term retention.
- Production experiments require privacy review, power analysis, logging, quality checks and an approved rollback plan.
