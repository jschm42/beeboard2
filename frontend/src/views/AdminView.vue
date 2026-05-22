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
        🤖 KI-Assistent & Wetter
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
      <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl overflow-hidden shadow-sm">
        <div class="px-6 py-5 border-b border-gray-100 dark:border-dark-border flex items-center justify-between gap-4">
          <div>
            <h2 class="text-lg font-bold text-gray-900 dark:text-white">Registrierte Benutzer</h2>
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">Aktiviere/Deaktiviere Konten und verwalte Benutzer inklusive Rollen, Profilen und Passwörtern.</p>
          </div>
          <button
            @click="openCreateUserDialog"
            class="px-4 py-2 bg-primary hover:bg-primary-hover text-white text-xs font-bold rounded-xl shadow-md"
          >
            + Benutzer anlegen
          </button>
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
                <th class="px-6 py-4 text-right">Aktionen</th>
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

                <td class="px-6 py-4 text-right space-x-2">
                  <button
                    @click="openEditUserDialog(u)"
                    class="p-1.5 text-gray-500 hover:text-primary hover:bg-gray-100 dark:hover:bg-dark-border rounded-lg transition-all duration-150 inline-flex"
                    title="Benutzer bearbeiten"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/></svg>
                  </button>
                  <button
                    @click="deleteUser(u)"
                    :disabled="u.id === authStore.user?.id"
                    class="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-500/10 rounded-lg transition-all duration-150 inline-flex disabled:opacity-40 disabled:cursor-not-allowed"
                    title="Benutzer löschen"
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
                Der API-Schlüssel kann in der Administration hinterlegt werden und überschreibt dann den Wert aus <code>.env</code>.
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

        <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-6 shadow-sm space-y-4">
          <div class="flex items-start justify-between gap-4 flex-wrap">
            <div>
              <h3 class="text-base font-bold text-gray-900 dark:text-white">🔐 API-Schlüssel und SMTP</h3>
              <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">DB-Werte sind verschlüsselt gespeichert und haben Vorrang vor <code>.env</code>.</p>
            </div>
            <div class="flex gap-2">
              <button @click="openApiKeyDialog" class="px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-xl text-xs font-semibold hover:bg-gray-100 dark:hover:bg-dark-border text-gray-700 dark:text-gray-300">API-Schlüssel verwalten</button>
              <button @click="openSmtpDialog" class="px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-xl text-xs font-semibold hover:bg-gray-100 dark:hover:bg-dark-border text-gray-700 dark:text-gray-300">SMTP konfigurieren</button>
            </div>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div v-for="provider in apiProviders" :key="provider" class="px-3 py-2 rounded-xl border border-gray-200 dark:border-dark-border text-xs">
              <div class="flex items-center justify-between">
                <span class="font-semibold text-gray-700 dark:text-gray-200">{{ provider }}</span>
                <span class="px-2 py-0.5 rounded-full text-[10px] font-bold" :class="apiSourceClass(provider)">{{ apiSourceLabel(provider) }}</span>
              </div>
              <div class="text-gray-500 dark:text-gray-400 mt-1">DB konfiguriert: {{ apiDbConfigured(provider) ? 'Ja' : 'Nein' }}</div>
              <div class="text-gray-500 dark:text-gray-400 mt-1">.env konfiguriert: {{ apiEnvConfigured(provider) ? 'Ja' : 'Nein' }}</div>
            </div>
            <div class="px-3 py-2 rounded-xl border border-gray-200 dark:border-dark-border text-xs">
              <div class="flex items-center justify-between">
                <span class="font-semibold text-gray-700 dark:text-gray-200">SMTP</span>
                <span class="px-2 py-0.5 rounded-full text-[10px] font-bold" :class="smtpSourceClass">{{ smtpSourceLabel }}</span>
              </div>
              <div class="text-gray-500 dark:text-gray-400 mt-1">DB konfiguriert: {{ smtpConfig.db_configured ? 'Ja' : 'Nein' }}</div>
              <div class="text-gray-500 dark:text-gray-400 mt-1">.env konfiguriert: {{ smtpConfig.env_configured ? 'Ja' : 'Nein' }}</div>
              <div class="text-gray-500 dark:text-gray-400 mt-1">SMTP-Benutzer gesetzt: {{ smtpConfig.username_configured ? 'Ja' : 'Nein' }}</div>
              <div class="text-gray-500 dark:text-gray-400 mt-1">SMTP-Passwort gesetzt: {{ smtpConfig.password_configured ? 'Ja' : 'Nein' }}</div>
            </div>
          </div>
        </div>

        <!-- Kleinunternehmer-Regelung Switch -->
        <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-6 shadow-sm space-y-4">
          <div class="flex items-start justify-between">
            <div class="space-y-1">
              <h3 class="text-base font-bold text-gray-900 dark:text-white flex items-center">
                <span>💼 Kleinunternehmer-Regelung (§ 19 UStG)</span>
              </h3>
              <p class="text-xs text-gray-500 dark:text-gray-400 max-w-2xl">
                Wenn aktiviert, wird bei Verkäufen und Steuerexporten keine Umsatzsteuer berechnet oder ausgewiesen.
              </p>
            </div>
            
            <button 
              @click="llmConfig.kleinunternehmer_regelung = !llmConfig.kleinunternehmer_regelung" 
              class="relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none"
              :class="llmConfig.kleinunternehmer_regelung ? 'bg-emerald-500' : 'bg-gray-300 dark:bg-gray-700'"
            >
              <span class="sr-only">Kleinunternehmer aktivieren</span>
              <span 
                class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out"
                :class="llmConfig.kleinunternehmer_regelung ? 'translate-x-5' : 'translate-x-0'"
              />
            </button>
          </div>
        </div>

        <!-- AI Insights Cron Config -->
        <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-6 shadow-sm">
          <div class="flex items-start justify-between">
            <div class="space-y-1">
              <h3 class="text-base font-bold text-gray-900 dark:text-white flex items-center">
                <span>🕒 AI-Insights Zeitplan</span>
                <span class="ml-2 text-[10px] bg-blue-500/10 text-blue-600 dark:text-blue-400 px-1.5 py-0.5 rounded uppercase font-black">
                  Cron-Format
                </span>
              </h3>
              <p class="text-xs text-gray-500 dark:text-gray-400 max-w-2xl">
                Lege fest, wann automatisch neue AI-Insights für deine Stände generiert werden.
                Verwende eine Cron-Expression im Format
                <code class="bg-gray-100 dark:bg-dark-bg px-1 py-0.5 rounded font-mono">MINUTE STUNDE TAG MONAT WOCHENTAG</code>.
                Beispiel: <code class="bg-gray-100 dark:bg-dark-bg px-1 py-0.5 rounded font-mono">0 */12 * * *</code> für alle 12 Stunden.
              </p>
            </div>
          </div>

          <div class="mt-4 grid grid-cols-1 md:grid-cols-[minmax(0,2fr)_minmax(0,1fr)] gap-4 items-center">
            <input
              v-model="llmConfig.ai_insights_cron"
              type="text"
              placeholder="z.B. 0 6 * * * (täglich um 06:00)"
              class="w-full px-3 py-2 border border-gray-300 dark:border-dark-border dark:bg-dark-bg dark:text-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary font-mono"
            />
            <div class="text-[11px] text-gray-500 dark:text-gray-400">
              <div class="font-semibold mb-1">Beispiele:</div>
              <ul class="space-y-0.5">
                <li><code class="bg-gray-100 dark:bg-dark-bg px-1 py-0.5 rounded font-mono">0 */12 * * *</code> – alle 12 Stunden</li>
                <li><code class="bg-gray-100 dark:bg-dark-bg px-1 py-0.5 rounded font-mono">0 6 * * *</code> – täglich um 06:00</li>
                <li><code class="bg-gray-100 dark:bg-dark-bg px-1 py-0.5 rounded font-mono">0 6,18 * * *</code> – 06:00 und 18:00</li>
              </ul>
            </div>
          </div>
        </div>

        <!-- Chatbot System Prompt Card -->
        <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-6 shadow-sm space-y-4">
          <div>
            <h3 class="text-base font-bold text-gray-900 dark:text-white">💬 Beekeeper Chatbot System-Prompt</h3>
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
              Definiert den Kerncharakter und das Verhalten des Beekeeper-Bots.
            </p>
          </div>

          <div class="relative">
            <textarea 
              v-model="llmConfig.chatbot_system_prompt" 
              rows="6"
              class="w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-700 bg-transparent text-sm focus:outline-none focus:ring-2 focus:ring-primary dark:text-white font-mono"
              placeholder="System-Prompt für den Chatbot eingeben..."
            ></textarea>
          </div>

          <!-- Helper Variables Info -->
          <div class="bg-amber-500/5 border border-amber-500/10 rounded-2xl p-4 flex items-start space-x-3 text-xs">
            <span class="text-base">💡</span>
            <div class="space-y-1 text-gray-600 dark:text-gray-300">
              <span class="font-bold text-gray-800 dark:text-white">Verfügbare Platzhaltervariablen:</span>
              <p class="mt-1">
                Du kannst die Variable <code class="bg-gray-100 dark:bg-dark-bg px-1 py-0.5 rounded font-mono font-bold">{context_str}</code> im Prompt einbinden. 
                Sie wird beim Aufruf durch die echten Bestandsdaten der Völker und die letzten Logbucheinträge ersetzt.
              </p>
            </div>
          </div>
        </div>

        <!-- Draft extraction System Prompt Card -->
        <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-6 shadow-sm space-y-4">
          <div>
            <h3 class="text-base font-bold text-gray-900 dark:text-white">📝 Notizen-Extraktor System-Prompt</h3>
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
              Definiert die Anweisungen, um unstrukturierte Freitexte in strukturierte JSON-Formularentwürfe zu extrahieren.
            </p>
          </div>

          <div class="relative">
            <textarea 
              v-model="llmConfig.draft_system_prompt" 
              rows="12"
              class="w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-700 bg-transparent text-sm focus:outline-none focus:ring-2 focus:ring-primary dark:text-white font-mono"
              placeholder="System-Prompt für den Entwurfsextraktor eingeben..."
            ></textarea>
          </div>

          <!-- Helper Variables Info -->
          <div class="bg-amber-500/5 border border-amber-500/10 rounded-2xl p-4 flex items-start space-x-3 text-xs">
            <span class="text-base">💡</span>
            <div class="space-y-1 text-gray-600 dark:text-gray-300">
              <span class="font-bold text-gray-800 dark:text-white">Verfügbare Platzhaltervariablen:</span>
              <p class="mt-1">
                Du kannst die Variable <code class="bg-gray-100 dark:bg-dark-bg px-1 py-0.5 rounded font-mono font-bold">{date_str}</code> im Prompt einbinden. 
                Sie wird automatisch durch das aktuelle Erstelldatum im ISO-Format (YYYY-MM-DD) ersetzt.
              </p>
            </div>
          </div>
        </div>

        <!-- Save Button Section -->
        <div class="flex items-center justify-end space-x-4">
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

    <div v-if="showUserDialog" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
      <div class="w-full max-w-2xl bg-white dark:bg-dark-card rounded-2xl border border-gray-200 dark:border-dark-border p-6 space-y-4">
        <h3 class="text-lg font-bold text-gray-900 dark:text-white">{{ isEditUser ? 'Benutzer bearbeiten' : 'Benutzer anlegen' }}</h3>
        <form @submit.prevent="submitUserForm" class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
            <input v-model="userForm.username" type="text" required placeholder="Benutzername" class="w-full px-3 py-2 border border-gray-300 dark:border-dark-border dark:bg-dark-bg dark:text-white rounded-xl text-sm" />
            <input v-model="userForm.email" type="email" required placeholder="E-Mail" class="w-full px-3 py-2 border border-gray-300 dark:border-dark-border dark:bg-dark-bg dark:text-white rounded-xl text-sm" />
            <input v-model="userForm.first_name" type="text" placeholder="Vorname" class="w-full px-3 py-2 border border-gray-300 dark:border-dark-border dark:bg-dark-bg dark:text-white rounded-xl text-sm" />
            <input v-model="userForm.last_name" type="text" placeholder="Nachname" class="w-full px-3 py-2 border border-gray-300 dark:border-dark-border dark:bg-dark-bg dark:text-white rounded-xl text-sm" />
            <input v-model="userForm.password" type="password" :required="!isEditUser" placeholder="Passwort (mind. 8 Zeichen)" class="w-full px-3 py-2 border border-gray-300 dark:border-dark-border dark:bg-dark-bg dark:text-white rounded-xl text-sm" />
            <select v-model="userForm.role" class="w-full px-3 py-2 border border-gray-300 dark:border-dark-border dark:bg-dark-bg dark:text-white rounded-xl text-sm">
              <option value="USER">USER</option>
              <option value="SYSTEM_ADMIN">SYSTEM_ADMIN</option>
            </select>
          </div>
          <label class="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
            <input v-model="userForm.is_active" type="checkbox" class="rounded text-primary" /> Aktiv
          </label>
          <div class="flex justify-end gap-2">
            <button type="button" @click="showUserDialog = false" class="px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-xl text-xs font-semibold">Abbrechen</button>
            <button type="submit" class="px-4 py-2 bg-primary hover:bg-primary-hover text-white rounded-xl text-xs font-bold" :disabled="savingUser">{{ savingUser ? 'Speichere...' : 'Speichern' }}</button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="showApiDialog" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
      <div class="w-full max-w-2xl bg-white dark:bg-dark-card rounded-2xl border border-gray-200 dark:border-dark-border p-6 space-y-4">
        <h3 class="text-lg font-bold text-gray-900 dark:text-white">API-Schlüssel verwalten</h3>
        <p class="text-xs text-gray-500 dark:text-gray-400">Neue Werte werden verschlüsselt gespeichert. Leeres Feld ändert nichts.</p>
        <div class="space-y-3">
          <div v-for="provider in apiProviders" :key="`dialog-${provider}`" class="space-y-1">
            <label class="text-xs font-semibold text-gray-700 dark:text-gray-300">{{ provider }}</label>
            <div class="flex gap-2">
              <input v-model="apiKeyForm[provider]" type="password" :placeholder="`Neuen ${provider}-Key eingeben`" class="flex-1 px-3 py-2 border border-gray-300 dark:border-dark-border dark:bg-dark-bg dark:text-white rounded-xl text-sm" />
              <button @click="clearApiKey(provider)" type="button" class="px-3 py-2 border border-gray-300 dark:border-dark-border rounded-xl text-xs font-semibold">DB-Key löschen</button>
            </div>
          </div>
        </div>
        <div class="flex justify-end gap-2">
          <button type="button" @click="showApiDialog = false" class="px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-xl text-xs font-semibold">Schließen</button>
          <button type="button" @click="saveApiKeys" class="px-4 py-2 bg-primary hover:bg-primary-hover text-white rounded-xl text-xs font-bold" :disabled="savingApiKeys">{{ savingApiKeys ? 'Speichere...' : 'Speichern' }}</button>
        </div>
      </div>
    </div>

    <div v-if="showSmtpDialog" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
      <div class="w-full max-w-2xl bg-white dark:bg-dark-card rounded-2xl border border-gray-200 dark:border-dark-border p-6 space-y-4">
        <h3 class="text-lg font-bold text-gray-900 dark:text-white">SMTP konfigurieren</h3>
        <p class="text-xs text-gray-500 dark:text-gray-400">Zugangsdaten werden verschlüsselt gespeichert. Leere Felder für Benutzer/Passwort löschen die DB-Werte.</p>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <input v-model="smtpForm.smtp_host" type="text" placeholder="SMTP Host" class="w-full px-3 py-2 border border-gray-300 dark:border-dark-border dark:bg-dark-bg dark:text-white rounded-xl text-sm" />
          <input v-model.number="smtpForm.smtp_port" type="number" min="1" max="65535" placeholder="Port" class="w-full px-3 py-2 border border-gray-300 dark:border-dark-border dark:bg-dark-bg dark:text-white rounded-xl text-sm" />
          <input v-model="smtpForm.smtp_from_email" type="email" placeholder="Absender-E-Mail" class="w-full px-3 py-2 border border-gray-300 dark:border-dark-border dark:bg-dark-bg dark:text-white rounded-xl text-sm" />
          <input v-model="smtpForm.smtp_username" type="text" placeholder="SMTP Benutzername" class="w-full px-3 py-2 border border-gray-300 dark:border-dark-border dark:bg-dark-bg dark:text-white rounded-xl text-sm" />
          <input v-model="smtpForm.smtp_password" type="password" placeholder="SMTP Passwort" class="w-full px-3 py-2 border border-gray-300 dark:border-dark-border dark:bg-dark-bg dark:text-white rounded-xl text-sm md:col-span-2" />
        </div>
        <div class="flex gap-4 text-sm text-gray-700 dark:text-gray-300">
          <label class="flex items-center gap-2"><input v-model="smtpForm.smtp_use_tls" type="checkbox" class="rounded text-primary" /> TLS</label>
          <label class="flex items-center gap-2"><input v-model="smtpForm.smtp_use_ssl" type="checkbox" class="rounded text-primary" /> SSL</label>
        </div>
        <div class="flex justify-end gap-2">
          <button type="button" @click="showSmtpDialog = false" class="px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-xl text-xs font-semibold">Schließen</button>
          <button type="button" @click="saveSmtpConfig" class="px-4 py-2 bg-primary hover:bg-primary-hover text-white rounded-xl text-xs font-bold" :disabled="savingSmtp">{{ savingSmtp ? 'Speichere...' : 'Speichern' }}</button>
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
const showUserDialog = ref(false)
const isEditUser = ref(false)
const editingUserId = ref(null)
const savingUser = ref(false)
const userForm = reactive({
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  password: '',
  role: 'USER',
  is_active: true
})

