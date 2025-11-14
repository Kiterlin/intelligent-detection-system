<template>
  <div class="min-h-screen bg-light-gray">
    <!-- 顶部导航栏 -->
    <nav class="bg-white shadow-soft">
      <div class="container-custom py-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-3">
            <div class="w-10 h-10 bg-gradient-ocean rounded-xl flex items-center justify-center">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
            </div>
            <h1 class="text-xl md:text-2xl font-bold text-deep-blue">目标检测</h1>
          </div>

          <el-dropdown trigger="click" @command="handleCommand">
            <button class="flex items-center space-x-2 px-4 py-2 rounded-lg hover:bg-gray-50 transition-colors">
              <div class="w-8 h-8 bg-gradient-sunset rounded-full flex items-center justify-center">
                <el-icon class="text-white"><User /></el-icon>
              </div>
              <span class="hidden md:inline text-gray-700 font-medium">{{ authStore.userInfo?.username }}</span>
              <el-icon class="text-gray-500"><ArrowDown /></el-icon>
            </button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="home">
                  <el-icon><HomeFilled /></el-icon>
                  返回首页
                </el-dropdown-item>
                <el-dropdown-item v-if="authStore.isAdmin" command="admin">
                  <el-icon><Setting /></el-icon>
                  管理后台
                </el-dropdown-item>
                <el-dropdown-item command="history">
                  <el-icon><Document /></el-icon>
                  检测历史
                </el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </nav>

    <!-- 主要内容区 -->
    <div class="container-custom py-6 md:py-8">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- 左侧：上传和配置 -->
        <div class="space-y-6">
          <!-- 文件上传卡片 -->
          <div class="card animate-slide-up">
            <div class="flex items-center justify-between mb-6">
              <h2 class="text-lg font-bold text-deep-blue flex items-center">
                <svg class="w-5 h-5 mr-2 text-bright-cyan" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                文件上传
              </h2>
            </div>

            <!-- 文件上传区 -->
            <el-upload
              ref="uploadRef"
              v-model:file-list="uploadFileList"
              class="upload-area-custom"
              drag
              :auto-upload="false"
              :limit="1"
              :on-change="handleFileChange"
              :on-exceed="handleExceed"
              :accept="acceptedFileTypes"
            >
              <div class="upload-content">
                <div class="upload-icon-wrapper">
                  <el-icon class="upload-icon"><UploadFilled /></el-icon>
                </div>
                <p class="upload-title">将文件拖到此处，或点击上传</p>
                <p class="upload-tip">
                  支持 JPG, PNG, BMP (最大20MB) | MP4, AVI, MOV (最大500MB)
                </p>
              </div>
            </el-upload>

            <!-- 文件信息 -->
            <transition name="slide-down">
              <div v-if="selectedFile" class="mt-4 p-4 bg-blue-50 border-l-4 border-bright-cyan rounded-lg">
                <div class="flex items-start">
                  <svg class="w-5 h-5 text-bright-cyan mt-0.5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <div class="flex-1">
                    <p class="font-semibold text-deep-blue">{{ selectedFile.name }}</p>
                    <p class="text-sm text-gray-600 mt-1">
                      类型: {{ fileType }} | 大小: {{ formatFileSize(selectedFile.size) }}
                    </p>
                  </div>
                </div>
              </div>
            </transition>
          </div>

          <!-- 配置卡片 -->
          <div class="card animate-slide-up" style="animation-delay: 0.1s">
            <h2 class="text-lg font-bold text-deep-blue mb-6 flex items-center">
              <svg class="w-5 h-5 mr-2 text-bright-cyan" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
              </svg>
              检测配置
            </h2>

            <!-- 模型选择 -->
            <div class="mb-6">
              <label class="label">选择检测模型</label>
              <el-select
                v-model="selectedModelId"
                placeholder="请选择模型"
                :loading="detectionStore.modelsLoading"
                size="large"
                class="w-full"
              >
                <el-option
                  v-for="model in detectionStore.modelList"
                  :key="model.id"
                  :label="`${model.name} (${model.version})`"
                  :value="model.id"
                >
                  <div class="flex items-center justify-between">
                    <span>{{ model.name }}</span>
                    <span class="text-xs text-gray-500">{{ model.version }}</span>
                  </div>
                </el-option>
              </el-select>
            </div>

            <!-- 置信度阈值 -->
            <div class="mb-6">
              <div class="flex items-center justify-between mb-3">
                <label class="label mb-0">置信度阈值: {{ confidenceThreshold }}</label>
                <el-tooltip
                  content="控制检测结果的最小置信度，值越高过滤越严格，建议0.25-0.5"
                  placement="top"
                >
                  <el-icon class="text-gray-400 cursor-help"><QuestionFilled /></el-icon>
                </el-tooltip>
              </div>
              <el-slider
                v-model="confidenceThreshold"
                :min="0"
                :max="1"
                :step="0.05"
                :marks="{ 0: '0', 0.25: '0.25', 0.5: '0.5', 0.75: '0.75', 1: '1' }"
              />
            </div>

            <!-- IOU阈值 -->
            <div class="mb-6">
              <div class="flex items-center justify-between mb-3">
                <label class="label mb-0">IOU阈值: {{ iouThreshold }}</label>
                <el-tooltip
                  content="非极大值抑制(NMS)的IOU阈值，用于去除重叠检测框，建议0.4-0.5"
                  placement="top"
                >
                  <el-icon class="text-gray-400 cursor-help"><QuestionFilled /></el-icon>
                </el-tooltip>
              </div>
              <el-slider
                v-model="iouThreshold"
                :min="0"
                :max="1"
                :step="0.05"
                :marks="{ 0: '0', 0.25: '0.25', 0.5: '0.5', 0.75: '0.75', 1: '1' }"
              />
            </div>

            <!-- 操作按钮 -->
            <div class="flex flex-col sm:flex-row gap-3">
              <button
                :disabled="!canDetect"
                :class="[
                  'flex-1 btn-primary py-3 text-base font-semibold',
                  detectionStore.detecting && 'opacity-75'
                ]"
                @click="handleDetect"
              >
                <span v-if="!detectionStore.detecting" class="flex items-center justify-center">
                  <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                  开始检测
                </span>
                <span v-else class="flex items-center justify-center">
                  <svg class="animate-spin h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  检测中...
                </span>
              </button>
              <button
                v-if="detectionStore.isVideoProcessing"
                class="flex-1 bg-red-500 text-white py-3 rounded-lg font-semibold hover:bg-red-600 transition-colors"
                @click="handleCancelVideo"
              >
                取消检测
              </button>
              <button
                class="flex-1 btn-ghost py-3 text-base font-semibold"
                @click="handleReset"
              >
                重置
              </button>
            </div>
          </div>
        </div>

        <!-- 右侧：结果展示 -->
        <div class="space-y-6">
          <div class="card animate-slide-up" style="animation-delay: 0.2s">
            <h2 class="text-lg font-bold text-deep-blue mb-6 flex items-center">
              <svg class="w-5 h-5 mr-2 text-bright-cyan" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
              </svg>
              检测结果
            </h2>

            <!-- 无结果提示 -->
            <div v-if="!detectionStore.hasResult && !detectionStore.detecting" class="flex flex-col items-center justify-center py-16">
              <div class="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mb-4">
                <svg class="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
              <p class="text-gray-500 text-center">暂无检测结果<br>请上传文件并开始检测</p>
            </div>

            <!-- 检测中 -->
            <div v-if="detectionStore.detecting" class="flex flex-col items-center justify-center py-16">
              <LoadingSpinner size="large" :text="fileType === 'image' ? '正在检测图片，请稍候...' : '正在处理视频，请稍候...'" />
              <p v-if="fileType === 'video'" class="text-sm text-bright-cyan mt-4">
                状态: {{ videoStatusText }}
              </p>
              <el-progress
                v-if="fileType === 'video'"
                :percentage="videoProgress"
                :indeterminate="videoProgress < 100"
                :stroke-width="12"
                :format="progressFormat"
                class="w-full mt-4"
              />
            </div>

            <!-- 检测结果 -->
            <div v-if="detectionStore.hasResult" class="space-y-6 animate-fade-in">
              <!-- 结果图片/视频 -->
              <div class="result-media-wrapper">
                <img
                  v-if="fileType === 'image'"
                  :src="resultImageUrl"
                  alt="检测结果"
                  class="result-image"
                  loading="lazy"
                >
                <video
                  v-if="fileType === 'video'"
                  :src="resultVideoUrl"
                  controls
                  class="result-video"
                  preload="metadata"
                />
              </div>

              <!-- 检测统计 -->
              <div class="grid grid-cols-2 gap-4">
                <div class="stat-card">
                  <div class="stat-icon bg-green-100">
                    <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div>
                    <p class="stat-label">检测对象数</p>
                    <p class="stat-value">{{ detectionStore.currentResult.detected_objects_count || 0 }}</p>
                  </div>
                </div>
                <div class="stat-card">
                  <div class="stat-icon bg-blue-100">
                    <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div>
                    <p class="stat-label">处理时间</p>
                    <p class="stat-value">{{ (detectionStore.currentResult.processing_time || 0).toFixed(2) }}s</p>
                  </div>
                </div>
              </div>

              <!-- 检测对象列表 -->
              <div v-if="detectionObjects.length > 0">
                <h3 class="text-sm font-semibold text-deep-blue mb-3">检测到的对象</h3>
                <div class="max-h-64 overflow-y-auto">
                  <el-table :data="detectionObjects" size="small" stripe>
                    <el-table-column prop="class_name" label="类别" width="120" />
                    <el-table-column prop="confidence" label="置信度" width="100">
                      <template #default="scope">
                        <el-tag type="success" size="small">{{ (scope.row.confidence * 100).toFixed(1) }}%</el-tag>
                      </template>
                    </el-table-column>
                    <el-table-column label="位置">
                      <template #default="scope">
                        <span class="text-xs text-gray-500">[{{ scope.row.bbox.join(', ') }}]</span>
                      </template>
                    </el-table-column>
                  </el-table>
                </div>
              </div>

              <!-- 下载按钮组 -->
              <el-dropdown trigger="click" class="w-full" @command="handleDownloadCommand">
                <button class="w-full btn-secondary py-3 text-base font-semibold">
                  <svg class="w-5 h-5 mr-2 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                  下载检测结果
                  <el-icon class="ml-2"><ArrowDown /></el-icon>
                </button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="result">
                      <div class="flex items-center space-x-2">
                        <svg class="w-4 h-4 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                        <span>下载结果文件</span>
                      </div>
                    </el-dropdown-item>
                    <el-dropdown-item command="report">
                      <div class="flex items-center space-x-2">
                        <svg class="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                        <span>下载检测报告</span>
                      </div>
                    </el-dropdown-item>
                    <el-dropdown-item command="all" divided>
                      <div class="flex items-center space-x-2">
                        <svg class="w-4 h-4 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
                        </svg>
                        <span>下载全部(ZIP)</span>
                      </div>
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useDetectionStore } from '@/stores/detection'
import { downloadResultFile, downloadReport, downloadAll } from '@/api/detect'
import { downloadFile, getFilenameFromContentDisposition } from '@/utils/helpers'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  User,
  ArrowDown,
  Setting,
  HomeFilled,
  Document,
  UploadFilled,
  QuestionFilled
} from '@element-plus/icons-vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'

