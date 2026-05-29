<template>
  <transition name="fade">
    <div
      v-if="modelValue"
      class="fixed inset-0 z-[90] flex items-center justify-center bg-black/50 backdrop-blur-sm p-4"
      @click.self="close"
    >
      <div class="w-full max-w-lg rounded-2xl bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border shadow-2xl overflow-hidden animate-scale">
        
        <!-- Header -->
        <div class="px-6 py-4 border-b border-gray-200 dark:border-dark-border flex items-center justify-between">
          <h2 class="text-lg font-extrabold text-gray-900 dark:text-white flex items-center gap-2">
            ⚙️ {{ $t('apiary.manage_title') }}
          </h2>
          <button
            class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-250 cursor-pointer"
            @click="close"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <form @submit.prevent="saveApiary" class="space-y-4 p-6">
          <!-- Name Input -->
          <div>
            <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">
              {{ $t('apiary.name_label') }}
            </label>
            <input
              v-model="form.name"
              type="text"
              required
              :placeholder="$t('apiary.name_placeholder')"
              class="w-full px-4 py-2.5 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm font-medium"
            />
          </div>

          <!-- Notes Textarea -->
          <div>
            <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">
              {{ $t('apiary.notes_label') }}
            </label>
            <textarea
              v-model="form.notes"
              :placeholder="$t('apiary.notes_placeholder')"
              rows="3"
              class="w-full px-4 py-2.5 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm font-medium"
            ></textarea>
          </div>

          <!-- Status / Error message -->
          <div v-if="apiaryStore.error" class="text-xs text-red-500 font-bold bg-red-50 dark:bg-red-950/20 p-3 rounded-lg border border-red-200 dark:border-red-900/50">
            ⚠️ {{ apiaryStore.error }}
          </div>

          <!-- Footer Actions -->
          <div class="pt-4 border-t border-gray-150 dark:border-dark-border flex justify-between items-center gap-4">
            
            <!-- Danger Delete Button -->
            <button
              type="button"
              @click="confirmDelete"
              :disabled="submitting || apiaryStore.loading"
              class="px-4 py-2 text-xs font-bold uppercase tracking-wider text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/20 border border-red-200 dark:border-red-900/50 rounded-xl cursor-pointer disabled:opacity-50 transition-colors"
            >
              {{ $t('apiary.delete_btn') }} 🗑️
            </button>

            <!-- Save / Cancel Buttons -->
            <div class="flex items-center space-x-2">
              <button
                type="button"
                @click="close"
                class="px-4 py-2.5 text-xs font-bold text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 cursor-pointer"
              >
                {{ $t('common.cancel') }}
              </button>
              <button
                type="submit"
                :disabled="submitting || apiaryStore.loading || !form.name.trim()"
                class="px-5 py-2.5 bg-primary hover:bg-primary-hover text-white font-extrabold text-xs uppercase tracking-wider rounded-xl shadow-md disabled:opacity-50 hover-scale cursor-pointer flex items-center justify-center space-x-1.5"
              >
                <svg v-if="submitting || apiaryStore.loading" class="animate-spin h-3.5 w-3.5 text-white" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span>{{ $t('common.save') }}</span>
              </button>
            </div>

          </div>

        </form>

      </div>
    </div>
  </transition>
</template>

<script setup>
import { reactive, watch, ref } from 'vue'
import { useApiaryStore } from '../stores/apiary'
import { useConfirmStore } from '../stores/confirm'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:modelValue'])

const apiaryStore = useApiaryStore()
const confirmStore = useConfirmStore()
const { t } = useI18n()

const submitting = ref(false)
const form = reactive({
  name: '',
  notes: '',
})

// Prefill form when modal opens
watch(
  () => props.modelValue,
  (val) => {
    if (val && apiaryStore.activeApiary) {
      form.name = apiaryStore.activeApiary.name || ''
      form.notes = apiaryStore.activeApiary.notes || ''
      apiaryStore.error = null
    }
  }
)

function close() {
  emit('update:modelValue', false)
}

async function saveApiary() {
  if (!form.name.trim() || !apiaryStore.activeApiaryId) return
  submitting.value = true
  try {
    await apiaryStore.updateApiary(apiaryStore.activeApiaryId, form.name.trim(), form.notes.trim())
    close()
  } catch (err) {
    console.error(err)
  } finally {
    submitting.value = false
  }
}

async function confirmDelete() {
  if (!apiaryStore.activeApiaryId) return
  
  const confirmed = await confirmStore.ask({
    title: t('apiary.delete_title'),
    message: t('apiary.delete_warning'),
    type: 'danger',
    confirmText: t('apiary.delete_confirm'),
    cancelText: t('common.cancel'),
  })

  if (confirmed) {
    submitting.value = true
    try {
      await apiaryStore.deleteApiary(apiaryStore.activeApiaryId)
      close()
      // Reload page to re-render UI with new/no active apiary
      window.location.reload()
    } catch (err) {
      console.error(err)
    } finally {
      submitting.value = false
    }
  }
}
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
