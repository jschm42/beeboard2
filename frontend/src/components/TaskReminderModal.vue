<template>
  <transition name="modal">
    <div 
      v-if="showModal && reminderTasks.length > 0" 
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm"
      @click.self="closeModal"
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
    >
      <div 
        class="bg-white dark:bg-dark-card rounded-3xl text-left overflow-hidden shadow-2xl transform transition-all sm:max-w-lg sm:w-full border border-red-500/20 dark:border-red-500/10 flex flex-col max-h-[85vh]"
      >
        <!-- Header -->
        <div class="px-6 py-4 bg-red-500/10 dark:bg-red-950/20 border-b border-red-100 dark:border-red-950/30 flex justify-between items-center shrink-0">
          <div class="flex items-center space-x-2">
            <span class="text-xl">🔔</span>
            <h3 class="text-base font-extrabold text-red-700 dark:text-red-400 uppercase tracking-wider" id="modal-title">
              Erinnerung: Fällige Aufgaben
            </h3>
          </div>
          <button @click="closeModal" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>

        <!-- Task List Body -->
        <div class="p-6 overflow-y-auto space-y-4 flex-grow">
          <p class="text-xs text-gray-500 dark:text-gray-400 leading-relaxed font-medium">
            Du hast anstehende oder überfällige Arbeiten an deinen Bienenständen. Erledige sie gleich hier mit einem Klick!
          </p>

          <div class="space-y-3">
            <div 
              v-for="task in reminderTasks" 
              :key="task.id"
              class="p-4 rounded-2xl border flex items-center justify-between gap-4 transition-all"
              :class="isOverdue(task.due_date) 
                ? 'bg-red-500/[0.03] dark:bg-red-500/[0.05] border-red-500/25' 
                : 'bg-yellow-500/[0.02] dark:bg-yellow-500/[0.04] border-yellow-500/20'"
            >
              <div class="min-w-0 flex-grow">
                <div class="flex items-center gap-1.5 flex-wrap">
                  <span 
                    class="text-[8px] font-black uppercase tracking-wider px-1.5 py-0.5 rounded-full"
                    :class="isOverdue(task.due_date) 
                      ? 'bg-red-100 text-red-700 dark:bg-red-950/40 dark:text-red-400' 
                      : 'bg-yellow-100 text-yellow-700 dark:bg-yellow-950/40 dark:text-yellow-400'"
                  >
                    {{ isOverdue(task.due_date) ? 'Überfällig' : 'Bald fällig' }}
                  </span>
                  
                  <span class="text-[9px] font-bold text-gray-400 dark:text-gray-500 font-mono">
                    {{ formatDate(task.due_date) }}
                  </span>
                </div>

                <h4 class="font-extrabold text-sm text-gray-900 dark:text-white mt-1.5 leading-snug truncate">
                  {{ task.title }}
                </h4>

                <div class="mt-1 flex flex-wrap gap-1">
                  <span v-if="task.location" class="text-[9px] font-bold text-blue-600 dark:text-blue-400">
                    📍 {{ task.location.name }}
                  </span>
                  <span v-if="task.hive" class="text-[9px] font-bold text-amber-700 dark:text-primary">
                    🐝 {{ task.hive.name }}
                  </span>
                </div>
              </div>

              <button 
                @click="completeTask(task.id)"
                class="px-3 py-1.5 bg-green-500 hover:bg-green-600 dark:bg-green-600 dark:hover:bg-green-700 text-white font-extrabold text-[9px] uppercase tracking-wider rounded-lg shadow-sm transition-colors shrink-0 flex items-center gap-0.5 cursor-pointer"
              >
                <span>Erledigt</span> ✓
              </button>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="px-6 py-4 bg-gray-50 dark:bg-dark-bg/25 border-t border-gray-100 dark:border-dark-border flex justify-end gap-2 shrink-0">
          <button 
            type="button" 
            @click="snoozeReminders" 
            class="px-4 py-2 text-xs font-extrabold text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-dark-border rounded-xl transition-all"
          >
            Später erinnern (Snooze)
          </button>
          <button 
            type="button" 
            @click="closeModal" 
            class="px-5 py-2 bg-gray-800 hover:bg-gray-900 dark:bg-dark-border dark:hover:bg-dark-border/80 text-white dark:text-gray-200 font-extrabold text-xs uppercase tracking-wider rounded-xl shadow-md transition-all cursor-pointer"
          >
            Schließen
          </button>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useApiaryStore } from '../stores/apiary'
import axios from 'axios'

const authStore = useAuthStore()
const apiaryStore = useApiaryStore()

const showModal = ref(false)
const reminderTasks = ref([])

async function fetchReminderTasks() {
  if (!authStore.isAuthenticated || !apiaryStore.activeApiaryId) return
  
  // Check if reminder was already shown during this session
  const alreadyShown = sessionStorage.getItem('tasks_reminder_shown')
  if (alreadyShown === 'true') return

  try {
    const apiaryId = apiaryStore.activeApiaryId
    const res = await axios.get('/api/tasks', { 
      params: { 
        apiary_id: apiaryId,
        is_completed: false
      } 
    })
    
    // Filter tasks that are either:
    // 1. Overdue (due_date < today)
    // 2. Due soon (due_date is between today and today + 3 days)
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    
    const maxFutureDate = new Date()
    maxFutureDate.setDate(maxFutureDate.getDate() + 3)
    maxFutureDate.setHours(23, 59, 59, 999)

    reminderTasks.value = res.data.filter(task => {
      if (!task.due_date) return false
      const due = new Date(task.due_date)
      return due <= maxFutureDate
    })

    if (reminderTasks.value.length > 0) {
      showModal.value = true
      sessionStorage.setItem('tasks_reminder_shown', 'true')
    }
  } catch (err) {
    console.error('Failed to fetch reminder tasks:', err)
  }
}

onMounted(() => {
  fetchReminderTasks()
})

// Re-fetch reminders if the active apiary changes
watch(() => apiaryStore.activeApiaryId, () => {
  sessionStorage.removeItem('tasks_reminder_shown') // reset on apiary switch
  fetchReminderTasks()
})

watch(() => authStore.isAuthenticated, (auth) => {
  if (auth) {
    sessionStorage.removeItem('tasks_reminder_shown')
    fetchReminderTasks()
  } else {
    showModal.value = false
    reminderTasks.value = []
  }
})

async function completeTask(id) {
  try {
    await axios.post(`/api/tasks/${id}/complete`)
    reminderTasks.value = reminderTasks.value.filter(t => t.id !== id)
    if (reminderTasks.value.length === 0) {
      showModal.value = false
    }
  } catch (err) {
    console.error('Failed to complete task from reminder modal:', err)
  }
}

function closeModal() {
  showModal.value = false
}

function snoozeReminders() {
  // Hide for now, but reset key so next page refresh or dashboard landing re-checks it
  showModal.value = false
  sessionStorage.removeItem('tasks_reminder_shown')
}

// Helpers
function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

function isOverdue(dateStr) {
  if (!dateStr) return false
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const d = new Date(dateStr)
  d.setHours(0, 0, 0, 0)
  return d < today
}
</script>

<style scoped>
@reference "../style.css";

/* Modal Transition Styles */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.modal-enter-active .bg-white,
.modal-leave-active .bg-white,
.modal-enter-active .dark\:bg-dark-card,
.modal-leave-active .dark\:bg-dark-card {
  transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .bg-white,
.modal-leave-to .bg-white,
.modal-enter-from .dark\:bg-dark-card,
.modal-leave-to .dark\:bg-dark-card {
  transform: scale(0.95) translateY(12px);
}
</style>
