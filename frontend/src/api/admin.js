/**
 * 管理员API调用
 */
import request from '@/utils/request'

// ==================== 用户管理 ====================

/**
 * 获取用户列表
 */
export function getUserList(params) {
  return request({
    url: '/admin/users',
    method: 'get',
    params
  })
}

/**
 * 创建用户
 */
export function createUser(data) {
  return request({
    url: '/admin/users',
    method: 'post',
    data
  })
}

/**
 * 获取用户详情
 */
export function getUserDetail(id) {
  return request({
    url: `/admin/users/${id}`,
    method: 'get'
  })
}

/**
 * 更新用户
 */
export function updateUser(id, data) {
  return request({
    url: `/admin/users/${id}`,
    method: 'put',
    data
  })
}

/**
 * 删除用户
 */
export function deleteUser(id) {
  return request({
    url: `/admin/users/${id}`,
    method: 'delete'
  })
}

/**
 * 批量删除用户
 */
export function batchDeleteUsers(userIds) {
  return request({
    url: '/admin/users/batch/delete',
    method: 'post',
    data: { user_ids: userIds }
  })
}

/**
 * 批量更新用户状态
 */
export function batchUpdateUserStatus(userIds, isActive) {
  return request({
    url: '/admin/users/batch/update-status',
    method: 'post',
    data: {
      user_ids: userIds,
      is_active: isActive
    }
  })
}

/**
 * 重置用户密码（管理员）
 */
export function resetUserPassword(userId, newPassword) {
  return request({
    url: `/admin/users/${userId}/reset-password`,
    method: 'post',
    data: {
      new_password: newPassword
    }
  })
}

// ==================== 模型管理 ====================

/**
 * 上传模型
 */
export function uploadModel(formData) {
  return request({
    url: '/admin/models/upload',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 获取模型列表
 */
export function getModelList(params) {
  return request({
    url: '/admin/models',
    method: 'get',
    params
  })
}

/**
 * 获取模型详情
 */
export function getModelDetail(id) {
  return request({
    url: `/admin/models/${id}`,
    method: 'get'
  })
}

/**
 * 更新模型信息
 */
export function updateModel(id, data) {
  return request({
    url: `/admin/models/${id}`,
    method: 'put',
    data
  })
}

/**
 * 更新模型状态
 */
export function updateModelStatus(id, status) {
  return request({
    url: `/admin/models/${id}/status`,
    method: 'patch',
    data: { status }
  })
}

/**
 * 删除模型
 */
export function deleteModel(id) {
  return request({
    url: `/admin/models/${id}`,
    method: 'delete'
  })
}

// ==================== Dashboard统计 ====================

/**
 * 获取Dashboard统计数据（真实后端API）
 */
export function getDashboardStats() {
  return request({
    url: '/admin/stats/dashboard',
    method: 'get'
  })
}
