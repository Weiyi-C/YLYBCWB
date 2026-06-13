<template>
  <el-container class="app-layout">
    <el-aside :width="app.sidebarCollapsed ? '64px' : '220px'" class="sidebar">
      <div class="logo">
        <h2 v-if="!app.sidebarCollapsed">家庭记账</h2>
        <h2 v-else>记</h2>
      </div>
      <el-menu :default-active="route.path" router :collapse="app.sidebarCollapsed">
        <el-menu-item index="/">
          <el-icon><Odometer /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>
        <el-menu-item index="/transactions">
          <el-icon><List /></el-icon>
          <span>交易记录</span>
        </el-menu-item>
        <el-menu-item index="/transactions/add">
          <el-icon><Plus /></el-icon>
          <span>记一笔</span>
        </el-menu-item>
        <el-menu-item index="/budgets">
          <el-icon><DataAnalysis /></el-icon>
          <span>预算管理</span>
        </el-menu-item>
        <el-sub-menu index="reports">
          <template #title>
            <el-icon><TrendCharts /></el-icon>
            <span>报表分析</span>
          </template>
          <el-menu-item index="/reports/monthly">月度报表</el-menu-item>
          <el-menu-item index="/reports/category">分类报表</el-menu-item>
          <el-menu-item index="/reports/trend">趋势分析</el-menu-item>
        </el-sub-menu>
        <el-menu-item index="/categories">
          <el-icon><Grid /></el-icon>
          <span>分类管理</span>
        </el-menu-item>
        <el-menu-item index="/settings">
          <el-icon><Setting /></el-icon>
          <span>系统设置</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <el-icon class="toggle-btn" @click="app.toggleSidebar"><Fold v-if="!app.sidebarCollapsed" /><Expand v-else /></el-icon>
          <span class="family-name">{{ auth.familyName }}</span>
        </div>
        <div class="header-right">
          <el-dropdown>
            <span class="user-info">
              <el-avatar :size="32" :src="auth.user?.avatar_url">{{ auth.user?.nickname?.[0] || 'U' }}</el-avatar>
              <span class="username">{{ auth.user?.nickname || auth.user?.username }}</span>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="$router.push('/settings')">个人设置</el-dropdown-item>
                <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useAppStore } from '@/stores/app'
import { useCategoryStore } from '@/stores/category'
import { authApi } from '@/api/auth'
import { onMounted } from 'vue'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const app = useAppStore()
const categoryStore = useCategoryStore()

onMounted(() => {
  categoryStore.fetchCategories().catch(() => {})
})

async function handleLogout() {
  try {
    await authApi.logout(auth.refreshToken)
  } catch {}
  auth.logout()
  router.push('/login')
}
</script>

<style scoped lang="scss">
.app-layout {
  height: 100vh;
}
.sidebar {
  background: #fff;
  border-right: 1px solid #e4e7ed;
  transition: width 0.3s;
  overflow: hidden;
  .logo {
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-bottom: 1px solid #e4e7ed;
    h2 { font-size: 18px; color: #409eff; }
  }
  .el-menu { border-right: none; }
}
.header {
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  .header-left {
    display: flex;
    align-items: center;
    gap: 16px;
    .toggle-btn { font-size: 20px; cursor: pointer; }
    .family-name { font-weight: 600; color: #303133; }
  }
  .header-right {
    .user-info {
      display: flex;
      align-items: center;
      gap: 8px;
      cursor: pointer;
      .username { font-size: 14px; }
    }
  }
}
.main-content {
  background: #f5f7fa;
  padding: 20px;
  overflow-y: auto;
}
</style>
