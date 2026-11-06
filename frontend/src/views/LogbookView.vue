<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 font-sans">

    <PageHeader icon="📓" :title="$t('logbook.title')" :subtitle="$t('logbook.subtitle')">
      <template v-if="apiaryStore.activeApiaryId" #actions>
        <div class="inline-flex rounded-xl p-1 bg-gray-100 dark:bg-dark-card border border-gray-200 dark:border-dark-border" role="tablist">
          <button
            v-for="mode in VIEW_MODES"
            :key="mode.value"
            type="button"
            role="tab"
            :aria-selected="viewMode === mode.value"
            class="px-3 py-1.5 rounded-lg text-sm font-semibold transition-colors flex items-center gap-1.5"
            :class="viewMode === mode.value ? 'bg-white dark:bg-dark-bg text-primary shadow-sm' : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'"
            @click="viewMode = mode.value"
          >
            <component :is="mode.icon" class="w-4 h-4" />
            {{ $t(mode.label) }}
          </button>
        </div>
        <button
          type="button"
          class="px-4 py-2 bg-primary hover:bg-primary-hover text-white font-bold text-sm rounded-xl shadow-md shadow-primary/20 flex items-center gap-1.5"
          @click="sessionModalRef?.open()"
        >
          <Plus class="w-4 h-4" />
          {{ $t('logbook.new_session_short') }}
        </button>
      </template>
    </PageHeader>

    <!-- No active apiary -->
    <div v-if="!apiaryStore.activeApiaryId" class="glass rounded-3xl p-12 text-center max-w-lg mx-auto border border-dashed border-gray-300 dark:border-gray-700">
      <div class="text-4xl mb-4">📓</div>
      <h3 class="text-lg font-bold text-gray-800 dark:text-white mb-2">{{ $t('logbook.no_active_apiary') }}</h3>
      <p class="text-gray-500 dark:text-gray-400">{{ $t('logbook.select_apiary_desc') }}</p>
    </div>

    <template v-else>
      <!-- ============ VIEW 1: LOGBOOKS ============ -->
      <div v-if="viewMode === 'tiles'">

        <!-- 1.1 Logbook overview -->
        <div v-if="!selectedSession">
          <div v-if="sessionsLoading" class="flex justify-center py-20">
            <Loader2 class="w-6 h-6 text-primary animate-spin" />
          </div>

          <div v-else-if="sessions.length === 0" class="bg-white dark:bg-dark-card border border-dashed border-gray-300 dark:border-dark-border rounded-3xl p-12 text-center">
            <div class="text-4xl mb-3">📓</div>
            <p class="text-gray-500 dark:text-gray-400 text-sm mb-4">{{ $t('logbook.no_sessions_yet') }}</p>
            <button type="button" class="px-4 py-2 bg-primary hover:bg-primary-hover text-white font-bold text-sm rounded-xl" @click="sessionModalRef?.open()">
              {{ $t('logbook.new_session_short') }}
            </button>
          </div>

          <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <div
              v-for="session in sessions"
              :key="session.id"
              role="button"
              tabindex="0"
              class="group bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-2xl p-5 shadow-sm hover:shadow-md hover:border-primary/50 cursor-pointer transition-all flex flex-col gap-3 focus:outline-none focus:ring-2 focus:ring-primary"
              @click="selectSession(session)"
              @keydown.enter="selectSession(session)"
            >
              <div class="flex justify-between items-start gap-2">
                <h3 class="font-bold text-base text-gray-900 dark:text-white line-clamp-2">{{ session.title }}</h3>
                <div class="flex items-center gap-0.5 flex-shrink-0 sm:opacity-0 sm:group-hover:opacity-100 sm:group-focus-within:opacity-100 transition-opacity">
                  <button
                    type="button"
                    class="p-1.5 text-gray-400 hover:text-primary hover:bg-primary/10 rounded-lg"
                    :title="$t('logbook.rename_session')"
                    :aria-label="$t('logbook.rename_session')"
                    @click.stop="sessionModalRef?.open(session)"
                  >
                    <Pencil class="w-4 h-4" />
                  </button>
                  <button
                    type="button"
                    class="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-500/10 rounded-lg"
                    :title="$t('logbook.delete_session')"
                    :aria-label="$t('logbook.delete_session')"
                    @click.stop="deleteSession(session)"
                  >
                    <Trash2 class="w-4 h-4" />
                  </button>
                </div>
              </div>
              <span class="self-start max-w-full truncate px-2 py-0.5 rounded-md text-xs font-semibold" :class="scopeInfo(session).chipClass">
                {{ scopeInfo(session).icon }} {{ scopeInfo(session).text }}
              </span>
              <p class="text-xs text-gray-400 mt-auto">{{ $t('logbook.last_active', { time: formatDateTime(session.updated_at) }) }}</p>
            </div>
          </div>
        </div>

        <!-- 1.2 Selected logbook workspace -->
        <div v-else class="space-y-4">
          <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-2xl p-4 sm:p-5 shadow-sm flex flex-col sm:flex-row sm:items-center gap-4">
            <button
              type="button"
              class="self-start sm:self-center p-2 rounded-xl text-gray-500 hover:text-primary hover:bg-gray-100 dark:hover:bg-dark-bg transition-colors"
              :title="$t('logbook.back_to_tiles')"
              :aria-label="$t('logbook.back_to_tiles')"
              @click="closeSession"
            >
              <ArrowLeft class="w-5 h-5" />
            </button>
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2">
                <h2 class="text-xl font-bold text-gray-900 dark:text-white truncate">{{ selectedSession.title }}</h2>
                <button
                  type="button"
                  class="p-1 text-gray-400 hover:text-primary rounded-lg hover:bg-gray-100 dark:hover:bg-dark-bg"
                  :title="$t('logbook.rename_session')"
                  :aria-label="$t('logbook.rename_session')"
                  @click="sessionModalRef?.open(selectedSession)"
                >
                  <Pencil class="w-4 h-4" />
                </button>
              </div>
              <p class="text-sm text-gray-500 dark:text-gray-400 mt-0.5 truncate">
                {{ scopeInfo(selectedSession).icon }} {{ scopeInfo(selectedSession).text }}
                · {{ $t('logbook.entry_count', { count: entries.length }, entries.length) }}
              </p>
            </div>
            <button
              type="button"
              class="px-4 py-2 bg-primary hover:bg-primary-hover text-white font-bold text-sm rounded-xl shadow-md flex items-center justify-center gap-1.5"
              @click="openCreateEntryModal"
            >
              <Plus class="w-4 h-4" />
              {{ $t('logbook.new_entry_short') }}
            </button>
          </div>

          <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
            <!-- Entries timeline -->
            <div class="lg:col-span-8 space-y-6">
              <div v-if="entriesLoading" class="flex justify-center py-20">
                <Loader2 class="w-6 h-6 text-primary animate-spin" />
              </div>

              <div v-else-if="entries.length === 0" class="bg-white dark:bg-dark-card border border-dashed border-gray-300 dark:border-dark-border rounded-2xl p-10 text-center text-gray-500 dark:text-gray-400 text-sm">
                {{ $t('logbook.no_entries_yet') }}
              </div>

              <template v-else>
                <section v-for="group in entriesByDate" :key="group.date" class="space-y-3">
                  <h3 class="text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400 flex items-center gap-3">
                    {{ formatGroupDate(group.date) }}
                    <span class="flex-1 h-px bg-gray-200 dark:bg-dark-border" />
                  </h3>
                  <LogbookEntryCard
                    v-for="entry in group.entries"
                    :key="entry.id"
                    :entry="entry"
                    @edit="openEditEntryModal"
                    @delete="deleteEntry"
                    @upload-image="uploadEntryImage"
                    @delete-image="deleteEntryImage"
                    @open-image="lightboxImage = $event"
                  />
                </section>
              </template>
            </div>

            <!-- AI assistant -->
            <aside class="lg:col-span-4 h-[520px] lg:h-[calc(100vh-4rem)] lg:max-h-[720px] bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-2xl overflow-hidden shadow-sm lg:sticky lg:top-6">
              <AIChatPane @apply-draft="onApplyDraft" />
            </aside>
          </div>
        </div>
      </div>

      <!-- ============ VIEW 2: ALL ENTRIES TABLE ============ -->
      <div v-else class="space-y-4">
        <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-2xl p-4 shadow-sm">
          <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
            <label class="block">
              <span class="block text-xs font-semibold text-gray-500 dark:text-gray-400 mb-1">{{ $t('logbook.filter_from_date') }}</span>
              <input v-model="tableFilters.startDate" type="date" :class="filterInputClass" />
            </label>
            <label class="block">
              <span class="block text-xs font-semibold text-gray-500 dark:text-gray-400 mb-1">{{ $t('logbook.filter_to_date') }}</span>
              <input v-model="tableFilters.endDate" type="date" :class="filterInputClass" />
            </label>
            <label class="block">
              <span class="block text-xs font-semibold text-gray-500 dark:text-gray-400 mb-1">{{ $t('logbook.table_type') }}</span>
              <select v-model="tableFilters.entryType" :class="filterInputClass">
                <option value="">{{ $t('logbook.filter_all_types') }}</option>
                <option v-for="type in ENTRY_TYPES" :key="type" :value="type">{{ entryTypeLabel({ entry_type: type }, t) }}</option>
              </select>
            </label>
            <label v-if="apiaryStore.apiaries.length > 1" class="block">
              <span class="block text-xs font-semibold text-gray-500 dark:text-gray-400 mb-1">{{ $t('sidebar.active_apiary') }}</span>
              <select v-model="tableFilters.apiaryId" :class="filterInputClass">
                <option value="">{{ $t('logbook.filter_all_apiaries') }}</option>
                <option v-for="a in apiaryStore.apiaries" :key="a.id" :value="a.id">{{ a.name }}</option>
              </select>
            </label>
            <label class="block">
              <span class="block text-xs font-semibold text-gray-500 dark:text-gray-400 mb-1">{{ $t('hives.location_label') }}</span>
              <select v-model="tableFilters.locationId" :class="filterInputClass">
                <option value="">{{ $t('logbook.filter_all_locations') }}</option>
                <option v-for="loc in uniqueLocations" :key="loc.id" :value="loc.id">{{ loc.name }}</option>
              </select>
            </label>
            <label class="block">
              <span class="block text-xs font-semibold text-gray-500 dark:text-gray-400 mb-1">{{ $t('hives.table_hive') }}</span>
              <select v-model="tableFilters.hiveId" :class="filterInputClass">
                <option value="">{{ $t('logbook.filter_all_hives') }}</option>
                <option v-for="h in uniqueHives" :key="h.id" :value="h.id">{{ h.name }}</option>
              </select>
            </label>
            <label class="block">
              <span class="block text-xs font-semibold text-gray-500 dark:text-gray-400 mb-1">{{ $t('logbook.table_creator') }}</span>
              <select v-model="tableFilters.userId" :class="filterInputClass">
                <option value="">{{ $t('logbook.filter_all_creators') }}</option>
                <option v-for="u in uniqueCreators" :key="u.id" :value="u.id">{{ u.name }}</option>
              </select>
            </label>
          </div>
          <div class="flex justify-between items-center mt-3 text-xs text-gray-500 dark:text-gray-400">
            <span>{{ $t('logbook.filtered_count', { shown: filteredEntries.length, total: allEntries.length }) }}</span>
            <button v-if="hasActiveFilters" type="button" class="text-primary hover:underline font-semibold" @click="resetTableFilters">
              {{ $t('hives.reset_filters') }}
            </button>
          </div>
        </div>

        <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-2xl overflow-hidden shadow-sm">
          <div v-if="loadingAllEntries" class="flex flex-col items-center justify-center py-20">
            <Loader2 class="w-6 h-6 text-primary animate-spin mb-3" />
            <span class="text-xs text-gray-400">{{ $t('logbook.loading_entries') }}</span>
          </div>

          <div v-else-if="filteredEntries.length === 0" class="p-12 text-center text-gray-500 dark:text-gray-400 text-sm">
            {{ $t('logbook.no_filtered_entries') }}
          </div>

          <div v-else class="overflow-x-auto">
            <table class="w-full text-left text-sm">
              <thead>
                <tr class="bg-gray-50 dark:bg-dark-bg text-gray-500 dark:text-gray-400 text-xs font-semibold border-b border-gray-100 dark:border-dark-border">
                  <th class="px-4 py-3">{{ $t('logbook.table_date') }}</th>
                  <th class="px-4 py-3">{{ $t('logbook.table_hive') }}</th>
                  <th class="px-4 py-3">{{ $t('logbook.table_type') }}</th>
                  <th class="px-4 py-3 min-w-[16rem]">{{ $t('logbook.table_notes') }}</th>
                  <th class="px-4 py-3">{{ $t('logbook.table_creator') }}</th>
                  <th class="px-4 py-3 text-center">{{ $t('logbook.table_images') }}</th>
                  <th class="px-4 py-3"><span class="sr-only">{{ $t('logbook.table_actions') }}</span></th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-100 dark:divide-dark-border">
                <tr v-for="entry in filteredEntries" :key="entry.id" class="hover:bg-gray-50/60 dark:hover:bg-dark-bg/30 align-top">
                  <td class="px-4 py-3 font-semibold text-gray-800 dark:text-gray-200 whitespace-nowrap">{{ formatDate(entry.date) }}</td>
                  <td class="px-4 py-3">
                    <div class="font-semibold text-primary">{{ entry.hive?.name || '–' }}</div>
                    <div class="text-xs text-gray-400">{{ [entry.apiary?.name, entry.hive?.location?.name].filter(Boolean).join(' · ') }}</div>
                  </td>
                  <td class="px-4 py-3 whitespace-nowrap">
                    <span class="text-gray-700 dark:text-gray-300">{{ entryTypeLabel(entry, t) }}</span>
                    <span v-if="entry.created_via_mcp" class="ml-1 px-1.5 py-0.5 text-[11px] font-semibold rounded bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400" :title="$t('logbook.mcp_badge_title')">🤖 MCP</span>
                  </td>
                  <td class="px-4 py-3 space-y-2">
                    <p v-if="entry.notes" class="text-gray-700 dark:text-gray-300 line-clamp-3 whitespace-pre-line">{{ entry.notes }}</p>
                    <LogbookInspectionSummary
                      v-if="entry.entry_type === 'INSPECTION' && entry.inspection_detail"
                      :inspection-detail="entry.inspection_detail"
                      compact
                    />
                    <p v-if="entry.entry_type === 'VARROA_COUNT' && entry.varroa_count_detail" class="text-xs text-red-600 dark:text-red-400">
                      {{ $t('logbook.measured_mites_raw_val', { count: entry.varroa_count_detail.raw_count }) }}
                      → {{ $t('logbook.estimated_mites_val', { count: Math.round(entry.varroa_count_detail.estimated_total).toLocaleString() }) }}
                    </p>
                    <p v-if="entry.entry_type === 'VARROA_TREATMENT' && entry.varroa_treatment_detail" class="text-xs text-green-700 dark:text-green-400">
                      {{ entry.varroa_treatment_detail.product }}<template v-if="entry.varroa_treatment_detail.dosage"> · {{ entry.varroa_treatment_detail.dosage }}</template>
                    </p>
                  </td>
                  <td class="px-4 py-3 text-gray-500 dark:text-gray-400 whitespace-nowrap">{{ entry.created_by?.username || '–' }}</td>
                  <td class="px-4 py-3">
                    <div v-if="entry.images?.length" class="flex justify-center -space-x-1.5">
                      <img
                        v-for="img in entry.images"
                        :key="img.id"
                        :src="`/uploads/${img.thumbnail_path || img.image_path}`"
                        :alt="$t('logbook.table_images')"
                        class="h-7 w-7 rounded-full ring-2 ring-white dark:ring-dark-card object-cover cursor-pointer hover:scale-110 hover:z-10 transition-transform"
                        @click="lightboxImage = `/uploads/${img.image_path}`"
                      />
                    </div>
                    <span v-else class="block text-center text-gray-300 dark:text-gray-600">–</span>
                  </td>
                  <td class="px-4 py-3 text-right whitespace-nowrap">
                    <button type="button" class="p-1.5 text-gray-400 hover:text-primary rounded-lg hover:bg-gray-100 dark:hover:bg-dark-border inline-flex" :title="$t('common.edit')" :aria-label="$t('common.edit')" @click="openEditEntryModal(entry)">
                      <Pencil class="w-4 h-4" />
                    </button>
                    <button type="button" class="p-1.5 text-gray-400 hover:text-red-500 rounded-lg hover:bg-red-500/10 inline-flex" :title="$t('common.delete')" :aria-label="$t('common.delete')" @click="deleteEntry(entry)">
                      <Trash2 class="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </template>

    <!-- Image lightbox -->
    <div v-if="lightboxImage" class="fixed inset-0 z-50 flex items-center justify-center bg-black/90 p-4" @click="lightboxImage = null">
      <div class="relative max-w-4xl max-h-screen">
        <img :src="lightboxImage" class="max-w-full max-h-[85vh] rounded-2xl shadow-2xl" :alt="$t('logbook.table_images')" />
        <button type="button" class="absolute top-4 right-4 p-2 bg-white/20 hover:bg-white/40 text-white rounded-full" :aria-label="$t('common.cancel')" @click="lightboxImage = null">
          <X class="w-6 h-6" />
        </button>
      </div>
    </div>

    <LogbookSessionModal
      ref="sessionModalRef"
      :apiaries="apiaryStore.apiaries"
      :locations="locations"
      :hives="hives"
      :apiary-id="apiaryStore.activeApiaryId"
      @saved="onSessionSaved"
    />

    <LogbookEntryModal
      ref="entryModalRef"
      v-model:show="showEntryModal"
      :editing-entry="editingEntry"
      :hives="hives"
      :selected-session="entryModalSession"
      :apiary-id="apiaryStore.activeApiaryId"
      @saved="refreshCurrentEntries"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, reactive, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import axios from 'axios'
