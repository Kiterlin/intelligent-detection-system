<template>
  <div class="space-y-6">
    <!-- 页面标题 -->
    <div>
      <h1 class="text-2xl font-bold text-deep-blue mb-2">数据看板</h1>
      <p class="text-gray-600">系统运营数据总览</p>
    </div>

    <!-- 统计卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <!-- 总用户数 -->
      <div class="bg-white rounded-xl shadow-soft p-6 border-l-4 border-bright-cyan">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600 mb-1">总用户数</p>
            <p class="text-3xl font-bold text-deep-blue">{{ stats.userCount }}</p>
            <p class="text-xs text-green-500 mt-2">
              <span class="inline-flex items-center">
                <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
                活跃用户
              </span>
            </p>
          </div>
          <div class="w-16 h-16 bg-gradient-to-br from-bright-cyan to-bright-cyan-dark rounded-2xl flex items-center justify-center">
            <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
          </div>
        </div>
      </div>

      <!-- 模型数量 -->
      <div class="bg-white rounded-xl shadow-soft p-6 border-l-4 border-coral-orange">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600 mb-1">模型数量</p>
            <p class="text-3xl font-bold text-deep-blue">{{ stats.modelCount }}</p>
            <p class="text-xs text-green-500 mt-2">
              <span class="inline-flex items-center">
                <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                已激活
              </span>
            </p>
          </div>
          <div class="w-16 h-16 bg-gradient-to-br from-coral-orange to-coral-orange-dark rounded-2xl flex items-center justify-center">
            <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
            </svg>
          </div>
        </div>
      </div>

      <!-- 今日检测数 -->
      <div class="bg-white rounded-xl shadow-soft p-6 border-l-4 border-purple-500">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600 mb-1">今日检测数</p>
            <p class="text-3xl font-bold text-deep-blue">{{ stats.todayDetections }}</p>
            <p class="text-xs text-green-500 mt-2">
              <span class="inline-flex items-center">
                <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
                较昨日
              </span>
            </p>
          </div>
          <div class="w-16 h-16 bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl flex items-center justify-center">
            <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- 检测趋势图 -->
      <div class="bg-white rounded-xl shadow-soft overflow-hidden">
        <div class="px-6 py-4 border-b border-gray-200">
          <h3 class="text-lg font-semibold text-deep-blue">检测趋势</h3>
          <p class="text-sm text-gray-500">最近7天检测数据统计</p>
        </div>
        <div class="p-6">
          <VChart class="chart" :option="detectionTrendOption" autoresize />
        </div>
      </div>

      <!-- 模型使用统计 -->
      <div class="bg-white rounded-xl shadow-soft overflow-hidden">
        <div class="px-6 py-4 border-b border-gray-200">
          <h3 class="text-lg font-semibold text-deep-blue">模型使用统计</h3>
          <p class="text-sm text-gray-500">各模型使用次数对比</p>
        </div>
        <div class="p-6">
          <VChart class="chart" :option="modelUsageOption" autoresize />
        </div>
      </div>
    </div>

    <!-- 快捷操作 -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <router-link
        to="/admin/users"
        class="bg-white rounded-xl shadow-soft p-6 hover:shadow-medium transition-shadow group"
      >
        <div class="flex items-center justify-between mb-4">
          <div class="w-12 h-12 bg-bright-cyan/10 rounded-xl flex items-center justify-center group-hover:bg-bright-cyan/20 transition-colors">
            <svg class="w-6 h-6 text-bright-cyan" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
          </div>
          <svg class="w-5 h-5 text-gray-400 group-hover:text-bright-cyan transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </div>
        <h4 class="text-lg font-semibold text-deep-blue mb-2">用户管理</h4>
        <p class="text-sm text-gray-600">查看和管理系统用户</p>
      </router-link>

      <router-link
        to="/admin/models"
        class="bg-white rounded-xl shadow-soft p-6 hover:shadow-medium transition-shadow group"
      >
        <div class="flex items-center justify-between mb-4">
          <div class="w-12 h-12 bg-coral-orange/10 rounded-xl flex items-center justify-center group-hover:bg-coral-orange/20 transition-colors">
            <svg class="w-6 h-6 text-coral-orange" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
            </svg>
          </div>
          <svg class="w-5 h-5 text-gray-400 group-hover:text-coral-orange transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </div>
        <h4 class="text-lg font-semibold text-deep-blue mb-2">模型管理</h4>
        <p class="text-sm text-gray-600">管理AI检测模型</p>
      </router-link>

      <button
        class="bg-white rounded-xl shadow-soft p-6 hover:shadow-medium transition-shadow group text-left"
        @click="handleRefresh"
      >
        <div class="flex items-center justify-between mb-4">
          <div class="w-12 h-12 bg-purple-500/10 rounded-xl flex items-center justify-center group-hover:bg-purple-500/20 transition-colors">
            <svg class="w-6 h-6 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </div>
          <svg class="w-5 h-5 text-gray-400 group-hover:text-purple-500 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </div>
        <h4 class="text-lg font-semibold text-deep-blue mb-2">刷新数据</h4>
        <p class="text-sm text-gray-600">重新加载统计数据</p>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, BarChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import { getUserList, getModelList, getDashboardStats } from '@/api/admin'
