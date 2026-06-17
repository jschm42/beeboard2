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
        <h1 class="text-3xl font-extrabold text-gray-900 dark:text-white tracking-tight">
          {{ viewMode === 'calendar' ? $t('tasks.title_calendar') : $t('tasks.title_tasks') }}
        </h1>
        <p class="text-gray-500 dark:text-gray-400 mt-1">
          {{ viewMode === 'calendar' 
            ? $t('tasks.subtitle_calendar') 
            : $t('tasks.subtitle_tasks') }}
        </p>
      </div>
      <button 
        @click="openCreateTaskModal" 
        class="px-5 py-2.5 bg-primary hover:bg-primary-hover text-white font-extrabold text-sm rounded-xl shadow-md shadow-primary/20 hover-scale flex items-center justify-center space-x-2 animate-fade-in"
      >
        <span>{{ $t('tasks.new_task') }}</span>
      </button>
    </div>

    <!-- Active Apiary check -->
    <div v-if="!apiaryStore.activeApiaryId" class="glass rounded-3xl p-12 text-center max-w-lg mx-auto border border-dashed border-gray-300 dark:border-gray-700">
      <div class="text-4xl mb-4">📋</div>
      <h3 class="text-lg font-bold text-gray-800 dark:text-white mb-2">{{ $t('logbook.no_active_apiary') }}</h3>
      <p class="text-gray-500 dark:text-gray-400">{{ $t('tasks.select_apiary_desc') }}</p>
    </div>

    <div v-else class="space-y-6 animate-scale">

      <!-- Quick Filter Bar -->
      <div class="flex flex-wrap items-center gap-2">
        <span class="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider shrink-0">{{ $t('tasks.quick_filters_label') }}</span>
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
            <span>🔍 {{ $t('tasks.filter_options') }}</span>
          </h3>
          <button 
            @click="resetFilters" 
            class="text-xs text-primary hover:underline font-bold"
          >
            {{ $t('hives.reset_filters') }}
          </button>
        </div>
        
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          <!-- Status -->
          <div>
            <label class="block text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">{{ $t('common.status') }}</label>
            <select 
              v-model="filters.status" 
              class="w-full px-3 py-2 border border-gray-200 dark:border-gray-800 dark:bg-dark-bg dark:text-white rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-primary cursor-pointer font-semibold"
            >
              <option value="ALL">{{ $t('tasks.filter_status_all') }}</option>
              <option value="PENDING">{{ $t('tasks.filter_status_pending') }}</option>
              <option value="OVERDUE">{{ $t('tasks.filter_status_overdue') }}</option>
              <option value="COMPLETED">{{ $t('tasks.filter_status_completed') }}</option>
            </select>
          </div>
          
          <!-- Standort -->
          <div>
            <label class="block text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">{{ $t('hives.location_label') }}</label>
            <select 
              v-model="filters.locationId" 
              class="w-full px-3 py-2 border border-gray-200 dark:border-gray-800 dark:bg-dark-bg dark:text-white rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-primary cursor-pointer font-semibold"
            >
              <option value="">{{ $t('hives.all_locations') }}</option>
              <option v-for="loc in locations" :key="loc.id" :value="loc.id">
                {{ loc.name }}
              </option>
            </select>
          </div>
          
          <!-- Volk -->
          <div>
            <label class="block text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">{{ $t('hives.table_hive') }}</label>
            <select 
              v-model="filters.hiveId" 
              class="w-full px-3 py-2 border border-gray-200 dark:border-gray-800 dark:bg-dark-bg dark:text-white rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-primary cursor-pointer font-semibold"
            >
              <option value="">{{ $t('hives.all_hives') }}</option>
              <option v-for="h in filteredHivesForFilter" :key="h.id" :value="h.id">
                {{ h.name }}
              </option>
            </select>
          </div>
          
          <!-- Priorität -->
          <div>
            <label class="block text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">{{ $t('hives.filter_tasks') }}</label>
            <select 
              v-model="filters.priority" 
              class="w-full px-3 py-2 border border-gray-200 dark:border-gray-800 dark:bg-dark-bg dark:text-white rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-primary cursor-pointer font-semibold"
            >
              <option value="">{{ $t('tasks.all_priorities') }}</option>
              <option value="HIGH">{{ $t('tasks.priority_high_emoji') }}</option>
              <option value="MEDIUM">{{ $t('tasks.priority_medium_emoji') }}</option>
              <option value="LOW">{{ $t('tasks.priority_low_emoji') }}</option>
            </select>
          </div>

          <!-- Von Datum -->
          <div>
            <label class="block text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">{{ $t('tasks.filter_due_from') }}</label>
            <input 
              v-model="filters.startDate" 
              type="date" 
              class="w-full px-3 py-2 border border-gray-200 dark:border-gray-800 dark:bg-dark-bg dark:text-white rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
          
          <!-- Bis Datum -->
          <div>
            <label class="block text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">{{ $t('tasks.filter_due_to') }}</label>
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
          <span class="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider">{{ $t('tasks.view_label') }}</span>
          <div class="inline-flex rounded-xl p-0.5 bg-gray-100 dark:bg-dark-bg border border-gray-200 dark:border-dark-border">
            <button 
              @click="viewMode = 'tiles'" 
              class="px-4 py-1.5 rounded-lg text-xs font-extrabold tracking-wide transition-all"
              :class="viewMode === 'tiles' ? 'bg-white dark:bg-dark-card text-primary shadow-sm' : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'"
            >
              {{ $t('tasks.view_tiles') }}
            </button>
            <button 
              @click="viewMode = 'list'" 
              class="px-4 py-1.5 rounded-lg text-xs font-extrabold tracking-wide transition-all"
              :class="viewMode === 'list' ? 'bg-white dark:bg-dark-card text-primary shadow-sm' : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'"
            >
              {{ $t('tasks.view_list') }}
            </button>
            <button 
              @click="viewMode = 'calendar'" 
              class="px-4 py-1.5 rounded-lg text-xs font-extrabold tracking-wide transition-all"
              :class="viewMode === 'calendar' ? 'bg-white dark:bg-dark-card text-primary shadow-sm' : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'"
            >
              {{ $t('tasks.view_calendar') }}
            </button>
          </div>
        </div>
        
        <div class="text-xs font-bold text-gray-500 dark:text-gray-400">
          {{ $t('tasks.found_count', { count: filteredTasks.length }) }}
        </div>
      </div>

      <!-- Loading Spinner -->
      <div v-if="loading" class="flex justify-center py-20 bg-white dark:bg-dark-card rounded-3xl border border-gray-200 dark:border-dark-border shadow-sm">
        <svg class="animate-spin h-8 w-8 text-primary" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
      </div>

      <!-- No Tasks Found -->
      <div v-else-if="viewMode !== 'calendar' && filteredTasks.length === 0" class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-12 text-center text-gray-400 italic text-sm">
        {{ $t('tasks.no_tasks_found') }}
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
            {{ $t('tasks.completed_badge') }}
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
                  :title="$t('tasks.recurring_tooltip')"
                >
                  🔄 {{ getRecurrenceIntervalText(task.recurrence_interval) }}
                </span>
              </div>

              <!-- Delete/Edit Actions -->
              <div class="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <button 
                  @click="openEditTaskModal(task)"
                  class="p-1 text-gray-400 hover:text-primary hover:bg-primary/10 rounded-lg transition-all"
                  :title="$t('tasks.edit_task_tooltip')"
                >
                  <svg class="w-4.5 h-4.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/></svg>
                </button>
                <button 
                  @click="deleteTask(task.id)"
                  class="p-1 text-gray-400 hover:text-red-500 hover:bg-red-500/10 rounded-lg transition-all"
                  :title="$t('tasks.delete_task_tooltip')"
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
                {{ $t('tasks.location_prefix', { name: task.location.name }) }}
              </span>
              <span v-if="task.hive" class="inline-flex items-center text-xs font-bold bg-amber-500/10 text-amber-700 dark:bg-amber-950/30 dark:text-primary px-2.5 py-1 rounded-lg">
                {{ $t('tasks.hive_prefix', { name: task.hive.name }) }}
              </span>
            </div>
          </div>

          <!-- Bottom Footer details and check off action -->
          <div class="mt-5 pt-3.5 border-t border-gray-100 dark:border-dark-border/60 flex items-center justify-between">
            <div class="text-xs font-mono">
              <span v-if="task.is_completed" class="text-green-500 dark:text-green-400 font-bold">
                {{ $t('tasks.completed_at', { date: formatDate(task.completed_at) }) }}
              </span>
              <span v-else :class="isOverdue(task.due_date) ? 'text-red-500 font-bold animate-pulse' : 'text-gray-400 dark:text-gray-500'">
                {{ formatDate(task.due_date) ? $t('tasks.due_prefix', { date: formatDate(task.due_date) }) : $t('tasks.no_date') }}
              </span>
            </div>
            
            <button 
              v-if="!task.is_completed"
              @click="completeTask(task.id)"
              class="px-3.5 py-1.5 bg-green-500 hover:bg-green-600 dark:bg-green-600 dark:hover:bg-green-700 text-white font-extrabold text-xs uppercase tracking-wider rounded-xl shadow transition-colors flex items-center gap-1 cursor-pointer"
            >
              <span>{{ $t('tasks.complete_btn') }}</span> ✓
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
                <th class="py-4 px-6 w-12 text-center">{{ $t('common.status') }}</th>
                <th class="py-4 px-4">{{ $t('tasks.table_title') }}</th>
                <th class="py-4 px-4 w-40">{{ $t('tasks.table_assigned') }}</th>
                <th class="py-4 px-4 w-28">{{ $t('tasks.table_due_date') }}</th>
                <th class="py-4 px-4 w-24">{{ $t('hives.filter_tasks') }}</th>
                <th class="py-4 px-4 w-24">{{ $t('tasks.table_interval') }}</th>
                <th class="py-4 px-6 w-20 text-right">{{ $t('common.actions') }}</th>
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
                  <span v-if="task.is_completed" class="text-green-500 font-bold">{{ $t('tasks.completed_badge') }}</span>
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
                      :title="$t('tasks.edit_task_tooltip')"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/></svg>
                    </button>
                    <button 
                      @click="deleteTask(task.id)"
                      class="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-500/10 rounded-lg transition-all"
                      :title="$t('tasks.delete_task_tooltip')"
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
        <div class="xl:col-span-2 bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-4 shadow-sm overflow-hidden">
          <VCalendar
            expanded
            borderless
            locale="de-DE"
            :attributes="calendarAttributes"
            @dayclick="onCalendarDayClick"
          >
            <template #day-content="{ day, attributes }">
              <div 
                class="flex flex-col flex-1 min-h-[75px] p-1.5 justify-between select-none transition-all duration-150 border-2"
                :class="[
                  toDateString(day.date) === selectedDateString 
                    ? 'border-primary bg-primary/5 dark:bg-primary/10 rounded-2xl' 
                    : 'border-transparent hover:bg-gray-50 dark:hover:bg-white/[0.04] rounded-2xl'
                ]"
              >
                <div class="flex justify-between items-center mb-1">
                  <span 
                    class="text-xs font-black w-6 h-6 flex items-center justify-center rounded-full"
                    :class="[
                      day.isToday 
                        ? 'bg-amber-500 text-white shadow-sm shadow-amber-500/30' 
                        : day.inMonth 
                          ? 'text-gray-900 dark:text-gray-100' 
                          : 'text-gray-400 dark:text-gray-500'
                    ]"
                  >
                    {{ day.day }}
                  </span>
                </div>
                
                <div class="flex-grow space-y-1 overflow-hidden mt-0.5">
                  <div 
                    v-for="attr in attributes.slice(0, 3)" 
                    :key="attr.key"
                    @click.stop="onCalendarItemClick(attr.customData)"
                    class="text-[9px] px-1.5 py-0.5 rounded-lg truncate font-extrabold tracking-wide border transition-all duration-150 shadow-sm cursor-pointer hover:brightness-95 hover:scale-[1.02] active:scale-[0.98]"
                    :class="getCalendarItemClasses(attr)"
                    :style="getCalendarItemStyle(attr)"
                    :title="attr.customData?.title"
                  >
                    {{ attr.customData?.title }}
                  </div>
                  <div v-if="attributes.length > 3" class="text-[8px] text-gray-400 dark:text-gray-500 font-bold text-center">
                    +{{ attributes.length - 3 }} {{ $t('common.more') }}
                  </div>
                </div>
              </div>
            </template>
          </VCalendar>
        </div>

        <div class="space-y-4">
          <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-5 shadow-sm">
            <h4 class="text-sm font-extrabold text-gray-900 dark:text-white mb-3">{{ $t('tasks.due_on_date', { date: formatDate(selectedDateString) }) }}</h4>

            <div v-if="!selectedDateTaskItems.length && !selectedDateCustomItems.length" class="text-xs text-gray-500 dark:text-gray-400 italic">
              {{ $t('tasks.no_events_on_day') }}
            </div>

            <div v-else class="space-y-2">
              <div
                v-for="item in selectedDateTaskItems"
                :key="`task-day-${item.id}`"
                class="p-2.5 rounded-xl border text-xs"
                :class="item.is_completed ? 'border-green-200 bg-green-50/70 dark:border-green-900/30 dark:bg-green-950/10' : 'border-gray-200 bg-gray-50 dark:border-dark-border dark:bg-dark-bg/60'"
              >
                <div class="font-bold text-gray-900 dark:text-white">{{ item.title }}</div>
                <div class="text-gray-500 dark:text-gray-400 mt-0.5">{{ $t('dashboard.task_kind') }}</div>
              </div>

              <div
                v-for="item in selectedDateCustomItems"
                :key="`custom-day-${item.id}`"
                class="p-2.5 rounded-xl border text-xs"
                :style="{ borderColor: item.color + '55' }"
              >
                <div class="font-bold text-gray-900 dark:text-white">{{ item.title }}</div>
                <div class="text-gray-500 dark:text-gray-400 mt-0.5">
                  {{ $t('dashboard.event_kind') }}: {{ formatDate(item.start_date) }}<span v-if="item.end_date !== item.start_date"> - {{ formatDate(item.end_date) }}</span>
                </div>
              </div>
            </div>
          </div>

          <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-5 shadow-sm">
            <div class="flex items-center justify-between mb-3">
              <h4 class="text-sm font-extrabold text-gray-900 dark:text-white">{{ $t('tasks.custom_event_header') }}</h4>
              <button
                v-if="customEventForm.id"
                @click="resetCustomEventForm"
                class="text-[11px] font-bold text-primary hover:underline"
              >
                {{ $t('tasks.new_custom_event_btn') }}
              </button>
            </div>

            <form class="space-y-3" @submit.prevent="saveCustomEvent">
              <input
                v-model="customEventForm.title"
                type="text"
                required
                :placeholder="$t('tasks.custom_event_placeholder')"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-primary"
              />

              <!-- Start/End dates -->
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

              <!-- Ganztägig & Wiederkehrend Toggles -->
              <div class="flex items-center space-x-4 py-1">
                <label class="flex items-center space-x-1 text-[10px] font-bold text-gray-600 dark:text-gray-400 uppercase tracking-wider cursor-pointer">
                  <input 
                    v-model="customEventForm.is_all_day" 
                    type="checkbox"
                    class="w-4 h-4 rounded border-gray-300 text-primary focus:ring-primary"
                  />
                  <span>{{ $t('tasks.all_day') }}</span>
                </label>

                <button 
                  type="button"
                  @click="customEventForm.is_recurring = !customEventForm.is_recurring"
                  class="flex items-center space-x-1 px-2.5 py-1 rounded-lg border text-[10px] font-bold uppercase transition-all"
                  :class="customEventForm.is_recurring
                    ? 'bg-primary/10 border-primary text-primary'
                    : 'bg-white dark:bg-dark-bg border-gray-200 dark:border-gray-700 text-gray-500'"
                >
                  <span>🔄 {{ $t('tasks.recurring_btn') }}</span>
                </button>
              </div>

              <!-- Start/End times if NOT Ganztägig -->
              <div v-if="!customEventForm.is_all_day" class="grid grid-cols-2 gap-2 animate-scale">
                <input 
                  v-model="customEventForm.start_time" 
                  type="time" 
                  class="w-full px-3 py-1.5 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-xs"
                />
                <input 
                  v-model="customEventForm.end_time" 
                  type="time" 
                  class="w-full px-3 py-1.5 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-xs"
                />
              </div>

              <!-- Custom Event Recurrence Panel -->
              <div v-if="customEventForm.is_recurring" class="p-3 bg-gray-50 dark:bg-dark-bg/40 rounded-xl border border-gray-200/60 dark:border-dark-border/60 space-y-2.5 text-xs animate-scale">
                <div class="flex flex-wrap items-center gap-2">
                  <span class="font-bold text-gray-500 uppercase tracking-wider">{{ $t('tasks.repeat_every') }}</span>
                  <select 
                    v-model.number="customEventForm.recurrence_interval_value"
                    class="px-1.5 py-1 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded focus:ring-1 focus:ring-primary font-bold text-center"
                  >
                    <option v-for="n in 30" :key="n" :value="n">{{ n }}</option>
                  </select>
                  <select 
                    v-model="customEventForm.recurrence_interval_type"
                    class="px-1.5 py-1 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded focus:ring-1 focus:ring-primary font-bold"
                  >
                    <option value="DAILY">{{ $t('tasks.day_unit') }}</option>
                    <option value="WEEKLY">{{ $t('tasks.week_unit') }}</option>
                    <option value="MONTHLY">{{ $t('tasks.month_unit') }}</option>
                    <option value="YEARLY">{{ $t('tasks.year_unit') }}</option>
                  </select>

                  <div class="flex items-center gap-1.5 shrink-0">
                    <span class="font-bold text-gray-500 uppercase tracking-wider">{{ $t('tasks.until') }}</span>
                    <input 
                      v-model="customEventForm.recurrence_end_date" 
                      type="date"
                      :title="$t('tasks.recurrence_end_date_tooltip')"
                      class="px-1.5 py-0.5 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded font-bold text-[11px]"
                    />
                  </div>
                </div>

                <!-- Weekday Selectors (Shown only when WEEKLY is selected) -->
                <div v-if="customEventForm.recurrence_interval_type === 'WEEKLY'" class="flex items-center gap-1 py-1">
                  <button
                    v-for="(day, index) in weekdaysList"
                    :key="index"
                    type="button"
                    @click="toggleCustomEventWeekday(index)"
                    class="w-7 h-7 rounded border text-[10px] font-black transition-all flex items-center justify-center cursor-pointer"
                    :class="customEventForm.recurrence_weekdays.includes(index)
                      ? 'bg-primary border-primary text-white'
                      : 'bg-white dark:bg-dark-bg border-gray-200 dark:border-gray-700 text-gray-500 hover:border-gray-300'"
                  >
                    {{ day.label }}
                  </button>
                </div>
              </div>

              <!-- Notes & Color -->
              <div class="grid grid-cols-[1fr_auto] gap-2 items-center">
                <input
                  v-model="customEventForm.notes"
                  type="text"
                  :placeholder="$t('tasks.custom_event_notes_placeholder')"
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
                class="w-full px-4 py-2 bg-primary hover:bg-primary-hover text-white text-xs font-extrabold uppercase tracking-wider rounded-xl shadow-sm"
              >
                {{ customEventForm.id ? $t('tasks.save_event_btn') : $t('tasks.create_event_btn') }}
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
                    <button @click="editCustomEvent(event)" class="text-[11px] text-primary font-bold hover:underline">{{ $t('common.edit') }}</button>
                    <button @click="removeCustomEvent(event.id)" class="text-[11px] text-red-500 font-bold hover:underline">{{ $t('common.delete') }}</button>
                  </div>
                </div>
              </div>

              <p v-if="customEvents.length === 0" class="text-xs text-gray-500 dark:text-gray-400 italic">
                {{ $t('tasks.no_custom_events_yet') }}
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
              {{ isEditMode ? $t('tasks.edit_modal_title') : $t('tasks.create_modal_title') }}
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
                <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('hives.task_label_title') }}</label>
                <input 
                  v-model="taskForm.title" 
                  type="text" 
                  required
                  :placeholder="$t('hives.task_title_placeholder')"
                  class="w-full px-3 py-2.5 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm font-semibold"
                />
              </div>

              <!-- Description -->
              <div>
                <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('hives.task_label_description') }}</label>
                <textarea 
                  v-model="taskForm.description" 
                  :placeholder="$t('hives.task_desc_placeholder')"
                  rows="2"
                  class="w-full px-3 py-2.5 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm"
                ></textarea>
              </div>

              <!-- Scope Section: Location / Hive -->
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('tasks.form_location') }}</label>
                  <select 
                    v-model="taskForm.locationId" 
                    @change="onLocationChange"
                    class="w-full px-3 py-2.5 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-xs cursor-pointer font-bold"
                  >
                    <option value="">{{ $t('tasks.form_global_location') }}</option>
                    <option v-for="loc in locations" :key="loc.id" :value="loc.id">
                      {{ loc.name }}
                    </option>
                  </select>
                </div>
                <div>
                  <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('tasks.form_hive') }}</label>
                  <select 
                    v-model="taskForm.hiveId" 
                    class="w-full px-3 py-2.5 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-xs cursor-pointer font-bold"
                  >
                    <option value="">{{ $t('tasks.form_global_hive') }}</option>
                    <option v-for="hive in filteredHivesForForm" :key="hive.id" :value="hive.id">
                      {{ hive.name }}
                    </option>
                  </select>
                </div>
              </div>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <!-- Priority -->
                <div>
                  <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('hives.task_priority') }}</label>
                  <select 
                    v-model="taskForm.priority" 
                    required
                    class="w-full px-3 py-2.5 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-xs cursor-pointer font-bold"
                  >
                    <option value="LOW">{{ $t('hives.priority_low') }}</option>
                    <option value="MEDIUM">{{ $t('hives.priority_medium') }}</option>
                    <option value="HIGH">{{ $t('hives.priority_high') }}</option>
                  </select>
                </div>

                <!-- Due Date -->
                <div>
                  <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('hives.task_due_date') }}</label>
                  <input 
                    v-model="taskForm.dueDate" 
                    type="date" 
                    class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 bg-white dark:bg-dark-bg text-gray-900 dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm font-semibold [color-scheme:light] dark:[color-scheme:dark]"
                  />
                </div>
              </div>

              <!-- Ganztägig & Wiederkehrend Toggles -->
              <div class="flex items-center space-x-6 py-1">
                <label class="flex items-center space-x-2 text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-0.5 cursor-pointer">
                  <input 
                    v-model="taskForm.isAllDay" 
                    type="checkbox"
                    class="w-4.5 h-4.5 rounded border-gray-300 text-primary focus:ring-primary"
                  />
                  <span class="ml-1.5">{{ $t('tasks.all_day') }}</span>
                </label>

                <button 
                  type="button"
                  @click="taskForm.isRecurring = !taskForm.isRecurring"
                  class="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl border text-xs font-extrabold tracking-wide transition-all cursor-pointer"
                  :class="taskForm.isRecurring
                    ? 'bg-primary/10 border-primary text-primary shadow-sm'
                    : 'bg-white dark:bg-dark-card border-gray-200 dark:border-dark-border text-gray-500 hover:border-gray-300 dark:hover:border-gray-700'"
                >
                  <span>🔄</span>
                  <span>{{ $t('tasks.recurring_btn') }}</span>
                </button>
              </div>

              <!-- Time Picker if NOT Ganztägig -->
              <div v-if="!taskForm.isAllDay" class="animate-scale">
                <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('tasks.due_time_label') }}</label>
                <input 
                  v-model="taskForm.dueTime" 
                  type="time" 
                  class="w-full px-3 py-2.5 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm font-semibold"
                />
              </div>

              <!-- Recurrence Settings Panel -->
              <div v-if="taskForm.isRecurring" class="p-4 bg-gray-50 dark:bg-dark-bg/40 rounded-2xl border border-gray-200/60 dark:border-dark-border/60 space-y-4 animate-scale">
                <div class="flex flex-wrap items-center gap-3 text-xs">
                  <span class="font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider">{{ $t('tasks.repeat_every') }}</span>
                  
                  <select 
                    v-model.number="taskForm.recurrenceIntervalValue"
                    class="px-2 py-1.5 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-primary font-bold text-center cursor-pointer"
                  >
                    <option v-for="n in 30" :key="n" :value="n">{{ n }}</option>
                  </select>
                  
                  <select 
                    v-model="taskForm.recurrenceIntervalType"
                    class="px-2 py-1.5 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-primary font-bold cursor-pointer"
                  >
                    <option value="DAILY">{{ $t('tasks.day_unit') }}</option>
                    <option value="WEEKLY">{{ $t('tasks.week_unit') }}</option>
                    <option value="MONTHLY">{{ $t('tasks.month_unit') }}</option>
                    <option value="YEARLY">{{ $t('tasks.year_unit') }}</option>
                  </select>

                  <div class="flex items-center gap-1.5 shrink-0 ml-auto sm:ml-0">
                    <span class="font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider">{{ $t('tasks.until') }}</span>
                    <input 
                      v-model="taskForm.recurrenceEndDate" 
                      type="date"
                      :title="$t('tasks.recurrence_end_date_tooltip')"
                      class="px-2 py-1 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-primary font-bold"
                    />
                  </div>

                  <button 
                    type="button"
                    @click="taskForm.isRecurring = false"
                    class="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-500/10 rounded-lg transition-all ml-auto cursor-pointer"
                    :title="$t('tasks.disable_recurrence')"
                  >
                    <svg class="w-4.5 h-4.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                  </button>
                </div>

                <!-- Weekday Selectors (Shown only when WEEKLY is selected) -->
                <div v-if="taskForm.recurrenceIntervalType === 'WEEKLY'" class="flex items-center gap-1.5 py-1 animate-scale">
                  <button
                    v-for="(day, index) in weekdaysList"
                    :key="index"
                    type="button"
                    @click="toggleFormWeekday(index)"
                    class="w-8 h-8 rounded-lg border text-xs font-black transition-all flex items-center justify-center cursor-pointer"
                    :class="taskForm.recurrenceWeekdays.includes(index)
                      ? 'bg-primary border-primary text-white shadow-sm'
                      : 'bg-white dark:bg-dark-bg border-gray-200 dark:border-gray-700 text-gray-500 hover:border-gray-300 dark:hover:border-gray-650'"
                  >
                    {{ day.label }}
                  </button>
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
                {{ $t('common.cancel') }}
              </button>
              <button 
                type="submit" 
                class="px-5 py-2 bg-primary hover:bg-primary-hover text-white font-extrabold text-xs uppercase tracking-wider rounded-xl shadow-md cursor-pointer"
              >
                {{ isEditMode ? $t('common.save') : $t('hives.create') }}
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
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { useApiaryStore } from '../stores/apiary'
import { useErrorStore } from '../stores/error'
import { useConfirmStore } from '../stores/confirm'
import { getCustomCalendarEvents, upsertCustomCalendarEvent, deleteCustomCalendarEvent, isDateInRange, getOccurrences } from '../utils/calendarEvents'

