<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  NButton,
  NIcon,
  NInput,
  NSpin,
  NTag,
} from 'naive-ui'
import {
  ChatbubblesOutline,
  CreateOutline,
  GridOutline,
  BookOutline,
  HomeOutline,
} from '@vicons/ionicons5'
import PostCard from '../components/PostCard.vue'
import BlogPreview from '../components/BlogPreview.vue'
import SheetsPanel from '../components/SheetsPanel.vue'
import GuestbookPanel from '../components/GuestbookPanel.vue'
import { listPosts, type PostItem, type PostType } from '../api/posts'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

// 路由决定内容模块：/ 为博客，/diary 为日记，/templates 模板，/guestbook 留言板（均在主页内切换）
const isPostModule = computed(() => route.path === '/' || route.path === '/diary')
const filter = ref<PostType>('blog')
const keyword = ref('')
const items = ref<PostItem[]>([])
const total = ref(0)
const loading = ref(false)

const previewVisible = ref(false)
const previewId = ref<number | null>(null)

const title = computed(() => (filter.value === 'diary' ? '日记' : '博客'))

// 四大模块入口（点击在主页内切换内容，不做页面跳转）
const modules = computed(() => [
  { key: 'home', label: '博客', desc: '技术分享与随笔', icon: HomeOutline, path: '/' },
  { key: 'diary', label: '日记', desc: '记录日常点滴', icon: BookOutline, path: '/diary' },
  { key: 'templates', label: '模板', desc: 'Excel/CSV 在线预览', icon: GridOutline, path: '/templates' },
  { key: 'guestbook', label: '留言板', desc: '留下你想说的话', icon: ChatbubblesOutline, path: '/guestbook' },
])

// 根据路由切换模块
watch(
  () => route.path,
  () => {
    filter.value = route.path === '/diary' ? 'diary' : 'blog'
    if (isPostModule.value) fetchData()
  },
)

// 列表加载：先用 sessionStorage 缓存秒显，再后台静默刷新（API 链路慢，缓存显著改善二次打开体验）
function listCacheKey() {
  return `posts-cache:${filter.value}:${keyword.value || ''}`
}

async function fetchData() {
  const raw = sessionStorage.getItem(listCacheKey())
  if (raw) {
    try {
      const c = JSON.parse(raw) as { items: PostItem[]; total: number }
      items.value = c.items
      total.value = c.total
    } catch {
      /* 缓存损坏则忽略 */
    }
  }
  if (!raw) loading.value = true
  try {
    const { data } = await listPosts({
      type: filter.value,
      q: keyword.value || undefined,
      page: 1,
      size: 50,
    })
    items.value = data.items
    total.value = data.total
    sessionStorage.setItem(listCacheKey(), JSON.stringify({ items: data.items, total: data.total }))
  } finally {
    loading.value = false
  }
}

function onSearch() {
  fetchData()
}

function goDetail(id: number) {
  router.push(`/post/${id}`)
}

function openPreview(id: number) {
  previewId.value = id
  previewVisible.value = true
}

onMounted(() => {
  fetchData()
})
</script>

