<script setup lang="ts">
import { onMounted, ref } from 'vue'
import {
  NAvatar,
  NButton,
  NCard,
  NFormItem,
  NIcon,
  NInput,
  NSpin,
  useMessage,
} from 'naive-ui'
import { CloudUploadOutline, SaveOutline } from '@vicons/ionicons5'
import { getMe, updateMe, uploadAvatar } from '../api/users'
import { useAuthStore } from '../stores/auth'
import { compressImageFile } from '../utils/image'

const message = useMessage()
const auth = useAuthStore()

const loading = ref(false)
const saving = ref(false)
const uploadingAvatar = ref(false)

const nickname = ref('')
const phone = ref('')
const email = ref('')
const avatarUrl = ref('')
const createdAt = ref('')

const avatarText = ref('U')

onMounted(async () => {
  loading.value = true
  try {
    const { data } = await getMe()
    nickname.value = data.nickname || ''
    phone.value = data.phone || ''
    email.value = data.email || ''
    avatarUrl.value = data.avatar_url || ''
    createdAt.value = data.created_at
      ? new Date(data.created_at).toLocaleDateString('zh-CN')
      : ''
    applyAuth(data)
  } catch {
    message.error('加载个人资料失败')
  } finally {
    loading.value = false
  }
})

/** 同步到全局 store（状态栏头像/名字即时更新） */
function applyAuth(u: Parameters<typeof auth.setUser>[0]) {
  auth.setUser({ ...auth.user!, ...u })
  avatarText.value = (auth.displayName || 'U').slice(0, 1).toUpperCase()
}

function extractError(e: any, fallback: string): string {
  const detail = e?.response?.data?.detail
  if (typeof detail === 'string' && detail) return detail
  return fallback
}

async function onPickAvatar(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  input.value = ''
  if (!file) return
  if (!file.type.startsWith('image/')) {
    message.warning('请选择图片文件')
    return
  }
  uploadingAvatar.value = true
  try {
    // 头像压缩到 256px，足够展示且体积小
    const compressed = await compressImageFile(file, 256, 0.9)
    const { data } = await uploadAvatar(compressed)
    avatarUrl.value = data.avatar_url
    applyAuth(data)
    message.success('头像已更新')
  } catch (err: any) {
    message.error(extractError(err, '头像上传失败'))
  } finally {
    uploadingAvatar.value = false
  }
}

async function save() {
  if (email.value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)) {
    message.warning('邮箱格式不正确')
    return
  }
  if (phone.value && !/^[\d+\-\s]{5,20}$/.test(phone.value)) {
    message.warning('手机号格式不正确')
    return
  }
  saving.value = true
  try {
    const { data } = await updateMe({
      nickname: nickname.value.trim(),
      phone: phone.value.trim(),
      email: email.value.trim(),
    })
    applyAuth(data)
    message.success('资料已保存')
  } catch (err: any) {
    message.error(extractError(err, '保存失败'))
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="page">
    <NSpin :show="loading">
      <NCard class="profile-card" :bordered="false">
        <div class="profile-head">
          <label class="avatar-wrap" title="点击更换头像">
            <NAvatar round :size="96" class="avatar">
              <img v-if="avatarUrl" :src="avatarUrl" alt="头像" />
              <span v-else>{{ avatarText }}</span>
            </NAvatar>
            <span class="avatar-mask" :class="{ busy: uploadingAvatar }">
              <NIcon :component="CloudUploadOutline" :size="20" />
              {{ uploadingAvatar ? '上传中' : '更换' }}
            </span>
            <input type="file" accept="image/*" class="avatar-input" @change="onPickAvatar" />
          </label>
          <div class="head-info">
            <h2>{{ auth.displayName }}</h2>
            <p class="sub">@{{ auth.user?.username }}<template v-if="createdAt"> · 加入于 {{ createdAt }}</template></p>
          </div>
        </div>

        <div class="form">
          <NFormItem label="平台昵称">
            <NInput v-model:value="nickname" maxlength="50" placeholder="展示在状态栏与留言处的名字" />
          </NFormItem>
          <NFormItem label="用户名">
            <NInput :value="auth.user?.username" disabled />
          </NFormItem>
          <NFormItem label="手机号">
            <NInput v-model:value="phone" maxlength="20" placeholder="仅自己可见" />
          </NFormItem>
          <NFormItem label="邮箱">
            <NInput v-model:value="email" maxlength="120" placeholder="仅自己可见" />
          </NFormItem>
          <div class="actions">
            <NButton type="primary" :loading="saving" @click="save">
              <template #icon><NIcon :component="SaveOutline" /></template>
              保存资料
            </NButton>
          </div>
        </div>
      </NCard>
    </NSpin>
  </div>
</template>

<style scoped>
.page {
  max-width: 640px;
  margin: 0 auto;
  /* 卡片在状态栏下方剩余空间内垂直居中，矮窗口时保底留白 */
  min-height: calc(100vh - 52px);
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 24px 16px 40px;
  box-sizing: border-box;
}
@media (min-width: 673px) {
  .page {
    padding-left: 0;
    padding-right: 0;
  }
}

.profile-card {
  border-radius: 16px;
  box-shadow: 0 4px 18px rgba(59, 130, 246, 0.1);
  animation: card-in 0.4s ease backwards;
}
@keyframes card-in {
  from {
    opacity: 0;
    transform: translateY(14px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 头像区 */
.profile-head {
  display: flex;
  align-items: center;
  gap: 20px;
  padding-bottom: 18px;
  border-bottom: 1px dashed rgba(147, 197, 253, 0.5);
  margin-bottom: 20px;
}
.avatar-wrap {
  position: relative;
  cursor: pointer;
  border-radius: 50%;
  flex-shrink: 0;
}
.avatar {
  background: linear-gradient(135deg, #3b82f6, #60a5fa);
  color: #fff;
  font-size: 34px;
  font-weight: 700;
  box-shadow: 0 6px 18px rgba(59, 130, 246, 0.35);
}
.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
  display: block;
}
.avatar-mask {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  background: rgba(15, 23, 42, 0.45);
  color: #fff;
  font-size: 11px;
  font-weight: 600;
  opacity: 0;
  transition: opacity 0.2s ease;
}
.avatar-wrap:hover .avatar-mask {
  opacity: 1;
}
.avatar-mask.busy {
  opacity: 1;
}
.avatar-input {
  display: none;
}
.head-info h2 {
  margin: 0 0 6px;
  font-size: 20px;
  color: #1e3a8a;
}
.head-info .sub {
  margin: 0;
  font-size: 12.5px;
  color: #94a3b8;
}

/* 表单 */
.form :deep(.n-form-item-label) {
  font-weight: 600;
  color: #475569;
}
.actions {
  display: flex;
  justify-content: flex-end;
  padding-top: 4px;
}
.actions :deep(.n-button) {
  position: relative;
  overflow: hidden;
}
.actions :deep(.n-button)::after {
  content: '';
  position: absolute;
  top: 0;
  left: -80%;
  width: 55%;
  height: 100%;
  background: linear-gradient(105deg, transparent, rgba(255, 255, 255, 0.55) 50%, transparent);
  transform: skewX(-20deg);
  pointer-events: none;
}
.actions :deep(.n-button:hover)::after {
  animation: btn-shine 0.8s ease;
}
@keyframes btn-shine {
  from {
    left: -80%;
  }
  to {
    left: 140%;
  }
}
</style>
