/**
 * 数据集相关 API
 */
import request from '@/utils/request'

// ==================== 数据集 CRUD ====================

/**
 * 创建数据集
 * @param {Object} data - 数据集信息 {name, description}
 */
export function createDataset(data) {
  return request({
    url: '/datasets',
    method: 'post',
    data
  })
}

/**
 * 获取数据集列表
 * @param {Object} params - 查询参数 {skip, limit, search}
 */
export function getDatasets(params) {
  return request({
    url: '/datasets',
    method: 'get',
    params
  })
}

/**
 * 获取数据集详情（包含文件列表）
 * @param {number} datasetId - 数据集ID
 */
export function getDatasetDetail(datasetId) {
  return request({
    url: `/datasets/${datasetId}`,
    method: 'get'
  })
}

/**
 * 更新数据集信息
 * @param {number} datasetId - 数据集ID
 * @param {Object} data - 更新数据 {name, description}
 */
export function updateDataset(datasetId, data) {
  return request({
    url: `/datasets/${datasetId}`,
    method: 'put',
    data
  })
}

/**
 * 删除数据集
 * @param {number} datasetId - 数据集ID
 */
export function deleteDataset(datasetId) {
  return request({
    url: `/datasets/${datasetId}`,
    method: 'delete'
  })
}

// ==================== 文件管理 ====================

/**
 * 上传文件到数据集
 * @param {number} datasetId - 数据集ID
 * @param {FormData} formData - 包含 files 数组
 */
export function uploadFiles(datasetId, formData) {
  return request({
    url: `/datasets/${datasetId}/files`,
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    // 上传进度回调
    onUploadProgress: formData.onUploadProgress
  })
}

/**
 * 获取数据集文件列表
 * @param {number} datasetId - 数据集ID
 * @param {Object} params - 查询参数 {skip, limit}
 */
export function getDatasetFiles(datasetId, params) {
  return request({
    url: `/datasets/${datasetId}/files`,
    method: 'get',
    params
  })
}

// ==================== 批量检测 ====================

/**
 * 启动批量检测任务
 * @param {number} datasetId - 数据集ID
 * @param {Object} data - 检测参数 {model_id, confidence_threshold, iou_threshold}
 */
export function startBatchDetection(datasetId, data) {
  return request({
    url: `/datasets/${datasetId}/batch-detect`,
    method: 'post',
    data
  })
}

/**
 * 获取批量任务状态
 * @param {number} jobId - 批量任务ID
 */
export function getBatchJobStatus(jobId) {
  return request({
    url: `/datasets/batch-jobs/${jobId}`,
    method: 'get'
  })
}

/**
 * 获取批量任务列表
 * @param {Object} params - 查询参数 {skip, limit, status}
 */
export function getBatchJobs(params) {
  return request({
    url: '/datasets/batch-jobs',
    method: 'get',
    params
  })
}

// ==================== 工具函数 ====================

/**
 * 格式化文件大小
 * @param {number} bytes - 字节数
 * @returns {string} 格式化后的大小
 */
export function formatFileSize(bytes) {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

/**
 * 格式化批量任务状态
 * @param {string} status - 状态值
 * @returns {Object} {type, label}
 */
export function formatBatchJobStatus(status) {
  const statusMap = {
    pending: { type: 'info', label: '等待中' },
    running: { type: 'warning', label: '运行中' },
    completed: { type: 'success', label: '已完成' },
    failed: { type: 'danger', label: '失败' },
    cancelled: { type: 'info', label: '已取消' }
  }
  return statusMap[status] || { type: 'info', label: status }
}
