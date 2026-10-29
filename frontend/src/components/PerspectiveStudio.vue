<script setup>
import { computed, ref } from 'vue'
import { api, newId, utcNow } from '../services/api.js'
import { useLatestRequest } from '../composables/useLatestRequest.js'

const props = defineProps({ preferences: { type: Object, required: true } })
const emit = defineEmits(['state', 'seed', 'history', 'entry'])
const requestGuard = useLatestRequest()
const state = ref('perspective-entry')
const mode = ref('fictional')
const interpretation = ref('A fictional classmate left because Alex’s idea was bad.')
const customText = ref('')
const supporting = ref(['A classmate left soon after Alex spoke.'])
const uncertainty = ref(['The reason for leaving is unknown.', 'Timing alone does not establish cause.'])
const alternatives = ref([])
const selectedAlternative = ref('')
const alternativeSource = ref('fictional_example')
const editMode = ref(false)
const observerMode = ref('none')
const observerLabel = ref('Alex')
const session = ref(null)
const startedAt = ref(0)
const ordinal = ref(0)
const busy = ref(false)
const error = ref('')
const savedArtifact = ref(null)
const modelOutcome = ref('skipped')
const requestPreview = computed(() => ({
  interpretation: interpretation.value,
  supporting_evidence: supporting.value,
  uncertainty: uncertainty.value,
  observer_mode: observerMode.value,
}))

function setState(next) { state.value = next; emit('state', next) }
async function recordStep(step, type = 'perspective_step') {
  if (!session.value) return
  ordinal.value += 1
  await api.createEvent(session.value.session_id, {
    client_event_id: newId(), ordinal: ordinal.value, event_type: type,
    happened_at: utcNow(), elapsed_ms: Date.now() - startedAt.value,
    payload: { item_id: step, step: ordinal.value, result: 'none' },
  })
}

async function begin(selectedMode) {
  if (busy.value) return
  mode.value = selectedMode
  if (selectedMode === 'custom') {
    if (!customText.value.trim()) return
    interpretation.value = customText.value.trim()
  }
  busy.value = true; error.value = ''; startedAt.value = Date.now()
  try {
    const result = await api.createSession({
      client_session_id: newId(), activity_type: 'perspective_studio', started_at: utcNow(),
      difficulty: props.preferences.difficulty, motion_mode: props.preferences.motion_mode,
      guidance_level: props.preferences.guidance_level,
    })
    session.value = result.session
    await recordStep('interpretation')
    setState('perspective-evidence')
  } catch (caught) { error.value = caught.message }
  finally { busy.value = false }
}

function toggleCard(list, text) {
  const index = list.indexOf(text)
  if (index >= 0) list.splice(index, 1)
  else if (list.length < 3) list.push(text)
}

async function requestAlternatives() {
  if (busy.value) return
  const guard = requestGuard.begin()
  busy.value = true; error.value = ''; setState('perspective-alt-loading')
  try {
    await recordStep('alternatives-requested')
    const result = await api.perspectiveAlternatives({ idempotency_key: newId(), ...requestPreview.value }, guard.signal)
    if (!requestGuard.isCurrent(guard.id)) return
    if (result.outcome === 'duplicate_request' && !result.alternatives) {
      error.value = 'This request was already received. No duplicate alternative was added.'
      modelOutcome.value = 'duplicate_request'
      setState('perspective-model-failed')
      return
    }
    alternatives.value = result.alternatives.alternatives
    modelOutcome.value = 'succeeded'
    alternativeSource.value = 'gemini'
    setState('perspective-alt-ready')
  } catch (caught) {
    if (caught.name === 'AbortError' || !requestGuard.isCurrent(guard.id)) return
    modelOutcome.value = caught.outcome ?? 'model_failure'
    error.value = modelMessage(modelOutcome.value)
    setState('perspective-model-failed')
  } finally { if (requestGuard.isCurrent(guard.id)) busy.value = false }
}

