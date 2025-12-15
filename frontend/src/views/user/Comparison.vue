<template>
  <div class="min-h-screen bg-light-gray">
    <!-- 导航栏 -->
    <nav class="bg-white border-b border-gray-200 sticky top-0 z-50 shadow-soft">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <div class="flex items-center space-x-3">
            <button
              class="w-10 h-10 bg-gray-100 rounded-xl flex items-center justify-center hover:bg-gray-200 transition-colors"
              @click="goBack"
            >
              <svg class="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <div>
              <h1 class="text-xl font-bold text-deep-blue">检测结果对比</h1>
              <p class="text-xs text-gray-500">Detection Comparison</p>
            </div>
          </div>
          <!-- 返回首页按钮 -->
          <button
            class="px-4 py-2 bg-gray-100 rounded-lg flex items-center space-x-2 hover:bg-gray-200 transition-colors"
            @click="goToHome"
          >
            <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
            </svg>
            <span class="text-sm font-medium text-gray-700">返回首页</span>
          </button>
        </div>
      </div>
    </nav>

    <!-- 主内容区 -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div v-if="loading" class="text-center py-20">
        <el-icon class="is-loading" :size="40">
          <Loading />
        </el-icon>
        <p class="mt-4 text-gray-600">加载对比数据中...</p>
      </div>

      <div v-else-if="error" class="text-center py-20">
        <svg class="w-16 h-16 mx-auto text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p class="mt-4 text-red-600">{{ error }}</p>
        <button class="mt-4 px-6 py-2 bg-bright-cyan text-white rounded-lg hover:bg-bright-cyan-dark" @click="goBack">
          返回历史
        </button>
      </div>

      <div v-else-if="comparisonData" class="space-y-6">
        <!-- 统计对比卡片 -->
        <div v-if="comparisonData.statistics" class="bg-white rounded-xl shadow-soft p-6">
          <h2 class="text-lg font-bold text-deep-blue mb-4">统计对比</h2>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <!-- 检测对象数量对比 -->
            <div class="bg-gradient-to-br from-bright-cyan/10 to-bright-cyan/5 rounded-xl p-4">
              <h3 class="text-sm font-semibold text-gray-700 mb-3">检测对象数量</h3>
              <div class="space-y-2">
                <div class="flex items-center justify-between">
                  <span class="text-sm text-gray-600">结果 1:</span>
                  <span class="text-lg font-bold text-bright-cyan">
                    {{ comparisonData.statistics.detection_count.first }}
                  </span>
                </div>
                <div class="flex items-center justify-between">
                  <span class="text-sm text-gray-600">结果 2:</span>
                  <span class="text-lg font-bold text-coral-orange">
                    {{ comparisonData.statistics.detection_count.second }}
                  </span>
                </div>
                <div class="flex items-center justify-between pt-2 border-t border-gray-200">
                  <span class="text-sm text-gray-600">差异:</span>
                  <span
                    class="text-lg font-bold"
                    :class="comparisonData.statistics.detection_count.diff >= 0 ? 'text-green-600' : 'text-red-600'"
                  >
                    {{ comparisonData.statistics.detection_count.diff > 0 ? '+' : '' }}{{ comparisonData.statistics.detection_count.diff }}
                  </span>
                </div>
              </div>
            </div>

            <!-- 处理时间对比 -->
            <div class="bg-gradient-to-br from-purple-500/10 to-purple-500/5 rounded-xl p-4">
              <h3 class="text-sm font-semibold text-gray-700 mb-3">处理时间（秒）</h3>
              <div class="space-y-2">
                <div class="flex items-center justify-between">
                  <span class="text-sm text-gray-600">结果 1:</span>
                  <span class="text-lg font-bold text-bright-cyan">
                    {{ comparisonData.statistics.processing_time.first }}s
                  </span>
                </div>
                <div class="flex items-center justify-between">
                  <span class="text-sm text-gray-600">结果 2:</span>
                  <span class="text-lg font-bold text-coral-orange">
                    {{ comparisonData.statistics.processing_time.second }}s
                  </span>
                </div>
                <div class="flex items-center justify-between pt-2 border-t border-gray-200">
                  <span class="text-sm text-gray-600">差异:</span>
                  <span
                    class="text-lg font-bold"
                    :class="comparisonData.statistics.processing_time.diff >= 0 ? 'text-red-600' : 'text-green-600'"
                  >
                    {{ comparisonData.statistics.processing_time.diff > 0 ? '+' : '' }}{{ comparisonData.statistics.processing_time.diff }}s
                  </span>
                </div>
              </div>
            </div>

            <!-- 匹配统计 -->
            <div class="bg-gradient-to-br from-green-500/10 to-green-500/5 rounded-xl p-4">
              <h3 class="text-sm font-semibold text-gray-700 mb-3">对象匹配统计</h3>
              <div class="space-y-2">
                <div class="flex items-center justify-between">
                  <span class="text-sm text-gray-600">共同对象:</span>
                  <span class="text-lg font-bold text-green-600">
                    {{ comparisonData.comparison.match_stats.common_count }}
                  </span>
                </div>
                <div class="flex items-center justify-between">
                  <span class="text-sm text-gray-600">仅结果1:</span>
                  <span class="text-lg font-bold text-bright-cyan">
                    {{ comparisonData.comparison.match_stats.unique_to_first_count }}
                  </span>
                </div>
                <div class="flex items-center justify-between">
                  <span class="text-sm text-gray-600">仅结果2:</span>
                  <span class="text-lg font-bold text-coral-orange">
                    {{ comparisonData.comparison.match_stats.unique_to_second_count }}
                  </span>
                </div>
                <div class="flex items-center justify-between pt-2 border-t border-gray-200">
                  <span class="text-sm text-gray-600">匹配率:</span>
                  <span class="text-lg font-bold text-green-600">
                    {{ comparisonData.comparison.match_stats.match_rate.toFixed(1) }}%
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 并排显示区域 -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- 结果 1 -->
          <div class="bg-white rounded-xl shadow-soft overflow-hidden">
            <div class="bg-bright-cyan text-white px-4 py-3 flex items-center justify-between">
              <h3 class="font-semibold">结果 #{{ detectionRecords[0]?.id }}</h3>
              <span class="text-sm opacity-90">
                {{ detectionRecords[0]?.metadata?.count || 0 }} 个对象
              </span>
            </div>
            <div class="p-4 bg-gray-900">
              <img
                v-if="detectionRecords[0]?.imageUrl"
                :src="detectionRecords[0].imageUrl"
                alt="检测结果 1"
                class="w-full h-auto max-h-96 object-contain"
                @load="onImageLoad"
              >
              <div v-else class="flex items-center justify-center h-64 text-gray-400">
                <p>无图像数据</p>
              </div>
            </div>
          </div>

          <!-- 结果 2 -->
          <div class="bg-white rounded-xl shadow-soft overflow-hidden">
            <div class="bg-coral-orange text-white px-4 py-3 flex items-center justify-between">
              <h3 class="font-semibold">结果 #{{ detectionRecords[1]?.id }}</h3>
              <span class="text-sm opacity-90">
                {{ detectionRecords[1]?.metadata?.count || 0 }} 个对象
              </span>
            </div>
            <div class="p-4 bg-gray-900">
              <img
                v-if="detectionRecords[1]?.imageUrl"
                :src="detectionRecords[1].imageUrl"
                alt="检测结果 2"
                class="w-full h-auto max-h-96 object-contain"
                @load="onImageLoad"
              >
              <div v-else class="flex items-center justify-center h-64 text-gray-400">
                <p>无图像数据</p>
              </div>
            </div>
          </div>
        </div>

        <!-- 差异详情 -->
        <div class="bg-white rounded-xl shadow-soft p-6">
          <h2 class="text-lg font-bold text-deep-blue mb-4">差异分析</h2>

          <el-tabs v-model="activeTab" class="comparison-tabs">
            <!-- 共同对象 -->
            <el-tab-pane label="共同对象" name="common">
              <template #label>
                <span class="flex items-center space-x-2">
                  <span class="w-2 h-2 bg-green-500 rounded-full" />
                  <span>共同对象 ({{ comparisonData.comparison.common_objects.length }})</span>
                </span>
              </template>
              <div v-if="comparisonData.comparison.common_objects.length === 0" class="text-center py-12 text-gray-500">
                无共同检测对象
              </div>
              <div v-else class="overflow-x-auto">
                <table class="w-full">
                  <thead class="bg-gray-50">
                    <tr>
                      <th class="px-4 py-2 text-left text-xs font-semibold text-gray-600">类别（结果1）</th>
                      <th class="px-4 py-2 text-left text-xs font-semibold text-gray-600">类别（结果2）</th>
                      <th class="px-4 py-2 text-left text-xs font-semibold text-gray-600">置信度1</th>
                      <th class="px-4 py-2 text-left text-xs font-semibold text-gray-600">置信度2</th>
                      <th class="px-4 py-2 text-left text-xs font-semibold text-gray-600">IOU</th>
                      <th class="px-4 py-2 text-left text-xs font-semibold text-gray-600">类别匹配</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-gray-200">
                    <tr v-for="(pair, index) in comparisonData.comparison.common_objects" :key="index" class="hover:bg-gray-50">
                      <td class="px-4 py-3 text-sm text-gray-700">{{ pair.first.class_name }}</td>
                      <td class="px-4 py-3 text-sm text-gray-700">{{ pair.second.class_name }}</td>
                      <td class="px-4 py-3">
                        <span class="inline-flex items-center px-2 py-1 rounded-full bg-bright-cyan/10 text-bright-cyan text-xs font-semibold">
                          {{ (pair.first.confidence * 100).toFixed(1) }}%
                        </span>
                      </td>
                      <td class="px-4 py-3">
                        <span class="inline-flex items-center px-2 py-1 rounded-full bg-coral-orange/10 text-coral-orange text-xs font-semibold">
                          {{ (pair.second.confidence * 100).toFixed(1) }}%
                        </span>
                      </td>
                      <td class="px-4 py-3">
                        <span class="inline-flex items-center px-2 py-1 rounded-full bg-green-100 text-green-700 text-xs font-semibold">
                          {{ (pair.iou * 100).toFixed(1) }}%
                        </span>
                      </td>
                      <td class="px-4 py-3">
                        <el-tag :type="pair.class_match ? 'success' : 'warning'" size="small">
                          {{ pair.class_match ? '✓ 匹配' : '✗ 不匹配' }}
                        </el-tag>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </el-tab-pane>

            <!-- 仅在结果1 -->
            <el-tab-pane label="仅结果1" name="unique1">
              <template #label>
                <span class="flex items-center space-x-2">
                  <span class="w-2 h-2 bg-bright-cyan rounded-full" />
                  <span>仅结果1 ({{ comparisonData.comparison.unique_to_first.length }})</span>
                </span>
              </template>
              <div v-if="comparisonData.comparison.unique_to_first.length === 0" class="text-center py-12 text-gray-500">
                无独有对象
              </div>
              <div v-else class="overflow-x-auto">
                <table class="w-full">
                  <thead class="bg-gray-50">
                    <tr>
                      <th class="px-4 py-2 text-left text-xs font-semibold text-gray-600">类别</th>
                      <th class="px-4 py-2 text-left text-xs font-semibold text-gray-600">置信度</th>
                      <th class="px-4 py-2 text-left text-xs font-semibold text-gray-600">位置坐标</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-gray-200">
                    <tr v-for="(obj, index) in comparisonData.comparison.unique_to_first" :key="index" class="hover:bg-gray-50">
                      <td class="px-4 py-3 text-sm text-gray-700">{{ obj.class_name }}</td>
                      <td class="px-4 py-3">
                        <span class="inline-flex items-center px-2 py-1 rounded-full bg-bright-cyan/10 text-bright-cyan text-xs font-semibold">
                          {{ (obj.confidence * 100).toFixed(1) }}%
                        </span>
                      </td>
                      <td class="px-4 py-3 text-xs text-gray-500 font-mono">[{{ obj.bbox.join(', ') }}]</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </el-tab-pane>

            <!-- 仅在结果2 -->
            <el-tab-pane label="仅结果2" name="unique2">
              <template #label>
                <span class="flex items-center space-x-2">
                  <span class="w-2 h-2 bg-coral-orange rounded-full" />
                  <span>仅结果2 ({{ comparisonData.comparison.unique_to_second.length }})</span>
                </span>
              </template>
              <div v-if="comparisonData.comparison.unique_to_second.length === 0" class="text-center py-12 text-gray-500">
                无独有对象
              </div>
              <div v-else class="overflow-x-auto">
                <table class="w-full">
                  <thead class="bg-gray-50">
                    <tr>
                      <th class="px-4 py-2 text-left text-xs font-semibold text-gray-600">类别</th>
                      <th class="px-4 py-2 text-left text-xs font-semibold text-gray-600">置信度</th>
                      <th class="px-4 py-2 text-left text-xs font-semibold text-gray-600">位置坐标</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-gray-200">
                    <tr v-for="(obj, index) in comparisonData.comparison.unique_to_second" :key="index" class="hover:bg-gray-50">
                      <td class="px-4 py-3 text-sm text-gray-700">{{ obj.class_name }}</td>
                      <td class="px-4 py-3">
                        <span class="inline-flex items-center px-2 py-1 rounded-full bg-coral-orange/10 text-coral-orange text-xs font-semibold">
                          {{ (obj.confidence * 100).toFixed(1) }}%
                        </span>
                      </td>
                      <td class="px-4 py-3 text-xs text-gray-500 font-mono">[{{ obj.bbox.join(', ') }}]</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import { compareDetections } from '@/api/comparison'
