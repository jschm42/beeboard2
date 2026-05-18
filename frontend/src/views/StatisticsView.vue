<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 font-sans">
    
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-extrabold text-gray-900 dark:text-white tracking-tight">📈 Bienenstand-Statistiken</h1>
      <p class="text-gray-500 dark:text-gray-400 mt-1">Verfolge die Entwicklung von Brut, Futter und Bienenmasse im zeitlichen Verlauf.</p>
    </div>

    <!-- Active Apiary Guard -->
    <div v-if="!apiaryStore.activeApiaryId" class="glass rounded-3xl p-12 text-center max-w-lg mx-auto border border-dashed border-gray-300 dark:border-gray-700">
      <div class="text-4xl mb-4">📊</div>
      <h3 class="text-lg font-bold text-gray-800 dark:text-white mb-2">Keine aktive Imkerei</h3>
      <p class="text-gray-500 dark:text-gray-400">Bitte wähle oben eine Imkerei aus, um Statistiken anzuzeigen.</p>
    </div>

    <div v-else class="space-y-8">
      
      <!-- Filter Dock -->
      <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-6 shadow-sm">
        <h3 class="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-4">🔍 Analyse-Filter</h3>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          
          <!-- Location Filter -->
          <div>
            <label class="block text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-1">Standort</label>
            <select 
              v-model="filters.locationId"
              @change="onFilterChange"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-primary cursor-pointer"
            >
              <option value="">Alle Standorte</option>
              <option v-for="loc in locations" :key="loc.id" :value="loc.id">
                {{ loc.name }}
              </option>
            </select>
          </div>

          <!-- Hive Filter -->
          <div>
            <label class="block text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-1">Bienenvolk</label>
            <select 
              v-model="filters.hiveId"
              @change="onFilterChange"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-primary cursor-pointer"
            >
              <option value="">Alle Bienenvölker</option>
              <option v-for="hive in filteredHives" :key="hive.id" :value="hive.id">
                {{ hive.name }}
              </option>
            </select>
          </div>

          <!-- Season Filter -->
          <div>
            <label class="block text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-1">Jahreszeit (Saison)</label>
            <select 
              v-model="filters.season"
              @change="onFilterChange"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-primary cursor-pointer"
            >
              <option value="">Ganzjährig</option>
              <option value="SPRING">Frühling (SPRING)</option>
              <option value="SUMMER">Sommer (SUMMER)</option>
              <option value="AUTUMN">Herbst (AUTUMN)</option>
              <option value="WINTER">Winter (WINTER)</option>
            </select>
          </div>

        </div>
      </div>

      <!-- High-Level Peaks (Dynamic Statistics) -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border p-6 rounded-2xl shadow-sm flex items-center space-x-4">
          <div class="p-3.5 bg-amber-500/10 rounded-xl text-amber-500">
            👑
          </div>
          <div>
            <p class="text-[10px] text-gray-500 dark:text-gray-400 font-bold uppercase tracking-wider">Brutwaben-Peak</p>
            <p class="text-2xl font-extrabold text-gray-900 dark:text-white mt-1">{{ formatNumber(peaks.brood) }} Waben</p>
          </div>
        </div>

        <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border p-6 rounded-2xl shadow-sm flex items-center space-x-4">
          <div class="p-3.5 bg-green-500/10 rounded-xl text-green-500">
            🐝
          </div>
          <div>
            <p class="text-[10px] text-gray-500 dark:text-gray-400 font-bold uppercase tracking-wider">Bienenmasse-Peak</p>
            <p class="text-2xl font-extrabold text-gray-900 dark:text-white mt-1">{{ formatNumber(peaks.bees) }} Waben</p>
          </div>
        </div>

        <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border p-6 rounded-2xl shadow-sm flex items-center space-x-4">
          <div class="p-3.5 bg-yellow-500/10 rounded-xl text-yellow-500">
            🍯
          </div>
          <div>
            <p class="text-[10px] text-gray-500 dark:text-gray-400 font-bold uppercase tracking-wider">Futterwaben-Peak</p>
            <p class="text-2xl font-extrabold text-gray-900 dark:text-white mt-1">{{ formatNumber(peaks.food) }} Waben</p>
          </div>
        </div>

      </div>

      <!-- Chart Display Card -->
      <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-6 shadow-sm">
        
        <div class="flex justify-between items-center mb-6 border-b border-gray-100 dark:border-dark-border pb-4">
          <h2 class="text-base font-extrabold text-gray-900 dark:text-white">⏰ Entwicklungsverlauf der Bienengesundheit</h2>
          <span class="text-[10px] text-gray-400 uppercase font-black tracking-wider bg-gray-50 dark:bg-dark-bg px-2 py-1 rounded">
            Datenpunkte: {{ statsData.labels?.length || 0 }}
          </span>
        </div>

        <!-- Chart loader -->
        <div v-if="loading" class="flex flex-col items-center justify-center py-32">
          <svg class="animate-spin h-10 w-10 text-primary mb-4" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
          <p class="text-gray-500 dark:text-gray-400 font-bold text-sm">Lade Zeitreihendaten...</p>
        </div>

        <!-- No data notification -->
        <div v-else-if="!statsData.labels || statsData.labels.length === 0" class="flex flex-col items-center justify-center py-24 text-center">
          <div class="text-3xl mb-2">📈</div>
          <h4 class="text-sm font-bold text-gray-800 dark:text-white">Keine passenden Inspektionsdaten gefunden</h4>
          <p class="text-xs text-gray-400 max-w-sm mt-1">
            Es müssen zuerst Logbucheinträge vom Typ "Beuteninspektion" mit Wabenbewertungen erfasst werden, um zeitliche Trends anzuzeigen.
          </p>
        </div>

        <!-- Canvas -->
        <div v-show="!loading && statsData.labels && statsData.labels.length > 0" class="relative h-96 w-full">
          <canvas ref="chartCanvas"></canvas>
        </div>

      </div>

    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, reactive, computed, watch, onBeforeUnmount } from 'vue'
