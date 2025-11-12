<template>
  <el-container class="admin-layout">
    <!-- 侧边栏 -->
    <el-aside width="200px" class="admin-aside">
      <div class="logo">
        <h3>管理后台</h3>
      </div>
      <el-scrollbar>
        <el-menu
          :default-active="currentRoute"
          router
          unique-opened
          :collapse-transition="false"
        >
          <el-menu-item index="/admin/dashboard">
            <el-icon><DataAnalysis /></el-icon>
            <span>数据看板</span>
          </el-menu-item>
          <el-menu-item index="/admin/users">
            <el-icon><User /></el-icon>
            <span>用户管理</span>
          </el-menu-item>
          <el-menu-item index="/admin/models">
            <el-icon><Box /></el-icon>
            <span>模型管理</span>
          </el-menu-item>
        </el-menu>
      </el-scrollbar>
    </el-aside>

    <!-- 主内容区 -->
    <el-container>
      <!-- 顶部栏 -->
      <el-header class="admin-header">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/admin/dashboard' }">
            管理后台
          </el-breadcrumb-item>
          <el-breadcrumb-item v-if="breadcrumbTitle">
            {{ breadcrumbTitle }}
          </el-breadcrumb-item>
        </el-breadcrumb>

        <div class="header-right">
          <span class="username">{{ userStore.user?.username || '管理员' }}</span>
          <el-dropdown>
            <el-icon class="avatar-icon"><UserFilled /></el-icon>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="handleLogout">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 内容区 -->
      <el-main class="admin-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import { DataAnalysis, User, Box, UserFilled, SwitchButton } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

// 当前路由路径
const currentRoute = computed(() => route.path)

// 面包屑标题
const breadcrumbTitle = computed(() => {
  const titles = {
    '/admin/dashboard': '数据看板',
    '/admin/users': '用户管理',
    '/admin/models': '模型管理',
  }
  return titles[route.path] || ''
})

// 退出登录
const handleLogout = async () => {
  await userStore.logout()
  ElMessage.success('退出登录成功')
  router.push('/login')
}
</script>

<style scoped>
.admin-layout {
  height: 100vh;
}

.admin-aside {
  background: #304156;
  color: #fff;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #2b3a4a;
}

.logo h3 {
  color: #fff;
  margin: 0;
  font-size: 18px;
}

.admin-aside :deep(.el-menu) {
  border-right: none;
  background: #304156;
}

.admin-aside :deep(.el-menu-item) {
  color: #bfcbd9;
}

.admin-aside :deep(.el-menu-item.is-active) {
  background: #409EFF !important;
  color: #fff;
}

.admin-aside :deep(.el-menu-item:hover) {
  background: #263445;
  color: #fff;
}

.admin-header {
  background: #fff;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.username {
  font-size: 14px;
  color: #606266;
}

.avatar-icon {
  font-size: 24px;
  cursor: pointer;
  color: #409EFF;
}

.admin-main {
  background: #f0f2f5;
  padding: 20px;
}
</style>
