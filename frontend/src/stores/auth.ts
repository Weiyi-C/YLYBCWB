import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref(localStorage.getItem('access_token') || '')
  const refreshToken = ref(localStorage.getItem('refresh_token') || '')
  const user = ref<any>(JSON.parse(localStorage.getItem('user') || 'null'))
  const familyId = ref(localStorage.getItem('family_id') || '')
  const familyName = ref(localStorage.getItem('family_name') || '')

  const isLoggedIn = computed(() => !!accessToken.value)

  function setTokens(access: string, refresh: string) {
    accessToken.value = access
    refreshToken.value = refresh
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)
  }

  function setLoginData(data: any) {
    setTokens(data.access_token, data.refresh_token)
    user.value = data.user
    familyId.value = data.family_id
    familyName.value = data.family_name
    localStorage.setItem('user', JSON.stringify(data.user))
    localStorage.setItem('family_id', data.family_id)
    localStorage.setItem('family_name', data.family_name)
  }

  function logout() {
    accessToken.value = ''
    refreshToken.value = ''
    user.value = null
    familyId.value = ''
    familyName.value = ''
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
    localStorage.removeItem('family_id')
    localStorage.removeItem('family_name')
  }

  return { accessToken, refreshToken, user, familyId, familyName, isLoggedIn, setTokens, setLoginData, logout }
})
