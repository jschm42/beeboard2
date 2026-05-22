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
        <h1 class="text-3xl font-extrabold text-gray-900 dark:text-white tracking-tight">🐝 Bienenvölker</h1>
        <p class="text-gray-500 dark:text-gray-400 mt-1">Verwalte deine Bienenvölker, Königinnen und Zargensysteme.</p>
      </div>
      <div class="flex space-x-2">
        <button 
          @click="openCreateModal" 
          class="px-5 py-2.5 bg-primary hover:bg-primary-hover text-white font-extrabold text-sm rounded-xl shadow-md shadow-primary/20 hover-scale flex items-center justify-center space-x-2"
        >
          <span>+ Neues Volk</span>
        </button>
      </div>
    </div>
    <!-- Alert Banner -->
    <div v-if="alertMessage" class="mb-6 p-4 rounded-xl text-sm flex items-start space-x-2 animate-pulse" :class="alertClass">
      <svg class="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
      <span>{{ alertMessage }}</span>
    </div>

    <!-- Empty State -->
    <div v-if="!loading && hives.length === 0" class="glass rounded-3xl p-12 text-center max-w-lg mx-auto border border-dashed border-gray-300 dark:border-gray-700 mt-8">
      <div class="text-4xl mb-4">🐝</div>
      <h3 class="text-lg font-bold text-gray-800 dark:text-white mb-1">Keine Bienenvölker angelegt</h3>
      <p class="text-gray-500 dark:text-gray-400 mb-6">Lege dein erstes Volk an, um danach Inspektionen und Honigräume verwalten zu können.</p>
      <button @click="openCreateModal" class="px-5 py-2.5 bg-primary hover:bg-primary-hover text-white font-extrabold text-sm rounded-xl shadow-md hover-scale">
        + Erstes Volk anlegen
      </button>
    </div>

    <div v-else>
      <!-- Filters & View Switcher Bar -->
      <div v-if="!loading && hives.length > 0" class="mb-6 bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-4 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        
        <!-- Filters grid -->
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 flex-1">
          <!-- Standort -->
          <div>
            <label class="block text-[10px] font-bold text-gray-400 dark:text-gray-500 uppercase tracking-wider mb-1 font-sans">Standort</label>
            <select 
              v-model="filters.locationId" 
              class="w-full px-2.5 py-1.5 bg-gray-50 dark:bg-dark-bg border border-gray-200 dark:border-gray-800 rounded-xl text-xs font-semibold text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-1 focus:ring-primary cursor-pointer"
            >
              <option value="">Alle Standorte</option>
              <option v-for="loc in locations" :key="loc.id" :value="loc.id">
                {{ loc.name }}
              </option>
            </select>
          </div>

          <!-- Aktiv/Inaktiv -->
          <div>
            <label class="block text-[10px] font-bold text-gray-400 dark:text-gray-500 uppercase tracking-wider mb-1 font-sans">Status</label>
            <select 
              v-model="filters.status" 
              class="w-full px-2.5 py-1.5 bg-gray-50 dark:bg-dark-bg border border-gray-200 dark:border-gray-800 rounded-xl text-xs font-semibold text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-1 focus:ring-primary cursor-pointer"
            >
              <option value="ALL">Alle Völker</option>
              <option value="ACTIVE">Nur aktive</option>
              <option value="INACTIVE">Nur inaktive</option>
            </select>
          </div>

          <!-- Aufgaben -->
          <div>
            <label class="block text-[10px] font-bold text-gray-400 dark:text-gray-500 uppercase tracking-wider mb-1 font-sans">Aufgaben</label>
            <select 
              v-model="filters.tasks" 
              class="w-full px-2.5 py-1.5 bg-gray-50 dark:bg-dark-bg border border-gray-200 dark:border-gray-800 rounded-xl text-xs font-semibold text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-1 focus:ring-primary cursor-pointer"
            >
              <option value="ALL">Alle</option>
              <option value="WITH">Mit Aufgaben</option>
              <option value="WITHOUT">Ohne Aufgaben</option>
            </select>
          </div>

          <!-- Königinjahr -->
          <div>
            <label class="block text-[10px] font-bold text-gray-400 dark:text-gray-500 uppercase tracking-wider mb-1 font-sans">Königinjahr</label>
            <select 
              v-model="filters.queenYear" 
              class="w-full px-2.5 py-1.5 bg-gray-50 dark:bg-dark-bg border border-gray-200 dark:border-gray-800 rounded-xl text-xs font-semibold text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-1 focus:ring-primary cursor-pointer"
            >
              <option value="">Alle Jahre</option>
              <option v-for="year in availableQueenYears" :key="year" :value="year">
                👑 {{ year }}
              </option>
            </select>
          </div>
        </div>

        <!-- View Switcher & Reset -->
        <div class="flex items-center space-x-2 shrink-0 md:pl-4 md:border-l border-gray-100 dark:border-dark-border">
          <div class="bg-gray-100 dark:bg-dark-bg p-1 rounded-xl flex items-center space-x-1">
            <button 
              type="button"
              @click="viewMode = 'tiles'" 
              class="px-3 py-1.5 rounded-lg text-xs font-extrabold transition-all cursor-pointer flex items-center gap-1"
              :class="viewMode === 'tiles' 
                ? 'bg-white dark:bg-dark-card text-primary shadow-sm' 
                : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200'"
            >
              🗂️ Kacheln
            </button>
            <button 
              type="button"
              @click="viewMode = 'list'" 
              class="px-3 py-1.5 rounded-lg text-xs font-extrabold transition-all cursor-pointer flex items-center gap-1"
              :class="viewMode === 'list' 
                ? 'bg-white dark:bg-dark-card text-primary shadow-sm' 
                : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200'"
            >
              📊 Liste
            </button>
          </div>

          <button 
            type="button"
            @click="resetFilters" 
            class="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 cursor-pointer"
            title="Filter zurücksetzen"
          >
            🧹
          </button>
        </div>

      </div>

      <div v-if="loading" class="flex flex-col items-center justify-center py-20 bg-white dark:bg-dark-card rounded-3xl border border-gray-200 dark:border-dark-border">
        <svg class="animate-spin h-10 w-10 text-primary mb-4" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
        <p class="text-gray-500 dark:text-gray-400 font-bold">Lade Bienenvölker...</p>
      </div>

      <template v-else>
        <!-- No results matching filters -->
        <div v-if="filteredHives.length === 0" class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-8 text-center text-gray-400 dark:text-gray-500 italic text-sm">
          Keine Bienenvölker entsprechen den ausgewählten Filtern.
        </div>

        <!-- TILES VIEW -->
        <template v-else-if="viewMode === 'tiles'">
          <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            <div 
              v-for="hive in filteredHives" 
              :key="hive.id"
              @click="openEditModal(hive)"
              class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-5 shadow-sm hover:shadow-md hover:border-primary/50 transition-all duration-200 cursor-pointer flex flex-col justify-between"
            >
              <!-- Card Header/Image -->
              <div class="relative w-full aspect-video rounded-2xl bg-amber-500/10 border border-amber-500/20 mb-4 overflow-hidden flex items-center justify-center">
                <img 
                  v-if="hive.image_path" 
                  :src="`/uploads/${hive.image_path}`" 
                  alt="Hive picture" 
                  class="w-full h-full object-cover"
                />
                <span v-else class="text-6xl animate-pulse">🐝</span>
                
                <!-- Queen marking color badge (overlay at top right) -->
                <div v-if="hive.queen_year" class="absolute top-2.5 right-2.5 flex items-center space-x-1 bg-white/95 dark:bg-dark-card/95 border border-gray-100 dark:border-dark-border px-2 py-1 rounded-xl shadow-sm">
                  <div 
                    class="w-2.5 h-2.5 rounded-full border border-gray-400 shadow-sm shrink-0" 
                    :style="{ backgroundColor: getQueenColor(hive.queen_year) }"
                  ></div>
                  <span class="text-[10px] font-black text-gray-700 dark:text-gray-300">👑 '{{ hive.queen_year.toString().slice(-2) }}</span>
                </div>

                <!-- Active/Inactive Status overlay (at top left) -->
                <span 
                  class="absolute top-2.5 left-2.5 px-2 py-0.5 text-[10px] font-black rounded-full tracking-wider uppercase shadow-sm"
                  :class="hive.is_active ? 'bg-green-500 text-white' : 'bg-gray-500 text-white'"
                >
                  {{ hive.is_active ? 'Aktiv' : 'Inaktiv' }}
                </span>
              </div>

              <!-- Hive Info -->
              <div class="mb-4">
                <h3 class="font-extrabold text-lg text-gray-900 dark:text-white truncate">{{ hive.name }}</h3>
                
                <p class="text-xs text-gray-500 dark:text-gray-400 mt-1 flex items-center space-x-1">
                  <span>📍 Standort:</span>
                  <span class="font-bold text-gray-700 dark:text-gray-300 truncate">
                    {{ hive.location?.name || 'Kein Standort' }}
                  </span>
                </p>
                
                <div class="flex items-center justify-between mt-2">
                  <span class="text-[10px] text-gray-400 font-bold uppercase tracking-wider">
                    {{ hive.frame_type?.name }}
                  </span>
                  <span class="px-2 py-0.5 bg-primary/15 text-primary text-[10px] font-extrabold rounded-full">
                    {{ hive.boxes?.length || 0 }} Zargen
                  </span>
                </div>
              </div>

              <!-- Tasks Section -->
              <div v-if="getTasksForHive(hive.id).length > 0" class="mt-auto pt-3 border-t border-gray-100 dark:border-dark-border/60 w-full" @click.stop>
                <div class="flex items-center justify-between mb-2">
                  <span class="text-[10px] font-bold text-gray-400 dark:text-gray-500 uppercase tracking-wider">
                    📋 Aufgaben ({{ getTasksForHive(hive.id).filter(t => !t.is_completed).length }} offen)
                  </span>
                  <div class="flex items-center space-x-1.5">
                    <router-link 
                      :to="{ name: 'tasks', query: { hiveId: hive.id } }" 
                      class="text-[10px] font-extrabold text-gray-500 hover:text-primary"
                    >
                      Anzeigen
                    </router-link>
                    <span class="text-gray-300 dark:text-gray-700">|</span>
                    <button 
                      type="button"
                      @click.stop="openCreateTaskModal(hive)"
                      class="text-[10px] font-extrabold text-primary hover:underline cursor-pointer"
                    >
                      + Erstellen
                    </button>
                  </div>
                </div>
                <ul class="space-y-1.5">
                  <li 
                    v-for="task in getTasksForHive(hive.id).slice(0, 2)" 
                    :key="task.id"
                    class="text-[11px] flex items-center justify-between bg-gray-50/50 dark:bg-dark-bg/30 px-2 py-1 rounded-lg border border-gray-100 dark:border-dark-border/40"
                  >
                    <div class="flex items-center gap-1 min-w-0">
                      <span :class="task.is_completed ? 'text-green-500' : 'text-amber-500'">
                        {{ task.is_completed ? '✓' : '●' }}
                      </span>
                      <span class="font-semibold text-gray-700 dark:text-gray-300 truncate" :class="{'line-through opacity-50': task.is_completed}">
                        {{ task.title }}
                      </span>
                    </div>
                  </li>
                  <li v-if="getTasksForHive(hive.id).length > 2" class="text-[9px] text-gray-400 italic pl-1">
                    ... und {{ getTasksForHive(hive.id).length - 2 }} weitere.
                  </li>
                </ul>
              </div>
              <div v-else class="mt-auto pt-3 border-t border-gray-100 dark:border-dark-border/60 flex items-center justify-between w-full" @click.stop>
                <span class="text-[10px] text-gray-400 italic">Keine Aufgaben</span>
                <button 
                  type="button"
                  @click.stop="openCreateTaskModal(hive)"
                  class="text-[10px] font-extrabold text-primary hover:underline cursor-pointer"
                >
                  + Erstellen
                </button>
              </div>

            </div>
          </div>
        </template>

        <!-- LIST VIEW -->
        <template v-else-if="viewMode === 'list'">
          <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl overflow-hidden shadow-sm">
            <div class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-100 dark:divide-dark-border">
                <thead class="bg-gray-50 dark:bg-dark-bg/50">
                  <tr>
                    <th scope="col" class="px-6 py-3.5 text-left text-xs font-bold text-gray-450 dark:text-gray-450 uppercase tracking-wider">Volk</th>
                    <th scope="col" class="px-6 py-3.5 text-left text-xs font-bold text-gray-450 dark:text-gray-450 uppercase tracking-wider">Standort</th>
                    <th scope="col" class="px-6 py-3.5 text-left text-xs font-bold text-gray-450 dark:text-gray-450 uppercase tracking-wider">Königin</th>
                    <th scope="col" class="px-6 py-3.5 text-left text-xs font-bold text-gray-450 dark:text-gray-450 uppercase tracking-wider">Zargen</th>
                    <th scope="col" class="px-6 py-3.5 text-left text-xs font-bold text-gray-450 dark:text-gray-450 uppercase tracking-wider">Aufgaben</th>
                  </tr>
                </thead>
                <tbody class="bg-white dark:bg-dark-card divide-y divide-gray-100 dark:divide-dark-border">
                  <tr 
                    v-for="hive in filteredHives" 
                    :key="hive.id"
                    @click="openEditModal(hive)"
                    class="hover:bg-gray-50/80 dark:hover:bg-dark-bg/25 transition-colors cursor-pointer"
                  >
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="flex items-center">
                        <div class="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/20 mr-3 overflow-hidden flex items-center justify-center">
                          <img 
                            v-if="hive.image_path" 
                            :src="`/uploads/${hive.image_path}`" 
                            alt="Hive thumbnail" 
                            class="w-full h-full object-cover"
                          />
                          <span v-else class="text-xl">🐝</span>
                        </div>
                        <div>
                          <div class="flex items-center gap-1.5">
                            <span class="text-sm font-black text-gray-900 dark:text-white">{{ hive.name }}</span>
                            <span 
                              class="px-1.5 py-0.2 text-[8px] font-black rounded-full uppercase"
                              :class="hive.is_active ? 'bg-green-500/10 text-green-500' : 'bg-gray-500/10 text-gray-500'"
                            >
                              {{ hive.is_active ? 'A' : 'I' }}
                            </span>
                          </div>
                          <div class="text-[10px] text-gray-400 font-bold uppercase tracking-wider">{{ hive.frame_type?.name }}</div>
                        </div>
                      </div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700 dark:text-gray-300 font-bold">
                      {{ hive.location?.name || 'Kein Standort' }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div v-if="hive.queen_year" class="flex items-center space-x-1.5">
                        <div 
                          class="w-2.5 h-2.5 rounded-full border border-gray-400 shadow-sm shrink-0" 
                          :style="{ backgroundColor: getQueenColor(hive.queen_year) }"
                        ></div>
                        <span class="text-xs font-bold text-gray-600 dark:text-gray-400">👑 '{{ hive.queen_year.toString().slice(-2) }}</span>
                      </div>
                      <span v-else class="text-xs text-gray-400">—</span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-xs font-bold text-gray-600 dark:text-gray-400">
                      {{ hive.boxes?.length || 0 }} Zargen
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="flex items-center space-x-2" @click.stop>
                        <span 
                          class="px-2 py-0.5 text-[10px] font-black rounded-full"
                          :class="getTasksForHive(hive.id).filter(t => !t.is_completed).length > 0 
                            ? 'bg-amber-100 text-amber-700 dark:bg-amber-950/40 dark:text-amber-400' 
                            : 'bg-green-100 text-green-700 dark:bg-green-950/40 dark:text-green-400'"
                        >
                          {{ getTasksForHive(hive.id).filter(t => !t.is_completed).length }} offen
                        </span>
                        
                        <!-- Links -->
                        <div class="flex items-center space-x-1.5 ml-2">
                          <router-link 
                            :to="{ name: 'tasks', query: { hiveId: hive.id } }" 
                            class="text-xs font-extrabold text-gray-500 hover:text-primary hover:underline"
                          >
                            Anzeigen
                          </router-link>
                          <span class="text-gray-300 dark:text-gray-700">|</span>
                          <button 
                            type="button"
                            @click.stop="openCreateTaskModal(hive)"
                            class="text-xs font-extrabold text-primary hover:underline flex items-center gap-0.5 cursor-pointer"
                          >
                            + Erstellen
                          </button>
                        </div>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </template>
      </template>
    </div>

    <!-- CREATE TASK DIALOG MODAL -->
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
              📝 Neue Aufgabe erfassen
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

              <!-- Scope Info -->
              <div class="bg-primary/5 dark:bg-primary/10 px-4 py-3 rounded-2xl border border-primary/10 flex items-center justify-between">
                <div>
                  <span class="text-[10px] uppercase font-black text-primary tracking-wider">Verknüpft mit</span>
                  <div class="text-sm font-extrabold text-gray-800 dark:text-white">🐝 {{ taskForm.hiveName }}</div>
                </div>
                <div class="text-right">
                  <span class="text-[10px] uppercase font-black text-gray-400 tracking-wider">Standort</span>
                  <div class="text-xs font-bold text-gray-600 dark:text-gray-300">{{ taskForm.locationName }}</div>
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
                :disabled="submittingTask"
                class="px-5 py-2 bg-primary hover:bg-primary-hover text-white font-extrabold text-xs uppercase tracking-wider rounded-xl shadow-md cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {{ submittingTask ? 'Erstelle...' : 'Erstellen' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- HIVE EDIT/CREATE DIALOG MODAL -->
    <div v-if="showModal" class="fixed inset-0 z-50 overflow-y-auto font-sans" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <!-- Backdrop -->
        <div @click="closeModal" class="fixed inset-0 z-0 bg-black/50 dark:bg-black/75 backdrop-blur-sm transition-opacity animate-fade-in" aria-hidden="true"></div>

        <!-- Center modal contents -->
        <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>

        <!-- Modal Box -->
        <div class="relative z-10 inline-block align-bottom bg-white dark:bg-dark-card rounded-[2rem] text-left overflow-hidden shadow-2xl transform transition-all sm:my-8 sm:align-middle sm:max-w-5xl sm:w-full border border-gray-150/40 dark:border-dark-border animate-scale">
          <!-- Header -->
          <div class="px-8 py-5 border-b border-gray-100 dark:border-dark-border flex justify-between items-center bg-gray-50/50 dark:bg-dark-bg/25">
            <h3 class="text-xl font-extrabold text-gray-900 dark:text-white flex items-center gap-2" id="modal-title">
              {{ isEditMode ? '🐝 Volk-Einstellungen bearbeiten' : '🐝 Neues Bienenvolk anlegen' }}
            </h3>
            <button type="button" @click="closeModal" class="text-gray-400 hover:text-gray-650 dark:hover:text-gray-200 p-2 hover:bg-gray-100 dark:hover:bg-dark-bg rounded-full transition-all cursor-pointer">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
            </button>
          </div>

          <form @submit.prevent="submitForm">
            <!-- Modal Body (Two columns on desktop) -->
            <div class="p-8 grid grid-cols-1 lg:grid-cols-12 gap-8">
              
              <!-- Left Column: Metadata (Form) -->
              <div class="lg:col-span-5 space-y-4">
                <h4 class="text-xs font-bold text-gray-400 dark:text-gray-505 uppercase tracking-widest mb-2 border-b border-gray-100 dark:border-dark-border/40 pb-2">📋 Stammdaten</h4>
                
                <div>
                  <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1.5">Volksbezeichnung / Name *</label>
                  <input 
                    v-model="form.name" 
                    type="text" 
                    required
                    placeholder="z.B. Volk 14"
                    class="w-full px-4 py-3 border border-gray-305 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm font-semibold transition-all"
                  />
                </div>

                <div>
                  <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1.5">Standort (Stand) *</label>
                  <select 
                    v-model="form.locationId" 
                    required
                    class="w-full px-4 py-3 border border-gray-305 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm cursor-pointer font-semibold transition-all"
                  >
                    <option value="" disabled>Bitte Standort wählen...</option>
                    <option v-for="loc in locations" :key="loc.id" :value="loc.id">
                      {{ loc.name }}
                    </option>
                  </select>
                </div>

                <div>
                  <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1.5">Wabenmaß *</label>
                  <select 
                    v-model="form.frameTypeId" 
                    required
                    class="w-full px-4 py-3 border border-gray-350 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm cursor-pointer font-semibold transition-all"
                  >
                    <option value="" disabled>Bitte Wabenmaß wählen...</option>
                    <option v-for="ft in frameTypes" :key="ft.id" :value="ft.id">
                      {{ ft.name }}
                    </option>
                  </select>
                </div>

                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1.5">Königin Jahr</label>
                    <input 
                      v-model.number="form.queenYear" 
                      type="number" 
                      placeholder="z.B. 2026"
                      class="w-full px-4 py-3 border border-gray-305 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm font-semibold transition-all"
                    />
                  </div>
                  <div class="flex flex-col justify-end pb-3">
                    <label class="flex items-center space-x-2.5 cursor-pointer select-none">
                      <input 
                        v-model="form.isActive" 
                        type="checkbox"
                        class="rounded text-primary focus:ring-primary h-5 w-5 border-gray-300 dark:border-gray-700"
                      />
                      <span class="text-xs font-bold text-gray-700 dark:text-gray-300">Volk ist aktiv</span>
                    </label>
                  </div>
                </div>

                <div>
                  <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1.5">Notizen (Königinlinie etc.)</label>
                  <textarea 
                    v-model="form.notes" 
                    placeholder="Königin F1 Carnica, standbegattet, sanftmütig..."
                    rows="3"
                    class="w-full px-4 py-3 border border-gray-305 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm transition-all"
                  ></textarea>
                </div>
              </div>

              <!-- Right Column: Box Editor & Photo (Only in Edit Mode) -->
              <div class="lg:col-span-7 space-y-6">
                <h4 class="text-xs font-bold text-gray-400 dark:text-gray-505 uppercase tracking-widest mb-2 border-b border-gray-100 dark:border-dark-border/40 pb-2">📦 Struktur & Foto</h4>
                
                <template v-if="isEditMode">
                  <!-- Profile Photo Uploader -->
                  <div class="flex items-center space-x-5 p-4 bg-gray-50 dark:bg-dark-bg/60 border border-gray-150/40 dark:border-gray-800 rounded-2xl">
                    <div class="w-16 h-16 rounded-xl bg-amber-500/10 border border-amber-500/20 shrink-0 overflow-hidden flex items-center justify-center relative group">
                      <img 
                        v-if="selectedHive?.image_path" 
                        :src="`/uploads/${selectedHive.image_path}`" 
                        alt="Hive profile picture" 
                        class="w-full h-full object-cover"
                      />
                      <span v-else class="text-3xl">📸</span>
                    </div>
                    <div>
                      <p class="text-xs font-black text-gray-850 dark:text-gray-200">Bienenvolk Profilbild</p>
                      <p class="text-[10px] text-gray-400 mt-0.5">Zeigt ein individuelles Foto für dieses Volk in der Kachelübersicht an.</p>
                      <input 
                        type="file" 
                        ref="photoInput" 
                        @change="uploadPhoto" 
                        accept="image/*" 
                        class="hidden"
                      />
                      <button 
                        type="button"
                        @click="$refs.photoInput.click()" 
                        class="text-[11px] font-black text-primary hover:text-primary-hover hover:underline uppercase tracking-wider mt-1.5 cursor-pointer flex items-center gap-1"
                      >
                        <span>Bild hochladen</span> 📤
                      </button>
                    </div>
                  </div>

                  <!-- Zargen Editor Section -->
                  <div class="space-y-4">
                    <div class="grid grid-cols-1 md:grid-cols-12 gap-6 items-start">
                      
                      <!-- Visual stack representation -->
                      <div class="md:col-span-5 flex justify-center">
                        <BeehiveVisualizer 
                          :boxes="editedBoxes" 
                          :selectedBoxId="selectedBoxId" 
                          @select-box="onSelectBox" 
                          @update-boxes="onUpdateBoxes"
                        />
                      </div>

                      <!-- Box properties config panel -->
                      <div class="md:col-span-7 space-y-4">
                        <div v-if="!selectedBox" class="text-xs text-gray-400 dark:text-gray-500 italic p-6 bg-gray-50 dark:bg-dark-bg/60 rounded-2xl border border-gray-150/40 text-center">
                          Wähle eine Zarge im Stapel aus, um deren Werte (Brut/Honig, Wabenzahl) zu editieren oder sie zu löschen.
                        </div>
                        
                        <div v-else class="p-5 bg-gray-50 dark:bg-dark-bg/60 border border-gray-200 dark:border-gray-800 rounded-2xl space-y-4 animate-scale">
                          <div class="flex justify-between items-center pb-2.5 border-b border-gray-200 dark:border-gray-700">
                            <span class="text-xs font-black uppercase text-gray-600 dark:text-gray-450">Zarge #{{ selectedBox.order }}</span>
                            <span 
                              class="px-2.5 py-0.5 text-[10px] font-black rounded-full uppercase"
                              :class="selectedBox.box_type === 'BROOD' ? 'bg-amber-600/10 text-amber-500' : 'bg-yellow-500/10 text-yellow-550'"
                            >
                              {{ selectedBox.box_type === 'BROOD' ? 'Brutraum' : 'Honigraum' }}
                            </span>
                          </div>

                          <div>
                            <label class="block text-[10px] font-bold text-gray-400 dark:text-gray-500 uppercase tracking-wider mb-1">Kammertyp</label>
                            <select 
                              v-model="selectedBox.box_type"
                              class="w-full px-3 py-2 bg-white dark:bg-dark-card border border-gray-300 dark:border-gray-700 rounded-lg text-xs font-semibold cursor-pointer"
                            >
                              <option value="BROOD">Brutraum</option>
                              <option value="HONEY">Honigraum</option>
                            </select>
                          </div>

                          <div class="grid grid-cols-2 gap-3">
                            <div>
                              <label class="block text-[10px] font-bold text-gray-400 dark:text-gray-500 uppercase tracking-wider mb-1">Anzahl Waben</label>
                              <input 
                                v-model.number="selectedBox.frame_count"
                                type="number"
                                min="1"
                                max="24"
                                class="w-full px-3 py-2 bg-white dark:bg-dark-card border border-gray-300 dark:border-gray-700 rounded-lg text-xs font-semibold"
                              />
                            </div>

                            <div>
                              <label class="block text-[10px] font-bold text-gray-400 dark:text-gray-500 uppercase tracking-wider mb-1">Wabenmaß</label>
                              <select 
                                v-model="selectedBox.frame_type_id"
                                class="w-full px-3 py-2 bg-white dark:bg-dark-card border border-gray-300 dark:border-gray-700 rounded-lg text-xs font-semibold cursor-pointer"
                              >
                                <option v-for="ft in frameTypes" :key="ft.id" :value="ft.id">
                                  {{ ft.name }}
                                </option>
                              </select>
                            </div>
                          </div>

                          <!-- Delete button in config panel -->
                          <div class="pt-2 border-t border-gray-200 dark:border-gray-700">
                            <button 
                              type="button"
                              @click="deleteSelectedBox"
                              class="w-full py-2 bg-red-50 hover:bg-red-100 dark:bg-red-950/20 dark:hover:bg-red-900/30 text-red-600 dark:text-red-400 font-extrabold text-[11px] rounded-xl tracking-wider uppercase border border-red-200 dark:border-red-900/50 transition-colors flex items-center justify-center gap-1 cursor-pointer"
                            >
                              <span>Zarge entfernen</span> 🗑️
                            </button>
                          </div>

                        </div>

                        <!-- Add Chamber CTA -->
                        <button 
                          type="button"
                          @click="addChamber"
                          class="w-full py-3 bg-gray-100 hover:bg-gray-250 dark:bg-dark-border dark:hover:bg-gray-750 text-gray-800 dark:text-gray-205 font-extrabold text-xs rounded-xl tracking-wider uppercase border border-gray-200 dark:border-gray-700 transition-colors cursor-pointer flex items-center justify-center gap-1"
                        >
                          <span>+ Zarge hinzufügen</span>
                        </button>
                      </div>

                    </div>
                  </div>
                </template>

                <template v-else>
                  <!-- Helper / Hint for new hives -->
                  <div class="h-full flex flex-col items-center justify-center p-8 bg-gray-50 dark:bg-dark-bg/40 border border-dashed border-gray-300 dark:border-gray-800 rounded-3xl text-center min-h-[300px]">
                    <span class="text-5xl mb-4">📦</span>
                    <h5 class="text-sm font-bold text-gray-700 dark:text-white mb-2">Zargenstruktur & Foto-Upload</h5>
                    <p class="text-xs text-gray-450 dark:text-gray-500 max-w-sm">
                      Nachdem du das neue Bienenvolk erstellt hast, kannst du hier im Dialog das Zargensystem aufbauen und ein Bild hochladen.
                    </p>
                  </div>
                </template>
              </div>

            </div>

            <!-- Footer -->
            <div class="px-8 py-5 bg-gray-50 dark:bg-dark-bg/25 border-t border-gray-100 dark:border-dark-border flex justify-between items-center">
              <div>
                <button 
                  v-if="isEditMode"
                  type="button" 
                  @click="deleteHive(selectedHive); closeModal()" 
                  class="px-4 py-2 bg-red-50 hover:bg-red-105 dark:bg-red-950/20 text-red-600 dark:text-red-400 font-bold text-xs uppercase tracking-wider rounded-xl border border-red-200 dark:border-red-900/50 cursor-pointer transition-colors"
                >
                  Volk auflösen 🗑️
                </button>
              </div>
              <div class="flex space-x-2">
                <button 
                  type="button" 
                  @click="closeModal" 
                  class="px-5 py-2.5 text-xs font-bold text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 cursor-pointer"
                >
                  Abbrechen
                </button>
                <button 
                  type="submit" 
                  class="px-6 py-2.5 bg-primary hover:bg-primary-hover text-white font-extrabold text-xs uppercase tracking-wider rounded-xl shadow-md cursor-pointer transition-all hover-scale"
                >
                  {{ isEditMode ? 'Speichern' : 'Volk anlegen' }}
                </button>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, reactive, computed, watch } from 'vue'
