<template>
  <div class="min-h-screen bg-light-gray">
    <!-- 页面标题 -->
    <div class="bg-gradient-ocean py-12 mb-8">
      <div class="container-custom">
        <h1 class="text-3xl md:text-4xl font-bold text-white mb-2">批量检测任务</h1>
        <p class="text-white/80">查看和监控您的批量检测任务进度</p>
      </div>
    </div>

    <div class="container-custom pb-12">
      <!-- 筛选栏 -->
      <div class="card-hover mb-6">
        <div class="flex flex-col md:flex-row gap-4">
          <div>
            <label class="text-sm text-gray-600 mb-2 block">任务状态</label>
            <el-select
              v-model="statusFilter"
              placeholder="全部状态"
              clearable
              @change="loadJobs"
            >
              <el-option label="全部" value="" />
              <el-option label="等待中" value="pending" />
              <el-option label="运行中" value="running" />
              <el-option label="已完成" value="completed" />
              <el-option label="失败" value="failed" />
              <el-option label="已取消" value="cancelled" />
            </el-select>
          </div>

          <div class="flex-1" />

          <div class="flex items-end">
            <el-button :icon="Refresh" @click="loadJobs">
              刷新
            </el-button>
          </div>
        </div>
      </div>

      <!-- 任务列表 -->
      <div v-loading="loading" class="card-hover">
        <div
          v-if="jobs.length === 0 && !loading"
          class="text-center py-20"
        >
          <el-icon :size="64" class="text-gray-300 mb-4">
            <DocumentCopy />
          </el-icon>
          <p class="text-gray-400">还没有批量检测任务</p>
        </div>

        <div v-else>
          <div
            v-for="job in jobs"
            :key="job.id"
            class="border-b border-gray-100 last:border-0 py-6"
          >
            <!-- 任务头部 -->
            <div class="flex items-start justify-between mb-4">
              <div class="flex-1">
                <div class="flex items-center gap-3 mb-2">
                  <h3 class="text-lg font-bold text-deep-blue">
                    {{ job.dataset_name }}
                  </h3>
                  <el-tag :type="getStatusType(job.status)">
                    {{ getStatusLabel(job.status) }}
                  </el-tag>
                </div>

                <div class="text-sm text-gray-500 space-y-1">
                  <div class="flex items-center gap-4">
                    <span>
                      <el-icon><Tools /></el-icon>
                      模型: {{ job.model_name }}
                    </span>
                    <span>
                      <el-icon><Files /></el-icon>
                      文件: {{ job.completed_files + job.failed_files }} / {{ job.total_files }}
                    </span>
                    <span>
                      <el-icon><Clock /></el-icon>
                      创建: {{ formatDate(job.created_at) }}
                    </span>
                  </div>
                </div>
              </div>

              <div v-if="job.status === 'completed'" class="ml-4">
                <el-button size="small" type="primary" @click="viewResults(job)">
                  查看结果
                </el-button>
              </div>
            </div>

            <!-- 进度条 -->
            <div class="mb-3">
              <el-progress
                :percentage="calculateProgress(job)"
                :status="getProgressStatus(job.status)"
                :show-text="true"
              >
                <template #default="{ percentage }">
                  <span class="text-xs">
                    {{ percentage }}%
                    <span v-if="job.status === 'running'">(运行中)</span>
                  </span>
                </template>
              </el-progress>
            </div>

            <!-- 详细统计 -->
            <div class="grid grid-cols-3 gap-4 text-center">
              <div class="bg-green-50 rounded px-3 py-2">
                <p class="text-xs text-gray-500 mb-1">成功</p>
                <p class="text-lg font-semibold text-green-600">
                  {{ job.completed_files }}
                </p>
              </div>
              <div class="bg-red-50 rounded px-3 py-2">
                <p class="text-xs text-gray-500 mb-1">失败</p>
                <p class="text-lg font-semibold text-red-600">
                  {{ job.failed_files }}
                </p>
              </div>
              <div class="bg-gray-50 rounded px-3 py-2">
                <p class="text-xs text-gray-500 mb-1">待处理</p>
                <p class="text-lg font-semibold text-gray-600">
                  {{ job.total_files - job.completed_files - job.failed_files }}
                </p>
              </div>
            </div>

            <!-- 错误信息 -->
            <div v-if="job.error_message" class="mt-4">
              <el-alert
                type="error"
                :title="job.error_message"
                :closable="false"
              />
            </div>
          </div>
        </div>

        <!-- 分页 -->
        <div v-if="total > 0" class="flex justify-center mt-6 pt-6 border-t border-gray-100">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :total="total"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next"
            @current-change="loadJobs"
            @size-change="loadJobs"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Refresh,
  DocumentCopy,
  Tools,
  Files,
  Clock
} from '@element-plus/icons-vue'
import { getBatchJobs, formatBatchJobStatus } from '@/api/dataset'

const router = useRouter()

// 任务列表
const jobs = ref([])
const loading = ref(false)
const statusFilter = ref('')

// 分页
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

// 轮询定时器
let pollingTimer = null

// 加载任务列表
const loadJobs = async () => {
  loading.value = true
  try {
    const params = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value
    }
    if (statusFilter.value) {
      params.status = statusFilter.value
    }

    const res = await getBatchJobs(params)
    jobs.value = res.items
    total.value = res.total
  } catch (error) {
    console.error('加载任务列表失败:', error)
    ElMessage.error('加载任务列表失败')
  } finally {
    loading.value = false
  }
}

// 启动轮询（只轮询运行中的任务）
const startPolling = () => {
  pollingTimer = setInterval(() => {
    const hasRunningJobs = jobs.value.some(job =>
      job.status === 'running' || job.status === 'pending'
    )
    if (hasRunningJobs) {
      loadJobs()
    }
  }, 3000) // 每3秒轮询一次
}

// 停止轮询
const stopPolling = () => {
  if (pollingTimer) {
    clearInterval(pollingTimer)
    pollingTimer = null
  }
}

// 计算进度
const calculateProgress = (job) => {
  if (job.total_files === 0) return 0
  const processed = job.completed_files + job.failed_files
  return Math.round((processed / job.total_files) * 100)
}

// 获取状态类型
const getStatusType = (status) => {
  const statusInfo = formatBatchJobStatus(status)
  return statusInfo.type
}

// 获取状态标签
const getStatusLabel = (status) => {
  const statusInfo = formatBatchJobStatus(status)
  return statusInfo.label
}

// 获取进度条状态
const getProgressStatus = (status) => {
  if (status === 'completed') return 'success'
  if (status === 'failed') return 'exception'
  if (status === 'running') return undefined
  return undefined
}

// 查看结果（跳转到检测历史）
const viewResults = (job) => {
  router.push({
    path: '/detection-history',
    query: {
      dataset_id: job.dataset_id
    }
  })
}

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 页面加载时获取数据并启动轮询
onMounted(() => {
  loadJobs()
  startPolling()
})

// 页面卸载时停止轮询
onUnmounted(() => {
  stopPolling()
})
</script>
