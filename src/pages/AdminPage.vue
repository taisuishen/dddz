<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-700">
    <!-- 顶部导航栏 -->
    <header class="bg-gray-900/50 backdrop-blur-md border-b border-gray-700">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <div class="flex items-center">
            <button
              @click="router.push('/lobby')"
              class="text-gray-300 hover:text-white transition-colors mr-4"
            >
              <ArrowLeft class="w-5 h-5" />
            </button>
            <Shield class="w-8 h-8 text-blue-500 mr-2" />
            <span class="text-white font-bold text-xl">后台管理</span>
          </div>
          <div class="flex items-center space-x-4">
            <span class="text-gray-300">管理员：{{ userStore.user?.username }}</span>
          </div>
        </div>
      </div>
    </header>

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- 统计卡片 -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div class="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-gray-300 text-sm">在线用户</p>
              <p class="text-white text-2xl font-bold">{{ stats.onlineUsers }}</p>
            </div>
            <Users class="w-8 h-8 text-blue-500" />
          </div>
        </div>
        
        <div class="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-gray-300 text-sm">活跃房间</p>
              <p class="text-white text-2xl font-bold">{{ stats.activeRooms }}</p>
            </div>
            <Home class="w-8 h-8 text-green-500" />
          </div>
        </div>
        
        <div class="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-gray-300 text-sm">今日收入</p>
              <p class="text-white text-2xl font-bold">¥{{ stats.todayRevenue.toLocaleString() }}</p>
            </div>
            <DollarSign class="w-8 h-8 text-yellow-500" />
          </div>
        </div>
        
        <div class="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-gray-300 text-sm">总用户数</p>
              <p class="text-white text-2xl font-bold">{{ stats.totalUsers }}</p>
            </div>
            <UserCheck class="w-8 h-8 text-purple-500" />
          </div>
        </div>
      </div>

      <!-- 主要内容区域 -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- 左侧管理功能 -->
        <div class="lg:col-span-2 space-y-6">
          <!-- 用户管理 -->
          <div class="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20">
            <div class="flex items-center justify-between mb-6">
              <h2 class="text-white text-xl font-bold">用户管理</h2>
              <div class="flex space-x-2">
                <button
                  @click="refreshUsers"
                  class="text-gray-300 hover:text-white transition-colors"
                >
                  <RefreshCw class="w-5 h-5" />
                </button>
                <button
                  @click="showAddUser = true"
                  class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
                >
                  添加用户
                </button>
              </div>
            </div>
            
            <!-- 搜索栏 -->
            <div class="mb-4">
              <div class="relative">
                <Search class="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  v-model="userSearch"
                  type="text"
                  placeholder="搜索用户名或ID"
                  class="w-full pl-10 pr-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                />
              </div>
            </div>
            
            <!-- 用户列表 -->
            <div class="overflow-x-auto">
              <table class="w-full">
                <thead>
                  <tr class="border-b border-white/20">
                    <th class="text-left text-gray-300 py-3">用户ID</th>
                    <th class="text-left text-gray-300 py-3">用户名</th>
                    <th class="text-left text-gray-300 py-3">筹码</th>
                    <th class="text-left text-gray-300 py-3">状态</th>
                    <th class="text-left text-gray-300 py-3">操作</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="user in filteredUsers"
                    :key="user.id"
                    class="border-b border-white/10 hover:bg-white/5 transition-colors"
                  >
                    <td class="text-white py-3">#{{ user.id }}</td>
                    <td class="text-white py-3">{{ user.username }}</td>
                    <td class="text-yellow-500 py-3 font-bold">{{ user.chips.toLocaleString() }}</td>
                    <td class="py-3">
                      <span
                        :class="[
                          'px-2 py-1 rounded-full text-xs font-medium',
                          user.status === 'online' ? 'bg-green-600 text-white' :
                          user.status === 'offline' ? 'bg-gray-600 text-white' :
                          'bg-red-600 text-white'
                        ]"
                      >
                        {{ getStatusText(user.status) }}
                      </span>
                    </td>
                    <td class="py-3">
                      <div class="flex space-x-2">
                        <button
                          @click="editUser(user)"
                          class="text-blue-400 hover:text-blue-300 transition-colors"
                        >
                          <Edit class="w-4 h-4" />
                        </button>
                        <button
                          @click="banUser(user)"
                          class="text-red-400 hover:text-red-300 transition-colors"
                        >
                          <Ban class="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- 房间管理 -->
          <div class="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20">
            <div class="flex items-center justify-between mb-6">
              <h2 class="text-white text-xl font-bold">房间管理</h2>
              <button
                @click="refreshRooms"
                class="text-gray-300 hover:text-white transition-colors"
              >
                <RefreshCw class="w-5 h-5" />
              </button>
            </div>
            
            <div class="overflow-x-auto">
              <table class="w-full">
                <thead>
                  <tr class="border-b border-white/20">
                    <th class="text-left text-gray-300 py-3">房间ID</th>
                    <th class="text-left text-gray-300 py-3">房间名</th>
                    <th class="text-left text-gray-300 py-3">玩家数</th>
                    <th class="text-left text-gray-300 py-3">盲注</th>
                    <th class="text-left text-gray-300 py-3">状态</th>
                    <th class="text-left text-gray-300 py-3">操作</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="room in rooms"
                    :key="room.id"
                    class="border-b border-white/10 hover:bg-white/5 transition-colors"
                  >
                    <td class="text-white py-3">#{{ room.id }}</td>
                    <td class="text-white py-3">{{ room.name }}</td>
                    <td class="text-white py-3">{{ room.currentPlayers }}/{{ room.maxPlayers }}</td>
                    <td class="text-white py-3">{{ room.smallBlind }}/{{ room.bigBlind }}</td>
                    <td class="py-3">
                      <span
                        :class="[
                          'px-2 py-1 rounded-full text-xs font-medium',
                          room.status === 'playing' ? 'bg-green-600 text-white' :
                          room.status === 'waiting' ? 'bg-yellow-600 text-white' :
                          'bg-gray-600 text-white'
                        ]"
                      >
                        {{ getRoomStatusText(room.status) }}
                      </span>
                    </td>
                    <td class="py-3">
                      <div class="flex space-x-2">
                        <button
                          @click="viewRoom(room)"
                          class="text-blue-400 hover:text-blue-300 transition-colors"
                        >
                          <Eye class="w-4 h-4" />
                        </button>
                        <button
                          @click="closeRoom(room)"
                          class="text-red-400 hover:text-red-300 transition-colors"
                        >
                          <X class="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- 右侧系统信息 -->
        <div class="space-y-6">
          <!-- 系统状态 -->
          <div class="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20">
            <h3 class="text-white text-lg font-bold mb-4">系统状态</h3>
            <div class="space-y-4">
              <div class="flex justify-between">
                <span class="text-gray-300">服务器状态</span>
                <span class="text-green-400 font-bold">正常</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-300">CPU使用率</span>
                <span class="text-white">45%</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-300">内存使用率</span>
                <span class="text-white">62%</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-300">数据库连接</span>
                <span class="text-green-400 font-bold">正常</span>
              </div>
            </div>
          </div>

          <!-- 最近活动 -->
          <div class="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20">
            <h3 class="text-white text-lg font-bold mb-4">最近活动</h3>
            <div class="space-y-3">
              <div
                v-for="activity in recentActivities"
                :key="activity.id"
                class="flex items-start space-x-3"
              >
                <div class="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
                <div>
                  <p class="text-white text-sm">{{ activity.message }}</p>
                  <p class="text-gray-400 text-xs">{{ formatTime(activity.timestamp) }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- 快速操作 -->
          <div class="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20">
            <h3 class="text-white text-lg font-bold mb-4">快速操作</h3>
            <div class="space-y-3">
              <button
                @click="sendSystemMessage"
                class="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-lg transition-colors"
              >
                发送系统消息
              </button>
              <button
                @click="exportData"
                class="w-full bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded-lg transition-colors"
              >
                导出数据
              </button>
              <button
                @click="clearLogs"
                class="w-full bg-red-600 hover:bg-red-700 text-white py-2 px-4 rounded-lg transition-colors"
              >
                清理日志
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加用户模态框 -->
    <div
      v-if="showAddUser"
      class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50"
      @click="showAddUser = false"
    >
      <div
        class="bg-gray-800 rounded-2xl p-6 w-full max-w-md mx-4"
        @click.stop
      >
        <h3 class="text-white text-xl font-bold mb-4">添加用户</h3>
        <form @submit.prevent="addUser" class="space-y-4">
          <div>
            <label class="block text-gray-300 text-sm mb-2">用户名</label>
            <input
              v-model="newUser.username"
              type="text"
              required
              class="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
              placeholder="输入用户名"
            />
          </div>
          <div>
            <label class="block text-gray-300 text-sm mb-2">密码</label>
            <input
              v-model="newUser.password"
              type="password"
              required
              class="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
              placeholder="输入密码"
            />
          </div>
          <div>
            <label class="block text-gray-300 text-sm mb-2">初始筹码</label>
            <input
              v-model="newUser.chips"
              type="number"
              required
              min="0"
              class="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
              placeholder="输入初始筹码"
            />
          </div>
          <div class="flex space-x-3">
            <button
              type="button"
              @click="showAddUser = false"
              class="flex-1 bg-gray-600 hover:bg-gray-700 text-white py-2 px-4 rounded-lg transition-colors"
            >
              取消
            </button>
            <button
              type="submit"
              class="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-lg transition-colors"
            >
              添加
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  ArrowLeft, Shield, Users, Home, DollarSign, UserCheck,
  RefreshCw, Search, Edit, Ban, Eye, X
} from 'lucide-vue-next'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()