const showApiDialog = ref(false)
const savingApiKeys = ref(false)
const apiProviders = ['GEMINI_API_KEY', 'OPENAI_API_KEY', 'OPENROUTER_API_KEY', 'ANTHROPIC_API_KEY', 'OPENWEATHERMAP_API_KEY']
const apiKeyConfig = ref({ api_keys: {} })
const apiKeyForm = reactive({
  GEMINI_API_KEY: '',
  OPENAI_API_KEY: '',
  OPENROUTER_API_KEY: '',
  ANTHROPIC_API_KEY: '',
  OPENWEATHERMAP_API_KEY: ''
})

const showSmtpDialog = ref(false)
const savingSmtp = ref(false)
const smtpConfig = ref({
  host: '',
  port: 587,
  from_email: '',
  use_tls: true,
  use_ssl: false,
  username_configured: false,
  password_configured: false,
  db_configured: false,
  env_configured: false,
  effective_source: null
})
const smtpForm = reactive({
  smtp_host: '',
  smtp_port: 587,
  smtp_username: '',
  smtp_password: '',
  smtp_from_email: '',
  smtp_use_tls: true,
  smtp_use_ssl: false
})

// LLM States
const llmConfig = ref({
  chatbot_system_prompt: '',
  draft_system_prompt: '',
  enable_weather_api: false,
  ai_insights_cron: '',
  kleinunternehmer_regelung: false
})
const loadingLLM = ref(false)
const savingLLM = ref(false)

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

