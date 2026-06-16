<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 font-sans">
    
    <!-- Back to Dashboard Link -->
    <router-link to="/dashboard" class="inline-flex items-center text-sm font-semibold text-primary hover:text-primary-hover mb-4 transition-colors duration-200">
      <svg class="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"/></svg>
      {{ $t('common.back_to_dashboard') }}
    </router-link>

    <!-- Header -->
    <div class="mb-8 flex flex-col sm:flex-row sm:justify-between sm:items-center space-y-4 sm:space-y-0">
      <div>
        <h1 class="text-3xl font-extrabold text-gray-900 dark:text-white tracking-tight">📓 {{ $t('logbook.title') }}</h1>
        <p class="text-gray-500 dark:text-gray-400 mt-1">{{ $t('logbook.subtitle') }}</p>
      </div>
      <button 
        @click="openCreateSessionModal" 
        class="px-5 py-2.5 bg-primary hover:bg-primary-hover text-white font-extrabold text-sm rounded-xl shadow-md shadow-primary/20 hover-scale flex items-center justify-center space-x-2"
      >
        <span>{{ $t('logbook.new_session') }}</span>
      </button>
    </div>

    <!-- Active Apiary check -->
    <div v-if="!apiaryStore.activeApiaryId" class="glass rounded-3xl p-12 text-center max-w-lg mx-auto border border-dashed border-gray-300 dark:border-gray-700">
      <div class="text-4xl mb-4">📓</div>
      <h3 class="text-lg font-bold text-gray-800 dark:text-white mb-2">{{ $t('logbook.no_active_apiary') }}</h3>
      <p class="text-gray-500 dark:text-gray-400">{{ $t('logbook.select_apiary_desc') }}</p>
    </div>

    <div v-else class="space-y-6">
      
      <!-- View Mode Switcher -->
      <div class="flex justify-between items-center bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border p-4 rounded-2xl shadow-sm">
        <div class="flex items-center space-x-2">
          <span class="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider">{{ $t('logbook.view_label') }}</span>
          <div class="inline-flex rounded-xl p-0.5 bg-gray-100 dark:bg-dark-bg border border-gray-200 dark:border-dark-border">
            <button 
              @click="viewMode = 'tiles'" 
              class="px-4 py-1.5 rounded-lg text-xs font-extrabold tracking-wide transition-all"
              :class="viewMode === 'tiles' ? 'bg-white dark:bg-dark-card text-primary shadow-sm' : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'"
            >
              {{ $t('logbook.view_tiles') }}
            </button>
            <button 
              @click="viewMode = 'table'" 
              class="px-4 py-1.5 rounded-lg text-xs font-extrabold tracking-wide transition-all"
              :class="viewMode === 'table' ? 'bg-white dark:bg-dark-card text-primary shadow-sm' : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'"
            >
              {{ $t('logbook.view_table') }}
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
              {{ isEditSessionMode ? $t('logbook.edit_session') : $t('logbook.new_session_title') }}
            </h4>
            <button @click="showSessionModal = false" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200">
              <svg class="w-4.5 h-4.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
            </button>
          </div>
          <form @submit.prevent="submitSessionForm" class="space-y-4">
            <div>
              <div class="flex justify-between items-center mb-1">
                <label class="block text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider">{{ $t('logbook.session_title_label') }}</label>
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
                :placeholder="$t('logbook.session_title_placeholder')"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-xs"
              />
            </div>
            <!-- Scope Type Segmented Buttons -->
            <div>
              <label class="block text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2">
                {{ $t('logbook.session_scope') }}
              </label>
              <div class="grid grid-cols-3 gap-2">
                <button
                  type="button"
                  @click="sessionForm.scopeType = 'APIARY'"
                  class="flex flex-col items-center justify-center p-3 rounded-2xl border text-xs font-bold transition-all duration-200"
                  :class="sessionForm.scopeType === 'APIARY' ? 'bg-primary/5 border-primary text-primary shadow-sm' : 'border-gray-200 hover:border-gray-300 dark:border-dark-border dark:text-gray-300'"
                >
                  <span class="text-base mb-1">🏢</span>
                  <span>{{ $t('beeAgent.scope_apiary') }}</span>
                </button>
                <button
                  type="button"
                  @click="sessionForm.scopeType = 'LOCATION'"
                  class="flex flex-col items-center justify-center p-3 rounded-2xl border text-xs font-bold transition-all duration-200"
                  :class="sessionForm.scopeType === 'LOCATION' ? 'bg-primary/5 border-primary text-primary shadow-sm' : 'border-gray-200 hover:border-gray-300 dark:border-dark-border dark:text-gray-300'"
                >
                  <span class="text-base mb-1">📍</span>
                  <span>{{ $t('beeAgent.scope_location') }}</span>
                </button>
                <button
                  type="button"
                  @click="sessionForm.scopeType = 'HIVE'"
                  class="flex flex-col items-center justify-center p-3 rounded-2xl border text-xs font-bold transition-all duration-200"
                  :class="sessionForm.scopeType === 'HIVE' ? 'bg-primary/5 border-primary text-primary shadow-sm' : 'border-gray-200 hover:border-gray-300 dark:border-dark-border dark:text-gray-300'"
                >
                  <span class="text-base mb-1">🐝</span>
                  <span>{{ $t('beeAgent.scope_hive') }}</span>
                </button>
              </div>
            </div>

            <!-- Apiaries Multi-Select Checklist -->
            <div v-if="sessionForm.scopeType === 'APIARY'">
              <label class="block text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2">
                {{ $t('logbook.select_apiaries') }}
              </label>
              <div class="max-h-40 overflow-y-auto border border-gray-200 dark:border-dark-border rounded-2xl p-3 space-y-2 bg-gray-50 dark:bg-dark-bg">
                <label v-for="apiary in apiaryStore.apiaries" :key="apiary.id" class="flex items-center space-x-2 text-xs text-gray-700 dark:text-gray-300 cursor-pointer hover:text-primary transition-colors">
                  <input
                    type="checkbox"
                    :value="apiary.id"
                    v-model="sessionForm.linkedApiaryIds"
                    class="rounded text-primary focus:ring-primary border-gray-300 dark:border-dark-border"
                  />
                  <span class="font-bold">{{ apiary.name }}</span>
                </label>
              </div>
            </div>

            <!-- Locations Multi-Select Checklist -->
            <div v-if="sessionForm.scopeType === 'LOCATION'">
              <label class="block text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2">
                {{ $t('logbook.select_locations') }}
              </label>
              <div v-if="locations.length === 0" class="text-xs text-gray-400 italic bg-gray-50 dark:bg-dark-bg p-3 rounded-2xl border">
                {{ $t('logbook.no_locations') }}
              </div>
              <div v-else class="max-h-40 overflow-y-auto border border-gray-200 dark:border-dark-border rounded-2xl p-3 space-y-2 bg-gray-50 dark:bg-dark-bg">
                <label v-for="loc in locations" :key="loc.id" class="flex items-center space-x-2 text-xs text-gray-700 dark:text-gray-300 cursor-pointer hover:text-primary transition-colors">
                  <input
                    type="checkbox"
                    :value="loc.id"
                    v-model="sessionForm.linkedLocationIds"
                    class="rounded text-primary focus:ring-primary border-gray-300 dark:border-dark-border"
                  />
                  <span class="font-bold">{{ loc.name }}</span>
                </label>
              </div>
            </div>

            <!-- Hives Multi-Select Checklist -->
            <div v-if="sessionForm.scopeType === 'HIVE'">
              <label class="block text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2">
                {{ $t('logbook.select_hives') }}
              </label>
              <div v-if="hives.length === 0" class="text-xs text-gray-400 italic bg-gray-50 dark:bg-dark-bg p-3 rounded-2xl border">
                {{ $t('logbook.no_hives') }}
              </div>
              <div v-else class="max-h-40 overflow-y-auto border border-gray-200 dark:border-dark-border rounded-2xl p-3 space-y-2 bg-gray-50 dark:bg-dark-bg">
                <label v-for="hive in hives" :key="hive.id" class="flex items-center space-x-2 text-xs text-gray-700 dark:text-gray-300 cursor-pointer hover:text-primary transition-colors">
                  <input
                    type="checkbox"
                    :value="hive.id"
                    v-model="sessionForm.linkedHiveIds"
                    class="rounded text-primary focus:ring-primary border-gray-300 dark:border-dark-border"
                  />
                  <span class="font-bold">{{ hive.name }} <span class="text-[10px] text-gray-400 font-medium">({{ hive.location?.name || $t('logbook.no_location') }})</span></span>
                </label>
              </div>
            </div>
            <div class="flex justify-end space-x-2 pt-2">
              <button type="button" @click="showSessionModal = false" class="px-3 py-1.5 text-xs font-bold text-gray-500 hover:text-gray-700 dark:hover:text-gray-300">{{ $t('common.cancel') }}</button>
              <button type="submit" class="px-4 py-1.5 bg-primary hover:bg-primary-hover text-white font-extrabold text-xs rounded-xl shadow-md">
                {{ isEditSessionMode ? $t('common.save') : $t('logbook.create') }}
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
            {{ $t('logbook.no_sessions_yet') }}
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
                  <span class="text-[9px] font-black uppercase tracking-wider text-primary bg-primary/10 px-2 py-0.5 rounded">{{ $t('logbook.session_badge') }}</span>
                  <div class="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button 
                      @click.stop="openEditSessionModal(session)"
                      class="p-1.5 text-gray-400 hover:text-primary hover:bg-primary/10 rounded-xl transition-all"
                      :title="$t('logbook.rename_session')"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/></svg>
                    </button>
                    <button 
                      @click.stop="deleteSession(session)"
                      class="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-500/10 rounded-xl transition-all"
                      :title="$t('logbook.delete_session')"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                    </button>
                  </div>
                </div>
                <h4 class="font-extrabold text-base text-gray-900 dark:text-white mt-3 line-clamp-2">
                  {{ session.title }}
                </h4>
                <div class="mt-2 flex flex-wrap gap-1">
                  <span 
                    v-if="session.scope_type === 'APIARY'" 
                    class="px-2 py-0.5 bg-blue-500/10 text-blue-600 dark:text-blue-400 text-[10px] font-bold rounded flex items-center space-x-1"
                  >
                    <span>🏢 Imkerei:</span>
                    <span class="font-medium max-w-[150px] truncate">
                      {{ session.linked_apiaries?.map(a => a.name).join(', ') || 'Alle' }}
                    </span>
                  </span>
                  <span 
                    v-else-if="session.scope_type === 'LOCATION'" 
                    class="px-2 py-0.5 bg-green-500/10 text-green-600 dark:text-green-400 text-[10px] font-bold rounded flex items-center space-x-1"
                  >
                    <span>📍 Standorte:</span>
                    <span class="font-medium max-w-[150px] truncate">
                      {{ session.linked_locations?.map(l => l.name).join(', ') || 'Keine' }}
                    </span>
                  </span>
                  <span 
                    v-else-if="session.scope_type === 'HIVE'" 
                    class="px-2 py-0.5 bg-amber-500/10 text-amber-600 dark:text-amber-400 text-[10px] font-bold rounded flex items-center space-x-1"
                  >
                    <span>🐝 Völker:</span>
                    <span class="font-medium max-w-[150px] truncate">
                      {{ session.linked_hives?.map(h => h.name).join(', ') || 'Keine' }}
                    </span>
                  </span>
                  <span 
                    v-else-if="session.hive" 
                    class="px-2 py-0.5 bg-amber-500/10 text-primary text-[10px] font-bold rounded"
                  >
                    {{ $t('logbook.hive_label', { name: session.hive.name }) }}
                  </span>
                </div>
              </div>
              <div class="text-[10px] text-gray-400 font-mono mt-4">
                {{ $t('logbook.last_active', { time: formatDateTime(session.updated_at) }) }}
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
            {{ $t('logbook.back_to_tiles') }}
          </button>

          <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
            <!-- Entries Pane (8 cols) -->
            <div class="lg:col-span-8 space-y-6">
              
              <!-- Session title & quick details card -->
              <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-6 shadow-sm flex justify-between items-center">
                <div>
                  <span class="text-[10px] font-black uppercase text-gray-400">{{ $t('logbook.active_session') }}</span>
                  <div class="flex items-center space-x-2 mt-1">
                    <h2 class="text-xl font-extrabold text-gray-900 dark:text-white">{{ selectedSession.title }}</h2>
                    <button 
                      @click="openEditSessionModal(selectedSession)"
                      class="p-1 text-gray-400 hover:text-primary rounded-lg hover:bg-gray-100 dark:hover:bg-dark-border transition-colors inline-flex items-center"
                      :title="$t('logbook.rename_session')"
                    >
                      <svg class="w-4.5 h-4.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/></svg>
                    </button>
                  </div>
                  <div class="text-xs text-gray-500 mt-1 space-y-0.5">
                    <div v-if="selectedSession.scope_type === 'APIARY'" class="flex items-center space-x-1">
                      <span>🏢 Imkereien:</span>
                      <span class="font-bold text-primary">{{ selectedSession.linked_apiaries?.map(a => a.name).join(', ') || 'Alle' }}</span>
                    </div>
                    <div v-else-if="selectedSession.scope_type === 'LOCATION'" class="flex items-center space-x-1">
                      <span>📍 Standorte:</span>
                      <span class="font-bold text-primary">{{ selectedSession.linked_locations?.map(l => l.name).join(', ') || 'Keine' }}</span>
                    </div>
                    <div v-else-if="selectedSession.scope_type === 'HIVE'" class="flex items-center space-x-1">
                      <span>🐝 Völker:</span>
                      <span class="font-bold text-primary">{{ selectedSession.linked_hives?.map(h => h.name).join(', ') || 'Keine' }}</span>
                    </div>
                    <div v-else-if="selectedSession.hive" class="flex items-center space-x-1">
                      <span>🐝 Volk:</span>
                      <span class="font-bold text-primary">{{ selectedSession.hive.name }}</span>
                    </div>
                  </div>
                </div>
                
                <button 
                  @click="openCreateEntryModal" 
                  class="px-4 py-2 bg-primary hover:bg-primary-hover text-white font-extrabold text-xs uppercase tracking-wider rounded-xl shadow-md hover-scale"
                >
                  {{ $t('logbook.new_entry') }}
                </button>
              </div>

              <!-- Inline Create/Edit Form -->
              <div v-if="showEntryModal" class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl shadow-md p-6 mb-6 animate-scale">
                <div class="flex justify-between items-center mb-6 pb-4 border-b border-gray-100 dark:border-dark-border">
                  <h3 class="text-xl font-bold text-gray-900 dark:text-white">
                    {{ isEditEntryMode ? $t('logbook.edit_entry_title') : $t('logbook.new_entry_title') }}
                  </h3>
                  <button @click="showEntryModal = false" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
                  </button>
                </div>
                
                <form @submit.prevent="submitEntryForm" class="space-y-4">
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('logbook.hive_required') }}</label>
                      <select 
                        v-model="entryForm.hiveId" 
                        required
                        :disabled="isHiveSelectorDisabled"
                        @change="onHiveSelected"
                        class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm cursor-pointer disabled:opacity-60 disabled:cursor-not-allowed"
                      >
                        <option value="" disabled>{{ $t('logbook.select_hive_placeholder') }}</option>
                        <option v-for="hive in filteredHivesForEntry" :key="hive.id" :value="hive.id">
                          {{ hive.name }}
                        </option>
                      </select>
                    </div>
                    <div>
                      <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('logbook.date_required') }}</label>
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
                      <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('logbook.entry_type_required') }}</label>
                      <select 
                        v-model="selectedTypeOption" 
                        required
                        :disabled="isEditEntryMode"
                        class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm cursor-pointer"
                      >
                        <option value="GENERAL">{{ $t('logbook.type_general') }}</option>
                        <option value="INSPECTION_EXACT">{{ $t('logbook.type_inspection_exact') }}</option>
                        <option value="INSPECTION_EIGHTHS">{{ $t('logbook.type_inspection_eighths') }}</option>
                        <option value="VARROA_COUNT">{{ $t('logbook.type_varroa_count') }}</option>
                        <option value="VARROA_TREATMENT">{{ $t('logbook.type_varroa_treatment') }}</option>
                      </select>
                    </div>
                  </div>

                  <div>
                    <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('logbook.notes_label') }}</label>
                    <textarea 
                      v-model="entryForm.notes" 
                      :placeholder="$t('logbook.notes_placeholder')"
                      rows="6"
                      class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm"
                    ></textarea>
                  </div>

                  <!-- Image Upload Section -->
                  <div class="space-y-3">
                    <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">
                      {{ $t('logbook.table_images') }}
                    </label>
                    <div 
                      @dragover.prevent="dragOver = true"
                      @dragleave.prevent="dragOver = false"
                      @drop.prevent="onFileDrop"
                      @click="triggerFileInput"
                      class="border-2 border-dashed rounded-2xl p-6 text-center cursor-pointer transition-all duration-200"
                      :class="dragOver ? 'border-primary bg-primary/5' : 'border-gray-300 dark:border-gray-700 bg-gray-50/50 dark:bg-dark-bg/30 hover:border-primary/50'"
                    >
                      <input 
                        type="file" 
                        ref="modalFileInput" 
                        multiple 
                        accept="image/*" 
                        class="hidden" 
                        @change="onFileSelect" 
                      />
                      <div class="text-2xl mb-1">📸</div>
                      <p class="text-xs font-bold text-gray-700 dark:text-gray-300">
                        {{ $t('logbook.drag_drop_area') }}
                      </p>
                      <p class="text-[10px] text-gray-400 mt-1">
                        {{ $t('logbook.drag_drop_hint') }}
                      </p>
                    </div>

                    <!-- Image Preview Grid -->
                    <div v-if="entryFiles.length > 0" class="grid grid-cols-3 sm:grid-cols-5 gap-3 mt-3">
                      <div 
                        v-for="(img, idx) in entryFiles" 
                        :key="idx"
                        class="relative aspect-square rounded-2xl overflow-hidden border border-gray-100 dark:border-dark-border group bg-gray-50 dark:bg-dark-card"
                      >
                        <img 
                          :src="img.isExisting ? `/uploads/${img.thumbnail_path || img.image_path}` : img.previewUrl" 
                          alt="Preview" 
                          class="w-full h-full object-cover"
                        />
                        <button 
                          type="button"
                          @click="removeEntryFile(idx)"
                          class="absolute top-1 right-1 p-1 bg-red-500 text-white rounded-lg shadow opacity-0 group-hover:opacity-100 transition-opacity duration-150"
                          :title="$t('logbook.delete_image')"
                        >
                          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                        </button>
                      </div>
                    </div>
                  </div>

                  <!-- SUB-FORM: INSPECTION DETAILS (nur Zargen-weise) -->
                  <div v-if="entryForm.entryType === 'INSPECTION'" class="space-y-4 border-t border-gray-100 dark:border-dark-border pt-4">
                    <div class="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-2">
                      <h4 class="text-xs font-extrabold uppercase text-gray-500 tracking-wider">
                        {{ $t('logbook.assessment_variant') }}
                      </h4>
                    </div>

                    <!-- Zargen-weise Vereinfachte Assessment -->
                    <div class="space-y-4 animate-scale">

                      <!-- Boxes List -->
                      <div class="space-y-3">
                        <div 
                          v-for="box in entryForm.inspectionDetail.boxes" 
                          :key="box.id"
                          class="p-4 bg-white dark:bg-dark-card border rounded-2xl shadow-sm space-y-3 border-gray-200 dark:border-dark-border"
                        >
                          <div class="flex justify-between items-center pb-2 border-b border-gray-50 dark:border-dark-border">
                            <span class="text-xs font-extrabold text-gray-800 dark:text-gray-200 flex items-center">
                              {{ $t('logbook.box_label', { order: box.order, type: box.box_type === 'BROOD' ? $t('logbook.brood_chamber') : $t('logbook.honey_chamber') }) }}
                            </span>
                            <span class="text-[9px] font-bold text-gray-400 font-mono">
                              {{ $t('logbook.box_detail_hint', { count: box.frame_count, name: box.frame_type_name, multiplier: box.multiplier }) }}
                            </span>
                          </div>

                          <div class="grid grid-cols-2 sm:grid-cols-6 gap-3 text-center">
                            <!-- Brood -->
                            <div class="space-y-1">
                              <span class="text-[9px] text-amber-500 font-bold uppercase">{{ $t('logbook.brood') }}</span>
                              <input 
                                v-model.number="box.brood" 
                                type="number" 
                                step="any"
                                min="0" 
                                :max="entryForm.inspectionDetail.boxMode === 'eighths' ? 300 : undefined" 
                                class="w-full px-2 py-1.5 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg rounded-xl text-center text-xs font-mono font-bold"
                                :placeholder="entryForm.inspectionDetail.boxMode === 'exact' ? $t('logbook.exact_placeholder_pcs') : $t('logbook.eighths_placeholder')"
                              />
                            </div>

                            <!-- Bees -->
                            <div class="space-y-1">
                              <span class="text-[9px] text-green-500 font-bold uppercase">{{ $t('logbook.bees') }}</span>
                              <input 
                                v-model.number="box.bees" 
                                type="number" 
                                step="any"
                                min="0" 
                                :max="entryForm.inspectionDetail.boxMode === 'eighths' ? 300 : undefined" 
                                class="w-full px-2 py-1.5 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg rounded-xl text-center text-xs font-mono font-bold"
                                :placeholder="entryForm.inspectionDetail.boxMode === 'exact' ? $t('logbook.exact_placeholder_pcs') : $t('logbook.eighths_placeholder')"
                              />
                            </div>

                            <!-- Drones -->
                            <div class="space-y-1">
                              <span class="text-[9px] text-sky-500 font-bold uppercase">{{ $t('logbook.drones') }}</span>
                              <input 
                                v-model.number="box.drones" 
                                type="number" 
                                step="any"
                                min="0" 
                                :max="entryForm.inspectionDetail.boxMode === 'eighths' ? 300 : undefined" 
                                class="w-full px-2 py-1.5 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg rounded-xl text-center text-xs font-mono font-bold"
                                :placeholder="entryForm.inspectionDetail.boxMode === 'exact' ? $t('logbook.exact_placeholder_pcs') : $t('logbook.eighths_placeholder')"
                              />
                            </div>

                            <!-- Drone Brood -->
                            <div class="space-y-1">
                              <span class="text-[9px] text-orange-500 font-bold uppercase">{{ $t('logbook.drone_brood') }}</span>
                              <input 
                                v-model.number="box.drone_brood" 
                                type="number" 
                                step="any"
                                min="0" 
                                :max="entryForm.inspectionDetail.boxMode === 'eighths' ? 300 : undefined" 
                                class="w-full px-2 py-1.5 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg rounded-xl text-center text-xs font-mono font-bold"
                                :placeholder="entryForm.inspectionDetail.boxMode === 'exact' ? $t('logbook.exact_placeholder_pcs') : $t('logbook.eighths_placeholder')"
                              />
                            </div>

                            <!-- Pollen -->
                            <div class="space-y-1">
                              <span class="text-[9px] text-purple-500 font-bold uppercase">{{ $t('logbook.pollen') }}</span>
                              <input 
                                v-model.number="box.pollen" 
                                type="number" 
                                step="any"
                                min="0" 
                                :max="entryForm.inspectionDetail.boxMode === 'eighths' ? 300 : undefined" 
                                class="w-full px-2 py-1.5 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg rounded-xl text-center text-xs font-mono font-bold"
                                :placeholder="entryForm.inspectionDetail.boxMode === 'exact' ? $t('logbook.exact_placeholder_g') : $t('logbook.eighths_placeholder')"
                              />
                            </div>

                            <!-- Food -->
                            <div class="space-y-1">
                              <span class="text-[9px] text-yellow-500 font-bold uppercase">{{ $t('logbook.food') }}</span>
                              <input 
                                v-model.number="box.food" 
                                type="number" 
                                step="any"
                                min="0" 
                                :max="entryForm.inspectionDetail.boxMode === 'eighths' ? 300 : undefined" 
                                class="w-full px-2 py-1.5 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg rounded-xl text-center text-xs font-mono font-bold"
                                :placeholder="entryForm.inspectionDetail.boxMode === 'exact' ? $t('logbook.exact_placeholder_g') : $t('logbook.eighths_placeholder')"
                              />
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- SUB-FORM: VARROA COUNT DETAILS -->
                  <div v-if="entryForm.entryType === 'VARROA_COUNT'" class="space-y-3 border-t border-gray-100 dark:border-dark-border pt-4">
                    <h4 class="text-xs font-extrabold uppercase text-gray-500 tracking-wider">{{ $t('logbook.varroa_windel_result') }}</h4>
                    <div>
                      <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 mb-1">{{ $t('logbook.varroa_raw_count_label') }}</label>
                      <input 
                        v-model.number="entryForm.varroaCountDetail.rawCount" 
                        type="number" 
                        required
                        min="0"
                        class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm"
                      />
                      <p class="text-[10px] text-gray-400 mt-1 italic">{{ $t('logbook.varroa_calc_hint') }}</p>
                    </div>
                  </div>

                  <!-- SUB-FORM: VARROA TREATMENT DETAILS -->
                  <div v-if="entryForm.entryType === 'VARROA_TREATMENT'" class="space-y-3 border-t border-gray-100 dark:border-dark-border pt-4">
                    <h4 class="text-xs font-extrabold uppercase text-gray-500 tracking-wider">{{ $t('logbook.treatment_method') }}</h4>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 mb-1">{{ $t('logbook.treatment_product_label') }}</label>
                        <input 
                          v-model="entryForm.varroaTreatmentDetail.product" 
                          type="text" 
                          required
                          :placeholder="$t('logbook.treatment_product_placeholder')"
                          class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm"
                        />
                      </div>
                      <div>
                        <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 mb-1">{{ $t('logbook.treatment_dosage_label') }}</label>
                        <input 
                          v-model="entryForm.varroaTreatmentDetail.dosage" 
                          type="text" 
                          required
                          :placeholder="$t('logbook.treatment_dosage_placeholder')"
                          class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm"
                        />
                      </div>
                    </div>
                    <div>
                      <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 mb-1">{{ $t('logbook.treatment_notes_label') }}</label>
                      <textarea 
                        v-model="entryForm.varroaTreatmentDetail.treatmentNotes" 
                        :placeholder="$t('logbook.treatment_notes_placeholder')"
                        rows="2"
                        class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm"
                      ></textarea>
                    </div>
                  </div>

                  <div class="flex justify-end space-x-2 pt-4 border-t border-gray-100 dark:border-dark-border">
                    <button type="button" @click="showEntryModal = false" class="px-4 py-2 text-sm font-bold text-gray-500 hover:text-gray-700 dark:hover:text-gray-300">{{ $t('common.cancel') }}</button>
                    <button type="submit" class="px-5 py-2 bg-primary hover:bg-primary-hover text-white font-extrabold text-sm rounded-xl shadow-md">
                      {{ $t('common.save') }}
                    </button>
                  </div>
                </form>
              </div>

              <!-- Entries Stream List -->
              <div v-if="entriesLoading" class="flex justify-center py-20 bg-white dark:bg-dark-card rounded-3xl border border-gray-200 dark:border-dark-border shadow-sm">
                <svg class="animate-spin h-6 w-6 text-primary" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
              </div>

              <div v-else-if="entries.length === 0" class="bg-white dark:bg-dark-card border rounded-3xl p-12 text-center text-gray-400 italic text-sm">
                {{ $t('logbook.no_entries_yet') }}
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
                        {{ getEntryTypeName(entry) }}
                      </span>
                      <span class="text-xs font-bold text-primary">{{ $t('logbook.hive_label', { name: entry.hive?.name || $t('logbook.unknown') }) }}</span>
                      <span class="text-[10px] text-gray-400 font-mono">{{ formatDate(entry.date) }}</span>
                    </div>

                    <div class="flex items-center space-x-1">
                      <button 
                        @click="openEditEntryModal(entry)"
                        class="p-1 text-gray-400 hover:text-primary rounded-xl hover:bg-gray-50 dark:hover:bg-dark-bg transition-colors"
                        :title="$t('common.edit')"
                      >
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/></svg>
                      </button>
                      <button 
                        @click="deleteEntry(entry)"
                        class="p-1 text-gray-400 hover:text-red-500 hover:bg-red-500/10 rounded-xl transition-all"
                        :title="$t('common.delete')"
                      >
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                      </button>
                    </div>
                  </div>

                  <p class="text-sm text-gray-700 dark:text-gray-300 font-medium italic">"{{ entry.notes || $t('logbook.no_notes_recorded') }}"</p>

                  <!-- Nested Inspections -->
                  <div v-if="entry.entry_type === 'INSPECTION' && entry.inspection_detail" class="space-y-3">
                    <span class="text-[10px] font-black uppercase text-gray-400">{{ $t('logbook.inspection_details_header') }}</span>
                    
                    <div v-if="getBoxTotalsForEntry(entry)" class="space-y-3">
                      <!-- Box Grid (Waben-Äquivalente) -->
                      <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
                        <div 
                          v-for="box in getBoxTotalsForEntry(entry).boxes" 
                          :key="box.id"
                          class="p-4 bg-gray-50 dark:bg-dark-bg/60 border border-gray-100 dark:border-dark-border rounded-2xl flex flex-col justify-between"
                        >
                          <div class="flex justify-between items-center mb-2 pb-1.5 border-b border-gray-200/50 dark:border-dark-border">
                            <span class="text-[10px] font-black text-gray-500">{{ $t('logbook.box_title_order', { order: box.order, type: box.box_type === 'BROOD' ? $t('logbook.brood_chamber') : $t('logbook.honey_chamber') }) }}</span>
                            <span class="text-[9px] font-bold text-primary bg-primary/10 px-2 py-0.5 rounded-full">{{ $t('logbook.box_frame_info', { count: box.frame_count, name: box.frame_type_name }) }}</span>
                          </div>
                          <!-- Box values (Summen, ohne Nachkommastellen) -->
                          <div class="grid grid-cols-2 gap-x-4 gap-y-1 text-xs font-mono font-bold">
                            <div class="flex justify-between items-center text-amber-500">
                              <span>{{ $t('logbook.brood') }}:</span>
                              <span>{{ box.brood.toFixed(0) }}</span>
                            </div>
                            <div class="flex justify-between items-center text-green-500">
                              <span>{{ $t('logbook.bees') }}:</span>
                              <span>{{ box.bees.toFixed(0) }}</span>
                            </div>
                            <div class="flex justify-between items-center text-sky-500">
                              <span>{{ $t('logbook.drones') }}:</span>
                              <span>{{ box.drones.toFixed(0) }}</span>
                            </div>
                            <div class="flex justify-between items-center text-orange-500">
                              <span>{{ $t('logbook.drone_brood') }}:</span>
                              <span>{{ box.drone_brood.toFixed(0) }}</span>
                            </div>
                            <div class="flex justify-between items-center text-purple-500">
                              <span>{{ $t('logbook.pollen') }}:</span>
                              <span>{{ box.pollen.toFixed(0) }} g</span>
                            </div>
                            <div class="flex justify-between items-center text-yellow-500">
                              <span>{{ $t('logbook.food') }}:</span>
                              <span>{{ box.food.toFixed(0) }} g</span>
                            </div>
                          </div>
                        </div>
                      </div>

                      <!-- Hive Total Summary (Summen, ohne Nachkommastellen) -->
                      <div class="p-4 bg-amber-500/5 dark:bg-amber-500/10 border border-amber-500/20 rounded-2xl flex flex-col md:flex-row justify-between items-start md:items-center space-y-2 md:space-y-0 shadow-sm">
                        <div>
                          <span class="text-[9px] font-black text-amber-600 dark:text-amber-400 uppercase tracking-wider">{{ $t('logbook.hive_total_header') }}</span>
                          <h4 class="text-sm font-extrabold text-gray-900 dark:text-white">{{ $t('logbook.sum_all_boxes') }}</h4>
                        </div>
                        <div class="flex flex-wrap gap-2 font-mono font-black text-[10px]">
                          <div class="flex items-center space-x-1 text-amber-500 bg-amber-500/10 px-2 py-1 rounded-xl">
                            <span>{{ $t('logbook.brood') }}:</span>
                            <span>{{ getBoxTotalsForEntry(entry).hive.brood.toFixed(0) }}</span>
                          </div>
                          <div class="flex items-center space-x-1 text-green-500 bg-green-500/10 px-2 py-1 rounded-xl">
                            <span>{{ $t('logbook.bees') }}:</span>
                            <span>{{ getBoxTotalsForEntry(entry).hive.bees.toFixed(0) }}</span>
                          </div>
                          <div class="flex items-center space-x-1 text-sky-500 bg-sky-500/10 px-2 py-1 rounded-xl">
                            <span>{{ $t('logbook.drones') }}:</span>
                            <span>{{ getBoxTotalsForEntry(entry).hive.drones.toFixed(0) }}</span>
                          </div>
                          <div class="flex items-center space-x-1 text-orange-500 bg-orange-500/10 px-2 py-1 rounded-xl">
                            <span>{{ $t('logbook.drone_brood') }}:</span>
                            <span>{{ getBoxTotalsForEntry(entry).hive.drone_brood.toFixed(0) }}</span>
                          </div>
                          <div class="flex items-center space-x-1 text-purple-500 bg-purple-500/10 px-2 py-1 rounded-xl">
                            <span>{{ $t('logbook.pollen') }}:</span>
                            <span>{{ getBoxTotalsForEntry(entry).hive.pollen.toFixed(0) }} g</span>
                          </div>
                          <div class="flex items-center space-x-1 text-yellow-500 bg-yellow-500/10 px-2 py-1 rounded-xl">
                            <span>{{ $t('logbook.food') }}:</span>
                            <span>{{ getBoxTotalsForEntry(entry).hive.food.toFixed(0) }} g</span>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    <!-- Fallback if getBoxTotalsForEntry returns null -->
                    <div v-else class="text-xs text-gray-400 italic">
                      {{ $t('logbook.box_calc_error') }}
                    </div>
                  </div>

                  <!-- Nested Varroa counts -->
                  <div v-if="entry.entry_type === 'VARROA_COUNT' && entry.varroa_count_detail" class="grid grid-cols-2 gap-4 p-4 bg-red-500/5 dark:bg-red-500/10 border border-red-500/10 rounded-2xl">
                    <div>
                      <span class="text-[9px] font-bold text-gray-400 uppercase">{{ $t('logbook.measured_mites_raw') }}</span>
                      <p class="text-xl font-black text-gray-800 dark:text-gray-100 mt-1">{{ $t('logbook.measured_mites_raw_val', { count: entry.varroa_count_detail.raw_count }) }}</p>
                    </div>
                    <div>
                      <span class="text-[9px] font-bold text-gray-400 uppercase">{{ $t('logbook.estimated_mites_day') }}</span>
                      <p class="text-xl font-black text-red-500 mt-1">{{ $t('logbook.estimated_mites_day_val', { count: entry.varroa_count_detail.estimated_total.toFixed(1) }) }}</p>
                    </div>
                  </div>

                  <!-- Nested Varroa treatments -->
                  <div v-if="entry.entry_type === 'VARROA_TREATMENT' && entry.varroa_treatment_detail" class="p-4 bg-green-500/5 dark:bg-green-500/10 border border-green-500/10 rounded-2xl space-y-1">
                    <span class="text-[9px] font-bold text-gray-400 uppercase">{{ $t('logbook.treatment_recorded') }}</span>
                    <p class="text-sm font-bold text-green-600 dark:text-green-400">{{ $t('logbook.treatment_product', { product: entry.varroa_treatment_detail.product }) }}</p>
                    <p class="text-xs font-bold mt-1 text-gray-600 dark:text-gray-400">{{ $t('logbook.treatment_dosage', { dosage: entry.varroa_treatment_detail.dosage }) }}</p>
                    <p v-if="entry.varroa_treatment_detail.treatment_notes" class="text-xs text-gray-400 italic mt-1">"{{ entry.varroa_treatment_detail.treatment_notes }}"</p>
                  </div>

                  <!-- Images stream & upload gallery -->
                  <div class="space-y-2 border-t border-gray-100 dark:border-dark-border pt-4">
                    <div class="flex justify-between items-center">
                      <span class="text-[10px] font-black uppercase text-gray-400">{{ $t('logbook.image_gallery', { count: entry.images?.length || 0 }) }}</span>
                      
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
                        {{ $t('logbook.add_image') }}
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
                          :title="$t('logbook.delete_image')"
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
            <span>🔍 {{ $t('logbook.filter_options') }}</span>
            <button 
              @click="resetTableFilters" 
              class="ml-auto text-xs text-primary hover:underline font-bold"
            >
              {{ $t('hives.reset_filters') }}
            </button>
          </h3>
          
          <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            <!-- Zeitraum Start -->
            <div>
              <label class="block text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">{{ $t('logbook.filter_from_date') }}</label>
              <input 
                v-model="tableFilters.startDate" 
                type="date" 
                class="w-full px-3 py-2 border border-gray-200 dark:border-gray-800 dark:bg-dark-bg dark:text-white rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
            
            <!-- Zeitraum Ende -->
            <div>
              <label class="block text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">{{ $t('logbook.filter_to_date') }}</label>
              <input 
                v-model="tableFilters.endDate" 
                type="date" 
                class="w-full px-3 py-2 border border-gray-200 dark:border-gray-800 dark:bg-dark-bg dark:text-white rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
            
            <!-- Imkerei -->
            <div>
              <label class="block text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">{{ $t('sidebar.active_apiary') }}</label>
              <select 
                v-model="tableFilters.apiaryId" 
                class="w-full px-3 py-2 border border-gray-200 dark:border-gray-800 dark:bg-dark-bg dark:text-white rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-primary cursor-pointer"
              >
                <option value="">{{ $t('logbook.filter_all_apiaries') }}</option>
                <option v-for="a in apiaryStore.apiaries" :key="a.id" :value="a.id">
                  {{ a.name }}
                </option>
              </select>
            </div>
            
            <!-- Standort -->
            <div>
              <label class="block text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">{{ $t('hives.location_label') }}</label>
              <select 
                v-model="tableFilters.locationId" 
                class="w-full px-3 py-2 border border-gray-200 dark:border-gray-800 dark:bg-dark-bg dark:text-white rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-primary cursor-pointer"
              >
                <option value="">{{ $t('logbook.filter_all_locations') }}</option>
                <option v-for="loc in uniqueLocations" :key="loc.id" :value="loc.id">
                  {{ loc.name }}
                </option>
              </select>
            </div>
            
            <!-- Volk -->
            <div>
              <label class="block text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">{{ $t('hives.table_hive') }}</label>
              <select 
                v-model="tableFilters.hiveId" 
                class="w-full px-3 py-2 border border-gray-200 dark:border-gray-800 dark:bg-dark-bg dark:text-white rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-primary cursor-pointer"
              >
                <option value="">{{ $t('logbook.filter_all_hives') }}</option>
                <option v-for="h in uniqueHives" :key="h.id" :value="h.id">
                  {{ h.name }}
                </option>
              </select>
            </div>
            
            <!-- Erfasser -->
            <div>
              <label class="block text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">{{ $t('logbook.table_creator') }}</label>
              <select 
                v-model="tableFilters.userId" 
                class="w-full px-3 py-2 border border-gray-200 dark:border-gray-800 dark:bg-dark-bg dark:text-white rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-primary cursor-pointer"
              >
                <option value="">{{ $t('logbook.filter_all_creators') }}</option>
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
              {{ isEditEntryMode ? $t('logbook.edit_entry_title') : $t('logbook.new_entry_title') }}
            </h3>
            <button @click="showEntryModal = false" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
            </button>
          </div>
          
          <form @submit.prevent="submitEntryForm" class="space-y-4">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('logbook.hive_required') }}</label>
                <select 
                  v-model="entryForm.hiveId" 
                  required
                  :disabled="isHiveSelectorDisabled"
                  @change="onHiveSelected"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm cursor-pointer disabled:opacity-60 disabled:cursor-not-allowed"
                >
                  <option value="" disabled>{{ $t('logbook.select_hive_placeholder') }}</option>
                  <option v-for="hive in hives" :key="hive.id" :value="hive.id">
                    {{ hive.name }}
                  </option>
                </select>
              </div>
              <div>
                <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('logbook.date_required') }}</label>
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
                <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('logbook.entry_type_required') }}</label>
                <select 
                  v-model="selectedTypeOption" 
                  required
                  :disabled="isEditEntryMode"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm cursor-pointer"
                >
                  <option value="GENERAL">{{ $t('logbook.type_general') }}</option>
                  <option value="INSPECTION_EXACT">{{ $t('logbook.type_inspection_exact') }}</option>
                  <option value="INSPECTION_EIGHTHS">{{ $t('logbook.type_inspection_eighths') }}</option>
                  <option value="VARROA_COUNT">{{ $t('logbook.type_varroa_count') }}</option>
                  <option value="VARROA_TREATMENT">{{ $t('logbook.type_varroa_treatment') }}</option>
                </select>
              </div>
            </div>

            <div>
              <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('logbook.notes_label') }}</label>
              <textarea 
                v-model="entryForm.notes" 
                :placeholder="$t('logbook.notes_placeholder')"
                rows="6"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm"
              ></textarea>
            </div>

            <!-- Image Upload Section -->
            <div class="space-y-3">
              <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">
                {{ $t('logbook.table_images') }}
              </label>
              <div 
                @dragover.prevent="dragOver = true"
                @dragleave.prevent="dragOver = false"
                @drop.prevent="onFileDrop"
                @click="triggerFileInput"
                class="border-2 border-dashed rounded-2xl p-6 text-center cursor-pointer transition-all duration-200"
                :class="dragOver ? 'border-primary bg-primary/5' : 'border-gray-300 dark:border-gray-700 bg-gray-50/50 dark:bg-dark-bg/30 hover:border-primary/50'"
              >
                <input 
                  type="file" 
                  ref="modalFileInputTable" 
                  multiple 
                  accept="image/*" 
                  class="hidden" 
                  @change="onFileSelect" 
                />
                <div class="text-2xl mb-1">📸</div>
                <p class="text-xs font-bold text-gray-700 dark:text-gray-300">
                  {{ $t('logbook.drag_drop_area') }}
                </p>
                <p class="text-[10px] text-gray-400 mt-1">
                  {{ $t('logbook.drag_drop_hint') }}
                </p>
              </div>

              <!-- Image Preview Grid -->
              <div v-if="entryFiles.length > 0" class="grid grid-cols-3 sm:grid-cols-5 gap-3 mt-3">
                <div 
                  v-for="(img, idx) in entryFiles" 
                  :key="idx"
                  class="relative aspect-square rounded-2xl overflow-hidden border border-gray-100 dark:border-dark-border group bg-gray-50 dark:bg-dark-card"
                >
                  <img 
                    :src="img.isExisting ? `/uploads/${img.thumbnail_path || img.image_path}` : img.previewUrl" 
                    alt="Preview" 
                    class="w-full h-full object-cover"
                  />
                  <button 
                    type="button"
                    @click="removeEntryFile(idx)"
                    class="absolute top-1 right-1 p-1 bg-red-500 text-white rounded-lg shadow opacity-0 group-hover:opacity-100 transition-opacity duration-150"
                    :title="$t('logbook.delete_image')"
                  >
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                  </button>
                </div>
              </div>
            </div>

            <!-- SUB-FORM: INSPECTION DETAILS -->
            <div v-if="entryForm.entryType === 'INSPECTION'" class="space-y-4 border-t border-gray-100 dark:border-dark-border pt-4">
              
              <!-- Warning card when hive has no boxes -->
              <div v-if="activeHive && (!activeHive.boxes || activeHive.boxes.length === 0)" class="p-3.5 bg-amber-50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-900/60 rounded-xl text-xs font-bold text-amber-700 dark:text-amber-400 flex items-start space-x-2">
                <span class="mt-0.5 text-base shrink-0">⚠️</span>
                <span>{{ $t('logbook.no_boxes_warning') }}</span>
              </div>

              <div class="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-2">
                <h4 class="text-xs font-extrabold uppercase text-gray-500 tracking-wider">{{ $t('logbook.assessment_variant_simple') }}</h4>
                <span class="inline-flex items-center px-3 py-1 rounded-lg text-[10px] font-black bg-white dark:bg-dark-card text-primary border border-gray-200 dark:border-dark-border">
                  {{ $t('logbook.assessment_variant_badge') }}
                </span>
              </div>

              <!-- Zargen-weise Vereinfachte Assessment (Standard, einzige Variante) -->
              <div class="space-y-4 animate-scale">

                <!-- Boxes List -->
                <div class="space-y-3">
                  <div 
                    v-for="(box, idx) in entryForm.inspectionDetail.boxes" 
                    :key="box.id"
                    class="p-4 bg-white dark:bg-dark-card border rounded-2xl shadow-sm space-y-3 border-gray-200 dark:border-dark-border"
                  >
                    <div class="flex justify-between items-center pb-2 border-b border-gray-50 dark:border-dark-border">
                      <span class="text-xs font-extrabold text-gray-800 dark:text-gray-200 flex items-center">
                        {{ $t('logbook.box_label', { order: box.order, type: box.box_type === 'BROOD' ? $t('logbook.brood_chamber') : $t('logbook.honey_chamber') }) }}
                      </span>
                      <span class="text-[9px] font-bold text-gray-400 font-mono">
                        {{ $t('logbook.box_detail_hint', { count: box.frame_count, name: box.frame_type_name, multiplier: box.multiplier }) }}
                      </span>
                    </div>

                    <div class="grid grid-cols-2 sm:grid-cols-6 gap-3 text-center">
                      <!-- Brood -->
                      <div class="space-y-1">
                        <span class="text-[9px] text-amber-500 font-bold uppercase">{{ $t('logbook.brood') }}</span>
                        <input 
                          v-model.number="box.brood" 
                          type="number" 
                          step="any"
                          min="0" 
                          :max="entryForm.inspectionDetail.boxMode === 'exact' ? undefined : 300" 
                          class="w-full px-2 py-1.5 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg rounded-xl text-center text-xs font-mono font-bold"
                          :placeholder="entryForm.inspectionDetail.boxMode === 'exact' ? $t('logbook.exact_placeholder_pcs') : $t('logbook.eighths_placeholder')"
                        />
                        <div v-if="calculatedBoxTotals && calculatedBoxTotals[idx]" class="text-[9px] text-gray-400 font-mono">
                          ≙ {{ calculatedBoxTotals[idx].brood }}
                        </div>
                      </div>

                      <!-- Bees -->
                      <div class="space-y-1">
                        <span class="text-[9px] text-green-500 font-bold uppercase">{{ $t('logbook.bees') }}</span>
                        <input 
                          v-model.number="box.bees" 
                          type="number" 
                          step="any"
                          min="0" 
                          :max="entryForm.inspectionDetail.boxMode === 'exact' ? undefined : 300" 
                          class="w-full px-2 py-1.5 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg rounded-xl text-center text-xs font-mono font-bold"
                          :placeholder="entryForm.inspectionDetail.boxMode === 'exact' ? $t('logbook.exact_placeholder_pcs') : $t('logbook.eighths_placeholder')"
                        />
                        <div v-if="calculatedBoxTotals && calculatedBoxTotals[idx]" class="text-[9px] text-gray-400 font-mono">
                          ≙ {{ calculatedBoxTotals[idx].bees }}
                        </div>
                      </div>

                      <!-- Drones -->
                      <div class="space-y-1">
                        <span class="text-[9px] text-sky-500 font-bold uppercase">{{ $t('logbook.drones') }}</span>
                        <input 
                          v-model.number="box.drones" 
                          type="number" 
                          step="any"
                          min="0" 
                          :max="entryForm.inspectionDetail.boxMode === 'exact' ? undefined : 300" 
                          class="w-full px-2 py-1.5 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg rounded-xl text-center text-xs font-mono font-bold"
                          :placeholder="entryForm.inspectionDetail.boxMode === 'exact' ? $t('logbook.exact_placeholder_pcs') : $t('logbook.eighths_placeholder')"
                        />
                        <div v-if="calculatedBoxTotals && calculatedBoxTotals[idx]" class="text-[9px] text-gray-400 font-mono">
                          ≙ {{ calculatedBoxTotals[idx].drones }}
                        </div>
                      </div>

                      <!-- Drone Brood -->
                      <div class="space-y-1">
                        <span class="text-[9px] text-orange-500 font-bold uppercase">{{ $t('logbook.drone_brood') }}</span>
                        <input 
                          v-model.number="box.drone_brood" 
                          type="number" 
                          step="any"
                          min="0" 
                          :max="entryForm.inspectionDetail.boxMode === 'exact' ? undefined : 300" 
                          class="w-full px-2 py-1.5 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg rounded-xl text-center text-xs font-mono font-bold"
                          :placeholder="entryForm.inspectionDetail.boxMode === 'exact' ? $t('logbook.exact_placeholder_pcs') : $t('logbook.eighths_placeholder')"
                        />
                        <div v-if="calculatedBoxTotals && calculatedBoxTotals[idx]" class="text-[9px] text-gray-400 font-mono">
                          ≙ {{ calculatedBoxTotals[idx].drone_brood }}
                        </div>
                      </div>

                      <!-- Pollen -->
                      <div class="space-y-1">
                        <span class="text-[9px] text-purple-500 font-bold uppercase">{{ $t('logbook.pollen') }}</span>
                        <input 
                          v-model.number="box.pollen" 
                          type="number" 
                          step="any"
                          min="0" 
                          :max="entryForm.inspectionDetail.boxMode === 'exact' ? undefined : 300" 
                          class="w-full px-2 py-1.5 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg rounded-xl text-center text-xs font-mono font-bold"
                          :placeholder="entryForm.inspectionDetail.boxMode === 'exact' ? $t('logbook.exact_placeholder_g') : $t('logbook.eighths_placeholder')"
                        />
                        <div v-if="calculatedBoxTotals && calculatedBoxTotals[idx]" class="text-[9px] text-gray-400 font-mono">
                          ≙ {{ calculatedBoxTotals[idx].pollen }}
                        </div>
                      </div>

                      <!-- Food -->
                      <div class="space-y-1">
                        <span class="text-[9px] text-yellow-500 font-bold uppercase">{{ $t('logbook.food') }}</span>
                        <input 
                          v-model.number="box.food" 
                          type="number" 
                          step="any"
                          min="0" 
                          :max="entryForm.inspectionDetail.boxMode === 'exact' ? undefined : 300" 
                          class="w-full px-2 py-1.5 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg rounded-xl text-center text-xs font-mono font-bold"
                          :placeholder="entryForm.inspectionDetail.boxMode === 'exact' ? $t('logbook.exact_placeholder_g') : $t('logbook.eighths_placeholder')"
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
              <h4 class="text-xs font-extrabold uppercase text-gray-500 tracking-wider">{{ $t('logbook.varroa_windel_result') }}</h4>
              <div>
                <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 mb-1">{{ $t('logbook.varroa_raw_count_label') }}</label>
                <input 
                  v-model.number="entryForm.varroaCountDetail.rawCount" 
                  type="number" 
                  required
                  min="0"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm"
                />
                <p class="text-[10px] text-gray-400 mt-1 italic">{{ $t('logbook.varroa_calc_hint') }}</p>
              </div>
            </div>

            <!-- SUB-FORM: VARROA TREATMENT DETAILS -->
            <div v-if="entryForm.entryType === 'VARROA_TREATMENT'" class="space-y-3 border-t border-gray-100 dark:border-dark-border pt-4">
              <h4 class="text-xs font-extrabold uppercase text-gray-500 tracking-wider">{{ $t('logbook.treatment_method') }}</h4>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 mb-1">{{ $t('logbook.treatment_product_label') }}</label>
                  <input 
                    v-model="entryForm.varroaTreatmentDetail.product" 
                    type="text" 
                    required
                    :placeholder="$t('logbook.treatment_product_placeholder')"
                    class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm"
                  />
                </div>
                <div>
                  <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 mb-1">{{ $t('logbook.treatment_dosage_label') }}</label>
                  <input 
                    v-model="entryForm.varroaTreatmentDetail.dosage" 
                    type="text" 
                    required
                    :placeholder="$t('logbook.treatment_dosage_placeholder')"
                    class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm"
                  />
                </div>
              </div>
              <div>
                <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 mb-1">{{ $t('logbook.treatment_notes_label') }}</label>
                <textarea 
                  v-model="entryForm.varroaTreatmentDetail.treatmentNotes" 
                  :placeholder="$t('logbook.treatment_notes_placeholder')"
                  rows="2"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm"
                ></textarea>
              </div>
            </div>

            <div class="flex justify-end space-x-2 pt-4 border-t border-gray-100 dark:border-dark-border">
              <button type="button" @click="showEntryModal = false" class="px-4 py-2 text-sm font-bold text-gray-500 hover:text-gray-700 dark:hover:text-gray-300">{{ $t('common.cancel') }}</button>
              <button type="submit" class="px-5 py-2 bg-primary hover:bg-primary-hover text-white font-extrabold text-sm rounded-xl shadow-md">
                {{ $t('common.save') }}
              </button>
            </div>
          </form>
        </div>

        <!-- Entries Table Display -->
        <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl overflow-hidden shadow-sm">
          <div v-if="loadingAllEntries" class="flex flex-col items-center justify-center py-20">
            <svg class="animate-spin h-8 w-8 text-primary mb-3" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
            <span class="text-xs text-gray-400 font-bold">{{ $t('logbook.loading_entries') }}</span>
          </div>

          <div v-else-if="filteredEntries.length === 0" class="p-12 text-center text-gray-400 italic text-sm">
            {{ $t('logbook.no_filtered_entries') }}
          </div>

          <div v-else class="overflow-x-auto">
            <table class="w-full text-left border-collapse">
              <thead>
                <tr class="bg-gray-50 dark:bg-dark-bg text-gray-500 dark:text-gray-400 text-[10px] font-bold uppercase tracking-wider border-b border-gray-100 dark:border-dark-border">
                  <th class="px-6 py-4">{{ $t('logbook.table_date') }}</th>
                  <th class="px-6 py-4">{{ $t('logbook.table_apiary_location') }}</th>
                  <th class="px-6 py-4">{{ $t('logbook.table_hive') }}</th>
                  <th class="px-6 py-4">{{ $t('logbook.table_type') }}</th>
                  <th class="px-6 py-4">{{ $t('logbook.table_notes') }}</th>
                  <th class="px-6 py-4">{{ $t('logbook.table_creator') }}</th>
                  <th class="px-6 py-4 text-center">{{ $t('logbook.table_images') }}</th>
                  <th class="px-6 py-4 text-right">{{ $t('logbook.table_actions') }}</th>
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
                      {{ getEntryTypeName(entry) }}
                    </span>
                  </td>
                  
                  <!-- Notes & details -->
                  <td class="px-6 py-4 max-w-xs md:max-w-md">
                    <p class="text-gray-700 dark:text-gray-300 italic mb-2">"{{ entry.notes || $t('logbook.no_notes_recorded') }}"</p>
                    
                    <!-- Nested details rendering -->
                    <div v-if="entry.entry_type === 'INSPECTION' && entry.inspection_detail" class="mt-2 text-[10px] bg-gray-50 dark:bg-dark-bg/40 p-2.5 rounded-xl border space-y-1.5 border-gray-100 dark:border-dark-border">
                      <div class="flex justify-between items-center pb-1 border-b border-gray-200/40 dark:border-dark-border">
                        <span class="font-bold text-gray-500 uppercase tracking-wide">{{ $t('logbook.inspection_details_header') }}</span>
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
                        {{ $t('logbook.box_calc_error') }}
                      </div>
                    </div>

                    <div v-if="entry.entry_type === 'VARROA_COUNT' && entry.varroa_count_detail" class="mt-2 text-[10px] bg-red-500/5 p-2 rounded-xl border border-red-500/10 flex space-x-3 text-red-500">
                      <div>{{ $t('logbook.measured_mites_raw') }}: <span class="font-bold font-mono">{{ entry.varroa_count_detail.raw_count }}</span></div>
                      <div>{{ $t('logbook.estimated_mites_day') }}: <span class="font-bold font-mono">{{ $t('logbook.estimated_mites_day_val', { count: entry.varroa_count_detail.estimated_total.toFixed(1) }) }}</span></div>
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
import { useI18n } from 'vue-i18n'
import { useApiaryStore } from '../stores/apiary'
import { useErrorStore } from '../stores/error'
import { useConfirmStore } from '../stores/confirm'
import AIChatPane from '../components/AIChatPane.vue'
import axios from 'axios'

