<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NButton, NConfigProvider, NForm, NFormItem, NInput, darkTheme, useMessage } from 'naive-ui'
import { login } from '../api/auth'
import { useAuthStore } from '../stores/auth'
import MeteorBackground from '../components/MeteorBackground.vue'

// 卡片内局部深色主题：输入框透出星空玻璃质感；按约定 primary 必须覆盖为蓝，防止暗色主题默认绿
const cardTheme = {
  common: {
    primaryColor: '#3b82f6',
    primaryColorHover: '#60a5fa',
    primaryColorPressed: '#2563eb',
    primaryColorSuppl: '#3b82f6',
    successColor: '#0ea5e9',
  },
}

const route = useRoute()
const router = useRouter()
const message = useMessage()
const auth = useAuthStore()

const username = ref('')
const password = ref('')
const loading = ref(false)

// 卡片 3D 倾斜（跟随鼠标）
const cardRef = ref<HTMLElement | null>(null)
const rx = ref(0)
const ry = ref(0)

function onMove(e: MouseEvent) {
  const el = cardRef.value
  if (!el) return
  const r = el.getBoundingClientRect()
  const dx = (e.clientX - (r.left + r.width / 2)) / (r.width / 2)
  const dy = (e.clientY - (r.top + r.height / 2)) / (r.height / 2)
  ry.value = Math.max(-12, Math.min(12, dx * 12))
  rx.value = Math.max(-12, Math.min(12, -dy * 12))
}

function onLeave() {
  rx.value = 0
  ry.value = 0
}

const cardStyle = computed(() => {
  const resting = rx.value === 0 && ry.value === 0
  return {
    transform: `perspective(950px) rotateX(${rx.value}deg) rotateY(${ry.value}deg)`,
    transition: resting ? 'transform .6s ease' : 'transform .12s ease-out',
  }
})

async function submit() {
  if (!username.value || !password.value) {
    message.warning('请输入用户名和密码')
    return
  }
  loading.value = true
  try {
    const { data } = await login(username.value, password.value)
    auth.setAuth(data.access_token, data.user)
    // 标记一次性欢迎过渡屏（App.vue 检测后播放）
    sessionStorage.setItem('welcome-pending', '1')
    message.success('登录成功')
    const redirect = (route.query.redirect as string) || '/'
    router.push(redirect)
  } catch (e: any) {
    message.error(e?.response?.data?.detail || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-wrap" @mousemove="onMove" @mouseleave="onLeave">
    <MeteorBackground />

    <div ref="cardRef" class="login-card" :style="cardStyle">
      <NConfigProvider abstract :theme="darkTheme" :theme-overrides="cardTheme">
        <div class="brand">
          <h1 class="brand-title">我的博客</h1>
          <p class="brand-slogan">记录此刻 · 写给时间</p>
        </div>
        <NForm @keyup.enter="submit">
          <NFormItem label="用户名">
            <NInput v-model:value="username" placeholder="用户名" />
          </NFormItem>
          <NFormItem label="密码">
            <NInput v-model:value="password" type="password" show-password-on="click" placeholder="密码" />
          </NFormItem>
          <NButton type="primary" block :loading="loading" @click="submit">进入我的博客</NButton>
        </NForm>
      </NConfigProvider>
    </div>
  </div>
</template>

<style scoped>
.login-wrap {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  position: relative;
  overflow: hidden;
  /* 清透浅蓝底色，流星画布叠在其上；叠加两团柔光更灵动 */
  background:
    radial-gradient(560px 380px at 78% 18%, rgba(160, 205, 255, 0.32), transparent 70%),
    radial-gradient(640px 460px at 14% 82%, rgba(130, 175, 255, 0.28), transparent 72%),
    linear-gradient(165deg, #2c4fa4 0%, #3e72d6 45%, #71a9f2 100%);
}

/* 星空玻璃卡片：半透明浅蓝，透出背景流星 */
.login-card {
  width: 100%;
  max-width: 400px;
  padding: 34px 30px 28px;
  border-radius: 18px;
  background: linear-gradient(160deg, rgba(130, 170, 240, 0.32) 0%, rgba(70, 110, 200, 0.44) 100%);
  backdrop-filter: blur(18px) saturate(150%);
  -webkit-backdrop-filter: blur(18px) saturate(150%);
  border: 1px solid rgba(200, 225, 255, 0.5);
  box-shadow:
    0 24px 70px rgba(30, 60, 140, 0.35),
    0 1px 0 rgba(255, 255, 255, 0.3) inset,
    0 -20px 46px rgba(140, 180, 255, 0.18) inset;
  animation: card-in 0.6s ease backwards;
  position: relative;
  z-index: 1;
  will-change: transform;
}
@keyframes card-in {
  from {
    opacity: 0;
    transform: perspective(950px) translateY(26px) rotateX(6deg);
  }
  to {
    opacity: 1;
    transform: perspective(950px) translateY(0) rotateX(0deg);
  }
}

.brand {
  text-align: center;
  margin-bottom: 18px;
}
.brand-title {
  margin: 0 0 6px;
  font-size: 27px;
  color: #f2f7ff;
  letter-spacing: 2px;
  text-shadow: 0 2px 14px rgba(59, 130, 246, 0.55);
}
.brand-slogan {
  margin: 0;
  font-size: 13px;
  color: #9ec5ff;
  letter-spacing: 3px;
}

@media (max-width: 640px) {
  .login-card {
    padding: 26px 20px 22px;
  }
}
</style>
