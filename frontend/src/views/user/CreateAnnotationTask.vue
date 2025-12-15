<template>
  <div class="min-h-screen bg-light-gray">
    <!-- 页面头部 -->
    <PageHeader
      title="创建标注任务"
      subtitle="配置标注任务参数，为模型训练准备高质量标注数据"
    />

    <div class="container-custom pb-12">
      <div class="max-w-4xl mx-auto">
        <!-- 步骤导航 -->
        <el-steps :active="currentStep" finish-status="success" class="mb-8">
          <el-step title="基本信息" />
          <el-step title="配置标签" />
          <el-step title="选择数据源" />
          <el-step title="确认创建" />
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
            <!-- 步骤1: 基本信息 -->
            <div v-show="currentStep === 0">
              <h2 class="text-xl font-bold text-deep-blue mb-6">基本信息</h2>

              <el-form-item label="任务名称" prop="name">
                <el-input
                  v-model="formData.name"
                  placeholder="例如：行人检测标注任务 v1.0"
                  maxlength="100"
                  show-word-limit
                />
              </el-form-item>

              <el-form-item label="任务描述" prop="description">
                <el-input
                  v-model="formData.description"
                  type="textarea"
                  :rows="4"
                  placeholder="描述标注任务的目的、要求和注意事项"
                  maxlength="500"
                  show-word-limit
                />
              </el-form-item>
            </div>

            <!-- 步骤2: 配置标签 -->
            <div v-show="currentStep === 1">
              <h2 class="text-xl font-bold text-deep-blue mb-6">配置类别标签</h2>

              <el-form-item label="标注类别" prop="labels">
                <div class="space-y-3">
                  <!-- 已添加的标签 -->
                  <div v-if="formData.labels.length > 0" class="flex flex-wrap gap-2 p-4 bg-gray-50 rounded-lg">
                    <el-tag
                      v-for="(label, index) in formData.labels"
                      :key="index"
                      closable
                      size="large"
                      @close="removeLabel(index)"
                    >
                      {{ label }}
                    </el-tag>
                  </div>

                  <!-- 添加标签输入 -->
                  <div class="flex gap-2">
                    <el-input
                      v-model="newLabel"
                      placeholder="输入类别名称，例如：person, car, dog"
                      @keyup.enter="addLabel"
                    >
                      <template #prepend>
                        <el-icon><Stamp /></el-icon>
                      </template>
                    </el-input>
                    <el-button type="primary" :icon="Plus" @click="addLabel">
                      添加
                    </el-button>
                  </div>

                  <!-- 常用标签快捷选择 -->
                  <div class="mt-4">
                    <div class="text-sm text-gray-500 mb-2">常用标签快捷添加:</div>
                    <div class="flex flex-wrap gap-2">
                      <el-button
                        v-for="commonLabel in commonLabels"
                        :key="commonLabel"
                        size="small"
                        plain
                        @click="addCommonLabel(commonLabel)"
                        :disabled="formData.labels.includes(commonLabel)"
                      >
                        {{ commonLabel }}
                      </el-button>
                    </div>
                  </div>
                </div>
              </el-form-item>

              <el-alert
                type="info"
                :closable="false"
                class="mt-4"
              >
                <template #title>
                  <div class="text-sm">
                    提示：标签名称建议使用英文，避免使用特殊字符。至少需要添加一个类别标签。
                  </div>
                </template>
              </el-alert>
            </div>

            <!-- 步骤3: 选择数据源 -->
            <div v-show="currentStep === 2">
              <h2 class="text-xl font-bold text-deep-blue mb-6">选择数据源</h2>

              <el-form-item label="数据来源" prop="dataSource">
                <el-radio-group v-model="dataSourceType" class="w-full">
                  <div class="space-y-3">
                    <!-- 从数据集选择 -->
                    <div
                      class="border rounded-lg p-4 hover:border-blue-500 cursor-pointer transition-colors"
                      :class="{ 'border-blue-500 bg-blue-50': dataSourceType === 'dataset' }"
                      @click="dataSourceType = 'dataset'"
                    >
                      <el-radio label="dataset" class="w-full">
                        <div class="ml-2">
                          <div class="font-bold text-base">从数据集选择</div>
                          <div class="text-sm text-gray-500 mt-1">从已上传的数据集中选择图片进行标注</div>
                        </div>
                      </el-radio>
                    </div>

                    <!-- 从检测记录导入 -->
                    <div
                      class="border rounded-lg p-4 hover:border-blue-500 cursor-pointer transition-colors"
                      :class="{ 'border-blue-500 bg-blue-50': dataSourceType === 'detections' }"
                      @click="dataSourceType = 'detections'"
                    >
                      <el-radio label="detections" class="w-full">
                        <div class="ml-2">
                          <div class="font-bold text-base">从检测记录导入</div>
                          <div class="text-sm text-gray-500 mt-1">从已有的检测结果中导入作为预标注</div>
                        </div>
                      </el-radio>
                    </div>
                  </div>
                </el-radio-group>
              </el-form-item>

              <!-- 数据集选择 -->
              <el-form-item
                v-if="dataSourceType === 'dataset'"
                label="选择数据集"
                prop="dataset_id"
              >
                <el-select
                  v-model="formData.dataset_id"
                  placeholder="请选择数据集"
                  class="w-full"
                  filterable
                  @change="loadDatasetInfo"
                >
                  <el-option
                    v-for="dataset in availableDatasets"
                    :key="dataset.id"
                    :label="`${dataset.name} (${dataset.total_images || 0} 张图片)`"
                    :value="dataset.id"
                  />
                </el-select>
              </el-form-item>

              <!-- 检测记录选择 -->
              <el-form-item
                v-if="dataSourceType === 'detections'"
                label="选择检测记录"
                prop="detection_record_ids"
              >
                <el-select
                  v-model="formData.detection_record_ids"
                  multiple
                  placeholder="请选择检测记录（可多选）"
                  class="w-full"
                  filterable
                >
                  <el-option
                    v-for="record in availableDetections"
                    :key="record.id"
                    :label="`${record.image_name} - ${formatDate(record.created_at)}`"
                    :value="record.id"
                  />
                </el-select>
                <div class="text-xs text-gray-500 mt-2">
                  已选择 {{ formData.detection_record_ids?.length || 0 }} 条记录
                </div>
              </el-form-item>
            </div>

            <!-- 步骤4: 确认创建 -->
            <div v-show="currentStep === 3">
              <h2 class="text-xl font-bold text-deep-blue mb-6">确认任务配置</h2>

              <div class="space-y-4 bg-gray-50 rounded-lg p-6">
                <div class="flex justify-between">
                  <span class="text-gray-600">任务名称:</span>
                  <span class="font-semibold">{{ formData.name }}</span>
                </div>
                <div v-if="formData.description" class="flex justify-between">
                  <span class="text-gray-600">任务描述:</span>
                  <span class="font-semibold text-right max-w-md">{{ formData.description }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">类别标签:</span>
                  <span class="font-semibold">{{ formData.labels.length }} 个标签</span>
                </div>
                <div class="flex flex-wrap gap-2 mt-2">
                  <el-tag v-for="label in formData.labels" :key="label" size="small">
                    {{ label }}
                  </el-tag>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">数据来源:</span>
                  <span class="font-semibold">
                    {{ dataSourceType === 'dataset' ? '数据集' : '检测记录' }}
                  </span>
                </div>
                <div v-if="dataSourceType === 'dataset' && selectedDataset" class="flex justify-between">
                  <span class="text-gray-600">数据集名称:</span>
                  <span class="font-semibold">{{ selectedDataset.name }}</span>
                </div>
                <div v-if="dataSourceType === 'detections'" class="flex justify-between">
                  <span class="text-gray-600">检测记录:</span>
                  <span class="font-semibold">{{ formData.detection_record_ids?.length || 0 }} 条</span>
                </div>
              </div>

              <el-alert
                type="success"
                :closable="false"
                class="mt-6"
              >
                <template #title>
                  <div class="flex items-center">
                    <el-icon class="mr-2"><SuccessFilled /></el-icon>
                    任务创建后，将自动集成 Label Studio 进行在线标注
                  </div>
                </template>
              </el-alert>
            </div>

            <!-- 按钮组 -->
            <div class="flex justify-between mt-8 pt-6 border-t">
              <div>
                <el-button @click="goBack" v-if="currentStep === 0">
                  取消
                </el-button>
                <el-button @click="prevStep" v-else>
                  上一步
                </el-button>
              </div>
              <div>
                <el-button
                  v-if="currentStep < 3"
                  type="primary"
                  @click="nextStep"
                >
                  下一步
                </el-button>
                <el-button
                  v-else
                  type="primary"
                  :loading="submitting"
                  @click="submitForm"
                >
                  创建任务
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
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Plus,
  Stamp,
  SuccessFilled
} from '@element-plus/icons-vue'
import PageHeader from '@/components/common/PageHeader.vue'
import {
  createAnnotationTask,
  validateTaskData
} from '@/api/annotations'
import { getDatasets } from '@/api/dataset'
import { getDetectionHistory } from '@/api/detect'

