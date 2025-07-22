import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface User {
  id: string
  username: string
  email: string
  balance: number
  borrow_times: number
  avatar?: string
  isAdmin?: boolean
  chips?: number
  level?: number
  winRate?: number
  totalGames?: number
}

const API_BASE_URL = 'http://localhost:8000'

export const useUserStore = defineStore('user', () => {
  const currentUser = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('token'))
  const isLoggedIn = computed(() => currentUser.value !== null && token.value !== null)
  const isAdmin = computed(() => currentUser.value?.isAdmin || false)

  // API请求头
  const getAuthHeaders = () => ({
    'Content-Type': 'application/json',
    'Authorization': token.value ? `Bearer ${token.value}` : ''
  })

  const login = async (username: string, password: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || '登录失败')
      }

      const data = await response.json()
      
      // 保存token和用户信息
      token.value = data.token
      currentUser.value = {
        id: data.user.id.toString(),
        username: data.user.username,
        email: data.user.email,
        balance: data.user.balance,
        borrow_times: data.user.borrow_times,
        isAdmin: data.user.is_admin,
        avatar: `https://trae-api-sg.mchost.guru/api/ide/v1/text_to_image?prompt=${encodeURIComponent(data.user.is_admin ? 'professional casino manager avatar portrait' : 'poker player avatar portrait')}&image_size=square`,
        chips: data.user.balance || 10000, // 使用balance作为chips，或默认10000
        level: data.user.level || 1,
        winRate: data.user.win_rate || 0,
        totalGames: data.user.total_games || 0
      }
      
      localStorage.setItem('token', data.token)
      localStorage.setItem('user', JSON.stringify(currentUser.value))
      
      return { success: true, user: currentUser.value }
    } catch (error) {
      console.error('Login error:', error)
      return { success: false, message: error instanceof Error ? error.message : '登录失败' }
    }
  }

  const register = async (userData: { username: string; email: string; password: string }) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || '注册失败')
      }

      const data = await response.json()
      
      // 注册成功后自动登录
      return await login(userData.username, userData.password)
    } catch (error) {
      console.error('Register error:', error)
      return { success: false, message: error instanceof Error ? error.message : '注册失败' }
    }
  }

  const logout = () => {
    // 断开WebSocket连接
    import('../utils/websocket').then(({ disconnectWebSocket }) => {
      disconnectWebSocket()
    })
    
    currentUser.value = null
    token.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  const updateBalance = (amount: number) => {
    if (currentUser.value) {
      currentUser.value.balance += amount
      localStorage.setItem('user', JSON.stringify(currentUser.value))
    }
  }

  const updateChips = (chips: number) => {
    if (currentUser.value) {
      currentUser.value.chips = chips
      currentUser.value.balance = chips // 同步更新balance
      localStorage.setItem('user', JSON.stringify(currentUser.value))
    }
  }

  const borrowChips = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/user/borrow`, {
        method: 'POST',
        headers: getAuthHeaders(),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || '借码失败')
      }

      const data = await response.json()
      
      if (currentUser.value) {
        currentUser.value.balance = data.balance
        currentUser.value.borrow_times = data.borrow_times
        localStorage.setItem('user', JSON.stringify(currentUser.value))
      }
      
      return { success: true, data }
    } catch (error) {
      console.error('Borrow chips error:', error)
      throw error
    }
  }

  const initFromStorage = () => {
    const storedUser = localStorage.getItem('user')
    if (storedUser && token.value) {
      try {
        currentUser.value = JSON.parse(storedUser)
      } catch (error) {
        console.error('Failed to parse stored user:', error)
        logout()
      }
    }
  }

  // 为了向后兼容，添加user别名
  const user = computed(() => currentUser.value)

  return {
    currentUser,
    user,
    token,
    isLoggedIn,
    isAdmin,
    login,
    register,
    logout,
    updateBalance,
    updateChips,
    borrowChips,
    initFromStorage
  }
})