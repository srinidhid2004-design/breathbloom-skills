import { afterEach, describe, expect, it, vi } from 'vitest'
import { ApiError, api } from './api.js'

function response(body, status = 200, contentType = 'application/json') {
  return Promise.resolve(new Response(contentType === 'application/json' ? JSON.stringify(body) : body, {
    status,
    headers: { 'Content-Type': contentType },
  }))
}

describe('approved frontend API service', () => {
  afterEach(() => vi.restoreAllMocks())

  it('sends only the approved Perspective fields and no browser provider controls', async () => {
    globalThis.fetch = vi.fn(() => response({ outcome: 'success', alternatives: { alternatives: [] } }))
    const input = {
      idempotency_key: '11111111-1111-4111-8111-111111111111',
      interpretation: 'A fictional interpretation',
      supporting_evidence: ['Visible timing'],
      uncertainty: ['Reason unknown'],
      observer_mode: 'none',
    }
    await api.perspectiveAlternatives(input)
    const [, options] = globalThis.fetch.mock.calls[0]
    const sent = JSON.parse(options.body)
    expect(sent).toEqual(input)
    expect(options.headers).toEqual({ 'Content-Type': 'application/json' })
    expect(sent).not.toHaveProperty('provider')
    expect(sent).not.toHaveProperty('model')
    expect(sent).not.toHaveProperty('prompt')
    expect(sent).not.toHaveProperty('sql')
    expect(sent).not.toHaveProperty('profile_id')
    expect(sent).not.toHaveProperty('database_path')
    expect(sent).not.toHaveProperty('api_key')
    expect(JSON.stringify(options.headers)).not.toMatch(/authorization/i)
  })

  it('sends the exact two-step Garden Guide bodies', async () => {
    globalThis.fetch = vi.fn()
      .mockImplementationOnce(() => response({ outcome: 'success', message: {}, request: { request_id: 'request-1' } }, 201))
      .mockImplementationOnce(() => response({ outcome: 'history_no_match', answer: null }))
    await api.createHistoryMessage('conversation-1', { idempotency_key: 'id-1', question: 'Which activities were completed?' })
    await api.runHistoryQuestion({ request_id: 'request-1' })
    expect(JSON.parse(globalThis.fetch.mock.calls[0][1].body)).toEqual({ idempotency_key: 'id-1', question: 'Which activities were completed?' })
    expect(JSON.parse(globalThis.fetch.mock.calls[1][1].body)).toEqual({ request_id: 'request-1' })
  })

  it.each([
    ['missing_configuration', 503],
    ['invalid_request', 422],
    ['history_query_rejected', 422],
    ['database_failure', 503],
    ['model_failure', 502],
  ])('normalizes the safe %s outcome', async (outcome, status) => {
    globalThis.fetch = vi.fn(() => response({ outcome, message: 'Safe message.' }, status))
    await expect(api.health()).rejects.toMatchObject({ name: 'ApiError', outcome, status, message: 'Safe message.' })
  })

  it('handles malformed JSON without exposing raw content', async () => {
    globalThis.fetch = vi.fn(() => response('<html>private server output</html>', 502, 'text/html'))
    await expect(api.health()).rejects.toEqual(expect.objectContaining({ outcome: 'service_failure' }))
  })

  it('preserves abort cancellation as AbortError', async () => {
    globalThis.fetch = vi.fn((_url, options) => new Promise((_resolve, reject) => {
      options.signal.addEventListener('abort', () => reject(new DOMException('Aborted', 'AbortError')))
    }))
    const controller = new AbortController()
    const pending = api.health(controller.signal)
    controller.abort()
    await expect(pending).rejects.toMatchObject({ name: 'AbortError' })
  })

  it('uses a stable safe error for network failures', async () => {
    globalThis.fetch = vi.fn(() => Promise.reject(new Error('socket included a private path')))
    await expect(api.health()).rejects.toEqual(expect.objectContaining({
      outcome: 'network_failure',
      message: 'FocusBloom could not reach its local service. Your action was not saved.',
    }))
    expect(ApiError.prototype).toBeInstanceOf(Error)
  })
})
