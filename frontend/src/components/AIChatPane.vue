<template>
  <div class="flex flex-col h-full bg-white dark:bg-dark-card rounded-3xl border border-gray-200 dark:border-dark-border overflow-hidden shadow-sm">
    
    <!-- Header -->
    <div class="p-4 bg-gradient-to-r from-amber-500 to-amber-600 text-white flex justify-between items-center shrink-0">
      <div class="flex items-center space-x-2">
        <span class="text-2xl animate-bounce">🐝</span>
        <div>
          <h3 class="font-extrabold text-sm tracking-wide uppercase">{{ $t('ai_assistant.title') }}</h3>
          <p class="text-[10px] text-amber-100 font-bold">{{ $t('ai_assistant.subtitle') }}</p>
        </div>
      </div>
      <button 
        @click="clearHistory"
        class="p-1 rounded hover:bg-white/10 text-white/80 hover:text-white transition-colors"
        :title="$t('ai_assistant.clear_history')"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
      </button>
    </div>

    <!-- Mode Selector: Chat vs Auto-Drafting -->
    <div class="flex border-b border-gray-100 dark:border-dark-border bg-gray-50/50 dark:bg-dark-card/50 p-1 shrink-0">
      <button 
        @click="activeMode = 'chat'" 
        class="flex-1 py-1.5 text-center text-xs font-bold rounded-lg transition-all duration-200"
        :class="activeMode === 'chat' ? 'bg-white dark:bg-dark-border text-primary shadow-sm' : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'"
      >
        {{ $t('ai_assistant.tab_qa') }}
      </button>
      <button 
        @click="activeMode = 'draft'" 
        class="flex-1 py-1.5 text-center text-xs font-bold rounded-lg transition-all duration-200"
        :class="activeMode === 'draft' ? 'bg-white dark:bg-dark-border text-primary shadow-sm' : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'"
      >
        {{ $t('ai_assistant.tab_draft') }}
      </button>
    </div>

    <!-- Mode 1: Chat pane -->
    <div v-if="activeMode === 'chat'" class="flex-grow flex flex-col justify-between overflow-hidden min-h-0">
      <!-- Chat history stream -->
      <div 
        ref="chatStream"
        class="flex-grow overflow-y-auto p-4 space-y-4 min-h-0"
      >
        <div 
          v-for="(msg, index) in chatHistory" 
          :key="index"
          class="flex flex-col max-w-[85%] rounded-2xl p-3 text-xs leading-relaxed"
          :class="[
            msg.role === 'user'
              ? 'bg-primary text-white ml-auto rounded-tr-none'
              : 'bg-gray-100 dark:bg-dark-bg text-gray-800 dark:text-gray-200 mr-auto rounded-tl-none border border-gray-200 dark:border-gray-800'
          ]"
        >
          <!-- Message text with formatting -->
          <div class="whitespace-pre-line font-medium">{{ msg.text }}</div>
          <span class="text-[8px] mt-1 text-right opacity-60 font-bold block">{{ msg.time }}</span>
        </div>

        <div v-if="aiLoading" class="flex items-center space-x-2 bg-gray-100 dark:bg-dark-bg border border-gray-200 dark:border-gray-800 mr-auto rounded-2xl rounded-tl-none p-3 max-w-[85%]">
          <svg class="animate-spin h-4 w-4 text-primary shrink-0" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
          <span class="text-[10px] text-gray-400 font-bold">{{ $t('ai_assistant.analyzing') }}</span>
        </div>
      </div>

      <!-- Chat input -->
      <form @submit.prevent="sendChat" class="p-3 border-t border-gray-100 dark:border-dark-border flex space-x-2 shrink-0 bg-gray-50/50 dark:bg-dark-card/50">
        <input 
          v-model="chatQuery" 
          type="text" 
          :placeholder="$t('ai_assistant.placeholder_qa')"
          required
          :disabled="aiLoading"
          class="flex-grow px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-xs"
        />
        <button 
          type="submit" 
          :disabled="aiLoading"
          class="px-3 py-2 bg-primary hover:bg-primary-hover text-white rounded-xl text-xs font-bold shadow-md hover-scale shrink-0"
        >
          {{ $t('ai_assistant.btn_send') }}
        </button>
      </form>
    </div>

    <!-- Mode 2: Auto-Drafting Pane -->
    <div v-else class="flex-grow flex flex-col justify-between overflow-y-auto p-4 space-y-4">
      
      <!-- Freetext input form -->
      <div class="space-y-3">
        <label class="block text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider">{{ $t('ai_assistant.freetext_label') }}</label>
        <textarea 
          v-model="draftText"
          rows="5"
          :placeholder="$t('ai_assistant.placeholder_draft')"
          class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-2xl focus:outline-none focus:ring-2 focus:ring-primary text-xs"
        ></textarea>
        
        <button 
          type="button" 
          @click="generateDraft"
          :disabled="draftLoading || !draftText.trim()"
          class="w-full py-2.5 bg-primary hover:bg-primary-hover text-white font-extrabold text-xs uppercase tracking-wider rounded-xl shadow-md hover-scale flex items-center justify-center space-x-2"
        >
          <span v-if="draftLoading">
            <svg class="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
          </span>
          <span>{{ $t('ai_assistant.btn_draft') }}</span>
        </button>
      </div>

      <!-- Generated Draft Display -->
      <div v-if="generatedDraft" class="bg-amber-500/5 dark:bg-amber-500/10 border-2 border-dashed border-amber-500/20 p-4 rounded-2xl space-y-3 relative overflow-hidden animate-scale">
        <h4 class="text-xs font-black text-amber-700 dark:text-amber-400 uppercase tracking-wider flex items-center space-x-1">
          <span>{{ isHoneyDraft ? $t('ai_assistant.draft_honey_title') : $t('ai_assistant.draft_inspection_title') }}</span>
        </h4>
        
        <div v-if="isHoneyDraft" class="space-y-1.5 text-xs text-gray-700 dark:text-gray-300">
          <p><span class="font-bold text-gray-400">{{ $t('ai_assistant.honey_type') }}:</span> {{ generatedDraft.honey_type || 'Blütenhonig' }}</p>
          <p v-if="generatedDraft.quantity_kg"><span class="font-bold text-gray-400">{{ $t('ai_assistant.quantity') }}:</span> {{ generatedDraft.quantity_kg }} kg</p>
          <p v-if="generatedDraft.water_content_percent"><span class="font-bold text-gray-400">{{ $t('ai_assistant.water_content') }}:</span> {{ generatedDraft.water_content_percent }} %</p>
          <p v-if="generatedDraft.harvest_date"><span class="font-bold text-gray-400">{{ $t('ai_assistant.harvest') }}:</span> {{ formatDate(generatedDraft.harvest_date) }}</p>
          <p v-if="generatedDraft.dib_label_start || generatedDraft.dib_label_end">
            <span class="font-bold text-gray-400">{{ $t('ai_assistant.dib_numbers') }}:</span> {{ generatedDraft.dib_label_start || '?' }} bis {{ generatedDraft.dib_label_end || '?' }}
          </p>
          <p v-if="generatedDraft.reserve_sample_taken">
            <span class="font-bold text-gray-400">{{ $t('ai_assistant.reserve_sample') }}:</span> {{ $t('ai_assistant.reserve_sample_yes') }} ({{ generatedDraft.reserve_sample_id || $t('ai_assistant.unspecified') }})
          </p>
          <p v-if="generatedDraft.notes"><span class="font-bold text-gray-400">{{ $t('ai_assistant.notes') }}:</span> "{{ generatedDraft.notes }}"</p>
        </div>

        <div v-else class="space-y-1.5 text-xs text-gray-700 dark:text-gray-300">
          <p><span class="font-bold text-gray-400">{{ $t('ai_assistant.type') }}:</span> {{ getEntryTypeName(generatedDraft.entry_type) }}</p>
          <p v-if="generatedDraft.hive_name"><span class="font-bold text-gray-400">{{ $t('ai_assistant.found_hive') }}:</span> {{ generatedDraft.hive_name }}</p>
          <p v-if="generatedDraft.date"><span class="font-bold text-gray-400">{{ $t('ai_assistant.date') }}:</span> {{ formatDate(generatedDraft.date) }}</p>
          <p v-if="generatedDraft.notes"><span class="font-bold text-gray-400">{{ $t('ai_assistant.notes') }}:</span> "{{ generatedDraft.notes }}"</p>
          
          <!-- Inspection Details preview -->
          <div v-if="generatedDraft.entry_type === 'INSPECTION' && generatedDraft.inspection_detail" class="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700/60">
            <p class="font-bold text-[10px] text-gray-400 uppercase">{{ $t('ai_assistant.inspection_sum') }}:</p>
            <div class="grid grid-cols-3 gap-2 mt-1 font-mono text-[10px]">
              <div class="bg-amber-500/10 text-amber-600 px-2 py-0.5 rounded text-center">{{ $t('ai_assistant.brood') }}: {{ getInspectionSum('brood_eighths') }} W.</div>
              <div class="bg-green-500/10 text-green-600 px-2 py-0.5 rounded text-center">{{ $t('ai_assistant.bees') }}: {{ getInspectionSum('bee_eighths') }} W.</div>
              <div class="bg-yellow-500/10 text-yellow-600 px-2 py-0.5 rounded text-center">{{ $t('ai_assistant.food') }}: {{ getInspectionSum('food_eighths') }} W.</div>
            </div>
          </div>

          <!-- Varroa Count details preview -->
          <div v-if="generatedDraft.entry_type === 'VARROA_COUNT' && generatedDraft.varroa_count_detail" class="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700/60">
            <p class="font-bold text-[10px] text-gray-400 uppercase">{{ $t('ai_assistant.varroa_values') }}:</p>
            <p class="text-[11px] font-bold">{{ $t('ai_assistant.raw_value') }}: {{ generatedDraft.varroa_count_detail.raw_count }} {{ $t('ai_assistant.mites') }}</p>
          </div>

          <!-- Varroa Treatment details preview -->
          <div v-if="generatedDraft.entry_type === 'VARROA_TREATMENT' && generatedDraft.varroa_treatment_detail" class="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700/60">
            <p class="font-bold text-[10px] text-gray-400 uppercase">{{ $t('ai_assistant.treatment') }}:</p>
            <p class="text-[11px] font-bold">{{ generatedDraft.varroa_treatment_detail.product }} ({{ $t('ai_assistant.dosage') }}: {{ generatedDraft.varroa_treatment_detail.dosage }})</p>
          </div>
        </div>

        <button 
          type="button" 
          @click="applyDraft"
          class="w-full py-2 bg-amber-500 hover:bg-amber-600 text-white font-extrabold text-xs uppercase tracking-wider rounded-xl shadow-sm hover-scale mt-3 flex items-center justify-center space-x-1"
        >
          <span>{{ isHoneyDraft ? $t('ai_assistant.btn_apply_honey') : $t('ai_assistant.btn_apply_form') }}</span>
        </button>
      </div>

    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useApiaryStore } from '../stores/apiary'
