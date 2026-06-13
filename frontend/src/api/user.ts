import request from './request'
import type { ApiResponse, User } from '@/types'

export const userApi = {
  getMe() {
    return request.get('/users/me') as Promise<ApiResponse<User>>
  },
  updateMe(data: { nickname?: string; avatar_url?: string; phone?: string }) {
    return request.put('/users/me', data) as Promise<ApiResponse<User>>
  },
}
