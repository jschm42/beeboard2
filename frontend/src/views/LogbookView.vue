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

    <div v-else class="space-y-6">
      
      <!-- View Mode Switcher -->
      <div class="flex justify-between items-center bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border p-4 rounded-2xl shadow-sm">
        <div class="flex items-center space-x-2">
          <span class="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Ansicht:</span>
          <div class="inline-flex rounded-xl p-0.5 bg-gray-100 dark:bg-dark-bg border border-gray-200 dark:border-dark-border">
            <button 
              @click="viewMode = 'tiles'" 
              class="px-4 py-1.5 rounded-lg text-xs font-extrabold tracking-wide transition-all"
              :class="viewMode === 'tiles' ? 'bg-white dark:bg-dark-card text-primary shadow-sm' : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'"
            >
              🗂️ Arbeitssitzungen (Kacheln)
            </button>
            <button 
              @click="viewMode = 'table'" 
              class="px-4 py-1.5 rounded-lg text-xs font-extrabold tracking-wide transition-all"
              :class="viewMode === 'table' ? 'bg-white dark:bg-dark-card text-primary shadow-sm' : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'"
            >
              📊 Tabellarische Übersicht (Alle Einträge)
            </button>
          </div>
        </div>
      </div>

      <!-- VIEW 1: TILES (Kachelansicht) -->
      <div v-if="viewMode === 'tiles'" class="space-y-6 animate-scale">
        
        <!-- Inline Create/Edit Session Card (if modal is open) -->
        <div v-if="showSessionModal" class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-6 shadow-md max-w-xl mx-auto space-y-4 animate-scale mb-6">
          <div class="flex justify-between items-center pb-2 border-b border-gray-100 dark:border-dark-border">
            <h4 class="font-extrabold text-sm text-gray-900 dark:text-white">
              {{ isEditSessionMode ? 'Arbeitssitzung bearbeiten' : 'Neue Arbeitssitzung' }}
            </h4>
            <button @click="showSessionModal = false" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200">
              <svg class="w-4.5 h-4.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
            </button>
          </div>
          <form @submit.prevent="submitSessionForm" class="space-y-4">
            <div>
              <div class="flex justify-between items-center mb-1">
                <label class="block text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Bezeichnung *</label>
                <span 
                  class="text-[9px] font-mono font-bold"
                  :class="sessionForm.title.length >= 30 ? 'text-red-500 font-extrabold animate-pulse' : sessionForm.title.length > 25 ? 'text-amber-500' : 'text-gray-400'"
                >
                  {{ sessionForm.title.length }}/30
                </span>
              </div>
              <input 
                v-model="sessionForm.title" 
                type="text" 
                required
                maxlength="30"
                placeholder="z.B. Honigraum aufsetzen & Varroakontrolle"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-xs"
              />
            </div>
            <div>
              <label class="block text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Bienenvolk (Optional)</label>
              <select 
                v-model="sessionForm.hiveId" 
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-xs"
              >
                <option value="">Keines (Global für Imkerei)</option>
                <option v-for="hive in hives" :key="hive.id" :value="hive.id">
                  {{ hive.name }}
                </option>
              </select>
            </div>
            <div class="flex justify-end space-x-2 pt-2">
              <button type="button" @click="showSessionModal = false" class="px-3 py-1.5 text-xs font-bold text-gray-500 hover:text-gray-700 dark:hover:text-gray-300">Abbrechen</button>
              <button type="submit" class="px-4 py-1.5 bg-primary hover:bg-primary-hover text-white font-extrabold text-xs rounded-xl shadow-md">
                {{ isEditSessionMode ? 'Speichern' : 'Erstellen' }}
              </button>
            </div>
          </form>
        </div>

        <!-- 1.1: SESSIONS GRID OVERVIEW (when no session is selected) -->
        <div v-if="!selectedSession" class="space-y-6">

          <div v-if="sessionsLoading" class="flex justify-center py-20 bg-white dark:bg-dark-card rounded-3xl border border-gray-200 dark:border-dark-border">
            <svg class="animate-spin h-6 w-6 text-primary" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
          </div>

          <div v-else-if="sessions.length === 0" class="bg-white dark:bg-dark-card border rounded-3xl p-12 text-center text-gray-400 italic text-sm">
            Keine Arbeitssitzungen angelegt. Beginne mit "+ Neue Arbeitssitzung" oben rechts.
          </div>

          <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div 
              v-for="session in sessions" 
              :key="session.id"
              @click="selectSession(session)"
              class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-6 shadow-sm hover:shadow-md cursor-pointer hover:border-primary/50 transition-all duration-200 flex flex-col justify-between h-48 group hover:-translate-y-0.5"
            >
              <div>
                <div class="flex justify-between items-start">
                  <span class="text-[9px] font-black uppercase tracking-wider text-primary bg-primary/10 px-2 py-0.5 rounded">Sitzung</span>
                  <div class="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button 
                      @click.stop="openEditSessionModal(session)"
                      class="p-1.5 text-gray-400 hover:text-primary hover:bg-primary/10 rounded-xl transition-all"
                      title="Sitzung umbenennen"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/></svg>
                    </button>
                    <button 
                      @click.stop="deleteSession(session)"
                      class="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-500/10 rounded-xl transition-all"
                      title="Sitzung löschen"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                    </button>
                  </div>
                </div>
                <h4 class="font-extrabold text-base text-gray-900 dark:text-white mt-3 line-clamp-2">
                  {{ session.title }}
                </h4>
                <span 
                  v-if="session.hive" 
                  class="inline-block mt-2 px-2 py-0.5 bg-amber-500/10 text-primary text-[10px] font-bold rounded"
                >
                  Volk: {{ session.hive.name }}
                </span>
              </div>
              <div class="text-[10px] text-gray-400 font-mono mt-4">
                Zuletzt aktiv: {{ formatDateTime(session.updated_at) }}
              </div>
            </div>
          </div>
        </div>

        <!-- 1.2: SELECTED SESSION WORKSPACE (splitscreen with entries stream + AI) -->
        <div v-else class="space-y-6">
          <button 
            @click="selectedSession = null" 
            class="inline-flex items-center text-sm font-semibold text-primary hover:text-primary-hover transition-colors duration-200"
          >
            <svg class="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"/></svg>
            Zurück zur Kachelübersicht
          </button>

          <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
            <!-- Entries Pane (8 cols) -->
            <div class="lg:col-span-8 space-y-6">
              
              <!-- Session title & quick details card -->
              <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-6 shadow-sm flex justify-between items-center">
                <div>
                  <span class="text-[10px] font-black uppercase text-gray-400">Aktive Arbeitssitzung</span>
                  <div class="flex items-center space-x-2 mt-1">
                    <h2 class="text-xl font-extrabold text-gray-900 dark:text-white">{{ selectedSession.title }}</h2>
                    <button 
                      @click="openEditSessionModal(selectedSession)"
                      class="p-1 text-gray-400 hover:text-primary rounded-lg hover:bg-gray-100 dark:hover:bg-dark-border transition-colors inline-flex items-center"
                      title="Sitzung umbenennen"
                    >
                      <svg class="w-4.5 h-4.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/></svg>
                    </button>
                  </div>
                  <p v-if="selectedSession.hive" class="text-xs text-gray-500 mt-1">Gekoppeltes Volk: <span class="font-bold text-primary">{{ selectedSession.hive.name }}</span></p>
                </div>
                
                <button 
                  @click="openCreateEntryModal" 
                  class="px-4 py-2 bg-primary hover:bg-primary-hover text-white font-extrabold text-xs uppercase tracking-wider rounded-xl shadow-md hover-scale"
                >
                  + Neuer Eintrag
                </button>
              </div>

              <!-- Inline Create/Edit Form -->
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

                  <!-- SUB-FORM: INSPECTION DETAILS (nur Zargen-weise) -->
                  <div v-if="entryForm.entryType === 'INSPECTION'" class="space-y-4 border-t border-gray-100 dark:border-dark-border pt-4">
                    <div class="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-2">
                      <h4 class="text-xs font-extrabold uppercase text-gray-500 tracking-wider">
                        Erfassungs-Variante: 📦 Zargen-weise (vereinfacht)
                      </h4>
                    </div>

                    <!-- Zargen-weise Vereinfachte Assessment -->
                    <div class="space-y-4 animate-scale">
                      <!-- Box Mode Switcher: Exact vs Eighths -->
                      <div class="flex justify-between items-center bg-gray-50 dark:bg-dark-bg p-3 rounded-2xl border">
                        <span class="text-[10px] font-bold text-gray-500 uppercase">Zargen-Modus:</span>
                        <div class="inline-flex rounded-lg p-0.5 bg-gray-200 dark:bg-dark-border">
                          <button 
                            type="button"
                            @click="entryForm.inspectionDetail.boxMode = 'exact'" 
                            class="px-2.5 py-1 rounded text-[10px] font-bold transition-all"
                            :class="entryForm.inspectionDetail.boxMode === 'exact' ? 'bg-white dark:bg-dark-card text-primary shadow-sm' : 'text-gray-500'"
                          >
                            🔢 Geschätzte Gesamtmenge (Stk./g)
                          </button>
                          <button 
                            type="button"
                            @click="entryForm.inspectionDetail.boxMode = 'eighths'" 
                            class="px-2.5 py-1 rounded text-[10px] font-bold transition-all"
                            :class="entryForm.inspectionDetail.boxMode === 'eighths' ? 'bg-white dark:bg-dark-card text-primary shadow-sm' : 'text-gray-500'"
                          >
                            🍕 Belegung in Achteln
                          </button>
                        </div>
                      </div>

                      <!-- Boxes List -->
                      <div class="space-y-3">
                        <div 
                          v-for="(box, idx) in entryForm.inspectionDetail.boxes" 
                          :key="box.id"
                          class="p-4 bg-white dark:bg-dark-card border rounded-2xl shadow-sm space-y-3 border-gray-200 dark:border-dark-border"
                        >
                          <div class="flex justify-between items-center pb-2 border-b border-gray-50 dark:border-dark-border">
                            <span class="text-xs font-extrabold text-gray-800 dark:text-gray-200 flex items-center">
                              📦 Zarge #{{ box.order }} ({{ box.box_type === 'BROOD' ? 'Brutraum' : 'Honigraum' }})
                            </span>
                            <span class="text-[9px] font-bold text-gray-400 font-mono">
                              {{ box.frame_count }} Waben · {{ box.frame_type_name }} (x{{ box.multiplier }})
                            </span>
                          </div>

                          <div class="grid grid-cols-2 sm:grid-cols-6 gap-3 text-center">
                            <!-- Brood -->
                            <div class="space-y-1">
                              <span class="text-[9px] text-amber-500 font-bold uppercase">Brut</span>
                              <input 
                                v-model.number="box.brood" 
                                type="number" 
                                step="any"
                                min="0" 
                                :max="entryForm.inspectionDetail.boxMode === 'eighths' ? 8 : undefined" 
                                class="w-full px-2 py-1.5 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg rounded-xl text-center text-xs font-mono font-bold"
                                :placeholder="entryForm.inspectionDetail.boxMode === 'exact' ? '0 Stk.' : '0/8 Waben'"
                              />
                            </div>

                            <!-- Bees -->
                            <div class="space-y-1">
                              <span class="text-[9px] text-green-500 font-bold uppercase">Bienen</span>
                              <input 
                                v-model.number="box.bees" 
                                type="number" 
                                step="any"
                                min="0" 
                                :max="entryForm.inspectionDetail.boxMode === 'eighths' ? 8 : undefined" 
                                class="w-full px-2 py-1.5 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg rounded-xl text-center text-xs font-mono font-bold"
                                :placeholder="entryForm.inspectionDetail.boxMode === 'exact' ? '0 Stk.' : '0/8 Waben'"
                              />
                            </div>

                            <!-- Drones -->
                            <div class="space-y-1">
                              <span class="text-[9px] text-sky-500 font-bold uppercase">Drohnen</span>
                              <input 
                                v-model.number="box.drones" 
                                type="number" 
                                step="any"
                                min="0" 
                                :max="entryForm.inspectionDetail.boxMode === 'eighths' ? 8 : undefined" 
                                class="w-full px-2 py-1.5 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg rounded-xl text-center text-xs font-mono font-bold"
                                :placeholder="entryForm.inspectionDetail.boxMode === 'exact' ? '0 Stk.' : '0/8 Waben'"
                              />
                            </div>

                            <!-- Drone Brood -->
                            <div class="space-y-1">
                              <span class="text-[9px] text-orange-500 font-bold uppercase">Drohnenbrut</span>
                              <input 
                                v-model.number="box.drone_brood" 
                                type="number" 
                                step="any"
                                min="0" 
                                :max="entryForm.inspectionDetail.boxMode === 'eighths' ? 8 : undefined" 
                                class="w-full px-2 py-1.5 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg rounded-xl text-center text-xs font-mono font-bold"
                                :placeholder="entryForm.inspectionDetail.boxMode === 'exact' ? '0 Stk.' : '0/8 Waben'"
                              />
                            </div>

                            <!-- Pollen -->
                            <div class="space-y-1">
                              <span class="text-[9px] text-purple-500 font-bold uppercase">Pollen</span>
                              <input 
                                v-model.number="box.pollen" 
                                type="number" 
                                step="any"
                                min="0" 
                                :max="entryForm.inspectionDetail.boxMode === 'eighths' ? 8 : undefined" 
                                class="w-full px-2 py-1.5 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg rounded-xl text-center text-xs font-mono font-bold"
                                :placeholder="entryForm.inspectionDetail.boxMode === 'exact' ? '0 g' : '0/8 Waben'"
                              />
                            </div>

                            <!-- Food -->
                            <div class="space-y-1">
                              <span class="text-[9px] text-yellow-500 font-bold uppercase">Futter</span>
                              <input 
                                v-model.number="box.food" 
                                type="number" 
                                step="any"
                                min="0" 
                                :max="entryForm.inspectionDetail.boxMode === 'eighths' ? 8 : undefined" 
                                class="w-full px-2 py-1.5 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg rounded-xl text-center text-xs font-mono font-bold"
                                :placeholder="entryForm.inspectionDetail.boxMode === 'exact' ? '0 g' : '0/8 Waben'"
                              />
                            </div>
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
                        <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 mb-1">Dosierung (z.B. 50ml, 1 Streifen) *</label>
                        <input 
                          v-model="entryForm.varroaTreatmentDetail.dosage" 
                          type="text" 
                          required
                          placeholder="z.B. 50 ml"
                          class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm"
                        />
                      </div>
                    </div>
                    <div>
                      <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 mb-1">Behandlungshinweise</label>
                      <textarea 
                        v-model="entryForm.varroaTreatmentDetail.treatmentNotes" 
                        placeholder="Zusätzliche Behandlungsdetails..."
                        rows="2"
                        class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm"
                      ></textarea>
                    </div>
                  </div>

                  <div class="flex justify-end space-x-2 pt-4 border-t border-gray-100 dark:border-dark-border">
                    <button type="button" @click="showEntryModal = false" class="px-4 py-2 text-sm font-bold text-gray-500 hover:text-gray-700 dark:hover:text-gray-300">Abbrechen</button>
                    <button type="submit" class="px-5 py-2 bg-primary hover:bg-primary-hover text-white font-extrabold text-sm rounded-xl shadow-md">
                      Speichern
                    </button>
                  </div>
                </form>
              </div>

              <!-- Entries Stream List -->
              <div v-if="entriesLoading" class="flex justify-center py-20 bg-white dark:bg-dark-card rounded-3xl border border-gray-200 dark:border-dark-border shadow-sm">
                <svg class="animate-spin h-6 w-6 text-primary" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
              </div>

              <div v-else-if="entries.length === 0" class="bg-white dark:bg-dark-card border rounded-3xl p-12 text-center text-gray-400 italic text-sm">
                Noch keine Protokolleinträge in dieser Sitzung erfasst. Klicke oben rechts auf "+ Neuer Eintrag" um zu starten!
              </div>

              <div v-else class="space-y-4">
                <div 
                  v-for="entry in entries" 
                  :key="entry.id"
                  class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-6 shadow-sm hover:shadow-md transition-shadow duration-200 space-y-4"
                >
                  <div class="flex justify-between items-start">
                    <div class="flex items-center space-x-3">
                      <span class="text-[10px] font-black uppercase rounded tracking-wider bg-gray-100 dark:bg-dark-bg text-gray-500 px-2 py-0.5">
                        {{ getEntryTypeName(entry.entry_type) }}
                      </span>
                      <span class="text-xs font-bold text-primary">Volk: {{ entry.hive?.name || 'Unbekannt' }}</span>
                      <span class="text-[10px] text-gray-400 font-mono">{{ formatDate(entry.date) }}</span>
                    </div>

                    <div class="flex items-center space-x-1">
                      <button 
                        @click="openEditEntryModal(entry)"
                        class="p-1 text-gray-400 hover:text-primary rounded-xl hover:bg-gray-50 dark:hover:bg-dark-bg transition-colors"
                        title="Eintrag bearbeiten"
                      >
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/></svg>
                      </button>
                      <button 
                        @click="deleteEntry(entry)"
                        class="p-1 text-gray-400 hover:text-red-500 hover:bg-red-500/10 rounded-xl transition-all"
                        title="Eintrag löschen"
                      >
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                      </button>
                    </div>
                  </div>

                  <p class="text-sm text-gray-700 dark:text-gray-300 font-medium italic">"{{ entry.notes || 'Keine Anmerkungen erfasst.' }}"</p>

                  <!-- Nested Inspections -->
                  <div v-if="entry.entry_type === 'INSPECTION' && entry.inspection_detail" class="space-y-3">
                    <span class="text-[10px] font-black uppercase text-gray-400">🔎 Brut- & Raumbelegung (Zargen- & Volkssummen):</span>
                    
                    <div v-if="getBoxTotalsForEntry(entry)" class="space-y-3">
                      <!-- Box Grid -->
                      <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
                        <div 
                          v-for="box in getBoxTotalsForEntry(entry).boxes" 
                          :key="box.id"
                          class="p-4 bg-gray-50 dark:bg-dark-bg/60 border border-gray-100 dark:border-dark-border rounded-2xl flex flex-col justify-between"
                        >
                          <div class="flex justify-between items-center mb-2 pb-1.5 border-b border-gray-200/50 dark:border-dark-border">
                            <span class="text-[10px] font-black text-gray-500">Zarge {{ box.order }}: {{ box.box_type === 'BROOD' ? 'Brutraum' : 'Honigraum' }}</span>
                            <span class="text-[9px] font-bold text-primary bg-primary/10 px-2 py-0.5 rounded-full">{{ box.frame_count }} Waben ({{ box.frame_type_name }})</span>
                          </div>
                          <!-- Box values -->
                          <div class="grid grid-cols-2 gap-x-4 gap-y-1 text-xs font-mono font-bold">
                            <div class="flex justify-between items-center text-amber-500">
                              <span>Brut:</span>
                              <span>{{ box.brood.toFixed(0) }}</span>
                            </div>
                            <div class="flex justify-between items-center text-green-500">
                              <span>Bienen:</span>
                              <span>{{ box.bees.toFixed(0) }}</span>
                            </div>
                            <div class="flex justify-between items-center text-sky-500">
                              <span>Drohnen:</span>
                              <span>{{ box.drones.toFixed(0) }}</span>
                            </div>
                            <div class="flex justify-between items-center text-orange-500">
                              <span>Dr.Brut:</span>
                              <span>{{ box.drone_brood.toFixed(0) }}</span>
                            </div>
                            <div class="flex justify-between items-center text-purple-500">
                              <span>Pollen:</span>
                              <span>{{ box.pollen.toFixed(0) }} g</span>
                            </div>
                            <div class="flex justify-between items-center text-yellow-500">
                              <span>Futter:</span>
                              <span>{{ box.food.toFixed(0) }} g</span>
                            </div>
                          </div>
                        </div>
                      </div>

                      <!-- Hive Total Summary -->
                      <div class="p-4 bg-amber-500/5 dark:bg-amber-500/10 border border-amber-500/20 rounded-2xl flex flex-col md:flex-row justify-between items-start md:items-center space-y-2 md:space-y-0 shadow-sm">
                        <div>
                          <span class="text-[9px] font-black text-amber-600 dark:text-amber-400 uppercase tracking-wider">🐝 Volk Gesamt (Beute):</span>
                          <h4 class="text-sm font-extrabold text-gray-900 dark:text-white">Summe über alle Zargen</h4>
                        </div>
                        <div class="flex flex-wrap gap-2 font-mono font-black text-[10px]">
                          <div class="flex items-center space-x-1 text-amber-500 bg-amber-500/10 px-2 py-1 rounded-xl">
                            <span>Brut:</span>
                            <span>{{ getBoxTotalsForEntry(entry).hive.brood.toFixed(0) }}</span>
                          </div>
                          <div class="flex items-center space-x-1 text-green-500 bg-green-500/10 px-2 py-1 rounded-xl">
                            <span>Bienen:</span>
                            <span>{{ getBoxTotalsForEntry(entry).hive.bees.toFixed(0) }}</span>
                          </div>
                          <div class="flex items-center space-x-1 text-sky-500 bg-sky-500/10 px-2 py-1 rounded-xl">
                            <span>Drohnen:</span>
                            <span>{{ getBoxTotalsForEntry(entry).hive.drones.toFixed(0) }}</span>
                          </div>
                          <div class="flex items-center space-x-1 text-orange-500 bg-orange-500/10 px-2 py-1 rounded-xl">
                            <span>Dr.Brut:</span>
                            <span>{{ getBoxTotalsForEntry(entry).hive.drone_brood.toFixed(0) }}</span>
                          </div>
                          <div class="flex items-center space-x-1 text-purple-500 bg-purple-500/10 px-2 py-1 rounded-xl">
                            <span>Pollen:</span>
                            <span>{{ getBoxTotalsForEntry(entry).hive.pollen.toFixed(0) }} g</span>
                          </div>
                          <div class="flex items-center space-x-1 text-yellow-500 bg-yellow-500/10 px-2 py-1 rounded-xl">
                            <span>Futter:</span>
                            <span>{{ getBoxTotalsForEntry(entry).hive.food.toFixed(0) }} g</span>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    <!-- Fallback if getBoxTotalsForEntry returns null -->
                    <div v-else class="text-xs text-gray-400 italic">
                      Zargen- und Volksdaten konnten nicht berechnet werden.
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
                        class="text-[10px] font-bold text-primary hover:text-primary-hover hover:underline cursor-pointer uppercase font-sans"
                      >
                        + Bild hinzufügen
                      </label>
                    </div>

                    <!-- Gallery Grid -->
                    <div v-if="entry.images && entry.images.length > 0" class="grid grid-cols-3 sm:grid-cols-5 gap-3">
                      <div 
                        v-for="img in entry.images" 
                        :key="img.id"
                        class="relative aspect-square rounded-2xl overflow-hidden border border-gray-100 dark:border-dark-border group bg-gray-50 dark:bg-dark-card"
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

            </div>

            <!-- AI Pane (4 cols) -->
            <div class="lg:col-span-4 h-[600px] bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl overflow-hidden shadow-sm sticky top-6">
              <AIChatPane @apply-draft="onApplyDraft" />
            </div>
          </div>

        </div>

      </div>

      <!-- VIEW 2: TABLE (Tabellenansicht aller Logeinträge) -->
      <div v-if="viewMode === 'table'" class="space-y-6 animate-scale">
        
        <!-- Filter Panel Card -->
        <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-6 shadow-sm">
          <h3 class="text-sm font-bold text-gray-900 dark:text-white mb-4 flex items-center">
            <span>🔍 Filter-Optionen</span>
            <button 
              @click="resetTableFilters" 
              class="ml-auto text-xs text-primary hover:underline font-bold"
            >
              Filter zurücksetzen
            </button>
          </h3>
          
          <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            <!-- Zeitraum Start -->
            <div>
              <label class="block text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Von Datum</label>
              <input 
                v-model="tableFilters.startDate" 
                type="date" 
                class="w-full px-3 py-2 border border-gray-200 dark:border-gray-800 dark:bg-dark-bg dark:text-white rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
            
            <!-- Zeitraum Ende -->
            <div>
              <label class="block text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Bis Datum</label>
              <input 
                v-model="tableFilters.endDate" 
                type="date" 
                class="w-full px-3 py-2 border border-gray-200 dark:border-gray-800 dark:bg-dark-bg dark:text-white rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
            
            <!-- Imkerei -->
            <div>
              <label class="block text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Imkerei</label>
              <select 
                v-model="tableFilters.apiaryId" 
                class="w-full px-3 py-2 border border-gray-200 dark:border-gray-800 dark:bg-dark-bg dark:text-white rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-primary cursor-pointer"
              >
                <option value="">Alle Imkereien</option>
                <option v-for="a in apiaryStore.apiaries" :key="a.id" :value="a.id">
                  {{ a.name }}
                </option>
              </select>
            </div>
            
            <!-- Standort -->
            <div>
              <label class="block text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Standort</label>
              <select 
                v-model="tableFilters.locationId" 
                class="w-full px-3 py-2 border border-gray-200 dark:border-gray-800 dark:bg-dark-bg dark:text-white rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-primary cursor-pointer"
              >
                <option value="">Alle Standorte</option>
                <option v-for="loc in uniqueLocations" :key="loc.id" :value="loc.id">
                  {{ loc.name }}
                </option>
              </select>
            </div>
            
            <!-- Volk -->
            <div>
              <label class="block text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Volk</label>
              <select 
                v-model="tableFilters.hiveId" 
                class="w-full px-3 py-2 border border-gray-200 dark:border-gray-800 dark:bg-dark-bg dark:text-white rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-primary cursor-pointer"
              >
                <option value="">Alle Völker</option>
                <option v-for="h in uniqueHives" :key="h.id" :value="h.id">
                  {{ h.name }}
                </option>
              </select>
            </div>
            
            <!-- Erfasser -->
            <div>
              <label class="block text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Erfasser (User)</label>
              <select 
                v-model="tableFilters.userId" 
                class="w-full px-3 py-2 border border-gray-200 dark:border-gray-800 dark:bg-dark-bg dark:text-white rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-primary cursor-pointer"
              >
                <option value="">Alle Erfasser</option>
                <option v-for="u in uniqueCreators" :key="u.id" :value="u.id">
                  {{ u.username }}
                </option>
              </select>
            </div>
          </div>
        </div>

        <!-- Inline Entry creation form in table mode -->
        <div v-if="showEntryModal" class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl shadow-md p-6 max-w-3xl mx-auto mb-6 animate-scale">
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
            <div v-if="entryForm.entryType === 'INSPECTION'" class="space-y-4 border-t border-gray-100 dark:border-dark-border pt-4">
              
              <!-- Warning card when hive has no boxes -->
              <div v-if="activeHive && (!activeHive.boxes || activeHive.boxes.length === 0)" class="p-3.5 bg-amber-50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-900/60 rounded-xl text-xs font-bold text-amber-700 dark:text-amber-400 flex items-start space-x-2">
                <span class="mt-0.5 text-base shrink-0">⚠️</span>
                <span>Dieses Volk hat noch keine Zargen konfiguriert. Eingaben sind nur Waben-weise möglich. Füge in der Völker-Ansicht Zargen hinzu, um die vereinfachte Zargen-weise Erfassung freizuschalten.</span>
              </div>

              <div class="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-2">
                <h4 class="text-xs font-extrabold uppercase text-gray-500 tracking-wider">Erfassungs-Variante</h4>
                <span class="inline-flex items-center px-3 py-1 rounded-lg text-[10px] font-black bg-white dark:bg-dark-card text-primary border border-gray-200 dark:border-dark-border">
                  📦 Zargen-weise (Vereinfacht)
                </span>
              </div>

              <!-- Zargen-weise Vereinfachte Assessment (Standard, einzige Variante) -->
              <div class="space-y-4 animate-scale">
                <!-- Box Mode Switcher: Exact vs Eighths -->
                <div class="flex justify-between items-center bg-gray-50 dark:bg-dark-bg p-3 rounded-2xl border">
                  <span class="text-[10px] font-bold text-gray-500 uppercase">Zargen-Modus:</span>
                  <div class="inline-flex rounded-lg p-0.5 bg-gray-200 dark:bg-dark-border">
                    <button 
                      type="button"
                      @click="entryForm.inspectionDetail.boxMode = 'exact'" 
                      class="px-2.5 py-1 rounded text-[10px] font-bold transition-all"
                      :class="entryForm.inspectionDetail.boxMode === 'exact' ? 'bg-white dark:bg-dark-card text-primary shadow-sm' : 'text-gray-500'"
                    >
                      🔢 Geschätzte Gesamtmenge (Stk./g)
                    </button>
                    <button 
                      type="button"
                      @click="entryForm.inspectionDetail.boxMode = 'eighths'" 
                      class="px-2.5 py-1 rounded text-[10px] font-bold transition-all"
                      :class="entryForm.inspectionDetail.boxMode === 'eighths' ? 'bg-white dark:bg-dark-card text-primary shadow-sm' : 'text-gray-500'"
                    >
                      🍕 Belegung in Achteln
                    </button>
                  </div>
                </div>

                <!-- Boxes List -->
                <div class="space-y-3">
                  <div 
                    v-for="(box, idx) in entryForm.inspectionDetail.boxes" 
                    :key="box.id"
                    class="p-4 bg-white dark:bg-dark-card border rounded-2xl shadow-sm space-y-3 border-gray-200 dark:border-dark-border"
                  >
                    <div class="flex justify-between items-center pb-2 border-b border-gray-50 dark:border-dark-border">
                      <span class="text-xs font-extrabold text-gray-800 dark:text-gray-200 flex items-center">
                        📦 Zarge #{{ box.order }} ({{ box.box_type === 'BROOD' ? 'Brutraum' : 'Honigraum' }})
                      </span>
                      <span class="text-[9px] font-bold text-gray-400 font-mono">
                        {{ box.frame_count }} Waben · {{ box.frame_type_name }} (x{{ box.multiplier }})
                      </span>
                    </div>

                    <div class="grid grid-cols-2 sm:grid-cols-6 gap-3 text-center">
                      <!-- Brood -->
                      <div class="space-y-1">
                        <span class="text-[9px] text-amber-500 font-bold uppercase">Brut</span>
                        <input 
                          v-model.number="box.brood" 
                          type="number" 
                          step="any"
                          min="0" 
                          :max="entryForm.inspectionDetail.boxMode === 'exact' ? undefined : 8" 
                          class="w-full px-2 py-1.5 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg rounded-xl text-center text-xs font-mono font-bold"
                          :placeholder="entryForm.inspectionDetail.boxMode === 'exact' ? '0 Stk.' : '0/8 Waben'"
                        />
                        <div v-if="calculatedBoxTotals && calculatedBoxTotals[idx]" class="text-[9px] text-gray-400 font-mono">
                          ≙ {{ calculatedBoxTotals[idx].brood }}
                        </div>
                      </div>

                      <!-- Bees -->
                      <div class="space-y-1">
                        <span class="text-[9px] text-green-500 font-bold uppercase">Bienen</span>
                        <input 
                          v-model.number="box.bees" 
                          type="number" 
                          step="any"
                          min="0" 
                          :max="entryForm.inspectionDetail.boxMode === 'exact' ? undefined : 8" 
                          class="w-full px-2 py-1.5 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg rounded-xl text-center text-xs font-mono font-bold"
                          :placeholder="entryForm.inspectionDetail.boxMode === 'exact' ? '0 Stk.' : '0/8 Waben'"
                        />
                        <div v-if="calculatedBoxTotals && calculatedBoxTotals[idx]" class="text-[9px] text-gray-400 font-mono">
                          ≙ {{ calculatedBoxTotals[idx].bees }}
                        </div>
                      </div>

                      <!-- Drones -->
                      <div class="space-y-1">
                        <span class="text-[9px] text-sky-500 font-bold uppercase">Drohnen</span>
                        <input 
                          v-model.number="box.drones" 
                          type="number" 
                          step="any"
                          min="0" 
                          :max="entryForm.inspectionDetail.boxMode === 'exact' ? undefined : 8" 
                          class="w-full px-2 py-1.5 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg rounded-xl text-center text-xs font-mono font-bold"
                          :placeholder="entryForm.inspectionDetail.boxMode === 'exact' ? '0 Stk.' : '0/8 Waben'"
                        />
                        <div v-if="calculatedBoxTotals && calculatedBoxTotals[idx]" class="text-[9px] text-gray-400 font-mono">
                          ≙ {{ calculatedBoxTotals[idx].drones }}
                        </div>
                      </div>

                      <!-- Drone Brood -->
                      <div class="space-y-1">
                        <span class="text-[9px] text-orange-500 font-bold uppercase">Drohnenbrut</span>
                        <input 
                          v-model.number="box.drone_brood" 
                          type="number" 
                          step="any"
                          min="0" 
                          :max="entryForm.inspectionDetail.boxMode === 'exact' ? undefined : 8" 
                          class="w-full px-2 py-1.5 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg rounded-xl text-center text-xs font-mono font-bold"
                          :placeholder="entryForm.inspectionDetail.boxMode === 'exact' ? '0 Stk.' : '0/8 Waben'"
                        />
                        <div v-if="calculatedBoxTotals && calculatedBoxTotals[idx]" class="text-[9px] text-gray-400 font-mono">
                          ≙ {{ calculatedBoxTotals[idx].drone_brood }}
                        </div>
                      </div>

                      <!-- Pollen -->
                      <div class="space-y-1">
                        <span class="text-[9px] text-purple-500 font-bold uppercase">Pollen</span>
                        <input 
                          v-model.number="box.pollen" 
                          type="number" 
                          step="any"
                          min="0" 
                          :max="entryForm.inspectionDetail.boxMode === 'exact' ? undefined : 8" 
                          class="w-full px-2 py-1.5 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg rounded-xl text-center text-xs font-mono font-bold"
                          :placeholder="entryForm.inspectionDetail.boxMode === 'exact' ? '0 g' : '0/8 Waben'"
                        />
                        <div v-if="calculatedBoxTotals && calculatedBoxTotals[idx]" class="text-[9px] text-gray-400 font-mono">
                          ≙ {{ calculatedBoxTotals[idx].pollen }}
                        </div>
                      </div>

                      <!-- Food -->
                      <div class="space-y-1">
                        <span class="text-[9px] text-yellow-500 font-bold uppercase">Futter</span>
                        <input 
                          v-model.number="box.food" 
                          type="number" 
                          step="any"
                          min="0" 
                          :max="entryForm.inspectionDetail.boxMode === 'exact' ? undefined : 8" 
                          class="w-full px-2 py-1.5 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg rounded-xl text-center text-xs font-mono font-bold"
                          :placeholder="entryForm.inspectionDetail.boxMode === 'exact' ? '0 g' : '0/8 Waben'"
                        />
                        <div v-if="calculatedBoxTotals && calculatedBoxTotals[idx]" class="text-[9px] text-gray-400 font-mono">
                          ≙ {{ calculatedBoxTotals[idx].food }}
                        </div>
                      </div>
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
                  <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 mb-1">Dosierung (z.B. 50ml, 1 Streifen) *</label>
                  <input 
                    v-model="entryForm.varroaTreatmentDetail.dosage" 
                    type="text" 
                    required
                    placeholder="z.B. 50 ml"
                    class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm"
                  />
                </div>
              </div>
              <div>
                <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 mb-1">Behandlungshinweise</label>
                <textarea 
                  v-model="entryForm.varroaTreatmentDetail.treatmentNotes" 
                  placeholder="Zusätzliche Behandlungsdetails..."
                  rows="2"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm"
                ></textarea>
              </div>
            </div>

            <div class="flex justify-end space-x-2 pt-4 border-t border-gray-100 dark:border-dark-border">
              <button type="button" @click="showEntryModal = false" class="px-4 py-2 text-sm font-bold text-gray-500 hover:text-gray-700 dark:hover:text-gray-300">Abbrechen</button>
              <button type="submit" class="px-5 py-2 bg-primary hover:bg-primary-hover text-white font-extrabold text-sm rounded-xl shadow-md">
                Speichern
              </button>
            </div>
          </form>
        </div>

        <!-- Entries Table Display -->
        <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl overflow-hidden shadow-sm">
          <div v-if="loadingAllEntries" class="flex flex-col items-center justify-center py-20">
            <svg class="animate-spin h-8 w-8 text-primary mb-3" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
            <span class="text-xs text-gray-400 font-bold">Lade Logeinträge...</span>
          </div>

          <div v-else-if="filteredEntries.length === 0" class="p-12 text-center text-gray-400 italic text-sm">
            Keine Einträge für die gewählten Filterkriterien gefunden.
          </div>

          <div v-else class="overflow-x-auto">
            <table class="w-full text-left border-collapse">
              <thead>
                <tr class="bg-gray-50 dark:bg-dark-bg text-gray-500 dark:text-gray-400 text-[10px] font-bold uppercase tracking-wider border-b border-gray-100 dark:border-dark-border">
                  <th class="px-6 py-4">Datum</th>
                  <th class="px-6 py-4">Imkerei / Standort</th>
                  <th class="px-6 py-4">Volk</th>
                  <th class="px-6 py-4">Typ</th>
                  <th class="px-6 py-4">Beschreibung / Notizen</th>
                  <th class="px-6 py-4">Erfasser</th>
                  <th class="px-6 py-4 text-center">Bilder</th>
                  <th class="px-6 py-4 text-right">Aktionen</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-100 dark:divide-dark-border text-xs">
                <tr 
                  v-for="entry in filteredEntries" 
                  :key="entry.id" 
                  class="hover:bg-gray-50/50 dark:hover:bg-dark-bg/30 transition-colors duration-150 align-top"
                >
                  <!-- Date -->
                  <td class="px-6 py-4 font-bold text-gray-800 dark:text-gray-200 whitespace-nowrap">
                    {{ formatDate(entry.date) }}
                  </td>
                  
                  <!-- Apiary & Location -->
                  <td class="px-6 py-4 text-gray-600 dark:text-gray-300">
                    <div class="font-bold">{{ entry.apiary?.name || '-' }}</div>
                    <div class="text-[10px] text-gray-400 mt-0.5">{{ entry.hive?.location?.name || '-' }}</div>
                  </td>
                  
                  <!-- Hive -->
                  <td class="px-6 py-4 font-bold text-primary">
                    {{ entry.hive?.name || '-' }}
                  </td>
                  
                  <!-- Type -->
                  <td class="px-6 py-4 whitespace-nowrap">
                    <span class="px-2 py-0.5 text-[9px] font-black uppercase rounded tracking-wider bg-gray-100 dark:bg-dark-bg text-gray-500">
                      {{ getEntryTypeName(entry.entry_type) }}
                    </span>
                  </td>
                  
                  <!-- Notes & details -->
                  <td class="px-6 py-4 max-w-xs md:max-w-md">
                    <p class="text-gray-700 dark:text-gray-300 italic mb-2">"{{ entry.notes || 'Keine Anmerkungen erfasst.' }}"</p>
                    
                    <!-- Nested details rendering -->
                    <div v-if="entry.entry_type === 'INSPECTION' && entry.inspection_detail" class="mt-2 text-[10px] bg-gray-50 dark:bg-dark-bg/40 p-2.5 rounded-xl border space-y-1.5 border-gray-100 dark:border-dark-border">
                      <div class="flex justify-between items-center pb-1 border-b border-gray-200/40 dark:border-dark-border">
                        <span class="font-bold text-gray-500 uppercase tracking-wide">🔎 Belegung nach Zarge & Volk:</span>
                        <span v-if="getBoxTotalsForEntry(entry)" class="font-black text-amber-500 text-[10px] flex flex-wrap gap-2">
                          <span>B: {{ getBoxTotalsForEntry(entry).hive.brood.toFixed(0) }}</span>
                          <span>N: {{ getBoxTotalsForEntry(entry).hive.bees.toFixed(0) }}</span>
                          <span>D: {{ getBoxTotalsForEntry(entry).hive.drones.toFixed(0) }}</span>
                          <span>DB: {{ getBoxTotalsForEntry(entry).hive.drone_brood.toFixed(0) }}</span>
                          <span>P: {{ getBoxTotalsForEntry(entry).hive.pollen.toFixed(0) }} g</span>
                          <span>F: {{ getBoxTotalsForEntry(entry).hive.food.toFixed(0) }} g</span>
                        </span>
                      </div>
                      <div v-if="getBoxTotalsForEntry(entry)" class="flex flex-wrap gap-1.5 mt-1">
                        <span 
                          v-for="box in getBoxTotalsForEntry(entry).boxes" 
                          :key="box.id"
                          class="px-2 py-0.5 bg-white dark:bg-dark-card border rounded-lg text-[9px] font-mono border-gray-100 dark:border-dark-border flex flex-wrap gap-x-1.5 font-bold shadow-sm"
                        >
                          <span class="text-gray-400">Z{{ box.order }}:</span>
                          <span class="text-amber-500">B:{{ box.brood.toFixed(1) }}</span>
                          <span class="text-green-500">N:{{ box.bees.toFixed(1) }}</span>
                          <span class="text-sky-500">D:{{ box.drones.toFixed(1) }}</span>
                          <span class="text-orange-500">DB:{{ box.drone_brood.toFixed(1) }}</span>
                          <span class="text-purple-500">P:{{ box.pollen.toFixed(1) }}</span>
                          <span class="text-yellow-500">F:{{ box.food.toFixed(1) }}</span>
                        </span>
                      </div>
                      <div v-else class="text-[9px] text-gray-400 italic">
                        Zargen- und Volksdaten konnten nicht berechnet werden.
                      </div>
                    </div>

                    <div v-if="entry.entry_type === 'VARROA_COUNT' && entry.varroa_count_detail" class="mt-2 text-[10px] bg-red-500/5 p-2 rounded-xl border border-red-500/10 flex space-x-3 text-red-500">
                      <div>Roh: <span class="font-bold font-mono">{{ entry.varroa_count_detail.raw_count }}</span></div>
                      <div>Berechnet: <span class="font-bold font-mono">~{{ entry.varroa_count_detail.estimated_total.toFixed(1) }}/Tag</span></div>
                    </div>

                    <div v-if="entry.entry_type === 'VARROA_TREATMENT' && entry.varroa_treatment_detail" class="mt-2 text-[10px] bg-green-500/5 p-2 rounded-xl border border-green-500/10 text-green-600 dark:text-green-400">
                      <div class="font-bold">{{ entry.varroa_treatment_detail.product }} ({{ entry.varroa_treatment_detail.dosage }})</div>
                      <div v-if="entry.varroa_treatment_detail.treatment_notes" class="text-[9px] text-gray-400 italic mt-0.5">"{{ entry.varroa_treatment_detail.treatment_notes }}"</div>
                    </div>
                  </td>
                  
                  <!-- User -->
                  <td class="px-6 py-4 text-gray-500 dark:text-gray-400 whitespace-nowrap font-bold">
                    {{ entry.created_by?.username || '-' }}
                  </td>
                  
                  <!-- Images count/gallery -->
                  <td class="px-6 py-4 text-center">
                    <div v-if="entry.images && entry.images.length > 0" class="flex justify-center -space-x-1.5 overflow-hidden">
                      <img 
                        v-for="img in entry.images" 
                        :key="img.id"
                        :src="`/uploads/${img.thumbnail_path || img.image_path}`" 
                        class="inline-block h-6 w-6 rounded-full ring-2 ring-white dark:ring-dark-card object-cover cursor-pointer hover:scale-110 hover:z-10 transition-all"
                        @click="openLightbox(`/uploads/${img.image_path}`)"
                      />
                    </div>
                    <span v-else class="text-gray-300 dark:text-gray-700">-</span>
                  </td>
                  
                  <!-- Actions -->
                  <td class="px-6 py-4 text-right space-x-1 whitespace-nowrap">
                    <button 
                      @click="openEditEntryModal(entry)" 
                      class="p-1 text-gray-400 hover:text-primary rounded hover:bg-gray-100 dark:hover:bg-dark-border transition-colors inline-flex"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/></svg>
                    </button>
                    <button 
                      @click="deleteEntry(entry)" 
                      class="p-1 text-gray-400 hover:text-red-500 rounded hover:bg-red-500/10 transition-colors inline-flex"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

      </div>

    </div>

    <!-- Image Lightbox Modal -->
    <div v-if="lightboxImage" class="fixed inset-0 z-50 flex items-center justify-center bg-black/90 p-4" @click="closeLightbox">
      <div class="relative max-w-4xl max-h-screen">
        <img :src="lightboxImage" class="max-w-full max-h-[85vh] rounded-2xl shadow-2xl border border-white/10 animate-scale" alt="Full screen preview" />
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
import { ref, onMounted, reactive, computed, watch } from 'vue'
import { useApiaryStore } from '../stores/apiary'
import { useErrorStore } from '../stores/error'
import AIChatPane from '../components/AIChatPane.vue'
import axios from 'axios'

