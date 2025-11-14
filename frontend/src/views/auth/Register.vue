<template>
  <div class="min-h-screen flex flex-col md:flex-row">
    <!-- 左侧品牌区 -->
    <div class="relative w-full md:w-3/5 lg:w-1/2 bg-gradient-deep flex items-center justify-center p-8 md:p-12 overflow-hidden">
      <!-- 粒子背景 -->
      <ParticlesBg theme="ocean" :particle-count="80" />

      <!-- 品牌内容 -->
      <div class="relative z-10 text-center text-white space-y-6 max-w-2xl animate-fade-in">
        <!-- Logo图标 -->
        <div class="flex justify-center">
          <div class="w-20 h-20 md:w-24 md:h-24 bg-coral-orange/20 rounded-2xl flex items-center justify-center backdrop-blur-sm border-2 border-coral-orange/30 animate-float">
            <svg class="w-12 h-12 md:w-14 md:h-14 text-coral-orange" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
            </svg>
          </div>
        </div>

        <!-- 系统标题 -->
        <div>
          <h1 class="text-3xl md:text-4xl lg:text-5xl font-bold mb-3 md:mb-4">
            加入我们
          </h1>
          <p class="text-lg md:text-xl text-coral-orange font-medium">
            开启智能检测之旅
          </p>
        </div>

        <!-- 注册优势 -->
        <div class="space-y-3 pt-6">
          <p class="text-base md:text-lg text-white/90">
            免费注册 · 即刻使用 · 专业服务
          </p>
          <p class="text-sm md:text-base text-white/70">
            注册后即可体验强大的AI检测功能
          </p>
        </div>

        <!-- 优势列表 -->
        <div class="space-y-4 pt-8 text-left max-w-md mx-auto">
          <div class="flex items-start space-x-3">
            <div class="flex-shrink-0 w-6 h-6 rounded-full bg-coral-orange/20 flex items-center justify-center mt-1">
              <svg class="w-4 h-4 text-coral-orange" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <div>
              <h3 class="font-semibold text-white">多模型支持</h3>
              <p class="text-sm text-white/70">支持多种YOLO模型，精准识别</p>
            </div>
          </div>
          <div class="flex items-start space-x-3">
            <div class="flex-shrink-0 w-6 h-6 rounded-full bg-coral-orange/20 flex items-center justify-center mt-1">
              <svg class="w-4 h-4 text-coral-orange" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <div>
              <h3 class="font-semibold text-white">历史记录</h3>
              <p class="text-sm text-white/70">自动保存检测结果，随时查看</p>
            </div>
          </div>
          <div class="flex items-start space-x-3">
            <div class="flex-shrink-0 w-6 h-6 rounded-full bg-coral-orange/20 flex items-center justify-center mt-1">
              <svg class="w-4 h-4 text-coral-orange" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <div>
              <h3 class="font-semibold text-white">数据安全</h3>
              <p class="text-sm text-white/70">企业级安全保障，数据加密存储</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧注册表单区 -->
    <div class="w-full md:w-2/5 lg:w-1/2 bg-light-gray flex items-center justify-center p-6 md:p-8 lg:p-12">
      <div class="w-full max-w-md animate-slide-up">
        <!-- 表单卡片 -->
        <div class="bg-white rounded-2xl shadow-strong p-8 md:p-10">
          <!-- 表单头部 -->
          <div class="text-center mb-8">
            <h2 class="text-2xl md:text-3xl font-bold text-deep-blue mb-2">
              创建新账号
            </h2>
            <p class="text-gray-600">填写信息完成注册</p>
          </div>

          <!-- 注册表单 -->
          <el-form
            ref="registerFormRef"
            :model="registerForm"
            :rules="registerRules"
            size="large"
            @submit.prevent="handleRegister"
          >
            <!-- 用户名输入 -->
            <el-form-item prop="username">
              <el-input
                v-model="registerForm.username"
                placeholder="请输入用户名（3-50个字符）"
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

            <!-- 邮箱输入 -->
            <el-form-item prop="email">
              <el-input
                v-model="registerForm.email"
                placeholder="请输入电子邮箱"
                clearable
                class="form-input"
              >
                <template #prefix>
                  <el-icon class="text-bright-cyan">
                    <Message />
                  </el-icon>
                </template>
              </el-input>
            </el-form-item>

            <!-- 密码输入 -->
            <el-form-item prop="password">
              <el-input
                v-model="registerForm.password"
                type="password"
                placeholder="请输入密码（至少6位）"
                show-password
                class="form-input"
              >
                <template #prefix>
                  <el-icon class="text-bright-cyan">
                    <Lock />
                  </el-icon>
                </template>
              </el-input>
            </el-form-item>

            <!-- 确认密码输入 -->
            <el-form-item prop="confirmPassword">
              <el-input
                v-model="registerForm.confirmPassword"
                type="password"
                placeholder="请确认密码"
                show-password
                class="form-input"
                @keyup.enter="handleRegister"
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

            <!-- 注册按钮 -->
            <el-form-item>
              <button
                type="button"
                :disabled="loading"
                class="w-full btn-primary py-3.5 text-base font-semibold"
                @click="handleRegister"
              >
                <span v-if="!loading">注册</span>
                <span v-else class="flex items-center justify-center">
                  <svg class="animate-spin h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  注册中...
                </span>
              </button>
            </el-form-item>
          </el-form>

          <!-- 底部链接 -->
          <div class="text-center space-y-3 pt-4 border-t border-gray-100">
            <p class="text-sm text-gray-600">
              已有账号？
              <router-link
                to="/login"
                class="text-bright-cyan hover:text-bright-cyan-dark font-medium transition-colors"
              >
                立即登录
              </router-link>
            </p>
            <p class="text-xs text-gray-500">
              注册即表示您同意我们的服务条款和隐私政策
            </p>
          </div>
        </div>

        <!-- 页脚信息 -->
        <div class="text-center mt-6 text-sm text-gray-500">
          <p>&copy; 2025 水下目标智能检测平台. All rights reserved.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { User, Message, Lock, WarningFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import ParticlesBg from '@/components/common/ParticlesBg.vue'

const router = useRouter()
const authStore = useAuthStore()

const registerFormRef = ref(null)
const loading = ref(false)
const errorMessage = ref('')

const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
})

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== registerForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const registerRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度为 3-50 个字符', trigger: 'blur' },
  ],
  email: [
    { required: true, message: '请输入电子邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 50, message: '密码长度为 6-50 位', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' },
  ],
}

const handleRegister = async () => {
  if (!registerFormRef.value) return

  errorMessage.value = ''

  await registerFormRef.value.validate(async (valid) => {
    if (!valid) return

    loading.value = true

    try {
      const success = await authStore.register({
        username: registerForm.username,
        email: registerForm.email,
        password: registerForm.password,
      })

      if (success) {
        ElMessage.success('注册成功，请登录')
        router.push('/login')
      } else {
        errorMessage.value = '注册失败，用户名或邮箱可能已存在'
      }
    } catch (error) {
      errorMessage.value = error.message || '注册失败，请稍后重试'
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
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