function modelMessage(outcome) {
  const messages = {
    missing_configuration: 'Gemini is not configured. Your unsaved work remains here, and you can continue without it.',
    invalid_request: 'The request did not match the approved bounded format. Your work was not sent again.',
    authentication_failure: 'The provider could not authenticate the backend request. Your work remains unsaved.',
    permission_failure: 'The provider did not permit this request. Your work remains unsaved.',
    quota_failure: 'The provider quota was unavailable. Your work remains unsaved.',
    rate_limit: 'The provider asked the backend to wait. FocusBloom does not retry automatically.',
    timeout: 'The provider request timed out. FocusBloom does not retry automatically.',
    malformed_response: 'The provider response did not match the approved format and was not used.',
    duplicate_request: 'The same request was already recorded; no second request was made.',
    model_failure: 'The provider could not complete the request. Your unsaved work remains here.',
  }
  return messages[outcome] ?? messages.model_failure
}

function continueWithoutModel() {
  requestGuard.cancel()
  busy.value = false
  alternatives.value = [
    { alternative: 'They may have needed to leave.', factual_basis: 'The fictional scenario does not give a reason for leaving.' },
    { alternative: 'The timing may be unrelated.', factual_basis: 'Events occurring together do not establish cause.' },
  ]
  alternativeSource.value = 'fictional_example'
  modelOutcome.value = 'skipped'
  setState('perspective-alt-ready')
}

function selectAlternative(item) {
  selectedAlternative.value = item.alternative
  editMode.value = false
}

function createOwn() {
  selectedAlternative.value = ''
  alternativeSource.value = 'user'
  editMode.value = true
}

function useLens() {
  observerMode.value = 'fictional_alex'
  if (!selectedAlternative.value) selectedAlternative.value = `${observerLabel.value || 'Alex'} may not have all relevant context.`
}

async function saveArtifact() {
  if (busy.value || !selectedAlternative.value.trim()) return
  busy.value = true; error.value = ''
  try {
    const result = await api.createArtifact({
      client_artifact_id: newId(), session_id: session.value?.session_id ?? null,
      interpretation_text: interpretation.value, supporting_evidence: supporting.value,
      uncertainty: uncertainty.value, alternative_text: selectedAlternative.value.trim(),
      alternative_source: alternativeSource.value, observer_mode: observerMode.value,
    })
    savedArtifact.value = result.artifact
    await recordStep('alternative-reviewed', 'alternative_reviewed')
    const terminal = await api.updateSession(session.value.session_id, {
      action: 'complete', expected_version: session.value.version, idempotency_key: newId(),
      ended_at: utcNow(), duration_ms: Date.now() - startedAt.value,
      perspective_progress: 'reviewed', model_status: modelOutcome.value === 'succeeded' ? 'succeeded' : modelOutcome.value === 'skipped' ? 'skipped' : 'failed',
    })
    session.value = terminal.session
  } catch (caught) { error.value = `${caught.message} Nothing is shown as saved.` }
  finally { busy.value = false }
}

async function deleteArtifact() {
  if (!savedArtifact.value || busy.value) return
  busy.value = true
  try { await api.deleteArtifact(savedArtifact.value.artifact_id); savedArtifact.value = null }
  catch (caught) { error.value = caught.message }
  finally { busy.value = false }
}

function terminalModelStatus() {
  if (modelOutcome.value === 'succeeded') return 'succeeded'
  if (modelOutcome.value === 'skipped') return 'skipped'
  return 'failed'
}

async function terminalize(action, progress) {
  if (!session.value || session.value.status !== 'active') return
  const result = await api.updateSession(session.value.session_id, {
    action,
    expected_version: session.value.version,
    idempotency_key: newId(),
    ended_at: utcNow(),
    duration_ms: action === 'skip' ? 0 : Date.now() - startedAt.value,
    perspective_progress: progress,
    model_status: terminalModelStatus(),
  })
  session.value = result.session
}

async function leaveForSeed() {
  if (busy.value || !selectedAlternative.value.trim()) return
  busy.value = true
  try {
    await terminalize('complete', 'reviewed')
    emit('seed', session.value?.session_id ?? null)
  } catch (caught) { error.value = `${caught.message} The Perspective session was not shown as completed.` }
  finally { busy.value = false }
}