import { ArrowLeft, LayoutGrid, Loader2, Pencil, Plus, Table2, Trash2, X } from 'lucide-vue-next'
import { useApiaryStore } from '../stores/apiary'
import { useErrorStore } from '../stores/error'
import { useConfirmStore } from '../stores/confirm'
import AIChatPane from '../components/AIChatPane.vue'
import PageHeader from '../components/PageHeader.vue'
import LogbookEntryModal from '../components/LogbookEntryModal.vue'
import LogbookEntryCard from '../components/LogbookEntryCard.vue'
import LogbookSessionModal from '../components/LogbookSessionModal.vue'
import LogbookInspectionSummary from '../components/LogbookInspectionSummary.vue'
import { entryTypeLabel, formatLogDate, formatLogDateTime } from '../utils/logbook'

const VIEW_MODES = [
  { value: 'tiles', label: 'logbook.view_tiles', icon: LayoutGrid },
  { value: 'table', label: 'logbook.view_table', icon: Table2 },
]
const ENTRY_TYPES = ['INSPECTION', 'VARROA_COUNT', 'VARROA_TREATMENT', 'GENERAL']
const filterInputClass = 'w-full px-3 py-2 border border-gray-200 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary'

const { t, locale } = useI18n()
const apiaryStore = useApiaryStore()
const errorStore = useErrorStore()
const confirmStore = useConfirmStore()

