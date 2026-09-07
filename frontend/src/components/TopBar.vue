<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NAvatar, NButton, NIcon } from 'naive-ui'
import { GridOutline, HomeOutline, MenuOutline } from '@vicons/ionicons5'
import { useAuthStore } from '../stores/auth'
import DrawerMenu from './DrawerMenu.vue'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const menuOpen = ref(false)

// 状态栏快捷跳转（日记与留言板从菜单进入）
const shortcuts = [
  { key: 'home', label: '博客', icon: HomeOutline, path: '/' },
  { key: 'templates', label: '模板', icon: GridOutline, path: '/templates' },
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
</script>

<template>
  <header class="topbar">
    <div class="bar-inner">
      <!-- 左：菜单按钮 + 快捷跳转 -->
      <div class="left">
        <NButton quaternary circle size="small" class="menu-btn" title="菜单" @click="menuOpen = true">
          <template #icon><NIcon :component="MenuOutline" :size="19" /></template>
        </NButton>
        <button
          v-for="s in shortcuts"
          :key="s.key"
          class="nav-item"
          :class="{ active: route.path === s.path }"
          @click="router.push(s.path)"
        >
          <span class="n-shine" aria-hidden="true"></span>
          <NIcon :component="s.icon" :size="15" />
          <span>{{ s.label }}</span>
        </button>
      </div>

      <!-- 右：问候 + 日期 + 头像 + 名字 -->
      <div class="right">
        <span class="greet">{{ greeting }}</span>
        <span class="dot">·</span>
        <span class="date">{{ today }}</span>
        <NAvatar round :size="28" class="me-avatar">{{ avatarText }}</NAvatar>
        <span class="me-name">{{ username }}</span>
      </div>
    </div>

    <!-- 抽屉菜单：跳转 / 新建 / 退出 -->
    <DrawerMenu v-model:show="menuOpen" />
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
  justify-content: space-between;
  gap: 12px;
}

/* 左侧：菜单按钮 + 快捷跳转 */
.left {
  display: flex;
  align-items: center;
  gap: 4px;
  min-width: 0;
}
.menu-btn {
  color: #1e3a8a;
  margin-right: 2px;
}
.menu-btn:hover {
  color: #2563eb;
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

/* 右侧：问候 + 日期 + 头像 + 名字 */
.right {
  display: flex;
  align-items: center;
  gap: 8px;
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
.me-avatar {
  margin-left: 6px;
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

@media (max-width: 860px) {
  .date,
  .dot {
    display: none;
  }
}
@media (max-width: 640px) {
  .bar-inner {
    padding: 0 12px;
    gap: 8px;
  }
  .greet {
    display: none;
  }
  .me-name {
    display: none;
  }
}
</style>