// 统计数据
const stats = reactive({
  onlineUsers: 156,
  activeRooms: 23,
  todayRevenue: 12580,
  totalUsers: 2847
})

// 用户管理
const userSearch = ref('')
const showAddUser = ref(false)
const newUser = reactive({
  username: '',
  password: '',
  chips: 1000
})

const users = ref([
  {
    id: 1,
    username: 'player1',
    chips: 5000,
    status: 'online'
  },
  {
    id: 2,
    username: 'player2',
    chips: 3200,
    status: 'offline'
  },
  {
    id: 3,
    username: 'player3',
    chips: 8500,
    status: 'online'
  },
  {
    id: 4,
    username: 'player4',
    chips: 1200,
    status: 'banned'
  }
])

const filteredUsers = computed(() => {
  if (!userSearch.value) return users.value
  return users.value.filter(user => 
    user.username.toLowerCase().includes(userSearch.value.toLowerCase()) ||
    user.id.toString().includes(userSearch.value)
  )
})

// 房间管理
const rooms = ref([
  {
    id: 1,
    name: '新手房间',
    currentPlayers: 4,
    maxPlayers: 6,
    smallBlind: 10,
    bigBlind: 20,
    status: 'playing'
  },
  {
    id: 2,
    name: '高级房间',
    currentPlayers: 2,
    maxPlayers: 8,
    smallBlind: 50,
    bigBlind: 100,
    status: 'waiting'
  },
  {
    id: 3,
    name: 'VIP房间',
    currentPlayers: 6,
    maxPlayers: 6,
    smallBlind: 100,
    bigBlind: 200,
    status: 'playing'
  }
])

