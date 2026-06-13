import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Family, FamilyMember } from '@/types'
import { familyApi } from '@/api/family'

export const useFamilyStore = defineStore('family', () => {
  const family = ref<Family | null>(null)
  const members = ref<FamilyMember[]>([])

  async function fetchFamily() {
    const res = await familyApi.getCurrent()
    family.value = res.data
  }

  async function fetchMembers() {
    const res = await familyApi.listMembers()
    members.value = res.data
  }

  return { family, members, fetchFamily, fetchMembers }
})
