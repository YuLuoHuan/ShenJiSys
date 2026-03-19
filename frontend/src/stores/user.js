// 用户状态管理（Pinia）
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUserStore = defineStore('user', () => {
  // 从 localStorage 恢复登录态
  const _saved = JSON.parse(localStorage.getItem('audit_user') || 'null')
  const user = ref(_saved)

  const isLoggedIn = computed(() => !!user.value)
  const isAdmin    = computed(() => user.value?.rolecode === 1)
  const isAuditor  = computed(() => user.value?.rolecode === 2)

  function setUser(u) {
    user.value = u
    localStorage.setItem('audit_user', JSON.stringify(u))
  }

  function logout() {
    user.value = null
    localStorage.removeItem('audit_user')
  }

  return { user, isLoggedIn, isAdmin, isAuditor, setUser, logout }
})