const weekdaysList = [
  { value: 0, label: 'M' },
  { value: 1, label: 'D' },
  { value: 2, label: 'M' },
  { value: 3, label: 'D' },
  { value: 4, label: 'F' },
  { value: 5, label: 'S' },
  { value: 6, label: 'S' }
]

function toggleFormWeekday(dayValue) {
  if (!taskForm.value.recurrenceWeekdays) {
    taskForm.value.recurrenceWeekdays = []
  }
  const idx = taskForm.value.recurrenceWeekdays.indexOf(dayValue)
  if (idx >= 0) {
    taskForm.value.recurrenceWeekdays.splice(idx, 1)
  } else {
    taskForm.value.recurrenceWeekdays.push(dayValue)
  }
}

function toggleCustomEventWeekday(dayValue) {
  if (!customEventForm.value.recurrence_weekdays) {
    customEventForm.value.recurrence_weekdays = []
  }
  const idx = customEventForm.value.recurrence_weekdays.indexOf(dayValue)
  if (idx >= 0) {
    customEventForm.value.recurrence_weekdays.splice(idx, 1)
  } else {
    customEventForm.value.recurrence_weekdays.push(dayValue)
  }
}

function getCalendarItemClasses(attr) {
  if (attr.customData?.type === 'task') {
    if (attr.customData.isDone) {
      return 'bg-green-100/50 text-green-700 border-green-200 dark:bg-green-950/20 dark:text-green-400 dark:border-green-900/20 border-l-4 border-l-green-500'
    } else if (attr.customData.overdue) {
      return 'bg-red-100 text-red-700 border-red-200 dark:bg-red-950/40 dark:text-red-400 dark:border-red-900/30 font-black animate-pulse border-l-4 border-l-red-500'
    } else {
      // Differentiate by priority for better visual recognition
      if (attr.customData.priority === 'HIGH') {
        return 'bg-red-50 text-red-800 border-red-200 dark:bg-red-950/30 dark:text-red-300 dark:border-red-900/40 border-l-4 border-l-red-500 font-bold'
      } else if (attr.customData.priority === 'MEDIUM') {
        return 'bg-amber-50 text-amber-800 border-amber-200 dark:bg-amber-950/30 dark:text-amber-300 dark:border-amber-900/40 border-l-4 border-l-amber-500 font-bold'
      } else {
        // LOW
        return 'bg-blue-50 text-blue-800 border-blue-200 dark:bg-blue-950/30 dark:text-blue-300 dark:border-blue-900/40 border-l-4 border-l-blue-400 font-semibold'
      }
    }
  }
  return ''
}