async function leaveForHistory() {
  if (busy.value) return
  busy.value = true
  try {
    await terminalize('stop', selectedAlternative.value.trim() ? 'reviewed' : 'alternative')
    emit('history')
  } catch (caught) { error.value = `${caught.message} The Perspective session was not shown as ended.` }
  finally { busy.value = false }
}
</script>

<template>
  <section
    class="view"
    :data-state="state"
    aria-labelledby="perspective-heading"
  >
    <template v-if="state === 'perspective-entry'">
      <span class="status-pill">Step 1 of 5</span>
      <h1
        id="perspective-heading"
        data-view-heading
        tabindex="-1"
      >
        Perspective Studio
      </h1>
      <p>Review one interpretation without turning uncertainty into a conclusion. This is coursework, not therapy or advice.</p>
      <section class="feature-card">
        <h2>Lowest-effort path</h2>
        <p><strong>“They left because my idea was bad.”</strong></p>
        <p class="caption">
          Fictional Alex scenario · no personal information required.
        </p>
      </section>
      <button
        class="button primary full-width"
        type="button"
        :disabled="busy"
        @click="begin('fictional')"
      >
        Try a fictional example
      </button>
      <details class="custom-entry">
        <summary>Write a fictional example (optional)</summary>
        <label for="custom-interpretation">One short initial interpretation</label>
        <textarea
          id="custom-interpretation"
          v-model="customText"
          maxlength="280"
          rows="3"
          placeholder="A fictional coursework scenario"
        />
        <p class="caption">
          {{ customText.length }}/280 · Do not enter private, medical, identifying, or crisis information.
        </p>
        <button
          class="button secondary"
          type="button"
          :disabled="!customText.trim() || busy"
          @click="begin('custom')"
        >
          Use this fictional text
        </button>
      </details>
      <p>Unsaved text stays in browser memory only and may reset on refresh.</p>
      <p
        v-if="error"
        class="error-text"
        role="alert"
      >
        {{ error }}
      </p>
    </template>

    <template v-else-if="state === 'perspective-evidence'">
      <span class="status-pill">Steps 2–3 of 5</span>
      <h1
        id="perspective-heading"
        data-view-heading
        tabindex="-1"
      >
        Review evidence and uncertainty
      </h1>
      <p class="current-instruction">
        Select what is visible and what the scenario does not establish.
      </p>
      <h2>What appears to support it?</h2>
      <button
        class="option-card selected"
        type="button"
        aria-pressed="true"
        @click="toggleCard(supporting, 'A classmate left soon after Alex spoke.')"
      >
        <strong>A classmate left soon after Alex spoke</strong><small>The timing is visible in the fictional scenario.</small>
      </button>
      <h2>What does not establish it?</h2>
      <button
        class="option-card selected"
        type="button"
        :aria-pressed="uncertainty.includes('The reason for leaving is unknown.')"
        @click="toggleCard(uncertainty, 'The reason for leaving is unknown.')"
      >
        <strong>The reason for leaving is unknown</strong><small>Timing alone does not establish why someone left.</small>
      </button>
      <button
        class="option-card"
        type="button"
        :aria-pressed="uncertainty.includes('Timing alone does not establish cause.')"
        @click="toggleCard(uncertainty, 'Timing alone does not establish cause.')"
      >
        <strong>Timing is not a stated reason</strong><small>Events occurring together do not establish cause.</small>
      </button>
      <details class="request-preview">
        <summary>Review exactly what Gemini would receive</summary>
        <dl class="fact-list compact">
          <div><dt>Interpretation</dt><dd>{{ interpretation }}</dd></div><div><dt>Supporting evidence</dt><dd>{{ supporting.join(' · ') || 'None selected' }}</dd></div><div><dt>Uncertainty</dt><dd>{{ uncertainty.join(' · ') || 'None selected' }}</dd></div>
        </dl>
      </details>
      <button
        class="button primary full-width"
        type="button"
        @click="requestAlternatives"
      >
        Request up to two alternatives
      </button>
      <button
        class="button secondary full-width"
        type="button"
        @click="continueWithoutModel"
      >
        Skip Gemini and continue
      </button>
    </template>

    <template v-else-if="state === 'perspective-alt-loading'">
      <span class="status-pill">Step 4 of 5 · Loading</span>
      <h1
        id="perspective-heading"
        data-view-heading
        tabindex="-1"
      >
        Requesting bounded alternatives
      </h1>
      <p role="status">
        Gemini may return at most two alternatives. Nothing will be saved automatically.
      </p>
      <button
        class="button secondary"
        type="button"
        @click="continueWithoutModel"
      >
        Cancel and continue without Gemini
      </button>
    </template>

    <template v-else-if="state === 'perspective-model-failed'">
      <span class="status-pill">Provider unavailable</span>
      <h1
        id="perspective-heading"
        data-view-heading
        tabindex="-1"
      >
        Your work is still here
      </h1>
      <p
        class="error-text"
        role="alert"
      >
        {{ error }}
      </p>
      <p>The failed request did not save an alternative or control navigation.</p>
      <button
        class="button primary full-width"
        type="button"
        @click="continueWithoutModel"
      >
        Continue without Gemini
      </button>
      <button
        class="button secondary full-width"
        type="button"
        @click="requestAlternatives"
      >
        Retry by explicit choice
      </button>
    </template>

    <template v-else>
      <span class="status-pill">Steps 4–5 of 5</span>
      <h1
        id="perspective-heading"
        data-view-heading
        tabindex="-1"
      >
        Compare alternatives
      </h1>
      <p>At most two bounded alternatives; none is advice, automatically saved, or described as true.</p>
      <button
        v-for="item in alternatives"
        :key="item.alternative"
        class="option-card"
        :class="{ selected: selectedAlternative === item.alternative }"
        type="button"
        :aria-pressed="selectedAlternative === item.alternative"
        @click="selectAlternative(item)"
      >
        <strong>{{ item.alternative }}</strong><small>{{ item.factual_basis }}</small><small>Source: {{ alternativeSource === 'gemini' ? 'Gemini-generated draft' : 'reviewed fictional example' }}</small>
      </button>
      <div class="button-row">
        <button
          class="button secondary"
          type="button"
          @click="editMode = true"
        >
          Edit selected
        </button>
        <button
          class="button secondary"
          type="button"
          @click="createOwn"
        >
          Create my own
        </button>
        <button
          class="button secondary"
          type="button"
          @click="selectedAlternative = ''; editMode = false"
        >
          Reject both
        </button>
      </div>
      <label
        v-if="editMode"
        for="alternative-edit"
      >Alternative text
        <textarea
          id="alternative-edit"
          v-model="selectedAlternative"
          maxlength="240"
          rows="3"
        />
      </label>

      <details class="lens-card">
        <summary>Perspective Lens (optional)</summary>
        <p>Use a fictional observer view. No real name is required and no clinical effect is claimed.</p>
        <label>Fictional label <input
          v-model="observerLabel"
          maxlength="40"
        ></label>
        <p><strong>If {{ observerLabel || 'Alex' }} described this situation, what other possibilities might be missing?</strong></p>
        <button
          class="button secondary"
          type="button"
          @click="useLens"
        >
          Use this observer view
        </button>
        <button
          class="text-button"
          type="button"
          @click="observerMode = 'none'"
        >
          Skip Lens
        </button>
      </details>

      <button
        class="button primary full-width"
        type="button"
        :disabled="!selectedAlternative.trim() || busy || savedArtifact"
        @click="saveArtifact"
      >
        Save reviewed alternative
      </button>
      <p
        v-if="savedArtifact"
        class="success-text"
        role="status"
      >
        Saved as a factual coursework artifact. It can be deleted.
      </p>
      <button
        v-if="savedArtifact"
        class="button secondary"
        type="button"
        :disabled="busy"
        @click="deleteArtifact"
      >
        Delete saved alternative
      </button>
      <button
        class="button secondary full-width"
        type="button"
        :disabled="!selectedAlternative.trim() || busy"
        @click="leaveForSeed"
      >
        Continue to optional Next-Step Seed
      </button>
      <button
        class="text-button"
        type="button"
        @click="leaveForHistory"
      >
        Open History Garden
      </button>
      <p
        v-if="error"
        class="error-text"
        role="alert"
      >
        {{ error }}
      </p>
    </template>
  </section>
</template>
