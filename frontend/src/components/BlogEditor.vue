<script setup lang="ts">
import { onBeforeUnmount, ref, watch } from 'vue'
import { EditorContent, useEditor } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import Underline from '@tiptap/extension-underline'
import Highlight from '@tiptap/extension-highlight'
import TextStyle from '@tiptap/extension-text-style'
import Color from '@tiptap/extension-color'
import TextAlign from '@tiptap/extension-text-align'
import Image from '@tiptap/extension-image'
import Link from '@tiptap/extension-link'
import { NButton, NColorPicker, NIcon, NSelect, useMessage } from 'naive-ui'
import {
  ArrowRedoOutline,
  ArrowUndoOutline,
  CodeSlashOutline,
  CreateOutline,
  ImageOutline,
  LinkOutline,
  ListCircleOutline,
  ListOutline,
  ReturnDownBackOutline,
} from '@vicons/ionicons5'
import { FontFamily, FontSize } from '../utils/tiptapExt'
import { FONT_OPTIONS, FONT_SIZE_OPTIONS } from '../utils/fonts'
import { uploadImage } from '../api/posts'
import { compressImageFile } from '../utils/image'

const props = defineProps<{ modelValue: string }>()
const emit = defineEmits<{ (e: 'update:modelValue', v: string): void }>()

const message = useMessage()
const imgInput = ref<HTMLInputElement>()
const textColor = ref('#333333')

const editor = useEditor({
  content: props.modelValue,
  extensions: [
    StarterKit,
    Underline,
    Highlight,
    TextStyle,
    Color,
    TextAlign.configure({ types: ['heading', 'paragraph'] }),
    Image.configure({ inline: false, allowBase64: true }),
    Link.configure({ openOnClick: false }),
    FontFamily,
    FontSize,
  ],
  editorProps: {
    attributes: {
      class: 'tip-tap-body',
    },
  },
  onUpdate: ({ editor }) => {
    emit('update:modelValue', editor.getHTML())
  },
})

// 外部（如 Word 导入）改值 -> 同步到编辑器
watch(
  () => props.modelValue,
  (val) => {
    if (editor.value && val !== editor.value.getHTML()) {
      editor.value.commands.setContent(val || '', false)
    }
  },
)

const headingOptions = [
  { label: '正文', value: 0 },
  { label: '标题 1', value: 1 },
  { label: '标题 2', value: 2 },
  { label: '标题 3', value: 3 },
]
const heading = ref(0)
function setHeading(v: number) {
  if (!editor.value) return
  if (v === 0) editor.value.chain().focus().setParagraph().run()
  else editor.value.chain().focus().toggleHeading({ level: v as 1 | 2 | 3 }).run()
}

function isActive(name: string, attrs?: Record<string, any>) {
  return editor.value?.isActive(name, attrs) || false
}

function setColor(color: string) {
  textColor.value = color
  editor.value?.chain().focus().setColor(color).run()
}

function pickImage() {
  imgInput.value?.click()
}
async function onImage(e: Event) {
  const input = e.target as HTMLInputElement
  const picked = input.files?.[0]
  if (!picked || !editor.value) return
  try {
    const file = await compressImageFile(picked)
    const url = await uploadImage(file)
    editor.value.chain().focus().setImage({ src: url }).run()
    message.success('图片已插入')
  } catch {
    message.error('图片上传失败')
  } finally {
    input.value = ''
  }
}

function setLink() {
  const url = window.prompt('请输入链接地址：')
  if (url) editor.value?.chain().focus().setLink({ href: url }).run()
}
function unsetLink() {
  editor.value?.chain().focus().unsetLink().run()
}

onBeforeUnmount(() => editor.value?.destroy())
</script>

