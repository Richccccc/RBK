<script setup lang="ts">
import { RouterView } from 'vue-router'
import {
  NConfigProvider,
  NDialogProvider,
  NMessageProvider,
  dateZhCN,
  zhCN,
} from 'naive-ui'
import FeatureDrawer from './components/FeatureDrawer.vue'
import { useAuthStore } from './stores/auth'

const auth = useAuthStore()
</script>

<template>
  <n-config-provider :locale="zhCN" :date-locale="dateZhCN">
    <n-message-provider>
      <n-dialog-provider>
        <FeatureDrawer v-if="auth.isLogin" />
        <RouterView />
      </n-dialog-provider>
    </n-message-provider>
  </n-config-provider>
</template>