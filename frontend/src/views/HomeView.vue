<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    
    <!-- Welcome Header -->
    <div class="mb-8 flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-4 sm:space-y-0">
      <div>
        <h1 class="text-3xl font-extrabold text-gray-900 dark:text-white tracking-tight">
          Hallo, {{ authStore.user?.first_name || authStore.user?.username }}!
        </h1>
        <p v-if="apiaryStore.activeApiary" class="text-gray-500 dark:text-gray-400 mt-1">
          Willkommen zurück auf deinem Bienenstand. Hier ist der aktuelle Zustand der Imkerei <span class="font-bold text-primary">{{ apiaryStore.activeApiary?.name }}</span>.
        </p>
        <p v-else class="text-gray-500 dark:text-gray-400 mt-1">
          Willkommen auf deinem Bienenstand. Richte bitte deine Imkerei ein, um mit BeeBoard zu starten.
        </p>
      </div>
      <div v-if="apiaryStore.activeApiary" class="flex items-center space-x-2 bg-primary/10 border border-primary/20 text-primary px-4 py-2 rounded-2xl">
        <svg class="w-5 h-5 fill-primary" viewBox="0 0 24 24"><path d="M12 2C11.5 2 11 2.2 10.6 2.6L7.4 5.8C6.9 6.3 6.9 7.1 7.4 7.6L8.4 8.6C7.6 9.8 7 11 7 12H5C3.3 12 2 13.3 2 15C2 16.7 3.3 18 5 18H7C7 19.1 7.9 20 9 20H15C16.1 20 17 19.1 17 18H19C20.7 18 22 16.7 22 15C22 13.3 20.7 12 19 12H17C17 11 16.4 9.8 15.6 8.6L16.6 7.6C17.1 7.1 17.1 6.3 16.6 5.8L13.4 2.6C13 2.2 12.5 2 12 2M12 4L14.4 6.4L13 7.8L12.5 7.3C12.1 6.9 11.3 6.9 10.9 7.3L10.4 7.8L9.6 7L12 4M9 10H15V12H9V10M5 14H19C19.6 14 20 14.4 20 15C20 15.6 19.6 16 19 16H5C4.4 16 4 15.6 4 15C4 14.4 4.4 14 5 14M9 18H15V19H9V18Z"/></svg>
        <span class="text-sm font-bold uppercase tracking-wider">Aktiv</span>
      </div>
    </div>

    <!-- Beautiful Inline creation form instead of modal or blank page -->
    <div v-if="!apiaryStore.activeApiaryId" class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl shadow-xl w-full max-w-md p-8 mx-auto space-y-6">
      <div class="text-center">
        <div class="inline-flex items-center justify-center p-3.5 bg-primary/10 rounded-full mb-3">
          <!-- Bee SVG Icon -->
          <svg class="w-10 h-10 fill-primary" viewBox="0 0 24 24">
            <path d="M12 2C11.5 2 11 2.2 10.6 2.6L7.4 5.8C6.9 6.3 6.9 7.1 7.4 7.6L8.4 8.6C7.6 9.8 7 11 7 12H5C3.3 12 2 13.3 2 15C2 16.7 3.3 18 5 18H7C7 19.1 7.9 20 9 20H15C16.1 20 17 19.1 17 18H19C20.7 18 22 16.7 22 15C22 13.3 20.7 12 19 12H17C17 11 16.4 9.8 15.6 8.6L16.6 7.6C17.1 7.1 17.1 6.3 16.6 5.8L13.4 2.6C13 2.2 12.5 2 12 2M12 4L14.4 6.4L13 7.8L12.5 7.3C12.1 6.9 11.3 6.9 10.9 7.3L10.4 7.8L9.6 7L12 4M9 10H15V12H9V10M5 14H19C19.6 14 20 14.4 20 15C20 15.6 19.6 16 19 16H5C4.4 16 4 15.6 4 15C4 14.4 4.4 14 5 14M9 18H15V19H9V18Z"/>
          </svg>
        </div>
        <h3 class="text-xl font-extrabold text-gray-900 dark:text-white">Neue Imkerei anlegen</h3>
        <p class="text-xs text-gray-500 dark:text-gray-400 mt-1 leading-relaxed">
          Um BeeBoard nutzen zu können, lege bitte zuerst deine Imkerei an.
        </p>
      </div>

      <form @submit.prevent="createApiary" class="space-y-4">
        <div>
          <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">Name der Imkerei *</label>
          <input 
            v-model="newApiaryName" 
            type="text" 
            required
            placeholder="z.B. Imkerei Sonnenschein"
            class="w-full px-4 py-3 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm"
          />
        </div>
        <div>
          <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">Anmerkungen (Optional)</label>
          <textarea 
            v-model="newApiaryNotes" 
            placeholder="z.B. Standorte hauptsächlich im Odenwald"
            rows="3"
            class="w-full px-4 py-3 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm"
          ></textarea>
        </div>
        <button 
          type="submit" 
          :disabled="apiaryStore.loading"
          class="w-full py-3 text-sm font-bold text-white bg-primary hover:bg-primary-hover rounded-xl shadow-md hover-scale flex items-center justify-center space-x-2"
        >
          <span v-if="apiaryStore.loading">
            <!-- Spinner -->
            <svg class="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
          </span>
          <span>Imkerei erstellen 🚀</span>
        </button>
      </form>
    </div>

    <div v-else-if="loading" class="flex flex-col items-center justify-center py-20">
      <svg class="animate-spin h-10 w-10 text-primary mb-4" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
      <p class="text-gray-500 dark:text-gray-400 font-bold">Lade Bienenstand-Daten...</p>
    </div>

    <div v-else class="space-y-8">
      
      <!-- Varroa Warning Banner -->
      <div v-if="varroaWarnings.length > 0" class="space-y-3">
        <div v-for="warning in varroaWarnings" :key="warning.hive_id" class="bg-amber-500/10 border border-amber-500/20 text-amber-800 dark:text-amber-400 p-5 rounded-2xl flex items-start space-x-4 shadow-sm animate-pulse">
          <div class="p-2 bg-amber-500/10 rounded-xl shrink-0">
            <svg class="w-6 h-6 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
          </div>
          <div>
            <h4 class="font-bold text-base">Achtung: Erhöhter Milbenfall!</h4>
            <p class="text-sm mt-1 text-gray-700 dark:text-gray-300">
              Bei <strong>{{ warning.hive_name }}</strong> wurde am {{ formatDate(warning.date) }} ein geschätzter natürlicher Varroamilbenfall von <strong class="text-amber-600 dark:text-amber-400">{{ warning.estimated_total.toFixed(1) }} Milben/Tag</strong> festgestellt (Gemessener Wert: {{ warning.raw_count }} Milben in der Saison {{ warning.season }}). 
            </p>
            <p class="text-sm mt-1 font-bold text-primary">
              Empfehlung: Leite umgehend eine Varroabehandlung ein oder kontrolliere die Beute.
            </p>
          </div>
        </div>
      </div>


      <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-6 shadow-sm">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-bold text-gray-900 dark:text-white">🗓️ Fällige Termine (14 Tage)</h3>
          <router-link to="/tasks?view=calendar" class="text-xs font-extrabold text-primary hover:underline uppercase tracking-wider">
            Kalender öffnen
          </router-link>
        </div>

        <div v-if="dueScheduleItems.length === 0" class="text-sm text-gray-500 dark:text-gray-400 italic">
          Keine fälligen Aufgaben oder Termine in den nächsten 14 Tagen.
        </div>

        <div v-else class="space-y-2">
          <div
            v-for="item in dueScheduleItems"
            :key="item.id"
            class="p-3 rounded-2xl border flex items-start justify-between gap-3"
            :class="item.status === 'overdue'
              ? 'border-red-200 bg-red-50/70 dark:border-red-900/40 dark:bg-red-950/15'
              : item.status === 'today'
                ? 'border-amber-200 bg-amber-50/80 dark:border-amber-900/40 dark:bg-amber-950/15'
                : 'border-gray-200 bg-gray-50 dark:border-dark-border dark:bg-dark-bg/60'"
          >
            <div>
              <div class="text-sm font-bold text-gray-900 dark:text-white">{{ item.title }}</div>
              <div class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">{{ item.subtitle }}</div>
            </div>

            <div class="shrink-0 flex flex-col items-end gap-1">
              <span class="text-[10px] font-black uppercase px-2 py-0.5 rounded-full"
                :class="item.kind === 'task' ? 'bg-primary/15 text-primary' : 'bg-blue-500/15 text-blue-600 dark:text-blue-400'"
              >
                {{ item.kind === 'task' ? 'Aufgabe' : 'Termin' }}
              </span>
              <span class="text-[10px] font-bold uppercase"
                :class="item.status === 'overdue' ? 'text-red-500' : item.status === 'today' ? 'text-amber-600 dark:text-amber-400' : 'text-gray-500 dark:text-gray-400'"
              >
                {{ item.statusLabel }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Main Layout: Tasks left, Activity Stream right -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        <!-- Left 2 Cols: Smart Tasks & Insights -->
        <div class="lg:col-span-2 space-y-6">
          
          <!-- Intelligent Tasks Card -->
          <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-6 shadow-sm">
            <div class="flex justify-between items-center mb-6">
              <h3 class="text-lg font-bold text-gray-900 dark:text-white flex items-center space-x-2">
                <span>📋 Anstehende Aufgaben & Empfehlungen</span>
              </h3>
              <span class="px-2.5 py-1 bg-primary/10 text-primary text-xs font-extrabold rounded-full">
                {{ tasks.length }} Aufgaben
              </span>
            </div>

            <!-- Add quick manual task -->
            <form @submit.prevent="addManualTask" class="mb-6 flex space-x-2">
              <input 
                v-model="newTaskTitle" 
                type="text" 
                placeholder="z.B. Honigraum aufsetzen bei Volk 3..."
                required
                class="flex-grow px-4 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent text-sm"
              />
              <button type="submit" class="px-4 py-2 bg-primary hover:bg-primary-hover text-white font-bold rounded-xl text-sm shadow-md hover-scale shrink-0">
                + Hinzufügen
              </button>
            </form>

            <div v-if="tasks.length === 0" class="text-center py-8 text-gray-400">
              <p>Hervorragend! Keine fälligen Aufgaben oder Warnungen auf deinem Bienenstand.</p>
            </div>

            <div v-else class="space-y-3">
              <div 
                v-for="task in tasks" 
                :key="task.id" 
                class="p-4 rounded-2xl flex items-center justify-between transition-all duration-150 border"
                :class="task.urgent 
                  ? 'bg-red-500/5 dark:bg-red-500/10 border-red-500/20' 
                  : 'bg-gray-50 dark:bg-dark-bg border-gray-200 dark:border-gray-800'"
              >
                <div class="flex items-center space-x-3">
                  <button 
                    @click="completeTask(task.id)"
                    class="w-5 h-5 rounded-full border-2 border-gray-300 dark:border-gray-600 hover:border-primary flex items-center justify-center transition-colors shrink-0"
                  >
                    <div class="w-2.5 h-2.5 bg-primary rounded-full opacity-0 hover:opacity-100 transition-opacity"></div>
                  </button>
                  <div>
                    <p class="text-sm font-bold text-gray-800 dark:text-gray-200" :class="{'line-through text-gray-400': task.completed}">
                      {{ task.title }}
                    </p>
                    <p class="text-xs text-gray-400 mt-0.5">
                      {{ task.subtitle }}
                    </p>
                  </div>
                </div>
                <span 
                  v-if="task.urgent" 
                  class="px-2 py-0.5 bg-red-500/10 text-red-500 text-[10px] font-bold uppercase rounded-full shrink-0"
                >
                  Dringend
                </span>
              </div>
            </div>

          </div>

          <!-- Quick AI Assistant / Insight Banner -->
          <div v-if="latestInsight" class="bg-gradient-to-br from-amber-50 to-orange-50 border border-amber-200 dark:from-dark-card dark:to-dark-bg dark:border-amber-900/50 rounded-3xl p-6 shadow-sm relative overflow-hidden">
            <div class="flex items-center gap-2 mb-4">
              <span class="bg-amber-100 text-amber-800 dark:bg-amber-900/50 dark:text-amber-300 text-xs font-black uppercase px-3 py-1 rounded-full">KI-Analyse</span>
              <span class="text-xs text-gray-500 dark:text-gray-400 font-bold uppercase tracking-widest">{{ formatDateTime(latestInsight.created_at) }}</span>
            </div>
            <h3 class="text-xl font-black mb-3 text-gray-900 dark:text-white">{{ latestInsight.title }}</h3>
            <div class="prose dark:prose-invert max-w-none text-sm text-gray-700 dark:text-gray-300 line-clamp-4 markdown-content mb-4" v-html="renderMarkdown(latestInsight.content)"></div>
            <router-link to="/ai-insights" class="inline-block px-5 py-2 bg-amber-500 hover:bg-amber-600 text-white font-extrabold text-sm rounded-xl shadow-sm hover-scale transition-colors">
              Ganzer Beitrag & Mehr Insights 🐝
            </router-link>
          </div>
          
          <div v-else class="bg-gradient-to-r from-amber-500 to-amber-600 rounded-3xl p-6 text-white shadow-lg relative overflow-hidden">
            <!-- Bee vector background design -->
            <div class="absolute right-0 bottom-0 opacity-10 transform translate-y-1/4 translate-x-1/4">
              <svg class="w-72 h-72 fill-white" viewBox="0 0 24 24"><path d="M12 2C11.5 2 11 2.2 10.6 2.6L7.4 5.8C6.9 6.3 6.9 7.1 7.4 7.6L8.4 8.6C7.6 9.8 7 11 7 12H5C3.3 12 2 13.3 2 15C2 16.7 3.3 18 5 18H7C7 19.1 7.9 20 9 20H15C16.1 20 17 19.1 17 18H19C20.7 18 22 16.7 22 15C22 13.3 20.7 12 19 12H17C17 11 16.4 9.8 15.6 8.6L16.6 7.6C17.1 7.1 17.1 6.3 16.6 5.8L13.4 2.6C13 2.2 12.5 2 12 2Z"/></svg>
            </div>

            <h3 class="text-xl font-black mb-2">Fragen an deine Bienen?</h3>
            <p class="text-sm opacity-90 max-w-lg mb-4">
              Unser KI-Imkerassistent analysiert deine Standorte, die Volksstärken und Varroaverläufe, um dir kompetenten Rat zu geben oder gesprochene Notizen automatisch in Logbucheinträge umzuwandeln.
            </p>
            <router-link to="/ai-insights" class="inline-block px-5 py-2.5 bg-white text-amber-700 font-extrabold text-sm rounded-xl shadow-md hover:bg-gray-100 hover-scale">
              KI-Insights öffnen 🐝
            </router-link>
          </div>

        </div>

        <!-- Right 1 Col: Recent Activities Log -->
        <div class="space-y-6">
          <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-6 shadow-sm">
            <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-6">🔔 Letzte Aktivitäten</h3>
            
            <div v-if="recentEntries.length === 0" class="text-center py-10 text-gray-400">
              <p>Noch keine Logbucheinträge vorhanden.</p>
              <router-link to="/logbook" class="text-primary hover:underline text-sm font-bold block mt-2">
                Jetzt Eintrag erfassen ->
              </router-link>
            </div>

            <div v-else class="space-y-6 relative before:absolute before:left-[17px] before:top-2 before:bottom-2 before:w-0.5 before:bg-gray-100 dark:before:bg-dark-border">
              <div 
                v-for="entry in recentEntries" 
                :key="entry.id" 
                class="flex items-start space-x-4 relative"
              >
                <!-- Dot marker with conditional colors -->
                <div 
                  class="w-9 h-9 rounded-full flex items-center justify-center shadow-sm shrink-0 z-10 border border-white dark:border-dark-card"
                  :class="getEntryColorClass(entry.entry_type)"
                >
                  <span class="text-xs">{{ getEntryIcon(entry.entry_type) }}</span>
                </div>
                
                <div class="flex-grow">
                  <div class="flex justify-between items-start">
                    <h4 class="text-sm font-bold text-gray-800 dark:text-gray-200">
                      {{ entry.hive?.name }}
                    </h4>
                    <span class="text-[10px] text-gray-400 uppercase font-bold">{{ formatDate(entry.date) }}</span>
                  </div>
                  <p class="text-xs text-gray-500 font-semibold uppercase mt-0.5 tracking-wider">
                    {{ getEntryTypeName(entry.entry_type) }}
                  </p>
                  <p class="text-xs text-gray-600 dark:text-gray-400 mt-1 line-clamp-2 italic">
                    "{{ entry.notes || 'Keine Anmerkungen erfasst.' }}"
                  </p>
                </div>
              </div>
            </div>

            <div class="border-t border-gray-100 dark:border-dark-border mt-6 pt-4 text-center">
              <router-link to="/logbook" class="text-primary hover:text-primary-hover text-sm font-bold hover:underline">
                Alle Aktivitäten ansehen
              </router-link>
            </div>
          </div>
        </div>

      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useApiaryStore } from '../stores/apiary'
