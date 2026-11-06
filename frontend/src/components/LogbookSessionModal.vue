<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div
        v-if="show"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm"
        role="dialog"
        aria-modal="true"
        @click.self="close"
      >
        <div class="bg-white dark:bg-dark-card rounded-3xl shadow-2xl w-full max-w-lg flex flex-col max-h-[calc(100vh-2rem)] overflow-hidden">
          <div class="flex justify-between items-center px-6 py-4 border-b border-gray-100 dark:border-dark-border">
            <h3 class="text-lg font-bold text-gray-900 dark:text-white">
              {{ isEdit ? $t('logbook.edit_session') : $t('logbook.new_session_title') }}
            </h3>
            <button type="button" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200" :aria-label="$t('common.cancel')" @click="close">
              <X class="w-5 h-5" />
            </button>
          </div>

          <form class="p-6 space-y-5 overflow-y-auto" @submit.prevent="submit">
            <div>
              <div class="flex justify-between items-center mb-1">
                <label for="session-title" class="block text-xs font-semibold text-gray-600 dark:text-gray-300">{{ $t('logbook.session_title_label') }}</label>
                <span class="text-[11px] font-mono" :class="form.title.length >= TITLE_MAX ? 'text-red-500' : 'text-gray-400'">
                  {{ form.title.length }}/{{ TITLE_MAX }}
                </span>
              </div>
              <input
                id="session-title"
                v-model="form.title"
                type="text"
                required
                :maxlength="TITLE_MAX"
                :placeholder="$t('logbook.session_title_placeholder')"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm"
              />
            </div>

            <div>
              <span class="block text-xs font-semibold text-gray-600 dark:text-gray-300 mb-2">{{ $t('logbook.session_scope') }}</span>
              <div class="grid grid-cols-3 gap-2">
                <button
                  v-for="scope in SCOPES"
                  :key="scope.type"
                  type="button"
                  class="flex flex-col items-center justify-center p-3 rounded-2xl border text-xs font-semibold transition-colors"
                  :class="form.scopeType === scope.type ? 'bg-primary/5 border-primary text-primary' : 'border-gray-200 hover:border-gray-300 dark:border-dark-border dark:text-gray-300'"
                  @click="form.scopeType = scope.type"
                >
                  <span class="text-base mb-1">{{ scope.icon }}</span>
                  <span>{{ $t(scope.label) }}</span>
                </button>
              </div>
            </div>

            <div>
              <span class="block text-xs font-semibold text-gray-600 dark:text-gray-300 mb-2">{{ $t(activeScope.selectLabel) }}</span>
              <div v-if="scopeOptions.length === 0" class="text-xs text-gray-400 italic bg-gray-50 dark:bg-dark-bg p-3 rounded-2xl border border-gray-200 dark:border-dark-border">
                {{ $t(activeScope.emptyLabel) }}
              </div>
              <div v-else class="max-h-48 overflow-y-auto border border-gray-200 dark:border-dark-border rounded-2xl p-3 space-y-2 bg-gray-50 dark:bg-dark-bg">
                <label
                  v-for="option in scopeOptions"
                  :key="option.id"
                  class="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300 cursor-pointer hover:text-primary"
                >
                  <input
                    v-model="form.selected[form.scopeType]"
                    type="checkbox"
                    :value="option.id"
                    class="rounded text-primary focus:ring-primary border-gray-300 dark:border-dark-border"
                  />
                  <span class="font-medium">{{ option.name }}</span>
                  <span v-if="option.hint" class="text-xs text-gray-400">({{ option.hint }})</span>
                </label>
              </div>
            </div>

            <div class="flex justify-end gap-2 pt-2">
              <button type="button" class="px-4 py-2 text-sm font-semibold text-gray-500 hover:text-gray-700 dark:hover:text-gray-300" @click="close">
                {{ $t('common.cancel') }}
              </button>
              <button type="submit" :disabled="saving" class="px-5 py-2 bg-primary hover:bg-primary-hover disabled:opacity-60 text-white font-bold text-sm rounded-xl shadow-md">
                {{ isEdit ? $t('common.save') : $t('logbook.create') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { reactive, ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useI18n } from 'vue-i18n'
import axios from 'axios'
import { X } from 'lucide-vue-next'
import { useErrorStore } from '../stores/error'

const props = defineProps({
  apiaries: { type: Array, default: () => [] },
  locations: { type: Array, default: () => [] },
  hives: { type: Array, default: () => [] },
  apiaryId: { type: String, default: null },
})

const emit = defineEmits(['saved'])

const TITLE_MAX = 30
const SCOPES = [
  { type: 'APIARY', icon: '🏢', label: 'beeAgent.scope_apiary', selectLabel: 'logbook.select_apiaries', emptyLabel: 'logbook.no_apiaries' },
  { type: 'LOCATION', icon: '📍', label: 'beeAgent.scope_location', selectLabel: 'logbook.select_locations', emptyLabel: 'logbook.no_locations' },
  { type: 'HIVE', icon: '🐝', label: 'beeAgent.scope_hive', selectLabel: 'logbook.select_hives', emptyLabel: 'logbook.no_hives' },
]

const { t } = useI18n()
const errorStore = useErrorStore()

const show = ref(false)
const saving = ref(false)
const editingSession = ref(null)
const isEdit = computed(() => !!editingSession.value)

const form = reactive({
  title: '',
  scopeType: 'APIARY',
  selected: { APIARY: [], LOCATION: [], HIVE: [] },
})

const activeScope = computed(() => SCOPES.find(s => s.type === form.scopeType))

const scopeOptions = computed(() => {
  if (form.scopeType === 'LOCATION') return props.locations
  if (form.scopeType === 'HIVE') {
    return props.hives.map(h => ({ id: h.id, name: h.name, hint: h.location?.name || t('logbook.no_location') }))
  }
  return props.apiaries
})

function open(session = null) {
  editingSession.value = session
  form.title = session?.title || ''
  form.scopeType = session?.scope_type || 'APIARY'
  form.selected.APIARY = session ? (session.linked_apiaries || []).map(a => a.id) : (props.apiaryId ? [props.apiaryId] : [])
  form.selected.LOCATION = (session?.linked_locations || []).map(l => l.id)
  form.selected.HIVE = (session?.linked_hives || []).map(h => h.id)
  show.value = true
}

function close() {
  show.value = false
}

async function submit() {
  const title = form.title.trim()
  if (!title) return
  if (form.selected[form.scopeType].length === 0) {
    errorStore.showError(t('logbook.error_select_at_least_one'))
    return
  }

  const payload = {
    title,
    scope_type: form.scopeType,
    hive_id: editingSession.value?.hive_id || null,
    linked_apiary_ids: form.scopeType === 'APIARY' ? form.selected.APIARY : [],
    linked_location_ids: form.scopeType === 'LOCATION' ? form.selected.LOCATION : [],
    linked_hive_ids: form.scopeType === 'HIVE' ? form.selected.HIVE : [],
  }

  saving.value = true
  try {
    const response = isEdit.value
      ? await axios.put(`/api/logbook/sessions/${editingSession.value.id}`, payload)
      : await axios.post('/api/logbook/sessions', payload, { params: { apiary_id: props.apiaryId } })
    close()
    emit('saved', response.data, isEdit.value)
  } catch (err) {
    errorStore.showError(t('logbook.session_form_submission_error'), err, t('common.save'))
  } finally {
    saving.value = false
  }
}

function handleEscape(event) {
  if (event.key === 'Escape' && show.value) close()
}

onMounted(() => document.addEventListener('keydown', handleEscape))
onBeforeUnmount(() => document.removeEventListener('keydown', handleEscape))

defineExpose({ open })
</script>

<style scoped>
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.2s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}
</style>