const apiaryStore = useApiaryStore()
const errorStore = useErrorStore()

// Sessions & stream data
const sessions = ref([])
const hives = ref([])
const entries = ref([])

const sessionsLoading = ref(false)
const entriesLoading = ref(false)

const selectedSession = ref(null)
const rightTab = ref('entries') // 'entries' or 'ai'
const lightboxImage = ref(null)

// View modes & global tables
const viewMode = ref('tiles') // 'tiles' or 'table'
const allEntries = ref([])
const loadingAllEntries = ref(false)

const tableFilters = reactive({
  startDate: '',
  endDate: '',
  apiaryId: '',
  locationId: '',
  hiveId: '',
  userId: ''
})

// Modals toggles
const showSessionModal = ref(false)
const isEditSessionMode = ref(false)
const editingSessionId = ref(null)
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
    assessmentMode: 'boxes', // only simplified box mode
    boxMode: 'exact', // 'exact' or 'eighths'
    frames: [],
    boxes: []
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

// Lifecycle
onMounted(async () => {
  if (apiaryStore.activeApiaryId) {
    await Promise.all([
      fetchSessions(),
      fetchHives()
    ])
  }
})

// Watches
watch(() => apiaryStore.activeApiaryId, async (newVal) => {
  if (newVal) {
    selectedSession.value = null
    resetTableFilters()
    await Promise.all([
      fetchSessions(),
      fetchHives()
    ])
    if (viewMode.value === 'table') {
      await fetchAllEntries()
    }
  }
})

