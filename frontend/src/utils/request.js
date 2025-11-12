import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

// 创建 axios 实例
const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  timeout: 30000,
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    // 从 localStorage 获取 token
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    console.error('Response error:', error)

    if (error.response) {
      const { status, data, config } = error.response

      // 401 未授权 - token 过期或无效
      if (status === 401) {
        // 如果是登录接口返回401，不需要清除token和跳转，让登录页面处理
        if (!config.url.includes('/auth/login')) {
          localStorage.removeItem('access_token')
          router.push('/login')
          ElMessage.error('登录已过期，请重新登录')
        } else {
          // 登录接口返回401，显示具体错误信息
          ElMessage.error(data.detail || '用户名或密码错误')
        }
      }
      // 403 禁止访问 - 权限不足
      else if (status === 403) {
        ElMessage.error(data.detail || '权限不足')
      }
      // 其他错误
      else {
        ElMessage.error(data.detail || '请求失败')
      }
    } else {
      ElMessage.error('网络错误，请检查网络连接')
    }

    return Promise.reject(error)
  }
)

export default request
