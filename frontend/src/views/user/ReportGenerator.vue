<template>
  <div class="min-h-screen bg-light-gray">
    <!-- 页面标题 -->
    <div class="bg-gradient-ocean py-12 mb-8">
      <div class="container-custom">
        <h1 class="text-3xl md:text-4xl font-bold text-white mb-2">生成报告</h1>
        <p class="text-white/80">配置并生成检测分析报告</p>
      </div>
    </div>

    <div class="container-custom pb-12">
      <div class="max-w-4xl mx-auto">
        <!-- 步骤导航 -->
        <el-steps :active="currentStep" finish-status="success" class="mb-8">
          <el-step title="选择类型" />
          <el-step title="配置参数" />
          <el-step title="生成报告" />
        </el-steps>

        <!-- 表单容器 -->
        <div class="bg-white rounded-lg shadow-sm p-8">
          <el-form
            ref="formRef"
            :model="formData"
            :rules="formRules"
            label-width="120px"
            label-position="top"
          >
            <!-- 步骤1: 选择报告类型 -->
            <div v-show="currentStep === 0">
              <h2 class="text-xl font-bold text-deep-blue mb-6">选择报告类型</h2>

              <el-form-item label="报告名称" prop="name">
                <el-input
                  v-model="formData.name"
                  placeholder="请输入报告名称"
                  maxlength="100"
                  show-word-limit
                />
              </el-form-item>

              <el-form-item label="报告类型" prop="report_type">
                <el-radio-group v-model="formData.report_type" class="w-full">
                  <div class="space-y-3">
                    <div
                      v-for="type in reportTypes"
                      :key="type.value"
                      class="border rounded-lg p-4 hover:border-blue-500 cursor-pointer transition-colors"
                      :class="{ 'border-blue-500 bg-blue-50': formData.report_type === type.value }"
                      @click="formData.report_type = type.value"
                    >
                      <el-radio :label="type.value" class="w-full">
                        <div class="ml-2">
                          <div class="font-bold text-base">{{ type.title }}</div>
                          <div class="text-sm text-gray-500 mt-1">{{ type.description }}</div>
                        </div>
                      </el-radio>
                    </div>
                  </div>
                </el-radio-group>
              </el-form-item>
            </div>

            <!-- 步骤2: 配置参数 -->
            <div v-show="currentStep === 1">
              <h2 class="text-xl font-bold text-deep-blue mb-6">配置报告参数</h2>

              <!-- 时间范围 -->
              <el-form-item label="时间范围">
                <el-date-picker
                  v-model="dateRange"
                  type="daterange"
                  range-separator="至"
                  start-placeholder="开始日期"
                  end-placeholder="结束日期"
                  value-format="YYYY-MM-DD"
                  class="w-full"
                />
              </el-form-item>

              <!-- 对比报告特有: 选择模型 -->
              <el-form-item
                v-if="formData.report_type === 'comparison'"
                label="选择模型（至少2个）"
                prop="model_ids"
              >
                <el-select
                  v-model="formData.parameters.filters.model_ids"
                  multiple
                  placeholder="请选择要对比的模型"
                  class="w-full"
                >
                  <el-option
                    v-for="model in availableModels"
                    :key="model.id"
                    :label="model.name"
                    :value="model.id"
                  />
                </el-select>
              </el-form-item>

              <!-- 其他报告: 选择单个模型（可选） -->
              <el-form-item
                v-else
                label="筛选模型（可选）"
              >
                <el-select
                  v-model="formData.parameters.filters.model_id"
                  clearable
                  placeholder="选择模型（留空表示全部）"
                  class="w-full"
                >
                  <el-option
                    v-for="model in availableModels"
                    :key="model.id"
                    :label="model.name"
                    :value="model.id"
                  />
                </el-select>
              </el-form-item>

              <!-- 检测类型筛选 -->
              <el-form-item label="检测类型">
                <el-select
                  v-model="formData.parameters.filters.detection_type"
                  clearable
                  placeholder="选择检测类型（留空表示全部）"
                  class="w-full"
                >
                  <el-option label="图片检测" value="image" />
                  <el-option label="视频检测" value="video" />
                </el-select>
              </el-form-item>
            </div>

            <!-- 步骤3: 确认生成 -->
            <div v-show="currentStep === 2">
              <h2 class="text-xl font-bold text-deep-blue mb-6">确认报告配置</h2>

              <div class="space-y-4 bg-gray-50 rounded-lg p-6">
                <div class="flex justify-between">
                  <span class="text-gray-600">报告名称:</span>
                  <span class="font-semibold">{{ formData.name }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">报告类型:</span>
                  <span class="font-semibold">
                    {{ reportTypes.find(t => t.value === formData.report_type)?.title }}
                  </span>
                </div>
                <div v-if="dateRange && dateRange.length === 2" class="flex justify-between">
                  <span class="text-gray-600">时间范围:</span>
                  <span class="font-semibold">{{ dateRange[0] }} 至 {{ dateRange[1] }}</span>
                </div>
                <div v-if="formData.report_type === 'comparison'" class="flex justify-between">
                  <span class="text-gray-600">对比模型:</span>
                  <span class="font-semibold">
                    已选择 {{ formData.parameters.filters.model_ids?.length || 0 }} 个模型
                  </span>
                </div>
              </div>

              <el-alert
                type="info"
                :closable="false"
                class="mt-6"
              >
                <template #title>
                  <div class="flex items-center">
                    <el-icon class="mr-2"><InfoFilled /></el-icon>
                    报告将在后台异步生成，生成完成后可在报告列表中下载
                  </div>
                </template>
              </el-alert>
            </div>

            <!-- 按钮组 -->
            <div class="flex justify-between mt-8 pt-6 border-t">
              <div>
                <el-button @click="goBack">
                  返回列表
                </el-button>
              </div>
              <div class="flex gap-3">
                <el-button
                  v-if="currentStep > 0"
                  @click="prevStep"
                >
                  上一步
                </el-button>
                <el-button
                  v-if="currentStep < 2"
                  type="primary"
                  @click="nextStep"
                >
                  下一步
                </el-button>
                <el-button
                  v-if="currentStep === 2"
                  type="primary"
                  :loading="submitting"
                  @click="submitForm"
                >
                  生成报告
                </el-button>
              </div>
            </div>
          </el-form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { InfoFilled } from '@element-plus/icons-vue'
import { createReport, validateReportParameters } from '@/api/reports'
import { getActiveModels } from '@/api/detect'

const router = useRouter()

// 数据
const currentStep = ref(0)
const submitting = ref(false)
const formRef = ref(null)
const dateRange = ref([])
const availableModels = ref([])

// 报告类型选项
const reportTypes = [
  {
    value: 'summary',
    title: '概要报告',
    description: '1页快速概览，包含关键统计信息和图表，适合快速查看'
  },
  {
    value: 'detailed',
    title: '详细报告',
    description: '完整的多页分析报告，包含详细的统计数据、趋势图和记录列表'
  },
  {
    value: 'comparison',
    title: '对比报告',
    description: '多模型性能对比报告，横向对比不同模型的检测效果'
  }
]

// 表单数据
const formData = reactive({
  name: '',
  report_type: 'summary',
  parameters: {
    time_range: {},
    filters: {
      model_id: null,
      model_ids: [],
      detection_type: null
    }
  }
})

// 表单验证规则
const formRules = {
  name: [
    { required: true, message: '请输入报告名称', trigger: 'blur' },
    { min: 2, max: 100, message: '长度在 2 到 100 个字符', trigger: 'blur' }
  ],
  report_type: [
    { required: true, message: '请选择报告类型', trigger: 'change' }
  ],
  model_ids: [
    {
      validator: (rule, value, callback) => {
        if (formData.report_type === 'comparison' && (!value || value.length < 2)) {
          callback(new Error('对比报告至少需要选择2个模型'))
        } else {
          callback()
        }
      },
      trigger: 'change'
    }
  ]
}

// 加载可用模型
const loadModels = async () => {
  try {
    const res = await getActiveModels()
    availableModels.value = res.models || []
  } catch (error) {
    console.error('加载模型列表失败', error)
  }
}

// 下一步
const nextStep = async () => {
  if (currentStep.value === 0) {
    // 验证第一步
    try {
      await formRef.value.validateField(['name', 'report_type'])
      currentStep.value++
    } catch (error) {
      console.error('表单验证失败', error)
    }
  } else if (currentStep.value === 1) {
    // 验证第二步
    const errors = validateReportParameters(formData.report_type, formData.parameters)
    if (errors.length > 0) {
      ElMessage.error(errors[0])
      return
    }
    currentStep.value++
  }
}

// 上一步
const prevStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

// 返回列表
const goBack = () => {
  router.push('/user/reports')
}

// 提交表单
const submitForm = async () => {
  submitting.value = true
  try {
    // 构建时间范围
    if (dateRange.value && dateRange.value.length === 2) {
      formData.parameters.time_range = {
        start: dateRange.value[0],
        end: dateRange.value[1]
      }
    }

    // 创建报告
    await createReport(formData)

    ElMessage.success('报告生成任务已提交，请在报告列表中查看进度')

    // 返回列表页
    setTimeout(() => {
      router.push('/user/reports')
    }, 1500)
  } catch (error) {
    ElMessage.error('创建报告失败: ' + (error.message || '未知错误'))
    console.error(error)
  } finally {
    submitting.value = false
  }
}

// 监听报告类型变化，清空模型选择
watch(() => formData.report_type, () => {
  formData.parameters.filters.model_id = null
  formData.parameters.filters.model_ids = []
})

// 初始化
onMounted(() => {
  loadModels()

  // 生成默认报告名称
  const now = new Date()
  const dateStr = now.toLocaleDateString('zh-CN').replace(/\//g, '-')
  formData.name = `检测报告_${dateStr}`
})
</script>

<style scoped>
:deep(.el-step__title) {
  font-size: 14px;
}
</style>
