<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NButton, NEmpty, NInput, NRadioButton, NRadioGroup, NSpin } from 'naive-ui'
import PostCard from '../components/PostCard.vue'
import BlogPreview from '../components/BlogPreview.vue'
import { listPosts, type PostItem, type PostType } from '../api/posts'

const route = useRoute()
const router = useRouter()

const filter = ref<'all' | PostType>('all')
const keyword = ref('')
const items = ref<PostItem[]>([])
const total = ref(0)
const loading = ref(false)

const previewVisible = ref(false)
const previewId = ref<number | null>(null)

const title = computed(() => (route.path === '/diary' ? '日记' : '博客'))

// 根据路由初始化过滤（/diary 默认只看日记）
watch(
  () => route.path,
  () => {
    filter.value = route.path === '/diary' ? 'diary' : 'all'
    fetchData()
  },
)

async function fetchData() {
  loading.value = true
  try {
    const { data } = await listPosts({
      type: filter.value === 'all' ? undefined : filter.value,
      q: keyword.value || undefined,
      page: 1,
      size: 50,
    })
    items.value = data.items
    total.value = data.total
  } finally {
    loading.value = false
  }
}

function onFilterChange() {
  fetchData()
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

onMounted(fetchData)
</script>

<template>
  <div class="page">
    <header class="header">
      <h1>{{ title }}</h1>
      <p class="sub">{{ total }} 篇</p>
    </header>

    <div class="filters">
      <NRadioGroup v-model:value="filter" @update:value="onFilterChange">
        <NRadioButton value="all">全部</NRadioButton>
        <NRadioButton value="blog">博客</NRadioButton>
        <NRadioButton value="diary">日记</NRadioButton>
      </NRadioGroup>
      <NInput
        v-model:value="keyword"
        placeholder="搜索标题或摘要"
        clearable
        style="width: 220px"
        @keyup.enter="onSearch"
        @clear="onSearch"
      />
      <NButton size="small" @click="onSearch">搜索</NButton>
    </div>

    <NSpin :show="loading">
      <div v-if="items.length" class="grid">
        <PostCard
          v-for="p in items"
          :key="p.id"
          :post="p"
          @click="goDetail(p.id)"
          @preview="openPreview(p.id)"
        />
      </div>
      <NEmpty v-else-if="!loading" description="还没有内容，去写一篇吧" />
    </NSpin>

    <BlogPreview v-model:show="previewVisible" :post-id="previewId" />
  </div>
</template>

<style scoped>
.page {
  max-width: 1080px;
  margin: 0 auto;
  padding: 80px 24px 60px;
}
.header h1 {
  margin: 0;
  font-size: 28px;
}
.sub {
  color: #999;
  font-size: 13px;
}
.filters {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 20px 0 24px;
  flex-wrap: wrap;
}
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 18px;
}
</style>