const sessions = ref([])
const hives = ref([])
const locations = ref([])
const entries = ref([])
const sessionsLoading = ref(false)
const entriesLoading = ref(false)
const selectedSession = ref(null)
const lightboxImage = ref(null)

const viewMode = ref('tiles')
const allEntries = ref([])
const loadingAllEntries = ref(false)

const tableFilters = reactive({
  startDate: '',
  endDate: '',
  entryType: '',
  apiaryId: '',
  locationId: '',
  hiveId: '',
  userId: '',
})

const sessionModalRef = ref(null)
const entryModalRef = ref(null)
const showEntryModal = ref(false)
const editingEntry = ref(null)

// Editing from the table view must not attach the entry to whatever logbook happens to be open.
const entryModalSession = computed(() => {
  if (editingEntry.value) {
    return sessions.value.find(s => s.id === editingEntry.value.session_id) || null
  }
  return selectedSession.value
})

onMounted(loadApiaryData)

watch(() => apiaryStore.activeApiaryId, async (newVal) => {
  if (!newVal) return
  selectedSession.value = null
  entries.value = []
  resetTableFilters()
  await loadApiaryData()
  if (viewMode.value === 'table') await fetchAllEntries()
})

watch(viewMode, async (newVal) => {
  if (newVal === 'table') await fetchAllEntries()
})

