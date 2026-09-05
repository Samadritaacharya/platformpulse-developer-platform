import { NextResponse } from 'next/server'
import { project, runSimulation } from '@/lib/engine'

export const dynamic = 'force-dynamic'

export async function GET() {
  return NextResponse.json({
    status: 'ok',
    project: project.slug,
    engine: 'deterministic-local',
    paid_api_required: false,
    scenarios: project.scenarios.map(({ id, name }) => ({ id, name })),
  })
}

export async function POST(request: Request) {
  const raw = await request.text()
  if (raw.length > 16_000) {
    return NextResponse.json({ error: 'Request body is too large.' }, { status: 413 })
  }

  let body: unknown
  try {
    body = JSON.parse(raw || '{}')
  } catch {
    return NextResponse.json({ error: 'Body must be valid JSON.' }, { status: 400 })
  }

  if (!body || typeof body !== 'object' || Array.isArray(body)) {
    return NextResponse.json({ error: 'Body must be a JSON object.' }, { status: 422 })
  }

  const input = body as Record<string, unknown>
  const scenario = typeof input.scenario === 'string' ? input.scenario : project.scenarios[0].id
  const intensity = typeof input.intensity === 'number' && Number.isFinite(input.intensity) ? input.intensity : 50
  const context = typeof input.context === 'string' ? input.context.slice(0, 4000) : ''

  return NextResponse.json(runSimulation(scenario, intensity, context), {
    headers: { 'Cache-Control': 'no-store', 'X-Portfolio-Engine': 'deterministic-local' },
  })
}
