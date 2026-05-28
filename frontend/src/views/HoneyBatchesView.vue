<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 font-sans">
    
    <!-- Back to Dashboard Link -->
    <router-link to="/dashboard" class="inline-flex items-center text-sm font-semibold text-primary hover:text-primary-hover mb-4 transition-colors duration-200">
      <svg class="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"/></svg>
      {{ $t('common.back_to_dashboard') }}
    </router-link>

    <!-- Header Area -->
    <div class="mb-8 flex flex-col md:flex-row md:justify-between md:items-center space-y-4 md:space-y-0">
      <div>
        <h1 class="text-3xl font-extrabold text-gray-900 dark:text-white tracking-tight">🍯 {{ $t('honey_batches.title') }}</h1>
        <p class="text-gray-500 dark:text-gray-400 mt-1">{{ $t('honey_batches.subtitle') }}</p>
      </div>
      
      <div class="flex items-center space-x-3">
        <button 
          @click="exportCSV" 
          :disabled="batches.length === 0"
          class="px-4 py-2.5 bg-gray-100 hover:bg-gray-200 dark:bg-dark-card dark:hover:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-200 font-extrabold text-sm rounded-xl transition-all duration-200 hover-scale flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
          <span>{{ $t('honey_batches.export_csv_btn') }}</span>
        </button>
        <button 
          @click="openCreateModal" 
          class="px-5 py-2.5 bg-primary hover:bg-primary-hover text-white font-extrabold text-sm rounded-xl shadow-md shadow-primary/20 hover-scale flex items-center justify-center space-x-2"
        >
          <span>{{ $t('honey_batches.new_batch_btn') }}</span>
        </button>
      </div>
    </div>

    <!-- Alert Message -->
    <div v-if="alertMessage" class="mb-6 p-4 rounded-xl text-sm flex items-start space-x-2" :class="alertClass">
      <svg class="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
      <span>{{ alertMessage }}</span>
    </div>

    <!-- AI Batch Draft Card -->
    <div class="mb-8 bg-gradient-to-r from-amber-500/10 to-primary/10 border border-amber-500/20 rounded-3xl p-6 shadow-sm">
      <div class="flex items-center space-x-2.5 mb-3">
        <div class="p-2 bg-amber-500 text-white rounded-xl">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 9.172V5L8 4z"/></svg>
        </div>
        <h3 class="text-lg font-bold text-gray-900 dark:text-white">{{ $t('honey_batches.ai_draft_title') }}</h3>
      </div>
      <p class="text-xs text-gray-600 dark:text-gray-400 mb-4">
        {{ $t('honey_batches.ai_draft_subtitle') }}
      </p>
      <div class="flex flex-col sm:flex-row space-y-3 sm:space-y-0 sm:space-x-3">
        <textarea 
          v-model="aiDraftText" 
          :placeholder="$t('honey_batches.ai_draft_placeholder')"
          rows="2"
          class="flex-1 px-3 py-2 border border-amber-300 dark:border-amber-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-amber-500 text-sm placeholder-gray-400 dark:placeholder-gray-600"
        ></textarea>
        <button 
          @click="generateAIDraft"
          :disabled="aiLoading || !aiDraftText.trim()"
          class="px-5 py-2.5 bg-amber-500 hover:bg-amber-600 text-white font-extrabold text-sm rounded-xl shadow-md transition-all duration-200 shrink-0 flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed hover-scale"
        >
          <svg class="animate-spin h-4 w-4 text-white" v-if="aiLoading" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
          <span>{{ $t('honey_batches.ai_draft_btn') }}</span>
        </button>
      </div>
    </div>

    <!-- Create/Edit Modal Form -->
    <div v-if="showModal" class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl shadow-md w-full max-w-3xl mx-auto p-6 mb-8 animate-scale">
      <div class="flex justify-between items-center mb-6 pb-4 border-b border-gray-100 dark:border-dark-border">
        <h3 class="text-xl font-bold text-gray-900 dark:text-white">
          {{ isEditMode ? $t('honey_batches.edit_modal_title') : $t('honey_batches.create_modal_title') }}
        </h3>
        <button @click="closeModal" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
        </button>
      </div>
      
      <form @submit.prevent="submitForm">
        <div class="space-y-6">
          
          <!-- Section 1: Basic Info -->
          <div>
            <h4 class="text-sm font-bold text-amber-500 uppercase tracking-wider mb-3">{{ $t('honey_batches.section_basic_info') }}</h4>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div :class="selectedHoneyTypePreset === 'custom' ? 'md:col-span-3 grid grid-cols-1 md:grid-cols-3 gap-4' : 'md:col-span-1'">
                <div :class="selectedHoneyTypePreset === 'custom' ? 'md:col-span-1' : 'w-full'">
                  <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('honey_batches.honey_type_label') }}</label>
                  <select 
                    v-model="selectedHoneyTypePreset" 
                    required
                    class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm"
                  >
                    <optgroup :label="$t('honey_batches.optgroup_specific')">
                      <option v-for="t in DIB_HONEY_TYPES.specific" :key="t" :value="t">{{ $t('honey_types.' + t) }}</option>
                    </optgroup>
                    <optgroup :label="$t('honey_batches.optgroup_double')">
                      <option v-for="t in DIB_HONEY_TYPES.double" :key="t" :value="t">{{ $t('honey_types.' + t) }}</option>
                    </optgroup>
                    <optgroup :label="$t('honey_batches.optgroup_regional')">
                      <option v-for="t in DIB_HONEY_TYPES.regional" :key="t" :value="t">{{ $t('honey_types.' + t) }}</option>
                    </optgroup>
                    <optgroup :label="$t('honey_batches.optgroup_unspecific')">
                      <option v-for="t in DIB_HONEY_TYPES.unspecific" :key="t" :value="t">{{ $t('honey_types.' + t) }}</option>
                    </optgroup>
                    <optgroup :label="$t('honey_batches.optgroup_general')">
                      <option v-for="t in DIB_HONEY_TYPES.general" :key="t" :value="t">{{ $t('honey_types.' + t) }}</option>
                    </optgroup>
                    <option value="custom">{{ $t('honey_batches.custom_preset_label') }}</option>
                  </select>
                </div>

                <div v-if="selectedHoneyTypePreset === 'custom'" class="md:col-span-2 animate-scale">
                  <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('honey_batches.custom_honey_type_label') }}</label>
                  <input 
                    v-model="form.honey_type" 
                    type="text" 
                    required
                    :placeholder="$t('honey_batches.custom_honey_type_placeholder')"
                    class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm"
                  />
                  <span class="text-[10px] text-gray-500 dark:text-gray-400 mt-1 block">
                    {{ $t('honey_batches.honey_type_hint') }}
                  </span>
                </div>
              </div>

              <div :class="selectedHoneyTypePreset === 'custom' ? 'md:col-span-3 grid grid-cols-1 md:grid-cols-2 gap-4' : 'contents'">
                <div>
                  <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('honey_batches.harvest_date_label') }}</label>
                  <input 
                    v-model="form.harvest_date" 
                    type="date" 
                    required
                    class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm font-mono"
                  />
                </div>

                <div>
                  <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('honey_batches.bottling_date_label') }}</label>
                  <input 
                    v-model="form.bottling_date" 
                    type="date" 
                    class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm font-mono"
                  />
                </div>
              </div>
            </div>
          </div>

          <!-- Section 2: Quantities & Quality -->
          <div>
            <h4 class="text-sm font-bold text-amber-500 uppercase tracking-wider mb-3">{{ $t('honey_batches.section_quantities') }}</h4>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('honey_batches.quantity_kg_label') }}</label>
                <input 
                  v-model="form.quantity_kg" 
                  type="number" 
                  step="0.01"
                  required
                  min="0.01"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm"
                />
              </div>

              <div>
                <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('honey_batches.water_content_label') }}</label>
                <input 
                  v-model="form.water_content_percent" 
                  type="number" 
                  step="0.1"
                  min="0"
                  max="100"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm"
                />
                <span v-if="form.water_content_percent > 18" class="text-[10px] text-red-500 font-bold block mt-1">{{ $t('honey_batches.water_content_warning') }}</span>
              </div>

              <div>
                <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('honey_batches.heating_temp_label') }}</label>
                <input 
                  v-model="form.heating_temperature_celsius" 
                  type="number" 
                  step="0.1"
                  min="0"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm"
                />
              </div>
            </div>
          </div>

          <!-- Section 3: Compliance & Labeling (LKV) -->
          <div>
            <h4 class="text-sm font-bold text-amber-500 uppercase tracking-wider mb-3">{{ $t('honey_batches.section_compliance') }}</h4>
            <div class="bg-gray-50 dark:bg-dark-bg border border-gray-200 dark:border-gray-800 rounded-2xl p-4 space-y-4">
              
              <!-- Checkbox exact date exception -->
              <div class="flex items-start space-x-3">
                <input 
                  v-model="form.is_exact_date" 
                  id="is_exact_date"
                  type="checkbox"
                  class="mt-1 h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                />
                <label for="is_exact_date" class="text-sm text-gray-700 dark:text-gray-300">
                  <span class="font-bold block">{{ $t('honey_batches.exact_date_mhd_label') }}</span>
                  <span class="text-xs text-gray-500 dark:text-gray-400 block mt-0.5">
                    {{ $t('honey_batches.exact_date_mhd_desc') }}
                  </span>
                </label>
              </div>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
                <div>
                  <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">
                    {{ $t('honey_batches.batch_number_label') }} {{ form.is_exact_date ? $t('honey_batches.batch_number_optional') : $t('honey_batches.batch_number_required') }}
                  </label>
                  <div class="flex space-x-2">
                    <input 
                      v-model="form.batch_number" 
                      type="text" 
                      :required="!form.is_exact_date"
                      :placeholder="$t('honey_batches.batch_number_placeholder')"
                      class="flex-1 min-w-0 px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm font-mono"
                    />
                    <button
                      type="button"
                      @click="fetchSuggestion('batch_number')"
                      class="px-3 py-2 bg-gray-100 hover:bg-gray-200 dark:bg-gray-800 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-200 text-xs font-bold rounded-xl transition duration-150 border border-gray-200 dark:border-gray-700 shrink-0"
                      :title="$t('honey_batches.suggest_btn')"
                    >
                      {{ $t('honey_batches.suggest_btn') }}
                    </button>
                  </div>
                </div>

                <div>
                  <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('honey_batches.best_before_date_label') }}</label>
                  <input 
                    v-model="form.best_before_date" 
                    type="date" 
                    required
                    class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm font-mono"
                  />
                </div>
              </div>

            </div>
          </div>

          <!-- Section 4: D.I.B. Gewährverschlüsse -->
          <div>
            <h4 class="text-sm font-bold text-amber-500 uppercase tracking-wider mb-3">{{ $t('honey_batches.section_dib_labels') }}</h4>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('honey_batches.dib_label_start_label') }}</label>
                <input 
                  v-model="form.dib_label_start" 
                  type="text" 
                  :placeholder="$t('honey_batches.dib_label_start_placeholder')"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm font-mono"
                />
              </div>

              <div>
                <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('honey_batches.dib_label_end_label') }}</label>
                <input 
                  v-model="form.dib_label_end" 
                  type="text" 
                  :placeholder="$t('honey_batches.dib_label_end_placeholder')"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm font-mono"
                />
              </div>
            </div>
            <p class="text-[10px] text-gray-500 dark:text-gray-400 mt-1.5 italic">
              {{ $t('honey_batches.dib_label_desc') }}
            </p>
          </div>

          <!-- Section 5: Reserve Sample -->
          <div>
            <h4 class="text-sm font-bold text-amber-500 uppercase tracking-wider mb-3">{{ $t('honey_batches.section_reserve_sample') }}</h4>
            <div class="bg-gray-50 dark:bg-dark-bg border border-gray-200 dark:border-gray-800 rounded-2xl p-4 space-y-4">
              <div class="flex items-start space-x-3">
                <input 
                  v-model="form.reserve_sample_taken" 
                  id="reserve_sample_taken"
                  type="checkbox"
                  class="mt-1 h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                />
                <label for="reserve_sample_taken" class="text-sm text-gray-700 dark:text-gray-300">
                  <span class="font-bold block">{{ $t('honey_batches.reserve_sample_taken_label') }}</span>
                </label>
              </div>

              <div v-if="form.reserve_sample_taken" class="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2 animate-scale">
                <div>
                  <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('honey_batches.reserve_sample_date_label') }}</label>
                  <input 
                    v-model="form.reserve_sample_date" 
                    type="date" 
                    required
                    class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm font-mono"
                  />
                </div>

                <div>
                  <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('honey_batches.reserve_sample_id_label') }}</label>
                  <div class="flex space-x-2">
                    <input 
                      v-model="form.reserve_sample_id" 
                      type="text" 
                      required
                      :placeholder="$t('honey_batches.reserve_sample_id_placeholder')"
                      class="flex-1 min-w-0 px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm font-mono"
                    />
                    <button
                      type="button"
                      @click="fetchSuggestion('reserve_sample_id')"
                      class="px-3 py-2 bg-gray-100 hover:bg-gray-200 dark:bg-gray-800 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-200 text-xs font-bold rounded-xl transition duration-150 border border-gray-200 dark:border-gray-700 shrink-0"
                      :title="$t('honey_batches.suggest_btn')"
                    >
                      {{ $t('honey_batches.suggest_btn') }}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Section 6: Notes -->
          <div>
            <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('honey_batches.section_notes') }}</label>
            <textarea 
              v-model="form.notes" 
              :placeholder="$t('honey_batches.notes_placeholder')"
              rows="3"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm"
            ></textarea>
          </div>

        </div>

        <!-- Buttons -->
        <div class="flex justify-end space-x-3 mt-8 border-t border-gray-100 dark:border-dark-border pt-4">
          <button 
            type="button" 
            @click="closeModal" 
            class="px-4 py-2 text-sm font-bold text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
          >
            {{ $t('common.cancel') }}
          </button>
          <button 
            type="submit" 
            class="px-5 py-2.5 bg-primary hover:bg-primary-hover text-white font-extrabold text-sm rounded-xl shadow-md hover-scale"
          >
            {{ $t('common.save') }}
          </button>
        </div>
      </form>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex flex-col items-center justify-center py-20">
      <svg class="animate-spin h-10 w-10 text-primary mb-4" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
      <p class="text-gray-500 dark:text-gray-400 font-bold">{{ $t('honey_batches.loading_batches') }}</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="batches.length === 0" class="glass rounded-3xl p-12 text-center max-w-lg mx-auto border border-dashed border-gray-300 dark:border-gray-700 mt-8">
      <div class="text-4xl mb-4">🍯</div>
      <h3 class="text-lg font-bold text-gray-800 dark:text-white mb-1">{{ $t('honey_batches.empty_title') }}</h3>
      <p class="text-gray-500 dark:text-gray-400 mb-6">{{ $t('honey_batches.empty_desc') }}</p>
      <button @click="openCreateModal" class="px-5 py-2.5 bg-primary hover:bg-primary-hover text-white font-extrabold text-sm rounded-xl shadow-md hover-scale">
        {{ $t('honey_batches.create_first_btn') }}
      </button>
    </div>

    <!-- Batches List (Responsive Table) -->
    <div v-else class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl overflow-hidden shadow-sm">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-800 text-left">
          <thead class="bg-gray-50 dark:bg-dark-bg text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
            <tr>
              <th scope="col" class="px-6 py-4">{{ $t('honey_batches.table_batch_mhd') }}</th>
              <th scope="col" class="px-6 py-4">{{ $t('honey_batches.table_honey_type') }}</th>
              <th scope="col" class="px-6 py-4">{{ $t('honey_batches.table_harvest_date') }}</th>
              <th scope="col" class="px-6 py-4">{{ $t('honey_batches.table_quantity') }}</th>
              <th scope="col" class="px-6 py-4">{{ $t('honey_batches.table_quality') }}</th>
              <th scope="col" class="px-6 py-4">{{ $t('honey_batches.table_dib_label') }}</th>
              <th scope="col" class="px-6 py-4">{{ $t('honey_batches.table_reserve_sample') }}</th>
              <th scope="col" class="px-6 py-4 text-right">{{ $t('common.actions') }}</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200 dark:divide-gray-800 text-sm">
            <tr 
              v-for="b in batches" 
              :key="b.id" 
              class="hover:bg-gray-50 dark:hover:bg-dark-bg/50 transition-colors duration-150"
            >
              <!-- Los-Nr. / MHD -->
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="font-mono font-bold text-gray-900 dark:text-white">
                  {{ b.batch_number || $t('honey_batches.mhd_exemption') }}
                </div>
                <div class="text-xs text-gray-500 dark:text-gray-400 flex items-center space-x-1 mt-0.5">
                  <span>MHD: {{ formatDate(b.best_before_date) }}</span>
                  <span 
                    class="px-1.5 py-0.5 text-[9px] font-bold rounded-full"
                    :class="b.is_exact_date ? 'bg-green-500/10 text-green-600' : 'bg-amber-500/10 text-amber-600'"
                  >
                    {{ b.is_exact_date ? $t('honey_batches.exact_date_badge') : $t('honey_batches.month_year_badge') }}
                  </span>
                </div>
              </td>

              <!-- Sorte -->
              <td class="px-6 py-4 whitespace-nowrap font-semibold text-gray-700 dark:text-gray-300">
                {{ $t('honey_types.' + b.honey_type, b.honey_type) }}
              </td>

              <!-- Erntedatum -->
              <td class="px-6 py-4 whitespace-nowrap font-mono text-xs text-gray-600 dark:text-gray-400">
                {{ formatDate(b.harvest_date) }}
                <div v-if="b.bottling_date" class="text-[10px] text-gray-400 dark:text-gray-500">
                  {{ $t('honey_batches.bottled_prefix', { date: formatDate(b.bottling_date) }) }}
                </div>
              </td>

              <!-- Menge -->
              <td class="px-6 py-4 whitespace-nowrap font-bold text-gray-900 dark:text-white">
                {{ b.quantity_kg.toLocaleString(locale === 'de' ? 'de-DE' : 'en-US') }} kg
              </td>

              <!-- Qualität -->
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex flex-col space-y-1">
                  <!-- Water percent -->
                  <div v-if="b.water_content_percent !== null" class="flex items-center space-x-1">
                    <span class="text-xs text-gray-500 dark:text-gray-400">{{ $t('honey_batches.water_label') }}</span>
                    <span 
                      class="px-2 py-0.5 rounded-full text-xs font-bold"
                      :class="b.water_content_percent <= 18 ? 'bg-green-500/10 text-green-600' : 'bg-red-500/10 text-red-600'"
                    >
                      {{ b.water_content_percent }} %
                    </span>
                  </div>
                  <!-- Heating temp -->
                  <div v-if="b.heating_temperature_celsius !== null" class="text-xs text-gray-500 dark:text-gray-400">
                    {{ $t('honey_batches.heating_label') }} <span class="font-mono text-gray-700 dark:text-gray-300">{{ b.heating_temperature_celsius }} °C</span>
                  </div>
                </div>
              </td>

              <!-- D.I.B. Labels -->
              <td class="px-6 py-4 whitespace-nowrap text-xs">
                <div v-if="b.dib_label_start || b.dib_label_end" class="font-mono text-gray-700 dark:text-gray-300">
                  {{ b.dib_label_start || '?' }} &rarr; {{ b.dib_label_end || '?' }}
                  <div class="text-[10px] text-gray-500 dark:text-gray-400 font-bold mt-0.5">
                    {{ $t('honey_batches.dib_count_suffix', { count: getDIBCount(b.dib_label_start, b.dib_label_end) }) }}
                  </div>
                </div>
                <span v-else class="text-gray-400 dark:text-gray-600 italic">{{ $t('honey_batches.no_dib_data') }}</span>
              </td>

              <!-- Rückstellprobe -->
              <td class="px-6 py-4 whitespace-nowrap">
                <div v-if="b.reserve_sample_taken" class="flex flex-col">
                  <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold bg-amber-500/10 text-amber-600 w-max">
                    {{ $t('honey_batches.reserve_sample_taken_badge') }}
                  </span>
                  <span v-if="b.reserve_sample_id" class="text-[10px] font-mono text-gray-500 dark:text-gray-400 mt-1">
                    ID: {{ b.reserve_sample_id }}
                  </span>
                </div>
                <span v-else class="text-gray-400 dark:text-gray-600 italic">—</span>
              </td>

              <!-- Actions -->
              <td class="px-6 py-4 whitespace-nowrap text-right text-xs font-medium">
                <div class="flex items-center justify-end space-x-2">
                  <button 
                    @click="openEditModal(b)" 
                    class="p-2 text-gray-500 hover:text-primary hover:bg-gray-100 dark:hover:bg-dark-border rounded-xl transition-all duration-150 hover-scale"
                    :title="$t('common.edit')"
                  >
                    <svg class="w-4.5 h-4.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/></svg>
                  </button>
                  <button 
                    @click="deleteBatch(b)" 
                    class="p-2 text-gray-400 hover:text-red-500 hover:bg-red-500/10 rounded-xl transition-all duration-150 hover-scale"
                    :title="$t('common.delete')"
                  >
                    <svg class="w-4.5 h-4.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, reactive, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useApiaryStore } from '../stores/apiary'