const router = useRouter()
const authStore = useAuthStore()
const detectionStore = useDetectionStore()

// 上传相关
const uploadRef = ref(null)
const uploadFileList = ref([])
const selectedFile = ref(null)
const selectedModelId = ref(null)
const confidenceThreshold = ref(0.5)
const iouThreshold = ref(0.45)

// 文件类型限制
const acceptedFileTypes = 'image/jpeg,image/jpg,image/png,image/bmp,video/mp4,video/avi,video/quicktime'

// 计算属性
const fileType = computed(() => {
  if (!selectedFile.value) return null
  return selectedFile.value.type.startsWith('image/') ? 'image' : 'video'
})

const canDetect = computed(() => {
  return selectedFile.value && selectedModelId.value && !detectionStore.detecting
})

const videoStatusText = computed(() => {
  const status = detectionStore.videoTaskStatus
  const statusMap = {
    PENDING: '等待处理',
    PROCESSING: '处理中',
    COMPLETED: '已完成',
    FAILED: '处理失败'
  }
  return statusMap[status] || '未知状态'
})

const videoProgress = computed(() => {
  const status = detectionStore.videoTaskStatus
  if (status === 'PENDING') return 20
  if (status === 'PROCESSING') return 60
  if (status === 'COMPLETED') return 100
  return 0
})