import { useErrorStore } from '../stores/error'
import { getCustomCalendarEvents, classifyDueStatus } from '../utils/calendarEvents'
import axios from 'axios'
import { marked } from 'marked'
import DOMPurify from 'dompurify'

const authStore = useAuthStore()
const apiaryStore = useApiaryStore()
const errorStore = useErrorStore()

const loading = ref(false)
const locations = ref([])
const hives = ref([])
const recentEntries = ref([])
const tasks = ref([])
const newTaskTitle = ref('')
const latestInsight = ref(null)
const dueScheduleItems = ref([])

const newApiaryName = ref('')
const newApiaryNotes = ref('')

const activeHivesCount = computed(() => hives.value.filter(h => h.is_active).length)

// Calculations based on recent inspection entries
const estimatedTotalBees = ref(0)
const estimatedTotalFood = ref(0)
const varroaWarnings = ref([])

onMounted(async () => {
  if (apiaryStore.activeApiaryId) {
    await fetchDashboardData()
  }
})

async function fetchDashboardData() {
  loading.value = true
  try {
    const apiaryId = apiaryStore.activeApiaryId
    
    // Fetch locations, hives, tasks, and entries in parallel
    const [locRes, hiveRes, logRes, insightRes, tasksRes] = await Promise.all([
      axios.get('/api/locations', { params: { apiary_id: apiaryId } }),
      axios.get('/api/hives', { params: { apiary_id: apiaryId } }),
      axios.get('/api/logbook/entries', { params: { apiary_id: apiaryId } }),
      axios.get('/api/ai-insights/latest', { params: { apiary_id: apiaryId } }).catch(() => ({ data: null })),
      axios.get('/api/tasks', { params: { apiary_id: apiaryId, is_completed: false } })
    ])
    
    locations.value = locRes.data
    hives.value = hiveRes.data
    recentEntries.value = logRes.data.slice(0, 5) // recent 5 entries
    latestInsight.value = insightRes.data

    // Calculate biological aggregates from recent hive inspections
    calculateBiologicalAggregates(logRes.data)
    
    // Generate intelligent system-driven tasks
    generateIntelligentTasks(logRes.data, tasksRes.data)

    const customEvents = getCustomCalendarEvents(apiaryId)
    dueScheduleItems.value = buildDueScheduleOverview(tasksRes.data, customEvents)

  } catch (err) {
    console.error('Fetch dashboard data failed:', err)
  } finally {
    loading.value = false
  }
}