async function fetchSecretConfig() {
  try {
    const [apiRes, smtpRes] = await Promise.all([
      axios.get('/api/admin/secret-config/api-keys'),
      axios.get('/api/admin/secret-config/smtp')
    ])
    apiKeyConfig.value = apiRes.data
    smtpConfig.value = smtpRes.data
  } catch (err) {
    console.error('Fetch secret config error:', err)
    showToast('Fehler beim Laden der Schlüssel-/SMTP-Konfiguration', 'error')
  }
}

function openCreateUserDialog() {
  isEditUser.value = false
  editingUserId.value = null
  userForm.username = ''
  userForm.email = ''
  userForm.first_name = ''
  userForm.last_name = ''
  userForm.password = ''
  userForm.role = 'USER'
  userForm.is_active = true
  showUserDialog.value = true
}

function openEditUserDialog(user) {
  isEditUser.value = true
  editingUserId.value = user.id
  userForm.username = user.username
  userForm.email = user.email
  userForm.first_name = user.first_name || ''
  userForm.last_name = user.last_name || ''
  userForm.password = ''
  userForm.role = user.role
  userForm.is_active = user.is_active
  showUserDialog.value = true
}

async function submitUserForm() {
  savingUser.value = true
  try {
    const payload = {
      username: userForm.username,
      email: userForm.email,
      first_name: userForm.first_name || null,
      last_name: userForm.last_name || null,
      role: userForm.role,
      is_active: userForm.is_active
    }
    if (userForm.password) {
      payload.password = userForm.password
    }

    if (isEditUser.value) {
      await axios.put(`/api/admin/users/${editingUserId.value}`, payload)
      showToast('Benutzer erfolgreich aktualisiert.')
    } else {
      if (!userForm.password || userForm.password.length < 8) {
        showToast('Passwort muss mindestens 8 Zeichen haben.', 'error')
        return
      }
      await axios.post('/api/admin/users', payload)
      showToast('Benutzer erfolgreich angelegt.')
    }

    showUserDialog.value = false
    await fetchUsers()
  } catch (err) {
    console.error('Save user error:', err)
    showToast(err.response?.data?.detail || 'Fehler beim Speichern des Benutzers.', 'error')
  } finally {
    savingUser.value = false
  }
}

