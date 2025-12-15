<template>
  <div class="min-h-screen bg-light-gray">
    <!-- 页面标题 -->
    <div class="bg-gradient-ocean py-12 mb-8">
      <div class="container-custom">
        <h1 class="text-3xl md:text-4xl font-bold text-white mb-2">告警规则</h1>
        <p class="text-white/80">配置智能告警规则，在检测到特定目标时自动通知您</p>
      </div>
    </div>

    <div class="container-custom pb-12">
      <!-- 操作栏 -->
      <div class="flex flex-col md:flex-row gap-4 mb-6">
        <!-- 搜索框 -->
        <div class="flex-1">
          <el-input
            v-model="searchQuery"
            placeholder="搜索规则名称或描述..."
            clearable
            @clear="loadRules"
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <el-icon>
                <Search />
              </el-icon>
            </template>
          </el-input>
        </div>

        <!-- 过滤器 -->
        <el-select
          v-model="statusFilter"
          placeholder="状态筛选"
          clearable
          @change="loadRules"
          style="width: 150px"
        >
          <el-option label="全部" :value="null" />
          <el-option label="已启用" :value="true" />
          <el-option label="已禁用" :value="false" />
        </el-select>

        <!-- 返回首页按钮 -->
        <el-button :icon="HomeFilled" @click="goToHome">
          返回首页
        </el-button>

        <!-- 创建按钮 -->
        <el-button
          type="primary"
          :icon="Plus"
          @click="showCreateDialog"
        >
          创建规则
        </el-button>
      </div>

      <!-- 规则列表 -->
      <div v-loading="loading">
        <div
          v-if="rules.length === 0 && !loading"
          class="text-center py-20"
        >
          <el-icon :size="64" class="text-gray-300 mb-4">
            <Bell />
          </el-icon>
          <p class="text-gray-400 mb-4">还没有创建告警规则</p>
          <el-button type="primary" @click="showCreateDialog">
            立即创建
          </el-button>
        </div>

        <div
          v-else
          class="grid grid-cols-1 lg:grid-cols-2 gap-6"
        >
          <div
            v-for="rule in rules"
            :key="rule.id"
            class="card-hover animate-fade-in"
          >
            <!-- 规则头部 -->
            <div class="flex items-start justify-between mb-4">
              <div class="flex items-start flex-1">
                <div class="w-12 h-12 rounded-lg flex items-center justify-center mr-4 flex-shrink-0"
                     :class="rule.is_active ? 'bg-green-100' : 'bg-gray-100'">
                  <el-icon :size="24" :class="rule.is_active ? 'text-green-600' : 'text-gray-400'">
                    <Bell />
                  </el-icon>
                </div>
                <div class="flex-1 min-w-0">
                  <h3 class="text-lg font-bold text-deep-blue mb-1">
                    {{ rule.name }}
                  </h3>
                  <p
                    v-if="rule.description"
                    class="text-sm text-gray-500 line-clamp-2"
                  >
                    {{ rule.description }}
                  </p>
                </div>
              </div>

              <!-- 状态开关 -->
              <el-switch
                v-model="rule.is_active"
                @change="handleToggle(rule)"
                :loading="rule.toggling"
              />
            </div>

            <!-- 规则详情 -->
            <div class="space-y-3 mb-4 p-4 bg-gray-50 rounded-lg">
              <div>
                <p class="text-xs text-gray-500 mb-1">触发条件</p>
                <p class="text-sm text-deep-blue">
                  {{ formatConditions(rule.conditions) }}
                </p>
              </div>
              <div>
                <p class="text-xs text-gray-500 mb-1">执行动作</p>
                <p class="text-sm text-deep-blue">
                  {{ formatActions(rule.actions) }}
                </p>
              </div>
            </div>

            <!-- 统计信息 -->
            <div class="flex items-center justify-between text-xs text-gray-400 mb-4">
              <span>触发次数: {{ rule.trigger_count }}</span>
              <span>创建于 {{ formatDate(rule.created_at) }}</span>
            </div>

            <!-- 操作按钮 -->
            <div class="flex gap-2">
              <el-button
                size="small"
                @click="showEditDialog(rule)"
              >
                编辑
              </el-button>
              <el-button
                size="small"
                @click="viewLogs(rule.id)"
              >
                查看日志
              </el-button>
              <el-button
                size="small"
                type="danger"
                @click="handleDelete(rule)"
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
            @current-change="loadRules"
            @size-change="loadRules"
          />
        </div>
      </div>
    </div>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEditing ? '编辑告警规则' : '创建告警规则'"
      width="90%"
      :max-width="800"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="120px"
      >
        <!-- 基本信息 -->
        <el-form-item label="规则名称" prop="name">
          <el-input
            v-model="formData.name"
            placeholder="例如：高风险目标告警"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="规则描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="2"
            placeholder="描述此规则的用途"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="启用状态" prop="is_active">
          <el-switch v-model="formData.is_active" />
          <span class="ml-2 text-sm text-gray-500">
            {{ formData.is_active ? '已启用' : '已禁用' }}
          </span>
        </el-form-item>

        <el-divider content-position="left">触发条件</el-divider>

        <!-- 目标类别 -->
        <el-form-item label="目标类别" prop="conditions.target_classes">
          <el-select
            v-model="formData.conditions.target_classes"
            multiple
            filterable
            allow-create
            placeholder="选择或输入目标类别（留空表示所有类别）"
            style="width: 100%"
          >
            <el-option
              v-for="cls in commonClasses"
              :key="cls"
              :label="cls"
              :value="cls"
            />
          </el-select>
          <div class="text-xs text-gray-500 mt-1">
            常用类别：fish, shark, diver, coral, turtle
          </div>
        </el-form-item>

        <!-- 最小数量 -->
        <el-form-item label="最小数量" prop="conditions.min_count">
          <el-input-number
            v-model="formData.conditions.min_count"
            :min="1"
            :max="100"
            placeholder="1"
          />
          <span class="ml-2 text-sm text-gray-500">
            检测到至少多少个目标时触发
          </span>
        </el-form-item>

        <!-- 最小置信度 -->
        <el-form-item label="最小置信度" prop="conditions.min_confidence">
          <el-slider
            v-model="formData.conditions.min_confidence"
            :min="0"
            :max="1"
            :step="0.05"
            :format-tooltip="(val) => `${(val * 100).toFixed(0)}%`"
            style="width: 100%"
          />
          <div class="text-sm text-gray-500 mt-1">
            当前值: {{ (formData.conditions.min_confidence * 100).toFixed(0) }}%
          </div>
        </el-form-item>

        <el-divider content-position="left">执行动作</el-divider>

        <!-- 邮件通知 -->
        <el-form-item label="邮件通知">
          <el-switch v-model="formData.actions.email.enabled" />
        </el-form-item>

        <el-form-item
          v-if="formData.actions.email.enabled"
          label="收件人"
          prop="actions.email.recipients"
        >
          <el-select
            v-model="formData.actions.email.recipients"
            multiple
            filterable
            allow-create
            placeholder="输入邮箱地址后按回车"
            style="width: 100%"
          >
          </el-select>
          <div class="text-xs text-gray-500 mt-1">
            输入完整邮箱地址后按回车键添加
          </div>
        </el-form-item>

        <!-- Webhook 通知 -->
        <el-form-item label="Webhook通知">
          <el-switch v-model="formData.actions.webhook.enabled" />
        </el-form-item>

        <el-form-item
          v-if="formData.actions.webhook.enabled"
          label="Webhook URL"
          prop="actions.webhook.url"
        >
          <el-input
            v-model="formData.actions.webhook.url"
            placeholder="https://example.com/webhook"
          />
        </el-form-item>

        <el-form-item
          v-if="formData.actions.webhook.enabled"
          label="HTTP方法"
        >
          <el-select v-model="formData.actions.webhook.method">
            <el-option label="POST" value="POST" />
            <el-option label="GET" value="GET" />
            <el-option label="PUT" value="PUT" />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          :loading="submitting"
          @click="handleSubmit"
        >
          {{ isEditing ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Bell, HomeFilled } from '@element-plus/icons-vue'
import {
  getAlertRules,
  createAlertRule,
  updateAlertRule,
  deleteAlertRule,
  toggleAlertRule,
  formatConditions,
  formatActions
} from '@/api/alerts'
import { formatDate } from '@/utils/helpers'

const router = useRouter()

// 数据
const loading = ref(false)
const rules = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const searchQuery = ref('')
const statusFilter = ref(null)

// 对话框
const dialogVisible = ref(false)
const isEditing = ref(false)
const submitting = ref(false)
const formRef = ref(null)
const currentRuleId = ref(null)

// 常用类别
const commonClasses = ['fish', 'shark', 'diver', 'coral', 'turtle', 'octopus', 'whale', 'dolphin']

// 表单数据
const formData = reactive({
  name: '',
  description: '',
  is_active: true,
  conditions: {
    target_classes: [],
    min_count: 1,
    min_confidence: 0.5
  },
  actions: {
    email: {
      enabled: false,
      recipients: []
    },
    webhook: {
      enabled: false,
      url: '',
      method: 'POST'
    }
  }
})

// 表单验证规则
const formRules = {
  name: [
    { required: true, message: '请输入规则名称', trigger: 'blur' },
    { min: 1, max: 100, message: '长度在 1 到 100 个字符', trigger: 'blur' }
  ],
  'actions.email.recipients': [
    {
      validator: (rule, value, callback) => {
        if (formData.actions.email.enabled && (!value || value.length === 0)) {
          callback(new Error('启用邮件通知时必须至少添加一个收件人'))
        } else {
          callback()
        }
      },
      trigger: 'change'
    }
  ],
  'actions.webhook.url': [
    {
      validator: (rule, value, callback) => {
        if (formData.actions.webhook.enabled && !value) {
          callback(new Error('启用Webhook通知时必须填写URL'))
        } else if (formData.actions.webhook.enabled && !value.startsWith('http')) {
          callback(new Error('URL必须以http://或https://开头'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 加载规则列表
const loadRules = async () => {
  loading.value = true
  try {
    const params = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value
    }

    if (searchQuery.value) {
      params.search = searchQuery.value
    }

    if (statusFilter.value !== null) {
      params.is_active = statusFilter.value
    }

    const response = await getAlertRules(params)
    rules.value = (response.items || []).map(rule => ({
      ...rule,
      toggling: false
    }))
    total.value = response.total || 0
  } catch (error) {
    ElMessage.error('加载规则列表失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  loadRules()
}

// 显示创建对话框
const showCreateDialog = () => {
  isEditing.value = false
  currentRuleId.value = null
  resetForm()
  dialogVisible.value = true
}

// 显示编辑对话框
const showEditDialog = (rule) => {
  isEditing.value = true
  currentRuleId.value = rule.id

  formData.name = rule.name
  formData.description = rule.description || ''
  formData.is_active = rule.is_active
  formData.conditions = { ...rule.conditions }
  formData.actions = JSON.parse(JSON.stringify(rule.actions))

  dialogVisible.value = true
}

// 重置表单
const resetForm = () => {
  formData.name = ''
  formData.description = ''
  formData.is_active = true
  formData.conditions = {
    target_classes: [],
    min_count: 1,
    min_confidence: 0.5
  }
  formData.actions = {
    email: {
      enabled: false,
      recipients: []
    },
    webhook: {
      enabled: false,
      url: '',
      method: 'POST'
    }
  }

  if (formRef.value) {
    formRef.value.clearValidate()
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    // 验证至少启用一个动作
    if (!formData.actions.email.enabled && !formData.actions.webhook.enabled) {
      ElMessage.error('请至少启用一个通知方式（邮件或Webhook）')
      return
    }

    submitting.value = true
    try {
      const data = {
        name: formData.name,
        description: formData.description,
        is_active: formData.is_active,
        conditions: formData.conditions,
        actions: formData.actions
      }

      if (isEditing.value) {
        await updateAlertRule(currentRuleId.value, data)
        ElMessage.success('更新规则成功')
      } else {
        await createAlertRule(data)
        ElMessage.success('创建规则成功')
      }

      dialogVisible.value = false
      loadRules()
    } catch (error) {
      ElMessage.error(
        (isEditing.value ? '更新' : '创建') + '规则失败: ' +
        (error.response?.data?.detail || error.message)
      )
    } finally {
      submitting.value = false
    }
  })
}

// 切换启用状态
const handleToggle = async (rule) => {
  rule.toggling = true
  try {
    await toggleAlertRule(rule.id, rule.is_active)
    ElMessage.success(rule.is_active ? '已启用规则' : '已禁用规则')
  } catch (error) {
    rule.is_active = !rule.is_active // 恢复状态
    ElMessage.error('切换状态失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    rule.toggling = false
  }
}

// 删除规则
const handleDelete = async (rule) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除规则"${rule.name}"吗？此操作将同时删除所有相关的告警日志。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await deleteAlertRule(rule.id)
    ElMessage.success('删除成功')
    loadRules()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败: ' + (error.response?.data?.detail || error.message))
    }
  }
}

// 查看日志
const viewLogs = (ruleId) => {
  router.push({ name: 'AlertLogs', query: { rule_id: ruleId } })
}

// 返回首页
const goToHome = () => {
  router.push('/')
}

// 页面加载
onMounted(() => {
  loadRules()
})
</script>

<style scoped>
.card-hover {
  @apply bg-white rounded-xl shadow-sm p-6 transition-all duration-300;
}

.card-hover:hover {
  @apply shadow-lg transform -translate-y-1;
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
