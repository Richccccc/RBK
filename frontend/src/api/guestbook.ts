import { http } from './client'

export interface GuestMessage {
  id: number
  name: string
  content: string
  created_at: string
}

export interface GuestListResponse {
  total: number
  items: GuestMessage[]
}

export function listMessages(params?: { page?: number; size?: number }) {
  return http.get<GuestListResponse>('/guestbook', { params })
}

export function createMessage(name: string, content: string) {
  return http.post<GuestMessage>('/guestbook', { name, content })
}

export function deleteMessage(id: number | string) {
  return http.delete(`/guestbook/${id}`)
}