function getCalendarItemStyle(attr) {
  if (attr.customData?.type === 'event') {
    const color = attr.customData.color || '#2563eb'
    return {
      backgroundColor: `${color}15`,
      color: color,
      borderColor: `${color}40`,
      borderLeft: `4px solid ${color}`
    }
  }
  return {}
}
import axios from 'axios'

const { t, locale } = useI18n()
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
  color: '#2563eb',
  is_recurring: false,
  recurrence_interval_type: 'WEEKLY',
  recurrence_interval_value: 1,
  recurrence_weekdays: [],
  recurrence_end_date: '',
  is_all_day: true,
  start_time: '',
  end_time: ''
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
    label: t('tasks.qf_today'),
    icon: '📅',
    activeClass: 'bg-primary border-primary text-white shadow-md shadow-primary/20',
    count: tasks.value.filter(t => !t.is_completed && t.due_date === todayStr()).length
  },
  {
    key: 'OVERDUE',
    label: t('tasks.qf_overdue'),
    icon: '🔴',
    activeClass: 'bg-red-500 border-red-500 text-white shadow-md shadow-red-500/20',
    count: tasks.value.filter(t => !t.is_completed && t.due_date && t.due_date < todayStr()).length
  },
  {
    key: 'UPCOMING',
    label: t('tasks.qf_upcoming'),
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
  recurrenceIntervalType: 'WEEKLY',
  recurrenceIntervalValue: 1,
  recurrenceWeekdays: [],
  recurrenceEndDate: '',
  isAllDay: true,
  dueTime: ''
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
    errorStore.showError(t('tasks.error_fetch'), err, t('sidebar.tasks'))
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
  const attrs = []
  const today = todayStr()

  const startRange = todayOffsetStr(-90)
  const endRange = todayOffsetStr(365)

  // Expand Tasks
  filteredTasks.value.forEach(task => {
    if (!task.due_date) return

    if (task.is_completed) {
      attrs.push({
        key: `task-${task.id}`,
        dates: new Date(`${task.due_date}T12:00:00`),
        customData: {
          id: task.id,
          type: 'task',
          title: `✓ ${task.title}`,
          isDone: true,
          overdue: false,
          priority: task.priority
        }
      })
      return
    }

    const occurrences = getOccurrences(
      {
        due_date: task.due_date,
        is_recurring: task.is_recurring,
        recurrence_interval_type: task.recurrence_interval_type,
        recurrence_interval_value: task.recurrence_interval_value,
        recurrence_weekdays: task.recurrence_weekdays,
        recurrence_end_date: task.recurrence_end_date
      },
      startRange,
      endRange
    )

    occurrences.forEach((occDate, idx) => {
      const isOverdueTask = occDate < today
      attrs.push({
        key: `task-${task.id}-${occDate}`,
        dates: new Date(`${occDate}T12:00:00`),
        customData: {
          id: task.id,
          type: 'task',
          title: `${task.is_all_day ? '' : (task.due_time ? task.due_time + ' ' : '')}📋 ${task.title}`,
          isDone: false,
          overdue: isOverdueTask,
          priority: task.priority,
          isVirtual: idx > 0
        }
      })
    })
  })

  // Expand Custom Events
  customEvents.value.forEach(event => {
    if (!event.start_date) return

    const occurrences = getOccurrences(
      {
        start_date: event.start_date,
        is_recurring: event.is_recurring,
        recurrence_interval_type: event.recurrence_interval_type,
        recurrence_interval_value: event.recurrence_interval_value,
        recurrence_weekdays: event.recurrence_weekdays,
        recurrence_end_date: event.recurrence_end_date
      },
      startRange,
      endRange
    )

    occurrences.forEach(occDate => {
      attrs.push({
        key: `custom-${event.id}-${occDate}`,
        dates: new Date(`${occDate}T12:00:00`),
        customData: {
          id: event.id,
          type: 'event',
          title: `${event.is_all_day ? '' : (event.start_time ? event.start_time + ' ' : '')}📅 ${event.title}`,
          color: event.color
        }
      })
    })
  })

  return attrs
})

