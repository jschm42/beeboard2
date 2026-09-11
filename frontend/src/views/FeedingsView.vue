<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 font-sans">
    
    <!-- Back to Dashboard Link -->
    <router-link to="/dashboard" class="inline-flex items-center text-sm font-semibold text-primary hover:text-primary-hover mb-4 transition-colors duration-200">
      <svg class="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"/></svg>
      {{ $t('common.back_to_dashboard') }}
    </router-link>

    <!-- Header Area -->
    <div class="mb-8 flex flex-col sm:flex-row sm:justify-between sm:items-center space-y-4 sm:space-y-0">
      <div>
        <h1 class="text-3xl font-extrabold text-gray-900 dark:text-white tracking-tight flex items-center gap-2">
          <span>🍯</span>
          <span>{{ $t('feedings.title') }}</span>
        </h1>
        <p class="text-gray-500 dark:text-gray-400 mt-1">{{ $t('feedings.subtitle') }}</p>
      </div>
      <div class="flex items-center gap-2.5 self-end sm:self-auto shrink-0">
        <button 
          v-if="apiaryStore.activeApiaryId"
          @click="exportCSV" 
          class="px-3.5 py-2.5 bg-gray-100 hover:bg-gray-200 dark:bg-gray-800 dark:hover:bg-gray-700 border border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-200 font-bold text-xs rounded-xl transition duration-150 flex items-center justify-center space-x-1.5 hover-scale"
          :title="$t('feedings.export_csv_btn')"
        >
          <span>📊 {{ $t('feedings.export_csv_btn') }}</span>
        </button>
        <button 
          v-if="apiaryStore.activeApiaryId"
          @click="openCreateModal" 
          class="px-4 py-2.5 bg-primary hover:bg-primary-hover text-white font-extrabold text-xs sm:text-sm rounded-xl shadow-md shadow-primary/20 hover-scale flex items-center justify-center space-x-1.5"
        >
          <span>{{ $t('feedings.new_feeding') }}</span>
        </button>
      </div>
    </div>

    <!-- Alert / Toast Messages -->
    <div v-if="alertMessage" class="mb-6 p-4 rounded-xl text-sm flex items-start space-x-2" :class="alertClass">
      <svg class="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
      <span>{{ alertMessage }}</span>
    </div>

    <!-- No Active Apiary Notice -->
    <div v-if="!apiaryStore.activeApiaryId" class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-8 text-center shadow-sm">
      <span class="text-4xl block mb-2">🐝</span>
      <h3 class="text-lg font-bold text-gray-900 dark:text-white">{{ $t('feedings.error_no_apiary') }}</h3>
    </div>

    <div v-else class="space-y-6">

      <!-- Summary Statistics Cards -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 animate-scale">
        <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-5 shadow-sm flex items-center gap-4">
          <div class="w-12 h-12 rounded-2xl bg-primary/10 text-primary flex items-center justify-center text-2xl font-bold">
            📋
          </div>
          <div>
            <span class="text-xs font-bold text-gray-400 dark:text-gray-500 uppercase tracking-wider block">
              {{ $t('feedings.stat_total_feedings') }}
            </span>
            <span class="text-2xl font-extrabold text-gray-900 dark:text-white font-mono">
              {{ feedingStats.total_count }}
            </span>
          </div>
        </div>

        <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-5 shadow-sm flex items-center gap-4">
          <div class="w-12 h-12 rounded-2xl bg-amber-500/10 text-amber-500 flex items-center justify-center text-2xl font-bold">
            🍯
          </div>
          <div class="min-w-0">
            <span class="text-xs font-bold text-gray-400 dark:text-gray-500 uppercase tracking-wider block">
              {{ $t('feedings.stat_total_fed') }}
            </span>
            <div class="flex flex-wrap gap-2 mt-0.5">
              <span 
                v-for="(tot, unit) in feedingStats.totals_by_unit" 
                :key="unit"
                class="text-sm font-bold font-mono px-2 py-0.5 rounded-lg bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-300 border border-amber-200 dark:border-amber-800"
              >
                {{ tot }} {{ unit }}
              </span>
              <span v-if="Object.keys(feedingStats.totals_by_unit).length === 0" class="text-xs text-gray-400">
                0
              </span>
            </div>
          </div>
        </div>

        <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-5 shadow-sm flex items-center gap-4">
          <div class="w-12 h-12 rounded-2xl bg-emerald-500/10 text-emerald-500 flex items-center justify-center text-2xl font-bold">
            🌾
          </div>
          <div class="min-w-0 flex-1">
            <span class="text-xs font-bold text-gray-400 dark:text-gray-500 uppercase tracking-wider block">
              {{ $t('feedings.stat_by_type') }}
            </span>
            <div class="flex flex-wrap gap-1.5 mt-1 overflow-x-auto max-h-12">
              <span 
                v-for="bt in feedingStats.by_feed_type" 
                :key="bt.feed_type_id"
                class="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-gray-100 dark:bg-dark-border text-gray-700 dark:text-gray-300"
                :title="`${bt.feed_type_name}: ${bt.total_amount} ${bt.unit} (${bt.count}x)`"
              >
                {{ bt.feed_type_name }}: <span class="font-mono font-bold">{{ bt.total_amount }} {{ bt.unit }}</span>
              </span>
              <span v-if="feedingStats.by_feed_type.length === 0" class="text-xs text-gray-400">
                -
              </span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Filter Bar -->
      <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-6 shadow-sm flex flex-col md:flex-row gap-4 items-end animate-scale">
        <div class="flex-1 w-full">
          <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('feedings.filter_location') }}</label>
          <select 
            v-model="filters.locationId" 
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-sm cursor-pointer focus:outline-none focus:ring-2 focus:ring-primary"
            @change="onLocationFilterChange"
          >
            <option value="">{{ $t('feedings.all_locations') }}</option>
            <option v-for="loc in locations" :key="loc.id" :value="loc.id">{{ loc.name }}</option>
          </select>
        </div>

        <div class="flex-1 w-full">
          <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('feedings.filter_hive') }}</label>
          <select 
            v-model="filters.hiveId" 
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-sm cursor-pointer focus:outline-none focus:ring-2 focus:ring-primary"
            @change="fetchFeedings"
          >
            <option value="">{{ $t('feedings.all_hives') }}</option>
            <option v-for="hive in filteredHivesForFilter" :key="hive.id" :value="hive.id">{{ hive.name }}</option>
          </select>
        </div>

        <div class="flex-1 w-full">
          <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('feedings.filter_feed_type') }}</label>
          <select 
            v-model="filters.feedTypeId" 
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-sm cursor-pointer focus:outline-none focus:ring-2 focus:ring-primary"
            @change="fetchFeedings"
          >
            <option value="">{{ $t('feedings.all_feed_types') }}</option>
            <option v-for="ft in activeFeedTypes" :key="ft.id" :value="ft.id">{{ ft.name }} ({{ ft.unit }})</option>
          </select>
        </div>

        <div class="flex-1 w-full">
          <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('feedings.filter_start_date') }}</label>
          <input 
            v-model="filters.startDate" 
            type="date" 
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-sm font-mono focus:outline-none focus:ring-2 focus:ring-primary"
            @change="fetchFeedings"
          />
        </div>

        <div class="flex-1 w-full">
          <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('feedings.filter_end_date') }}</label>
          <input 
            v-model="filters.endDate" 
            type="date" 
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-sm font-mono focus:outline-none focus:ring-2 focus:ring-primary"
            @change="fetchFeedings"
          />
        </div>

        <button 
          @click="resetFilters" 
          class="px-4 py-2 bg-gray-100 hover:bg-gray-200 dark:bg-gray-800 dark:hover:bg-gray-700 border border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-200 text-xs font-bold rounded-xl transition duration-150 w-full md:w-auto h-[38px] flex items-center justify-center hover-scale shrink-0"
        >
          {{ $t('feedings.filter_reset') }}
        </button>
      </div>

      <!-- Feedings Ledger Table/Cards -->
      <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl overflow-hidden shadow-sm">
        <div v-if="loadingFeedings" class="flex flex-col items-center justify-center py-20">
          <svg class="animate-spin h-8 w-8 text-primary mb-3" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
          <span class="text-xs text-gray-400 font-bold">{{ $t('feedings.loading') }}</span>
        </div>

        <div v-else-if="feedings.length === 0" class="flex flex-col items-center justify-center py-20 text-center px-4">
          <span class="text-4xl mb-3">🍯</span>
          <h3 class="text-base font-bold text-gray-900 dark:text-white">{{ $t('feedings.empty_title') }}</h3>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1 max-w-sm">{{ $t('feedings.empty_desc') }}</p>
          <button 
            @click="openCreateModal"
            class="mt-4 px-4 py-2 bg-primary hover:bg-primary-hover text-white text-xs font-bold rounded-xl shadow-md hover-scale"
          >
            {{ $t('feedings.new_feeding') }}
          </button>
        </div>

        <div v-else class="overflow-x-auto">
          <!-- Desktop Table view -->
          <table class="w-full text-left border-collapse hidden md:table">
            <thead>
              <tr class="bg-gray-50 dark:bg-dark-bg text-gray-500 dark:text-gray-400 text-[10px] font-bold uppercase tracking-wider border-b border-gray-100 dark:border-dark-border">
                <th class="px-5 py-4">{{ $t('feedings.table_date') }}</th>
                <th class="px-4 py-4">{{ $t('feedings.table_hive') }}</th>
                <th class="px-4 py-4">{{ $t('feedings.table_location') }}</th>
                <th class="px-4 py-4">{{ $t('feedings.table_feed_type') }}</th>
                <th class="px-4 py-4 text-right">{{ $t('feedings.table_amount') }}</th>
                <th class="px-4 py-4">{{ $t('feedings.table_fed_by') }}</th>
                <th class="px-4 py-4">{{ $t('feedings.table_notes') }}</th>
                <th class="px-4 py-4 text-right">{{ $t('common.actions') }}</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100 dark:divide-dark-border text-sm">
              <tr 
                v-for="f in feedings" 
                :key="f.id" 
                class="hover:bg-gray-50/50 dark:hover:bg-dark-bg/30 transition-colors duration-150"
              >
                <td class="px-5 py-4 font-mono font-bold text-gray-900 dark:text-white shrink-0 text-xs whitespace-nowrap">
                  {{ formatDate(f.date) }}
                </td>
                <td class="px-4 py-4 font-bold text-primary whitespace-nowrap">
                  {{ f.hive?.name || '-' }}
                </td>
                <td class="px-4 py-4 text-gray-600 dark:text-gray-300 whitespace-nowrap text-xs">
                  📍 {{ f.hive?.location?.name || '-' }}
                </td>
                <td class="px-4 py-4 text-gray-900 dark:text-white font-semibold">
                  {{ f.feed_type?.name || '-' }}
                </td>
                <td class="px-4 py-4 text-right font-mono font-bold text-amber-600 dark:text-amber-500 whitespace-nowrap">
                  {{ f.amount }} {{ f.feed_type?.unit }}
                </td>
                <td class="px-4 py-4 text-gray-600 dark:text-gray-300 text-xs whitespace-nowrap">
                  {{ f.fed_by || '-' }}
                </td>
                <td class="px-4 py-4 text-gray-500 dark:text-gray-400 text-xs max-w-xs truncate" :title="f.notes">
                  {{ f.notes || '-' }}
                </td>
                <td class="px-4 py-4 text-right space-x-2 whitespace-nowrap">
                  <button 
                    @click="openEditModal(f)" 
                    class="p-1.5 text-gray-500 hover:text-primary hover:bg-gray-100 dark:hover:bg-dark-border rounded-lg transition-all duration-150 inline-flex hover-scale"
                    :title="$t('common.edit')"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/></svg>
                  </button>
                  <button 
                    @click="deleteFeeding(f)" 
                    class="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-500/10 rounded-lg transition-all duration-150 inline-flex hover-scale"
                    :title="$t('common.delete')"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>

          <!-- Mobile Cards View -->
          <div class="md:hidden divide-y divide-gray-100 dark:divide-dark-border">
            <div 
              v-for="f in feedings" 
              :key="f.id" 
              class="p-4 space-y-3"
            >
              <div class="flex justify-between items-start">
                <div>
                  <span class="font-mono text-xs font-bold text-gray-500 dark:text-gray-400 block">
                    {{ formatDate(f.date) }}
                  </span>
                  <h4 class="font-extrabold text-base text-gray-900 dark:text-white">
                    {{ f.hive?.name }}
                  </h4>
                  <span class="text-xs text-gray-500 dark:text-gray-400">
                    📍 {{ f.hive?.location?.name || '-' }}
                  </span>
                </div>
                <div class="text-right">
                  <span class="px-2.5 py-1 rounded-lg bg-amber-500/10 text-amber-600 dark:text-amber-400 font-mono font-bold text-sm block">
                    {{ f.amount }} {{ f.feed_type?.unit }}
                  </span>
                  <span class="text-[11px] text-gray-500 dark:text-gray-400 font-semibold block mt-0.5">
                    {{ f.feed_type?.name }}
                  </span>
                </div>
              </div>

              <div v-if="f.notes" class="text-xs text-gray-600 dark:text-gray-300 italic bg-gray-50 dark:bg-dark-bg p-2 rounded-xl">
                {{ f.notes }}
              </div>

              <div class="flex justify-between items-center pt-1 text-xs">
                <span class="text-gray-400">👤 {{ f.fed_by || '-' }}</span>
                <div class="flex gap-2">
                  <button 
                    @click="openEditModal(f)" 
                    class="px-3 py-1 bg-gray-100 dark:bg-dark-border text-gray-700 dark:text-gray-300 rounded-lg font-bold"
                  >
                    {{ $t('common.edit') }}
                  </button>
                  <button 
                    @click="deleteFeeding(f)" 
                    class="px-3 py-1 bg-red-50 dark:bg-red-950/40 text-red-600 dark:text-red-400 rounded-lg font-bold"
                  >
                    {{ $t('common.delete') }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>

    <!-- Create / Edit Modal -->
    <div 
      v-if="showModal" 
      class="fixed inset-0 z-50 overflow-y-auto bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 animate-fade-in"
    >
      <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl max-w-xl w-full p-6 shadow-2xl space-y-5 animate-scale">
        <div class="flex justify-between items-center border-b border-gray-100 dark:border-dark-border/60 pb-4">
          <h3 class="text-lg font-extrabold text-gray-900 dark:text-white flex items-center gap-2">
            <span>🍯</span>
            <span>{{ isEditing ? $t('feedings.edit_feeding') : $t('feedings.new_feeding') }}</span>
          </h3>
          <button 
            @click="showModal = false" 
            class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 p-1"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>

        <form @submit.prevent="submitForm" class="space-y-4">
          
          <!-- Mode Toggle (Only when creating) -->
          <div v-if="!isEditing" class="p-1 bg-gray-100 dark:bg-dark-bg rounded-xl flex">
            <button 
              type="button" 
              @click="entryMode = 'single'" 
              class="flex-1 py-1.5 text-xs font-bold rounded-lg transition-all"
              :class="entryMode === 'single' ? 'bg-white dark:bg-dark-card text-primary shadow-sm' : 'text-gray-500 hover:text-gray-800 dark:hover:text-gray-200'"
            >
              {{ $t('feedings.form_single_mode') }}
            </button>
            <button 
              type="button" 
              @click="entryMode = 'batch'" 
              class="flex-1 py-1.5 text-xs font-bold rounded-lg transition-all"
              :class="entryMode === 'batch' ? 'bg-white dark:bg-dark-card text-primary shadow-sm' : 'text-gray-500 hover:text-gray-800 dark:hover:text-gray-200'"
            >
              {{ $t('feedings.form_batch_mode') }}
            </button>
          </div>

          <!-- Single Hive Selection -->
          <div v-if="isEditing || entryMode === 'single'">
            <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">
              {{ $t('feedings.form_hive') }}
            </label>
            <select 
              v-model="form.hive_id" 
              required
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary cursor-pointer"
            >
              <option value="" disabled>{{ $t('feedings.select_hive') }}</option>
              <option v-for="hive in allHives" :key="hive.id" :value="hive.id">
                {{ hive.name }} (📍 {{ hive.location?.name || '-' }})
              </option>
            </select>
          </div>

          <!-- Batch Multiple Hives Selection -->
          <div v-else class="space-y-2">
            <div class="flex justify-between items-center">
              <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider">
                {{ $t('feedings.form_hives') }}
              </label>
              <span class="text-xs font-mono font-bold text-primary">
                {{ form.hive_ids.length }} ausgewählt
              </span>
            </div>
            
            <div class="max-h-40 overflow-y-auto border border-gray-200 dark:border-dark-border rounded-xl p-3 space-y-2 bg-gray-50/50 dark:bg-dark-bg/50">
              <div v-for="loc in locations" :key="loc.id" class="space-y-1">
                <div class="flex justify-between items-center text-xs font-bold text-gray-500 dark:text-gray-400 pt-1">
                  <span>📍 {{ loc.name }}</span>
                  <button 
                    type="button" 
                    @click="toggleLocationHives(loc.id)" 
                    class="text-[11px] text-primary hover:underline"
                  >
                    Alle an/abwählen
                  </button>
                </div>
                <div class="grid grid-cols-2 gap-1.5 pl-2">
                  <label 
                    v-for="h in getHivesByLocation(loc.id)" 
                    :key="h.id"
                    class="flex items-center space-x-2 text-xs text-gray-700 dark:text-gray-300 cursor-pointer p-1 rounded hover:bg-gray-100 dark:hover:bg-dark-border"
                  >
                    <input 
                      type="checkbox" 
                      :value="h.id" 
                      v-model="form.hive_ids" 
                      class="rounded text-primary focus:ring-primary h-3.5 w-3.5"
                    />
                    <span class="font-medium truncate">{{ h.name }}</span>
                  </label>
                </div>
              </div>
            </div>
          </div>

          <!-- Feed Type Selection -->
          <div>
            <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">
              {{ $t('feedings.form_feed_type') }}
            </label>
            <select 
              v-model="form.feed_type_id" 
              required
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary cursor-pointer"
            >
              <option value="" disabled>{{ $t('feedings.select_feed_type') }}</option>
              <option v-for="ft in activeFeedTypes" :key="ft.id" :value="ft.id">
                {{ ft.name }} ({{ ft.unit }})
              </option>
            </select>
          </div>

          <!-- Amount and Date in Grid -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">
                {{ $t('feedings.form_amount') }}
              </label>
              <div class="relative flex items-center">
                <input 
                  v-model.number="form.amount" 
                  type="number" 
                  step="0.01" 
                  min="0.01" 
                  required
                  placeholder="z.B. 5.0"
                  class="w-full px-3 py-2 pr-12 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-sm font-mono focus:outline-none focus:ring-2 focus:ring-primary"
                />
                <span class="absolute right-3 text-xs font-bold font-mono text-gray-400">
                  {{ selectedFeedTypeUnit }}
                </span>
              </div>
            </div>

            <div>
              <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">
                {{ $t('feedings.form_date') }}
              </label>
              <input 
                v-model="form.date" 
                type="date" 
                required
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-sm font-mono focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
          </div>

          <!-- Fed By -->
          <div>
            <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">
              {{ $t('feedings.form_fed_by') }}
            </label>
            <input 
              v-model="form.fed_by" 
              type="text" 
              placeholder="z.B. Imker Name"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>

          <!-- Notes -->
          <div>
            <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">
              {{ $t('feedings.form_notes') }}
            </label>
            <textarea 
              v-model="form.notes" 
              rows="2"
              :placeholder="$t('feedings.form_notes_placeholder')"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary resize-y"
            ></textarea>
          </div>

          <!-- Actions -->
          <div class="flex justify-end gap-3 pt-3 border-t border-gray-100 dark:border-dark-border/60">
            <button 
              type="button" 
              @click="showModal = false" 
              class="px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-xl text-xs font-semibold hover:bg-gray-100 dark:hover:bg-dark-border text-gray-700 dark:text-gray-300 transition duration-150"
            >
              {{ $t('common.cancel') }}
            </button>
            <button 
              type="submit" 
              class="px-5 py-2 bg-primary hover:bg-primary-hover text-white text-xs font-bold rounded-xl shadow-md hover-scale flex items-center gap-1.5"
              :disabled="savingFeeding"
            >
              <svg v-if="savingFeeding" class="animate-spin h-3.5 w-3.5 text-white" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
              <span>{{ savingFeeding ? $t('common.loading') : $t('common.save') }}</span>
            </button>
          </div>

        </form>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import axios from 'axios'
import { useApiaryStore } from '../stores/apiary'
import { useAuthStore } from '../stores/auth'
import { useConfirmStore } from '../stores/confirm'

const { t } = useI18n()
const apiaryStore = useApiaryStore()
const authStore = useAuthStore()
const confirmStore = useConfirmStore()

const feedings = ref([])
const activeFeedTypes = ref([])
const locations = ref([])
const allHives = ref([])
const loadingFeedings = ref(false)
const savingFeeding = ref(false)

const feedingStats = ref({
  total_count: 0,
  totals_by_unit: {},
  by_feed_type: []
})

const alertMessage = ref('')
const alertClass = ref('')

const filters = reactive({
  locationId: '',
  hiveId: '',
  feedTypeId: '',
  startDate: '',
  endDate: ''
})

const showModal = ref(false)
const isEditing = ref(false)
const editingFeedingId = ref(null)
const entryMode = ref('single') // 'single' | 'batch'

const form = reactive({
  hive_id: '',
  hive_ids: [],
  feed_type_id: '',
  amount: null,
  date: new Date().toISOString().split('T')[0],
  fed_by: '',
  notes: ''
})

const selectedFeedTypeUnit = computed(() => {
  if (!form.feed_type_id) return ''
  const ft = activeFeedTypes.value.find(t => t.id === form.feed_type_id)
  return ft ? ft.unit : ''
})

const filteredHivesForFilter = computed(() => {
  if (!filters.locationId) return allHives.value
  return allHives.value.filter(h => h.location_id === filters.locationId)
})

function getHivesByLocation(locationId) {
  return allHives.value.filter(h => h.location_id === locationId)
}

function toggleLocationHives(locationId) {
  const locHiveIds = getHivesByLocation(locationId).map(h => h.id)
  const allSelected = locHiveIds.every(id => form.hive_ids.includes(id))
  if (allSelected) {
    form.hive_ids = form.hive_ids.filter(id => !locHiveIds.includes(id))
  } else {
    const combined = new Set([...form.hive_ids, ...locHiveIds])
    form.hive_ids = Array.from(combined)
  }
}

function onLocationFilterChange() {
  filters.hiveId = ''
  fetchFeedings()
}

function resetFilters() {
  filters.locationId = ''
  filters.hiveId = ''
  filters.feedTypeId = ''
  filters.startDate = ''
  filters.endDate = ''
  fetchFeedings()
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  try {
    const parts = dateStr.split('-')
    if (parts.length === 3) {
      return `${parts[2]}.${parts[1]}.${parts[0]}`
    }
    return dateStr
  } catch {
    return dateStr
  }
}

function showAlert(msg, isError = false) {
  alertMessage.value = msg
  alertClass.value = isError 
    ? 'bg-rose-500/10 border border-rose-500/20 text-rose-600 dark:text-rose-400' 
    : 'bg-emerald-500/10 border border-emerald-500/20 text-emerald-600 dark:text-emerald-400'
  setTimeout(() => {
    alertMessage.value = ''
  }, 4000)
}

async function fetchActiveFeedTypes() {
  try {
    const res = await axios.get('/api/feedings/feed-types')
    activeFeedTypes.value = res.data
  } catch (err) {
    console.error('Failed to load feed types:', err)
  }
}

async function fetchLocationsAndHives() {
  if (!apiaryStore.activeApiaryId) return
  try {
    const [locRes, hivesRes] = await Promise.all([
      axios.get('/api/locations', { params: { apiary_id: apiaryStore.activeApiaryId } }),
      axios.get('/api/hives', { params: { apiary_id: apiaryStore.activeApiaryId } })
    ])
    locations.value = locRes.data
    allHives.value = hivesRes.data
  } catch (err) {
    console.error('Failed to load locations/hives:', err)
  }
}

async function fetchStats() {
  if (!apiaryStore.activeApiaryId) return
  try {
    const params = {
      apiary_id: apiaryStore.activeApiaryId,
      ...(filters.hiveId && { hive_id: filters.hiveId }),
      ...(filters.locationId && { location_id: filters.locationId }),
      ...(filters.feedTypeId && { feed_type_id: filters.feedTypeId }),
      ...(filters.startDate && { start_date: filters.startDate }),
      ...(filters.endDate && { end_date: filters.endDate })
    }
    const res = await axios.get('/api/feedings/stats', { params })
    feedingStats.value = res.data
  } catch (err) {
    console.error('Failed to load feeding stats:', err)
  }
}

async function fetchFeedings() {
  if (!apiaryStore.activeApiaryId) {
    feedings.value = []
    return
  }
  loadingFeedings.value = true
  try {
    const params = {
      apiary_id: apiaryStore.activeApiaryId,
      ...(filters.hiveId && { hive_id: filters.hiveId }),
      ...(filters.locationId && { location_id: filters.locationId }),
      ...(filters.feedTypeId && { feed_type_id: filters.feedTypeId }),
      ...(filters.startDate && { start_date: filters.startDate }),
      ...(filters.endDate && { end_date: filters.endDate })
    }
    const res = await axios.get('/api/feedings', { params })
    feedings.value = res.data
    await fetchStats()
  } catch (err) {
    console.error('Failed to fetch feedings:', err)
    showAlert(t('feedings.error_fetch'), true)
  } finally {
    loadingFeedings.value = false
  }
}

function openCreateModal() {
  isEditing.value = false
  editingFeedingId.value = null
  entryMode.value = 'single'
  
  const userFull = [authStore.user?.first_name, authStore.user?.last_name].filter(Boolean).join(' ')
  form.hive_id = allHives.value.length > 0 ? allHives.value[0].id : ''
  form.hive_ids = []
  form.feed_type_id = activeFeedTypes.value.length > 0 ? activeFeedTypes.value[0].id : ''
  form.amount = null
  form.date = new Date().toISOString().split('T')[0]
  form.fed_by = userFull || authStore.user?.username || ''
  form.notes = ''
  
  showModal.value = true
}

function openEditModal(feeding) {
  isEditing.value = true
  editingFeedingId.value = feeding.id
  entryMode.value = 'single'
  
  form.hive_id = feeding.hive_id
  form.hive_ids = []
  form.feed_type_id = feeding.feed_type_id
  form.amount = feeding.amount
  form.date = feeding.date
  form.fed_by = feeding.fed_by || ''
  form.notes = feeding.notes || ''
  
  showModal.value = true
}

async function submitForm() {
  if (isEditing.value) {
    if (!form.hive_id || !form.feed_type_id || !form.amount || form.amount <= 0) {
      return
    }
    savingFeeding.value = true
    try {
      await axios.put(`/api/feedings/${editingFeedingId.value}`, {
        hive_id: form.hive_id,
        feed_type_id: form.feed_type_id,
        amount: form.amount,
        date: form.date,
        fed_by: form.fed_by.trim() || null,
        notes: form.notes.trim() || null
      })
      showAlert(t('feedings.success_update'))
      showModal.value = false
      await fetchFeedings()
    } catch (err) {
      console.error('Update feeding error:', err)
      showAlert(err.response?.data?.detail || t('feedings.error_save'), true)
    } finally {
      savingFeeding.value = false
    }
  } else {
    // Creation mode
    if (entryMode.value === 'single') {
      if (!form.hive_id || !form.feed_type_id || !form.amount || form.amount <= 0) {
        return
      }
      savingFeeding.value = true
      try {
        await axios.post('/api/feedings', {
          hive_id: form.hive_id,
          feed_type_id: form.feed_type_id,
          amount: form.amount,
          date: form.date,
          fed_by: form.fed_by.trim() || null,
          notes: form.notes.trim() || null
        })
        showAlert(t('feedings.success_create'))
        showModal.value = false
        await fetchFeedings()
      } catch (err) {
        console.error('Create feeding error:', err)
        showAlert(err.response?.data?.detail || t('feedings.error_save'), true)
      } finally {
        savingFeeding.value = false
      }
    } else {
      // Batch mode
      if (form.hive_ids.length === 0) {
        showAlert('Bitte wähle mindestens ein Bienenvolk aus.', true)
        return
      }
      if (!form.feed_type_id || !form.amount || form.amount <= 0) {
        return
      }
      savingFeeding.value = true
      try {
        const res = await axios.post('/api/feedings/batch', {
          hive_ids: form.hive_ids,
          feed_type_id: form.feed_type_id,
          amount: form.amount,
          date: form.date,
          fed_by: form.fed_by.trim() || null,
          notes: form.notes.trim() || null
        })
        showAlert(t('feedings.success_batch_create', { count: res.data.length }))
        showModal.value = false
        await fetchFeedings()
      } catch (err) {
        console.error('Batch feeding error:', err)
        showAlert(err.response?.data?.detail || t('feedings.error_save'), true)
      } finally {
        savingFeeding.value = false
      }
    }
  }
}

async function deleteFeeding(feeding) {
  const confirmed = await confirmStore.ask({
    title: t('feedings.delete_feeding'),
    message: t('feedings.delete_confirm'),
    type: 'danger',
    confirmText: t('feedings.delete_btn_confirm')
  })
  if (!confirmed) return

  try {
    await axios.delete(`/api/feedings/${feeding.id}`)
    showAlert(t('feedings.success_delete'))
    await fetchFeedings()
  } catch (err) {
    console.error('Delete feeding error:', err)
    showAlert(err.response?.data?.detail || t('feedings.error_delete'), true)
  }
}

function exportCSV() {
  if (!apiaryStore.activeApiaryId) return
  const params = new URLSearchParams({
    apiary_id: apiaryStore.activeApiaryId,
    ...(filters.hiveId && { hive_id: filters.hiveId }),
    ...(filters.locationId && { location_id: filters.locationId }),
    ...(filters.feedTypeId && { feed_type_id: filters.feedTypeId }),
    ...(filters.startDate && { start_date: filters.startDate }),
    ...(filters.endDate && { end_date: filters.endDate })
  })
  window.open(`/api/feedings/export/csv?${params.toString()}`, '_blank')
}

watch(() => apiaryStore.activeApiaryId, async () => {
  await fetchLocationsAndHives()
  await fetchFeedings()
})

onMounted(async () => {
  await fetchActiveFeedTypes()
  await fetchLocationsAndHives()
  await fetchFeedings()
})
</script>

<style scoped>
.animate-scale {
  animation: scaleIn 0.2s ease-out;
}
@keyframes scaleIn {
  from { opacity: 0; transform: scale(0.98); }
  to { opacity: 1; transform: scale(1); }
}
</style>
