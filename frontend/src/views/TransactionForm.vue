<template>
  <div>
    <div class="page-header">
      <h2>{{ isEdit ? '编辑交易' : '记一笔' }}</h2>
    </div>

    <div class="card" style="max-width: 600px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="收支类型" prop="type">
          <el-radio-group v-model="form.type">
            <el-radio-button value="expense">支出</el-radio-button>
            <el-radio-button value="income">收入</el-radio-button>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="金额" prop="amount">
          <el-input-number v-model="form.amount" :min="0.01" :precision="2" :step="10" style="width: 100%" />
        </el-form-item>

        <el-form-item label="日期" prop="transaction_date">
          <el-date-picker v-model="form.transaction_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>

        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" placeholder="买了什么" />
        </el-form-item>

        <el-form-item label="大分类" prop="category_id">
          <el-select v-model="form.category_id" placeholder="选择分类" @change="onCategoryChange" style="width: 100%">
            <el-option v-for="c in currentCategories" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>

        <el-form-item label="小分类" prop="sub_category_id">
          <el-select v-model="form.sub_category_id" placeholder="选择小分类" style="width: 100%">
            <el-option v-for="s in currentSubCategories" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </el-form-item>

        <el-form-item label="交易对象">
          <el-input v-model="form.merchant" placeholder="商家/收款人" />
        </el-form-item>

        <el-form-item label="备注">
          <el-input v-model="form.notes" type="textarea" :rows="2" />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="loading" @click="handleSubmit">{{ isEdit ? '保存' : '记一笔' }}</el-button>
          <el-button @click="$router.back()">取消</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { transactionApi } from '@/api/transaction'
import { useCategoryStore } from '@/stores/category'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'
import type { Category } from '@/types'

const route = useRoute()
const router = useRouter()
const categoryStore = useCategoryStore()
const auth = useAuthStore()
const formRef = ref()
const loading = ref(false)
const isEdit = computed(() => !!route.params.id)

const form = reactive({
  type: 'expense',
  amount: 0,
  transaction_date: dayjs().format('YYYY-MM-DD'),
  description: '',
  category_id: '',
  sub_category_id: '',
  merchant: '',
  notes: '',
  member_id: '',
})

const rules = {
  type: [{ required: true }],
  amount: [{ required: true, message: '请输入金额' }],
  transaction_date: [{ required: true, message: '请选择日期' }],
  description: [{ required: true, message: '请输入描述' }],
  category_id: [{ required: true, message: '请选择分类' }],
  sub_category_id: [{ required: true, message: '请选择小分类' }],
}

const currentCategories = computed(() => {
  return form.type === 'expense' ? categoryStore.expenseCategories : categoryStore.incomeCategories
})

const currentSubCategories = computed(() => {
  const cat = currentCategories.value.find((c: Category) => c.id === form.category_id)
  return cat?.sub_categories?.filter((s) => s.is_active) || []
})

function onCategoryChange() {
  form.sub_category_id = ''
}

async function handleSubmit() {
  await formRef.value?.validate()
  loading.value = true
  try {
    if (isEdit.value) {
      await transactionApi.update(route.params.id as string, form)
      ElMessage.success('保存成功')
    } else {
      await transactionApi.create(form)
      ElMessage.success('记录成功')
    }
    router.push('/transactions')
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '操作失败')
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  if (isEdit.value) {
    try {
      const res = await transactionApi.get(route.params.id as string)
      Object.assign(form, res.data)
    } catch {
      ElMessage.error('交易记录不存在')
      router.back()
    }
  }
})
</script>
