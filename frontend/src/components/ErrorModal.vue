<template>
  <transition name="modal">
    <div 
      v-if="errorStore.show" 
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/45 backdrop-blur-md"
      @click.self="close"
    >
      <div 
        class="bg-white dark:bg-dark-card border border-red-200 dark:border-red-900/30 rounded-3xl shadow-2xl w-full max-w-lg overflow-hidden transform transition-all duration-300 scale-100 flex flex-col max-h-[85vh]"
        role="dialog" 
        aria-modal="true"
      >
        <!-- Top Colored Accent Bar -->
        <div class="h-2 bg-gradient-to-r from-red-500 via-amber-500 to-red-600"></div>

        <!-- Scrollable Content Area -->
        <div class="p-6 overflow-y-auto space-y-6 flex-grow">
          <!-- Icon & Title -->
          <div class="flex items-start space-x-4">
            <div class="p-3 bg-red-100 dark:bg-red-500/10 rounded-2xl text-red-600 dark:text-red-400 shrink-0">
              <!-- Custom Premium Alert Icon -->
              <svg class="w-8 h-8 stroke-current fill-none" viewBox="0 0 24 24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                <line x1="12" y1="9" x2="12" y2="13"></line>
                <line x1="12" y1="17" x2="12.01" y2="17"></line>
              </svg>
            </div>
            <div class="flex-grow pt-1">
              <h3 class="text-xl font-black text-gray-900 dark:text-white leading-tight">
                {{ errorStore.title }}
              </h3>
              <p class="text-sm font-semibold text-red-500 dark:text-red-400 mt-0.5">
                Aktion fehlgeschlagen
              </p>
            </div>
          </div>

          <!-- Main Friendly Message -->
          <div class="bg-gray-50 dark:bg-dark-bg/60 border border-gray-100 dark:border-dark-border p-5 rounded-2xl">
            <p class="text-sm md:text-base text-gray-700 dark:text-gray-200 leading-relaxed font-medium">
              {{ errorStore.message }}
            </p>
          </div>

          <!-- Technical Details Accordion -->
          <div v-if="errorStore.details" class="border border-gray-200 dark:border-dark-border rounded-2xl overflow-hidden transition-all">
            <button 
              @click="toggleDetails"
              class="w-full px-5 py-3 bg-gray-50 dark:bg-dark-bg/30 text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider flex justify-between items-center hover:bg-gray-100 dark:hover:bg-dark-bg/60 transition-colors"
            >
              <span>🔍 Technische Details</span>
              <svg 
                class="w-4 h-4 transform transition-transform duration-200" 
                :class="{'rotate-180': showDetails}"
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            
            <transition name="details-slide">
              <div v-if="showDetails" class="bg-gray-950 p-5 font-mono text-[11px] text-gray-300 border-t border-gray-200 dark:border-dark-border space-y-2 max-h-60 overflow-y-auto select-text">
                <div v-if="errorStore.details.status" class="flex justify-between border-b border-gray-800 pb-1.5">
                  <span class="text-red-400 font-bold">Status:</span>
                  <span class="text-white font-extrabold">{{ errorStore.details.status }} {{ errorStore.details.statusText }}</span>
                </div>
                <div v-if="errorStore.details.method" class="flex justify-between border-b border-gray-800 pb-1.5">
                  <span class="text-gray-400">Methode:</span>
                  <span class="text-amber-400 font-bold">{{ errorStore.details.method }}</span>
                </div>
                <div v-if="errorStore.details.url" class="border-b border-gray-800 pb-1.5 space-y-1">
                  <p class="text-gray-400">Anforderungs-URL:</p>
                  <p class="text-white break-all">{{ errorStore.details.url }}</p>
                </div>
                <div class="space-y-1">
                  <p class="text-gray-400">Server-Antwort:</p>
                  <p class="text-emerald-400 whitespace-pre-wrap break-all leading-normal">
                    {{ errorStore.details.detail }}
                  </p>
                </div>
              </div>
            </transition>
          </div>
        </div>

        <!-- Footer Actions -->
        <div class="p-6 bg-gray-50 dark:bg-dark-bg/40 border-t border-gray-100 dark:border-dark-border flex justify-end">
          <button 
            @click="close"
            class="px-8 py-3 bg-red-600 hover:bg-red-700 text-white font-extrabold text-sm rounded-2xl shadow-lg shadow-red-500/10 hover:shadow-red-500/20 transition-all hover-scale duration-150"
          >
            Schließen
          </button>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { ref } from 'vue'
import { useErrorStore } from '../stores/error'

const errorStore = useErrorStore()
const showDetails = ref(false)

function toggleDetails() {
  showDetails.value = !showDetails.value
}

function close() {
  errorStore.clearError()
  showDetails.value = false
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

/* Accordion slide animation */
.details-slide-enter-active,
.details-slide-leave-active {
  transition: max-height 0.25s ease-out, opacity 0.2s ease-out;
  max-height: 250px;
}

.details-slide-enter-from,
.details-slide-leave-to {
  max-height: 0;
  opacity: 0;
}
</style>
