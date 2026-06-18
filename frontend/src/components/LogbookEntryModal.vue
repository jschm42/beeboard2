<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div
        v-if="show"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm overflow-y-auto"
        role="dialog"
        aria-modal="true"
        @click.self="close"
      >
        <div class="bg-white dark:bg-dark-card rounded-3xl shadow-2xl max-w-4xl w-full my-8 flex flex-col max-h-[calc(100vh-4rem)] overflow-hidden animate-scale">
          <!-- Header -->
          <div class="flex justify-between items-center p-6 pb-4 border-b border-gray-100 dark:border-dark-border flex-shrink-0">
            <h3 class="text-xl font-bold text-gray-900 dark:text-white">
              {{ isEditMode ? $t('logbook.edit_entry_title') : $t('logbook.new_entry_title') }}
            </h3>
            <button
              type="button"
              class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
              :aria-label="$t('common.cancel')"
              @click="close"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
            </button>
          </div>

          <!-- Form -->
          <form class="p-6 space-y-4 overflow-y-auto flex-1" @submit.prevent="submitEntryForm">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('logbook.hive_required') }}</label>
                <select
                  v-model="entryForm.hiveId"
                  required
                  :disabled="isHiveSelectorDisabled"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm cursor-pointer disabled:opacity-60 disabled:cursor-not-allowed"
                  @change="onHiveSelected"
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
                  :disabled="isEditMode"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm cursor-pointer disabled:opacity-60 disabled:cursor-not-allowed"
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
              />
            </div>

            <!-- Image Upload Section -->
            <div class="space-y-2">
              <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">
                {{ $t('logbook.table_images') }}
              </label>
              <div
                class="border-2 border-dashed rounded-2xl p-6 text-center cursor-pointer transition-all duration-200"
                :class="dragOver ? 'border-primary bg-primary/5' : 'border-gray-300 dark:border-gray-700 bg-gray-50/50 dark:bg-dark-bg/30 hover:border-primary/50'"
                @click="triggerFileInput"
                @dragover.prevent="dragOver = true"
                @dragleave.prevent="dragOver = false"
                @drop.prevent="onFileDrop"
              >
                <input
                  ref="modalFileInput"
                  type="file"
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

              <div class="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  class="px-3 py-2 rounded-xl border border-gray-200 dark:border-dark-border text-xs font-bold text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-dark-border hover:text-primary dark:hover:text-primary transition-colors flex items-center justify-center gap-1.5"
                  @click="triggerFileInput"
                >
                  <Upload class="w-4 h-4" />
                  {{ $t('logbook.choose_file') }}
                </button>
                <button
                  type="button"
                  class="px-3 py-2 rounded-xl border border-gray-200 dark:border-dark-border text-xs font-bold text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-dark-border hover:text-primary dark:hover:text-primary transition-colors flex items-center justify-center gap-1.5"
                  @click="triggerCamera"
                >
                  <input
                    ref="cameraFileInput"
                    type="file"
                    accept="image/*"
                    capture="environment"
                    class="hidden"
                    @change="onFileSelect"
                  />
                  <Camera class="w-4 h-4" />
                  {{ $t('logbook.take_photo') }}
                </button>
              </div>

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
                    class="absolute top-1 right-1 p-1 bg-red-500 text-white rounded-lg shadow opacity-0 group-hover:opacity-100 transition-opacity duration-150"
                    :title="$t('logbook.delete_image')"
                    @click="removeEntryFile(idx)"
                  >
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                  </button>
                </div>
              </div>
            </div>

            <!-- SUB-FORM: INSPECTION DETAILS -->
            <div v-if="entryForm.entryType === 'INSPECTION'" class="space-y-4 border-t border-gray-100 dark:border-dark-border pt-4">
              <div class="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-2">
                <h4 class="text-xs font-extrabold uppercase text-gray-500 tracking-wider">
                  {{ $t('logbook.assessment_variant') }}
                </h4>
              </div>

              <div class="space-y-4 animate-scale">
                <div class="p-4 bg-gray-50 dark:bg-dark-bg/60 border border-gray-200 dark:border-dark-border rounded-2xl space-y-2.5">
                  <span class="block text-[10px] font-black text-gray-500 uppercase tracking-wide">{{ $t('logbook.categories_to_record') }}</span>
                  <div class="flex flex-wrap gap-x-4 gap-y-2 text-xs font-bold text-gray-700 dark:text-gray-300">
                    <label class="flex items-center space-x-1.5 cursor-pointer hover:text-primary transition-colors">
                      <input v-model="activeCategories.brood" type="checkbox" class="rounded text-primary focus:ring-primary h-4 w-4 border-gray-300 dark:border-dark-border">
                      <span class="text-amber-500">🥚 {{ $t('logbook.brood') }}</span>
                    </label>
                    <label class="flex items-center space-x-1.5 cursor-pointer hover:text-primary transition-colors">
                      <input v-model="activeCategories.bees" type="checkbox" class="rounded text-primary focus:ring-primary h-4 w-4 border-gray-300 dark:border-dark-border">
                      <span class="text-green-500">🐝 {{ $t('logbook.bees') }}</span>
                    </label>
                    <label class="flex items-center space-x-1.5 cursor-pointer hover:text-primary transition-colors">
                      <input v-model="activeCategories.drones" type="checkbox" class="rounded text-primary focus:ring-primary h-4 w-4 border-gray-300 dark:border-dark-border">
                      <span class="text-sky-500">♂️ {{ $t('logbook.drones') }}</span>
                    </label>
                    <label class="flex items-center space-x-1.5 cursor-pointer hover:text-primary transition-colors">
                      <input v-model="activeCategories.drone_brood" type="checkbox" class="rounded text-primary focus:ring-primary h-4 w-4 border-gray-300 dark:border-dark-border">
                      <span class="text-orange-500">🥚♂️ {{ $t('logbook.drone_brood') }}</span>
                    </label>
                    <label class="flex items-center space-x-1.5 cursor-pointer hover:text-primary transition-colors">
                      <input v-model="activeCategories.pollen" type="checkbox" class="rounded text-primary focus:ring-primary h-4 w-4 border-gray-300 dark:border-dark-border">
                      <span class="text-purple-500">🌺 {{ $t('logbook.pollen') }}</span>
                    </label>
                    <label class="flex items-center space-x-1.5 cursor-pointer hover:text-primary transition-colors">
                      <input v-model="activeCategories.food" type="checkbox" class="rounded text-primary focus:ring-primary h-4 w-4 border-gray-300 dark:border-dark-border">
                      <span class="text-yellow-500">🍯 {{ $t('logbook.food') }}</span>
                    </label>
                  </div>
                </div>

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
                      <div v-if="activeCategories.brood" class="space-y-1">
                        <span class="text-[9px] text-amber-500 font-bold uppercase">{{ $t('logbook.brood') }}</span>
                        <input
                          v-model.number="box.brood"
                          type="number"
                          step="any"
                          min="0"
                          :max="entryForm.inspectionDetail.boxMode === 'eighths' ? 300 : undefined"
                          class="w-full px-2 py-1.5 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg rounded-xl text-center text-xs font-mono font-bold"
                          :placeholder="entryForm.inspectionDetail.boxMode === 'exact' ? $t('logbook.exact_placeholder_pcs') : $t('logbook.eighths_placeholder')"
                        >
                      </div>

                      <div v-if="activeCategories.bees" class="space-y-1">
                        <span class="text-[9px] text-green-500 font-bold uppercase">{{ $t('logbook.bees') }}</span>
                        <input
                          v-model.number="box.bees"
                          type="number"
                          step="any"
                          min="0"
                          :max="entryForm.inspectionDetail.boxMode === 'eighths' ? 300 : undefined"
                          class="w-full px-2 py-1.5 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg rounded-xl text-center text-xs font-mono font-bold"
                          :placeholder="entryForm.inspectionDetail.boxMode === 'exact' ? $t('logbook.exact_placeholder_pcs') : $t('logbook.eighths_placeholder')"
                        >
                      </div>

                      <div v-if="activeCategories.drones" class="space-y-1">
                        <span class="text-[9px] text-sky-500 font-bold uppercase">{{ $t('logbook.drones') }}</span>
                        <input
                          v-model.number="box.drones"
                          type="number"
                          step="any"
                          min="0"
                          :max="entryForm.inspectionDetail.boxMode === 'eighths' ? 300 : undefined"
                          class="w-full px-2 py-1.5 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg rounded-xl text-center text-xs font-mono font-bold"
                          :placeholder="entryForm.inspectionDetail.boxMode === 'exact' ? $t('logbook.exact_placeholder_pcs') : $t('logbook.eighths_placeholder')"
                        >
                      </div>

                      <div v-if="activeCategories.drone_brood" class="space-y-1">
                        <span class="text-[9px] text-orange-500 font-bold uppercase">{{ $t('logbook.drone_brood') }}</span>
                        <input
                          v-model.number="box.drone_brood"
                          type="number"
                          step="any"
                          min="0"
                          :max="entryForm.inspectionDetail.boxMode === 'eighths' ? 300 : undefined"
                          class="w-full px-2 py-1.5 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg rounded-xl text-center text-xs font-mono font-bold"
                          :placeholder="entryForm.inspectionDetail.boxMode === 'exact' ? $t('logbook.exact_placeholder_pcs') : $t('logbook.eighths_placeholder')"
                        >
                      </div>

                      <div v-if="activeCategories.pollen" class="space-y-1">
                        <span class="text-[9px] text-purple-500 font-bold uppercase">{{ $t('logbook.pollen') }}</span>
                        <input
                          v-model.number="box.pollen"
                          type="number"
                          step="any"
                          min="0"
                          :max="entryForm.inspectionDetail.boxMode === 'eighths' ? 300 : undefined"
                          class="w-full px-2 py-1.5 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg rounded-xl text-center text-xs font-mono font-bold"
                          :placeholder="entryForm.inspectionDetail.boxMode === 'exact' ? $t('logbook.exact_placeholder_g') : $t('logbook.eighths_placeholder')"
                        >
                      </div>

                      <div v-if="activeCategories.food" class="space-y-1">
                        <span class="text-[9px] text-yellow-500 font-bold uppercase">{{ $t('logbook.food') }}</span>
                        <input
                          v-model.number="box.food"
                          type="number"
                          step="any"
                          min="0"
                          :max="entryForm.inspectionDetail.boxMode === 'eighths' ? 300 : undefined"
                          class="w-full px-2 py-1.5 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg rounded-xl text-center text-xs font-mono font-bold"
                          :placeholder="entryForm.inspectionDetail.boxMode === 'exact' ? $t('logbook.exact_placeholder_g') : $t('logbook.eighths_placeholder')"
                        >
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
                >
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
                  >
                </div>
                <div>
                  <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 mb-1">{{ $t('logbook.treatment_dosage_label') }}</label>
                  <input
                    v-model="entryForm.varroaTreatmentDetail.dosage"
                    type="text"
                    required
                    :placeholder="$t('logbook.treatment_dosage_placeholder')"
                    class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm"
                  >
                </div>
              </div>
              <div>
                <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 mb-1">{{ $t('logbook.treatment_notes_label') }}</label>
                <textarea
                  v-model="entryForm.varroaTreatmentDetail.treatmentNotes"
                  :placeholder="$t('logbook.treatment_notes_placeholder')"
                  rows="2"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm"
                />
              </div>
            </div>

            <div class="flex justify-end space-x-2 pt-4 border-t border-gray-100 dark:border-dark-border">
              <button type="button" class="px-4 py-2 text-sm font-bold text-gray-500 hover:text-gray-700 dark:hover:text-gray-300" @click="close">{{ $t('common.cancel') }}</button>
              <button type="submit" class="px-5 py-2 bg-primary hover:bg-primary-hover text-white font-extrabold text-sm rounded-xl shadow-md">
                {{ $t('common.save') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { useI18n } from 'vue-i18n'
import axios from 'axios'
import { Camera, Upload } from 'lucide-vue-next'
import { useErrorStore } from '../stores/error'
import { useConfirmStore } from '../stores/confirm'

const props = defineProps({
  show: { type: Boolean, default: false },
  editingEntry: { type: Object, default: null },
  hives: { type: Array, default: () => [] },
  selectedSession: { type: Object, default: null },
  apiaryId: { type: String, default: null },
})

const emit = defineEmits(['update:show', 'saved'])

const { t } = useI18n()
const errorStore = useErrorStore()
const confirmStore = useConfirmStore()

const isEditMode = computed(() => !!props.editingEntry)

const entryForm = reactive({
  hiveId: '',
  date: new Date().toISOString().substring(0, 10),
  entryType: 'GENERAL',
  notes: '',
  inspectionDetail: {
    assessmentMode: 'boxes',
    boxMode: 'exact',
    frames: [],
    boxes: [],
  },
  varroaCountDetail: { rawCount: 0 },
  varroaTreatmentDetail: { product: '', dosage: '', treatmentNotes: '' },
})

const entryFiles = ref([])
const dragOver = ref(false)
const modalFileInput = ref(null)
const cameraFileInput = ref(null)
const selectedTypeOption = ref('GENERAL')

const CATEGORIES_STORAGE_KEY = 'beeboard_active_categories'

function loadSavedCategories() {
  try {
    const saved = localStorage.getItem(CATEGORIES_STORAGE_KEY)
    if (saved) return JSON.parse(saved)
  } catch { /* ignore parse error, use defaults */ }
  return null
}

const _savedCats = loadSavedCategories()
const activeCategories = reactive({
  brood: _savedCats ? _savedCats.brood !== false : true,
  bees: _savedCats ? _savedCats.bees !== false : true,
  drones: _savedCats ? _savedCats.drones !== false : true,
  drone_brood: _savedCats ? _savedCats.drone_brood !== false : true,
  pollen: _savedCats ? _savedCats.pollen !== false : true,
  food: _savedCats ? _savedCats.food !== false : true,
})

const isHiveSelectorDisabled = computed(() => {
  if (!props.selectedSession) return false
  if (props.selectedSession.hive_id) return true
  if (props.selectedSession.scope_type === 'HIVE' && props.selectedSession.linked_hives?.length === 1) return true
  return false
})

const filteredHivesForEntry = computed(() => {
  if (!props.selectedSession) return props.hives

  const scope = props.selectedSession.scope_type || 'APIARY'
  if (scope === 'HIVE') {
    const linkedIds = props.selectedSession.linked_hives?.map(h => h.id) || []
    return props.hives.filter(h => linkedIds.includes(h.id))
  } else if (scope === 'LOCATION') {
    const linkedIds = props.selectedSession.linked_locations?.map(l => l.id) || []
    return props.hives.filter(h => linkedIds.includes(h.location_id))
  } else if (scope === 'APIARY') {
    const linkedIds = props.selectedSession.linked_apiaries?.map(a => a.id) || []
    return props.hives.filter(h => linkedIds.includes(h.apiary_id))
  }
  return props.hives
})

watch(() => props.show, (newVal) => {
  if (!newVal) {
    clearEntryFormFiles()
  }
})

watch(activeCategories, (newVal) => {
  try {
    localStorage.setItem(CATEGORIES_STORAGE_KEY, JSON.stringify({ ...newVal }))
  } catch { /* ignore storage write error */ }
}, { deep: true })

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

function handleEscape(event) {
  if (event.key === 'Escape' && props.show) {
    close()
  }
}

onMounted(() => {
  document.addEventListener('keydown', handleEscape)
})

onBeforeUnmount(() => {
  document.removeEventListener('keydown', handleEscape)
})

function close() {
  emit('update:show', false)
}

function resetForm() {
  entryForm.hiveId = props.selectedSession?.hive_id || (filteredHivesForEntry.value[0]?.id || '')
  entryForm.date = new Date().toISOString().substring(0, 10)
  selectedTypeOption.value = 'GENERAL'
  entryForm.notes = ''
  entryForm.inspectionDetail.assessmentMode = 'boxes'
  entryForm.inspectionDetail.boxMode = 'exact'
  entryForm.varroaCountDetail.rawCount = 0
  entryForm.varroaTreatmentDetail.product = ''
  entryForm.varroaTreatmentDetail.dosage = ''
  entryForm.varroaTreatmentDetail.treatmentNotes = ''

  const saved = loadSavedCategories()
  activeCategories.brood = saved ? saved.brood !== false : true
  activeCategories.bees = saved ? saved.bees !== false : true
  activeCategories.drones = saved ? saved.drones !== false : true
  activeCategories.drone_brood = saved ? saved.drone_brood !== false : true
  activeCategories.pollen = saved ? saved.pollen !== false : true
  activeCategories.food = saved ? saved.food !== false : true

  onHiveSelected()
  clearEntryFormFiles()
}

function open(entry) {
  if (entry) {
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
        b.pollen_eighths != null,
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
        isExisting: true,
      }))
    }

    if (entry.entry_type === 'INSPECTION' && entry.inspection_detail) {
      const hive = props.hives.find(h => h.id === entry.hive_id)

      const anyEighths = (entry.inspection_detail.boxes || []).some(b =>
        (b.brood_eighths != null && b.brood_eighths !== -1) ||
        (b.bee_eighths != null && b.bee_eighths !== -1) ||
        (b.food_eighths != null && b.food_eighths !== -1) ||
        (b.drone_eighths != null && b.drone_eighths !== -1) ||
        (b.drone_brood_eighths != null && b.drone_brood_eighths !== -1) ||
        (b.pollen_eighths != null && b.pollen_eighths !== -1),
      )

      const boxesFromDb = entry.inspection_detail.boxes || []
      activeCategories.brood = boxesFromDb.some(b => anyEighths ? (b.brood_eighths !== null && b.brood_eighths !== -1) : (b.brood_total !== null && b.brood_total !== -1))
      activeCategories.bees = boxesFromDb.some(b => anyEighths ? (b.bee_eighths !== null && b.bee_eighths !== -1) : (b.bee_total !== null && b.bee_total !== -1))
      activeCategories.food = boxesFromDb.some(b => anyEighths ? (b.food_eighths !== null && b.food_eighths !== -1) : (b.food_total !== null && b.food_total !== -1))
      activeCategories.drones = boxesFromDb.some(b => anyEighths ? (b.drone_eighths !== null && b.drone_eighths !== -1) : (b.drone_total !== null && b.drone_total !== -1))
      activeCategories.drone_brood = boxesFromDb.some(b => anyEighths ? (b.drone_brood_eighths !== null && b.drone_brood_eighths !== -1) : (b.drone_brood_total !== null && b.drone_brood_total !== -1))
      activeCategories.pollen = boxesFromDb.some(b => anyEighths ? (b.pollen_eighths !== null && b.pollen_eighths !== -1) : (b.pollen_total !== null && b.pollen_total !== -1))

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
            brood: anyEighths ? (b.brood_eighths !== null && b.brood_eighths !== -1 ? b.brood_eighths : 0) : (b.brood_total !== null && b.brood_total !== -1 ? b.brood_total : 0),
            bees: anyEighths ? (b.bee_eighths !== null && b.bee_eighths !== -1 ? b.bee_eighths : 0) : (b.bee_total !== null && b.bee_total !== -1 ? b.bee_total : 0),
            food: anyEighths ? (b.food_eighths !== null && b.food_eighths !== -1 ? b.food_eighths : 0) : (b.food_total !== null && b.food_total !== -1 ? b.food_total : 0),
            drones: anyEighths ? (b.drone_eighths !== null && b.drone_eighths !== -1 ? b.drone_eighths : 0) : (b.drone_total !== null && b.drone_total !== -1 ? b.drone_total : 0),
            drone_brood: anyEighths ? (b.drone_brood_eighths !== null && b.drone_brood_eighths !== -1 ? b.drone_brood_eighths : 0) : (b.drone_brood_total !== null && b.drone_brood_total !== -1 ? b.drone_brood_total : 0),
            pollen: anyEighths ? (b.pollen_eighths !== null && b.pollen_eighths !== -1 ? b.pollen_eighths : 0) : (b.pollen_total !== null && b.pollen_total !== -1 ? b.pollen_total : 0),
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
  } else {
    resetForm()
  }

  emit('update:show', true)
}

