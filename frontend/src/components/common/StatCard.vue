<template>
  <div class="stat-card" :class="cardClass">
    <div class="stat-icon" :style="iconStyle">
      <el-icon :size="iconSize">
        <component :is="icon" />
      </el-icon>
    </div>
    <div class="stat-content">
      <div class="stat-label">{{ label }}</div>
      <div class="stat-value">
        <span class="value-number">{{ formattedValue }}</span>
        <span v-if="unit" class="value-unit">{{ unit }}</span>
      </div>
      <div v-if="trend !== null" class="stat-trend" :class="trendClass">
        <el-icon :size="14">
          <component :is="trendIcon" />
        </el-icon>
        <span>{{ Math.abs(trend) }}%</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import {
  ArrowUp,
  ArrowDown,
  Minus
} from '@element-plus/icons-vue'

const props = defineProps({
  label: {
    type: String,
    required: true
  },
  value: {
    type: [Number, String],
    required: true
  },
  unit: {
    type: String,
    default: ''
  },
  icon: {
    type: Object,
    required: true
  },
  iconSize: {
    type: Number,
    default: 24
  },
  color: {
    type: String,
    default: '#409EFF' // 默认蓝色
  },
  trend: {
    type: Number,
    default: null // 正数表示上升，负数表示下降，null 表示无趋势
  },
  variant: {
    type: String,
    default: 'default', // default, gradient
    validator: (value) => ['default', 'gradient'].includes(value)
  }
})

const formattedValue = computed(() => {
  if (typeof props.value === 'number') {
    return props.value.toLocaleString()
  }
  return props.value
})

const iconStyle = computed(() => {
  if (props.variant === 'gradient') {
    return {
      background: `linear-gradient(135deg, ${props.color} 0%, ${adjustColor(props.color, -20)} 100%)`,
      color: 'white'
    }
  }
  return {
    background: `${props.color}20`,
    color: props.color
  }
})

const cardClass = computed(() => {
  return {
    'stat-card-gradient': props.variant === 'gradient'
  }
})

const trendClass = computed(() => {
  if (props.trend === null || props.trend === 0) {
    return 'trend-neutral'
  }
  return props.trend > 0 ? 'trend-up' : 'trend-down'
})

const trendIcon = computed(() => {
  if (props.trend === null || props.trend === 0) {
    return Minus
  }
  return props.trend > 0 ? ArrowUp : ArrowDown
})

// 辅助函数：调整颜色亮度
function adjustColor(color, amount) {
  const usePound = color[0] === '#'
  if (usePound) {
    color = color.slice(1)
  }

  const num = parseInt(color, 16)
  let r = (num >> 16) + amount
  let g = ((num >> 8) & 0x00FF) + amount
  let b = (num & 0x0000FF) + amount

  r = Math.max(Math.min(255, r), 0)
  g = Math.max(Math.min(255, g), 0)
  b = Math.max(Math.min(255, b), 0)

  return (usePound ? '#' : '') + (r << 16 | g << 8 | b).toString(16).padStart(6, '0')
}
</script>

<style scoped>
.stat-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  background: white;
  border-radius: var(--radius-lg, 12px);
  box-shadow: var(--shadow-soft, 0 2px 12px rgba(10, 46, 91, 0.08));
  transition: all var(--duration-normal, 0.2s) var(--ease-out, ease-out);
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-medium, 0 4px 20px rgba(10, 46, 91, 0.12));
}

.stat-card-gradient {
  background: linear-gradient(135deg, rgba(10, 46, 91, 0.03) 0%, rgba(0, 191, 255, 0.05) 100%);
}

.stat-icon {
  flex-shrink: 0;
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-lg, 12px);
  transition: all var(--duration-normal, 0.2s) var(--ease-out, ease-out);
}

.stat-card:hover .stat-icon {
  transform: scale(1.05);
}

.stat-content {
  flex: 1;
  min-width: 0;
}

.stat-label {
  font-size: 0.875rem;
  color: #666;
  margin-bottom: 0.25rem;
  font-weight: 500;
}

.stat-value {
  display: flex;
  align-items: baseline;
  gap: 0.25rem;
  margin-bottom: 0.25rem;
}

.value-number {
  font-size: 1.875rem;
  font-weight: 700;
  color: #0A2E5B;
  line-height: 1.2;
}

.value-unit {
  font-size: 1rem;
  color: #999;
  font-weight: 500;
}

.stat-trend {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.125rem 0.5rem;
  border-radius: var(--radius-base, 8px);
}

.trend-up {
  color: #52C41A;
  background: rgba(82, 196, 26, 0.1);
}

.trend-down {
  color: #F5222D;
  background: rgba(245, 34, 45, 0.1);
}

.trend-neutral {
  color: #999;
  background: rgba(153, 153, 153, 0.1);
}
</style>