watch(viewMode, async (newVal) => {
  if (newVal === 'table') {
    await fetchAllEntries()
  }
})

// Dropdown unique filter computed values
const activeHive = computed(() => hives.value.find(h => h.id === entryForm.hiveId))

const uniqueLocations = computed(() => {
  const map = new Map()
  allEntries.value.forEach(e => {
    if (e.hive?.location) {
      map.set(e.hive.location.id, e.hive.location.name)
    }
  })
  return Array.from(map.entries()).map(([id, name]) => ({ id, name }))
})

const uniqueHives = computed(() => {
  const map = new Map()
  allEntries.value.forEach(e => {
    if (e.hive) {
      map.set(e.hive.id, e.hive.name)
    }
  })
  return Array.from(map.entries()).map(([id, name]) => ({ id, name }))
})

const uniqueCreators = computed(() => {
  const map = new Map()
  allEntries.value.forEach(e => {
    if (e.created_by) {
      map.set(e.created_by.id, e.created_by.username)
    }
  })
  return Array.from(map.entries()).map(([id, name]) => ({ id, name }))
})

const filteredEntries = computed(() => {
  return allEntries.value.filter(entry => {
    if (tableFilters.apiaryId && entry.apiary_id !== tableFilters.apiaryId) {
      return false
    }
    if (tableFilters.locationId && entry.hive?.location?.id !== tableFilters.locationId) {
      return false
    }
    if (tableFilters.hiveId && entry.hive_id !== tableFilters.hiveId) {
      return false
    }
    if (tableFilters.userId && entry.created_by_id !== tableFilters.userId) {
      return false
    }
    if (tableFilters.startDate) {
      const entryDate = new Date(entry.date)
      const startDate = new Date(tableFilters.startDate)
      if (entryDate < startDate) return false
    }
    if (tableFilters.endDate) {
      const entryDate = new Date(entry.date)
      const endDate = new Date(tableFilters.endDate)
      if (entryDate > endDate) return false
    }
    return true
  })
})

