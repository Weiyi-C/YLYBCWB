import request from './request'
import type { ApiResponse, DashboardOverview, Transaction } from '@/types'

export const dashboardApi = {
  overview() {
    return request.get('/dashboard/overview') as Promise<ApiResponse<DashboardOverview>>
  },
  recent(limit: number = 10) {
    return request.get('/dashboard/recent', { params: { limit } }) as Promise<ApiResponse<Transaction[]>>
  },
}
