<template>
  <div class="min-h-screen bg-gradient-to-br from-green-900 via-green-800 to-green-700 overflow-hidden">
    <!-- 顶部信息栏 -->
    <header class="bg-green-900/50 backdrop-blur-md border-b border-green-700 px-4 py-2">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <button
            @click="leaveGame"
            class="text-gray-300 hover:text-white transition-colors"
          >
            <ArrowLeft class="w-5 h-5" />
          </button>
          <div class="text-white">
            <span class="font-bold">{{ roomStore.currentRoom?.name }}</span>
            <span class="text-gray-300 ml-2">盲注: {{ roomStore.currentRoom?.smallBlind }}/{{ roomStore.currentRoom?.bigBlind }}</span>
          </div>
        </div>
        <div class="flex items-center space-x-4">
          <div class="text-yellow-500 font-bold">
            底池: {{ gameStore.currentGame?.pot.toLocaleString() || 0 }}
          </div>
          <div class="text-white">
            {{ userStore.user?.username }}
          </div>
        </div>
      </div>
    </header>

    <div class="h-[calc(100vh-60px)]">
      <!-- 主游戏区域 -->
      <div class="w-full h-full relative">
        <!-- 牌桌 -->
        <div class="absolute inset-0 flex items-center justify-center">
          <div class="relative">
            <!-- 椭圆形牌桌 -->
            <div class="w-[300px] h-[200px] md:w-[600px] md:h-[400px] bg-green-800 rounded-full border-4 md:border-8 border-yellow-600 shadow-2xl relative">
              <!-- 公共牌区域 -->
              <div class="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
                <!-- 所有公共牌显示在一行 -->
                <div class="flex space-x-2 mb-3 justify-center">
                  <!-- 已发的公共牌 -->
                  <div
                    v-for="(card, index) in communityCards"
                    :key="'community-' + index"
                    :class="getCardColor(card.suit)"
                    class="w-12 h-16 rounded-lg border-2 flex flex-col items-center justify-center text-xs font-bold shadow-lg transform hover:scale-105 transition-transform bg-white"
                  >
                    <div class="text-center leading-tight">
                      <div>{{ getDisplayRank(card.rank) }}</div>
                      <div class="text-lg">{{ getSuitSymbol(card.suit) }}</div>
                    </div>
                  </div>
                  
                  <!-- 未发牌的占位符 -->
                  <div 
                    v-for="i in Math.max(0, 5 - communityCards.length)" 
                    :key="'placeholder-' + i" 
                    class="w-12 h-16 bg-green-700/50 border-2 border-dashed border-green-500/50 rounded-lg flex items-center justify-center"
                  >
                    <span class="text-green-400 text-xs">?</span>
                  </div>
                </div>
                
                <!-- 底池显示 -->
                <div class="text-center mt-4">
                  <div class="bg-yellow-500 text-green-900 px-4 py-2 rounded-full font-bold text-lg shadow-lg">
                    底池: {{ gameStore.currentGame?.pot.toLocaleString() || 0 }}
                  </div>
                </div>
              </div>

              <!-- 玩家位置 -->
              <div
                v-for="index in maxSeats"
                :key="index"
                :class="getPlayerPositionClass(index - 1, maxSeats)"
                :style="getPlayerPositionStyle(index - 1, maxSeats)"
                class="absolute"
              >
                <PlayerSeat
                  :player="getPlayerAtSeat(index - 1)"
                  :seat-index="index - 1"
                  :is-current="isCurrentPlayerAtSeat(index - 1)"
                  :is-dealer="isDealerAtSeat(index - 1)"
                  @seat-click="handleSeatClick"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- 游戏阶段指示器 -->
        <div class="absolute top-4 left-4">
          <div class="bg-white/10 backdrop-blur-md rounded-lg px-4 py-2 border border-white/20">
            <div class="text-white font-bold">
              {{ getPhaseText(gameStore.currentGame?.phase) }}
            </div>
          </div>
        </div>

        <!-- 操作按钮区域 -->
        <div class="absolute bottom-4 left-1/2 transform -translate-x-1/2 w-full max-w-4xl px-4">
          <!-- 游戏未开始时显示准备按钮 -->
          <div v-if="gameStore.currentGame?.phase === 'waiting'" class="flex flex-col md:flex-row space-y-2 md:space-y-0 md:space-x-4 justify-center">
            <!-- 只有当用户在游戏中时才显示准备按钮 - 确保ID类型匹配 -->
            <template v-if="gameStore.currentGame.players.find(p => p.id === String(userStore.user?.id))">
              <button
                v-if="!isPlayerReady"
                @click="toggleReady"
                class="bg-green-600 hover:bg-green-500 text-white font-bold py-3 px-6 rounded-xl transition-all shadow-lg"
              >
                准备
              </button>
              <button
                v-else
                @click="toggleReady"
                class="bg-yellow-600 hover:bg-yellow-500 text-white font-bold py-3 px-6 rounded-xl transition-all shadow-lg"
              >
                取消准备
              </button>
            </template>

          </div>
          
          <!-- 游戏进行中的操作按钮 -->
          <div v-else-if="isMyTurn" class="flex flex-col md:flex-row space-y-2 md:space-y-0 md:space-x-4 justify-center">
            <!-- 弃牌 -->
            <button
              @click="fold"
              class="bg-red-600 hover:bg-red-500 text-white font-bold py-3 px-6 rounded-xl transition-all shadow-lg"
            >
              弃牌
            </button>
            
            <!-- 跟注/过牌 -->
            <button
              @click="callOrCheck"
              :class="[
                'font-bold py-3 px-6 rounded-xl transition-all shadow-lg',
                needToCall ? 'bg-yellow-600 hover:bg-yellow-500 text-white' : 'bg-green-600 hover:bg-green-500 text-white'
              ]"
            >
              {{ needToCall ? `跟注 ${callAmount}` : '过牌' }}
            </button>
            
            <!-- 加注 -->
            <div class="flex flex-col md:flex-row items-center space-y-2 md:space-y-0 md:space-x-2">
              <button
                @click="raise"
                :disabled="raiseAmount < minRaise"
                class="bg-orange-600 hover:bg-orange-500 text-white font-bold py-3 px-6 rounded-xl transition-all shadow-lg disabled:opacity-50 disabled:cursor-not-allowed w-full md:w-auto"
              >
                加注
              </button>
              <input
                v-model.number="raiseAmount"
                type="number"
                :min="minRaise"
                :step="minRaise"
                :max="currentPlayerChips"
                class="w-full md:w-24 px-2 py-1 bg-white/20 border border-white/30 rounded text-white text-center focus:outline-none focus:ring-2 focus:ring-yellow-500"
                :placeholder="`加注: ${minRaise}的倍数`"
              />
            </div>
            
            <!-- 全下 -->
            <button
              @click="allIn"
              class="bg-purple-600 hover:bg-purple-500 text-white font-bold py-3 px-6 rounded-xl transition-all shadow-lg"
            >
              全下
            </button>
            
            <!-- 展示手牌 -->
            <button
              @click="showCards"
              class="bg-indigo-600 hover:bg-indigo-500 text-white font-bold py-3 px-6 rounded-xl transition-all shadow-lg"
            >
              展示手牌
            </button>
          </div>
          
          <!-- 游戏结束状态 -->
          <div v-else-if="gameStore.currentGame?.phase === 'finished' && showGameEndStatus" class="text-white text-center space-y-4">
            <div class="bg-gradient-to-r from-yellow-600/20 to-orange-600/20 backdrop-blur-md rounded-xl px-8 py-6 border border-yellow-500/30">
              <h2 class="text-2xl font-bold text-yellow-400 mb-4">🎉 游戏结束 🎉</h2>
              
              <!-- 显示获胜者信息 -->
              <div v-if="gameStore.gameResults && gameStore.gameResults.results && gameStore.gameResults.results.length > 0" class="mb-4">
                <h3 class="text-lg font-semibold text-white mb-2">获胜者:</h3>
                <div class="space-y-2">
                  <div 
                    v-for="result in gameStore.gameResults.results.filter(r => r.win_amount > 0)" 
                    :key="result.user_id"
                    class="bg-white/10 rounded-lg px-4 py-2"
                  >
                    <span class="text-yellow-300 font-bold">{{ result.username }}</span>
                    <span class="text-white ml-2">赢得 {{ result.win_amount.toLocaleString() }} 筹码</span>
                  </div>
                </div>
              </div>
              
              <!-- 显示底池信息 -->
              <div class="text-gray-300 mb-4">
                总底池: {{ gameStore.currentGame?.pot?.toLocaleString() || 0 }} 筹码
              </div>
              
              <!-- 操作按钮 -->
              <div class="flex justify-center">
                <button
                  @click="leaveGame"
                  class="bg-gray-600 hover:bg-gray-500 text-white font-bold py-3 px-6 rounded-xl transition-all shadow-lg"
                >
                  返回大厅
                </button>
              </div>
            </div>
          </div>
          
          <!-- 等待其他玩家 -->
          <div v-else class="text-white text-center">
            <div class="bg-white/10 backdrop-blur-md rounded-lg px-6 py-3 border border-white/20">
              {{ (gameStore.currentGame?.phase as string) === 'waiting' ? '等待所有玩家准备...' : '等待其他玩家操作...' }}
            </div>
          </div>
        </div>
      </div>

    </div>

    <!-- 游戏结果详情弹窗 -->
    <div v-if="showGameResultModal" class="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div class="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20 w-full max-w-4xl max-h-[80vh] overflow-y-auto">
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-white text-2xl font-bold">🃏 游戏结果详情</h3>
          <button
            @click="showGameResultModal = false"
            class="text-white hover:text-gray-300 text-2xl font-bold"
          >
            ×
          </button>
        </div>
        
        <!-- 公共牌展示 -->
        <div class="mb-8">
          <h4 class="text-white text-lg font-semibold mb-4 text-center">公共牌</h4>
          <div class="flex justify-center space-x-3">
            <div
              v-for="(card, index) in communityCards" 
              :key="`community-${index}`"
              :class="getCardColor(card.suit)"
              class="w-16 h-24 rounded-lg border-2 flex flex-col items-center justify-center text-sm font-bold shadow-lg bg-white"
            >
              <div class="text-center leading-tight">
                <div class="text-lg">{{ getDisplayRank(card.rank) }}</div>
                <div class="text-xl">{{ getSuitSymbol(card.suit) }}</div>
              </div>
            </div>
            <!-- 如果公共牌不足5张，显示空白占位符 -->
            <div
              v-for="index in (5 - communityCards.length)" 
              :key="`placeholder-${index}`"
              class="w-16 h-24 rounded-lg border-2 border-dashed border-white/30 flex items-center justify-center bg-white/10"
            >
              <span class="text-white/50 text-xs">?</span>
            </div>
          </div>
        </div>
        
        <!-- 玩家手牌排序 -->
        <div class="space-y-4">
          <h4 class="text-white text-lg font-semibold mb-4">玩家手牌排序 (按牌力从大到小)</h4>
          
          <div 
            v-for="(playerResult, index) in sortedPlayerResults" 
            :key="playerResult.playerId"
            class="bg-white/10 rounded-xl p-4 border border-white/20"
          >
            <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <!-- 玩家信息和排名 -->
              <div class="flex items-center space-x-4">
                <div class="bg-gradient-to-r from-yellow-500 to-orange-500 text-white font-bold w-8 h-8 rounded-full flex items-center justify-center text-sm">
                  {{ index + 1 }}
                </div>
                <div>
                  <div class="text-white font-bold text-lg">{{ playerResult.username }}</div>
                  <div class="text-gray-300 text-sm">{{ playerResult.handType }}</div>
                </div>
              </div>
              
              <!-- 手牌展示 -->
              <div class="flex space-x-2">
                <div
                  v-for="card in playerResult.cards" 
                  :key="`${card.suit}-${card.rank}`"
                  :class="getCardColor(card.suit)"
                  class="w-12 h-16 rounded-lg border-2 flex flex-col items-center justify-center text-xs font-bold shadow-lg transform hover:scale-105 transition-transform bg-white"
                >
                  <div class="text-center leading-tight">
                    <div>{{ getDisplayRank(card.rank) }}</div>
                    <div class="text-lg">{{ getSuitSymbol(card.suit) }}</div>
                  </div>
                </div>
              </div>
              
              <!-- 输赢金额 -->
              <div class="text-right">
                <div :class="playerResult.winAmount >= 0 ? 'text-green-400' : 'text-red-400'" class="font-bold text-lg">
                  {{ playerResult.winAmount >= 0 ? '+' : '' }}{{ playerResult.winAmount.toLocaleString() }}
                </div>
                <div class="text-gray-300 text-sm">筹码变化</div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 操作按钮 -->
        <div class="flex justify-center mt-6">
          <button
            @click="leaveGame"
            class="bg-gray-600 hover:bg-gray-500 text-white font-bold py-3 px-6 rounded-xl transition-all shadow-lg"
          >
            返回大厅
          </button>
        </div>
      </div>
    </div>


  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft } from 'lucide-vue-next'