watch(showEntryModal, (newVal) => {
  if (!newVal) editingEntry.value = null
})

async function loadApiaryData() {
  if (!apiaryStore.activeApiaryId) return
  await Promise.all([fetchSessions(), fetchHives(), fetchLocations()])
}

// ---------- Scope display ----------

function scopeInfo(session) {
  const names = list => (list || []).map(item => item.name).join(', ')
  switch (session.scope_type) {
    case 'LOCATION':
      return { icon: '📍', text: names(session.linked_locations) || t('logbook.scope_none'), chipClass: 'bg-green-500/10 text-green-700 dark:text-green-400' }
    case 'HIVE':
      return { icon: '🐝', text: names(session.linked_hives) || t('logbook.scope_none'), chipClass: 'bg-amber-500/10 text-amber-700 dark:text-amber-400' }
    case 'APIARY':
      return { icon: '🏢', text: names(session.linked_apiaries) || t('logbook.scope_all'), chipClass: 'bg-blue-500/10 text-blue-700 dark:text-blue-400' }
    default:
      return { icon: '🐝', text: session.hive?.name || t('logbook.scope_all'), chipClass: 'bg-gray-100 dark:bg-dark-bg text-gray-600 dark:text-gray-300' }
  }
}

// ---------- Session workspace ----------