const router = useRouter()

// 表单数据
const formRef = ref(null)
const currentStep = ref(0)
const submitting = ref(false)
const dataSourceType = ref('dataset')
const newLabel = ref('')

const formData = reactive({
  name: '',
  description: '',
  labels: [],
  dataset_id: null,
  detection_record_ids: []
})

// 表单验证规则
const formRules = {
  name: [
    { required: true, message: '请输入任务名称', trigger: 'blur' },
    { min: 2, max: 100, message: '长度在 2 到 100 个字符', trigger: 'blur' }
  ],
  labels: [
    {
      validator: (rule, value, callback) => {
        if (!value || value.length === 0) {
          callback(new Error('至少需要添加一个类别标签'))
        } else {
          callback()
        }
      },
      trigger: 'change'
    }
  ],
  dataset_id: [
    {
      validator: (rule, value, callback) => {
        if (dataSourceType.value === 'dataset' && !value) {
          callback(new Error('请选择数据集'))
        } else {
          callback()
        }
      },
      trigger: 'change'
    }
  ],
  detection_record_ids: [
    {
      validator: (rule, value, callback) => {
        if (dataSourceType.value === 'detections' && (!value || value.length === 0)) {
          callback(new Error('请选择至少一条检测记录'))
        } else {
          callback()
        }
      },
      trigger: 'change'
    }
  ]
}

