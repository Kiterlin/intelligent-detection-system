/**
 * 检测相关 API
 */
import request from '@/utils/request'

// ==================== 图片检测 ====================

/**
 * 图片检测（同步）
 * @param {FormData} formData - 包含 file, model_id, confidence_threshold, iou_threshold
 */
export function detectImage(formData) {
  return request({
    url: '/detect/image',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// ==================== 视频检测 ====================

/**
 * 视频检测（异步）
 * @param {FormData} formData - 包含 file, model_id, confidence_threshold, iou_threshold
 */
export function detectVideo(formData) {
  return request({
    url: '/detect/video',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 查询视频检测任务状态
 * @param {string} taskId - Celery任务ID
 */
export function getTaskStatus(taskId) {
  return request({
    url: `/detect/status/${taskId}`,
    method: 'get'
  })
}

// ==================== 检测历史 ====================

/**
 * 获取检测历史列表
 * @param {Object} params - 查询参数 {skip, limit, input_type, status}
 */
export function getDetectionHistory(params) {
  return request({
    url: '/detect/history',
    method: 'get',
    params
  })
}

/**
 * 获取检测历史详情
 * @param {number} id - 检测历史ID
 */
export function getDetectionDetail(id) {
  return request({
    url: `/detect/history/${id}`,
    method: 'get'
  })
}

/**
 * 删除检测历史
 * @param {number} id - 检测历史ID
 */
export function deleteDetection(id) {
  return request({
    url: `/detect/history/${id}`,
    method: 'delete'
  })
}

/**
 * 下载检测结果
 * @param {number} id - 检测历史ID
 * @returns {string} 下载URL
 */
export function getDownloadUrl(id) {
  // 返回完整的下载URL
  const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'
  return `${baseURL}/detect/download/${id}`
}

/**
 * 下载检测结果文件（图片/视频）
 * @param {number} id - 检测历史ID
 * @returns {Promise} 下载的 Blob 数据
 */
export function downloadResultFile(id) {
  return request({
    url: `/detect/download/${id}/result`,
    method: 'get',
    responseType: 'blob'
  })
}

/**
 * 下载检测报告（TXT文档）
 * @param {number} id - 检测历史ID
 * @returns {Promise} 下载的 Blob 数据
 */
export function downloadReport(id) {
  return request({
    url: `/detect/download/${id}/report`,
    method: 'get',
    responseType: 'blob'
  })
}

/**
 * 下载全部（ZIP压缩包）
 * @param {number} id - 检测历史ID
 * @returns {Promise} 下载的 Blob 数据
 */
export function downloadAll(id) {
  return request({
    url: `/detect/download/${id}/all`,
    method: 'get',
    responseType: 'blob'
  })
}

/**
 * 下载检测结果文件（携带认证）- 保留用于兼容
 * @param {number} id - 检测历史ID
 * @returns {Promise} 下载的 Blob 数据
 */
export function downloadDetectionResult(id) {
  return downloadResultFile(id)
}

// ==================== 统计数据 ====================

/**
 * 获取用户检测统计数据
 */
export function getDetectionStats() {
  return request({
    url: '/detect/stats',
    method: 'get'
  })
}

// ==================== 模型列表 ====================

/**
 * 获取可用的活动模型列表（普通用户可访问）
 */
export function getActiveModels() {
  return request({
    url: '/detect/models',
    method: 'get'
  })
}

// ==================== 仪表盘 ====================

/**
 * 获取用户仪表盘统计数据
 * @returns {Promise} 仪表盘数据
 */
export function getDashboardStats() {
  return request({
    url: '/detect/dashboard',
    method: 'get'
  })
}