async function deleteUser(user) {
  const confirmed = await confirmStore.ask({
    title: 'Benutzer löschen',
    message: `Möchtest du den Benutzer '${user.username}' wirklich löschen?`,
    type: 'danger',
    confirmText: 'Ja, löschen'
  })
  if (!confirmed) return
  try {
    await axios.delete(`/api/admin/users/${user.id}`)
    showToast(`Benutzer '${user.username}' wurde gelöscht.`)
    await fetchUsers()
  } catch (err) {
    console.error('Delete user error:', err)
    showToast(err.response?.data?.detail || 'Fehler beim Löschen des Benutzers.', 'error')
  }
}

function openApiKeyDialog() {
  for (const provider of apiProviders) {
    apiKeyForm[provider] = ''
  }
  showApiDialog.value = true
}

function clearApiKey(provider) {
  apiKeyForm[provider] = ''
  saveApiKeys({ [provider]: '' })
}

async function saveApiKeys(forcedPayload = null) {
  savingApiKeys.value = true
  try {
    const payload = forcedPayload || Object.fromEntries(
      apiProviders.filter((p) => apiKeyForm[p]).map((p) => [p, apiKeyForm[p]])
    )
    if (!Object.keys(payload).length) {
      showToast('Keine Änderungen zum Speichern vorhanden.', 'error')
      return
    }
    const res = await axios.put('/api/admin/secret-config/api-keys', payload)
    apiKeyConfig.value = res.data
    for (const provider of apiProviders) {
      apiKeyForm[provider] = ''
    }
    showToast('API-Schlüssel-Konfiguration aktualisiert.')
  } catch (err) {
    console.error('Save API keys error:', err)
    showToast(err.response?.data?.detail || 'Fehler beim Speichern der API-Schlüssel.', 'error')
  } finally {
    savingApiKeys.value = false
  }
}