import { useUserStore } from '../stores/user'
import { useRoomStore } from '../stores/room'
import { useGameStore, type Card, type Player, type GameState } from '../stores/game'
import PlayerSeat from '../components/PlayerSeat.vue'
import PlayingCard from '../components/PlayingCard.vue'
import { websocketService, connectWebSocket, disconnectWebSocket } from '../utils/websocket'

// API基础URL
const API_BASE_URL = 'http://localhost:8000'

const router = useRouter()
const userStore = useUserStore()
const roomStore = useRoomStore()
const gameStore = useGameStore()

const raiseAmount = ref(100)

const isPlayerReady = ref(false)
const showGameResultModal = ref(false)
const showGameEndStatus = ref(false)

// 监听游戏阶段变化，自动显示结果弹窗
watch(() => gameStore.currentGame?.phase, (newPhase, oldPhase) => {
  // 只有在游戏进行中切换到finished状态时才显示弹窗
  // 避免初次进入游戏时显示上一局的结果
  if (newPhase === 'finished' && oldPhase && oldPhase !== 'finished') {
    // 显示底部游戏结束状态
    showGameEndStatus.value = true
    // 3秒后自动隐藏底部游戏结束状态
    setTimeout(() => {
      showGameEndStatus.value = false
    }, 3000)
    
    // 只有当前用户参与了游戏才显示弹窗
    const currentUserId = String(userStore.user?.id)
    const currentPlayer = gameStore.currentGame?.players.find(p => p.id === currentUserId)
    if (currentPlayer && currentPlayer.cards && currentPlayer.cards.length > 0) {
      showGameResultModal.value = true
    }
  }
  
  // 当游戏开始新一轮时，清除之前的游戏结果数据
  if (newPhase === 'preflop' && oldPhase === 'finished') {
    gameStore.clearGameResults()
    showGameResultModal.value = false
    showGameEndStatus.value = false
  }
  
  // 当进入等待状态时，不自动关闭结果弹窗，让用户手动关闭
  // 移除自动关闭逻辑，保持弹窗显示直到用户手动关闭
})



