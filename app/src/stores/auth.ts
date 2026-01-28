import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null as null | { username: string; email: string })
  const token = ref<string | null>(null)
  const isAuthenticated = ref(false)

  function login(userData: { username: string; email: string }, authToken: string) {
    user.value = userData
    token.value = authToken
    isAuthenticated.value = true
    // Optionally: persist token in localStorage
  }

  function logout() {
    user.value = null
    token.value = null
    isAuthenticated.value = false
    // Optionally: remove token from localStorage
  }

  return { user, token, isAuthenticated, login, logout }
})
