<template>
  <div class="min-h-screen bg-light-gray">
    <!-- 导航栏 -->
    <nav class="bg-white border-b sticky top-0 z-50 shadow-sm">
      <div class="container-custom py-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-4">
            <el-button :icon="ArrowLeft" @click="goBack" circle />
            <div>
              <h1 class="text-xl font-bold text-deep-blue">{{ job?.name || '加载中...' }}</h1>
              <div v-if="job" class="flex items-center gap-2 mt-1">
                <StatusTag :status="job.status" size="small" />
                <span class="text-sm text-gray-500">创建于 {{ formatDate(job.created_at) }}</span>
              </div>
            </div>
          </div>
          <div class="flex gap-2">
            <el-button
              v-if="job?.status === 'completed' && job.model_path"
              type="primary"
              :icon="Download"
            >
              下载模型
            </el-button>
            <el-button
              v-if="['training', 'preparing'].includes(job?.status)"
              type="warning"
              :icon="VideoPause"
            >
              取消训练
            </el-button>
            <el-button
              v-if="['failed', 'completed', 'cancelled'].includes(job?.status)"
              type="danger"
              :icon="Delete"
              @click="handleDelete"
            >
              删除任务
            </el-button>
          </div>
        </div>
      </div>
    </nav>

    <div class="container-custom py-8" v-loading="loading">
      <!-- 进度卡片 -->
      <div v-if="job && ['training', 'preparing'].includes(job.status)" class="bg-white rounded-lg shadow-sm p-6 mb-6">
        <div class="flex justify-between items-center mb-3">
          <h3 class="text-lg font-bold text-deep-blue">训练进度</h3>
          <div class="text-right">
            <div class="text-sm text-gray-500">当前轮次</div>
            <div class="text-2xl font-bold text-deep-blue">
              {{ job.current_epoch || 0 }} / {{ job.config?.training_params?.epochs || 0 }}
            </div>
          </div>
        </div>
        <el-progress
          :percentage="progress"
          :color="progressColor"
          :stroke-width="16"
        >
          <template #default="{ percentage }">
            <span class="font-bold">{{ percentage }}%</span>
          </template>
        </el-progress>
      </div>

      <!-- 统计卡片 -->
      <div v-if="job" class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
        <StatCard
          label="训练轮次"
          :value="job.config?.training_params?.epochs || 0"
          :icon="TrendCharts"
          color="#409EFF"
        />
        <StatCard
          label="批次大小"
          :value="job.config?.training_params?.batch_size || 0"
          :icon="CollectionTag"
          color="#67C23A"
        />
        <StatCard
          label="图像尺寸"
          :value="job.config?.training_params?.img_size || 0"
          unit="px"
          :icon="PictureFilled"
          color="#E6A23C"
        />
        <StatCard
          label="当前轮次"
          :value="job.current_epoch || 0"
          :icon="Cpu"
          color="#F56C6C"
        />
      </div>

      <!-- 主要内容区 -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <!-- 训练曲线 -->
        <div class="bg-white rounded-lg shadow-sm p-6">
          <h3 class="text-lg font-bold text-deep-blue mb-4">训练损失曲线</h3>
          <div v-if="metricsData.epochs.length > 0" class="h-80">
            <v-chart :option="lossChartOption" autoresize />
          </div>
          <EmptyState
            v-else
            icon="DataLine"
            title="暂无训练数据"
            description="训练开始后将显示损失曲线"
            :icon-size="48"
          />
        </div>

        <!-- 性能指标曲线 -->
        <div class="bg-white rounded-lg shadow-sm p-6">
          <h3 class="text-lg font-bold text-deep-blue mb-4">模型性能指标</h3>
          <div v-if="metricsData.epochs.length > 0" class="h-80">
            <v-chart :option="metricsChartOption" autoresize />
          </div>
          <EmptyState
            v-else
            icon="DataLine"
            title="暂无性能数据"
            description="训练开始后将显示性能曲线"
            :icon-size="48"
          />
        </div>
      </div>

      <!-- 训练配置和日志 -->
      <div class="bg-white rounded-lg shadow-sm p-6">
        <el-tabs v-model="activeTab" type="border-card">
          <!-- 训练配置 -->
          <el-tab-pane label="训练配置" name="config">
            <div v-if="job" class="space-y-6">
              <!-- 基础信息 -->
              <div>
                <h3 class="text-lg font-bold text-deep-blue mb-4">基础信息</h3>
                <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
                  <div>
                    <div class="text-sm text-gray-500 mb-1">任务名称</div>
                    <div class="font-medium">{{ job.name }}</div>
                  </div>
                  <div>
                    <div class="text-sm text-gray-500 mb-1">基础模型</div>
                    <div class="font-medium">{{ job.config?.base_model }}</div>
                  </div>
                  <div>
                    <div class="text-sm text-gray-500 mb-1">任务状态</div>
                    <StatusTag :status="job.status" />
                  </div>
                  <div>
                    <div class="text-sm text-gray-500 mb-1">创建时间</div>
                    <div class="font-medium">{{ formatDate(job.created_at) }}</div>
                  </div>
                  <div v-if="job.started_at">
                    <div class="text-sm text-gray-500 mb-1">开始时间</div>
                    <div class="font-medium">{{ formatDate(job.started_at) }}</div>
                  </div>
                  <div v-if="job.completed_at">
                    <div class="text-sm text-gray-500 mb-1">完成时间</div>
                    <div class="font-medium">{{ formatDate(job.completed_at) }}</div>
                  </div>
                </div>
              </div>

              <!-- 训练参数 -->
              <div>
                <h3 class="text-lg font-bold text-deep-blue mb-4">训练参数</h3>
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div v-for="(value, key) in job.config?.training_params" :key="key">
                    <div class="text-gray-500 mb-1">{{ key }}</div>
                    <div class="font-medium">{{ value }}</div>
                  </div>
                </div>
              </div>

              <!-- 最终指标（已完成时） -->
              <div v-if="job.status === 'completed' && job.final_metrics">
                <h3 class="text-lg font-bold text-deep-blue mb-4">最终性能指标</h3>
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4 p-4 bg-green-50 rounded-lg">
                  <div class="text-center">
                    <div class="text-gray-600 text-sm mb-1">mAP@50</div>
                    <div class="text-green-600 font-bold text-2xl">
                      {{ (job.final_metrics.mAP50 * 100).toFixed(2) }}%
                    </div>
                  </div>
                  <div class="text-center">
                    <div class="text-gray-600 text-sm mb-1">mAP@50-95</div>
                    <div class="text-green-600 font-bold text-2xl">
                      {{ (job.final_metrics.mAP50_95 * 100).toFixed(2) }}%
                    </div>
                  </div>
                  <div class="text-center">
                    <div class="text-gray-600 text-sm mb-1">Precision</div>
                    <div class="text-green-600 font-bold text-2xl">
                      {{ (job.final_metrics.precision * 100).toFixed(2) }}%
                    </div>
                  </div>
                  <div class="text-center">
                    <div class="text-gray-600 text-sm mb-1">Recall</div>
                    <div class="text-green-600 font-bold text-2xl">
                      {{ (job.final_metrics.recall * 100).toFixed(2) }}%
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </el-tab-pane>

          <!-- 训练日志 -->
          <el-tab-pane name="logs">
            <template #label>
              <span>训练日志 ({{ logs.length }})</span>
            </template>

            <div class="mb-4 flex justify-between items-center">
              <el-checkbox v-model="autoScroll" border>
                自动滚动到底部
              </el-checkbox>
              <el-button :icon="Refresh" @click="loadLogs" size="small">
                刷新日志
              </el-button>
            </div>

            <!-- 日志容器 -->
            <div
              ref="logsContainer"
              class="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm h-96 overflow-y-auto"
            >
              <div v-if="logs.length === 0" class="text-gray-500 text-center py-8">
                暂无日志
              </div>
              <div v-else>
                <div
                  v-for="(log, index) in logs"
                  :key="index"
                  class="mb-1 hover:bg-gray-800 px-2 py-1"
                >
                  <span class="text-gray-500">[{{ formatLogTime(log.timestamp) }}]</span>
                  <span class="ml-2">{{ log.message }}</span>
                </div>
              </div>
            </div>
          </el-tab-pane>

          <!-- 详细指标 -->
          <el-tab-pane label="详细指标" name="metrics">
            <div class="mb-4">
              <el-button :icon="Refresh" @click="loadMetrics" size="small">
                刷新指标
              </el-button>
            </div>

            <!-- 指标表格 -->
            <el-table
              :data="metricsTable"
              stripe
              max-height="500"
            >
              <el-table-column prop="epoch" label="Epoch" width="80" fixed />
              <el-table-column prop="train_loss" label="Train Loss" width="120">
                <template #default="{ row }">
                  {{ row.train_loss?.toFixed(4) || '-' }}
                </template>
              </el-table-column>
              <el-table-column prop="val_loss" label="Val Loss" width="120">
                <template #default="{ row }">
                  {{ row.val_loss?.toFixed(4) || '-' }}
                </template>
              </el-table-column>
              <el-table-column label="mAP@50" width="100">
                <template #default="{ row }">
                  {{ row.metrics?.mAP50 ? (row.metrics.mAP50 * 100).toFixed(2) + '%' : '-' }}
                </template>
              </el-table-column>
              <el-table-column label="mAP@50-95" width="120">
                <template #default="{ row }">
                  {{ row.metrics?.mAP50_95 ? (row.metrics.mAP50_95 * 100).toFixed(2) + '%' : '-' }}
                </template>
              </el-table-column>
              <el-table-column label="Precision" width="110">
                <template #default="{ row }">
                  {{ row.metrics?.precision ? (row.metrics.precision * 100).toFixed(2) + '%' : '-' }}
                </template>
              </el-table-column>
              <el-table-column label="Recall" width="100">
                <template #default="{ row }">
                  {{ row.metrics?.recall ? (row.metrics.recall * 100).toFixed(2) + '%' : '-' }}
                </template>
              </el-table-column>
              <el-table-column prop="timestamp" label="时间" width="180">
                <template #default="{ row }">
                  {{ formatDate(row.timestamp) }}
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ArrowLeft,
  Download,
  Delete,
  Refresh,
  VideoPause,
  TrendCharts,
  CollectionTag,
  PictureFilled,
  Cpu
} from '@element-plus/icons-vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'
import EmptyState from '@/components/common/EmptyState.vue'
import StatusTag from '@/components/common/StatusTag.vue'
import StatCard from '@/components/common/StatCard.vue'
import {
  getTrainingJob,
  getTrainingLogs,
  getTrainingMetrics,
  deleteTrainingJob,
  getLossChartOption,
  getMetricsChartOption,
  prepareChartData,
  calculateTrainingProgress
} from '@/api/training'

