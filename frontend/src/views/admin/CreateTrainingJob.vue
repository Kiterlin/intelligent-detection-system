<template>
  <div class="min-h-screen bg-light-gray">
    <!-- 页面头部 -->
    <PageHeader
      title="创建训练任务"
      subtitle="配置 YOLO 模型训练参数，使用标注数据训练自定义检测模型"
    />

    <div class="container-custom pb-12">
      <div class="max-w-5xl mx-auto">
        <!-- 步骤导航 -->
        <el-steps :active="currentStep" finish-status="success" class="mb-8">
          <el-step title="基本信息" />
          <el-step title="选择模型" />
          <el-step title="训练参数" />
          <el-step title="确认创建" />
        </el-steps>

        <!-- 表单容器 -->
        <div class="bg-white rounded-lg shadow-sm p-8">
          <el-form
            ref="formRef"
            :model="formData"
            :rules="formRules"
            label-width="140px"
            label-position="top"
          >
            <!-- 步骤1: 基本信息 -->
            <div v-show="currentStep === 0">
              <h2 class="text-xl font-bold text-deep-blue mb-6">基本信息</h2>

              <el-form-item label="任务名称" prop="name">
                <el-input
                  v-model="formData.name"
                  placeholder="例如：YOLOv8s 行人检测模型 v1.0"
                  maxlength="100"
                  show-word-limit
                />
              </el-form-item>

              <el-form-item label="选择标注任务" prop="annotation_task_id">
                <el-select
                  v-model="formData.annotation_task_id"
                  placeholder="选择已完成的标注任务作为训练数据源"
                  class="w-full"
                  filterable
                  @change="loadTaskInfo"
                >
                  <el-option
                    v-for="task in availableTasks"
                    :key="task.id"
                    :label="`${task.name} (${task.annotated_images || 0} 张已标注图片)`"
                    :value="task.id"
                    :disabled="!task.annotated_images || task.annotated_images === 0"
                  />
                </el-select>
                <div v-if="selectedTask" class="mt-2 p-3 bg-blue-50 rounded text-sm">
                  <div class="flex items-center justify-between mb-1">
                    <span class="text-gray-600">已标注图片:</span>
                    <span class="font-medium">{{ selectedTask.annotated_images }} 张</span>
                  </div>
                  <div class="flex items-center justify-between mb-1">
                    <span class="text-gray-600">标注对象数:</span>
                    <span class="font-medium">{{ selectedTask.total_annotations }} 个</span>
                  </div>
                  <div class="flex flex-wrap gap-1 mt-2">
                    <el-tag v-for="label in selectedTask.labels" :key="label" size="small">
                      {{ label }}
                    </el-tag>
                  </div>
                </div>
              </el-form-item>
            </div>

            <!-- 步骤2: 选择模型 -->
            <div v-show="currentStep === 1">
              <h2 class="text-xl font-bold text-deep-blue mb-6">选择基础模型</h2>

              <el-form-item label="选择模型" prop="base_model_id">
                <template v-if="availableBaseModels.length > 0">
                  <el-radio-group v-model="formData.base_model_id" class="w-full">
                    <div class="space-y-3">
                      <div
                        v-for="model in availableBaseModels"
                        :key="model.id"
                        class="border rounded-lg p-4 hover:border-blue-500 cursor-pointer transition-colors"
                        :class="{ 'border-blue-500 bg-blue-50': formData.base_model_id === model.id }"
                        @click="formData.base_model_id = model.id"
                      >
                        <el-radio :label="model.id" class="w-full">
                          <div class="ml-2">
                            <div class="flex items-center justify-between">
                              <div class="font-bold text-base">{{ model.name }}</div>
                              <el-tag size="small" type="info">
                                {{ model.version || '未标记' }}
                              </el-tag>
                            </div>
                            <div class="text-sm text-gray-500 mt-1">
                              {{ model.description || '暂无描述' }}
                            </div>
                          </div>
                        </el-radio>
                      </div>
                    </div>
                  </el-radio-group>
                </template>
                <template v-else>
                  <el-alert
                    title="尚未上传可用的基础模型，请先在模型管理中上传或启用模型。"
                    type="warning"
                    :closable="false"
                  />
                </template>
              </el-form-item>
            </div>

            <!-- 步骤3: 训练参数 -->
            <div v-show="currentStep === 2">
              <h2 class="text-xl font-bold text-deep-blue mb-6">配置训练参数</h2>

              <!-- 基础参数 -->
              <div class="mb-8">
                <h3 class="text-lg font-semibold text-deep-blue mb-4">基础参数</h3>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <el-form-item label="训练轮次 (epochs)" prop="training_params.epochs">
                    <el-input-number
                      v-model="formData.training_params.epochs"
                      :min="1"
                      :max="1000"
                      class="w-full"
                    />
                    <div class="text-xs text-gray-500 mt-1">
                      推荐: 100-300 轮，数据越多轮次可越少
                    </div>
                  </el-form-item>

                  <el-form-item label="批次大小 (batch)" prop="training_params.batch_size">
                    <el-input-number
                      v-model="formData.training_params.batch_size"
                      :min="1"
                      :max="128"
                      class="w-full"
                    />
                    <div class="text-xs text-gray-500 mt-1">
                      推荐: 16-32，取决于显存大小
                    </div>
                  </el-form-item>

                  <el-form-item label="图像尺寸 (imgsz)" prop="training_params.img_size">
                    <el-select v-model="formData.training_params.img_size" class="w-full">
                      <el-option :value="320" label="320 - 快速训练" />
                      <el-option :value="640" label="640 - 推荐" />
                      <el-option :value="1280" label="1280 - 高精度" />
                    </el-select>
                  </el-form-item>

                  <el-form-item label="计算设备 (device)" prop="training_params.device">
                    <el-select v-model="formData.training_params.device" class="w-full">
                      <el-option value="cuda:0" label="GPU (cuda:0)" />
                      <el-option value="cpu" label="CPU" />
                    </el-select>
                  </el-form-item>
                </div>
              </div>

              <!-- 高级参数（可折叠） -->
              <el-collapse v-model="activeCollapse">
                <el-collapse-item title="高级参数（可选）" name="advanced">
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <el-form-item label="优化器 (optimizer)">
                      <el-select v-model="formData.training_params.optimizer" class="w-full">
                        <el-option value="auto" label="Auto - 自动选择" />
                        <el-option value="SGD" label="SGD" />
                        <el-option value="Adam" label="Adam" />
                        <el-option value="AdamW" label="AdamW" />
                      </el-select>
                    </el-form-item>

                    <el-form-item label="初始学习率 (lr0)">
                      <el-input-number
                        v-model="formData.training_params.lr0"
                        :min="0.0001"
                        :max="1"
                        :step="0.001"
                        :precision="4"
                        class="w-full"
                      />
                    </el-form-item>

                    <el-form-item label="最终学习率 (lrf)">
                      <el-input-number
                        v-model="formData.training_params.lrf"
                        :min="0.0001"
                        :max="1"
                        :step="0.001"
                        :precision="4"
                        class="w-full"
                      />
                    </el-form-item>

                    <el-form-item label="动量 (momentum)">
                      <el-input-number
                        v-model="formData.training_params.momentum"
                        :min="0"
                        :max="1"
                        :step="0.001"
                        :precision="3"
                        class="w-full"
                      />
                    </el-form-item>

                    <el-form-item label="权重衰减 (weight_decay)">
                      <el-input-number
                        v-model="formData.training_params.weight_decay"
                        :min="0"
                        :max="0.01"
                        :step="0.0001"
                        :precision="4"
                        class="w-full"
                      />
                    </el-form-item>

                    <el-form-item label="预热轮次 (warmup_epochs)">
                      <el-input-number
                        v-model="formData.training_params.warmup_epochs"
                        :min="0"
                        :max="10"
                        class="w-full"
                      />
                    </el-form-item>

                    <el-form-item label="早停耐心 (patience)">
                      <el-input-number
                        v-model="formData.training_params.patience"
                        :min="0"
                        :max="100"
                        class="w-full"
                      />
                      <div class="text-xs text-gray-500 mt-1">
                        0 表示关闭早停
                      </div>
                    </el-form-item>

                    <el-form-item label="保存周期 (save_period)">
                      <el-input-number
                        v-model="formData.training_params.save_period"
                        :min="1"
                        :max="100"
                        class="w-full"
                      />
                      <div class="text-xs text-gray-500 mt-1">
                        每 N 轮保存一次模型
                      </div>
                    </el-form-item>
                  </div>
                </el-collapse-item>
              </el-collapse>
            </div>

            <!-- 步骤4: 确认创建 -->
            <div v-show="currentStep === 3">
              <h2 class="text-xl font-bold text-deep-blue mb-6">确认训练配置</h2>

              <div class="space-y-6">
                <!-- 基本信息 -->
                <div class="bg-gray-50 rounded-lg p-6">
                  <h3 class="font-semibold mb-4">基本信息</h3>
                  <div class="space-y-2">
                    <div class="flex justify-between">
                      <span class="text-gray-600">任务名称:</span>
                      <span class="font-semibold">{{ formData.name }}</span>
                    </div>
                    <div class="flex justify-between">
                      <span class="text-gray-600">基础模型:</span>
                      <span class="font-semibold">{{ selectedBaseModel?.name || '-' }}</span>
                    </div>
                    <div v-if="selectedTask" class="flex justify-between">
                      <span class="text-gray-600">训练数据:</span>
                      <span class="font-semibold">
                        {{ selectedTask.name }} ({{ selectedTask.annotated_images }} 张图片)
                      </span>
                    </div>
                  </div>
                </div>

                <!-- 训练参数 -->
                <div class="bg-blue-50 rounded-lg p-6">
                  <h3 class="font-semibold mb-4">训练参数</h3>
                  <div class="grid grid-cols-2 gap-3 text-sm">
                    <div class="flex justify-between">
                      <span class="text-gray-600">训练轮次:</span>
                      <span class="font-medium">{{ formData.training_params.epochs }}</span>
                    </div>
                    <div class="flex justify-between">
                      <span class="text-gray-600">批次大小:</span>
                      <span class="font-medium">{{ formData.training_params.batch_size }}</span>
                    </div>
                    <div class="flex justify-between">
                      <span class="text-gray-600">图像尺寸:</span>
                      <span class="font-medium">{{ formData.training_params.img_size }}</span>
                    </div>
                    <div class="flex justify-between">
                      <span class="text-gray-600">计算设备:</span>
                      <span class="font-medium">{{ formData.training_params.device }}</span>
                    </div>
                  </div>
                </div>

                <el-alert
                  type="warning"
                  :closable="false"
                >
                  <template #title>
                    <div class="text-sm">
                      <strong>注意事项：</strong>
                      <ul class="list-disc ml-5 mt-2 space-y-1">
                        <li>训练过程将在后台执行，可能需要数小时到数天</li>
                        <li>请确保服务器有足够的存储空间和计算资源</li>
                        <li>训练过程中可以在监控页面查看实时进度和日志</li>
                        <li>建议先使用较小的轮次进行测试训练</li>
                      </ul>
                    </div>
                  </template>
                </el-alert>
              </div>
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
                  开始训练
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
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import PageHeader from '@/components/common/PageHeader.vue'
import {
  createTrainingJob,
  getDefaultTrainingParams,
  validateTrainingParams
} from '@/api/training'
import { getAnnotationTasks } from '@/api/annotations'
import { getModelList } from '@/api/admin'

