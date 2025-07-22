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
            <span class="text-white font-bold text-xl">充值中心</span>
          </div>
          <div class="flex items-center space-x-4">
            <div class="flex items-center space-x-2">
              <Coins class="w-5 h-5 text-yellow-500" />
              <span class="text-yellow-500 font-bold">{{ userStore.user?.chips.toLocaleString() }}</span>
            </div>
          </div>
        </div>
      </div>
    </header>

    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- 左侧充值选项 -->
        <div class="lg:col-span-2 space-y-6">
          <!-- 筹码包选择 -->
          <div class="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20">
            <h2 class="text-white text-xl font-bold mb-6">选择筹码包</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div
                v-for="package_ in chipPackages"
                :key="package_.id"
                @click="selectedPackage = package_"
                :class="[
                  'relative cursor-pointer rounded-xl p-6 border-2 transition-all',
                  selectedPackage?.id === package_.id
                    ? 'border-yellow-500 bg-yellow-500/10'
                    : 'border-white/20 bg-white/5 hover:bg-white/10'
                ]"
              >
                <!-- 推荐标签 -->
                <div
                  v-if="package_.recommended"
                  class="absolute -top-2 -right-2 bg-red-500 text-white text-xs px-2 py-1 rounded-full font-bold"
                >
                  推荐
                </div>
                
                <!-- 筹码图标 -->
                <div class="flex items-center justify-center mb-4">
                  <div class="w-16 h-16 bg-yellow-500 rounded-full flex items-center justify-center">
                    <Coins class="w-8 h-8 text-green-900" />
                  </div>
                </div>
                
                <!-- 筹码数量 -->
                <div class="text-center mb-4">
                  <div class="text-2xl font-bold text-yellow-500 mb-1">
                    {{ package_.chips.toLocaleString() }}
                  </div>
                  <div class="text-gray-300 text-sm">筹码</div>
                </div>
                
                <!-- 价格 -->
                <div class="text-center mb-4">
                  <div class="text-xl font-bold text-white">
                    ¥{{ package_.price }}
                  </div>
                  <div v-if="package_.originalPrice" class="text-gray-400 text-sm line-through">
                    ¥{{ package_.originalPrice }}
                  </div>
                </div>
                
                <!-- 赠送 -->
                <div v-if="package_.bonus" class="text-center">
                  <div class="bg-green-600 text-white text-xs px-2 py-1 rounded-full">
                    赠送 {{ package_.bonus.toLocaleString() }} 筹码
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 支付方式 -->
          <div class="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20">
            <h3 class="text-white text-lg font-bold mb-4">选择支付方式</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div
                v-for="method in paymentMethods"
                :key="method.id"
                @click="selectedPayment = method"
                :class="[
                  'cursor-pointer rounded-lg p-4 border-2 transition-all flex items-center space-x-3',
                  selectedPayment?.id === method.id
                    ? 'border-yellow-500 bg-yellow-500/10'
                    : 'border-white/20 bg-white/5 hover:bg-white/10'
                ]"
              >
                <div
                  :class="[
                    'w-12 h-12 rounded-lg flex items-center justify-center',
                    method.color
                  ]"
                >
                  <component :is="method.icon" class="w-6 h-6" />
                </div>
                <div>
                  <div class="text-white font-medium">{{ method.name }}</div>
                  <div class="text-gray-300 text-sm">{{ method.description }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 右侧订单信息 -->
        <div class="space-y-6">
          <!-- 订单详情 -->
          <div class="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20">
            <h3 class="text-white text-lg font-bold mb-4">订单详情</h3>
            
            <div v-if="selectedPackage" class="space-y-4">
              <div class="flex justify-between">
                <span class="text-gray-300">筹码数量</span>
                <span class="text-white font-bold">{{ selectedPackage.chips.toLocaleString() }}</span>
              </div>
              
              <div v-if="selectedPackage.bonus" class="flex justify-between">
                <span class="text-gray-300">赠送筹码</span>
                <span class="text-green-400 font-bold">+{{ selectedPackage.bonus.toLocaleString() }}</span>
              </div>
              
              <div class="border-t border-white/20 pt-4">
                <div class="flex justify-between">
                  <span class="text-gray-300">总筹码</span>
                  <span class="text-yellow-500 font-bold text-lg">
                    {{ (selectedPackage.chips + (selectedPackage.bonus || 0)).toLocaleString() }}
                  </span>
                </div>
              </div>
              
              <div class="border-t border-white/20 pt-4">
                <div class="flex justify-between">
                  <span class="text-gray-300">支付金额</span>
                  <span class="text-white font-bold text-xl">¥{{ selectedPackage.price }}</span>
                </div>
              </div>
            </div>
            
            <div v-else class="text-center text-gray-400 py-8">
              请选择筹码包
            </div>
          </div>

          <!-- 安全提示 -->
          <div class="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20">
            <div class="flex items-center space-x-2 mb-3">
              <Shield class="w-5 h-5 text-green-400" />
              <h3 class="text-white font-bold">安全保障</h3>
            </div>
            <ul class="text-gray-300 text-sm space-y-2">
              <li class="flex items-center space-x-2">
                <Check class="w-4 h-4 text-green-400" />
                <span>SSL加密传输</span>
              </li>
              <li class="flex items-center space-x-2">
                <Check class="w-4 h-4 text-green-400" />
                <span>银行级安全防护</span>
              </li>
              <li class="flex items-center space-x-2">
                <Check class="w-4 h-4 text-green-400" />
                <span>7×24小时客服</span>
              </li>
            </ul>
          </div>

          <!-- 支付按钮 -->
          <button
            @click="processPayment"
            :disabled="!selectedPackage || !selectedPayment || processing"
            class="w-full bg-gradient-to-r from-yellow-500 to-yellow-600 text-green-900 font-bold py-4 px-6 rounded-xl hover:from-yellow-400 hover:to-yellow-500 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
          >
            <div v-if="processing" class="flex items-center">
              <div class="animate-spin rounded-full h-5 w-5 border-b-2 border-green-900 mr-2"></div>
              处理中...
            </div>
            <span v-else>立即支付</span>
          </button>
        </div>
      </div>

      <!-- 充值记录 -->
      <div class="mt-8 bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-white text-xl font-bold">充值记录</h3>
          <button
            @click="loadRechargeHistory"
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
                <th class="text-left text-gray-300 py-3">筹码数量</th>
                <th class="text-left text-gray-300 py-3">支付方式</th>
                <th class="text-left text-gray-300 py-3">金额</th>
                <th class="text-left text-gray-300 py-3">状态</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="record in rechargeHistory"
                :key="record.id"
                class="border-b border-white/10 hover:bg-white/5 transition-colors"
              >
                <td class="text-white py-3">{{ formatDate(record.timestamp) }}</td>
                <td class="text-yellow-500 py-3 font-bold">{{ record.chips.toLocaleString() }}</td>
                <td class="text-gray-300 py-3">{{ record.paymentMethod }}</td>
                <td class="text-white py-3 font-bold">¥{{ record.amount }}</td>
                <td class="py-3">
                  <span
                    :class="[
                      'px-2 py-1 rounded-full text-xs font-medium',
                      record.status === 'success' ? 'bg-green-600 text-white' :
                      record.status === 'pending' ? 'bg-yellow-600 text-white' :
                      'bg-red-600 text-white'
                    ]"
                  >
                    {{ getStatusText(record.status) }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  ArrowLeft, Spade, Coins, Shield, Check, RefreshCw,
  CreditCard, Smartphone, Wallet
} from 'lucide-vue-next'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()