function openSmtpDialog() {
  smtpForm.smtp_host = smtpConfig.value.host || ''
  smtpForm.smtp_port = smtpConfig.value.port || 587
  smtpForm.smtp_username = ''
  smtpForm.smtp_password = ''
  smtpForm.smtp_from_email = smtpConfig.value.from_email || ''
  smtpForm.smtp_use_tls = smtpConfig.value.use_tls ?? true
  smtpForm.smtp_use_ssl = smtpConfig.value.use_ssl ?? false
  showSmtpDialog.value = true
}

async function saveSmtpConfig() {
  savingSmtp.value = true
  try {
    const payload = {
      smtp_host: smtpForm.smtp_host || null,
      smtp_port: Number(smtpForm.smtp_port),
      smtp_username: smtpForm.smtp_username || '',
      smtp_password: smtpForm.smtp_password || '',
      smtp_from_email: smtpForm.smtp_from_email || null,
      smtp_use_tls: smtpForm.smtp_use_tls,
      smtp_use_ssl: smtpForm.smtp_use_ssl
    }
    const res = await axios.put('/api/admin/secret-config/smtp', payload)
    smtpConfig.value = res.data
    smtpForm.smtp_username = ''
    smtpForm.smtp_password = ''
    showToast('SMTP-Konfiguration aktualisiert.')
    showSmtpDialog.value = false
  } catch (err) {
    console.error('Save SMTP config error:', err)
    showToast(err.response?.data?.detail || 'Fehler beim Speichern der SMTP-Konfiguration.', 'error')
  } finally {
    savingSmtp.value = false
  }
}

