import { http } from './client'

export type PostType = 'blog' | 'diary'

export interface PostItem {
  id: number
  title: string
  summary: string
  type: PostType
  category: string
  cover_image: string
  created_at: string
  updated_at: string
}

export interface PostDetail extends PostItem {
  content: string
  font_family: string
  author_id: number
}

export interface PostListResponse {
  total: number
  items: PostItem[]
}

export interface PostStats {
  all: number
  blog: number
  diary: number
}

export interface PostPayload {
  title: string
  content: string
  summary?: string
  type?: PostType
  category?: string
  font_family?: string
  cover_image?: string
}

export function listPosts(params?: {
  type?: PostType
  category?: string
  q?: string
  page?: number
  size?: number
}) {
  return http.get<PostListResponse>('/posts', { params })
}

export function postStats() {
  return http.get<PostStats>('/posts/stats')
}

export function getPost(id: number | string) {
  return http.get<PostDetail>(`/posts/${id}`)
}

export function createPost(data: PostPayload) {
  return http.post<PostDetail>('/posts', data)
}

export function updatePost(id: number | string, data: PostPayload) {
  return http.put<PostDetail>(`/posts/${id}`, data)
}

export function deletePost(id: number | string) {
  return http.delete(`/posts/${id}`)
}

export async function uploadImage(file: File) {
  const fd = new FormData()
  fd.append('file', file)
  const res = await http.post<{ url: string }>('/upload/image', fd)
  return res.data.url
}

export async function uploadWord(file: File) {
  const fd = new FormData()
  fd.append('file', file)
  const res = await http.post<{ html: string }>('/upload/word', fd)
  return res.data.html
}