function applyDraft(draft) {
  let targetHiveId = props.hives[0]?.id || ''
  if (draft.hive_name) {
    const matched = props.hives.find(h => h.name.toLowerCase() === draft.hive_name.toLowerCase())
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
      food_eighths: f.food_eighths || 0,
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

  emit('update:show', true)
}

function onHiveSelected() {
  if (entryForm.entryType !== 'INSPECTION') return

  const hive = props.hives.find(h => h.id === entryForm.hiveId)
  if (!hive) return

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
      pollen: 0,
    }))
  } else {
    entryForm.inspectionDetail.boxes = []
    entryForm.inspectionDetail.assessmentMode = 'frames'
  }
}

async function submitEntryForm() {
  try {
    const isExact = entryForm.inspectionDetail.boxMode === 'exact'

    const payload = {
      hive_id: entryForm.hiveId,
      session_id: props.selectedSession ? props.selectedSession.id : null,
      date: entryForm.date,
      entry_type: entryForm.entryType,
      notes: entryForm.notes.trim() || null,
      inspection_detail: entryForm.entryType === 'INSPECTION' ? {
        boxes: entryForm.inspectionDetail.boxes.map((box, idx) => {
          const broodVal = activeCategories.brood ? Number(box.brood || 0) : -1
          const beeVal = activeCategories.bees ? Number(box.bees || 0) : -1
          const foodVal = activeCategories.food ? Number(box.food || 0) : -1
          const droneVal = activeCategories.drones ? Number(box.drones || 0) : -1
          const droneBroodVal = activeCategories.drone_brood ? Number(box.drone_brood || 0) : -1
          const pollenVal = activeCategories.pollen ? Number(box.pollen || 0) : -1

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
            broodTotal = broodVal !== -1 ? broodVal * broodMult : -1
            beeTotal = beeVal !== -1 ? beeVal * beeMult : -1
            foodTotal = foodVal !== -1 ? foodVal * foodMult : -1
            droneTotal = droneVal !== -1 ? droneVal * droneMult : -1
            droneBroodTotal = droneBroodVal !== -1 ? droneBroodVal * droneBroodMult : -1
            pollenTotal = pollenVal !== -1 ? pollenVal * pollenMult : -1
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
            food_eighths: isExact ? null : foodVal,
          }
        }),
      } : null,
      varroa_count_detail: entryForm.entryType === 'VARROA_COUNT' ? {
        raw_count: entryForm.varroaCountDetail.rawCount,
      } : null,
      varroa_treatment_detail: entryForm.entryType === 'VARROA_TREATMENT' ? {
        product: entryForm.varroaTreatmentDetail.product.trim(),
        dosage: entryForm.varroaTreatmentDetail.dosage.trim(),
        treatment_notes: entryForm.varroaTreatmentDetail.treatmentNotes.trim() || null,
      } : null,
    }

    let response
    if (isEditMode.value) {
      response = await axios.put(`/api/logbook/entries/${props.editingEntry.id}`, payload)
    } else {
      response = await axios.post('/api/logbook/entries', payload, {
        params: { apiary_id: props.apiaryId },
      })
    }

    const entryId = response.data?.id || props.editingEntry?.id
    const uploads = entryFiles.value.filter(f => !f.isExisting)
    for (const uf of uploads) {
      const formData = new FormData()
      formData.append('file', uf.file)
      await axios.post(`/api/logbook/entries/${entryId}/images`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
    }

    close()
    emit('saved')
  } catch (err) {
    errorStore.showError(t('logbook.entry_form_submission_error'), err, t('common.save'))
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
      isExisting: false,
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
  modalFileInput.value?.click()
}

function triggerCamera() {
  cameraFileInput.value?.click()
}

async function removeEntryFile(index) {
  const img = entryFiles.value[index]
  if (img.isExisting) {
    const confirmed = await confirmStore.ask({
      title: t('logbook.delete_image'),
      message: t('logbook.delete_image_confirm'),
      type: 'danger',
      confirmText: t('common.delete'),
    })
    if (!confirmed) return
    try {
      await axios.delete(`/api/logbook/images/${img.id}`)
      entryFiles.value.splice(index, 1)
    } catch (err) {
      console.error('Delete image failed:', err)
    }
  } else {
    if (img.previewUrl) {
      URL.revokeObjectURL(img.previewUrl)
    }
    entryFiles.value.splice(index, 1)
  }
}

defineExpose({ open, applyDraft })
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
