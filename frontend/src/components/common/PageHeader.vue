<template>
  <div class="page-header bg-gradient-ocean py-12 mb-8">
    <div class="container-custom">
      <div class="flex items-start justify-between">
        <div class="flex-1">
          <h1 class="text-3xl md:text-4xl font-bold text-white mb-2">
            {{ title }}
          </h1>
          <p v-if="subtitle" class="text-white/80 text-base md:text-lg">
            {{ subtitle }}
          </p>
        </div>
        <div v-if="$slots.actions" class="flex-shrink-0 ml-6">
          <slot name="actions"></slot>
        </div>
      </div>
      <div v-if="$slots.tabs" class="mt-6">
        <slot name="tabs"></slot>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true
  },
  subtitle: {
    type: String,
    default: ''
  }
})
</script>

<style scoped>
.page-header {
  position: relative;
  overflow: hidden;
}

.page-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background:
    radial-gradient(circle at 20% 50%, rgba(0, 191, 255, 0.2) 0%, transparent 50%),
    radial-gradient(circle at 80% 80%, rgba(255, 127, 80, 0.15) 0%, transparent 50%);
  pointer-events: none;
}

.container-custom {
  position: relative;
  z-index: 1;
}
</style>