// Box capacity conversions display
const calculatedBoxTotals = computed(() => {
  if (entryForm.entryType !== 'INSPECTION' || entryForm.inspectionDetail.assessmentMode !== 'boxes') return null
  
  return entryForm.inspectionDetail.boxes.map(box => {
    const C = box.frame_count
    const M = box.multiplier || 1.0
    
    let broodVal = 0
    let beeVal = 0
    let foodVal = 0
    let droneVal = 0
    let droneBroodVal = 0
    let pollenVal = 0
    
    if (entryForm.inspectionDetail.boxMode === 'exact') {
      broodVal = Number(box.brood || 0)
      beeVal = Number(box.bees || 0)
      foodVal = Number(box.food || 0)
      droneVal = Number(box.drones || 0)
      droneBroodVal = Number(box.drone_brood || 0)
      pollenVal = Number(box.pollen || 0)
    } else {
      broodVal = (Number(box.brood || 0) / 8) * C * M
      beeVal = (Number(box.bees || 0) / 8) * C * M
      foodVal = (Number(box.food || 0) / 8) * C * M
      droneVal = (Number(box.drones || 0) / 8) * C * M
      droneBroodVal = (Number(box.drone_brood || 0) / 8) * C * M
      pollenVal = (Number(box.pollen || 0) / 8) * C * M
    }
    
    return {
      brood: broodVal.toFixed(0) + ' Stk.',
      bees: beeVal.toFixed(0) + ' Stk.',
      food: foodVal.toFixed(0) + ' g',
      drones: droneVal.toFixed(0) + ' Stk.',
      drone_brood: droneBroodVal.toFixed(0) + ' Stk.',
      pollen: pollenVal.toFixed(0) + ' g'
    }
  })
})

