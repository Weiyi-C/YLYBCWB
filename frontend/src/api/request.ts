import axios from 'axios'
import type { ApiResponse } from '@/types'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'

const request = axios.create({
  baseURL: '/api/v1',
  timeout: 15000,
})

request.interceptors.request.use((config) => {
  const auth = useAuthStore()
  if (auth.accessToken) {
    config.headers.Authorization = `Bearer ${auth.accessToken}`
  }
  return config
})

request.interceptors.response.use(
  (response) => response.data,
  async (error) => {
    const originalRequest = error.config
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      const auth = useAuthStore()
      try {
        const { data } = await axios.post('/api/v1/auth/refresh', {
          refresh_token: auth.refreshToken,
        })
        auth.setTokens(data.data.access_token, data.data.refresh_token)
        originalRequest.headers.Authorization = `Bearer ${data.data.access_token}`
        return request(originalRequest)
      } catch {
        auth.logout()
        router.push('/login')
      }
    }
    return Promise.reject(error)
  }
)

export default request