function todayOffsetStr(offsetDays) {
  const d = new Date()
  d.setDate(d.getDate() + offsetDays)
  return d.toISOString().split('T')[0]
}

const selectedDateTaskItems = computed(() => {
  return calendarAttributes.value
    .filter(attr => {
      if (attr.customData?.type !== 'task') return false
      const attrDateStr = toDateString(attr.dates)
      return attrDateStr === selectedDateString.value
    })
    .map(attr => ({
      id: attr.key,
      title: attr.customData.title,
      is_completed: attr.customData.isDone
    }))
})

const selectedDateCustomItems = computed(() => {
  return calendarAttributes.value
    .filter(attr => {
      if (attr.customData?.type !== 'event') return false
      const attrDateStr = toDateString(attr.dates)
      return attrDateStr === selectedDateString.value
    })
    .map(attr => ({
      id: attr.key,
      title: attr.customData.title,
      color: attr.customData.color,
      start_date: toDateString(attr.dates)
    }))
})

function onCalendarDayClick(dayInfo) {
  const dateValue = dayInfo?.id || dayInfo?.date || dayInfo
  selectedDateString.value = toDateString(dateValue)
}

function onCalendarItemClick(customData) {
  if (!customData || !customData.id) return
  if (customData.type === 'task') {
    const task = tasks.value.find(t => t.id === customData.id)
    if (task) {
      openEditTaskModal(task)
    }
  } else if (customData.type === 'event') {
    const event = customEvents.value.find(e => e.id === customData.id)
    if (event) {
      editCustomEvent(event)
    }
  }
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
    color: '#2563eb',
    is_recurring: false,
    recurrence_interval_type: 'WEEKLY',
    recurrence_interval_value: 1,
    recurrence_weekdays: [],
    recurrence_end_date: '',
    is_all_day: true,
    start_time: '',
    end_time: ''
  }
}

