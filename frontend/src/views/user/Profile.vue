<template>
  <div class="profile-container">
    <div class="header">
      <h1>个人中心</h1>
      <el-button @click="router.push('/')">返回首页</el-button>
    </div>

    <div class="content">
      <!-- 头像和基本信息 -->
      <el-card class="avatar-card">
        <div class="avatar-section">
          <el-avatar :size="120" :src="avatarUrl" class="avatar">
            <el-icon :size="60"><User /></el-icon>
          </el-avatar>
          <div class="avatar-actions">
            <el-upload
              :show-file-list="false"
              :before-upload="beforeAvatarUpload"
              :http-request="() => {}"
              accept="image/*"
            >
              <el-button type="primary" size="small">
                <el-icon><Upload /></el-icon>
                上传头像
              </el-button>
            </el-upload>
            <el-button
              v-if="authStore.userInfo?.avatar_url"
              type="danger"
              size="small"
              @click="handleDeleteAvatar"
            >
              <el-icon><Delete /></el-icon>
              删除头像
            </el-button>
          </div>
        </div>
        <div class="user-basic-info">
          <h2>{{ authStore.userInfo?.nickname || authStore.userInfo?.username }}</h2>
          <el-tag :type="authStore.isAdmin ? 'danger' : 'success'">
            {{ authStore.userInfo?.role === 'admin' ? '管理员' : '普通用户' }}
          </el-tag>
        </div>
      </el-card>

      <!-- 个人信息编辑 -->
      <el-card class="info-card">
        <template #header>
          <div class="card-header">
            <span>个人信息</span>
            <el-button v-if="!editing" type="primary" @click="startEdit">编辑</el-button>
            <div v-else>
              <el-button @click="cancelEdit">取消</el-button>
              <el-button type="primary" @click="saveProfile">保存</el-button>
            </div>
          </div>
        </template>

        <el-form :model="profileForm" label-width="100px" :disabled="!editing">
          <el-form-item label="用户名">
            <el-input v-model="authStore.userInfo.username" disabled />
          </el-form-item>
          <el-form-item label="昵称">
            <el-input v-model="profileForm.nickname" placeholder="请输入昵称或真实姓名" />
          </el-form-item>
          <el-form-item label="邮箱">
            <el-input v-model="profileForm.email" placeholder="请输入邮箱" />
          </el-form-item>
          <el-form-item label="手机号">
            <el-input v-model="profileForm.phone" placeholder="请输入手机号" />
          </el-form-item>
          <el-form-item label="个人简介">
            <el-input
              v-model="profileForm.bio"
              type="textarea"
              :rows="3"
              placeholder="介绍一下自己吧"
              maxlength="500"
              show-word-limit
            />
          </el-form-item>
          <el-form-item label="创建时间">
            <el-input :value="formatDate(authStore.userInfo?.created_at)" disabled />
          </el-form-item>
        </el-form>
      </el-card>

      <!-- 账号操作 -->
      <el-card class="actions-card">
        <template #header>
          <span>账号操作</span>
        </template>
        <div class="actions">
          <el-button
            v-if="authStore.isAdmin"
            type="warning"
            @click="showPasswordDialog = true"
          >
            <el-icon><Lock /></el-icon>
            修改密码
          </el-button>
          <el-button type="danger" @click="authStore.logout()">
            <el-icon><SwitchButton /></el-icon>
            退出登录
          </el-button>
        </div>
      </el-card>
    </div>

    <!-- 头像裁剪对话框 -->
    <el-dialog
      v-model="showCropperDialog"
      title="裁剪头像"
      width="600px"
      :close-on-click-modal="false"
      :destroy-on-close="true"
      @opened="handleDialogOpened"
    >
      <div class="cropper-container">
        <VueCropper
          v-if="cropperImg"
          ref="cropperRef"
          :img="cropperImg"
          :output-size="1"
          :output-type="'jpeg'"
          :info="true"
          :full="false"
          :can-move="true"
          :can-move-box="true"
          :fixed-box="false"
          :original="false"
          :auto-crop="true"
          :auto-crop-width="200"
          :auto-crop-height="200"
          :center-box="true"
          :fixed="true"
          :fixed-number="[1, 1]"
          mode="cover"
        />
        <div v-else class="cropper-placeholder">
          <el-icon :size="60" color="#ccc"><Picture /></el-icon>
          <p>正在加载图片...</p>
        </div>
      </div>
      <template #footer>
        <el-button @click="showCropperDialog = false">取消</el-button>
        <el-button type="primary" :loading="uploading" @click="handleCropperUpload">
          确认上传
        </el-button>
      </template>
    </el-dialog>

    <!-- 修改密码对话框 -->
    <el-dialog
      v-model="showPasswordDialog"
      title="修改密码"
      width="400px"
      :close-on-click-modal="false"
    >
      <el-form :model="passwordForm" label-width="80px">
        <el-form-item label="旧密码">
          <el-input
            v-model="passwordForm.old_password"
            type="password"
            placeholder="请输入旧密码"
            show-password
          />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input
            v-model="passwordForm.new_password"
            type="password"
            placeholder="请输入新密码（至少6位）"
            show-password
          />
        </el-form-item>
        <el-form-item label="确认密码">
          <el-input
            v-model="passwordForm.confirm_password"
            type="password"
            placeholder="请再次输入新密码"
            show-password
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showPasswordDialog = false">取消</el-button>
        <el-button type="primary" :loading="changingPassword" @click="handleChangePassword">
          确认修改
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { updateProfile, uploadAvatar, deleteAvatar, changePassword } from '@/api/auth'
import { ElMessage, ElMessageBox } from 'element-plus'
import { User, Upload, Delete, Lock, SwitchButton, Picture } from '@element-plus/icons-vue'
import { VueCropper } from 'vue-cropper'
import 'vue-cropper/dist/index.css'

