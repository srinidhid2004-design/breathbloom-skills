<script setup>
import { computed, onMounted, ref } from 'vue'
import { activityLabels } from '../data/activities.js'
import { api } from '../services/api.js'
import { useLatestRequest } from '../composables/useLatestRequest.js'

defineEmits(['guide', 'entry'])
const guard = useLatestRequest()
const sessions = ref([])
const artifacts = ref([])
const seeds = ref([])
const filter = ref('all')
const loading = ref(true)
const error = ref('')
const confirmAction = ref('')
const notice = ref('')
const visibleSessions = computed(() => filter.value === 'all' ? sessions.value : sessions.value.filter((item) => item.status === filter.value))
const artifactSessionIds = computed(() => new Set(artifacts.value.map((item) => item.session_id).filter(Boolean)))
const seedSessionIds = computed(() => new Set(seeds.value.map((item) => item.session_id).filter(Boolean)))

function formatDate(value) { return new Intl.DateTimeFormat(undefined, { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(value)) }
function formatDuration(ms) { return `${Math.round((ms || 0) / 1000)} seconds` }

async function load() {
  const request = guard.begin()
  loading.value = true; error.value = ''
  try {
    const [sessionResult, artifactResult, seedResult] = await Promise.all([
      api.sessions({}, request.signal), api.artifacts(request.signal), api.seeds(request.signal),
    ])
    if (!guard.isCurrent(request.id)) return
    sessions.value = sessionResult.sessions
    artifacts.value = artifactResult.artifacts
    seeds.value = seedResult.seeds
  } catch (caught) {
    if (caught.name !== 'AbortError' && guard.isCurrent(request.id)) error.value = caught.message
  } finally { if (guard.isCurrent(request.id)) loading.value = false }
}

async function deleteArtifact(id) {
  try { await api.deleteArtifact(id); await load(); notice.value = 'The selected saved Perspective text was deleted.' }
  catch (caught) { error.value = caught.message }
}
async function deleteSeed(id) {
  try { await api.deleteSeed(id); await load(); notice.value = 'The selected Next-Step Seed was deleted.' }
  catch (caught) { error.value = caught.message }
}
async function deleteSavedText() {
  try { await api.deleteSavedText(); confirmAction.value = ''; await load(); notice.value = 'Saved Perspective and seed text was deleted. Session facts remain.' }
  catch (caught) { error.value = caught.message }
}
async function resetDemo() {
  try { await api.resetDemo(0); confirmAction.value = ''; await load(); notice.value = 'The fictional demo records were reset.' }
  catch (caught) { error.value = caught.message }
}
onMounted(load)
</script>

<template>
  <section
    class="view history-view"
    data-state="history"
    aria-labelledby="history-heading"
  >
    <h1
      id="history-heading"
      data-view-heading
      tabindex="-1"
    >
      History Garden
    </h1>
    <p>Factual fictional records only. No scores, ranks, treatment claims, or missed-day warnings.</p>
    <div
      class="filter-row"
      aria-label="Filter sessions"
    >
      <button
        v-for="choice in ['all', 'completed', 'stopped', 'skipped', 'interrupted']"
        :key="choice"
        class="button secondary"
        :aria-pressed="filter === choice"
        type="button"
        @click="filter = choice"
      >
        {{ choice }}
      </button>
    </div>
    <p
      v-if="loading"
      role="status"
    >
      Loading factual history…
    </p>
    <div
      v-else-if="error"
      class="error-card"
      role="alert"
    >
      <p>{{ error }}</p><button
        class="button secondary"
        type="button"
        @click="load"
      >
        Retry loading history
      </button>
    </div>
    <section
      v-else-if="!visibleSessions.length"
      class="empty-card"
    >
      <h2>No matching saved sessions</h2><p>Start a fictional Focus Garden or Perspective Studio session to create a factual record.</p>
    </section>
    <div
      v-else
      class="history-list"
    >
      <article
        v-for="item in visibleSessions"
        :key="item.session_id"
        class="history-card"
      >
        <span class="status-pill">{{ item.status }}</span>
        <h2>{{ activityLabels[item.activity_type] ?? 'Perspective Studio' }}</h2>
        <p>{{ formatDate(item.started_at) }} · {{ formatDuration(item.duration_ms) }}</p>
        <p class="caption">
          Difficulty: {{ item.difficulty }} · Motion: {{ item.motion_mode }} · Guidance: {{ item.guidance_level }}
        </p>
        <p class="caption">
          Perspective saved: {{ artifactSessionIds.has(item.session_id) ? 'yes' : 'no' }} · Next-Step Seed: {{ seedSessionIds.has(item.session_id) ? 'yes' : 'no' }} · Model: {{ item.model_status }}
        </p>
      </article>
    </div>

    <section
      v-if="artifacts.length || seeds.length"
      class="saved-text-section"
    >
      <h2>Saved user-authored text</h2>
      <article
        v-for="item in artifacts"
        :key="item.artifact_id"
        class="saved-text-card"
      >
        <p><strong>Perspective alternative:</strong> {{ item.alternative_text }}</p>
        <button
          class="button secondary"
          type="button"
          @click="deleteArtifact(item.artifact_id)"
        >
          Delete this alternative
        </button>
      </article>
      <article
        v-for="item in seeds"
        :key="item.seed_id"
        class="saved-text-card"
      >
        <p><strong>Next-Step Seed:</strong> {{ item.formatted_plan }}</p>
        <button
          class="button secondary"
          type="button"
          @click="deleteSeed(item.seed_id)"
        >
          Delete this seed
        </button>
      </article>
    </section>
    <p
      v-if="notice"
      class="success-text"
      role="status"
    >
      {{ notice }}
    </p>
    <button
      class="button primary full-width"
      type="button"
      @click="$emit('guide')"
    >
      Ask Garden Guide
    </button>
    <div class="button-row">
      <button
        class="button secondary"
        type="button"
        @click="confirmAction = 'text'"
      >
        Delete saved text
      </button>
      <button
        class="button secondary"
        type="button"
        @click="confirmAction = 'reset'"
      >
        Reset demo
      </button>
      <button
        class="button secondary"
        type="button"
        @click="$emit('entry')"
      >
        Return to entry
      </button>
    </div>
    <section
      v-if="confirmAction"
      class="confirm-card"
      role="alertdialog"
      aria-modal="true"
      aria-labelledby="confirm-heading"
    >
      <h2 id="confirm-heading">
        Confirm {{ confirmAction === 'reset' ? 'complete fictional reset' : 'saved-text deletion' }}
      </h2>
      <p>{{ confirmAction === 'reset' ? 'This removes fictional sessions, artifacts, seeds, and messages.' : 'This removes Perspective and seed text while retaining session facts.' }}</p>
      <div class="button-row">
        <button
          class="button stop"
          type="button"
          @click="confirmAction === 'reset' ? resetDemo() : deleteSavedText()"
        >
          Confirm
        </button><button
          class="button secondary"
          type="button"
          @click="confirmAction = ''"
        >
          Cancel
        </button>
      </div>
    </section>
  </section>
</template>
