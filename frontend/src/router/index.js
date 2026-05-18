import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useApiaryStore } from '../stores/apiary'

const routes = [
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/AuthView.vue'),
    meta: { guest: true }
  },
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: () => import('../views/HomeView.vue')
  },
  {
    path: '/locations',
    name: 'locations',
    component: () => import('../views/LocationsView.vue')
  },
  {
    path: '/hives',
    name: 'hives',
    component: () => import('../views/HivesView.vue')
  },
  {
    path: '/logbook',
    name: 'logbook',
    component: () => import('../views/LogbookView.vue')
  },
  {
    path: '/stats',
    name: 'stats',
    component: () => import('../views/StatisticsView.vue')
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/dashboard'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation Guards
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  const apiaryStore = useApiaryStore()

  // Initialize Axios Auth Headers on first load
  authStore.initAxiosHeaders()

  // If token exists but user profile is not loaded yet, fetch it
  if (authStore.isAuthenticated && !authStore.user) {
    await authStore.fetchMe()
    if (authStore.isAuthenticated) {
      await apiaryStore.fetchApiaries()
    }
  }

  const isLoggedIn = authStore.isAuthenticated

  if (to.meta.guest) {
    if (isLoggedIn) {
      next('/dashboard')
    } else {
      next()
    }
  } else {
    if (!isLoggedIn) {
      next('/login')
    } else {
      next()
    }
  }
})

export default router