const router = useRouter()
const authStore = useAuthStore()

// 头像 URL（计算属性，确保响应式更新）
const avatarUrl = computed(() => {
  if (authStore.userInfo?.avatar_url) {
    const baseUrl = import.meta.env.VITE_API_BASE_URL.replace('/api/v1', '')
    const timestamp = Date.now()
    return `${baseUrl}/${authStore.userInfo.avatar_url}?t=${timestamp}`
  }
  return ''
})

// 编辑状态
const editing = ref(false)
const profileForm = reactive({
  nickname: '',
  email: '',
  phone: '',
  bio: ''
})

// 头像裁剪
const showCropperDialog = ref(false)
const cropperRef = ref(null)
const uploading = ref(false)
const cropperImg = ref('')

// 密码修改
const showPasswordDialog = ref(false)
const changingPassword = ref(false)
const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

// 初始化
onMounted(() => {
  initProfileForm()
})

// 初始化表单数据
function initProfileForm() {
  if (authStore.userInfo) {
    profileForm.nickname = authStore.userInfo.nickname || ''
    profileForm.email = authStore.userInfo.email || ''
    profileForm.phone = authStore.userInfo.phone || ''
    profileForm.bio = authStore.userInfo.bio || ''
  }
}

// 开始编辑
function startEdit() {
  editing.value = true
  initProfileForm()
}

// 取消编辑
function cancelEdit() {
  editing.value = false
  initProfileForm()
}

// 保存个人信息
async function saveProfile() {
  try {
    const data = {}
    if (profileForm.nickname) data.nickname = profileForm.nickname
    if (profileForm.email) data.email = profileForm.email
    if (profileForm.phone) data.phone = profileForm.phone
    if (profileForm.bio) data.bio = profileForm.bio

    await updateProfile(data)
    await authStore.fetchUserInfo()
    editing.value = false
    ElMessage.success('个人信息更新成功')
  } catch (error) {
    console.error('Update profile error:', error)
    ElMessage.error(error.response?.data?.detail || '个人信息更新失败')
  }
}

// 格式化日期
function formatDate(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

// 对话框打开后的处理
function handleDialogOpened() {
  nextTick(() => {
    if (cropperRef.value) {
      cropperRef.value.refresh()
    }
  })
}

// 上传前验证
function beforeAvatarUpload(file) {
  const isImage = file.type.startsWith('image/')
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('图片大小不能超过 2MB!')
    return false
  }

  // 读取文件并显示裁剪器
  const reader = new FileReader()
  reader.onload = (e) => {
    cropperImg.value = e.target.result
    showCropperDialog.value = true
  }
  reader.readAsDataURL(file)

  return false // 阻止自动上传
}

