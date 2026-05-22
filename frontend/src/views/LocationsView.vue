<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 font-sans">
    
    <!-- Back to Dashboard Link -->
    <router-link to="/dashboard" class="inline-flex items-center text-sm font-semibold text-primary hover:text-primary-hover mb-4 transition-colors duration-200">
      <svg class="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"/></svg>
      Zurück zum Dashboard
    </router-link>

    <!-- Header Area -->
    <div class="mb-8 flex flex-col sm:flex-row sm:justify-between sm:items-center space-y-4 sm:space-y-0">
      <div>
        <h1 class="text-3xl font-extrabold text-gray-900 dark:text-white tracking-tight">📍 Standorte</h1>
        <p class="text-gray-500 dark:text-gray-400 mt-1">Verwalte die geografischen Standorte deiner Bienenstände.</p>
      </div>
      <button 
        @click="openCreateModal" 
        class="px-5 py-2.5 bg-primary hover:bg-primary-hover text-white font-extrabold text-sm rounded-xl shadow-md shadow-primary/20 hover-scale flex items-center justify-center space-x-2"
      >
        <span>+ Neuer Standort</span>
      </button>
    </div>

    <!-- Alert Message -->
    <div v-if="alertMessage" class="mb-6 p-4 rounded-xl text-sm flex items-start space-x-2" :class="alertClass">
      <svg class="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
      <span>{{ alertMessage }}</span>
    </div>

    <!-- Create/Edit Form (Inline, embedded on page) -->
    <div v-if="showModal" class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl shadow-md w-full max-w-2xl mx-auto p-6 mb-8 animate-scale">
      <div class="flex justify-between items-center mb-6 pb-4 border-b border-gray-100 dark:border-dark-border">
        <h3 class="text-xl font-bold text-gray-900 dark:text-white">
          {{ isEditMode ? '📍 Standort bearbeiten' : '📍 Neuen Standort anlegen' }}
        </h3>
        <button @click="closeModal" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
        </button>
      </div>
      
      <form @submit.prevent="submitForm">
        <div class="space-y-4">
          
          <div>
            <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">Name des Bienenstands *</label>
            <input 
              v-model="form.name" 
              type="text" 
              required
              placeholder="z.B. Waldrand Beutenbach"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm"
            />
          </div>

          <div>
            <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">Adresse</label>
            <div class="flex gap-2">
              <input 
                v-model="form.address" 
                type="text" 
                placeholder="z.B. Beutenweg 12, 70190 Stuttgart"
                class="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm"
              />
              <button 
                type="button"
                @click="lookupCoordinates"
                :disabled="geocoding"
                class="px-3 py-2 bg-gray-100 hover:bg-gray-200 dark:bg-dark-bg dark:hover:bg-dark-border border border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-300 text-xs font-bold rounded-xl shadow-sm hover-scale transition-all flex items-center gap-1.5 shrink-0 disabled:opacity-50"
              >
                <span v-if="geocoding">
                  <svg class="animate-spin h-3.5 w-3.5 text-gray-500" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                </span>
                <span v-else>🔍 Suchen</span>
              </button>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">Breitengrad (Lat)</label>
              <input 
                v-model="form.latitude" 
                type="number" 
                step="any"
                placeholder="z.B. 48.7758"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm font-mono"
              />
            </div>
            <div>
              <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">Längengrad (Lng)</label>
              <input 
                v-model="form.longitude" 
                type="number" 
                step="any"
                placeholder="z.B. 9.1829"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm font-mono"
              />
            </div>
          </div>

          <div>
            <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">Anmerkungen</label>
            <textarea 
              v-model="form.notes" 
              placeholder="z.B. Schattiger Platz am Vormittag, gute Trachtbedingungen durch nahe Rapsfelder..."
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

    <!-- Loading State -->
    <div v-if="loading" class="flex flex-col items-center justify-center py-20">
      <svg class="animate-spin h-10 w-10 text-primary mb-4" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
      <p class="text-gray-500 dark:text-gray-400 font-bold">Lade Standorte...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="!showModal && locations.length === 0" class="glass rounded-3xl p-12 text-center max-w-lg mx-auto border border-dashed border-gray-300 dark:border-gray-700 mt-8">
      <div class="text-4xl mb-4">📍</div>
      <h3 class="text-lg font-bold text-gray-800 dark:text-white mb-1">Keine Bienenstandorte vorhanden</h3>
      <p class="text-gray-500 dark:text-gray-400 mb-6">Erstelle deinen ersten Standort, um danach Bienenvölker dort ansiedeln zu können.</p>
      <button @click="openCreateModal" class="px-5 py-2.5 bg-primary hover:bg-primary-hover text-white font-extrabold text-sm rounded-xl shadow-md hover-scale">
        + Neuen Standort erstellen
      </button>
    </div>

    <!-- Locations Grid -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div 
        v-for="loc in locations" 
        :key="loc.id" 
        class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-6 shadow-sm flex flex-col justify-between hover-scale relative overflow-hidden"
      >
        <!-- Decorative subtle background badge -->
        <div class="absolute right-0 top-0 text-[100px] opacity-5 select-none pointer-events-none translate-x-10 -translate-y-8 font-black">
          MAP
        </div>

        <div>
          <div class="flex justify-between items-start mb-4">
            <h3 class="text-lg font-bold text-gray-900 dark:text-white truncate max-w-[200px]" :title="loc.name">
              {{ loc.name }}
            </h3>
            <span class="px-2.5 py-1 bg-primary/10 text-primary text-xs font-extrabold rounded-full shrink-0">
              {{ loc.hives?.length || 0 }} Völker
            </span>
          </div>

          <!-- Metadata -->
          <div class="space-y-2 mb-6 text-sm text-gray-600 dark:text-gray-400">
            <div v-if="loc.address" class="flex items-start space-x-2">
              <svg class="w-4 h-4 shrink-0 text-gray-400 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
              <span class="line-clamp-2">{{ loc.address }}</span>
            </div>
            
            <div v-if="loc.latitude || loc.longitude" class="flex items-center space-x-2">
              <svg class="w-4 h-4 shrink-0 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"/></svg>
              <span class="font-mono text-xs">{{ loc.latitude?.toFixed(5) }}, {{ loc.longitude?.toFixed(5) }}</span>
            </div>

            <div v-if="loc.notes" class="mt-3 pt-3 border-t border-gray-100 dark:border-dark-border italic text-xs text-gray-500">
              "{{ loc.notes }}"
            </div>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="flex items-center justify-end space-x-2 border-t border-gray-100 dark:border-dark-border pt-4">
          <button 
            @click="openEditModal(loc)" 
            class="p-2 text-gray-500 hover:text-primary hover:bg-gray-100 dark:hover:bg-dark-border rounded-xl transition-all duration-150 hover-scale"
            title="Bearbeiten"
          >
            <svg class="w-4.5 h-4.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/></svg>
          </button>
          <button 
            @click="deleteLocation(loc)" 
            class="p-2 text-gray-400 hover:text-red-500 hover:bg-red-500/10 rounded-xl transition-all duration-150 hover-scale"
            title="Löschen"
          >
            <svg class="w-4.5 h-4.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
          </button>
        </div>

      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { useApiaryStore } from '../stores/apiary'
