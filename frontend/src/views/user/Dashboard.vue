<template>
  <div class="min-h-screen bg-light-gray">
    <!-- 页面标题 -->
    <div class="bg-gradient-ocean py-12 mb-8">
      <div class="container-custom">
        <h1 class="text-3xl md:text-4xl font-bold text-white mb-2">仪表盘</h1>
        <p class="text-white/80">查看您的检测数据概览和统计信息</p>
      </div>
    </div>

    <div class="container-custom pb-12">
      <!-- 统计卡片 -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <!-- 总检测次数 -->
        <div class="card-hover bg-gradient-to-br from-blue-500 to-blue-600 text-white animate-fade-in">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-blue-100 text-sm mb-1">总检测次数</p>
              <h3 class="text-3xl font-bold">{{ stats.total_detections }}</h3>
            </div>
            <div class="w-14 h-14 bg-white/20 rounded-lg flex items-center justify-center">
              <el-icon :size="28">
                <DataAnalysis />
              </el-icon>
            </div>
          </div>
        </div>

        <!-- 本周视频检测 -->
        <div class="card-hover bg-gradient-to-br from-purple-500 to-purple-600 text-white animate-fade-in" style="animation-delay: 0.1s">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-purple-100 text-sm mb-1">本周视频检测</p>
              <h3 class="text-3xl font-bold">{{ stats.weekly_videos }}</h3>
            </div>
            <div class="w-14 h-14 bg-white/20 rounded-lg flex items-center justify-center">
              <el-icon :size="28">
                <VideoCamera />
              </el-icon>
            </div>
          </div>
        </div>

        <!-- 总检测对象数 -->
        <div class="card-hover bg-gradient-to-br from-green-500 to-green-600 text-white animate-fade-in" style="animation-delay: 0.2s">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-green-100 text-sm mb-1">总检测对象</p>
              <h3 class="text-3xl font-bold">{{ stats.total_objects }}</h3>
            </div>
            <div class="w-14 h-14 bg-white/20 rounded-lg flex items-center justify-center">
              <el-icon :size="28">
                <Box />
              </el-icon>
            </div>
          </div>
        </div>

        <!-- 最常检测类别 -->
        <div class="card-hover bg-gradient-to-br from-orange-500 to-orange-600 text-white animate-fade-in" style="animation-delay: 0.3s">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-orange-100 text-sm mb-1">最常检测类别</p>
              <h3 class="text-xl font-bold truncate">{{ stats.most_detected_class }}</h3>
            </div>
            <div class="w-14 h-14 bg-white/20 rounded-lg flex items-center justify-center">
              <el-icon :size="28">
                <Trophy />
              </el-icon>
            </div>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <!-- 模型使用统计图 -->
        <div class="card-hover animate-slide-up">
          <h3 class="text-lg font-bold text-deep-blue mb-4 flex items-center">
            <el-icon class="mr-2" :size="20">
              <PieChart />
            </el-icon>
            模型使用分布
          </h3>
          <div v-if="stats.model_usage && stats.model_usage.length > 0">
            <v-chart
              class="chart"
              :option="modelUsageChartOption"
              autoresize
              style="height: 300px"
            />
          </div>
          <div v-else class="flex items-center justify-center h-64 text-gray-400">
            <div class="text-center">
              <el-icon :size="48" class="mb-2">
                <Document />
              </el-icon>
              <p>暂无数据</p>
            </div>
          </div>
        </div>

        <!-- 快速操作 -->
        <div class="card-hover animate-slide-up" style="animation-delay: 0.1s">
          <h3 class="text-lg font-bold text-deep-blue mb-4 flex items-center">
            <el-icon class="mr-2" :size="20">
              <Pointer />
            </el-icon>
            快速操作
          </h3>
          <div class="grid grid-cols-1 gap-3">
            <button
              class="flex items-center justify-between p-4 bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg hover:shadow-md transition-all group"
              @click="router.push('/detection')"
            >
              <div class="flex items-center">
                <div class="w-12 h-12 bg-blue-500 rounded-lg flex items-center justify-center mr-3 group-hover:scale-110 transition-transform">
                  <el-icon :size="24" class="text-white">
                    <Camera />
                  </el-icon>
                </div>
                <div class="text-left">
                  <p class="font-semibold text-deep-blue">开始图像检测</p>
                  <p class="text-sm text-gray-600">上传图片进行目标检测</p>
                </div>
              </div>
              <el-icon class="text-gray-400 group-hover:text-blue-500 group-hover:translate-x-1 transition-all">
                <ArrowRight />
              </el-icon>
            </button>

            <button
              class="flex items-center justify-between p-4 bg-gradient-to-r from-purple-50 to-purple-100 rounded-lg hover:shadow-md transition-all group"
              @click="router.push('/detection')"
            >
              <div class="flex items-center">
                <div class="w-12 h-12 bg-purple-500 rounded-lg flex items-center justify-center mr-3 group-hover:scale-110 transition-transform">
                  <el-icon :size="24" class="text-white">
                    <VideoCamera />
                  </el-icon>
                </div>
                <div class="text-left">
                  <p class="font-semibold text-deep-blue">开始视频检测</p>
                  <p class="text-sm text-gray-600">上传视频进行批量检测</p>
                </div>
              </div>
              <el-icon class="text-gray-400 group-hover:text-purple-500 group-hover:translate-x-1 transition-all">
                <ArrowRight />
              </el-icon>
            </button>

            <button
              class="flex items-center justify-between p-4 bg-gradient-to-r from-green-50 to-green-100 rounded-lg hover:shadow-md transition-all group"
              @click="router.push('/detection-history')"
            >
              <div class="flex items-center">
                <div class="w-12 h-12 bg-green-500 rounded-lg flex items-center justify-center mr-3 group-hover:scale-110 transition-transform">
                  <el-icon :size="24" class="text-white">
                    <Clock />
                  </el-icon>
                </div>
                <div class="text-left">
                  <p class="font-semibold text-deep-blue">查看检测历史</p>
                  <p class="text-sm text-gray-600">浏览所有历史检测记录</p>
                </div>
              </div>
              <el-icon class="text-gray-400 group-hover:text-green-500 group-hover:translate-x-1 transition-all">
                <ArrowRight />
              </el-icon>
            </button>
          </div>
        </div>
      </div>

      <!-- 最近活动 -->
      <div class="card-hover animate-slide-up" style="animation-delay: 0.2s">
        <h3 class="text-lg font-bold text-deep-blue mb-4 flex items-center">
          <el-icon class="mr-2" :size="20">
            <Timer />
          </el-icon>
          最近活动
        </h3>
        <div v-if="stats.recent_activities && stats.recent_activities.length > 0">
          <div class="space-y-3">
            <div
              v-for="activity in stats.recent_activities"
              :key="activity.id"
              class="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer"
              @click="router.push('/detection-history')"
            >
              <div class="flex items-center space-x-3">
                <!-- 类型图标 -->
                <div :class="getActivityIconClass(activity.input_type)">
                  <el-icon :size="20">
                    <Camera v-if="activity.input_type === 'image'" />
                    <VideoCamera v-else />
                  </el-icon>
                </div>
                <!-- 信息 -->
                <div>
                  <p class="font-medium text-deep-blue">
                    {{ activity.input_type === 'image' ? '图像检测' : '视频检测' }}
                  </p>
                  <p class="text-sm text-gray-600">
                    检测到 {{ activity.detected_count }} 个对象
                  </p>
                </div>
              </div>
              <!-- 状态和时间 -->
              <div class="text-right">
                <el-tag
                  :type="getStatusType(activity.status)"
                  size="small"
                  class="mb-1"
                >
                  {{ getStatusText(activity.status) }}
                </el-tag>
                <p class="text-xs text-gray-500">
                  {{ formatTime(activity.created_at) }}
                </p>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="flex items-center justify-center py-12 text-gray-400">
          <div class="text-center">
            <el-icon :size="48" class="mb-2">
              <Document />
            </el-icon>
            <p>暂无最近活动</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <el-skeleton v-if="loading" :rows="10" animated />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  DataAnalysis,
  VideoCamera,
  Box,
  Trophy,
  PieChart,
  Pointer,
  Camera,
  ArrowRight,
  Clock,
  Timer,
  Document
} from '@element-plus/icons-vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart as EchartsPie } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent
} from 'echarts/components'
import { getDashboardStats } from '@/api/detect'

