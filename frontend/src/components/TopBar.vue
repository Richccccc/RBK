<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NAvatar, NButton, NIcon } from 'naive-ui'
import {
  BookOutline,
  ChatbubblesOutline,
  GridOutline,
  HomeOutline,
  LogOutOutline,
} from '@vicons/ionicons5'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

// 一级菜单（顶栏内切换，不再使用左上角浮动菜单）
const menus = [
  { key: 'home', label: '博客', icon: HomeOutline, path: '/' },
  { key: 'diary', label: '日记', icon: BookOutline, path: '/diary' },
  { key: 'templates', label: '模板', icon: GridOutline, path: '/templates' },
  { key: 'guestbook', label: '留言板', icon: ChatbubblesOutline, path: '/guestbook' },
]

// 问候语与日期（横向排开，紧凑显示）
const greeting = computed(() => {
  const h = new Date().getHours()
  if (h >= 5 && h < 11) return '早上好'
  if (h >= 11 && h < 18) return '下午好'
  return '晚上好'
})
const today = computed(() =>
  new Date().toLocaleDateString('zh-CN', { month: 'long', day: 'numeric', weekday: 'long' }),
)

const username = computed(() => auth.user?.username || '朋友')
const avatarText = computed(() => username.value.slice(0, 1).toUpperCase())

function isActive(path: string) {
  return route.path === path
}

function logout() {
  auth.logout()
  // 显式去登录页（push('/') 在首页时是同路由导航，守卫不会重定向）
  router.push('/login')
}
</script>

<template>
  <header class="topbar">
    <div class="bar-inner">
      <!-- 左：头像 + 名字 -->
      <div class="me">
        <NAvatar round :size="28" class="me-avatar">{{ avatarText }}</NAvatar>
        <span class="me-name">{{ username }}</span>
      </div>

      <!-- 中：一级菜单 -->
      <nav class="nav">
        <button
          v-for="m in menus"
          :key="m.key"
          class="nav-item"
          :class="{ active: isActive(m.path) }"
          @click="router.push(m.path)"
        >
          <span class="n-shine" aria-hidden="true"></span>
          <NIcon :component="m.icon" :size="15" />
          <span>{{ m.label }}</span>
        </button>
      </nav>

      <!-- 右：问候 + 日期 + 退出 -->
      <div class="right">
        <span class="greet">{{ greeting }}</span>
        <span class="dot">·</span>
        <span class="date">{{ today }}</span>
        <NButton
          quaternary
          circle
          size="tiny"
          class="logout"
          title="退出登录"
          @click="logout"
        >
          <template #icon><NIcon :component="LogOutOutline" :size="16" /></template>
        </NButton>
      </div>
    </div>
  </header>
</template>

<style scoped>
/* 紧凑状态栏：吸附顶部，玻璃质感 */
.topbar {
  position: sticky;
  top: 0;
  z-index: 1500;
  background: rgba(255, 255, 255, 0.82);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(147, 197, 253, 0.35);
  box-shadow: 0 2px 12px rgba(96, 140, 220, 0.08);
}
.bar-inner {
  max-width: 1320px;
  margin: 0 auto;
  height: 52px;
  padding: 0 20px;
  display: flex;
  align-items: center;
  gap: 18px;
}

/* 左侧头像与名字 */
.me {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}
.me-avatar {
  background: linear-gradient(135deg, #3b82f6, #60a5fa);
  color: #fff;
  font-weight: 700;
  font-size: 13px;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.35);
}
.me-name {
  font-size: 14px;
  font-weight: 600;
  color: #1e3a8a;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 中间一级菜单 */
.nav {
  display: flex;
  align-items: center;
  gap: 4px;
  flex: 1;
  min-width: 0;
  overflow-x: auto;
  scrollbar-width: none;
}
.nav::-webkit-scrollbar {
  display: none;
}
.nav-item {
  position: relative;
  overflow: hidden;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 6px 14px;
  border: none;
  border-radius: 999px;
  background: transparent;
  color: #4b5563;
  font-size: 13.5px;
  font-family: inherit;
  font-weight: 500;
  cursor: pointer;
  white-space: nowrap;
  transition: color 0.2s ease, background 0.2s ease, box-shadow 0.2s ease;
}
.nav-item:hover {
  color: #2563eb;
  background: rgba(219, 234, 254, 0.6);
}
.nav-item.active {
  color: #fff;
  background: linear-gradient(120deg, #2563eb, #3b82f6);
  box-shadow: 0 3px 10px rgba(37, 99, 235, 0.35);
}
/* hover 流光扫过 */
.n-shine {
  position: absolute;
  top: 0;
  left: -80%;
  width: 55%;
  height: 100%;
  background: linear-gradient(105deg, transparent, rgba(255, 255, 255, 0.5) 50%, transparent);
  transform: skewX(-20deg);
  pointer-events: none;
}
.nav-item:hover .n-shine {
  animation: n-shine 0.8s ease;
}
@keyframes n-shine {
  from {
    left: -80%;
  }
  to {
    left: 140%;
  }
}

/* 右侧问候与日期 */
.right {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
  font-size: 12.5px;
  color: rgba(30, 58, 138, 0.66);
  letter-spacing: 0.5px;
}
.greet {
  font-weight: 600;
  color: #2563eb;
}
.dot {
  color: rgba(30, 58, 138, 0.35);
}
.logout {
  margin-left: 4px;
  color: #93a6c4;
}
.logout:hover {
  color: #2563eb;
}

@media (max-width: 860px) {
  .date,
  .dot {
    display: none;
  }
}
@media (max-width: 640px) {
  .bar-inner {
    padding: 0 12px;
    gap: 10px;
  }
  .greet {
    display: none;
  }
  .me-name {
    display: none;
  }
}
</style>
