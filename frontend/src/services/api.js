const API_ROOT = '/api'

export class ApiError extends Error {
  constructor(outcome, message, status = 0, details = null) {
    super(message)
    this.name = 'ApiError'
    this.outcome = outcome
    this.status = status
    this.details = details
  }
}
export function newId() {
  return globalThis.crypto?.randomUUID?.() ?? `00000000-0000-4000-8000-${Date.now().toString().padStart(12, '0').slice(-12)}`
}

export function utcNow() {
  return new Date().toISOString()
}

async function request(path, { method = 'GET', body, signal } = {}) {
  let response
  try {
    response = await fetch(`${API_ROOT}${path}`, {
      method,
      signal,
      headers: body === undefined ? undefined : { 'Content-Type': 'application/json' },
      body: body === undefined ? undefined : JSON.stringify(body),
    })
  } catch (error) {
    if (error?.name === 'AbortError') throw error
    throw new ApiError('network_failure', 'FocusBloom could not reach its local service. Your action was not saved.')
  }

  let payload
  try {
    payload = await response.json()
  } catch {
    throw new ApiError(
      response.ok ? 'malformed_response' : 'service_failure',
      response.ok
        ? 'The local service returned an unreadable response. Nothing was assumed saved.'
        : 'The local service could not complete that request. Nothing was assumed saved.',
      response.status,
    )
  }

  if (!response.ok) {
    throw new ApiError(
      typeof payload?.outcome === 'string' ? payload.outcome : 'service_failure',
      typeof payload?.message === 'string' ? payload.message : 'The local service could not complete that request.',
      response.status,
      payload,
    )
  }
  if (!payload || typeof payload !== 'object') {
    throw new ApiError('malformed_response', 'The local service returned an unreadable response. Nothing was assumed saved.', response.status)
  }
  return payload
}

export const api = {
  health: (signal) => request('/health', { signal }),
  preferences: (signal) => request('/preferences', { signal }),
  savePreferences: (preferences, signal) => request('/preferences', { method: 'PUT', body: preferences, signal }),
  focusActivities: (signal) => request('/focus-activities', { signal }),
  createSession: (session, signal) => request('/activity-sessions', { method: 'POST', body: session, signal }),
  updateSession: (sessionId, update, signal) => request(`/activity-sessions/${encodeURIComponent(sessionId)}`, { method: 'PATCH', body: update, signal }),
  createEvent: (sessionId, event, signal) => request(`/activity-sessions/${encodeURIComponent(sessionId)}/events`, { method: 'POST', body: event, signal }),
  sessions: (filters = {}, signal) => {
    const query = new URLSearchParams({ cursor: String(filters.cursor ?? 0), limit: String(filters.limit ?? 20) })
    if (filters.status) query.set('status', filters.status)
    if (filters.activity_type) query.set('activity_type', filters.activity_type)
    return request(`/activity-sessions?${query}`, { signal })
  },
  perspectiveAlternatives: (input, signal) => request('/perspective/alternatives', { method: 'POST', body: input, signal }),
  createArtifact: (artifact, signal) => request('/perspective-artifacts', { method: 'POST', body: artifact, signal }),
  artifacts: (signal) => request('/perspective-artifacts?cursor=0&limit=20', { signal }),
  deleteArtifact: (artifactId, signal) => request(`/perspective-artifacts/${encodeURIComponent(artifactId)}`, { method: 'DELETE', signal }),
  createSeed: (seed, signal) => request('/next-step-seeds', { method: 'POST', body: seed, signal }),
  seeds: (signal) => request('/next-step-seeds?cursor=0&limit=20', { signal }),
  deleteSeed: (seedId, signal) => request(`/next-step-seeds/${encodeURIComponent(seedId)}`, { method: 'DELETE', signal }),
  createConversation: (input, signal) => request('/conversations', { method: 'POST', body: input, signal }),
  createHistoryMessage: (conversationId, input, signal) => request(`/conversations/${encodeURIComponent(conversationId)}/messages`, { method: 'POST', body: input, signal }),
  runHistoryQuestion: (input, signal) => request('/garden-guide/history-questions', { method: 'POST', body: input, signal }),
  deleteSavedText: (signal) => request('/demo/saved-text', { method: 'DELETE', body: { confirmation: 'DELETE SAVED FOCUSBLOOM TEXT' }, signal }),
  resetDemo: (expectedResetVersion, signal) => request('/demo/reset', {
    method: 'POST',
    body: { confirmation: 'RESET FICTIONAL FOCUSBLOOM DATA', expected_reset_version: expectedResetVersion, idempotency_key: newId() },
    signal,
  }),
}
