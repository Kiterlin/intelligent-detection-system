<template>
  <div class="min-h-screen bg-light-gray">
    <!-- 页面头部 -->
    <PageHeader
      title="模型训练"
      subtitle="创建和管理 YOLO 模型训练任务，训练自定义目标检测模型"
    >
      <template #actions>
        <el-button
          type="primary"
          :icon="Plus"
          size="large"
          @click="goToCreate"
        >
          创建训练任务
        </el-button>
      </template>
    </PageHeader>

    <div class="container-custom pb-12">
      <!-- 操作栏 -->
      <div class="flex flex-col md:flex-row gap-4 mb-6">
        <!-- 状态过滤 -->
        <el-select
          v-model="statusFilter"
          placeholder="状态筛选"
          clearable
          @change="loadJobs"
          style="width: 150px"
        >
          <el-option
            v-for="option in statusOptions"
            :key="option.value"
            :label="option.label"
            :value="option.value"
          />
        </el-select>

        <div class="flex-1"></div>

        <!-- 刷新按钮 -->
        <el-button :icon="Refresh" @click="loadJobs">
          刷新
        </el-button>
      </div>

      <!-- 任务列表 -->
      <div v-loading="loading">
        <!-- 空状态 -->
        <EmptyState
          v-if="jobs.length === 0 && !loading"
          icon="Cpu"
          title="还没有训练任务"
          description="创建第一个训练任务，使用标注数据训练自定义目标检测模型"
        >
          <template #actions>
            <el-button type="primary" :icon="Plus" @click="goToCreate">
              创建训练任务
            </el-button>
          </template>
        </EmptyState>

        <!-- 任务卡片 -->
        <div v-else class="grid grid-cols-1 gap-6">
          <div
            v-for="job in jobs"
            :key="job.id"
            class="card-hover animate-fade-in"
          >
            <div class="flex items-start gap-6">
              <!-- 左侧：状态图标 -->
              <div class="flex-shrink-0">
                <div
                  class="w-16 h-16 rounded-lg flex items-center justify-center"
                  :class="getStatusBgClass(job.status)"
                >
                  <el-icon :size="32" class="text-white">
                    <component :is="getStatusIcon(job.status)" />
                  </el-icon>
                </div>
              </div>

              <!-- 中间：任务信息 -->
              <div class="flex-1 min-w-0">
                <!-- 任务名称和状态 -->
                <div class="flex items-start justify-between mb-3">
                  <div>
                    <h3 class="text-xl font-bold text-deep-blue mb-2">
                      {{ job.name }}
                    </h3>
                    <div class="flex items-center gap-2">
                      <StatusTag :status="job.status" />
                      <el-tag size="small" effect="plain">
                        {{ getBaseModelLabel(job.config?.base_model) }}
                      </el-tag>
                    </div>
                  </div>
                </div>

                <!-- 训练进度（训练中时显示） -->
                <div v-if="job.status === 'training' && job.current_epoch" class="mb-3">
                  <div class="flex justify-between text-sm mb-1">
                    <span class="text-gray-500">训练进度</span>
                    <span class="text-deep-blue font-medium">
                      Epoch {{ job.current_epoch }}/{{ job.config?.training_params?.epochs || 0 }}
                      ({{ calculateProgress(job) }}%)
                    </span>
                  </div>
                  <el-progress
                    :percentage="calculateProgress(job)"
                    :color="getProgressColor(job.status)"
                    :stroke-width="8"
                  />
                </div>

                <!-- 训练参数 -->
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-3 p-3 bg-gray-50 rounded-lg text-sm">
                  <div class="text-center">
                    <div class="text-gray-500 text-xs mb-1">训练轮次</div>
                    <div class="text-deep-blue font-bold">
                      {{ job.config?.training_params?.epochs || '-' }}
                    </div>
                  </div>
                  <div class="text-center">
                    <div class="text-gray-500 text-xs mb-1">批次大小</div>
                    <div class="text-deep-blue font-bold">
                      {{ job.config?.training_params?.batch_size || '-' }}
                    </div>
                  </div>
                  <div class="text-center">
                    <div class="text-gray-500 text-xs mb-1">图像尺寸</div>
                    <div class="text-deep-blue font-bold">
                      {{ job.config?.training_params?.img_size || '-' }}
                    </div>
                  </div>
                  <div class="text-center">
                    <div class="text-gray-500 text-xs mb-1">设备</div>
                    <div class="text-deep-blue font-bold">
                      {{ job.config?.training_params?.device || '-' }}
                    </div>
                  </div>
                </div>

                <!-- 性能指标（已完成时显示） -->
                <div v-if="job.status === 'completed' && job.final_metrics" class="mb-3">
                  <div class="grid grid-cols-4 gap-4 p-3 bg-green-50 rounded-lg text-sm">
                    <div class="text-center">
                      <div class="text-gray-600 text-xs mb-1">mAP@50</div>
                      <div class="text-green-600 font-bold text-lg">
                        {{ (job.final_metrics.mAP50 * 100).toFixed(1) }}%
                      </div>
                    </div>
                    <div class="text-center">
                      <div class="text-gray-600 text-xs mb-1">mAP@50-95</div>
                      <div class="text-green-600 font-bold text-lg">
                        {{ (job.final_metrics.mAP50_95 * 100).toFixed(1) }}%
                      </div>
                    </div>
                    <div class="text-center">
                      <div class="text-gray-600 text-xs mb-1">Precision</div>
                      <div class="text-green-600 font-bold text-lg">
                        {{ (job.final_metrics.precision * 100).toFixed(1) }}%
                      </div>
                    </div>
                    <div class="text-center">
                      <div class="text-gray-600 text-xs mb-1">Recall</div>
                      <div class="text-green-600 font-bold text-lg">
                        {{ (job.final_metrics.recall * 100).toFixed(1) }}%
                      </div>
                    </div>
                  </div>
                </div>

                <!-- 错误信息（失败时显示） -->
                <div v-if="job.status === 'failed' && job.error_message" class="mb-3">
                  <el-alert type="error" :closable="false">
                    <template #title>
                      <div class="text-sm">{{ job.error_message }}</div>
                    </template>
                  </el-alert>
                </div>

                <!-- 底部信息和操作 -->
                <div class="flex items-center justify-between text-sm text-gray-500">
                  <div class="flex items-center gap-4">
                    <span>创建时间: {{ formatDate(job.created_at) }}</span>
                    <span v-if="job.completed_at">
                      完成时间: {{ formatDate(job.completed_at) }}
                    </span>
                  </div>
                  <div class="flex gap-2">
                    <el-button
                      size="small"
                      type="primary"
                      :icon="Monitor"
                      @click="goToMonitor(job.id)"
                    >
                      查看详情
                    </el-button>
                    <el-button
                      v-if="job.status === 'completed' && job.model_path"
                      size="small"
                      :icon="Download"
                      @click="downloadModel(job)"
                    >
                      下载模型
                    </el-button>
                    <el-button
                      v-if="['failed', 'completed', 'cancelled'].includes(job.status)"
                      size="small"
                      type="danger"
                      :icon="Delete"
                      @click="handleDelete(job)"
                    >
                      删除
                    </el-button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 分页 -->
        <div v-if="total > 0" class="mt-8 flex justify-center">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :total="total"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="loadJobs"
            @current-change="loadJobs"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  Refresh,
  Monitor,
  Download,
  Delete,
  Loading,
  CircleCheck,
  CircleClose,
  Clock,
  Cpu
} from '@element-plus/icons-vue'
import PageHeader from '@/components/common/PageHeader.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import StatusTag from '@/components/common/StatusTag.vue'
import {
  getTrainingJobs,
  deleteTrainingJob,
  getTrainingStatusOptions,
  calculateTrainingProgress
} from '@/api/training'

