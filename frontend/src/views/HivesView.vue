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

    <!-- Create/Edit Hive Form (Inline, embedded on page) -->
    <div v-if="showModal" class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl shadow-md w-full max-w-2xl mx-auto p-6 mb-8 animate-scale">
      <div class="flex justify-between items-center mb-6 pb-4 border-b border-gray-100 dark:border-dark-border">
        <h3 class="text-xl font-bold text-gray-900 dark:text-white">
          {{ isEditMode ? '🐝 Volk-Einstellungen bearbeiten' : '🐝 Neues Volk anlegen' }}
        </h3>
        <button @click="closeModal" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
        </button>
      </div>
      
      <form @submit.prevent="submitForm">
        <div class="space-y-4">
          
          <div>
            <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">Volksbezeichnung / Name *</label>
            <input 
              v-model="form.name" 
              type="text" 
              required
              placeholder="z.B. Volk 14"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm"
            />
          </div>

          <div>
            <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">Standort (Stand) *</label>
            <select 
              v-model="form.locationId" 
              required
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm cursor-pointer"
            >
              <option value="" disabled>Bitte Standort wählen...</option>
              <option v-for="loc in locations" :key="loc.id" :value="loc.id">
                {{ loc.name }}
              </option>
            </select>
          </div>

          <div>
            <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">Wabenmaß *</label>
            <select 
              v-model="form.frameTypeId" 
              required
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm cursor-pointer"
            >
              <option value="" disabled>Bitte Wabenmaß wählen...</option>
              <option v-for="ft in frameTypes" :key="ft.id" :value="ft.id">
                {{ ft.name }}
              </option>
            </select>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">Königin Jahr (Schlüpfjahr)</label>
              <input 
                v-model.number="form.queenYear" 
                type="number" 
                placeholder="z.B. 2025"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm"
              />
            </div>
            <div class="flex flex-col justify-end pb-2">
              <label class="flex items-center space-x-2 cursor-pointer select-none">
                <input 
                  v-model="form.isActive" 
                  type="checkbox"
                  class="rounded text-primary focus:ring-primary h-4.5 w-4.5"
                />
                <span class="text-xs font-bold text-gray-700 dark:text-gray-300">Volk ist aktiv</span>
              </label>
            </div>
          </div>

          <div>
            <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">Notizen (Königinlinie etc.)</label>
            <textarea 
              v-model="form.notes" 
              placeholder="Königin F1 Carnica, standbegattet, sanftmütig..."
              rows="3"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm"
            ></textarea>
          </div>

        </div>

        <div class="flex justify-end space-x-3 mt-6 border-t border-gray-100 dark:border-dark-border pt-4">
          <button 
            type="button" 
            @click="closeModal" 
            class="px-4 py-2 text-sm font-bold text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
          >
            Abbrechen
          </button>
          <button 
            type="submit" 
            class="px-5 py-2.5 bg-primary hover:bg-primary-hover text-white font-extrabold text-sm rounded-xl shadow-md hover-scale"
          >
            Speichern
          </button>
        </div>
      </form>
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

    <!-- Main Splitscreen Grid -->
    <div v-else class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
      
      <!-- Left Panel: Hives List (7 cols on desktop) -->
      <div class="lg:col-span-7 space-y-4">
        
        <div v-if="loading" class="flex flex-col items-center justify-center py-20 bg-white dark:bg-dark-card rounded-3xl border border-gray-200 dark:border-dark-border">
          <svg class="animate-spin h-10 w-10 text-primary mb-4" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
          <p class="text-gray-500 dark:text-gray-400 font-bold">Lade Bienenvölker...</p>
        </div>

        <div 
          v-else
          v-for="hive in hives" 
          :key="hive.id"
          @click="selectHive(hive)"
          class="bg-white dark:bg-dark-card border rounded-3xl p-5 shadow-sm transition-all duration-200 cursor-pointer flex items-center justify-between"
          :class="[
            selectedHive?.id === hive.id 
              ? 'border-primary ring-2 ring-primary/20 shadow-md scale-[1.01]' 
              : 'border-gray-200 dark:border-dark-border hover:border-primary/50'
          ]"
        >
          <div class="flex items-center space-x-4 min-w-0">
            <!-- Profile Thumbnail -->
            <div class="w-14 h-14 rounded-2xl bg-amber-500/10 border border-amber-500/20 shrink-0 flex items-center justify-center overflow-hidden">
              <img 
                v-if="hive.image_path" 
                :src="`/uploads/${hive.image_path}`" 
                alt="Hive picture" 
                class="w-full h-full object-cover"
              />
              <span v-else class="text-2xl">🐝</span>
            </div>

            <!-- Hive Info -->
            <div class="min-w-0">
              <div class="flex items-center space-x-2">
                <h3 class="font-extrabold text-base text-gray-900 dark:text-white truncate">
                  {{ hive.name }}
                </h3>
                <span 
                  class="px-2 py-0.5 text-[9px] font-black rounded-full tracking-wider shrink-0 uppercase"
                  :class="hive.is_active ? 'bg-green-500/10 text-green-500' : 'bg-gray-500/10 text-gray-500'"
                >
                  {{ hive.is_active ? 'Aktiv' : 'Inaktiv' }}
                </span>
              </div>
              <p class="text-xs text-gray-500 dark:text-gray-400 mt-1 flex items-center space-x-1">
                <span>📍 Standort:</span>
                <span class="font-bold text-gray-700 dark:text-gray-300 truncate max-w-[120px]">
                  {{ hive.location?.name || 'Kein Standort' }}
                </span>
              </p>
              
              <!-- Frame size -->
              <p class="text-[10px] text-gray-400 font-bold uppercase mt-1 tracking-wider">
                {{ hive.frame_type?.name }} (Faktor: {{ (hive.frame_type?.brood_multiplier || 1.0).toFixed(1) }}x)
              </p>
            </div>
          </div>

          <!-- Queen marker color and boxes count -->
          <div class="flex flex-col items-end space-y-2 shrink-0 pl-3">
            <!-- Queen Color Year -->
            <div v-if="hive.queen_year" class="flex items-center space-x-1.5 bg-gray-50 dark:bg-dark-bg/60 border border-gray-200 dark:border-gray-800 px-2 py-1 rounded-lg">
              <div 
                class="w-3 h-3 rounded-full border border-gray-400 shadow-sm shrink-0" 
                :style="{ backgroundColor: getQueenColor(hive.queen_year) }"
                :title="`Königin Jahr ${hive.queen_year}`"
              ></div>
              <span class="text-[10px] font-bold text-gray-600 dark:text-gray-400">👑 '{{ hive.queen_year.toString().slice(-2) }}</span>
            </div>
            
            <span class="px-2 py-0.5 bg-primary/10 text-primary text-[10px] font-extrabold rounded-full">
              {{ hive.boxes?.length || 0 }} Zargen
            </span>
          </div>

        </div>

      </div>

      <!-- Right Panel: Box Structure Details & Editor (5 cols on desktop) -->
      <div class="lg:col-span-5">
        <div v-if="!selectedHive" class="bg-gray-50 dark:bg-dark-card/20 border border-dashed border-gray-300 dark:border-gray-700 rounded-3xl p-8 text-center text-gray-400 italic text-sm">
          Wähle ein Volk aus der Liste aus, um die Zargenstruktur zu verwalten, Fotos hochzuladen oder Einstellungen anzupassen.
        </div>

        <div v-else class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-6 shadow-sm space-y-6">
          
          <!-- Selected Hive Header Info -->
          <div class="flex justify-between items-start border-b border-gray-100 dark:border-dark-border pb-4">
            <div>
              <h2 class="text-xl font-bold text-gray-900 dark:text-white">{{ selectedHive.name }}</h2>
              <p class="text-xs text-gray-400 mt-1">Gekoppeltes Wabenmaß: {{ selectedHive.frame_type?.name }}</p>
            </div>
            
            <div class="flex space-x-1">
              <button 
                @click="openEditModal(selectedHive)" 
                class="p-2 text-gray-500 hover:text-primary hover:bg-gray-100 dark:hover:bg-dark-border rounded-xl transition-all duration-150"
                title="Profil bearbeiten"
              >
                <svg class="w-4.5 h-4.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/></svg>
              </button>
              <button 
                @click="deleteHive(selectedHive)" 
                class="p-2 text-gray-400 hover:text-red-500 hover:bg-red-500/10 rounded-xl transition-all duration-150"
                title="Volk auflösen / löschen"
              >
                <svg class="w-4.5 h-4.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
              </button>
            </div>
          </div>

          <!-- Profile Photo Uploader -->
          <div class="flex items-center space-x-4 p-4 bg-gray-50 dark:bg-dark-bg/60 border border-gray-200 dark:border-gray-800 rounded-2xl">
            <div class="w-12 h-12 rounded-xl bg-amber-500/10 border border-amber-500/20 shrink-0 overflow-hidden flex items-center justify-center">
              <img 
                v-if="selectedHive.image_path" 
                :src="`/uploads/${selectedHive.image_path}`" 
                alt="Hive thumb" 
                class="w-full h-full object-cover"
              />
              <span v-else class="text-xl">📸</span>
            </div>
            <div>
              <p class="text-xs font-bold text-gray-700 dark:text-gray-300">Bienenvolk Foto</p>
              <input 
                type="file" 
                ref="photoInput" 
                @change="uploadPhoto" 
                accept="image/*" 
                class="hidden"
              />
              <button 
                @click="$refs.photoInput.click()" 
                class="text-[11px] font-extrabold text-primary hover:text-primary-hover hover:underline uppercase tracking-wider mt-1"
              >
                Foto hochladen
              </button>
            </div>
          </div>

          <!-- Zargen Editor Section -->
          <div>
            <h3 class="text-sm font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-4">🧱 Zargen-Editor</h3>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 items-center">
              <!-- Visual stack representation -->
              <BeehiveVisualizer 
                :boxes="editedBoxes" 
                :selectedBoxId="selectedBoxId" 
                @select-box="onSelectBox" 
                @update-boxes="onUpdateBoxes"
              />

              <!-- Box properties config panel -->
              <div class="space-y-4">
                <div v-if="!selectedBox" class="text-xs text-gray-400 italic p-4 bg-gray-50 dark:bg-dark-bg/60 rounded-2xl border text-center">
                  Wähle eine Zarge im Stapel aus, um deren Werte (Brut/Honig, Wabenzahl) zu editieren oder sie zu löschen.
                </div>
                
                <div v-else class="p-4 bg-gray-50 dark:bg-dark-bg/60 border border-gray-200 dark:border-dark-800 rounded-2xl space-y-3">
                  <div class="flex justify-between items-center pb-2 border-b border-gray-200 dark:border-gray-700">
                    <span class="text-xs font-black uppercase text-gray-600 dark:text-gray-300">Zarge #{{ selectedBox.order }}</span>
                    <span 
                      class="px-2 py-0.5 text-[9px] font-bold rounded-full"
                      :class="selectedBox.box_type === 'BROOD' ? 'bg-amber-600/10 text-amber-500' : 'bg-yellow-500/10 text-yellow-500'"
                    >
                      {{ selectedBox.box_type === 'BROOD' ? 'Brutraum' : 'Honigraum' }}
                    </span>
                  </div>

                  <div>
                    <label class="block text-[10px] font-bold text-gray-500 uppercase tracking-wider mb-1">Typ</label>
                    <select 
                      v-model="selectedBox.box_type"
                      class="w-full px-2 py-1.5 bg-white dark:bg-dark-card border border-gray-300 dark:border-gray-700 rounded-lg text-xs"
                    >
                      <option value="BROOD">Brutraum</option>
                      <option value="HONEY">Honigraum</option>
                    </select>
                  </div>

                  <div>
                    <label class="block text-[10px] font-bold text-gray-500 uppercase tracking-wider mb-1">Anzahl Waben</label>
                    <input 
                      v-model.number="selectedBox.frame_count"
                      type="number"
                      min="1"
                      max="24"
                      class="w-full px-2 py-1.5 bg-white dark:bg-dark-card border border-gray-300 dark:border-gray-700 rounded-lg text-xs"
                    />
                  </div>

                  <div>
                    <label class="block text-[10px] font-bold text-gray-500 uppercase tracking-wider mb-1">Wabenmaß</label>
                    <select 
                      v-model="selectedBox.frame_type_id"
                      class="w-full px-2 py-1.5 bg-white dark:bg-dark-card border border-gray-300 dark:border-gray-700 rounded-lg text-xs"
                    >
                      <option v-for="ft in frameTypes" :key="ft.id" :value="ft.id">
                        {{ ft.name }}
                      </option>
                    </select>
                  </div>

                </div>

                <!-- Add Chamber CTA -->
                <button 
                  type="button"
                  @click="addChamber"
                  class="w-full py-2.5 bg-gray-100 hover:bg-gray-200 dark:bg-dark-border dark:hover:bg-gray-700 text-gray-800 dark:text-gray-200 font-extrabold text-xs rounded-xl tracking-wider uppercase border border-gray-300 dark:border-gray-700 transition-colors"
                >
                  + Zarge hinzufügen
                </button>
              </div>
            </div>

            <!-- Save Chamber Structure CTA -->
            <div v-if="boxesChanged" class="mt-6 pt-4 border-t border-gray-100 dark:border-dark-border flex justify-end">
              <button 
                type="button" 
                @click="saveChamberStructure"
                class="px-5 py-2.5 bg-primary hover:bg-primary-hover text-white font-extrabold text-xs uppercase tracking-wider rounded-xl shadow-md hover-scale"
              >
                Speichern & Struktur sichern 💾
              </button>
            </div>

          </div>

        </div>
      </div>

    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, reactive, computed } from 'vue'
import { useApiaryStore } from '../stores/apiary'
import BeehiveVisualizer from '../components/BeehiveVisualizer.vue'
import axios from 'axios'

const apiaryStore = useApiaryStore()

const hives = ref([])
const locations = ref([])
const frameTypes = ref([])
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
      fetchFrameTypes()
    ])
  }
})

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
        selectHive(refreshed)
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

function selectHive(hive) {
  selectedHive.value = hive
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

function onSelectBox(id) {
  selectedBoxId.value = id
}

function onUpdateBoxes(newBoxes) {
  editedBoxes.value = newBoxes
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
      showAlert('Vok erfolgreich aktualisiert!', 'success')
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
  if (!confirm(`Möchtest du das Volk "${hive.name}" wirklich auflösen/löschen? Dadurch werden alle Zargen und dazugehörigen Logbucheinträge gelöscht.`)) return
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