<template>
  <div class="page">
    <!-- 四大模块入口 -->
    <nav class="modules">
      <button
        v-for="(m, i) in modules"
        :key="m.key"
        class="module-card"
        :class="{ active: route.path === m.path }"
        :style="{ animationDelay: i * 70 + 'ms' }"
        @click="router.push(m.path)"
      >
        <span class="m-shine" aria-hidden="true"></span>
        <NIcon :component="m.icon" :size="26" class="m-icon" />
        <span class="m-label">{{ m.label }}</span>
        <span class="m-desc">{{ m.desc }}</span>
      </button>
    </nav>

    <!-- 内容区：模块内切换（带淡入过渡） -->
    <Transition name="panel" mode="out-in">
      <!-- 博客 / 日记列表 -->
      <div v-if="isPostModule" :key="route.path">
        <div class="filters">
          <NTag size="small" :bordered="false" type="primary">{{ title }}</NTag>
          <NInput
            v-model:value="keyword"
            placeholder="搜索标题或摘要"
            clearable
            style="width: 220px"
            @keyup.enter="onSearch"
            @clear="onSearch"
          />
          <NButton size="small" @click="onSearch">搜索</NButton>
          <NButton size="small" type="primary" @click="router.push('/new')">
            <template #icon><NIcon :component="CreateOutline" /></template>
            写一篇
          </NButton>
          <span class="count">{{ title }}共 {{ total }} 篇</span>
        </div>

        <NSpin :show="loading">
          <div v-if="items.length" class="grid">
            <PostCard
              v-for="(p, i) in items"
              :key="p.id"
              :post="p"
              :style="{ animationDelay: Math.min(i * 60, 600) + 'ms' }"
              @click="goDetail(p.id)"
              @preview="openPreview(p.id)"
            />
          </div>
          <div v-else-if="!loading" class="empty">
            <NIcon :component="CreateOutline" :size="46" class="empty-icon" />
            <p class="empty-text">还没有内容，写下第一篇吧</p>
            <NButton type="primary" @click="router.push('/new')">
              开始写作
            </NButton>
          </div>
        </NSpin>

        <BlogPreview v-model:show="previewVisible" :post-id="previewId" />
      </div>

      <!-- 模板 -->
      <SheetsPanel v-else-if="route.path === '/templates'" key="templates" />

      <!-- 留言板 -->
      <GuestbookPanel v-else key="guestbook" />
    </Transition>
  </div>
</template>

<style scoped>
.page {
  max-width: 1320px;
  margin: 0 auto;
  padding: 28px 24px 60px;
}

/* 内容区切换过渡 */
.panel-enter-active,
.panel-leave-active {
  transition: opacity 0.22s ease, transform 0.22s ease;
}
.panel-enter-from {
  opacity: 0;
  transform: translateY(8px);
}
.panel-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

.filters {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 4px 0 24px;
  flex-wrap: wrap;
}
.count {
  margin-left: auto;
  font-size: 13px;
  color: #999;
}

/* ---------- 四大模块入口卡片 ---------- */
.modules {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}
.module-card {
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 4px;
  padding: 18px 20px;
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.8);
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.85), rgba(219, 234, 254, 0.55));
  backdrop-filter: blur(8px);
  cursor: pointer;
  text-align: left;
  font-family: inherit;
  box-shadow: 0 4px 16px rgba(96, 140, 220, 0.12);
  transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
  animation: module-in 0.5s ease backwards;
}
@keyframes module-in {
  from {
    opacity: 0;
    transform: translateY(14px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
.module-card:hover {
  transform: translateY(-4px);
  border-color: rgba(59, 130, 246, 0.55);
  box-shadow: 0 10px 26px rgba(59, 130, 246, 0.25);
}
.module-card.active {
  border-color: rgba(59, 130, 246, 0.65);
  background: linear-gradient(135deg, rgba(219, 234, 254, 0.9), rgba(147, 197, 253, 0.5));
}
/* hover 流光扫过 */
.m-shine {
  position: absolute;
  top: 0;
  left: -80%;
  width: 55%;
  height: 100%;
  background: linear-gradient(105deg, transparent, rgba(255, 255, 255, 0.55) 50%, transparent);
  transform: skewX(-20deg);
  transition: none;
  pointer-events: none;
}
.module-card:hover .m-shine {
  animation: m-shine 0.9s ease;
}
@keyframes m-shine {
  from {
    left: -80%;
  }
  to {
    left: 140%;
  }
}
.m-icon {
  color: #2563eb;
  margin-bottom: 4px;
}
.m-label {
  font-size: 16px;
  font-weight: 600;
  color: #1e3a8a;
}
.m-desc {
  font-size: 12px;
  color: rgba(30, 58, 138, 0.6);
}

@media (max-width: 900px) {
  .modules {
    grid-template-columns: repeat(2, 1fr);
  }
}
@media (max-width: 480px) {
  .modules {
    grid-template-columns: 1fr;
  }
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 18px;
}

/* ---------- 空状态 ---------- */
.empty {
  padding: 70px 0 90px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}
.empty-icon {
  color: #9ec3f7;
}
.empty-text {
  margin: 0 0 4px;
  color: #8a8a94;
  font-size: 15px;
}

@media (max-width: 640px) {
  .page {
    padding: 20px 14px 50px;
  }
}
</style>
