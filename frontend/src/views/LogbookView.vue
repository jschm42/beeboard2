<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 font-sans">
    
    <!-- Back to Dashboard Link -->
    <router-link to="/dashboard" class="inline-flex items-center text-sm font-semibold text-primary hover:text-primary-hover mb-4 transition-colors duration-200">
      <svg class="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"/></svg>
      Zurück zum Dashboard
    </router-link>

    <!-- Header -->
    <div class="mb-8 flex flex-col sm:flex-row sm:justify-between sm:items-center space-y-4 sm:space-y-0">
      <div>
        <h1 class="text-3xl font-extrabold text-gray-900 dark:text-white tracking-tight">📓 Imker-Logbuch</h1>
        <p class="text-gray-500 dark:text-gray-400 mt-1">Erfasse Beutenkontrollen, Varroamessungen und Behandlungen.</p>
      </div>
      <button 
        @click="openCreateSessionModal" 
        class="px-5 py-2.5 bg-primary hover:bg-primary-hover text-white font-extrabold text-sm rounded-xl shadow-md shadow-primary/20 hover-scale flex items-center justify-center space-x-2"
      >
        <span>+ Neue Arbeitssitzung</span>
      </button>
    </div>

    <!-- Active Apiary check -->
    <div v-if="!apiaryStore.activeApiaryId" class="glass rounded-3xl p-12 text-center max-w-lg mx-auto border border-dashed border-gray-300 dark:border-gray-700">
      <div class="text-4xl mb-4">📓</div>
      <h3 class="text-lg font-bold text-gray-800 dark:text-white mb-2">Keine aktive Imkerei ausgewählt</h3>
      <p class="text-gray-500 dark:text-gray-400">Bitte wähle oben eine Imkerei aus, um auf das Logbuch zuzugreifen.</p>
    </div>

    <div v-else class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
      
      <!-- Left Panel: Session Stream (4 cols) -->
      <div class="lg:col-span-4 space-y-4">
        <h3 class="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider px-1">Sitzungen (Arbeitstage)</h3>
        
        <!-- Inline Create Session Card -->
        <div v-if="showSessionModal" class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-2xl p-4 shadow-md space-y-4 animate-scale mb-4">
          <div class="flex justify-between items-center pb-2 border-b border-gray-100 dark:border-dark-border">
            <h4 class="font-extrabold text-sm text-gray-900 dark:text-white">Neue Arbeitssitzung</h4>
            <button @click="showSessionModal = false" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200">
              <svg class="w-4.5 h-4.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
            </button>
          </div>
          <form @submit.prevent="submitSessionForm" class="space-y-3">
            <div>
              <label class="block text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Bezeichnung *</label>
              <input 
                v-model="sessionForm.title" 
                type="text" 
                required
                placeholder="z.B. Honigraum aufsetzen & Varroakontrolle"
                class="w-full px-3 py-1.5 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-xs"
              />
            </div>
            <div>
              <label class="block text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Bienenvolk (Optional)</label>
              <select 
                v-model="sessionForm.hiveId" 
                class="w-full px-3 py-1.5 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-xs"
              >
                <option value="">Keines (Global für Imkerei)</option>
                <option v-for="hive in hives" :key="hive.id" :value="hive.id">
                  {{ hive.name }}
                </option>
              </select>
            </div>
            <div class="flex justify-end space-x-2 pt-2">
              <button type="button" @click="showSessionModal = false" class="px-3 py-1.5 text-xs font-bold text-gray-500 hover:text-gray-700 dark:hover:text-gray-300">Abbrechen</button>
              <button type="submit" class="px-4 py-1.5 bg-primary hover:bg-primary-hover text-white font-extrabold text-xs rounded-xl shadow-md">Erstellen</button>
            </div>
          </form>
        </div>

        <div v-if="sessionsLoading" class="flex justify-center py-10 bg-white dark:bg-dark-card rounded-3xl border border-gray-200 dark:border-dark-border">
          <svg class="animate-spin h-6 w-6 text-primary" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
        </div>

        <div v-else-if="sessions.length === 0" class="bg-white dark:bg-dark-card border rounded-3xl p-8 text-center text-gray-400 italic text-xs">
          Keine Arbeitssitzungen angelegt. Beginne mit "+ Neue Arbeitssitzung".
        </div>

        <div 
          v-else
          v-for="session in sessions" 
          :key="session.id"
          @click="selectSession(session)"
          class="bg-white dark:bg-dark-card border rounded-2xl p-4 shadow-sm cursor-pointer transition-all duration-200 flex items-center justify-between"
          :class="[
            selectedSession?.id === session.id 
              ? 'border-primary ring-2 ring-primary/20 shadow-md scale-[1.01]' 
              : 'border-gray-200 dark:border-dark-border hover:border-primary/50'
          ]"
        >
          <div class="min-w-0">
            <h4 class="font-extrabold text-sm text-gray-900 dark:text-white truncate">
              {{ session.title }}
            </h4>
            <p class="text-[10px] text-gray-400 mt-1 font-mono">
              Aktualisiert: {{ formatDateTime(session.updated_at) }}
            </p>
            <span 
              v-if="session.hive" 
              class="inline-block mt-2 px-2 py-0.5 bg-amber-500/10 text-primary text-[9px] font-bold rounded"
            >
              Volk: {{ session.hive.name }}
            </span>
          </div>

          <button 
            @click.stop="deleteSession(session)"
            class="p-2 text-gray-400 hover:text-red-500 hover:bg-red-500/10 rounded-xl transition-all"
            title="Sitzung löschen"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
          </button>
        </div>

      </div>

      <!-- Right Panel: Dynamic Tabs - Entries vs AI assistant (8 cols) -->
      <div class="lg:col-span-8">
        
        <div v-if="!selectedSession" class="bg-gray-50 dark:bg-dark-card/20 border border-dashed border-gray-300 dark:border-gray-700 rounded-3xl p-12 text-center text-gray-400 italic text-sm">
          Wähle links eine Arbeitssitzung aus, um die Protokoll-Einträge anzuzeigen oder den KI-Assistenten zu nutzen.
        </div>

        <div v-else class="space-y-6">
          
          <!-- Splitscreen top bar: Tabs -->
          <div class="flex justify-between items-center bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border px-4 py-2 rounded-2xl shadow-sm">
            <div class="flex space-x-1">
              <button 
                @click="rightTab = 'entries'" 
                class="px-4 py-2 text-xs font-black uppercase tracking-wider rounded-lg transition-all"
                :class="rightTab === 'entries' ? 'bg-primary text-white shadow-sm' : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'"
              >
                📝 Einträge & Fotos
              </button>
              <button 
                @click="rightTab = 'ai'" 
                class="px-4 py-2 text-xs font-black uppercase tracking-wider rounded-lg transition-all"
                :class="rightTab === 'ai' ? 'bg-primary text-white shadow-sm' : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'"
              >
                🤖 Co-Imker KI
              </button>
            </div>
            
            <button 
              v-if="rightTab === 'entries'"
              @click="openCreateEntryModal" 
              class="px-3.5 py-1.5 bg-primary hover:bg-primary-hover text-white font-extrabold text-[11px] uppercase tracking-wider rounded-xl shadow-md hover-scale"
            >
              + Neuer Eintrag
            </button>
          </div>

          <!-- TAB 1: LOG ENTRIES -->
          <div v-if="rightTab === 'entries'" class="space-y-4">
            
            <!-- Inline Create/Edit Log Entry Form -->
            <div v-if="showEntryModal" class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl shadow-md p-6 mb-6 animate-scale">
              <div class="flex justify-between items-center mb-6 pb-4 border-b border-gray-100 dark:border-dark-border">
                <h3 class="text-xl font-bold text-gray-900 dark:text-white">
                  {{ isEditEntryMode ? '📝 Protokolleintrag bearbeiten' : '📝 Neuer Protokolleintrag' }}
                </h3>
                <button @click="showEntryModal = false" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
                </button>
              </div>
              
              <form @submit.prevent="submitEntryForm" class="space-y-4">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">Bienenvolk *</label>
                    <select 
                      v-model="entryForm.hiveId" 
                      required
                      @change="onHiveSelected"
                      class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm cursor-pointer"
                    >
                      <option value="" disabled>Bitte Volk wählen...</option>
                      <option v-for="hive in hives" :key="hive.id" :value="hive.id">
                        {{ hive.name }}
                      </option>
                    </select>
                  </div>
                  <div>
                    <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">Datum *</label>
                    <input 
                      v-model="entryForm.date" 
                      type="date" 
                      required
                      class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm"
                    />
                  </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">Eintrags-Typ *</label>
                    <select 
                      v-model="entryForm.entryType" 
                      required
                      :disabled="isEditEntryMode"
                      class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm cursor-pointer"
                    >
                      <option value="INSPECTION">🔎 Beuteninspektion</option>
                      <option value="VARROA_COUNT">🕷️ Varroazählung (Windel)</option>
                      <option value="VARROA_TREATMENT">🧪 Varroabehandlung</option>
                      <option value="GENERAL">📝 Allgemeine Notiz</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">Notizen (Zustand, Brutwaben etc.)</label>
                  <textarea 
                    v-model="entryForm.notes" 
                    placeholder="Sanftmütiges Verhalten, Stifte vorhanden, Königin gesichtet..."
                    rows="2"
                    class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm"
                  ></textarea>
                </div>

                <!-- SUB-FORM: INSPECTION DETAILS -->
                <div v-if="entryForm.entryType === 'INSPECTION'" class="space-y-3 border-t border-gray-100 dark:border-dark-border pt-4">
                  <h4 class="text-xs font-extrabold uppercase text-gray-500 tracking-wider">Brut- und Belegungsbeurteilung pro Wabe</h4>
                  
                  <div class="max-h-60 overflow-y-auto space-y-2 border border-gray-200 dark:border-gray-800 rounded-2xl p-3">
                    <div 
                      v-for="(frame, index) in entryForm.inspectionDetail.frames" 
                      :key="index"
                      class="p-3 bg-gray-50 dark:bg-dark-bg/60 border border-gray-100 dark:border-gray-800 rounded-xl flex items-center justify-between space-x-4 text-xs font-bold"
                    >
                      <span class="w-16">Wabe #{{ frame.frame_number }}</span>
                      <div class="flex items-center space-x-3 flex-grow justify-end">
                        <div class="flex flex-col items-center">
                          <span class="text-[9px] text-amber-500 font-bold uppercase">Brut</span>
                          <input 
                            v-model.number="frame.brood_eighths" 
                            type="number" 
                            min="0" 
                            max="8" 
                            class="w-12 px-1 py-0.5 border border-gray-300 dark:border-gray-700 dark:bg-dark-card rounded text-center"
                          />
                        </div>
                        <div class="flex flex-col items-center">
                          <span class="text-[9px] text-green-500 font-bold uppercase">Bienen</span>
                          <input 
                            v-model.number="frame.bee_eighths" 
                            type="number" 
                            min="0" 
                            max="8" 
                            class="w-12 px-1 py-0.5 border border-gray-300 dark:border-gray-700 dark:bg-dark-card rounded text-center"
                          />
                        </div>
                        <div class="flex flex-col items-center">
                          <span class="text-[9px] text-yellow-500 font-bold uppercase">Futter</span>
                          <input 
                            v-model.number="frame.food_eighths" 
                            type="number" 
                            min="0" 
                            max="8" 
                            class="w-12 px-1 py-0.5 border border-gray-300 dark:border-gray-700 dark:bg-dark-card rounded text-center"
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- SUB-FORM: VARROA COUNT DETAILS -->
                <div v-if="entryForm.entryType === 'VARROA_COUNT'" class="space-y-3 border-t border-gray-100 dark:border-dark-border pt-4">
                  <h4 class="text-xs font-extrabold uppercase text-gray-500 tracking-wider">Windel-Messergebnis</h4>
                  <div>
                    <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 mb-1">Gezählte Milben (Rohwert auf der Windel) *</label>
                    <input 
                      v-model.number="entryForm.varroaCountDetail.rawCount" 
                      type="number" 
                      required
                      min="0"
                      class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm"
                    />
                    <p class="text-[10px] text-gray-400 mt-1 italic">Unser Berechnungs-Service korrigiert den Milbenfall automatisch anhand saisonaler Multiplikatoren.</p>
                  </div>
                </div>

                <!-- SUB-FORM: VARROA TREATMENT DETAILS -->
                <div v-if="entryForm.entryType === 'VARROA_TREATMENT'" class="space-y-3 border-t border-gray-100 dark:border-dark-border pt-4">
                  <h4 class="text-xs font-extrabold uppercase text-gray-500 tracking-wider">Behandlungsmethode</h4>
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 mb-1">Produkt (z.B. Ameisensäure, Oxalsäure) *</label>
                      <input 
                        v-model="entryForm.varroaTreatmentDetail.product" 
                        type="text" 
                        required
                        placeholder="z.B. Ameisensäure 60%"
                        class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm"
                      />
                    </div>
                    <div>
                      <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 mb-1">Dosierung (z.B. 50ml, Verdampfung) *</label>
                      <input 
                        v-model="entryForm.varroaTreatmentDetail.dosage" 
                        type="text" 
                        required
                        placeholder="z.B. 50ml Nassenheider"
                        class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm"
                      />
                    </div>
                  </div>
                  <div>
                    <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 mb-1">Spezifische Anmerkungen zur Behandlung</label>
                    <textarea 
                      v-model="entryForm.varroaTreatmentDetail.treatmentNotes" 
                      placeholder="Verdunstung über 10 Tage, Außentemperatur ca. 22°C..."
                      rows="2"
                      class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm"
                    ></textarea>
                  </div>
                </div>

                <div class="flex justify-end space-x-3 mt-6 border-t border-gray-100 dark:border-dark-border pt-4">
                  <button type="button" @click="showEntryModal = false" class="px-4 py-2 text-sm font-bold text-gray-500 hover:text-gray-700 dark:hover:text-gray-300">Abbrechen</button>
                  <button type="submit" class="px-5 py-2.5 bg-primary hover:bg-primary-hover text-white font-extrabold text-sm rounded-xl shadow-md">Speichern</button>
                </div>
              </form>
            </div>

            <div v-if="entriesLoading" class="flex justify-center py-20 bg-white dark:bg-dark-card rounded-3xl border border-gray-200 dark:border-dark-border">
              <svg class="animate-spin h-10 w-10 text-primary" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
            </div>

            <div v-else-if="entries.length === 0" class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-12 text-center text-gray-400 italic text-xs">
              Noch keine Logbucheinträge in dieser Sitzung erfasst.
            </div>

            <!-- List entries -->
            <div 
              v-else
              v-for="entry in entries" 
              :key="entry.id"
              class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-6 shadow-sm space-y-4 relative overflow-hidden"
            >
              <!-- Top bar info -->
              <div class="flex justify-between items-start border-b border-gray-100 dark:border-dark-border pb-3">
                <div>
                  <div class="flex items-center space-x-2">
                    <span class="text-sm font-black text-gray-900 dark:text-white">{{ entry.hive?.name || 'Unbekanntes Volk' }}</span>
                    <span class="text-[10px] text-gray-400 uppercase font-mono">Date: {{ formatDate(entry.date) }}</span>
                  </div>
                  <div class="flex items-center space-x-2 mt-1">
                    <span class="px-2 py-0.5 text-[9px] font-black uppercase rounded tracking-wider bg-gray-100 dark:bg-dark-bg text-gray-500">
                      {{ getEntryTypeName(entry.entry_type) }}
                    </span>
                  </div>
                </div>

                <div class="flex space-x-1">
                  <button 
                    @click="openEditEntryModal(entry)" 
                    class="p-1.5 text-gray-400 hover:text-primary rounded hover:bg-gray-50 dark:hover:bg-dark-bg transition-colors"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/></svg>
                  </button>
                  <button 
                    @click="deleteEntry(entry)" 
                    class="p-1.5 text-gray-400 hover:text-red-500 rounded hover:bg-red-500/10 transition-colors"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                  </button>
                </div>
              </div>

              <!-- Notes -->
              <p class="text-xs text-gray-700 dark:text-gray-300 leading-relaxed bg-gray-50 dark:bg-dark-bg/60 p-3 rounded-2xl border italic">
                "{{ entry.notes || 'Keine Anmerkungen erfasst.' }}"
              </p>

              <!-- Nested Inspection details -->
              <div v-if="entry.entry_type === 'INSPECTION' && entry.inspection_detail" class="space-y-3">
                <p class="text-[10px] font-black uppercase text-gray-400 tracking-wider">🔎 Brut- und Raumbelegung (Brutraum/Honigraum)</p>
                <div class="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-3">
                  <div 
                    v-for="frame in sortedFrames(entry.inspection_detail.frames)" 
                    :key="frame.id"
                    class="p-2.5 bg-gray-50 dark:bg-dark-bg/60 border border-gray-100 dark:border-gray-800 rounded-xl flex flex-col justify-center items-center shadow-sm"
                  >
                    <span class="text-[10px] font-black text-gray-500 mb-1.5">Wabe #{{ frame.frame_number }}</span>
                    <!-- HSL progress bar indicators -->
                    <div class="w-full space-y-1 text-[9px] font-mono font-bold">
                      <div class="flex justify-between items-center text-amber-500">
                        <span>Brut:</span>
                        <span>{{ frame.brood_eighths }}/8</span>
                      </div>
                      <div class="flex justify-between items-center text-green-500">
                        <span>Biene:</span>
                        <span>{{ frame.bee_eighths }}/8</span>
                      </div>
                      <div class="flex justify-between items-center text-yellow-500">
                        <span>Futter:</span>
                        <span>{{ frame.food_eighths }}/8</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Nested Varroa counts -->
              <div v-if="entry.entry_type === 'VARROA_COUNT' && entry.varroa_count_detail" class="grid grid-cols-2 gap-4 p-4 bg-red-500/5 dark:bg-red-500/10 border border-red-500/10 rounded-2xl">
                <div>
                  <span class="text-[9px] font-bold text-gray-400 uppercase">Gemessene Milben (Rohwert)</span>
                  <p class="text-xl font-black text-gray-800 dark:text-gray-100 mt-1">{{ entry.varroa_count_detail.raw_count }} Milben</p>
                </div>
                <div>
                  <span class="text-[9px] font-bold text-gray-400 uppercase">Saisonbereinigter Milbenfall / Tag</span>
                  <p class="text-xl font-black text-red-500 mt-1">~{{ entry.varroa_count_detail.estimated_total.toFixed(1) }} / Tag</p>
                </div>
              </div>

              <!-- Nested Varroa treatments -->
              <div v-if="entry.entry_type === 'VARROA_TREATMENT' && entry.varroa_treatment_detail" class="p-4 bg-green-500/5 dark:bg-green-500/10 border border-green-500/10 rounded-2xl space-y-1">
                <span class="text-[9px] font-bold text-gray-400 uppercase">Varroabehandlung eingetragen</span>
                <p class="text-sm font-bold text-green-600 dark:text-green-400">Produkt: {{ entry.varroa_treatment_detail.product }}</p>
                <p class="text-xs font-bold mt-1 text-gray-600 dark:text-gray-400">Dosierung: {{ entry.varroa_treatment_detail.dosage }}</p>
                <p v-if="entry.varroa_treatment_detail.treatment_notes" class="text-xs text-gray-400 italic mt-1">"{{ entry.varroa_treatment_detail.treatment_notes }}"</p>
              </div>

              <!-- Images stream & upload gallery -->
              <div class="space-y-2 border-t border-gray-100 dark:border-dark-border pt-4">
                <div class="flex justify-between items-center">
                  <span class="text-[10px] font-black uppercase text-gray-400">🖼️ Bilder-Galerie ({{ entry.images?.length || 0 }} / 5)</span>
                  
                  <input 
                    v-if="entry.images?.length < 5"
                    type="file" 
                    :id="`file-upload-${entry.id}`" 
                    @change="uploadEntryImage($event, entry.id)" 
                    accept="image/*" 
                    class="hidden"
                  />
                  <label 
                    v-if="entry.images?.length < 5"
                    :for="`file-upload-${entry.id}`"
                    class="text-[10px] font-bold text-primary hover:text-primary-hover hover:underline cursor-pointer uppercase"
                  >
                    + Bild hinzufügen
                  </label>
                </div>

                <!-- Gallery Grid -->
                <div v-if="entry.images && entry.images.length > 0" class="grid grid-cols-3 sm:grid-cols-5 gap-3">
                  <div 
                    v-for="img in entry.images" 
                    :key="img.id"
                    class="relative group rounded-xl overflow-hidden aspect-square border border-gray-200 dark:border-gray-800"
                  >
                    <img 
                      :src="`/uploads/${img.thumbnail_path || img.image_path}`" 
                      alt="Thumbnail" 
                      @click="openLightbox(`/uploads/${img.image_path}`)"
                      class="w-full h-full object-cover cursor-pointer group-hover:scale-105 transition-transform duration-200"
                    />
                    <button 
                      @click="deleteEntryImage(img.id)"
                      class="absolute top-1 right-1 p-1 bg-red-500 text-white rounded-lg shadow opacity-0 group-hover:opacity-100 transition-opacity duration-150"
                      title="Bild löschen"
                    >
                      <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                    </button>
                  </div>
                </div>
              </div>

            </div>

          </div>

          <!-- TAB 2: AI CO-IMKER -->
          <div v-else class="h-[600px]">
            <AIChatPane @apply-draft="onApplyDraft" />
          </div>

        </div>
      </div>
    </div>

    <!-- Image Lightbox Modal -->
    <div v-if="lightboxImage" class="fixed inset-0 z-50 flex items-center justify-center bg-black/90 p-4" @click="closeLightbox">
      <div class="relative max-w-4xl max-h-screen">
        <img :src="lightboxImage" class="max-w-full max-h-[85vh] rounded-2xl shadow-2xl border border-white/10" alt="Full screen preview" />
        <button 
          @click="closeLightbox" 
          class="absolute top-4 right-4 p-2 bg-white/20 hover:bg-white/40 text-white rounded-full transition-colors"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
        </button>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { useApiaryStore } from '../stores/apiary'
