<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 font-sans">
    
    <!-- Back to Dashboard Link -->
    <router-link to="/dashboard" class="inline-flex items-center text-sm font-semibold text-primary hover:text-primary-hover mb-4 transition-colors duration-200">
      <svg class="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"/></svg>
      Zurück zum Dashboard
    </router-link>

    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-extrabold text-gray-900 dark:text-white tracking-tight">⚙️ Administration</h1>
      <p class="text-gray-500 dark:text-gray-400 mt-1">Verwalte Benutzerkonten, passe System-Prompts an und steuere API-Integrationen.</p>
    </div>

    <!-- Toast Notifications -->
    <TransitionGroup 
      name="list" 
      tag="div" 
      class="fixed bottom-5 right-5 z-50 space-y-2 pointer-events-none"
    >
      <div 
        v-for="t in toasts" 
        :key="t.id" 
        class="flex items-center space-x-3 px-4 py-3 rounded-xl shadow-lg border text-sm font-semibold pointer-events-auto backdrop-blur-md"
        :class="[
          t.type === 'success' 
            ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-600 dark:text-emerald-400' 
            : 'bg-rose-500/10 border-rose-500/20 text-rose-600 dark:text-rose-400'
        ]"
      >
        <span>{{ t.type === 'success' ? '✅' : '⚠️' }}</span>
        <span>{{ t.message }}</span>
      </div>
    </TransitionGroup>

    <!-- Tabs Dock -->
    <div class="flex border-b border-gray-200 dark:border-dark-border mb-8 space-x-6">
      <button 
        @click="activeTab = 'users'"
        class="pb-4 text-sm font-bold tracking-wide border-b-2 transition-all duration-200"
        :class="[
          activeTab === 'users' 
            ? 'border-primary text-primary' 
            : 'border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
        ]"
      >
        👤 Benutzerverwaltung
      </button>
      <button 
        @click="activeTab = 'llm'"
        class="pb-4 text-sm font-bold tracking-wide border-b-2 transition-all duration-200"
        :class="[
          activeTab === 'llm' 
            ? 'border-primary text-primary' 
            : 'border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
        ]"
      >
        🐝 Bee-Agent & KI
      </button>
      <button 
        @click="activeTab = 'finance'"
        class="pb-4 text-sm font-bold tracking-wide border-b-2 transition-all duration-200"
        :class="[
          activeTab === 'finance' 
            ? 'border-primary text-primary' 
            : 'border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
        ]"
      >
        💼 Finanzen & Steuern
      </button>
      <button 
        @click="activeTab = 'frame-types'"
        class="pb-4 text-sm font-bold tracking-wide border-b-2 transition-all duration-200"
        :class="[
          activeTab === 'frame-types' 
            ? 'border-primary text-primary' 
            : 'border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
        ]"
      >
        📏 Wabenmaße
      </button>
      <button 
        @click="activeTab = 'number-ranges'"
        class="pb-4 text-sm font-bold tracking-wide border-b-2 transition-all duration-200"
        :class="[
          activeTab === 'number-ranges' 
            ? 'border-primary text-primary' 
            : 'border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
        ]"
      >
        🔢 Nummernkreise
      </button>
    </div>

    <!-- Tab Content: User Management -->
    <div v-if="activeTab === 'users'" class="space-y-6">
      <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-6 shadow-sm">
        <h2 class="text-lg font-bold text-gray-900 dark:text-white">Neuen Benutzer anlegen</h2>
        <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">Als Administrator kannst du hier neue Benutzerkonten erstellen.</p>

        <form @submit.prevent="createUser" class="mt-5 grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">Benutzername *</label>
            <input v-model="newUserForm.username" type="text" required class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary" />
          </div>
          <div>
            <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">E-Mail *</label>
            <input v-model="newUserForm.email" type="email" required class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary" />
          </div>
          <div>
            <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">Vorname</label>
            <input v-model="newUserForm.first_name" type="text" class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary" />
          </div>
          <div>
            <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">Nachname</label>
            <input v-model="newUserForm.last_name" type="text" class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary" />
          </div>
          <div>
            <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">Passwort *</label>
            <input v-model="newUserForm.password" type="password" minlength="8" required class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary" />
          </div>
          <div>
            <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">Rolle *</label>
            <select v-model="newUserForm.role" class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary">
              <option value="USER">USER</option>
              <option value="SYSTEM_ADMIN">SYSTEM_ADMIN</option>
            </select>
          </div>
          <div class="md:col-span-2 flex justify-end">
            <button type="submit" :disabled="creatingUser" class="px-5 py-2.5 bg-primary hover:bg-primary-hover text-white text-sm font-bold rounded-xl transition duration-200 disabled:opacity-60">
              {{ creatingUser ? 'Erstelle...' : 'Benutzer erstellen' }}
            </button>
          </div>
        </form>
      </div>

      <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl overflow-hidden shadow-sm">
        <div class="px-6 py-5 border-b border-gray-100 dark:border-dark-border">
          <h2 class="text-lg font-bold text-gray-900 dark:text-white">Registrierte Benutzer</h2>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">Aktiviere/Deaktiviere Konten und verwalte die System-Administratorrechte der Benutzer.</p>
        </div>

        <div v-if="loadingUsers" class="flex flex-col items-center justify-center py-20">
          <svg class="animate-spin h-8 w-8 text-primary mb-3" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
          <span class="text-xs text-gray-400 font-bold">Lade Benutzerdaten...</span>
        </div>

        <div v-else class="overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="bg-gray-50 dark:bg-dark-bg text-gray-500 dark:text-gray-400 text-[10px] font-bold uppercase tracking-wider border-b border-gray-100 dark:border-dark-border">
                <th class="px-6 py-4">Benutzername</th>
                <th class="px-6 py-4">Name</th>
                <th class="px-6 py-4">E-Mail-Adresse</th>
                <th class="px-6 py-4 text-center">Status</th>
                <th class="px-6 py-4 text-center">Rolle</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100 dark:divide-dark-border text-sm">
              <tr 
                v-for="u in sortedUsers" 
                :key="u.id" 
                class="hover:bg-gray-50/50 dark:hover:bg-dark-bg/30 transition-colors duration-150"
              >
                <!-- Username -->
                <td class="px-6 py-4 font-bold text-gray-800 dark:text-gray-200">
                  <div class="flex items-center space-x-2">
                    <span>{{ u.username }}</span>
                    <span 
                      v-if="u.id === authStore.user?.id" 
                      class="text-[9px] bg-primary/10 text-primary px-1.5 py-0.5 rounded font-black tracking-wide uppercase"
                    >
                      Du
                    </span>
                  </div>
                </td>
                
                <!-- Name -->
                <td class="px-6 py-4 text-gray-600 dark:text-gray-300">
                  {{ u.first_name || '-' }} {{ u.last_name || '' }}
                </td>
                
                <!-- Email -->
                <td class="px-6 py-4 text-gray-500 dark:text-gray-400">
                  {{ u.email }}
                </td>
                
                <!-- Active Toggle -->
                <td class="px-6 py-4">
                  <div class="flex items-center justify-center">
                    <button 
                      @click="toggleUserActive(u)" 
                      :disabled="u.id === authStore.user?.id || togglingUser === u.id"
                      class="relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none"
                      :class="[
                        u.is_active ? 'bg-emerald-500' : 'bg-gray-300 dark:bg-gray-700',
                        (u.id === authStore.user?.id) ? 'opacity-40 cursor-not-allowed' : ''
                      ]"
                    >
                      <span class="sr-only">Status ändern</span>
                      <span 
                        class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out"
                        :class="u.is_active ? 'translate-x-5' : 'translate-x-0'"
                      />
                    </button>
                    <span 
                      v-if="u.id === authStore.user?.id" 
                      class="ml-2 text-gray-400 text-xs cursor-help" 
                      title="Du kannst dein eigenes Konto nicht deaktivieren"
                    >
                      🔒
                    </span>
                  </div>
                </td>
                
                <!-- Role Toggle -->
                <td class="px-6 py-4">
                  <div class="flex items-center justify-center">
                    <select 
                      v-model="u.role" 
                      @change="changeUserRole(u)"
                      :disabled="u.id === authStore.user?.id || togglingUser === u.id"
                      class="px-2 py-1 bg-white dark:bg-dark-bg border border-gray-300 dark:border-gray-700 rounded-lg text-xs font-semibold focus:outline-none focus:ring-1 focus:ring-primary cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed text-gray-800 dark:text-gray-200"
                    >
                      <option value="USER">USER</option>
                      <option value="SYSTEM_ADMIN">SYSTEM_ADMIN</option>
                    </select>
                    <span 
                      v-if="u.id === authStore.user?.id" 
                      class="ml-2 text-gray-400 text-xs cursor-help" 
                      title="Du kannst deine eigene Administrator-Rolle nicht entziehen"
                    >
                      🔒
                    </span>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Tab Content: LLM & Weather Configuration -->
    <div v-if="activeTab === 'llm'" class="space-y-6">
      
      <div v-if="loadingLLM" class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-16 flex flex-col items-center justify-center shadow-sm">
        <svg class="animate-spin h-10 w-10 text-primary mb-4" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
        <span class="text-sm text-gray-400 font-bold">Lade Systemkonfiguration...</span>
      </div>

      <div v-else class="grid grid-cols-1 gap-8">
        
        <!-- Live Weather API Switch -->
        <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-6 shadow-sm space-y-4">
          <div class="flex items-start justify-between">
            <div class="space-y-1">
              <h3 class="text-base font-bold text-gray-900 dark:text-white flex items-center">
                <span>🌦️ Echtzeit-Wetter abrufen</span>
                <span class="ml-2 text-[10px] bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 px-1.5 py-0.5 rounded uppercase font-black">OpenWeatherMap API</span>
              </h3>
              <p class="text-xs text-gray-500 dark:text-gray-400 max-w-2xl">
                Wenn aktiviert, fragt der KI-Assistent bei Standortabfragen die aktuellen Wetterbedingungen an den Koordinaten der Stände ab.
                Der API-Schlüssel wird sicher über die Server-Umgebungsvariablen (<code>.env</code>) konfiguriert.
              </p>
            </div>
            
            <button 
              @click="llmConfig.enable_weather_api = !llmConfig.enable_weather_api" 
              class="relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none"
              :class="llmConfig.enable_weather_api ? 'bg-emerald-500' : 'bg-gray-300 dark:bg-gray-700'"
            >
              <span class="sr-only">Wetter aktivieren</span>
              <span 
                class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out"
                :class="llmConfig.enable_weather_api ? 'translate-x-5' : 'translate-x-0'"
              />
            </button>
          </div>
        </div>

        <!-- AI Insights Cron Jobs -->
        <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-6 shadow-sm space-y-4">
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-base font-bold text-gray-900 dark:text-white">🕒 KI-Insights Cron-Aufträge</h3>
              <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">Lege mehrere Zeitpläne an. Jeder aktive Auftrag erzeugt automatisch Insights für alle Imkereien.</p>
            </div>
            <button
              @click="openCreateAIInsightJob"
              class="px-3 py-2 bg-primary hover:bg-primary-hover text-white rounded-xl text-xs font-bold"
            >
              + Neuer Auftrag
            </button>
          </div>

          <div v-if="loadingAIInsightJobs" class="text-xs text-gray-400 font-bold">Lade Cron-Aufträge...</div>
          <div v-else-if="aiInsightJobs.length === 0" class="text-xs text-gray-500 dark:text-gray-400">Noch keine Aufträge vorhanden.</div>
          <div v-else class="space-y-2">
            <div
              v-for="job in aiInsightJobs"
              :key="job.id"
              class="border border-gray-200 dark:border-dark-border rounded-xl p-3 flex items-center justify-between gap-3"
            >
              <div class="min-w-0">
                <div class="text-sm font-bold text-gray-900 dark:text-white truncate">{{ job.name }}</div>
                <div class="text-xs font-mono text-gray-500 dark:text-gray-400">{{ job.cron_expression }}</div>
                <div class="mt-1 flex flex-wrap gap-1">
                  <span v-if="job.inject_weather" class="px-1.5 py-0.5 rounded bg-sky-500/10 text-sky-700 dark:text-sky-300 text-[10px] font-bold">Weather</span>
                  <span v-if="job.inject_apiary" class="px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-700 dark:text-amber-300 text-[10px] font-bold">Imkerei</span>
                  <span v-if="job.inject_locations" class="px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-700 dark:text-emerald-300 text-[10px] font-bold">Standorte</span>
                  <span v-if="job.inject_hives" class="px-1.5 py-0.5 rounded bg-indigo-500/10 text-indigo-700 dark:text-indigo-300 text-[10px] font-bold">Voelker</span>
                  <span v-if="job.inject_log_entries" class="px-1.5 py-0.5 rounded bg-rose-500/10 text-rose-700 dark:text-rose-300 text-[10px] font-bold">Logs: {{ job.log_scope }} ({{ job.max_log_entries }})</span>
                </div>
              </div>
              <div class="flex items-center gap-2">
                <span
                  class="px-2 py-0.5 rounded-full text-[10px] font-bold"
                  :class="job.is_active ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400' : 'bg-gray-200 dark:bg-gray-700 text-gray-500'"
                >
                  {{ job.is_active ? 'Aktiv' : 'Inaktiv' }}
                </span>
                <button @click="openEditAIInsightJob(job)" class="px-2 py-1 text-xs font-bold border border-gray-300 dark:border-gray-700 rounded-lg">Bearbeiten</button>
                <button @click="deleteAIInsightJob(job)" class="px-2 py-1 text-xs font-bold border border-red-300 dark:border-red-900/60 text-red-600 dark:text-red-300 rounded-lg">Löschen</button>
              </div>
            </div>
          </div>

          <div v-if="showAIInsightJobForm" class="border border-gray-200 dark:border-dark-border rounded-2xl p-4 space-y-3">
            <div class="text-sm font-bold text-gray-900 dark:text-white">{{ editingAIInsightJobId ? 'Auftrag bearbeiten' : 'Neuen Auftrag erstellen' }}</div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div>
                <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">Name</label>
                <input v-model="aiInsightJobForm.name" type="text" class="w-full px-3 py-2 border border-gray-300 dark:border-dark-border dark:bg-dark-bg dark:text-white rounded-xl text-sm" />
              </div>
              <div>
                <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">Cron</label>
                <input v-model="aiInsightJobForm.cron_expression" type="text" placeholder="0 */12 * * *" class="w-full px-3 py-2 border border-gray-300 dark:border-dark-border dark:bg-dark-bg dark:text-white rounded-xl text-sm font-mono" />
                <p class="text-[11px] text-gray-500 dark:text-gray-400 mt-1">Format: MINUTE STUNDE TAG MONAT WOCHENTAG</p>
                <p v-if="aiInsightJobForm.cron_expression.trim() && !isAIInsightCronValid" class="text-[11px] text-rose-600 dark:text-rose-400 mt-1">
                  Ungültiges Cron-Format. Erwartet werden 5 durch Leerzeichen getrennte Felder.
                </p>
              </div>
            </div>
            <div>
              <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">Prompt</label>
              <textarea
                v-model="aiInsightJobForm.prompt"
                rows="4"
                class="w-full px-3 py-2 border border-gray-300 dark:border-dark-border dark:bg-dark-bg dark:text-white rounded-xl text-sm"
                placeholder="Beschreibe, welche Analyse dieser Cron-Auftrag erstellen soll..."
              />
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <label class="flex items-center gap-2 text-xs font-semibold text-gray-700 dark:text-gray-300">
                <input v-model="aiInsightJobForm.inject_weather" type="checkbox" class="rounded" />
                Wetter injizieren
              </label>
              <label class="flex items-center gap-2 text-xs font-semibold text-gray-700 dark:text-gray-300">
                <input v-model="aiInsightJobForm.inject_apiary" type="checkbox" class="rounded" />
                Imkerei injizieren
              </label>
              <label class="flex items-center gap-2 text-xs font-semibold text-gray-700 dark:text-gray-300">
                <input v-model="aiInsightJobForm.inject_locations" type="checkbox" class="rounded" />
                Standorte injizieren
              </label>
              <label class="flex items-center gap-2 text-xs font-semibold text-gray-700 dark:text-gray-300">
                <input v-model="aiInsightJobForm.inject_hives" type="checkbox" class="rounded" />
                Voelker injizieren
              </label>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
              <label class="flex items-center gap-2 text-xs font-semibold text-gray-700 dark:text-gray-300 md:col-span-1">
                <input v-model="aiInsightJobForm.inject_log_entries" type="checkbox" class="rounded" />
                Logeintraege injizieren
              </label>
              <div class="md:col-span-1" v-if="aiInsightJobForm.inject_log_entries">
                <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">Log-Scope</label>
                <select v-model="aiInsightJobForm.log_scope" class="w-full px-3 py-2 border border-gray-300 dark:border-dark-border dark:bg-dark-bg dark:text-white rounded-xl text-sm">
                  <option value="IMKEREI">Imkerei</option>
                  <option value="STANDORT">Standort</option>
                  <option value="VOLK">Volk</option>
                </select>
              </div>
              <div class="md:col-span-1" v-if="aiInsightJobForm.inject_log_entries">
                <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">Max Logs</label>
                <input v-model.number="aiInsightJobForm.max_log_entries" type="number" min="1" max="500" class="w-full px-3 py-2 border border-gray-300 dark:border-dark-border dark:bg-dark-bg dark:text-white rounded-xl text-sm" />
              </div>
            </div>
            <label class="flex items-center gap-2 text-xs font-semibold text-gray-700 dark:text-gray-300">
              <input v-model="aiInsightJobForm.is_active" type="checkbox" class="rounded" />
              Auftrag aktiv
            </label>
            <div class="flex justify-end gap-2">
              <button @click="cancelAIInsightJobForm" class="px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-xl text-xs font-semibold">Abbrechen</button>
              <button @click="saveAIInsightJob" :disabled="savingAIInsightJob || !isAIInsightCronValid || !aiInsightJobForm.prompt.trim() || aiInsightJobForm.max_log_entries < 1 || aiInsightJobForm.max_log_entries > 500" class="px-3 py-2 bg-primary hover:bg-primary-hover text-white rounded-xl text-xs font-bold disabled:opacity-60">
                {{ savingAIInsightJob ? 'Speichere...' : 'Speichern' }}
              </button>
            </div>
          </div>
        </div>

        <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-6 shadow-sm space-y-2">
          <h3 class="text-base font-bold text-gray-900 dark:text-white">🧠 Bee-Agent Prompt-Template</h3>
          <p class="text-xs text-gray-500 dark:text-gray-400 max-w-2xl">
            Das Basis-Template wird zentral im Backend gepflegt und ist hier bewusst nicht editierbar. Für job-spezifische Anpassungen verwende in der Bee-Agent Job-Konfiguration das Feld "Spezielle Anweisung", das zusätzlich in den Prompt injiziert wird.
          </p>
        </div>

        <!-- Save Button Section -->
        <div class="flex items-center justify-end space-x-4">
          <button 
            @click="resetBeeAgentConfigToDefault"
            class="px-5 py-3 border border-gray-300 dark:border-gray-700 rounded-xl text-sm font-semibold hover:bg-gray-100 dark:hover:bg-dark-border text-gray-700 dark:text-gray-300 transition duration-200"
            :disabled="savingLLM"
          >
            Zurücksetzen auf Defaults
          </button>
          
          <button 
            @click="saveBeeAgentConfig"
            class="px-6 py-3 bg-primary hover:bg-primary-hover text-white rounded-xl text-sm font-bold transition duration-200 flex items-center space-x-2 shadow-lg shadow-primary/20 hover-scale disabled:opacity-50 disabled:cursor-not-allowed"
            :disabled="savingLLM"
          >
            <svg v-if="savingLLM" class="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
            <span>{{ savingLLM ? 'Speichere...' : 'Änderungen speichern' }}</span>
          </button>
        </div>

      </div>
    </div>

    <!-- Tab Content: Finance & Taxes -->
    <div v-if="activeTab === 'finance'" class="space-y-6">
      <div v-if="loadingLLM" class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-16 flex flex-col items-center justify-center shadow-sm">
        <svg class="animate-spin h-10 w-10 text-primary mb-4" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
        <span class="text-sm text-gray-400 font-bold">Lade Finanzkonfiguration...</span>
      </div>

      <div v-else class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-6 shadow-sm space-y-4">
        <div>
          <h3 class="text-base font-bold text-gray-900 dark:text-white flex items-center">
            <span>💼 Finanzen & Steuern</span>
          </h3>
          <p class="text-xs text-gray-500 dark:text-gray-400 max-w-2xl mt-1">
            Konfiguriere Währung, Steuersätze und ob in Verkäufen sowie Steuerexporten Steuern berechnet werden.
          </p>
        </div>

        <div class="flex items-center justify-between pt-2 border-t border-gray-100 dark:border-dark-border/60">
          <div class="space-y-0.5">
            <p class="text-sm font-semibold text-gray-700 dark:text-gray-200">Steuern berechnen</p>
            <p class="text-xs text-gray-500 dark:text-gray-400">
              Wenn deaktiviert, wird in Verkäufen und im Steuerexport stets mit 0% Steuer gearbeitet.
            </p>
          </div>
          <button
            @click="llmConfig.calculate_taxes = !llmConfig.calculate_taxes"
            class="relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ml-4"
            :class="llmConfig.calculate_taxes ? 'bg-emerald-500' : 'bg-gray-300 dark:bg-gray-700'"
          >
            <span class="sr-only">Steuerberechnung umschalten</span>
            <span
              class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out"
              :class="llmConfig.calculate_taxes ? 'translate-x-5' : 'translate-x-0'"
            />
          </button>
        </div>

        <div class="pt-2 border-t border-gray-100 dark:border-dark-border/60">
          <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">Währung</label>
          <p class="text-xs text-gray-500 dark:text-gray-400 mb-2">Währung für die Darstellung von Verkaufspreisen (z.B. EUR, USD, CHF, GBP).</p>
          <div class="flex gap-2">
            <select
              v-model="llmConfig.currency"
              class="px-3 py-2 border border-gray-300 dark:border-dark-border dark:bg-dark-bg dark:text-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="EUR">EUR – Euro</option>
              <option value="USD">USD – US Dollar</option>
              <option value="CHF">CHF – Schweizer Franken</option>
              <option value="GBP">GBP – Britisches Pfund</option>
              <option value="custom">Andere...</option>
            </select>
            <input
              v-if="llmConfig.currency === 'custom' || !['EUR','USD','CHF','GBP'].includes(llmConfig.currency)"
              v-model="llmConfig.currency"
              type="text"
              maxlength="10"
              placeholder="z.B. JPY"
              class="flex-1 px-3 py-2 border border-gray-300 dark:border-dark-border dark:bg-dark-bg dark:text-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary font-mono"
            />
          </div>
        </div>

        <div class="pt-2 border-t border-gray-100 dark:border-dark-border/60">
          <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">Steuersätze</label>
          <p class="text-xs text-gray-500 dark:text-gray-400 mb-2">Kommagetrennte Steuersätze in Prozent (0–100), die im Produktformular zur Auswahl stehen (z.B. <code class="bg-gray-100 dark:bg-dark-bg px-1 rounded font-mono">0.0,7.0,19.0</code>).</p>
          <input
            v-model="llmConfig.tax_rates"
            type="text"
            placeholder="z.B. 0.0,7.0,19.0"
            class="w-full px-3 py-2 border border-gray-300 dark:border-dark-border dark:bg-dark-bg dark:text-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary font-mono"
          />
        </div>

        <div class="flex items-center justify-end space-x-4 pt-2">
          <button
            @click="resetConfigToDefault"
            class="px-5 py-3 border border-gray-300 dark:border-gray-700 rounded-xl text-sm font-semibold hover:bg-gray-100 dark:hover:bg-dark-border text-gray-700 dark:text-gray-300 transition duration-200"
            :disabled="savingLLM"
          >
            Zurücksetzen auf Defaults
          </button>

          <button
            @click="saveLLMConfig"
            class="px-6 py-3 bg-primary hover:bg-primary-hover text-white rounded-xl text-sm font-bold transition duration-200 flex items-center space-x-2 shadow-lg shadow-primary/20 hover-scale disabled:opacity-50 disabled:cursor-not-allowed"
            :disabled="savingLLM"
          >
            <svg v-if="savingLLM" class="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
            <span>{{ savingLLM ? 'Speichere...' : 'Änderungen speichern' }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Tab Content: Frame Types Management -->
    <div v-if="activeTab === 'frame-types'" class="space-y-6">
      <div class="flex justify-between items-center bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-6 shadow-sm animate-scale">
        <div>
          <h2 class="text-lg font-bold text-gray-900 dark:text-white">📏 Wabenmaße & Multiplikatoren</h2>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">Verwalte Wabenmaße und definiere deren Umrechnungsfaktoren für Honig-, Brut- und Bienenvolumen bei der Beuteninspektion.</p>
        </div>
        <button 
          @click="openCreateFrameType" 
          class="px-4 py-2 bg-primary hover:bg-primary-hover text-white text-xs font-bold rounded-xl shadow-md flex items-center space-x-1 hover-scale"
        >
          <span>+ Neues Maß</span>
        </button>
      </div>

      <!-- Frame Type Form (embedded/inline) -->
      <div v-if="showFrameTypeForm" class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-6 shadow-sm">
        <h3 class="text-sm font-bold text-gray-900 dark:text-white mb-4">
          {{ isEditFrameType ? '📏 Wabenmaß bearbeiten' : '📏 Neues Wabenmaß anlegen' }}
        </h3>
        <form @submit.prevent="submitFrameTypeForm" class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">Bezeichnung *</label>
              <input 
                v-model="formFrameType.name" 
                type="text" 
                required 
                placeholder="z.B. Dadant Blatt, Zander..." 
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
            <div class="flex items-center pt-5">
              <label class="flex items-center space-x-2 cursor-pointer">
                <input 
                  v-model="formFrameType.is_default" 
                  type="checkbox" 
                  class="rounded text-primary focus:ring-primary h-4 w-4"
                />
                <span class="text-xs font-bold text-gray-700 dark:text-gray-300">Als Standard für neue Völker vorauswählen</span>
              </label>
            </div>
          </div>

          <div class="grid grid-cols-2 md:grid-cols-6 gap-4">
            <div>
              <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">Brut-Multiplikator *</label>
              <input 
                v-model.number="formFrameType.brood_multiplier" 
                type="number" 
                step="0.01" 
                min="0.1" 
                required 
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary font-mono"
              />
            </div>
            <div>
              <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">Futter-Multiplikator *</label>
              <input 
                v-model.number="formFrameType.food_multiplier" 
                type="number" 
                step="0.01" 
                min="0.1" 
                required 
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary font-mono"
              />
            </div>
            <div>
              <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">Bienen-Multiplikator *</label>
              <input 
                v-model.number="formFrameType.bee_multiplier" 
                type="number" 
                step="0.01" 
                min="0.1" 
                required 
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary font-mono"
              />
            </div>
            <div>
              <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">Drohnen-Multiplikator *</label>
              <input 
                v-model.number="formFrameType.drone_multiplier" 
                type="number" 
                step="0.01" 
                min="0.1" 
                required 
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary font-mono"
              />
            </div>
            <div>
              <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">Dr.Brut-Multiplikator *</label>
              <input 
                v-model.number="formFrameType.drone_brood_multiplier" 
                type="number" 
                step="0.01" 
                min="0.1" 
                required 
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary font-mono"
              />
            </div>
            <div>
              <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">Pollen-Multiplikator *</label>
              <input 
                v-model.number="formFrameType.pollen_multiplier" 
                type="number" 
                step="0.01" 
                min="0.1" 
                required 
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary font-mono"
              />
            </div>
          </div>

          <div class="flex justify-end space-x-3 pt-2">
            <button 
              type="button" 
              @click="showFrameTypeForm = false" 
              class="px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-xl text-xs font-semibold hover:bg-gray-100 dark:hover:bg-dark-border text-gray-700 dark:text-gray-300"
            >
              Abbrechen
            </button>
            <button 
              type="submit" 
              class="px-4 py-2 bg-primary hover:bg-primary-hover text-white text-xs font-bold rounded-xl shadow-md hover-scale"
              :disabled="savingFrameType"
            >
              Speichern
            </button>
          </div>
        </form>
      </div>

      <!-- Frame Types Table -->
      <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl overflow-hidden shadow-sm">
        <div v-if="loadingFrameTypes" class="flex flex-col items-center justify-center py-20">
          <svg class="animate-spin h-8 w-8 text-primary mb-3" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
          <span class="text-xs text-gray-400 font-bold">Lade Wabenmaße...</span>
        </div>

        <div v-else class="overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="bg-gray-50 dark:bg-dark-bg text-gray-500 dark:text-gray-400 text-[10px] font-bold uppercase tracking-wider border-b border-gray-100 dark:border-dark-border">
                <th class="px-6 py-4">Bezeichnung</th>
                <th class="px-6 py-4 text-center">Brut-Faktor</th>
                <th class="px-6 py-4 text-center">Futter-Faktor</th>
                <th class="px-6 py-4 text-center">Bienen-Faktor</th>
                <th class="px-6 py-4 text-center">Drohnen-Faktor</th>
                <th class="px-6 py-4 text-center">Dr.Brut-Faktor</th>
                <th class="px-6 py-4 text-center">Pollen-Faktor</th>
                <th class="px-6 py-4 text-center">Standard</th>
                <th class="px-6 py-4 text-right">Aktionen</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100 dark:divide-dark-border text-sm">
              <tr 
                v-for="ft in frameTypes" 
                :key="ft.id" 
                class="hover:bg-gray-50/50 dark:hover:bg-dark-bg/30 transition-colors duration-150"
              >
                <td class="px-6 py-4 font-bold text-gray-800 dark:text-gray-200">
                  {{ ft.name }}
                </td>
                <td class="px-6 py-4 text-center font-mono text-xs text-gray-600 dark:text-gray-300">
                  x{{ ft.brood_multiplier.toFixed(2) }}
                </td>
                <td class="px-6 py-4 text-center font-mono text-xs text-gray-600 dark:text-gray-300">
                  x{{ ft.food_multiplier.toFixed(2) }}
                </td>
                <td class="px-6 py-4 text-center font-mono text-xs text-gray-600 dark:text-gray-300">
                  x{{ ft.bee_multiplier.toFixed(2) }}
                </td>
                <td class="px-6 py-4 text-center font-mono text-xs text-gray-600 dark:text-gray-300">
                  x{{ (ft.drone_multiplier || 1.0).toFixed(2) }}
                </td>
                <td class="px-6 py-4 text-center font-mono text-xs text-gray-600 dark:text-gray-300">
                  x{{ (ft.drone_brood_multiplier || 1.0).toFixed(2) }}
                </td>
                <td class="px-6 py-4 text-center font-mono text-xs text-gray-600 dark:text-gray-300">
                  x{{ (ft.pollen_multiplier || 1.0).toFixed(2) }}
                </td>
                <td class="px-6 py-4 text-center">
                  <span v-if="ft.is_default" class="text-amber-500 font-bold text-lg" title="Standardmaß">★</span>
                  <span v-else class="text-gray-300 dark:text-gray-700">-</span>
                </td>
                <td class="px-6 py-4 text-right space-x-2">
                  <button 
                    @click="openEditFrameType(ft)" 
                    class="p-1.5 text-gray-500 hover:text-primary hover:bg-gray-100 dark:hover:bg-dark-border rounded-lg transition-all duration-150 inline-flex"
                    title="Bearbeiten"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/></svg>
                  </button>
                  <button 
                    @click="deleteFrameType(ft)" 
                    class="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-500/10 rounded-lg transition-all duration-150 inline-flex"
                    title="Löschen"
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

    <!-- Tab Content: Number Ranges Management -->
    <div v-if="activeTab === 'number-ranges'" class="space-y-6">
      <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-6 shadow-sm animate-scale flex flex-col md:flex-row justify-between items-start md:items-center space-y-4 md:space-y-0">
        <div>
          <h2 class="text-lg font-bold text-gray-900 dark:text-white">🔢 Nummernkreise</h2>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
            Definiere hier Prefix, Stellenanzahl und Zählerstände für deine Chargen- und Rückstellproben-IDs.
          </p>
        </div>
      </div>

      <!-- Edit Number Range Form (embedded/inline) -->
      <div v-if="showNumberRangeForm" class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-6 shadow-sm animate-scale">
        <h3 class="text-sm font-bold text-gray-900 dark:text-white mb-4">
          ✏️ Nummernkreis bearbeiten: {{ formNumberRange.name }}
        </h3>
        <form @submit.prevent="submitNumberRangeForm" class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">Prefix</label>
              <input 
                v-model="formNumberRange.prefix" 
                type="text" 
                placeholder="z.B. LOT-" 
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary font-mono"
              />
            </div>
            <div>
              <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">Aktueller Zählerstand *</label>
              <input 
                v-model.number="formNumberRange.current_value" 
                type="number" 
                min="1" 
                required 
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary font-mono"
              />
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">Stellenanzahl (Digits) *</label>
              <input 
                v-model.number="formNumberRange.digits" 
                type="number" 
                min="1" 
                max="10" 
                required 
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary font-mono"
              />
            </div>
            <div class="flex items-center pt-5">
              <label class="flex items-center space-x-2 cursor-pointer">
                <input 
                  v-model="formNumberRange.is_active" 
                  type="checkbox" 
                  class="rounded text-primary focus:ring-primary h-4 w-4"
                />
                <span class="text-xs font-bold text-gray-700 dark:text-gray-300">Nummernkreis aktivieren</span>
              </label>
            </div>
          </div>

          <!-- Preview -->
          <div class="p-3 bg-gray-50 dark:bg-dark-bg border border-gray-100 dark:border-dark-border rounded-xl">
            <span class="text-xs text-gray-500 dark:text-gray-400 font-bold block mb-1">Vorschau nächste Nummer:</span>
            <span class="font-mono text-sm font-bold text-amber-500">{{ previewNextNumber }}</span>
          </div>

          <div class="flex justify-end space-x-3 pt-2">
            <button 
              type="button" 
              @click="showNumberRangeForm = false" 
              class="px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-xl text-xs font-semibold hover:bg-gray-100 dark:hover:bg-dark-border text-gray-700 dark:text-gray-300"
            >
              Abbrechen
            </button>
            <button 
              type="submit" 
              class="px-5 py-2 bg-primary hover:bg-primary-hover text-white text-xs font-bold rounded-xl shadow-md hover-scale"
              :disabled="savingNumberRange"
            >
              Speichern
            </button>
          </div>
        </form>
      </div>

      <!-- Number Ranges Table -->
      <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl overflow-hidden shadow-sm">
        <div v-if="loadingNumberRanges" class="flex flex-col items-center justify-center py-20">
          <svg class="animate-spin h-8 w-8 text-primary mb-3" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
          <span class="text-xs text-gray-400 font-bold">Lade Nummernkreise...</span>
        </div>

        <div v-else class="overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="bg-gray-50 dark:bg-dark-bg text-gray-500 dark:text-gray-400 text-[10px] font-bold uppercase tracking-wider border-b border-gray-100 dark:border-dark-border">
                <th class="px-6 py-4">Bezeichnung</th>
                <th class="px-6 py-4">Prefix</th>
                <th class="px-6 py-4 text-center">Aktueller Wert</th>
                <th class="px-6 py-4 text-center">Stellen (Digits)</th>
                <th class="px-6 py-4 text-center">Nächste Nummer</th>
                <th class="px-6 py-4 text-center">Status</th>
                <th class="px-6 py-4 text-right">Aktionen</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100 dark:divide-dark-border text-sm">
              <tr 
                v-for="nr in numberRanges" 
                :key="nr.id" 
                class="hover:bg-gray-50/50 dark:hover:bg-dark-bg/30 transition-colors duration-150"
              >
                <td class="px-6 py-4 font-bold text-gray-800 dark:text-gray-200">
                  {{ nr.name }}
                </td>
                <td class="px-6 py-4 font-mono text-gray-600 dark:text-gray-300">
                  {{ nr.prefix || '-' }}
                </td>
                <td class="px-6 py-4 text-center font-mono text-gray-600 dark:text-gray-300">
                  {{ nr.current_value }}
                </td>
                <td class="px-6 py-4 text-center font-mono text-gray-600 dark:text-gray-300">
                  {{ nr.digits }}
                </td>
                <td class="px-6 py-4 text-center font-mono font-bold text-amber-500">
                  {{ nr.prefix || '' }}{{ String(nr.current_value).padStart(nr.digits, '0') }}
                </td>
                <td class="px-6 py-4 text-center">
                  <span 
                    class="px-2 py-0.5 rounded-full text-[10px] font-bold"
                    :class="nr.is_active ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400' : 'bg-rose-500/10 text-rose-600 dark:text-rose-400'"
                  >
                    {{ nr.is_active ? 'Aktiv' : 'Inaktiv' }}
                  </span>
                </td>
                <td class="px-6 py-4 text-right">
                  <button 
                    @click="openEditNumberRange(nr)" 
                    class="p-1.5 text-gray-500 hover:text-primary hover:bg-gray-100 dark:hover:bg-dark-border rounded-lg transition-all duration-150 inline-flex hover-scale"
                    title="Bearbeiten"
                  >
                    <svg class="w-4.5 h-4.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/></svg>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useConfirmStore } from '../stores/confirm'
import axios from 'axios'

const authStore = useAuthStore()
const confirmStore = useConfirmStore()

const activeTab = ref('users')

// Users States
const users = ref([])
const loadingUsers = ref(false)
const togglingUser = ref(null)
const creatingUser = ref(false)
const newUserForm = reactive({
  username: '',
  email: '',
  password: '',
  first_name: '',
  last_name: '',
  role: 'USER'
})

// LLM States
const llmConfig = ref({
  enable_weather_api: false,
  calculate_taxes: true,
  currency: 'EUR',
  tax_rates: '0.0,7.0,19.0'
})
const loadingLLM = ref(false)
const savingLLM = ref(false)

const aiInsightJobs = ref([])
const loadingAIInsightJobs = ref(false)
const savingAIInsightJob = ref(false)
const showAIInsightJobForm = ref(false)
const editingAIInsightJobId = ref(null)
const aiInsightJobForm = reactive({
  name: '',
  prompt: '',
  cron_expression: '0 */12 * * *',
  inject_weather: false,
  inject_locations: true,
  inject_apiary: true,
  inject_hives: true,
  inject_log_entries: true,
  log_scope: 'IMKEREI',
  max_log_entries: 20,
  is_active: true
})

function validateCronExpression(value) {
  const parts = value.trim().split(/\s+/)
  return parts.length === 5 && parts.every(p => p.length > 0)
}

const isAIInsightCronValid = computed(() => validateCronExpression(aiInsightJobForm.cron_expression || ''))

// Toast Notifications System
const toasts = ref([])
let toastId = 0

function showToast(message, type = 'success') {
  const id = toastId++
  toasts.value.push({ id, message, type })
  setTimeout(() => {
    toasts.value = toasts.value.filter(t => t.id !== id)
  }, 3500)
}

// Fetch Users List
async function fetchUsers() {
  loadingUsers.value = true
  try {
    const res = await axios.get('/api/admin/users')
    users.value = res.data
  } catch (err) {
    console.error('Fetch users error:', err)
    showToast('Fehler beim Laden der Benutzerliste', 'error')
  } finally {
    loadingUsers.value = false
  }
}

async function createUser() {
  creatingUser.value = true
  try {
    await axios.post('/api/admin/users', {
      username: newUserForm.username.trim(),
      email: newUserForm.email.trim(),
      password: newUserForm.password,
      first_name: newUserForm.first_name?.trim() || null,
      last_name: newUserForm.last_name?.trim() || null,
      role: newUserForm.role
    })
    showToast(`Benutzer '${newUserForm.username}' wurde erstellt.`)
    newUserForm.username = ''
    newUserForm.email = ''
    newUserForm.password = ''
    newUserForm.first_name = ''
    newUserForm.last_name = ''
    newUserForm.role = 'USER'
    await fetchUsers()
  } catch (err) {
    console.error('Create user error:', err)
    const errDetail = err.response?.data?.detail || 'Fehler beim Erstellen des Benutzers.'
    showToast(errDetail, 'error')
  } finally {
    creatingUser.value = false
  }
}

// Fetch LLM and Weather configs
async function fetchLLMConfig() {
  loadingLLM.value = true
  try {
    const res = await axios.get('/api/admin/llm-config')
    llmConfig.value = res.data
  } catch (err) {
    console.error('Fetch LLM config error:', err)
    showToast('Fehler beim Laden der System-Prompts', 'error')
  } finally {
    loadingLLM.value = false
  }
}

async function fetchAIInsightJobs() {
  loadingAIInsightJobs.value = true
  try {
    const res = await axios.get('/api/admin/ai-insight-jobs')
    aiInsightJobs.value = res.data
  } catch (err) {
    console.error('Fetch AI insight jobs error:', err)
    showToast('Fehler beim Laden der KI-Insights-Cron-Aufträge', 'error')
  } finally {
    loadingAIInsightJobs.value = false
  }
}

function openCreateAIInsightJob() {
  editingAIInsightJobId.value = null
  aiInsightJobForm.name = ''
  aiInsightJobForm.prompt = ''
  aiInsightJobForm.cron_expression = '0 */12 * * *'
  aiInsightJobForm.inject_weather = false
  aiInsightJobForm.inject_locations = true
  aiInsightJobForm.inject_apiary = true
  aiInsightJobForm.inject_hives = true
  aiInsightJobForm.inject_log_entries = true
  aiInsightJobForm.log_scope = 'IMKEREI'
  aiInsightJobForm.max_log_entries = 20
  aiInsightJobForm.is_active = true
  showAIInsightJobForm.value = true
}

function openEditAIInsightJob(job) {
  editingAIInsightJobId.value = job.id
  aiInsightJobForm.name = job.name
  aiInsightJobForm.prompt = job.prompt || ''
  aiInsightJobForm.cron_expression = job.cron_expression
  aiInsightJobForm.inject_weather = !!job.inject_weather
  aiInsightJobForm.inject_locations = !!job.inject_locations
  aiInsightJobForm.inject_apiary = !!job.inject_apiary
  aiInsightJobForm.inject_hives = !!job.inject_hives
  aiInsightJobForm.inject_log_entries = !!job.inject_log_entries
  aiInsightJobForm.log_scope = job.log_scope || 'IMKEREI'
  aiInsightJobForm.max_log_entries = Number(job.max_log_entries || 20)
  aiInsightJobForm.is_active = job.is_active
  showAIInsightJobForm.value = true
}

function cancelAIInsightJobForm() {
  showAIInsightJobForm.value = false
  editingAIInsightJobId.value = null
}

async function saveAIInsightJob() {
  if (!aiInsightJobForm.name.trim()) {
    showToast('Name darf nicht leer sein.', 'error')
    return
  }
  if (!aiInsightJobForm.cron_expression.trim()) {
    showToast('Cron-Ausdruck darf nicht leer sein.', 'error')
    return
  }
  if (!aiInsightJobForm.prompt.trim()) {
    showToast('Prompt darf nicht leer sein.', 'error')
    return
  }
  if (!validateCronExpression(aiInsightJobForm.cron_expression)) {
    showToast('Ungültiges Cron-Format. Bitte 5 Felder angeben.', 'error')
    return
  }
  if (aiInsightJobForm.max_log_entries < 1 || aiInsightJobForm.max_log_entries > 500) {
    showToast('Maximale Anzahl Logeintraege muss zwischen 1 und 500 liegen.', 'error')
    return
  }

  savingAIInsightJob.value = true
  try {
    const payload = {
      name: aiInsightJobForm.name.trim(),
      prompt: aiInsightJobForm.prompt.trim(),
      cron_expression: aiInsightJobForm.cron_expression.trim(),
      inject_weather: aiInsightJobForm.inject_weather,
      inject_locations: aiInsightJobForm.inject_locations,
      inject_apiary: aiInsightJobForm.inject_apiary,
      inject_hives: aiInsightJobForm.inject_hives,
      inject_log_entries: aiInsightJobForm.inject_log_entries,
      log_scope: aiInsightJobForm.log_scope,
      max_log_entries: aiInsightJobForm.max_log_entries,
      is_active: aiInsightJobForm.is_active
    }
    if (editingAIInsightJobId.value) {
      await axios.put(`/api/admin/ai-insight-jobs/${editingAIInsightJobId.value}`, payload)
      showToast('KI-Insights-Cron-Auftrag aktualisiert.')
    } else {
      await axios.post('/api/admin/ai-insight-jobs', payload)
      showToast('KI-Insights-Cron-Auftrag erstellt.')
    }
    cancelAIInsightJobForm()
    await fetchAIInsightJobs()
  } catch (err) {
    console.error('Save AI insight job error:', err)
    const msg = err.response?.data?.detail || 'Fehler beim Speichern des KI-Insights-Cron-Auftrags.'
    showToast(msg, 'error')
  } finally {
    savingAIInsightJob.value = false
  }
}

async function deleteAIInsightJob(job) {
  const confirmed = await confirmStore.ask({
    title: 'KI-Insights-Cron-Auftrag löschen',
    message: `Möchtest du den Auftrag '${job.name}' wirklich löschen?`,
    type: 'danger',
    confirmText: 'Ja, löschen'
  })
  if (!confirmed) return

  try {
    await axios.delete(`/api/admin/ai-insight-jobs/${job.id}`)
    showToast('KI-Insights-Cron-Auftrag gelöscht.')
    await fetchAIInsightJobs()
  } catch (err) {
    console.error('Delete AI insight job error:', err)
    const msg = err.response?.data?.detail || 'Fehler beim Löschen des KI-Insights-Cron-Auftrags.'
    showToast(msg, 'error')
  }
}

// Update active status for user
async function toggleUserActive(user) {
  togglingUser.value = user.id
  const originalStatus = user.is_active
  const targetStatus = !originalStatus
  try {
    const res = await axios.put(`/api/admin/users/${user.id}`, {
      is_active: targetStatus
    })
    user.is_active = res.data.is_active
    showToast(`Benutzer '${user.username}' erfolgreich ${user.is_active ? 'aktiviert' : 'deaktiviert'}.`)
  } catch (err) {
    console.error('Toggle active error:', err)
    const errDetail = err.response?.data?.detail || 'Fehler beim Ändern des Aktivitätsstatus.'
    showToast(errDetail, 'error')
    user.is_active = originalStatus // Rollback visual
  } finally {
    togglingUser.value = null
  }
}

// Change role for user
async function changeUserRole(user) {
  togglingUser.value = user.id
  const originalRole = user.role
  try {
    const res = await axios.put(`/api/admin/users/${user.id}`, {
      role: user.role
    })
    user.role = res.data.role
    showToast(`Rolle von '${user.username}' auf ${user.role} geändert.`)
  } catch (err) {
    console.error('Change role error:', err)
    const errDetail = err.response?.data?.detail || 'Fehler beim Ändern der Rolle.'
    showToast(errDetail, 'error')
    user.role = originalRole // Rollback visual
  } finally {
    togglingUser.value = null
  }
}

// Save dynamic system prompts and weather api switch
async function saveLLMConfig() {
  savingLLM.value = true
  try {
    const res = await axios.put('/api/admin/llm-config', {
      enable_weather_api: llmConfig.value.enable_weather_api,
      calculate_taxes: llmConfig.value.calculate_taxes,
      currency: llmConfig.value.currency,
      tax_rates: llmConfig.value.tax_rates
    })
    llmConfig.value = res.data
    showToast('KI- und Wettereinstellungen erfolgreich aktualisiert.')
  } catch (err) {
    console.error('Save config error:', err)
    const msg = err.response?.data?.detail || 'Fehler beim Aktualisieren der Einstellungen.'
    showToast(msg, 'error')
  } finally {
    savingLLM.value = false
  }
}

async function saveBeeAgentConfig() {
  savingLLM.value = true
  try {
    const res = await axios.put('/api/admin/llm-config', {
      enable_weather_api: llmConfig.value.enable_weather_api
    })
    llmConfig.value = res.data
    showToast('Bee-Agent Einstellungen erfolgreich aktualisiert.')
  } catch (err) {
    console.error('Save bee-agent config error:', err)
    const msg = err.response?.data?.detail || 'Fehler beim Aktualisieren der Bee-Agent Einstellungen.'
    showToast(msg, 'error')
  } finally {
    savingLLM.value = false
  }
}

function resetBeeAgentConfigToDefault() {
  llmConfig.value.enable_weather_api = false
  showToast('Bee-Agent Standardwerte temporär geladen. Zum Übernehmen "Änderungen speichern" klicken.', 'success')
}

// Restore editable admin settings to defaults
function resetConfigToDefault() {
  llmConfig.value.enable_weather_api = false
  llmConfig.value.calculate_taxes = true
  llmConfig.value.currency = 'EUR'
  llmConfig.value.tax_rates = '0.0,7.0,19.0'

  showToast('Standardwerte temporär geladen. Zum Übernehmen "Änderungen speichern" klicken.', 'success')
}

// Order users: admins first, then by username
const sortedUsers = computed(() => {
  return [...users.value].sort((a, b) => {
    if (a.role === 'SYSTEM_ADMIN' && b.role !== 'SYSTEM_ADMIN') return -1
    if (a.role !== 'SYSTEM_ADMIN' && b.role === 'SYSTEM_ADMIN') return 1
    return a.username.localeCompare(b.username)
  })
})

// Frame Types States
const frameTypes = ref([])
const loadingFrameTypes = ref(false)
const savingFrameType = ref(false)
const showFrameTypeForm = ref(false)
const isEditFrameType = ref(false)
const editingFrameTypeId = ref(null)

const formFrameType = reactive({
  name: '',
  is_default: false,
  brood_multiplier: 1.0,
  food_multiplier: 1.0,
  bee_multiplier: 1.0,
  drone_multiplier: 1.0,
  drone_brood_multiplier: 1.0,
  pollen_multiplier: 1.0
})

async function fetchFrameTypes() {
  loadingFrameTypes.value = true
  try {
    const res = await axios.get('/api/admin/frame-types')
    frameTypes.value = res.data
  } catch (err) {
    console.error('Fetch frame types error:', err)
    showToast('Fehler beim Laden der Wabenmaße', 'error')
  } finally {
    loadingFrameTypes.value = false
  }
}

function openCreateFrameType() {
  isEditFrameType.value = false
  editingFrameTypeId.value = null
  formFrameType.name = ''
  formFrameType.is_default = false
  formFrameType.brood_multiplier = 1.0
  formFrameType.food_multiplier = 1.0
  formFrameType.bee_multiplier = 1.0
  formFrameType.drone_multiplier = 1.0
  formFrameType.drone_brood_multiplier = 1.0
  formFrameType.pollen_multiplier = 1.0
  showFrameTypeForm.value = true
}

function openEditFrameType(ft) {
  isEditFrameType.value = true
  editingFrameTypeId.value = ft.id
  formFrameType.name = ft.name
  formFrameType.is_default = ft.is_default
  formFrameType.brood_multiplier = ft.brood_multiplier
  formFrameType.food_multiplier = ft.food_multiplier
  formFrameType.bee_multiplier = ft.bee_multiplier
  formFrameType.drone_multiplier = ft.drone_multiplier || 1.0
  formFrameType.drone_brood_multiplier = ft.drone_brood_multiplier || 1.0
  formFrameType.pollen_multiplier = ft.pollen_multiplier || 1.0
  showFrameTypeForm.value = true
}

async function submitFrameTypeForm() {
  savingFrameType.value = true
  try {
    const payload = {
      name: formFrameType.name,
      is_default: formFrameType.is_default,
      brood_multiplier: Number(formFrameType.brood_multiplier),
      food_multiplier: Number(formFrameType.food_multiplier),
      bee_multiplier: Number(formFrameType.bee_multiplier),
      drone_multiplier: Number(formFrameType.drone_multiplier),
      drone_brood_multiplier: Number(formFrameType.drone_brood_multiplier),
      pollen_multiplier: Number(formFrameType.pollen_multiplier)
    }
    if (isEditFrameType.value) {
      await axios.put(`/api/admin/frame-types/${editingFrameTypeId.value}`, payload)
      showToast(`Wabenmaß '${payload.name}' erfolgreich aktualisiert.`)
    } else {
      await axios.post('/api/admin/frame-types', payload)
      showToast(`Wabenmaß '${payload.name}' erfolgreich erstellt.`)
    }
    showFrameTypeForm.value = false
    await fetchFrameTypes()
  } catch (err) {
    console.error('Save frame type error:', err)
    const errDetail = err.response?.data?.detail || 'Fehler beim Speichern des Wabenmaßes.'
    showToast(errDetail, 'error')
  } finally {
    savingFrameType.value = false
  }
}

async function deleteFrameType(ft) {
  const confirmed = await confirmStore.ask({
    title: 'Wabenmaß löschen',
    message: `Möchtest du das Wabenmaß '${ft.name}' wirklich löschen?`,
    type: 'danger',
    confirmText: 'Ja, löschen'
  })
  if (!confirmed) {
    return
  }
  try {
    await axios.delete(`/api/admin/frame-types/${ft.id}`)
    showToast(`Wabenmaß '${ft.name}' erfolgreich gelöscht.`)
    await fetchFrameTypes()
  } catch (err) {
    console.error('Delete frame type error:', err)
    const errDetail = err.response?.data?.detail || 'Fehler beim Löschen des Wabenmaßes.'
    showToast(errDetail, 'error')
  }
}

// Number Ranges States
const numberRanges = ref([])
const loadingNumberRanges = ref(false)
const savingNumberRange = ref(false)
const showNumberRangeForm = ref(false)
const formNumberRange = reactive({
  id: '',
  name: '',
  prefix: '',
  current_value: 1,
  digits: 4,
  is_active: true
})

const previewNextNumber = computed(() => {
  const prefix = formNumberRange.prefix || ''
  const current = String(formNumberRange.current_value || 0)
  const digits = formNumberRange.digits || 4
  return prefix + current.padStart(digits, '0')
})

async function fetchNumberRanges() {
  loadingNumberRanges.value = true
  try {
    const res = await axios.get('/api/admin/number-ranges')
    numberRanges.value = res.data
  } catch (err) {
    console.error('Fetch number ranges error:', err)
    showToast('Fehler beim Laden der Nummernkreise', 'error')
  } finally {
    loadingNumberRanges.value = false
  }
}

function openEditNumberRange(nr) {
  formNumberRange.id = nr.id
  formNumberRange.name = nr.name
  formNumberRange.prefix = nr.prefix || ''
  formNumberRange.current_value = nr.current_value
  formNumberRange.digits = nr.digits
  formNumberRange.is_active = nr.is_active
  showNumberRangeForm.value = true
}

async function submitNumberRangeForm() {
  savingNumberRange.value = true
  try {
    const payload = {
      name: formNumberRange.name,
      prefix: formNumberRange.prefix || null,
      current_value: Number(formNumberRange.current_value),
      digits: Number(formNumberRange.digits),
      is_active: formNumberRange.is_active
    }
    await axios.put(`/api/admin/number-ranges/${formNumberRange.id}`, payload)
    showToast(`Nummernkreis '${payload.name}' erfolgreich aktualisiert.`)
    showNumberRangeForm.value = false
    await fetchNumberRanges()
  } catch (err) {
    console.error('Save number range error:', err)
    const errDetail = err.response?.data?.detail || 'Fehler beim Speichern des Nummernkreises.'
    showToast(errDetail, 'error')
  } finally {
    savingNumberRange.value = false
  }
}

onMounted(() => {
  fetchUsers()
  fetchLLMConfig()
  fetchAIInsightJobs()
  fetchFrameTypes()
  fetchNumberRanges()
})
</script>

<style scoped>
/* List Transitions for Toasts */
.list-enter-active,
.list-leave-active {
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
.list-enter-from {
  opacity: 0;
  transform: translateY(30px) scale(0.9);
}
.list-leave-to {
  opacity: 0;
  transform: scale(0.9);
}
</style>
