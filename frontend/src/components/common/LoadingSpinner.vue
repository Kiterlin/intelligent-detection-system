<template>
  <div class="loading-spinner-wrapper" :class="wrapperClass">
    <div class="loading-spinner" :class="sizeClass">
      <svg class="spinner" viewBox="0 0 50 50">
        <circle
          class="path"
          cx="25"
          cy="25"
          r="20"
          fill="none"
          :stroke="color"
          stroke-width="4"
        />
      </svg>
    </div>
    <p v-if="text" class="loading-text" :class="textSizeClass">{{ text }}</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  size: {
    type: String,
    default: 'medium', // small, medium, large
    validator: (value) => ['small', 'medium', 'large'].includes(value)
  },
  color: {
    type: String,
    default: '#00BFFF'
  },
  text: {
    type: String,
    default: ''
  },
  fullscreen: {
    type: Boolean,
    default: false
  }
})

const sizeClass = computed(() => {
  return {
    'size-small': props.size === 'small',
    'size-medium': props.size === 'medium',
    'size-large': props.size === 'large'
  }
})

const textSizeClass = computed(() => {
  return {
    'text-sm': props.size === 'small',
    'text-base': props.size === 'medium',
    'text-lg': props.size === 'large'
  }
})

const wrapperClass = computed(() => {
  return {
    'fullscreen': props.fullscreen
  }
})
</script>

<style scoped>
.loading-spinner-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
}

.loading-spinner-wrapper.fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(10, 46, 91, 0.05);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  z-index: 9999;
}

.loading-spinner {
  display: inline-block;
}

.loading-spinner.size-small {
  width: 30px;
  height: 30px;
}

.loading-spinner.size-medium {
  width: 50px;
  height: 50px;
}

.loading-spinner.size-large {
  width: 70px;
  height: 70px;
}

.spinner {
  animation: rotate 2s linear infinite;
  width: 100%;
  height: 100%;
}

.path {
  stroke-linecap: round;
  animation: dash 1.5s ease-in-out infinite;
}

@keyframes rotate {
  100% {
    transform: rotate(360deg);
  }
}

@keyframes dash {
  0% {
    stroke-dasharray: 1, 150;
    stroke-dashoffset: 0;
  }
  50% {
    stroke-dasharray: 90, 150;
    stroke-dashoffset: -35;
  }
  100% {
    stroke-dasharray: 90, 150;
    stroke-dashoffset: -124;
  }
}

.loading-text {
  margin: 0;
  font-weight: 500;
  color: var(--color-primary);
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}
</style>
