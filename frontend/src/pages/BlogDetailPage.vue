<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  NBackTop,
  NButton,
  NPopconfirm,
  NSpin,
  NTag,
  useDialog,
  useMessage,
} from 'naive-ui'
import { deletePost, getPost, type PostDetail } from '../api/posts'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const dialog = useDialog()
const message = useMessage()
const auth = useAuthStore()

const post = ref<PostDetail | null>(null)
const loading = ref(true)

function formatDate(s: string) {
  const d = new Date(s)
  return Number.isNaN(d.getTime()) ? '' : d.toLocaleString('zh-CN')
}

async function load() {
  loading.value = true
  try {
    const { data } = await getPost(route.params.id as string)
    post.value = data
    document.title = data.title
  } catch {
    message.error('加载失败')
  } finally {
    loading.value = false
  }
}

function onEdit() {
  router.push(`/edit/${post.value!.id}`)
}

function onDelete() {
  dialog.warning({
    title: '删除博客',
    content: '确定删除这篇博客吗？删除后不可恢复。',
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await deletePost(post.value!.id)
        message.success('已删除')
        router.push('/')
      } catch {
        message.error('删除失败')
      }
    },
  })
}

onMounted(load)
</script>

<template>
  <div class="detail-page">
    <NSpin :show="loading">
      <article v-if="post" class="article">
        <div class="meta">
          <NTag size="small" :bordered="false" :type="post.type === 'diary' ? 'info' : 'primary'">
            {{ post.type === 'diary' ? '日记' : '博客' }}
          </NTag>
          <span class="category">{{ post.category }}</span>
          <span class="date">{{ formatDate(post.created_at) }}</span>
          <span v-if="auth.isLogin" class="actions">
            <NButton size="tiny" quaternary @click="onEdit">编辑</NButton>
            <NPopconfirm @positive-click="onDelete">
              <template #trigger>
                <NButton size="tiny" quaternary type="error">删除</NButton>
              </template>
              确定删除？
            </NPopconfirm>
          </span>
        </div>

        <h1 class="title">{{ post.title }}</h1>

        <div v-if="post.cover_image" class="cover">
          <img :src="post.cover_image" alt="cover" />
        </div>

        <div
          class="post-content"
          :style="post.font_family ? { fontFamily: post.font_family } : {}"
          v-html="post.content"
        />
      </article>
    </NSpin>

    <NBackTop :right="40" :bottom="40" />
  </div>
</template>

<style scoped>
.detail-page {
  max-width: 760px;
  margin: 0 auto;
  padding: 80px 24px 80px;
}
.meta {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #999;
  font-size: 13px;
}
.category {
  color: var(--brand);
}
.date {
  margin-left: auto;
}
.actions {
  display: inline-flex;
  gap: 4px;
}
.title {
  margin: 16px 0 20px;
  font-size: 30px;
  line-height: 1.4;
}
.cover {
  margin-bottom: 20px;
}
.cover img {
  width: 100%;
  border-radius: 12px;
}
</style>