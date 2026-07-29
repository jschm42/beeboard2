<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 font-sans">
    
    <!-- Back to Dashboard Link -->
    <router-link to="/dashboard" class="inline-flex items-center text-sm font-semibold text-primary hover:text-primary-hover mb-4 transition-colors duration-200">
      <svg class="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"/>
      </svg>
      {{ $t('common.back_to_dashboard') }}
    </router-link>

    <!-- Header Area -->
    <div class="mb-8 flex flex-col sm:flex-row sm:justify-between sm:items-center space-y-4 sm:space-y-0">
      <div>
        <h1 class="text-3xl font-extrabold text-gray-900 dark:text-white tracking-tight flex items-center gap-2.5">
          <span class="p-2 bg-primary/10 rounded-2xl text-primary leading-none text-2xl">🔑</span>
          {{ $t('sidebar.api_keys') }}
        </h1>
        <p class="text-gray-500 dark:text-gray-400 mt-1">
          Verwalte Zugriffsschlüssel für externe KI-Agenten (wie Hermes) und Drittanwendungen.
        </p>
      </div>
      <button 
        @click="openCreateModal" 
        class="px-5 py-2.5 bg-primary hover:bg-primary-hover text-white font-extrabold text-sm rounded-xl shadow-md shadow-primary/20 hover-scale flex items-center justify-center space-x-2 cursor-pointer"
      >
        <span>+ Neuen Schlüssel generieren</span>
      </button>
    </div>

    <!-- Alert / Info Message -->
    <div class="mb-6 p-4 bg-blue-50 dark:bg-blue-950/30 border border-blue-100 dark:border-blue-900/50 rounded-2xl text-sm flex items-start space-x-3 text-blue-700 dark:text-blue-300">
      <svg class="w-5 h-5 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
      </svg>
      <div>
        <p class="font-semibold mb-0.5">Model Context Protocol (MCP)</p>
        <p>Du kannst diesen API-Key verwenden, um den Beeboard-MCP-Server lokal oder über das Netzwerk an Hermes oder einen anderen MCP-Client anzubinden. Setze dazu einfach die Umgebungsvariable <code class="px-1.5 py-0.5 bg-blue-100 dark:bg-blue-900 rounded font-mono text-xs text-blue-900 dark:text-blue-100 font-bold">BEEBOARD_API_KEY</code> auf den Wert deines generierten Schlüssels.</p>
      </div>
    </div>

    <!-- Create Modal / Form -->
    <div v-if="showModal" class="fixed inset-0 z-50 overflow-y-auto flex items-center justify-center p-4 bg-gray-900/50 dark:bg-black/70 backdrop-blur-sm animate-fade-in">
      <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl shadow-2xl w-full max-w-lg p-6 animate-scale">
        <div class="flex justify-between items-center mb-6 pb-4 border-b border-gray-100 dark:border-dark-border">
          <h3 class="text-xl font-bold text-gray-900 dark:text-white">API-Schlüssel generieren</h3>
          <button @click="closeModal" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 cursor-pointer">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
        
        <form @submit.prevent="submitForm">
          <div class="space-y-4">
            <div>
              <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1.5">Bezeichnung / Name *</label>
              <input 
                v-model="form.name" 
                type="text" 
                required
                placeholder="z. B. Hermes KI-Agent"
                class="w-full px-3 py-2.5 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm transition-all"
              />
            </div>

            <div>
              <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1.5">Gültigkeit / Ablauf</label>
              <select 
                v-model="form.expires_days"
                class="w-full px-3 py-2.5 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm transition-all"
              >
                <option :value="null">Unbegrenzt gültig (Empfohlen für Agents)</option>
                <option :value="7">7 Tage gültig</option>
                <option :value="30">30 Tage gültig</option>
                <option :value="90">90 Tage gültig</option>
                <option :value="365">1 Jahr gültig</option>
              </select>
            </div>
          </div>

          <div class="flex justify-end space-x-3 mt-6 border-t border-gray-100 dark:border-dark-border pt-4">
            <button 
              type="button" 
              @click="closeModal" 
              class="px-4 py-2 text-sm font-bold text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 cursor-pointer"
            >
              {{ $t('common.cancel') }}
            </button>
            <button 
              type="submit" 
              :disabled="saving"
              class="px-5 py-2 bg-primary hover:bg-primary-hover text-white text-sm font-extrabold rounded-xl shadow-md shadow-primary/10 hover-scale transition-all flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
            >
              <span v-if="saving">Generiere...</span>
              <span v-else>Generieren</span>
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Generated Key Success Modal (Shows key exactly once) -->
    <div v-if="showGeneratedModal" class="fixed inset-0 z-50 overflow-y-auto flex items-center justify-center p-4 bg-gray-900/50 dark:bg-black/70 backdrop-blur-sm animate-fade-in">
      <div class="bg-white dark:bg-dark-card border-2 border-emerald-500 dark:border-emerald-600 rounded-3xl shadow-2xl w-full max-w-lg p-6 animate-scale">
        <div class="text-center mb-5">
          <div class="w-12 h-12 bg-emerald-100 dark:bg-emerald-950/50 text-emerald-600 dark:text-emerald-400 rounded-full flex items-center justify-center mx-auto mb-3 text-2xl font-bold">✓</div>
          <h3 class="text-xl font-bold text-gray-900 dark:text-white">API-Schlüssel generiert!</h3>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">Dieser Schlüssel wird dir nur ein einziges Mal angezeigt. Bitte speichere ihn sicher ab.</p>
        </div>

        <div class="bg-gray-50 dark:bg-dark-bg border border-gray-200 dark:border-dark-border p-4 rounded-2xl flex items-center justify-between gap-3 mb-4 font-mono text-sm break-all relative">
          <span class="text-gray-800 dark:text-gray-200 font-bold select-all">{{ generatedKey }}</span>
          <button 
            @click="copyToClipboard" 
            class="shrink-0 p-2 bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border text-gray-500 hover:text-primary dark:hover:text-primary rounded-xl shadow-sm transition-all hover-scale cursor-pointer"
            title="Kopieren"
          >
            <span v-if="copySuccess" class="text-emerald-500 text-xs font-bold font-sans">Kopiert!</span>
            <svg v-else class="w-4.5 h-4.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3"/>
            </svg>
          </button>
        </div>

        <div class="p-3.5 bg-amber-50 dark:bg-amber-950/20 border border-amber-100 dark:border-amber-900/30 text-amber-800 dark:text-amber-300 rounded-xl text-xs flex items-start space-x-2 mb-6">
          <svg class="w-4 h-4 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
          </svg>
          <span><strong>Wichtig:</strong> Wenn du dieses Fenster schließt, kannst du den Schlüssel nicht mehr abrufen oder kopieren! Kopiere ihn jetzt.</span>
        </div>

        <div class="flex justify-end">
          <button 
            @click="closeGeneratedModal" 
            class="px-5 py-2.5 bg-gray-900 hover:bg-black dark:bg-emerald-600 dark:hover:bg-emerald-700 text-white font-extrabold text-sm rounded-xl hover-scale cursor-pointer"
          >
            Fertig, ich habe den Schlüssel kopiert
          </button>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex flex-col items-center justify-center py-20">
      <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-primary"></div>
      <p class="text-gray-500 dark:text-gray-400 mt-4 font-semibold text-sm">Lade API-Schlüssel...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="apiKeys.length === 0" class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-12 text-center max-w-xl mx-auto shadow-sm">
      <div class="text-5xl mb-4">🔑</div>
      <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-2">Noch keine API-Schlüssel</h3>
      <p class="text-gray-500 dark:text-gray-400 text-sm mb-6">Erstelle deinen ersten API-Schlüssel, um externen KI-Agenten oder Programmen Zugriff auf deine Imkerei-Daten zu geben.</p>
      <button 
        @click="openCreateModal" 
        class="px-5 py-2.5 bg-primary hover:bg-primary-hover text-white font-extrabold text-sm rounded-xl hover-scale cursor-pointer"
      >
        + Neuen Schlüssel generieren
      </button>
    </div>

    <!-- Keys List -->
    <div v-else class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl shadow-sm overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="bg-gray-50 dark:bg-dark-bg border-b border-gray-100 dark:border-dark-border text-xs font-bold text-gray-400 dark:text-gray-500 uppercase tracking-wider">
              <th class="px-6 py-4">Bezeichnung</th>
              <th class="px-6 py-4">Status</th>
              <th class="px-6 py-4">Erstellt am</th>
              <th class="px-6 py-4">Gültig bis</th>
              <th class="px-6 py-4 text-right">Aktionen</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100 dark:divide-dark-border text-sm">
            <tr v-for="key in apiKeys" :key="key.id" class="hover:bg-gray-50/50 dark:hover:bg-dark-bg/20 transition-all">
              <td class="px-6 py-4.5 font-bold text-gray-800 dark:text-gray-100">
                {{ key.name }}
              </td>
              <td class="px-6 py-4.5">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 dark:bg-emerald-950/30 dark:text-emerald-400 border border-emerald-100 dark:border-emerald-900/40">
                  <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 mr-1.5 animate-pulse"></span>
                  Aktiv
                </span>
              </td>
              <td class="px-6 py-4.5 text-gray-500 dark:text-gray-400">
                {{ formatDate(key.created_at) }}
              </td>
              <td class="px-6 py-4.5 text-gray-500 dark:text-gray-400">
                {{ key.expires_at ? formatDate(key.expires_at) : 'Unbegrenzt' }}
              </td>
              <td class="px-6 py-4.5 text-right">
                <button 
                  @click="deleteKey(key)" 
                  class="px-3 py-1.5 text-red-600 hover:text-white hover:bg-red-500 dark:hover:bg-red-600 border border-red-100 dark:border-red-950 text-xs font-bold rounded-xl shadow-sm hover-scale transition-all cursor-pointer"
                >
                  Widerrufen
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <!-- MCP Integration Guide -->
    <div v-if="mcpInfo" class="mt-8 bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-6 shadow-sm">
      <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6 pb-4 border-b border-gray-100 dark:border-dark-border">
        <div>
          <h3 class="text-lg font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <span>🤖</span> Model Context Protocol (MCP) Integration
          </h3>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">Binde Beeboard2 als Toolset in deine KI-Agenten (Hermes, Claude Desktop, etc.) ein.</p>
        </div>
        <!-- Tab Selector -->
        <div class="flex bg-gray-100 dark:bg-dark-bg p-1 rounded-xl">
          <button 
            type="button"
            @click="activeTab = 'sse'" 
            class="px-4 py-1.5 text-xs font-bold rounded-lg transition-all cursor-pointer"
            :class="activeTab === 'sse' ? 'bg-white dark:bg-dark-card text-primary shadow-sm' : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'"
          >
            Docker & API (SSE)
          </button>
          <button 
            type="button"
            @click="activeTab = 'stdio'" 
            class="px-4 py-1.5 text-xs font-bold rounded-lg transition-all cursor-pointer"
            :class="activeTab === 'stdio' ? 'bg-white dark:bg-dark-card text-primary shadow-sm' : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'"
          >
            Lokaler Prozess (Stdio)
          </button>
        </div>
      </div>

      <!-- Option 1: SSE / Docker (Selected) -->
      <div v-if="activeTab === 'sse'" class="space-y-4 animate-fade-in">
        <p class="text-sm text-gray-500 dark:text-gray-400">
          Empfohlen für Docker-Setups oder wenn die KI von außerhalb auf Beeboard2 zugreifen soll. Der MCP-Server wird direkt über das HTTP-API-Gateway bereitgestellt.
        </p>
        
        <div>
          <label class="block text-xs font-bold text-gray-400 dark:text-gray-500 uppercase tracking-wider mb-1.5">Ziel-API-Endpunkt (SSE URL)</label>
          <div class="flex items-center gap-2 bg-gray-50 dark:bg-dark-bg border border-gray-200 dark:border-dark-border rounded-xl p-3 font-mono text-xs break-all relative">
            <span class="text-gray-800 dark:text-gray-200 font-bold select-all flex-grow">{{ sseUrl }}</span>
            <button 
              type="button"
              @click="copySseUrl" 
              class="shrink-0 px-3 py-1.5 bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border hover:text-primary rounded-xl text-gray-500 text-xs font-bold shadow-sm transition-all hover-scale cursor-pointer"
            >
              <span v-if="sseCopySuccess" class="text-emerald-500">Kopiert!</span>
              <span v-else>Kopieren</span>
            </button>
          </div>
        </div>

        <div>
          <label class="block text-xs font-bold text-gray-400 dark:text-gray-500 uppercase tracking-wider mb-1.5">Claude / Hermes Client-Konfiguration</label>
          <div class="relative bg-gray-50 dark:bg-dark-bg border border-gray-200 dark:border-dark-border rounded-2xl p-4 font-mono text-xs overflow-x-auto text-gray-800 dark:text-gray-200">
            <button 
              type="button"
              @click="copyConfigToClipboard" 
              class="absolute top-3 right-3 px-3 py-1.5 bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border hover:text-primary rounded-xl text-gray-500 text-xs font-bold shadow-sm transition-all hover-scale cursor-pointer"
            >
              <span v-if="configCopySuccess" class="text-emerald-500">Kopiert!</span>
              <span v-else>Kopieren</span>
            </button>
            <pre class="leading-relaxed select-all">{{ formattedMcpConfig }}</pre>
          </div>
        </div>
      </div>

      <!-- Option 2: Stdio (Local Process) -->
      <div v-else class="space-y-4 animate-fade-in">
        <p class="text-sm text-gray-500 dark:text-gray-400">
          Verwendet den lokalen Python-Prozess direkt im Workspace. Gut geeignet für Entwicklungszwecke, wenn der Client auf demselben Rechner läuft.
        </p>

        <div>
          <label class="block text-xs font-bold text-gray-400 dark:text-gray-500 uppercase tracking-wider mb-1.5">Stdio Client-Konfiguration</label>
          <div class="relative bg-gray-50 dark:bg-dark-bg border border-gray-200 dark:border-dark-border rounded-2xl p-4 font-mono text-xs overflow-x-auto text-gray-800 dark:text-gray-200">
            <button 
              type="button"
              @click="copyStdioConfig" 
              class="absolute top-3 right-3 px-3 py-1.5 bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border hover:text-primary rounded-xl text-gray-500 text-xs font-bold shadow-sm transition-all hover-scale cursor-pointer"
            >
              <span v-if="stdioCopySuccess" class="text-emerald-500">Kopiert!</span>
              <span v-else>Kopieren</span>
            </button>
            <pre class="leading-relaxed select-all">{{ formattedStdioConfig }}</pre>
          </div>
        </div>
      </div>

      <p class="text-xs text-amber-600 dark:text-amber-400 mt-3 flex items-center gap-1.5">
        <span>⚠️</span> Ersetze <code class="px-1 bg-amber-50 dark:bg-amber-950 border border-amber-200 dark:border-amber-900 rounded font-mono font-bold">DEIN_API_KEY</code> durch einen oben generierten API-Schlüssel.
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'

