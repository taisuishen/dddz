<template>
  <div class="min-h-screen bg-gradient-to-br from-green-900 via-green-800 to-green-700">
    <!-- 顶部导航栏 -->
    <header class="bg-green-900/50 backdrop-blur-md border-b border-green-700">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <div class="flex items-center">
            <button
              @click="router.push('/lobby')"
              class="text-gray-300 hover:text-white transition-colors mr-4"
            >
              <ArrowLeft class="w-5 h-5" />
            </button>
            <Spade class="w-8 h-8 text-yellow-500 mr-2" />
            <span class="text-white font-bold text-xl">个人中心</span>
          </div>
          <div class="flex items-center space-x-4">
            <div class="flex items-center space-x-2">
              <Coins class="w-5 h-5 text-yellow-500" />
              <span class="text-yellow-500 font-bold">{{ userStore.currentUser?.balance?.toLocaleString() || 0 }}</span>
            </div>
            <div class="flex items-center space-x-2">
              <span class="text-gray-300 text-sm">借码次数:</span>
              <span class="text-yellow-500 font-bold">{{ userStore.currentUser?.borrow_times || 0 }}</span>
            </div>
          </div>
        </div>
      </div>
    </header>

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- 左侧个人信息 -->
        <div class="lg:col-span-1 space-y-6">
          <!-- 用户资料卡 -->
          <div class="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20">
            <div class="text-center">
              <div class="relative inline-block mb-4">
                <img
                  :src="userStore.currentUser?.avatar || 'https://trae-api-sg.mchost.guru/api/ide/v1/text_to_image?prompt=poker%20player%20avatar%20portrait&image_size=square'"
                  :alt="userStore.currentUser?.username"
                  class="w-24 h-24 rounded-full border-4 border-yellow-500"
                />
                <button
                  @click="showAvatarUpload = true"
                  class="absolute bottom-0 right-0 bg-yellow-500 text-green-900 rounded-full p-2 hover:bg-yellow-400 transition-colors"
                >
                  <Camera class="w-4 h-4" />
                </button>
              </div>
              <h2 class="text-white text-2xl font-bold mb-2">{{ userStore.currentUser?.username }}</h2>
              <div class="flex items-center justify-center space-x-2 mb-4">
                <Coins class="w-5 h-5 text-yellow-500" />
                <span class="text-yellow-500 font-bold text-lg">余额: {{ userStore.currentUser?.balance?.toLocaleString() || 0 }}</span>
              </div>
              <div class="grid grid-cols-2 gap-4 text-center">
                <div>
                  <div class="text-2xl font-bold text-green-400">{{ userStore.currentUser?.borrow_times || 0 }}</div>
                  <div class="text-gray-300 text-sm">借码次数</div>
                </div>
                <div>
                  <div class="text-2xl font-bold text-white">{{ userStore.currentUser?.isAdmin ? '管理员' : '玩家' }}</div>
                  <div class="text-gray-300 text-sm">用户类型</div>
                </div>
              </div>
            </div>
          </div>

          <!-- 快捷操作 -->
          <div class="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20">
            <h3 class="text-white text-lg font-bold mb-4">快捷操作</h3>
            <div class="space-y-3">
              <button
                @click="router.push('/recharge')"
                class="w-full bg-gradient-to-r from-green-600 to-green-700 text-white font-bold py-3 px-4 rounded-lg hover:from-green-500 hover:to-green-600 transition-all flex items-center justify-center"
              >
                <CreditCard class="w-5 h-5 mr-2" />
                充值筹码
              </button>
              <button
                @click="handleBorrow"
                :disabled="borrowing"
                class="w-full bg-gradient-to-r from-yellow-600 to-yellow-700 text-white font-bold py-3 px-4 rounded-lg hover:from-yellow-500 hover:to-yellow-600 transition-all flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Coins class="w-5 h-5 mr-2" />
                {{ borrowing ? '借码中...' : '借码' }}
              </button>
              <button
                @click="showPasswordChange = true"
                class="w-full bg-white/20 text-white font-bold py-3 px-4 rounded-lg hover:bg-white/30 transition-all flex items-center justify-center border border-white/30"
              >
                <Lock class="w-5 h-5 mr-2" />
                修改密码
              </button>
              <button
                @click="logout"
                class="w-full bg-red-600 text-white font-bold py-3 px-4 rounded-lg hover:bg-red-500 transition-all flex items-center justify-center"
              >
                <LogOut class="w-5 h-5 mr-2" />
                退出登录
              </button>
            </div>
          </div>
        </div>

        <!-- 右侧详细信息 -->
        <div class="lg:col-span-2 space-y-6">
          <!-- 统计图表 -->
          <div class="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20">
            <h3 class="text-white text-xl font-bold mb-6">游戏统计</h3>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
              <div class="text-center">
                <div class="text-3xl font-bold text-green-400 mb-2">+{{ totalWinnings.toLocaleString() }}</div>
                <div class="text-gray-300">总盈利</div>
              </div>
              <div class="text-center">
                <div class="text-3xl font-bold text-yellow-500 mb-2">{{ averagePot.toLocaleString() }}</div>
                <div class="text-gray-300">平均底池</div>
              </div>
              <div class="text-center">
                <div class="text-3xl font-bold text-blue-400 mb-2">{{ playTime }}h</div>
                <div class="text-gray-300">游戏时长</div>
              </div>
            </div>
            
            <!-- 简单的图表展示 -->
            <div class="bg-white/5 rounded-lg p-4">
              <h4 class="text-white font-medium mb-4">最近7天盈亏</h4>
              <div class="flex items-end justify-between h-32 space-x-2">
                <div
                  v-for="(day, index) in weeklyData"
                  :key="index"
                  class="flex-1 flex flex-col items-center"
                >
                  <div
                    :class="[
                      'w-full rounded-t transition-all',
                      day.profit >= 0 ? 'bg-green-500' : 'bg-red-500'
                    ]"
                    :style="{ height: `${Math.abs(day.profit) / 1000 * 80 + 10}px` }"
                  ></div>
                  <div class="text-xs text-gray-300 mt-2">{{ day.day }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- 游戏历史 -->
          <div class="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20">
            <div class="flex items-center justify-between mb-6">
              <h3 class="text-white text-xl font-bold">游戏历史</h3>
              <button
                @click="loadGameHistory"
                class="text-gray-300 hover:text-white transition-colors"
              >
                <RefreshCw class="w-5 h-5" />
              </button>
            </div>
            
            <div class="overflow-x-auto">
              <table class="w-full">
                <thead>
                  <tr class="border-b border-white/20">
                    <th class="text-left text-gray-300 py-3">时间</th>
                    <th class="text-left text-gray-300 py-3">房间</th>
                    <th class="text-left text-gray-300 py-3">盲注</th>
                    <th class="text-left text-gray-300 py-3">结果</th>
                    <th class="text-right text-gray-300 py-3">盈亏</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="game in gameHistory"
                    :key="game.id"
                    class="border-b border-white/10 hover:bg-white/5 transition-colors"
                  >
                    <td class="text-white py-3">{{ formatDate(game.timestamp) }}</td>
                    <td class="text-white py-3">{{ game.roomName }}</td>
                    <td class="text-gray-300 py-3">{{ game.blinds }}</td>
                    <td class="py-3">
                      <span
                        :class="[
                          'px-2 py-1 rounded-full text-xs font-medium',
                          game.result === 'win' ? 'bg-green-600 text-white' :
                          game.result === 'lose' ? 'bg-red-600 text-white' :
                          'bg-gray-600 text-white'
                        ]"
                      >
                        {{ game.result === 'win' ? '胜利' : game.result === 'lose' ? '失败' : '平局' }}
                      </span>
                    </td>
                    <td
                      :class="[
                        'text-right py-3 font-bold',
                        game.profit >= 0 ? 'text-green-400' : 'text-red-400'
                      ]"
                    >
                      {{ game.profit >= 0 ? '+' : '' }}{{ game.profit.toLocaleString() }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 修改密码弹窗 -->
    <div v-if="showPasswordChange" class="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div class="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20 w-full max-w-md">
        <h3 class="text-white text-xl font-bold mb-4">修改密码</h3>
        <form @submit.prevent="changePassword" class="space-y-4">
          <div>
            <label class="block text-white text-sm font-medium mb-2">当前密码</label>
            <input
              v-model="passwordForm.current"
              type="password"
              required
              class="w-full px-4 py-2 bg-white/20 border border-white/30 rounded-lg text-white placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-yellow-500"
              placeholder="请输入当前密码"
            />
          </div>
          <div>
            <label class="block text-white text-sm font-medium mb-2">新密码</label>
            <input
              v-model="passwordForm.new"
              type="password"
              required
              class="w-full px-4 py-2 bg-white/20 border border-white/30 rounded-lg text-white placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-yellow-500"
              placeholder="请输入新密码"
            />
          </div>
          <div>
            <label class="block text-white text-sm font-medium mb-2">确认新密码</label>
            <input
              v-model="passwordForm.confirm"
              type="password"
              required
              class="w-full px-4 py-2 bg-white/20 border border-white/30 rounded-lg text-white placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-yellow-500"
              placeholder="请再次输入新密码"
            />
          </div>
          <div class="flex space-x-4">
            <button
              type="button"
              @click="showPasswordChange = false"
              class="flex-1 bg-gray-600 text-white font-bold py-2 px-4 rounded-lg hover:bg-gray-500 transition-colors"
            >
              取消
            </button>
            <button
              type="submit"
              class="flex-1 bg-gradient-to-r from-yellow-500 to-yellow-600 text-green-900 font-bold py-2 px-4 rounded-lg hover:from-yellow-400 hover:to-yellow-500 transition-all"
            >
              确认
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 头像上传弹窗 -->
    <div v-if="showAvatarUpload" class="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div class="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20 w-full max-w-md">
        <h3 class="text-white text-xl font-bold mb-4">更换头像</h3>
        <div class="text-center">
          <div class="mb-4">
            <img
              :src="userStore.currentUser?.avatar || 'https://trae-api-sg.mchost.guru/api/ide/v1/text_to_image?prompt=poker%20player%20avatar%20portrait&image_size=square'"
              :alt="userStore.currentUser?.username"
              class="w-24 h-24 rounded-full border-4 border-yellow-500 mx-auto"
            />
          </div>
          <p class="text-gray-300 text-sm mb-4">点击下方按钮生成新头像</p>
          <div class="flex space-x-4">
            <button
              type="button"
              @click="showAvatarUpload = false"
              class="flex-1 bg-gray-600 text-white font-bold py-2 px-4 rounded-lg hover:bg-gray-500 transition-colors"
            >
              取消
            </button>
            <button
              @click="generateNewAvatar"
              class="flex-1 bg-gradient-to-r from-yellow-500 to-yellow-600 text-green-900 font-bold py-2 px-4 rounded-lg hover:from-yellow-400 hover:to-yellow-500 transition-all"
            >
              生成新头像
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  ArrowLeft, Spade, Coins, Camera, Star, CreditCard, Lock, LogOut, RefreshCw
} from 'lucide-vue-next'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()

