<template>
  <div class="min-h-screen bg-light-gray">
    <!-- 页面标题 -->
    <div class="bg-gradient-ocean py-12 mb-8">
      <div class="container-custom">
        <h1 class="text-3xl md:text-4xl font-bold text-white mb-2">报告管理</h1>
        <p class="text-white/80">查看和管理生成的检测报告</p>
      </div>
    </div>

    <div class="container-custom pb-12">
      <!-- 操作栏 -->
      <div class="flex flex-col md:flex-row gap-4 mb-6">
        <!-- 状态过滤 -->
        <el-select
          v-model="statusFilter"
          placeholder="状态筛选"
          clearable
          @change="loadReports"
          style="width: 150px"
        >
          <el-option
            v-for="option in statusOptions"
            :key="option.value"
            :label="option.label"
            :value="option.value"
          />
        </el-select>

        <div class="flex-1"></div>

        <!-- 返回首页按钮 -->
        <el-button :icon="HomeFilled" @click="goToHome">
          返回首页
        </el-button>

        <!-- 刷新按钮 -->
        <el-button :icon="Refresh" @click="loadReports">
          刷新
        </el-button>

        <!-- 创建报告按钮 -->
        <el-button
          type="primary"
          :icon="Plus"
          @click="goToGenerator"
        >
          生成新报告
        </el-button>
      </div>

      <!-- 报告列表 -->
      <div v-loading="loading">
        <!-- 空状态 -->
        <div
          v-if="reports.length === 0 && !loading"
          class="text-center py-20"
        >
          <el-icon :size="64" class="text-gray-300 mb-4">
            <Document />
          </el-icon>
          <p class="text-gray-400 mb-4">还没有生成报告</p>
          <el-button type="primary" @click="goToGenerator">
            生成第一个报告
          </el-button>
        </div>

        <!-- 报告卡片 -->
        <div v-else class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div
            v-for="report in reports"
            :key="report.id"
            class="card-hover animate-fade-in"
          >
            <!-- 报告头部 -->
            <div class="flex items-start justify-between mb-4">
              <div class="flex items-start flex-1">
                <div class="w-12 h-12 rounded-lg bg-blue-100 flex items-center justify-center mr-4 flex-shrink-0">
                  <el-icon :size="24" class="text-blue-600">
                    <Document />
                  </el-icon>
                </div>
                <div class="flex-1 min-w-0">
                  <h3 class="text-lg font-bold text-deep-blue mb-1">
                    {{ report.name }}
                  </h3>
                  <div class="flex items-center gap-2 text-sm">
                    <el-tag :type="getReportTypeInfo(report.report_type).type" size="small">
                      {{ getReportTypeInfo(report.report_type).text }}
                    </el-tag>
                    <el-tag :type="getStatusInfo(report.status).type" size="small">
                      <el-icon v-if="report.status === 'generating'" class="is-loading mr-1">
                        <Loading />
                      </el-icon>
                      {{ getStatusInfo(report.status).text }}
                    </el-tag>
                  </div>
                </div>
              </div>
            </div>

            <!-- 报告信息 -->
            <div class="space-y-2 mb-4 p-4 bg-gray-50 rounded-lg text-sm">
              <div class="flex justify-between">
                <span class="text-gray-500">创建时间:</span>
                <span class="text-deep-blue">{{ formatDate(report.created_at) }}</span>
              </div>
              <div v-if="report.completed_at" class="flex justify-between">
                <span class="text-gray-500">完成时间:</span>
                <span class="text-deep-blue">{{ formatDate(report.completed_at) }}</span>
              </div>
              <div v-if="report.error_message" class="text-red-500 text-xs">
                错误: {{ report.error_message }}
              </div>
            </div>

            <!-- 操作按钮 -->
            <div class="flex gap-2">
              <el-button
                v-if="report.status === 'completed'"
                size="small"
                type="primary"
                @click="downloadReport(report, 'pdf')"
              >
                下载PDF
              </el-button>
              <el-button
                v-if="report.status === 'completed'"
                size="small"
                @click="downloadReport(report, 'html')"
              >
                下载HTML
              </el-button>
              <el-button
                size="small"
                type="danger"
                @click="handleDelete(report)"
                :disabled="report.status === 'generating'"
              >
                删除
              </el-button>
            </div>
          </div>
        </div>

        <!-- 分页 -->
        <div v-if="total > 0" class="mt-8 flex justify-center">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :total="total"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="loadReports"
            @current-change="loadReports"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Document, Plus, Refresh, Loading, HomeFilled } from '@element-plus/icons-vue'
import {
  getReports,
  deleteReport,
  downloadAndSaveReport,
  formatReportType,
  formatReportStatus,
  getReportStatusOptions
} from '@/api/reports'

const router = useRouter()

// 数据
const loading = ref(false)
const reports = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const statusFilter = ref('')
const statusOptions = getReportStatusOptions()

// 加载报告列表
const loadReports = async () => {
  loading.value = true
  try {
    const params = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value
    }
    if (statusFilter.value) {
      params.status_filter = statusFilter.value
    }

    const response = await getReports(params)
    reports.value = response.reports || []
    total.value = response.total || 0
  } catch (error) {
    ElMessage.error('加载报告列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 下载报告
const downloadReport = async (report, format) => {
  try {
    const { success, error } = await downloadAndSaveReport(
      report.id,
      report.name,
      format
    )
    if (success) {
      ElMessage.success(`${format.toUpperCase()}文件下载成功`)
    } else {
      ElMessage.error(`下载失败: ${error}`)
    }
  } catch (error) {
    ElMessage.error('下载报告失败')
    console.error(error)
  }
}

// 删除报告
const handleDelete = async (report) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除报告"${report.name}"吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await deleteReport(report.id)
    ElMessage.success('报告已删除')
    loadReports()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除报告失败')
      console.error(error)
    }
  }
}

// 跳转到报告生成器
const goToGenerator = () => {
  router.push('/user/reports/generator')
}

// 返回首页
const goToHome = () => {
  router.push('/')
}

// 格式化报告类型
const getReportTypeInfo = (type) => {
  const info = formatReportType(type)
  return {
    text: info.text,
    type: type === 'summary' ? 'primary' : type === 'detailed' ? 'success' : 'warning'
  }
}

// 格式化状态
const getStatusInfo = (status) => {
  const info = formatReportStatus(status)
  return {
    text: info.text,
    type: info.type
  }
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

// 定时器引用
let refreshInterval = null

// 初始化
onMounted(() => {
  loadReports()

  // 自动刷新生成中的报告
  refreshInterval = setInterval(() => {
    const hasGenerating = reports.value.some(r => r.status === 'generating')
    if (hasGenerating) {
      loadReports()
    }
  }, 5000) // 每5秒刷新一次
})

// 清理定时器
onBeforeUnmount(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})
</script>

<style scoped>
.card-hover {
  @apply bg-white rounded-lg shadow-sm p-6 transition-all duration-200 hover:shadow-md;
}

.animate-fade-in {
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
