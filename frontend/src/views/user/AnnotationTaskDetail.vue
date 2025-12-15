<template>
  <div class="min-h-screen bg-light-gray">
    <!--导航栏 -->
    <nav class="bg-white border-b sticky top-0 z-50 shadow-sm">
      <div class="container-custom py-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-4">
            <el-button :icon="ArrowLeft" @click="goBack" circle />
            <div>
              <h1 class="text-xl font-bold text-deep-blue">{{ task?.name || '加载中...' }}</h1>
              <div v-if="task" class="flex items-center gap-2 mt-1">
                <StatusTag :status="task.status" size="small" />
                <span class="text-sm text-gray-500">创建于 {{ formatDate(task.created_at) }}</span>
              </div>
            </div>
          </div>
          <div class="flex gap-2">
            <el-button
              v-if="task?.label_studio_url"
              type="primary"
              :icon="Link"
              @click="openLabelStudio"
            >
              打开 Label Studio
            </el-button>
            <el-dropdown @command="handleCommand">
              <el-button :icon="MoreFilled">
                更多操作
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="import" :icon="Upload">
                    导入检测结果
                  </el-dropdown-item>
                  <el-dropdown-item command="edit" :icon="Edit">
                    编辑任务
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
    </nav>

    <div class="container-custom py-8" v-loading="loading">
      <div v-if="loadError" class="bg-white rounded-lg shadow-sm p-10">
        <EmptyState
          icon="WarningFilled"
          :icon-size="64"
          :title="loadError"
          description="请返回标注任务列表后重试。"
        >
          <template #actions>
            <el-button type="primary" @click="goBack">
              返回列表
            </el-button>
          </template>
        </EmptyState>
      </div>
      <div v-else-if="task">
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          <!-- 统计卡片 -->
          <StatCard
            label="总图片数"
          :value="statistics.total_images || 0"
          :icon="PictureFilled"
          color="#409EFF"
        />
        <StatCard
          label="已标注图片"
          :value="statistics.annotated_images || 0"
          :icon="CircleCheck"
          color="#67C23A"
          :trend="calculateTrend()"
        />
        <StatCard
          label="标注对象数"
          :value="statistics.total_annotations || 0"
          :icon="CollectionTag"
          color="#E6A23C"
        />
      </div>

        <!-- 进度条 -->
        <div class="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div class="flex justify-between items-center mb-3">
            <h3 class="text-lg font-bold text-deep-blue">标注进度</h3>
            <span class="text-2xl font-bold text-deep-blue">{{ progress }}%</span>
          </div>
          <el-progress
            :percentage="progress"
            :color="getProgressColor(progress)"
            :stroke-width="12"
          />
        </div>

        <!-- 任务信息和标注数据 -->
        <div class="bg-white rounded-lg shadow-sm p-6">
          <el-tabs v-model="activeTab" type="border-card">
          <!-- 任务信息 -->
          <el-tab-pane label="任务信息" name="info">
            <div class="space-y-6">
              <!-- 基本信息 -->
              <div>
                <h3 class="text-lg font-bold text-deep-blue mb-4">基本信息</h3>
                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <div class="text-sm text-gray-500 mb-1">任务名称</div>
                    <div class="font-medium">{{ task.name }}</div>
                  </div>
                  <div>
                    <div class="text-sm text-gray-500 mb-1">任务状态</div>
                    <StatusTag :status="task.status" />
                  </div>
                  <div>
                    <div class="text-sm text-gray-500 mb-1">创建时间</div>
                    <div class="font-medium">{{ formatDate(task.created_at) }}</div>
                  </div>
                  <div>
                    <div class="text-sm text-gray-500 mb-1">更新时间</div>
                    <div class="font-medium">{{ formatDate(task.updated_at) }}</div>
                  </div>
                </div>
              </div>

              <!-- 任务描述 -->
              <div v-if="task.description">
                <h3 class="text-lg font-bold text-deep-blue mb-4">任务描述</h3>
                <p class="text-gray-700 whitespace-pre-wrap">{{ task.description }}</p>
              </div>

              <!-- 类别标签 -->
              <div>
                <h3 class="text-lg font-bold text-deep-blue mb-4">类别标签</h3>
                <div class="flex flex-wrap gap-2">
                  <el-tag
                    v-for="label in task.labels"
                    :key="label"
                    size="large"
                    effect="plain"
                  >
                    {{ label }}
                  </el-tag>
                </div>
              </div>

              <!-- Label Studio 链接 -->
              <div v-if="task.label_studio_url">
                <h3 class="text-lg font-bold text-deep-blue mb-4">在线标注</h3>
                <el-button type="primary" :icon="Link" @click="openLabelStudio">
                  打开 Label Studio 进行标注
                </el-button>
              </div>
            </div>
          </el-tab-pane>

          <!-- 标注列表 -->
          <el-tab-pane name="annotations">
            <template #label>
              <span>标注列表 ({{ annotations.length }})</span>
            </template>

            <div class="mb-4">
              <el-button :icon="Refresh" @click="loadAnnotations">
                刷新
              </el-button>
            </div>

            <!-- 空状态 -->
            <EmptyState
              v-if="annotations.length === 0 && !annotationsLoading"
              icon="DocumentCopy"
              title="还没有标注数据"
              description="在 Label Studio 中进行标注，或从检测结果导入预标注"
            >
              <template #actions>
                <el-button type="primary" :icon="Link" @click="openLabelStudio" v-if="task.label_studio_url">
                  开始标注
                </el-button>
              </template>
            </EmptyState>

            <!-- 标注表格 -->
            <el-table
              v-else
              :data="annotations"
              v-loading="annotationsLoading"
              stripe
            >
              <el-table-column prop="id" label="ID" width="80" />
              <el-table-column label="图片">
                <template #default="{ row }">
                  <div class="flex items-center gap-3">
                    <img
                      v-if="row.image_url"
                      :src="row.image_url"
                      class="w-16 h-16 object-cover rounded"
                      @error="handleImageError"
                    />
                    <span class="text-sm">{{ getImageName(row.image_url) }}</span>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="标注对象数" width="120">
                <template #default="{ row }">
                  <el-tag size="small">{{ row.annotations?.length || 0 }} 个</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="创建时间" width="180">
                <template #default="{ row }">
                  {{ formatDate(row.created_at) }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="150">
                <template #default="{ row }">
                  <el-button
                    size="small"
                    type="danger"
                    :icon="Delete"
                    @click="deleteAnnotation(row)"
                  >
                    删除
                  </el-button>
                </template>
              </el-table-column>
            </el-table>

            <!-- 分页 -->
            <div v-if="annotationsTotal > 0" class="mt-4 flex justify-center">
              <el-pagination
                v-model:current-page="annotationsPage"
                v-model:page-size="annotationsPageSize"
                :total="annotationsTotal"
                :page-sizes="[10, 20, 50]"
                layout="total, sizes, prev, pager, next"
                @size-change="loadAnnotations"
                @current-change="loadAnnotations"
              />
            </div>
          </el-tab-pane>

          <!-- 导出管理 -->
          <el-tab-pane name="exports">
            <template #label>
              <span>导出管理 ({{ exports.length }})</span>
            </template>

            <div class="mb-4">
              <el-button type="primary" :icon="Download" @click="showExportDialog = true">
                创建导出任务
              </el-button>
              <el-button :icon="Refresh" @click="loadExports">
                刷新
              </el-button>
            </div>

            <!-- 空状态 -->
            <EmptyState
              v-if="exports.length === 0 && !exportsLoading"
              icon="Download"
              title="还没有导出记录"
              description="创建导出任务，将标注数据导出为训练格式"
            >
              <template #actions>
                <el-button type="primary" :icon="Download" @click="showExportDialog = true">
                  创建导出任务
                </el-button>
              </template>
            </EmptyState>

            <!-- 导出表格 -->
            <el-table
              v-else
              :data="exports"
              v-loading="exportsLoading"
              stripe
            >
              <el-table-column prop="id" label="ID" width="80" />
              <el-table-column label="导出格式" width="180">
                <template #default="{ row }">
                  <el-tag :type="getFormatType(row.format)">
                    {{ getFormatLabel(row.format) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="状态" width="120">
                <template #default="{ row }">
                  <StatusTag :status="row.status" size="small" />
                </template>
              </el-table-column>
              <el-table-column label="创建时间" width="180">
                <template #default="{ row }">
                  {{ formatDate(row.created_at) }}
                </template>
              </el-table-column>
              <el-table-column label="操作">
                <template #default="{ row }">
                  <el-button
                    v-if="row.status === 'completed'"
                    size="small"
                    type="primary"
                    :icon="Download"
                    @click="downloadExportFile(row)"
                  >
                    下载
                  </el-button>
                  <el-tag v-else-if="row.status === 'processing'" type="warning" size="small">
                    <el-icon class="is-loading"><Loading /></el-icon>
                    处理中
                  </el-tag>
                  <el-tag v-else-if="row.status === 'failed'" type="danger" size="small">
                    导出失败
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
        </el-tabs>
        </div>
      </div>
      <div v-else class="bg-white rounded-lg shadow-sm p-10">
        <EmptyState
          icon="Loading"
          title="正在加载标注任务"
          description="请稍候..."
        />
      </div>
    </div>

    <!-- 创建导出对话框 -->
    <el-dialog
      v-model="showExportDialog"
      title="创建导出任务"
      width="500px"
    >
      <el-form :model="exportForm" label-width="100px">
        <el-form-item label="导出格式">
          <el-radio-group v-model="exportForm.format">
            <el-radio label="yolo">YOLO 格式</el-radio>
            <el-radio label="coco">COCO 格式</el-radio>
            <el-radio label="label_studio">Label Studio JSON</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showExportDialog = false">取消</el-button>
        <el-button type="primary" :loading="exportSubmitting" @click="submitExport">
          创建导出
        </el-button>
      </template>
    </el-dialog>

    <!-- 导入检测结果对话框 -->
    <el-dialog
      v-model="showImportDialog"
      title="导入检测结果"
      width="600px"
    >
      <el-form :model="importForm" label-width="120px">
        <el-form-item label="选择检测记录">
          <el-select
            v-model="importForm.detection_record_ids"
            multiple
            filterable
            placeholder="请选择检测记录"
            class="w-full"
          >
            <el-option
              v-for="record in availableDetections"
              :key="record.id"
              :label="`${record.image_name} - ${formatDate(record.created_at)}`"
              :value="record.id"
            />
          </el-select>
          <div class="text-xs text-gray-500 mt-2">
            已选择 {{ importForm.detection_record_ids.length }} 条记录
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showImportDialog = false">取消</el-button>
        <el-button type="primary" :loading="importSubmitting" @click="submitImport">
          导入预标注
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ArrowLeft,
  Link,
  Edit,
  Delete,
  Download,
  Upload,
  Refresh,
  MoreFilled,
  Loading,
  PictureFilled,
  CircleCheck,
  CollectionTag
} from '@element-plus/icons-vue'
import PageHeader from '@/components/common/PageHeader.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import StatusTag from '@/components/common/StatusTag.vue'
import StatCard from '@/components/common/StatCard.vue'
import {
  getAnnotationTask,
  getTaskStatistics,
  deleteAnnotationTask,
  getAnnotations,
  deleteAnnotation as deleteAnnotationAPI,
  importDetectionsAsAnnotations,
  getExportTasks,
  createExportTask,
  downloadAndSaveExport
} from '@/api/annotations'
import { getDetectionHistory } from '@/api/detect'

const router = useRouter()
const route = useRoute()

// 数据
const loading = ref(true)
const loadError = ref(null)
const task = ref(null)
const statistics = ref({})
const activeTab = ref('info')

// 标注列表
const annotationsLoading = ref(false)
const annotations = ref([])
const annotationsTotal = ref(0)
const annotationsPage = ref(1)
const annotationsPageSize = ref(10)

// 导出列表
const exportsLoading = ref(false)
const exports = ref([])

// 对话框
const showExportDialog = ref(false)
const showImportDialog = ref(false)
const exportSubmitting = ref(false)
const importSubmitting = ref(false)

const exportForm = reactive({
  format: 'yolo'
})

const importForm = reactive({
  detection_record_ids: []
})

const availableDetections = ref([])

// 定时刷新
let refreshTimer = null

// 计算进度
const progress = computed(() => {
  if (!statistics.value.total_images || statistics.value.total_images === 0) {
    return 0
  }
  const annotatedImages = statistics.value.annotated_images || 0
  return Math.round((annotatedImages / statistics.value.total_images) * 100)
})

// 计算趋势（示例：固定返回正值）
const calculateTrend = () => {
  // 实际应用中可以对比历史数据
  return null
}

// 获取进度条颜色
const getProgressColor = (percentage) => {
  if (percentage === 0) return '#E5E7EB'
  if (percentage < 30) return '#F56C6C'
  if (percentage < 70) return '#E6A23C'
  if (percentage < 100) return '#409EFF'
  return '#67C23A'
}

// 获取格式类型
const getFormatType = (format) => {
  const typeMap = {
    yolo: '',
    coco: 'success',
    label_studio: 'warning'
  }
  return typeMap[format] || ''
}

// 获取格式标签
const getFormatLabel = (format) => {
  const labelMap = {
    yolo: 'YOLO 格式',
    coco: 'COCO 格式',
    label_studio: 'Label Studio JSON'
  }
  return labelMap[format] || format
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString('zh-CN')
}

// 获取图片名称
const getImageName = (url) => {
  if (!url) return '-'
  return url.split('/').pop()
}

// 图片加载错误处理
const handleImageError = (e) => {
  e.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="100" height="100"%3E%3Crect fill="%23ddd" width="100" height="100"/%3E%3Ctext fill="%23999" x="50%25" y="50%25" text-anchor="middle" dy=".3em"%3E无法加载%3C/text%3E%3C/svg%3E'
}

// 加载任务详情
const loadTaskDetail = async () => {
  loading.value = true
  loadError.value = null
  try {
    const taskId = route.params.id
    const taskResponse = await getAnnotationTask(taskId)
    const normalizedLabels = Array.isArray(taskResponse.labels) && taskResponse.labels.length > 0
      ? taskResponse.labels
      : (taskResponse.class_labels || [])
    const labelStudioUrl = taskResponse.label_studio_project_url || taskResponse.label_studio_url || null
    task.value = {
      ...taskResponse,
      labels: normalizedLabels,
      label_studio_url: labelStudioUrl
    }
    statistics.value = await getTaskStatistics(taskId)

    // 根据 URL 参数切换标签页
    if (route.query.tab) {
      activeTab.value = route.query.tab
    }
  } catch (error) {
    console.error('加载任务详情失败:', error)
    loadError.value = error.response?.data?.detail || '加载任务详情失败'
    ElMessage.error(loadError.value)
    task.value = null
  } finally {
    loading.value = false
  }
}

// 加载标注列表
const loadAnnotations = async () => {
  annotationsLoading.value = true
  try {
    const taskId = route.params.id
    const params = {
      skip: (annotationsPage.value - 1) * annotationsPageSize.value,
      limit: annotationsPageSize.value
    }
    const response = await getAnnotations(taskId, params)
    annotations.value = response.items || []
    annotationsTotal.value = response.total || 0
  } catch (error) {
    console.error('加载标注列表失败:', error)
    ElMessage.error('加载标注列表失败')
  } finally {
    annotationsLoading.value = false
  }
}

// 加载导出列表
const loadExports = async () => {
  exportsLoading.value = true
  try {
    const taskId = route.params.id
    const response = await getExportTasks(taskId)
    exports.value = response || []
  } catch (error) {
    console.error('加载导出列表失败:', error)
    ElMessage.error('加载导出列表失败')
  } finally {
    exportsLoading.value = false
  }
}

// 打开 Label Studio
const openLabelStudio = () => {
  const url = task.value?.label_studio_url
  if (url) {
    window.open(url, '_blank')
  } else {
    ElMessage.warning('Label Studio URL 未配置')
  }
}

// 处理命令
const handleCommand = async (command) => {
  switch (command) {
    case 'import':
      await loadDetectionHistory()
      showImportDialog.value = true
      break
    case 'edit':
      // 跳转到编辑页面（暂未实现）
      ElMessage.info('编辑功能开发中')
      break
    case 'delete':
      await handleDelete()
      break
  }
}

// 删除任务
const handleDelete = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要删除任务"${task.value.name}"吗？此操作将删除所有相关的标注数据，且不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )

    await deleteAnnotationTask(route.params.id)
    ElMessage.success('删除成功')
    router.push('/annotations/tasks')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除任务失败:', error)
      ElMessage.error('删除任务失败')
    }
  }
}

