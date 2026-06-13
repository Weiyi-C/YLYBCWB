import request from './request'
import type { ApiResponse, PaginatedData, Transaction } from '@/types'

export interface TransactionQuery {
  page?: number
  page_size?: number
  type?: string
  date_from?: string
  date_to?: string
  category_id?: string
  sub_category_id?: string
  member_id?: string
  payment_method_id?: string
  fund_source_id?: string
  reimbursement?: string
  necessity?: string
  keyword?: string
  min_amount?: number
  max_amount?: number
  sort_by?: string
  sort_order?: string
}

export const transactionApi = {
  list(params: TransactionQuery) {
    return request.get('/transactions', { params }) as Promise<ApiResponse<PaginatedData<Transaction>>>
  },
  get(id: string) {
    return request.get(`/transactions/${id}`) as Promise<ApiResponse<Transaction>>
  },
  create(data: any) {
    return request.post('/transactions', data) as Promise<ApiResponse<Transaction>>
  },
  update(id: string, data: any) {
    return request.put(`/transactions/${id}`, data) as Promise<ApiResponse<Transaction>>
  },
  delete(id: string) {
    return request.delete(`/transactions/${id}`) as Promise<ApiResponse<null>>
  },
}
