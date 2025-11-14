<template>
  <div class="space-y-6">
    <!-- 页面标题 -->
    <div>
      <h1 class="text-2xl font-bold text-deep-blue mb-2">模型管理</h1>
      <p class="text-gray-600">管理AI检测模型和版本</p>
    </div>

    <!-- 搜索和操作栏 -->
    <div class="bg-white rounded-xl shadow-soft p-6">
      <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <!-- 搜索区域 -->
        <div class="flex flex-col sm:flex-row gap-3 flex-1">
          <el-input
            v-model="searchQuery"
            placeholder="搜索模型名称"
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
            v-model="statusFilter"
            placeholder="状态筛选"
            clearable
            class="w-full sm:w-40"
            @change="handleSearch"
          >
            <el-option label="全部状态" value="" />
            <el-option label="激活" value="active">
              <div class="flex items-center">
                <span class="w-2 h-2 bg-green-500 rounded-full mr-2" />
                激活
              </div>
            </el-option>
            <el-option label="停用" value="inactive">
              <div class="flex items-center">
                <span class="w-2 h-2 bg-gray-400 rounded-full mr-2" />
                停用
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
        <button
          class="px-4 py-2 bg-coral-orange text-white rounded-lg hover:bg-coral-orange-dark transition-colors flex items-center space-x-2"
          @click="uploadDialogVisible = true"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
          <span>上传模型</span>
        </button>
      </div>
    </div>

    <!-- 模型表格 -->
    <div class="bg-white rounded-xl shadow-soft overflow-hidden">
      <el-table
        v-loading="loading"
        :data="modelList"
        style="width: 100%"
        element-loading-text="加载中..."
        :header-cell-style="{ background: '#f8fafc', color: '#0A2E5B', fontWeight: '600' }"
      >
        <el-table-column prop="id" label="ID" width="80" align="center" />

        <el-table-column label="模型信息" min-width="250">
          <template #default="{ row }">
            <div class="flex items-center space-x-3">
              <div class="w-12 h-12 bg-gradient-to-br from-coral-orange to-coral-orange-dark rounded-xl flex items-center justify-center">
                <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                </svg>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-semibold text-gray-700 truncate">{{ row.name }}</p>
                <p class="text-xs text-gray-500">{{ row.version || '无版本信息' }}</p>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="文件大小" width="120" align="center">
          <template #default="{ row }">
            <span class="text-sm text-gray-600">{{ formatFileSize(row.file_size) }}</span>
          </template>
        </el-table-column>

        <el-table-column label="描述" min-width="200">
          <template #default="{ row }">
            <span class="text-sm text-gray-600" :title="row.description">
              {{ row.description || '-' }}
            </span>
          </template>
        </el-table-column>

        <el-table-column label="状态" width="120" align="center">
          <template #default="{ row }">
            <el-switch
              v-model="row.status"
              active-value="active"
              inactive-value="inactive"
              active-text="激活"
              inactive-text="停用"
              @change="handleStatusChange(row)"
            />
          </template>
        </el-table-column>

        <el-table-column label="上传时间" width="180" align="center">
          <template #default="{ row }">
            <span class="text-sm text-gray-600">{{ formatDate(row.created_at) }}</span>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="180" fixed="right" align="center">
          <template #default="{ row }">
            <div class="flex justify-center space-x-2">
              <button
                class="px-3 py-1 text-xs bg-bright-cyan text-white rounded-lg hover:bg-bright-cyan-dark transition-colors"
                @click="handleEdit(row)"
              >
                编辑
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

    <!-- 上传模型对话框 -->
    <el-dialog
      v-model="uploadDialogVisible"
      title="上传模型文件"
      width="90%"
      :style="{ maxWidth: '600px' }"
      @close="resetUploadForm"
    >
      <el-form ref="uploadFormRef" :model="uploadForm" :rules="uploadRules" label-width="100px">
        <el-form-item label="模型名称" prop="name">
          <el-input v-model="uploadForm.name" placeholder="请输入模型名称" />
        </el-form-item>

        <el-form-item label="版本号" prop="version">
          <el-input v-model="uploadForm.version" placeholder="如：v1.0.0（可选）" />
        </el-form-item>

        <el-form-item label="描述" prop="description">
          <el-input
            v-model="uploadForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入模型描述（可选）"
          />
        </el-form-item>

        <el-form-item label="模型文件" required>
          <el-upload
            ref="uploadRef"
            :file-list="uploadFileList"
            class="w-full"
            drag
            :auto-upload="false"
            :limit="1"
            :on-change="handleFileChange"
            :on-exceed="handleExceed"
            :on-remove="handleRemove"
            accept=".pt,.pth"
          >
            <div class="flex flex-col items-center justify-center py-8">
              <svg class="w-12 h-12 text-coral-orange mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              <p class="text-sm text-gray-600">
                将文件拖到此处，或<span class="text-bright-cyan cursor-pointer">点击上传</span>
              </p>
              <p class="text-xs text-gray-500 mt-2">
                只能上传 .pt 或 .pth 文件，且不超过 500MB
              </p>
            </div>
          </el-upload>
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="flex justify-end space-x-3">
          <button
            class="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium text-gray-700"
            @click="uploadDialogVisible = false"
          >
            取消
          </button>
          <button
            :disabled="uploading"
            class="btn-primary px-6 py-2 text-sm font-medium"
            @click="handleUpload"
          >
            <span v-if="!uploading">上传</span>
            <span v-else class="flex items-center">
              <svg class="animate-spin h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              上传中...
            </span>
          </button>
        </div>
      </template>
    </el-dialog>

    <!-- 编辑模型对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑模型信息"
      width="90%"
      :style="{ maxWidth: '500px' }"
      @close="resetEditForm"
    >
      <el-form ref="editFormRef" :model="editForm" :rules="editRules" label-width="100px">
        <el-form-item label="模型名称" prop="name">
          <el-input v-model="editForm.name" placeholder="请输入模型名称" />
        </el-form-item>

        <el-form-item label="版本号" prop="version">
          <el-input v-model="editForm.version" placeholder="请输入版本号" />
        </el-form-item>

        <el-form-item label="描述" prop="description">
          <el-input
            v-model="editForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入模型描述"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="flex justify-end space-x-3">
          <button
            class="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium text-gray-700"
            @click="editDialogVisible = false"
          >
            取消
          </button>
          <button
            :disabled="submitting"
            class="btn-primary px-6 py-2 text-sm font-medium"
            @click="handleEditSubmit"
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
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Search, UploadFilled } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getModelList,
  uploadModel,
  updateModel,
  updateModelStatus,
  deleteModel
} from '@/api/admin'