import { useConfirmStore } from '../stores/confirm'
import { useApiaryStore } from '../stores/apiary'
import BeehiveVisualizer from '../components/BeehiveVisualizer.vue'
import axios from 'axios'

const apiaryStore = useApiaryStore()
const confirmStore = useConfirmStore()

const hives = ref([])
const locations = ref([])
const frameTypes = ref([])
const tasks = ref([])
const loading = ref(false)

const selectedHive = ref(null)
const selectedBoxId = ref(null)

const showModal = ref(false)
const isEditMode = ref(false)
const editingId = ref(null)

const alertMessage = ref('')
const alertClass = ref('')

// Temporary list of edited boxes during configuration
const editedBoxes = ref([])
const boxesChanged = ref(false)

const form = reactive({
  name: '',
  locationId: '',
  frameTypeId: '',
  queenYear: null,
  isActive: true,
  notes: ''
})

const selectedBox = computed(() => {
  return editedBoxes.value.find(b => b.id === selectedBoxId.value) || null
})

onMounted(async () => {
  if (apiaryStore.activeApiaryId) {
    await Promise.all([
      fetchHives(),
      fetchLocations(),
      fetchFrameTypes(),
      fetchTasks()
    ])
  }
})

watch(() => apiaryStore.activeApiaryId, async (newId) => {
  if (newId) {
    await Promise.all([
      fetchHives(),
      fetchLocations(),
      fetchFrameTypes(),
      fetchTasks()
    ])
  } else {
    hives.value = []
    locations.value = []
    frameTypes.value = []
    tasks.value = []
    selectedHive.value = null
  }
})

