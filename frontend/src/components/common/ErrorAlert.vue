<template>
  <transition name="slide-down">
    <div v-if="visible" class="error-alert" :class="typeClass">
      <div class="alert-icon">
        <component :is="iconComponent" class="icon" />
      </div>
      <div class="alert-content">
        <p class="alert-title">{{ title }}</p>
        <p v-if="message" class="alert-message">{{ message }}</p>
      </div>
      <button v-if="closable" class="alert-close" @click="handleClose">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-5 h-5">
          <path d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z" />
        </svg>
      </button>
    </div>
  </transition>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const props = defineProps({
  type: {
    type: String,
    default: 'error', // error, warning, success, info
    validator: (value) => ['error', 'warning', 'success', 'info'].includes(value)
  },
  title: {
    type: String,
    required: true
  },
  message: {
    type: String,
    default: ''
  },
  closable: {
    type: Boolean,
    default: true
  },
  duration: {
    type: Number,
    default: 0 // 0 means no auto close
  }
})

const emit = defineEmits(['close'])

const visible = ref(false)

onMounted(() => {
  visible.value = true
  if (props.duration > 0) {
    setTimeout(() => {
      handleClose()
    }, props.duration)
  }
})

const typeClass = computed(() => {
  return `alert-${props.type}`
})

const iconComponent = computed(() => {
  const icons = {
    error: 'ErrorIcon',
    warning: 'WarningIcon',
    success: 'SuccessIcon',
    info: 'InfoIcon'
  }
  return icons[props.type]
})

const handleClose = () => {
  visible.value = false
  setTimeout(() => {
    emit('close')
  }, 300)
}

// Icon components
const ErrorIcon = {
  template: `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-6 h-6">
      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.28 7.22a.75.75 0 00-1.06 1.06L8.94 10l-1.72 1.72a.75.75 0 101.06 1.06L10 11.06l1.72 1.72a.75.75 0 101.06-1.06L11.06 10l1.72-1.72a.75.75 0 00-1.06-1.06L10 8.94 8.28 7.22z" clip-rule="evenodd" />
    </svg>
  `
}

const WarningIcon = {
  template: `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-6 h-6">
      <path fill-rule="evenodd" d="M8.485 2.495c.673-1.167 2.357-1.167 3.03 0l6.28 10.875c.673 1.167-.17 2.625-1.516 2.625H3.72c-1.347 0-2.189-1.458-1.515-2.625L8.485 2.495zM10 5a.75.75 0 01.75.75v3.5a.75.75 0 01-1.5 0v-3.5A.75.75 0 0110 5zm0 9a1 1 0 100-2 1 1 0 000 2z" clip-rule="evenodd" />
    </svg>
  `
}

const SuccessIcon = {
  template: `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-6 h-6">
      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z" clip-rule="evenodd" />
    </svg>
  `
}

const InfoIcon = {
  template: `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-6 h-6">
      <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a.75.75 0 000 1.5h.253a.25.25 0 01.244.304l-.459 2.066A1.75 1.75 0 0010.747 15H11a.75.75 0 000-1.5h-.253a.25.25 0 01-.244-.304l.459-2.066A1.75 1.75 0 009.253 9H9z" clip-rule="evenodd" />
    </svg>
  `
}
</script>

<style scoped>
.error-alert {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1rem 1.25rem;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  margin-bottom: 1rem;
  animation: slideDown 0.3s ease-out;
}

.alert-error {
  background: linear-gradient(135deg, #F5222D 0%, #CF1322 100%);
  color: white;
}

.alert-warning {
  background: linear-gradient(135deg, #FAAD14 0%, #D48806 100%);
  color: white;
}

.alert-success {
  background: linear-gradient(135deg, #52C41A 0%, #389E0D 100%);
  color: white;
}

.alert-info {
  background: var(--gradient-ocean);
  color: white;
}

.alert-icon {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon {
  width: 24px;
  height: 24px;
}

.alert-content {
  flex: 1;
}

.alert-title {
  margin: 0;
  font-weight: 600;
  font-size: 0.9375rem;
  line-height: 1.4;
}

.alert-message {
  margin: 0.25rem 0 0;
  font-size: 0.875rem;
  line-height: 1.5;
  opacity: 0.95;
}

.alert-close {
  flex-shrink: 0;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.25rem;
  color: white;
  opacity: 0.8;
  transition: opacity var(--duration-fast) var(--ease-out);
  border-radius: var(--radius-base);
}

.alert-close:hover {
  opacity: 1;
  background: rgba(255, 255, 255, 0.1);
}

.alert-close svg {
  width: 20px;
  height: 20px;
  display: block;
}

/* Transition */
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease-out;
}

.slide-down-enter-from {
  transform: translateY(-20px);
  opacity: 0;
}

.slide-down-leave-to {
  transform: translateY(-20px);
  opacity: 0;
}

@keyframes slideDown {
  from {
    transform: translateY(-20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}
</style>