import { useErrorStore } from '../stores/error'
import axios from 'axios'

const { t, locale } = useI18n()
const apiaryStore = useApiaryStore()
const errorStore = useErrorStore()
const router = useRouter()

const activeMode = ref('chat') // 'chat' or 'draft'
const chatStream = ref(null)

const chatQuery = ref('')
const chatHistory = ref([])
const aiLoading = ref(false)

const draftText = ref('')
const generatedDraft = ref(null)
const draftLoading = ref(false)
const isHoneyDraft = ref(false)

const emit = defineEmits(['apply-draft'])

onMounted(() => {
  // Add initial hello message if empty
  if (chatHistory.value.length === 0) {
    chatHistory.value.push({
      role: 'assistant',
      text: t('ai_assistant.welcome_msg'),
      time: new Date().toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' })
    })
  }
})

async function sendChat() {
  if (!chatQuery.value.trim() || aiLoading.value) return
  
  const userText = chatQuery.value.trim()
  chatQuery.value = ''
  
  chatHistory.value.push({
    role: 'user',
    text: userText,
    time: new Date().toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' })
  })
  
  scrollToBottom()
  aiLoading.value = true

  try {
    const response = await axios.post('/api/ai/chat', 
      { query: userText, lang: locale.value },
      { params: { apiary_id: apiaryStore.activeApiaryId } }
    )

    chatHistory.value.push({
      role: 'assistant',
      text: response.data.response,
      time: new Date().toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' })
    })
  } catch (err) {
    console.error('AI chat failed:', err)
    chatHistory.value.push({
      role: 'assistant',
      text: t('ai_assistant.error_msg'),
      time: new Date().toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' })
    })
  } finally {
    aiLoading.value = false
    scrollToBottom()
  }
}

