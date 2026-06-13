<template>
  <div>
    <div class="page-header">
      <h2>分类管理</h2>
      <el-button type="primary" @click="showAddDialog">新增分类</el-button>
    </div>

    <el-tabs v-model="activeType">
      <el-tab-pane label="支出分类" name="expense" />
      <el-tab-pane label="收入分类" name="income" />
    </el-tabs>

    <div class="card">
      <el-table :data="filteredCategories">
        <el-table-column prop="name" label="名称" width="150" />
        <el-table-column prop="icon" label="图标" width="80" />
        <el-table-column label="子分类">
          <template #default="{ row }">
            <el-tag v-for="sub in row.sub_categories" :key="sub.id" size="small" style="margin: 2px">{{ sub.name }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_system" label="系统" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_system ? 'info' : 'success'" size="small">{{ row.is_system ? '是' : '否' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="showSubDialog(row)">添加子分类</el-button>
            <el-button link type="danger" size="small" :disabled="row.is_system" @click="handleDelete(row.id)">停用</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="addVisible" title="新增分类" width="400px">
      <el-form :model="addForm" label-width="60px">
        <el-form-item label="名称"><el-input v-model="addForm.name" /></el-form-item>
        <el-form-item label="图标"><el-input v-model="addForm.icon" placeholder="如 food" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addVisible = false">取消</el-button>
        <el-button type="primary" @click="handleAdd">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="subVisible" title="添加子分类" width="400px">
      <el-form :model="subForm" label-width="60px">
        <el-form-item label="名称"><el-input v-model="subForm.name" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="subVisible = false">取消</el-button>
        <el-button type="primary" @click="handleAddSub">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useCategoryStore } from '@/stores/category'
import { categoryApi } from '@/api/category'
import { ElMessage, ElMessageBox } from 'element-plus'

const categoryStore = useCategoryStore()
const activeType = ref('expense')
const addVisible = ref(false)
const subVisible = ref(false)
const currentCategoryId = ref('')
const addForm = reactive({ name: '', icon: '' })
const subForm = reactive({ name: '' })

const filteredCategories = computed(() => {
  return activeType.value === 'expense' ? categoryStore.expenseCategories : categoryStore.incomeCategories
})

function showAddDialog() {
  addForm.name = ''
  addForm.icon = ''
  addVisible.value = true
}

function showSubDialog(row: any) {
  currentCategoryId.value = row.id
  subForm.name = ''
  subVisible.value = true
}

async function handleAdd() {
  await categoryApi.create({ name: addForm.name, type: activeType.value, icon: addForm.icon })
  ElMessage.success('添加成功')
  addVisible.value = false
  categoryStore.fetchCategories()
}

async function handleAddSub() {
  await categoryApi.createSub(currentCategoryId.value, { name: subForm.name })
  ElMessage.success('添加成功')
  subVisible.value = false
  categoryStore.fetchCategories()
}

async function handleDelete(id: string) {
  await ElMessageBox.confirm('确定停用此分类？', '确认')
  await categoryApi.delete(id)
  ElMessage.success('已停用')
  categoryStore.fetchCategories()
}

onMounted(() => categoryStore.fetchCategories())
</script>
