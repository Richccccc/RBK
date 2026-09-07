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
import { CreateOutline } from '@vicons/ionicons5'
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
