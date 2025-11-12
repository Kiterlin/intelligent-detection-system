<template>
  <div class="profile-container">
    <div class="header">
      <h1>个人中心</h1>
      <el-button @click="router.push('/')">返回首页</el-button>
    </div>

    <div class="content">
      <el-card>
        <h2>个人信息</h2>
        <el-descriptions :column="1" border>
          <el-descriptions-item label="用户名">{{
            authStore.userInfo?.username
          }}</el-descriptions-item>
          <el-descriptions-item label="邮箱">{{
            authStore.userInfo?.email
          }}</el-descriptions-item>
          <el-descriptions-item label="角色">{{
            authStore.userInfo?.role === 'admin' ? '管理员' : '普通用户'
          }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{
            formatDate(authStore.userInfo?.created_at)
          }}</el-descriptions-item>
        </el-descriptions>

        <div class="actions">
          <h3>账号操作</h3>
          <el-button type="primary" disabled>修改密码</el-button>
          <el-button type="danger" @click="authStore.logout()">退出登录</el-button>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}
</script>

<style scoped>
.profile-container {
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

.content {
  max-width: 800px;
  margin: 40px auto;
  padding: 0 20px;
}

.content h2 {
  margin-bottom: 20px;
  color: #333;
}

.actions {
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid #eee;
}

.actions h3 {
  margin-bottom: 16px;
  font-size: 16px;
  color: #333;
}

.actions .el-button {
  margin-right: 12px;
}
</style>
