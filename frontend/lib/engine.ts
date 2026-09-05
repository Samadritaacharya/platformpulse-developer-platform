export type Metric = {
  label: string
  value: string
  detail: string
  tone: 'good' | 'warn' | 'risk'
}

export type RunResult = {
  scenarioId: string
  status: 'HEALTHY' | 'WATCH' | 'INTERVENE'
  score: number
  headline: string
  metrics: Metric[]
  signals: string[]
  recommendations: string[]
  trace: string[]
  contextSignals: string[]
}

type Scenario = {
  id: string
  name: string
  summary: string
  score: number
  pressure: number
  headline: string
  metrics: Array<{ label: string; base: number; slope: number; unit: string; detail: string; inverse?: boolean }>
  signals: string[]
  recommendations: string[]
}

export const project = {
  slug: 'platformpulse-developer-platform',
  name: 'PlatformPulse',
  eyebrow: 'Developer Experience · Internal Platform Product',
  title: 'Developer platform signals, under control.',
  description: 'Explore how discovery, secure self-service, service ownership, SLOs, experimentation, AI governance, and reliability combine into one measurable platform product.',
  accent: '#7c5cff',
  secondary: '#22d3ee',
  nodes: ['Discover', 'Golden Path', 'Services', 'Delivery', 'SLOs', 'Experiment', 'Govern'],
  proof: ['9 product views', 'Zero required API keys', 'Secure service generator', 'CI + browser QA'],
  scenarios: [
    {
      id: 'golden-path',
      name: 'Golden path adoption',
      summary: 'Teams move from manual onboarding to a secure self-service service template.',
      score: 88,
      pressure: 14,
      headline: 'Self-service is improving delivery without weakening controls.',
      metrics: [
        { label: 'DevEx score', base: 86, slope: -8, unit: '/100', detail: 'Composite synthetic developer-experience signal' },
        { label: 'First deploy', base: 14, slope: 8, unit: ' min', detail: 'Synthetic time to first successful deployment', inverse: true },
        { label: 'Golden path adoption', base: 78, slope: -6, unit: '%', detail: 'Share of eligible teams using the secure path' },
        { label: 'Healthy services', base: 94, slope: -10, unit: '%', detail: 'Synthetic service catalogue health coverage' },
      ],
      signals: ['Onboarding friction is concentrated outside the golden path.', 'Service ownership metadata is complete for most generated services.', 'Guardrail checks remain visible alongside adoption metrics.'],
      recommendations: ['Prioritize the remaining high-friction onboarding steps.', 'Pair adoption targets with SLO and support guardrails.', 'Use experiment evidence before expanding the template surface.'],
    },
    {
      id: 'reliability-pressure',
      name: 'Reliability pressure',
      summary: 'A week of noisy alerts and change failures puts platform reliability under stress.',
      score: 72,
      pressure: 22,
      headline: 'Reliability is acceptable, but operational friction is starting to erode trust.',
      metrics: [
        { label: 'DevEx score', base: 74, slope: -12, unit: '/100', detail: 'Developer-experience signal under operational pressure' },
        { label: 'Change failure rate', base: 15, slope: 10, unit: '%', detail: 'Synthetic failed-change indicator', inverse: true },
        { label: 'Healthy services', base: 76, slope: -18, unit: '%', detail: 'Services currently meeting platform health criteria' },
        { label: 'Support demand', base: 28, slope: 16, unit: ' req', detail: 'Synthetic weekly platform-support requests', inverse: true },
      ],
      signals: ['Deployment failures correlate with lower service health.', 'Support demand is rising faster than self-service adoption.', 'Ownership is clear enough to route the highest-risk services.'],
      recommendations: ['Focus the next roadmap slice on change reliability.', 'Add first-action runbooks to the lowest-health services.', 'Track support demand as a guardrail for platform adoption.'],
    },
    {
      id: 'ai-governance',
      name: 'AI governance review',
      summary: 'New platform AI use cases are reviewed for data, oversight, audit, and adoption readiness.',
      score: 81,
      pressure: 17,
      headline: 'AI adoption is viable when oversight and evidence stay attached to the use case.',
      metrics: [
        { label: 'Governed use cases', base: 84, slope: -9, unit: '%', detail: 'Use cases meeting the synthetic control checklist' },
        { label: 'Human oversight', base: 96, slope: -4, unit: '%', detail: 'Use cases with an explicit human-control point' },
        { label: 'Audit coverage', base: 88, slope: -8, unit: '%', detail: 'Synthetic traceability and logging coverage' },
        { label: 'Adoption readiness', base: 79, slope: -12, unit: '%', detail: 'Composite product and governance readiness' },
      ],
      signals: ['Human oversight is present for the highest-risk use cases.', 'Auditability is stronger than adoption readiness.', 'External-model and data-classification questions drive most residual risk.'],
      recommendations: ['Resolve data-classification gaps before expanding access.', 'Make audit evidence part of the release gate.', 'Separate experimentation permission from production authorization.'],
    },
  ] as Scenario[],
}

const clamp = (value: number, min = 0, max = 100) => Math.min(max, Math.max(min, value))
const round = (value: number) => Math.round(value * 10) / 10

function toneFor(value: number, inverse = false): Metric['tone'] {
  const normalized = inverse ? 100 - value : value
  if (normalized >= 80) return 'good'
  if (normalized >= 62) return 'warn'
  return 'risk'
}

export function runSimulation(scenarioId: string, intensity = 50, context = ''): RunResult {
  const scenario = project.scenarios.find((item) => item.id === scenarioId) ?? project.scenarios[0]
  const boundedIntensity = clamp(intensity)
  const pressureDelta = (boundedIntensity - 50) / 50
  const contextSignals: string[] = []
  let contextPenalty = 0

  if (/outage|blocked|breach|security incident|critical/i.test(context)) {
    contextPenalty += 7
    contextSignals.push('Context contains a high-pressure reliability or security signal.')
  }
  if (/manual|slow|friction|ticket|support/i.test(context)) {
    contextPenalty += 3
    contextSignals.push('Context suggests developer-friction or support demand.')
  }
  if (/automated|self-service|template|golden path/i.test(context)) {
    contextPenalty -= 2
    contextSignals.push('Context includes a self-service or automation signal.')
  }

  const score = Math.round(clamp(scenario.score - pressureDelta * scenario.pressure - contextPenalty, 20, 99))
  const status: RunResult['status'] = score >= 80 ? 'HEALTHY' : score >= 65 ? 'WATCH' : 'INTERVENE'

  const metrics = scenario.metrics.map((metric) => {
    const value = round(Math.max(0, metric.base + pressureDelta * metric.slope))
    return {
      label: metric.label,
      value: `${value}${metric.unit}`,
      detail: metric.detail,
      tone: toneFor(metric.inverse ? Math.max(0, 100 - value) : value),
    } satisfies Metric
  })

  return {
    scenarioId: scenario.id,
    status,
    score,
    headline: scenario.headline,
    metrics,
    signals: scenario.signals,
    recommendations: scenario.recommendations,
    trace: ['Discover signal', 'Normalize evidence', 'Score product health', 'Apply guardrails', 'Prioritize intervention', 'Publish decision view'],
    contextSignals,
  }
}
