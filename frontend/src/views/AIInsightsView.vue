<template>
  <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 ai-insights-container">
    
    <div class="mb-8">
      <h1 class="text-3xl font-extrabold text-gray-900 dark:text-white tracking-tight flex items-center gap-3">
        <span>🤖</span> AI Insights Blog
      </h1>
      <p class="text-gray-500 dark:text-gray-400 mt-2">
        Automatisch generierte, intelligente Analysen deiner Imkerei basierend auf aktuellen Wetterdaten und deinen letzten Inspektionen.
      </p>
    </div>

    <div v-if="loading" class="flex flex-col items-center justify-center py-20">
      <svg class="animate-spin h-10 w-10 text-primary mb-4" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
      <p class="text-gray-500 dark:text-gray-400 font-bold">Lade Insights...</p>
    </div>

    <div v-else-if="insights.length === 0" class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-8 text-center shadow-sm">
      <span class="text-4xl mb-4 block">📝</span>
      <h3 class="text-xl font-bold text-gray-900 dark:text-white">Noch keine Insights vorhanden</h3>
      <p class="text-gray-500 dark:text-gray-400 mt-2 max-w-md mx-auto">
        Die KI hat noch keine Analysen für diese Imkerei durchgeführt. Das System generiert automatisch im Hintergrund neue Beiträge.
      </p>
      <button 
        @click="triggerManualInsight" 
        :disabled="generating"
        class="mt-6 px-6 py-2.5 bg-primary text-white font-bold rounded-xl shadow-md hover-scale hover:bg-primary-hover transition-all flex items-center justify-center gap-2 mx-auto"
      >
        <span v-if="generating">
            <svg class="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
        </span>
        <span v-else>Manuelle Analyse starten</span>
      </button>
    </div>

    <div v-else class="space-y-8">
      <!-- Filter & Actions Row -->
      <div class="flex flex-col md:flex-row md:items-center gap-4 mb-4">
        <!-- Zeitraum Filter -->
        <div class="flex flex-wrap items-end gap-3 flex-1">
          <div>
            <label class="block text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Von Datum</label>
            <input 
              v-model="filters.startDate" 
              type="date" 
              class="px-3 py-2 border border-gray-200 dark:border-gray-800 dark:bg-dark-bg dark:text-white rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
          <div>
            <label class="block text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Bis Datum</label>
            <input 
              v-model="filters.endDate" 
              type="date" 
              class="px-3 py-2 border border-gray-200 dark:border-gray-800 dark:bg-dark-bg dark:text-white rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
          <button 
            @click="resetFilters" 
            class="text-xs text-primary hover:underline font-bold mt-2"
          >
            Filter zurücksetzen
          </button>
        </div>

        <!-- Generate Button -->
        <button 
          @click="triggerManualInsight" 
          :disabled="generating"
          class="px-4 py-2 bg-gray-100 hover:bg-gray-200 dark:bg-dark-card dark:hover:bg-dark-border text-gray-800 dark:text-white text-sm font-bold rounded-xl shadow-sm hover-scale transition-all flex items-center justify-center gap-2"
        >
          <span v-if="generating" class="flex gap-2 items-center">
            <svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
            Generiere...
          </span>
          <span v-else>Aktualisieren (Manuell)</span>
        </button>
      </div>

      <div 
        v-for="(insight, index) in filteredInsights" 
        :key="insight.id"
        :class="[
          'bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-4 md:p-6 shadow-sm transition-all relative overflow-hidden cursor-pointer',
          expandedId === insight.id ? 'md:col-span-2 shadow-md' : 'hover:shadow-md'
        ]"
        @click.stop="toggleExpand(insight.id)"
      >
        <div v-if="index === 0" class="absolute top-0 right-0 bg-amber-500 text-white text-xs font-black uppercase px-4 py-1.5 rounded-bl-xl shadow-sm z-10">
          Neueste Analyse
        </div>

        <div class="mb-3 flex items-start gap-3">
          <div class="flex-1">
            <p class="text-xs font-bold text-gray-400 uppercase tracking-widest mb-1">{{ formatDate(insight.created_at) }}</p>
            <h2 class="text-lg md:text-2xl font-extrabold text-gray-900 dark:text-white line-clamp-2">{{ insight.title }}</h2>
          </div>
          <button 
            @click.stop="deleteInsight(insight)" 
            class="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-500/10 rounded-xl transition-all"
            title="Insight löschen"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
          </button>
        </div>

        <div 
          class="prose dark:prose-invert max-w-none text-gray-700 dark:text-gray-300 markdown-content transition-all duration-200"
          :class="expandedId === insight.id ? '' : 'line-clamp-6 max-h-40 overflow-hidden'
          "
          v-html="renderMarkdown(insight.content)"
        ></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, onBeforeUnmount } from 'vue'
