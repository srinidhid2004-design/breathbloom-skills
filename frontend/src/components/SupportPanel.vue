<script setup>
import { nextTick, onMounted, onBeforeUnmount, ref } from 'vue'

const emit = defineEmits(['close'])
const panel = ref(null)

function onKeydown(event) {
  if (event.key === 'Escape') emit('close')
  if (event.key !== 'Tab' || !panel.value) return
  const controls = [...panel.value.querySelectorAll('a[href], button:not([disabled])')]
  if (!controls.length) return
  const first = controls[0]
  const last = controls[controls.length - 1]
  if (event.shiftKey && document.activeElement === first) {
    event.preventDefault(); last.focus()
  } else if (!event.shiftKey && document.activeElement === last) {
    event.preventDefault(); first.focus()
  }
}

onMounted(async () => {
  document.addEventListener('keydown', onKeydown)
  await nextTick()
  panel.value?.querySelector('h1')?.focus()
})
onBeforeUnmount(() => document.removeEventListener('keydown', onKeydown))
</script>

<template>
  <div class="support-backdrop">
    <section
      ref="panel"
      class="support-panel"
      role="dialog"
      aria-modal="true"
      aria-labelledby="support-heading"
      data-state="support-open"
    >
      <h1
        id="support-heading"
        tabindex="-1"
      >
        Support information — United States demo
      </h1>
      <p>FocusBloom is a coursework prototype for fictional scenarios. It is not an emergency service, is not monitored, and cannot contact help for you. This page does not use your location or activity to choose resources.</p>

      <section
        class="support-resource"
        aria-labelledby="emergency-heading"
      >
        <h2 id="emergency-heading">
          Emergency assistance
        </h2>
        <p>If there is immediate danger or a medical emergency, call 911 now or go to the nearest emergency room.</p>
        <a
          class="button secondary"
          href="tel:911"
        >Call 911</a>
      </section>

      <section
        class="support-resource"
        aria-labelledby="crisis-heading"
      >
        <h2 id="crisis-heading">
          Crisis support
        </h2>
        <p>In the United States, call or text 988, or use the 988 Lifeline chat, for crisis support.</p>
        <div class="button-row">
          <a
            class="button secondary"
            href="tel:988"
          >Call 988</a>
          <a
            class="button secondary"
            href="sms:988"
          >Text 988</a>
          <a
            class="button secondary"
            href="https://chat.988lifeline.org/"
            target="_blank"
            rel="noreferrer"
          >988 Lifeline chat</a>
        </div>
      </section>

      <section
        class="support-resource"
        aria-labelledby="treatment-heading"
      >
        <h2 id="treatment-heading">
          Non-emergency treatment information
        </h2>
        <p>FindTreatment.gov lists mental-health and substance-use treatment facilities in the United States and its territories. It is not an emergency service.</p>
        <a
          class="button secondary"
          href="https://findtreatment.gov/"
          target="_blank"
          rel="noreferrer"
        >FindTreatment.gov</a>
      </section>

      <section aria-labelledby="about-support-heading">
        <h2 id="about-support-heading">
          About FocusBloom
        </h2>
        <p>FocusBloom does not diagnose, provide therapy or medical advice, detect distress, or notify another person.</p>
      </section>
      <button
        class="button primary full-width"
        type="button"
        @click="$emit('close')"
      >
        Return
      </button>
    </section>
  </div>
</template>