// 注册 ECharts 组件
use([
  CanvasRenderer,
  LineChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

const router = useRouter()
const route = useRoute()

// 数据
const loading = ref(true)
const job = ref(null)
const activeTab = ref('config')
const autoScroll = ref(true)
const logsContainer = ref(null)

// 日志和指标
const logs = ref([])
const metricsTable = ref([])
const metricsData = ref({
  epochs: [],
  trainLoss: [],
  valLoss: [],
  mAP50: [],
  mAP5095: [],
  precision: [],
  recall: []
})

// 定时刷新
let refreshTimer = null

// 计算进度
const progress = computed(() => {
  if (!job.value?.current_epoch || !job.value?.config?.training_params?.epochs) {
    return 0
  }
  return calculateTrainingProgress(
    job.value.current_epoch,
    job.value.config.training_params.epochs
  )
})

// 进度条颜色
const progressColor = computed(() => {
  const p = progress.value
  if (p < 30) return '#F56C6C'
  if (p < 70) return '#E6A23C'
  if (p < 100) return '#409EFF'
  return '#67C23A'
})

// 图表配置
const lossChartOption = computed(() => {
  return getLossChartOption(metricsData.value)
})

const metricsChartOption = computed(() => {
  return getMetricsChartOption(metricsData.value)
})

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString('zh-CN')
}

// 格式化日志时间
const formatLogTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN', { hour12: false })
}

