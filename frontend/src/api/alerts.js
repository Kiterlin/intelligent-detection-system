/**
 * 告警系统相关 API
 */
import request from '@/utils/request'

// ==================== 告警规则 CRUD ====================

/**
 * 创建告警规则
 * @param {Object} data - 规则信息 {name, description, is_active, conditions, actions}
 */
export function createAlertRule(data) {
  return request({
    url: '/alerts',
    method: 'post',
    data
  })
}

/**
 * 获取告警规则列表
 * @param {Object} params - 查询参数 {skip, limit, is_active, search}
 */
export function getAlertRules(params) {
  return request({
    url: '/alerts',
    method: 'get',
    params
  })
}

/**
 * 获取告警规则详情
 * @param {number} ruleId - 规则ID
 */
export function getAlertRule(ruleId) {
  return request({
    url: `/alerts/${ruleId}`,
    method: 'get'
  })
}

/**
 * 更新告警规则
 * @param {number} ruleId - 规则ID
 * @param {Object} data - 更新数据 {name, description, conditions, actions, is_active}
 */
export function updateAlertRule(ruleId, data) {
  return request({
    url: `/alerts/${ruleId}`,
    method: 'put',
    data
  })
}

/**
 * 删除告警规则
 * @param {number} ruleId - 规则ID
 */
export function deleteAlertRule(ruleId) {
  return request({
    url: `/alerts/${ruleId}`,
    method: 'delete'
  })
}

/**
 * 切换告警规则启用状态
 * @param {number} ruleId - 规则ID
 * @param {boolean} isActive - 是否启用
 */
export function toggleAlertRule(ruleId, isActive) {
  return request({
    url: `/alerts/${ruleId}/toggle`,
    method: 'patch',
    data: { is_active: isActive }
  })
}

// ==================== 告警日志 ====================

/**
 * 获取告警日志列表
 * @param {Object} params - 查询参数 {skip, limit, rule_id, status}
 */
export function getAlertLogs(params) {
  return request({
    url: '/alerts/logs',
    method: 'get',
    params
  })
}

// ==================== 辅助函数 ====================

/**
 * 格式化告警状态
 * @param {string} status - 状态值
 */
export function formatAlertStatus(status) {
  const statusMap = {
    success: { text: '成功', type: 'success' },
    failed: { text: '失败', type: 'danger' },
    partial: { text: '部分成功', type: 'warning' }
  }
  return statusMap[status] || { text: status, type: 'info' }
}

/**
 * 格式化告警条件为易读文本
 * @param {Object} conditions - 条件对象
 */
export function formatConditions(conditions) {
  const parts = []

  if (conditions.target_classes && conditions.target_classes.length > 0) {
    parts.push(`目标类别: ${conditions.target_classes.join(', ')}`)
  } else {
    parts.push('目标类别: 所有')
  }

  if (conditions.min_count) {
    parts.push(`最小数量: ${conditions.min_count}`)
  }

  if (conditions.min_confidence) {
    parts.push(`最小置信度: ${(conditions.min_confidence * 100).toFixed(0)}%`)
  }

  if (conditions.dataset_id) {
    parts.push(`数据集ID: ${conditions.dataset_id}`)
  }

  return parts.join(' | ')
}

/**
 * 格式化告警动作为易读文本
 * @param {Object} actions - 动作对象
 */
export function formatActions(actions) {
  const parts = []

  if (actions.email && actions.email.enabled) {
    const count = actions.email.recipients ? actions.email.recipients.length : 0
    parts.push(`邮件通知 (${count}人)`)
  }

  if (actions.webhook && actions.webhook.enabled) {
    parts.push('Webhook通知')
  }

  return parts.length > 0 ? parts.join(', ') : '无'
}
