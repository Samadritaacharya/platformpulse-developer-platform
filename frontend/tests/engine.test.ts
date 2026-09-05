import assert from 'node:assert/strict'
import test from 'node:test'
import { project, runSimulation } from '../lib/engine.ts'

test('all configured scenarios produce bounded deterministic results', () => {
  for (const scenario of project.scenarios) {
    const first = runSimulation(scenario.id, 50, '')
    const second = runSimulation(scenario.id, 50, '')
    assert.deepEqual(first, second)
    assert.ok(first.score >= 0 && first.score <= 100)
    assert.equal(first.metrics.length, 4)
    assert.ok(first.recommendations.length >= 3)
  }
})

test('operating pressure lowers the product-health score', () => {
  const low = runSimulation('golden-path', 10, '')
  const high = runSimulation('golden-path', 90, '')
  assert.ok(low.score > high.score)
})

test('context signals are recognized without changing the deterministic contract', () => {
  const result = runSimulation('golden-path', 50, 'Manual support tickets are slow after a security incident')
  assert.ok(result.contextSignals.length >= 2)
  assert.equal(result.scenarioId, 'golden-path')
})

test('unknown scenarios safely fall back to the first configured scenario', () => {
  assert.equal(runSimulation('does-not-exist').scenarioId, project.scenarios[0].id)
})