// 加载任务详情
const loadJobDetail = async () => {
  loading.value = true
  try {
    const jobId = route.params.id
    job.value = await getTrainingJob(jobId)
  } catch (error) {
    console.error('加载任务详情失败:', error)
    ElMessage.error('加载任务详情失败')
  } finally {
    loading.value = false
  }
}

// 加载日志
const loadLogs = async () => {
  try {
    const jobId = route.params.id
    const response = await getTrainingLogs(jobId)
    const content = response.log_content || ''
    logs.value = content
      .split('\n')
      .map(line => line.trim())
      .filter(line => line.length > 0)
      .map(line => {
        const match = line.match(/^\[(.+?)\]\s*(.*)$/)
        if (match) {
          return {
            timestamp: match[1],
            message: match[2] || ''
          }
        }
        return { timestamp: null, message: line }
      })

    // 自动滚动到底部
    if (autoScroll.value) {
      await nextTick()
      scrollToBottom()
    }
  } catch (error) {
    console.error('加载日志失败:', error)
  }
}

// 加载指标
const loadMetrics = async () => {
  try {
    const jobId = route.params.id
    const response = await getTrainingMetrics(jobId)
    metricsTable.value = response.metrics || []

    // 准备图表数据
    metricsData.value = prepareChartData(metricsTable.value)
  } catch (error) {
    console.error('加载指标失败:', error)
  }
}

