<script setup lang="ts">
import { h, ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  NButton,
  NDrawer,
  NDrawerContent,
  NIcon,
  NMenu,
  NTag,
  type MenuOption,
} from 'naive-ui'
import {
  BookOutline,
  ChatbubblesOutline,
  CreateOutline,
  HomeOutline,
  ImagesOutline,
  InformationCircleOutline,
  LogInOutline,
  LogOutOutline,
  MenuOutline,
  PersonOutline,
} from '@vicons/ionicons5'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()

const show = ref(false)

const renderIcon = (icon: any) => () => h(NIcon, null, { default: () => h(icon) })

const options = ref<MenuOption[]>([
  { label: '博客列表', key: 'home', icon: renderIcon(HomeOutline) },
  { label: '日记', key: 'diary', icon: renderIcon(BookOutline) },
  { label: '新建博客', key: 'new', icon: renderIcon(CreateOutline) },
  { type: 'divider', key: 'd1' },
  { label: '关于我', key: 'about', icon: renderIcon(InformationCircleOutline), disabled: true },
  { label: '相册', key: 'album', icon: renderIcon(ImagesOutline), disabled: true },
  { label: '留言板', key: 'guestbook', icon: renderIcon(ChatbubblesOutline), disabled: true },
  { type: 'divider', key: 'd2' },
])

// 登录态动态追加
const accountOptions = ref<MenuOption[]>([])

function refreshAccountOptions() {
  if (auth.isLogin) {
    accountOptions.value = [
      { label: auth.user?.username || '账号', key: 'profile', icon: renderIcon(PersonOutline), disabled: true },
      { label: '退出登录', key: 'logout', icon: renderIcon(LogOutOutline) },
    ]
  } else {
    accountOptions.value = [{ label: '登录', key: 'login', icon: renderIcon(LogInOutline) }]
  }
}

const allOptions = () => [...options.value, ...accountOptions.value]
refreshAccountOptions()

function onSelect(key: string) {
  show.value = false
  switch (key) {
    case 'home':
      router.push('/')
      break
    case 'diary':
      router.push('/diary')
      break
    case 'new':
      router.push(auth.isLogin ? '/new' : '/login?redirect=/new')
      break
    case 'login':
      router.push('/login')
      break
    case 'logout':
      auth.logout()
      refreshAccountOptions()
      router.push('/')
      break
    default:
      break
  }
}

function open() {
  refreshAccountOptions()
  show.value = true
}
</script>

<template>
  <NButton class="fab" circle size="large" type="primary" @click="open">
    <template #icon>
      <NIcon :component="MenuOutline" />
    </template>
  </NButton>

  <NDrawer v-model:show="show" placement="left" :width="260">
    <NDrawerContent title="功能" closable>
      <NMenu
        :options="allOptions()"
        :default-value="null"
        @update:value="onSelect"
      />
      <div class="drawer-tip">
        <NTag size="small" :bordered="false" type="warning">灰度</NTag>
        灰色项为预留功能入口，后续接入
      </div>
    </NDrawerContent>
  </NDrawer>
</template>

<style scoped>
.fab {
  position: fixed;
  top: 18px;
  left: 18px;
  z-index: 2000;
  box-shadow: 0 6px 18px rgba(124, 124, 230, 0.35);
}
.drawer-tip {
  margin-top: 16px;
  padding: 0 12px;
  font-size: 12px;
  color: #999;
  display: flex;
  align-items: center;
  gap: 6px;
}
</style>