const router = useRouter()

// 数据
const loading = ref(false)
const jobs = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const statusFilter = ref('')
const statusOptions = getTrainingStatusOptions()

// 自动刷新定时器
let refreshTimer = null

// 加载训练任务列表
const loadJobs = async () => {
  loading.value = true
  try {
    const params = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value,
      status_filter: statusFilter.value || undefined
    }
    const response = await getTrainingJobs(params)
    jobs.value = response.items || []
    total.value = response.total || 0
  } catch (error) {
    console.error('加载训练任务失败:', error)
    ElMessage.error('加载训练任务失败')
  } finally {
    loading.value = false
  }
}

// 计算训练进度
const calculateProgress = (job) => {
  if (!job.current_epoch || !job.config?.training_params?.epochs) {
    return 0
  }
  return calculateTrainingProgress(job.current_epoch, job.config.training_params.epochs)
}

// 获取进度条颜色
const getProgressColor = (status) => {
  if (status === 'training') return '#409EFF'
  if (status === 'completed') return '#67C23A'
  if (status === 'failed') return '#F56C6C'
  return '#E6A23C'
}

// 获取状态图标
const getStatusIcon = (status) => {
  const iconMap = {
    pending: Clock,
    preparing: Loading,
    training: Cpu,
    completed: CircleCheck,
    failed: CircleClose,
    cancelled: CircleClose
  }
  return iconMap[status] || Clock
}