function calculateBiologicalAggregates(entries) {
  let totalBees = 0
  let totalFood = 0
  const processedHives = new Set()
  varroaWarnings.value = []

  // Entries are pre-sorted by date desc
  for (const entry of entries) {
    // 1. Process latest inspection per hive to calculate sum masses
    if (entry.entry_type === 'INSPECTION' && !processedHives.has(entry.hive_id) && entry.inspection_detail) {
      processedHives.add(entry.hive_id)
      
      // We look at frames
      let bees = 0
      let food = 0
      const hiveObj = hives.value.find(h => h.id === entry.hive_id)
      const beeFactor = hiveObj?.frame_type?.bee_multiplier || 1.0
      const foodFactor = hiveObj?.frame_type?.food_multiplier || 1.0
      
      if (entry.inspection_detail.frames) {
        for (const frame of entry.inspection_detail.frames) {
          bees += frame.bee_eighths
          food += frame.food_eighths
        }
      }
      
      // Bees mass in Dadant/Zander scales: frames sum * eighths * 1000 * frame type multiplier
      totalBees += (bees / 8) * 1000 * beeFactor
      totalFood += (food / 8) * foodFactor
    }

    // 2. Check Varroa warning threshold
    if (entry.entry_type === 'VARROA_COUNT' && entry.varroa_count_detail) {
      const detail = entry.varroa_count_detail
      const threshold = detail.season === 'AUTUMN' ? 10.0 : 5.0
      
      // If daily estimated fall exceeds limit and we haven't warned for this hive yet
      if (detail.estimated_total >= threshold && !varroaWarnings.value.some(w => w.hive_id === entry.hive_id)) {
        varroaWarnings.value.push({
          hive_id: entry.hive_id,
          hive_name: entry.hive?.name || 'Unbekanntes Volk',
          raw_count: detail.raw_count,
          estimated_total: detail.estimated_total,
          season: detail.season,
          date: entry.date
        })
      }
    }
  }

  estimatedTotalBees.value = totalBees
  estimatedTotalFood.value = totalFood
}