function apiEnvConfigured(provider) {
  return Boolean(apiKeyConfig.value.api_keys?.[provider]?.env_configured)
}

function apiDbConfigured(provider) {
  return Boolean(apiKeyConfig.value.api_keys?.[provider]?.db_configured)
}

function apiSourceLabel(provider) {
  const source = apiKeyConfig.value.api_keys?.[provider]?.effective_source
  if (source === 'db') return 'DB'
  if (source === 'env') return '.env'
  return 'Nicht gesetzt'
}

function apiSourceClass(provider) {
  const source = apiKeyConfig.value.api_keys?.[provider]?.effective_source
  if (source === 'db') return 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400'
  if (source === 'env') return 'bg-blue-500/10 text-blue-600 dark:text-blue-400'
  return 'bg-gray-200/60 text-gray-600 dark:text-gray-300'
}

const smtpSourceLabel = computed(() => {
  if (smtpConfig.value.effective_source === 'db') return 'DB'
  if (smtpConfig.value.effective_source === 'env') return '.env'
  return 'Nicht gesetzt'
})

const smtpSourceClass = computed(() => {
  if (smtpConfig.value.effective_source === 'db') return 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400'
  if (smtpConfig.value.effective_source === 'env') return 'bg-blue-500/10 text-blue-600 dark:text-blue-400'
  return 'bg-gray-200/60 text-gray-600 dark:text-gray-300'
})

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
      chatbot_system_prompt: llmConfig.value.chatbot_system_prompt,
      draft_system_prompt: llmConfig.value.draft_system_prompt,
      enable_weather_api: llmConfig.value.enable_weather_api,
      ai_insights_cron: llmConfig.value.ai_insights_cron || null,
      kleinunternehmer_regelung: llmConfig.value.kleinunternehmer_regelung
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