const router = useRouter()

// 表单数据
const formRef = ref(null)
const currentStep = ref(0)
const submitting = ref(false)
const activeCollapse = ref([])

const formData = reactive({
  name: '',
  annotation_task_id: null,
  base_model_id: null,
  training_params: getDefaultTrainingParams()
})

// 表单验证规则
const formRules = {
  name: [
    { required: true, message: '请输入任务名称', trigger: 'blur' },
    { min: 2, max: 100, message: '长度在 2 到 100 个字符', trigger: 'blur' }
  ],
  annotation_task_id: [
    { required: true, message: '请选择标注任务', trigger: 'change' }
  ],
  base_model_id: [
    { required: true, message: '请选择基础模型', trigger: 'change' }
  ],
  'training_params.epochs': [
    { required: true, message: '请输入训练轮次', trigger: 'blur' }
  ],
  'training_params.batch_size': [
    { required: true, message: '请输入批次大小', trigger: 'blur' }
  ]
}

// 数据源
const availableTasks = ref([])
const selectedTask = ref(null)
const availableBaseModels = ref([])
const selectedBaseModel = computed(() => {
  if (!formData.base_model_id) return null
  return availableBaseModels.value.find(model => model.id === formData.base_model_id) || null
})

// 加载标注任务
const loadAnnotationTasks = async () => {
  try {
    const response = await getAnnotationTasks({ skip: 0, limit: 100, status: 'completed' })
    availableTasks.value = (response.items || []).map(task => ({
      ...task,
      labels: Array.isArray(task.labels) && task.labels.length > 0
        ? task.labels
        : (task.class_labels || [])
    }))
  } catch (error) {
    console.error('加载标注任务失败:', error)
    ElMessage.error('加载标注任务失败')
  }
}

