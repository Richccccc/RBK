<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import {
  NAvatar,
  NButton,
  NEmpty,
  NIcon,
  NInput,
  NPagination,
  NPopconfirm,
  NSpin,
  useMessage,
} from 'naive-ui'
import { ChatbubblesOutline, SendOutline, TrashOutline } from '@vicons/ionicons5'
import { createMessage, deleteMessage, listMessages, type GuestMessage } from '../api/guestbook'
import { useAuthStore } from '../stores/auth'

const message = useMessage()
const auth = useAuthStore()

const items = ref<GuestMessage[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = 20
const loading = ref(false)

const name = ref('')
const content = ref('')
const submitting = ref(false)

const totalpages = computed(() => Math.max(1, Math.ceil(total.value / pageSize)))

async function fetchData() {
  loading.value = true
  try {
    const { data } = await listMessages({ page: page.value, size: pageSize })
    items.value = data.items
    total.value = data.total
  } catch {
    message.error('加载留言失败')
  } finally {
    loading.value = false
  }
}

function onPageChange(p: number) {
  page.value = p
  fetchData()
}

async function submit() {
  if (!name.value.trim() || !content.value.trim()) {
    message.warning('请填写昵称和留言内容')
    return
  }
  submitting.value = true
  try {
    await createMessage(name.value.trim(), content.value.trim())
    content.value = ''
    message.success('留言成功')
    page.value = 1
    fetchData()
  } catch {
    message.error('留言失败，请稍后再试')
  } finally {
    submitting.value = false
  }
}

async function onDelete(id: number) {
  try {
    await deleteMessage(id)
    message.success('已删除')
    fetchData()
  } catch {
    message.error('删除失败')
  }
}

function fmtDate(s: string) {
  const d = new Date(s)
  return Number.isNaN(d.getTime()) ? '' : d.toLocaleString('zh-CN')
}

const AVATAR_COLORS = ['#60a5fa', '#3b82f6', '#93c5fd', '#2563eb', '#7dd3fc', '#818cf8']
function avatarColor(name: string) {
  let h = 0
  for (const ch of name) h = (h * 31 + ch.charCodeAt(0)) & 0xffff
  return AVATAR_COLORS[h % AVATAR_COLORS.length]
}

onMounted(fetchData)
</script>

<template>
  <div class="page">
    <header class="head">
      <div>
        <h1>留言板</h1>
        <p class="sub">有什么想说的，留下一句话吧 · 共 {{ total }} 条</p>
      </div>
    </header>

    <!-- 留言表单 -->
    <div class="composer">
      <NIcon :component="ChatbubblesOutline" :size="26" class="composer-icon" />
      <div class="composer-main">
        <NInput v-model:value="name" placeholder="你的昵称" maxlength="30" style="width: 200px" />
        <NInput
          v-model:value="content"
          type="textarea"
          placeholder="写下你的留言…（≤1000 字）"
          :rows="3"
          maxlength="1000"
          show-count
        />
        <div class="composer-foot">
          <NButton type="primary" :loading="submitting" @click="submit">
            <template #icon><NIcon :component="SendOutline" /></template>
            发表留言
          </NButton>
        </div>
      </div>
    </div>

    <NSpin :show="loading">
      <div v-if="items.length" class="list">
        <div v-for="m in items" :key="m.id" class="msg">
          <NAvatar round :style="{ background: avatarColor(m.name), color: '#fff', fontWeight: 600 }">
            {{ m.name.slice(0, 1).toUpperCase() }}
          </NAvatar>
          <div class="bubble-wrap">
            <div class="bubble-head">
              <span class="name">{{ m.name }}</span>
              <span class="time">{{ fmtDate(m.created_at) }}</span>
              <NPopconfirm v-if="auth.isLogin" @positive-click="onDelete(m.id)">
                <template #trigger>
                  <NButton size="tiny" quaternary type="error" class="del">
                    <template #icon><NIcon :component="TrashOutline" /></template>
                  </NButton>
                </template>
                确定删除这条留言？
              </NPopconfirm>
            </div>
            <div class="bubble">{{ m.content }}</div>
          </div>
        </div>
      </div>
      <NEmpty v-else-if="!loading" description="还没有留言，来抢沙发" style="padding: 60px 0" />
    </NSpin>

    <div v-if="totalpages > 1" class="pager">
      <NPagination :page="page" :page-count="totalpages" @update:page="onPageChange" />
    </div>
  </div>
</template>

<style scoped>
.page {
  max-width: 880px;
  margin: 0 auto;
  padding: 28px 24px 60px;
}
.head {
  margin-bottom: 20px;
}
.head h1 {
  margin: 0 0 6px;
  font-size: 26px;
  color: var(--ink, #1f2937);
}
.sub {
  margin: 0;
  font-size: 13px;
  color: #999;
}

/* 留言表单：浅蓝玻璃卡 */
.composer {
  display: flex;
  gap: 14px;
  padding: 18px 20px;
  border-radius: 16px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(219, 234, 254, 0.5));
  border: 1px solid rgba(255, 255, 255, 0.85);
  box-shadow: 0 4px 16px rgba(96, 140, 220, 0.14);
  margin-bottom: 26px;
}
.composer-icon {
  color: #2563eb;
  margin-top: 4px;
}
.composer-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.composer-foot {
  display: flex;
  justify-content: flex-end;
}

/* 留言列表：气泡 */
.list {
  display: flex;
  flex-direction: column;
  gap: 18px;
}
.msg {
  display: flex;
  gap: 12px;
  animation: msg-in 0.4s ease backwards;
}
@keyframes msg-in {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
.bubble-wrap {
  flex: 1;
  min-width: 0;
}
.bubble-head {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
}
.name {
  font-size: 14px;
  font-weight: 600;
  color: #1e3a8a;
}
.time {
  font-size: 12px;
  color: #b3b3b3;
}
.del {
  margin-left: auto;
}
.bubble {
  position: relative;
  padding: 12px 16px;
  border-radius: 4px 14px 14px 14px;
  background: #fff;
  border: 1px solid rgba(147, 197, 253, 0.35);
  box-shadow: 0 2px 8px rgba(96, 140, 220, 0.08);
  color: #333;
  font-size: 14px;
  line-height: 1.7;
  white-space: pre-wrap;
  word-break: break-word;
}
.pager {
  display: flex;
  justify-content: center;
  margin-top: 26px;
}
</style>
