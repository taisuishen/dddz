<template>
  <div class="min-h-screen bg-gradient-to-br from-green-900 via-green-800 to-green-700">
    <!-- 顶部导航栏 -->
    <header class="bg-green-900/50 backdrop-blur-md border-b border-green-700">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <!-- Logo -->
          <div class="flex items-center">
            <Spade class="w-8 h-8 text-yellow-500 mr-2" />
            <span class="text-white font-bold text-xl">德州扑克</span>
          </div>

          <!-- 用户信息 -->
          <div class="flex items-center space-x-4">
            <div class="flex items-center space-x-2">
              <Coins class="w-5 h-5 text-yellow-500" />
              <span class="text-yellow-500 font-bold">{{ userStore.user?.chips?.toLocaleString() || '0' }}</span>
            </div>
            <div class="flex items-center space-x-2">
              <img
                :src="userStore.user?.avatar"
                :alt="userStore.user?.username"
                class="w-8 h-8 rounded-full"
              />
              <span class="text-white">{{ userStore.user?.username }}</span>
            </div>
            <button
              @click="logout"
              class="text-gray-300 hover:text-white transition-colors"
            >
              <LogOut class="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </header>

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="grid grid-cols-1 lg:grid-cols-4 gap-8">
        <!-- 左侧主要内容 -->
        <div class="lg:col-span-3 space-y-6">
          <!-- 快速操作区 -->
          <div class="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20">
            <h2 class="text-white text-xl font-bold mb-4">快速开始</h2>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <button
                @click="quickMatch"
                :disabled="loading"
                class="bg-gradient-to-r from-yellow-500 to-yellow-600 text-green-900 font-bold py-4 px-6 rounded-xl hover:from-yellow-400 hover:to-yellow-500 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
              >
                <Zap class="w-5 h-5 mr-2" />
                快速匹配
              </button>
              <button
                @click="showCreateRoom = true"
                class="bg-white/20 text-white font-bold py-4 px-6 rounded-xl hover:bg-white/30 transition-all flex items-center justify-center border border-white/30"
              >
                <Plus class="w-5 h-5 mr-2" />
                创建房间
              </button>
              <button
                @click="router.push('/profile')"
                class="bg-white/20 text-white font-bold py-4 px-6 rounded-xl hover:bg-white/30 transition-all flex items-center justify-center border border-white/30"
              >
                <User class="w-5 h-5 mr-2" />
                个人中心
              </button>
            </div>
          </div>

          <!-- 房间列表 -->
          <div class="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20">
            <div class="flex items-center justify-between mb-6">
              <h2 class="text-white text-xl font-bold">游戏房间</h2>
              <button
                @click="roomStore.loadRooms()"
                class="text-gray-300 hover:text-white transition-colors"
              >
                <RefreshCw class="w-5 h-5" />
              </button>
            </div>

            <div v-if="roomStore.rooms.length === 0" class="text-center py-8">
              <div class="text-gray-400 text-lg mb-2">暂无房间</div>
              <div class="text-gray-500 text-sm">点击"创建房间"开始游戏</div>
            </div>
            <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div
                v-for="room in roomStore.rooms"
                :key="room.id"
                class="bg-white/10 rounded-xl p-4 border border-white/20 hover:bg-white/20 transition-all relative"
              >
                <div class="flex items-center justify-between mb-3">
                  <h3 class="text-white font-bold cursor-pointer" @click="joinRoom(room)">{{ room.name }}</h3>
                  <div class="flex items-center space-x-2">
                    <Lock v-if="room.isPrivate" class="w-4 h-4 text-gray-400" />
                    <span
                      :class="[
                        'px-2 py-1 rounded-full text-xs font-medium',
                        room.status === 'waiting' ? 'bg-green-500 text-white' :
                        room.status === 'playing' ? 'bg-yellow-500 text-green-900' :
                        'bg-red-500 text-white'
                      ]"
                    >
                      {{ room.status === 'waiting' ? '等待中' : room.status === 'playing' ? '游戏中' : '已满' }}
                    </span>
                    <button
                      v-if="userStore.isAdmin || (userStore.user && room.created_by === parseInt(userStore.user.id))"
                      @click.stop="deleteRoom(room)"
                      class="text-red-400 hover:text-red-300 transition-colors"
                      title="删除房间"
                    >
                      <X class="w-4 h-4" />
                    </button>
                  </div>
                </div>

                <div class="grid grid-cols-2 gap-4 text-sm cursor-pointer" @click="joinRoom(room)">
                  <div class="text-gray-300">
                    <Users class="w-4 h-4 inline mr-1" />
                    {{ room.current_players || room.playerCount || 0 }}/{{ room.max_players || room.maxPlayers }}
                  </div>
                  <div class="text-gray-300">
                    <Coins class="w-4 h-4 inline mr-1" />
                    {{ room.small_blind || room.smallBlind }}/{{ room.big_blind || room.bigBlind }}
                  </div>
                  <div class="text-gray-300">
                    买入: {{ ((room.min_buy_in || room.minBuyIn || 0)).toLocaleString() }}
                  </div>
                  <div class="text-gray-300">
                    最大: {{ ((room.max_buy_in || room.maxBuyIn || 0)).toLocaleString() }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 右侧边栏 -->
        <div class="space-y-6">
          <!-- 个人统计 -->
          <div class="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20">
            <h3 class="text-white text-lg font-bold mb-4">个人统计</h3>
            <div class="space-y-3">
              <div class="flex justify-between">
                <span class="text-gray-300">等级</span>
                <span class="text-yellow-500 font-bold">Lv.{{ userStore.user?.level }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-300">胜率</span>
                <span class="text-green-400 font-bold">{{ userStore.user?.winRate }}%</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-300">总局数</span>
                <span class="text-white">{{ userStore.user?.totalGames }}</span>
              </div>
            </div>
          </div>

          <!-- 在线玩家 -->
          <div class="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20">
            <h3 class="text-white text-lg font-bold mb-4">在线玩家</h3>
            <div class="text-center text-yellow-500 text-2xl font-bold">
              {{ onlineCount }}
            </div>
            <div class="text-center text-gray-300 text-sm mt-1">
              当前在线
            </div>
          </div>

          <!-- 快捷操作 -->
          <div class="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20">
            <h3 class="text-white text-lg font-bold mb-4">快捷操作</h3>
            <div class="space-y-3">
              <button
                @click="router.push('/recharge')"
                class="w-full bg-gradient-to-r from-green-600 to-green-700 text-white font-bold py-2 px-4 rounded-lg hover:from-green-500 hover:to-green-600 transition-all flex items-center justify-center"
              >
                <CreditCard class="w-4 h-4 mr-2" />
                充值筹码
              </button>
              <button
                v-if="userStore.isAdmin"
                @click="router.push('/admin')"
                class="w-full bg-gradient-to-r from-purple-600 to-purple-700 text-white font-bold py-2 px-4 rounded-lg hover:from-purple-500 hover:to-purple-600 transition-all flex items-center justify-center"
              >
                <Settings class="w-4 h-4 mr-2" />
                后台管理
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 创建房间弹窗 -->
    <div v-if="showCreateRoom" class="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div class="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20 w-full max-w-md">
        <h3 class="text-white text-xl font-bold mb-4">创建房间</h3>
        <form @submit.prevent="createRoom" class="space-y-4">
          <div>
            <label class="block text-white text-sm font-medium mb-2">房间名称</label>
            <input
              v-model="newRoom.name"
              type="text"
              required
              class="w-full px-4 py-2 bg-white/20 border border-white/30 rounded-lg text-white placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-yellow-500"
              placeholder="请输入房间名称"
            />
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-white text-sm font-medium mb-2">小盲注</label>
              <input
                v-model.number="newRoom.smallBlind"
                type="number"
                required
                min="1"
                class="w-full px-4 py-2 bg-white/20 border border-white/30 rounded-lg text-white placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-yellow-500"
              />
            </div>
            <div>
              <label class="block text-white text-sm font-medium mb-2">大盲注</label>
              <input
                v-model.number="newRoom.bigBlind"
                type="number"
                required
                min="2"
                class="w-full px-4 py-2 bg-white/20 border border-white/30 rounded-lg text-white placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-yellow-500"
              />
            </div>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-white text-sm font-medium mb-2">最小买入</label>
              <input
                v-model.number="newRoom.minBuyIn"
                type="number"
                required
                min="100"
                class="w-full px-4 py-2 bg-white/20 border border-white/30 rounded-lg text-white placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-yellow-500"
              />
            </div>
            <div>
              <label class="block text-white text-sm font-medium mb-2">最大买入</label>
              <input
                v-model.number="newRoom.maxBuyIn"
                type="number"
                required
                min="1000"
                class="w-full px-4 py-2 bg-white/20 border border-white/30 rounded-lg text-white placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-yellow-500"
              />
            </div>
          </div>
          <div>
            <label class="block text-white text-sm font-medium mb-2">最大玩家数</label>
            <select
              v-model.number="newRoom.maxPlayers"
              class="w-full px-4 py-2 bg-white/20 border border-white/30 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
            >
              <option value="2">2人</option>
              <option value="4">4人</option>
              <option value="6">6人</option>
              <option value="8">8人</option>
              <option value="9">9人</option>
            </select>
          </div>
          <div class="flex items-center">
            <input
              v-model="newRoom.isPrivate"
              type="checkbox"
              id="private"
              class="mr-2"
            />
            <label for="private" class="text-white text-sm">私人房间</label>
          </div>
          <div v-if="newRoom.isPrivate">
            <label class="block text-white text-sm font-medium mb-2">房间密码</label>
            <input
              v-model="newRoom.password"
              type="password"
              class="w-full px-4 py-2 bg-white/20 border border-white/30 rounded-lg text-white placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-yellow-500"
              placeholder="请设置房间密码"
            />
          </div>
          <div class="flex space-x-4">
            <button
              type="button"
              @click="showCreateRoom = false"
              class="flex-1 bg-gray-600 text-white font-bold py-2 px-4 rounded-lg hover:bg-gray-500 transition-colors"
            >
              取消
            </button>
            <button
              type="submit"
              class="flex-1 bg-gradient-to-r from-yellow-500 to-yellow-600 text-green-900 font-bold py-2 px-4 rounded-lg hover:from-yellow-400 hover:to-yellow-500 transition-all"
            >
              创建
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 加入房间密码弹窗 -->
    <div v-if="showPasswordDialog" class="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div class="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20 w-full max-w-sm">
        <h3 class="text-white text-xl font-bold mb-4">输入房间密码</h3>
        <form @submit.prevent="confirmJoinRoom">
          <input
            v-model="roomPassword"
            type="password"
            required
            class="w-full px-4 py-2 bg-white/20 border border-white/30 rounded-lg text-white placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-yellow-500 mb-4"
            placeholder="请输入房间密码"
          />
          <div class="flex space-x-4">
            <button
              type="button"
              @click="showPasswordDialog = false"
              class="flex-1 bg-gray-600 text-white font-bold py-2 px-4 rounded-lg hover:bg-gray-500 transition-colors"
            >
              取消
            </button>
            <button
              type="submit"
              class="flex-1 bg-gradient-to-r from-yellow-500 to-yellow-600 text-green-900 font-bold py-2 px-4 rounded-lg hover:from-yellow-400 hover:to-yellow-500 transition-all"
            >
              加入
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  Spade, Coins, LogOut, Zap, Plus, User, RefreshCw, Lock, Users,
  CreditCard, Settings, X
} from 'lucide-vue-next'
import { useUserStore } from '../stores/user'
import { useRoomStore, type Room } from '../stores/room'

const router = useRouter()
const userStore = useUserStore()
const roomStore = useRoomStore()

const loading = ref(false)
const showCreateRoom = ref(false)
const showPasswordDialog = ref(false)
const roomPassword = ref('')
const selectedRoom = ref<Room | null>(null)
const onlineCount = ref(0) // 真实在线人数

const newRoom = reactive({
  name: '',
  smallBlind: 10,
  bigBlind: 20,
  minBuyIn: 1000,
  maxBuyIn: 5000,
  maxPlayers: 6,
  isPrivate: false,
  password: ''
})

const logout = () => {
  userStore.logout()
  router.push('/login')
}

const quickMatch = async () => {
  loading.value = true
  try {
    const result = await roomStore.quickMatch()
    if (result.success) {
      router.push(`/game/${roomStore.currentRoom?.id}`)
    } else {
      alert(result.message)
    }
  } finally {
    loading.value = false
  }
}

const joinRoom = async (room: Room) => {
  if (room.status === 'full') {
    alert('房间已满')
    return
  }

  if (room.isPrivate) {
    selectedRoom.value = room
    showPasswordDialog.value = true
    return
  }

  const result = await roomStore.joinRoom(room.id.toString())
  if (result.success) {
    router.push(`/game/${room.id}`)
  } else {
    alert(result.message)
  }
}

const confirmJoinRoom = async () => {
  if (!selectedRoom.value) return

  const result = await roomStore.joinRoom(selectedRoom.value.id.toString(), roomPassword.value)
  if (result.success) {
    router.push(`/game/${selectedRoom.value.id}`)
  } else {
    alert(result.message)
  }
  
  showPasswordDialog.value = false
  roomPassword.value = ''
  selectedRoom.value = null
}

const createRoom = async () => {
  const result = await roomStore.createRoom({
    name: newRoom.name,
    smallBlind: newRoom.smallBlind,
    bigBlind: newRoom.bigBlind,
    maxPlayers: newRoom.maxPlayers,
    isPrivate: newRoom.isPrivate,
    password: newRoom.isPrivate ? newRoom.password : undefined
  })

  if (result.success) {
    showCreateRoom.value = false
    // 重置表单
    Object.assign(newRoom, {
      name: '',
      smallBlind: 10,
      bigBlind: 20,
      minBuyIn: 1000,
      maxBuyIn: 5000,
      maxPlayers: 6,
      isPrivate: false,
      password: ''
    })
    alert(result.message || '房间创建成功')
  } else {
    alert(result.message)
  }
}

const deleteRoom = async (room: Room) => {
  if (!confirm(`确定要删除房间"${room.name}"吗？`)) {
    return
  }

  const result = await roomStore.deleteRoom(room.id.toString())
  if (result.success) {
    alert(result.message || '房间删除成功')
  } else {
    alert(result.message || '删除房间失败')
  }
}

const fetchOnlineCount = async () => {
  try {
    // 计算当前房间中的玩家总数
    let totalPlayers = 0
    roomStore.rooms.forEach(room => {
      totalPlayers += room.current_players || room.playerCount || 0
    })
    onlineCount.value = Math.max(totalPlayers, 1) // 至少显示1个在线用户（当前用户）
  } catch (error) {
    console.error('获取在线人数失败:', error)
    onlineCount.value = 1 // 默认显示1个在线用户
  }
}

onMounted(() => {
  roomStore.loadRooms()
  fetchOnlineCount()
  
  // 每30秒更新一次在线人数
  setInterval(fetchOnlineCount, 30000)
})
</script>