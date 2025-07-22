<template>
  <div class="relative">
    <!-- 空座位 -->
    <div
      v-if="!player"
      @click="handleSeatClick"
      class="bg-white/5 backdrop-blur-md rounded-lg p-2 border border-white/10 transition-all cursor-pointer hover:bg-white/10 hover:border-white/30 flex items-center justify-center h-20 w-24"
    >
      <div class="text-white/50 text-center">
        <div class="text-lg mb-1">+</div>
        <div class="text-xs">入座</div>
      </div>
    </div>
    
    <!-- 玩家信息卡片 -->
    <div
      v-else
      @click="handleSeatClick"
      :class="[
        'bg-white/10 backdrop-blur-md rounded-lg p-2 border transition-all cursor-pointer hover:bg-white/20 w-24',
        isCurrent ? 'border-yellow-500 shadow-lg shadow-yellow-500/50' : 'border-white/20',
        player.isFolded ? 'opacity-50' : ''
      ]"
    >
      <!-- 庄家标识 -->
      <div
        v-if="isDealer"
        class="absolute -top-2 -right-2 w-6 h-6 bg-yellow-500 rounded-full flex items-center justify-center text-xs font-bold text-green-900"
      >
        D
      </div>

      <!-- 玩家头像和信息 -->
      <div class="flex flex-col items-center mb-1">
        <div class="relative mb-1">
          <img
            :src="player.avatar"
            :alt="player.username"
            class="w-8 h-8 rounded-full border border-white/30"
          />
          <!-- 在线状态指示器 -->
          <div
            :class="[
              'absolute -bottom-0.5 -right-0.5 w-2 h-2 rounded-full border border-white',
              player.isActive ? 'bg-green-500' : 'bg-gray-500'
            ]"
          ></div>
          <!-- 准备状态指示器 -->
          <div
            v-if="player.isReady"
            class="absolute -top-0.5 -left-0.5 w-3 h-3 bg-blue-500 rounded-full border border-white flex items-center justify-center"
          >
            <div class="text-white text-xs font-bold">✓</div>
          </div>
        </div>
        
        <div class="text-center">
          <div class="text-white text-xs font-medium truncate max-w-20">{{ player.username }}</div>
          <div class="text-yellow-500 text-xs font-bold">
            {{ player.chips.toLocaleString() }}
          </div>
        </div>
      </div>

      <!-- 手牌 -->
      <div class="flex justify-center space-x-0.5 mb-1">
        <!-- 显示具体牌面（自己的牌或摊牌阶段） -->
        <div
          v-for="(card, index) in displayCards"
          :key="'card-' + index"
          :class="getCardColor(card.suit)"
          class="w-8 h-12 rounded-lg border-2 flex flex-col items-center justify-center text-xs font-bold shadow-lg transform hover:scale-110 transition-transform bg-white"
        >
          <div class="text-center leading-tight">
            <div class="text-xs">{{ getDisplayRank(card.rank) }}</div>
            <div class="text-sm">{{ getSuitSymbol(card.suit) }}</div>
          </div>
        </div>
        <!-- 背面牌（其他玩家） -->
        <div
          v-for="i in (2 - displayCards.length)"
          :key="'back-' + i"
          class="w-8 h-12 rounded-lg border-2 border-blue-600 bg-gradient-to-br from-blue-800 to-blue-900 flex items-center justify-center shadow-lg"
        >
          <div class="text-white text-xs font-bold">🂠</div>
        </div>
      </div>

      <!-- 当前下注 -->
      <div class="text-center">
        <div class="bg-red-600 text-white text-xs px-1 py-0.5 rounded font-bold">
          {{ player.currentBet.toLocaleString() }}
        </div>
      </div>

      <!-- 玩家状态 -->
      <div v-if="player.action || player.isFolded" class="text-center mt-1">
        <div
          :class="[
            'text-xs px-2 py-1 rounded-full font-medium',
            getActionColor(player.isFolded ? 'fold' : player.action)
          ]"
        >
          {{ getActionText(player.isFolded ? 'fold' : player.action) }}
        </div>
      </div>

      <!-- 全下标识 -->
      <div v-if="player.isAllIn" class="absolute -top-1 left-1/2 transform -translate-x-1/2">
        <div class="bg-purple-600 text-white text-xs px-2 py-1 rounded-full font-bold">
          ALL IN
        </div>
      </div>
    </div>

    <!-- 思考时间指示器 -->
    <div
      v-if="isCurrent && !player.isFolded"
      class="absolute -bottom-8 left-1/2 transform -translate-x-1/2"
    >
      <div class="flex items-center space-x-2">
        <div class="w-2 h-2 bg-yellow-500 rounded-full animate-pulse"></div>
        <div class="text-yellow-500 text-xs font-medium">思考中...</div>
        <div class="w-2 h-2 bg-yellow-500 rounded-full animate-pulse"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Player, Card } from '../stores/game'
import { useUserStore } from '../stores/user'
import { useGameStore } from '../stores/game'

interface Props {
  player?: Player | null
  isCurrent: boolean
  isDealer: boolean
  seatIndex: number
}

interface Emits {
  seatClick: [seatIndex: number]
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()
const userStore = useUserStore()
const gameStore = useGameStore()

// 处理座位点击
const handleSeatClick = () => {
  console.log(`[DEBUG PlayerSeat] Seat ${props.seatIndex} clicked`)
  emit('seatClick', props.seatIndex)
}

// 计算属性
const displayCards = computed(() => {
  // 如果没有玩家，返回空数组
  if (!props.player) {
    return []
  }
  // 当前用户总是能看到自己的手牌
  if (props.player.id === userStore.user?.id) {
    return props.player.cards || []
  }
  // 其他玩家的牌在以下情况显示：
  // 1. 摊牌阶段 (showdown)
  // 2. 玩家主动展示手牌 (showCards标记)
  if (props.player.showCards || gameStore.currentGame?.phase === 'showdown') {
    return props.player.cards || []
  }
  // 其他情况不显示
  return []
})

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
  const suitMap: { [key: string]: string } = {
    'hearts': '♥',
    'diamonds': '♦', 
    'clubs': '♣',
    'spades': '♠'
  }
  return suitMap[suit] || suit
}

const getDisplayRank = (rank: number) => {
  const rankMap: { [key: number]: string } = {
    1: 'A',
    11: 'J',
    12: 'Q', 
    13: 'K',
    14: 'A' // 有些系统中A可能是14
  }
  return rankMap[rank] || rank.toString()
}

const getActionColor = (action: string) => {
  const colors = {
    fold: 'bg-red-600 text-white',
    call: 'bg-yellow-600 text-white',
    raise: 'bg-orange-600 text-white',
    check: 'bg-green-600 text-white',
    'all-in': 'bg-purple-600 text-white'
  }
  return colors[action as keyof typeof colors] || 'bg-gray-600 text-white'
}

const getActionText = (action: string) => {
  const texts = {
    fold: '弃牌',
    call: '跟注',
    raise: '加注',
    check: '过牌',
    'all-in': '全下'
  }
  return texts[action as keyof typeof texts] || action
}
</script>