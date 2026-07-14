<template>
  <div>
    <!-- Desktop Sidebar (md and up) -->
    <aside
      class="fixed inset-y-0 left-0 z-30 bg-white dark:bg-dark-card border-r border-gray-200 dark:border-dark-border flex flex-col justify-between hidden lg:flex transition-all duration-300 ease-in-out"
      :class="[
        settingsStore.sidebarCollapsed ? 'w-16' : 'w-64',
        settingsStore.sidebarOverlaysContent ? 'shadow-2xl' : ''
      ]"
    >
      
      <!-- Brand Logo Section -->
      <div class="border-b border-gray-200 dark:border-dark-border/60 flex flex-col">
        <router-link to="/" class="flex items-center gap-3 hover-scale min-w-0 px-5 py-4" :class="settingsStore.sidebarCollapsed ? 'justify-center px-2' : ''" :title="APP_NAME">
          <img :src="beeboardLogo" alt="BeeBoard" class="h-12 w-auto flex-shrink-0" />
          <div v-if="!settingsStore.sidebarCollapsed" class="flex flex-col leading-tight min-w-0">
            <span class="text-base font-extrabold tracking-tight text-gray-800 dark:text-white truncate">{{ APP_NAME }}</span>
            <span class="text-[10px] font-semibold text-gray-400 dark:text-gray-500 tracking-wider">v{{ APP_VERSION }}</span>
          </div>
        </router-link>

        <!-- Collapse/Expand Toggle (below the logo) -->
        <button
          type="button"
          @click="settingsStore.toggleSidebar()"
          class="w-full px-5 py-1.5 flex items-center gap-2 text-xs font-semibold text-gray-400 hover:text-primary dark:text-gray-500 dark:hover:text-primary hover:bg-gray-100 dark:hover:bg-dark-border transition-colors duration-200 border-t border-gray-100 dark:border-dark-border/40"
          :class="settingsStore.sidebarCollapsed ? 'justify-center px-2' : ''"
          :title="settingsStore.sidebarCollapsed ? $t('sidebar.expand') : $t('sidebar.collapse')"
          :aria-label="settingsStore.sidebarCollapsed ? $t('sidebar.expand') : $t('sidebar.collapse')"
        >
          <ChevronsLeft v-if="!settingsStore.sidebarCollapsed" class="w-4 h-4" />
          <ChevronsRight v-else class="w-4 h-4" />
          <span v-if="!settingsStore.sidebarCollapsed">{{ $t('sidebar.collapse') }}</span>
        </button>
      </div>

      <!-- Navigation Links -->
      <nav class="flex-grow py-4 overflow-y-auto space-y-1">
        <router-link 
          v-for="item in filteredNavItems" 
          :key="item.path" 
          :to="item.path"
          class="mx-3 px-3 py-2.5 rounded-xl flex items-center text-sm font-semibold transition-all duration-200 group relative"
          :class="[
            settingsStore.sidebarCollapsed ? 'justify-center' : 'gap-3',
            $route.path.startsWith(item.path) 
              ? 'bg-primary text-white shadow-md shadow-primary/20' 
              : 'text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-dark-border hover:text-primary dark:hover:text-primary'
          ]"
          :title="settingsStore.sidebarCollapsed ? item.name : null"
        >
          <component 
            :is="item.icon" 
            class="w-5 h-5 flex-shrink-0 transition-colors duration-200"
            :class="$route.path.startsWith(item.path) ? 'text-white' : 'text-gray-400 dark:text-gray-500 group-hover:text-primary dark:group-hover:text-primary'"
          />
          <span v-if="!settingsStore.sidebarCollapsed" class="flex-1">{{ item.name }}</span>
          <span
            v-if="item.path === '/ai-insights' && unreadInsightsCount > 0"
            class="min-w-5 h-5 px-1.5 rounded-full text-[10px] font-black flex items-center justify-center"
            :class="[
              settingsStore.sidebarCollapsed ? 'absolute top-1 right-1' : '',
              $route.path.startsWith(item.path)
                ? 'bg-white/20 text-white'
                : 'bg-primary/15 text-primary'
            ]"
          >
            {{ unreadInsightsCount > 99 ? '99+' : unreadInsightsCount }}
          </span>
        </router-link>
      </nav>

      <!-- Sidebar Footer (Switcher, Profile, Actions) -->
      <div class="p-3 border-t border-gray-200 dark:border-dark-border space-y-3 bg-gray-50/50 dark:bg-dark-bg/20">
        
        <!-- Apiary Switcher -->
        <div v-if="!settingsStore.sidebarCollapsed" class="space-y-1.5">
          <label class="text-[10px] uppercase tracking-wider font-extrabold text-gray-400 dark:text-gray-500 block px-1">
            {{ $t('sidebar.active_apiary') }}
          </label>
          <div class="flex items-center gap-1.5 w-full">
            <div class="relative flex-grow flex items-center">
              <select 
                v-model="apiaryStore.activeApiaryId" 
                @change="onApiaryChange" 
                class="w-full bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-xl pl-3 pr-8 py-2 text-sm font-bold text-gray-700 dark:text-gray-200 cursor-pointer focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary appearance-none transition-all duration-200 animate-fade-in"
              >
                <option v-for="a in apiaryStore.apiaries" :key="a.id" :value="a.id" class="dark:bg-dark-card dark:text-gray-100">
                  {{ a.name }}
                </option>
                <option value="NEW" class="text-primary font-bold dark:bg-dark-card">+ Neue Imkerei...</option>
              </select>
              <div class="pointer-events-none absolute right-3 flex items-center">
                <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
                </svg>
              </div>
            </div>
            <button
              v-if="apiaryStore.activeApiaryId"
              type="button"
              @click="manageApiaryOpen = true"
              class="p-2 rounded-xl border border-gray-200 dark:border-dark-border hover:bg-gray-100 dark:hover:bg-dark-border hover:text-primary dark:hover:text-primary transition-all shrink-0 cursor-pointer"
              title="Imkerei verwalten"
            >
              <Settings class="w-4.5 h-4.5" />
            </button>
          </div>
        </div>

        <!-- Compact Apiary Indicator (collapsed) -->
        <button
          v-else
          type="button"
          @click="manageApiaryOpen = true"
          class="w-full flex justify-center items-center p-2 rounded-xl border border-gray-200 dark:border-dark-border hover:bg-gray-100 dark:hover:bg-dark-border hover:text-primary dark:hover:text-primary transition-all cursor-pointer"
          :title="apiaryStore.apiaries.find(a => a.id === apiaryStore.activeApiaryId)?.name || 'Imkerei wählen'"
        >
          <Hexagon class="w-4.5 h-4.5 text-primary" />
        </button>

        <!-- User Profile Area -->
        <div v-if="!settingsStore.sidebarCollapsed" class="flex items-center gap-3 px-1 pt-1">
          <div class="w-9 h-9 rounded-xl bg-primary/10 text-primary flex items-center justify-center font-bold text-sm flex-shrink-0 uppercase border border-primary/20">
            {{ (authStore.user?.first_name || authStore.user?.username || 'U').substring(0, 2) }}
          </div>
          <div class="flex-grow min-w-0">
            <p class="text-sm font-bold text-gray-700 dark:text-gray-200 truncate leading-tight">
              {{ authStore.user?.first_name || authStore.user?.username }}
            </p>
            <span class="text-[10px] text-gray-400 dark:text-gray-500 font-semibold truncate block">
              {{ authStore.user?.email || 'Imker' }}
            </span>
          </div>
        </div>

        <!-- User Avatar (collapsed) -->
        <div v-else class="flex justify-center pt-1">
          <div class="w-9 h-9 rounded-xl bg-primary/10 text-primary flex items-center justify-center font-bold text-sm uppercase border border-primary/20" :title="authStore.user?.first_name || authStore.user?.username || ''">
            {{ (authStore.user?.first_name || authStore.user?.username || 'U').substring(0, 2) }}
          </div>
        </div>

        <!-- Utilities -->
        <div class="flex gap-2 pt-2 border-t border-gray-200/50 dark:border-dark-border/40">
          <button 
            v-if="!settingsStore.sidebarCollapsed"
            @click="toggleDarkMode" 
            class="flex-grow px-3 py-2 rounded-xl text-gray-500 hover:text-primary dark:text-gray-400 dark:hover:text-primary hover:bg-gray-100 dark:hover:bg-dark-border transition-colors duration-200 hover-scale flex justify-center items-center gap-1.5"
            :title="$t('sidebar.theme')"
          >
            <component :is="isDark ? Sun : Moon" class="w-4.5 h-4.5" />
            <span class="text-xs font-semibold">{{ $t('sidebar.theme') }}</span>
          </button>
          <button
            v-else
            @click="toggleDarkMode"
            class="flex-grow p-2 rounded-xl text-gray-500 hover:text-primary dark:text-gray-400 dark:hover:text-primary hover:bg-gray-100 dark:hover:bg-dark-border transition-colors duration-200 hover-scale flex justify-center items-center"
            :title="$t('sidebar.theme')"
          >
            <component :is="isDark ? Sun : Moon" class="w-4.5 h-4.5" />
          </button>

          <button
            @click="toggleLanguage"
            class="p-2 rounded-xl text-gray-500 hover:text-primary dark:text-gray-400 dark:hover:text-primary hover:bg-gray-100 dark:hover:bg-dark-border transition-colors duration-200 hover-scale flex justify-center items-center"
            :title="$t('sidebar.toggle_language')"
          >
            <Globe class="w-4.5 h-4.5" />
          </button>

          <button
            v-if="!settingsStore.sidebarCollapsed"
            @click="aboutOpen = true"
            class="p-2 rounded-xl text-gray-500 hover:text-primary dark:text-gray-400 dark:hover:text-primary hover:bg-gray-100 dark:hover:bg-dark-border transition-colors duration-200 hover-scale flex justify-center items-center"
            :title="$t('sidebar.about')"
          >
            <CircleHelp class="w-4.5 h-4.5" />
          </button>
          
          <button 
            @click="logout" 
            class="p-2 rounded-xl text-red-500 hover:text-white hover:bg-red-500 dark:hover:bg-red-600 transition-colors duration-200 hover-scale flex justify-center items-center"
            :title="$t('sidebar.logout')"
          >
            <LogOut class="w-4.5 h-4.5" />
          </button>
        </div>

      </div>
    </aside>

    <!-- Mobile Top Header (below md) -->
    <header class="fixed top-0 left-0 right-0 h-16 z-40 bg-white/80 dark:bg-dark-bg/80 backdrop-blur-md border-b border-gray-200 dark:border-dark-border flex items-center justify-between px-4 lg:hidden transition-colors duration-300">
      <div class="flex items-center gap-2">
        <button 
          @click="mobileMenuOpen = !mobileMenuOpen" 
          class="p-2 rounded-xl text-gray-500 hover:text-primary hover:bg-gray-100 dark:text-gray-400 dark:hover:text-primary dark:hover:bg-dark-border transition-colors duration-200"
          aria-label="Menü öffnen"
        >
          <Menu v-if="!mobileMenuOpen" class="w-6 h-6" />
          <X v-else class="w-6 h-6" />
        </button>

        <router-link to="/" class="flex items-center gap-2 hover-scale">
          <img :src="beeboardLogo" alt="BeeBoard" class="h-10 w-auto" />
          <span class="font-extrabold text-sm text-gray-800 dark:text-white tracking-tight">{{ APP_NAME }}</span>
        </router-link>
      </div>

      <div class="flex items-center gap-2">
        <button 
          @click="toggleDarkMode" 
          class="p-2 rounded-xl text-gray-500 hover:text-primary dark:text-gray-400 dark:hover:text-primary hover:bg-gray-100 dark:hover:bg-dark-border transition-colors duration-200 hover-scale"
        >
          <component :is="isDark ? Sun : Moon" class="w-5 h-5" />
        </button>

        <div class="w-8 h-8 rounded-xl bg-primary/10 text-primary flex items-center justify-center font-bold text-xs uppercase border border-primary/20">
          {{ (authStore.user?.first_name || authStore.user?.username || 'U').substring(0, 2) }}
        </div>
      </div>
    </header>

    <!-- Mobile Drawer Sidebar Backdrop -->
    <transition name="fade">
      <div 
        v-if="mobileMenuOpen" 
        @click="mobileMenuOpen = false"
        class="fixed inset-0 bg-black/40 backdrop-blur-sm z-40 lg:hidden"
      ></div>
    </transition>

    <!-- Mobile Drawer Sidebar (below md) -->
    <aside 
      class="fixed inset-y-0 left-0 w-64 bg-white dark:bg-dark-card z-50 shadow-2xl flex flex-col justify-between transform transition-transform duration-300 ease-in-out lg:hidden"
      :class="mobileMenuOpen ? 'translate-x-0' : '-translate-x-full'"
    >
      <!-- Brand Logo Section -->
      <div class="h-16 flex items-center justify-between px-6 border-b border-gray-200 dark:border-dark-border/60">
        <router-link to="/" @click="mobileMenuOpen = false" class="flex items-center gap-2.5 hover-scale">
          <img :src="beeboardLogo" alt="BeeBoard" class="h-9 w-auto" />
          <div class="flex flex-col leading-tight">
            <span class="text-sm font-extrabold text-gray-800 dark:text-white tracking-tight">{{ APP_NAME }}</span>
            <span class="text-[9px] font-semibold text-gray-400 dark:text-gray-500">v{{ APP_VERSION }}</span>
          </div>
        </router-link>

        <button 
          @click="mobileMenuOpen = false" 
          class="p-1 rounded-lg text-gray-400 hover:text-primary hover:bg-gray-100 dark:hover:text-primary dark:hover:bg-dark-border"
          aria-label="Schließen"
        >
          <X class="w-5 h-5" />
        </button>
      </div>

      <!-- Navigation Links -->
      <nav class="flex-grow py-4 overflow-y-auto space-y-1">
        <router-link 
          v-for="item in filteredNavItems" 
          :key="item.path" 
          :to="item.path"
          @click="mobileMenuOpen = false"
          class="mx-3 px-4 py-2.5 rounded-xl flex items-center gap-3 text-sm font-semibold transition-all duration-200 group"
          :class="$route.path.startsWith(item.path) 
            ? 'bg-primary text-white shadow-md shadow-primary/20' 
            : 'text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-dark-border hover:text-primary dark:hover:text-primary'"
        >
          <component 
            :is="item.icon" 
            class="w-5 h-5 flex-shrink-0 transition-colors duration-200"
            :class="$route.path.startsWith(item.path) ? 'text-white' : 'text-gray-400 dark:text-gray-500 group-hover:text-primary dark:group-hover:text-primary'"
          />
          <span class="flex-1">{{ item.name }}</span>
          <span
            v-if="item.path === '/ai-insights' && unreadInsightsCount > 0"
            class="min-w-5 h-5 px-1.5 rounded-full text-[10px] font-black flex items-center justify-center"
            :class="$route.path.startsWith(item.path)
              ? 'bg-white/20 text-white'
              : 'bg-primary/15 text-primary'"
          >
            {{ unreadInsightsCount > 99 ? '99+' : unreadInsightsCount }}
          </span>
        </router-link>
      </nav>

      <!-- Sidebar Footer (Switcher, Profile, Actions) -->
      <div class="p-4 border-t border-gray-200 dark:border-dark-border space-y-4 bg-gray-50/50 dark:bg-dark-bg/20">
        
        <!-- Apiary Switcher -->
        <div class="space-y-1.5">
          <label class="text-[10px] uppercase tracking-wider font-extrabold text-gray-400 dark:text-gray-500 block px-1">
            Aktive Imkerei
          </label>
          <div class="flex items-center gap-1.5 w-full">
            <div class="relative flex-grow flex items-center">
              <select 
                v-model="apiaryStore.activeApiaryId" 
                @change="onApiaryChange" 
                class="w-full bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-xl pl-3 pr-8 py-2 text-sm font-bold text-gray-700 dark:text-gray-200 cursor-pointer focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary appearance-none transition-all duration-200"
              >
                <option v-for="a in apiaryStore.apiaries" :key="a.id" :value="a.id" class="dark:bg-dark-card dark:text-gray-100">
                  {{ a.name }}
                </option>
                <option value="NEW" class="text-primary font-bold dark:bg-dark-card">+ Neue Imkerei...</option>
              </select>
              <div class="pointer-events-none absolute right-3 flex items-center">
                <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
                </svg>
              </div>
            </div>
            <button
              v-if="apiaryStore.activeApiaryId"
              type="button"
              @click="manageApiaryOpen = true"
              class="p-2 rounded-xl border border-gray-200 dark:border-dark-border hover:bg-gray-100 dark:hover:bg-dark-border hover:text-primary dark:hover:text-primary transition-all shrink-0 cursor-pointer"
              title="Imkerei verwalten"
            >
              <Settings class="w-4.5 h-4.5" />
            </button>
          </div>
        </div>

        <!-- User Profile Area -->
        <div class="flex items-center gap-3 px-1 pt-1">
          <div class="w-9 h-9 rounded-xl bg-primary/10 text-primary flex items-center justify-center font-bold text-sm flex-shrink-0 uppercase border border-primary/20">
            {{ (authStore.user?.first_name || authStore.user?.username || 'U').substring(0, 2) }}
          </div>
          <div class="flex-grow min-w-0">
            <p class="text-sm font-bold text-gray-700 dark:text-gray-200 truncate leading-tight">
              {{ authStore.user?.first_name || authStore.user?.username }}
            </p>
            <span class="text-[10px] text-gray-400 dark:text-gray-500 font-semibold truncate block">
              {{ authStore.user?.email || 'Imker' }}
            </span>
          </div>
        </div>

        <!-- Utilities -->
        <div class="flex gap-2 pt-2 border-t border-gray-200/50 dark:border-dark-border/40">
          <button 
            @click="toggleDarkMode" 
            class="flex-grow px-3 py-2 rounded-xl text-gray-500 hover:text-primary dark:text-gray-400 dark:hover:text-primary hover:bg-gray-100 dark:hover:bg-dark-border transition-colors duration-200 hover-scale flex justify-center items-center gap-1.5"
            :title="$t('sidebar.theme')"
          >
            <component :is="isDark ? Sun : Moon" class="w-4.5 h-4.5" />
            <span class="text-xs font-semibold">{{ $t('sidebar.theme') }}</span>
          </button>

          <button
            @click="toggleLanguage"
            class="p-2 rounded-xl text-gray-500 hover:text-primary dark:text-gray-400 dark:hover:text-primary hover:bg-gray-100 dark:hover:bg-dark-border transition-colors duration-200 hover-scale flex justify-center items-center"
            :title="$t('sidebar.toggle_language')"
          >
            <Globe class="w-4.5 h-4.5" />
          </button>

          <button
            @click="aboutOpen = true"
            class="p-2 rounded-xl text-gray-500 hover:text-primary dark:text-gray-400 dark:hover:text-primary hover:bg-gray-100 dark:hover:bg-dark-border transition-colors duration-200 hover-scale flex justify-center items-center"
            :title="$t('sidebar.about')"
          >
            <CircleHelp class="w-4.5 h-4.5" />
          </button>
          
          <button 
            @click="logout" 
            class="p-2 rounded-xl text-red-500 hover:text-white hover:bg-red-500 dark:hover:bg-red-600 transition-colors duration-200 hover-scale flex justify-center items-center"
            :title="$t('sidebar.logout')"
          >
            <LogOut class="w-4.5 h-4.5" />
          </button>
        </div>

      </div>
    </aside>

    <AboutDialog v-model="aboutOpen" />
    <ManageApiaryModal v-model="manageApiaryOpen" />

  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { useI18n } from 'vue-i18n'
