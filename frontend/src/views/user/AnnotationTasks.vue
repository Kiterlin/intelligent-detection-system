<template>
  <div class="min-h-screen bg-light-gray">
    <!-- 页面头部 -->
    <PageHeader
      title="数据标注"
      subtitle="管理和组织数据标注任务，为模型训练准备高质量数据"
    >
      <template #actions>
        <el-button
          type="primary"
          :icon="Plus"
          size="large"
          @click="goToCreate"
        >
          创建标注任务
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
          @change="loadTasks"
          style="width: 150px"
        >
          <el-option
            v-for="option in statusOptions"
            :key="option.value"
            :label="option.label"
            :value="option.value"
          />
        </el-select>

        <!-- 我的任务筛选 -->
        <el-checkbox v-model="createdByMe" @change="loadTasks" border>
          仅显示我创建的
        </el-checkbox>

        <div class="flex-1"></div>

        <!-- 返回首页按钮 -->
        <el-button :icon="HomeFilled" @click="goToHome">
          返回首页
        </el-button>

        <!-- 刷新按钮 -->
        <el-button :icon="Refresh" @click="loadTasks">
          刷新
        </el-button>
      </div>

      <!-- 任务列表 -->
      <div v-loading="loading">
        <!-- 空状态 -->
        <EmptyState
          v-if="tasks.length === 0 && !loading"
          icon="Folder"
          title="还没有标注任务"
          description="创建第一个标注任务，开始为模型训练准备数据"
        >
          <template #actions>
            <el-button type="primary" :icon="Plus" @click="goToCreate">
              创建标注任务
            </el-button>
          </template>
        </EmptyState>

        <!-- 任务卡片 -->
        <div v-else class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div
            v-for="task in tasks"
            :key="task.id"
            class="card-hover animate-fade-in cursor-pointer"
            @click="goToDetail(task.id)"
          >
            <!-- 任务头部 -->
            <div class="flex items-start justify-between mb-4">
              <div class="flex items-start flex-1">
                <div class="w-12 h-12 rounded-lg bg-gradient-ocean flex items-center justify-center mr-4 flex-shrink-0">
                  <el-icon :size="24" class="text-white">
                    <Edit />
                  </el-icon>
                </div>
                <div class="flex-1 min-w-0">
                  <h3 class="text-lg font-bold text-deep-blue mb-1">
                    {{ task.name }}
                  </h3>
                  <p v-if="task.description" class="text-sm text-gray-500 mb-2 line-clamp-2">
                    {{ task.description }}
                  </p>
                  <div class="flex items-center gap-2">
                    <StatusTag :status="task.status" size="small" />
                  </div>
                </div>
              </div>
            </div>

            <!-- 标签列表 -->
            <div class="mb-4">
              <div class="text-xs text-gray-500 mb-2">类别标签:</div>
              <div class="flex flex-wrap gap-2">
                <el-tag
                  v-for="(label, index) in task.labels.slice(0, 5)"
                  :key="index"
                  size="small"
                  effect="plain"
                >
                  {{ label }}
                </el-tag>
                <el-tag
                  v-if="task.labels.length > 5"
                  size="small"
                  type="info"
                  effect="plain"
                >
                  +{{ task.labels.length - 5 }}
                </el-tag>
              </div>
            </div>

            <!-- 进度条 -->
            <div class="mb-4">
              <div class="flex justify-between text-sm mb-1">
                <span class="text-gray-500">标注进度</span>
                <span class="text-deep-blue font-medium">{{ calculateProgress(task) }}%</span>
              </div>
              <el-progress
                :percentage="calculateProgress(task)"
                :color="getProgressColor(calculateProgress(task))"
                :stroke-width="8"
                :show-text="false"
              />
            </div>

            <!-- 统计信息 -->
            <div class="grid grid-cols-3 gap-4 mb-4 p-3 bg-gray-50 rounded-lg text-sm">
              <div class="text-center">
                <div class="text-gray-500 text-xs mb-1">总图片</div>
                <div class="text-deep-blue font-bold">{{ task.total_images || 0 }}</div>
              </div>
              <div class="text-center">
                <div class="text-gray-500 text-xs mb-1">已标注</div>
                <div class="text-green-600 font-bold">{{ task.annotated_images || 0 }}</div>
              </div>
              <div class="text-center">
                <div class="text-gray-500 text-xs mb-1">对象数</div>
                <div class="text-blue-600 font-bold">{{ task.total_annotations || 0 }}</div>
              </div>
            </div>

            <!-- 底部信息和操作 -->
            <div class="flex items-center justify-between text-sm text-gray-500">
              <div class="flex items-center gap-4">
                <span>创建时间: {{ formatDate(task.created_at) }}</span>
              </div>
              <div class="flex gap-2" @click.stop>
                <el-button
                  v-if="task.label_studio_url"
                  size="small"
                  type="primary"
                  :icon="Link"
                  @click="openLabelStudio(task)"
                >
                  在线标注
                </el-button>
                <el-dropdown @command="handleCommand($event, task)">
                  <el-button size="small" :icon="MoreFilled">
                    更多
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item command="edit" :icon="Edit">
                        编辑
                      </el-dropdown-item>
                      <el-dropdown-item command="export" :icon="Download">
                        导出数据
                      </el-dropdown-item>
                      <el-dropdown-item command="delete" :icon="Delete" divided>
                        删除任务
                      </el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
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
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="loadTasks"
            @current-change="loadTasks"
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
  Edit,
  Delete,
  Download,
  Link,
  MoreFilled,
  HomeFilled
} from '@element-plus/icons-vue'
import PageHeader from '@/components/common/PageHeader.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import StatusTag from '@/components/common/StatusTag.vue'
import {
  getAnnotationTasks,
  deleteAnnotationTask,
  getTaskStatusOptions
} from '@/api/annotations'

