import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useApiaryStore } from '../stores/apiary'
import { useSettingsStore } from '../stores/settings'

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
    path: '/treatments',
    name: 'treatments',
    component: () => import('../views/TreatmentsView.vue')
  },
  {
    path: '/tasks',
    name: 'tasks',
    component: () => import('../views/TasksView.vue')
  },
  {
    path: '/calendar',
    name: 'calendar',
    component: () => import('../views/TasksView.vue')
  },
  {
    path: '/stats',
    name: 'stats',
    component: () => import('../views/StatisticsView.vue')
  },
  {
    path: '/ai-insights',
    name: 'ai-insights',
    component: () => import('../views/AIInsightsView.vue')
  },
  {
    path: '/honey-batches',
    name: 'honey-batches',
    component: () => import('../views/HoneyBatchesView.vue')
  },
  {
    path: '/sales',
    name: 'sales',
    component: () => import('../views/SalesView.vue')
  },
  {
    path: '/admin',
    name: 'admin',
    component: () => import('../views/AdminView.vue'),
    meta: { requiresAdmin: true }
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
  const settingsStore = useSettingsStore()

  // Initialize Axios Auth Headers on first load
  authStore.initAxiosHeaders()

  // If token exists but user profile is not loaded yet, fetch it
  if (authStore.isAuthenticated && !authStore.user) {
    await authStore.fetchMe()
    if (authStore.isAuthenticated) {
      // Parallel fetch apiaries and settings
      await Promise.all([
        apiaryStore.fetchApiaries(),
        settingsStore.fetchSettings()
      ]).catch(err => {
        console.error('Failed to load initial session data:', err)
      })
      apiaryStore.initApiaryHeader()
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
    } else if (to.meta.requiresAdmin && !authStore.isAdmin) {
      // Prevent non-admin users from accessing admin routes
      next('/dashboard')
    } else {
      next()
    }
  }
})

export default router
