export interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

export interface PaginatedData<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface User {
  id: string
  username: string
  email: string
  nickname: string | null
  avatar_url: string | null
  phone: string | null
  is_active: boolean
  last_login_at: string | null
  created_at: string
}

export interface LoginData {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  user: {
    id: string
    username: string
    nickname: string | null
    avatar_url: string | null
  }
  family_id: string
  family_name: string
}

export interface Family {
  id: string
  name: string
  invite_code: string
  owner_id: string
  created_at: string
}

export interface FamilyMember {
  id: string
  user_id: string
  username: string
  nickname: string | null
  display_name: string | null
  role: string
  joined_at: string
}

export interface SubCategory {
  id: string
  name: string
  sort_order: number
  is_active: boolean
}

export interface Category {
  id: string
  name: string
  type: string
  icon: string | null
  color: string
  sort_order: number
  is_system: boolean
  is_active: boolean
  sub_categories: SubCategory[]
}

export interface Transaction {
  id: string
  family_id: string
  creator_id: string
  member_id: string
  transaction_date: string
  transaction_time: string | null
  type: 'expense' | 'income'
  amount: number
  description: string
  merchant: string | null
  category_id: string
  sub_category_id: string
  payment_method_id: string | null
  fund_source_id: string | null
  reimbursement: string
  necessity: string | null
  is_recurring: boolean
  notes: string | null
  attachments: any[] | null
  is_deleted: boolean
  created_at: string
  updated_at: string
  category_name?: string
  sub_category_name?: string
  member_name?: string
}

export interface BudgetCategoryItem {
  category_id: string
  category_name: string
  budget: number
  actual: number
  remaining: number
  ratio: number
  status: 'normal' | 'warning' | 'exceeded'
}

export interface BudgetResponse {
  year_month: string
  total_budget: number
  total_actual: number
  total_remaining: number
  items: BudgetCategoryItem[]
}

export interface MonthlySummaryItem {
  month: string
  income: number
  expense: number
  balance: number
}

export interface CategoryBreakdownItem {
  category_id: string
  category_name: string
  amount: number
  ratio: number
  count: number
}

export interface TrendItem {
  month: string
  income: number
  expense: number
}

export interface MemberComparisonItem {
  member_id: string
  member_name: string
  total_expense: number
  transaction_count: number
}

export interface DashboardOverview {
  month_income: number
  month_expense: number
  month_balance: number
  pending_reimbursement: number
}
