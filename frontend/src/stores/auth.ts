import { defineStore } from 'pinia'

export interface UserInfo {
  id: number
  username: string
  nickname: string
  phone: string
  email: string
  avatar_url: string
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    user: JSON.parse(localStorage.getItem('user') || 'null') as UserInfo | null,
  }),
  getters: {
    isLogin: (state) => !!state.token,
    // 展示名：平台昵称优先，未设置则用用户名
    displayName: (state) => state.user?.nickname || state.user?.username || '朋友',
  },
  actions: {
    setAuth(token: string, user: UserInfo) {
      this.token = token
      this.user = user
      localStorage.setItem('token', token)
      localStorage.setItem('user', JSON.stringify(user))
    },
    // 个人资料更新后同步本地（登录态 token 不变）
    setUser(user: UserInfo) {
      this.user = user
      localStorage.setItem('user', JSON.stringify(user))
    },
    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    },
  },
})
