<script setup>
import { reactive, watch } from 'vue'
import { api, newId } from '../services/api.js'

const props = defineProps({ preferences: { type: Object, required: true } })
const emit = defineEmits(['start-focus', 'perspective', 'history', 'guide', 'preferences'])
const draft = reactive({ ...props.preferences })
let saving = false

watch(() => props.preferences, (value) => Object.assign(draft, value), { deep: true })

async function savePreferences() {
  if (saving) return
  saving = true
  try {
    const result = await api.savePreferences({
      motion_mode: draft.motion_mode,
      guidance_level: draft.guidance_level,
      difficulty: draft.difficulty,
      remember_preferences: draft.remember_preferences,
      expected_version: draft.version,
      idempotency_key: newId(),
    })
    emit('preferences', result.preferences)
  } catch {
    emit('preferences', { ...draft, unsaved: true })
  } finally { saving = false }
}
</script>

<template>
  <section
    class="view entry-view"
    data-state="entry"
    aria-labelledby="entry-heading"
  >
    <h1
      id="entry-heading"
      data-view-heading
      tabindex="-1"
    >
      Choose one small step
    </h1>
    <p class="lead">
      Start with a no-typing Focus Garden, or use the fictional Perspective Studio example.
    </p>

    <section class="feature-card">
      <h2>Focus Garden</h2>
      <div class="focus-tile">
        <span
          class="leaf-mark"
          aria-hidden="true"
        >◒◐</span>
        <span><strong>Match the leaf</strong><small>One visible search task. No typing and no score.</small></span>
      </div>
      <p class="caption">
        Display preferences are optional and stay editable.
      </p>
    </section>

    <button
      class="button primary full-width"
      type="button"
      @click="$emit('start-focus')"
    >
      Start a Focus Garden
    </button>
    <button
      class="button secondary full-width"
      type="button"
      @click="$emit('perspective')"
    >
      Try a fictional example
    </button>
    <button
      class="button secondary full-width"
      type="button"
      @click="$emit('history')"
    >
      Open History Garden
    </button>
    <div class="entry-links">
      <button
        class="text-button"
        type="button"
        @click="$emit('perspective')"
      >
        Perspective Studio
      </button>
      <button
        class="text-button"
        type="button"
        @click="$emit('guide')"
      >
        Garden Guide
      </button>
    </div>
    <p>Setup is skippable. Stop, Back, and Support never carry a penalty.</p>

    <details class="preferences-card">
      <summary>Edit optional display preferences</summary>
      <fieldset>
        <legend>Motion</legend>
        <label><input
          v-model="draft.motion_mode"
          type="radio"
          value="standard"
        > Standard — restrained visual feedback</label>
        <label><input
          v-model="draft.motion_mode"
          type="radio"
          value="no_motion"
        > No motion — no scaling, ripples, fades, or translation</label>
      </fieldset>
      <label>Guidance
        <select v-model="draft.guidance_level"><option value="minimal">Minimal</option><option value="standard">Standard</option><option value="more">More</option></select>
      </label>
      <label>Difficulty
        <select v-model="draft.difficulty"><option value="easy">Easy</option><option value="standard">Standard</option><option value="challenge">Challenge</option></select>
      </label>
      <label><input
        v-model="draft.remember_preferences"
        type="checkbox"
      > Remember these display choices</label>
      <button
        class="button secondary"
        type="button"
        @click="savePreferences"
      >
        Save preferences
      </button>
      <p
        v-if="draft.unsaved"
        class="error-text"
        role="status"
      >
        The local service was unavailable. These choices are active for this screen but were not saved.
      </p>
    </details>
    <p class="boundary-note">
      Preferences are saved only after the interface explains what will be remembered.
    </p>
  </section>
</template>
