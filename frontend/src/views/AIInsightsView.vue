<template>
  <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 ai-insights-container">
    <div class="mb-6">
      <h1 class="text-3xl font-extrabold text-gray-900 dark:text-white tracking-tight flex items-center gap-3">
        <span>🤖</span>
        <span>AI Insights</span>
      </h1>
      <p class="text-gray-500 dark:text-gray-400 mt-2">
        Analysen deiner Imkerei als Blog oder Liste, inklusive Lesestatus und LLM-Anfragebereich.
      </p>
    </div>

    <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-4 md:p-5 shadow-sm mb-6 space-y-4">
      <div class="flex flex-col xl:flex-row xl:items-end gap-4">
        <div class="flex-1 grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-3">
          <div>
            <label class="block text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Ansicht</label>
            <div class="inline-flex w-full rounded-xl p-1 bg-gray-100 dark:bg-dark-bg border border-gray-200 dark:border-gray-700">
              <button
                type="button"
                class="flex-1 px-3 py-1.5 rounded-lg text-xs font-bold transition-colors"
                :class="viewMode === 'blog' ? 'bg-primary text-white' : 'text-gray-600 dark:text-gray-300'"
                @click="viewMode = 'blog'"
              >
                Blog
              </button>
              <button
                type="button"
                class="flex-1 px-3 py-1.5 rounded-lg text-xs font-bold transition-colors"
                :class="viewMode === 'list' ? 'bg-primary text-white' : 'text-gray-600 dark:text-gray-300'"
                @click="viewMode = 'list'"
              >
                Liste
              </button>
            </div>
          </div>

          <div>
            <label class="block text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Gelesen</label>
            <select
              v-model="filters.readStatus"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-primary"
              @change="fetchInsights"
            >
              <option value="unread">Nicht gelesen</option>
              <option value="read">Gelesen</option>
              <option value="all">Alle</option>
            </select>
          </div>

          <div>
            <label class="block text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Von</label>
            <input
              v-model="filters.startDate"
              type="date"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-primary"
              @change="onCustomDateChange"
            />
          </div>

          <div>
            <label class="block text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Bis</label>
            <input
              v-model="filters.endDate"
              type="date"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-primary"
              @change="onCustomDateChange"
            />
          </div>
        </div>

        <div class="flex gap-2 flex-wrap xl:justify-end">
          <button
            v-for="range in quickRanges"
            :key="range.value"
            type="button"
            class="px-3 py-2 rounded-xl text-xs font-bold border transition-colors"
            :class="filters.quickRange === range.value
              ? 'bg-primary text-white border-primary'
              : 'bg-white dark:bg-dark-bg text-gray-700 dark:text-gray-200 border-gray-300 dark:border-gray-700 hover:border-primary'"
            @click="applyQuickRange(range.value)"
          >
            {{ range.label }}
          </button>
        </div>
      </div>

      <div class="flex flex-wrap gap-2 justify-between items-center">
        <button
          type="button"
          class="text-xs text-primary hover:underline font-bold"
          @click="resetToDefaultFilters"
        >
          Auf Standard zurücksetzen (7 Tage, nicht gelesen)
        </button>

        <button
          @click="triggerManualInsight"
          :disabled="generating"
          class="px-4 py-2 bg-gray-100 hover:bg-gray-200 dark:bg-dark-bg dark:hover:bg-gray-700 text-gray-800 dark:text-white text-sm font-bold rounded-xl shadow-sm transition-all flex items-center justify-center gap-2"
        >
          <span v-if="generating" class="flex gap-2 items-center">
            <svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
            Generiere...
          </span>
          <span v-else>Analyse manuell erzeugen</span>
        </button>
      </div>
    </div>

    <div v-if="loading" class="flex flex-col items-center justify-center py-20">
      <svg class="animate-spin h-10 w-10 text-primary mb-4" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
      <p class="text-gray-500 dark:text-gray-400 font-bold">Lade Insights...</p>
    </div>

    <div v-else-if="insights.length === 0" class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-8 text-center shadow-sm mb-8">
      <span class="text-4xl mb-4 block">📝</span>
      <h3 class="text-xl font-bold text-gray-900 dark:text-white">Keine Insights für den aktuellen Filter</h3>
      <p class="text-gray-500 dark:text-gray-400 mt-2 max-w-md mx-auto">
        Passe Zeitraum oder Lesestatus an, oder starte eine manuelle Analyse.
      </p>
    </div>

    <div v-else class="space-y-4 mb-8">
      <template v-if="viewMode === 'blog'">
        <article
          v-for="(insight, index) in insights"
          :key="insight.id"
          class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-4 md:p-6 shadow-sm transition-all relative overflow-hidden"
        >
          <div v-if="index === 0" class="absolute top-0 right-0 bg-amber-500 text-white text-[10px] font-black uppercase px-4 py-1.5 rounded-bl-xl shadow-sm z-10">
            Neueste Analyse
          </div>

          <div :class="['mb-3 flex items-start gap-3', index === 0 ? 'mt-4' : '']">
            <div class="flex-1">
              <div class="flex items-center gap-2 mb-1">
                <p class="text-xs font-bold text-gray-400 uppercase tracking-widest">{{ formatDate(insight.created_at) }}</p>
                <span
                  class="px-2 py-0.5 rounded-full text-[10px] font-black uppercase"
                  :class="insight.is_read
                    ? 'bg-emerald-500/15 text-emerald-700 dark:text-emerald-300'
                    : 'bg-amber-500/15 text-amber-700 dark:text-amber-300'"
                >
                  {{ insight.is_read ? 'Gelesen' : 'Neu' }}
                </span>
              </div>
              <h2 class="text-lg md:text-2xl font-extrabold text-gray-900 dark:text-white line-clamp-2">{{ insight.title }}</h2>
            </div>
            <div class="flex gap-1">
              <button
                @click.stop="toggleReadStatus(insight, !insight.is_read)"
                class="px-2.5 py-1.5 text-[10px] font-bold rounded-lg border transition-colors"
                :class="insight.is_read
                  ? 'border-gray-300 dark:border-gray-700 text-gray-600 dark:text-gray-300 hover:border-primary'
                  : 'border-emerald-400/40 text-emerald-700 dark:text-emerald-300 hover:bg-emerald-500/10'"
                :title="insight.is_read ? 'Als ungelesen markieren' : 'Als gelesen markieren'"
              >
                {{ insight.is_read ? 'Ungelesen' : 'Gelesen' }}
              </button>
              <button
                @click.stop="deleteInsight(insight)"
                class="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-500/10 rounded-xl transition-all"
                title="Insight löschen"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
              </button>
            </div>
          </div>

          <div
            class="prose dark:prose-invert max-w-none text-gray-700 dark:text-gray-300 markdown-content transition-all duration-200"
            :class="expandedId === insight.id ? '' : 'line-clamp-6 max-h-40 overflow-hidden'"
            v-html="renderMarkdown(insight.content)"
            @click="toggleExpand(insight.id)"
          ></div>
        </article>
      </template>

      <template v-else>
        <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl shadow-sm overflow-hidden">
          <div
            v-for="insight in insights"
            :key="insight.id"
            class="px-4 md:px-5 py-3 border-b last:border-b-0 border-gray-100 dark:border-gray-800 hover:bg-gray-50/80 dark:hover:bg-dark-bg/40 transition-colors"
          >
            <div class="flex flex-col md:flex-row md:items-center gap-3">
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 mb-1">
                  <span class="text-[11px] font-bold text-gray-400">{{ formatDate(insight.created_at) }}</span>
                  <span
                    class="px-2 py-0.5 rounded-full text-[10px] font-black uppercase"
                    :class="insight.is_read
                      ? 'bg-emerald-500/15 text-emerald-700 dark:text-emerald-300'
                      : 'bg-amber-500/15 text-amber-700 dark:text-amber-300'"
                  >
                    {{ insight.is_read ? 'Gelesen' : 'Neu' }}
                  </span>
                </div>
                <h3 class="text-sm md:text-base font-extrabold text-gray-900 dark:text-white truncate">{{ insight.title }}</h3>
                <p class="text-xs text-gray-500 dark:text-gray-400 mt-1 line-clamp-2">{{ stripMarkdown(insight.content) }}</p>
              </div>

              <div class="flex items-center gap-2 shrink-0">
                <button
                  type="button"
                  class="px-2.5 py-1.5 text-[10px] font-bold rounded-lg border border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-200 hover:border-primary"
                  @click="openInsightModal(insight)"
                >
                  Öffnen
                </button>
                <button
                  type="button"
                  class="px-2.5 py-1.5 text-[10px] font-bold rounded-lg border transition-colors"
                  :class="insight.is_read
                    ? 'border-gray-300 dark:border-gray-700 text-gray-600 dark:text-gray-300 hover:border-primary'
                    : 'border-emerald-400/40 text-emerald-700 dark:text-emerald-300 hover:bg-emerald-500/10'"
                  @click="toggleReadStatus(insight, !insight.is_read)"
                >
                  {{ insight.is_read ? 'Ungelesen' : 'Gelesen' }}
                </button>
                <button
                  type="button"
                  class="px-2.5 py-1.5 text-[10px] font-bold rounded-lg border border-red-300 dark:border-red-900/60 text-red-600 dark:text-red-300 hover:bg-red-500/10"
                  @click="deleteInsight(insight)"
                >
                  Löschen
                </button>
              </div>
            </div>
          </div>
        </div>
      </template>
    </div>

    <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-5 shadow-sm">
      <h3 class="text-base font-bold text-gray-900 dark:text-white mb-1">LLM Anfrage</h3>
      <p class="text-xs text-gray-500 dark:text-gray-400 mb-3">
        Stelle eine freie Frage an den Imkerei-Assistenten. Das Ergebnis wird in einem Dialog angezeigt und kann optional als Insight gespeichert werden.
      </p>
      <textarea
        v-model="chatPrompt"
        rows="4"
        placeholder="z.B. Welche Maßnahmen empfiehlst du für die nächsten 7 Tage bei wechselhaftem Wetter?"
        class="w-full px-4 py-3 rounded-2xl border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-primary"
      ></textarea>
      <div class="mt-3 flex justify-end">
        <button
          type="button"
          :disabled="chatLoading || !chatPrompt.trim()"
          @click="runChatQuery"
          class="px-5 py-2.5 bg-primary hover:bg-primary-hover disabled:opacity-60 text-white text-sm font-bold rounded-xl transition-colors flex items-center gap-2"
        >
          <svg v-if="chatLoading" class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
          <span>{{ chatLoading ? 'Frage läuft...' : 'Anfrage senden' }}</span>
        </button>
      </div>
    </div>

    <div v-if="showInsightModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
      <div class="w-full max-w-4xl max-h-[90vh] overflow-hidden rounded-3xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-dark-card shadow-2xl">
        <div class="px-5 py-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between gap-3">
          <div>
            <h3 class="text-lg font-extrabold text-gray-900 dark:text-white">{{ modalTitle }}</h3>
            <p v-if="modalDate" class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">{{ modalDate }}</p>
          </div>
          <button type="button" class="p-2 rounded-xl hover:bg-gray-100 dark:hover:bg-dark-bg" @click="closeInsightModal">
            <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>

        <div class="p-5 overflow-y-auto max-h-[52vh]">
          <div class="prose dark:prose-invert max-w-none markdown-content" v-html="renderMarkdown(modalContent)"></div>
        </div>

        <div v-if="modalSource === 'chat'" class="px-5 pb-5 space-y-3 border-t border-gray-200 dark:border-gray-700 pt-4">
          <div>
            <label class="block text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Titel für optionales Speichern</label>
            <input
              v-model="chatSaveTitle"
              type="text"
              class="w-full px-3 py-2 rounded-xl border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
          <div class="flex justify-end gap-2">
            <button
              type="button"
              class="px-4 py-2 text-sm font-bold rounded-xl border border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-200 hover:border-primary"
              @click="closeInsightModal"
            >
              Schließen
            </button>
            <button
              type="button"
              :disabled="savingChatInsight || !chatSaveTitle.trim()"
              class="px-4 py-2 text-sm font-bold rounded-xl bg-primary hover:bg-primary-hover text-white disabled:opacity-60"
              @click="saveChatAsInsight"
            >
              {{ savingChatInsight ? 'Speichere...' : 'Als Insight speichern' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
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
const viewMode = ref('blog')

const filters = ref({
  quickRange: '7d',
  readStatus: 'unread',
  startDate: '',
  endDate: ''
})

const expandedId = ref(null)
const quickRanges = [
  { value: '7d', label: '7 Tage' },
  { value: '14d', label: '14 Tage' },
  { value: 'month', label: 'Monat' },
  { value: 'quarter', label: 'Quartal' },
  { value: 'year', label: 'Jahr' }
]

const chatPrompt = ref('')
const chatLoading = ref(false)
const savingChatInsight = ref(false)

const showInsightModal = ref(false)
const modalTitle = ref('')
const modalDate = ref('')
const modalContent = ref('')
const modalSource = ref('insight')
const chatSaveTitle = ref('')

function notifyInsightsUpdated() {
  window.dispatchEvent(new Event('ai-insights-updated'))
}

watch(() => apiaryStore.activeApiaryId, async (newApiaryId) => {
  if (!newApiaryId) return
  await fetchInsights()
})

function toDateInputValue(dateObj) {
  const year = dateObj.getFullYear()
  const month = String(dateObj.getMonth() + 1).padStart(2, '0')
  const day = String(dateObj.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function applyQuickRange(range) {
  const now = new Date()
  const start = new Date(now)

  if (range === '7d') start.setDate(now.getDate() - 7)
  if (range === '14d') start.setDate(now.getDate() - 14)
  if (range === 'month') start.setMonth(now.getMonth() - 1)
  if (range === 'quarter') start.setMonth(now.getMonth() - 3)
  if (range === 'year') start.setFullYear(now.getFullYear() - 1)

  filters.value.quickRange = range
  filters.value.startDate = toDateInputValue(start)
  filters.value.endDate = toDateInputValue(now)
  if (apiaryStore.activeApiaryId) {
    fetchInsights()
  }
}

function onCustomDateChange() {
  filters.value.quickRange = 'custom'
  if (apiaryStore.activeApiaryId) {
    fetchInsights()
  }
}

function resetToDefaultFilters() {
  filters.value.readStatus = 'unread'
  applyQuickRange('7d')
}

onMounted(async () => {
  resetToDefaultFilters()
})

async function fetchInsights() {
  if (!apiaryStore.activeApiaryId) {
    insights.value = []
    loading.value = false
    return
  }

  loading.value = true
  try {
    const params = {
      apiary_id: apiaryStore.activeApiaryId,
      read_status: filters.value.readStatus
    }
    if (filters.value.startDate) {
      params.start_date = filters.value.startDate
    }
    if (filters.value.endDate) {
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

function toggleExpand(id) {
  expandedId.value = expandedId.value === id ? null : id
}

function openInsightModal(insight) {
  modalTitle.value = insight.title
  modalDate.value = formatDate(insight.created_at)
  modalContent.value = insight.content
  modalSource.value = 'insight'
  showInsightModal.value = true
}

function closeInsightModal() {
  showInsightModal.value = false
  modalDate.value = ''
  modalContent.value = ''
  modalSource.value = 'insight'
}

async function toggleReadStatus(insight, nextReadState) {
  try {
    const res = await axios.patch(`/api/ai-insights/${insight.id}/read`, { is_read: nextReadState })
    const idx = insights.value.findIndex(i => i.id === insight.id)
    if (idx >= 0) {
      insights.value[idx] = res.data
    }
    if (filters.value.readStatus === 'read' && !nextReadState) {
      insights.value = insights.value.filter(i => i.id !== insight.id)
    }
    if (filters.value.readStatus === 'unread' && nextReadState) {
      insights.value = insights.value.filter(i => i.id !== insight.id)
    }
    notifyInsightsUpdated()
  } catch (err) {
    errorStore.showError('Lesestatus konnte nicht aktualisiert werden.', err)
  }
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
    notifyInsightsUpdated()
  } catch (err) {
    errorStore.showError('Fehler beim Löschen des Insights.', err)
  }
}

async function runChatQuery() {
  if (!chatPrompt.value.trim()) return
  chatLoading.value = true
  try {
    const res = await axios.post('/api/ai/chat', {
      query: chatPrompt.value.trim()
    }, {
      params: { apiary_id: apiaryStore.activeApiaryId }
    })

    modalTitle.value = 'LLM Antwort'
    modalDate.value = formatDate(new Date().toISOString())
    modalContent.value = res.data.response || ''
    modalSource.value = 'chat'
    chatSaveTitle.value = `LLM Anfrage ${new Date().toLocaleDateString('de-DE')}`
    showInsightModal.value = true
  } catch (err) {
    errorStore.showError('LLM Anfrage fehlgeschlagen.', err)
  } finally {
    chatLoading.value = false
  }
}

async function saveChatAsInsight() {
  if (!chatSaveTitle.value.trim() || !modalContent.value.trim()) return
  savingChatInsight.value = true
  try {
    await axios.post('/api/ai-insights', {
      apiary_id: apiaryStore.activeApiaryId,
      title: chatSaveTitle.value.trim(),
      content: modalContent.value
    })
    await fetchInsights()
    notifyInsightsUpdated()
    closeInsightModal()
  } catch (err) {
    errorStore.showError('Chat-Antwort konnte nicht als Insight gespeichert werden.', err)
  } finally {
    savingChatInsight.value = false
  }
}

async function triggerManualInsight() {
  generating.value = true
  try {
    await axios.post('/api/ai-insights/trigger', null, { params: { apiary_id: apiaryStore.activeApiaryId } })
    await fetchInsights()
    notifyInsightsUpdated()
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

function stripMarkdown(text) {
  if (!text) return ''
  return text
    .replace(/[#*_`>-]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
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