const entriesByDate = computed(() => {
  const groups = []
  for (const entry of entries.value) {
    const last = groups[groups.length - 1]
    if (last && last.date === entry.date) {
      last.entries.push(entry)
    } else {
      groups.push({ date: entry.date, entries: [entry] })
    }
  }
  return groups
})

// ---------- Table filters ----------

function uniqueBy(getItem) {
  const map = new Map()
  allEntries.value.forEach(entry => {
    const item = getItem(entry)
    if (item) map.set(item.id, item.name)
  })
  return Array.from(map.entries())
    .map(([id, name]) => ({ id, name }))
    .sort((a, b) => a.name.localeCompare(b.name))
}

const uniqueLocations = computed(() => uniqueBy(e => e.hive?.location))
const uniqueHives = computed(() => uniqueBy(e => e.hive))
const uniqueCreators = computed(() => uniqueBy(e => e.created_by && { id: e.created_by.id, name: e.created_by.username }))

const hasActiveFilters = computed(() => Object.values(tableFilters).some(Boolean))

const filteredEntries = computed(() => allEntries.value.filter(entry => {
  // ISO dates (YYYY-MM-DD) compare correctly as strings and avoid timezone shifts.
  if (tableFilters.startDate && entry.date < tableFilters.startDate) return false
  if (tableFilters.endDate && entry.date > tableFilters.endDate) return false
  if (tableFilters.entryType && entry.entry_type !== tableFilters.entryType) return false
  if (tableFilters.apiaryId && entry.apiary_id !== tableFilters.apiaryId) return false
  if (tableFilters.locationId && entry.hive?.location?.id !== tableFilters.locationId) return false
  if (tableFilters.hiveId && entry.hive_id !== tableFilters.hiveId) return false
  if (tableFilters.userId && entry.created_by_id !== tableFilters.userId) return false
  return true
}))