// 删除标注
const deleteAnnotation = async (annotation) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这条标注吗？',
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await deleteAnnotationAPI(annotation.id)
    ElMessage.success('删除成功')
    await loadAnnotations()
    await loadTaskDetail()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除标注失败:', error)
      ElMessage.error('删除标注失败')
    }
  }
}

// 创建导出
const submitExport = async () => {
  exportSubmitting.value = true
  try {
    const taskId = route.params.id
    await createExportTask(taskId, exportForm.format)
    ElMessage.success('导出任务创建成功，正在后台处理')
    showExportDialog.value = false
    await loadExports()
  } catch (error) {
    console.error('创建导出失败:', error)
    ElMessage.error('创建导出失败')
  } finally {
    exportSubmitting.value = false
  }
}

// 下载导出文件
const downloadExportFile = async (exportTask) => {
  try {
    await downloadAndSaveExport(exportTask.id, exportTask.format, task.value.name)
    ElMessage.success('下载成功')
  } catch (error) {
    console.error('下载失败:', error)
    ElMessage.error('下载失败')
  }
}

// 加载检测历史
const loadDetectionHistory = async () => {
  try {
    const response = await getDetectionHistory({ page: 1, page_size: 100 })
    availableDetections.value = response.histories || []
  } catch (error) {
    console.error('加载检测历史失败:', error)
    ElMessage.error('加载检测历史失败')
  }
}