import { useConfirmStore } from '../stores/confirm'
import axios from 'axios'

const apiaryStore = useApiaryStore()
const confirmStore = useConfirmStore()

const locations = ref([])
const loading = ref(false)
const showModal = ref(false)
const isEditMode = ref(false)
const editingId = ref(null)

const alertMessage = ref('')
const alertClass = ref('')
const geocoding = ref(false)

const form = reactive({
  name: '',
  address: '',
  latitude: null,
  longitude: null,
  notes: ''
})

onMounted(async () => {
  if (apiaryStore.activeApiaryId) {
    await fetchLocations()
  }
})

async function fetchLocations() {
  loading.value = true
  try {
    const response = await axios.get('/api/locations', {
      params: { apiary_id: apiaryStore.activeApiaryId }
    })
    locations.value = response.data
  } catch (err) {
    console.error('Fetch locations error:', err)
    showAlert('Fehler beim Laden der Standorte.', 'error')
  } finally {
    loading.value = false
  }
}

function openCreateModal() {
  isEditMode.value = false
  editingId.value = null
  form.name = ''
  form.address = ''
  form.latitude = null
  form.longitude = null
  form.notes = ''
  showModal.value = true
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function openEditModal(loc) {
  isEditMode.value = true
  editingId.value = loc.id
  form.name = loc.name
  form.address = loc.address || ''
  form.latitude = loc.latitude
  form.longitude = loc.longitude
  form.notes = loc.notes || ''
  showModal.value = true
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function closeModal() {
  showModal.value = false
}

async function lookupCoordinates() {
  const query = form.address.trim()
  if (!query) {
    showAlert('Bitte gib zuerst eine Adresse ein.', 'error')
    return
  }
  geocoding.value = true
  try {
    const res = await axios.get('/api/locations/geocode', {
      params: { address: query }
    })
    form.latitude = Number(res.data.lat.toFixed(6))
    form.longitude = Number(res.data.lon.toFixed(6))
    showAlert(`Koordinaten gefunden: ${res.data.name || query} (${res.data.country || ''})`, 'success')
  } catch (err) {
    console.error('Geocoding error:', err)
    showAlert(err.response?.data?.detail || 'Adresse konnte nicht aufgelöst werden.', 'error')
  } finally {
    geocoding.value = false
  }
}

async function submitForm() {
  if (!form.name.trim()) return
  if (!apiaryStore.activeApiaryId) {
    showAlert('Kein Bienenstand ausgewählt. Bitte wähle zuerst eine Imkerei aus.', 'error')
    return
  }
  try {
    const payload = {
      name: form.name.trim(),
      address: form.address.trim() || null,
      latitude: form.latitude ? parseFloat(form.latitude) : null,
      longitude: form.longitude ? parseFloat(form.longitude) : null,
      notes: form.notes.trim() || null
    }

    if (isEditMode.value) {
      await axios.put(`/api/locations/${editingId.value}`, payload)
      showAlert('Standort erfolgreich aktualisiert!', 'success')
    } else {
      await axios.post('/api/locations', payload, {
        params: { apiary_id: apiaryStore.activeApiaryId }
      })
      showAlert('Standort erfolgreich angelegt!', 'success')
    }
    
    showModal.value = false
    await fetchLocations()
  } catch (err) {
    console.error('Submit location error:', err)
    showAlert(err.response?.data?.detail || 'Fehler beim Speichern des Standorts.', 'error')
  }
}

async function deleteLocation(loc) {
  const confirmed = await confirmStore.ask({
    title: 'Standort löschen',
    message: `Möchtest du den Standort "${loc.name}" wirklich löschen?`,
    type: 'danger',
    confirmText: 'Ja, löschen'
  })
  if (!confirmed) return
  try {
    await axios.delete(`/api/locations/${loc.id}`)
    showAlert('Standort erfolgreich gelöscht.', 'success')
    await fetchLocations()
  } catch (err) {
    console.error('Delete location error:', err)
    showAlert(err.response?.data?.detail || 'Fehler beim Löschen des Standorts.', 'error')
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