async function saveCustomEvent() {
  if (!apiaryStore.activeApiaryId) return
  try {
    const payload = {
      ...customEventForm.value,
      title: customEventForm.value.title.trim(),
      notes: customEventForm.value.notes.trim(),
      recurrence_weekdays: customEventForm.value.recurrence_weekdays.join(','),
      is_all_day: customEventForm.value.is_all_day,
      start_time: customEventForm.value.is_all_day ? '' : customEventForm.value.start_time,
      end_time: customEventForm.value.is_all_day ? '' : customEventForm.value.end_time
    }
    upsertCustomCalendarEvent(apiaryStore.activeApiaryId, payload)
    customEvents.value = getCustomCalendarEvents(apiaryStore.activeApiaryId)
    resetCustomEventForm()
  } catch (err) {
    errorStore.showError(t('tasks.error_save'), err, t('sidebar.calendar'))
  }
}

function editCustomEvent(event) {
  const weekdays = event.recurrence_weekdays
    ? event.recurrence_weekdays.split(',').map(d => parseInt(d)).filter(d => !isNaN(d))
    : []
  customEventForm.value = {
    ...event,
    is_recurring: !!event.is_recurring,
    recurrence_interval_type: event.recurrence_interval_type || 'WEEKLY',
    recurrence_interval_value: event.recurrence_interval_value || 1,
    recurrence_weekdays: weekdays,
    recurrence_end_date: event.recurrence_end_date || '',
    is_all_day: event.is_all_day !== false,
    start_time: event.start_time || '',
    end_time: event.end_time || ''
  }
}

