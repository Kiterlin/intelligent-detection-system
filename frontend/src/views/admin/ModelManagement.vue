<template>
  <div class="model-management">
    <el-card>
      <!-- 工具栏 -->
      <div class="toolbar">
        <div class="search-area">
          <el-input
            v-model="searchQuery"
            placeholder="搜索模型名称"
            clearable
            style="width: 300px"
            @clear="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-select
            v-model="statusFilter"
            placeholder="状态筛选"
            clearable
            style="width: 150px; margin-left: 10px"
            @change="handleSearch"
          >
            <el-option label="激活" value="active" />
            <el-option label="停用" value="inactive" />
          </el-select>
          <el-button type="primary" @click="handleSearch" style="margin-left: 10px">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
        </div>
        <div class="action-area">
          <el-button type="primary" @click="uploadDialogVisible = true">
            <el-icon><Upload /></el-icon>
            上传模型
          </el-button>
        </div>
      </div>

      <!-- 模型表格 -->
      <el-table
        :data="modelList"
        v-loading="loading"
        style="margin-top: 20px"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="模型名称" width="200" />
        <el-table-column prop="version" label="版本" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'">
              {{ row.status === 'active' ? '激活' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="file_size" label="文件大小" width="120">
          <template #default="{ row }">
            {{ formatFileSize(row.file_size) }}
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="created_at" label="上传时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="250">
          <template #default="{ row }">
            <el-switch
              v-model="row.status"
              active-value="active"
              inactive-value="inactive"
              @change="handleStatusChange(row)"
              style="margin-right: 10px"
            />
            <el-button link type="primary" @click="handleEdit(row)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button link type="danger" @click="handleDelete(row)">
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handlePageChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 上传模型对话框 -->
    <el-dialog
      v-model="uploadDialogVisible"
      title="上传模型文件"
      width="600px"
      @close="resetUploadForm"
    >
      <el-form :model="uploadForm" :rules="uploadRules" ref="uploadFormRef" label-width="100px">
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
        <el-form-item label="模型文件" prop="file" required>
          <el-upload
            ref="uploadRef"
            class="upload-demo"
            drag
            :auto-upload="false"
            :limit="1"
            :on-change="handleFileChange"
            :on-exceed="handleExceed"
            accept=".pt,.pth"
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              将文件拖到此处，或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                只能上传 .pt 或 .pth 文件，且不超过 500MB
              </div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="uploadDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleUpload" :loading="uploading">
          上传
        </el-button>
      </template>
    </el-dialog>

    <!-- 编辑模型对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑模型信息"
      width="500px"
      @close="resetEditForm"
    >
      <el-form :model="editForm" :rules="editRules" ref="editFormRef" label-width="100px">
        <el-form-item label="模型名称" prop="name">
          <el-input v-model="editForm.name" />
        </el-form-item>
        <el-form-item label="版本号" prop="version">
          <el-input v-model="editForm.version" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="editForm.description"
            type="textarea"
            :rows="3"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleEditSubmit" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Search, Upload, Edit, Delete, UploadFilled } from '@element-plus/icons-vue'
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
    modelList.value = res.data.models
    total.value = res.data.total
  } catch (error) {
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
}

// 文件数量超限
const handleExceed = () => {
  ElMessage.warning('只能上传一个文件')
}

// 上传模型
const handleUpload = async () => {
  if (!uploadFormRef.value) return

  await uploadFormRef.value.validate(async (valid) => {
    if (!valid) return

    if (!uploadForm.file) {
      ElMessage.warning('请选择要上传的模型文件')
      return
    }

    uploading.value = true
    try {
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
      ElMessage.error('上传失败：' + (error.response?.data?.detail || error.message))
    } finally {
      uploading.value = false
    }
  })
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
.model-management {
  padding: 0;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-area {
  display: flex;
  align-items: center;
}

.action-area {
  display: flex;
  gap: 10px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.upload-demo {
  width: 100%;
}

:deep(.el-upload-dragger) {
  width: 100%;
  height: 200px;
}
</style>
