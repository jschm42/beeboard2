<template>
  <div class="min-h-screen flex flex-col bg-gray-50 dark:bg-dark-bg text-gray-900 dark:text-gray-100 transition-colors duration-300">
    <!-- Render Navbar only if user is authenticated -->
    <Navbar v-if="authStore.isAuthenticated" />
    
    <main class="flex-grow">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>

    <!-- Global Premium Error Modal -->
    <ErrorModal />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import axios from 'axios'
import { useAuthStore } from './stores/auth'
import { useApiaryStore } from './stores/apiary'
import { useErrorStore } from './stores/error'
import Navbar from './components/Navbar.vue'
import ErrorModal from './components/ErrorModal.vue'

const authStore = useAuthStore()
const apiaryStore = useApiaryStore()
const errorStore = useErrorStore()

// Configure global Axios response interceptors
axios.interceptors.response.use(
  response => response,
  error => {
    // Prevent global modal popups for standard boot checks
    const isBootCheck = error.config?.url?.includes('/api/auth/setup-status') || error.config?.url?.includes('/api/auth/me')
    if (isBootCheck) {
      return Promise.reject(error)
    }

    let friendlyMessage = 'Ein unerwarteter Fehler ist aufgetreten. Bitte versuchen Sie es später noch einmal.'
    
    if (error.response) {
      const status = error.response.status
      const detail = error.response.data?.detail

      if (status === 401) {
        friendlyMessage = 'Sie sind nicht angemeldet oder Ihre Sitzung ist abgelaufen. Bitte loggen Sie sich erneut ein.'
        if (authStore.isAuthenticated) {
          authStore.logout()
        }
      } else if (status === 403) {
        friendlyMessage = detail || 'Sie haben keine ausreichenden Berechtigungen, um diese Aktion auszuführen.'
      } else if (status === 404) {
        friendlyMessage = detail || 'Die angeforderte Ressource wurde nicht gefunden.'
      } else if (status === 422) {
        friendlyMessage = 'Ungültige Daten übermittelt. Bitte prüfen Sie Ihre Eingaben.'
      } else if (status >= 500) {
        friendlyMessage = 'Ein Serverfehler ist aufgetreten. Unsere Bienen arbeiten bereits an einer Lösung.'
      } else if (detail) {
        friendlyMessage = detail
      }
    } else if (error.request) {
      friendlyMessage = 'Verbindung zum Server fehlgeschlagen. Bitte prüfen Sie Ihre Internetverbindung.'
    }

    // Trigger global modal
    errorStore.showError(friendlyMessage, error, 'Aktion fehlgeschlagen')
    return Promise.reject(error)
  }
)

onMounted(async () => {
  // Restore Bearer token from localStorage into axios headers on every page load
  authStore.initAxiosHeaders()
  // Re-fetch current user profile if a token exists
  if (authStore.token) {
    await authStore.fetchMe()
  }
  // Restore the active apiary header from localStorage
  apiaryStore.initApiaryHeader()
})
</script>

<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