const resultImageUrl = computed(() => {
  if (!detectionStore.currentResult || !detectionStore.currentResult.output_file_path) {
    return null
  }
  const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'
  return baseURL.replace('/api/v1', '') + '/' + detectionStore.currentResult.output_file_path
})

const resultVideoUrl = computed(() => {
  if (!detectionStore.currentResult || !detectionStore.currentResult.output_file_path) {
    return null
  }
  const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'
  return baseURL.replace('/api/v1', '') + '/' + detectionStore.currentResult.output_file_path
})

const detectionObjects = computed(() => {
  if (!detectionStore.currentResult) {
    return []
  }
  if (detectionStore.currentResult.objects) {
    return detectionStore.currentResult.objects
  }
  if (detectionStore.currentResult.result_json) {
    const results = detectionStore.currentResult.result_json
    return results.detections || []
  }
  return []
})

const progressFormat = (percentage) => {
  return percentage === 100 ? '完成' : `${percentage}%`
}

// 生命周期
onMounted(async () => {
  await detectionStore.fetchModels()
  if (detectionStore.modelList.length === 1) {
    selectedModelId.value = detectionStore.modelList[0].id
  }
})

// 文件处理
function handleFileChange(file) {
  selectedFile.value = file.raw
  const maxSize = file.raw.type.startsWith('image/') ? 20 * 1024 * 1024 : 500 * 1024 * 1024
  if (file.size > maxSize) {
    ElMessage.error(
      `文件大小超出限制（${file.raw.type.startsWith('image/') ? '20MB' : '500MB'}）`
    )
    selectedFile.value = null
    uploadFileList.value = []
    uploadRef.value.clearFiles()
  }
}

