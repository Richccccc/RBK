<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import {
  NButton,
  NCard,
  NDataTable,
  NDrawer,
  NDrawerContent,
  NEmpty,
  NIcon,
  NInput,
  NModal,
  NPopconfirm,
  NSpin,
  NTabPane,
  NTabs,
  NTag,
  NUpload,
  useMessage,
  type UploadFileInfo,
} from 'naive-ui'
import { CloudDownloadOutline, DocumentOutline, TrashOutline } from '@vicons/ionicons5'
import {
  deleteSheet,
  getSheet,
  listSheets,
  sheetDownloadUrl,
  uploadSheet,
  type SheetDetail,
  type SheetMeta,
} from '../api/sheets'
import { useAuthStore } from '../stores/auth'

const message = useMessage()
const auth = useAuthStore()

const items = ref<SheetMeta[]>([])
const total = ref(0)
const loading = ref(false)
const keyword = ref('')

// 上传弹层（支持多选，逐个上传）
const uploadVisible = ref(false)
const uploading = ref(false)
const uploadFiles = ref<File[]>([])
const formName = ref('')
const formDesc = ref('')

// 预览抽屉
const previewVisible = ref(false)
const previewLoading = ref(false)
const detail = ref<SheetDetail | null>(null)
const activeTab = ref('')

// 预览表格列（每个 sheet 动态生成）；横向滚动需要显式 scroll-x（列数 × 列宽）
const previewColumns = computed(() => {
  const t = currentTable.value
  if (!t) return []
  return t.headers.map((h, i) => ({
    title: h || `列${i + 1}`,
    key: `c${i}`,
    width: 170,
    ellipsis: { tooltip: true },
  }))
})

const previewScrollX = computed(() =>
  Math.max(720, (currentTable.value?.headers.length || 0) * 170 + 40),
)

const previewData = computed(() => {
  const t = currentTable.value
  if (!t) return []
  return t.rows.map((r, idx) => {
    const row: Record<string, string> = { __idx: String(idx) }
    r.forEach((c, i) => (row[`c${i}`] = c))
    return row
  })
})

const currentTable = computed(
  () => detail.value?.tables.find((t) => t.name === activeTab.value) ?? detail.value?.tables[0] ?? null,
)

async function fetchData() {
  loading.value = true
  try {
    const { data } = await listSheets({ q: keyword.value || undefined, page: 1, size: 100 })
    items.value = data.items
    total.value = data.total
  } catch {
    message.error('加载模板列表失败')
  } finally {
    loading.value = false
  }
}

function onSearch() {
  fetchData()
}

function openUpload() {
  if (!auth.isLogin) {
    message.warning('请先登录')
    return
  }
  uploadFiles.value = []
  formName.value = ''
  formDesc.value = ''
  uploadVisible.value = true
}

function onFilesChange(info: { fileList: UploadFileInfo[] }) {
  const files: File[] = []
  let bad = false
  for (const fi of info.fileList) {
    const f = fi.file
    if (!f) continue
    if (/\.(xlsx|csv)$/i.test(f.name)) files.push(f)
    else bad = true
  }
  uploadFiles.value = files
  if (bad) message.warning('已忽略非 xlsx/csv 文件')
  // 单个文件时默认名称取文件名；多选时各用各的文件名
  formName.value = files.length === 1 ? files[0].name.replace(/\.(xlsx|csv)$/i, '') : ''
}

async function submitUpload() {
  if (!uploadFiles.value.length) {
    message.warning('请选择 xlsx 或 csv 文件')
    return
  }
  uploading.value = true
  let ok = 0
  let fail = 0
  for (const f of uploadFiles.value) {
    // 单文件用表单里的名称（可编辑），多选时各用各的文件名，备注为公共值
    const name = uploadFiles.value.length === 1 ? formName.value.trim() : ''
    try {
      await uploadSheet(f, name, formDesc.value.trim())
      ok++
    } catch {
      fail++
    }
  }
  uploading.value = false
  if (ok) {
    message.success(`成功上传 ${ok} 个模板${fail ? `，${fail} 个失败` : ''}`)
    uploadVisible.value = false
    fetchData()
  } else {
    message.error('全部上传失败')
  }
}