const apiKeys = ref([])
const loading = ref(true)
const mcpInfo = ref(null)
const activeTab = ref('sse')
const configCopySuccess = ref(false)
const sseCopySuccess = ref(false)
const stdioCopySuccess = ref(false)
const showModal = ref(false)
const showGeneratedModal = ref(false)
const saving = ref(false)
const generatedKey = ref('')
const copySuccess = ref(false)

const form = ref({
  name: '',
  expires_days: null
})

async function fetchKeys() {
  loading.value = true
  try {
    const res = await axios.get('/api/api-keys')
    apiKeys.value = res.data
  } catch (err) {
    console.error('Failed to fetch api keys:', err)
  } finally {
    loading.value = false
  }
}

function openCreateModal() {
  form.value.name = ''
  form.value.expires_days = null
  showModal.value = true
}

function closeModal() {
  showModal.value = false
}

async function submitForm() {
  saving.value = true
  try {
    const res = await axios.post('/api/api-keys', form.value)
    generatedKey.value = res.data.raw_key
    showModal.value = false
    showGeneratedModal.value = true
    await fetchKeys()
  } catch (err) {
    console.error('Failed to generate API key:', err)
  } finally {
    saving.value = false
  }
}

function copyToClipboard() {
  navigator.clipboard.writeText(generatedKey.value)
  copySuccess.value = true
  setTimeout(() => {
    copySuccess.value = false
  }, 2000)
}

