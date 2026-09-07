<script setup lang="ts">
import { ref, watch } from 'vue'
import { RouterView, useRoute } from 'vue-router'
import {
  NConfigProvider,
  NDialogProvider,
  NMessageProvider,
  dateZhCN,
  zhCN,
  type GlobalThemeOverrides,
} from 'naive-ui'
import TopBar from './components/TopBar.vue'
import WelcomeOverlay from './components/WelcomeOverlay.vue'
import { useAuthStore } from './stores/auth'

const auth = useAuthStore()
const route = useRoute()

// 晴朗天蓝主题（覆盖 Naive UI 默认绿色）
// 注意：Naive UI 的 common 覆盖键是 primaryColor/xxxColor 系列，写 primary 会被静默忽略
const themeOverrides: GlobalThemeOverrides = {
  common: {
    primaryColor: '#3b82f6',
    primaryColorHover: '#5a97f8',
    primaryColorPressed: '#2e6fe3',
    primaryColorSuppl: '#3b82f6',
    // 成功提示也走蓝色系（用户不喜欢绿色）
    successColor: '#0ea5e9',
    successColorHover: '#38bdf8',
    successColorPressed: '#0284c7',
    successColorSuppl: '#0ea5e9',
  },
}

// 登录成功后的一次性欢迎过渡屏（sessionStorage 标记，刷新不重复）
const showWelcome = ref(false)
function checkWelcome() {
  if (auth.isLogin && sessionStorage.getItem('welcome-pending') === '1') {
    sessionStorage.removeItem('welcome-pending')
    showWelcome.value = true
  }
}
watch(
  () => route.path,
  () => checkWelcome(),
)
</script>

<template>
  <n-config-provider :locale="zhCN" :date-locale="dateZhCN" :theme-overrides="themeOverrides">
    <n-message-provider>
      <n-dialog-provider>
        <TopBar v-if="auth.isLogin" />
        <WelcomeOverlay v-if="showWelcome" @done="showWelcome = false" />
        <RouterView v-slot="{ Component }">
          <Transition name="page" mode="out-in">
            <component :is="Component" />
          </Transition>
        </RouterView>
      </n-dialog-provider>
    </n-message-provider>
  </n-config-provider>
</template>

<style scoped>
/* 路由切换淡入过渡 */
.page-enter-active,
.page-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}
.page-enter-from {
  opacity: 0;
  transform: translateY(8px);
}
.page-leave-to {
  opacity: 0;
}
</style>
