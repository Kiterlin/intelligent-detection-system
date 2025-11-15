/**
 * 报告生成相关 API
 */
import request from '@/utils/request'

// ==================== 报告 CRUD ====================

/**
 * 创建报告生成任务
 * @param {Object} data - 报告配置 {name, report_type, parameters}
 */
export function createReport(data) {
  return request({
    url: '/reports',
    method: 'post',
    data
  })
}

/**
 * 获取报告列表
 * @param {Object} params - 查询参数 {skip, limit, status_filter}
 */
export function getReports(params) {
  return request({
    url: '/reports',
    method: 'get',
    params
  })
}

/**
 * 获取报告详情
 * @param {number} reportId - 报告ID
 */
export function getReport(reportId) {
  return request({
    url: `/reports/${reportId}`,
    method: 'get'
  })
}

/**
 * 下载报告文件
 * @param {number} reportId - 报告ID
 * @param {string} format - 文件格式 (pdf/html)
 */
export function downloadReport(reportId, format) {
  return request({
    url: `/reports/${reportId}/download/${format}`,
    method: 'get',
    responseType: 'blob'
  })
}

/**
 * 删除报告
 * @param {number} reportId - 报告ID
 */
export function deleteReport(reportId) {
  return request({
    url: `/reports/${reportId}`,
    method: 'delete'
  })
}

// ==================== 辅助函数 ====================

/**
 * 格式化报告类型
 * @param {string} type - 报告类型
 */
export function formatReportType(type) {
  const typeMap = {
    summary: { text: '概要报告', icon: 'document', color: '#409EFF' },
    detailed: { text: '详细报告', icon: 'document-copy', color: '#67C23A' },
    comparison: { text: '对比报告', icon: 'data-analysis', color: '#E6A23C' }
  }
  return typeMap[type] || { text: type, icon: 'document', color: '#909399' }
}

/**
 * 格式化报告状态
 * @param {string} status - 状态值
 */
export function formatReportStatus(status) {
  const statusMap = {
    pending: { text: '等待中', type: 'info', icon: 'clock' },
    generating: { text: '生成中', type: 'warning', icon: 'loading' },
    completed: { text: '已完成', type: 'success', icon: 'circle-check' },
    failed: { text: '生成失败', type: 'danger', icon: 'circle-close' }
  }
  return statusMap[status] || { text: status, type: 'info', icon: 'question' }
}

/**
 * 获取报告类型选项
 */
export function getReportTypeOptions() {
  return [
    { value: 'summary', label: '概要报告 - 1页快速概览' },
    { value: 'detailed', label: '详细报告 - 完整分析报告' },
    { value: 'comparison', label: '对比报告 - 多模型性能对比' }
  ]
}

/**
 * 获取报告状态选项（用于筛选）
 */
export function getReportStatusOptions() {
  return [
    { value: '', label: '全部状态' },
    { value: 'pending', label: '等待中' },
    { value: 'generating', label: '生成中' },
    { value: 'completed', label: '已完成' },
    { value: 'failed', label: '生成失败' }
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
 * 下载报告并保存
 * @param {number} reportId - 报告ID
 * @param {string} reportName - 报告名称
 * @param {string} format - 文件格式
 */
export async function downloadAndSaveReport(reportId, reportName, format) {
  try {
    const response = await downloadReport(reportId, format)
    const filename = `${reportName}_${reportId}.${format}`
    triggerDownload(response, filename)
    return { success: true }
  } catch (error) {
    console.error('下载报告失败:', error)
    return { success: false, error }
  }
}

/**
 * 验证报告参数
 * @param {string} reportType - 报告类型
 * @param {Object} parameters - 报告参数
 */
export function validateReportParameters(reportType, parameters) {
  const errors = []

  // 检查必需的参数
  if (!parameters) {
    errors.push('缺少报告参数')
    return errors
  }

  // 对比报告需要至少2个模型
  if (reportType === 'comparison') {
    const modelIds = parameters.filters?.model_ids || []
    if (modelIds.length < 2) {
      errors.push('对比报告至少需要选择2个模型')
    }
  }

  // 检查时间范围
  if (parameters.time_range) {
    const { start, end } = parameters.time_range
    if (start && end && new Date(start) > new Date(end)) {
      errors.push('开始时间不能晚于结束时间')
    }
  }

  return errors
}
