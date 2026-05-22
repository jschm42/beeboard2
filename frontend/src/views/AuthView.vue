<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-900 px-4 py-12 sm:px-6 lg:px-8 relative overflow-hidden font-sans">
    
    <!-- Premium Honeycomb Background Blur Circles -->
    <div class="absolute top-1/4 left-1/4 w-96 h-96 bg-primary/20 rounded-full blur-3xl"></div>
    <div class="absolute bottom-1/4 right-1/4 w-96 h-96 bg-amber-600/10 rounded-full blur-3xl"></div>
    
    <!-- Honeycomb Pattern SVG overlay -->
    <div class="absolute inset-0 opacity-10 bg-[radial-gradient(#f59e0b_1px,transparent_1px)] [background-size:24px_24px]"></div>

    <div 
      class="max-w-md w-full space-y-8 z-10 p-8 rounded-3xl shadow-2xl transition-all duration-300 relative border"
      :class="setupRequired 
        ? 'bg-gray-950 border-primary/40 shadow-primary/10 shadow-2xl' 
        : 'glass border-white/10 bg-gray-900/60 backdrop-blur-xl'"
    >
      
      <!-- Border glow when in onboarding mode (now acts as a premium outer halo) -->
      <div v-if="setupRequired" class="absolute -inset-0.5 bg-gradient-to-r from-amber-500 to-primary rounded-3xl blur opacity-30 -z-10"></div>

      <!-- Brand Logo Header -->
      <div class="text-center">
        <div class="inline-flex items-center justify-center p-4 bg-primary/10 rounded-2xl mb-3">
          <img :src="beeboardLogo" alt="BeeBoard" class="w-16 h-16 object-contain" />
        </div>
        <h2 class="text-3xl font-extrabold tracking-tight text-white">Bee<span class="text-primary">Board</span></h2>
        <p class="mt-1 text-xs text-gray-500 font-mono tracking-widest">v{{ APP_VERSION }}</p>
        <p class="mt-2 text-sm text-gray-400">Verwalte deine Bienenvölker mit modernster Präzision</p>
      </div>

      <!-- Onboarding Header (only shown during first-run) -->
      <div v-if="setupRequired" class="text-center space-y-2 bg-gray-900/80 p-4 rounded-2xl border border-primary/20">
        <div class="inline-flex items-center space-x-1.5 px-3 py-1 bg-amber-500/10 border border-amber-500/30 rounded-full text-xs font-black text-primary uppercase tracking-widest">
          <span class="inline-block h-2 w-2 rounded-full bg-primary"></span>
          <span>Ersteinrichtung</span>
        </div>
        <h3 class="text-lg font-bold text-white">Superadmin einrichten</h3>
        <p class="text-xs text-gray-300 leading-relaxed">
          Willkommen bei BeeBoard! Es wurden noch keine Konten im System gefunden. Erstelle jetzt das erste Konto, welches automatisch als System-Administrator (Superadmin) registriert wird.
        </p>
      </div>

      <!-- Tab selection (Anmelden vs. Registrieren) - ONLY if setup is NOT required -->
      <div v-if="!setupRequired" class="flex bg-gray-800/80 p-1.5 rounded-xl border border-gray-700/50">
        <button 
          @click="isLoginTab = true" 
          class="flex-1 py-2 text-center text-sm font-bold rounded-lg transition-all duration-200"
          :class="isLoginTab ? 'bg-primary text-white shadow-md' : 'text-gray-400 hover:text-white'"
        >
          Anmelden
        </button>
        <button 
          @click="isLoginTab = false" 
          class="flex-1 py-2 text-center text-sm font-bold rounded-lg transition-all duration-200"
          :class="!isLoginTab ? 'bg-primary text-white shadow-md' : 'text-gray-400 hover:text-white'"
        >
          Registrieren
        </button>
      </div>

      <!-- Error Alert -->
      <div v-if="errorMessage" class="bg-red-500/10 border border-red-500/20 text-red-400 p-4 rounded-xl text-sm flex items-start space-x-2 animate-shake">
        <svg class="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
        <span>{{ errorMessage }}</span>
      </div>

      <!-- Success Alert -->
      <div v-if="successMessage" class="bg-green-500/10 border border-green-500/20 text-green-400 p-4 rounded-xl text-sm flex items-start space-x-2">
        <svg class="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
        <span>{{ successMessage }}</span>
      </div>

      <!-- Onboarding Superadmin Setup Form -->
      <form v-if="setupRequired" class="space-y-4" @submit.prevent="handleOnboardingSetup">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-xs font-bold text-gray-200 uppercase tracking-wider mb-1">Vorname</label>
            <input 
              v-model="registerForm.firstName" 
              type="text" 
              placeholder="Max"
              class="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent placeholder-gray-500 transition-all duration-150"
            />
          </div>
          <div>
            <label class="block text-xs font-bold text-gray-200 uppercase tracking-wider mb-1">Nachname</label>
            <input 
              v-model="registerForm.lastName" 
              type="text" 
              placeholder="Mustermann"
              class="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent placeholder-gray-500 transition-all duration-150"
            />
          </div>
        </div>
        <div>
          <label class="block text-xs font-bold text-gray-200 uppercase tracking-wider mb-1">Benutzername *</label>
          <input 
            v-model="registerForm.username" 
            type="text" 
            required 
            placeholder="admin"
            class="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent placeholder-gray-500 transition-all duration-150"
          />
        </div>
        <div>
          <label class="block text-xs font-bold text-gray-200 uppercase tracking-wider mb-1">E-Mail *</label>
          <input 
            v-model="registerForm.email" 
            type="email" 
            required 
            placeholder="admin@beeboard.de"
            class="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent placeholder-gray-500 transition-all duration-150"
          />
        </div>
        <div>
          <label class="block text-xs font-bold text-gray-200 uppercase tracking-wider mb-1">Passwort *</label>
          <input 
            v-model="registerForm.password" 
            type="password" 
            required 
            placeholder="Mind. 8 Zeichen"
            class="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent placeholder-gray-500 transition-all duration-150"
          />
        </div>
        
        <button 
          type="submit" 
          :disabled="authStore.loading"
          class="w-full py-3 bg-gradient-to-r from-amber-500 to-primary hover:from-amber-600 hover:to-primary-hover text-white font-bold rounded-xl shadow-lg shadow-primary/20 transition-all duration-150 hover-scale flex items-center justify-center space-x-2 border border-amber-400/10"
        >
          <span v-if="authStore.loading">
            <!-- Spinner -->
            <svg class="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
          </span>
          <span>Superadmin erstellen & einloggen 🚀</span>
        </button>
      </form>

      <!-- Standard Forms (Only shown if setup is NOT required) -->
      <template v-else>
        <!-- Login Form -->
        <form v-if="isLoginTab" class="space-y-4" @submit.prevent="handleLogin">
          <div>
            <label class="block text-xs font-bold text-gray-400 uppercase tracking-wider mb-1">Benutzername oder E-Mail</label>
            <input 
              v-model="loginForm.username" 
              type="text" 
              required 
              placeholder="imker123"
              class="w-full px-4 py-3 bg-gray-800/50 border border-gray-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent placeholder-gray-500 transition-all duration-150"
            />
          </div>
          <div>
            <label class="block text-xs font-bold text-gray-400 uppercase tracking-wider mb-1">Passwort</label>
            <input 
              v-model="loginForm.password" 
              type="password" 
              required 
              placeholder="••••••••"
              class="w-full px-4 py-3 bg-gray-800/50 border border-gray-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent placeholder-gray-500 transition-all duration-150"
            />
          </div>
          <button 
            type="submit" 
            :disabled="authStore.loading"
            class="w-full py-3 bg-primary hover:bg-primary-hover text-white font-bold rounded-xl shadow-lg shadow-primary/20 transition-all duration-150 hover-scale flex items-center justify-center space-x-2"
          >
            <span v-if="authStore.loading">
              <!-- Spinner -->
              <svg class="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
            </span>
            <span>Einloggen</span>
          </button>
        </form>

        <!-- Register Form -->
        <form v-else class="space-y-4" @submit.prevent="handleRegister">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-bold text-gray-400 uppercase tracking-wider mb-1">Vorname</label>
              <input 
                v-model="registerForm.firstName" 
                type="text" 
                placeholder="Max"
                class="w-full px-4 py-3 bg-gray-800/50 border border-gray-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent placeholder-gray-500 transition-all duration-150"
              />
            </div>
            <div>
              <label class="block text-xs font-bold text-gray-400 uppercase tracking-wider mb-1">Nachname</label>
              <input 
                v-model="registerForm.lastName" 
                type="text" 
                placeholder="Mustermann"
                class="w-full px-4 py-3 bg-gray-800/50 border border-gray-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent placeholder-gray-500 transition-all duration-150"
              />
            </div>
          </div>
          <div>
            <label class="block text-xs font-bold text-gray-400 uppercase tracking-wider mb-1">Benutzername *</label>
            <input 
              v-model="registerForm.username" 
              type="text" 
              required 
              placeholder="imker_max"
              class="w-full px-4 py-3 bg-gray-800/50 border border-gray-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent placeholder-gray-500 transition-all duration-150"
            />
          </div>
          <div>
            <label class="block text-xs font-bold text-gray-400 uppercase tracking-wider mb-1">E-Mail *</label>
            <input 
              v-model="registerForm.email" 
              type="email" 
              required 
              placeholder="max@bienen.de"
              class="w-full px-4 py-3 bg-gray-800/50 border border-gray-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent placeholder-gray-500 transition-all duration-150"
            />
          </div>
          <div>
            <label class="block text-xs font-bold text-gray-400 uppercase tracking-wider mb-1">Passwort *</label>
            <input 
              v-model="registerForm.password" 
              type="password" 
              required 
              placeholder="Mind. 8 Zeichen"
              class="w-full px-4 py-3 bg-gray-800/50 border border-gray-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent placeholder-gray-500 transition-all duration-150"
            />
          </div>
          <button 
            type="submit" 
            :disabled="authStore.loading"
            class="w-full py-3 bg-primary hover:bg-primary-hover text-white font-bold rounded-xl shadow-lg shadow-primary/20 transition-all duration-150 hover-scale flex items-center justify-center space-x-2"
          >
            <span v-if="authStore.loading">
              <!-- Spinner -->
              <svg class="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
            </span>
            <span>Registrieren</span>
          </button>
        </form>
      </template>

    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import beeboardLogo from '../assets/beeboard-logo.svg'
