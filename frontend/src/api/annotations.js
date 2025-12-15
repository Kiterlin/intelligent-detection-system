/**
 * 数据标注相关 API
 */
import request from '@/utils/request'

// ==================== 标注任务管理 ====================

/**
 * 创建标注任务
 * @param {Object} data - 任务数据 {name, description, labels, dataset_id?, detection_record_ids?}
 */
export function createAnnotationTask(data) {
  return request({
    url: '/annotations/tasks',
    method: 'post',
    data
  })
}

/**
 * 获取标注任务列表
 * @param {Object} params - 查询参数 {skip, limit, status, created_by_me}
 */
export function getAnnotationTasks(params) {
  return request({
    url: '/annotations/tasks',
    method: 'get',
    params
  })
}

/**
 * 获取标注任务详情
 * @param {number} taskId - 任务ID
 */
export function getAnnotationTask(taskId) {
  return request({
    url: `/annotations/tasks/${taskId}`,
    method: 'get'
  })
}

/**
 * 更新标注任务
 * @param {number} taskId - 任务ID
 * @param {Object} data - 更新数据
 */
export function updateAnnotationTask(taskId, data) {
  return request({
    url: `/annotations/tasks/${taskId}`,
    method: 'put',
    data
  })
}

/**
 * 删除标注任务
 * @param {number} taskId - 任务ID
 */
export function deleteAnnotationTask(taskId) {
  return request({
    url: `/annotations/tasks/${taskId}`,
    method: 'delete'
  })
}

/**
 * 获取任务统计信息
 * @param {number} taskId - 任务ID
 */
export function getTaskStatistics(taskId) {
  return request({
    url: `/annotations/tasks/${taskId}/statistics`,
    method: 'get'
  })
}

/**
 * 从检测结果导入预标注
 * @param {number} taskId - 任务ID
 * @param {Array} detectionRecordIds - 检测记录ID数组
 */
export function importDetectionsAsAnnotations(taskId, detectionRecordIds) {
  return request({
    url: `/annotations/tasks/${taskId}/import-detections`,
    method: 'post',
    data: { detection_record_ids: detectionRecordIds }
  })
}

// ==================== 标注记录管理 ====================

/**
 * 获取任务的标注列表
 * @param {number} taskId - 任务ID
 * @param {Object} params - 查询参数 {skip, limit}
 */
export function getAnnotations(taskId, params) {
  return request({
    url: `/annotations/tasks/${taskId}/annotations`,
    method: 'get',
    params
  })
}

/**
 * 创建标注
 * @param {number} taskId - 任务ID
 * @param {Object} data - 标注数据 {image_url, annotations}
 */
export function createAnnotation(taskId, data) {
  return request({
    url: `/annotations/tasks/${taskId}/annotations`,
    method: 'post',
    data
  })
}

/**
 * 获取标注详情
 * @param {number} annotationId - 标注ID
 */
export function getAnnotation(annotationId) {
  return request({
    url: `/annotations/${annotationId}`,
    method: 'get'
  })
}

/**
 * 更新标注
 * @param {number} annotationId - 标注ID
 * @param {Object} data - 更新数据
 */
export function updateAnnotation(annotationId, data) {
  return request({
    url: `/annotations/${annotationId}`,
    method: 'put',
    data
  })
}

/**
 * 删除标注
 * @param {number} annotationId - 标注ID
 */
export function deleteAnnotation(annotationId) {
  return request({
    url: `/annotations/${annotationId}`,
    method: 'delete'
  })
}

// ==================== 导出管理 ====================

/**
 * 创建导出任务
 * @param {number} taskId - 任务ID
 * @param {string} format - 导出格式 (yolo/coco/label_studio)
 */
export function createExportTask(taskId, format) {
  return request({
    url: `/annotations/tasks/${taskId}/exports`,
    method: 'post',
    data: { format }
  })
}

/**
 * 获取导出任务列表
 * @param {number} taskId - 任务ID
 */
export function getExportTasks(taskId) {
  return request({
    url: `/annotations/tasks/${taskId}/exports`,
    method: 'get'
  })
}

/**
 * 获取导出任务详情
 * @param {number} exportId - 导出ID
 */
export function getExportTask(exportId) {
  return request({
    url: `/annotations/exports/${exportId}`,
    method: 'get'
  })
}

