import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/Login.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/auth/Register.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/user/Home.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/user/Profile.vue'),
    meta: { requiresAuth: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // 如果路由需要认证
  if (to.meta.requiresAuth) {
    if (!authStore.isAuthenticated) {
      // 未登录，跳转到登录页
      next({
        path: '/login',
        query: { redirect: to.fullPath },
      })
    } else {
      // 已登录，检查是否需要管理员权限
      if (to.meta.requiresAdmin && !authStore.isAdmin) {
        next('/')
        ElMessage.error('需要管理员权限')
      } else {
        next()
      }
    }
  } else {
    // 不需要认证的路由
    if (authStore.isAuthenticated && (to.path === '/login' || to.path === '/register')) {
      // 已登录用户访问登录/注册页，跳转到首页
      next('/')
    } else {
      next()
    }
  }
})

export default router
