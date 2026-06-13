<template>
  <div>
    <div class="page-header">
      <h2>交易记录</h2>
      <el-button type="primary" @click="$router.push('/transactions/add')">
        <el-icon><Plus /></el-icon> 记一笔
      </el-button>
    </div>

    <div class="card filter-bar">
      <el-date-picker v-model="filters.dateRange" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" value-format="YYYY-MM-DD" @change="fetchData" />
      <el-select v-model="filters.type" placeholder="收支类型" clearable @change="fetchData" style="width: 120px">
        <el-option label="支出" value="expense" />
        <el-option label="收入" value="income" />
      </el-select>
      <el-select v-model="filters.category_id" placeholder="分类" clearable @change="fetchData" style="width: 140px">
        <el-option v-for="c in categoryStore.categories" :key="c.id" :label="c.name" :value="c.id" />
      </el-select>
      <el-input v-model="filters.keyword" placeholder="搜索描述/备注" clearable @clear="fetchData" @keyup.enter="fetchData" style="width: 200px" />
      <el-button @click="fetchData">搜索</el-button>
    </div>

    <div class="card">
      <el-table :data="list" v-loading="loading" @row-click="(row: any) => $router.push(`/transactions/${row.id}/edit`)">
        <el-table-column prop="transaction_date" label="日期" width="100" />
        <el-table-column prop="description" label="描述" min-width="150" />
        <el-table-column prop="category_name" label="分类" width="100" />
        <el-table-column prop="member_name" label="记账人" width="80" />
        <el-table-column prop="amount" label="金额" width="100">
          <template #default="{ row }">
            <span :class="row.type === 'expense' ? 'amount-negative' : 'amount-positive'">
              {{ row.type === 'expense' ? '-' : '+' }}{{ row.amount }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80">
          <template #default="{ row }">
            <el-button link type="danger" size="small" @click.stop="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div style="margin-top: 16px; text-align: right">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          @current-change="fetchData"
          @size-change="fetchData"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { transactionApi } from '@/api/transaction'
import { useCategoryStore } from '@/stores/category'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { Transaction } from '@/types'

const categoryStore = useCategoryStore()
const loading = ref(false)
const list = ref<Transaction[]>([])
const pagination = reactive({ page: 1, pageSize: 20, total: 0 })
const filters = reactive({ dateRange: null as [string, string] | null, type: '', category_id: '', keyword: '' })

async function fetchData() {
  loading.value = true
  try {
    const params: any = { page: pagination.page, page_size: pagination.pageSize }
    if (filters.dateRange) { params.date_from = filters.dateRange[0]; params.date_to = filters.dateRange[1] }
    if (filters.type) params.type = filters.type
    if (filters.category_id) params.category_id = filters.category_id
    if (filters.keyword) params.keyword = filters.keyword
    const res = await transactionApi.list(params)
    list.value = res.data.items
    pagination.total = res.data.total
  } finally {
    loading.value = false
  }
}

async function handleDelete(id: string) {
  await ElMessageBox.confirm('确定删除这条记录？', '确认')
  await transactionApi.delete(id)
  ElMessage.success('已删除')
  fetchData()
}

onMounted(fetchData)
</script>