import { useApiaryStore } from '../stores/apiary'
import { Chart, registerables } from 'chart.js'
import axios from 'axios'

Chart.register(...registerables)

const apiaryStore = useApiaryStore()

const loading = ref(false)
const locations = ref([])
const hives = ref([])
const statsData = ref({})

const chartCanvas = ref(null)
let chartInstance = null

const filters = reactive({
  locationId: '',
  hiveId: '',
  season: ''
})

const filteredHives = computed(() => {
  if (!filters.locationId) return hives.value
  return hives.value.filter(h => h.location_id === filters.locationId)
})

const peaks = computed(() => {
  const data = statsData.value
  return {
    brood: data.brood?.length > 0 ? Math.max(...data.brood) : 0,
    bees: data.bees?.length > 0 ? Math.max(...data.bees) : 0,
    food: data.food?.length > 0 ? Math.max(...data.food) : 0
  }
})

// Watch active apiary and refetch
watch(() => apiaryStore.activeApiaryId, async (newVal) => {
  if (newVal) {
    filters.locationId = ''
    filters.hiveId = ''
    filters.season = ''
    await Promise.all([
      fetchLocations(),
      fetchHives()
    ])
    await fetchStats()
  }
})

onMounted(async () => {
  if (apiaryStore.activeApiaryId) {
    await Promise.all([
      fetchLocations(),
      fetchHives()
    ])
    await fetchStats()
  }
})

onBeforeUnmount(() => {
  if (chartInstance) {
    chartInstance.destroy()
  }
})

async function fetchLocations() {
  try {
    const res = await axios.get('/api/locations/', {
      params: { apiary_id: apiaryStore.activeApiaryId }
    })
    locations.value = res.data
  } catch (err) {
    console.error('Fetch locations error:', err)
  }
}

