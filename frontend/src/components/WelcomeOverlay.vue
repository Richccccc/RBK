<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useAuthStore } from '../stores/auth'

const emit = defineEmits<{ (e: 'done'): void }>()
const auth = useAuthStore()

const leaving = ref(false)

const greeting = computed(() => {
  const h = new Date().getHours()
  if (h >= 5 && h < 11) return '早上好'
  if (h >= 11 && h < 18) return '下午好'
  return '晚上好'
})

onMounted(() => {
  // 1.6s 后开始淡出，2.2s 后卸载
  setTimeout(() => (leaving.value = true), 1600)
  setTimeout(() => emit('done'), 2200)
})
</script>

<template>
  <div class="welcome" :class="{ leave: leaving }">
    <div class="shine" aria-hidden="true"></div>
    <div class="blob b1" aria-hidden="true"></div>
    <div class="blob b2" aria-hidden="true"></div>
    <p class="greet">{{ greeting }}</p>
    <h1 class="name">欢迎回来，{{ auth.user?.username || '朋友' }}</h1>
    <p class="slogan">记录此刻 · 写给时间</p>
  </div>
</template>

<style scoped>
.welcome {
  position: fixed;
  inset: 0;
  z-index: 3000;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 14px;
  background: linear-gradient(160deg, #1d4ed8, #3b82f6 45%, #7db4fc);
  overflow: hidden;
  transition: opacity 0.55s ease;
}
.welcome.leave {
  opacity: 0;
  pointer-events: none;
}

/* 流光扫过 */
.shine {
  position: absolute;
  top: 0;
  left: -70%;
  width: 45%;
  height: 100%;
  background: linear-gradient(105deg, transparent, rgba(255, 255, 255, 0.22) 50%, transparent);
  transform: skewX(-18deg);
  animation: welcome-shine 1.5s ease forwards;
}
@keyframes welcome-shine {
  to {
    left: 135%;
  }
}

/* 漂浮光斑 */
.blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(70px);
  opacity: 0.5;
}
.b1 {
  width: 380px;
  height: 380px;
  background: #93c5fd;
  top: -120px;
  left: -100px;
  animation: blob-float 7s ease-in-out infinite alternate;
}
.b2 {
  width: 300px;
  height: 300px;
  background: #60a5fa;
  bottom: -100px;
  right: -80px;
  animation: blob-float 9s ease-in-out infinite alternate-reverse;
}
@keyframes blob-float {
  from {
    transform: translate(0, 0) scale(1);
  }
  to {
    transform: translate(40px, 26px) scale(1.12);
  }
}

/* 文字分层渐显 */
.greet,
.name,
.slogan {
  margin: 0;
  color: #fff;
  opacity: 0;
  animation: rise-in 0.6s ease forwards;
  position: relative;
  z-index: 1;
}
.greet {
  font-size: 20px;
  letter-spacing: 6px;
  opacity: 0;
  animation-delay: 0.12s;
}
.name {
  font-size: 34px;
  font-weight: 700;
  animation-delay: 0.32s;
  text-shadow: 0 4px 18px rgba(0, 0, 0, 0.18);
}
.slogan {
  font-size: 14px;
  letter-spacing: 3px;
  opacity: 0;
  animation-delay: 0.55s;
}
@keyframes rise-in {
  from {
    opacity: 0;
    transform: translateY(16px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 640px) {
  .name {
    font-size: 26px;
    padding: 0 24px;
    text-align: center;
  }
}
</style>
