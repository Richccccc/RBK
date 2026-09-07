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
import { listPosts, postStats, type PostItem, type PostType } from '../api/posts'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

// 路由决定内容模块：/ 为博客，/diary 为日记
const filter = ref<PostType>('blog')
const keyword = ref('')
const items = ref<PostItem[]>([])
const total = ref(0)
const loading = ref(false)

const stats = ref({ all: 0, blog: 0, diary: 0, sheets: 0, messages: 0 })

const previewVisible = ref(false)
const previewId = ref<number | null>(null)

const title = computed(() => (filter.value === 'diary' ? '日记' : '博客'))

// Hero 问候与日期
const greeting = computed(() => {
  const h = new Date().getHours()
  if (h >= 5 && h < 11) return '早上好'
  if (h >= 11 && h < 18) return '下午好'
  return '晚上好'
})
const today = computed(() =>
  new Date().toLocaleDateString('zh-CN', { month: 'long', day: 'numeric', weekday: 'long' }),
)

// 四大模块入口
const modules = computed(() => [
  { key: 'home', label: '博客', desc: '技术分享与随笔', icon: HomeOutline, count: stats.value.blog, path: '/' },
  { key: 'diary', label: '日记', desc: '记录日常点滴', icon: BookOutline, count: stats.value.diary, path: '/diary' },
  { key: 'sheets', label: '表格参考', desc: 'Excel/CSV 在线预览', icon: GridOutline, count: stats.value.sheets, path: '/sheets' },
  { key: 'guestbook', label: '留言板', desc: '留下你想说的话', icon: ChatbubblesOutline, count: stats.value.messages, path: '/guestbook' },
])

// 根据路由切换模块（/ 博客，/diary 日记）
watch(
  () => route.path,
  () => {
    filter.value = route.path === '/diary' ? 'diary' : 'blog'
    fetchData()
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

// Hero 统计（单次请求拿全部计数）
async function fetchStats() {
  try {
    const { data } = await postStats()
    stats.value = {
      all: data.all,
      blog: data.blog,
      diary: data.diary,
      sheets: data.sheets ?? 0,
      messages: data.messages ?? 0,
    }
  } catch {
    /* 统计失败不阻塞页面 */
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
  fetchStats()
})
</script>

<template>
  <div class="page">
    <!-- Hero 横幅 -->
    <header class="hero">
      <div class="hero-shine" aria-hidden="true"></div>
      <div class="hero-blob hb1" aria-hidden="true"></div>
      <div class="hero-blob hb2" aria-hidden="true"></div>
      <div class="hero-main">
        <div class="hero-text">
          <h1>{{ greeting }}，{{ auth.user?.username || '朋友' }}</h1>
          <p class="date">{{ today }} · 这里是你的小天地</p>
        </div>
        <div class="hero-stats">
          <div class="stat">
            <span class="num">{{ stats.all }}</span>
            <span class="label">文章</span>
          </div>
          <div class="stat">
            <span class="num">{{ stats.sheets }}</span>
            <span class="label">表格</span>
          </div>
          <div class="stat">
            <span class="num">{{ stats.messages }}</span>
            <span class="label">留言</span>
          </div>
        </div>
      </div>
    </header>

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
        <span class="m-count">{{ m.count }}</span>
      </button>
    </nav>

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
        <NButton type="primary" @click="router.push(auth.isLogin ? '/new' : '/login?redirect=/new')">
          开始写作
        </NButton>
      </div>
    </NSpin>

    <BlogPreview v-model:show="previewVisible" :post-id="previewId" />
  </div>
</template>

<style scoped>
.page {
  max-width: 1320px;
  margin: 0 auto;
  padding: 28px 24px 60px;
}

/* ---------- Hero 横幅（浅蓝玻璃 + 流动彩光） ---------- */
.hero {
  position: relative;
  overflow: hidden;
  border-radius: 20px;
  padding: 26px 30px;
  /* 白-蓝为主，穿插淡紫/淡金过渡色，渐变缓慢循环流动 */
  background: linear-gradient(
    120deg,
    rgba(255, 255, 255, 0.75),
    rgba(219, 234, 254, 0.62) 22%,
    rgba(147, 197, 253, 0.52) 42%,
    rgba(167, 180, 252, 0.45) 60%,
    rgba(253, 230, 190, 0.4) 78%,
    rgba(186, 214, 255, 0.55) 92%,
    rgba(255, 255, 255, 0.7)
  );
  background-size: 320% 320%;
  animation: hero-flow 16s ease-in-out infinite;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.75);
  color: #1e3a8a;
  box-shadow: 0 10px 30px rgba(96, 140, 220, 0.18);
}
@keyframes hero-flow {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}
.hero-shine {
  position: absolute;
  top: 0;
  left: -70%;
  width: 45%;
  height: 100%;
  background: linear-gradient(105deg, transparent, rgba(255, 255, 255, 0.2) 50%, transparent);
  transform: skewX(-18deg);
  animation: hero-shine 3.2s ease infinite;
}
@keyframes hero-shine {
  0% {
    left: -70%;
  }
  55%,
  100% {
    left: 135%;
  }
}
.hero-blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
  opacity: 0.4;
  pointer-events: none;
}
.hb1 {
  width: 260px;
  height: 260px;
  background: #bfdbfe;
  top: -110px;
  right: -60px;
}
.hb2 {
  width: 200px;
  height: 200px;
  background: #93c5fd;
  bottom: -100px;
  left: 30%;
}
.hero-main {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 18px;
  flex-wrap: wrap;
}
.hero-text h1 {
  margin: 0 0 6px;
  font-size: 26px;
  letter-spacing: 1px;
}
.date {
  margin: 0;
  font-size: 13px;
  color: rgba(30, 58, 138, 0.62);
  letter-spacing: 1px;
}
.hero-stats {
  display: flex;
  gap: 12px;
}
.stat {
  min-width: 74px;
  padding: 10px 14px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(6px);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}
.stat .num {
  font-size: 22px;
  font-weight: 700;
  line-height: 1.2;
  color: #2563eb;
}
.stat .label {
  font-size: 12px;
  color: rgba(30, 58, 138, 0.68);
}

.filters {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 22px 0 24px;
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
  margin-top: 18px;
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
.m-count {
  position: absolute;
  top: 14px;
  right: 16px;
  min-width: 26px;
  padding: 2px 8px;
  border-radius: 999px;
  background: rgba(37, 99, 235, 0.12);
  color: #2563eb;
  font-size: 12px;
  font-weight: 600;
  text-align: center;
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
  .hero {
    padding: 20px 18px;
  }
  .hero-text h1 {
    font-size: 21px;
  }
  .hero-stats {
    width: 100%;
  }
  .stat {
    flex: 1;
  }
}
</style>