import { useConfirmStore } from '../stores/confirm'
import axios from 'axios'

const { t, locale } = useI18n()

const DIB_HONEY_TYPES = {
  specific: [
    'Akazienhonig / Robinienhonig',
    'Edelkastanienhonig',
    'Eukalyptushonig',
    'Fichtenhonig (Fichtenhonigtauhonig)',
    'Heidehonig',
    'Kleehonig',
    'Kornblumenhonig',
    'Lindenhonig',
    'Löwenzahnhonig',
    'Obstblütenhonig',
    'Orangenblütenhonig',
    'Pinienhonig (Pinienhonigtauhonig)',
    'Rapshonig',
    'Sonnenblumenhonig',
    'Tannenhonig (Weißtannenhonigtauhonig)'
  ],
  double: [
    'Tannen-/Fichtenhonig',
    'Tannen-/Edelkastanienhonig',
    'Raps-Klee-Honig'
  ],
  regional: [
    'Waldhonig',
    'Wald- und Blütenhonig',
    'Gebirgsblütenhonig / Bergblütenhonig'
  ],
  unspecific: [
    'Wildblütenhonig'
  ],
  general: [
    'Blütenhonig',
    'Honigtauhonig',
    'Frühjahrsblütenhonig',
    'Frühjahrstrachthonig',
    'Sommerblütenhonig',
    'Sommertrachthonig'
  ]
}