import { APP_VERSION } from '../config/app.js'
import { useAuthStore } from '../stores/auth'
import { useApiaryStore } from '../stores/apiary'

const router = useRouter()
const authStore = useAuthStore()
const apiaryStore = useApiaryStore()

const setupRequired = ref(false)
const isLoginTab = ref(true)
const errorMessage = ref('')
const successMessage = ref('')

const loginForm = reactive({
  username: '',
  password: ''
})

const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  firstName: '',
  lastName: ''
})

// Check setup status when loaded
onMounted(async () => {
  try {
    const response = await axios.get('/api/auth/setup-status')
    setupRequired.value = response.data.setup_required
  } catch (err) {
    console.error('Fehler beim Laden des Setup-Status:', err)
  }
})

async function handleLogin() {
  errorMessage.value = ''
  successMessage.value = ''
  try {
    const success = await authStore.login(loginForm.username, loginForm.password)
    if (success) {
      // Fetch user apiaries immediately
      await apiaryStore.fetchApiaries()
      router.push('/dashboard')
    }
  } catch (err) {
    errorMessage.value = authStore.error
  }
}

async function handleRegister() {
  errorMessage.value = ''
  successMessage.value = ''
  if (registerForm.password.length < 8) {
    errorMessage.value = 'Das Passwort muss mindestens 8 Zeichen lang sein.'
    return
  }
  try {
    const success = await authStore.register(registerForm)
    if (success) {
      successMessage.value = 'Registrierung erfolgreich! Bitte melde dich an.'
      // Clear inputs
      registerForm.username = ''
      registerForm.email = ''
      registerForm.password = ''
      registerForm.firstName = ''
      registerForm.lastName = ''
      // Switch tab
      isLoginTab.value = true
    }
  } catch (err) {
    errorMessage.value = authStore.error
  }
}

