<script setup>
import { nextTick, onMounted, ref } from 'vue'
import AppHeader from './components/AppHeader.vue'
import EntryView from './components/EntryView.vue'
import FocusGarden from './components/FocusGarden.vue'
import GardenGuide from './components/GardenGuide.vue'
import HistoryGarden from './components/HistoryGarden.vue'
import NextStepSeed from './components/NextStepSeed.vue'
import PerspectiveStudio from './components/PerspectiveStudio.vue'
import SupportPanel from './components/SupportPanel.vue'
import { api, newId, utcNow } from './services/api.js'

const view = ref('entry')
const supportOpen = ref(false)
const supportOpener = ref(null)
const focusGarden = ref(null)
const focusActivity = ref('different_leaf')
const seedSessionId = ref(null)
const shellNotice = ref('')
const preferences = ref({ motion_mode: 'standard', guidance_level: 'standard', difficulty: 'standard', remember_preferences: false, version: 1 })
const focusStates = new Set(['focus-ready', 'focus-active', 'focus-stopped', 'focus-completed'])
const perspectiveStates = new Set(['perspective-entry', 'perspective-evidence', 'perspective-alt-loading', 'perspective-alt-ready', 'perspective-model-failed'])
const guideStates = new Set(['history-question-loading', 'history-answer-ready', 'history-no-match', 'history-query-rejected', 'guide-entry'])

async function navigate(next) {
  view.value = next
  await nextTick()
  document.querySelector('[data-view-heading]')?.focus()
}

function startFocus(activityType = 'different_leaf') {
  focusActivity.value = activityType
  navigate('focus-ready')
}

async function openSupport() {
  supportOpener.value = document.activeElement
  if (view.value === 'focus-active') {
    await focusGarden.value?.interruptForSupport()
    view.value = 'focus-stopped'
  }
  supportOpen.value = true
}

async function closeSupport() {
  supportOpen.value = false
  await nextTick()
  supportOpener.value?.focus?.()
}

async function reconcileInterruptedSession() {
  const raw = sessionStorage.getItem('focusbloom_active_session')
  if (!raw) return
  sessionStorage.removeItem('focusbloom_active_session')
  try {
    const stale = JSON.parse(raw)
    await api.updateSession(stale.id, {
      action: 'interrupt', expected_version: stale.version, idempotency_key: newId(), ended_at: utcNow(),
      duration_ms: Math.max(0, Date.now() - stale.startedAt), perspective_progress: 'none', model_status: 'skipped',
    })
    shellNotice.value = 'A previously active Focus Garden was recorded as interrupted after refresh. It was not resumed or completed.'
  } catch {
    shellNotice.value = 'A previous Focus Garden may have been interrupted. FocusBloom could not confirm that record; it was not shown as completed.'
  }
}

onMounted(async () => {
  await reconcileInterruptedSession()
  try { preferences.value = (await api.preferences()).preferences }
  catch { shellNotice.value ||= 'The local service is unavailable. Static Support still works; actions are not assumed saved.' }
})
</script>

<template>
  <div class="app-shell">
    <a
      class="skip-link"
      href="#main-content"
    >Skip to main content</a>
    <AppHeader @support="openSupport" />
    <p class="prototype-notice">
      Fictional coursework prototype · not therapy, diagnosis, or monitoring.
    </p>
    <p
      v-if="shellNotice"
      class="shell-notice"
      role="status"
    >
      {{ shellNotice }}
    </p>
    <main id="main-content">
      <EntryView
        v-if="view === 'entry'"
        :preferences="preferences"
        @start-focus="startFocus"
        @perspective="navigate('perspective-entry')"
        @history="navigate('history')"
        @guide="navigate('guide-entry')"
        @preferences="preferences = $event"
      />
      <FocusGarden
        v-else-if="focusStates.has(view)"
        ref="focusGarden"
        :preferences="preferences"
        :activity-type="focusActivity"
        @state="view = $event"
        @perspective="navigate('perspective-entry')"
        @history="navigate('history')"
        @entry="navigate('entry')"
      />
      <PerspectiveStudio
        v-else-if="perspectiveStates.has(view)"
        :preferences="preferences"
        @state="view = $event"
        @seed="seedSessionId = $event; navigate('next-step-seed')"
        @history="navigate('history')"
        @entry="navigate('entry')"
      />
      <NextStepSeed
        v-else-if="view === 'next-step-seed'"
        :session-id="seedSessionId"
        @history="navigate('history')"
        @entry="navigate('entry')"
      />
      <HistoryGarden
        v-else-if="view === 'history'"
        @guide="navigate('guide-entry')"
        @entry="navigate('entry')"
      />
      <GardenGuide
        v-else-if="guideStates.has(view)"
        @state="view = $event"
        @history="navigate('history')"
      />
    </main>
    <SupportPanel
      v-if="supportOpen"
      @close="closeSupport"
    />
  </div>
</template>
