import request from './request'
import type { ApiResponse, LoginData } from '@/types'

export const authApi = {
  register(data: { username: string; email: string; password: string; nickname?: string }) {
    return request.post('/auth/register', data) as Promise<ApiResponse<null>>
  },
  login(data: { username: string; password: string }) {
    return request.post('/auth/login', data) as Promise<ApiResponse<LoginData>>
  },
  refresh(refresh_token: string) {
    return request.post('/auth/refresh', { refresh_token }) as Promise<ApiResponse<any>>
  },
  logout(refresh_token: string) {
    return request.post('/auth/logout', { refresh_token }) as Promise<ApiResponse<null>>
  },
  changePassword(data: { old_password: string; new_password: string }) {
    return request.put('/auth/password', data) as Promise<ApiResponse<null>>
  },
}