<template>
  <div class="editor-shell">
    <div v-if="editor" class="toolbar">
      <NButton quaternary size="small" @click="editor.chain().focus().undo().run()">
        <template #icon><NIcon :component="ArrowUndoOutline" /></template>
      </NButton>
      <NButton quaternary size="small" @click="editor.chain().focus().redo().run()">
        <template #icon><NIcon :component="ArrowRedoOutline" /></template>
      </NButton>

      <span class="sep" />

      <NSelect v-model:value="heading" size="small" :options="headingOptions" style="width: 96px" @update:value="setHeading" />

      <span class="sep" />

      <NSelect
        key="font"
        :value="''"
        size="small"
        :options="FONT_OPTIONS"
        placeholder="字体"
        style="width: 120px"
        filterable
        @update:value="(v: string) => editor!.chain().focus().setFontFamily(v).run()"
      />
      <NSelect
        key="size"
        :value="null"
        size="small"
        :options="FONT_SIZE_OPTIONS"
        placeholder="字号"
        style="width: 88px"
        @update:value="(v: string) => editor!.chain().focus().setFontSize(v).run()"
      />

      <span class="sep" />

      <NButton size="small" :type="isActive('bold') ? 'primary' : 'default'" @click="editor.chain().focus().toggleBold().run()">B</NButton>
      <NButton size="small" :type="isActive('italic') ? 'primary' : 'default'" @click="editor.chain().focus().toggleItalic().run()"><em>I</em></NButton>
      <NButton size="small" :type="isActive('underline') ? 'primary' : 'default'" @click="editor.chain().focus().toggleUnderline().run()"><u>U</u></NButton>
      <NButton size="small" :type="isActive('strike') ? 'primary' : 'default'" @click="editor.chain().focus().toggleStrike().run()"><s>S</s></NButton>
      <NButton size="small" :type="isActive('highlight') ? 'primary' : 'default'" @click="editor.chain().focus().toggleHighlight().run()">高亮</NButton>

      <NColorPicker :show-alpha="false" :value="textColor" @update:value="setColor" />

      <span class="sep" />

      <NButton size="small" :type="isActive({ textAlign: 'left' }) ? 'primary' : 'default'" @click="editor.chain().focus().setTextAlign('left').run()">左</NButton>
      <NButton size="small" :type="isActive({ textAlign: 'center' }) ? 'primary' : 'default'" @click="editor.chain().focus().setTextAlign('center').run()">中</NButton>
      <NButton size="small" :type="isActive({ textAlign: 'right' }) ? 'primary' : 'default'" @click="editor.chain().focus().setTextAlign('right').run()">右</NButton>

      <span class="sep" />

      <NButton size="small" :type="isActive('bulletList') ? 'primary' : 'default'" @click="editor.chain().focus().toggleBulletList().run()">
        <template #icon><NIcon :component="ListOutline" /></template>
      </NButton>
      <NButton size="small" :type="isActive('orderedList') ? 'primary' : 'default'" @click="editor.chain().focus().toggleOrderedList().run()">
        <template #icon><NIcon :component="ListCircleOutline" /></template>
      </NButton>
      <NButton size="small" :type="isActive('blockquote') ? 'primary' : 'default'" @click="editor.chain().focus().toggleBlockquote().run()">
        <template #icon><NIcon :component="ReturnDownBackOutline" /></template>
      </NButton>
      <NButton size="small" :type="isActive('codeBlock') ? 'primary' : 'default'" @click="editor.chain().focus().toggleCodeBlock().run()">
        <template #icon><NIcon :component="CodeSlashOutline" /></template>
      </NButton>

      <span class="sep" />

      <NButton size="small" @click="pickImage">
        <template #icon><NIcon :component="ImageOutline" /></template>
      </NButton>
      <NButton size="small" @click="setLink">
        <template #icon><NIcon :component="LinkOutline" /></template>
      </NButton>
      <NButton size="small" @click="editor.chain().focus().setHorizontalRule().run()">
        <template #icon><NIcon :component="CreateOutline" /></template>
      </NButton>
    </div>

    <input ref="imgInput" type="file" accept="image/*" hidden @change="onImage" />

    <EditorContent :editor="editor" class="editor-content" />
  </div>
</template>

<style scoped>
.editor-shell {
  border: 1px solid #e5e5ea;
  border-radius: 12px;
  background: #fff;
  overflow: hidden;
}
.toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
  padding: 10px;
  border-bottom: 1px solid #eee;
}
.sep {
  width: 1px;
  height: 20px;
  background: #eee;
  margin: 0 2px;
}
.editor-content {
  min-height: 320px;
}
.editor-content :deep(.tip-tap-body) {
  min-height: 320px;
  padding: 16px 20px;
  outline: none;
  font-size: 16px;
  line-height: 1.8;
}
.editor-content :deep(img) {
  max-width: 100%;
}
</style>