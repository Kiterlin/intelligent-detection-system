<template>
  <div class="min-h-screen bg-light-gray">
    <!-- 页面标题 -->
    <div class="bg-gradient-ocean py-12 mb-8">
      <div class="container-custom">
        <h1 class="text-3xl md:text-4xl font-bold text-white mb-2">告警日志</h1>
        <p class="text-white/80">查看所有告警触发历史和执行结果</p>
      </div>
    </div>

    <div class="container-custom pb-12">
      <!-- 过滤器 -->
      <div class="bg-white rounded-xl shadow-sm p-6 mb-6">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <!-- 状态筛选 -->
          <el-select
            v-model="statusFilter"
            placeholder="执行状态"
            clearable
            @change="loadLogs"
          >
            <el-option label="全部状态" :value="null" />
            <el-option label="成功" value="success" />
            <el-option label="失败" value="failed" />
            <el-option label="部分成功" value="partial" />
          </el-select>

          <!-- 规则筛选 -->
          <el-select
            v-model="ruleFilter"
            placeholder="告警规则"
            clearable
            filterable
            @change="loadLogs"
          >
            <el-option
              v-for="rule in availableRules"
              :key="rule.id"
              :label="rule.name"
              :value="rule.id"
            />
          </el-select>

          <!-- 刷新按钮 -->
          <el-button
            :icon="Refresh"
            @click="loadLogs"
          >
            刷新
          </el-button>
        </div>
      </div>

      <!-- 日志列表 -->
      <div class="bg-white rounded-xl shadow-sm overflow-hidden" v-loading="loading">
        <el-table
          :data="logs"
          stripe
          style="width: 100%"
          :empty-text="loading ? '加载中...' : '暂无数据'"
        >
          <el-table-column
            prop="id"
            label="ID"
            width="80"
          />

          <el-table-column
            prop="rule_name"
            label="规则名称"
            min-width="180"
          >
            <template #default="scope">
              <span class="font-medium">{{ scope.row.rule_name || '未知规则' }}</span>
            </template>
          </el-table-column>

          <el-table-column
            prop="detection_type"
            label="检测类型"
            width="100"
            align="center"
          >
            <template #default="scope">
              <el-tag
                :type="scope.row.detection_type === 'image' ? 'success' : 'primary'"
                size="small"
              >
                {{ scope.row.detection_type === 'image' ? '图像' : '视频' }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column
            label="触发条件"
            min-width="200"
          >
            <template #default="scope">
              <div class="text-sm">
                <div v-if="scope.row.conditions_met.target_classes">
                  类别: {{ scope.row.conditions_met.target_classes.join(', ') || '全部' }}
                </div>
                <div v-if="scope.row.conditions_met.matched_count">
                  数量: {{ scope.row.conditions_met.matched_count }} / {{ scope.row.conditions_met.min_count }}
                </div>
              </div>
            </template>
          </el-table-column>

          <el-table-column
            prop="status"
            label="执行状态"
            width="120"
            align="center"
          >
            <template #default="scope">
              <el-tag
                :type="getStatusType(scope.row.status)"
                size="small"
              >
                {{ getStatusText(scope.row.status) }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column
            prop="triggered_at"
            label="触发时间"
            width="180"
          >
            <template #default="scope">
              {{ formatDateTime(scope.row.triggered_at) }}
            </template>
          </el-table-column>

          <el-table-column
            label="操作"
            width="120"
            align="center"
            fixed="right"
          >
            <template #default="scope">
              <el-button
                size="small"
                @click="showDetail(scope.row)"
              >
                查看详情
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <div v-if="total > 0" class="flex justify-center p-4 border-t">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :total="total"
            :page-sizes="[20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            @current-change="loadLogs"
            @size-change="loadLogs"
          />
        </div>
      </div>
    </div>

    <!-- 详情对话框 -->
    <el-dialog
      v-model="detailVisible"
      title="告警日志详情"
      width="90%"
      :max-width="900"
    >
      <div v-if="currentLog" class="space-y-6">
        <!-- 基本信息 -->
        <div>
          <h3 class="text-lg font-bold text-deep-blue mb-4">基本信息</h3>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <p class="text-sm text-gray-500 mb-1">日志ID</p>
              <p class="text-base">{{ currentLog.id }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-500 mb-1">规则名称</p>
              <p class="text-base">{{ currentLog.rule_name }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-500 mb-1">检测ID</p>
              <p class="text-base">{{ currentLog.detection_id }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-500 mb-1">触发时间</p>
              <p class="text-base">{{ formatDateTime(currentLog.triggered_at) }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-500 mb-1">执行状态</p>
              <el-tag :type="getStatusType(currentLog.status)">
                {{ getStatusText(currentLog.status) }}
              </el-tag>
            </div>
          </div>
        </div>

        <!-- 满足的条件 -->
        <div>
          <h3 class="text-lg font-bold text-deep-blue mb-4">满足的条件</h3>
          <div class="bg-gray-50 rounded-lg p-4">
            <div class="space-y-2">
              <div v-if="currentLog.conditions_met.target_classes">
                <span class="text-sm text-gray-600">目标类别: </span>
                <span class="text-sm font-medium">
                  {{ currentLog.conditions_met.target_classes.join(', ') || '全部' }}
                </span>
              </div>
              <div v-if="currentLog.conditions_met.min_count">
                <span class="text-sm text-gray-600">最小数量: </span>
                <span class="text-sm font-medium">{{ currentLog.conditions_met.min_count }}</span>
              </div>
              <div v-if="currentLog.conditions_met.matched_count">
                <span class="text-sm text-gray-600">实际检测数量: </span>
                <span class="text-sm font-medium">{{ currentLog.conditions_met.matched_count }}</span>
              </div>
              <div v-if="currentLog.conditions_met.min_confidence !== undefined">
                <span class="text-sm text-gray-600">最小置信度: </span>
                <span class="text-sm font-medium">
                  {{ (currentLog.conditions_met.min_confidence * 100).toFixed(0) }}%
                </span>
              </div>
            </div>

            <!-- 检测详情 -->
            <div v-if="currentLog.conditions_met.matching_detections" class="mt-4">
              <p class="text-sm font-medium text-gray-700 mb-2">匹配的检测对象：</p>
              <div class="space-y-1">
                <div
                  v-for="(det, idx) in currentLog.conditions_met.matching_detections"
                  :key="idx"
                  class="text-sm bg-white rounded px-3 py-2"
                >
                  <span class="font-medium">{{ idx + 1 }}.</span>
                  类别: <span class="font-medium">{{ det.class }}</span> |
                  置信度: <span class="font-medium">{{ (det.confidence * 100).toFixed(1) }}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 执行的动作 -->
        <div>
          <h3 class="text-lg font-bold text-deep-blue mb-4">执行的动作</h3>
          <div class="space-y-3">
            <!-- 邮件通知 -->
            <div v-if="currentLog.actions_executed.email" class="bg-gray-50 rounded-lg p-4">
              <div class="flex items-center justify-between mb-2">
                <h4 class="font-medium">邮件通知</h4>
                <el-tag
                  :type="currentLog.actions_executed.email.success ? 'success' : 'danger'"
                  size="small"
                >
                  {{ currentLog.actions_executed.email.success ? '成功' : '失败' }}
                </el-tag>
              </div>
              <div class="text-sm space-y-1">
                <div v-if="currentLog.actions_executed.email.recipients">
                  <span class="text-gray-600">收件人: </span>
                  <span>{{ currentLog.actions_executed.email.recipients.join(', ') }}</span>
                </div>
                <div v-if="currentLog.actions_executed.email.subject">
                  <span class="text-gray-600">主题: </span>
                  <span>{{ currentLog.actions_executed.email.subject }}</span>
                </div>
                <div v-if="currentLog.actions_executed.email.error" class="text-red-600">
                  <span class="text-gray-600">错误: </span>
                  <span>{{ currentLog.actions_executed.email.error }}</span>
                </div>
              </div>
            </div>

            <!-- Webhook 通知 -->
            <div v-if="currentLog.actions_executed.webhook" class="bg-gray-50 rounded-lg p-4">
              <div class="flex items-center justify-between mb-2">
                <h4 class="font-medium">Webhook 通知</h4>
                <el-tag
                  :type="currentLog.actions_executed.webhook.success ? 'success' : 'danger'"
                  size="small"
                >
                  {{ currentLog.actions_executed.webhook.success ? '成功' : '失败' }}
                </el-tag>
              </div>
              <div class="text-sm space-y-1">
                <div v-if="currentLog.actions_executed.webhook.url">
                  <span class="text-gray-600">URL: </span>
                  <span class="break-all">{{ currentLog.actions_executed.webhook.url }}</span>
                </div>
                <div v-if="currentLog.actions_executed.webhook.status_code">
                  <span class="text-gray-600">状态码: </span>
                  <span>{{ currentLog.actions_executed.webhook.status_code }}</span>
                </div>
                <div v-if="currentLog.actions_executed.webhook.error" class="text-red-600">
                  <span class="text-gray-600">错误: </span>
                  <span>{{ currentLog.actions_executed.webhook.error }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { getAlertLogs, getAlertRules, formatAlertStatus } from '@/api/alerts'
import { formatDate } from '@/utils/helpers'

const route = useRoute()

// 数据
const loading = ref(false)
const logs = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const statusFilter = ref(null)
const ruleFilter = ref(null)

// 可用规则列表
const availableRules = ref([])

// 详情对话框
const detailVisible = ref(false)
const currentLog = ref(null)

// 格式化日期时间
const formatDateTime = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 获取状态类型
const getStatusType = (status) => {
  const statusInfo = formatAlertStatus(status)
  return statusInfo.type
}

// 获取状态文本
const getStatusText = (status) => {
  const statusInfo = formatAlertStatus(status)
  return statusInfo.text
}

// 加载规则列表（用于筛选）
const loadRules = async () => {
  try {
    const response = await getAlertRules({ skip: 0, limit: 100 })
    availableRules.value = response.items || []
  } catch (error) {
    console.error('加载规则列表失败:', error)
  }
}

// 加载日志列表
const loadLogs = async () => {
  loading.value = true
  try {
    const params = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value
    }

    if (statusFilter.value) {
      params.status = statusFilter.value
    }

    if (ruleFilter.value) {
      params.rule_id = ruleFilter.value
    }

    const response = await getAlertLogs(params)
    logs.value = response.items || []
    total.value = response.total || 0
  } catch (error) {
    ElMessage.error('加载日志失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

// 显示详情
const showDetail = (log) => {
  currentLog.value = log
  detailVisible.value = true
}

// 页面加载
onMounted(() => {
  // 如果URL有rule_id参数，自动设置过滤器
  if (route.query.rule_id) {
    ruleFilter.value = parseInt(route.query.rule_id)
  }

  loadRules()
  loadLogs()
})
</script>

<style scoped>
.container-custom {
  @apply max-w-7xl mx-auto px-4 sm:px-6 lg:px-8;
}
</style>