import { ElMessage } from 'element-plus'

// 注册ECharts组件
use([
  CanvasRenderer,
  LineChart,
  BarChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

// 统计数据
const stats = ref({
  userCount: 0,
  modelCount: 0,
  todayDetections: 0
})

// 图表数据
const chartData = ref({
  detectionTrend: [],
  modelUsage: []
})

// 检测趋势图配置
const detectionTrendOption = computed(() => ({
  tooltip: {
    trigger: 'axis',
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    borderColor: '#00BFFF',
    borderWidth: 1,
    textStyle: {
      color: '#0A2E5B'
    }
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '10%',
    top: '10%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    boundaryGap: false,
    data: chartData.value.detectionTrend.map(item => {
      const date = new Date(item.date)
      return `${date.getMonth() + 1}/${date.getDate()}`
    }),
    axisLine: {
      lineStyle: {
        color: '#e5e7eb'
      }
    },
    axisLabel: {
      color: '#6b7280'
    }
  },
  yAxis: {
    type: 'value',
    axisLine: {
      lineStyle: {
        color: '#e5e7eb'
      }
    },
    axisLabel: {
      color: '#6b7280'
    },
    splitLine: {
      lineStyle: {
        color: '#f3f4f6',
        type: 'dashed'
      }
    }
  },
  series: [
    {
      name: '检测数量',
      type: 'line',
      smooth: true,
      data: chartData.value.detectionTrend.map(item => item.count),
      areaStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(0, 191, 255, 0.3)' },
            { offset: 1, color: 'rgba(0, 191, 255, 0.05)' }
          ]
        }
      },
      lineStyle: {
        color: '#00BFFF',
        width: 3
      },
      itemStyle: {
        color: '#00BFFF',
        borderWidth: 2,
        borderColor: '#fff'
      },
      emphasis: {
        itemStyle: {
          scale: 1.5
        }
      }
    }
  ]
}))

// 模型使用统计图配置
const modelUsageOption = computed(() => ({
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'shadow'
    },
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    borderColor: '#FF7F50',
    borderWidth: 1,
    textStyle: {
      color: '#0A2E5B'
    }
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '10%',
    top: '10%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    data: chartData.value.modelUsage.map(item => item.name),
    axisLine: {
      lineStyle: {
        color: '#e5e7eb'
      }
    },
    axisLabel: {
      color: '#6b7280',
      interval: 0,
      rotate: chartData.value.modelUsage.length > 5 ? 30 : 0
    }
  },
  yAxis: {
    type: 'value',
    axisLine: {
      lineStyle: {
        color: '#e5e7eb'
      }
    },
    axisLabel: {
      color: '#6b7280'
    },
    splitLine: {
      lineStyle: {
        color: '#f3f4f6',
        type: 'dashed'
      }
    }
  },
  series: [
    {
      name: '使用次数',
      type: 'bar',
      data: chartData.value.modelUsage.map(item => item.count),
      itemStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [
            { offset: 0, color: '#FF7F50' },
            { offset: 1, color: '#FFA07A' }
          ]
        },
        borderRadius: [8, 8, 0, 0]
      },
      emphasis: {
        itemStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: '#FF6347' },
              { offset: 1, color: '#FF7F50' }
            ]
          }
        }
      },
      barWidth: '50%'
    }
  ]
}))

// 加载数据
const loadData = async () => {
  try {
    // 获取用户总数
    const userRes = await getUserList({ page: 1, page_size: 1 })
    stats.value.userCount = userRes.total || 0

    // 获取模型总数
    const modelRes = await getModelList({ page: 1, page_size: 1 })
    stats.value.modelCount = modelRes.total || 0

    // 获取Dashboard统计数据
    const dashboardStats = await getDashboardStats()
    stats.value.todayDetections = dashboardStats.today_detections || 0

    // ��新图表数据
    chartData.value.detectionTrend = dashboardStats.detection_trend || []
    chartData.value.modelUsage = dashboardStats.model_usage || []
  } catch (error) {
    console.error('Load data error:', error)
    ElMessage.error('加载数据失败：' + (error.response?.data?.detail || error.message))
  }
}

// 刷新数据
const handleRefresh = async () => {
  try {
    await loadData()
    ElMessage.success('数据刷新成功')
  } catch (error) {
    ElMessage.error('刷新失败')
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.chart {
  width: 100%;
  height: 300px;
}
</style>