function closeGeneratedModal() {
  showGeneratedModal.value = false
  generatedKey.value = ''
}

async function deleteKey(key) {
  if (!confirm(`Möchtest du den API-Schlüssel "${key.name}" wirklich widerrufen? Externe Anwendungen verlieren sofort ihren Zugriff.`)) {
    return
  }
  try {
    await axios.delete(`/api/api-keys/${key.id}`)
    await fetchKeys()
  } catch (err) {
    console.error('Failed to revoke API key:', err)
  }
}

function formatDate(dtStr) {
  if (!dtStr) return ''
  const d = new Date(dtStr)
  return d.toLocaleDateString('de-DE', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

async function fetchMcpInfo() {
  try {
    const res = await axios.get('/api/api-keys/mcp-info')
    mcpInfo.value = res.data
  } catch (err) {
    console.error('Failed to fetch MCP info:', err)
  }
}

const sseUrl = computed(() => {
  return `${window.location.origin}/mcp/sse?api_key=DEIN_API_KEY`
})

const formattedMcpConfig = computed(() => {
  if (!mcpInfo.value) return ''
  const configObj = {
    beeboard: {
      url: sseUrl.value
    }
  }
  return JSON.stringify(configObj, null, 2)
})

const formattedStdioConfig = computed(() => {
  if (!mcpInfo.value) return ''
  const configObj = {
    beeboard: {
      command: mcpInfo.value.command,
      args: mcpInfo.value.args,
      cwd: mcpInfo.value.cwd,
      env: {
        BEEBOARD_API_KEY: "DEIN_API_KEY"
      }
    }
  }
  return JSON.stringify(configObj, null, 2)
})

function copyConfigToClipboard() {
  navigator.clipboard.writeText(formattedMcpConfig.value)
  configCopySuccess.value = true
  setTimeout(() => {
    configCopySuccess.value = false
  }, 2000)
}

function copySseUrl() {
  navigator.clipboard.writeText(sseUrl.value)
  sseCopySuccess.value = true
  setTimeout(() => {
    sseCopySuccess.value = false
  }, 2000)
}

function copyStdioConfig() {
  navigator.clipboard.writeText(formattedStdioConfig.value)
  stdioCopySuccess.value = true
  setTimeout(() => {
    stdioCopySuccess.value = false
  }, 2000)
}

onMounted(() => {
  fetchKeys()
  fetchMcpInfo()
})
</script>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.2s ease-out forwards;
}
.animate-scale {
  animation: scaleUp 0.2s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes scaleUp {
  from { transform: scale(0.95); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}
</style>