function generateIntelligentTasks(entries, dbTasks = []) {
  const generated = []
  
  // 1. General database tasks
  dbTasks.forEach(t => {
    let subtitle = t.description || 'Fällige Aufgabe'
    if (t.location || t.hive) {
      const parts = []
      if (t.location) parts.push(`Standort: ${t.location.name}`)
      if (t.hive) parts.push(`Volk: ${t.hive.name}`)
      subtitle = `${parts.join(', ')} — ${subtitle}`
    }
    if (t.due_date) {
      subtitle = `Fällig: ${formatDate(t.due_date)} | ${subtitle}`
    }
    
    generated.push({
      id: t.id,
      title: t.title,
      subtitle: subtitle,
      urgent: t.priority === 'HIGH' || (t.due_date && isOverdue(t.due_date)),
      completed: false,
      isDbTask: true
    })
  })

  tasks.value = generated
}

function buildDueScheduleOverview(dbTasks, customEvents) {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const todayStr = toLocalDateString(today)

  const horizon = new Date(today)
  horizon.setDate(horizon.getDate() + 14)

  const output = []

  dbTasks
    .filter(task => !task.is_completed && task.due_date)
    .forEach(task => {
      const due = new Date(`${task.due_date}T12:00:00`)
      if (Number.isNaN(due.getTime())) return
      if (due > horizon && task.due_date >= todayStr) return

      const status = classifyDueStatus(task.due_date, todayStr)
      output.push({
        id: `task-${task.id}`,
        kind: 'task',
        title: task.title,
        subtitle: `Fällig am ${formatDate(task.due_date)}`,
        sortDate: task.due_date,
        status,
        statusLabel: status === 'overdue' ? 'überfällig' : status === 'today' ? 'heute' : 'anstehend'
      })
    })

  customEvents.forEach(event => {
    const end = event.end_date || event.start_date
    const isFutureRelevant = event.start_date <= toLocalDateString(horizon) && end >= todayStr
    const isOverdue = end < todayStr
    if (!isFutureRelevant && !isOverdue) return

    const dueDate = event.start_date >= todayStr ? event.start_date : end
    const status = classifyDueStatus(dueDate, todayStr)

    output.push({
      id: `custom-${event.id}`,
      kind: 'custom',
      title: event.title,
      subtitle: `Zeitraum ${formatDate(event.start_date)}${end !== event.start_date ? ` - ${formatDate(end)}` : ''}`,
      sortDate: dueDate,
      status,
      statusLabel: status === 'overdue' ? 'abgelaufen' : status === 'today' ? 'heute' : 'anstehend'
    })
  })

  return output
    .sort((a, b) => a.sortDate.localeCompare(b.sortDate))
    .slice(0, 8)
}