import axios from 'axios'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { useApiaryStore } from '../stores/apiary'
import { useErrorStore } from '../stores/error'
import { useConfirmStore } from '../stores/confirm'

const apiaryStore = useApiaryStore()
const errorStore = useErrorStore()
const confirmStore = useConfirmStore()

const loading = ref(true)
const generating = ref(false)
const insights = ref([])

const filters = ref({
  startDate: '',
  endDate: ''
})

const expandedId = ref(null)

// Close expanded card when clicking outside
function handleClickOutside(event) {
  const container = document.querySelector('.ai-insights-container')
  if (container && !container.contains(event.target)) {
    expandedId.value = null
  }
}

onMounted(async () => {
  document.addEventListener('click', handleClickOutside)
  if (apiaryStore.activeApiaryId) {
    await fetchInsights()
  }
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
})

async function fetchInsights() {
  loading.value = true
  try {
    const params = { apiary_id: apiaryStore.activeApiaryId }
    if (filters.value.startDate) {
      params.start_date = filters.value.startDate
    }
    if (filters.value.endDate) {
      // include full day
      params.end_date = filters.value.endDate + 'T23:59:59'
    }
    const res = await axios.get('/api/ai-insights', { params })
    insights.value = res.data
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

const filteredInsights = computed(() => insights.value)

function resetFilters() {
  filters.value.startDate = ''
  filters.value.endDate = ''
  fetchInsights()
}

function toggleExpand(id) {
  expandedId.value = expandedId.value === id ? null : id
}

async function deleteInsight(insight) {
  const confirmed = await confirmStore.ask({
    title: 'Insight-Eintrag löschen',
    message: 'Diesen Insight-Eintrag wirklich löschen?',
    type: 'danger',
    confirmText: 'Ja, löschen'
  })
  if (!confirmed) return
  try {
    await axios.delete(`/api/ai-insights/${insight.id}`)
    insights.value = insights.value.filter(i => i.id !== insight.id)
  } catch (err) {
    errorStore.showError('Fehler beim Löschen des Insights.', err)
  }
}

async function triggerManualInsight() {
  generating.value = true
  try {
    await axios.post('/api/ai-insights/trigger', null, { params: { apiary_id: apiaryStore.activeApiaryId } })
    await fetchInsights()
  } catch (err) {
    errorStore.showError('Fehler beim Generieren des Insights.', err)
  } finally {
    generating.value = false
  }
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

function renderMarkdown(text) {
  if (!text) return ''
  let cleaned = text.trim()
  if (cleaned.startsWith('```markdown')) {
    cleaned = cleaned.substring(11).trim()
  } else if (cleaned.startsWith('```')) {
    cleaned = cleaned.substring(3).trim()
  }
  if (cleaned.endsWith('```')) {
    cleaned = cleaned.substring(0, cleaned.length - 3).trim()
  }
  const html = marked.parse(cleaned, { breaks: true })
  return DOMPurify.sanitize(html)
}
</script>

<style>
@reference "../style.css";
.markdown-content h1 {
  @apply text-xl md:text-2xl font-black mt-6 mb-4 text-gray-900 dark:text-white border-b border-gray-100 dark:border-gray-800 pb-2;
}
.markdown-content h2 {
  @apply text-lg md:text-xl font-extrabold mt-6 mb-3 text-gray-900 dark:text-white;
}
.markdown-content h3 {
  @apply text-base md:text-lg font-bold mt-5 mb-2 text-gray-900 dark:text-white;
}
.markdown-content p {
  @apply mb-4 leading-relaxed text-sm md:text-base;
}
.markdown-content ul {
  @apply list-disc pl-5 mb-4 space-y-2 text-sm md:text-base;
}
.markdown-content ol {
  @apply list-decimal pl-5 mb-4 space-y-2 text-sm md:text-base;
}
.markdown-content li {
  @apply pl-1;
}
.markdown-content strong {
  @apply font-black text-gray-900 dark:text-white;
}
</style>
