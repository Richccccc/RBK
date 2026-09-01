import { http } from './client'

export interface AuthUser {
  id: number
  username: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: AuthUser
}

export function register(username: string, password: string) {
  return http.post<LoginResponse>('/auth/register', { username, password })
}

export function login(username: string, password: string) {
  return http.post<LoginResponse>('/auth/login', { username, password })
}