async function generateDraft() {
  if (!draftText.value.trim() || draftLoading.value) return
  
  draftLoading.value = true
  generatedDraft.value = null
  isHoneyDraft.value = false
  
  const text = draftText.value.toLowerCase()
  const isHoney = text.includes('honig') || text.includes('ernte') || text.includes('geerntet') || text.includes('wasser') || text.includes('banderole') || text.includes('schleudern') || text.includes('abgefüllt') || text.includes('charge')
  
  try {
    if (isHoney) {
      const response = await axios.post('/api/ai/draft-honey', { text: draftText.value.trim(), lang: locale.value })
      generatedDraft.value = response.data.draft
      isHoneyDraft.value = true
    } else {
      const response = await axios.post('/api/ai/draft', { text: draftText.value.trim(), lang: locale.value })
      generatedDraft.value = response.data.draft
      isHoneyDraft.value = false
    }
  } catch (err) {
    errorStore.showError(t('ai_assistant.error_parsing_failed'), err, t('ai_assistant.error_parsing_failed_title'))
  } finally {
    draftLoading.value = false
  }
}

function applyDraft() {
  if (!generatedDraft.value) return
  if (isHoneyDraft.value) {
    sessionStorage.setItem('pending_honey_draft', JSON.stringify(generatedDraft.value))
    router.push('/honey-batches')
  } else {
    emit('apply-draft', generatedDraft.value)
  }
  // Switch to chat or clear
  draftText.value = ''
  generatedDraft.value = null
  isHoneyDraft.value = false
}

