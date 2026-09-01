import { defineStore } from 'pinia'

export interface UserInfo {
  id: number
  username: string
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    user: JSON.parse(localStorage.getItem('user') || 'null') as UserInfo | null,
  }),
  getters: {
    isLogin: (state) => !!state.token,
  },
  actions: {
    setAuth(token: string, user: UserInfo) {
      this.token = token
      this.user = user
      localStorage.setItem('token', token)
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