// 提交导入
const submitImport = async () => {
  if (importForm.detection_record_ids.length === 0) {
    ElMessage.warning('请选择至少一条检测记录')
    return
  }

  importSubmitting.value = true
  try {
    const taskId = route.params.id
    await importDetectionsAsAnnotations(taskId, importForm.detection_record_ids)
    ElMessage.success('导入成功')
    showImportDialog.value = false
    importForm.detection_record_ids = []
    await loadAnnotations()
    await loadTaskDetail()
  } catch (error) {
    console.error('导入失败:', error)
    ElMessage.error('导入失败')
  } finally {
    importSubmitting.value = false
  }
}

// 返回
const goBack = () => {
  router.push('/annotations/tasks')
}

// 自动刷新
const startAutoRefresh = () => {
  refreshTimer = setInterval(async () => {
    try {
      const taskId = route.params.id
      statistics.value = await getTaskStatistics(taskId)

      // 如果正在查看导出列表，刷新导出状态
      if (activeTab.value === 'exports' && exports.value.some(e => e.status === 'processing')) {
        await loadExports()
      }
    } catch (error) {
      // 静默失败
    }
  }, 10000)
}

// 生命周期
onMounted(async () => {
  await loadTaskDetail()
  if (loadError.value) {
    return
  }
  await loadAnnotations()
  await loadExports()
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
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 1rem;
}

:deep(.el-tabs__item) {
  font-size: 15px;
  font-weight: 500;
}

:deep(.el-table) {
  font-size: 14px;
}

:deep(.is-loading) {
  animation: rotating 2s linear infinite;
}

@keyframes rotating {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
