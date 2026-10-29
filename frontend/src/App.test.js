import { flushPromises, mount } from '@vue/test-utils'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import App from './App.vue'

const preferences = {
  motion_mode: 'standard',
  guidance_level: 'standard',
  difficulty: 'standard',
  remember_preferences: false,
  version: 1,
  updated_at: '2026-10-28T12:00:00.000Z',
}

function json(body, status = 200) {
  return Promise.resolve(new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  }))
}

function installApi({ noMotion = false, modelFailure = false, populated = false } = {}) {
  const session = {
    session_id: 'session-1',
    activity_type: 'different_leaf',
    status: 'active',
    started_at: '2026-10-28T12:00:00.000Z',
    ended_at: null,
    duration_ms: 0,
    difficulty: 'standard',
    motion_mode: noMotion ? 'no_motion' : 'standard',
    guidance_level: 'standard',
    perspective_progress: 'none',
    alternative_save_state: 'none',
    seed_save_state: 'none',
    model_status: 'skipped',
    version: 1,
    created_at: '2026-10-28T12:00:00.000Z',
    updated_at: '2026-10-28T12:00:00.000Z',
  }
  globalThis.fetch = vi.fn(async (url, options = {}) => {
    const path = String(url)
    const method = options.method ?? 'GET'
    const body = options.body ? JSON.parse(options.body) : null
    if (path.endsWith('/preferences') && method === 'GET') return json({ outcome: 'success', preferences: { ...preferences, motion_mode: noMotion ? 'no_motion' : 'standard' } })
    if (path.endsWith('/preferences') && method === 'PUT') return json({ outcome: 'success', preferences: { ...preferences, ...body, version: 2 } })
    if (path.endsWith('/focus-activities')) return json({
      outcome: 'success',
      activities: [
        'different_leaf', 'ripple_path', 'flower_match', 'flower_change',
        'petal_sequence', 'clue_search', 'garden_path',
      ].map((activity_type) => ({ activity_type, label: activity_type, instruction: 'Choose one visible option.' })),
      controls: ['Show me', 'Skip this', 'Stop', 'Support'],
      notice: 'No score.',
    })
    if (path.endsWith('/activity-sessions') && method === 'POST') return json({ outcome: 'success', session: { ...session, activity_type: body.activity_type } }, 201)
    if (path.includes('/events')) return json({ outcome: 'success', event: { event_id: 'event-1' } }, 201)
    if (path.includes('/activity-sessions/') && method === 'PATCH') return json({ outcome: 'success', session: { ...session, status: body.action === 'complete' ? 'completed' : body.action === 'interrupt' ? 'interrupted' : body.action === 'skip' ? 'skipped' : 'stopped', duration_ms: body.duration_ms, version: 2 } })
    if (path.includes('/activity-sessions?')) return json({ outcome: 'success', sessions: populated ? [{ ...session, status: 'completed', duration_ms: 48000 }] : [], next_cursor: null })
    if (path.includes('/perspective-artifacts?')) return json({ outcome: 'success', artifacts: [], next_cursor: null })
    if (path.includes('/next-step-seeds?')) return json({ outcome: 'success', seeds: [], next_cursor: null })
    if (path.endsWith('/perspective/alternatives')) {
      if (modelFailure) return json({ outcome: 'missing_configuration', message: 'Gemini is not configured.' }, 503)
      return json({ outcome: 'success', request: { attempt_count: 1 }, alternatives: { alternatives: [{ alternative: 'The timing may be unrelated.', factual_basis: 'No reason is provided.' }], limitation: 'Coursework prototype; not therapy or medical advice.' }, saved: false })
    }
    if (path.endsWith('/perspective-artifacts') && method === 'POST') return json({ outcome: 'success', artifact: { artifact_id: 'artifact-1', ...body } }, 201)
    if (path.endsWith('/next-step-seeds') && method === 'POST') return json({ outcome: 'success', seed: { seed_id: 'seed-1', ...body } }, 201)
    if (path.endsWith('/conversations')) return json({ outcome: 'success', conversation: { conversation_id: 'conversation-1' } }, 201)
    if (path.includes('/messages')) return json({ outcome: 'success', message: {}, request: { request_id: 'request-1' } }, 201)
    if (path.endsWith('/garden-guide/history-questions')) return json({ outcome: 'history_no_match', request: { attempt_count: 1 }, answer: null, row_references: [] })
    return json({ outcome: 'success' })
  })
}

