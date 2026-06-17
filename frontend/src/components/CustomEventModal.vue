<template>
  <transition name="fade">
    <div
      v-if="modelValue"
      class="fixed inset-0 z-[90] flex items-center justify-center bg-black/50 backdrop-blur-sm p-4"
      @click.self="close"
    >
      <div class="w-full max-w-lg rounded-2xl bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border shadow-2xl overflow-hidden animate-scale flex flex-col max-h-[90vh]">
        <!-- Header -->
        <div class="px-6 py-4 border-b border-gray-200 dark:border-dark-border flex items-center justify-between shrink-0">
          <h2 class="text-lg font-extrabold text-gray-900 dark:text-white flex items-center gap-2">
            📅 {{ form.id ? $t('tasks.custom_event_modal_edit_title') : $t('tasks.custom_event_modal_title') }}
          </h2>
          <button
            class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 cursor-pointer"
            @click="close"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <form @submit.prevent="saveEvent" class="space-y-4 p-6 overflow-y-auto flex-grow">
          <!-- Title -->
          <input
            v-model="form.title"
            type="text"
            required
            :placeholder="$t('tasks.custom_event_placeholder')"
            class="w-full px-4 py-2.5 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm font-semibold"
          />

          <!-- Start/End dates -->
          <div class="grid grid-cols-2 gap-2">
            <input
              v-model="form.start_date"
              type="date"
              required
              class="w-full px-4 py-2.5 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm"
            />
            <input
              v-model="form.end_date"
              type="date"
              required
              class="w-full px-4 py-2.5 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm"
            />
          </div>

          <!-- All-day & Recurring Toggles -->
          <div class="flex items-center space-x-4 py-1">
            <label class="flex items-center space-x-2 text-xs font-bold text-gray-600 dark:text-gray-400 uppercase tracking-wider cursor-pointer">
              <input
                v-model="form.is_all_day"
                type="checkbox"
                class="w-4 h-4 rounded border-gray-300 text-primary focus:ring-primary"
              />
              <span>{{ $t('tasks.all_day') }}</span>
            </label>

            <button
              type="button"
              @click="form.is_recurring = !form.is_recurring"
              class="flex items-center space-x-1 px-3 py-1.5 rounded-lg border text-xs font-bold uppercase transition-all"
              :class="form.is_recurring
                ? 'bg-primary/10 border-primary text-primary'
                : 'bg-white dark:bg-dark-bg border-gray-200 dark:border-gray-700 text-gray-500 hover:border-gray-300'"
            >
              <span>🔄 {{ $t('tasks.recurring_btn') }}</span>
            </button>
          </div>

          <!-- Time pickers when NOT all-day -->
          <div v-if="!form.is_all_day" class="grid grid-cols-2 gap-2 animate-scale">
            <input
              v-model="form.start_time"
              type="time"
              class="w-full px-4 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-sm"
            />
            <input
              v-model="form.end_time"
              type="time"
              class="w-full px-4 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-sm"
            />
          </div>

          <!-- Recurrence Panel -->
          <div
            v-if="form.is_recurring"
            class="p-3 bg-gray-50 dark:bg-dark-bg/40 rounded-xl border border-gray-200/60 dark:border-dark-border/60 space-y-2.5 text-xs animate-scale"
          >
            <div class="flex flex-wrap items-center gap-2">
              <span class="font-bold text-gray-500 uppercase tracking-wider">{{ $t('tasks.repeat_every') }}</span>
              <select
                v-model.number="form.recurrence_interval_value"
                class="px-2 py-1 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded focus:ring-1 focus:ring-primary font-bold text-center"
              >
                <option v-for="n in 30" :key="n" :value="n">{{ n }}</option>
              </select>
              <select
                v-model="form.recurrence_interval_type"
                class="px-2 py-1 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded focus:ring-1 focus:ring-primary font-bold"
              >
                <option value="DAILY">{{ $t('tasks.day_unit') }}</option>
                <option value="WEEKLY">{{ $t('tasks.week_unit') }}</option>
                <option value="MONTHLY">{{ $t('tasks.month_unit') }}</option>
                <option value="YEARLY">{{ $t('tasks.year_unit') }}</option>
              </select>

              <div class="flex items-center gap-1.5 shrink-0">
                <span class="font-bold text-gray-500 uppercase tracking-wider">{{ $t('tasks.until') }}</span>
                <input
                  v-model="form.recurrence_end_date"
                  type="date"
                  :title="$t('tasks.recurrence_end_date_tooltip')"
                  class="px-2 py-1 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded font-bold"
                />
              </div>
            </div>

            <!-- Weekday Selectors (Shown only when WEEKLY is selected) -->
            <div v-if="form.recurrence_interval_type === 'WEEKLY'" class="flex items-center gap-1 py-1">
              <button
                v-for="(day, index) in weekdaysList"
                :key="index"
                type="button"
                @click="toggleWeekday(index)"
                class="w-8 h-8 rounded border text-[11px] font-black transition-all flex items-center justify-center cursor-pointer"
                :class="form.recurrence_weekdays.includes(index)
                  ? 'bg-primary border-primary text-white'
                  : 'bg-white dark:bg-dark-bg border-gray-200 dark:border-gray-700 text-gray-500 hover:border-gray-300'"
              >
                {{ day.label }}
              </button>
            </div>
          </div>

          <!-- Notes & Color -->
          <div class="grid grid-cols-[1fr_auto] gap-2 items-center">
            <input
              v-model="form.notes"
              type="text"
              :placeholder="$t('tasks.custom_event_notes_placeholder')"
              class="w-full px-4 py-2.5 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm"
            />
            <input
              v-model="form.color"
              type="color"
              class="h-10 w-12 p-1 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-dark-bg cursor-pointer"
            />
          </div>

          <!-- Existing events list -->
          <div v-if="events.length" class="pt-4 border-t border-gray-100 dark:border-dark-border space-y-2">
            <h4 class="text-xs font-extrabold uppercase tracking-wider text-gray-500 dark:text-gray-400">
              {{ $t('tasks.custom_event_list_title') }}
            </h4>
            <div class="space-y-1.5 max-h-48 overflow-y-auto">
              <div
                v-for="event in events"
                :key="event.id"
                class="p-2.5 rounded-xl border border-gray-200 dark:border-dark-border bg-gray-50 dark:bg-dark-bg/60"
              >
                <div class="flex items-start justify-between gap-2">
                  <div class="min-w-0 flex-1">
                    <div class="text-xs font-bold text-gray-900 dark:text-white flex items-center gap-1.5">
                      <span class="inline-block w-2.5 h-2.5 rounded-full shrink-0" :style="{ backgroundColor: event.color }"></span>
                      <span class="truncate">{{ event.title }}</span>
                    </div>
                    <div class="text-[11px] text-gray-500 dark:text-gray-400 mt-0.5">
                      {{ formatDate(event.start_date) }}<span v-if="event.end_date !== event.start_date"> – {{ formatDate(event.end_date) }}</span>
                    </div>
                  </div>
                  <div class="flex items-center gap-2 shrink-0">
                    <button type="button" @click="loadEvent(event)" class="text-[11px] text-primary font-bold hover:underline">
                      {{ $t('common.edit') }}
                    </button>
                    <button type="button" @click="removeEvent(event.id)" class="text-[11px] text-red-500 font-bold hover:underline">
                      {{ $t('common.delete') }}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Footer Actions -->
          <div class="pt-4 border-t border-gray-200 dark:border-dark-border flex justify-end items-center gap-2">
            <button
              type="button"
              @click="close"
              class="px-4 py-2.5 text-xs font-bold text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 cursor-pointer"
            >
              {{ $t('common.cancel') }}
            </button>
            <button
              type="submit"
              :disabled="submitting || !form.title.trim()"
              class="px-5 py-2.5 bg-primary hover:bg-primary-hover text-white font-extrabold text-xs uppercase tracking-wider rounded-xl shadow-md disabled:opacity-50 hover-scale cursor-pointer flex items-center justify-center space-x-1.5"
            >
              <svg v-if="submitting" class="animate-spin h-3.5 w-3.5 text-white" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span>{{ form.id ? $t('tasks.save_event_btn') : $t('tasks.create_event_btn') }}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useConfirmStore } from '../stores/confirm'
