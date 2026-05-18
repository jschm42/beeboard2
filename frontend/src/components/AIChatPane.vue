<template>
  <div class="flex flex-col h-full bg-white dark:bg-dark-card rounded-3xl border border-gray-200 dark:border-dark-border overflow-hidden shadow-sm">
    
    <!-- Header -->
    <div class="p-4 bg-gradient-to-r from-amber-500 to-amber-600 text-white flex justify-between items-center shrink-0">
      <div class="flex items-center space-x-2">
        <span class="text-2xl animate-bounce">🐝</span>
        <div>
          <h3 class="font-extrabold text-sm tracking-wide uppercase">Co-Imker KI-Assistent</h3>
          <p class="text-[10px] text-amber-100 font-bold">Direkt mit deinen Beuten verbunden</p>
        </div>
      </div>
      <button 
        @click="clearHistory"
        class="p-1 rounded hover:bg-white/10 text-white/80 hover:text-white transition-colors"
        title="Verlauf löschen"
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
        💬 Bienenstand Q&A
      </button>
      <button 
        @click="activeMode = 'draft'" 
        class="flex-1 py-1.5 text-center text-xs font-bold rounded-lg transition-all duration-200"
        :class="activeMode === 'draft' ? 'bg-white dark:bg-dark-border text-primary shadow-sm' : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'"
      >
        📝 Smart Auto-Entwurf
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
          <span class="text-[10px] text-gray-400 font-bold">KI analysiert Daten...</span>
        </div>
      </div>

      <!-- Chat input -->
      <form @submit.prevent="sendChat" class="p-3 border-t border-gray-100 dark:border-dark-border flex space-x-2 shrink-0 bg-gray-50/50 dark:bg-dark-card/50">
        <input 
          v-model="chatQuery" 
          type="text" 
          placeholder="z.B. Welches Volk hat den höchsten Milbenfall?"
          required
          :disabled="aiLoading"
          class="flex-grow px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-xs"
        />
        <button 
          type="submit" 
          :disabled="aiLoading"
          class="px-3 py-2 bg-primary hover:bg-primary-hover text-white rounded-xl text-xs font-bold shadow-md hover-scale shrink-0"
        >
          Senden
        </button>
      </form>
    </div>

    <!-- Mode 2: Auto-Drafting Pane -->
    <div v-else class="flex-grow flex flex-col justify-between overflow-y-auto p-4 space-y-4">
      
      <!-- Freetext input form -->
      <div class="space-y-3">
        <label class="block text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Mitschrift / gesprochener Text (Deutsch)</label>
        <textarea 
          v-model="draftText"
          rows="5"
          placeholder="Beispiel: Heute Volk 2 kontrolliert. Brut auf 4 Waben. Bienenmasse füllt die Beute gut aus. Aufgezeichnete Milben heute: 3. Zarge sieht gut aus, keine Anzeichen von Weiselzellen."
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
          <span>✨ Protokoll entwerfen</span>
        </button>
      </div>

      <!-- Generated Draft Display -->
      <div v-if="generatedDraft" class="bg-amber-500/5 dark:bg-amber-500/10 border-2 border-dashed border-amber-500/20 p-4 rounded-2xl space-y-3 relative overflow-hidden animate-scale">
        <h4 class="text-xs font-black text-amber-700 dark:text-amber-400 uppercase tracking-wider flex items-center space-x-1">
          <span>📝 KI Protokoll-Entwurf</span>
        </h4>
        
        <div class="space-y-1.5 text-xs text-gray-700 dark:text-gray-300">
          <p><span class="font-bold text-gray-400">Typ:</span> {{ getEntryTypeName(generatedDraft.entry_type) }}</p>
          <p v-if="generatedDraft.hive_name"><span class="font-bold text-gray-400">Gefundenes Volk:</span> {{ generatedDraft.hive_name }}</p>
          <p v-if="generatedDraft.date"><span class="font-bold text-gray-400">Datum:</span> {{ formatDate(generatedDraft.date) }}</p>
          <p v-if="generatedDraft.notes"><span class="font-bold text-gray-400">Notiz:</span> "{{ generatedDraft.notes }}"</p>
          
          <!-- Inspection Details preview -->
          <div v-if="generatedDraft.entry_type === 'INSPECTION' && generatedDraft.inspection_detail" class="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700/60">
            <p class="font-bold text-[10px] text-gray-400 uppercase">Wabenbelegung:</p>
            <div class="grid grid-cols-3 gap-2 mt-1 font-mono text-[10px]">
              <div class="bg-amber-500/10 text-amber-600 px-2 py-0.5 rounded text-center">Brut: {{ getInspectionSum('brood_eighths') }} W.</div>
              <div class="bg-green-500/10 text-green-600 px-2 py-0.5 rounded text-center">Bienen: {{ getInspectionSum('bee_eighths') }} W.</div>
              <div class="bg-yellow-500/10 text-yellow-600 px-2 py-0.5 rounded text-center">Futter: {{ getInspectionSum('food_eighths') }} W.</div>
            </div>
          </div>

          <!-- Varroa Count details preview -->
          <div v-if="generatedDraft.entry_type === 'VARROA_COUNT' && generatedDraft.varroa_count_detail" class="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700/60">
            <p class="font-bold text-[10px] text-gray-400 uppercase">Varroawerte:</p>
            <p class="text-[11px] font-bold">Rohwert: {{ generatedDraft.varroa_count_detail.raw_count }} Milben</p>
          </div>

          <!-- Varroa Treatment details preview -->
          <div v-if="generatedDraft.entry_type === 'VARROA_TREATMENT' && generatedDraft.varroa_treatment_detail" class="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700/60">
            <p class="font-bold text-[10px] text-gray-400 uppercase">Behandlung:</p>
            <p class="text-[11px] font-bold">{{ generatedDraft.varroa_treatment_detail.product }} (Dosierung: {{ generatedDraft.varroa_treatment_detail.dosage }})</p>
          </div>
        </div>

        <button 
          type="button" 
          @click="applyDraft"
          class="w-full py-2 bg-amber-500 hover:bg-amber-600 text-white font-extrabold text-xs uppercase tracking-wider rounded-xl shadow-sm hover-scale mt-3 flex items-center justify-center space-x-1"
        >
          <span>📥 In Protokollformular laden</span>
        </button>
      </div>

    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useApiaryStore } from '../stores/apiary'
