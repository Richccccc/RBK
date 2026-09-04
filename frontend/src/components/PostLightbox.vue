<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'

/**
 * 全屏图片灯箱：点击正文/封面图片后放大查看
 * - 滚轮缩放、双击在 1x/2x 间切换
 * - Esc 或点击空白处关闭
 */
const props = defineProps<{ src: string | null }>()
const emit = defineEmits<{ (e: 'close'): void }>()

const scale = ref(1)

watch(
  () => props.src,
  (v) => {
    if (v) scale.value = 1
  },
)

function onWheel(e: WheelEvent) {
  scale.value = Math.min(5, Math.max(0.4, scale.value * (e.deltaY < 0 ? 1.15 : 0.87)))
}

function onDblClick() {
  scale.value = scale.value > 1 ? 1 : 2
}

function onKey(e: KeyboardEvent) {
  if (e.key === 'Escape' && props.src) emit('close')
}

onMounted(() => window.addEventListener('keydown', onKey))
onBeforeUnmount(() => window.removeEventListener('keydown', onKey))
</script>

<template>
  <Teleport to="body">
    <Transition name="lb">
      <div v-if="src" class="lightbox" @click="emit('close')">
        <img
          :src="src"
          alt="查看图片"
          :style="{ transform: `scale(${scale})` }"
          @click.stop
          @dblclick="onDblClick"
          @wheel.prevent="onWheel"
        />
        <div class="lb-tip" @click.stop>滚轮缩放 · 双击放大 · 点击空白关闭</div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.lightbox {
  position: fixed;
  inset: 0;
  z-index: 6000;
  background: rgba(8, 14, 32, 0.82);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: zoom-out;
}
.lightbox img {
  max-width: 92vw;
  max-height: 90vh;
  border-radius: 10px;
  box-shadow: 0 24px 80px rgba(0, 0, 0, 0.5);
  transition: transform 0.18s ease;
  user-select: none;
}
.lb-tip {
  position: absolute;
  bottom: 22px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 12px;
  letter-spacing: 1px;
  color: rgba(255, 255, 255, 0.78);
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 6px 14px;
  border-radius: 999px;
  backdrop-filter: blur(6px);
  white-space: nowrap;
}
.lb-enter-active,
.lb-leave-active {
  transition: opacity 0.2s ease;
}
.lb-enter-from,
.lb-leave-to {
  opacity: 0;
}
</style>