// 最近活动
const recentActivities = ref([
  {
    id: 1,
    message: '用户 player1 加入了房间 #1',
    timestamp: new Date(Date.now() - 300000)
  },
  {
    id: 2,
    message: '房间 #2 游戏结束',
    timestamp: new Date(Date.now() - 600000)
  },
  {
    id: 3,
    message: '用户 player3 充值 ¥50',
    timestamp: new Date(Date.now() - 900000)
  },
  {
    id: 4,
    message: '系统维护完成',
    timestamp: new Date(Date.now() - 1800000)
  }
])

const getStatusText = (status: string) => {
  const statusTexts = {
    online: '在线',
    offline: '离线',
    banned: '封禁'
  }
  return statusTexts[status as keyof typeof statusTexts] || status
}

const getRoomStatusText = (status: string) => {
  const statusTexts = {
    playing: '游戏中',
    waiting: '等待中',
    closed: '已关闭'
  }
  return statusTexts[status as keyof typeof statusTexts] || status
}

const formatTime = (date: Date) => {
  return date.toLocaleString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

const refreshUsers = () => {
  console.log('刷新用户列表')
}

const editUser = (user: any) => {
  console.log('编辑用户:', user)
}

const banUser = (user: any) => {
  if (confirm(`确定要封禁用户 ${user.username} 吗？`)) {
    user.status = 'banned'
    console.log('封禁用户:', user)
  }
}

const addUser = () => {
  const user = {
    id: Date.now(),
    username: newUser.username,
    chips: newUser.chips,
    status: 'offline'
  }
  users.value.push(user)
  
  // 重置表单
  newUser.username = ''
  newUser.password = ''
  newUser.chips = 1000
  showAddUser.value = false
  
  console.log('添加用户:', user)
}

const refreshRooms = () => {
  console.log('刷新房间列表')
}

const viewRoom = (room: any) => {
  console.log('查看房间:', room)
}

const closeRoom = (room: any) => {
  if (confirm(`确定要关闭房间 ${room.name} 吗？`)) {
    room.status = 'closed'
    console.log('关闭房间:', room)
  }
}

const sendSystemMessage = () => {
  const message = prompt('请输入系统消息:')
  if (message) {
    console.log('发送系统消息:', message)
    alert('系统消息已发送')
  }
}

const exportData = () => {
  console.log('导出数据')
  alert('数据导出功能开发中')
}

const clearLogs = () => {
  if (confirm('确定要清理日志吗？')) {
    console.log('清理日志')
    alert('日志已清理')
  }
}

onMounted(() => {
  // 检查管理员权限
  if (!userStore.user?.isAdmin) {
    alert('无权限访问')
    router.push('/lobby')
  }
})
</script>