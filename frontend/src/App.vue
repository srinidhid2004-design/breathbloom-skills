<script setup>
import { ref } from 'vue'

const sections = [
  { id: 'focus-garden', label: 'Focus Garden' },
  { id: 'perspective-studio', label: 'Perspective Studio' },
  { id: 'history-garden', label: 'History Garden' },
  { id: 'support', label: 'Support' },
]

const lastVisited = ref('Focus Garden')

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
        FocusBloom
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
      <h1>FocusBloom coursework prototype</h1>
      <p class="boundary">
        This fictional local prototype will explore brief visual-attention activities and a
        structured perspective exercise. It is not therapy, an emergency service, or a monitored
        support service.
      </p>
      <p
        class="status"
        aria-live="polite"
      >
        Foundation area: {{ lastVisited }}
      </p>

      <div class="foundation-grid">
        <section
          id="focus-garden"
          aria-labelledby="focus-garden-heading"
        >
          <h2 id="focus-garden-heading">
            Focus Garden
          </h2>
          <p>
            Short no-typing visual-attention activities will be implemented in a later checkpoint.
          </p>
        </section>

        <section
          id="perspective-studio"
          aria-labelledby="perspective-studio-heading"
        >
          <h2 id="perspective-studio-heading">
            Perspective Studio
          </h2>
          <p>
            A one-minute cognitive-reframe flow with a fictional-example path is planned here.
          </p>
        </section>

        <section
          id="history-garden"
          aria-labelledby="history-garden-heading"
        >
          <h2 id="history-garden-heading">
            History Garden
          </h2>
          <p>
            Factual fictional-demo activity history will appear after the revised data model is implemented.
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
