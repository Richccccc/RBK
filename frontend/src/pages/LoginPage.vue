<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NButton, NCard, NForm, NFormItem, NInput, NTabPane, NTabs, useMessage } from 'naive-ui'
import { login, register } from '../api/auth'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const message = useMessage()
const auth = useAuthStore()

const tab = ref('login')
const username = ref('')
const password = ref('')
const loading = ref(false)

async function submit() {
  if (!username.value || !password.value) {
    message.warning('请输入用户名和密码')
    return
  }
  loading.value = true
  try {
    const fn = tab.value === 'login' ? login : register
    const { data } = await fn(username.value, password.value)
    auth.setAuth(data.access_token, data.user)
    message.success(tab.value === 'login' ? '登录成功' : '注册成功')
    const redirect = (route.query.redirect as string) || '/'
    router.push(redirect)
  } catch (e: any) {
    message.error(e?.response?.data?.detail || '操作失败')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-wrap">
    <NCard class="login-card" title="我的博客">
      <NTabs v-model:value="tab" type="line" justify="space-evenly">
        <NTabPane name="login" tab="登录" />
        <NTabPane name="register" tab="注册" />
      </NTabs>
      <NForm @keyup.enter="submit">
        <NFormItem label="用户名">
          <NInput v-model:value="username" placeholder="用户名" />
        </NFormItem>
        <NFormItem label="密码">
          <NInput v-model:value="password" type="password" show-password-on="click" placeholder="密码" />
        </NFormItem>
        <NButton type="primary" block :loading="loading" @click="submit">
          {{ tab === 'login' ? '登录' : '注册' }}
        </NButton>
      </NForm>
    </NCard>
  </div>
</template>

<style scoped>
.login-wrap {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}
.login-card {
  width: 100%;
  max-width: 380px;
}
</style>