const { t, locale } = useI18n()
const apiaryStore = useApiaryStore()
const errorStore = useErrorStore()
const confirmStore = useConfirmStore()

// Sessions & stream data
const sessions = ref([])
const hives = ref([])
const locations = ref([])
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
  scopeType: 'APIARY',
  hiveId: '',
  linkedApiaryIds: [],
  linkedLocationIds: [],
  linkedHiveIds: []
})

const entryForm = reactive({
  hiveId: '',
  date: new Date().toISOString().substring(0, 10),
  entryType: 'GENERAL',
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

const entryFiles = ref([])
const dragOver = ref(false)
const modalFileInput = ref(null)
const modalFileInputTable = ref(null)
const selectedTypeOption = ref('GENERAL')

// Lifecycle
onMounted(async () => {
  if (apiaryStore.activeApiaryId) {
    await Promise.all([
      fetchSessions(),
      fetchHives(),
      fetchLocations()
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
      fetchHives(),
      fetchLocations()
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

watch(showEntryModal, (newVal) => {
  if (!newVal) {
    clearEntryFormFiles()
  }
})

watch(selectedTypeOption, (newVal) => {
  if (newVal === 'INSPECTION_EXACT') {
    entryForm.entryType = 'INSPECTION'
    entryForm.inspectionDetail.boxMode = 'exact'
  } else if (newVal === 'INSPECTION_EIGHTHS') {
    entryForm.entryType = 'INSPECTION'
    entryForm.inspectionDetail.boxMode = 'eighths'
  } else {
    entryForm.entryType = newVal
  }
  
  if (entryForm.entryType === 'INSPECTION') {
    onHiveSelected()
  }
})

// Dropdown unique filter computed values
const activeHive = computed(() => hives.value.find(h => h.id === entryForm.hiveId))

const isHiveSelectorDisabled = computed(() => {
  if (!selectedSession.value) return false
  if (selectedSession.value.hive_id) return true
  if (selectedSession.value.scope_type === 'HIVE' && selectedSession.value.linked_hives?.length === 1) return true
  return false
})

const filteredHivesForEntry = computed(() => {
  if (!selectedSession.value) return hives.value
  
  const scope = selectedSession.value.scope_type || 'APIARY'
  if (scope === 'HIVE') {
    const linkedIds = selectedSession.value.linked_hives?.map(h => h.id) || []
    return hives.value.filter(h => linkedIds.includes(h.id))
  } else if (scope === 'LOCATION') {
    const linkedIds = selectedSession.value.linked_locations?.map(l => l.id) || []
    return hives.value.filter(h => linkedIds.includes(h.location_id))
  } else if (scope === 'APIARY') {
    const linkedIds = selectedSession.value.linked_apiaries?.map(a => a.id) || []
    return hives.value.filter(h => linkedIds.includes(h.apiary_id))
  }
  return hives.value
})

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
      const broodMult = box.brood_multiplier || 400.0
      const beeMult = box.bee_multiplier || 125.0
      const foodMult = box.food_multiplier || 125.0
      const droneMult = box.drone_multiplier || 100.0
      const droneBroodMult = box.drone_brood_multiplier || 230.0
      const pollenMult = box.pollen_multiplier || 40.0

      broodVal = Number(box.brood || 0) * broodMult
      beeVal = Number(box.bees || 0) * beeMult
      foodVal = Number(box.food || 0) * foodMult
      droneVal = Number(box.drones || 0) * droneMult
      droneBroodVal = Number(box.drone_brood || 0) * droneBroodMult
      pollenVal = Number(box.pollen || 0) * pollenMult
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

async function fetchLocations() {
  try {
    const response = await axios.get('/api/locations', {
      params: { apiary_id: apiaryStore.activeApiaryId }
    })
    locations.value = response.data
  } catch (err) {
    console.error('Fetch locations failed:', err)
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
  sessionForm.scopeType = 'APIARY'
  sessionForm.hiveId = ''
  sessionForm.linkedApiaryIds = apiaryStore.activeApiaryId ? [apiaryStore.activeApiaryId] : []
  sessionForm.linkedLocationIds = []
  sessionForm.linkedHiveIds = []
  showSessionModal.value = true
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function openEditSessionModal(session) {
  isEditSessionMode.value = true
  editingSessionId.value = session.id
  sessionForm.title = session.title
  sessionForm.scopeType = session.scope_type || 'APIARY'
  sessionForm.hiveId = session.hive_id || ''
  sessionForm.linkedApiaryIds = session.linked_apiaries?.map(a => a.id) || []
  sessionForm.linkedLocationIds = session.linked_locations?.map(l => l.id) || []
  sessionForm.linkedHiveIds = session.linked_hives?.map(h => h.id) || []
  showSessionModal.value = true
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

async function submitSessionForm() {
  if (!sessionForm.title.trim()) return
  if (sessionForm.title.trim().length > 30) {
    if (errorStore && typeof errorStore.showError === 'function') {
      errorStore.showError(t('logbook.limit_session_title_error'))
    } else {
      alert(t('logbook.limit_session_title_error'))
    }
    return
  }

  // Validate at least one selection
  let hasSelection = false
  if (sessionForm.scopeType === 'APIARY' && sessionForm.linkedApiaryIds.length > 0) hasSelection = true
  if (sessionForm.scopeType === 'LOCATION' && sessionForm.linkedLocationIds.length > 0) hasSelection = true
  if (sessionForm.scopeType === 'HIVE' && sessionForm.linkedHiveIds.length > 0) hasSelection = true

  if (!hasSelection) {
    if (errorStore && typeof errorStore.showError === 'function') {
      errorStore.showError(t('logbook.error_select_at_least_one'))
    } else {
      alert(t('logbook.error_select_at_least_one'))
    }
    return
  }

  const payload = {
    title: sessionForm.title.trim(),
    scope_type: sessionForm.scopeType,
    hive_id: sessionForm.hiveId || null,
    linked_apiary_ids: sessionForm.scopeType === 'APIARY' ? sessionForm.linkedApiaryIds : [],
    linked_location_ids: sessionForm.scopeType === 'LOCATION' ? sessionForm.linkedLocationIds : [],
    linked_hive_ids: sessionForm.scopeType === 'HIVE' ? sessionForm.linkedHiveIds : []
  }

  try {
    if (isEditSessionMode.value) {
      const response = await axios.put(`/api/logbook/sessions/${editingSessionId.value}`, payload)
      
      // Update selectedSession if it is the one being renamed
      if (selectedSession.value?.id === editingSessionId.value) {
        selectedSession.value = response.data
      }
      
      showSessionModal.value = false
      await fetchSessions()
    } else {
      const session = await axios.post('/api/logbook/sessions', payload, {
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
  const confirmed = await confirmStore.ask({
    title: t('logbook.delete_session'),
    message: t('logbook.delete_session_confirm', { title: session.title }),
    type: 'danger',
    confirmText: t('common.delete')
  })
  if (!confirmed) return
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
  
  entryForm.hiveId = selectedSession.value?.hive_id || (filteredHivesForEntry.value[0]?.id || '')
  entryForm.date = new Date().toISOString().substring(0, 10)
  selectedTypeOption.value = 'GENERAL'
  entryForm.notes = ''
  entryForm.inspectionDetail.assessmentMode = 'boxes'
  entryForm.inspectionDetail.boxMode = 'exact'
  entryForm.varroaCountDetail.rawCount = 0
  entryForm.varroaTreatmentDetail.product = ''
  entryForm.varroaTreatmentDetail.dosage = ''
  entryForm.varroaTreatmentDetail.treatmentNotes = ''
  
  onHiveSelected()
  clearEntryFormFiles()
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
  
  clearEntryFormFiles()
  
  if (entry.entry_type === 'INSPECTION' && entry.inspection_detail) {
    const anyEighths = (entry.inspection_detail.boxes || []).some(b =>
      b.brood_eighths != null ||
      b.bee_eighths != null ||
      b.food_eighths != null ||
      b.drone_eighths != null ||
      b.drone_brood_eighths != null ||
      b.pollen_eighths != null
    )
    selectedTypeOption.value = anyEighths ? 'INSPECTION_EIGHTHS' : 'INSPECTION_EXACT'
  } else {
    selectedTypeOption.value = entry.entry_type
  }
  if (entry.images) {
    entryFiles.value = entry.images.map(img => ({
      id: img.id,
      image_path: img.image_path,
      thumbnail_path: img.thumbnail_path,
      isExisting: true
    }))
  }
  
  if (entry.entry_type === 'INSPECTION' && entry.inspection_detail) {
    const hive = hives.value.find(h => h.id === entry.hive_id)

    const anyEighths = (entry.inspection_detail.boxes || []).some(b =>
      b.brood_eighths != null ||
      b.bee_eighths != null ||
      b.food_eighths != null ||
      b.drone_eighths != null ||
      b.drone_brood_eighths != null ||
      b.pollen_eighths != null
    )

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
          brood_multiplier: hiveBox?.frame_type?.brood_multiplier || 400.0,
          food_multiplier: hiveBox?.frame_type?.food_multiplier || 125.0,
          bee_multiplier: hiveBox?.frame_type?.bee_multiplier || 125.0,
          drone_multiplier: hiveBox?.frame_type?.drone_multiplier || 100.0,
          drone_brood_multiplier: hiveBox?.frame_type?.drone_brood_multiplier || 230.0,
          pollen_multiplier: hiveBox?.frame_type?.pollen_multiplier || 40.0,
          frame_type_name: hiveBox?.frame_type?.name || 'Zarge',
          brood: anyEighths ? (b.brood_eighths ?? 0) : (b.brood_total ?? 0),
          bees: anyEighths ? (b.bee_eighths ?? 0) : (b.bee_total ?? 0),
          food: anyEighths ? (b.food_eighths ?? 0) : (b.food_total ?? 0),
          drones: anyEighths ? (b.drone_eighths ?? 0) : (b.drone_total ?? 0),
          drone_brood: anyEighths ? (b.drone_brood_eighths ?? 0) : (b.drone_brood_total ?? 0),
          pollen: anyEighths ? (b.pollen_eighths ?? 0) : (b.pollen_total ?? 0)
        }
      })

    entryForm.inspectionDetail.assessmentMode = 'boxes'
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
      brood_multiplier: box.frame_type?.brood_multiplier || 400.0,
      food_multiplier: box.frame_type?.food_multiplier || 125.0,
      bee_multiplier: box.frame_type?.bee_multiplier || 125.0,
      drone_multiplier: box.frame_type?.drone_multiplier || 100.0,
      drone_brood_multiplier: box.frame_type?.drone_brood_multiplier || 230.0,
      pollen_multiplier: box.frame_type?.pollen_multiplier || 40.0,
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

          const broodMult = box.brood_multiplier || 400.0
          const beeMult = box.bee_multiplier || 125.0
          const foodMult = box.food_multiplier || 125.0
          const droneMult = box.drone_multiplier || 100.0
          const droneBroodMult = box.drone_brood_multiplier || 230.0
          const pollenMult = box.pollen_multiplier || 40.0

          let broodTotal, beeTotal, foodTotal, droneTotal, droneBroodTotal, pollenTotal

          if (isExact) {
            broodTotal = broodVal
            beeTotal = beeVal
            foodTotal = foodVal
            droneTotal = droneVal
            droneBroodTotal = droneBroodVal
            pollenTotal = pollenVal
          } else {
            broodTotal = broodVal * broodMult
            beeTotal = beeVal * beeMult
            foodTotal = foodVal * foodMult
            droneTotal = droneVal * droneMult
            droneBroodTotal = droneBroodVal * droneBroodMult
            pollenTotal = pollenVal * pollenMult
          }

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

    let response
    if (isEditEntryMode.value) {
      response = await axios.put(`/api/logbook/entries/${editingEntryId.value}`, payload)
    } else {
      response = await axios.post('/api/logbook/entries', payload, {
        params: { apiary_id: apiaryStore.activeApiaryId }
      })
    }

    const entryId = response.data?.id || editingEntryId.value
    const uploads = entryFiles.value.filter(f => !f.isExisting)
    for (const uf of uploads) {
      const formData = new FormData()
      formData.append('file', uf.file)
      await axios.post(`/api/logbook/entries/${entryId}/images`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
    }

    showEntryModal.value = false
    await refreshCurrentEntries()
  } catch (err) {
    errorStore.showError(t('logbook.entry_form_submission_error'), err, t('common.save'))
  }
}

async function deleteEntry(entry) {
  const confirmed = await confirmStore.ask({
    title: t('common.delete'),
    message: t('logbook.delete_entry_confirm'),
    type: 'danger',
    confirmText: t('common.delete')
  })
  if (!confirmed) return
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
    errorStore.showError(t('hives.error_upload_photo'), err, t('hives.photo_upload_btn'))
  }
}

async function deleteEntryImage(imageId) {
  const confirmed = await confirmStore.ask({
    title: t('logbook.delete_image'),
    message: t('logbook.delete_image_confirm'),
    type: 'danger',
    confirmText: t('common.delete')
  })
  if (!confirmed) return
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
  const draftType = draft.entry_type || 'GENERAL'
  if (draftType === 'INSPECTION') {
    selectedTypeOption.value = 'INSPECTION_EXACT'
  } else {
    selectedTypeOption.value = draftType
  }
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
  return d.toLocaleString(locale.value === 'de' ? 'de-DE' : 'en-US', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString(locale.value === 'de' ? 'de-DE' : 'en-US', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

function getEntryTypeName(entryOrType) {
  if (typeof entryOrType === 'object' && entryOrType !== null) {
    if (entryOrType.entry_type === 'INSPECTION') {
      const anyEighths = (entryOrType.inspection_detail?.boxes || []).some(b =>
        b.brood_eighths != null ||
        b.bee_eighths != null ||
        b.food_eighths != null ||
        b.drone_eighths != null ||
        b.drone_brood_eighths != null ||
        b.pollen_eighths != null
      )
      return anyEighths ? t('logbook.type_inspection_eighths') : t('logbook.type_inspection_exact')
    }
    return getEntryTypeName(entryOrType.entry_type)
  }
  
  switch (entryOrType) {
    case 'INSPECTION': return t('logbook.type_inspection')
    case 'VARROA_COUNT': return t('logbook.type_varroa_count')
    case 'VARROA_TREATMENT': return t('logbook.type_varroa_treatment')
    case 'GENERAL': return t('logbook.type_general')
    default: return entryOrType
  }
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
      frame_type_name: t('hives.box_label'),
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

function clearEntryFormFiles() {
  entryFiles.value.forEach(img => {
    if (!img.isExisting && img.previewUrl) {
      URL.revokeObjectURL(img.previewUrl)
    }
  })
  entryFiles.value = []
}

function handleFilesAdd(files) {
  const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
  const currentCount = entryFiles.value.length
  let addedCount = 0
  
  for (let i = 0; i < files.length; i++) {
    const file = files[i]
    if (!allowedTypes.includes(file.type.toLowerCase())) {
      errorStore.showError(t('logbook.error_unsupported_format') || 'Dateiformat nicht unterstützt')
      continue
    }
    
    if (currentCount + addedCount >= 5) {
      errorStore.showError(t('logbook.max_images_reached'))
      break
    }
    
    const previewUrl = URL.createObjectURL(file)
    entryFiles.value.push({
      file,
      previewUrl,
      isExisting: false
    })
    addedCount++
  }
}

function onFileSelect(event) {
  const files = event.target.files
  if (files && files.length > 0) {
    handleFilesAdd(files)
  }
}

function onFileDrop(event) {
  dragOver.value = false
  const files = event.dataTransfer?.files
  if (files && files.length > 0) {
    handleFilesAdd(files)
  }
}

function triggerFileInput() {
  if (viewMode.value === 'table') {
    modalFileInputTable.value?.click()
  } else {
    modalFileInput.value?.click()
  }
}

async function removeEntryFile(index) {
  const img = entryFiles.value[index]
  if (img.isExisting) {
    await deleteEntryImage(img.id)
    entryFiles.value.splice(index, 1)
  } else {
    if (img.previewUrl) {
      URL.revokeObjectURL(img.previewUrl)
    }
    entryFiles.value.splice(index, 1)
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