// 公共牌
const communityCards = computed(() => gameStore.currentGame?.communityCards || [])

// 计算属性
const players = computed(() => gameStore.currentGame?.players || [])
// 优化的防抖逻辑：更稳定的状态管理
const stableGameState = ref<any>(null)
const lastStateUpdateTime = ref(0)
const stateUpdateCount = ref(0)
const STATE_UPDATE_DEBOUNCE = 500 // 增加到500ms防抖
const MAX_UPDATES_PER_SECOND = 3 // 每秒最多3次更新

const isMyTurn = computed(() => {
  const now = Date.now()
  const currentUserId = userStore.user?.id?.toString()
  
  console.log(`\n=== isMyTurn 计算开始 [${new Date().toLocaleTimeString()}] ===`)
  console.log('当前时间戳:', now)
  console.log('用户ID:', currentUserId)
  
  // 基础检查
  if (!gameStore.currentGame || !currentUserId) {
    console.log('❌ 基础检查失败: 游戏状态或用户ID为空')
    return false
  }
  
  const game = gameStore.currentGame
  console.log('游戏基础信息:')
  console.log('  游戏阶段:', game.phase)
  console.log('  当前玩家ID:', game.currentPlayerId)
  console.log('  玩家总数:', game.players.length)
  
  // 游戏阶段检查
  if (game.phase === 'waiting' || game.phase === 'finished') {
    console.log('❌ 游戏阶段检查失败: 游戏处于等待或结束状态')
    return false
  }
  
  // 增强的防抖逻辑
  const timeSinceLastUpdate = now - lastStateUpdateTime.value
  
  // 重置更新计数器（每秒重置）
  if (timeSinceLastUpdate > 1000) {
    stateUpdateCount.value = 0
  }
  
  console.log('防抖检查:')
  console.log('  距离上次更新:', timeSinceLastUpdate, 'ms')
  console.log('  本秒更新次数:', stateUpdateCount.value)
  console.log('  防抖阈值:', STATE_UPDATE_DEBOUNCE, 'ms')
  
  // 如果更新过于频繁，使用稳定状态
  const shouldUseStableState = (
    (timeSinceLastUpdate < STATE_UPDATE_DEBOUNCE && stableGameState.value) ||
    (stateUpdateCount.value >= MAX_UPDATES_PER_SECOND && stableGameState.value)
  )
  
  if (shouldUseStableState) {
    console.log('⏱️ 防抖触发: 使用稳定状态')
    console.log('稳定状态当前玩家ID:', stableGameState.value.currentPlayerId)
    
    const stableResult = stableGameState.value.currentPlayerId === currentUserId
    console.log('稳定状态匹配结果:', stableResult)
    console.log('=== isMyTurn 计算结束 (使用稳定状态) ===\n')
    return stableResult
  }
  
  console.log('🔄 状态更新: 使用最新状态')
  
  // 检查状态是否真的发生了变化
  const hasStateChanged = !stableGameState.value || 
    stableGameState.value.currentPlayerId !== game.currentPlayerId ||
    stableGameState.value.phase !== game.phase
  
  if (hasStateChanged) {
    console.log('状态确实发生变化，更新稳定状态')
    stableGameState.value = {
      currentPlayerId: game.currentPlayerId,
      phase: game.phase,
      currentPlayerIndex: game.currentPlayerIndex
    }
    lastStateUpdateTime.value = now
    stateUpdateCount.value++
  } else {
    console.log('状态未发生变化，保持稳定状态')
  }
  
  // 玩家匹配检查
  console.log('玩家匹配检查:')
  console.log('  当前行动玩家ID:', game.currentPlayerId)
  console.log('  登录用户ID:', currentUserId)
  
  const isMatch = game.currentPlayerId === currentUserId
  console.log('最终匹配结果:', isMatch)
  
  if (isMatch) {
    console.log('✅ 玩家匹配成功: 显示操作按钮')
  } else {
    console.log('❌ 玩家匹配失败: 隐藏操作按钮')
  }
  
  console.log('=== isMyTurn 计算结束 ===\n')
  return isMatch
})