async function fetchHives() {
  try {
    const res = await axios.get('/api/hives', {
      params: { apiary_id: apiaryStore.activeApiaryId }
    })
    hives.value = res.data
  } catch (err) {
    console.error('Fetch hives error:', err)
  }
}

async function fetchStats() {
  loading.value = true
  try {
    const params = {
      apiary_id: apiaryStore.activeApiaryId
    }
    if (filters.locationId) params.location_id = filters.locationId
    if (filters.hiveId) params.hive = [filters.hiveId]
    if (filters.season) params.season = filters.season

    const res = await axios.get('/api/stats/aggregation', { params })
    statsData.value = res.data

    renderChart()
  } catch (err) {
    console.error('Fetch stats failed:', err)
  } finally {
    loading.value = false
  }
}

function onFilterChange() {
  // If location changes, reset hive filter if it's no longer matching
  if (filters.locationId && filters.hiveId) {
    const matched = hives.value.find(h => h.id === filters.hiveId)
    if (matched && matched.location_id !== filters.locationId) {
      filters.hiveId = ''
    }
  }
  fetchStats()
}

function renderChart() {
  if (!chartCanvas.value) return
  if (chartInstance) {
    chartInstance.destroy()
  }

  const data = statsData.value
  if (!data.labels || data.labels.length === 0) return

  // Format label dates to de-DE locale
  const formattedLabels = data.labels.map(l => {
    const d = new Date(l)
    return d.toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit' })
  })

  // Detect dark mode setting in window/HTML
  const isDark = document.documentElement.classList.contains('dark')
  const textColor = isDark ? '#9CA3AF' : '#4B5563'
  const gridColor = isDark ? 'rgba(75, 85, 99, 0.15)' : 'rgba(229, 231, 235, 0.5)'

  chartInstance = new Chart(chartCanvas.value, {
    type: 'line',
    data: {
      labels: formattedLabels,
      datasets: [
        {
          label: 'Brutraum (Waben)',
          data: data.brood,
          borderColor: '#D97706', // Warm Amber
          backgroundColor: 'rgba(217, 119, 6, 0.1)',
          fill: true,
          tension: 0.35,
          borderWidth: 3.5,
          pointRadius: 4.5,
          pointHoverRadius: 7
        },
        {
          label: 'Bienen (Waben)',
          data: data.bees,
          borderColor: '#10B981', // Green
          backgroundColor: 'rgba(16, 185, 129, 0.1)',
          fill: true,
          tension: 0.35,
          borderWidth: 3.5,
          pointRadius: 4.5,
          pointHoverRadius: 7
        },
        {
          label: 'Futter (Waben)',
          data: data.food,
          borderColor: '#F59E0B', // Honey Yellow
          backgroundColor: 'rgba(245, 158, 11, 0.05)',
          fill: true,
          tension: 0.35,
          borderWidth: 3.5,
          pointRadius: 4.5,
          pointHoverRadius: 7
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: {
            color: textColor,
            font: {
              family: 'Outfit, sans-serif',
              size: 11,
              weight: 'bold'
            }
          }
        },
        tooltip: {
          backgroundColor: isDark ? '#1F2937' : '#FFFFFF',
          titleColor: isDark ? '#FFFFFF' : '#1F2937',
          bodyColor: isDark ? '#E5E7EB' : '#4B5563',
          borderWidth: 1,
          borderColor: isDark ? '#374151' : '#E5E7EB',
          padding: 12,
          boxPadding: 4,
          usePointStyle: true,
          titleFont: { weight: 'bold' }
        }
      },
      scales: {
        x: {
          grid: { color: gridColor },
          ticks: { color: textColor, font: { weight: 'semibold', size: 10 } }
        },
        y: {
          grid: { color: gridColor },
          ticks: { color: textColor, font: { weight: 'semibold', size: 10 } },
          min: 0
        }
      }
    }
  })
}

// Helper
function formatNumber(num) {
  return num.toFixed(1)
}
</script>
