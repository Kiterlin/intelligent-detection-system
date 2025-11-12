/**
 * 认证状态管理
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginApi, getCurrentUser, register as registerApi } from '@/api/auth'
import { ElMessage } from 'element-plus'
import router from '@/router'

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const token = ref(localStorage.getItem('access_token') || '')
  const userInfo = ref(null)

  // 计算属性
  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => userInfo.value?.role === 'admin')

  /**
   * 登录
   */
  async function login(username, password) {
    try {
      const data = await loginApi({ username, password })
      token.value = data.access_token
      localStorage.setItem('access_token', data.access_token)

      // 获取用户信息
      await fetchUserInfo()

      ElMessage.success('登录成功')
      return true
    } catch (error) {
      console.error('Login failed:', error)
      return false
    }
  }

  /**
   * 注册
   */
  async function register(userData) {
    try {
      await registerApi(userData)
      ElMessage.success('注册成功，请登录')
      return true
    } catch (error) {
      console.error('Register failed:', error)
      return false
    }
  }

  /**
   * 获取用户信息
   */
  async function fetchUserInfo() {
    try {
      const data = await getCurrentUser()
      userInfo.value = data
    } catch (error) {
      console.error('Fetch user info failed:', error)
      logout()
    }
  }

  /**
   * 登出
   */
  function logout() {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('access_token')
    router.push('/login')
    ElMessage.info('已退出登录')
  }

  /**
   * 初始化（如果有 token，获取用户信息）
   */
  async function init() {
    if (token.value) {
      await fetchUserInfo()
    }
  }

  return {
    token,
    userInfo,
    isAuthenticated,
    isAdmin,
    login,
    register,
    logout,
    fetchUserInfo,
    init,
  }
})
