<template>
  <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    
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
      <div class="flex justify-end mb-4">
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
        v-for="(insight, index) in insights" 
        :key="insight.id"
        class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-6 md:p-8 shadow-sm hover:shadow-md transition-shadow relative overflow-hidden"
      >
        <div v-if="index === 0" class="absolute top-0 right-0 bg-amber-500 text-white text-xs font-black uppercase px-4 py-1.5 rounded-bl-xl shadow-sm z-10">
          Neueste Analyse
        </div>

        <div class="mb-4">
          <p class="text-xs font-bold text-gray-400 uppercase tracking-widest mb-1">{{ formatDate(insight.created_at) }}</p>
          <h2 class="text-2xl font-extrabold text-gray-900 dark:text-white">{{ insight.title }}</h2>
        </div>

        <div class="prose dark:prose-invert max-w-none text-gray-700 dark:text-gray-300 markdown-content" v-html="renderMarkdown(insight.content)"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { useApiaryStore } from '../stores/apiary'
import { useErrorStore } from '../stores/error'

const apiaryStore = useApiaryStore()
const errorStore = useErrorStore()

const loading = ref(true)
const generating = ref(false)
const insights = ref([])

onMounted(async () => {
  if (apiaryStore.activeApiaryId) {
    await fetchInsights()
  }
})

async function fetchInsights() {
  loading.value = true
  try {
    const res = await axios.get('/api/ai-insights', { params: { apiary_id: apiaryStore.activeApiaryId } })
    insights.value = res.data
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
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
  const html = marked(text, { breaks: true })
  return DOMPurify.sanitize(html)
}
</script>

<style>
@reference "../style.css";
.markdown-content h3 {
  @apply text-lg font-bold mt-6 mb-3 text-gray-900 dark:text-white;
}
.markdown-content p {
  @apply mb-4 leading-relaxed;
}
.markdown-content ul {
  @apply list-disc list-inside mb-4 space-y-1;
}
.markdown-content strong {
  @apply font-extrabold text-gray-900 dark:text-white;
}
</style>
