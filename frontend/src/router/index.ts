import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  { path: '/login', name: 'Login', component: () => import('@/views/Login.vue'), meta: { public: true } },
  { path: '/register', name: 'Register', component: () => import('@/views/Register.vue'), meta: { public: true } },
  {
    path: '/',
    component: () => import('@/views/AppLayout.vue'),
    children: [
      { path: '', name: 'Dashboard', component: () => import('@/views/Dashboard.vue') },
      { path: 'transactions', name: 'TransactionList', component: () => import('@/views/TransactionList.vue') },
      { path: 'transactions/add', name: 'TransactionAdd', component: () => import('@/views/TransactionForm.vue') },
      { path: 'transactions/:id/edit', name: 'TransactionEdit', component: () => import('@/views/TransactionForm.vue') },
      { path: 'categories', name: 'CategoryManage', component: () => import('@/views/CategoryManage.vue') },
      { path: 'budgets', name: 'BudgetManage', component: () => import('@/views/BudgetManage.vue') },
      { path: 'reports/monthly', name: 'ReportMonthly', component: () => import('@/views/ReportMonthly.vue') },
      { path: 'reports/category', name: 'ReportCategory', component: () => import('@/views/ReportCategory.vue') },
      { path: 'reports/trend', name: 'ReportTrend', component: () => import('@/views/ReportTrend.vue') },
      { path: 'settings', name: 'Settings', component: () => import('@/views/Settings.vue') },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, _from, next) => {
  const auth = useAuthStore()
  if (to.meta.public) {
    if (auth.isLoggedIn && (to.name === 'Login' || to.name === 'Register')) {
      next({ name: 'Dashboard' })
    } else {
      next()
    }
  } else if (!auth.isLoggedIn) {
    next({ name: 'Login' })
  } else {
    next()
  }
})

export default router