// Seed / Restore prompts to default constants hardcoded in the codebase
function resetConfigToDefault() {
  llmConfig.value.chatbot_system_prompt = 
    "Du bist der hochkompetente 'BeeBoard KI-Assistent' für Imker.\n" +
    "Deine Aufgabe ist es, dem Imker basierend auf seinen Daten präzise Auskunft " +
    "zu geben. Antworte immer freundlich, sachlich und auf Deutsch. Halte dich kurz " +
    "und hebe wichtige Warnungen (wie hohe Varroazahlen) hervor.\n\n" +
    "Hier ist der aktuelle Zustand der Imkerei (Völker, Standorte, letzte Messungen):\n" +
    "{context_str}"

  llmConfig.value.draft_system_prompt = 
    "Du bist ein intelligentere Daten-Extraktor für Imker.\n" +
    "Lies die folgende Freitext-Notiz des Imkers durch und wandle sie in ein valides JSON-Objekt um.\n" +
    "Das JSON-Objekt MUSS exakt der folgenden Struktur entsprechen. Gib NUR das reine JSON zurück. Keine Markdowns wie ```json.\n\n" +
    "STRUKTUR:\n" +
    "{\n" +
    "  \"hive_name\": \"Name des Volks (z.B. Volk 3) oder null wenn nicht genannt\",\n" +
    "  \"entry_type\": \"Einer der Werte: 'INSPECTION', 'VARROA_COUNT', 'VARROA_TREATMENT', 'GENERAL'\",\n" +
    "  \"notes\": \"Zusammenfassung der Notiz als Fließtext\",\n" +
    "  \"date\": \"Datum im Format YYYY-MM-DD (Standard: '{date_str}')\",\n" +
    "  \"inspection_detail\": {\n" +
    "    \"frames\": [\n" +
    "      {\n" +
    "        \"frame_number\": 1, // Nummer der Wabe (1-basiert)\n" +
    "        \"side\": 1,         // Waben-Seite (1 oder 2)\n" +
    "        \"brood_eighths\": 0, // Brut in Achteln (0-8)\n" +
    "        \"food_eighths\": 0,  // Futter in Achteln (0-8)\n" +
    "        \"bee_eighths\": 0    // Bienenmasse in Achteln (0-8)\n" +
    "      }\n" +
    "    ]\n" +
    "  }, // Nur vorhanden bei entry_type = 'INSPECTION', sonst null\n" +
    "  \"varroa_count_detail\": {\n" +
    "    \"raw_count\": 0 // Rohwert Varroamilben (Zahl)\n" +
    "  }, // Nur vorhanden bei entry_type = 'VARROA_COUNT', sonst null\n" +
    "  \"varroa_treatment_detail\": {\n" +
    "    \"product\": \"Name des Präparats\",\n" +
    "    \"dosage\": \"Dosis (z.B. 50ml)\"\n" +
    "  } // Nur vorhanden bei entry_type = 'VARROA_TREATMENT', sonst null\n" +
    "}"
  
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
  fetchSecretConfig()
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
