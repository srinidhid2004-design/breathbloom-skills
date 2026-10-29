<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { activityPresentations } from '../data/activities.js'
import { api, newId, utcNow } from '../services/api.js'

const props = defineProps({ preferences: { type: Object, required: true } })
const emit = defineEmits(['state', 'perspective', 'history', 'entry'])
const state = ref('focus-ready')
const catalog = ref([])
const activityIndex = ref(0)
const session = ref(null)
const feedback = ref('')
const hintVisible = ref(false)
const busy = ref(false)
const saved = ref(false)
const startedAt = ref(0)
const ordinal = ref(0)
const error = ref('')
const active = computed(() => catalog.value[activityIndex.value] ?? { activity_type: 'different_leaf' })
const presentation = computed(() => activityPresentations[active.value.activity_type] ?? activityPresentations.different_leaf)
const duration = computed(() => Math.max(0, Date.now() - startedAt.value))
const noMotion = computed(() => props.preferences.motion_mode === 'no_motion')

function setState(next) { state.value = next; emit('state', next) }
async function event(eventType, payload = {}) {
  if (!session.value) return
  ordinal.value += 1
  await api.createEvent(session.value.session_id, {
    client_event_id: newId(), ordinal: ordinal.value, event_type: eventType,
    happened_at: utcNow(), elapsed_ms: duration.value, payload,
  })
}

async function start() {
  if (busy.value || session.value) return
  busy.value = true; error.value = ''
  try {
    const catalogResult = await api.focusActivities()
    catalog.value = catalogResult.activities
    startedAt.value = Date.now()
    const result = await api.createSession({
      client_session_id: newId(), activity_type: catalog.value[0].activity_type,
      started_at: utcNow(), difficulty: props.preferences.difficulty,
      motion_mode: props.preferences.motion_mode, guidance_level: props.preferences.guidance_level,
    })
    session.value = result.session
    sessionStorage.setItem('focusbloom_active_session', JSON.stringify({ id: session.value.session_id, version: session.value.version, startedAt: startedAt.value }))
    await event('started', { item_id: active.value.activity_type, step: 0, result: 'none' })
    setState('focus-active')
  } catch (caught) {
    error.value = caught.message
    setState('focus-stopped')
  } finally { busy.value = false }
}

async function choose(option) {
  if (busy.value || saved.value || state.value !== 'focus-active') return
  busy.value = true
  try {
    await event('attempted', { item_id: option.id, step: 1, result: option.correct ? 'correct' : 'not_correct' })
    if (!option.correct) {
      feedback.value = 'That is a different option. Try again, use Show me, or Skip this.'
      return
    }
    feedback.value = 'The visible pattern matches.'
    await event('completed', { item_id: option.id, step: 1, result: 'correct' })
    await terminal('complete')
  } catch (caught) { error.value = caught.message }
  finally { busy.value = false }
}

async function showHint() {
  if (busy.value || state.value !== 'focus-active') return
  hintVisible.value = true
  try { await event('shown', { item_id: active.value.activity_type, step: 1, result: 'shown' }) }
  catch (caught) { error.value = caught.message }
}

async function terminal(action, fromSupport = false) {
  if (!session.value || saved.value) return
  saved.value = true
  const finalAction = action === 'interrupt' ? 'interrupt' : action
  try {
    if (action !== 'complete') await event(action === 'interrupt' ? 'interrupted' : action === 'skip' ? 'skipped' : 'stopped', { item_id: active.value.activity_type, step: 1, result: 'none' })
    const result = await api.updateSession(session.value.session_id, {
      action: finalAction, expected_version: session.value.version, idempotency_key: newId(),
      ended_at: utcNow(), duration_ms: action === 'skip' ? 0 : duration.value,
      perspective_progress: 'none', model_status: 'skipped',
    })
    session.value = result.session
    sessionStorage.removeItem('focusbloom_active_session')
    setState(action === 'complete' ? 'focus-completed' : 'focus-stopped')
    feedback.value = fromSupport ? 'The activity was interrupted when Support opened. It did not resume or complete automatically.' :
      action === 'skip' ? 'This activity was skipped without a score or penalty.' :
      action === 'stop' ? 'The activity was stopped. The saved record reports only what happened.' : feedback.value
  } catch (caught) {
    saved.value = false
    error.value = `${caught.message} The interface did not mark this activity saved.`
  }
}

async function interruptForSupport() {
  if (state.value === 'focus-active') await terminal('interrupt', true)
}

