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
        <h1 class="text-3xl font-extrabold text-gray-900 dark:text-white tracking-tight">❤️ {{ $t('treatments.title') }}</h1>
        <p class="text-gray-500 dark:text-gray-400 mt-1">{{ $t('treatments.subtitle') }}</p>
      </div>
      <div class="flex items-center gap-3 self-end sm:self-auto shrink-0">
        <button 
          v-if="apiaryStore.activeApiaryId"
          @click="exportCSV" 
          class="px-4 py-2.5 bg-gray-100 hover:bg-gray-205 dark:bg-gray-800 dark:hover:bg-gray-700 border border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-200 font-bold text-sm rounded-xl transition duration-150 flex items-center justify-center space-x-2 hover-scale"
        >
          <span>{{ $t('treatments.export_csv_btn') }}</span>
        </button>
        <button 
          v-if="apiaryStore.activeApiaryId"
          @click="openCreateModal" 
          class="px-5 py-2.5 bg-primary hover:bg-primary-hover text-white font-extrabold text-sm rounded-xl shadow-md shadow-primary/20 hover-scale flex items-center justify-center space-x-2"
        >
          <span>{{ $t('treatments.new_treatment') }}</span>
        </button>
      </div>
    </div>

    <!-- Alert / Toast Messages -->
    <div v-if="alertMessage" class="mb-6 p-4 rounded-xl text-sm flex items-start space-x-2" :class="alertClass">
      <svg class="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
      <span>{{ alertMessage }}</span>
    </div>

    <div v-if="!apiaryStore.activeApiaryId" class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-8 text-center shadow-sm">
      <span class="text-4xl block mb-2">🐝</span>
      <h3 class="text-lg font-bold text-gray-900 dark:text-white">{{ $t('treatments.error_no_apiary') }}</h3>
    </div>

    <div v-else class="space-y-6">
      
      <!-- Filter Bar -->
      <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-6 shadow-sm flex flex-col md:flex-row gap-4 items-end animate-scale">
        <div class="flex-1 w-full">
          <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('treatments.filter_location') }}</label>
          <select 
            v-model="filters.locationId" 
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-sm cursor-pointer focus:outline-none focus:ring-2 focus:ring-primary"
            @change="onLocationFilterChange"
          >
            <option value="">{{ $t('treatments.all_locations') }}</option>
            <option v-for="loc in locations" :key="loc.id" :value="loc.id">{{ loc.name }}</option>
          </select>
        </div>

        <div class="flex-1 w-full">
          <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('treatments.filter_hive') }}</label>
          <select 
            v-model="filters.hiveId" 
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-sm cursor-pointer focus:outline-none focus:ring-2 focus:ring-primary"
            @change="fetchTreatments"
          >
            <option value="">{{ $t('treatments.all_hives') }}</option>
            <option v-for="hive in filteredHivesForFilter" :key="hive.id" :value="hive.id">{{ hive.name }}</option>
          </select>
        </div>

        <div class="flex-1 w-full">
          <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('treatments.filter_start_date') }}</label>
          <input 
            v-model="filters.startDate" 
            type="date" 
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-sm font-mono focus:outline-none focus:ring-2 focus:ring-primary"
            @change="fetchTreatments"
          />
        </div>

        <div class="flex-1 w-full">
          <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('treatments.filter_end_date') }}</label>
          <input 
            v-model="filters.endDate" 
            type="date" 
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-sm font-mono focus:outline-none focus:ring-2 focus:ring-primary"
            @change="fetchTreatments"
          />
        </div>

        <button 
          @click="resetFilters" 
          class="px-4 py-2 bg-gray-100 hover:bg-gray-200 dark:bg-gray-800 dark:hover:bg-gray-700 border border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-200 text-xs font-bold rounded-xl transition duration-150 w-full md:w-auto h-[38px] flex items-center justify-center hover-scale shrink-0"
        >
          {{ $t('treatments.filter_reset') }}
        </button>
      </div>

      <!-- Treatments Ledger Table/Cards -->
      <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl overflow-hidden shadow-sm">
        <div v-if="loadingTreatments" class="flex flex-col items-center justify-center py-20">
          <svg class="animate-spin h-8 w-8 text-primary mb-3" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
          <span class="text-xs text-gray-400 font-bold">{{ $t('treatments.loading') }}</span>
        </div>

        <div v-else-if="treatments.length === 0" class="flex flex-col items-center justify-center py-20 text-center px-4">
          <span class="text-4xl mb-3">❤️</span>
          <h3 class="text-base font-bold text-gray-900 dark:text-white">{{ $t('treatments.empty_title') }}</h3>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1 max-w-sm">{{ $t('treatments.empty_desc') }}</p>
        </div>

        <div v-else class="overflow-x-auto">
          <!-- Desktop Table view -->
          <table class="w-full text-left border-collapse hidden md:table">
            <thead>
              <tr class="bg-gray-50 dark:bg-dark-bg text-gray-500 dark:text-gray-400 text-[10px] font-bold uppercase tracking-wider border-b border-gray-100 dark:border-dark-border">
                <th class="px-6 py-4">{{ $t('treatments.table_date') }}</th>
                <th class="px-6 py-4">{{ $t('treatments.table_hive') }}</th>
                <th class="px-6 py-4">{{ $t('treatments.table_location') }}</th>
                <th class="px-6 py-4">{{ $t('treatments.table_method') }}</th>
                <th class="px-6 py-4 text-right">{{ $t('treatments.table_amount') }}</th>
                <th class="px-6 py-4">{{ $t('treatments.table_app_type') }}</th>
                <th class="px-6 py-4">{{ $t('treatments.table_images') }}</th>
                <th class="px-6 py-4">{{ $t('treatments.table_notes') }}</th>
                <th class="px-6 py-4 text-right">{{ $t('common.actions') }}</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100 dark:divide-dark-border text-sm">
              <tr 
                v-for="t in treatments" 
                :key="t.id" 
                class="hover:bg-gray-50/50 dark:hover:bg-dark-bg/30 transition-colors duration-150"
              >
                <td class="px-6 py-4 font-mono font-bold text-gray-900 dark:text-white shrink-0">
                  {{ formatDate(t.date) }}
                </td>
                <td class="px-6 py-4 font-bold text-primary">
                  {{ t.hive?.name || $t('dashboard.unknown_hive') }}
                </td>
                <td class="px-6 py-4 text-gray-600 dark:text-gray-300">
                  📍 {{ t.hive?.location?.name || '-' }}
                </td>
                <td class="px-6 py-4 text-gray-900 dark:text-white font-semibold">
                  {{ t.treatment_method?.name || '-' }}
                </td>
                <td class="px-6 py-4 text-right font-mono font-bold text-amber-600 dark:text-amber-500">
                  {{ t.amount }} {{ t.treatment_method?.unit }}
                </td>
                <td class="px-6 py-4 text-gray-600 dark:text-gray-300 font-medium">
                  {{ t.application_type?.name || '-' }}
                </td>
                <td class="px-6 py-4">
                  <div class="flex gap-1.5 overflow-hidden max-w-[120px]">
                    <div 
                      v-for="img in t.images" 
                      :key="img.id" 
                      @click="openLightbox(`/uploads/${img.image_path}`)"
                      class="w-8 h-8 rounded-lg overflow-hidden border border-gray-200 dark:border-gray-700 cursor-pointer hover:opacity-80 shrink-0"
                    >
                      <img :src="`/uploads/${img.thumbnail_path || img.image_path}`" alt="Thumbnail" class="w-full h-full object-cover" />
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4 max-w-[200px] truncate text-gray-500 dark:text-gray-400" :title="t.notes">
                  {{ t.notes || '-' }}
                </td>
                <td class="px-6 py-4 text-right space-x-1.5 whitespace-nowrap">
                  <button 
                    @click="openEditModal(t)" 
                    class="p-1.5 text-gray-500 hover:text-primary hover:bg-gray-100 dark:hover:bg-dark-border rounded-lg transition-all duration-150 inline-flex hover-scale"
                    :title="$t('common.edit')"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/></svg>
                  </button>
                  <button 
                    @click="deleteTreatment(t)" 
                    class="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-500/10 rounded-lg transition-all duration-150 inline-flex hover-scale"
                    :title="$t('common.delete')"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>

          <!-- Mobile Cards list view -->
          <div class="grid grid-cols-1 divide-y divide-gray-100 dark:divide-dark-border md:hidden">
            <div 
              v-for="t in treatments" 
              :key="t.id" 
              class="p-4 space-y-3"
            >
              <div class="flex justify-between items-center">
                <span class="font-mono text-xs text-gray-500 dark:text-gray-400">{{ formatDate(t.date) }}</span>
                <span class="font-mono font-bold text-amber-600 dark:text-amber-500">{{ t.amount }} {{ t.treatment_method?.unit }}</span>
              </div>
              <div class="flex justify-between items-start">
                <div>
                  <h4 class="font-bold text-primary text-sm">{{ t.hive?.name || $t('dashboard.unknown_hive') }}</h4>
                  <p class="text-xs text-gray-600 dark:text-gray-300">📍 {{ t.hive?.location?.name || '-' }}</p>
                </div>
                <div class="flex flex-col items-end gap-1">
                  <div class="px-2.5 py-1 bg-gray-100 dark:bg-dark-bg text-gray-800 dark:text-gray-200 text-xs rounded-lg font-semibold">
                    {{ t.treatment_method?.name || '-' }}
                  </div>
                  <div v-if="t.application_type" class="text-[10px] text-gray-500 dark:text-gray-400 font-medium">
                    {{ t.application_type.name }}
                  </div>
                </div>
              </div>
              
              <p v-if="t.notes" class="text-xs text-gray-500 dark:text-gray-400 bg-gray-50 dark:bg-dark-bg/40 p-2.5 rounded-xl border border-gray-100 dark:border-dark-border/40">
                {{ t.notes }}
              </p>

              <!-- Thumbnails -->
              <div v-if="t.images && t.images.length > 0" class="flex gap-1.5 pt-1 overflow-x-auto">
                <div 
                  v-for="img in t.images" 
                  :key="img.id" 
                  @click="openLightbox(`/uploads/${img.image_path}`)"
                  class="w-10 h-10 rounded-lg overflow-hidden border border-gray-200 dark:border-gray-700 cursor-pointer hover:opacity-80 shrink-0"
                >
                  <img :src="`/uploads/${img.thumbnail_path || img.image_path}`" alt="Thumbnail" class="w-full h-full object-cover" />
                </div>
              </div>

              <div class="flex justify-end gap-3 pt-2">
                <button 
                  @click="openEditModal(t)" 
                  class="px-3 py-1.5 border border-gray-200 dark:border-gray-700 rounded-xl text-xs font-semibold hover:bg-gray-100 dark:hover:bg-dark-border text-gray-700 dark:text-gray-300 flex items-center gap-1"
                >
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/></svg>
                  <span>{{ $t('common.edit') }}</span>
                </button>
                <button 
                  @click="deleteTreatment(t)" 
                  class="px-3 py-1.5 bg-red-500/10 hover:bg-red-500/20 text-red-600 dark:text-red-400 rounded-xl text-xs font-semibold flex items-center gap-1"
                >
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                  <span>{{ $t('common.delete') }}</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <Teleport to="body">
      <Transition name="modal-fade">
        <div 
          v-if="showModal" 
          class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm overflow-y-auto"
          role="dialog"
          aria-modal="true"
          @click.self="closeModal"
        >
          <div class="bg-white dark:bg-dark-card rounded-3xl shadow-2xl max-w-2xl w-full my-8 flex flex-col max-h-[calc(100vh-4rem)] overflow-hidden animate-scale">
            <!-- Header -->
            <div class="flex justify-between items-center p-6 border-b border-gray-100 dark:border-dark-border">
              <h3 class="text-xl font-bold text-gray-900 dark:text-white">
                {{ isEditMode ? $t('treatments.edit_treatment') : $t('treatments.new_treatment') }}
              </h3>
              <button @click="closeModal" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
              </button>
            </div>

            <!-- Form Body -->
            <form @submit.prevent="submitForm" class="p-6 space-y-4 overflow-y-auto flex-1">
              
              <!-- Hive selector -->
              <div>
                <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('treatments.form_hive') }}</label>
                <select 
                  v-model="form.hiveId" 
                  required
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm cursor-pointer"
                >
                  <option value="">{{ $t('treatments.select_hive') }}</option>
                  <option v-for="h in hives" :key="h.id" :value="h.id">{{ h.name }} (📍 {{ h.location?.name || '-' }})</option>
                </select>
              </div>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <!-- Date selector -->
                <div>
                  <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('treatments.form_date') }}</label>
                  <input 
                    v-model="form.date" 
                    type="date" 
                    required 
                    class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm"
                  />
                </div>

                <!-- Method selector -->
                <div>
                  <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('treatments.form_method') }}</label>
                  <select 
                    v-model="form.treatmentMethodId" 
                    required
                    class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm cursor-pointer"
                  >
                    <option value="">{{ $t('treatments.select_method') }}</option>
                    <option v-for="m in treatmentMethods" :key="m.id" :value="m.id">{{ m.name }}</option>
                  </select>
                </div>
              </div>

              <!-- Quantity Amount -->
              <div>
                <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('treatments.form_amount') }}</label>
                <div class="relative flex items-center">
                  <input 
                    v-model.number="form.amount" 
                    type="number" 
                    step="any"
                    min="0.01"
                    required 
                    class="w-full pl-3 pr-16 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm font-mono"
                  />
                  <div class="absolute right-3 text-xs font-extrabold text-gray-400 dark:text-gray-500 select-none">
                    {{ selectedMethodUnit }}
                  </div>
                </div>
              </div>

              <!-- Application Method -->
              <div>
                <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('treatments.form_app_type') }}</label>
                <select 
                  v-model="form.applicationTypeId" 
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm cursor-pointer"
                >
                  <option value="">{{ $t('treatments.select_app_type') }}</option>
                  <option v-for="app in treatmentApplicationTypes" :key="app.id" :value="app.id">{{ app.name }}</option>
                </select>
              </div>

              <!-- Notes -->
              <div>
                <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('treatments.form_notes') }}</label>
                <textarea 
                  v-model="form.notes" 
                  :placeholder="$t('treatments.form_notes_placeholder')"
                  rows="3"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm resize-y"
                />
              </div>

              <!-- Image Uploader -->
              <div class="space-y-2">
                <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('treatments.table_images') }}</label>
                <div 
                  class="border-2 border-dashed rounded-2xl p-4 text-center cursor-pointer transition-all duration-200"
                  :class="dragOver ? 'border-primary bg-primary/5' : 'border-gray-300 dark:border-gray-700 bg-gray-50/50 dark:bg-dark-bg/30 hover:border-primary/50'"
                  @click="triggerFileInput"
                  @dragover.prevent="dragOver = true"
                  @dragleave.prevent="dragOver = false"
                  @drop.prevent="onFileDrop"
                >
                  <input 
                    ref="fileInputRef" 
                    type="file" 
                    multiple 
                    accept="image/*"
                    class="hidden" 
                    @change="onFileSelect" 
                  />
                  <div class="text-2xl mb-1">📸</div>
                  <p class="text-xs font-bold text-gray-700 dark:text-gray-300">{{ $t('treatments.drag_drop_area') }}</p>
                  <p class="text-[10px] text-gray-400 mt-0.5">{{ $t('treatments.drag_drop_hint') }}</p>
                </div>

                <div class="grid grid-cols-2 gap-2">
                  <button 
                    type="button"
                    @click="triggerFileInput"
                    class="px-3 py-2 border border-gray-200 dark:border-dark-border text-xs font-bold text-gray-600 dark:text-gray-300 rounded-xl hover:bg-gray-50 dark:hover:bg-dark-border hover:text-primary dark:hover:text-primary transition-all flex items-center justify-center gap-1.5"
                  >
                    📥 {{ $t('treatments.choose_file') }}
                  </button>
                  <button 
                    type="button"
                    @click="triggerCameraInput"
                    class="px-3 py-2 border border-gray-200 dark:border-dark-border text-xs font-bold text-gray-600 dark:text-gray-300 rounded-xl hover:bg-gray-50 dark:hover:bg-dark-border hover:text-primary dark:hover:text-primary transition-all flex items-center justify-center gap-1.5"
                  >
                    📷 {{ $t('treatments.take_photo') }}
                  </button>
                  <input 
                    ref="cameraInputRef" 
                    type="file" 
                    accept="image/*" 
                    capture="environment" 
                    class="hidden" 
                    @change="onFileSelect" 
                  />
                </div>

                <!-- Preview list -->
                <div v-if="treatmentFiles.length > 0" class="grid grid-cols-4 gap-3 mt-3">
                  <div 
                    v-for="(img, idx) in treatmentFiles" 
                    :key="idx" 
                    class="relative aspect-square rounded-2xl overflow-hidden border border-gray-200 dark:border-gray-700 group bg-gray-50 dark:bg-dark-card"
                  >
                    <img 
                      :src="img.isExisting ? `/uploads/${img.thumbnail_path || img.image_path}` : img.previewUrl" 
                      alt="Preview" 
                      class="w-full h-full object-cover" 
                    />
                    <button 
                      type="button"
                      @click="removeFile(idx)"
                      class="absolute top-1 right-1 p-1 bg-red-500 hover:bg-red-650 text-white rounded-full transition-opacity opacity-100 md:opacity-0 group-hover:opacity-100 flex items-center justify-center shadow-md cursor-pointer"
                    >
                      <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
                    </button>
                  </div>
                </div>
              </div>

              <!-- Action buttons -->
              <div class="flex justify-end space-x-3 pt-4 border-t border-gray-100 dark:border-dark-border">
                <button 
                  type="button" 
                  @click="closeModal" 
                  class="px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-xl text-sm font-semibold hover:bg-gray-100 dark:hover:bg-dark-border text-gray-700 dark:text-gray-300"
                >
                  {{ $t('common.cancel') }}
                </button>
                <button 
                  type="submit" 
                  class="px-6 py-2 bg-primary hover:bg-primary-hover text-white text-sm font-bold rounded-xl shadow-md hover-scale"
                  :disabled="submitting"
                >
                  {{ submitting ? $t('common.loading') : $t('common.save') }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Lightbox Modal -->
    <Teleport to="body">
      <Transition name="fade">
        <div 
          v-if="lightboxUrl" 
          @click="lightboxUrl = ''"
          class="fixed inset-0 z-50 bg-black/85 backdrop-blur-md flex items-center justify-center p-4 cursor-pointer"
        >
          <img :src="lightboxUrl" alt="Lightbox Preview" class="max-w-full max-h-[92vh] object-contain rounded-xl shadow-2xl animate-scale" />
          <button @click="lightboxUrl = ''" class="absolute top-5 right-5 text-white/80 hover:text-white p-2 hover:bg-white/10 rounded-full cursor-pointer">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>
      </Transition>
    </Teleport>

  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import axios from 'axios'
import { useApiaryStore } from '../stores/apiary'
import { useConfirmStore } from '../stores/confirm'
import { useErrorStore } from '../stores/error'

const { t } = useI18n()
const apiaryStore = useApiaryStore()
const confirmStore = useConfirmStore()
const errorStore = useErrorStore()

// State
const treatments = ref([])
const hives = ref([])
const locations = ref([])
const treatmentMethods = ref([])
const treatmentApplicationTypes = ref([])

const loadingTreatments = ref(false)
const submitting = ref(false)
const dragOver = ref(false)
const showModal = ref(false)
const isEditMode = ref(false)
const editingId = ref(null)

const fileInputRef = ref(null)
const cameraInputRef = ref(null)
const treatmentFiles = ref([])
const lightboxUrl = ref('')

const alertMessage = ref('')
const alertClass = ref('')

const filters = reactive({
  locationId: '',
  hiveId: '',
  startDate: '',
  endDate: ''
})

const form = reactive({
  hiveId: '',
  treatmentMethodId: '',
  applicationTypeId: '',
  date: '',
  amount: '',
  notes: ''
})

// Hives filtered by Standort selector inside the filters bar
const filteredHivesForFilter = computed(() => {
  if (!filters.locationId) return hives.value
  return hives.value.filter(h => h.location_id === filters.locationId)
})

// Dynamic Unit tag in the form
const selectedMethodUnit = computed(() => {
  if (!form.treatmentMethodId) return ''
  const m = treatmentMethods.value.find(x => x.id === form.treatmentMethodId)
  return m ? m.unit : ''
})

// Methods
async function fetchTreatments() {
  if (!apiaryStore.activeApiaryId) return
  loadingTreatments.value = true
  try {
    const params = { apiary_id: apiaryStore.activeApiaryId }
    if (filters.hiveId) params.hive_id = filters.hiveId
    if (filters.locationId) params.location_id = filters.locationId
    if (filters.startDate) params.start_date = filters.startDate
    if (filters.endDate) params.end_date = filters.endDate

    const res = await axios.get('/api/treatments', { params })
    treatments.value = res.data
  } catch (err) {
    console.error('Fetch treatments failed:', err)
    showAlert(t('treatments.error_fetch'), 'error')
  } finally {
    loadingTreatments.value = false
  }
}

async function fetchLocations() {
  if (!apiaryStore.activeApiaryId) return
  try {
    const res = await axios.get('/api/locations', {
      params: { apiary_id: apiaryStore.activeApiaryId }
    })
    locations.value = res.data
  } catch (err) {
    console.error('Fetch locations failed:', err)
  }
}

async function fetchHives() {
  if (!apiaryStore.activeApiaryId) return
  try {
    const res = await axios.get('/api/hives', {
      params: { apiary_id: apiaryStore.activeApiaryId }
    })
    hives.value = res.data
  } catch (err) {
    console.error('Fetch hives failed:', err)
  }
}

async function fetchTreatmentMethods() {
  try {
    const res = await axios.get('/api/treatments/methods')
    treatmentMethods.value = res.data
  } catch (err) {
    console.error('Fetch methods failed:', err)
  }
}

async function fetchTreatmentApplicationTypes() {
  try {
    const res = await axios.get('/api/treatments/application-types')
    treatmentApplicationTypes.value = res.data
  } catch (err) {
    console.error('Fetch application types failed:', err)
  }
}

async function exportCSV() {
  if (!apiaryStore.activeApiaryId) return
  try {
    const params = { apiary_id: apiaryStore.activeApiaryId }
    if (filters.hiveId) params.hive_id = filters.hiveId
    if (filters.locationId) params.location_id = filters.locationId
    if (filters.startDate) params.start_date = filters.startDate
    if (filters.endDate) params.end_date = filters.endDate

    const response = await axios.get('/api/treatments/export/csv', {
      params,
      responseType: 'blob'
    })

    const blob = new Blob([response.data], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    
    let filename = `behandlungen_${new Date().toISOString().slice(0, 10)}.csv`
    link.setAttribute('download', filename)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } catch (err) {
    console.error('CSV export failed:', err)
    showAlert(t('treatments.error_fetch'), 'error')
  }
}

function onLocationFilterChange() {
  // Reset hive selector if the currently selected hive is not in the newly selected location
  if (filters.locationId && filters.hiveId) {
    const h = hives.value.find(x => x.id === filters.hiveId)
    if (h && h.location_id !== filters.locationId) {
      filters.hiveId = ''
    }
  }
  fetchTreatments()
}

function resetFilters() {
  filters.locationId = ''
  filters.hiveId = ''
  filters.startDate = ''
  filters.endDate = ''
  fetchTreatments()
}

// Helpers
function formatDate(dStr) {
  if (!dStr) return ''
  // Format YYYY-MM-DD to German local DD.MM.YYYY
  const parts = dStr.split('-')
  if (parts.length === 3) {
    return `${parts[2]}.${parts[1]}.${parts[0]}`
  }
  return dStr
}

function getTodayString() {
  const d = new Date()
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

// Modals
function openCreateModal() {
  isEditMode.value = false
  editingId.value = null
  
  form.hiveId = filters.hiveId || ''
  form.treatmentMethodId = ''
  form.applicationTypeId = ''
  form.date = getTodayString()
  form.amount = ''
  form.notes = ''
  
  clearFiles()
  showModal.value = true
}

function openEditModal(tRecord) {
  isEditMode.value = true
  editingId.value = tRecord.id
  
  form.hiveId = tRecord.hive_id
  form.treatmentMethodId = tRecord.treatment_method_id
  form.applicationTypeId = tRecord.application_type_id || ''
  form.date = tRecord.date
  form.amount = tRecord.amount
  form.notes = tRecord.notes || ''
  
  clearFiles()
  if (tRecord.images && tRecord.images.length > 0) {
    treatmentFiles.value = tRecord.images.map(img => ({
      ...img,
      isExisting: true
    }))
  }
  
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  clearFiles()
}

function clearFiles() {
  treatmentFiles.value.forEach(img => {
    if (!img.isExisting && img.previewUrl) {
      URL.revokeObjectURL(img.previewUrl)
    }
  })
  treatmentFiles.value = []
}

// Save Submit Form
async function submitForm() {
  if (!form.hiveId || !form.treatmentMethodId || !form.date || !form.amount) return
  submitting.value = true
  try {
    const payload = {
      hive_id: form.hiveId,
      treatment_method_id: form.treatmentMethodId,
      application_type_id: form.applicationTypeId || null,
      date: form.date,
      amount: parseFloat(form.amount),
      notes: form.notes.trim() || null
    }

    let res
    if (isEditMode.value) {
      res = await axios.put(`/api/treatments/${editingId.value}`, payload)
      showAlert(t('treatments.success_update'), 'success')
    } else {
      res = await axios.post('/api/treatments', payload)
      showAlert(t('treatments.success_create'), 'success')
    }

    // Upload newly selected images
    const tId = res.data?.id || editingId.value
    const uploads = treatmentFiles.value.filter(f => !f.isExisting)
    for (const uf of uploads) {
      const fd = new FormData()
      fd.append('file', uf.file)
      await axios.post(`/api/treatments/${tId}/images`, fd, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
    }

    showModal.value = false
    await fetchTreatments()
  } catch (err) {
    console.error('Submit treatment failed:', err)
    const detail = err.response?.data?.detail || t('treatments.error_save')
    errorStore.showError(detail, err, t('common.save'))
  } finally {
    submitting.value = false
  }
}

async function deleteTreatment(tRecord) {
  const confirmed = await confirmStore.ask({
    title: t('treatments.delete_treatment'),
    message: t('treatments.delete_confirm'),
    type: 'danger',
    confirmText: t('treatments.delete_btn_confirm')
  })
  if (!confirmed) return
  try {
    await axios.delete(`/api/treatments/${tRecord.id}`)
    showAlert(t('treatments.success_delete'), 'success')
    await fetchTreatments()
  } catch (err) {
    console.error('Delete treatment failed:', err)
    showAlert(err.response?.data?.detail || t('treatments.error_delete'), 'error')
  }
}

// Uploader files handling
function triggerFileInput() {
  fileInputRef.value?.click()
}

function triggerCameraInput() {
  cameraInputRef.value?.click()
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

function handleFilesAdd(files) {
  const allowed = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
  const currentCount = treatmentFiles.value.length
  let added = 0
  
  for (let i = 0; i < files.length; i++) {
    const file = files[i]
    if (!allowed.includes(file.type.toLowerCase())) {
      errorStore.showError(t('treatments.error_unsupported_format'))
      continue
    }
    if (currentCount + added >= 5) {
      errorStore.showError(t('treatments.max_images_reached'))
      break
    }

    const previewUrl = URL.createObjectURL(file)
    treatmentFiles.value.push({
      file,
      previewUrl,
      isExisting: false
    })
    added++
  }
}

async function removeFile(idx) {
  const img = treatmentFiles.value[idx]
  if (img.isExisting) {
    const confirmed = await confirmStore.ask({
      title: t('treatments.delete_image'),
      message: t('treatments.delete_image_confirm'),
      type: 'danger',
      confirmText: t('common.delete')
    })
    if (!confirmed) return
    try {
      await axios.delete(`/api/treatments/images/${img.id}`)
      treatmentFiles.value.splice(idx, 1)
    } catch (err) {
      console.error('Delete image failed:', err)
    }
  } else {
    if (img.previewUrl) {
      URL.revokeObjectURL(img.previewUrl)
    }
    treatmentFiles.value.splice(idx, 1)
  }
}

// Lightbox
function openLightbox(url) {
  lightboxUrl.value = url
}

// Banner feedback
function showAlert(message, type = 'success') {
  alertMessage.value = message
  alertClass.value = type === 'success' 
    ? 'bg-green-500/10 border border-green-500/20 text-green-600 dark:text-green-400' 
    : 'bg-red-500/10 border border-red-500/20 text-red-600 dark:text-red-400'
  
  setTimeout(() => {
    alertMessage.value = ''
  }, 5000)
}

// Lifecycle Hooks & Watchers
onMounted(() => {
  if (apiaryStore.activeApiaryId) {
    fetchTreatments()
    fetchLocations()
    fetchHives()
    fetchTreatmentMethods()
    fetchTreatmentApplicationTypes()
  }
})

watch(() => apiaryStore.activeApiaryId, () => {
  if (apiaryStore.activeApiaryId) {
    fetchTreatments()
    fetchLocations()
    fetchHives()
    fetchTreatmentMethods()
    fetchTreatmentApplicationTypes()
  } else {
    treatments.value = []
    locations.value = []
    hives.value = []
    treatmentApplicationTypes.value = []
  }
})
</script>

<style scoped>
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.2s ease;
}
.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

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