function resetTableFilters() {
  Object.keys(tableFilters).forEach(key => { tableFilters[key] = '' })
}

// ---------- Data loading ----------

async function fetchSessions() {
  sessionsLoading.value = true
  try {
    const response = await axios.get('/api/logbook/sessions', { params: { apiary_id: apiaryStore.activeApiaryId } })
    sessions.value = response.data
  } catch (err) {
    console.error('Fetch sessions failed:', err)
  } finally {
    sessionsLoading.value = false
  }
}

async function fetchHives() {
  try {
    const response = await axios.get('/api/hives', { params: { apiary_id: apiaryStore.activeApiaryId } })
    hives.value = response.data
  } catch (err) {
    console.error('Fetch hives failed:', err)
  }
}

async function fetchLocations() {
  try {
    const response = await axios.get('/api/locations', { params: { apiary_id: apiaryStore.activeApiaryId } })
    locations.value = response.data
  } catch (err) {
    console.error('Fetch locations failed:', err)
  }
}

async function fetchEntries() {
  if (!selectedSession.value) return
  entriesLoading.value = true
  try {
    const response = await axios.get('/api/logbook/entries', {
      params: { apiary_id: apiaryStore.activeApiaryId, session_id: selectedSession.value.id },
    })
    entries.value = response.data
  } catch (err) {
    console.error('Fetch entries failed:', err)
  } finally {
    entriesLoading.value = false
  }
}

