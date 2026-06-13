import request from './request'
import type { ApiResponse, Family, FamilyMember } from '@/types'

export const familyApi = {
  getCurrent() {
    return request.get('/families/current') as Promise<ApiResponse<Family>>
  },
  updateCurrent(data: { name: string }) {
    return request.put('/families/current', data) as Promise<ApiResponse<Family>>
  },
  join(invite_code: string) {
    return request.post('/families/join', { invite_code }) as Promise<ApiResponse<null>>
  },
  listMembers() {
    return request.get('/families/current/members') as Promise<ApiResponse<FamilyMember[]>>
  },
  updateMember(id: string, data: { display_name?: string; role?: string }) {
    return request.put(`/families/current/members/${id}`, data) as Promise<ApiResponse<null>>
  },
  removeMember(id: string) {
    return request.delete(`/families/current/members/${id}`) as Promise<ApiResponse<null>>
  },
}
