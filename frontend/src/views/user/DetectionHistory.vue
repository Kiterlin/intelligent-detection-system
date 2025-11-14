<template>
  <div class="min-h-screen bg-light-gray">
    <!-- 导航栏 -->
    <nav class="bg-white border-b border-gray-200 sticky top-0 z-50 shadow-soft">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <!-- Logo和标题 -->
          <div class="flex items-center space-x-3">
            <div class="w-10 h-10 bg-gradient-ocean rounded-xl flex items-center justify-center">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <h1 class="text-xl font-bold text-deep-blue">检测历史</h1>
              <p class="text-xs text-gray-500">Detection History</p>
            </div>
          </div>

          <!-- 用户信息和操作 -->
          <div class="flex items-center space-x-4">
            <el-dropdown class="cursor-pointer" @command="handleCommand">
              <div class="flex items-center space-x-2 px-4 py-2 rounded-lg hover:bg-gray-50 transition-colors">
                <div class="w-8 h-8 bg-gradient-ocean rounded-full flex items-center justify-center">
                  <el-icon class="text-white">
                    <User />
                  </el-icon>
                </div>
                <span class="text-sm font-medium text-gray-700">{{ authStore.userInfo?.username }}</span>
                <el-icon class="text-gray-400">
                  <ArrowDown />
                </el-icon>
              </div>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="home">
                    <el-icon><HomeFilled /></el-icon>
                    返回首页
                  </el-dropdown-item>
                  <el-dropdown-item command="detection">
                    <el-icon><Camera /></el-icon>
                    开始检测
                  </el-dropdown-item>
                  <el-dropdown-item v-if="authStore.isAdmin" command="admin">
                    <el-icon><Setting /></el-icon>
                    管理后台
                  </el-dropdown-item>
                  <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </div>
    </nav>

    <!-- 主内容区 -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- 统计卡片 -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div class="bg-white rounded-xl shadow-soft p-6 border-l-4 border-bright-cyan">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-gray-600 mb-1">总检测次数</p>
              <p class="text-2xl font-bold text-deep-blue">{{ detectionStore.historyTotal }}</p>
            </div>
            <div class="w-12 h-12 bg-bright-cyan/10 rounded-xl flex items-center justify-center">
              <svg class="w-6 h-6 text-bright-cyan" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-xl shadow-soft p-6 border-l-4 border-green-500">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-gray-600 mb-1">已完成</p>
              <p class="text-2xl font-bold text-deep-blue">{{ completedCount }}</p>
            </div>
            <div class="w-12 h-12 bg-green-500/10 rounded-xl flex items-center justify-center">
              <svg class="w-6 h-6 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-xl shadow-soft p-6 border-l-4 border-coral-orange">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-gray-600 mb-1">图片检测</p>
              <p class="text-2xl font-bold text-deep-blue">{{ imageCount }}</p>
            </div>
            <div class="w-12 h-12 bg-coral-orange/10 rounded-xl flex items-center justify-center">
              <svg class="w-6 h-6 text-coral-orange" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-xl shadow-soft p-6 border-l-4 border-purple-500">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-gray-600 mb-1">视频检测</p>
              <p class="text-2xl font-bold text-deep-blue">{{ videoCount }}</p>
            </div>
            <div class="w-12 h-12 bg-purple-500/10 rounded-xl flex items-center justify-center">
              <svg class="w-6 h-6 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      <!-- 筛选和操作区 -->
      <div class="bg-white rounded-xl shadow-soft p-6 mb-6">
        <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <!-- 筛选器 -->
          <div class="flex flex-col sm:flex-row gap-3 flex-1">
            <el-select
              v-model="filterType"
              placeholder="文件类型"
              clearable
              class="w-full sm:w-40"
              @change="handleFilter"
            >
              <el-option label="全部类型" value="" />
              <el-option label="图片" value="image">
                <div class="flex items-center">
                  <svg class="w-4 h-4 mr-2 text-coral-orange" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  图片
                </div>
              </el-option>
              <el-option label="视频" value="video">
                <div class="flex items-center">
                  <svg class="w-4 h-4 mr-2 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                  视频
                </div>
              </el-option>
            </el-select>

            <el-select
              v-model="filterStatus"
              placeholder="检测状态"
              clearable
              class="w-full sm:w-40"
              @change="handleFilter"
            >
              <el-option label="全部状态" value="" />
              <el-option label="已完成" value="completed">
                <div class="flex items-center">
                  <span class="w-2 h-2 bg-green-500 rounded-full mr-2" />
                  已完成
                </div>
              </el-option>
              <el-option label="处理中" value="processing">
                <div class="flex items-center">
                  <span class="w-2 h-2 bg-yellow-500 rounded-full mr-2" />
                  处理中
                </div>
              </el-option>
              <el-option label="失败" value="failed">
                <div class="flex items-center">
                  <span class="w-2 h-2 bg-red-500 rounded-full mr-2" />
                  失败
                </div>
              </el-option>
            </el-select>
          </div>

          <!-- 操作按钮 -->
          <div class="flex gap-3">
            <button
              class="px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors flex items-center space-x-2"
              @click="handleRefresh"
            >
              <svg class="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              <span class="text-sm font-medium text-gray-700">刷新</span>
            </button>

            <button
              v-if="selectedIds.length > 0"
              class="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors flex items-center space-x-2"
              @click="handleBatchDelete"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
              <span class="text-sm font-medium">删除 ({{ selectedIds.length }})</span>
            </button>
          </div>
        </div>
      </div>

      <!-- 数据表格 -->
      <div class="bg-white rounded-xl shadow-soft overflow-hidden">
        <el-table
          v-loading="detectionStore.historyLoading"
          :data="detectionStore.historyList"
          style="width: 100%"
          element-loading-text="加载中..."
          :header-cell-style="{ background: '#f8fafc', color: '#0A2E5B', fontWeight: '600' }"
          :row-style="{ cursor: 'pointer' }"
          @selection-change="handleSelectionChange"
          @row-click="handleView"
        >
          <el-table-column type="selection" width="55" />
          <el-table-column prop="id" label="ID" width="80" align="center" />

          <el-table-column label="类型" width="100" align="center">
            <template #default="scope">
              <el-tag
                :type="scope.row.input_type === 'image' ? '' : 'info'"
                :color="scope.row.input_type === 'image' ? '#FF7F50' : '#9333ea'"
                style="color: white; border: none;"
                effect="dark"
              >
                <div class="flex items-center space-x-1">
                  <svg v-if="scope.row.input_type === 'image'" class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clip-rule="evenodd" />
                  </svg>
                  <svg v-else class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M2 6a2 2 0 012-2h6a2 2 0 012 2v8a2 2 0 01-2 2H4a2 2 0 01-2-2V6zM14.553 7.106A1 1 0 0014 8v4a1 1 0 00.553.894l2 1A1 1 0 0018 13V7a1 1 0 00-1.447-.894l-2 1z" />
                  </svg>
                  <span>{{ scope.row.input_type === 'image' ? '图片' : '视频' }}</span>
                </div>
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column label="文件名" min-width="200">
            <template #default="scope">
              <div class="flex items-center space-x-2">
                <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                </svg>
                <span class="text-sm text-gray-700 truncate">{{ getFileName(scope.row.input_file_path) }}</span>
              </div>
            </template>
          </el-table-column>

          <el-table-column label="检测对象数" width="120" align="center">
            <template #default="scope">
              <div class="inline-flex items-center px-3 py-1 rounded-full bg-green-100 text-green-700">
                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span class="text-sm font-semibold">{{ scope.row.detected_objects_count || 0 }}</span>
              </div>
            </template>
          </el-table-column>

          <el-table-column label="状态" width="100" align="center">
            <template #default="scope">
              <el-tag :type="getStatusType(scope.row.status)" effect="plain">
                {{ getStatusText(scope.row.status) }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column label="处理时间" width="120" align="center">
            <template #default="scope">
              <span class="text-sm text-gray-600">
                {{ scope.row.processing_time ? scope.row.processing_time.toFixed(2) + 's' : '-' }}
              </span>
            </template>
          </el-table-column>

          <el-table-column label="创建时间" width="180" align="center">
            <template #default="scope">
              <span class="text-sm text-gray-600">{{ formatDate(scope.row.created_at) }}</span>
            </template>
          </el-table-column>

          <el-table-column label="操作" width="220" fixed="right" align="center">
            <template #default="scope">
              <div class="flex justify-center space-x-2" @click.stop>
                <button
                  class="px-3 py-1 text-xs bg-bright-cyan text-white rounded-lg hover:bg-bright-cyan-dark transition-colors"
                  @click="handleView(scope.row)"
                >
                  查看
                </button>
                <el-dropdown
                  v-if="scope.row.status === 'completed'"
                  trigger="click"
                  @command="(cmd) => handleDownloadCommand(cmd, scope.row)"
                >
                  <button class="px-3 py-1 text-xs bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors">
                    下载 ▾
                  </button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item command="result">结果文件</el-dropdown-item>
                      <el-dropdown-item command="report">检测报告</el-dropdown-item>
                      <el-dropdown-item command="all" divided>全部(ZIP)</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
                <button
                  class="px-3 py-1 text-xs bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
                  @click="handleDelete(scope.row)"
                >
                  删除
                </button>
              </div>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <div class="px-6 py-4 border-t border-gray-200 flex justify-center">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="detectionStore.historyTotal"
            layout="total, sizes, prev, pager, next, jumper"
            background
            @size-change="handleSizeChange"
            @current-change="handlePageChange"
          />
        </div>
      </div>
    </div>

    <!-- 查看详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="检测详情"
      width="90%"
      :style="{ maxWidth: '900px' }"
      :close-on-click-modal="false"
    >
      <div v-if="currentDetail" class="space-y-6">
        <!-- 结果展示区 -->
        <div class="bg-gray-900 rounded-xl overflow-hidden">
          <img
            v-if="currentDetail.input_type === 'image' && currentDetail.output_file_path"
            :src="getMediaUrl(currentDetail.output_file_path)"
            alt="检测结果"
            class="w-full h-auto max-h-96 object-contain"
            loading="lazy"
          >
          <video
            v-if="currentDetail.input_type === 'video' && currentDetail.output_file_path"
            :src="getMediaUrl(currentDetail.output_file_path)"
            controls
            class="w-full h-auto max-h-96"
            preload="metadata"
          />
        </div>

        <!-- 检测信息卡片 -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div class="bg-gradient-to-br from-bright-cyan to-bright-cyan-dark rounded-xl p-4 text-white">
            <p class="text-xs opacity-90 mb-1">检测ID</p>
            <p class="text-2xl font-bold">#{{ currentDetail.id }}</p>
          </div>
          <div class="bg-gradient-to-br from-coral-orange to-coral-orange-dark rounded-xl p-4 text-white">
            <p class="text-xs opacity-90 mb-1">检测对象数</p>
            <p class="text-2xl font-bold">{{ currentDetail.detected_objects_count || 0 }}</p>
          </div>
          <div class="bg-gradient-to-br from-green-500 to-green-600 rounded-xl p-4 text-white">
            <p class="text-xs opacity-90 mb-1">处理时间</p>
            <p class="text-2xl font-bold">
              {{ currentDetail.processing_time ? currentDetail.processing_time.toFixed(2) + 's' : '-' }}
            </p>
          </div>
          <div class="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl p-4 text-white">
            <p class="text-xs opacity-90 mb-1">文件类型</p>
            <p class="text-2xl font-bold">{{ currentDetail.input_type === 'image' ? '图片' : '视频' }}</p>
          </div>
        </div>

        <!-- 参数信息 -->
        <div class="bg-gray-50 rounded-xl p-4">
          <h3 class="text-sm font-semibold text-deep-blue mb-3">检测参数</h3>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p class="text-xs text-gray-500 mb-1">置信度阈值</p>
              <p class="text-sm font-semibold text-gray-700">{{ currentDetail.confidence_threshold }}</p>
            </div>
            <div>
              <p class="text-xs text-gray-500 mb-1">IOU阈值</p>
              <p class="text-sm font-semibold text-gray-700">{{ currentDetail.iou_threshold }}</p>
            </div>
            <div>
              <p class="text-xs text-gray-500 mb-1">状态</p>
              <el-tag :type="getStatusType(currentDetail.status)" size="small">
                {{ getStatusText(currentDetail.status) }}
              </el-tag>
            </div>
            <div>
              <p class="text-xs text-gray-500 mb-1">创建时间</p>
              <p class="text-sm font-semibold text-gray-700">{{ formatDate(currentDetail.created_at) }}</p>
            </div>
          </div>
        </div>

        <!-- 检测对象列表 -->
        <div v-if="detailObjects.length > 0" class="bg-white rounded-xl border border-gray-200">
          <div class="px-4 py-3 border-b border-gray-200">
            <h3 class="text-sm font-semibold text-deep-blue">检测到的对象 ({{ detailObjects.length }})</h3>
          </div>
          <div class="overflow-x-auto">
            <table class="w-full">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-4 py-2 text-left text-xs font-semibold text-gray-600">类别</th>
                  <th class="px-4 py-2 text-left text-xs font-semibold text-gray-600">置信度</th>
                  <th class="px-4 py-2 text-left text-xs font-semibold text-gray-600">位置坐标</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200">
                <tr v-for="(obj, index) in detailObjects" :key="index" class="hover:bg-gray-50">
                  <td class="px-4 py-3 text-sm text-gray-700">{{ obj.class }}</td>
                  <td class="px-4 py-3">
                    <div class="inline-flex items-center px-2 py-1 rounded-full bg-green-100 text-green-700">
                      <span class="text-xs font-semibold">{{ (obj.confidence * 100).toFixed(1) }}%</span>
                    </div>
                  </td>
                  <td class="px-4 py-3 text-xs text-gray-500 font-mono">[{{ obj.bbox.join(', ') }}]</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="flex justify-end space-x-3">
          <button
            class="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium text-gray-700"
            @click="detailDialogVisible = false"
          >
            关闭
          </button>
          <el-dropdown
            v-if="currentDetail?.status === 'completed'"
            trigger="click"
            @command="(cmd) => handleDownloadCommand(cmd, currentDetail)"
          >
            <button class="btn-primary px-6 py-2 text-sm font-medium">
              下载结果 ▾
            </button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="result">
                  <div class="flex items-center space-x-2">
                    <span>📷</span>
                    <span>结果文件</span>
                  </div>
                </el-dropdown-item>
                <el-dropdown-item command="report">
                  <div class="flex items-center space-x-2">
                    <span>📄</span>
                    <span>检测报告</span>
                  </div>
                </el-dropdown-item>
                <el-dropdown-item command="all" divided>
                  <div class="flex items-center space-x-2">
                    <span>📦</span>
                    <span>全部(ZIP)</span>
                  </div>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useDetectionStore } from '@/stores/detection'