import { useErrorStore } from '../stores/error'
import AIChatPane from '../components/AIChatPane.vue'
import axios from 'axios'

const apiaryStore = useApiaryStore()
const errorStore = useErrorStore()

const sessions = ref([])
const hives = ref([])
const entries = ref([])

const sessionsLoading = ref(false)
const entriesLoading = ref(false)

const selectedSession = ref(null)
const rightTab = ref('entries') // 'entries' or 'ai'
const lightboxImage = ref(null)

// Modals toggles
const showSessionModal = ref(false)
const showEntryModal = ref(false)
const isEditEntryMode = ref(false)
const editingEntryId = ref(null)

const sessionForm = reactive({
  title: '',
  hiveId: ''
})

const entryForm = reactive({
  hiveId: '',
  date: new Date().toISOString().substring(0, 10),
  entryType: 'INSPECTION',
  notes: '',
  inspectionDetail: {
    frames: []
  },
  varroaCountDetail: {
    rawCount: 0
  },
  varroaTreatmentDetail: {
    product: '',
    dosage: '',
    treatmentNotes: ''
  }
})

onMounted(async () => {
  if (apiaryStore.activeApiaryId) {
    await Promise.all([
      fetchSessions(),
      fetchHives()
    ])
  }
})

async function fetchSessions() {
  sessionsLoading.value = true
  try {
    const response = await axios.get('/api/logbook/sessions', {
      params: { apiary_id: apiaryStore.activeApiaryId }
    })
    sessions.value = response.data
    
    // Auto-select first session if none selected
    if (sessions.value.length > 0 && !selectedSession.value) {
      selectSession(sessions.value[0])
    }
  } catch (err) {
    console.error('Fetch sessions failed:', err)
  } finally {
    sessionsLoading.value = false
  }
}