const showPasswordChange = ref(false)
const showAvatarUpload = ref(false)
const borrowing = ref(false)

const passwordForm = reactive({
  current: '',
  new: '',
  confirm: ''
})

// 模拟数据
const totalWinnings = ref(15420)
const averagePot = ref(850)
const playTime = ref(127)

const weeklyData = ref([
  { day: '周一', profit: 500 },
  { day: '周二', profit: -200 },
  { day: '周三', profit: 800 },
  { day: '周四', profit: 300 },
  { day: '周五', profit: -150 },
  { day: '周六', profit: 1200 },
  { day: '周日', profit: 600 }
])

const gameHistory = ref([
  {
    id: 1,
    timestamp: new Date(Date.now() - 3600000),
    roomName: '新手桌',
    blinds: '10/20',
    result: 'win',
    profit: 450
  },
  {
    id: 2,
    timestamp: new Date(Date.now() - 7200000),
    roomName: '中级桌',
    blinds: '25/50',
    result: 'lose',
    profit: -300
  },
  {
    id: 3,
    timestamp: new Date(Date.now() - 10800000),
    roomName: '高级桌',
    blinds: '50/100',
    result: 'win',
    profit: 1200
  },
  {
    id: 4,
    timestamp: new Date(Date.now() - 14400000),
    roomName: '新手桌',
    blinds: '10/20',
    result: 'tie',
    profit: 0
  }
])

