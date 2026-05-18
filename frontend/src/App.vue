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
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from './stores/auth'
import { useApiaryStore } from './stores/apiary'
import Navbar from './components/Navbar.vue'

const authStore = useAuthStore()
const apiaryStore = useApiaryStore()

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
