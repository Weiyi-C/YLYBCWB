<template>
  <div>
    <div class="page-header">
      <h2>趋势分析</h2>
      <el-select v-model="months" @change="fetchData" style="width: 120px">
        <el-option :value="6" label="近6个月" />
        <el-option :value="12" label="近12个月" />
        <el-option :value="24" label="近24个月" />
      </el-select>
    </div>

    <div class="card">
      <div ref="chartRef" style="height: 400px"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import { reportApi } from '@/api/report'
import type { TrendItem } from '@/types'

const months = ref(12)
const data = ref<TrendItem[]>([])
const chartRef = ref<HTMLElement>()

async function fetchData() {
  const res = await reportApi.trend(months.value)
  data.value = res.data
  renderChart()
}

function renderChart() {
  if (!chartRef.value) return
  const chart = echarts.init(chartRef.value)
  chart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['收入', '支出'] },
    xAxis: { type: 'category', data: data.value.map((i) => i.month) },
    yAxis: { type: 'value' },
    series: [
      { name: '收入', type: 'line', data: data.value.map((i) => i.income), smooth: true, areaStyle: {} },
      { name: '支出', type: 'line', data: data.value.map((i) => i.expense), smooth: true, areaStyle: {} },
    ],
  })
}

onMounted(fetchData)
</script>
