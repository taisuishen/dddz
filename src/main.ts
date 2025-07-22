import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import { pinia } from './stores'
import { useUserStore } from './stores/user'
import { connectWebSocket } from './utils/websocket'

// 创建Vue应用实例
const app = createApp(App)

// 使用路由
app.use(router)

// 使用Pinia状态管理
app.use(pinia)

// 初始化用户状态
const userStore = useUserStore()
userStore.initFromStorage()

// 如果用户已登录，尝试连接WebSocket
if (userStore.isLoggedIn) {
  connectWebSocket().catch(console.error)
}

// 挂载应用
app.mount('#app')
