/**
 * 模型训练相关 API
 */
import request from '@/utils/request'

const TRAINING_BASE_URL = '/training'

// ==================== 辅助函数 ====================

function transformTrainingJob(job) {
  if (!job) return null

  const config = job.config_json || {}
  const trainingParams = {
    epochs: config.epochs,
    batch_size: config.batch_size,
    img_size: config.img_size,
    device: config.device,
    optimizer: config.optimizer,
    learning_rate: config.learning_rate,
    workers: config.workers,
    patience: config.patience
  }

  return {
    ...job,
    name: job.job_name,
    config: {
      base_model: config.base_model,
      training_params: trainingParams
    },
    final_metrics: job.metrics_json,
    model_path: job.weights_path
  }
}

// ==================== 训练任务管理 ====================

/**
 * 创建训练任务
 * @param {Object} data - 训练配置 {job_name, base_model_id, config_json, dataset_config}
 */
export async function createTrainingJob(data) {
  const response = await request({
    url: TRAINING_BASE_URL,
    method: 'post',
    data
  })
  return transformTrainingJob(response)
}

/**
 * 获取训练任务列表
 * @param {Object} params - 查询参数 {skip, limit, status_filter}
 */
export async function getTrainingJobs(params) {
  const response = await request({
    url: TRAINING_BASE_URL,
    method: 'get',
    params
  })
  return {
    ...response,
    items: (response.items || []).map(transformTrainingJob)
  }
}

/**
 * 获取训练任务详情
 * @param {number} jobId - 任务ID
 */
export async function getTrainingJob(jobId) {
  const response = await request({
    url: `${TRAINING_BASE_URL}/${jobId}`,
    method: 'get'
  })
  return transformTrainingJob(response)
}

/**
 * 删除训练任务
 * @param {number} jobId - 任务ID
 */
export function deleteTrainingJob(jobId) {
  return request({
    url: `${TRAINING_BASE_URL}/${jobId}`,
    method: 'delete'
  })
}

/**
 * 获取训练日志
 * @param {number} jobId - 任务ID
 */
export function getTrainingLogs(jobId) {
  return request({
    url: `${TRAINING_BASE_URL}/${jobId}/logs`,
    method: 'get'
  })
}

/**
 * 获取训练指标
 * @param {number} jobId - 任务ID
 */
export function getTrainingMetrics(jobId) {
  return request({
    url: `${TRAINING_BASE_URL}/${jobId}/metrics`,
    method: 'get'
  })
}

// ==================== 辅助函数 ====================

/**
 * 格式化训练状态
 * @param {string} status - 状态值
 */
export function formatTrainingStatus(status) {
  const statusMap = {
    pending: { text: '待处理', type: 'info', icon: 'clock' },
    preparing: { text: '准备数据', type: 'warning', icon: 'loading' },
    training: { text: '训练中', type: 'warning', icon: 'cpu' },
    completed: { text: '已完成', type: 'success', icon: 'circle-check' },
    failed: { text: '失败', type: 'danger', icon: 'circle-close' },
    cancelled: { text: '已取消', type: 'info', icon: 'close' }
  }
  return statusMap[status] || { text: status, type: 'info', icon: 'question' }
}

/**
 * 获取训练状态选项（用于筛选）
 */
export function getTrainingStatusOptions() {
  return [
    { value: '', label: '全部状态' },
    { value: 'pending', label: '待处理' },
    { value: 'preparing', label: '准备数据' },
    { value: 'training', label: '训练中' },
    { value: 'completed', label: '已完成' },
    { value: 'failed', label: '失败' },
    { value: 'cancelled', label: '已取消' }
  ]
}

/**
 * 获取基础模型选项
 */
export function getBaseModelOptions() {
  return [
    { value: 'yolov8n.pt', label: 'YOLOv8n - 最快速度，较低精度（推荐入门）', size: '~6 MB' },
    { value: 'yolov8s.pt', label: 'YOLOv8s - 快速，中等精度（推荐常用）', size: '~22 MB' },
    { value: 'yolov8m.pt', label: 'YOLOv8m - 平衡速度和精度', size: '~52 MB' },
    { value: 'yolov8l.pt', label: 'YOLOv8l - 较慢，高精度', size: '~87 MB' },
    { value: 'yolov8x.pt', label: 'YOLOv8x - 最慢，最高精度', size: '~136 MB' }
  ]
}

/**
 * 获取默认训练参数
 */
export function getDefaultTrainingParams() {
  return {
    epochs: 100,
    batch_size: 16,
    img_size: 640,
    optimizer: 'auto',
    lr0: 0.01,
    lrf: 0.01,
    momentum: 0.937,
    weight_decay: 0.0005,
    warmup_epochs: 3,
    patience: 50,
    save_period: 10,
    device: 'cuda:0'
  }
}

