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
        <h1 class="text-3xl font-extrabold text-gray-900 dark:text-white tracking-tight">
          {{ viewMode === 'calendar' ? '📅 Kalender' : '📋 Aufgaben & To-Dos' }}
        </h1>
        <p class="text-gray-500 dark:text-gray-400 mt-1">
          {{ viewMode === 'calendar' 
            ? 'Verwalte deine Termine und anstehenden Aufgaben in der Kalenderansicht.' 
            : 'Verwalte anstehende Arbeiten, Zyklen und wiederkehrende Aufgaben an deinen Ständen.' }}
        </p>
      </div>
      <button 
        @click="openCreateTaskModal" 
        class="px-5 py-2.5 bg-primary hover:bg-primary-hover text-white font-extrabold text-sm rounded-xl shadow-md shadow-primary/20 hover-scale flex items-center justify-center space-x-2 animate-fade-in"
      >
        <span>+ Neue Aufgabe</span>
      </button>
    </div>

    <!-- Active Apiary check -->
    <div v-if="!apiaryStore.activeApiaryId" class="glass rounded-3xl p-12 text-center max-w-lg mx-auto border border-dashed border-gray-300 dark:border-gray-700">
      <div class="text-4xl mb-4">📋</div>
      <h3 class="text-lg font-bold text-gray-800 dark:text-white mb-2">Keine aktive Imkerei ausgewählt</h3>
      <p class="text-gray-500 dark:text-gray-400">Bitte wähle oben eine Imkerei aus, um auf die Aufgaben zuzugreifen.</p>
    </div>

    <div v-else class="space-y-6 animate-scale">

      <!-- Quick Filter Bar -->
      <div class="flex flex-wrap items-center gap-2">
        <span class="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider shrink-0">Schnellfilter:</span>
        <button
          v-for="qf in quickFilters"
          :key="qf.key"
          @click="setQuickFilter(qf.key)"
          class="flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-extrabold tracking-wide border transition-all duration-200"
          :class="quickFilter === qf.key
            ? qf.activeClass
            : 'bg-white dark:bg-dark-card border-gray-200 dark:border-dark-border text-gray-500 dark:text-gray-400 hover:border-primary/40 hover:text-primary'"
        >
          <span>{{ qf.icon }}</span>
          <span>{{ qf.label }}</span>
          <span
            class="ml-0.5 px-1.5 py-0.5 rounded-full text-[9px] font-black"
            :class="quickFilter === qf.key ? 'bg-white/20' : 'bg-gray-100 dark:bg-dark-border text-gray-500'"
          >{{ qf.count }}</span>
        </button>
      </div>

      <!-- Filter Panel Card -->
      <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-6 shadow-sm">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-sm font-bold text-gray-900 dark:text-white flex items-center gap-1.5">
            <span>🔍 Filter-Optionen</span>
          </h3>
          <button 
            @click="resetFilters" 
            class="text-xs text-primary hover:underline font-bold"
          >
            Filter zurücksetzen
          </button>
        </div>
        
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          <!-- Status -->
          <div>
            <label class="block text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Status</label>
            <select 
              v-model="filters.status" 
              class="w-full px-3 py-2 border border-gray-200 dark:border-gray-800 dark:bg-dark-bg dark:text-white rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-primary cursor-pointer font-semibold"
            >
              <option value="ALL">Alle Aufgaben</option>
              <option value="PENDING">Offen</option>
              <option value="OVERDUE">Überfällig</option>
              <option value="COMPLETED">Abgeschlossen</option>
            </select>
          </div>
          
          <!-- Standort -->
          <div>
            <label class="block text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Standort</label>
            <select 
              v-model="filters.locationId" 
              class="w-full px-3 py-2 border border-gray-200 dark:border-gray-800 dark:bg-dark-bg dark:text-white rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-primary cursor-pointer font-semibold"
            >
              <option value="">Alle Standorte</option>
              <option v-for="loc in locations" :key="loc.id" :value="loc.id">
                {{ loc.name }}
              </option>
            </select>
          </div>
          
          <!-- Volk -->
          <div>
            <label class="block text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Volk</label>
            <select 
              v-model="filters.hiveId" 
              class="w-full px-3 py-2 border border-gray-200 dark:border-gray-800 dark:bg-dark-bg dark:text-white rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-primary cursor-pointer font-semibold"
            >
              <option value="">Alle Völker</option>
              <option v-for="h in filteredHivesForFilter" :key="h.id" :value="h.id">
                {{ h.name }}
              </option>
            </select>
          </div>
          
          <!-- Priorität -->
          <div>
            <label class="block text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Priorität</label>
            <select 
              v-model="filters.priority" 
              class="w-full px-3 py-2 border border-gray-200 dark:border-gray-800 dark:bg-dark-bg dark:text-white rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-primary cursor-pointer font-semibold"
            >
              <option value="">Alle Prioritäten</option>
              <option value="HIGH">Hoch 🔴</option>
              <option value="MEDIUM">Mittel 🟡</option>
              <option value="LOW">Niedrig 🟢</option>
            </select>
          </div>

          <!-- Von Datum -->
          <div>
            <label class="block text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Fällig Von</label>
            <input 
              v-model="filters.startDate" 
              type="date" 
              class="w-full px-3 py-2 border border-gray-200 dark:border-gray-800 dark:bg-dark-bg dark:text-white rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
          
          <!-- Bis Datum -->
          <div>
            <label class="block text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Fällig Bis</label>
            <input 
              v-model="filters.endDate" 
              type="date" 
              class="w-full px-3 py-2 border border-gray-200 dark:border-gray-800 dark:bg-dark-bg dark:text-white rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
        </div>
      </div>

      <!-- View Mode & Summary Switcher -->
      <div class="flex flex-col sm:flex-row sm:justify-between sm:items-center bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border p-4 rounded-2xl shadow-sm gap-4">
        <div class="flex items-center space-x-2">
          <span class="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Ansicht:</span>
          <div class="inline-flex rounded-xl p-0.5 bg-gray-100 dark:bg-dark-bg border border-gray-200 dark:border-dark-border">
            <button 
              @click="viewMode = 'tiles'" 
              class="px-4 py-1.5 rounded-lg text-xs font-extrabold tracking-wide transition-all"
              :class="viewMode === 'tiles' ? 'bg-white dark:bg-dark-card text-primary shadow-sm' : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'"
            >
              🗂️ Kacheln
            </button>
            <button 
              @click="viewMode = 'list'" 
              class="px-4 py-1.5 rounded-lg text-xs font-extrabold tracking-wide transition-all"
              :class="viewMode === 'list' ? 'bg-white dark:bg-dark-card text-primary shadow-sm' : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'"
            >
              📊 Liste
            </button>
            <button 
              @click="viewMode = 'calendar'" 
              class="px-4 py-1.5 rounded-lg text-xs font-extrabold tracking-wide transition-all"
              :class="viewMode === 'calendar' ? 'bg-white dark:bg-dark-card text-primary shadow-sm' : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'"
            >
              🗓️ Kalender
            </button>
          </div>
        </div>
        
        <div class="text-xs font-bold text-gray-500 dark:text-gray-400">
          Gefunden: <span class="text-primary font-extrabold">{{ filteredTasks.length }}</span> Aufgaben
        </div>
      </div>

      <!-- Loading Spinner -->
      <div v-if="loading" class="flex justify-center py-20 bg-white dark:bg-dark-card rounded-3xl border border-gray-200 dark:border-dark-border shadow-sm">
        <svg class="animate-spin h-8 w-8 text-primary" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
      </div>

      <!-- No Tasks Found -->
      <div v-else-if="viewMode !== 'calendar' && filteredTasks.length === 0" class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-12 text-center text-gray-400 italic text-sm">
        Keine Aufgaben für diese Filterkriterien vorhanden. Lege eine neue Aufgabe an, um zu starten!
      </div>

      <!-- VIEW 1: TILES GRID -->
      <div v-else-if="viewMode === 'tiles'" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div 
          v-for="task in filteredTasks" 
          :key="task.id"
          class="bg-white dark:bg-dark-card border rounded-3xl p-5 shadow-sm transition-all duration-200 flex flex-col justify-between hover:shadow-md border-gray-200 dark:border-dark-border hover:border-primary/50 relative overflow-hidden group"
          :class="{'opacity-75 border-green-500/30 dark:border-green-500/20 bg-green-500/[0.01]': task.is_completed}"
        >
          <!-- Corner Ribbon for completed tasks -->
          <div v-if="task.is_completed" class="absolute top-0 right-0 bg-green-500 text-white text-[9px] font-black uppercase px-2 py-0.5 rounded-bl-xl">
            Erledigt ✓
          </div>

          <div>
            <!-- Badges and Actions -->
            <div class="flex justify-between items-start gap-2">
              <div class="flex flex-wrap gap-1">
                <!-- Priority Badge -->
                <span 
                  class="text-[9px] font-black uppercase tracking-wider px-2 py-0.5 rounded-full"
                  :class="getPriorityBadgeClass(task.priority)"
                >
                  {{ getPriorityText(task.priority) }}
                </span>
                
                <!-- Recurrence Badge -->
                <span 
                  v-if="task.is_recurring"
                  class="text-[9px] font-black uppercase tracking-wider px-2 py-0.5 rounded-full bg-indigo-100 text-indigo-700 dark:bg-indigo-950/40 dark:text-indigo-400 flex items-center gap-1"
                  title="Wiederkehrende Aufgabe"
                >
                  🔄 {{ getRecurrenceIntervalText(task.recurrence_interval) }}
                </span>
              </div>

              <!-- Delete/Edit Actions -->
              <div class="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <button 
                  @click="openEditTaskModal(task)"
                  class="p-1 text-gray-400 hover:text-primary hover:bg-primary/10 rounded-lg transition-all"
                  title="Aufgabe bearbeiten"
                >
                  <svg class="w-4.5 h-4.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/></svg>
                </button>
                <button 
                  @click="deleteTask(task.id)"
                  class="p-1 text-gray-400 hover:text-red-500 hover:bg-red-500/10 rounded-lg transition-all"
                  title="Aufgabe löschen"
                >
                  <svg class="w-4.5 h-4.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                </button>
              </div>
            </div>

            <!-- Title -->
            <h4 class="font-extrabold text-lg text-gray-900 dark:text-white mt-3 leading-tight" :class="{'line-through text-gray-400 dark:text-gray-500': task.is_completed}">
              {{ task.title }}
            </h4>

            <!-- Description -->
            <p v-if="task.description" class="text-sm text-gray-500 dark:text-gray-400 mt-2 line-clamp-3 leading-relaxed italic">
              "{{ task.description }}"
            </p>

            <!-- Links (Location / Hive) -->
            <div class="mt-3.5 flex flex-wrap gap-1.5">
              <span v-if="task.location" class="inline-flex items-center text-xs font-bold bg-blue-500/10 text-blue-600 dark:bg-blue-950/30 dark:text-blue-400 px-2.5 py-1 rounded-lg">
                📍 Stand: {{ task.location.name }}
              </span>
              <span v-if="task.hive" class="inline-flex items-center text-xs font-bold bg-amber-500/10 text-amber-700 dark:bg-amber-950/30 dark:text-primary px-2.5 py-1 rounded-lg">
                🐝 Volk: {{ task.hive.name }}
              </span>
            </div>
          </div>

          <!-- Bottom Footer details and check off action -->
          <div class="mt-5 pt-3.5 border-t border-gray-100 dark:border-dark-border/60 flex items-center justify-between">
            <div class="text-xs font-mono">
              <span v-if="task.is_completed" class="text-green-500 dark:text-green-400 font-bold">
                Erledigt am: {{ formatDate(task.completed_at) }}
              </span>
              <span v-else :class="isOverdue(task.due_date) ? 'text-red-500 font-bold animate-pulse' : 'text-gray-400 dark:text-gray-500'">
                Fällig: {{ formatDate(task.due_date) || 'Kein Datum' }}
              </span>
            </div>
            
            <button 
              v-if="!task.is_completed"
              @click="completeTask(task.id)"
              class="px-3.5 py-1.5 bg-green-500 hover:bg-green-600 dark:bg-green-600 dark:hover:bg-green-700 text-white font-extrabold text-xs uppercase tracking-wider rounded-xl shadow transition-colors flex items-center gap-1 cursor-pointer"
            >
              <span>Erledigt</span> ✓
            </button>
          </div>
        </div>
      </div>

      <!-- VIEW 2: LIST / TABLE -->
      <div v-else-if="viewMode === 'list'" class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl overflow-hidden shadow-sm">
        <div class="overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="bg-gray-50 dark:bg-dark-bg/60 border-b border-gray-200 dark:border-dark-border text-[10px] font-black uppercase tracking-wider text-gray-500 dark:text-gray-400">
                <th class="py-4 px-6 w-12 text-center">Status</th>
                <th class="py-4 px-4">Bezeichnung</th>
                <th class="py-4 px-4 w-40">Zugeordnet</th>
                <th class="py-4 px-4 w-28">Fälligkeit</th>
                <th class="py-4 px-4 w-24">Priorität</th>
                <th class="py-4 px-4 w-24">Intervall</th>
                <th class="py-4 px-6 w-20 text-right">Aktionen</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100 dark:divide-dark-border">
              <tr 
                v-for="task in filteredTasks" 
                :key="task.id"
                class="hover:bg-gray-50/50 dark:hover:bg-dark-card/50 transition-colors"
                :class="{'opacity-75 bg-green-500/[0.005]': task.is_completed}"
              >
                <!-- Check off circle checkbox -->
                <td class="py-4 px-6 text-center">
                  <button 
                    @click="task.is_completed ? null : completeTask(task.id)"
                    class="w-5.5 h-5.5 rounded-full border-2 flex items-center justify-center transition-colors cursor-pointer"
                    :class="task.is_completed 
                      ? 'border-green-500 bg-green-500 text-white' 
                      : 'border-gray-300 dark:border-gray-600 hover:border-green-500'"
                    :disabled="task.is_completed"
                  >
                    <svg v-if="task.is_completed" class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"/></svg>
                  </button>
                </td>
                
                <!-- Title & Description -->
                <td class="py-4 px-4">
                  <h4 class="text-sm font-bold text-gray-900 dark:text-white leading-snug" :class="{'line-through text-gray-400 dark:text-gray-500': task.is_completed}">
                    {{ task.title }}
                  </h4>
                  <p v-if="task.description" class="text-xs text-gray-400 dark:text-gray-500 italic mt-0.5 line-clamp-1">
                    {{ task.description }}
                  </p>
                </td>
                
                <!-- Scope Links -->
                <td class="py-4 px-4">
                  <div class="flex flex-col gap-0.5">
                    <span v-if="task.location" class="text-[10px] text-blue-600 dark:text-blue-400 font-bold truncate">📍 {{ task.location.name }}</span>
                    <span v-if="task.hive" class="text-[10px] text-amber-700 dark:text-primary font-bold truncate">🐝 {{ task.hive.name }}</span>
                  </div>
                </td>
                
                <!-- Due Date -->
                <td class="py-4 px-4 text-xs font-mono">
                  <span v-if="task.is_completed" class="text-green-500 font-bold">Erledigt</span>
                  <span v-else :class="isOverdue(task.due_date) ? 'text-red-500 font-black animate-pulse' : 'text-gray-600 dark:text-gray-300'">
                    {{ formatDate(task.due_date) || '—' }}
                  </span>
                </td>
                
                <!-- Priority -->
                <td class="py-4 px-4">
                  <span 
                    class="text-[9px] font-black uppercase px-2 py-0.5 rounded-full inline-block"
                    :class="getPriorityBadgeClass(task.priority)"
                  >
                    {{ getPriorityText(task.priority) }}
                  </span>
                </td>
                
                <!-- Recurrence -->
                <td class="py-4 px-4 text-xs font-bold text-indigo-600 dark:text-indigo-400">
                  <span v-if="task.is_recurring" class="flex items-center gap-1">
                    🔄 {{ getRecurrenceIntervalText(task.recurrence_interval) }}
                  </span>
                  <span v-else class="text-gray-400 dark:text-gray-600">—</span>
                </td>
                
                <!-- Delete & Edit -->
                <td class="py-4 px-6 text-right">
                  <div class="inline-flex items-center space-x-1">
                    <button 
                      @click="openEditTaskModal(task)"
                      class="p-1.5 text-gray-400 hover:text-primary hover:bg-primary/10 rounded-lg transition-all"
                      title="Aufgabe bearbeiten"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/></svg>
                    </button>
                    <button 
                      @click="deleteTask(task.id)"
                      class="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-500/10 rounded-lg transition-all"
                      title="Aufgabe löschen"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- VIEW 3: CALENDAR -->
      <div v-else class="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <div class="xl:col-span-2 bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-4 shadow-sm">
          <VCalendar
            expanded
            borderless
            locale="de-DE"
            :attributes="calendarAttributes"
            @dayclick="onCalendarDayClick"
          />
        </div>

        <div class="space-y-4">
          <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-5 shadow-sm">
            <h4 class="text-sm font-extrabold text-gray-900 dark:text-white mb-3">📌 Fällig am {{ formatDate(selectedDateString) }}</h4>

            <div v-if="!selectedDateTaskItems.length && !selectedDateCustomItems.length" class="text-xs text-gray-500 dark:text-gray-400 italic">
              Keine Aufgaben oder Termine für diesen Tag.
            </div>

            <div v-else class="space-y-2">
              <div
                v-for="item in selectedDateTaskItems"
                :key="`task-day-${item.id}`"
                class="p-2.5 rounded-xl border text-xs"
                :class="item.is_completed ? 'border-green-200 bg-green-50/70 dark:border-green-900/30 dark:bg-green-950/10' : 'border-gray-200 bg-gray-50 dark:border-dark-border dark:bg-dark-bg/60'"
              >
                <div class="font-bold text-gray-900 dark:text-white">{{ item.title }}</div>
                <div class="text-gray-500 dark:text-gray-400 mt-0.5">Aufgabe</div>
              </div>

              <div
                v-for="item in selectedDateCustomItems"
                :key="`custom-day-${item.id}`"
                class="p-2.5 rounded-xl border text-xs"
                :style="{ borderColor: item.color + '55' }"
              >
                <div class="font-bold text-gray-900 dark:text-white">{{ item.title }}</div>
                <div class="text-gray-500 dark:text-gray-400 mt-0.5">
                  Termin: {{ formatDate(item.start_date) }}<span v-if="item.end_date !== item.start_date"> - {{ formatDate(item.end_date) }}</span>
                </div>
              </div>
            </div>
          </div>

          <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-5 shadow-sm">
            <div class="flex items-center justify-between mb-3">
              <h4 class="text-sm font-extrabold text-gray-900 dark:text-white">🗂️ Eigener Termin</h4>
              <button
                v-if="customEventForm.id"
                @click="resetCustomEventForm"
                class="text-[11px] font-bold text-primary hover:underline"
              >
                Neu
              </button>
            </div>

            <form class="space-y-3" @submit.prevent="saveCustomEvent">
              <input
                v-model="customEventForm.title"
                type="text"
                required
                placeholder="z.B. Wanderung Rapsfeld"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-primary"
              />

              <div class="grid grid-cols-2 gap-2">
                <input
                  v-model="customEventForm.start_date"
                  type="date"
                  required
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-primary"
                />
                <input
                  v-model="customEventForm.end_date"
                  type="date"
                  required
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>

              <div class="grid grid-cols-[1fr_auto] gap-2 items-center">
                <input
                  v-model="customEventForm.notes"
                  type="text"
                  placeholder="Notiz (optional)"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-primary"
                />
                <input
                  v-model="customEventForm.color"
                  type="color"
                  class="h-9 w-11 p-1 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-dark-bg cursor-pointer"
                />
              </div>

              <button
                type="submit"
                class="w-full px-4 py-2 bg-primary hover:bg-primary-hover text-white text-xs font-extrabold uppercase tracking-wider rounded-xl"
              >
                {{ customEventForm.id ? 'Termin speichern' : 'Termin anlegen' }}
              </button>
            </form>

            <div class="mt-4 pt-4 border-t border-gray-100 dark:border-dark-border space-y-2 max-h-56 overflow-y-auto">
              <div
                v-for="event in customEvents"
                :key="event.id"
                class="p-2.5 rounded-xl border border-gray-200 dark:border-dark-border bg-gray-50 dark:bg-dark-bg/60"
              >
                <div class="flex items-start justify-between gap-2">
                  <div>
                    <div class="text-xs font-bold text-gray-900 dark:text-white flex items-center gap-1.5">
                      <span class="inline-block w-2.5 h-2.5 rounded-full" :style="{ backgroundColor: event.color }"></span>
                      <span>{{ event.title }}</span>
                    </div>
                    <div class="text-[11px] text-gray-500 dark:text-gray-400 mt-0.5">
                      {{ formatDate(event.start_date) }}<span v-if="event.end_date !== event.start_date"> - {{ formatDate(event.end_date) }}</span>
                    </div>
                  </div>

                  <div class="flex items-center gap-1">
                    <button @click="editCustomEvent(event)" class="text-[11px] text-primary font-bold hover:underline">Bearbeiten</button>
                    <button @click="removeCustomEvent(event.id)" class="text-[11px] text-red-500 font-bold hover:underline">Löschen</button>
                  </div>
                </div>
              </div>

              <p v-if="customEvents.length === 0" class="text-xs text-gray-500 dark:text-gray-400 italic">
                Noch keine eigenen Termine vorhanden.
              </p>
            </div>
          </div>
        </div>
      </div>

    </div>

    <!-- CREATE/EDIT TASK DIALOG MODAL -->
    <div v-if="showTaskModal" class="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <!-- Backdrop -->
        <div @click="showTaskModal = false" class="fixed inset-0 z-0 bg-black/45 transition-opacity" aria-hidden="true"></div>

        <!-- Center modal contents -->
        <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>

        <div class="relative z-10 inline-block align-bottom bg-white dark:bg-dark-card rounded-3xl text-left overflow-hidden shadow-2xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full border border-gray-100 dark:border-dark-border animate-scale">
          <!-- Header -->
          <div class="px-6 py-4 border-b border-gray-100 dark:border-dark-border flex justify-between items-center bg-gray-50/50 dark:bg-dark-bg/25">
            <h3 class="text-lg font-extrabold text-gray-900 dark:text-white" id="modal-title">
              {{ isEditMode ? '📝 Aufgabe bearbeiten' : '📝 Neue Aufgabe erfassen' }}
            </h3>
            <button @click="showTaskModal = false" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
            </button>
          </div>

          <form @submit.prevent="submitTaskForm">
            <!-- Form Body -->
            <div class="p-6 space-y-4">
              <!-- Title -->
              <div>
                <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">Bezeichnung *</label>
                <input 
                  v-model="taskForm.title" 
                  type="text" 
                  required
                  placeholder="z.B. Varroagitter einschieben"
                  class="w-full px-3 py-2.5 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm font-semibold"
                />
              </div>

              <!-- Description -->
              <div>
                <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">Beschreibung / Details</label>
                <textarea 
                  v-model="taskForm.description" 
                  placeholder="Zusätzliche Notizen zur Durchführung..."
                  rows="2"
                  class="w-full px-3 py-2.5 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm"
                ></textarea>
              </div>

              <!-- Scope Section: Location / Hive -->
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">Standort (Optional)</label>
                  <select 
                    v-model="taskForm.locationId" 
                    @change="onLocationChange"
                    class="w-full px-3 py-2.5 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-xs cursor-pointer font-bold"
                  >
                    <option value="">Global (Alle Stände)</option>
                    <option v-for="loc in locations" :key="loc.id" :value="loc.id">
                      {{ loc.name }}
                    </option>
                  </select>
                </div>
                <div>
                  <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">Bienenvolk (Optional)</label>
                  <select 
                    v-model="taskForm.hiveId" 
                    class="w-full px-3 py-2.5 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-xs cursor-pointer font-bold"
                  >
                    <option value="">Keines (Global für Stand)</option>
                    <option v-for="hive in filteredHivesForForm" :key="hive.id" :value="hive.id">
                      {{ hive.name }}
                    </option>
                  </select>
                </div>
              </div>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <!-- Priority -->
                <div>
                  <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">Priorisierung *</label>
                  <select 
                    v-model="taskForm.priority" 
                    required
                    class="w-full px-3 py-2.5 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-xs cursor-pointer font-bold"
                  >
                    <option value="LOW">Niedrig (Grün)</option>
                    <option value="MEDIUM">Mittel (Gelb)</option>
                    <option value="HIGH">Hoch (Rot)</option>
                  </select>
                </div>

                <!-- Due Date -->
                <div>
                  <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">Fälligkeitsdatum</label>
                  <input 
                    v-model="taskForm.dueDate" 
                    type="date" 
                    class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 bg-white dark:bg-dark-bg text-gray-900 dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm font-semibold [color-scheme:light] dark:[color-scheme:dark]"
                  />
                </div>
              </div>

              <!-- Recurrence Settings -->
              <div class="border-t border-gray-100 dark:border-dark-border/80 pt-4 space-y-3">
                <div class="flex items-center justify-between">
                  <div>
                    <h5 class="text-xs font-bold text-gray-800 dark:text-gray-200 uppercase tracking-wide">🔄 Wiederholende Aufgabe</h5>
                    <p class="text-[10px] text-gray-400 dark:text-gray-500">Auto-Generierung bei Fertigstellung</p>
                  </div>
                  <input 
                    v-model="taskForm.isRecurring" 
                    type="checkbox"
                    class="w-5 h-5 rounded border-gray-300 text-primary focus:ring-primary cursor-pointer"
                  />
                </div>

                <div v-if="taskForm.isRecurring" class="animate-scale">
                  <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">Wiederholungsintervall</label>
                  <select 
                    v-model="taskForm.recurrenceInterval" 
                    required
                    class="w-full px-3 py-2.5 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-xs cursor-pointer font-bold"
                  >
                    <option value="DAILY">Täglich</option>
                    <option value="WEEKLY">Wöchentlich</option>
                    <option value="BIWEEKLY">Alle 2 Wochen</option>
                    <option value="MONTHLY">Monatlich</option>
                    <option value="YEARLY">Jährlich</option>
                  </select>
                </div>
              </div>
            </div>

            <!-- Footer -->
            <div class="px-6 py-4 bg-gray-50 dark:bg-dark-bg/25 border-t border-gray-100 dark:border-dark-border flex justify-end space-x-2">
              <button 
                type="button" 
                @click="showTaskModal = false" 
                class="px-4 py-2 text-xs font-bold text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
              >
                Abbrechen
              </button>
              <button 
                type="submit" 
                class="px-5 py-2 bg-primary hover:bg-primary-hover text-white font-extrabold text-xs uppercase tracking-wider rounded-xl shadow-md cursor-pointer"
              >
                {{ isEditMode ? 'Speichern' : 'Erstellen' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useApiaryStore } from '../stores/apiary'
import { useErrorStore } from '../stores/error'
import { useConfirmStore } from '../stores/confirm'
import { getCustomCalendarEvents, upsertCustomCalendarEvent, deleteCustomCalendarEvent, isDateInRange } from '../utils/calendarEvents'
import axios from 'axios'

const apiaryStore = useApiaryStore()
const errorStore = useErrorStore()
const confirmStore = useConfirmStore()
const route = useRoute()
const router = useRouter()


const loading = ref(false)
const tasks = ref([])
const locations = ref([])
const hives = ref([])
const viewMode = ref('tiles')
const customEvents = ref([])
const selectedDateString = ref(todayStr())
const customEventForm = ref({
  id: null,
  title: '',
  notes: '',
  start_date: todayStr(),
  end_date: todayStr(),
  color: '#2563eb'
})

// Filter state
const filters = ref({
  status: 'ALL',
  locationId: '',
  hiveId: '',
  priority: '',
  startDate: '',
  endDate: ''
})

// Quick filter state — persisted in sessionStorage
const QF_KEY = 'bb_task_quick_filter'
const quickFilter = ref(sessionStorage.getItem(QF_KEY) || 'TODAY')

function setQuickFilter(key) {
  quickFilter.value = key
  sessionStorage.setItem(QF_KEY, key)
}

function todayStr() {
  return new Date().toISOString().split('T')[0]
}

const quickFilters = computed(() => [
  {
    key: 'TODAY',
    label: 'Heute fällig',
    icon: '📅',
    activeClass: 'bg-primary border-primary text-white shadow-md shadow-primary/20',
    count: tasks.value.filter(t => !t.is_completed && t.due_date === todayStr()).length
  },
  {
    key: 'OVERDUE',
    label: 'Überfällig',
    icon: '🔴',
    activeClass: 'bg-red-500 border-red-500 text-white shadow-md shadow-red-500/20',
    count: tasks.value.filter(t => !t.is_completed && t.due_date && t.due_date < todayStr()).length
  },
  {
    key: 'UPCOMING',
    label: 'Anstehend',
    icon: '⏳',
    activeClass: 'bg-blue-500 border-blue-500 text-white shadow-md shadow-blue-500/20',
    count: tasks.value.filter(t => !t.is_completed && (!t.due_date || t.due_date > todayStr())).length
  }
])

// Modal form state
const showTaskModal = ref(false)
const isEditMode = ref(false)
const editingTaskId = ref(null)
const taskForm = ref({
  title: '',
  description: '',
  locationId: '',
  hiveId: '',
  priority: 'MEDIUM',
  dueDate: '',
  isRecurring: false,
  recurrenceInterval: 'WEEKLY'
})

// Filter hives based on selected location
const filteredHivesForFilter = computed(() => {
  if (!filters.value.locationId) return hives.value
  return hives.value.filter(h => h.location_id === filters.value.locationId)
})

const filteredHivesForForm = computed(() => {
  if (!taskForm.value.locationId) return hives.value
  return hives.value.filter(h => h.location_id === taskForm.value.locationId)
})

// Fetch all dependencies
async function fetchData() {
  if (!apiaryStore.activeApiaryId) return
  loading.value = true
  try {
    const apiaryId = apiaryStore.activeApiaryId
    const [locRes, hivesRes, tasksRes] = await Promise.all([
      axios.get('/api/locations', { params: { apiary_id: apiaryId } }),
      axios.get('/api/hives', { params: { apiary_id: apiaryId } }),
      axios.get('/api/tasks', { params: { apiary_id: apiaryId } })
    ])
    
    locations.value = locRes.data
    hives.value = hivesRes.data
    tasks.value = tasksRes.data
    customEvents.value = getCustomCalendarEvents(apiaryId)
  } catch (err) {
    errorStore.showError('Fehler beim Laden der Aufgabendaten.', err, 'Aufgaben')
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  if (route.query.view === 'calendar' || route.path === '/calendar') {
    viewMode.value = 'calendar'
    setQuickFilter('ALL')
  }

  await fetchData()
  if (route.query.hiveId) {
    filters.value.hiveId = route.query.hiveId
    filters.value.status = 'ALL'
    quickFilter.value = 'ALL'
    
    if (route.query.createTask === 'true') {
      openCreateTaskModal()
    }
  }
})

watch(() => apiaryStore.activeApiaryId, () => {
  fetchData()
  resetCustomEventForm()
})

watch(viewMode, (newMode) => {
  if (newMode === 'calendar') {
    if (quickFilter.value !== 'ALL') {
      setQuickFilter('ALL')
    }
    if (route.path !== '/calendar' && route.query.view !== 'calendar') {
      router.push({ path: '/calendar' })
    }
  } else {
    if (route.path === '/calendar') {
      router.push({ path: '/tasks' })
    } else if (route.query.view === 'calendar') {
      router.push({ path: '/tasks' })
    }
  }
})

watch(() => route.path, (newPath) => {
  if (newPath === '/calendar') {
    viewMode.value = 'calendar'
  } else if (newPath === '/tasks') {
    if (route.query.view === 'calendar') {
      viewMode.value = 'calendar'
    } else {
      if (viewMode.value === 'calendar') {
        viewMode.value = 'tiles'
      }
    }
  }
})

watch(() => route.query.view, (newView) => {
  if (newView === 'calendar') {
    viewMode.value = 'calendar'
  } else if (route.path === '/tasks') {
    if (viewMode.value === 'calendar') {
      viewMode.value = 'tiles'
    }
  }
})

watch(() => route.query.hiveId, (newHiveId) => {
  if (newHiveId) {
    filters.value.hiveId = newHiveId
    filters.value.status = 'ALL'
    quickFilter.value = 'ALL'
    if (route.query.createTask === 'true') {
      openCreateTaskModal(newHiveId)
    }
  } else {
    filters.value.hiveId = ''
  }
})

watch(() => route.query.createTask, (newVal) => {
  if (newVal === 'true') {
    openCreateTaskModal()
  }
})

watch(showTaskModal, (isOpen) => {
  if (!isOpen) {
    if (route.query.createTask) {
      const query = { ...route.query }
      delete query.createTask
      router.replace({ query })
    }
  }
})


// If location changes, reset hive filter
function onLocationChange() {
  taskForm.value.hiveId = ''
}

// Compute client-side filtering matching standard backend API filters
const filteredTasks = computed(() => {
  const today = todayStr()
  return tasks.value.filter(task => {
    // 0. Quick Filter (applied first)
    if (quickFilter.value === 'TODAY') {
      if (task.is_completed || task.due_date !== today) return false
    } else if (quickFilter.value === 'OVERDUE') {
      if (task.is_completed || !task.due_date || task.due_date >= today) return false
    } else if (quickFilter.value === 'UPCOMING') {
      if (task.is_completed || (task.due_date && task.due_date <= today)) return false
    }

    // 1. Status Filter (detail filter)
    if (filters.value.status === 'PENDING' && task.is_completed) return false
    if (filters.value.status === 'COMPLETED' && !task.is_completed) return false
    if (filters.value.status === 'OVERDUE') {
      if (task.is_completed) return false
      if (!task.due_date || !isOverdue(task.due_date)) return false
    }

    // 2. Location
    if (filters.value.locationId && task.location_id !== filters.value.locationId) return false

    // 3. Hive
    if (filters.value.hiveId && task.hive_id !== filters.value.hiveId) return false

    // 4. Priority
    if (filters.value.priority && task.priority !== filters.value.priority) return false

    // 5. Date Range
    if (filters.value.startDate && task.due_date && task.due_date < filters.value.startDate) return false
    if (filters.value.endDate && task.due_date && task.due_date > filters.value.endDate) return false

    return true
  })
})

const calendarAttributes = computed(() => {
  const taskAttributes = filteredTasks.value
    .filter(task => task.due_date)
    .map(task => {
      const isDone = task.is_completed
      const overdue = !isDone && isOverdue(task.due_date)
      return {
        key: `task-${task.id}`,
        dates: new Date(`${task.due_date}T12:00:00`),
        dot: { color: isDone ? '#16a34a' : overdue ? '#dc2626' : '#f59e0b' },
        popover: { label: `Aufgabe: ${task.title}` }
      }
    })

  const customAttributes = customEvents.value.map(event => ({
    key: `custom-${event.id}`,
    dates: {
      start: new Date(`${event.start_date}T12:00:00`),
      end: new Date(`${event.end_date}T12:00:00`)
    },
    highlight: { color: event.color, fillMode: 'outline' },
    popover: { label: `Termin: ${event.title}` }
  }))

  return [
    {
      key: 'today',
      dates: new Date(),
      highlight: { color: '#f59e0b', fillMode: 'light' }
    },
    ...taskAttributes,
    ...customAttributes
  ]
})

const selectedDateTaskItems = computed(() => {
  return filteredTasks.value.filter(task => task.due_date === selectedDateString.value)
})

const selectedDateCustomItems = computed(() => {
  return customEvents.value.filter(event => isDateInRange(selectedDateString.value, event.start_date, event.end_date))
})

function onCalendarDayClick(dayInfo) {
  const dateValue = dayInfo?.id || dayInfo?.date || dayInfo
  selectedDateString.value = toDateString(dateValue)
}

function toDateString(value) {
  const dateValue = value instanceof Date ? value : new Date(value)
  if (Number.isNaN(dateValue.getTime())) return todayStr()
  return dateValue.toISOString().slice(0, 10)
}

function resetCustomEventForm() {
  customEventForm.value = {
    id: null,
    title: '',
    notes: '',
    start_date: selectedDateString.value || todayStr(),
    end_date: selectedDateString.value || todayStr(),
    color: '#2563eb'
  }
}

async function saveCustomEvent() {
  if (!apiaryStore.activeApiaryId) return
  try {
    upsertCustomCalendarEvent(apiaryStore.activeApiaryId, customEventForm.value)
    customEvents.value = getCustomCalendarEvents(apiaryStore.activeApiaryId)
    resetCustomEventForm()
  } catch (err) {
    errorStore.showError('Fehler beim Speichern des Kalendereintrags.', err, 'Kalender')
  }
}

function editCustomEvent(event) {
  customEventForm.value = { ...event }
}

async function removeCustomEvent(eventId) {
  const confirmed = await confirmStore.ask({
    title: 'Termin löschen',
    message: 'Möchtest du diesen eigenen Termin wirklich löschen?',
    type: 'danger',
    confirmText: 'Ja, löschen'
  })
  if (!confirmed) return

  deleteCustomCalendarEvent(apiaryStore.activeApiaryId, eventId)
  customEvents.value = getCustomCalendarEvents(apiaryStore.activeApiaryId)
  if (customEventForm.value.id === eventId) {
    resetCustomEventForm()
  }
}

function resetFilters() {
  filters.value = {
    status: 'PENDING',
    locationId: '',
    hiveId: '',
    priority: '',
    startDate: '',
    endDate: ''
  }
}

// Task actions
async function completeTask(id) {
  try {
    const res = await axios.post(`/api/tasks/${id}/complete`)
    
    // Update local task
    const index = tasks.value.findIndex(t => t.id === id)
    if (index !== -1) {
      tasks.value[index] = res.data
    }
    
    // Re-fetch to load new recurring instances if they were spawned
    if (res.data.is_recurring) {
      await fetchData()
    }
  } catch (err) {
    errorStore.showError('Fehler beim Abschließen der Aufgabe.', err, 'Aufgabe abschließen')
  }
}

async function deleteTask(id) {
  const confirmed = await confirmStore.ask({
    title: 'Aufgabe löschen',
    message: 'Möchtest du diese Aufgabe wirklich löschen?',
    type: 'danger',
    confirmText: 'Ja, löschen'
  })
  if (!confirmed) return
  try {
    await axios.delete(`/api/tasks/${id}`)
    tasks.value = tasks.value.filter(t => t.id !== id)
  } catch (err) {
    errorStore.showError('Fehler beim Löschen der Aufgabe.', err, 'Aufgabe löschen')
  }
}

function openCreateTaskModal(overrideHiveId = null) {
  isEditMode.value = false
  editingTaskId.value = null
  
  let initialLocationId = ''
  let initialHiveId = ''
  
  const targetHiveId = overrideHiveId || route.query.hiveId
  if (targetHiveId) {
    const hive = hives.value.find(h => h.id === targetHiveId)
    if (hive) {
      initialHiveId = hive.id
      initialLocationId = hive.location_id || ''
    }
  }

  taskForm.value = {
    title: '',
    description: '',
    locationId: initialLocationId,
    hiveId: initialHiveId,
    priority: 'MEDIUM',
    dueDate: '',
    isRecurring: false,
    recurrenceInterval: 'WEEKLY'
  }
  showTaskModal.value = true
}

function openEditTaskModal(task) {
  isEditMode.value = true
  editingTaskId.value = task.id
  taskForm.value = {
    title: task.title,
    description: task.description || '',
    locationId: task.location_id || '',
    hiveId: task.hive_id || '',
    priority: task.priority,
    dueDate: task.due_date || '',
    isRecurring: task.is_recurring,
    recurrenceInterval: task.recurrence_interval || 'WEEKLY'
  }
  showTaskModal.value = true
}

async function submitTaskForm() {
  try {
    const payload = {
      title: taskForm.value.title.trim(),
      description: taskForm.value.description.trim() || null,
      due_date: taskForm.value.dueDate || null,
      priority: taskForm.value.priority,
      location_id: taskForm.value.locationId || null,
      hive_id: taskForm.value.hiveId || null,
      is_recurring: taskForm.value.isRecurring,
      recurrence_interval: taskForm.value.isRecurring ? taskForm.value.recurrenceInterval : null
    }

    if (isEditMode.value) {
      const res = await axios.put(`/api/tasks/${editingTaskId.value}`, payload)
      const index = tasks.value.findIndex(t => t.id === editingTaskId.value)
      if (index !== -1) {
        tasks.value[index] = res.data
      }
    } else {
      const res = await axios.post(`/api/tasks`, payload, {
        params: { apiary_id: apiaryStore.activeApiaryId }
      })
      tasks.value.unshift(res.data)
    }
    
    showTaskModal.value = false
  } catch (err) {
    errorStore.showError('Fehler beim Speichern der Aufgabe.', err, 'Aufgabe speichern')
  }
}

// Helpers
function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

function isOverdue(dateStr) {
  if (!dateStr) return false
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const d = new Date(dateStr)
  d.setHours(0, 0, 0, 0)
  return d < today
}

function getPriorityText(prio) {
  switch (prio) {
    case 'HIGH': return 'Hoch 🔴'
    case 'MEDIUM': return 'Mittel 🟡'
    case 'LOW': return 'Niedrig 🟢'
    default: return prio
  }
}

function getPriorityBadgeClass(prio) {
  switch (prio) {
    case 'HIGH': return 'bg-red-100 text-red-700 dark:bg-red-950/40 dark:text-red-400'
    case 'MEDIUM': return 'bg-yellow-100 text-yellow-700 dark:bg-yellow-950/40 dark:text-yellow-400'
    case 'LOW': return 'bg-green-100 text-green-700 dark:bg-green-950/40 dark:text-green-400'
    default: return 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-400'
  }
}

function getRecurrenceIntervalText(interval) {
  switch (interval?.toUpperCase()) {
    case 'DAILY': return 'Täglich'
    case 'WEEKLY': return 'Wöchentlich'
    case 'BIWEEKLY': return 'Alle 2 Wochen'
    case 'MONTHLY': return 'Monatlich'
    case 'YEARLY': return 'Jährlich'
    default: return interval
  }
}
</script>

<style scoped>
@reference "../style.css";
</style>
