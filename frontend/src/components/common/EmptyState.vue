<template>
  <div class="empty-state text-center py-20">
    <div class="empty-icon mb-4">
      <el-icon :size="iconSize" :class="iconClass">
        <component :is="icon" />
      </el-icon>
    </div>
    <p class="empty-title text-lg font-medium mb-2" :class="titleClass">
      {{ title }}
    </p>
    <p v-if="description" class="empty-description text-sm mb-6" :class="descriptionClass">
      {{ description }}
    </p>
    <div v-if="$slots.actions" class="empty-actions">
      <slot name="actions"></slot>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import {
  Document,
  Folder,
  Files,
  DataLine,
  Search,
  Warning,
  InfoFilled
} from '@element-plus/icons-vue'

const props = defineProps({
  icon: {
    type: [String, Object],
    default: 'Document'
  },
  iconSize: {
    type: Number,
    default: 64
  },
  title: {
    type: String,
    default: '暂无数据'
  },
  description: {
    type: String,
    default: ''
  },
  type: {
    type: String,
    default: 'default', // default, info, warning
    validator: (value) => ['default', 'info', 'warning'].includes(value)
  }
})

const iconClass = computed(() => {
  const classes = {
    default: 'text-gray-300',
    info: 'text-blue-300',
    warning: 'text-orange-300'
  }
  return classes[props.type] || classes.default
})

const titleClass = computed(() => {
  const classes = {
    default: 'text-gray-500',
    info: 'text-blue-500',
    warning: 'text-orange-500'
  }
  return classes[props.type] || classes.default
})

const descriptionClass = computed(() => {
  const classes = {
    default: 'text-gray-400',
    info: 'text-blue-400',
    warning: 'text-orange-400'
  }
  return classes[props.type] || classes.default
})
</script>

<style scoped>
.empty-state {
  animation: fadeIn 0.3s ease-in-out;
}

.empty-icon {
  display: inline-block;
  animation: float 3s ease-in-out infinite;
}

.empty-title {
  font-weight: 500;
}

.empty-description {
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
  line-height: 1.6;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}
</style>
