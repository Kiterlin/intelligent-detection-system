<template>
  <div class="home-container">
    <div class="header">
      <h1>水下目标智能检测平台</h1>
      <div class="user-info">
        <el-dropdown @command="handleCommand">
          <span class="user-dropdown">
            <el-icon><User /></el-icon>
            {{ authStore.userInfo?.username }}
            <el-icon class="el-icon--right"><arrow-down /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">个人中心</el-dropdown-item>
              <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <div class="content">
      <el-card class="welcome-card">
        <h2>欢迎，{{ authStore.userInfo?.username }}！</h2>
        <p>这是水下目标智能检测平台的首页</p>
        <div class="user-details">
          <el-descriptions title="用户信息" :column="2" border>
            <el-descriptions-item label="用户名">{{
              authStore.userInfo?.username
            }}</el-descriptions-item>
            <el-descriptions-item label="邮箱">{{
              authStore.userInfo?.email
            }}</el-descriptions-item>
            <el-descriptions-item label="角色">{{
              authStore.userInfo?.role === 'admin' ? '管理员' : '普通用户'
            }}</el-descriptions-item>
            <el-descriptions-item label="账号状态">
              <el-tag :type="authStore.userInfo?.is_active ? 'success' : 'danger'">
                {{ authStore.userInfo?.is_active ? '激活' : '禁用' }}
              </el-tag>
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <div class="quick-actions">
          <h3>快捷操作</h3>
          <el-button type="primary" icon="Camera" disabled>开始检测</el-button>
          <el-button type="success" icon="Document" disabled>检测历史</el-button>
          <el-button type="info" @click="router.push('/profile')" icon="User"
            >个人中心</el-button
          >
        </div>
        <p class="note">注：检测功能将在后续阶段实现</p>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { User, ArrowDown } from '@element-plus/icons-vue'

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
  }
}
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  background: #f5f7fa;
}

.header {
  background: white;
  padding: 20px 40px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header h1 {
  margin: 0;
  font-size: 24px;
  color: #333;
}

.user-dropdown {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
}

.content {
  max-width: 1200px;
  margin: 40px auto;
  padding: 0 20px;
}

.welcome-card {
  margin-bottom: 20px;
}

.welcome-card h2 {
  margin-bottom: 12px;
  color: #333;
}

.welcome-card p {
  color: #666;
  margin-bottom: 24px;
}

.user-details {
  margin: 24px 0;
}

.quick-actions {
  margin-top: 32px;
}

.quick-actions h3 {
  margin-bottom: 16px;
  color: #333;
  font-size: 16px;
}

.quick-actions .el-button {
  margin-right: 12px;
}

.note {
  margin-top: 16px;
  color: #999;
  font-size: 14px;
}
</style>