const apiaryStore = useApiaryStore()
const confirmStore = useConfirmStore()

const batches = ref([])
const loading = ref(false)
const showModal = ref(false)
const isEditMode = ref(false)
const editingId = ref(null)

const alertMessage = ref('')
const alertClass = ref('')

const aiDraftText = ref('')
const aiLoading = ref(false)

const form = reactive({
  batch_number: '',
  honey_type: 'Blütenhonig',
  harvest_date: new Date().toISOString().substring(0, 10),
  bottling_date: '',
  quantity_kg: 0,
  water_content_percent: null,
  heating_temperature_celsius: null,
  best_before_date: '',
  is_exact_date: false,
  dib_label_start: '',
  dib_label_end: '',
  reserve_sample_taken: false,
  reserve_sample_date: '',
  reserve_sample_id: '',
  notes: ''
})

const selectedHoneyTypePreset = ref('Blütenhonig')

function syncPresetFromHoneyType() {
  const allPresets = [
    ...DIB_HONEY_TYPES.specific,
    ...DIB_HONEY_TYPES.double,
    ...DIB_HONEY_TYPES.regional,
    ...DIB_HONEY_TYPES.unspecific,
    ...DIB_HONEY_TYPES.general
  ]
  if (allPresets.includes(form.honey_type)) {
    selectedHoneyTypePreset.value = form.honey_type
  } else if (form.honey_type) {
    selectedHoneyTypePreset.value = 'custom'
  } else {
    selectedHoneyTypePreset.value = 'Blütenhonig'
    form.honey_type = 'Blütenhonig'
  }
}

