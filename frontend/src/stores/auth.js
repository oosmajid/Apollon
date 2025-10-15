// src/stores/auth.js
import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { useRouter } from 'vue-router'

export const useAuthStore = defineStore('auth', () => {
  const router = useRouter()
  
  // State
  const accessToken = ref(localStorage.getItem('accessToken'))
  const refreshToken = ref(localStorage.getItem('refreshToken'))
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  
  // Getters
  const isAuthenticated = computed(() => {
    return !!accessToken.value
  })
  
  const fullName = computed(() => {
    if (user.value && user.value.first_name && user.value.last_name) {
      return `${user.value.first_name} ${user.value.last_name}`.trim()
    }
    return 'کاربر'
  })
  
  // Actions
  function setTokens(access, refresh) {
    accessToken.value = access
    refreshToken.value = refresh
    localStorage.setItem('accessToken', access)
    localStorage.setItem('refreshToken', refresh)
  }
  
  function setUser(userData) {
    user.value = userData
    if (userData) {
      localStorage.setItem('user', JSON.stringify(userData))
    } else {
      localStorage.removeItem('user')
    }
  }
  
  function logout() {
    accessToken.value = null
    refreshToken.value = null
    user.value = null
    localStorage.removeItem('accessToken')
    localStorage.removeItem('refreshToken')
    localStorage.removeItem('user')
    router.push({ name: 'login' })
  }
  
  function checkAuth() {
    const token = localStorage.getItem('accessToken')
    if (token) {
      accessToken.value = token
      
      // اگر توکن موجود است اما اطلاعات کاربر نیست، آن‌ها را بارگذاری کن
      if (!user.value) {
        loadUserFromToken()
      }
      
      return true
    }
    // Clear any stale tokens
    accessToken.value = null
    refreshToken.value = null
    return false
  }
  
  async function loadUserFromToken() {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/auth/me/', {
        headers: {
          'Authorization': `Bearer ${accessToken.value}`,
          'Content-Type': 'application/json'
        }
      })
      
      if (response.ok) {
        const userData = await response.json()
        setUser(userData)
      }
    } catch (error) {
      console.error('Failed to load user data:', error)
    }
  }
  
  return {
    // State
    accessToken,
    refreshToken,
    user,
    // Getters
    isAuthenticated,
    fullName,
    // Actions
    setTokens,
    setUser,
    logout,
    checkAuth
  }
})
