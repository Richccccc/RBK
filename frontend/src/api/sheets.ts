import { http } from './client'

export interface SheetTable {
  name: string
  headers: string[]
  rows: string[][]
}

export interface SheetMeta {
  id: number
  name: string
  description: string
  file_name: string
  sheet_count: number
  rows_count: number
  cols_count: number
  created_at: string
  updated_at: string
}

export interface SheetDetail extends SheetMeta {
  tables: SheetTable[]
}

export interface SheetListResponse {
  total: number
  items: SheetMeta[]
}

export function listSheets(params?: { q?: string; page?: number; size?: number }) {
  return http.get<SheetListResponse>('/sheets', { params })
}

export function getSheet(id: number | string) {
  return http.get<SheetDetail>(`/sheets/${id}`)
}

/** 上传表格：解析在服务端完成，直接返回元信息 */
export async function uploadSheet(file: File, name: string, description: string) {
  const fd = new FormData()
  fd.append('file', file)
  fd.append('name', name)
  fd.append('description', description)
  const res = await http.post<SheetMeta>('/sheets', fd)
  return res.data
}

export function deleteSheet(id: number | string) {
  return http.delete(`/sheets/${id}`)
}

/** 下载原始文件：直接拼 URL 让浏览器走下载（带登录态的接口无需鉴权头） */
export function sheetDownloadUrl(id: number | string) {
  return `${import.meta.env.VITE_API_BASE || '/api'}/sheets/${id}/download`
}