function handleExceed() {
  ElMessage.warning('只能上传一个文件')
}

function formatFileSize(bytes) {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
}

// 检测操作
async function handleDetect() {
  if (!selectedFile.value || !selectedModelId.value) {
    ElMessage.warning('请选择文件和模型')
    return
  }

  try {
    if (fileType.value === 'image') {
      await detectionStore.detectImage(
        selectedFile.value,
        selectedModelId.value,
        confidenceThreshold.value,
        iouThreshold.value
      )
    } else {
      await detectionStore.detectVideo(
        selectedFile.value,
        selectedModelId.value,
        confidenceThreshold.value,
        iouThreshold.value
      )
    }
  } catch (error) {
    console.error('Detection error:', error)
  }
}

function handleCancelVideo() {
  ElMessageBox.confirm('确定要取消当前视频检测任务吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  })
    .then(() => {
      detectionStore.cancelVideoDetection()
    })
    .catch(() => {})
}

function handleReset() {
  selectedFile.value = null
  uploadFileList.value = []
  uploadRef.value?.clearFiles()
  detectionStore.resetDetection()
}

async function handleDownloadCommand(command) {
  if (!detectionStore.currentResult || !detectionStore.currentResult.id) {
    ElMessage.error('无法下载，结果不存在')
    return
  }

  try {
    ElMessage.info('正在准备下载...')
    let response

    switch (command) {
      case 'result':
        response = await downloadResultFile(detectionStore.currentResult.id)
        break
      case 'report':
        response = await downloadReport(detectionStore.currentResult.id)
        break
      case 'all':
        response = await downloadAll(detectionStore.currentResult.id)
        break
      default:
        ElMessage.error('未知的下载选项')
        return
    }

    // 从响应头获取文件名
    const contentDisposition = response.headers['content-disposition']
    const filename = getFilenameFromContentDisposition(contentDisposition)

    // 触发下载
    downloadFile(response.data, filename)
    ElMessage.success('下载成功')
  } catch (error) {
    console.error('Download error:', error)
    ElMessage.error('下载失败：' + (error.response?.data?.detail || error.message))
  }
}

// 导航操作
const handleCommand = (command) => {
  if (command === 'logout') {
    authStore.logout()
  } else if (command === 'home') {
    router.push('/')
  } else if (command === 'history') {
    router.push('/detection-history')
  } else if (command === 'admin') {
    router.push('/admin/dashboard')
  }
}
</script>

<style scoped>
/* 上传区域自定义样式 */
.upload-area-custom :deep(.el-upload-dragger) {
  @apply border-2 border-dashed border-gray-300 rounded-xl p-8 transition-all duration-300;
  @apply hover:border-bright-cyan hover:bg-blue-50;
}

.upload-area-custom :deep(.el-upload-dragger.is-dragover) {
  @apply border-bright-cyan bg-blue-50;
}

.upload-content {
  @apply flex flex-col items-center;
}

.upload-icon-wrapper {
  @apply w-16 h-16 bg-gradient-ocean rounded-full flex items-center justify-center mb-4;
}

.upload-icon {
  @apply text-4xl text-white;
}

.upload-title {
  @apply text-base font-semibold text-deep-blue mb-2;
}

.upload-tip {
  @apply text-sm text-gray-500;
}

/* 结果媒体包装器 */
.result-media-wrapper {
  @apply w-full bg-black rounded-xl overflow-hidden;
}

.result-image {
  @apply w-full h-auto max-h-96 object-contain;
}

.result-video {
  @apply w-full max-h-96;
}

/* 统计卡片 */
.stat-card {
  @apply flex items-center space-x-3 p-4 bg-gray-50 rounded-lg;
}

.stat-icon {
  @apply w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0;
}

.stat-label {
  @apply text-xs text-gray-500;
}

.stat-value {
  @apply text-xl font-bold text-deep-blue;
}

/* 动画 */
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease-out;
}

.slide-down-enter-from {
  transform: translateY(-10px);
  opacity: 0;
}

.slide-down-leave-to {
  transform: translateY(-10px);
  opacity: 0;
}
</style>
