<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { NButton, NModal, NSkeleton, NTag } from 'naive-ui'
import { getPost, type PostDetail } from '../api/posts'

const props = defineProps<{ show: boolean; postId: number | null }>()
const emit = defineEmits<{ (e: 'update:show', v: boolean): void }>()

const router = useRouter()
const post = ref<PostDetail | null>(null)
const loading = ref(false)

// 首选用封图，否则取正文第一张图片
function firstImage(p: PostDetail): string {
  if (p.cover_image) return p.cover_image
  const m = p.content.match(/<img[^>]+src=["']([^"']+)["']/i)
  return m ? m[1] : ''
}

function stripHtml(html: string): string {
  return html
    .replace(/<[^>]+>/g, ' ')
    .replace(/&nbsp;/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
}

const cover = computed(() => (post.value ? firstImage(post.value) : ''))
const textPreview = computed(() => {
  if (!post.value) return ''
  return post.value.summary || stripHtml(post.value.content).slice(0, 160)
})

watch(
  () => [props.show, props.postId] as const,
  async ([show, id]) => {
    if (!show || id == null) return
    loading.value = true
    try {
      const { data } = await getPost(id)
      post.value = data
    } catch {
      post.value = null
    } finally {
      loading.value = false
    }
  },
)

function onClose() {
  emit('update:show', false)
}

function openDetail() {
  if (post.value) {
    emit('update:show', false)
    router.push(`/post/${post.value.id}`)
  }
}
</script>

<template>
  <NModal
    :show="show"
    :auto-focus="false"
    :block-scroll="true"
    @update:show="(v: boolean) => emit('update:show', v)"
  >
    <div class="preview">
      <div class="win">
        <template v-if="loading">
          <div class="text-mode"><NSkeleton text :repeat="3" /></div>
        </template>
        <template v-else-if="post">
          <img v-if="cover" :src="cover" class="cover-img" alt="封面" />
          <div v-else class="text-mode">
            <h2 class="text-title">{{ post.title }}</h2>
            <p class="text-body">{{ textPreview }}</p>
          </div>
          <div v-if="cover" class="scrim">
            <NTag size="tiny" :bordered="false" type="primary">
              {{ post.type === 'diary' ? '日记' : '博客' }}
            </NTag>
            <h2 class="scrim-title">{{ post.title }}</h2>
          </div>
        </template>
        <template v-else>
          <div class="text-mode">加载失败</div>
        </template>
      </div>

      <div v-if="post && !loading" class="actions">
        <NButton size="small" @click="onClose">关闭</NButton>
        <NButton size="small" type="primary" @click="openDetail">查看全文</NButton>
      </div>
    </div>
  </NModal>
</template>

<style scoped>
.preview {
  max-width: 92vw;
}
.win {
  position: relative;
  width: 640px;
  max-width: 92vw;
  height: 400px;
  border-radius: 14px;
  overflow: hidden;
  background: #1e1e28;
}
.cover-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.text-mode {
  width: 100%;
  height: 100%;
  padding: 28px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  justify-content: center;
  background: linear-gradient(135deg, #eef0ff, #fdfdff);
  color: var(--ink);
}
.text-title {
  margin: 0 0 12px;
  font-size: 26px;
}
.text-body {
  margin: 0;
  color: #666;
  line-height: 1.8;
  font-size: 15px;
  max-height: 220px;
  overflow: hidden;
}
.scrim {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  padding: 40px 24px 20px;
  box-sizing: border-box;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.65), transparent);
}
.scrim-title {
  margin: 8px 0 0;
  color: #fff;
  font-size: 24px;
}
.actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 12px;
}
</style>