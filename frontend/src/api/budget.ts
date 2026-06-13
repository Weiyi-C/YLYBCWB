import request from './request'
import type { ApiResponse, BudgetResponse } from '@/types'

export const budgetApi = {
  get(year_month: string) {
    return request.get('/budgets', { params: { year_month } }) as Promise<ApiResponse<BudgetResponse>>
  },
  set(data: { year_month: string; items: { category_id: string; amount: number }[] }) {
    return request.put('/budgets', data) as Promise<ApiResponse<null>>
  },
}