async function fetchHives() {
  try {
    const response = await axios.get('/api/hives', {
      params: { apiary_id: apiaryStore.activeApiaryId }
    })
    hives.value = response.data
  } catch (err) {
    console.error('Fetch hives failed:', err)
  }
}

async function fetchEntries() {
  if (!selectedSession.value) return
  entriesLoading.value = true
  try {
    const response = await axios.get('/api/logbook/entries', {
      params: {
        apiary_id: apiaryStore.activeApiaryId,
        session_id: selectedSession.value.id
      }
    })
    entries.value = response.data
  } catch (err) {
    console.error('Fetch entries failed:', err)
  } finally {
    entriesLoading.value = false
  }
}

function selectSession(session) {
  selectedSession.value = session
  fetchEntries()
}

function openCreateSessionModal() {
  sessionForm.title = ''
  sessionForm.hiveId = ''
  showSessionModal.value = true
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

async function submitSessionForm() {
  if (!sessionForm.title.trim()) return
  try {
    const session = await axios.post('/api/logbook/sessions', {
      title: sessionForm.title.trim(),
      hive_id: sessionForm.hiveId || null
    }, {
      params: { apiary_id: apiaryStore.activeApiaryId }
    })
    
    showSessionModal.value = false
    await fetchSessions()
    selectSession(session.data)
  } catch (err) {
    console.error('Create session error:', err)
  }
}

async function deleteSession(session) {
  if (!confirm(`Möchtest du die Arbeitssitzung "${session.title}" wirklich löschen? Alle darin enthaltenen Inspektionen und Fotos werden endgültig gelöscht.`)) return
  try {
    await axios.delete(`/api/logbook/sessions/${session.id}`)
    if (selectedSession.value?.id === session.id) {
      selectedSession.value = null
      entries.value = []
    }
    await fetchSessions()
  } catch (err) {
    console.error('Delete session failed:', err)
  }
}

function openCreateEntryModal() {
  isEditEntryMode.value = false
  editingEntryId.value = null
  
  // Pre-populate defaults
  entryForm.hiveId = selectedSession.value?.hive_id || (hives.value[0]?.id || '')
  entryForm.date = new Date().toISOString().substring(0, 10)
  entryForm.entryType = 'INSPECTION'
  entryForm.notes = ''
  entryForm.varroaCountDetail.rawCount = 0
  entryForm.varroaTreatmentDetail.product = ''
  entryForm.varroaTreatmentDetail.dosage = ''
  entryForm.varroaTreatmentDetail.treatmentNotes = ''
  
  onHiveSelected()
  showEntryModal.value = true
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function openEditEntryModal(entry) {
  isEditEntryMode.value = true
  editingEntryId.value = entry.id
  
  entryForm.hiveId = entry.hive_id
  entryForm.date = entry.date
  entryForm.entryType = entry.entry_type
  entryForm.notes = entry.notes || ''
  
  if (entry.entry_type === 'INSPECTION' && entry.inspection_detail) {
    entryForm.inspectionDetail.frames = (entry.inspection_detail.frames || []).map(f => ({
      frame_number: f.frame_number,
      side: f.side || 'BOTH',
      brood_eighths: f.brood_eighths,
      bee_eighths: f.bee_eighths,
      food_eighths: f.food_eighths
    }))
  }
  
  if (entry.entry_type === 'VARROA_COUNT' && entry.varroa_count_detail) {
    entryForm.varroaCountDetail.rawCount = entry.varroa_count_detail.raw_count
  }
  
  if (entry.entry_type === 'VARROA_TREATMENT' && entry.varroa_treatment_detail) {
    entryForm.varroaTreatmentDetail.product = entry.varroa_treatment_detail.product
    entryForm.varroaTreatmentDetail.dosage = entry.varroa_treatment_detail.dosage
    entryForm.varroaTreatmentDetail.treatmentNotes = entry.varroa_treatment_detail.treatment_notes || ''
  }
  
  showEntryModal.value = true
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function onHiveSelected() {
  if (entryForm.entryType !== 'INSPECTION') return
  
  const hive = hives.value.find(h => h.id === entryForm.hiveId)
  if (!hive) return

  // Gather frame type or box sum
  let count = 10 // standard fallback
  if (hive.boxes && hive.boxes.length > 0) {
    count = hive.boxes.reduce((acc, box) => acc + box.frame_count, 0)
  }
  
  // Build frames
  const frames = []
  for (let i = 1; i <= count; i++) {
    frames.push({
      frame_number: i,
      side: 'BOTH',
      brood_eighths: 0,
      bee_eighths: 0,
      food_eighths: 0
    })
  }
  entryForm.inspectionDetail.frames = frames
}

async function submitEntryForm() {
  try {
    const payload = {
      hive_id: entryForm.hiveId,
      session_id: selectedSession.value.id,
      date: entryForm.date,
      entry_type: entryForm.entryType,
      notes: entryForm.notes.trim() || null,
      inspection_detail: entryForm.entryType === 'INSPECTION' ? {
        frames: entryForm.inspectionDetail.frames
      } : null,
      varroa_count_detail: entryForm.entryType === 'VARROA_COUNT' ? {
        raw_count: entryForm.varroaCountDetail.rawCount
      } : null,
      varroa_treatment_detail: entryForm.entryType === 'VARROA_TREATMENT' ? {
        product: entryForm.varroaTreatmentDetail.product.trim(),
        dosage: entryForm.varroaTreatmentDetail.dosage.trim(),
        treatment_notes: entryForm.varroaTreatmentDetail.treatmentNotes.trim() || null
      } : null
    }

    if (isEditEntryMode.value) {
      await axios.put(`/api/logbook/entries/${editingEntryId.value}`, payload)
    } else {
      await axios.post('/api/logbook/entries', payload, {
        params: { apiary_id: apiaryStore.activeApiaryId }
      })
    }

    showEntryModal.value = false
    await fetchEntries()
  } catch (err) {
    errorStore.showError('Fehler beim Speichern des Eintrags.', err, 'Eintrag speichern')
  }
}

async function deleteEntry(entry) {
  if (!confirm('Möchtest du diesen Eintrag und alle verknüpften Messwerte und Fotos wirklich löschen?')) return
  try {
    await axios.delete(`/api/logbook/entries/${entry.id}`)
    await fetchEntries()
  } catch (err) {
    console.error('Delete entry failed:', err)
  }
}

async function uploadEntryImage(event, entryId) {
  const file = event.target.files[0]
  if (!file) return

  const formData = new FormData()
  formData.append('file', file)

  try {
    await axios.post(`/api/logbook/entries/${entryId}/images`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    await fetchEntries()
  } catch (err) {
    errorStore.showError('Bilderupload fehlgeschlagen.', err, 'Bilder-Upload')
  }
}

async function deleteEntryImage(imageId) {
  if (!confirm('Bild wirklich löschen?')) return
  try {
    await axios.delete(`/api/logbook/images/${imageId}`)
    await fetchEntries()
  } catch (err) {
    console.error('Delete image failed:', err)
  }
}

function onApplyDraft(draft) {
  // Pre-populate form fields from AI draft!
  isEditEntryMode.value = false
  editingEntryId.value = null
  
  rightTab.value = 'entries'
  
  // Try to resolve hive_id
  let targetHiveId = hives.value[0]?.id || ''
  if (draft.hive_name) {
    const matched = hives.value.find(h => h.name.toLowerCase() === draft.hive_name.toLowerCase())
    if (matched) targetHiveId = matched.id
  }
  
  entryForm.hiveId = targetHiveId
  entryForm.date = draft.date || new Date().toISOString().substring(0, 10)
  entryForm.entryType = draft.entry_type || 'INSPECTION'
  entryForm.notes = draft.notes || ''
  
  // Set details
  if (draft.entry_type === 'INSPECTION' && draft.inspection_detail) {
    entryForm.inspectionDetail.frames = (draft.inspection_detail.frames || []).map((f, i) => ({
      frame_number: f.frame_number || (i + 1),
      side: f.side || 'BOTH',
      brood_eighths: f.brood_eighths || 0,
      bee_eighths: f.bee_eighths || 0,
      food_eighths: f.food_eighths || 0
    }))
  } else {
    onHiveSelected()
  }
  
  if (draft.entry_type === 'VARROA_COUNT' && draft.varroa_count_detail) {
    entryForm.varroaCountDetail.rawCount = draft.varroa_count_detail.raw_count || 0
  }
  
  if (draft.entry_type === 'VARROA_TREATMENT' && draft.varroa_treatment_detail) {
    entryForm.varroaTreatmentDetail.product = draft.varroa_treatment_detail.product || ''
    entryForm.varroaTreatmentDetail.dosage = draft.varroa_treatment_detail.dosage || ''
    entryForm.varroaTreatmentDetail.treatmentNotes = draft.varroa_treatment_detail.treatment_notes || ''
  }

  showEntryModal.value = true
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// Lightbox helpers
function openLightbox(url) {
  lightboxImage.value = url
}

function closeLightbox() {
  lightboxImage.value = null
}

// Helpers
function formatDateTime(dateTimeStr) {
  if (!dateTimeStr) return ''
  const d = new Date(dateTimeStr)
  return d.toLocaleString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

function getEntryTypeName(type) {
  switch (type) {
    case 'INSPECTION': return '🔍 Inspektion'
    case 'VARROA_COUNT': return '🕷️ Varroazählung'
    case 'VARROA_TREATMENT': return '🧪 Varroabehandlung'
    case 'GENERAL': return '📝 Allgemeine Notiz'
    default: return type
  }
}

function sortedFrames(frames) {
  return [...frames].sort((a, b) => a.frame_number - b.frame_number)
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
