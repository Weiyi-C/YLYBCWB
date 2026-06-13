<template>
  <div>
    <div class="page-header">
      <h2>月度报表</h2>
      <el-date-picker v-model="year" type="year" value-format="YYYY" @change="fetchData" />
    </div>

    <div class="card">
      <div ref="chartRef" style="height: 400px"></div>
    </div>

    <div class="card">
      <el-table :data="data">
        <el-table-column prop="month" label="月份" width="100" />
        <el-table-column prop="income" label="收入" width="120">
          <template #default="{ row }"><span class="amount-positive">¥{{ row.income }}</span></template>
        </el-table-column>
        <el-table-column prop="expense" label="支出" width="120">
          <template #default="{ row }"><span class="amount-negative">¥{{ row.expense }}</span></template>
        </el-table-column>
        <el-table-column prop="balance" label="结余" width="120">
          <template #default="{ row }"><span :class="row.balance >= 0 ? 'amount-positive' : 'amount-negative'">¥{{ row.balance }}</span></template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import { reportApi } from '@/api/report'
import dayjs from 'dayjs'
import type { MonthlySummaryItem } from '@/types'

const year = ref(dayjs().format('YYYY'))
const data = ref<MonthlySummaryItem[]>([])
const chartRef = ref<HTMLElement>()

async function fetchData() {
  const res = await reportApi.monthlySummary(Number(year.value))
  data.value = res.data
  renderChart()
}

function renderChart() {
  if (!chartRef.value) return
  const chart = echarts.init(chartRef.value)
  chart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['收入', '支出', '结余'] },
    xAxis: { type: 'category', data: data.value.map((i) => i.month) },
    yAxis: { type: 'value' },
    series: [
      { name: '收入', type: 'bar', data: data.value.map((i) => i.income) },
      { name: '支出', type: 'bar', data: data.value.map((i) => i.expense) },
      { name: '结余', type: 'line', data: data.value.map((i) => i.balance) },
    ],
  })
}

onMounted(fetchData)
</script>
