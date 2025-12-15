<template>
  <div class="min-h-screen bg-light-gray">
    <!-- 页面标题 -->
    <div class="bg-gradient-ocean py-12 mb-8">
      <div class="container-custom">
        <div class="flex items-center mb-2">
          <el-button
            text
            class="text-white hover:text-white/80 mr-4"
            @click="$router.back()"
          >
            <el-icon :size="20">
              <ArrowLeft />
            </el-icon>
          </el-button>
          <h1 class="text-3xl md:text-4xl font-bold text-white">
            {{ dataset?.name || '数据集详情' }}
          </h1>
        </div>
        <p v-if="dataset?.description" class="text-white/80 ml-12">
          {{ dataset.description }}
        </p>
      </div>
    </div>

    <div v-loading="loading" class="container-custom pb-12">
      <!-- 数据集统计卡片 -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div class="card-hover bg-gradient-to-br from-blue-500 to-blue-600 text-white">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-blue-100 text-sm mb-1">文件数量</p>
              <h3 class="text-3xl font-bold">{{ dataset?.file_count || 0 }}</h3>
            </div>
            <div class="w-14 h-14 bg-white/20 rounded-lg flex items-center justify-center">
              <el-icon :size="28">
                <Document />
              </el-icon>
            </div>
          </div>
        </div>

        <div class="card-hover bg-gradient-to-br from-purple-500 to-purple-600 text-white">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-purple-100 text-sm mb-1">总大小</p>
              <h3 class="text-2xl font-bold">{{ formatFileSize(dataset?.total_size || 0) }}</h3>
            </div>
            <div class="w-14 h-14 bg-white/20 rounded-lg flex items-center justify-center">
              <el-icon :size="28">
                <FolderOpened />
              </el-icon>
            </div>
          </div>
        </div>

        <div class="card-hover bg-gradient-to-br from-green-500 to-green-600 text-white">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-green-100 text-sm mb-1">创建时间</p>
              <h3 class="text-lg font-bold">{{ formatDate(dataset?.created_at) }}</h3>
            </div>
            <div class="w-14 h-14 bg-white/20 rounded-lg flex items-center justify-center">
              <el-icon :size="28">
                <Clock />
              </el-icon>
            </div>
          </div>
        </div>
      </div>

      <!-- 文件上传区域 -->
      <div class="card-hover mb-8">
        <h3 class="text-lg font-bold text-deep-blue mb-4 flex items-center">
          <el-icon class="mr-2" :size="20">
            <Upload />
          </el-icon>
          上传文件
        </h3>

        <el-upload
          ref="uploadRef"
          class="upload-demo"
          drag
          :action="uploadAction"
          :headers="uploadHeaders"
          :data="uploadData"
          :on-success="handleUploadSuccess"
          :on-error="handleUploadError"
          :before-upload="beforeUpload"
          :on-progress="handleUploadProgress"
          multiple
          :limit="50"
          :file-list="fileList"
        >
          <el-icon class="el-icon--upload" :size="64">
            <UploadFilled />
          </el-icon>
          <div class="el-upload__text">
            拖拽文件到此处或 <em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">
              支持图片（jpg/png）和视频（mp4/avi/mov），单次最多上传50个文件
            </div>
          </template>
        </el-upload>

        <!-- 上传进度 -->
        <div v-if="uploading" class="mt-4">
          <el-progress :percentage="uploadProgress" />
        </div>
      </div>

      <!-- 批量检测区域 -->
      <div class="card-hover mb-8">
        <h3 class="text-lg font-bold text-deep-blue mb-4 flex items-center">
          <el-icon class="mr-2" :size="20">
            <DataAnalysis />
          </el-icon>
          批量检测
        </h3>

        <div class="flex items-end gap-4">
          <div class="flex-1">
            <el-form :model="batchForm" label-width="120px">
              <el-form-item label="选择模型">
                <el-select
                  v-model="batchForm.model_id"
                  placeholder="请选择检测模型"
                  class="w-full"
                >
                  <el-option
                    v-for="model in models"
                    :key="model.id"
                    :label="model.name"
                    :value="model.id"
                  />
                </el-select>
              </el-form-item>

              <el-form-item label="置信度阈值">
                <el-slider
                  v-model="batchForm.confidence_threshold"
                  :min="0"
                  :max="1"
                  :step="0.05"
                  :marks="{ 0: '0', 0.25: '0.25', 0.5: '0.5', 0.75: '0.75', 1: '1' }"
                  show-input
                />
              </el-form-item>

              <el-form-item label="IOU阈值">
                <el-slider
                  v-model="batchForm.iou_threshold"
                  :min="0"
                  :max="1"
                  :step="0.05"
                  :marks="{ 0: '0', 0.25: '0.25', 0.5: '0.5', 0.75: '0.75', 1: '1' }"
                  show-input
                />
              </el-form-item>
            </el-form>
          </div>

          <el-button
            type="primary"
            size="large"
            :disabled="!dataset || dataset.file_count === 0 || !batchForm.model_id"
            :loading="startingBatch"
            @click="handleStartBatch"
          >
            启动批量检测
          </el-button>
        </div>
      </div>

      <!-- 文件列表 -->
      <div class="card-hover">
        <h3 class="text-lg font-bold text-deep-blue mb-4 flex items-center">
          <el-icon class="mr-2" :size="20">
            <List />
          </el-icon>
          文件列表 ({{ files.length }})
        </h3>

        <el-table
          v-loading="filesLoading"
          :data="files"
          stripe
          style="width: 100%"
        >
          <el-table-column prop="filename" label="文件名" min-width="200">
            <template #default="{ row }">
              <div class="flex items-center">
                <el-icon
                  :size="16"
                  :class="row.file_type === 'image' ? 'text-blue-500' : 'text-purple-500'"
                  class="mr-2"
                >
                  <Picture v-if="row.file_type === 'image'" />
                  <VideoCamera v-else />
                </el-icon>
                <span class="truncate">{{ row.filename }}</span>
              </div>
            </template>
          </el-table-column>

          <el-table-column prop="file_type" label="类型" width="100">
            <template #default="{ row }">
              <el-tag :type="row.file_type === 'image' ? 'primary' : 'success'">
                {{ row.file_type === 'image' ? '图片' : '视频' }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column prop="file_size" label="大小" width="120">
            <template #default="{ row }">
              {{ formatFileSize(row.file_size) }}
            </template>
          </el-table-column>

          <el-table-column prop="uploaded_at" label="上传时间" width="180">
            <template #default="{ row }">
              {{ formatDate(row.uploaded_at) }}
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  ArrowLeft,
  Document,
  FolderOpened,
  Clock,
  Upload,
  UploadFilled,
  DataAnalysis,
  List,
  Picture,
  VideoCamera
} from '@element-plus/icons-vue'
import {
  getDatasetDetail,
  startBatchDetection,
  formatFileSize
} from '@/api/dataset'
import { getActiveModels } from '@/api/detect'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

