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
  <div class="post-card" :class="{ pinned: post.pinned }">
    <div v-if="post.pinned" class="pin-badge">
      <svg viewBox="0 0 24 24" width="11" height="11" fill="currentColor">
        <path d="M16 3a1 1 0 0 1 .7 1.7l-.9.9 2.6 2.6.9-.9A1 1 0 0 1 21 8l-4 4 .6 2.4a1 1 0 0 1-1.7 1L12 12l-5.3 5.3a1 1 0 0 1-1.4-1.4L10.6 11 7.6 8a1 1 0 0 1 1-1.7L11 7l4-4a1 1 0 0 1 1-.1z" />
      </svg>
      置顶
    </div>
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
  position: relative;
  background: #fff;
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  transition: transform 0.15s ease, box-shadow 0.15s ease;
  cursor: pointer;
  animation: card-in 0.45s ease backwards;
}
@keyframes card-in {
  from {
    opacity: 0;
    transform: translateY(14px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
.post-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 22px rgba(59, 130, 246, 0.18);
}
/* 置顶角标与边框高亮 */
.post-card.pinned {
  border: 1px solid rgba(59, 130, 246, 0.45);
}
.pin-badge {
  position: absolute;
  top: 10px;
  left: 10px;
  z-index: 2;
  display: inline-flex;
  align-items: center;
  gap: 3px;
  padding: 3px 9px;
  border-radius: 999px;
  background: linear-gradient(120deg, #1d4ed8, #3b82f6);
  color: #fff;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 1px;
  box-shadow: 0 3px 10px rgba(29, 78, 216, 0.35);
}
/* hover 顶部流光 */
.post-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  z-index: 1;
  background: linear-gradient(90deg, #1d4ed8, #60a5fa, #1d4ed8);
  transform: translateX(-100%);
  transition: transform 0.5s ease;
}
.post-card:hover::before {
  transform: translateX(0);
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
  background: linear-gradient(135deg, #eaf2ff, #f5faff);
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