const router = useRouter()

// 数据
const loading = ref(false)
const tasks = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const statusFilter = ref('')
const createdByMe = ref(false)
const statusOptions = getTaskStatusOptions()

// 自动刷新定时器
let refreshTimer = null

// 加载任务列表
const normalizeLabels = (labels, classLabels) => {
  if (Array.isArray(labels) && labels.length > 0) return labels
  if (Array.isArray(classLabels) && classLabels.length > 0) return classLabels
  return []
}

const loadTasks = async () => {
  loading.value = true
  try {
    const params = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value,
      status: statusFilter.value || undefined,
      created_by_me: createdByMe.value
    }
    const response = await getAnnotationTasks(params)
    tasks.value = (response.items || []).map(task => ({
      ...task,
      labels: normalizeLabels(task.labels, task.class_labels)
    }))
    total.value = response.total || 0
  } catch (error) {
    console.error('加载任务列表失败:', error)
    ElMessage.error('加载任务列表失败')
  } finally {
    loading.value = false
  }
}

// 计算进度百分比
const calculateProgress = (task) => {
  if (!task.total_images || task.total_images === 0) {
    return 0
  }
  const annotatedImages = task.annotated_images || 0
  return Math.round((annotatedImages / task.total_images) * 100)
}

// 获取进度条颜色
const getProgressColor = (percentage) => {
  if (percentage === 0) return '#E5E7EB'
  if (percentage < 30) return '#F56C6C'
  if (percentage < 70) return '#E6A23C'
  if (percentage < 100) return '#409EFF'
  return '#67C23A'
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

// 返回首页
const goToHome = () => {
  router.push('/')
}

// 跳转到创建页面
const goToCreate = () => {
  router.push('/annotations/create')
}

// 跳转到详情页面
const goToDetail = (taskId) => {
  router.push(`/annotations/tasks/${taskId}`)
}

// 打开 Label Studio
const openLabelStudio = (task) => {
  if (task.label_studio_url) {
    window.open(task.label_studio_url, '_blank')
  } else {
    ElMessage.warning('Label Studio URL 未配置')
  }
}

// 处理下拉菜单命令
const canManageTask = (task) => {
  const currentUserId = userStore.userInfo?.id
  return userStore.isAdmin || (currentUserId && task.created_by === currentUserId)
}

const handleCommand = async (command, task) => {
  switch (command) {
    case 'edit':
      goToDetail(task.id)
      break
    case 'export':
      router.push(`/annotations/tasks/${task.id}?tab=exports`)
      break
    case 'delete':
      await handleDelete(task)
      break
  }
}

// 删除任务
const handleDelete = async (task) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除标注任务"${task.name}"吗？此操作将删除所有相关的标注数据，且不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )

    await deleteAnnotationTask(task.id)
    ElMessage.success('删除成功')
    await loadTasks()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除任务失败:', error)
      ElMessage.error('删除任务失败')
    }
  }
}

// 启动自动刷新（每30秒）
const startAutoRefresh = () => {
  refreshTimer = setInterval(() => {
    // 静默刷新，不显示 loading
    const params = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value,
      status: statusFilter.value || undefined,
      created_by_me: createdByMe.value
    }
    getAnnotationTasks(params).then(response => {
      tasks.value = response.items || []
      total.value = response.total || 0
    }).catch(() => {
      // 静默失败
    })
  }, 30000)
}

// 生命周期
onMounted(() => {
  loadTasks()
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

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
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