const currentPlayerChips = computed(() => {
  if (!userStore.user || !gameStore.currentGame) return 0
  const player = gameStore.currentGame.players.find(p => p.id === String(userStore.user.id))
  return player?.chips || 0
})

const needToCall = computed(() => {
  if (!gameStore.currentGame || !userStore.user) return false
  const player = gameStore.currentGame.players.find(p => p.id === String(userStore.user.id))
  return (player?.currentBet || 0) < gameStore.currentGame.currentBet
})

const callAmount = computed(() => {
  if (!gameStore.currentGame || !userStore.user) return 0
  const player = gameStore.currentGame.players.find(p => p.id === String(userStore.user.id))
  return gameStore.currentGame.currentBet - (player?.currentBet || 0)
})

const minRaise = computed(() => {
  if (!gameStore.currentGame) return 0
  
  // 获取上一个加注的金额
  const currentBet = gameStore.currentGame.currentBet || 0
  const bigBlind = gameStore.currentGame.bigBlind || 20
  
  // 如果当前没有人下注，最小加注是大盲注
  if (currentBet === 0) {
    return bigBlind
  }
  
  // 最小加注是上一个加注的金额（即当前最高下注减去大盲注）
  const lastRaiseAmount = Math.max(currentBet - bigBlind, bigBlind)
  return lastRaiseAmount
})

// 根据房间最大玩家数确定座位数量
const maxSeats = computed(() => {
  return roomStore.currentRoom?.max_players || roomStore.currentRoom?.maxPlayers || 9
})



