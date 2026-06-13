<template>
  <div>
    <div class="page-header">
      <h2>预算管理</h2>
      <el-date-picker v-model="yearMonth" type="month" value-format="YYYY-MM" @change="fetchData" />
    </div>

    <div class="card" v-if="data">
      <el-row :gutter="16" style="margin-bottom: 20px">
        <el-col :span="8">
          <el-statistic title="总预算" :value="data.total_budget" prefix="¥" />
        </el-col>
        <el-col :span="8">
          <el-statistic title="已支出" :value="data.total_actual" prefix="¥" />
        </el-col>
        <el-col :span="8">
          <el-statistic title="剩余" :value="data.total_remaining" prefix="¥" />
        </el-col>
      </el-row>

      <el-table :data="data.items">
        <el-table-column prop="category_name" label="分类" width="150" />
        <el-table-column prop="budget" label="预算" width="120">
          <template #default="{ row }">¥{{ row.budget.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="actual" label="实际" width="120">
          <template #default="{ row }">¥{{ row.actual.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="进度">
          <template #default="{ row }">
            <el-progress :percentage="Math.min(row.ratio * 100, 100)" :status="row.status === 'exceeded' ? 'exception' : row.status === 'warning' ? 'warning' : 'success'" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="showEditDialog(row)">设置预算</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="editVisible" title="设置预算" width="400px">
      <el-form label-width="60px">
        <el-form-item label="金额">
          <el-input-number v-model="editAmount" :min="0" :precision="2" :step="100" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { budgetApi } from '@/api/budget'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'
import type { BudgetResponse } from '@/types'

const yearMonth = ref(dayjs().format('YYYY-MM'))
const data = ref<BudgetResponse | null>(null)
const editVisible = ref(false)
const editCategoryId = ref('')
const editAmount = ref(0)

async function fetchData() {
  const res = await budgetApi.get(yearMonth.value)
  data.value = res.data
}

function showEditDialog(row: any) {
  editCategoryId.value = row.category_id
  editAmount.value = row.budget
  editVisible.value = true
}

async function handleSave() {
  await budgetApi.set({ year_month: yearMonth.value, items: [{ category_id: editCategoryId.value, amount: editAmount.value }] })
  ElMessage.success('保存成功')
  editVisible.value = false
  fetchData()
}

onMounted(fetchData)
</script>
