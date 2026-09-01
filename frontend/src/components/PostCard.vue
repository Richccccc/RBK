<script setup lang="ts">
import { NButton, NIcon, NTag } from 'naive-ui'
import { EyeOutline } from '@vicons/ionicons5'
import type { PostItem } from '../api/posts'

defineProps<{ post: PostItem }>()
const emit = defineEmits<{ (e: 'preview'): void }>()

function formatDate(s: string) {
  const d = new Date(s)
  return Number.isNaN(d.getTime()) ? '' : d.toLocaleDateString('zh-CN')
}
</script>

<template>
  <div class="post-card">
    <div class="cover">
      <img v-if="post.cover_image" :src="post.cover_image" alt="cover" />
      <div v-else class="cover-text">{{ post.title }}</div>
    </div>
    <div class="body">
      <div class="meta">
        <NTag size="small" :bordered="false" :type="post.type === 'diary' ? 'info' : 'primary'">
          {{ post.type === 'diary' ? '日记' : '博客' }}
        </NTag>
        <span class="category">{{ post.category }}</span>
        <span class="date">{{ formatDate(post.created_at) }}</span>
      </div>
      <h3 class="title">{{ post.title }}</h3>
      <p v-if="post.summary" class="summary">{{ post.summary }}</p>
      <div class="actions">
        <NButton size="tiny" quaternary type="primary" @click.stop="emit('preview')">
          <template #icon><NIcon :component="EyeOutline" /></template>
          预览
        </NButton>
      </div>
    </div>
  </div>
</template>

<style scoped>
.post-card {
  background: #fff;
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  transition: transform 0.15s ease, box-shadow 0.15s ease;
  cursor: pointer;
}
.post-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 22px rgba(0, 0, 0, 0.1);
}
.cover {
  width: 100%;
  height: 160px;
  background: #eee;
}
.cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.cover-text {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 16px;
  background: linear-gradient(135deg, #eef0ff, #f6f6fb);
  color: #8a8a94;
  font-size: 15px;
  text-align: center;
}
.body {
  padding: 14px 16px 16px;
}
.meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #999;
}
.category {
  color: var(--brand);
}
.date {
  margin-left: auto;
}
.title {
  margin: 10px 0 6px;
  font-size: 18px;
  color: var(--ink);
}
.summary {
  margin: 0;
  font-size: 14px;
  color: #777;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.actions {
  margin-top: 10px;
}
</style>