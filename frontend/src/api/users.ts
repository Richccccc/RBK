import { http } from './client'

/** 当前登录用户资料（含昵称/手机号/邮箱/头像） */
export interface MeInfo {
  id: number
  username: string
  nickname: string
  phone: string
  email: string
  avatar_url: string
  created_at: string | null
}

export function getMe() {
  return http.get<MeInfo>('/users/me')
}

/** 更新个人资料（昵称/手机号/邮箱） */
export function updateMe(payload: { nickname: string; phone: string; email: string }) {
  return http.put<MeInfo>('/users/me', payload)
}

/** 上传头像：服务端存 GitHub 图床（未配置时降级 base64），返回更新后的用户 */
export function uploadAvatar(file: File) {
  const fd = new FormData()
  fd.append('file', file)
  return http.post<MeInfo>('/users/me/avatar', fd)
}