// 游戏结果排序计算属性
const sortedPlayerResults = computed(() => {
  // 优先使用gameStore中的游戏结果数据
  if (gameStore.gameResults && gameStore.gameResults.results) {
    return gameStore.gameResults.results.map(result => ({
      playerId: result.user_id,
      username: result.username,
      cards: result.hole_cards,
      handType: result.hand_rank,
      handStrength: result.hand_strength,
      winAmount: result.win_amount
    }))
  }
  
  // 如果没有游戏结果数据，使用原有逻辑作为后备
  if (!gameStore.currentGame || gameStore.currentGame.phase !== 'finished') return []
  
  // 获取所有未弃牌的玩家
  const activePlayers = gameStore.currentGame.players.filter(player => 
    !player.isFolded && player.cards && player.cards.length > 0
  )
  
  // 计算每个玩家的结果
  const playerResults = activePlayers.map(player => {
    // 计算手牌类型和强度
    const handInfo = evaluateHand(player.cards, gameStore.currentGame?.communityCards || [])
    
    // 计算输赢金额 - 使用gameResults数据
    let winAmount = 0
    if (gameStore.gameResults && gameStore.gameResults.results) {
      const result = gameStore.gameResults.results.find(r => r.user_id === player.id)
      if (result) {
        winAmount = result.win_amount
      }
    }
    
    // 如果没有游戏结果数据，计算损失（当前下注金额）
    if (winAmount === 0) {
      winAmount = -(player.currentBet || 0)
    }
    
    return {
      playerId: player.id,
      username: player.username,
      cards: player.cards,
      handType: handInfo.type,
      handStrength: handInfo.strength,
      winAmount: winAmount
    }
  })
  
  // 按手牌强度从大到小排序
  return playerResults.sort((a, b) => b.handStrength - a.handStrength)
})

// 手牌评估函数
const evaluateHand = (playerCards: Card[], communityCards: Card[]) => {
  // 合并玩家手牌和公共牌
  const allCards = [...playerCards, ...communityCards]
  
  // 简化的手牌评估逻辑
  // 这里可以根据需要实现更复杂的德州扑克手牌评估
  
  // 按点数分组
  const rankCounts: { [key: number]: number } = {}
  allCards.forEach(card => {
    rankCounts[card.rank] = (rankCounts[card.rank] || 0) + 1
  })
  
  // 按花色分组
  const suitCounts: { [key: string]: number } = {}
  allCards.forEach(card => {
    suitCounts[card.suit] = (suitCounts[card.suit] || 0) + 1
  })
  
  const counts = Object.values(rankCounts).sort((a, b) => b - a)
  const maxSuitCount = Math.max(...Object.values(suitCounts))
  
  // 判断手牌类型和强度
  if (counts[0] === 4) {
    return { type: '四条', strength: 7000 + Math.max(...Object.keys(rankCounts).map(Number)) }
  } else if (counts[0] === 3 && counts[1] === 2) {
    return { type: '葫芦', strength: 6000 + Math.max(...Object.keys(rankCounts).map(Number)) }
  } else if (maxSuitCount >= 5) {
    return { type: '同花', strength: 5000 + Math.max(...allCards.map(c => c.rank)) }
  } else if (counts[0] === 3) {
    return { type: '三条', strength: 3000 + Math.max(...Object.keys(rankCounts).map(Number)) }
  } else if (counts[0] === 2 && counts[1] === 2) {
    return { type: '两对', strength: 2000 + Math.max(...Object.keys(rankCounts).map(Number)) }
  } else if (counts[0] === 2) {
    return { type: '一对', strength: 1000 + Math.max(...Object.keys(rankCounts).map(Number)) }
  } else {
    return { type: '高牌', strength: Math.max(...allCards.map(c => c.rank)) }
  }
}

// 方法
const getCardColor = (suit: string) => {
  // 支持后端返回的符号格式和英文名称格式
  if (suit === '♥' || suit === '♦' || suit === 'hearts' || suit === 'diamonds') {
    return 'text-red-600'
  }
  return 'text-black'
}

const getSuitSymbol = (suit: string) => {
  // 如果已经是符号，直接返回
  if (['♥', '♦', '♣', '♠'].includes(suit)) {
    return suit
  }
  
  // 如果是英文名称，转换为符号
  const symbols = {
    hearts: '♥',
    diamonds: '♦',
    clubs: '♣',
    spades: '♠'
  }
  return symbols[suit as keyof typeof symbols] || suit
}

const getDisplayRank = (rank: number) => {
  if (rank === 1) return 'A'
  if (rank === 11) return 'J'
  if (rank === 12) return 'Q'
  if (rank === 13) return 'K'
  if (rank === 14) return 'A'
  return rank.toString()
}

const getPlayerPositionClass = (index: number, totalSeats: number) => {
  // 对于6座位及以下，使用预设的Tailwind类
  if (totalSeats <= 6) {
    const positions = [
      'bottom-2 left-1/2 transform -translate-x-1/2 translate-y-full',
      'bottom-8 right-2 transform translate-x-full',
      'top-8 right-2 transform translate-x-full', 
      'top-2 left-1/2 transform -translate-x-1/2 -translate-y-full',
      'top-8 left-2 transform -translate-x-full',
      'bottom-8 left-2 transform -translate-x-full'
    ]
    return positions[index] || positions[0]
  }
  // 对于更多座位，只返回基本的transform类
  return 'transform -translate-x-1/2 -translate-y-1/2'
}