// 搜索和筛选
const searchQuery = ref('')
const statusFilter = ref('')

// 表格数据
const modelList = ref([])
const loading = ref(false)

// 分页
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 上传对话框
const uploadDialogVisible = ref(false)
const uploading = ref(false)
const uploadFormRef = ref(null)
const uploadRef = ref(null)
const uploadFileList = ref([])
const uploadForm = reactive({
  name: '',
  version: '',
  description: '',
  file: null
})

const uploadRules = {
  name: [
    { required: true, message: '请输入模型名称', trigger: 'blur' },
    { min: 1, max: 100, message: '模型名称长度为1-100个字符', trigger: 'blur' }
  ]
}

// 编辑对话框
const editDialogVisible = ref(false)
const submitting = ref(false)
const editFormRef = ref(null)
const editForm = reactive({
  id: null,
  name: '',
  version: '',
  description: ''
})

const editRules = {
  name: [
    { required: true, message: '请输入模型名称', trigger: 'blur' },
    { min: 1, max: 100, message: '模型名称长度为1-100个字符', trigger: 'blur' }
  ]
}

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (!bytes) return '-'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
  if (bytes < 1024 * 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
  return (bytes / (1024 * 1024 * 1024)).toFixed(2) + ' GB'
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

// 加载模型列表
const loadModels = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    if (searchQuery.value) {
      params.search = searchQuery.value
    }
    if (statusFilter.value) {
      params.model_status = statusFilter.value
    }

    const res = await getModelList(params)
    modelList.value = res.models
    total.value = res.total
  } catch (error) {
    console.error('Load models error:', error)
    ElMessage.error('加载模型列表失败：' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  loadModels()
}

// 分页变化
const handlePageChange = () => {
  loadModels()
}

// 文件选择
const handleFileChange = (file) => {
  uploadForm.file = file.raw
  uploadFileList.value = [file]
}

// 文件数量超限
const handleExceed = () => {
  ElMessage.warning('只能上传一个文件')
}

// 移除文件
const handleRemove = () => {
  uploadForm.file = null
  uploadFileList.value = []
}

// 上传模型
const handleUpload = async () => {
  if (!uploadFormRef.value) {
    ElMessage.error('表单引用错误，请刷新页面重试')
    return
  }

  try {
    const valid = await uploadFormRef.value.validate()
    if (!valid) return

    if (!uploadForm.file) {
      ElMessage.warning('请选择要上传的模型文件')
      return
    }

    uploading.value = true

    const formData = new FormData()
    formData.append('file', uploadForm.file)
    formData.append('name', uploadForm.name)
    if (uploadForm.version) {
      formData.append('version', uploadForm.version)
    }
    if (uploadForm.description) {
      formData.append('description', uploadForm.description)
    }

    await uploadModel(formData)
    ElMessage.success('上传成功')
    uploadDialogVisible.value = false
    loadModels()
  } catch (error) {
    console.error('Upload error:', error)
    ElMessage.error('上传失败：' + (error.response?.data?.detail || error.message))
  } finally {
    uploading.value = false
  }
}

// 状态切换
const handleStatusChange = async (row) => {
  try {
    await updateModelStatus(row.id, row.status)
    ElMessage.success('状态更新成功')
    if (row.status === 'active') {
      ElMessage.info('注意：激活此模型会自动停用其他模型')
    }
    loadModels()
  } catch (error) {
    ElMessage.error('状态更新失败：' + (error.response?.data?.detail || error.message))
    // 回滚状态
    row.status = row.status === 'active' ? 'inactive' : 'active'
  }
}

// 编辑模型
const handleEdit = (row) => {
  editForm.id = row.id
  editForm.name = row.name
  editForm.version = row.version || ''
  editForm.description = row.description || ''
  editDialogVisible.value = true
}

// 提交编辑
const handleEditSubmit = async () => {
  if (!editFormRef.value) return

  await editFormRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      await updateModel(editForm.id, {
        name: editForm.name,
        version: editForm.version || null,
        description: editForm.description || null
      })
      ElMessage.success('更新成功')
      editDialogVisible.value = false
      loadModels()
    } catch (error) {
      ElMessage.error('更新失败：' + (error.response?.data?.detail || error.message))
    } finally {
      submitting.value = false
    }
  })
}