async function fetchAllEntries() {
  loadingAllEntries.value = true
  try {
    const response = await axios.get('/api/logbook/entries')
    allEntries.value = response.data
  } catch (err) {
    console.error('Fetch all entries failed:', err)
  } finally {
    loadingAllEntries.value = false
  }
}

async function refreshCurrentEntries() {
  if (viewMode.value === 'table') {
    await fetchAllEntries()
  } else {
    await Promise.all([fetchEntries(), fetchSessions()])
  }
}

// ---------- Sessions ----------

function selectSession(session) {
  selectedSession.value = session
  entries.value = []
  fetchEntries()
}

function closeSession() {
  selectedSession.value = null
  entries.value = []
}

async function onSessionSaved(session, wasEdit) {
  await fetchSessions()
  if (wasEdit) {
    if (selectedSession.value?.id === session.id) selectedSession.value = session
    return
  }
  viewMode.value = 'tiles'
  selectSession(session)
}

async function deleteSession(session) {
  const confirmed = await confirmStore.ask({
    title: t('logbook.delete_session'),
    message: t('logbook.delete_session_confirm', { title: session.title }),
    type: 'danger',
    confirmText: t('common.delete'),
  })
  if (!confirmed) return
  try {
    await axios.delete(`/api/logbook/sessions/${session.id}`)
    if (selectedSession.value?.id === session.id) closeSession()
    await fetchSessions()
  } catch (err) {
    errorStore.showError(t('logbook.delete_session'), err)
  }
}

// ---------- Entries ----------

function openCreateEntryModal() {
  editingEntry.value = null
  entryModalRef.value?.open(null)
}

function openEditEntryModal(entry) {
  editingEntry.value = entry
  entryModalRef.value?.open(entry)
}

function onApplyDraft(draft) {
  entryModalRef.value?.applyDraft(draft)
}

async function deleteEntry(entry) {
  const confirmed = await confirmStore.ask({
    title: t('common.delete'),
    message: t('logbook.delete_entry_confirm'),
    type: 'danger',
    confirmText: t('common.delete'),
  })
  if (!confirmed) return
  try {
    await axios.delete(`/api/logbook/entries/${entry.id}`)
    await refreshCurrentEntries()
  } catch (err) {
    errorStore.showError(t('common.delete'), err)
  }
}

async function uploadEntryImage(entryId, file) {
  const formData = new FormData()
  formData.append('file', file)
  try {
    await axios.post(`/api/logbook/entries/${entryId}/images`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    await refreshCurrentEntries()
  } catch (err) {
    errorStore.showError(t('hives.error_upload_photo'), err, t('hives.photo_upload_btn'))
  }
}

async function deleteEntryImage(imageId) {
  const confirmed = await confirmStore.ask({
    title: t('logbook.delete_image'),
    message: t('logbook.delete_image_confirm'),
    type: 'danger',
    confirmText: t('common.delete'),
  })
  if (!confirmed) return
  try {
    await axios.delete(`/api/logbook/images/${imageId}`)
    await refreshCurrentEntries()
  } catch (err) {
    errorStore.showError(t('logbook.delete_image'), err)
  }
}

// ---------- Formatting ----------

function formatDate(value) {
  return formatLogDate(value, locale.value)
}

function formatGroupDate(value) {
  return formatLogDate(value, locale.value, { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })
}

function formatDateTime(value) {
  return formatLogDateTime(value, locale.value)
}
</script>