async function completeTask(id) {
  const task = tasks.value.find(t => t.id === id)
  if (task && task.isDbTask) {
    try {
      await axios.post(`/api/tasks/${id}/complete`)
    } catch (err) {
      errorStore.showError('Fehler beim Abschließen der Aufgabe.', err, 'Aufgabe')
      return
    }
  }
  tasks.value = tasks.value.filter(t => t.id !== id)
}

async function addManualTask() {
  if (!newTaskTitle.value.trim()) return
  try {
    const res = await axios.post('/api/tasks', {
      title: newTaskTitle.value.trim(),
      priority: 'MEDIUM'
    }, {
      params: { apiary_id: apiaryStore.activeApiaryId }
    })
    
    const t = res.data
    tasks.value.unshift({
      id: t.id,
      title: t.title,
      subtitle: 'Fällige Aufgabe',
      urgent: false,
      completed: false,
      isDbTask: true
    })
    newTaskTitle.value = ''
  } catch (err) {
    errorStore.showError('Fehler beim Hinzufügen der Aufgabe.', err, 'Aufgabe erstellen')
  }
}

function isOverdue(dateStr) {
  if (!dateStr) return false
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const d = new Date(dateStr)
  d.setHours(0, 0, 0, 0)
  return d < today
}

async function createApiary() {
  if (!newApiaryName.value.trim()) return
  try {
    await apiaryStore.createApiary(newApiaryName.value.trim(), newApiaryNotes.value.trim())
    newApiaryName.value = ''
    newApiaryNotes.value = ''
    window.location.reload()
  } catch (err) {
    errorStore.showError('Fehler beim Erstellen der Imkerei.', err, 'Imkerei anlegen')
  }
}

