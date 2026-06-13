<template>
  <div>
    <div class="page-header"><h2>仪表盘</h2></div>

    <el-row :gutter="16" class="stat-cards">
      <el-col :xs="12" :sm="6">
        <div class="card stat-card income">
          <div class="label">本月收入</div>
          <div class="value">¥{{ formatAmount(overview?.month_income) }}</div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6">
        <div class="card stat-card expense">
          <div class="label">本月支出</div>
          <div class="value">¥{{ formatAmount(overview?.month_expense) }}</div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6">
        <div class="card stat-card balance">
          <div class="label">本月结余</div>
          <div class="value">¥{{ formatAmount(overview?.month_balance) }}</div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6">
        <div class="card stat-card reimburse">
          <div class="label">待报销</div>
          <div class="value">¥{{ formatAmount(overview?.pending_reimbursement) }}</div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="16">
      <el-col :xs="24" :lg="12">
        <div class="card">
          <h3>收支趋势</h3>
          <div ref="trendChartRef" style="height: 300px"></div>
        </div>
      </el-col>
      <el-col :xs="24" :lg="12">
        <div class="card">
          <h3>最近交易</h3>
          <el-table :data="recentList" size="small" max-height="280">
            <el-table-column prop="transaction_date" label="日期" width="100" />
            <el-table-column prop="description" label="描述" />
            <el-table-column prop="amount" label="金额" width="100">
              <template #default="{ row }">
                <span :class="row.type === 'expense' ? 'amount-negative' : 'amount-positive'">
                  {{ row.type === 'expense' ? '-' : '+' }}{{ row.amount }}
                </span>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import { dashboardApi } from '@/api/dashboard'
import { reportApi } from '@/api/report'
import type { DashboardOverview, Transaction, TrendItem } from '@/types'

const overview = ref<DashboardOverview | null>(null)
const recentList = ref<Transaction[]>([])
const trendChartRef = ref<HTMLElement>()
const trendData = ref<TrendItem[]>([])

function formatAmount(v?: number) {
  return (v ?? 0).toFixed(2)
}

onMounted(async () => {
  try {
    const [ov, recent, trend] = await Promise.all([
      dashboardApi.overview(),
      dashboardApi.recent(10),
      reportApi.trend(6),
    ])
    overview.value = ov.data
    recentList.value = recent.data
    trendData.value = trend.data
    renderChart()
  } catch {}
})

function renderChart() {
  if (!trendChartRef.value || !trendData.value.length) return
  const chart = echarts.init(trendChartRef.value)
  chart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['收入', '支出'] },
    xAxis: { type: 'category', data: trendData.value.map((i) => i.month) },
    yAxis: { type: 'value' },
    series: [
      { name: '收入', type: 'line', data: trendData.value.map((i) => i.income), smooth: true },
      { name: '支出', type: 'line', data: trendData.value.map((i) => i.expense), smooth: true },
    ],
  })
}
</script>

<style scoped lang="scss">
.stat-cards { margin-bottom: 16px; }
.stat-card {
  text-align: center;
  .label { font-size: 13px; color: #909399; margin-bottom: 8px; }
  .value { font-size: 24px; font-weight: 700; }
  &.income .value { color: #67c23a; }
  &.expense .value { color: #f56c6c; }
  &.balance .value { color: #409eff; }
  &.reimburse .value { color: #e6a23c; }
}
.card h3 { margin-bottom: 16px; font-size: 16px; }
</style>