// 注册 ECharts 组件
use([
  CanvasRenderer,
  EchartsPie,
  TitleComponent,
  TooltipComponent,
  LegendComponent
])

const router = useRouter()
const loading = ref(false)
const stats = ref({
  total_detections: 0,
  weekly_videos: 0,
  total_objects: 0,
  most_detected_class: '无',
  model_usage: [],
  recent_activities: []
})

// 模型使用图表配置
const modelUsageChartOption = computed(() => ({
  tooltip: {
    trigger: 'item',
    formatter: '{b}: {c} 次 ({d}%)'
  },
  legend: {
    orient: 'vertical',
    left: 'left',
    top: 'center'
  },
  series: [
    {
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 10,
        borderColor: '#fff',
        borderWidth: 2
      },
      label: {
        show: false,
        position: 'center'
      },
      emphasis: {
        label: {
          show: true,
          fontSize: 16,
          fontWeight: 'bold'
        }
      },
      labelLine: {
        show: false
      },
      data: stats.value.model_usage.map(item => ({
        value: item.count,
        name: item.model_name
      }))
    }
  ]
}))

// 获取活动类型图标样式
const getActivityIconClass = (type) => {
  const baseClass = 'w-10 h-10 rounded-lg flex items-center justify-center'
  return type === 'image'
    ? `${baseClass} bg-blue-100 text-blue-600`
    : `${baseClass} bg-purple-100 text-purple-600`
}

// 获取状态类型
const getStatusType = (status) => {
  const statusMap = {
    completed: 'success',
    processing: 'warning',
    pending: 'info',
    failed: 'danger'
  }
  return statusMap[status] || 'info'
}

// 获取状态文本
const getStatusText = (status) => {
  const statusMap = {
    completed: '已完成',
    processing: '处理中',
    pending: '等待中',
    failed: '失败'
  }
  return statusMap[status] || status
}

// 格式化时间
const formatTime = (timeStr) => {
  const time = new Date(timeStr)
  const now = new Date()
  const diff = now - time
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`

  return time.toLocaleDateString('zh-CN', {
    month: 'short',
    day: 'numeric'
  })
}

// 加载仪表盘数据
const loadDashboardData = async () => {
  loading.value = true
  try {
    const response = await getDashboardStats()
    stats.value = response.data
  } catch (error) {
    console.error('加载仪表盘数据失败:', error)
    ElMessage.error('加载数据失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadDashboardData()
})
</script>

<style scoped>
.chart {
  width: 100%;
}
</style>