import beeboardLogo from '../assets/beeboard-logo.svg'
import { APP_NAME, APP_VERSION } from '../config/app.js'
import { useAuthStore } from '../stores/auth'
import { useApiaryStore } from '../stores/apiary'
import { useSettingsStore } from '../stores/settings'
import AboutDialog from './AboutDialog.vue'
import ManageApiaryModal from './ManageApiaryModal.vue'
import { 
  LayoutDashboard, 
  MapPin, 
  Hexagon, 
  BookOpen, 
  Droplets, 
  BarChart3, 
  Sparkles, 
  Shield,
  LogOut,
  Sun,
  Moon,
  Menu,
  X,
  ShoppingBag,
  ClipboardList,
  CircleHelp,
  Globe,
  Calendar,
  Settings,
  ChevronsLeft,
  ChevronsRight,
  HeartPulse,
} from 'lucide-vue-next'

const router = useRouter()
const authStore = useAuthStore()
const apiaryStore = useApiaryStore()
const settingsStore = useSettingsStore()
const { t, locale } = useI18n()

const mobileMenuOpen = ref(false)
const isDark = ref(false)
const unreadInsightsCount = ref(0)
const aboutOpen = ref(false)
const manageApiaryOpen = ref(false)

const navItems = computed(() => [
  { name: t('sidebar.dashboard'), path: '/dashboard', icon: LayoutDashboard },
  { name: t('sidebar.locations'), path: '/locations', icon: MapPin },
  { name: t('sidebar.hives'), path: '/hives', icon: Hexagon },
  { name: t('sidebar.logbook'), path: '/logbook', icon: BookOpen },
  { name: t('sidebar.treatments'), path: '/treatments', icon: HeartPulse },
  { name: t('sidebar.tasks'), path: '/tasks', icon: ClipboardList },
  { name: t('sidebar.calendar'), path: '/calendar', icon: Calendar },
  { name: t('sidebar.honey_batches'), path: '/honey-batches', icon: Droplets },
  { name: t('sidebar.sales'), path: '/sales', icon: ShoppingBag },
  { name: t('sidebar.stats'), path: '/stats', icon: BarChart3 },
  { name: t('sidebar.ai_insights'), path: '/ai-insights', icon: Sparkles }
])

