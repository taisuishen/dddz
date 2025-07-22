import { useUserStore } from '../stores/user'
import { useGameStore } from '../stores/game'
import { useRoomStore } from '../stores/room'

export interface WebSocketMessage {
  type: string
  data: any
}

class WebSocketService {
  private ws: WebSocket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectInterval = 3000
  private isConnecting = false
  private messageQueue: WebSocketMessage[] = []
  private currentToken: string | null = null

  constructor() {
    // 不在构造函数中初始化store，而是在需要时获取
  }

  private getStores() {
    return {
      userStore: useUserStore(),
      gameStore: useGameStore(),
      roomStore: useRoomStore()
    }
  }

  connect(token: string): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN && this.currentToken === token) {
        resolve()
        return
      }

      if (this.isConnecting) {
        reject(new Error('Already connecting'))
        return
      }

      this.isConnecting = true
      this.currentToken = token
      const wsUrl = `ws://localhost:8000/ws?token=${encodeURIComponent(token)}`
      
      try {
        this.ws = new WebSocket(wsUrl)
        
        this.ws.onopen = () => {
          console.log('WebSocket connected')
          this.isConnecting = false
          this.reconnectAttempts = 0
          
          // 发送队列中的消息
          while (this.messageQueue.length > 0) {
            const message = this.messageQueue.shift()
            if (message) {
              this.send(message)
            }
          }
          
          resolve()
        }

        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data)
            this.handleMessage(message)
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error)
          }
        }

        this.ws.onclose = (event) => {
          console.log('WebSocket disconnected:', event.code, event.reason)
          this.isConnecting = false
          this.ws = null
          
          // 如果不是主动关闭，尝试重连
          if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
            setTimeout(() => {
              this.reconnectAttempts++
              console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})`)
              this.connect(token).catch(console.error)
            }, this.reconnectInterval)
          }
        }

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error)
          this.isConnecting = false
          reject(error)
        }
      } catch (error) {
        this.isConnecting = false
        reject(error)
      }
    })
  }

  disconnect() {
    if (this.ws) {
      this.ws.close(1000, 'User disconnected')
      this.ws = null
    }
    this.messageQueue = []
    this.currentToken = null
  }

  send(message: WebSocketMessage) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message))
    } else {
      // 如果连接未建立，将消息加入队列
      this.messageQueue.push(message)
    }
  }

  // 游戏动作
  sendGameAction(roomId: number, action: string, amount: number = 0) {
    const { userStore } = this.getStores()
    const playerId = userStore.user?.id
    
    if (!playerId) {
      console.error('Cannot send game action: user not logged in')
      return
    }
    
    this.send({
      type: 'game_action',
      data: {
        room_id: roomId,
        action,
        amount,
        player_id: playerId
      }
    })
  }

  // 加入房间
  joinRoom(roomId: number) {
    this.send({
      type: 'join_room',
      data: {
        room_id: roomId
      }
    })
  }

  // 离开房间
  leaveRoom(roomId: number) {
    this.send({
      type: 'leave_room',
      data: {
        room_id: roomId
      }
    })
  }

  // 发送聊天消息
  sendChatMessage(roomId: number, message: string) {
    this.send({
      type: 'chat',
      data: {
        room_id: roomId,
        message
      }
    })
  }

  // 开始游戏
  startGame(roomId: number) {
    this.send({
      type: 'start_game',
      data: {
        room_id: roomId
      }
    })
  }

  // 心跳包
  ping() {
    this.send({
      type: 'ping',
      data: {}
    })
  }

  // 展示手牌
  showCards(roomId: number) {
    const { userStore } = this.getStores()
    const playerId = userStore.user?.id
    
    if (!playerId) {
      console.error('Cannot show cards: user not logged in')
      return
    }
    
    this.send({
      type: 'show_cards',
      data: {
        room_id: roomId,
        player_id: playerId
      }
    })
  }

  private handleMessage(message: WebSocketMessage) {
    console.log('Received WebSocket message:', message)
    
    try {
      const { gameStore } = this.getStores()
      
      switch (message.type) {
        case 'game_state':
          // 详细调试game_state消息
          console.log('[DEBUG] WebSocket game_state 原始消息:', JSON.stringify(message.data, null, 2))
          console.log('[DEBUG] current_player 字段值:', message.data?.current_player)
          console.log('[DEBUG] current_player 类型:', typeof message.data?.current_player)
          
          // 更新游戏状态
          if (message.data) {
            gameStore.updateGameStateFromAPI(message.data)
          }
          break
          
        case 'game_action':
          // 处理游戏动作结果
          console.log('Game action result:', message.data)
          // 游戏动作后会收到单独的game_state消息进行状态更新
          break
          
        case 'game_started':
          console.log('Game started:', message.data)
          break
          
        case 'player_joined':
          console.log('Player joined:', message.data)
          break
          
        case 'player_left':
          console.log('Player left:', message.data)
          break
          
        case 'chat_message':
          // 处理聊天消息
          console.log('Chat message:', message.data)
          break
          
        case 'show_cards':
          // 处理展示手牌消息
          console.log('Show cards:', message.data)
          if (message.data && message.data.player_id) {
            // 更新玩家展示手牌状态
            gameStore.updatePlayerShowCards(message.data.player_id, true)
            
            // 如果有手牌数据，也可以在这里处理
            if (message.data.cards) {
              console.log('Player cards:', message.data.cards)
            }
          }
          break
          
        case 'game_results':
          // 处理游戏结果消息
          console.log('Game results:', message.data)
          if (message.data) {
            gameStore.setGameResults(message.data)
          }
          break
          
        case 'error':
          console.error('WebSocket error:', message.data)
          break
          
        case 'pong':
          // 心跳响应
          break
          
        default:
          console.log('Unknown message type:', message.type)
      }
    } catch (error) {
      console.error('Error handling WebSocket message:', error)
    }
  }

  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN
  }

  getCurrentToken(): string | null {
    return this.currentToken
  }
}

// 全局WebSocket服务实例
export const websocketService = new WebSocketService()

// 自动连接函数
export const connectWebSocket = async () => {
  try {
    const userStore = useUserStore()
    if (userStore.token) {
      // 检查是否需要重新连接（token变化或无连接）
      const needReconnect = !websocketService.isConnected() || 
                           websocketService.getCurrentToken() !== userStore.token
      
      if (needReconnect) {
        if (websocketService.isConnected()) {
          console.log('Token changed, disconnecting existing WebSocket connection')
          websocketService.disconnect()
        }
        
        await websocketService.connect(userStore.token)
        console.log('WebSocket connected successfully')
      }
    } else {
      // 如果没有token，断开连接
      if (websocketService.isConnected()) {
        console.log('No token, disconnecting WebSocket')
        websocketService.disconnect()
      }
    }
  } catch (error) {
    console.error('Failed to connect WebSocket:', error)
  }
}

// 断开连接函数
export const disconnectWebSocket = () => {
  websocketService.disconnect()
  console.log('WebSocket disconnected')
}