// Helpers
function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

function formatDateTime(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

function formatNumber(num) {
  return new Intl.NumberFormat('de-DE', { maximumFractionDigits: 0 }).format(num)
}

function toLocalDateString(dateObj) {
  const year = dateObj.getFullYear()
  const month = String(dateObj.getMonth() + 1).padStart(2, '0')
  const day = String(dateObj.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function renderMarkdown(text) {
  if (!text) return ''
  const html = marked(text, { breaks: true })
  return DOMPurify.sanitize(html)
}

function getEntryTypeName(type) {
  switch (type) {
    case 'INSPECTION': return 'Beuteninspektion'
    case 'VARROA_COUNT': return 'Varroazählung'
    case 'VARROA_TREATMENT': return 'Varroabehandlung'
    case 'GENERAL': return 'Allgemeine Notiz'
    default: return type
  }
}

function getEntryIcon(type) {
  switch (type) {
    case 'INSPECTION': return '🔎'
    case 'VARROA_COUNT': return '🕷️'
    case 'VARROA_TREATMENT': return '🧪'
    case 'GENERAL': return '📝'
    default: return '🐝'
  }
}

function getEntryColorClass(type) {
  switch (type) {
    case 'INSPECTION': return 'bg-blue-500/10 text-blue-500 border-blue-500/20'
    case 'VARROA_COUNT': return 'bg-red-500/10 text-red-500 border-red-500/20'
    case 'VARROA_TREATMENT': return 'bg-green-500/10 text-green-500 border-green-500/20'
    case 'GENERAL': return 'bg-gray-500/10 text-gray-500 border-gray-500/20'
    default: return 'bg-primary/10 text-primary border-primary/20'
  }
}
</script>

<style scoped>
@reference "../style.css";

.markdown-content :deep(h3) {
  @apply text-lg font-bold mt-4 mb-2 text-gray-900 dark:text-white;
}
.markdown-content :deep(p) {
  @apply mb-2 leading-relaxed;
}
.markdown-content :deep(ul) {
  @apply list-disc list-inside mb-2 space-y-1;
}
.markdown-content :deep(strong) {
  @apply font-extrabold text-gray-900 dark:text-white;
}

.animate-shake {
  animation: shake 0.3s ease-in-out;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-4px); }
  75% { transform: translateX(4px); }
}
</style>