async function openPreview(id: number) {
  previewVisible.value = true
  previewLoading.value = true
  detail.value = null
  try {
    const { data } = await getSheet(id)
    detail.value = data
    activeTab.value = data.tables[0]?.name ?? ''
  } catch {
    message.error('加载表格数据失败')
  } finally {
    previewLoading.value = false
  }
}

async function onDelete(id: number) {
  try {
    await deleteSheet(id)
    message.success('已删除')
    fetchData()
  } catch {
    message.error('删除失败')
  }
}

function fmtDate(s: string) {
  const d = new Date(s)
  return Number.isNaN(d.getTime()) ? '' : d.toLocaleDateString('zh-CN')
}

onMounted(fetchData)
</script>

<template>
  <div class="panel">
    <div class="toolbar">
      <span class="hint">上传 Excel/CSV，网页直接预览，随时下载原文件 · 共 {{ total }} 个</span>
      <div class="toolbar-actions">
        <NInput
          v-model:value="keyword"
          placeholder="搜索名称或备注"
          clearable
          style="width: 200px"
          @keyup.enter="onSearch"
          @clear="onSearch"
        />
        <NButton type="primary" @click="openUpload">上传模板</NButton>
      </div>
    </div>

    <NSpin :show="loading">
      <div v-if="items.length" class="grid">
        <NCard v-for="s in items" :key="s.id" class="sheet-card" @click="openPreview(s.id)">
          <div class="s-head">
            <NIcon :component="DocumentOutline" :size="24" class="s-icon" />
            <div class="s-title">
              <h3>{{ s.name }}</h3>
              <p v-if="s.description" class="s-desc">{{ s.description }}</p>
            </div>
          </div>
          <div class="s-meta">
            <NTag size="small" :bordered="false">{{ s.sheet_count }} 个工作表</NTag>
            <NTag size="small" :bordered="false" type="primary">{{ s.rows_count }} 行</NTag>
            <NTag v-if="s.cols_count" size="small" :bordered="false" type="info">
              {{ s.cols_count }} 列
            </NTag>
            <span class="s-file">{{ s.file_name }}</span>
            <span class="s-date">{{ fmtDate(s.created_at) }}</span>
          </div>
          <div class="s-actions" @click.stop>
            <NButton size="tiny" quaternary type="primary" @click="openPreview(s.id)">预览</NButton>
            <NButton
              size="tiny"
              quaternary
              tag="a"
              :href="sheetDownloadUrl(s.id)"
              :download="s.file_name"
            >
              <template #icon><NIcon :component="CloudDownloadOutline" /></template>
              下载
            </NButton>
            <NPopconfirm v-if="auth.isLogin" @positive-click="onDelete(s.id)">
              <template #trigger>
                <NButton size="tiny" quaternary type="error">
                  <template #icon><NIcon :component="TrashOutline" /></template>
                  删除
                </NButton>
              </template>
              确定删除该模板？
            </NPopconfirm>
          </div>
        </NCard>
      </div>
      <div v-else-if="!loading" class="empty">
        <p class="empty-text">还没有模板，上传一个 xlsx 或 csv 吧</p>
        <NButton type="primary" @click="openUpload">上传模板</NButton>
      </div>
    </NSpin>

    <!-- 上传弹层 -->
    <NModal v-model:show="uploadVisible" preset="card" title="上传模板" style="width: 460px">
      <div class="upload-form">
        <NUpload
          accept=".xlsx,.csv"
          multiple
          :max="10"
          :default-upload="false"
          :show-file-list="true"
          @change="onFilesChange"
        >
          <NButton>选择文件（可多选，.xlsx / .csv，单个 ≤8MB）</NButton>
        </NUpload>
        <NInput
          v-model:value="formName"
          placeholder="模板名称（默认取文件名）"
          :disabled="uploadFiles.length > 1"
        />
        <NInput v-model:value="formDesc" type="textarea" placeholder="备注（多选时应用到所有文件）" :rows="2" />
        <NButton type="primary" block :loading="uploading" @click="submitUpload">
          {{ uploadFiles.length > 1 ? `上传并解析（${uploadFiles.length} 个）` : '上传并解析' }}
        </NButton>
      </div>
    </NModal>

    <!-- 预览抽屉 -->
    <NDrawer v-model:show="previewVisible" :width="860" placement="right">
      <NDrawerContent :title="detail?.name || '模板预览'" closable>
        <div v-if="detail" class="preview">
          <div class="preview-bar">
            <NTag size="small" :bordered="false" type="primary">
              当前表 {{ currentTable?.rows.length || 0 }} 行 × {{ currentTable?.headers.length || 0 }} 列
            </NTag>
            <NButton
              size="small"
              tag="a"
              :href="sheetDownloadUrl(detail.id)"
              :download="detail.file_name"
            >
              <template #icon><NIcon :component="CloudDownloadOutline" /></template>
              下载 {{ detail.file_name }}
            </NButton>
          </div>

          <NTabs v-model:value="activeTab" type="line" size="small">
            <NTabPane
              v-for="t in detail.tables"
              :key="t.name"
              :name="t.name"
            >
              <template #tab>{{ t.name }}</template>
              <NDataTable
                :columns="previewColumns"
                :data="previewData"
                :row-key="(r: Record<string, string>) => r.__idx"
                :max-height="560"
                :scroll-x="previewScrollX"
                virtual-scroll
                size="small"
                class="preview-table"
              />
            </NTabPane>
          </NTabs>
        </div>
        <NEmpty v-else-if="!previewLoading" description="暂无数据" />
      </NDrawerContent>
    </NDrawer>
  </div>