// Watch for changes on the preset dropdown
watch(selectedHoneyTypePreset, (newVal) => {
  if (newVal !== 'custom') {
    form.honey_type = newVal
  } else {
    const allPresets = [
      ...DIB_HONEY_TYPES.specific,
      ...DIB_HONEY_TYPES.double,
      ...DIB_HONEY_TYPES.regional,
      ...DIB_HONEY_TYPES.unspecific,
      ...DIB_HONEY_TYPES.general
    ]
    if (allPresets.includes(form.honey_type)) {
      form.honey_type = ''
    }
  }
})

// Auto-generate Best Before Date (2 years after harvest date)
watch(() => form.harvest_date, (newDate) => {
  if (newDate) {
    const d = new Date(newDate)
    d.setFullYear(d.getFullYear() + 2)
    form.best_before_date = d.toISOString().substring(0, 10)
  }
})

// Auto-fill reserve sample date and suggest ID
watch(() => form.reserve_sample_taken, async (val) => {
  if (val) {
    if (!form.reserve_sample_date) {
      form.reserve_sample_date = form.harvest_date || new Date().toISOString().substring(0, 10)
    }
    if (!form.reserve_sample_id) {
      await fetchSuggestion('reserve_sample_id')
    }
  }
})

onMounted(async () => {
  if (apiaryStore.activeApiaryId) {
    await fetchBatches()
  }
  
  // Check for pending honey draft from AI assistant
  const pending = sessionStorage.getItem('pending_honey_draft')
  if (pending) {
    try {
      const draft = JSON.parse(pending)
      sessionStorage.removeItem('pending_honey_draft')
      
      form.batch_number = draft.batch_number || ''
      form.honey_type = draft.honey_type || 'Blütenhonig'
      form.harvest_date = draft.harvest_date ? draft.harvest_date.substring(0, 10) : new Date().toISOString().substring(0, 10)
      form.bottling_date = draft.bottling_date ? draft.bottling_date.substring(0, 10) : ''
      form.quantity_kg = draft.quantity_kg || 0
      form.water_content_percent = draft.water_content_percent
      form.heating_temperature_celsius = draft.heating_temperature_celsius
      form.best_before_date = draft.best_before_date ? draft.best_before_date.substring(0, 10) : ''
      form.is_exact_date = draft.is_exact_date || false
      form.dib_label_start = draft.dib_label_start || ''
      form.dib_label_end = draft.dib_label_end || ''
      form.reserve_sample_taken = draft.reserve_sample_taken || false
      form.reserve_sample_date = draft.reserve_sample_date ? draft.reserve_sample_date.substring(0, 10) : ''
      form.reserve_sample_id = draft.reserve_sample_id || ''
      form.notes = draft.notes || ''
      
      syncPresetFromHoneyType()
      
      isEditMode.value = false
      editingId.value = null
      showModal.value = true
      showAlert(t('honey_batches.ai_draft_loaded'), 'success')
    } catch (e) {
      console.error('Error loading pending honey draft:', e)
    }
  }
})