/**
 * 下载导出文件
 * @param {number} exportId - 导出ID
 */
export function downloadExport(exportId) {
  return request({
    url: `/annotations/exports/${exportId}/download`,
    method: 'get',
    responseType: 'blob'
  })
}

// ==================== 辅助函数 ====================

/**
 * 格式化任务状态
 * @param {string} status - 状态值
 */
export function formatTaskStatus(status) {
  const statusMap = {
    pending: { text: '待处理', type: 'info', icon: 'clock' },
    in_progress: { text: '进行中', type: 'warning', icon: 'loading' },
    completed: { text: '已完成', type: 'success', icon: 'circle-check' },
    archived: { text: '已归档', type: 'info', icon: 'finished' }
  }
  return statusMap[status] || { text: status, type: 'info', icon: 'question' }
}

/**
 * 格式化导出状态
 * @param {string} status - 状态值
 */
export function formatExportStatus(status) {
  const statusMap = {
    pending: { text: '等待中', type: 'info', icon: 'clock' },
    processing: { text: '处理中', type: 'warning', icon: 'loading' },
    completed: { text: '已完成', type: 'success', icon: 'circle-check' },
    failed: { text: '失败', type: 'danger', icon: 'circle-close' }
  }
  return statusMap[status] || { text: status, type: 'info', icon: 'question' }
}

/**
 * 格式化导出格式
 * @param {string} format - 格式值
 */
export function formatExportFormat(format) {
  const formatMap = {
    yolo: { text: 'YOLO 格式', icon: 'files', color: '#409EFF' },
    coco: { text: 'COCO 格式', icon: 'document', color: '#67C23A' },
    label_studio: { text: 'Label Studio JSON', icon: 'document-copy', color: '#E6A23C' }
  }
  return formatMap[format] || { text: format, icon: 'document', color: '#909399' }
}

/**
 * 获取任务状态选项（用于筛选）
 */
export function getTaskStatusOptions() {
  return [
    { value: '', label: '全部状态' },
    { value: 'pending', label: '待处理' },
    { value: 'in_progress', label: '进行中' },
    { value: 'completed', label: '已完成' },
    { value: 'archived', label: '已归档' }
  ]
}

/**
 * 获取导出格式选项
 */
export function getExportFormatOptions() {
  return [
    { value: 'yolo', label: 'YOLO 格式 - 用于 YOLOv8 训练' },
    { value: 'coco', label: 'COCO 格式 - 通用目标检测格式' },
    { value: 'label_studio', label: 'Label Studio JSON - 原始标注格式' }
  ]
}

/**
 * 触发文件下载
 * @param {Blob} blob - 文件Blob对象
 * @param {string} filename - 文件名
 */
export function triggerDownload(blob, filename) {
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)
}

/**
 * 下载导出文件并保存
 * @param {number} exportId - 导出ID
 * @param {string} format - 导出格式
 * @param {string} taskName - 任务名称
 */
export async function downloadAndSaveExport(exportId, format, taskName) {
  try {
    const response = await downloadExport(exportId)
    const extension = format === 'label_studio' ? 'json' : 'zip'
    const filename = `${taskName}_${format}_${exportId}.${extension}`
    triggerDownload(response, filename)
    return { success: true }
  } catch (error) {
    console.error('下载导出文件失败:', error)
    return { success: false, error }
  }
}

/**
 * 计算标注进度
 * @param {Object} statistics - 统计数据
 */
export function calculateProgress(statistics) {
  if (!statistics || !statistics.total_images) {
    return 0
  }
  const annotatedImages = statistics.annotated_images || 0
  const totalImages = statistics.total_images || 1
  return Math.round((annotatedImages / totalImages) * 100)
}

/**
 * 验证标注任务参数
 * @param {Object} data - 任务数据
 */
export function validateTaskData(data) {
  const errors = []

  if (!data.name || data.name.trim() === '') {
    errors.push('任务名称不能为空')
  }

  if (!data.labels || data.labels.length === 0) {
    errors.push('至少需要添加一个类别标签')
  }

  // 必须选择数据集或检测记录
  if (!data.dataset_id && (!data.detection_record_ids || data.detection_record_ids.length === 0)) {
    errors.push('必须选择数据集或检测记录作为数据源')
  }

  return errors
}