</template>

<style scoped>
/* 预览表格：加粗并常显 naive-ui 原生横向滚动条（默认 3px 细条几乎看不见） */
.preview-table :deep(.n-scrollbar-rail--horizontal) {
  height: 12px;
  opacity: 1;
}
.preview-table :deep(.n-scrollbar-rail--horizontal .n-scrollbar-container) {
  height: 12px;
}
.preview-table :deep(.n-scrollbar-rail--horizontal .n-scrollbar-content) {
  height: 8px;
  border-radius: 4px;
  background-color: rgba(100, 116, 139, 0.5);
}
.preview-table :deep(.n-scrollbar-rail--horizontal:hover .n-scrollbar-content),
.preview-table :deep(.n-scrollbar-rail--horizontal .n-scrollbar-content:active) {
  background-color: rgba(51, 65, 85, 0.75);
}

.panel {
  animation: panel-in 0.4s ease backwards;
}
@keyframes panel-in {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}
.hint {
  font-size: 13px;
  color: #999;
}
.toolbar-actions {
  display: flex;
  gap: 10px;
}
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 18px;
}
.sheet-card {
  cursor: pointer;
  border-radius: 14px;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.sheet-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 24px rgba(59, 130, 246, 0.18);
}
.s-head {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}
.s-icon {
  color: #2563eb;
  margin-top: 2px;
}
.s-title h3 {
  margin: 0 0 4px;
  font-size: 17px;
}
.s-desc {
  margin: 0;
  font-size: 13px;
  color: #888;
}
.s-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
  flex-wrap: wrap;
  font-size: 12px;
}
.s-file {
  color: #999;
  max-width: 40%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.s-date {
  margin-left: auto;
  color: #bbb;
}
.s-actions {
  display: flex;
  gap: 6px;
  margin-top: 8px;
}
.empty {
  padding: 70px 0 90px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}
.empty-text {
  margin: 0 0 4px;
  color: #8a8a94;
  font-size: 15px;
}
.upload-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.preview-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}
.preview-table {
  margin-top: 8px;
}
</style>