const getPlayerPositionStyle = (index: number, totalSeats: number) => {
  // 对于6座位及以下，不需要额外样式
  if (totalSeats <= 6) {
    return {}
  }
  
  // 对于更多座位，使用动态计算的位置
  const angle = (index * 360) / totalSeats
  const radians = (angle * Math.PI) / 180
  
  // 椭圆参数（相对于容器的百分比）
  const a = 45 // 水平半径百分比
  const b = 35 // 垂直半径百分比
  
  // 计算位置（从顶部开始，顺时针）
  const x = 50 + a * Math.cos(radians - Math.PI / 2)
  const y = 50 + b * Math.sin(radians - Math.PI / 2)
  
  return {
    left: `${x}%`,
    top: `${y}%`
  }
}

const getPhaseText = (phase?: string) => {
  const phaseTexts = {
    waiting: '等待开始',
    preflop: '翻牌前',
    flop: '翻牌',
    turn: '转牌',
    river: '河牌',
    showdown: '摊牌',
    finished: '结束'
  }
  return phaseTexts[phase as keyof typeof phaseTexts] || '未知阶段'
}

const formatTime = (timestamp: Date) => {
  return timestamp.toLocaleTimeString('zh-CN', { 
    hour: '2-digit', 
    minute: '2-digit' 
  })
}

// 游戏操作
const fold = () => {
  if (!userStore.user || !roomStore.currentRoom) return
  
  console.log('玩家弃牌')
  websocketService.sendGameAction(Number(roomStore.currentRoom.id), 'fold')
}

const callOrCheck = () => {
  if (!userStore.user || !gameStore.currentGame || !roomStore.currentRoom) return
  
  const action = needToCall.value ? 'call' : 'check'
  const amount = needToCall.value ? callAmount.value : 0
  
  console.log(`玩家${action}:`, amount)
  websocketService.sendGameAction(Number(roomStore.currentRoom.id), action, amount)
}

const raise = () => {
  if (!userStore.user || !gameStore.currentGame || !roomStore.currentRoom) return
  
  const currentUserId = String(userStore.user.id)
  const player = gameStore.currentGame.players.find(p => p.id === currentUserId)
  if (!player) return
  
  // 检查是否是最小加注的倍数
  if (raiseAmount.value % minRaise.value !== 0) {
    alert(`加注金额必须是 ${minRaise.value} 的倍数`)
    return
  }
  
  // 计算总下注金额（当前下注 + 加注金额）
  const totalBet = (player.currentBet || 0) + raiseAmount.value
  
  // 检查是否超过玩家筹码
  if (totalBet > player.chips) {
    alert('筹码不足，请选择全下')
    return
  }
  
  console.log('玩家加注:', raiseAmount.value, '总下注:', totalBet)
  websocketService.sendGameAction(Number(roomStore.currentRoom.id), 'raise', totalBet)
}

const allIn = () => {
  if (!userStore.user || !gameStore.currentGame || !roomStore.currentRoom) return
  
  const currentUserId = String(userStore.user.id)
  const player = gameStore.currentGame.players.find(p => p.id === currentUserId)
  if (!player) return

  const allInAmount = player.chips
  console.log('玩家全下:', allInAmount)
  websocketService.sendGameAction(Number(roomStore.currentRoom.id), 'all_in', allInAmount)
}

const showCards = () => {
  if (!userStore.user || !gameStore.currentGame || !roomStore.currentRoom) return
  
  const currentUserId = String(userStore.user.id)
  const player = gameStore.currentGame.players.find(p => p.id === currentUserId)
  if (!player || !player.cards || player.cards.length === 0) {
    alert('没有手牌可以展示')
    return
  }
  
  // 确认是否要展示手牌
  const confirmed = confirm('确定要向所有玩家展示你的手牌吗？')
  if (!confirmed) return
  
  // 通过WebSocket广播展示手牌
  websocketService.showCards(Number(roomStore.currentRoom.id))
  
  console.log('展示手牌:', player.cards)
  

}



const toggleReady = async () => {
  if (!userStore.user || !roomStore.currentRoom) return
  
  try {
    const newReadyState = !isPlayerReady.value
    
    // 通过WebSocket发送player_ready消息
    if (websocketService.isConnected()) {
      websocketService.send({
        type: 'player_ready',
        data: {
          room_id: roomStore.currentRoom.id,
          ready: newReadyState
        }
      })
      
      // 更新本地状态
      isPlayerReady.value = newReadyState
      console.log('玩家准备状态:', isPlayerReady.value)
    } else {
      console.error('WebSocket未连接，无法设置准备状态')
    }
  } catch (error) {
    console.error('设置准备状态错误:', error)
  }
}



// 获取指定座位的玩家
const getPlayerAtSeat = (seatIndex: number) => {
  if (!gameStore.currentGame) return null
  // 只返回position等于seatIndex且不为-1的玩家
  const player = gameStore.currentGame.players.find(player => player.position === seatIndex && player.position >= 0) || null
  console.log(`[DEBUG] getPlayerAtSeat(${seatIndex}):`, player ? `${player.username} (id: ${player.id}, position: ${player.position})` : 'empty')
  return player
}

