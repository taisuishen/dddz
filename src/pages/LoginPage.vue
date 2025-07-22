<template>
  <div class="min-h-screen bg-gradient-to-br from-green-900 via-green-800 to-green-700 flex items-center justify-center p-4">
    <div class="w-full max-w-md">
      <!-- Logo区域 -->
      <div class="text-center mb-8">
        <div class="inline-flex items-center justify-center w-20 h-20 bg-yellow-500 rounded-full mb-4">
          <Spade class="w-10 h-10 text-green-900" />
        </div>
        <h1 class="text-3xl font-bold text-white mb-2">德州扑克</h1>
        <p class="text-green-200">专业在线多人游戏平台</p>
      </div>

      <!-- 登录/注册表单 -->
      <div class="bg-white/10 backdrop-blur-md rounded-2xl p-6 shadow-2xl border border-white/20">
        <div class="flex mb-6">
          <button
            @click="isLogin = true"
            :class="[
              'flex-1 py-2 px-4 rounded-lg font-medium transition-all',
              isLogin
                ? 'bg-yellow-500 text-green-900 shadow-lg'
                : 'text-white hover:bg-white/10'
            ]"
          >
            登录
          </button>
          <button
            @click="isLogin = false"
            :class="[
              'flex-1 py-2 px-4 rounded-lg font-medium transition-all ml-2',
              !isLogin
                ? 'bg-yellow-500 text-green-900 shadow-lg'
                : 'text-white hover:bg-white/10'
            ]"
          >
            注册
          </button>
        </div>

        <form @submit.prevent="handleSubmit" class="space-y-4">
          <!-- 用户名输入 -->
          <div>
            <label class="block text-white text-sm font-medium mb-2">
              用户名
            </label>
            <div class="relative">
              <User class="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                v-model="form.username"
                type="text"
                required
                class="w-full pl-10 pr-4 py-3 bg-white/20 border border-white/30 rounded-lg text-white placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-transparent"
                placeholder="请输入用户名"
              />
            </div>
          </div>

          <!-- 密码输入 -->
          <div>
            <label class="block text-white text-sm font-medium mb-2">
              密码
            </label>
            <div class="relative">
              <Lock class="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                v-model="form.password"
                :type="showPassword ? 'text' : 'password'"
                required
                class="w-full pl-10 pr-12 py-3 bg-white/20 border border-white/30 rounded-lg text-white placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-transparent"
                placeholder="请输入密码"
              />
              <button
                type="button"
                @click="showPassword = !showPassword"
                class="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-white"
              >
                <Eye v-if="showPassword" class="w-5 h-5" />
                <EyeOff v-else class="w-5 h-5" />
              </button>
            </div>
          </div>

          <!-- 确认密码输入（仅注册时显示） -->
          <div v-if="!isLogin">
            <label class="block text-white text-sm font-medium mb-2">
              确认密码
            </label>
            <div class="relative">
              <Lock class="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                v-model="form.confirmPassword"
                :type="showConfirmPassword ? 'text' : 'password'"
                required
                class="w-full pl-10 pr-12 py-3 bg-white/20 border border-white/30 rounded-lg text-white placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-transparent"
                placeholder="请再次输入密码"
              />
              <button
                type="button"
                @click="showConfirmPassword = !showConfirmPassword"
                class="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-white"
              >
                <Eye v-if="showConfirmPassword" class="w-5 h-5" />
                <EyeOff v-else class="w-5 h-5" />
              </button>
            </div>
          </div>

          <!-- 错误信息 -->
          <div v-if="errorMessage" class="text-red-300 text-sm text-center">
            {{ errorMessage }}
          </div>

          <!-- 提交按钮 -->
          <button
            type="submit"
            :disabled="loading"
            class="w-full bg-gradient-to-r from-yellow-500 to-yellow-600 text-green-900 font-bold py-3 px-4 rounded-lg hover:from-yellow-400 hover:to-yellow-500 focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:ring-offset-2 focus:ring-offset-green-800 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <div v-if="loading" class="flex items-center justify-center">
              <div class="animate-spin rounded-full h-5 w-5 border-b-2 border-green-900 mr-2"></div>
              {{ isLogin ? '登录中...' : '注册中...' }}
            </div>
            <span v-else>{{ isLogin ? '登录' : '注册' }}</span>
          </button>
        </form>

        <!-- 快速登录提示 -->
        <div class="mt-6 text-center">
          <p class="text-green-200 text-sm mb-2">快速体验账号：</p>
          <div class="flex gap-2 justify-center">
            <button
              @click="quickLogin('admin', 'admin')"
              class="px-3 py-1 bg-white/20 text-white text-xs rounded hover:bg-white/30 transition-colors"
            >
              管理员
            </button>
            <button
              @click="quickLogin('player1', '123456')"
              class="px-3 py-1 bg-white/20 text-white text-xs rounded hover:bg-white/30 transition-colors"
            >
              玩家
            </button>
          </div>
        </div>
      </div>

      <!-- 底部链接 -->
      <div class="text-center mt-6">
        <a href="#" class="text-green-200 hover:text-white text-sm transition-colors">
          忘记密码？
        </a>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { Spade, User, Lock, Eye, EyeOff } from 'lucide-vue-next'
import { useUserStore } from '../stores/user'
import { connectWebSocket } from '../utils/websocket'

const router = useRouter()
const userStore = useUserStore()

const isLogin = ref(true)
const loading = ref(false)
const errorMessage = ref('')
const showPassword = ref(false)
const showConfirmPassword = ref(false)

const form = reactive({
  username: '',
  password: '',
  confirmPassword: ''
})

const handleSubmit = async () => {
  errorMessage.value = ''
  loading.value = true

  try {
    if (isLogin.value) {
      const result = await userStore.login(form.username, form.password)
      if (result.success) {
        // 登录成功后建立WebSocket连接
        await connectWebSocket()
        router.push('/lobby')
      } else {
        errorMessage.value = result.message || '登录失败'
      }
    } else {
      // 验证密码确认
      if (form.password !== form.confirmPassword) {
        errorMessage.value = '两次输入的密码不一致'
        return
      }
      
      const result = await userStore.register({
        username: form.username,
        email: form.username + '@example.com', // 临时使用用户名作为邮箱前缀
        password: form.password
      })
      if (result.success) {
        isLogin.value = true
        form.password = ''
        form.confirmPassword = ''
        errorMessage.value = ''
        // 可以显示成功消息
      } else {
        errorMessage.value = '注册失败'
      }
    }
  } catch (error) {
    errorMessage.value = '网络错误，请重试'
  } finally {
    loading.value = false
  }
}

const quickLogin = async (username: string, password: string) => {
  form.username = username
  form.password = password
  isLogin.value = true // 确保是登录模式
  await handleSubmit()
}
</script>