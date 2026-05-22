<template>
  <transition name="modal">
    <div 
      v-if="confirmStore.show" 
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/45 backdrop-blur-md"
      @click.self="cancel"
    >
      <div 
        class="bg-white dark:bg-dark-card border rounded-3xl shadow-2xl w-full max-w-md overflow-hidden transform transition-all duration-300 scale-100 flex flex-col"
        :class="borderClass"
        role="dialog" 
        aria-modal="true"
      >
        <!-- Top Colored Accent Bar -->
        <div class="h-2 bg-gradient-to-r" :class="accentBarClass"></div>

        <!-- Content Area -->
        <div class="p-6 space-y-5">
          <!-- Icon & Title -->
          <div class="flex items-start space-x-4">
            <div class="p-3 rounded-2xl shrink-0" :class="iconBgClass">
              <!-- Custom Icon based on Type -->
              <!-- Danger/Delete Icon -->
              <svg v-if="confirmStore.type === 'danger'" class="w-8 h-8 stroke-current fill-none" viewBox="0 0 24 24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="3 6 5 6 21 6"></polyline>
                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                <line x1="10" y1="11" x2="10" y2="17"></line>
                <line x1="14" y1="11" x2="14" y2="17"></line>
              </svg>
              <!-- Warning/Attention Icon -->
              <svg v-else-if="confirmStore.type === 'warning'" class="w-8 h-8 stroke-current fill-none" viewBox="0 0 24 24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                <line x1="12" y1="9" x2="12" y2="13"></line>
                <line x1="12" y1="17" x2="12.01" y2="17"></line>
              </svg>
              <!-- Info/Default Icon -->
              <svg v-else class="w-8 h-8 stroke-current fill-none" viewBox="0 0 24 24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="16" x2="12" y2="12"></line>
                <line x1="12" y1="8" x2="12.01" y2="8"></line>
              </svg>
            </div>
            <div class="flex-grow pt-1 text-left">
              <h3 class="text-lg font-black text-gray-900 dark:text-white leading-tight">
                {{ confirmStore.title }}
              </h3>
            </div>
          </div>

          <!-- Main Message -->
          <div class="bg-gray-50 dark:bg-dark-bg/60 border border-gray-100 dark:border-dark-border p-4.5 rounded-2xl text-left">
            <p class="text-sm text-gray-700 dark:text-gray-200 leading-relaxed font-semibold">
              {{ confirmStore.message }}
            </p>
          </div>
        </div>

        <!-- Footer Actions -->
        <div class="p-6 bg-gray-50 dark:bg-dark-bg/40 border-t border-gray-100 dark:border-dark-border/80 flex items-center justify-end gap-3">
          <button 
            @click="cancel"
            class="px-5 py-2.5 bg-gray-200 hover:bg-gray-300 dark:bg-dark-border dark:hover:bg-gray-700 text-gray-800 dark:text-gray-200 font-extrabold text-xs rounded-xl uppercase tracking-wider transition-all duration-150 cursor-pointer"
          >
            {{ confirmStore.cancelText }}
          </button>
          <button 
            @click="confirm"
            class="px-6 py-2.5 text-white font-extrabold text-xs rounded-xl shadow-lg uppercase tracking-wider transition-all hover-scale duration-150 cursor-pointer"
            :class="confirmBtnClass"
          >
            {{ confirmStore.confirmText }}
          </button>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { computed } from 'vue'
import { useConfirmStore } from '../stores/confirm'

const confirmStore = useConfirmStore()

const borderClass = computed(() => {
  if (confirmStore.type === 'danger') return 'border-red-200 dark:border-red-900/30'
  if (confirmStore.type === 'warning') return 'border-amber-200 dark:border-amber-900/30'
  return 'border-blue-200 dark:border-blue-900/30'
})

const accentBarClass = computed(() => {
  if (confirmStore.type === 'danger') return 'from-red-500 via-rose-500 to-red-600'
  if (confirmStore.type === 'warning') return 'from-amber-400 via-orange-500 to-amber-500'
  return 'from-blue-500 via-sky-500 to-indigo-600'
})

const iconBgClass = computed(() => {
  if (confirmStore.type === 'danger') return 'bg-red-100 dark:bg-red-500/10 text-red-600 dark:text-red-400'
  if (confirmStore.type === 'warning') return 'bg-amber-100 dark:bg-amber-500/10 text-amber-600 dark:text-amber-500'
  return 'bg-blue-100 dark:bg-blue-500/10 text-blue-600 dark:text-blue-400'
})

const confirmBtnClass = computed(() => {
  if (confirmStore.type === 'danger') {
    return 'bg-red-600 hover:bg-red-700 shadow-red-500/20'
  }
  if (confirmStore.type === 'warning') {
    return 'bg-amber-500 hover:bg-amber-600 shadow-amber-500/20'
  }
  return 'bg-blue-600 hover:bg-blue-700 shadow-blue-500/20'
})

function confirm() {
  confirmStore.confirm()
}

function cancel() {
  confirmStore.cancel()
}
</script>

<style scoped>
/* Modal Transition Styles */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.modal-enter-active .bg-white,
.modal-leave-active .bg-white {
  transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .bg-white,
.modal-leave-to .bg-white {
  transform: scale(0.95) translateY(12px);
}
</style>
