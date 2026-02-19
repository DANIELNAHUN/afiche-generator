import { createRouter, createWebHistory } from 'vue-router'
import { useSessionStore } from '../stores/session'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'welcome',
      component: () => import('../views/WelcomeView.vue')
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue')
    },
    {
      path: '/generator',
      name: 'generator',
      component: () => import('../views/GeneratorView.vue'),
      meta: { requiresAuth: true }
    }
  ]
})

// Guard para verificar autenticación
router.beforeEach((to, from, next) => {
  const sessionStore = useSessionStore()
  if (to.meta.requiresAuth && !sessionStore.isAuthenticated) {
    next({ name: 'login' })
  } else {
    next()
  }
})

export default router
