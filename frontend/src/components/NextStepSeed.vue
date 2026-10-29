<script setup>
import { computed, ref } from 'vue'
import { api, newId } from '../services/api.js'

const props = defineProps({ sessionId: { type: String, default: null } })
defineEmits(['history', 'entry'])
const situation = ref('I notice I am assuming one explanation')
const action = ref('check what facts I actually have')
const previewed = ref(false)
const saved = ref(null)
const error = ref('')
const busy = ref(false)
const plan = computed(() => `If ${situation.value.trim()}, then I will ${action.value.trim()}.`)

async function save() {
  if (!previewed.value || busy.value || !situation.value.trim() || !action.value.trim()) return
  busy.value = true; error.value = ''
  try {
    const result = await api.createSeed({
      client_seed_id: newId(), session_id: props.sessionId, situation_text: situation.value.trim(),
      action_text: action.value.trim(), formatted_plan: plan.value, source: 'template',
    })
    saved.value = result.seed
  } catch (caught) { error.value = caught.message }
  finally { busy.value = false }
}
async function remove() {
  if (!saved.value || busy.value) return
  busy.value = true
  try { await api.deleteSeed(saved.value.seed_id); saved.value = null; previewed.value = false }
  catch (caught) { error.value = caught.message }
  finally { busy.value = false }
}
</script>

<template>
  <section
    class="view"
    data-state="next-step-seed"
    aria-labelledby="seed-heading"
  >
    <span class="status-pill">Optional</span>
    <h1
      id="seed-heading"
      data-view-heading
      tabindex="-1"
    >
      Next-Step Seed
    </h1>
    <p>Create a user-authored if–then plan, or skip. Gemini never chooses the action and no reminder is scheduled.</p>
    <section class="seed-builder">
      <label>If <input
        v-model="situation"
        maxlength="180"
      ></label>
      <label>then I will <input
        v-model="action"
        maxlength="180"
      ></label>
    </section>
    <button
      class="button secondary full-width"
      type="button"
      @click="previewed = true"
    >
      Preview this plan
    </button>
    <section
      v-if="previewed"
      class="preview-card"
      aria-labelledby="preview-heading"
    >
      <h2 id="preview-heading">
        Save preview
      </h2><p>{{ plan }}</p>
    </section>
    <button
      class="button primary full-width"
      type="button"
      :disabled="!previewed || busy || saved"
      @click="save"
    >
      Save this seed
    </button>
    <p
      v-if="saved"
      class="success-text"
      role="status"
    >
      Saved. This is a user-authored plan, not a reminder or effectiveness claim.
    </p>
    <div class="button-row">
      <button
        v-if="saved"
        class="button secondary"
        type="button"
        @click="remove"
      >
        Delete seed
      </button>
      <button
        class="button secondary"
        type="button"
        @click="previewed = false"
      >
        Edit
      </button>
      <button
        class="button secondary"
        type="button"
        @click="$emit('history')"
      >
        Skip to History
      </button>
    </div>
    <p
      v-if="error"
      class="error-text"
      role="alert"
    >
      {{ error }}
    </p>
  </section>
</template>