import axios from 'axios'

const apiaryStore = useApiaryStore()

const activeMode = ref('chat') // 'chat' or 'draft'
const chatStream = ref(null)

const chatQuery = ref('')
const chatHistory = ref([])
const aiLoading = ref(false)

const draftText = ref('')
const generatedDraft = ref(null)
const draftLoading = ref(false)

const emit = defineEmits(['apply-draft'])

onMounted(() => {
  // Add initial hello message if empty
  if (chatHistory.value.length === 0) {
    chatHistory.value.push({
      role: 'assistant',
      text: 'Hallo! Ich bin dein digitaler Bienenstand-Assistent. 🐝\n\nDu kannst mich über den aktuellen Zustand deiner Bienenvölker, Standorte oder gesundheitliche Empfehlungen aus deinen Logbüchern befragen.\n\nBeispiel: "Welches Volk hat aktuell das meiste Futter?" oder "Gibt es Krankheitsanzeichen in meiner Imkerei?"',
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
      { query: userText },
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
      text: 'Entschuldigung, es gab einen Fehler bei der Bearbeitung deiner Anfrage. Ist dein LiteLLM-Dienst (z.B. Gemini Key) korrekt eingerichtet?',
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
  
  try {
    const response = await axios.post('/api/ai/draft', { text: draftText.value.trim() })
    generatedDraft.value = response.data.draft
  } catch (err) {
    console.error('AI drafting failed:', err)
    alert('Entschuldigung, das Mitschriften-Parsing ist fehlgeschlagen.')
  } finally {
    draftLoading.value = false
  }
}

function applyDraft() {
  if (!generatedDraft.value) return
  emit('apply-draft', generatedDraft.value)
  // Switch to chat or clear
  draftText.value = ''
  generatedDraft.value = null
}

function clearHistory() {
  chatHistory.value = []
  chatHistory.value.push({
    role: 'assistant',
    text: 'Verlauf gelöscht. Wie kann ich dir heute auf deinem Bienenstand helfen? 🐝',
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
    case 'INSPECTION': return '🔎 Inspektion'
    case 'VARROA_COUNT': return '🕷️ Varroazählung'
    case 'VARROA_TREATMENT': return '🧪 Varroabehandlung'
    case 'GENERAL': return '📝 Allgemeine Notiz'
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
  return d.toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' })
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