// 获取状态背景类
const getStatusBgClass = (status) => {
  const classMap = {
    pending: 'bg-gray-400',
    preparing: 'bg-orange-400',
    training: 'bg-blue-500',
    completed: 'bg-green-500',
    failed: 'bg-red-500',
    cancelled: 'bg-gray-500'
  }
  return classMap[status] || 'bg-gray-400'
}

// 获取基础模型标签
const getBaseModelLabel = (model) => {
  if (!model) return '-'
  return model.replace('.pt', '').toUpperCase()
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 跳转到创建页面
const goToCreate = () => {
  router.push('/admin/training/create')
}

// 跳转到监控页面
const goToMonitor = (jobId) => {
  router.push(`/admin/training/${jobId}`)
}

// 下载模型
const downloadModel = (job) => {
  if (job.model_path) {
    // 实际应用中应该调用下载 API
    ElMessage.info('模型下载功能开发中')
  }
}

// 删除任务
const handleDelete = async (job) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除训练任务"${job.name}"吗？此操作将删除所有训练数据和模型，且不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )

    await deleteTrainingJob(job.id)
    ElMessage.success('删除成功')
    await loadJobs()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除任务失败:', error)
      ElMessage.error('删除任务失败')
    }
  }
}

// 启动自动刷新（每10秒）
const startAutoRefresh = () => {
  refreshTimer = setInterval(async () => {
    // 如果有正在训练的任务，静默刷新
    if (jobs.value.some(j => ['training', 'preparing', 'pending'].includes(j.status))) {
      const params = {
        skip: (currentPage.value - 1) * pageSize.value,
        limit: pageSize.value,
        status_filter: statusFilter.value || undefined
      }
      try {
        const response = await getTrainingJobs(params)
        jobs.value = response.items || []
        total.value = response.total || 0
      } catch (error) {
        // 静默失败
      }
    }
  }, 10000)
}

// 生命周期
onMounted(() => {
  loadJobs()
  startAutoRefresh()
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
})
</script>

<style scoped>
.card-hover {
  background: white;
  border-radius: var(--radius-lg, 12px);
  padding: 1.5rem;
  box-shadow: var(--shadow-soft, 0 2px 12px rgba(10, 46, 91, 0.08));
  transition: all var(--duration-normal, 0.2s) var(--ease-out, ease-out);
}

.card-hover:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-medium, 0 4px 20px rgba(10, 46, 91, 0.12));
}

.animate-fade-in {
  animation: fadeIn 0.3s ease-in-out;
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
</style>
