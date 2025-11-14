<template>
  <div class="space-y-6">
    <!-- 页面标题 -->
    <div>
      <h1 class="text-2xl font-bold text-deep-blue mb-2">用户管理</h1>
      <p class="text-gray-600">管理系统用户和权限</p>
    </div>

    <!-- 搜索和操作栏 -->
    <div class="bg-white rounded-xl shadow-soft p-6">
      <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <!-- 搜索区域 -->
        <div class="flex flex-col sm:flex-row gap-3 flex-1">
          <el-input
            v-model="searchQuery"
            placeholder="搜索用户名或邮箱"
            clearable
            class="w-full sm:w-64"
            @clear="handleSearch"
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <el-icon class="text-bright-cyan">
                <Search />
              </el-icon>
            </template>
          </el-input>

          <el-select
            v-model="roleFilter"
            placeholder="角色筛选"
            clearable
            class="w-full sm:w-40"
            @change="handleSearch"
          >
            <el-option label="全部角色" value="" />
            <el-option label="普通用户" value="user">
              <div class="flex items-center">
                <span class="w-2 h-2 bg-blue-500 rounded-full mr-2" />
                普通用户
              </div>
            </el-option>
            <el-option label="管理员" value="admin">
              <div class="flex items-center">
                <span class="w-2 h-2 bg-red-500 rounded-full mr-2" />
                管理员
              </div>
            </el-option>
          </el-select>

          <button
            class="px-4 py-2 bg-bright-cyan text-white rounded-lg hover:bg-bright-cyan-dark transition-colors flex items-center justify-center space-x-2"
            @click="handleSearch"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <span>搜索</span>
          </button>
        </div>

        <!-- 操作按钮 -->
        <div class="flex gap-3">
          <button
            class="px-4 py-2 bg-coral-orange text-white rounded-lg hover:bg-coral-orange-dark transition-colors flex items-center space-x-2"
            @click="handleAdd"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            <span>添加用户</span>
          </button>

          <button
            v-if="selectedUsers.length > 0"
            class="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors flex items-center space-x-2"
            @click="handleBatchDelete"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
            <span>批量删除 ({{ selectedUsers.length }})</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 用户表格 -->
    <div class="bg-white rounded-xl shadow-soft overflow-hidden">
      <el-table
        v-loading="loading"
        :data="userList"
        style="width: 100%"
        element-loading-text="加载中..."
        :header-cell-style="{ background: '#f8fafc', color: '#0A2E5B', fontWeight: '600' }"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="ID" width="80" align="center" />

        <el-table-column label="用户信息" min-width="200">
          <template #default="{ row }">
            <div class="flex items-center space-x-3">
              <div class="w-10 h-10 bg-gradient-ocean rounded-full flex items-center justify-center">
                <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
              <div>
                <p class="text-sm font-semibold text-gray-700">{{ row.username }}</p>
                <p class="text-xs text-gray-500">{{ row.email }}</p>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="角色" width="120" align="center">
          <template #default="{ row }">
            <el-tag
              :color="row.role === 'admin' ? '#ef4444' : '#3b82f6'"
              style="color: white; border: none;"
              effect="dark"
            >
              <div class="flex items-center space-x-1">
                <svg v-if="row.role === 'admin'" class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                </svg>
                <svg v-else class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd" />
                </svg>
                <span>{{ row.role === 'admin' ? '管理员' : '普通用户' }}</span>
              </div>
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" effect="plain">
              {{ row.is_active ? '激活' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="创建时间" width="180" align="center">
          <template #default="{ row }">
            <span class="text-sm text-gray-600">{{ formatDate(row.created_at) }}</span>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="280" fixed="right" align="center">
          <template #default="{ row }">
            <div class="flex justify-center space-x-2">
              <button
                class="px-3 py-1 text-xs bg-bright-cyan text-white rounded-lg hover:bg-bright-cyan-dark transition-colors"
                @click="handleEdit(row)"
              >
                编辑
              </button>
              <button
                class="px-3 py-1 text-xs bg-amber-500 text-white rounded-lg hover:bg-amber-600 transition-colors"
                @click="handleResetPassword(row)"
              >
                重置密码
              </button>
              <button
                class="px-3 py-1 text-xs bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
                @click="handleDelete(row)"
              >
                删除
              </button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="px-6 py-4 border-t border-gray-200 flex justify-center">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          background
          @size-change="handlePageChange"
          @current-change="handlePageChange"
        />
      </div>
    </div>

    <!-- 添加/编辑用户对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="90%"
      :style="{ maxWidth: '500px' }"
      @close="resetForm"
    >
      <el-form ref="formRef" :model="userForm" :rules="formRules" label-width="100px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" :disabled="isEdit" placeholder="请输入用户名" />
        </el-form-item>

        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" placeholder="请输入邮箱地址" />
        </el-form-item>

        <el-form-item v-if="!isEdit" label="密码" prop="password">
          <el-input v-model="userForm.password" type="password" show-password placeholder="请输入密码" />
        </el-form-item>

        <el-form-item label="角色" prop="role">
          <el-select v-model="userForm.role" style="width: 100%" placeholder="请选择角色">
            <el-option label="普通用户" value="user">
              <div class="flex items-center">
                <svg class="w-4 h-4 mr-2 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd" />
                </svg>
                普通用户
              </div>
            </el-option>
            <el-option label="管理员" value="admin">
              <div class="flex items-center">
                <svg class="w-4 h-4 mr-2 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                </svg>
                管理员
              </div>
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="状态">
          <el-switch
            v-model="userForm.is_active"
            active-text="激活"
            inactive-text="停用"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="flex justify-end space-x-3">
          <button
            class="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium text-gray-700"
            @click="dialogVisible = false"
          >
            取消
          </button>
          <button
            :disabled="submitting"
            class="btn-primary px-6 py-2 text-sm font-medium"
            @click="handleSubmit"
          >
            <span v-if="!submitting">确定</span>
            <span v-else class="flex items-center">
              <svg class="animate-spin h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              提交中...
            </span>
          </button>
        </div>
      </template>
    </el-dialog>

    <!-- 重置密码对话框 -->
    <el-dialog
      v-model="resetPasswordDialogVisible"
      title="重置用户密码"
      width="90%"
      :style="{ maxWidth: '400px' }"
      @close="resetPasswordForm.new_password = ''; resetPasswordForm.confirm_password = ''"
    >
      <div class="mb-4">
        <p class="text-sm text-gray-600">
          正在为用户 <span class="font-semibold text-gray-900">{{ currentResetUser?.username }}</span> 重置密码
        </p>
      </div>

      <el-form :model="resetPasswordForm" label-width="100px">
        <el-form-item label="新密码">
          <el-input
            v-model="resetPasswordForm.new_password"
            type="password"
            show-password
            placeholder="请输入新密码（至少6位）"
          />
        </el-form-item>
        <el-form-item label="确认密码">
          <el-input
            v-model="resetPasswordForm.confirm_password"
            type="password"
            show-password
            placeholder="请再次输入新密码"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="flex justify-end space-x-3">
          <button
            class="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium text-gray-700"
            @click="resetPasswordDialogVisible = false"
          >
            取消
          </button>
          <button
            :disabled="resettingPassword"
            class="btn-primary px-6 py-2 text-sm font-medium"
            @click="handleConfirmResetPassword"
          >
            <span v-if="!resettingPassword">确认重置</span>
            <span v-else class="flex items-center">
              <svg class="animate-spin h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              重置中...
            </span>
          </button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getUserList,
  createUser,
  updateUser,
  deleteUser,
  batchDeleteUsers,
  resetUserPassword
} from '@/api/admin'

// 搜索和筛选
const searchQuery = ref('')
const roleFilter = ref('')

// 表格数据
const userList = ref([])
const loading = ref(false)
const selectedUsers = ref([])

// 分页
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 对话框
const dialogVisible = ref(false)
const dialogTitle = computed(() => (isEdit.value ? '编辑用户' : '添加用户'))
const isEdit = ref(false)
const submitting = ref(false)
const formRef = ref(null)

// 表单数据
const userForm = reactive({
  id: null,
  username: '',
  email: '',
  password: '',
  role: 'user',
  is_active: true
})

// 密码重置
const resetPasswordDialogVisible = ref(false)
const resettingPassword = ref(false)
const currentResetUser = ref(null)
const resetPasswordForm = reactive({
  new_password: '',
  confirm_password: ''
})

// 表单验证规则
const formRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度为3-50个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 50, message: '密码长度为6-50个字符', trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ]
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 加载用户列表
const loadUsers = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    if (searchQuery.value) {
      params.search = searchQuery.value
    }
    if (roleFilter.value) {
      params.role = roleFilter.value
    }

    const res = await getUserList(params)
    userList.value = res.users
    total.value = res.total
  } catch (error) {
    console.error('Load users error:', error)
    ElMessage.error('加载用户列表失败：' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  loadUsers()
}

// 分页变化
const handlePageChange = () => {
  loadUsers()
}

// 选择变化
const handleSelectionChange = (selection) => {
  selectedUsers.value = selection
}

// 添加用户
const handleAdd = () => {
  isEdit.value = false
  dialogVisible.value = true
}

// 编辑用户
const handleEdit = (row) => {
  isEdit.value = true
  userForm.id = row.id
  userForm.username = row.username
  userForm.email = row.email
  userForm.role = row.role
  userForm.is_active = row.is_active
  dialogVisible.value = true
}

// 删除用户
const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除用户 "${row.username}" 吗？此操作不可恢复。`,
    '确认删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  )
    .then(async () => {
      try {
        await deleteUser(row.id)
        ElMessage.success('删除成功')
        loadUsers()
      } catch (error) {
        ElMessage.error('删除失败：' + (error.response?.data?.detail || error.message))
      }
    })
    .catch(() => {})
}

// 批量删除
const handleBatchDelete = () => {
  ElMessageBox.confirm(
    `确定要删除选中的 ${selectedUsers.value.length} 个用户吗？此操作不可恢复。`,
    '确认批量删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  )
    .then(async () => {
      try {
        const userIds = selectedUsers.value.map(u => u.id)
        await batchDeleteUsers(userIds)
        ElMessage.success('批量删除成功')
        selectedUsers.value = []
        loadUsers()
      } catch (error) {
        ElMessage.error('批量删除失败：' + (error.response?.data?.detail || error.message))
      }
    })
    .catch(() => {})
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      if (isEdit.value) {
        // 编辑用户
        const updateData = {
          email: userForm.email,
          role: userForm.role,
          is_active: userForm.is_active
        }
        await updateUser(userForm.id, updateData)
        ElMessage.success('更新成功')
      } else {
        // 添加用户
        await createUser({
          username: userForm.username,
          email: userForm.email,
          password: userForm.password,
          role: userForm.role,
          is_active: userForm.is_active
        })
        ElMessage.success('添加成功')
      }
      dialogVisible.value = false
      loadUsers()
    } catch (error) {
      ElMessage.error(
        (isEdit.value ? '更新' : '添加') + '失败：' +
        (error.response?.data?.detail || error.message)
      )
    } finally {
      submitting.value = false
    }
  })
}

// 重置表单
const resetForm = () => {
  if (formRef.value) {
    formRef.value.resetFields()
  }
  userForm.id = null
  userForm.username = ''
  userForm.email = ''
  userForm.password = ''
  userForm.role = 'user'
  userForm.is_active = true
}

// 重置密码
const handleResetPassword = (user) => {
  currentResetUser.value = user
  resetPasswordForm.new_password = ''
  resetPasswordForm.confirm_password = ''
  resetPasswordDialogVisible.value = true
}

// 确认重置密码
const handleConfirmResetPassword = async () => {
  if (!resetPasswordForm.new_password || resetPasswordForm.new_password.length < 6) {
    ElMessage.warning('新密码至少6位')
    return
  }
  if (resetPasswordForm.new_password !== resetPasswordForm.confirm_password) {
    ElMessage.warning('两次输入的密码不一致')
    return
  }

  try {
    resettingPassword.value = true
    await resetUserPassword(currentResetUser.value.id, resetPasswordForm.new_password)
    ElMessage.success(`用户 ${currentResetUser.value.username} 的密码已重置`)
    resetPasswordDialogVisible.value = false
  } catch (error) {
    console.error('Reset password error:', error)
    ElMessage.error('密码重置失败：' + (error.response?.data?.detail || error.message))
  } finally {
    resettingPassword.value = false
  }
}

onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
/* 表格行悬停效果 */
:deep(.el-table__row):hover {
  background-color: #f8fafc;
}

/* 分页样式 */
:deep(.el-pagination.is-background .el-pager li:not(.disabled).active) {
  background-color: #00BFFF;
  color: white;
}

:deep(.el-pagination.is-background .el-pager li:hover) {
  color: #00BFFF;
}
</style>