// 检查指定座位是否是当前玩家
const isCurrentPlayerAtSeat = (seatIndex: number) => {
  if (!gameStore.currentGame) return false
  const player = getPlayerAtSeat(seatIndex)
  if (!player) return false
  
  // 通过currentPlayerIndex找到当前玩家
  const currentPlayer = gameStore.currentGame.players[gameStore.currentGame.currentPlayerIndex]
  if (!currentPlayer) return false
  
  const isCurrentPlayer = player.id === currentPlayer.id
  console.log(`[DEBUG] isCurrentPlayerAtSeat(${seatIndex}): player=${player.username}, currentPlayer=${currentPlayer.username}, isCurrent=${isCurrentPlayer}`)
  return isCurrentPlayer
}

// 检查指定座位是否是庄家
const isDealerAtSeat = (seatIndex: number) => {
  if (!gameStore.currentGame) return false
  const player = getPlayerAtSeat(seatIndex)
  if (!player) return false
  
  // 通过dealerPosition找到庄家
  const dealerPlayer = gameStore.currentGame.players.find(p => p.position === gameStore.currentGame.dealerPosition)
  if (!dealerPlayer) return false
  
  const isDealer = player.id === dealerPlayer.id
  console.log(`[DEBUG] isDealerAtSeat(${seatIndex}): player=${player.username}, dealerPlayer=${dealerPlayer.username}, isDealer=${isDealer}`)
  return isDealer
}

// 处理座位点击
const handleSeatClick = async (seatIndex: number) => {
  console.log(`[DEBUG] handleSeatClick called with seatIndex: ${seatIndex}`)
  
  if (!userStore.user || !roomStore.currentRoom) {
    console.log('[DEBUG] User or room not available')
    return
  }
  
  const playerAtSeat = getPlayerAtSeat(seatIndex)
  const currentUserId = String(userStore.user.id)
  
  console.log(`[DEBUG] Current user ID: ${currentUserId}`)
  console.log(`[DEBUG] Player at seat ${seatIndex}:`, playerAtSeat)
  
  // 如果座位为空，直接入座
  if (!playerAtSeat) {
    console.log(`[DEBUG] 座位 ${seatIndex} 为空，尝试入座`)
    await selectSeat(seatIndex)
    return
  }
  
  // 如果点击的是自己的座位，不做任何操作
  if (playerAtSeat.id === currentUserId) {
    console.log('[DEBUG] 点击了自己的座位，无需操作')
    return
  }
  
  // 如果座位被其他玩家占用，提示用户
  console.log(`[DEBUG] 座位 ${seatIndex} 已被玩家 ${playerAtSeat.username} 占用`)
  alert(`座位 ${seatIndex + 1} 已被 ${playerAtSeat.username} 占用`)
}

// 检查用户是否需要选择座位（已移除座位选择功能）
const checkUserSeat = async () => {
  if (!userStore.user || !gameStore.currentGame) return
  
  // 检查用户是否已经有座位
  const currentUserId = String(userStore.user.id)
  const currentPlayer = gameStore.currentGame.players.find(p => p.id === currentUserId)
  
  console.log(`[DEBUG] checkUserSeat: currentPlayer=`, currentPlayer)
  
  if (currentPlayer && currentPlayer.position >= 0) {
    console.log(`用户 ${currentUserId} 已有座位，位置:`, currentPlayer.position)
    return
  }
  
  console.log(`用户 ${currentUserId} 需要选择座位，但座位选择功能已移除`)
}

// 选择座位
const selectSeat = async (seatIndex: number) => {
  try {
    if (!userStore.user || !roomStore.currentRoom) {
      console.error('用户未登录或不在房间中')
      return
    }

    console.log(`[DEBUG] 尝试选择座位: ${seatIndex}`)
    
    const response = await fetch(`${API_BASE_URL}/api/rooms/${roomStore.currentRoom.id}/change-seat`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${userStore.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        seat_index: seatIndex
      })
    })

    if (response.ok) {
      const result = await response.json()
      console.log('切换座位成功:', result)
      
      // 更新游戏状态
      if (result.game_state) {
        updateGameStateFromAPI(result.game_state)
      } else {
        // 如果没有返回游戏状态，手动获取
        await fetchGameState()
      }
    } else {
      const error = await response.json()
      console.error('切换座位失败:', error)
      alert(error.detail || '切换座位失败，请稍后重试')
    }
  } catch (error) {
    console.error('切换座位错误:', error)
    alert('切换座位失败，请稍后重试')
  }
}

// 根据玩家ID获取玩家信息
const getPlayerById = (playerId: string) => {
  if (!gameStore.currentGame) return null
  return gameStore.currentGame.players.find(p => p.id === playerId)
}

// 开始新游戏
const startNewGame = async () => {
  try {
    if (!roomStore.currentRoom) return
    
    // 只关闭当前用户的游戏结束弹窗，不清除游戏结果数据
    showGameResultModal.value = false
    
    // 自动设置当前玩家为准备状态
    if (!isPlayerReady.value) {
      await toggleReady()
    }
    
    // 注意：不调用后端的start-game接口，因为那会影响所有玩家
    // 只是让当前玩家准备，等所有玩家都准备后游戏会自动开始
    
    console.log('当前玩家已准备，等待其他玩家准备')
  } catch (error) {
    console.error('准备游戏错误:', error)
    alert('准备失败，请稍后重试')
  }
}