import { downloadResultFile, downloadReport, downloadAll } from '@/api/detect'
import { downloadFile, getFilenameFromContentDisposition } from '@/utils/helpers'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  User,
  ArrowDown,
  Setting,
  HomeFilled,
  Camera
} from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()
const detectionStore = useDetectionStore()

// 筛选和分页
const filterType = ref('')
const filterStatus = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const selectedIds = ref([])

// 详情对话框
const detailDialogVisible = ref(false)
const currentDetail = ref(null)

// 统计数据
const completedCount = computed(() => {
  return detectionStore.historyList.filter(item => item.status === 'completed').length
})

const imageCount = computed(() => {
  return detectionStore.historyList.filter(item => item.input_type === 'image').length
})

const videoCount = computed(() => {
  return detectionStore.historyList.filter(item => item.input_type === 'video').length
})

const detailObjects = computed(() => {
  if (!currentDetail.value || !currentDetail.value.result_json) {
    return []
  }
  const results = currentDetail.value.result_json
  return results.detections || []
})

// 生命周期
onMounted(async () => {
  await fetchHistoryData()
})

// 获取历史数据
async function fetchHistoryData() {
  const params = {
    page: currentPage.value,
    page_size: pageSize.value
  }

  if (filterType.value) {
    params.input_type = filterType.value
  }

  if (filterStatus.value) {
    params.status = filterStatus.value
  }

  await detectionStore.fetchHistory(params)
}