const filteredNavItems = computed(() => {
  if (authStore.isAdmin) {
    return [
      ...navItems.value,
      { name: t('sidebar.admin'), path: '/admin', icon: Shield }
    ]
  }
  return navItems.value
})

let removeAutoCollapseListener = () => {}

onMounted(() => {
  // Check persisted dark mode setting
  if (localStorage.getItem('theme') === 'dark' || (!localStorage.getItem('theme') && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    isDark.value = true
    document.documentElement.classList.add('dark')
  } else {
    isDark.value = false
    document.documentElement.classList.remove('dark')
  }

  // App.vue owns the sidebar lifecycle, but make sure the listener is bound
  // even when the sidebar mounts independently of App.vue (defensive).
  removeAutoCollapseListener = settingsStore.bindAutoCollapseListener()

  fetchUnreadInsightsCount()
  window.addEventListener('ai-insights-updated', fetchUnreadInsightsCount)
})

onBeforeUnmount(() => {
  window.removeEventListener('ai-insights-updated', fetchUnreadInsightsCount)
  removeAutoCollapseListener()
})

watch(() => apiaryStore.activeApiaryId, () => {
  fetchUnreadInsightsCount()
})

async function fetchUnreadInsightsCount() {
  if (!apiaryStore.activeApiaryId) {
    unreadInsightsCount.value = 0
    return
  }

  try {
    const res = await axios.get('/api/ai-insights', {
      params: {
        apiary_id: apiaryStore.activeApiaryId,
        read_status: 'unread'
      }
    })
    unreadInsightsCount.value = Array.isArray(res.data) ? res.data.length : 0
  } catch {
    unreadInsightsCount.value = 0
  }
}

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

function toggleLanguage() {
  locale.value = locale.value === 'de' ? 'en' : 'de'
  localStorage.setItem('locale', locale.value)
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
  router.push({ path: '/login', query: { reason: 'logged_out' } })
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