const selectedPackage = ref(null)
const selectedPayment = ref(null)
const processing = ref(false)

// 筹码包数据
const chipPackages = ref([
  {
    id: 1,
    chips: 1000,
    price: 10,
    bonus: 0,
    recommended: false
  },
  {
    id: 2,
    chips: 5000,
    price: 45,
    originalPrice: 50,
    bonus: 500,
    recommended: true
  },
  {
    id: 3,
    chips: 10000,
    price: 85,
    originalPrice: 100,
    bonus: 1500,
    recommended: false
  },
  {
    id: 4,
    chips: 25000,
    price: 200,
    originalPrice: 250,
    bonus: 5000,
    recommended: false
  },
  {
    id: 5,
    chips: 50000,
    price: 380,
    originalPrice: 500,
    bonus: 12000,
    recommended: false
  },
  {
    id: 6,
    chips: 100000,
    price: 700,
    originalPrice: 1000,
    bonus: 30000,
    recommended: false
  }
])

// 支付方式数据
const paymentMethods = ref([
  {
    id: 1,
    name: '微信支付',
    description: '安全便捷',
    icon: Smartphone,
    color: 'bg-green-600'
  },
  {
    id: 2,
    name: '支付宝',
    description: '快速到账',
    icon: Wallet,
    color: 'bg-blue-600'
  },
  {
    id: 3,
    name: '银行卡',
    description: '银联支付',
    icon: CreditCard,
    color: 'bg-red-600'
  }
])

// 充值记录
const rechargeHistory = ref([
  {
    id: 1,
    timestamp: new Date(Date.now() - 3600000),
    chips: 5000,
    paymentMethod: '微信支付',
    amount: 45,
    status: 'success'
  },
  {
    id: 2,
    timestamp: new Date(Date.now() - 86400000),
    chips: 1000,
    paymentMethod: '支付宝',
    amount: 10,
    status: 'success'
  },
  {
    id: 3,
    timestamp: new Date(Date.now() - 172800000),
    chips: 10000,
    paymentMethod: '银行卡',
    amount: 85,
    status: 'success'
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

const getStatusText = (status: string) => {
  const statusTexts = {
    success: '成功',
    pending: '处理中',
    failed: '失败'
  }
  return statusTexts[status as keyof typeof statusTexts] || status
}

const processPayment = async () => {
  if (!selectedPackage.value || !selectedPayment.value) return
  
  processing.value = true
  
  try {
    // 模拟支付处理
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // 更新用户筹码
    const totalChips = selectedPackage.value.chips + (selectedPackage.value.bonus || 0)
    userStore.updateChips(totalChips)
    
    // 添加充值记录
    rechargeHistory.value.unshift({
      id: Date.now(),
      timestamp: new Date(),
      chips: totalChips,
      paymentMethod: selectedPayment.value.name,
      amount: selectedPackage.value.price,
      status: 'success'
    })
    
    alert(`充值成功！获得 ${totalChips.toLocaleString()} 筹码`)
    
    // 重置选择
    selectedPackage.value = null
    selectedPayment.value = null
    
  } catch (error) {
    alert('支付失败，请重试')
  } finally {
    processing.value = false
  }
}

const loadRechargeHistory = () => {
  // 模拟加载充值记录
  console.log('加载充值记录')
}

onMounted(() => {
  // 初始化数据
})
</script>