<template>
  <div class="min-h-screen bg-light-gray">
    <!-- 页面标题 -->
    <div class="bg-gradient-ocean py-12 mb-8">
      <div class="container-custom">
        <h1 class="text-3xl md:text-4xl font-bold text-white mb-2">数据集管理</h1>
        <p class="text-white/80">创建和管理您的检测数据集，支持批量上传和检测</p>
      </div>
    </div>

    <div class="container-custom pb-12">
      <!-- 操作栏 -->
      <div class="flex flex-col md:flex-row gap-4 mb-6">
        <!-- 搜索框 -->
        <div class="flex-1">
          <el-input
            v-model="searchQuery"
            placeholder="搜索数据集名称或描述..."
            clearable
            @clear="loadDatasets"
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <el-icon>
                <Search />
              </el-icon>
            </template>
          </el-input>
        </div>

        <!-- 创建按钮 -->
        <el-button
          type="primary"
          :icon="Plus"
          @click="showCreateDialog"
        >
          创建数据集
        </el-button>
      </div>

      <!-- 数据集列表 -->
      <div v-loading="loading">
        <div
          v-if="datasets.length === 0 && !loading"
          class="text-center py-20"
        >
          <el-icon :size="64" class="text-gray-300 mb-4">
            <FolderOpened />
          </el-icon>
          <p class="text-gray-400 mb-4">还没有创建数据集</p>
          <el-button type="primary" @click="showCreateDialog">
            立即创建
          </el-button>
        </div>

        <div
          v-else
          class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          <div
            v-for="dataset in datasets"
            :key="dataset.id"
            class="card-hover cursor-pointer animate-fade-in"
            @click="goToDetail(dataset.id)"
          >
            <!-- 数据集图标和信息 -->
            <div class="flex items-start mb-4">
              <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mr-4 flex-shrink-0">
                <el-icon :size="24" class="text-blue-600">
                  <Folder />
                </el-icon>
              </div>
              <div class="flex-1 min-w-0">
                <h3 class="text-lg font-bold text-deep-blue mb-1 truncate">
                  {{ dataset.name }}
                </h3>
                <p
                  v-if="dataset.description"
                  class="text-sm text-gray-500 line-clamp-2"
                >
                  {{ dataset.description }}
                </p>
                <p
                  v-else
                  class="text-sm text-gray-400 italic"
                >
                  暂无描述
                </p>
              </div>
            </div>

            <!-- 统计信息 -->
            <div class="grid grid-cols-2 gap-4 mb-4 pt-4 border-t border-gray-100">
              <div>
                <p class="text-xs text-gray-500 mb-1">文件数量</p>
                <p class="text-lg font-semibold text-deep-blue">
                  {{ dataset.file_count }}
                </p>
              </div>
              <div>
                <p class="text-xs text-gray-500 mb-1">总大小</p>
                <p class="text-lg font-semibold text-deep-blue">
                  {{ formatFileSize(dataset.total_size) }}
                </p>
              </div>
            </div>

            <!-- 时间信息 -->
            <div class="text-xs text-gray-400 mb-4">
              创建于 {{ formatDate(dataset.created_at) }}
            </div>

            <!-- 操作按钮 -->
            <div class="flex gap-2">
              <el-button
                size="small"
                @click.stop="goToDetail(dataset.id)"
              >
                查看详情
              </el-button>
              <el-button
                size="small"
                @click.stop="showEditDialog(dataset)"
              >
                编辑
              </el-button>
              <el-button
                size="small"
                type="danger"
                @click.stop="handleDelete(dataset)"
              >
                删除
              </el-button>
            </div>
          </div>
        </div>

        <!-- 分页 -->
        <div v-if="total > 0" class="flex justify-center mt-8">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :total="total"
            :page-sizes="[20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            @current-change="loadDatasets"
            @size-change="loadDatasets"
          />
        </div>
      </div>
    </div>

    <!-- 创建/编辑数据集对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogMode === 'create' ? '创建数据集' : '编辑数据集'"
      width="500px"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="数据集名称" prop="name">
          <el-input
            v-model="formData.name"
            placeholder="请输入数据集名称"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="4"
            placeholder="请输入数据集描述（可选）"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          {{ dialogMode === 'create' ? '创建' : '保存' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search,
  Plus,
  Folder,
  FolderOpened
} from '@element-plus/icons-vue'
import {
  getDatasets,
  createDataset,
  updateDataset,
  deleteDataset
} from '@/api/dataset'
import { formatFileSize } from '@/api/dataset'

const router = useRouter()

// 数据列表
const datasets = ref([])
const loading = ref(false)
const searchQuery = ref('')

// 分页
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

// 对话框
const dialogVisible = ref(false)
const dialogMode = ref('create') // 'create' or 'edit'
const formRef = ref(null)
const submitting = ref(false)
const currentDataset = ref(null)

// 表单数据
const formData = reactive({
  name: '',
  description: ''
})

// 表单验证规则
const formRules = {
  name: [
    { required: true, message: '请输入数据集名称', trigger: 'blur' },
    { min: 1, max: 100, message: '长度在 1 到 100 个字符', trigger: 'blur' }
  ]
}

// 加载数据集列表
const loadDatasets = async () => {
  loading.value = true
  try {
    const params = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value
    }
    if (searchQuery.value) {
      params.search = searchQuery.value
    }

    const res = await getDatasets(params)
    datasets.value = res.items
    total.value = res.total
  } catch (error) {
    console.error('加载数据集失败:', error)
    ElMessage.error('加载数据集失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  loadDatasets()
}

// 显示创建对话框
const showCreateDialog = () => {
  dialogMode.value = 'create'
  formData.name = ''
  formData.description = ''
  currentDataset.value = null
  dialogVisible.value = true
}

// 显示编辑对话框
const showEditDialog = (dataset) => {
  dialogMode.value = 'edit'
  formData.name = dataset.name
  formData.description = dataset.description || ''
  currentDataset.value = dataset
  dialogVisible.value = true
}

// 提交表单
const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    if (dialogMode.value === 'create') {
      await createDataset(formData)
      ElMessage.success('创建成功')
    } else {
      await updateDataset(currentDataset.value.id, formData)
      ElMessage.success('更新成功')
    }
    dialogVisible.value = false
    loadDatasets()
  } catch (error) {
    console.error('操作失败:', error)
    ElMessage.error(error.response?.data?.detail || '操作失败')
  } finally {
    submitting.value = false
  }
}

// 删除数据集
const handleDelete = (dataset) => {
  ElMessageBox.confirm(
    `确定要删除数据集"${dataset.name}"吗？此操作将删除数据集中的所有文件和相关任务。`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  )
    .then(async () => {
      try {
        await deleteDataset(dataset.id)
        ElMessage.success('删除成功')
        loadDatasets()
      } catch (error) {
        console.error('删除失败:', error)
        ElMessage.error(error.response?.data?.detail || '删除失败')
      }
    })
    .catch(() => {})
}

// 跳转到详情页
const goToDetail = (datasetId) => {
  router.push(`/datasets/${datasetId}`)
}

// 格式化日期
const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 页面加载时获取数据
onMounted(() => {
  loadDatasets()
})
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