// 加载任务信息
const loadTaskInfo = () => {
  const task = availableTasks.value.find(t => t.id === formData.annotation_task_id)
  selectedTask.value = task
}

// 加载基础模型列表
const loadBaseModels = async () => {
  try {
    const response = await getModelList({ page: 1, page_size: 100, status: 'active' })
    availableBaseModels.value = response.models || response.items || []

    if (!formData.base_model_id && availableBaseModels.value.length > 0) {
      formData.base_model_id = availableBaseModels.value[0].id
    }
  } catch (error) {
    console.error('加载基础模型失败:', error)
    ElMessage.error('加载基础模型失败')
  }
}

// 下一步
const nextStep = async () => {
  if (currentStep.value >= 3) return
  const fields = []
  if (currentStep.value === 0) {
    fields.push('name', 'annotation_task_id')
  } else if (currentStep.value === 1) {
    fields.push('base_model_id')
  } else if (currentStep.value === 2) {
    fields.push('training_params.epochs', 'training_params.batch_size')
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
  router.push('/admin/training')
}

// 提交表单
const submitForm = async () => {
  try {
    // 验证表单
    await formRef.value.validate()

    // 验证训练参数
    const errors = validateTrainingParams(formData.training_params)
    if (errors.length > 0) {
      ElMessage.error(errors[0])
      return
    }

    submitting.value = true

    const baseModel = selectedBaseModel.value
    if (!baseModel) {
      ElMessage.error('请选择基础模型')
      submitting.value = false
      return
    }

    const taskInfo = selectedTask.value
    if (!taskInfo) {
      ElMessage.error('请选择标注任务')
      submitting.value = false
      return
    }

    const datasetConfig = {
      source: 'annotations',
      annotation_task_id: formData.annotation_task_id,
      split_ratio: { train: 0.8, val: 0.15, test: 0.05 },
      classes: taskInfo.labels || []
    }

    const configJson = {
      base_model: baseModel.name,
      epochs: formData.training_params.epochs,
      batch_size: formData.training_params.batch_size,
      img_size: formData.training_params.img_size,
      learning_rate: formData.training_params.lr0 || 0.01,
      optimizer: formData.training_params.optimizer || 'auto',
      device: formData.training_params.device === 'cpu' ? 'cpu' : '0',
      workers: 8,
      patience: formData.training_params.patience || 50
    }

    const submitData = {
      job_name: formData.name,
      base_model_id: baseModel.id,
      config_json: configJson,
      dataset_config: datasetConfig
    }

    const response = await createTrainingJob(submitData)

    ElMessage.success('训练任务创建成功，已开始训练')
    router.push(`/admin/training/${response.id}`)
  } catch (error) {
    console.error('创建训练任务失败:', error)
    ElMessage.error(error.response?.data?.detail || '创建训练任务失败')
  } finally {
    submitting.value = false
  }
}

// 生命周期
onMounted(() => {
  loadAnnotationTasks()
  loadBaseModels()
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

:deep(.el-input-number) {
  width: 100%;
}

:deep(.el-collapse-item__header) {
  font-weight: 600;
  color: #0A2E5B;
}
</style>
