<template>
  <div>
    <div class="page-header">
      <h2>分类报表</h2>
      <el-date-picker v-model="yearMonth" type="month" value-format="YYYY-MM" @change="fetchData" />
    </div>

    <el-row :gutter="16">
      <el-col :xs="24" :lg="12">
        <div class="card">
          <div ref="pieChartRef" style="height: 400px"></div>
        </div>
      </el-col>
      <el-col :xs="24" :lg="12">
        <div class="card">
          <el-table :data="data">
            <el-table-column prop="category_name" label="分类" />
            <el-table-column prop="amount" label="金额" width="120">
              <template #default="{ row }">¥{{ row.amount }}</template>
            </el-table-column>
            <el-table-column label="占比" width="80">
              <template #default="{ row }">{{ (row.ratio * 100).toFixed(1) }}%</template>
            </el-table-column>
            <el-table-column prop="count" label="笔数" width="60" />
          </el-table>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import { reportApi } from '@/api/report'
import dayjs from 'dayjs'
import type { CategoryBreakdownItem } from '@/types'

const yearMonth = ref(dayjs().format('YYYY-MM'))
const data = ref<CategoryBreakdownItem[]>([])
const pieChartRef = ref<HTMLElement>()

async function fetchData() {
  const res = await reportApi.categoryBreakdown(yearMonth.value)
  data.value = res.data
  renderChart()
}

function renderChart() {
  if (!pieChartRef.value) return
  const chart = echarts.init(pieChartRef.value)
  chart.setOption({
    tooltip: { trigger: 'item' },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      data: data.value.map((i) => ({ name: i.category_name, value: Number(i.amount) })),
      label: { formatter: '{b}: {d}%' },
    }],
  })
}

onMounted(fetchData)
</script>