const formatDate = (date: Date) => {
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const changePassword = () => {
  if (passwordForm.new !== passwordForm.confirm) {
    alert('两次输入的新密码不一致')
    return
  }
  
  // 模拟密码修改
  alert('密码修改成功')
  showPasswordChange.value = false
  
  // 重置表单
  Object.assign(passwordForm, {
    current: '',
    new: '',
    confirm: ''
  })
}

const handleBorrow = async () => {
  if (borrowing.value) return
  
  try {
    borrowing.value = true
    await userStore.borrowChips()
    alert('借码成功！')
  } catch (error: any) {
    alert(error.message || '借码失败，请重试')
  } finally {
    borrowing.value = false
  }
}

const generateNewAvatar = () => {
  // 生成新的头像URL
  const avatarPrompts = [
    'professional%20poker%20player%20avatar',
    'casual%20poker%20player%20avatar',
    'elegant%20poker%20player%20avatar',
    'modern%20poker%20player%20avatar'
  ]
  const randomPrompt = avatarPrompts[Math.floor(Math.random() * avatarPrompts.length)]
  const newAvatarUrl = `https://trae-api-sg.mchost.guru/api/ide/v1/text_to_image?prompt=${randomPrompt}&image_size=square`
  
  if (userStore.currentUser) {
    userStore.currentUser.avatar = newAvatarUrl
    localStorage.setItem('user', JSON.stringify(userStore.currentUser))
  }
  
  showAvatarUpload.value = false
}

const loadGameHistory = () => {
  // 模拟加载游戏历史
  console.log('加载游戏历史')
}

const logout = () => {
  userStore.logout()
  router.push('/login')
}

onMounted(() => {
  // 初始化数据
})
</script>