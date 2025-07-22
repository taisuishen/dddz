import { createRouter, createWebHistory } from 'vue-router'
import LoginPage from '../pages/LoginPage.vue'
import LobbyPage from '../pages/LobbyPage.vue'
import GamePage from '../pages/GamePage.vue'
import ProfilePage from '../pages/ProfilePage.vue'
import RechargePage from '../pages/RechargePage.vue'
import AdminPage from '../pages/AdminPage.vue'
import { useUserStore } from '../stores/user'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/login'
    },
    {
      path: '/login',
      name: 'login',
      component: LoginPage,
    },
    {
      path: '/lobby',
      name: 'lobby',
      component: LobbyPage,
      meta: { requiresAuth: true }
    },
    {
      path: '/game/:roomId',
      name: 'game',
      component: GamePage,
      meta: { requiresAuth: true }
    },
    {
      path: '/profile',
      name: 'profile',
      component: ProfilePage,
      meta: { requiresAuth: true }
    },
    {
      path: '/recharge',
      name: 'recharge',
      component: RechargePage,
      meta: { requiresAuth: true }
    },
    {
      path: '/admin',
      name: 'admin',
      component: AdminPage,
      meta: { requiresAuth: true, requiresAdmin: true }
    }
  ],
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  
  // 检查是否需要登录
  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    next('/login')
    return
  }
  
  // 检查是否需要管理员权限
  if (to.meta.requiresAdmin && !userStore.user?.isAdmin) {
    next('/lobby')
    return
  }
  
  // 如果已登录且访问登录页，重定向到大厅
  if (to.path === '/login' && userStore.isLoggedIn) {
    next('/lobby')
    return
  }
  
  next()
})

export default router
