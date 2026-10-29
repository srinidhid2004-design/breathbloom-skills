<script setup>
import { ref } from 'vue'
import { api, newId } from '../services/api.js'
import { useLatestRequest } from '../composables/useLatestRequest.js'

const emit = defineEmits(['state', 'history'])
const guard = useLatestRequest()
const state = ref('history')
const suggestions = ['Which activity did I complete most often?', 'Show my saved Next-Step Seeds.', 'Which sessions were stopped or interrupted?']
const question = ref('')
const answer = ref(null)
const error = ref('')
const busy = ref(false)

function setState(next) { state.value = next; emit('state', next) }
async function ask() {
  if (busy.value || !question.value.trim()) return
  const current = guard.begin()
  busy.value = true; error.value = ''; answer.value = null; setState('history-question-loading')
  try {
    const conversationResult = await api.createConversation({ client_conversation_id: newId(), purpose: 'history_guide' }, current.signal)
    if (!guard.isCurrent(current.id)) return
    const messageResult = await api.createHistoryMessage(conversationResult.conversation.conversation_id, { idempotency_key: newId(), question: question.value.trim() }, current.signal)
    if (!guard.isCurrent(current.id)) return
    const result = await api.runHistoryQuestion({ request_id: messageResult.request.request_id }, current.signal)
    if (!guard.isCurrent(current.id)) return
    if (result.outcome === 'history_no_match') { setState('history-no-match'); return }
    if (result.outcome === 'duplicate_request' && !result.answer) {
      error.value = 'This request was already handled. No duplicate provider request was made.'; setState('history-query-rejected'); return
    }
    answer.value = result; setState('history-answer-ready')
  } catch (caught) {
    if (caught.name === 'AbortError' || !guard.isCurrent(current.id)) return
    if (caught.outcome === 'history_query_rejected') error.value = 'Rejected before execution. The proposed query was never executed and no database change occurred.'
    else if (caught.outcome === 'missing_configuration') error.value = 'Gemini is not configured. The factual history remains available without Garden Guide.'
    else error.value = caught.message || 'Garden Guide could not complete the request. No answer was invented.'
    setState('history-query-rejected')
  } finally { if (guard.isCurrent(current.id)) busy.value = false }
}
function resetQuestion() { guard.cancel(); busy.value = false; answer.value = null; error.value = ''; question.value = ''; setState('history') }
</script>

<template>
  <section
    class="view guide-view"
    :data-state="state"
    aria-labelledby="guide-heading"
  >
    <template v-if="state === 'history'">
      <h1
        id="guide-heading"
        data-view-heading
        tabindex="-1"
      >
        Garden Guide
      </h1>
      <p>Ask only factual questions about saved fictional FocusBloom history. Suggested questions come before optional text entry.</p>
      <div
        class="question-chips"
        aria-label="Suggested factual questions"
      >
        <button
          v-for="item in suggestions"
          :key="item"
          class="question-chip"
          type="button"
          @click="question = item"
        >
          <span aria-hidden="true">●</span>{{ item }}
        </button>
      </div>
      <label for="history-question">Optional factual-history question</label>
      <textarea
        id="history-question"
        v-model="question"
        maxlength="300"
        rows="3"
        placeholder="Ask about saved activity facts"
      />
      <p class="warning-note">
        Do not enter private, identifying, medical, or crisis information.
      </p>
      <button
        class="button primary full-width"
        type="button"
        :disabled="!question.trim() || busy"
        @click="ask"
      >
        Ask Garden Guide
      </button>
      <button
        class="button secondary full-width"
        type="button"
        @click="$emit('history')"
      >
        Return to History Garden
      </button>
    </template>

    <template v-else-if="state === 'history-question-loading'">
      <span class="status-pill">Loading</span><h1
        id="guide-heading"
        data-view-heading
        tabindex="-1"
      >
        Checking bounded fictional history
      </h1>
      <p role="status">
        The backend controls the model, prompt, read-only query validation, profile scope, and database path.
      </p>
      <button
        class="button secondary"
        type="button"
        @click="resetQuestion"
      >
        Cancel this screen request
      </button>
    </template>

    <template v-else-if="state === 'history-answer-ready'">
      <span class="status-pill">Grounded</span><h1
        id="guide-heading"
        data-view-heading
        tabindex="-1"
      >
        Garden Guide answer
      </h1>
      <section class="question-card">
        <h2>{{ question }}</h2><p>Only saved fictional FocusBloom history is in scope.</p>
      </section>
      <section class="answer-card">
        <p>{{ answer.answer.content }}</p><p><strong>Row references:</strong> {{ answer.row_references.join(' · ') }}</p><p class="limitation">
          Coursework prototype; factual saved records only. No diagnosis, reason, improvement, or effectiveness claim is inferred.
        </p>
      </section>
      <p class="boundary-note">
        <strong>Model:</strong> gemini-3.5-flash-lite · <strong>Provider attempts recorded:</strong> {{ answer.request.attempt_count }}. The approved workflow permits at most two provider requests.
      </p>
      <details class="trace-card">
        <summary>How this answer was grounded</summary><dl class="fact-list compact">
          <div><dt>Proposed read-only SQL</dt><dd>Validated and executed only by the backend; intentionally not returned to the browser.</dd></div>
          <div><dt>Safe bound parameters</dt><dd>Backend-owned and intentionally not returned to the browser.</dd></div>
          <div><dt>Retrieved bounded records</dt><dd>Kept within backend model context; not copied into the UI.</dd></div>
          <div><dt>Referenced rows</dt><dd>{{ answer.row_references.join(', ') }}</dd></div>
          <div><dt>Explanation</dt><dd>The answer was saved only after read-only validation, bounded retrieval, output validation, and reference checks.</dd></div>
          <div><dt>Limitation</dt><dd>No clinical or effectiveness claim is inferred.</dd></div>
        </dl>
      </details>
      <button
        class="button primary full-width"
        type="button"
        @click="resetQuestion"
      >
        Ask another question
      </button><button
        class="button secondary full-width"
        type="button"
        @click="$emit('history')"
      >
        Return to History Garden
      </button>
    </template>

    <template v-else-if="state === 'history-no-match'">
      <span class="status-pill">No match</span><h1
        id="guide-heading"
        data-view-heading
        tabindex="-1"
      >
        No matching saved records
      </h1><p>No grounded answer was created because the bounded query returned no records.</p><button
        class="button primary"
        type="button"
        @click="resetQuestion"
      >
        Ask another question
      </button>
    </template>

    <template v-else>
      <span class="status-pill">Request not completed</span><h1
        id="guide-heading"
        data-view-heading
        tabindex="-1"
      >
        Garden Guide did not create an answer
      </h1><p
        class="error-text"
        role="alert"
      >
        {{ error }}
      </p><p>No invented answer is shown. Saved history can still be browsed directly.</p>
      <button
        class="button primary"
        type="button"
        @click="ask"
      >
        Retry by explicit choice
      </button><button
        class="button secondary"
        type="button"
        @click="resetQuestion"
      >
        Change question
      </button><button
        class="button secondary"
        type="button"
        @click="$emit('history')"
      >
        Return to History Garden
      </button>
    </template>
  </section>
</template>