// 数据集信息
const dataset = ref(null)
const files = ref([])
const loading = ref(false)
const filesLoading = ref(false)

// 模型列表
const models = ref([])

// 上传相关
const uploadRef = ref(null)
const fileList = ref([])
const uploading = ref(false)
const uploadProgress = ref(0)

const datasetId = computed(() => parseInt(route.params.id))

const uploadAction = computed(() => {
  const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
  return `${baseURL}/api/v1/datasets/${datasetId.value}/files`
})

const uploadHeaders = computed(() => {
  return {
    Authorization: `Bearer ${userStore.token}`
  }
})

const uploadData = reactive({})

// 批量检测表单
const batchForm = reactive({
  model_id: null,
  confidence_threshold: 0.25,
  iou_threshold: 0.45
})
const startingBatch = ref(false)

// 加载数据集详情
const loadDataset = async () => {
  loading.value = true
  try {
    const res = await getDatasetDetail(datasetId.value)
    dataset.value = res
    files.value = res.files || []
  } catch (error) {
    console.error('加载数据集失败:', error)
    ElMessage.error('加载数据集失败')
    router.back()
  } finally {
    loading.value = false
  }
}

// 加载模型列表
const loadModels = async () => {
  try {
    const res = await getActiveModels()
    models.value = res.models || []

    // 默认选择第一个激活的模型
    if (models.value.length > 0 && !batchForm.model_id) {
      batchForm.model_id = models.value[0].id
    }
  } catch (error) {
    console.error('加载模型列表失败:', error)
  }
}

// 上传前检查
const beforeUpload = (file) => {
  const imageTypes = ['image/jpeg', 'image/png', 'image/bmp', 'image/webp']
  const videoTypes = ['video/mp4', 'video/avi', 'video/quicktime', 'video/x-matroska']
  const allowedTypes = [...imageTypes, ...videoTypes]

  if (!allowedTypes.includes(file.type)) {
    ElMessage.error('仅支持图片（JPG/PNG）和视频（MP4/AVI/MOV）文件')
    return false
  }

  const maxSize = 200 * 1024 * 1024 // 200MB
  if (file.size > maxSize) {
    ElMessage.error('文件大小不能超过 200MB')
    return false
  }

  return true
}

// 上传进度
const handleUploadProgress = (event) => {
  uploading.value = true
  uploadProgress.value = Math.round(event.percent)
}

// 上传成功
const handleUploadSuccess = (response, file) => {
  ElMessage.success(`上传成功: ${file.name}`)
  uploading.value = false
  uploadProgress.value = 0
  loadDataset() // 重新加载数据集
}

// 上传失败
const handleUploadError = (error, file) => {
  console.error('上传失败:', error)
  ElMessage.error(`上传失败: ${file.name}`)
  uploading.value = false
  uploadProgress.value = 0
}

// 启动批量检测
const handleStartBatch = async () => {
  if (!batchForm.model_id) {
    ElMessage.warning('请选择检测模型')
    return
  }

  if (dataset.value.file_count === 0) {
    ElMessage.warning('数据集中没有文件')
    return
  }

  startingBatch.value = true
  try {
    await startBatchDetection(datasetId.value, batchForm)
    ElMessage.success('批量检测任务已启动')
    router.push('/batch-jobs')
  } catch (error) {
    console.error('启动批量检测失败:', error)
    ElMessage.error(error.response?.data?.detail || '启动批量检测失败')
  } finally {
    startingBatch.value = false
  }
}

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 页面加载时获取数据
onMounted(() => {
  loadDataset()
  loadModels()
})
</script>

<style scoped>
.upload-demo {
  width: 100%;
}

:deep(.el-upload-dragger) {
  width: 100%;
}
</style>
