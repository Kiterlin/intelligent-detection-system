<template>
  <div class="min-h-screen bg-light-gray">
    <!-- 顶部导航栏 -->
    <nav class="bg-white shadow-soft">
      <div class="container-custom py-4">
        <div class="flex items-center justify-between">
          <!-- Logo和标题 -->
          <div class="flex items-center space-x-3">
            <div class="w-10 h-10 bg-gradient-ocean rounded-xl flex items-center justify-center">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h1 class="text-xl md:text-2xl font-bold text-deep-blue">水下目标智能检测平台</h1>
          </div>

          <!-- 用户菜单 -->
          <el-dropdown trigger="click" @command="handleCommand">
            <button class="flex items-center space-x-2 px-4 py-2 rounded-lg hover:bg-gray-50 transition-colors">
              <div class="w-8 h-8 bg-gradient-sunset rounded-full flex items-center justify-center">
                <el-icon class="text-white">
                  <User />
                </el-icon>
              </div>
              <span class="hidden md:inline text-gray-700 font-medium">{{ authStore.userInfo?.username }}</span>
              <el-icon class="text-gray-500">
                <ArrowDown />
              </el-icon>
            </button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item v-if="authStore.isAdmin" command="admin">
                  <el-icon><Setting /></el-icon>
                  管理后台
                </el-dropdown-item>
                <el-dropdown-item command="dashboard">
                  <el-icon><DataAnalysis /></el-icon>
                  仪表盘
                </el-dropdown-item>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>
                  个人中心
                </el-dropdown-item>
                <el-dropdown-item command="logout" divided>
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </nav>

    <!-- 主要内容区 -->
    <div class="container-custom py-8">
      <!-- 欢迎横幅 -->
      <div class="relative overflow-hidden bg-gradient-ocean rounded-2xl p-8 md:p-12 mb-8 animate-fade-in">
        <div class="relative z-10">
          <h2 class="text-2xl md:text-3xl lg:text-4xl font-bold text-white mb-3">
            欢迎回来，{{ authStore.userInfo?.username }}！
          </h2>
          <p class="text-white/90 text-lg mb-6">
            准备好开始您的智能检测之旅了吗？
          </p>
          <div class="flex flex-wrap gap-3">
            <button
              class="px-6 py-3 bg-white text-deep-blue rounded-lg font-semibold hover:shadow-lg transition-all hover:scale-105"
              @click="router.push('/detection')"
            >
              <span class="flex items-center">
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
                开始检测
              </span>
            </button>
            <button
              class="px-6 py-3 bg-white/10 backdrop-blur-sm text-white border-2 border-white/30 rounded-lg font-semibold hover:bg-white/20 transition-all"
              @click="router.push('/detection-history')"
            >
              <span class="flex items-center">
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                查看历史
              </span>
            </button>
          </div>
        </div>
        <!-- 装饰性元素 -->
        <div class="absolute top-0 right-0 w-64 h-64 bg-white/5 rounded-full -mr-32 -mt-32" />
        <div class="absolute bottom-0 right-0 w-48 h-48 bg-white/5 rounded-full -mr-24 -mb-24" />
      </div>

      <!-- 用户信息卡片 -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <!-- 账号信息 -->
        <div class="card-hover animate-slide-up">
          <div class="flex items-start justify-between mb-4">
            <div>
              <p class="text-sm text-gray-500 mb-1">账号信息</p>
              <h3 class="text-xl font-bold text-deep-blue">{{ authStore.userInfo?.username }}</h3>
            </div>
            <div class="w-12 h-12 bg-blue-50 rounded-xl flex items-center justify-center">
              <el-icon class="text-2xl text-bright-cyan">
                <User />
              </el-icon>
            </div>
          </div>
          <div class="space-y-2">
            <div class="flex items-center text-sm text-gray-600">
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
              {{ authStore.userInfo?.email }}
            </div>
            <div class="flex items-center text-sm">
              <el-tag :type="authStore.userInfo?.is_active ? 'success' : 'danger'" size="small">
                {{ authStore.userInfo?.is_active ? '账号正常' : '账号禁用' }}
              </el-tag>
              <el-tag
                class="ml-2"
                :type="authStore.userInfo?.role === 'admin' ? 'warning' : 'info'"
                size="small"
              >
                {{ authStore.userInfo?.role === 'admin' ? '管理员' : '普通用户' }}
              </el-tag>
            </div>
          </div>
        </div>

        <!-- 统计卡片 - 待实现 -->
        <div class="card-hover animate-slide-up" style="animation-delay: 0.1s">
          <div class="flex items-start justify-between mb-4">
            <div>
              <p class="text-sm text-gray-500 mb-1">检测次数</p>
              <h3 class="text-2xl font-bold text-deep-blue">--</h3>
            </div>
            <div class="w-12 h-12 bg-green-50 rounded-xl flex items-center justify-center">
              <svg class="w-6 h-6 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
          </div>
          <p class="text-xs text-gray-500">总检测次数</p>
        </div>

        <div class="card-hover animate-slide-up" style="animation-delay: 0.2s">
          <div class="flex items-start justify-between mb-4">
            <div>
              <p class="text-sm text-gray-500 mb-1">检测对象</p>
              <h3 class="text-2xl font-bold text-deep-blue">--</h3>
            </div>
            <div class="w-12 h-12 bg-orange-50 rounded-xl flex items-center justify-center">
              <svg class="w-6 h-6 text-coral-orange" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
              </svg>
            </div>
          </div>
          <p class="text-xs text-gray-500">已识别对象总数</p>
        </div>
      </div>

      <!-- 快捷操作 -->
      <div class="mb-8">
        <h3 class="text-lg font-bold text-deep-blue mb-4">快捷操作</h3>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <!-- 开始检测 -->
          <button
            class="card-interactive group text-left"
            @click="router.push('/detection')"
          >
            <div class="flex items-center space-x-4">
              <div class="w-14 h-14 bg-gradient-ocean rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
                <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
              </div>
              <div class="flex-1">
                <h4 class="font-semibold text-deep-blue mb-1">开始检测</h4>
                <p class="text-sm text-gray-500">上传图片或视频进行检测</p>
              </div>
            </div>
          </button>

          <!-- 检测历史 -->
          <button
            class="card-interactive group text-left"
            @click="router.push('/detection-history')"
          >
            <div class="flex items-center space-x-4">
              <div class="w-14 h-14 bg-gradient-sunset rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
                <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div class="flex-1">
                <h4 class="font-semibold text-deep-blue mb-1">检测历史</h4>
                <p class="text-sm text-gray-500">查看历史检测记录</p>
              </div>
            </div>
          </button>

          <!-- 个人中心 -->
          <button
            class="card-interactive group text-left"
            @click="router.push('/profile')"
          >
            <div class="flex items-center space-x-4">
              <div class="w-14 h-14 bg-purple-100 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
                <svg class="w-7 h-7 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
              <div class="flex-1">
                <h4 class="font-semibold text-deep-blue mb-1">个人中心</h4>
                <p class="text-sm text-gray-500">管理个人信息</p>
              </div>
            </div>
          </button>

          <!-- 管理后台 (仅管理员可见) -->
          <button
            v-if="authStore.isAdmin"
            class="card-interactive group text-left"
            @click="router.push('/admin/dashboard')"
          >
            <div class="flex items-center space-x-4">
              <div class="w-14 h-14 bg-yellow-100 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
                <svg class="w-7 h-7 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </div>
              <div class="flex-1">
                <h4 class="font-semibold text-deep-blue mb-1">管理后台</h4>
                <p class="text-sm text-gray-500">系统管理和配置</p>
              </div>
            </div>
          </button>
        </div>
      </div>

      <!-- 帮助提示 -->
      <div class="bg-blue-50 border-l-4 border-bright-cyan rounded-lg p-6">
        <div class="flex items-start">
          <div class="flex-shrink-0">
            <svg class="w-6 h-6 text-bright-cyan" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div class="ml-3">
            <h3 class="text-sm font-semibold text-deep-blue mb-1">使用提示</h3>
            <p class="text-sm text-gray-600">
              支持JPG、PNG、MP4等格式文件。图片最大20MB，视频最大500MB。
              首次使用建议从"开始检测"开始体验。
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { User, ArrowDown, Setting, SwitchButton, DataAnalysis } from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()

onMounted(async () => {
  // 确保加载用户信息
  if (!authStore.userInfo) {
    await authStore.fetchUserInfo()
  }
})

const handleCommand = (command) => {
  if (command === 'logout') {
    authStore.logout()
  } else if (command === 'profile') {
    router.push('/profile')
  } else if (command === 'dashboard') {
    router.push('/dashboard')
  } else if (command === 'admin') {
    router.push('/admin/dashboard')
  }
}
</script>

<style scoped>
/* 额外的动画延迟 */
.animate-slide-up[style*="animation-delay"] {
  animation-fill-mode: both;
}
</style>
