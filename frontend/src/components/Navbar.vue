<template>
  <nav class="sticky top-0 z-50 glass shadow-sm transition-all duration-300">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-16">
        
        <!-- Left Side: Brand Logo and Main Nav Links -->
        <div class="flex items-center space-x-8">
          <router-link to="/" class="flex items-center space-x-2 text-primary font-bold text-xl hover-scale">
            <!-- Bee SVG Icon -->
            <svg class="w-8 h-8 fill-primary animate-pulse" viewBox="0 0 24 24">
              <path d="M12 2C11.5 2 11 2.2 10.6 2.6L7.4 5.8C6.9 6.3 6.9 7.1 7.4 7.6L8.4 8.6C7.6 9.8 7 11 7 12H5C3.3 12 2 13.3 2 15C2 16.7 3.3 18 5 18H7C7 19.1 7.9 20 9 20H15C16.1 20 17 19.1 17 18H19C20.7 18 22 16.7 22 15C22 13.3 20.7 12 19 12H17C17 11 16.4 9.8 15.6 8.6L16.6 7.6C17.1 7.1 17.1 6.3 16.6 5.8L13.4 2.6C13 2.2 12.5 2 12 2M12 4L14.4 6.4L13 7.8L12.5 7.3C12.1 6.9 11.3 6.9 10.9 7.3L10.4 7.8L9.6 7L12 4M9 10H15V12H9V10M5 14H19C19.6 14 20 14.4 20 15C20 15.6 19.6 16 19 16H5C4.4 16 4 15.6 4 15C4 14.4 4.4 14 5 14M9 18H15V19H9V18Z"/>
            </svg>
            <span class="tracking-wider font-extrabold uppercase text-gray-800 dark:text-white">Bee<span class="text-primary">Board</span></span>
          </router-link>

          <!-- Desktop Nav Links -->
          <div class="hidden md:flex space-x-1">
            <router-link 
              v-for="item in filteredNavItems" 
              :key="item.path" 
              :to="item.path"
              class="px-3 py-2 rounded-lg text-sm font-semibold transition-all duration-200"
              :class="$route.path.startsWith(item.path) 
                ? 'bg-primary text-white shadow-md shadow-primary/20' 
                : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-dark-border hover:text-primary dark:hover:text-primary'"
            >
              {{ item.name }}
            </router-link>
          </div>
        </div>

        <!-- Right Side: Apiary Switcher, Theme Toggle, User Dropdown -->
        <div class="flex items-center space-x-4">
          
          <!-- Imkerei Switcher -->
          <div v-if="authStore.isAuthenticated" class="relative">
            <div class="flex items-center space-x-2 bg-gray-100 dark:bg-dark-border px-3 py-1.5 rounded-lg border border-gray-200 dark:border-gray-700">
              <span class="text-xs text-gray-500 dark:text-gray-400 font-bold uppercase hidden lg:inline">Imkerei:</span>
              <select 
                v-model="apiaryStore.activeApiaryId" 
                @change="onApiaryChange" 
                class="bg-transparent text-sm font-bold text-gray-700 dark:text-gray-200 focus:outline-none cursor-pointer pr-1"
              >
                <option v-for="a in apiaryStore.apiaries" :key="a.id" :value="a.id" class="dark:bg-dark-card dark:text-gray-100">
                  {{ a.name }}
                </option>
                <option value="NEW" class="text-primary font-bold dark:bg-dark-card">+ Neue Imkerei...</option>
              </select>
            </div>
          </div>

          <!-- Dark Mode Toggle -->
          <button @click="toggleDarkMode" class="p-2 rounded-lg text-gray-500 hover:text-primary dark:text-gray-400 dark:hover:text-primary hover:bg-gray-100 dark:hover:bg-dark-border transition-colors duration-200 hover-scale" aria-label="Toggle dark mode">
            <span v-if="isDark">
              <!-- Sun Icon -->
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364-6.364l-.707.707M6.343 17.657l-.707.707m0-12.728l.707.707m12.728 12.728l.707.707M12 8a4 4 0 100 8 4 4 0 000-8z"/></svg>
            </span>
            <span v-else>
              <!-- Moon Icon -->
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"/></svg>
            </span>
          </button>

          <!-- User Logout Button -->
          <div v-if="authStore.isAuthenticated" class="hidden sm:flex items-center space-x-2">
            <span class="text-sm font-semibold text-gray-700 dark:text-gray-300 max-w-[120px] truncate">
              {{ authStore.user?.first_name || authStore.user?.username }}
            </span>
            <button @click="logout" class="p-2 rounded-lg text-red-500 hover:text-white hover:bg-red-500 dark:hover:bg-red-600 transition-colors duration-200 hover-scale" title="Abmelden">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/></svg>
            </button>
          </div>

          <!-- Burger Menu Button (Mobile) -->
          <button @click="mobileMenuOpen = !mobileMenuOpen" class="md:hidden p-2 rounded-lg text-gray-500 hover:text-primary hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-dark-border transition-colors duration-200">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path v-if="mobileMenuOpen" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
              <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
            </svg>
          </button>
        </div>

      </div>
    </div>

    <!-- Mobile Nav Menu -->
    <div v-if="mobileMenuOpen" class="md:hidden border-t border-gray-200 dark:border-dark-border px-4 py-2 space-y-1 bg-white dark:bg-dark-card shadow-lg">
      <router-link 
        v-for="item in filteredNavItems" 
        :key="item.path" 
        :to="item.path"
        @click="mobileMenuOpen = false"
        class="block px-3 py-2 rounded-lg text-base font-semibold text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-dark-border hover:text-primary"
      >
        {{ item.name }}
      </router-link>
      <div v-if="authStore.isAuthenticated" class="pt-4 pb-2 border-t border-gray-100 dark:border-dark-border flex justify-between items-center px-3">
        <span class="text-sm font-semibold text-gray-700 dark:text-gray-300">{{ authStore.user?.username }}</span>
        <button @click="logout" class="flex items-center space-x-1 text-sm font-bold text-red-500">
          <span>Abmelden</span>
        </button>
      </div>
    </div>



  </nav>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useApiaryStore } from '../stores/apiary'