import { useErrorStore } from '../stores/error'
import {
  getCustomCalendarEvents,
  upsertCustomCalendarEvent,
  deleteCustomCalendarEvent,
} from '../utils/calendarEvents'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  apiaryId: { type: [String, Number], default: null },
  initialDate: { type: String, default: '' },
})

const emit = defineEmits(['update:modelValue', 'changed'])

const { t } = useI18n()
const confirmStore = useConfirmStore()
const errorStore = useErrorStore()

const submitting = ref(false)

const weekdaysList = [
  { value: 0, label: 'M' },
  { value: 1, label: 'D' },
  { value: 2, label: 'M' },
  { value: 3, label: 'D' },
  { value: 4, label: 'F' },
  { value: 5, label: 'S' },
  { value: 6, label: 'S' },
]

function todayStr() {
  return new Date().toISOString().split('T')[0]
}

function blankForm(date = '') {
  const start = date || todayStr()
  return {
    id: null,
    title: '',
    notes: '',
    start_date: start,
    end_date: start,
    color: '#2563eb',
    is_recurring: false,
    recurrence_interval_type: 'WEEKLY',
    recurrence_interval_value: 1,
    recurrence_weekdays: [],
    recurrence_end_date: '',
    is_all_day: true,
    start_time: '',
    end_time: '',
  }
}