// 事件处理
function handleFilter() {
  currentPage.value = 1
  fetchHistoryData()
}

function handleRefresh() {
  fetchHistoryData()
  ElMessage.success('刷新成功')
}

function handlePageChange(page) {
  currentPage.value = page
  fetchHistoryData()
}

function handleSizeChange(size) {
  pageSize.value = size
  currentPage.value = 1
  fetchHistoryData()
}

function handleSelectionChange(selection) {
  selectedIds.value = selection.map((item) => item.id)
}

function handleView(row) {
  currentDetail.value = row
  detailDialogVisible.value = true
}

async function handleDownloadCommand(command, row) {
  try {
    ElMessage.info('正在准备下载...')
    let response

    switch (command) {
      case 'result':
        response = await downloadResultFile(row.id)
        break
      case 'report':
        response = await downloadReport(row.id)
        break
      case 'all':
        response = await downloadAll(row.id)
        break
      default:
        ElMessage.error('未知的下载选项')
        return
    }

    // 从响应头获取文件名
    const contentDisposition = response.headers['content-disposition']
    const filename = getFilenameFromContentDisposition(contentDisposition)

    // 触发下载
    downloadFile(response.data, filename)
    ElMessage.success('下载成功')
  } catch (error) {
    console.error('Download error:', error)
    ElMessage.error('下载失败：' + (error.response?.data?.detail || error.message))
  }
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm('确定要删除这条检测记录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await detectionStore.removeDetection(row.id)
    ElMessage.success('删除成功')
    await fetchHistoryData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Delete error:', error)
      ElMessage.error('删除失败')
    }
  }
}