// 删除模型
const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除模型 "${row.name}" 吗？此操作将同时删除模型文件，且不可恢复。`,
    '确认删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  )
    .then(async () => {
      try {
        await deleteModel(row.id)
        ElMessage.success('删除成功')
        loadModels()
      } catch (error) {
        ElMessage.error('删除失败：' + (error.response?.data?.detail || error.message))
      }
    })
    .catch(() => {})
}

// 重置上传表单
const resetUploadForm = () => {
  if (uploadFormRef.value) {
    uploadFormRef.value.resetFields()
  }
  if (uploadRef.value) {
    uploadRef.value.clearFiles()
  }
  uploadFileList.value = []
  uploadForm.name = ''
  uploadForm.version = ''
  uploadForm.description = ''
  uploadForm.file = null
}

// 重置编辑表单
const resetEditForm = () => {
  if (editFormRef.value) {
    editFormRef.value.resetFields()
  }
  editForm.id = null
  editForm.name = ''
  editForm.version = ''
  editForm.description = ''
}

onMounted(() => {
  loadModels()
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

/* 上传区域样式 */
:deep(.el-upload-dragger) {
  width: 100%;
  border: 2px dashed #d1d5db;
  border-radius: 0.75rem;
  transition: all 0.3s;
}

:deep(.el-upload-dragger:hover) {
  border-color: #00BFFF;
  background-color: #f8fafc;
}
</style>