function clearHistory() {
  chatHistory.value = []
  chatHistory.value.push({
    role: 'assistant',
    text: t('ai_assistant.history_cleared'),
    time: new Date().toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' })
  })
}

async function scrollToBottom() {
  await nextTick()
  if (chatStream.value) {
    chatStream.value.scrollTop = chatStream.value.scrollHeight
  }
}

// Helpers
function getEntryTypeName(type) {
  switch (type) {
    case 'INSPECTION': return '🔎 ' + t('inspection.type_inspection')
    case 'VARROA_COUNT': return '🕷️ ' + t('inspection.type_varroa_count')
    case 'VARROA_TREATMENT': return '🧪 ' + t('inspection.type_varroa_treatment')
    case 'GENERAL': return '📝 ' + t('inspection.type_general')
    default: return type
  }
}

function getInspectionSum(field) {
  if (!generatedDraft.value?.inspection_detail?.frames) return 0
  const sum = generatedDraft.value.inspection_detail.frames.reduce((acc, frame) => {
    return acc + (frame[field] || 0)
  }, 0)
  return (sum / 8).toFixed(1)
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString(locale.value === 'de' ? 'de-DE' : 'en-US', { day: '2-digit', month: '2-digit', year: 'numeric' })
}
</script>

<style scoped>
.animate-scale {
  animation: scaleUp 0.2s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

@keyframes scaleUp {
  from {
    transform: scale(0.95);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}
</style>
