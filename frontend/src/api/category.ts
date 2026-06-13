import request from './request'
import type { ApiResponse, Category } from '@/types'

export const categoryApi = {
  list(type?: string) {
    return request.get('/categories', { params: type ? { type } : {} }) as Promise<ApiResponse<Category[]>>
  },
  create(data: { name: string; type: string; icon?: string; color?: string; sort_order?: number }) {
    return request.post('/categories', data) as Promise<ApiResponse<Category>>
  },
  update(id: string, data: { name?: string; icon?: string; color?: string; sort_order?: number; is_active?: boolean }) {
    return request.put(`/categories/${id}`, data) as Promise<ApiResponse<Category>>
  },
  delete(id: string) {
    return request.delete(`/categories/${id}`) as Promise<ApiResponse<null>>
  },
  createSub(categoryId: string, data: { name: string; sort_order?: number }) {
    return request.post(`/categories/${categoryId}/sub-categories`, data) as Promise<ApiResponse<any>>
  },
  updateSub(id: string, data: { name?: string; sort_order?: number; is_active?: boolean }) {
    return request.put(`/sub-categories/${id}`, data) as Promise<ApiResponse<any>>
  },
  deleteSub(id: string) {
    return request.delete(`/sub-categories/${id}`) as Promise<ApiResponse<null>>
  },
}