const leaveGame = async () => {
  try {
    console.log('[DEBUG] Leaving game...')
    const result = await roomStore.leaveRoom()
    console.log('[DEBUG] Leave room result:', result)
    
    gameStore.leaveGame()
    console.log('[DEBUG] Game store cleared')
    
    console.log('[DEBUG] Navigating to lobby...')
    // 使用replace而不是push，避免用户返回到游戏页面
    await router.replace('/lobby')
    console.log('[DEBUG] Navigation completed')
  } catch (error) {
    console.error('[DEBUG] Error leaving game:', error)
    // 清除本地状态
    gameStore.leaveGame()
    roomStore.currentRoom = null
    // 强制跳转到大厅
    console.log('[DEBUG] Force navigation to lobby')
    window.location.href = '/lobby'
  }
}

// 生命周期
onMounted(async () => {
  // 初始化游戏状态
  await initializeGame()
  
  // 设置定时器定期获取游戏状态
  const gameStateInterval = setInterval(async () => {
    await fetchGameState()
  }, 2000) // 每2秒更新一次游戏状态
  
  // 组件卸载时清理定时器
  onUnmounted(() => {
    clearInterval(gameStateInterval)
  })
})

// 初始化游戏
const initializeGame = async () => {
  try {
    // 确保用户已登录且在房间中
    if (!userStore.user || !roomStore.currentRoom) {
      console.error('用户未登录或不在房间中')
      router.push('/lobby')
      return
    }
    
    // 清除之前的游戏结果和弹窗状态
    showGameResultModal.value = false
    gameStore.clearGameResults()
    
    // 先加入游戏
    await joinGameAPI()
    
    // 然后获取游戏状态
    await fetchGameState()
    
    // 检查用户座位状态
    setTimeout(async () => {
      await checkUserSeat()
    }, 1000) // 延迟1秒确保游戏状态已更新
    
    console.log('游戏初始化完成')
  } catch (error) {
    console.error('游戏初始化失败:', error)
  }
}

// 加入游戏API
const joinGameAPI = async () => {
  try {
    if (!roomStore.currentRoom) return
    
    const response = await fetch(`${API_BASE_URL}/api/rooms/${roomStore.currentRoom.id}/join-game`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${userStore.token}`,
        'Content-Type': 'application/json'
      }
    })
    
    if (response.ok) {
      const result = await response.json()
      console.log('加入游戏成功:', result.message)
      
      // 如果返回了游戏状态，直接更新
      if (result.game_state) {
        updateGameStateFromAPI(result.game_state)
      }
    } else {
      console.error('加入游戏失败:', response.statusText)
    }
  } catch (error) {
    console.error('加入游戏错误:', error)
  }
}

// 获取游戏状态
const fetchGameState = async () => {
  try {
    if (!roomStore.currentRoom) return
    
    const response = await fetch(`${API_BASE_URL}/api/rooms/${roomStore.currentRoom.id}/game-state`, {
      headers: {
        'Authorization': `Bearer ${userStore.token}`,
        'Content-Type': 'application/json'
      }
    })
    
    if (response.ok) {
      const gameData = await response.json()
      
      // 更新游戏状态
      if (gameData.game) {
        updateGameStateFromAPI(gameData)
        // 更新游戏状态后检查用户座位
        await checkUserSeat()
      }
      
      console.log('游戏状态更新:', gameData)
    } else {
      console.error('获取游戏状态失败:', response.statusText)
    }
  } catch (error) {
    console.error('获取游戏状态错误:', error)
  }
}

// 从API数据更新游戏状态
const updateGameStateFromAPI = (apiData: any) => {
  try {
    // 更新房间信息
    if (apiData.room) {
      roomStore.currentRoom = apiData.room
    }
    
    // 使用gameStore的方法来更新游戏状态，确保与WebSocket处理一致
    gameStore.updateGameStateFromAPI(apiData)
    
    // 更新当前用户的准备状态
    if (userStore.user && gameStore.currentGame) {
      const currentUserId = String(userStore.user.id)
      const currentPlayer = gameStore.currentGame.players.find(p => p.id === currentUserId)
      if (currentPlayer) {
        isPlayerReady.value = currentPlayer.isReady
        console.log(`玩家 ${currentUserId} 准备状态更新为:`, isPlayerReady.value)
      } else {
        isPlayerReady.value = false
        console.log(`玩家 ${currentUserId} 不在游戏中，重置准备状态`)
      }
    }
    
    console.log('游戏状态已通过GamePage更新')
  } catch (error) {
    console.error('更新游戏状态失败:', error)
  }
}

onMounted(async () => {
  // 建立WebSocket连接
  await connectWebSocket()
  
  // 如果已连接，加入房间
  if (roomStore.currentRoom && websocketService.isConnected()) {
    websocketService.joinRoom(Number(roomStore.currentRoom.id))
  }
  
  // 初始化游戏
  await initializeGame()
})

onUnmounted(() => {
  // 离开房间
  if (roomStore.currentRoom && websocketService.isConnected()) {
    websocketService.leaveRoom(Number(roomStore.currentRoom.id))
  }
  
  // 断开WebSocket连接
  disconnectWebSocket()
  
  // 清理资源
})
</script>