async function handleOnboardingSetup() {
  errorMessage.value = ''
  successMessage.value = ''
  if (registerForm.password.length < 8) {
    errorMessage.value = 'Das Passwort muss mindestens 8 Zeichen lang sein.'
    return
  }
  try {
    // 1. Create Superadmin account (automatically promoted to SYSTEM_ADMIN in backend)
    const success = await authStore.register(registerForm)
    if (success) {
      successMessage.value = 'Superadmin erfolgreich registriert! Melde an...'
      
      const adminUsername = registerForm.username
      const adminPassword = registerForm.password

      // 2. Perform instant background login
      const loginSuccess = await authStore.login(adminUsername, adminPassword)
      if (loginSuccess) {
        // 3. Clear forms
        registerForm.username = ''
        registerForm.email = ''
        registerForm.password = ''
        registerForm.firstName = ''
        registerForm.lastName = ''
        
        // 4. Fetch apiaries (empty, but triggers state store initialization)
        await apiaryStore.fetchApiaries()
        
        // 5. Redirect to Dashboard
        router.push('/dashboard')
      }
    }
  } catch (err) {
    errorMessage.value = authStore.error || 'Ersteinrichtung fehlgeschlagen.'
  }
}
</script>

<style scoped>
.animate-shake {
  animation: shake 0.3s ease-in-out;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-4px); }
  75% { transform: translateX(4px); }
}
</style>
