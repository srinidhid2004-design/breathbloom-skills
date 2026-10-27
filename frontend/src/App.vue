<script setup>
import { ref } from 'vue'

const sections = [
  { id: 'practice', label: 'Practice' },
  { id: 'history', label: 'History' },
  { id: 'support', label: 'Support' },
]

const lastVisited = ref('Practice')

function noteVisit(label) {
  lastVisited.value = label
}
</script>

<template>
  <div class="app-shell">
    <header class="site-header">
      <a
        class="brand"
        href="#main-content"
      >
        BreathBloom
      </a>
      <nav aria-label="Foundation areas">
        <a
          v-for="section in sections"
          :key="section.id"
          :href="`#${section.id}`"
          @click="noteVisit(section.label)"
        >
          {{ section.label }}
        </a>
      </nav>
    </header>

    <main id="main-content">
      <p class="eyebrow">
        IST 402 · Assignment 3.2 foundation
      </p>
      <h1>BreathBloom coursework prototype</h1>
      <p class="boundary">
        This fictional local prototype will demonstrate a paced-breathing skill.
        It is not therapy, an emergency service, or a monitored support service.
      </p>
      <p
        class="status"
        aria-live="polite"
      >
        Foundation area: {{ lastVisited }}
      </p>

      <div class="foundation-grid">
        <section
          id="practice"
          aria-labelledby="practice-heading"
        >
          <h2 id="practice-heading">
            Practice
          </h2>
          <p>
            The deterministic 4-second inhale, 6-second exhale flow will be added in a later checkpoint.
          </p>
        </section>

        <section
          id="history"
          aria-labelledby="history-heading"
        >
          <h2 id="history-heading">
            History
          </h2>
          <p>
            Fictional saved-session history will appear here after persistence is implemented.
          </p>
        </section>

        <section
          id="support"
          aria-labelledby="support-heading"
        >
          <h2 id="support-heading">
            Support
          </h2>
          <p>
            The reviewed independent Support information route will be implemented in a later checkpoint.
          </p>
        </section>
      </div>
    </main>
  </div>
</template>
