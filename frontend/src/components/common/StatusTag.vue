<template>
  <el-tag
    :type="tagType"
    :effect="effect"
    :size="size"
    class="status-tag"
  >
    <el-icon v-if="showIcon" class="mr-1">
      <component :is="iconComponent" />
    </el-icon>
    <span>{{ text }}</span>
  </el-tag>
</template>

<script setup>
import { computed } from 'vue'
import {
  Clock,
  Loading,
  CircleCheck,
  CircleClose,
  Finished,
  Close,
  QuestionFilled,
  Cpu,
  DocumentCopy
} from '@element-plus/icons-vue'

const props = defineProps({
  status: {
    type: String,
    required: true
  },
  statusMap: {
    type: Object,
    default: () => ({})
  },
  showIcon: {
    type: Boolean,
    default: true
  },
  size: {
    type: String,
    default: 'default' // large / default /small
  },
  effect: {
    type: String,
    default: 'light' // dark / light / plain
  }
})

// 默认状态映射
const defaultStatusMap = {
  pending: { text: '待处理', type: 'info', icon: 'Clock' },
  in_progress: { text: '进行中', type: 'warning', icon: 'Loading' },
  processing: { text: '处理中', type: 'warning', icon: 'Loading' },
  preparing: { text: '准备中', type: 'warning', icon: 'Loading' },
  training: { text: '训练中', type: 'warning', icon: 'Cpu' },
  generating: { text: '生成中', type: 'warning', icon: 'Loading' },
  completed: { text: '已完成', type: 'success', icon: 'CircleCheck' },
  failed: { text: '失败', type: 'danger', icon: 'CircleClose' },
  cancelled: { text: '已取消', type: 'info', icon: 'Close' },
  archived: { text: '已归档', type: 'info', icon: 'Finished' }
}

// 合并自定义状态映射
const statusConfig = computed(() => {
  const merged = { ...defaultStatusMap, ...props.statusMap }
  return merged[props.status] || {
    text: props.status,
    type: 'info',
    icon: 'QuestionFilled'
  }
})

const text = computed(() => statusConfig.value.text)
const tagType = computed(() => statusConfig.value.type)

const iconComponent = computed(() => {
  const iconName = statusConfig.value.icon
  const icons = {
    Clock,
    Loading,
    CircleCheck,
    CircleClose,
    Finished,
    Close,
    QuestionFilled,
    Cpu,
    DocumentCopy
  }
  return icons[iconName] || QuestionFilled
})
</script>

<style scoped>
.status-tag {
  display: inline-flex;
  align-items: center;
  font-weight: 500;
}

.status-tag :deep(.el-icon) {
  margin-right: 4px;
}
</style>