async function fetchTasks() {
  if (!apiaryStore.activeApiaryId) return
  try {
    const response = await axios.get('/api/tasks', {
      params: { apiary_id: apiaryStore.activeApiaryId }
    })
    tasks.value = response.data
  } catch (err) {
    console.error('Fetch tasks error:', err)
  }
}

function getTasksForHive(hiveId) {
  return tasks.value.filter(t => t.hive_id === hiveId)
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

async function fetchHives() {
  loading.value = true
  try {
    const response = await axios.get('/api/hives', {
      params: { apiary_id: apiaryStore.activeApiaryId }
    })
    hives.value = response.data
    
    // Auto-reselect if editing same hive
    if (selectedHive.value) {
      const refreshed = hives.value.find(h => h.id === selectedHive.value.id)
      if (refreshed) {
        selectHive(refreshed, boxesChanged.value)
      } else {
        selectedHive.value = null
      }
    }
  } catch (err) {
    console.error('Fetch hives error:', err)
    showAlert('Fehler beim Laden der Bienenvölker.', 'error')
  } finally {
    loading.value = false
  }
}

async function fetchLocations() {
  try {
    const response = await axios.get('/api/locations', {
      params: { apiary_id: apiaryStore.activeApiaryId }
    })
    locations.value = response.data
  } catch (err) {
    console.error('Fetch locations error:', err)
  }
}

async function fetchFrameTypes() {
  try {
    const response = await axios.get('/api/hives/frame-types')
    frameTypes.value = response.data
  } catch (err) {
    console.error('Fetch frame types error:', err)
  }
}

function selectHive(hive, preserveEditedBoxes = false) {
  selectedHive.value = hive
  if (!preserveEditedBoxes) {
    // Deep clone boxes to edit state
    editedBoxes.value = (hive.boxes || []).map(box => ({
      id: box.id,
      order: box.order,
      frame_count: box.frame_count,
      box_type: box.box_type,
      frame_type_id: box.frame_type_id,
      frame_type_name: box.frame_type?.name
    }))
    selectedBoxId.value = null
    boxesChanged.value = false
  }
}

function onSelectBox(id) {
  selectedBoxId.value = id
}

function onUpdateBoxes(newBoxes) {
  editedBoxes.value = newBoxes
  boxesChanged.value = true
}

async function deleteSelectedBox() {
  if (!selectedBox.value) return
  const confirmed = await confirmStore.ask({
    title: 'Zarge entfernen',
    message: 'Möchtest du diese Zarge wirklich aus der Beute entfernen?',
    type: 'danger',
    confirmText: 'Ja, entfernen'
  })
  if (!confirmed) return
  
  let remaining = editedBoxes.value.filter(b => b.id !== selectedBoxId.value)
  
  // Recalculate order indices (ensure continuous 1..N order)
  remaining = remaining
    .sort((a, b) => a.order - b.order)
    .map((b, index) => {
      b.order = index + 1
      return b
    })
    
  editedBoxes.value = remaining
  selectedBoxId.value = null
  boxesChanged.value = true
}

function addChamber() {
  const newOrder = editedBoxes.value.length + 1
  const baseFrameType = selectedHive.value?.frame_type_id || (frameTypes.value[0]?.id || '')
  
  const newBox = {
    id: `temp-${Date.now()}`,
    order: newOrder,
    frame_count: 10,
    box_type: 'HONEY',
    frame_type_id: baseFrameType,
    frame_type_name: frameTypes.value.find(f => f.id === baseFrameType)?.name
  }

  editedBoxes.value.push(newBox)
  selectedBoxId.value = newBox.id
  boxesChanged.value = true
}

async function saveChamberStructure() {
  try {
    const payload = editedBoxes.value.map(box => ({
      order: box.order,
      frame_type_id: box.frame_type_id,
      frame_count: box.frame_count,
      box_type: box.box_type
    }))

    await axios.post(`/api/hives/${selectedHive.value.id}/boxes`, payload)
    showAlert('Zargenstruktur erfolgreich gespeichert!', 'success')
    boxesChanged.value = false
    await fetchHives()
  } catch (err) {
    console.error('Save chamber structure failed:', err)
    showAlert(err.response?.data?.detail || 'Fehler beim Speichern der Zargen.', 'error')
  }
}

async function uploadPhoto(event) {
  const file = event.target.files[0]
  if (!file) return
  
  const formData = new FormData()
  formData.append('file', file)

  try {
    await axios.post(`/api/hives/${selectedHive.value.id}/photo`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    showAlert('Bilder-Upload erfolgreich!', 'success')
    await fetchHives()
  } catch (err) {
    console.error('Upload photo failed:', err)
    showAlert(err.response?.data?.detail || 'Fehler beim Hochladen des Bildes.', 'error')
  }
}

function openCreateModal() {
  isEditMode.value = false
  editingId.value = null
  form.name = ''
  form.locationId = locations.value[0]?.id || ''
  form.frameTypeId = frameTypes.value[0]?.id || ''
  form.queenYear = new Date().getFullYear()
  form.isActive = true
  form.notes = ''
  
  selectedHive.value = null
  editedBoxes.value = []
  selectedBoxId.value = null
  boxesChanged.value = false
  
  showModal.value = true
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function openEditModal(hive) {
  isEditMode.value = true
  editingId.value = hive.id
  form.name = hive.name
  form.locationId = hive.location_id
  form.frameTypeId = hive.frame_type_id
  form.queenYear = hive.queen_year
  form.isActive = hive.is_active
  form.notes = hive.notes || ''
  
  selectHive(hive)
  
  showModal.value = true
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function closeModal() {
  showModal.value = false
}

async function submitForm() {
  if (!form.name.trim() || !form.locationId || !form.frameTypeId) return
  try {
    const payload = {
      name: form.name.trim(),
      location_id: form.locationId,
      frame_type_id: form.frameTypeId,
      queen_year: form.queenYear ? parseInt(form.queenYear) : null,
      is_active: form.isActive,
      notes: form.notes.trim() || null
    }

    if (isEditMode.value) {
      await axios.put(`/api/hives/${editingId.value}`, payload)
      if (boxesChanged.value) {
        const boxesPayload = editedBoxes.value.map(box => ({
          order: box.order,
          frame_type_id: box.frame_type_id,
          frame_count: box.frame_count,
          box_type: box.box_type
        }))
        await axios.post(`/api/hives/${editingId.value}/boxes`, boxesPayload)
        boxesChanged.value = false
      }
      showAlert('Volk erfolgreich aktualisiert!', 'success')
    } else {
      await axios.post('/api/hives', payload, {
        params: { apiary_id: apiaryStore.activeApiaryId }
      })
      showAlert('Volk erfolgreich angelegt!', 'success')
    }
    
    showModal.value = false
    await fetchHives()
  } catch (err) {
    console.error('Submit hive error:', err)
    showAlert(err.response?.data?.detail || 'Fehler beim Speichern des Volks.', 'error')
  }
}

async function deleteHive(hive) {
  const confirmed = await confirmStore.ask({
    title: 'Volk auflösen/löschen',
    message: `Möchtest du das Volk "${hive.name}" wirklich auflösen/löschen? Dadurch werden alle Zargen und dazugehörigen Logbucheinträge gelöscht.`,
    type: 'danger',
    confirmText: 'Ja, auflösen'
  })
  if (!confirmed) return
  try {
    await axios.delete(`/api/hives/${hive.id}`)
    showAlert('Volk erfolgreich gelöscht.', 'success')
    selectedHive.value = null
    await fetchHives()
  } catch (err) {
    console.error('Delete hive error:', err)
    showAlert(err.response?.data?.detail || 'Fehler beim Löschen des Volks.', 'error')
  }
}

// Helpers
function getQueenColor(year) {
  if (!year) {
    return '#F59E0B' // Default Gold
  }
  // Biological Queen Paint Code:
  // Years ending in:
  // 1 or 6: White
  // 2 or 7: Yellow
  // 3 or 8: Red
  // 4 or 9: Green
  // 5 or 0: Blue
  const endDigit = parseInt(year.toString().slice(-1))
  switch (endDigit) {
    case 1:
    case 6:
      return '#FFFFFF' // White
    case 2:
    case 7:
      return '#FBBF24' // Yellow
    case 3:
    case 8:
      return '#EF4444' // Red
    case 4:
    case 9:
      return '#10B981' // Green
    case 5:
    case 0:
      return '#3B82F6' // Blue
    default:
      return '#F59E0B' // Default Gold
  }
}

function showAlert(message, type = 'success') {
  alertMessage.value = message
  alertClass.value = type === 'success' 
    ? 'bg-green-500/10 border border-green-500/20 text-green-600 dark:text-green-400' 
    : 'bg-red-500/10 border border-red-500/20 text-red-600 dark:text-red-400'
  
  setTimeout(() => {
    alertMessage.value = ''
  }, 5000)
}

// Load filters and viewMode from sessionStorage if present
const savedViewMode = sessionStorage.getItem('beeboard_hives_view_mode')
const viewMode = ref(savedViewMode || 'tiles')

const savedFilters = sessionStorage.getItem('beeboard_hives_filters')
const filters = reactive(savedFilters ? JSON.parse(savedFilters) : {
  locationId: '',
  status: 'ALL', // 'ALL', 'ACTIVE', 'INACTIVE'
  tasks: 'ALL',  // 'ALL', 'WITH', 'WITHOUT'
  queenYear: ''
})

watch(viewMode, (newVal) => {
  sessionStorage.setItem('beeboard_hives_view_mode', newVal)
})

watch(filters, (newVal) => {
  sessionStorage.setItem('beeboard_hives_filters', JSON.stringify(newVal))
}, { deep: true })

// Available Queen Years for filtering
const availableQueenYears = computed(() => {
  const years = hives.value
    .map(h => h.queen_year)
    .filter(y => y !== null && y !== undefined)
  return [...new Set(years)].sort((a, b) => b - a)
})

// Filtered Hives computed property
const filteredHives = computed(() => {
  return hives.value.filter(hive => {
    // 1. Location
    if (filters.locationId && hive.location_id !== filters.locationId) {
      return false
    }
    // 2. Active status
    if (filters.status === 'ACTIVE' && !hive.is_active) {
      return false
    }
    if (filters.status === 'INACTIVE' && hive.is_active) {
      return false
    }
    // 3. Queen Year
    if (filters.queenYear && hive.queen_year !== parseInt(filters.queenYear)) {
      return false
    }
    // 4. Task existence
    if (filters.tasks !== 'ALL') {
      const hiveTasks = getTasksForHive(hive.id).filter(t => !t.is_completed)
      const hasOpenTasks = hiveTasks.length > 0
      if (filters.tasks === 'WITH' && !hasOpenTasks) {
        return false
      }
      if (filters.tasks === 'WITHOUT' && hasOpenTasks) {
        return false
      }
    }
    return true
  })
})

function resetFilters() {
  filters.locationId = ''
  filters.status = 'ALL'
  filters.tasks = 'ALL'
  filters.queenYear = ''
}

// In-context task creation modal state & submission
const showTaskModal = ref(false)
const submittingTask = ref(false)
const taskForm = reactive({
  title: '',
  description: '',
  priority: 'MEDIUM',
  dueDate: '',
  isRecurring: false,
  recurrenceInterval: 'WEEKLY',
  hiveId: null,
  hiveName: '',
  locationId: null,
  locationName: ''
})

function openCreateTaskModal(hive) {
  taskForm.title = ''
  taskForm.description = ''
  taskForm.priority = 'MEDIUM'
  
  // Default due date to today in YYYY-MM-DD
  const today = new Date()
  const year = today.getFullYear()
  const month = String(today.getMonth() + 1).padStart(2, '0')
  const day = String(today.getDate()).padStart(2, '0')
  taskForm.dueDate = `${year}-${month}-${day}`
  
  taskForm.isRecurring = false
  taskForm.recurrenceInterval = 'WEEKLY'
  taskForm.hiveId = hive.id
  taskForm.hiveName = hive.name
  taskForm.locationId = hive.location_id
  taskForm.locationName = hive.location?.name || 'Kein Standort'
  
  showTaskModal.value = true
}

async function submitTaskForm() {
  if (!taskForm.title.trim()) return
  submittingTask.value = true
  try {
    const payload = {
      title: taskForm.title.trim(),
      description: taskForm.description.trim() || null,
      priority: taskForm.priority,
      due_date: taskForm.dueDate || null,
      is_recurring: taskForm.isRecurring,
      recurrence_interval: taskForm.isRecurring ? taskForm.recurrenceInterval : null,
      hive_id: taskForm.hiveId,
      location_id: taskForm.locationId,
      is_completed: false
    }
    await axios.post('/api/tasks', payload)
    showAlert('Aufgabe erfolgreich angelegt!', 'success')
    showTaskModal.value = false
    await fetchTasks()
  } catch (err) {
    console.error('Submit task failed:', err)
    showAlert(err.response?.data?.detail || 'Fehler beim Erstellen der Aufgabe.', 'error')
  } finally {
    submittingTask.value = false
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
