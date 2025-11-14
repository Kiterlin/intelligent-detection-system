/**
 * 检测状态管理
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  detectImage as detectImageApi,
  detectVideo as detectVideoApi,
  getTaskStatus,
  getDetectionHistory,
  getDetectionDetail,
  deleteDetection,
  getDetectionStats,
  getActiveModels
} from '@/api/detect'
import { ElMessage } from 'element-plus'

export const useDetectionStore = defineStore('detection', () => {
  // ==================== 状态 ====================

  // 检测中状态
  const detecting = ref(false)

  // 当前检测结果
  const currentResult = ref(null)

  // 视频任务ID和状态
  const videoTaskId = ref(null)
  const videoTaskStatus = ref(null)
  const pollingInterval = ref(null)

  // 检测历史列表
  const historyList = ref([])
  const historyTotal = ref(0)
  const historyLoading = ref(false)

  // 统计数据
  const stats = ref({
    totalDetections: 0,
    todayDetections: 0,
    totalObjects: 0
  })

  // 可用模型列表
  const modelList = ref([])
  const modelsLoading = ref(false)

  // ==================== 计算属性 ====================

  const hasResult = computed(() => !!currentResult.value)
  const isVideoProcessing = computed(() =>
    videoTaskStatus.value === 'PENDING' ||
    videoTaskStatus.value === 'PROCESSING'
  )

  // ==================== 图片检测 ====================

  /**
   * 图片检测
   * @param {File} file - 图片文件
   * @param {number} modelId - 模型ID
   * @param {number} confidenceThreshold - 置信度阈值
   * @param {number} iouThreshold - IOU阈值
   */
  async function detectImage(file, modelId, confidenceThreshold = 0.5, iouThreshold = 0.45) {
    try {
      detecting.value = true
      currentResult.value = null

      const formData = new FormData()
      formData.append('file', file)
      formData.append('model_id', modelId)
      formData.append('confidence_threshold', confidenceThreshold)
      formData.append('iou_threshold', iouThreshold)

      const data = await detectImageApi(formData)
      // 确保结果包含 id 字段（用于下载）
      currentResult.value = {
        id: data.detection_id,
        ...data
      }

      ElMessage.success('图片检测完成')
      return data
    } catch (error) {
      console.error('Image detection failed:', error)
      ElMessage.error(error.message || '图片检测失败')
      throw error
    } finally {
      detecting.value = false
    }
  }

  // ==================== 视频检测 ====================

  /**
   * 视频检测
   * @param {File} file - 视频文件
   * @param {number} modelId - 模型ID
   * @param {number} confidenceThreshold - 置信度阈值
   * @param {number} iouThreshold - IOU阈值
   */
  async function detectVideo(file, modelId, confidenceThreshold = 0.5, iouThreshold = 0.45) {
    try {
      detecting.value = true
      currentResult.value = null
      videoTaskStatus.value = 'PENDING'

      const formData = new FormData()
      formData.append('file', file)
      formData.append('model_id', modelId)
      formData.append('confidence_threshold', confidenceThreshold)
      formData.append('iou_threshold', iouThreshold)

      const data = await detectVideoApi(formData)
      videoTaskId.value = data.task_id

      ElMessage.success('视频上传成功，开始处理...')

      // 开始轮询任务状态
      startPolling()

      return data
    } catch (error) {
      console.error('Video detection failed:', error)
      ElMessage.error(error.message || '视频上传失败')
      detecting.value = false
      videoTaskStatus.value = 'FAILED'
      throw error
    }
  }

  /**
   * 开始轮询任务状态
   */
  function startPolling() {
    if (pollingInterval.value) {
      clearInterval(pollingInterval.value)
    }

    pollingInterval.value = setInterval(async () => {
      if (videoTaskId.value) {
        await checkTaskStatus()
      }
    }, 2000) // 每2秒轮询一次
  }

  /**
   * 检查任务状态
   */
  async function checkTaskStatus() {
    try {
      const data = await getTaskStatus(videoTaskId.value)
      videoTaskStatus.value = data.status

      if (data.status === 'COMPLETED') {
        // 任务完成，合并 detection_id 到结果中
        currentResult.value = {
          id: data.detection_id,  // 添加 id 字段用于下载
          detection_id: data.detection_id,
          ...data.result
        }
        stopPolling()
        detecting.value = false
        ElMessage.success('视频检测完成')
      } else if (data.status === 'FAILED') {
        // 任务失败
        stopPolling()
        detecting.value = false
        ElMessage.error(data.error || '视频检测失败')
      }
    } catch (error) {
      console.error('Check task status failed:', error)
      stopPolling()
      detecting.value = false
    }
  }

  /**
   * 停止轮询
   */
  function stopPolling() {
    if (pollingInterval.value) {
      clearInterval(pollingInterval.value)
      pollingInterval.value = null
    }
  }

  /**
   * 取消视频检测
   */
  function cancelVideoDetection() {
    stopPolling()
    videoTaskId.value = null
    videoTaskStatus.value = null
    detecting.value = false
    ElMessage.info('已取消检测')
  }

  // ==================== 检测历史 ====================

  /**
   * 获取检测历史
   * @param {Object} params - 查询参数 {page, page_size, input_type, status}
   */
  async function fetchHistory(params = {}) {
    try {
      historyLoading.value = true
      const data = await getDetectionHistory(params)
      historyList.value = data.histories || []
      historyTotal.value = data.total || 0
      return data
    } catch (error) {
      console.error('Fetch history failed:', error)
      ElMessage.error('获取检测历史失败：' + (error.response?.data?.detail || error.message))
      throw error
    } finally {
      historyLoading.value = false
    }
  }

  /**
   * 删除检测历史
   * @param {number} id - 检测历史ID
   */
  async function removeDetection(id) {
    try {
      await deleteDetection(id)
      // 不在这里显示成功消息，由调用方决定
      // 刷新列表
      await fetchHistory()
    } catch (error) {
      console.error('Delete detection failed:', error)
      throw error
    }
  }

  // ==================== 统计数据 ====================

  /**
   * 获取统计数据
   */
  async function fetchStats() {
    try {
      const data = await getDetectionStats()
      stats.value = data
      return data
    } catch (error) {
      console.error('Fetch stats failed:', error)
      throw error
    }
  }

  // ==================== 模型列表 ====================

  /**
   * 获取可用模型列表
   */
  async function fetchModels() {
    try {
      modelsLoading.value = true
      const data = await getActiveModels()
      modelList.value = data.models || []
      return data
    } catch (error) {
      console.error('Fetch models failed:', error)
      ElMessage.error('获取模型列表失败：' + (error.response?.data?.detail || error.message))
      throw error
    } finally {
      modelsLoading.value = false
    }
  }

  // ==================== 重置状态 ====================

  /**
   * 重置当前检测状态
   */
  function resetDetection() {
    detecting.value = false
    currentResult.value = null
    videoTaskId.value = null
    videoTaskStatus.value = null
    stopPolling()
  }

  return {
    // 状态
    detecting,
    currentResult,
    videoTaskId,
    videoTaskStatus,
    historyList,
    historyTotal,
    historyLoading,
    stats,
    modelList,
    modelsLoading,

    // 计算属性
    hasResult,
    isVideoProcessing,

    // 方法
    detectImage,
    detectVideo,
    checkTaskStatus,
    cancelVideoDetection,
    fetchHistory,
    removeDetection,
    fetchStats,
    fetchModels,
    resetDetection
  }
})
