import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Category } from '@/types'
import { categoryApi } from '@/api/category'

export const useCategoryStore = defineStore('category', () => {
  const categories = ref<Category[]>([])
  const expenseCategories = ref<Category[]>([])
  const incomeCategories = ref<Category[]>([])

  async function fetchCategories() {
    const res = await categoryApi.list()
    categories.value = res.data
    expenseCategories.value = res.data.filter((c: Category) => c.type === 'expense')
    incomeCategories.value = res.data.filter((c: Category) => c.type === 'income')
  }

  return { categories, expenseCategories, incomeCategories, fetchCategories }
})