function nextActivity() {
  emit('entry')
}

onMounted(start)
onBeforeUnmount(() => {
  if (state.value === 'focus-active') sessionStorage.setItem('focusbloom_active_session', JSON.stringify({ id: session.value?.session_id, version: session.value?.version, startedAt: startedAt.value }))
})
defineExpose({ interruptForSupport })
</script>

<template>
  <section
    class="view"
    :class="{ 'no-motion': noMotion }"
    :data-state="state"
    aria-labelledby="focus-heading"
  >
    <template v-if="state === 'focus-ready'">
      <span class="status-pill">Ready</span>
      <h1
        id="focus-heading"
        data-view-heading
        tabindex="-1"
      >
        Preparing one Focus Garden activity
      </h1>
      <p>One visible task will appear. No typing, score, or required completion.</p>
      <p
        class="status-text"
        role="status"
      >
        Loading the approved activity catalog…
      </p>
    </template>

    <template v-else-if="state === 'focus-active'">
      <span class="status-pill">{{ noMotion ? 'No motion' : 'Standard motion' }}</span>
      <h1
        id="focus-heading"
        data-view-heading
        tabindex="-1"
      >
        {{ presentation.title }}
      </h1>
      <p>{{ presentation.prompt }}</p>
      <p
        v-if="noMotion"
        class="caption"
      >
        Nothing scales, ripples, fades, or translates. Shape, position, and text carry the task.
      </p>
      <div
        class="activity-board"
        role="group"
        :aria-label="presentation.prompt"
      >
        <button
          v-for="option in presentation.options"
          :key="option.id"
          class="activity-option"
          type="button"
          :disabled="busy"
          @click="choose(option)"
        >
          <span
            class="activity-symbol"
            aria-hidden="true"
          >{{ option.symbol }}</span>
          <span>{{ option.label }}</span>
        </button>
      </div>
      <p
        v-if="hintVisible"
        class="hint"
        role="status"
      >
        {{ presentation.hint }}
      </p>
      <p
        v-if="feedback"
        class="status-text"
        role="status"
      >
        {{ feedback }}
      </p>
      <p
        v-if="error"
        class="error-text"
        role="alert"
      >
        {{ error }}
      </p>
      <div class="button-row controls-row">
        <button
          class="button secondary"
          type="button"
          :disabled="busy"
          @click="showHint"
        >
          Show me
        </button>
        <button
          class="button secondary"
          type="button"
          :disabled="busy"
          @click="terminal('skip')"
        >
          Skip this
        </button>
        <button
          class="button stop"
          type="button"
          :disabled="busy"
          @click="terminal('stop')"
        >
          Stop
        </button>
      </div>
      <p class="caption">
        Incorrect choices receive neutral feedback. Stop and Skip remain available.
      </p>
    </template>

    <template v-else>
      <span class="status-pill">{{ state === 'focus-completed' ? 'Completed' : 'Stopped or interrupted' }}</span>
      <h1
        id="focus-heading"
        data-view-heading
        tabindex="-1"
      >
        {{ state === 'focus-completed' ? 'Focus Garden complete' : 'Focus Garden ended' }}
      </h1>
      <p>This record reports what happened. It does not score attention or claim an effect.</p>
      <dl
        v-if="session"
        class="fact-list"
      >
        <div><dt>Activity</dt><dd>{{ presentation.title }}</dd></div>
        <div><dt>Status</dt><dd>{{ session.status }}</dd></div>
        <div><dt>Duration</dt><dd>{{ Math.round((session.duration_ms || 0) / 1000) }} seconds</dd></div>
        <div><dt>Difficulty</dt><dd>{{ session.difficulty }}</dd></div>
        <div><dt>Model</dt><dd>{{ session.model_status }}</dd></div>
      </dl>
      <p
        v-if="feedback"
        class="status-text"
        role="status"
      >
        {{ feedback }}
      </p>
      <p
        v-if="error"
        class="error-text"
        role="alert"
      >
        {{ error }}
      </p>
      <button
        class="button primary full-width"
        type="button"
        @click="$emit('perspective')"
      >
        Try the fictional example
      </button>
      <button
        class="button secondary full-width"
        type="button"
        @click="$emit('history')"
      >
        Open History Garden
      </button>
      <button
        class="button secondary full-width"
        type="button"
        @click="nextActivity"
      >
        Return to entry
      </button>
    </template>
  </section>
</template>
