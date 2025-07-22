import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useUserStore } from './user'

export interface Room {
  id: string | number
  name: string
  current_players: number
  max_players: number
  small_blind: number
  big_blind: number
  min_buy_in?: number
  max_buy_in?: number
  status: 'waiting' | 'playing' | 'full'
  isPrivate?: boolean
  password?: string
  created_at?: string
  created_by?: number
  // 兼容旧字段名
  playerCount?: number
  maxPlayers?: number
  smallBlind?: number
  bigBlind?: number
  minBuyIn?: number
  maxBuyIn?: number
}

const API_BASE_URL = 'http://localhost:8000'

export const useRoomStore = defineStore('room', () => {
  const rooms = ref<Room[]>([])
  const currentRoom = ref<Room | null>(null)
  const isInRoom = computed(() => !!currentRoom.value)

  const userStore = useUserStore()

  // API请求头
  const getAuthHeaders = () => ({
    'Content-Type': 'application/json',
    'Authorization': userStore.token ? `Bearer ${userStore.token}` : ''
  })

  const loadRooms = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/rooms`, {
        headers: getAuthHeaders()
      })
      
      if (response.ok) {
        rooms.value = await response.json()
      } else {
        console.error('Failed to load rooms:', response.statusText)
        rooms.value = []
      }
    } catch (error) {
      console.error('Error loading rooms:', error)
      rooms.value = []
    }
  }

  const joinRoom = async (roomId: string, password?: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/rooms/${roomId}/join`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ password: password || '' }),
      })

      if (response.ok) {
        const roomData = await response.json()
        currentRoom.value = roomData.room
        // 重新加载房间列表以更新状态
        await loadRooms()
        return { success: true, message: '成功加入房间' }
      } else {
        const errorData = await response.json()
        return { success: false, message: errorData.detail || '加入房间失败' }
      }
    } catch (error) {
      console.error('Join room error:', error)
      return { success: false, message: '网络错误，加入房间失败' }
    }
  }

  const leaveRoom = async () => {
    if (!currentRoom.value) return { success: false, message: '当前不在房间中' }

    try {
      const response = await fetch(`${API_BASE_URL}/api/rooms/${currentRoom.value.id}/leave`, {
        method: 'POST',
        headers: getAuthHeaders()
      })

      if (response.ok) {
        currentRoom.value = null
        // 重新加载房间列表以更新状态
        await loadRooms()
        return { success: true, message: '成功离开房间' }
      } else {
        const errorData = await response.json()
        return { success: false, message: errorData.detail || '离开房间失败' }
      }
    } catch (error) {
      console.error('Leave room error:', error)
      // 即使API调用失败，也清除本地状态
      currentRoom.value = null
      return { success: true, message: '已离开房间' }
    }
  }

  const createRoom = async (roomData: {
    name: string
    small_blind?: number
    big_blind?: number
    max_players?: number
    isPrivate?: boolean
    password?: string
    // 兼容旧字段名
    smallBlind?: number
    bigBlind?: number
    maxPlayers?: number
  }) => {
    try {
      // 转换字段名以匹配后端API
      const apiData = {
        name: roomData.name,
        small_blind: roomData.small_blind || roomData.smallBlind || 10,
        big_blind: roomData.big_blind || roomData.bigBlind || 20,
        max_players: roomData.max_players || roomData.maxPlayers || 6
      }
      
      const response = await fetch(`${API_BASE_URL}/api/rooms`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(apiData),
      })

      if (response.ok) {
        const newRoom = await response.json()
        // 重新加载房间列表以获取最新状态
        await loadRooms()
        return { success: true, room: newRoom, message: '房间创建成功' }
      } else {
        const errorData = await response.json()
        return { success: false, message: errorData.detail || '创建房间失败' }
      }
    } catch (error) {
      console.error('Create room error:', error)
      return { success: false, message: '网络错误，创建房间失败' }
    }
  }

  const deleteRoom = async (roomId: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/rooms/${roomId}`, {
        method: 'DELETE',
        headers: getAuthHeaders()
      })

      if (response.ok) {
        // 重新加载房间列表
        await loadRooms()
        return { success: true, message: '房间删除成功' }
      } else {
        const errorData = await response.json()
        return { success: false, message: errorData.detail || '删除房间失败' }
      }
    } catch (error) {
      console.error('Delete room error:', error)
      return { success: false, message: '网络错误，删除房间失败' }
    }
  }

  const quickMatch = async (preferredBlind?: number) => {
    // 寻找合适的房间进行快速匹配
    const availableRooms = rooms.value.filter(room => 
      room.status !== 'full' && 
      !room.isPrivate &&
      (!preferredBlind || (room.big_blind || room.bigBlind || 0) <= preferredBlind * 2)
    )

    if (availableRooms.length === 0) {
      return { success: false, message: '暂无合适的房间' }
    }

    // 选择人数最多的房间
    const bestRoom = availableRooms.reduce((best, current) => {
      const currentPlayers = current.current_players || current.playerCount || 0
      const bestPlayers = best.current_players || best.playerCount || 0
      return currentPlayers > bestPlayers ? current : best
    })

    return await joinRoom(bestRoom.id.toString())
  }

  return {
    rooms,
    currentRoom,
    isInRoom,
    loadRooms,
    joinRoom,
    leaveRoom,
    createRoom,
    deleteRoom,
    quickMatch
  }
})