import request from './request'
import type { ApiResponse, MonthlySummaryItem, CategoryBreakdownItem, TrendItem, MemberComparisonItem } from '@/types'

export const reportApi = {
  monthlySummary(year: number) {
    return request.get('/reports/monthly-summary', { params: { year } }) as Promise<ApiResponse<MonthlySummaryItem[]>>
  },
  categoryBreakdown(year_month: string) {
    return request.get('/reports/category-breakdown', { params: { year_month } }) as Promise<ApiResponse<CategoryBreakdownItem[]>>
  },
  trend(months: number) {
    return request.get('/reports/trend', { params: { months } }) as Promise<ApiResponse<TrendItem[]>>
  },
  memberComparison(year_month: string) {
    return request.get('/reports/member-comparison', { params: { year_month } }) as Promise<ApiResponse<MemberComparisonItem[]>>
  },
  necessityAnalysis(year_month: string) {
    return request.get('/reports/necessity-analysis', { params: { year_month } }) as Promise<ApiResponse<any>>
  },
}
