<script setup>
defineEmits(['support'])
</script>

<template>
  <header class="site-header">
    <button
      class="brand-link"
      type="button"
      @click="$emit('support', 'home')"
    >
      FocusBloom
    </button>
    <p class="header-boundary">
      Fictional coursework prototype · bounded factual history assistant.
    </p>
    <button
      class="button support-button"
      type="button"
      @click="$emit('support')"
    >
      Support
    </button>
  </header>
</template>