import { getDetectionDetail } from '@/api/detect'

const route = useRoute()
const router = useRouter()

const loading = ref(true)
const error = ref(null)
const comparisonData = ref(null)
const detectionRecords = ref([])
const activeTab = ref('common')

onMounted(async () => {
  await loadComparisonData()
})

async function loadComparisonData() {
  try {
    loading.value = true
    error.value = null

    // 获取URL参数中的IDs
    const ids = route.query.ids
    if (!ids) {
      error.value = '缺少对比ID参数'
      return
    }

    // 调用对比API
    const response = await compareDetections(ids)
    comparisonData.value = response

    // 获取每个检测记录的详细信息（用于显示图片）
    const idArray = ids.split(',').map(id => parseInt(id))
    const detailPromises = idArray.map(id => getDetectionDetail(id))
    const details = await Promise.all(detailPromises)

    detectionRecords.value = details.map((detail, index) => {
      const recordData = comparisonData.value.records[index]
      return {
        id: recordData.detection_id,
        metadata: recordData.metadata,
        imageUrl: getMediaUrl(detail.output_file_path),
        data: detail
      }
    })

  } catch (err) {
    console.error('Load comparison error:', err)
    error.value = err.response?.data?.detail || '加载对比数据失败'
    ElMessage.error(error.value)
  } finally {
    loading.value = false
  }
}

function getMediaUrl(path) {
  if (!path) return null
  const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'
  return baseURL.replace('/api/v1', '') + '/' + path
}

const onImageLoad = () => {
  // 图片加载完成的回调（预留用于同步控制）
}

const goBack = () => {
  router.push('/detection-history')
}

const goToHome = () => {
  router.push('/')
}
</script>

<style scoped>
:deep(.comparison-tabs .el-tabs__header) {
  margin-bottom: 1.5rem;
}

:deep(.comparison-tabs .el-tabs__item.is-active) {
  color: #00BFFF;
}

:deep(.comparison-tabs .el-tabs__active-bar) {
  background-color: #00BFFF;
}

/* 响应式表格 */
@media (max-width: 768px) {
  .overflow-x-auto {
    overflow-x: auto;
  }
}
</style>