// 滚动到底部
const scrollToBottom = () => {
  if (logsContainer.value) {
    logsContainer.value.scrollTop = logsContainer.value.scrollHeight
  }
}

// 删除任务
const handleDelete = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要删除训练任务"${job.value.name}"吗？此操作将删除所有训练数据和模型，且不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )

    await deleteTrainingJob(route.params.id)
    ElMessage.success('删除成功')
    router.push('/admin/training')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除任务失败:', error)
      ElMessage.error('删除任务失败')
    }
  }
}

// 返回
const goBack = () => {
  router.push('/admin/training')
}

// 自动刷新
const startAutoRefresh = () => {
  refreshTimer = setInterval(async () => {
    try {
      // 刷新任务状态
      const jobId = route.params.id
      job.value = await getTrainingJob(jobId)

      // 如果正在训练，刷新日志和指标
      if (['training', 'preparing'].includes(job.value.status)) {
        if (activeTab.value === 'logs') {
          await loadLogs()
        }
        await loadMetrics()
      }
    } catch (error) {
      // 静默失败
    }
  }, 5000) // 每5秒刷新一次
}

// 监听标签页切换
watch(activeTab, async (newTab) => {
  if (newTab === 'logs' && logs.value.length === 0) {
    await loadLogs()
  } else if (newTab === 'metrics' && metricsTable.value.length === 0) {
    await loadMetrics()
  }
})

// 生命周期
onMounted(async () => {
  await loadJobDetail()
  await loadMetrics()
  startAutoRefresh()
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
})
</script>

<style scoped>
.container-custom {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 1rem;
}

/* 日志容器滚动条样式 */
.bg-gray-900::-webkit-scrollbar {
  width: 8px;
}

.bg-gray-900::-webkit-scrollbar-track {
  background: #1f2937;
}

.bg-gray-900::-webkit-scrollbar-thumb {
  background: #4b5563;
  border-radius: 4px;
}

.bg-gray-900::-webkit-scrollbar-thumb:hover {
  background: #6b7280;
}

:deep(.el-tabs__item) {
  font-size: 15px;
  font-weight: 500;
}
</style>