async function removeCustomEvent(eventId) {
  const confirmed = await confirmStore.ask({
    title: t('tasks.confirm_delete_event_title'),
    message: t('tasks.confirm_delete_event_msg'),
    type: 'danger',
    confirmText: t('tasks.confirm_delete_btn')
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
    errorStore.showError(t('dashboard.error_complete_task'), err, t('tasks.complete_btn'))
  }
}

async function deleteTask(id) {
  const confirmed = await confirmStore.ask({
    title: t('tasks.delete_title'),
    message: t('tasks.confirm_delete_msg'),
    type: 'danger',
    confirmText: t('tasks.confirm_delete_btn')
  })
  if (!confirmed) return
  try {
    await axios.delete(`/api/tasks/${id}`)
    tasks.value = tasks.value.filter(t => t.id !== id)
  } catch (err) {
    errorStore.showError(t('tasks.error_delete'), err, t('tasks.delete_title'))
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
    recurrenceIntervalType: 'WEEKLY',
    recurrenceIntervalValue: 1,
    recurrenceWeekdays: [],
    recurrenceEndDate: '',
    isAllDay: true,
    dueTime: ''
  }
  showTaskModal.value = true
}

function openEditTaskModal(task) {
  isEditMode.value = true
  editingTaskId.value = task.id
  const weekdays = task.recurrence_weekdays
    ? task.recurrence_weekdays.split(',').map(d => parseInt(d)).filter(d => !isNaN(d))
    : []
  taskForm.value = {
    title: task.title,
    description: task.description || '',
    locationId: task.location_id || '',
    hiveId: task.hive_id || '',
    priority: task.priority,
    dueDate: task.due_date || '',
    isRecurring: task.is_recurring,
    recurrenceIntervalType: task.recurrence_interval_type || 'WEEKLY',
    recurrenceIntervalValue: task.recurrence_interval_value || 1,
    recurrenceWeekdays: weekdays,
    recurrenceEndDate: task.recurrence_end_date || '',
    isAllDay: task.is_all_day !== false,
    dueTime: task.due_time || ''
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
      is_all_day: taskForm.value.isAllDay,
      due_time: taskForm.value.isAllDay ? null : (taskForm.value.dueTime || null),
      recurrence_interval_type: taskForm.value.isRecurring ? taskForm.value.recurrenceIntervalType : null,
      recurrence_interval_value: taskForm.value.isRecurring ? taskForm.value.recurrenceIntervalValue : 1,
      recurrence_weekdays: taskForm.value.isRecurring && taskForm.value.recurrenceIntervalType === 'WEEKLY'
        ? taskForm.value.recurrenceWeekdays.join(',')
        : null,
      recurrence_end_date: taskForm.value.isRecurring && taskForm.value.recurrenceEndDate
        ? taskForm.value.recurrenceEndDate
        : null
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
    errorStore.showError(t('tasks.error_save'), err, t('common.save'))
  }
}

// Helpers
function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString(locale.value === 'de' ? 'de-DE' : 'en-US', { day: '2-digit', month: '2-digit', year: 'numeric' })
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
    case 'HIGH': return t('tasks.priority_high_emoji')
    case 'MEDIUM': return t('tasks.priority_medium_emoji')
    case 'LOW': return t('tasks.priority_low_emoji')
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
  if (!interval) return ''
  const up = interval.toUpperCase()
  switch (up) {
    case 'DAILY': return t('hives.recurrence_daily')
    case 'WEEKLY': return t('hives.recurrence_weekly')
    case 'BIWEEKLY': return t('hives.recurrence_biweekly')
    case 'MONTHLY': return t('hives.recurrence_monthly')
    case 'YEARLY': return t('hives.recurrence_yearly')
    default:
      if (up.startsWith('EVERY_') && up.endsWith('_DAYS')) {
        const n = up.split('_')[1]
        return t('hives.recurrence_every_n_days', { n })
      }
      return interval
  }
}
</script>