async function fetchBatches() {
  loading.value = true
  try {
    const response = await axios.get('/api/honey-batches', {
      params: { apiary_id: apiaryStore.activeApiaryId }
    })
    batches.value = response.data
  } catch (err) {
    console.error('Fetch honey batches error:', err)
    showAlert(t('honey_batches.error_fetch'), 'error')
  } finally {
    loading.value = false
  }
}

async function fetchSuggestion(key) {
  try {
    const res = await axios.get('/api/honey-batches/suggest-number', { params: { key } })
    if (res.data.suggested_value) {
      if (key === 'batch_number') {
        form.batch_number = res.data.suggested_value
      } else if (key === 'reserve_sample_id') {
        form.reserve_sample_id = res.data.suggested_value
      }
    }
  } catch (err) {
    console.error(`Error fetching suggestion for ${key}:`, err)
  }
}

function openCreateModal() {
  isEditMode.value = false
  editingId.value = null
  
  // reset form
  form.batch_number = ''
  form.honey_type = 'Blütenhonig'
  form.harvest_date = new Date().toISOString().substring(0, 10)
  form.bottling_date = ''
  form.quantity_kg = 0
  form.water_content_percent = null
  form.heating_temperature_celsius = null
  form.is_exact_date = false
  form.dib_label_start = ''
  form.dib_label_end = ''
  form.reserve_sample_taken = false
  form.reserve_sample_date = ''
  form.reserve_sample_id = ''
  form.notes = ''
  
  syncPresetFromHoneyType()
  
  // Suggest next batch number
  fetchSuggestion('batch_number')
  
  // initial watch will trigger BB date
  showModal.value = true
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function openEditModal(b) {
  isEditMode.value = true
  editingId.value = b.id
  
  form.batch_number = b.batch_number || ''
  form.honey_type = b.honey_type
  form.harvest_date = b.harvest_date ? b.harvest_date.substring(0, 10) : ''
  form.bottling_date = b.bottling_date ? b.bottling_date.substring(0, 10) : ''
  form.quantity_kg = b.quantity_kg
  form.water_content_percent = b.water_content_percent
  form.heating_temperature_celsius = b.heating_temperature_celsius
  form.best_before_date = b.best_before_date ? b.best_before_date.substring(0, 10) : ''
  form.is_exact_date = b.is_exact_date
  form.dib_label_start = b.dib_label_start || ''
  form.dib_label_end = b.dib_label_end || ''
  form.reserve_sample_taken = b.reserve_sample_taken
  form.reserve_sample_date = b.reserve_sample_date ? b.reserve_sample_date.substring(0, 10) : ''
  form.reserve_sample_id = b.reserve_sample_id || ''
  form.notes = b.notes || ''
  
  syncPresetFromHoneyType()
  
  showModal.value = true
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function closeModal() {
  showModal.value = false
}

async function submitForm() {
  if (!form.honey_type.trim()) return
  
  // Custom checks
  if (!form.is_exact_date && (!form.batch_number || !form.batch_number.trim())) {
    showAlert(t('honey_batches.error_batch_number_required'), 'error')
    return
  }

  try {
    const payload = {
      batch_number: form.batch_number.trim() || null,
      honey_type: form.honey_type.trim(),
      harvest_date: form.harvest_date,
      bottling_date: form.bottling_date || null,
      quantity_kg: parseFloat(form.quantity_kg),
      water_content_percent: form.water_content_percent !== null ? parseFloat(form.water_content_percent) : null,
      heating_temperature_celsius: form.heating_temperature_celsius !== null ? parseFloat(form.heating_temperature_celsius) : null,
      best_before_date: form.best_before_date,
      is_exact_date: form.is_exact_date,
      dib_label_start: form.dib_label_start.trim() || null,
      dib_label_end: form.dib_label_end.trim() || null,
      reserve_sample_taken: form.reserve_sample_taken,
      reserve_sample_date: form.reserve_sample_taken ? form.reserve_sample_date : null,
      reserve_sample_id: form.reserve_sample_taken ? form.reserve_sample_id.trim() || null : null,
      notes: form.notes.trim() || null
    }

    if (isEditMode.value) {
      await axios.put(`/api/honey-batches/${editingId.value}`, payload)
      showAlert(t('honey_batches.success_update'), 'success')
    } else {
      await axios.post('/api/honey-batches', payload, {
        params: { apiary_id: apiaryStore.activeApiaryId }
      })
      showAlert(t('honey_batches.success_create'), 'success')
    }
    
    showModal.value = false
    await fetchBatches()
  } catch (err) {
    console.error('Submit honey batch error:', err)
    showAlert(err.response?.data?.detail || t('honey_batches.error_save'), 'error')
  }
}

async function deleteBatch(b) {
  const identifier = b.batch_number || `${locale.value === 'de' ? 'MHD' : 'BBD'}: ${formatDate(b.best_before_date)}`
  const confirmed = await confirmStore.ask({
    title: t('honey_batches.delete_title'),
    message: t('honey_batches.delete_confirm', { identifier }),
    type: 'danger',
    confirmText: t('honey_batches.confirm_delete_btn')
  })
  if (!confirmed) return
  try {
    await axios.delete(`/api/honey-batches/${b.id}`)
    showAlert(t('honey_batches.success_delete'), 'success')
    await fetchBatches()
  } catch (err) {
    console.error('Delete honey batch error:', err)
    showAlert(err.response?.data?.detail || t('honey_batches.error_delete'), 'error')
  }
}

async function generateAIDraft() {
  if (!aiDraftText.value.trim()) return
  aiLoading.value = true
  try {
    const response = await axios.post('/api/ai/draft-honey', {
      text: aiDraftText.value.trim()
    })
    
    const draft = response.data.draft
    if (draft) {
      // Pre-fill the form using the draft data
      form.batch_number = draft.batch_number || ''
      form.honey_type = draft.honey_type || 'Blütenhonig'
      form.harvest_date = draft.harvest_date ? draft.harvest_date.substring(0, 10) : new Date().toISOString().substring(0, 10)
      form.bottling_date = draft.bottling_date ? draft.bottling_date.substring(0, 10) : ''
      form.quantity_kg = draft.quantity_kg || 0
      form.water_content_percent = draft.water_content_percent
      form.heating_temperature_celsius = draft.heating_temperature_celsius
      form.best_before_date = draft.best_before_date ? draft.best_before_date.substring(0, 10) : ''
      form.is_exact_date = draft.is_exact_date || false
      form.dib_label_start = draft.dib_label_start || ''
      form.dib_label_end = draft.dib_label_end || ''
      form.reserve_sample_taken = draft.reserve_sample_taken || false
      form.reserve_sample_date = draft.reserve_sample_date ? draft.reserve_sample_date.substring(0, 10) : ''
      form.reserve_sample_id = draft.reserve_sample_id || ''
      form.notes = draft.notes || ''
      
      syncPresetFromHoneyType()
      
      isEditMode.value = false
      editingId.value = null
      showModal.value = true
      aiDraftText.value = ''
      showAlert(t('honey_batches.ai_draft_applied'), 'success')
    } else {
      showAlert(t('honey_batches.ai_draft_empty'), 'error')
    }
  } catch (err) {
    console.error('AI Draft generation error:', err)
    showAlert(t('honey_batches.ai_draft_error'), 'error')
  } finally {
    aiLoading.value = false
  }
}

async function exportCSV() {
  if (!apiaryStore.activeApiaryId) return
  try {
    // We navigate to the export endpoint directly to trigger download
    const url = `/api/honey-batches/export/csv?apiary_id=${apiaryStore.activeApiaryId}`
    const token = localStorage.getItem('token')
    
    // Create an anchor element, fetch file with authentication or request download
    // Since backend requires auth, we can fetch it via axios with blob response
    const response = await axios.get(url, { responseType: 'blob' })
    const blob = new Blob([response.data], { type: 'text/csv;charset=utf-8;' })
    
    const link = document.createElement('a')
    const urlBlob = URL.createObjectURL(blob)
    
    // Get filename from Content-Disposition header if possible
    let filename = `honigbuch_${new Date().toISOString().slice(0,10)}.csv`
    const disposition = response.headers['content-disposition']
    if (disposition && disposition.indexOf('attachment') !== -1) {
      const filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/
      const matches = filenameRegex.exec(disposition)
      if (matches != null && matches[1]) { 
        filename = matches[1].replace(/['"]/g, '')
      }
    }
    
    link.setAttribute('href', urlBlob)
    link.setAttribute('download', filename)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    showAlert(t('honey_batches.success_export'), 'success')
  } catch (err) {
    console.error('CSV export error:', err)
    showAlert(t('honey_batches.error_export'), 'error')
  }
}

function formatDate(dStr) {
  if (!dStr) return ''
  const parts = dStr.split('-')
  if (parts.length === 3) {
    return locale.value === 'de'
      ? `${parts[2]}.${parts[1]}.${parts[0]}`
      : `${parts[1]}/${parts[2]}/${parts[0]}`
  }
  return dStr
}

function getDIBCount(start, end) {
  if (!start || !end) return 0
  const sNum = parseInt(start.replace(/\D/g, ''))
  const eNum = parseInt(end.replace(/\D/g, ''))
  if (isNaN(sNum) || isNaN(eNum)) return 0
  return Math.max(0, eNum - sNum + 1)
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