const form = reactive(blankForm(props.initialDate))
const events = ref([])

function refreshEvents() {
  if (!props.apiaryId) {
    events.value = []
    return
  }
  events.value = getCustomCalendarEvents(props.apiaryId)
}

function resetForm() {
  Object.assign(form, blankForm(props.initialDate))
}

function loadEvent(event) {
  const weekdays = event.recurrence_weekdays
    ? event.recurrence_weekdays.split(',').map(d => parseInt(d)).filter(d => !isNaN(d))
    : []
  Object.assign(form, {
    ...event,
    is_recurring: !!event.is_recurring,
    recurrence_interval_type: event.recurrence_interval_type || 'WEEKLY',
    recurrence_interval_value: event.recurrence_interval_value || 1,
    recurrence_weekdays: weekdays,
    recurrence_end_date: event.recurrence_end_date || '',
    is_all_day: event.is_all_day !== false,
    start_time: event.start_time || '',
    end_time: event.end_time || '',
  })
}

function toggleWeekday(dayValue) {
  if (!form.recurrence_weekdays) {
    form.recurrence_weekdays = []
  }
  const idx = form.recurrence_weekdays.indexOf(dayValue)
  if (idx >= 0) {
    form.recurrence_weekdays.splice(idx, 1)
  } else {
    form.recurrence_weekdays.push(dayValue)
  }
}

async function saveEvent() {
  if (!props.apiaryId || !form.title.trim()) return
  submitting.value = true
  try {
    const payload = {
      ...form,
      title: form.title.trim(),
      notes: form.notes.trim(),
      recurrence_weekdays: (form.recurrence_weekdays || []).join(','),
      is_all_day: form.is_all_day,
      start_time: form.is_all_day ? '' : form.start_time,
      end_time: form.is_all_day ? '' : form.end_time,
    }
    upsertCustomCalendarEvent(props.apiaryId, payload)
    refreshEvents()
    resetForm()
    emit('changed')
  } catch (err) {
    errorStore.showError(t('tasks.error_save'), err, t('sidebar.calendar'))
  } finally {
    submitting.value = false
  }
}

async function removeEvent(eventId) {
  const confirmed = await confirmStore.ask({
    title: t('tasks.confirm_delete_event_title'),
    message: t('tasks.confirm_delete_event_msg'),
    type: 'danger',
    confirmText: t('tasks.confirm_delete_btn'),
  })
  if (!confirmed) return

  deleteCustomCalendarEvent(props.apiaryId, eventId)
  if (form.id === eventId) resetForm()
  refreshEvents()
  emit('changed')
}

function close() {
  emit('update:modelValue', false)
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString(
    (typeof navigator !== 'undefined' && navigator.language?.startsWith('de')) ? 'de-DE' : 'en-US',
    { day: '2-digit', month: '2-digit', year: 'numeric' }
  )
}

// Prefill when opened
watch(
  () => props.modelValue,
  (val) => {
    if (val) {
      resetForm()
      refreshEvents()
    }
  }
)

// External trigger to edit an existing event (e.g. clicking an event pill on the calendar)
defineExpose({ loadEvent, refreshEvents })
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
.animate-scale {
  animation: scaleUp 0.2s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
@keyframes scaleUp {
  from {
    transform: scale(0.95);
  }
  to {
    transform: scale(1);
  }
}
</style>