<style scoped>
@reference "../style.css";

/* Style overrides for v-calendar to make it look premium and fit our custom day cells.
   IMPORTANT: all theme colors come from CSS custom properties defined globally in
   style.css (--cal-*). We cannot use .dark :deep(...) here because Vue would attach
   the scope attribute to .dark, which lives on <html> outside the component subtree
   and would never match. CSS variables inherit through the tree, so this just works. */
:deep(.vc-container) {
  border: none !important;
  background: transparent !important;
  width: 100% !important;
  max-width: 100% !important;
  --calendar-not-month-bg: var(--cal-not-month-bg);
  --calendar-not-month-opacity: var(--cal-not-month-opacity);
}

/* v-calendar v3 DOM:
   .vc-container > .vc-pane > .vc-weeks > [ .vc-weekdays, .vc-week * 6 ] > .vc-day
   Each .vc-week is already a 7-col grid, but rows auto-size → empty weeks end up
   shorter than weeks with content. We use flexbox on .vc-weeks with flex:1 on every
   .vc-week so all 6 rows share the available height equally.
   Borders are produced via gap + background-color (the gap reveals the container bg)
   instead of fragile per-cell borders that conflict with v-calendar's absolute layers. */
:deep(.vc-weeks) {
  display: flex !important;
  flex-direction: column !important;
  gap: 1px !important;
  background-color: var(--cal-grid-line) !important;
  border: 1px solid var(--cal-grid-line) !important;
  border-radius: 0.75rem;
  overflow: hidden;
  padding: 0 !important;
  min-height: 620px !important;
  box-shadow: var(--cal-shadow) !important;
}