const router = useRouter()
const authStore = useAuthStore()
const apiaryStore = useApiaryStore()

const mobileMenuOpen = ref(false)
const isDark = ref(false)



const navItems = [
  { name: 'Dashboard', path: '/dashboard' },
  { name: 'Standorte', path: '/locations' },
  { name: 'Bienenvölker', path: '/hives' },
  { name: 'Logbuch', path: '/logbook' },
  { name: 'Statistiken', path: '/stats' }
]

const filteredNavItems = computed(() => {
  if (authStore.isAdmin) {
    return [
      ...navItems,
      { name: 'Admin', path: '/admin' }
    ]
  }
  return navItems
})

onMounted(() => {
  // Check persisted dark mode setting
  if (localStorage.getItem('theme') === 'dark' || (!localStorage.getItem('theme') && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    isDark.value = true
    document.documentElement.classList.add('dark')
  } else {
    isDark.value = false
    document.documentElement.classList.remove('dark')
  }
})

function toggleDarkMode() {
  isDark.value = !isDark.value
  if (isDark.value) {
    document.documentElement.classList.add('dark')
    localStorage.setItem('theme', 'dark')
  } else {
    document.documentElement.classList.remove('dark')
    localStorage.setItem('theme', 'light')
  }
}

function onApiaryChange(event) {
  if (event.target.value === 'NEW') {
    // Reset active apiary to allow creation inline on home page
    apiaryStore.activeApiaryId = null
    localStorage.removeItem('activeApiaryId')
    apiaryStore.initApiaryHeader()
    router.push('/dashboard')
  } else {
    apiaryStore.selectApiary(event.target.value)
    window.location.reload()
  }
}

function logout() {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.animate-scale {
  animation: scaleUp 0.2s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

@keyframes scaleUp {
  from {
    transform: scale(0.95);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}
</style>