// Reset filters
function resetTableFilters() {
  tableFilters.startDate = ''
  tableFilters.endDate = ''
  tableFilters.apiaryId = ''
  tableFilters.locationId = ''
  tableFilters.hiveId = ''
  tableFilters.userId = ''
}

// Fetch lists
async function fetchSessions() {
  sessionsLoading.value = true
  try {
    const response = await axios.get('/api/logbook/sessions', {
      params: { apiary_id: apiaryStore.activeApiaryId }
    })
    sessions.value = response.data
    
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
    await fetchEntries()
  }
}

function selectSession(session) {
  selectedSession.value = session
  fetchEntries()
}

function openCreateSessionModal() {
  isEditSessionMode.value = false
  editingSessionId.value = null
  sessionForm.title = ''
  sessionForm.hiveId = ''
  showSessionModal.value = true
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function openEditSessionModal(session) {
  isEditSessionMode.value = true
  editingSessionId.value = session.id
  sessionForm.title = session.title
  sessionForm.hiveId = session.hive_id || ''
  showSessionModal.value = true
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

async function submitSessionForm() {
  if (!sessionForm.title.trim()) return
  if (sessionForm.title.trim().length > 30) {
    if (errorStore && typeof errorStore.showError === 'function') {
      errorStore.showError('Die Bezeichnung darf maximal 30 Zeichen lang sein.')
    } else {
      alert('Die Bezeichnung darf maximal 30 Zeichen lang sein.')
    }
    return
  }
  try {
    if (isEditSessionMode.value) {
      const response = await axios.put(`/api/logbook/sessions/${editingSessionId.value}`, {
        title: sessionForm.title.trim(),
        hive_id: sessionForm.hiveId || null
      })
      
      // Update selectedSession if it is the one being renamed
      if (selectedSession.value?.id === editingSessionId.value) {
        selectedSession.value = response.data
      }
      
      showSessionModal.value = false
      await fetchSessions()
    } else {
      const session = await axios.post('/api/logbook/sessions', {
        title: sessionForm.title.trim(),
        hive_id: sessionForm.hiveId || null
      }, {
        params: { apiary_id: apiaryStore.activeApiaryId }
      })
      
      showSessionModal.value = false
      await fetchSessions()
      selectSession(session.data)
    }
  } catch (err) {
    console.error('Session form submission failed:', err)
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
  
  entryForm.hiveId = selectedSession.value?.hive_id || (hives.value[0]?.id || '')
  entryForm.date = new Date().toISOString().substring(0, 10)
  entryForm.entryType = 'INSPECTION'
  entryForm.notes = ''
  entryForm.inspectionDetail.assessmentMode = 'boxes'
  entryForm.inspectionDetail.boxMode = 'exact'
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
    const hive = hives.value.find(h => h.id === entry.hive_id)

    entryForm.inspectionDetail.boxes = (entry.inspection_detail.boxes || [])
      .sort((a, b) => (a.box_index ?? 0) - (b.box_index ?? 0))
      .map((b, idx) => {
        const hiveBox = hive?.boxes?.[b.box_index ?? idx]
        return {
          id: hiveBox?.id || `box-${idx}`,
          order: (b.box_index ?? idx) + 1,
          box_type: hiveBox?.box_type || 'BROOD',
          frame_count: hiveBox?.frame_count || 0,
          multiplier: hiveBox?.frame_type?.multiplier || 1.0,
          frame_type_name: hiveBox?.frame_type?.name || 'Zarge',
          brood: b.brood_total ?? 0,
          bees: b.bee_total ?? 0,
          food: b.food_total ?? 0,
          drones: b.drone_total ?? 0,
          drone_brood: b.drone_brood_total ?? 0,
          pollen: b.pollen_total ?? 0
        }
      })

    entryForm.inspectionDetail.assessmentMode = 'boxes'

    const anyEighths = (entry.inspection_detail.boxes || []).some(b =>
      b.brood_eighths != null ||
      b.bee_eighths != null ||
      b.food_eighths != null ||
      b.drone_eighths != null ||
      b.drone_brood_eighths != null ||
      b.pollen_eighths != null
    )
    entryForm.inspectionDetail.boxMode = anyEighths ? 'eighths' : 'exact'
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

  // Build box-level inputs if the hive has boxes
  if (hive.boxes && hive.boxes.length > 0) {
    entryForm.inspectionDetail.boxes = hive.boxes.map(box => ({
      id: box.id,
      order: box.order,
      box_type: box.box_type,
      frame_count: box.frame_count,
      multiplier: box.frame_type?.multiplier || 1.0,
      frame_type_name: box.frame_type?.name || 'Standard',
      brood: 0,
      bees: 0,
      food: 0,
      drones: 0,
      drone_brood: 0,
      pollen: 0
    }))
  } else {
    // If no boxes are configured, empty the boxes and force frames mode
    entryForm.inspectionDetail.boxes = []
    entryForm.inspectionDetail.assessmentMode = 'frames'
  }

  // nothing to do for frames anymore – boxes are precomputed elsewhere
}

async function submitEntryForm() {
  try {
    const isExact = entryForm.inspectionDetail.boxMode === 'exact'
    const EIGHTH_FACTOR = 1

    const payload = {
      hive_id: entryForm.hiveId,
      session_id: selectedSession.value ? selectedSession.value.id : null,
      date: entryForm.date,
      entry_type: entryForm.entryType,
      notes: entryForm.notes.trim() || null,
      inspection_detail: entryForm.entryType === 'INSPECTION' ? {
        boxes: entryForm.inspectionDetail.boxes.map((box, idx) => {
          const broodVal = Number(box.brood || 0)
          const beeVal = Number(box.bees || 0)
          const foodVal = Number(box.food || 0)
          const droneVal = Number(box.drones || 0)
          const droneBroodVal = Number(box.drone_brood || 0)
          const pollenVal = Number(box.pollen || 0)

          // Eingabe = Achtel, Übersicht = Summe (in Achteln)
          // -> Totals = Achtel-Summen, Overview summiert diese
          const broodTotal = isExact ? broodVal : broodVal * EIGHTH_FACTOR
          const beeTotal = isExact ? beeVal : beeVal * EIGHTH_FACTOR
          const foodTotal = isExact ? foodVal : foodVal * EIGHTH_FACTOR
          const droneTotal = isExact ? droneVal : droneVal * EIGHTH_FACTOR
          const droneBroodTotal = isExact ? droneBroodVal : droneBroodVal * EIGHTH_FACTOR
          const pollenTotal = isExact ? pollenVal : pollenVal * EIGHTH_FACTOR

          return {
            box_index: idx,
            brood_total: broodTotal,
            bee_total: beeTotal,
            drone_total: droneTotal,
            drone_brood_total: droneBroodTotal,
            pollen_total: pollenTotal,
            food_total: foodTotal,

            brood_eighths: isExact ? null : broodVal,
            bee_eighths: isExact ? null : beeVal,
            drone_eighths: isExact ? null : droneVal,
            drone_brood_eighths: isExact ? null : droneBroodVal,
            pollen_eighths: isExact ? null : pollenVal,
            food_eighths: isExact ? null : foodVal
          }
        })
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
    await refreshCurrentEntries()
  } catch (err) {
    errorStore.showError('Fehler beim Speichern des Eintrags.', err, 'Eintrag speichern')
  }
}

async function deleteEntry(entry) {
  if (!confirm('Möchtest du diesen Eintrag und alle verknüpften Messwerte und Fotos wirklich löschen?')) return
  try {
    await axios.delete(`/api/logbook/entries/${entry.id}`)
    await refreshCurrentEntries()
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
    await refreshCurrentEntries()
  } catch (err) {
    errorStore.showError('Bilderupload fehlgeschlagen.', err, 'Bilder-Upload')
  }
}

async function deleteEntryImage(imageId) {
  if (!confirm('Bild wirklich löschen?')) return
  try {
    await axios.delete(`/api/logbook/images/${imageId}`)
    await refreshCurrentEntries()
  } catch (err) {
    console.error('Delete image failed:', err)
  }
}

function onApplyDraft(draft) {
  isEditEntryMode.value = false
  editingEntryId.value = null
  
  rightTab.value = 'entries'
  
  let targetHiveId = hives.value[0]?.id || ''
  if (draft.hive_name) {
    const matched = hives.value.find(h => h.name.toLowerCase() === draft.hive_name.toLowerCase())
    if (matched) targetHiveId = matched.id
  }
  
  entryForm.hiveId = targetHiveId
  entryForm.date = draft.date || new Date().toISOString().substring(0, 10)
  entryForm.entryType = draft.entry_type || 'INSPECTION'
  entryForm.notes = draft.notes || ''
  
  if (draft.entry_type === 'INSPECTION' && draft.inspection_detail) {
    entryForm.inspectionDetail.assessmentMode = 'frames'
    entryForm.inspectionDetail.frames = (draft.inspection_detail.frames || []).map((f, i) => ({
      frame_number: f.frame_number || (i + 1),
      side: f.side || 1,
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

function getBoxTotalsForEntry(entry) {
  if (!entry.inspection_detail || !entry.inspection_detail.boxes) return null

  const boxes = [...entry.inspection_detail.boxes]
    .sort((a, b) => (a.box_index ?? 0) - (b.box_index ?? 0))
    .map((b, idx) => ({
      id: b.id || `box-${idx}`,
      order: (b.box_index ?? idx) + 1,
      box_type: 'BROOD',
      frame_count: 0,
      multiplier: 1.0,
      frame_type_name: 'Zarge',
      brood: b.brood_total ?? 0,
      bees: b.bee_total ?? 0,
      food: b.food_total ?? 0,
      drones: b.drone_total ?? 0,
      drone_brood: b.drone_brood_total ?? 0,
      pollen: b.pollen_total ?? 0
    }))

  const hiveTotal = {
    brood: boxes.reduce((acc, b) => acc + b.brood, 0),
    bees: boxes.reduce((acc, b) => acc + b.bees, 0),
    food: boxes.reduce((acc, b) => acc + b.food, 0),
    drones: boxes.reduce((acc, b) => acc + b.drones, 0),
    drone_brood: boxes.reduce((acc, b) => acc + b.drone_brood, 0),
    pollen: boxes.reduce((acc, b) => acc + b.pollen, 0)
  }

  return {
    boxes,
    hive: hiveTotal
  }
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
