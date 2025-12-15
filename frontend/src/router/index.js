import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'

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
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/user/Dashboard.vue'),
    meta: { requiresAuth: true },
  },
  // 检测功能路由
  {
    path: '/detection',
    name: 'Detection',
    component: () => import('@/views/user/Detection.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/detection-history',
    name: 'DetectionHistory',
    component: () => import('@/views/user/DetectionHistory.vue'),
    meta: { requiresAuth: true },
  },
  // 数据集管理路由
  {
    path: '/datasets',
    name: 'DatasetList',
    component: () => import('@/views/user/DatasetList.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/datasets/:id',
    name: 'DatasetDetail',
    component: () => import('@/views/user/DatasetDetail.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/batch-jobs',
    name: 'BatchJobList',
    component: () => import('@/views/user/BatchJobList.vue'),
    meta: { requiresAuth: true },
  },
  // 告警系统路由
  {
    path: '/alerts',
    name: 'AlertRules',
    component: () => import('@/views/user/AlertRules.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/alerts/logs',
    name: 'AlertLogs',
    component: () => import('@/views/user/AlertLogs.vue'),
    meta: { requiresAuth: true },
  },
  // 结果对比路由
  {
    path: '/comparison',
    name: 'Comparison',
    component: () => import('@/views/user/Comparison.vue'),
    meta: { requiresAuth: true },
  },
  // 报告生成路由
  {
    path: '/user/reports',
    name: 'Reports',
    component: () => import('@/views/user/Reports.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/user/reports/generator',
    name: 'ReportGenerator',
    component: () => import('@/views/user/ReportGenerator.vue'),
    meta: { requiresAuth: true },
  },
  // 数据标注路由
  {
    path: '/annotations/tasks',
    name: 'AnnotationTasks',
    component: () => import('@/views/user/AnnotationTasks.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/annotations/create',
    name: 'CreateAnnotationTask',
    component: () => import('@/views/user/CreateAnnotationTask.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/annotations/tasks/:id',
    name: 'AnnotationTaskDetail',
    component: () => import('@/views/user/AnnotationTaskDetail.vue'),
    meta: { requiresAuth: true },
  },
  // 管理后台路由
  {
    path: '/admin',
    component: () => import('@/layouts/AdminLayout.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
    redirect: '/admin/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'AdminDashboard',
        component: () => import('@/views/admin/Dashboard.vue'),
        meta: { requiresAuth: true, requiresAdmin: true },
      },
      {
        path: 'users',
        name: 'UserManagement',
        component: () => import('@/views/admin/UserManagement.vue'),
        meta: { requiresAuth: true, requiresAdmin: true },
      },
      {
        path: 'models',
        name: 'ModelManagement',
        component: () => import('@/views/admin/ModelManagement.vue'),
        meta: { requiresAuth: true, requiresAdmin: true },
      },
      {
        path: 'training',
        name: 'TrainingJobs',
        component: () => import('@/views/admin/TrainingJobs.vue'),
        meta: { requiresAuth: true, requiresAdmin: true },
      },
      {
        path: 'training/create',
        name: 'CreateTrainingJob',
        component: () => import('@/views/admin/CreateTrainingJob.vue'),
        meta: { requiresAuth: true, requiresAdmin: true },
      },
      {
        path: 'training/:id',
        name: 'TrainingMonitor',
        component: () => import('@/views/admin/TrainingMonitor.vue'),
        meta: { requiresAuth: true, requiresAdmin: true },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()

  // 如果路由需要认证
  if (to.meta.requiresAuth) {
    if (!userStore.isAuthenticated) {
      // 未登录，跳转到登录页
      next({
        path: '/login',
        query: { redirect: to.fullPath },
      })
    } else {
      // 已登录，检查是否需要管理员权限
      if (to.meta.requiresAdmin && !userStore.isAdmin) {
        ElMessage.error('需要管理员权限')
        next('/')
      } else {
        next()
      }
    }
  } else {
    // 不需要认证的路由
    if (userStore.isAuthenticated && (to.path === '/login' || to.path === '/register')) {
      // 已登录用户访问登录/注册页，跳转到首页
      next('/')
    } else {
      next()
    }
  }
})

export default router
