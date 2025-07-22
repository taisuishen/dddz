import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface Card {
  suit: string // 花色符号：♥, ♦, ♣, ♠
  rank: number // 牌面值：2-14
  display?: string // 显示字符串（可选）
}

export interface Player {
  id: string
  username: string
  avatar: string
  chips: number
  currentBet: number
  cards: Card[]
  position: number
  isActive: boolean
  isFolded: boolean
  isAllIn: boolean
  isReady: boolean
  showCards?: boolean
  action?: 'fold' | 'call' | 'raise' | 'check' | 'all-in'
}

export interface GameState {
  id: string
  players: Player[]
  communityCards: Card[]
  pot: number
  currentBet: number
  currentPlayerIndex: number
  currentPlayerId: string | null
  phase: 'waiting' | 'preflop' | 'flop' | 'turn' | 'river' | 'showdown' | 'finished'
  smallBlind: number
  bigBlind: number
  dealerPosition: number
}

export interface GameResults {
  pot_amount: number
  winner_id: string
  results: Array<{
    user_id: string
    username: string
    hole_cards: Card[]
    hand_rank: string
    hand_rank_value: number
    hand_strength: number[]
    win_amount: number
    final_chips: number
    rank: number
  }>
}

export const useGameStore = defineStore('game', () => {
  const currentGame = ref<GameState | null>(null)
  const gameResults = ref<GameResults | null>(null)
  const isInGame = computed(() => !!currentGame.value)
  const currentPlayer = computed(() => {
    if (!currentGame.value) return null
    return currentGame.value.players[currentGame.value.currentPlayerIndex]
  })

  const joinGame = (gameData: GameState) => {
    currentGame.value = gameData
  }

  const leaveGame = () => {
    currentGame.value = null
  }

  const updateGameState = (newState: Partial<GameState>) => {
    if (currentGame.value) {
      Object.assign(currentGame.value, newState)
    }
  }

  const updatePlayer = (playerId: string, updates: Partial<Player>) => {
    if (currentGame.value) {
      const playerIndex = currentGame.value.players.findIndex(p => p.id === playerId)
      if (playerIndex !== -1) {
        Object.assign(currentGame.value.players[playerIndex], updates)
      }
    }
  }

  const addCommunityCard = (card: Card) => {
    if (currentGame.value) {
      currentGame.value.communityCards.push(card)
    }
  }

  const updatePot = (amount: number) => {
    if (currentGame.value) {
      currentGame.value.pot += amount
    }
  }

  const nextPlayer = () => {
    if (currentGame.value) {
      const activePlayers = currentGame.value.players.filter(p => !p.isFolded && !p.isAllIn)
      if (activePlayers.length > 1) {
        let nextIndex = (currentGame.value.currentPlayerIndex + 1) % currentGame.value.players.length
        while (currentGame.value.players[nextIndex].isFolded || currentGame.value.players[nextIndex].isAllIn) {
          nextIndex = (nextIndex + 1) % currentGame.value.players.length
        }
        currentGame.value.currentPlayerIndex = nextIndex
      }
    }
  }

  const nextPhase = () => {
    if (!currentGame.value) return
    
    const phases = ['waiting', 'preflop', 'flop', 'turn', 'river', 'showdown', 'finished'] as const
    const currentPhaseIndex = phases.indexOf(currentGame.value.phase)
    
    if (currentPhaseIndex < phases.length - 1) {
      currentGame.value.phase = phases[currentPhaseIndex + 1]
      // 重置当前下注
      currentGame.value.currentBet = 0
      currentGame.value.players.forEach(player => {
        player.currentBet = 0
      })
    }
  }

  const updateGameStateFromAPI = (apiData: any) => {
    try {
      console.log('收到API数据:', JSON.stringify(apiData, null, 2))
      
      // 转换API数据格式为前端游戏状态格式
      if (apiData.game || apiData.stage) {
        const gameData = apiData.game || apiData
        
        console.log('处理游戏数据:', JSON.stringify(gameData, null, 2))
        
        // 转换玩家数据格式 - 确保ID类型一致性
        const players = (gameData.players || []).map((p: any) => {
          // 统一处理ID，确保为字符串类型
          const playerId = String(p.user_id || p.id || '')
          const player = {
            id: playerId,
            username: p.username || '',
            avatar: p.avatar || `https://trae-api-sg.mchost.guru/api/ide/v1/text_to_image?prompt=poker%20player%20avatar&image_size=square`,
            chips: p.chips || 0,
            currentBet: p.current_bet || 0,
            position: p.position !== undefined ? p.position : -1,
            isActive: p.is_active !== false,
            isFolded: p.is_folded || false,
            isAllIn: p.is_all_in || false,
            isReady: p.is_ready || false,
            showCards: p.show_cards || false,
            action: p.action || 'waiting',
            cards: p.hole_cards || []
          }
          console.log(`转换玩家数据 - ID: ${playerId}, 筹码: ${player.chips}, 当前下注: ${player.currentBet}, 位置: ${player.position}`)
          return player
        })
        
        // 转换公共牌数据格式
        const communityCards = (gameData.community_cards || gameData.communityCards || []).map((c: any) => ({
          suit: c.suit || '♠',
          rank: c.rank || 2,
          display: c.display
        }))
        
        // 计算正确的currentPlayerIndex - 基于玩家数组索引而不是座位位置
        let currentPlayerIndex = 0
        let currentPlayerId = null
        
        console.log('[DEBUG] 处理当前玩家信息:')
        console.log('[DEBUG] gameData.current_player:', gameData.current_player)
        console.log('[DEBUG] gameData.current_player 类型:', typeof gameData.current_player)
        console.log('[DEBUG] 玩家数组:', players.map(p => ({ id: p.id, username: p.username, position: p.position })))
        
        if (gameData.current_player !== null && gameData.current_player !== undefined) {
          currentPlayerId = String(gameData.current_player)
          console.log('[DEBUG] 转换后的currentPlayerId:', currentPlayerId)
          console.log('[DEBUG] currentPlayerId 类型:', typeof currentPlayerId)
          
          // 详细打印每个玩家的ID进行对比
          console.log('[DEBUG] 开始查找玩家:')
          players.forEach((p, index) => {
            console.log(`[DEBUG] 玩家${index}: id="${p.id}" (类型: ${typeof p.id}), username="${p.username}"`)
            console.log(`[DEBUG] 比较结果: "${p.id}" === "${currentPlayerId}" = ${p.id === currentPlayerId}`)
          })
          
          const playerIndex = players.findIndex(p => p.id === currentPlayerId)
          console.log('[DEBUG] findIndex 结果:', playerIndex)
          
          if (playerIndex !== -1) {
            currentPlayerIndex = playerIndex
            console.log(`[DEBUG] ✅ 找到当前玩家: ID=${currentPlayerId}, 索引=${playerIndex}, 用户名=${players[playerIndex].username}`)
            console.log(`[DEBUG] 当前玩家完整信息:`, players[playerIndex])
          } else {
            console.warn(`[DEBUG] ❌ 警告: 未找到当前玩家ID "${currentPlayerId}" 在玩家数组中`)
            console.log('[DEBUG] 所有玩家ID列表:', players.map(p => `"${p.id}" (${typeof p.id})`).join(', '))
            // 设置为null以便前端能正确处理
            currentPlayerId = null
          }
        } else {
          console.log('[DEBUG] current_player 为空或未定义')
        }
        
        const gameState = {
          id: gameData.id || gameData.room_id?.toString() || '',
          players,
          communityCards,
          pot: gameData.pot || 0,
          currentBet: gameData.current_bet || gameData.currentBet || 0,
          currentPlayerIndex,
          currentPlayerId,
          phase: gameData.stage || gameData.phase || 'waiting',
          smallBlind: gameData.smallBlind || 10,
          bigBlind: gameData.bigBlind || 20,
          dealerPosition: gameData.dealerPosition || 0
        }
        
        console.log('构建的游戏状态:', {
          pot: gameState.pot,
          currentBet: gameState.currentBet,
          currentPlayerIndex: gameState.currentPlayerIndex,
          phase: gameState.phase,
          playersCount: gameState.players.length
        })
        
        // 强制更新游戏状态以确保响应性
        console.log('强制更新游戏状态以确保响应性')
        currentGame.value = gameState
        
        console.log('游戏状态已通过WebSocket更新')
        console.log('当前玩家:', currentGame.value.players[currentGame.value.currentPlayerIndex]?.username)
        console.log('所有玩家筹码:', currentGame.value.players.map(p => ({ name: p.username, chips: p.chips, bet: p.currentBet })))
      }
    } catch (error) {
      console.error('更新游戏状态失败:', error)
    }
  }

  const updatePlayerShowCards = (playerId: string, showCards: boolean) => {
    if (currentGame.value) {
      const player = currentGame.value.players.find(p => p.id === playerId)
      if (player) {
        player.showCards = showCards
      }
    }
  }

  const setGameResults = (results: GameResults) => {
    console.log('Setting game results:', results)
    gameResults.value = results
  }

  const clearGameResults = () => {
    gameResults.value = null
  }

  return {
    currentGame,
    gameResults,
    isInGame,
    currentPlayer,
    joinGame,
    leaveGame,
    updateGameState,
    updatePlayer,
    addCommunityCard,
    updatePot,
    nextPlayer,
    nextPhase,
    updateGameStateFromAPI,
    updatePlayerShowCards,
    setGameResults,
    clearGameResults
  }
})