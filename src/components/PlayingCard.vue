<template>
  <div
    :class="[
      'relative inline-block transition-all duration-300',
      size === 'small' ? 'w-8 h-12' :
      size === 'medium' ? 'w-12 h-16' :
      'w-16 h-24',
      flipped ? 'transform rotate-y-180' : '',
      className
    ]"
  >
    <!-- 卡片背面 -->
    <div
      v-if="!card || hidden"
      :class="[
        'absolute inset-0 rounded-lg border-2 border-blue-300 bg-gradient-to-br from-blue-600 to-blue-800 flex items-center justify-center shadow-lg',
        'backface-hidden'
      ]"
    >
      <div class="text-white text-xs font-bold transform rotate-45">
        <Spade class="w-4 h-4" />
      </div>
    </div>

    <!-- 卡片正面 -->
    <div
      v-if="card && !hidden"
      :class="[
        'absolute inset-0 rounded-lg border-2 bg-white shadow-lg flex flex-col justify-between p-1',
        getSuitColor(card.suit),
        'backface-hidden'
      ]"
    >
      <!-- 左上角 -->
      <div class="flex flex-col items-center">
        <span :class="['font-bold leading-none', getTextSize()]">
          {{ getDisplayRank(card.rank) }}
        </span>
        <component
          :is="getSuitIcon(card.suit)"
          :class="['leading-none', getIconSize()]"
        />
      </div>

      <!-- 中央花色 -->
      <div class="flex-1 flex items-center justify-center">
        <component
          :is="getSuitIcon(card.suit)"
          :class="[
            'opacity-20',
            size === 'small' ? 'w-3 h-3' :
            size === 'medium' ? 'w-4 h-4' :
            'w-6 h-6'
          ]"
        />
      </div>

      <!-- 右下角（旋转180度） -->
      <div class="flex flex-col items-center transform rotate-180">
        <span :class="['font-bold leading-none', getTextSize()]">
          {{ getDisplayRank(card.rank) }}
        </span>
        <component
          :is="getSuitIcon(card.suit)"
          :class="['leading-none', getIconSize()]"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Spade, Heart, Diamond, Club } from 'lucide-vue-next'

interface Card {
  suit: string // 花色符号：♥, ♦, ♣, ♠
  rank: number // 牌面值：2-14
  display?: string // 显示字符串（可选）
}

interface Props {
  card?: Card
  hidden?: boolean
  flipped?: boolean
  size?: 'small' | 'medium' | 'large'
  className?: string
}

const props = withDefaults(defineProps<Props>(), {
  hidden: false,
  flipped: false,
  size: 'medium',
  className: ''
})

const getSuitIcon = (suit: string) => {
  const icons = {
    '♥': Heart,
    '♦': Diamond,
    '♣': Club,
    '♠': Spade
  }
  return icons[suit as keyof typeof icons] || Spade
}

const getSuitColor = (suit: string) => {
  return suit === '♥' || suit === '♦'
    ? 'text-red-600 border-red-300'
    : 'text-black border-gray-300'
}

const getDisplayRank = (rank: number) => {
  // 将数字转换为正确的牌面显示
  const rankMap: { [key: number]: string } = {
    1: 'A',
    11: 'J', 
    12: 'Q',
    13: 'K',
    14: 'A' // 有些系统中A可能是14
  }
  return rankMap[rank] || rank.toString()
}

const getTextSize = () => {
  return props.size === 'small' ? 'text-xs' :
         props.size === 'medium' ? 'text-sm' :
         'text-base'
}

const getIconSize = () => {
  return props.size === 'small' ? 'w-2 h-2' :
         props.size === 'medium' ? 'w-3 h-3' :
         'w-4 h-4'
}
</script>

<style scoped>
.backface-hidden {
  backface-visibility: hidden;
}

.rotate-y-180 {
  transform: rotateY(180deg);
}
</style>