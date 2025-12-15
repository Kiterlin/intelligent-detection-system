<template>
  <div class="min-h-screen flex flex-col md:flex-row">
    <!-- 左侧品牌区 -->
    <div class="relative w-full md:w-3/5 lg:w-1/2 bg-gradient-deep flex items-center justify-center p-8 md:p-12 overflow-hidden">
      <!-- 粒子背景 -->
      <ParticlesBg theme="sonar" :particle-count="60" />

      <!-- 品牌内容 -->
      <div class="relative z-10 text-center text-white space-y-6 max-w-2xl animate-fade-in">
        <!-- Logo图标 -->
        <div class="flex justify-center">
          <div class="w-20 h-20 md:w-24 md:h-24 bg-bright-cyan/20 rounded-2xl flex items-center justify-center backdrop-blur-sm border-2 border-bright-cyan/30 animate-float">
            <svg class="w-12 h-12 md:w-14 md:h-14 text-bright-cyan" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        </div>

        <!-- 系统标题 -->
        <div>
          <h1 class="text-3xl md:text-4xl lg:text-5xl font-bold mb-3 md:mb-4">
            智能目标检测系统
          </h1>
          <p class="text-lg md:text-xl text-bright-cyan font-medium">
            Intelligent Underwater Target Detection System
          </p>
        </div>

        <!-- Slogan -->
        <div class="space-y-3 pt-6">
          <p class="text-base md:text-lg text-white/90">
            深海科技 · 智能识别 · 精准分析
          </p>
          <p class="text-sm md:text-base text-white/70">
            运用先进AI技术,实现多场景目标的智能检测与识别
          </p>
        </div>

        <!-- 特性列表 -->
        <div class="grid grid-cols-3 gap-4 md:gap-6 pt-8">
          <div class="feature-item">
            <div class="feature-icon">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <p class="text-xs md:text-sm mt-2">极速检测</p>
          </div>
          <div class="feature-item">
            <div class="feature-icon">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <p class="text-xs md:text-sm mt-2">安全可靠</p>
          </div>
          <div class="feature-item">
            <div class="feature-icon">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
              </svg>
            </div>
            <p class="text-xs md:text-sm mt-2">精准分析</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧登录表单区 -->
    <div class="w-full md:w-2/5 lg:w-1/2 bg-light-gray flex items-center justify-center p-6 md:p-8 lg:p-12">
      <div class="w-full max-w-md animate-slide-up">
        <!-- 表单卡片 -->
        <div class="bg-white rounded-2xl shadow-strong p-8 md:p-10">
          <!-- 表单头部 -->
          <div class="text-center mb-8">
            <h2 class="text-2xl md:text-3xl font-bold text-deep-blue mb-2">
              欢迎回来
            </h2>
            <p class="text-gray-600">请登录您的账号</p>
          </div>

          <!-- 登录表单 -->
          <el-form
            ref="loginFormRef"
            :model="loginForm"
            :rules="loginRules"
            size="large"
            @submit.prevent="handleLogin"
          >
            <!-- 用户名输入 -->
            <el-form-item prop="username">
              <el-input
                v-model="loginForm.username"
                placeholder="请输入用户名"
                clearable
                class="form-input"
              >
                <template #prefix>
                  <el-icon class="text-bright-cyan">
                    <User />
                  </el-icon>
                </template>
              </el-input>
            </el-form-item>

            <!-- 密码输入 -->
            <el-form-item prop="password">
              <el-input
                v-model="loginForm.password"
                type="password"
                placeholder="请输入密码"
                show-password
                class="form-input"
                @keyup.enter="handleLogin"
              >
                <template #prefix>
                  <el-icon class="text-bright-cyan">
                    <Lock />
                  </el-icon>
                </template>
              </el-input>
            </el-form-item>

            <!-- 错误提示 -->
            <transition name="slide-down">
              <div v-if="errorMessage" class="mb-4">
                <div class="bg-red-50 border-l-4 border-red-500 p-3 rounded-lg">
                  <div class="flex items-start">
                    <el-icon class="text-red-500 mt-0.5 mr-2">
                      <WarningFilled />
                    </el-icon>
                    <p class="text-sm text-red-700">{{ errorMessage }}</p>
                  </div>
                </div>
              </div>
            </transition>

            <!-- 登录按钮 -->
            <el-form-item>
              <button
                type="button"
                :disabled="loading"
                class="w-full btn-primary py-3.5 text-base font-semibold"
                @click="handleLogin"
              >
                <span v-if="!loading">登录</span>
                <span v-else class="flex items-center justify-center">
                  <svg class="animate-spin h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  登录中...
                </span>
              </button>
            </el-form-item>
          </el-form>

          <!-- 底部链接 -->
          <div class="text-center space-y-3 pt-4 border-t border-gray-100">
            <p class="text-sm text-gray-600">
              还没有账号？
              <router-link
                to="/register"
                class="text-bright-cyan hover:text-bright-cyan-dark font-medium transition-colors"
              >
                立即注册
              </router-link>
            </p>
            <p class="text-xs text-gray-500">
              如需帮助,请联系系统管理员
            </p>
          </div>
        </div>

        <!-- 页脚信息 -->
        <div class="text-center mt-6 text-sm text-gray-500">
          <p>&copy; 2025 智能目标检测系统. All rights reserved.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { User, Lock, WarningFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import ParticlesBg from '@/components/common/ParticlesBg.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const loginFormRef = ref(null)
const loading = ref(false)
const errorMessage = ref('')

const loginForm = reactive({
  username: '',
  password: '',
})

const loginRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少为 6 位', trigger: 'blur' },
  ],
}

const handleLogin = async () => {
  if (!loginFormRef.value) return

  errorMessage.value = ''

  await loginFormRef.value.validate(async (valid) => {
    if (!valid) return

    loading.value = true

    try {
      const success = await authStore.login(loginForm.username, loginForm.password)

      if (success) {
        ElMessage.success('登录成功')
        // 登录成功,跳转到之前的页面或首页
        const redirect = route.query.redirect || '/'
        router.push(redirect)
      } else {
        errorMessage.value = '用户名或密码错误,请重试'
      }
    } catch (error) {
      errorMessage.value = error.message || '登录失败,请稍后重试'
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
/* 特性项样式 */
.feature-item {
  @apply flex flex-col items-center text-white/80 transition-all duration-300;
}

.feature-item:hover {
  @apply text-white transform -translate-y-1;
}

.feature-icon {
  @apply w-10 h-10 md:w-12 md:h-12 rounded-xl bg-bright-cyan/20 backdrop-blur-sm border border-bright-cyan/30 flex items-center justify-center;
}

/* 表单输入框样式增强 */
.form-input :deep(.el-input__wrapper) {
  @apply transition-all duration-300;
}

.form-input :deep(.el-input__wrapper:focus-within) {
  @apply shadow-glow-cyan;
}

/* 动画 */
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease-out;
}

.slide-down-enter-from {
  transform: translateY(-10px);
  opacity: 0;
}

.slide-down-leave-to {
  transform: translateY(-10px);
  opacity: 0;
}
</style>