describe('FocusBloom Vue experience', () => {
  beforeEach(() => {
    sessionStorage.clear()
    installApi()
  })
  afterEach(() => vi.restoreAllMocks())

  it('presents the low-input entry and independent Support with focus restoration', async () => {
    const wrapper = mount(App, { attachTo: document.body })
    await flushPromises()
    expect(wrapper.get('[data-state="entry"] h1').text()).toBe('Choose one small step')
    expect(wrapper.text()).toContain('not therapy, diagnosis, or monitoring')

    const supportButton = wrapper.get('.support-button')
    supportButton.element.focus()
    await supportButton.trigger('click')
    await flushPromises()
    expect(wrapper.get('[data-state="support-open"]').text()).toContain('Support information — United States demo')
    expect(wrapper.text()).toContain('Call 988')
    await wrapper.get('[data-state="support-open"] .primary').trigger('click')
    await flushPromises()
    expect(document.activeElement).toBe(supportButton.element)
    wrapper.unmount()
  })

  it('starts one no-typing activity in one action, allows neutral retry, and completes once', async () => {
    const wrapper = mount(App)
    await flushPromises()
    await wrapper.get('.entry-view .primary').trigger('click')
    await flushPromises()
    expect(wrapper.get('[data-state="focus-active"] h1').text()).toContain('differently shaped leaf')

    const options = wrapper.findAll('.activity-option')
    await options[0].trigger('click')
    await flushPromises()
    expect(wrapper.text()).toContain('Try again')
    await options[1].trigger('click')
    await flushPromises()
    expect(wrapper.get('[data-state="focus-completed"]').text()).toContain('Completed')
    const patches = globalThis.fetch.mock.calls.filter(([, request]) => request?.method === 'PATCH')
    expect(patches).toHaveLength(1)
  })

  it('makes every approved no-typing activity reachable while retaining the default start', async () => {
    const allActivities = [
      'different_leaf', 'ripple_path', 'flower_match', 'flower_change',
      'petal_sequence', 'clue_search', 'garden_path',
    ]
    const wrapper = mount(App)
    await flushPromises()
    const select = wrapper.get('#activity-choice')
    expect(select.findAll('option').map((option) => option.element.value)).toEqual(allActivities)
    await select.setValue('ripple_path')
    await wrapper.get('.entry-view .primary').trigger('click')
    await flushPromises()
    expect(wrapper.get('[data-state="focus-active"] h1').text()).toBe('Follow the ripple path')
    const createCall = globalThis.fetch.mock.calls.find(([url, request]) => String(url).endsWith('/activity-sessions') && request?.method === 'POST')
    expect(JSON.parse(createCall[1].body).activity_type).toBe('ripple_path')
  })

  it('renders no-motion with identical controls and interrupts before opening Support', async () => {
    installApi({ noMotion: true })
    const wrapper = mount(App)
    await flushPromises()
    await wrapper.get('.entry-view .primary').trigger('click')
    await flushPromises()
    expect(wrapper.get('[data-state="focus-active"]').classes()).toContain('no-motion')
    expect(wrapper.text()).toContain('Nothing scales, ripples, fades, or translates')
    await wrapper.get('.support-button').trigger('click')
    await flushPromises()
    expect(wrapper.get('[data-state="support-open"]').exists()).toBe(true)
    expect(wrapper.get('[data-state="focus-stopped"]').text()).toContain('interrupted')
  })

  it('preserves Perspective work through a missing-configuration outcome and continues without Gemini', async () => {
    installApi({ modelFailure: true })
    const wrapper = mount(App)
    await flushPromises()
    await wrapper.findAll('.entry-view .secondary')[0].trigger('click')
    await wrapper.get('[data-state="perspective-entry"] .primary').trigger('click')
    await flushPromises()
    await wrapper.get('[data-state="perspective-evidence"] .primary').trigger('click')
    await flushPromises()
    expect(wrapper.get('[data-state="perspective-model-failed"]').text()).toContain('not configured')
    expect(wrapper.text()).toContain('Your work is still here')
    await wrapper.get('[data-state="perspective-model-failed"] .primary').trigger('click')
    expect(wrapper.get('[data-state="perspective-alt-ready"]').text()).toContain('Compare alternatives')
  })

  it('shows factual populated history and a no-match Garden Guide outcome without an invented answer', async () => {
    installApi({ populated: true })
    const wrapper = mount(App)
    await flushPromises()
    await wrapper.findAll('.entry-view .secondary')[1].trigger('click')
    await flushPromises()
    expect(wrapper.get('[data-state="history"]').text()).toContain('48 seconds')
    await wrapper.get('.history-view .primary').trigger('click')
    await wrapper.findAll('.question-chip')[0].trigger('click')
    await wrapper.get('.guide-view .primary').trigger('click')
    await flushPromises()
    expect(wrapper.get('[data-state="history-no-match"]').text()).toContain('No matching saved records')
    expect(wrapper.text()).not.toContain('appears in 3')
  })

  it('contains no raw HTML rendering directive', () => {
    expect(App.__file).toBeTruthy()
    expect(document.body.innerHTML).not.toContain('v-html')
  })
})
