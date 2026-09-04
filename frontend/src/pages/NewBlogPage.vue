<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  NButton,
  NInput,
  NRadioButton,
  NRadioGroup,
  NSelect,
  NUpload,
  useMessage,
} from 'naive-ui'
import BlogEditor from '../components/BlogEditor.vue'
import { createPost, getPost, updatePost, uploadImage, uploadWord, type PostType } from '../api/posts'
import { FONT_OPTIONS } from '../utils/fonts'
import { compressImageFile } from '../utils/image'

const route = useRoute()
const router = useRouter()
const message = useMessage()

// 文章变更后清空首页列表缓存，避免回到首页时短暂显示旧数据
function clearListCache() {
  Object.keys(sessionStorage)
    .filter((k) => k.startsWith('posts-cache:'))
    .forEach((k) => sessionStorage.removeItem(k))
}

const isEdit = computed(() => !!route.params.id)

const title = ref('')
const type = ref<PostType>('blog')
const category = ref('')
const summary = ref('')
const cover = ref('')
const fontFamily = ref('')
const content = ref('')

const loading = ref(false)
const saving = ref(false)
const importingWord = ref(false)

onMounted(async () => {
  if (isEdit.value) {
    loading.value = true
    try {
      const { data } = await getPost(route.params.id as string)
      title.value = data.title
      type.value = data.type
      category.value = data.category
      summary.value = data.summary
      cover.value = data.cover_image
      fontFamily.value = data.font_family
      content.value = data.content
    } catch {
      message.error('加载失败')
    } finally {
      loading.value = false
    }
  }
})

// Naive UI 的 NUpload custom-request 传入的是 UploadFileInfo，真正的 File 在 options.file.file
interface NUploadRequest {
  file: {
    file: File | null
    name?: string
  }
}

function extractError(e: any, fallback: string): string {
  const detail = e?.response?.data?.detail
  if (Array.isArray(detail)) {
    return detail.map((d: any) => d?.msg || JSON.stringify(d)).join('；')
  }
  if (typeof detail === 'string' && detail) return detail
  return fallback
}

async function onPickCover(options: NUploadRequest) {
  const file = options?.file?.file
  if (!file) {
    message.error('未获取到文件')
    return
  }
  try {
    const compressed = await compressImageFile(file)
    cover.value = await uploadImage(compressed)
    message.success('封面已上传')
  } catch (e: any) {
    message.error(extractError(e, '封面上传失败'))
  }
}

async function importWord(options: NUploadRequest) {
  const file = options?.file?.file
  if (!file) {
    message.error('未获取到文件')
    return
  }
  importingWord.value = true
  try {
    const html = await uploadWord(file)
    content.value = html
    if (!title.value) {
      const name = options.file.name || file.name
      title.value = name.replace(/\.docx?$/i, '')
    }
    message.success('Word 内容已导入编辑器')
  } catch (e: any) {
    message.error(extractError(e, 'Word 导入失败'))
  } finally {
    importingWord.value = false
  }
}

async function save() {
  if (!title.value.trim()) {
    message.warning('请填写标题')
    return
  }
  if (!content.value || content.value === '<p></p>') {
    message.warning('请填写正文内容')
    return
  }
  saving.value = true
  const payload = {
    title: title.value.trim(),
    content: content.value,
    summary: summary.value,
    type: type.value,
    category: category.value || '未分类',
    font_family: fontFamily.value,
    cover_image: cover.value,
  }
  try {
    if (isEdit.value) {
      await updatePost(route.params.id as string, payload)
      clearListCache()
      message.success('已更新')
      router.push(`/post/${route.params.id}`)
    } else {
      const { data } = await createPost(payload)
      clearListCache()
      message.success('发布成功')
      router.push(`/post/${data.id}`)
    }
  } catch (e: any) {
    message.error(e?.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="editor-page">
    <header class="head">
      <div class="head-row">
        <NInput v-model:value="title" size="large" placeholder="输入标题…" class="title-input" />
        <div class="head-actions">
          <NUpload accept=".docx" :show-file-list="false" :custom-request="importWord">
            <NButton :loading="importingWord">导入 Word</NButton>
          </NUpload>
          <NButton type="primary" :loading="saving" @click="save">
            {{ isEdit ? '保存' : '发布' }}
          </NButton>
        </div>
      </div>

      <div class="options">
        <NRadioGroup v-model:value="type">
          <NRadioButton value="blog">博客</NRadioButton>
          <NRadioButton value="diary">日记</NRadioButton>
        </NRadioGroup>
        <NInput v-model:value="category" placeholder="分类（如：技术/生活）" style="width: 180px" />
        <NSelect
          v-model:value="fontFamily"
          :options="FONT_OPTIONS"
          placeholder="文章默认字体"
          style="width: 160px"
          clearable
        />
        <NUpload accept="image/*" :show-file-list="false" :custom-request="onPickCover">
          <NButton size="small">{{ cover ? '重选封面' : '上传封面' }}</NButton>
        </NUpload>
        <NInput v-model:value="summary" placeholder="摘要（可选）" style="flex: 1; min-width: 200px" />
      </div>
    </header>

    <BlogEditor v-model="content" />

    <div class="foot">
      <NButton :loading="saving" type="primary" @click="save">{{ isEdit ? '保存' : '发布' }}</NButton>
    </div>
  </div>
</template>

<style scoped>
.editor-page {
  max-width: 1240px;
  margin: 0 auto;
  padding: 28px 24px 60px;
}
.head {
  margin-bottom: 16px;
}
.head-row {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 12px;
}
.title-input {
  flex: 1;
}
.head-actions {
  display: flex;
  gap: 8px;
}
.options {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}
.foot {
  margin-top: 16px;
  text-align: right;
}
</style>