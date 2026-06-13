<template>
  <div>
    <div class="page-header"><h2>系统设置</h2></div>

    <el-row :gutter="16">
      <el-col :xs="24" :lg="12">
        <div class="card">
          <h3>个人信息</h3>
          <el-form :model="userForm" label-width="80px" style="margin-top: 16px">
            <el-form-item label="用户名">
              <el-input :model-value="auth.user?.username" disabled />
            </el-form-item>
            <el-form-item label="昵称">
              <el-input v-model="userForm.nickname" />
            </el-form-item>
            <el-form-item label="手机号">
              <el-input v-model="userForm.phone" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveUser">保存</el-button>
            </el-form-item>
          </el-form>
        </div>

        <div class="card">
          <h3>修改密码</h3>
          <el-form :model="pwForm" label-width="80px" style="margin-top: 16px">
            <el-form-item label="旧密码">
              <el-input v-model="pwForm.old_password" type="password" show-password />
            </el-form-item>
            <el-form-item label="新密码">
              <el-input v-model="pwForm.new_password" type="password" show-password />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="changePassword">修改密码</el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-col>

      <el-col :xs="24" :lg="12">
        <div class="card">
          <h3>家庭信息</h3>
          <el-form label-width="80px" style="margin-top: 16px">
            <el-form-item label="家庭名称">
              <el-input v-model="familyName" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveFamily">保存</el-button>
            </el-form-item>
            <el-form-item label="邀请码">
              <el-input :model-value="family?.invite_code" disabled>
                <template #append>
                  <el-button @click="copyInviteCode">复制</el-button>
                </template>
              </el-input>
            </el-form-item>
          </el-form>
        </div>

        <div class="card">
          <h3>家庭成员</h3>
          <el-table :data="members" size="small" style="margin-top: 16px">
            <el-table-column prop="display_name" label="昵称" />
            <el-table-column prop="role" label="角色" width="80">
              <template #default="{ row }">
                <el-tag :type="row.role === 'owner' ? 'danger' : 'info'" size="small">{{ row.role }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { userApi } from '@/api/user'
import { familyApi } from '@/api/family'
import { authApi } from '@/api/auth'
import { ElMessage } from 'element-plus'
import type { Family, FamilyMember } from '@/types'

const auth = useAuthStore()
const userForm = reactive({ nickname: auth.user?.nickname || '', phone: '' })
const pwForm = reactive({ old_password: '', new_password: '' })
const family = ref<Family | null>(null)
const familyName = ref('')
const members = ref<FamilyMember[]>([])

async function saveUser() {
  await userApi.updateMe(userForm)
  ElMessage.success('保存成功')
}

async function changePassword() {
  if (!pwForm.old_password || !pwForm.new_password) return ElMessage.warning('请填写完整')
  await authApi.changePassword(pwForm)
  ElMessage.success('密码已修改')
  pwForm.old_password = ''
  pwForm.new_password = ''
}

async function saveFamily() {
  if (!familyName.value) return
  await familyApi.updateCurrent({ name: familyName.value })
  ElMessage.success('保存成功')
}

function copyInviteCode() {
  if (family.value?.invite_code) {
    navigator.clipboard.writeText(family.value.invite_code)
    ElMessage.success('已复制')
  }
}

onMounted(async () => {
  const [f, m] = await Promise.all([familyApi.getCurrent(), familyApi.listMembers()])
  family.value = f.data
  familyName.value = f.data.name
  members.value = m.data
})
</script>
