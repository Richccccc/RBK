<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import {
  NButton,
  NDrawer,
  NDrawerContent,
  NIcon,
  NTag,
  useMessage,
} from 'naive-ui'
import {
  BookmarkOutline,
  BookOutline,
  ChatbubblesOutline,
  GridOutline,
  HomeOutline,
  ImageOutline,
  LogOutOutline,
  PersonOutline,
  RocketOutline,
} from '@vicons/ionicons5'
import { useAuthStore } from '../stores/auth'

const props = defineProps<{ show: boolean }>()
const emit = defineEmits<{ (e: 'update:show', v: boolean): void }>()

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const message = useMessage()

// 可用功能
const menus = [
  { key: 'home', label: '博客', desc: '技术分享与随笔', icon: HomeOutline, path: '/' },
  { key: 'diary', label: '日记', desc: '记录日常点滴', icon: BookOutline, path: '/diary' },
  { key: 'templates', label: '模板', desc: 'Excel 在线预览', icon: GridOutline, path: '/templates' },
  { key: 'guestbook', label: '留言板', desc: '留下你想说的话', icon: ChatbubblesOutline, path: '/guestbook' },
]

// 占位菜单：预留未来功能入口
const placeholders = [
  { key: 'gallery', label: '相册', icon: ImageOutline },
  { key: 'fav', label: '收藏', icon: BookmarkOutline },
  { key: 'about', label: '关于', icon: PersonOutline },
]

function go(path: string) {
  emit('update:show', false)
  router.push(path)
}

function comingSoon(label: string) {
  message.info(`「${label}」正在筹备中，敬请期待`)
}

function logout() {
  emit('update:show', false)
  auth.logout()
  // 显式去登录页（push('/') 在首页时是同路由导航，守卫不会重定向）
  router.push('/login')
}
</script>

<template>
  <NDrawer
    :show="props.show"
    :width="260"
    placement="left"
    @update:show="(v: boolean) => emit('update:show', v)"
  >
    <NDrawerContent
      :closable="false"
      body-content-style="padding: 0;"
      :header-style="{ height: '0', padding: '0', overflow: 'hidden', borderBottom: 'none' }"
    >
      <!-- 导航 -->
      <p class="group-label first">导航</p>
      <nav class="menu-list">
        <button
          v-for="m in menus"
          :key="m.key"
          class="menu-item"
          :class="{ active: route.path === m.path }"
          @click="go(m.path)"
        >
          <span class="mi-shine" aria-hidden="true"></span>
          <span class="mi-icon"><NIcon :component="m.icon" :size="17" /></span>
          <span class="mi-text">
            <span class="mi-label">{{ m.label }}</span>
            <span class="mi-desc">{{ m.desc }}</span>
          </span>
          <span class="mi-dot" aria-hidden="true"></span>
        </button>
      </nav>

      <!-- 占位：即将上线 -->
      <p class="group-label soon">
        即将上线
        <NIcon :component="RocketOutline" :size="12" />
      </p>
      <nav class="menu-list">
        <button
          v-for="p in placeholders"
          :key="p.key"
          class="menu-item placeholder"
          @click="comingSoon(p.label)"
        >
          <span class="mi-icon"><NIcon :component="p.icon" :size="17" /></span>
          <span class="mi-text">
            <span class="mi-label">{{ p.label }}</span>
          </span>
          <NTag size="tiny" :bordered="false" round class="mi-tag">筹备中</NTag>
        </button>
      </nav>

      <template #footer>
        <NButton block type="error" secondary @click="logout">
          <template #icon><NIcon :component="LogOutOutline" /></template>
          退出登录
        </NButton>
      </template>
    </NDrawerContent>
  </NDrawer>
</template>

<style scoped>
/* ---------- 分组标签 ---------- */
.group-label {
  margin: 18px 20px 8px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 2px;
  color: #94a3b8;
  display: flex;
  align-items: center;
  gap: 4px;
}
.group-label.first {
  margin-top: 14px;
}
.group-label.soon {
  color: #b6c2d4;
}

/* ---------- 菜单项 ---------- */
.menu-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 0 12px;
}
.menu-item {
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 9px 12px;
  border: none;
  border-radius: 13px;
  background: transparent;
  color: #374151;
  font-size: 14.5px;
  font-family: inherit;
  cursor: pointer;
  text-align: left;
  transition: background 0.2s ease, box-shadow 0.2s ease, transform 0.15s ease;
}
.menu-item:hover {
  background: #eef4ff;
  transform: translateX(2px);
}
.menu-item:active {
  transform: translateX(2px) scale(0.985);
}
/* 图标容器 */
.mi-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border-radius: 10px;
  background: #e3edff;
  color: #2563eb;
  flex-shrink: 0;
  transition: background 0.2s ease, color 0.2s ease;
}
.mi-text {
  display: flex;
  flex-direction: column;
  gap: 1px;
  min-width: 0;
  flex: 1;
}
.mi-label {
  font-weight: 600;
  line-height: 1.3;
}
.mi-desc {
  font-size: 11.5px;
  color: #9aa7ba;
  line-height: 1.3;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
/* active 右侧小圆点 */
.mi-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: transparent;
  flex-shrink: 0;
  transition: background 0.2s ease;
}
.menu-item.active {
  background: linear-gradient(120deg, #2563eb, #3b82f6);
  box-shadow: 0 5px 14px rgba(37, 99, 235, 0.35);
  color: #fff;
}
.menu-item.active .mi-icon {
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
}
.menu-item.active .mi-desc {
  color: rgba(255, 255, 255, 0.75);
}
.menu-item.active .mi-dot {
  background: #fff;
}
/* hover 流光扫过 */
.mi-shine {
  position: absolute;
  top: 0;
  left: -80%;
  width: 55%;
  height: 100%;
  background: linear-gradient(105deg, transparent, rgba(120, 170, 255, 0.28) 50%, transparent);
  transform: skewX(-20deg);
  pointer-events: none;
}
.menu-item:hover .mi-shine {
  animation: mi-shine 0.8s ease;
}
@keyframes mi-shine {
  from {
    left: -80%;
  }
  to {
    left: 140%;
  }
}

/* ---------- 占位项 ---------- */
.menu-item.placeholder {
  cursor: default;
}
.menu-item.placeholder .mi-icon {
  background: #f1f4f9;
  color: #b3bfd0;
}
.menu-item.placeholder .mi-label {
  color: #a5b1c2;
}
.menu-item.placeholder:hover {
  background: #f7fafd;
}
.mi-tag {
  background: #eef2f7;
  color: #a5b1c2;
  font-size: 10px;
}
</style>