// 裁剪并上传
async function handleCropperUpload() {
  if (!cropperRef.value) {
    ElMessage.error('裁剪器未准备好，请重试')
    return
  }

  try {
    uploading.value = true

    // 获取裁剪后的 blob
    cropperRef.value.getCropBlob(async (blob) => {
      try {
        // 创建 File 对象
        const file = new File([blob], 'avatar.jpg', { type: 'image/jpeg' })

        // 上传
        const result = await uploadAvatar(file)
        console.log('头像上传成功:', result)

        // 刷新用户信息
        await authStore.fetchUserInfo()
        console.log('用户信息已更新:', authStore.userInfo)

        showCropperDialog.value = false
        cropperImg.value = '' // 清空裁剪器图片
        ElMessage.success('头像上传成功')
      } catch (error) {
        console.error('Upload avatar error:', error)
        ElMessage.error(error.response?.data?.detail || '头像上传失败')
      } finally {
        uploading.value = false
      }
    })
  } catch (error) {
    uploading.value = false
    ElMessage.error('裁剪失败，请重试')
    console.error('Cropper error:', error)
  }
}

// 删除头像
async function handleDeleteAvatar() {
  try {
    await ElMessageBox.confirm('确定要删除头像吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await deleteAvatar()
    await authStore.fetchUserInfo()
    ElMessage.success('头像删除成功')
  } catch (error) {
    if (error === 'cancel') return
    console.error('Delete avatar error:', error)
    ElMessage.error(error.response?.data?.detail || '头像删除失败')
  }
}

// 修改密码
async function handleChangePassword() {
  if (!passwordForm.old_password) {
    ElMessage.warning('请输入旧密码')
    return
  }
  if (!passwordForm.new_password || passwordForm.new_password.length < 6) {
    ElMessage.warning('新密码至少6位')
    return
  }
  if (passwordForm.new_password !== passwordForm.confirm_password) {
    ElMessage.warning('两次输入的密码不一致')
    return
  }

  try {
    changingPassword.value = true
    await changePassword({
      old_password: passwordForm.old_password,
      new_password: passwordForm.new_password
    })

    showPasswordDialog.value = false
    passwordForm.old_password = ''
    passwordForm.new_password = ''
    passwordForm.confirm_password = ''

    ElMessage.success('密码修改成功')
  } catch (error) {
    console.error('Change password error:', error)
    ElMessage.error(error.response?.data?.detail || '密码修改失败')
  } finally {
    changingPassword.value = false
  }
}
</script>

<style scoped>
.profile-container {
  min-height: 100vh;
  background: #f5f7fa;
}

.header {
  background: white;
  padding: 20px 40px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header h1 {
  margin: 0;
  font-size: 24px;
  color: #333;
}

.content {
  max-width: 900px;
  margin: 40px auto;
  padding: 0 20px;
}

/* 头像卡片 */
.avatar-card {
  margin-bottom: 24px;
}

.avatar-section {
  display: flex;
  align-items: center;
  gap: 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
}

.avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.avatar-actions {
  display: flex;
  gap: 12px;
}

.user-basic-info {
  margin-top: 20px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-basic-info h2 {
  margin: 0;
  font-size: 20px;
  color: #333;
}

/* 信息卡片 */
.info-card {
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}

/* 操作卡片 */
.actions {
  display: flex;
  gap: 12px;
}

/* 裁剪器 */
.cropper-container {
  width: 100%;
  height: 400px;
  background-color: #f5f5f5;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  border-radius: 4px;
}

:deep(.vue-cropper) {
  width: 100%;
  height: 100%;
  background-color: #f5f5f5;
}

:deep(.cropper-view-box) {
  outline: 1px solid rgba(0, 191, 255, 0.75);
  outline-color: rgba(0, 191, 255, 0.75);
}

:deep(.cropper-point) {
  background-color: #00bfff;
}

:deep(.cropper-line) {
  background-color: #00bfff;
}

.cropper-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #999;
}

.cropper-placeholder p {
  margin-top: 12px;
  font-size: 14px;
}
</style>