:deep(.vc-weekdays) {
  flex-shrink: 0 !important;
  display: grid !important;
  grid-template-columns: repeat(7, 1fr) !important;
  gap: 1px !important;
  background-color: var(--cal-grid-line) !important;
}
:deep(.vc-weekday) {
  background-color: var(--cal-header-bg) !important;
  padding: 10px 0 !important;
  text-align: center !important;
  font-size: 11px !important;
  font-weight: 800 !important;
  letter-spacing: 0.08em !important;
  text-transform: uppercase !important;
  color: var(--cal-header-text) !important;
}

:deep(.vc-week) {
  flex: 1 1 0 !important;
  display: grid !important;
  grid-template-columns: repeat(7, minmax(0, 1fr)) !important;
  gap: 1px !important;
  background-color: var(--cal-grid-line) !important;
  min-height: 0 !important;
}

:deep(.vc-day) {
  display: flex !important;
  flex-direction: column !important;
  min-height: 0 !important;
  background-color: var(--cal-cell-bg) !important;
  padding: 0 !important;
  position: relative !important;
  z-index: 1 !important;
  overflow: hidden !important;
  transition: background-color 0.15s ease !important;
}

:deep(.vc-day.is-not-in-month) {
  background-color: var(--calendar-not-month-bg) !important;
  opacity: var(--calendar-not-month-opacity) !important;
}
</style>