async function handleBatchDelete() {
  try {
    await ElMessageBox.confirm(`确定要删除选中的 ${selectedIds.value.length} 条记录吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    // 批量删除
    for (const id of selectedIds.value) {
      await detectionStore.removeDetection(id)
    }

    selectedIds.value = []
    ElMessage.success('批量删除成功')
    await fetchHistoryData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Batch delete error:', error)
      ElMessage.error('批量删除失败')
    }
  }
}

// 工具函数
function getFileName(path) {
  if (!path) return '-'
  return path.split('/').pop()
}

function getStatusType(status) {
  const typeMap = {
    completed: 'success',
    processing: 'warning',
    pending: 'info',
    failed: 'danger'
  }
  return typeMap[status] || 'info'
}

function getStatusText(status) {
  const textMap = {
    completed: '已完成',
    processing: '处理中',
    pending: '等待中',
    failed: '失败'
  }
  return textMap[status] || status
}

function formatDate(dateString) {
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

function getMediaUrl(path) {
  if (!path) return null
  const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'
  return baseURL.replace('/api/v1', '') + '/' + path
}

// 导航操作
const handleCommand = (command) => {
  if (command === 'logout') {
    authStore.logout()
  } else if (command === 'home') {
    router.push('/')
  } else if (command === 'detection') {
    router.push('/detection')
  } else if (command === 'admin') {
    router.push('/admin/dashboard')
  }
}
</script>

<style scoped>
/* 表格行悬停效果 */
:deep(.el-table__row):hover {
  background-color: #f8fafc;
}

/* 对话框样式优化 */
:deep(.el-dialog__header) {
  border-bottom: 1px solid #e5e7eb;
  padding: 1.5rem;
}

:deep(.el-dialog__body) {
  padding: 1.5rem;
  max-height: 70vh;
  overflow-y: auto;
}

:deep(.el-dialog__footer) {
  border-top: 1px solid #e5e7eb;
  padding: 1rem 1.5rem;
}

/* 分页样式 */
:deep(.el-pagination) {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
}

:deep(.el-pagination.is-background .el-pager li:not(.disabled).active) {
  background-color: #00BFFF;
  color: white;
}

:deep(.el-pagination.is-background .el-pager li:hover) {
  color: #00BFFF;
}

/* 响应式设计 */
@media (max-width: 768px) {
  :deep(.el-table__header-wrapper) {
    overflow-x: auto;
  }

  :deep(.el-table__body-wrapper) {
    overflow-x: auto;
  }
}
</style>