/**
 * 验证训练参数
 * @param {Object} params - 训练参数
 */
export function validateTrainingParams(params) {
  const errors = []

  if (!params.epochs || params.epochs < 1) {
    errors.push('训练轮次必须大于0')
  }

  if (!params.batch_size || params.batch_size < 1) {
    errors.push('批次大小必须大于0')
  }

  if (!params.img_size || params.img_size < 32) {
    errors.push('图像尺寸必须大于等于32')
  }

  if (params.lr0 && (params.lr0 <= 0 || params.lr0 > 1)) {
    errors.push('初始学习率必须在0到1之间')
  }

  if (params.lrf && (params.lrf <= 0 || params.lrf > 1)) {
    errors.push('最终学习率必须在0到1之间')
  }

  return errors
}

/**
 * 计算训练进度
 * @param {number} currentEpoch - 当前轮次
 * @param {number} totalEpochs - 总轮次
 */
export function calculateTrainingProgress(currentEpoch, totalEpochs) {
  if (!totalEpochs || totalEpochs === 0) {
    return 0
  }
  return Math.round((currentEpoch / totalEpochs) * 100)
}

/**
 * 格式化训练时长
 * @param {number} seconds - 秒数
 */
export function formatTrainingDuration(seconds) {
  if (!seconds || seconds < 0) {
    return '-'
  }

  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = Math.floor(seconds % 60)

  if (hours > 0) {
    return `${hours}小时 ${minutes}分钟`
  } else if (minutes > 0) {
    return `${minutes}分钟 ${secs}秒`
  } else {
    return `${secs}秒`
  }
}

/**
 * 准备图表数据（用于 ECharts）
 * @param {Array} metrics - 训练指标数组
 */
export function prepareChartData(metrics) {
  if (!metrics || metrics.length === 0) {
    return {
      epochs: [],
      trainLoss: [],
      valLoss: [],
      mAP50: [],
      mAP5095: [],
      precision: [],
      recall: []
    }
  }

  const data = {
    epochs: [],
    trainLoss: [],
    valLoss: [],
    mAP50: [],
    mAP5095: [],
    precision: [],
    recall: []
  }

  metrics.forEach(metric => {
    data.epochs.push(metric.epoch)
    data.trainLoss.push(metric.train_loss)
    data.valLoss.push(metric.val_loss)
    data.mAP50.push(metric.metrics?.mAP50 || 0)
    data.mAP5095.push(metric.metrics?.mAP50_95 || 0)
    data.precision.push(metric.metrics?.precision || 0)
    data.recall.push(metric.metrics?.recall || 0)
  })

  return data
}

/**
 * 获取损失曲线图表配置
 * @param {Object} chartData - 图表数据
 */
export function getLossChartOption(chartData) {
  return {
    title: {
      text: '训练损失曲线',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: ['训练损失', '验证损失'],
      bottom: 0
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: chartData.epochs,
      name: 'Epoch'
    },
    yAxis: {
      type: 'value',
      name: 'Loss'
    },
    series: [
      {
        name: '训练损失',
        type: 'line',
        data: chartData.trainLoss,
        smooth: true,
        itemStyle: { color: '#409EFF' }
      },
      {
        name: '验证损失',
        type: 'line',
        data: chartData.valLoss,
        smooth: true,
        itemStyle: { color: '#67C23A' }
      }
    ]
  }
}

/**
 * 获取性能指标图表配置
 * @param {Object} chartData - 图表数据
 */
export function getMetricsChartOption(chartData) {
  return {
    title: {
      text: '模型性能指标',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: ['mAP@50', 'mAP@50-95', 'Precision', 'Recall'],
      bottom: 0
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: chartData.epochs,
      name: 'Epoch'
    },
    yAxis: {
      type: 'value',
      name: '指标值',
      min: 0,
      max: 1
    },
    series: [
      {
        name: 'mAP@50',
        type: 'line',
        data: chartData.mAP50,
        smooth: true,
        itemStyle: { color: '#409EFF' }
      },
      {
        name: 'mAP@50-95',
        type: 'line',
        data: chartData.mAP5095,
        smooth: true,
        itemStyle: { color: '#67C23A' }
      },
      {
        name: 'Precision',
        type: 'line',
        data: chartData.precision,
        smooth: true,
        itemStyle: { color: '#E6A23C' }
      },
      {
        name: 'Recall',
        type: 'line',
        data: chartData.recall,
        smooth: true,
        itemStyle: { color: '#F56C6C' }
      }
    ]
  }
}