// 常用标签
const commonLabels = [
  'person', 'car', 'bicycle', 'dog', 'cat',
  'motorcycle', 'bus', 'truck', 'traffic_light', 'stop_sign'
]

// 数据源
const availableDatasets = ref([])
const availableDetections = ref([])
const selectedDataset = ref(null)

// 添加标签
const addLabel = () => {
  const label = newLabel.value.trim()
  if (!label) {
    ElMessage.warning('请输入标签名称')
    return
  }
  if (formData.labels.includes(label)) {
    ElMessage.warning('标签已存在')
    return
  }
  formData.labels.push(label)
  newLabel.value = ''
}

// 添加常用标签
const addCommonLabel = (label) => {
  if (!formData.labels.includes(label)) {
    formData.labels.push(label)
  }
}

// 移除标签
const removeLabel = (index) => {
  formData.labels.splice(index, 1)
}

// 加载数据集信息
const loadDatasetInfo = () => {
  const dataset = availableDatasets.value.find(d => d.id === formData.dataset_id)
  selectedDataset.value = dataset
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 下一步
const nextStep = async () => {
  if (currentStep.value >= 3) return
  const fields = []
  if (currentStep.value === 0) {
    fields.push('name')
  } else if (currentStep.value === 1) {
    fields.push('labels')
  } else if (currentStep.value === 2) {
    if (dataSourceType.value === 'dataset') {
      fields.push('dataset_id')
    } else {
      fields.push('detection_record_ids')
    }
  }

  try {
    if (fields.length > 0) {
      for (const field of fields) {
        await formRef.value.validateField(field)
      }
    }
    currentStep.value++
  } catch (error) {
    console.log('表单验证失败:', error)
  }
}

// 上一步
const prevStep = () => {
  currentStep.value--
}

// 返回
const goBack = () => {
  router.push('/annotations/tasks')
}

// 提交表单
const submitForm = async () => {
  try {
    // 验证表单
    await formRef.value.validate()

    // 验证任务数据
    const errors = validateTaskData(formData)
    if (errors.length > 0) {
      ElMessage.error(errors[0])
      return
    }

    submitting.value = true

    // 准备提交数据
    const submitData = {
      name: formData.name,
      description: formData.description,
      class_labels: [...formData.labels]
    }

    if (dataSourceType.value === 'dataset') {
      submitData.dataset_id = formData.dataset_id
    } else {
      submitData.detection_record_ids = formData.detection_record_ids
    }

    // 创建任务
    await createAnnotationTask(submitData)

    ElMessage.success('标注任务创建成功')
    router.push('/annotations/tasks')
  } catch (error) {
    console.error('创建任务失败:', error)
    ElMessage.error(error.response?.data?.detail || '创建任务失败')
  } finally {
    submitting.value = false
  }
}

// 加载数据源
const loadDataSources = async () => {
  try {
    // 加载数据集
    const datasetsResponse = await getDatasets({ skip: 0, limit: 100 })
    availableDatasets.value = datasetsResponse.items || []

    // 加载检测记录
    const detectionsResponse = await getDetectionHistory({ page: 1, page_size: 100 })
    availableDetections.value = detectionsResponse.histories || []
  } catch (error) {
    console.error('加载数据源失败:', error)
    ElMessage.error('加载数据源失败')
  }
}

// 生命周期
onMounted(() => {
  loadDataSources()
})
</script>

<style scoped>
:deep(.el-step__title) {
  font-size: 14px;
}

:deep(.el-radio) {
  width: 100%;
  height: auto;
  margin-right: 0;
}

:deep(.el-radio__label) {
  width: 100%;
}
</style>
