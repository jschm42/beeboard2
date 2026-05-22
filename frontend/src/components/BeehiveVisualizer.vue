<template>
  <div class="w-full max-w-[340px] flex flex-col items-center justify-center p-6 md:p-7 border border-gray-300 dark:border-gray-700 rounded-3xl bg-white/90 dark:bg-dark-card/55 backdrop-blur-sm relative overflow-visible shadow-sm">

    <!-- Empty stack helper -->
    <div v-if="boxes.length === 0" class="w-full py-8 px-4 text-center text-gray-600 dark:text-gray-300 text-sm italic bg-gray-50/80 dark:bg-dark-bg/70 border border-dashed border-gray-300 dark:border-gray-600 rounded-2xl leading-relaxed">
      Keine Zargen definiert. Klicke auf
      <span class="font-bold text-primary not-italic">+ Zarge hinzufügen</span>,
      um den Stapel aufzubauen.
    </div>

    <!-- SVG Box Stack Container -->
    <div v-else class="space-y-2.5 w-full max-w-[260px] flex flex-col mb-1">
      <div 
        v-for="(box, idx) in sortedBoxes" 
        :key="box.id || idx"
        class="relative transition-all duration-300 transform cursor-grab active:cursor-grabbing"
        :class="[
          selectedBoxId === box.id ? 'scale-[1.02] z-10 shadow-xl' : '',
          draggedIdx === idx ? 'opacity-30 scale-[0.98]' : 'hover:scale-[1.02]',
          dragOverIdx === idx && draggedIdx !== idx ? 'scale-[1.04] z-20' : ''
        ]"
        draggable="true"
        @dragstart="onDragStart($event, idx)"
        @dragover.prevent
        @dragenter.prevent="onDragEnter(idx)"
        @dragleave="onDragLeave(idx)"
        @dragend="onDragEnd"
        @drop="onDrop(idx)"
      >
        <!-- Box Shape representation -->
        <div 
          @click="selectBox(box)"
          class="w-full h-20 rounded-2xl border-2 cursor-pointer transition-all duration-200 flex flex-col justify-center items-center shadow-md relative overflow-hidden"
          :class="[
            selectedBoxId === box.id 
              ? 'border-primary border-[4px] ring-8 ring-primary/30 shadow-2xl z-30' 
              : (dragOverIdx === idx && draggedIdx !== idx
                ? 'border-primary ring-4 ring-primary/40 shadow-lg'
                : 'border-amber-900/45 dark:border-amber-950/80'),
            box.box_type === 'BROOD'
              ? 'bg-gradient-to-r from-amber-600 to-amber-700 dark:from-amber-700 dark:to-amber-800 text-white'
              : 'bg-gradient-to-r from-yellow-400 to-yellow-500 dark:from-yellow-500 dark:to-yellow-600 text-gray-900'
          ]"
        >
          <!-- Text content overlay (Larger text!) -->
          <span class="text-base font-black tracking-wide z-10 uppercase">
            {{ box.box_type === 'BROOD' ? 'Brutraum' : 'Honigraum' }}
          </span>
          <span class="text-sm font-extrabold opacity-95 z-10">
            {{ box.frame_count }} Waben ({{ box.frame_type_name || 'Standard' }})
          </span>

        </div>

        <!-- Float Control Arrows displayed on hover / select -->
        <div 
          v-if="selectedBoxId === box.id" 
          class="absolute right-2 top-2 flex items-center gap-1 z-20 bg-white/95 dark:bg-dark-card/95 border border-gray-200 dark:border-dark-border p-1 rounded-lg shadow-lg animate-scale"
        >
          <button 
            type="button"
            @click.stop="moveUp(box)" 
            :disabled="box.order === boxes.length"
            class="p-1 rounded hover:bg-gray-100 dark:hover:bg-dark-border text-gray-700 dark:text-gray-200 disabled:opacity-30"
            title="Nach oben verschieben"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7"/></svg>
          </button>
          <button 
            type="button"
            @click.stop="moveDown(box)" 
            :disabled="box.order === 1"
            class="p-1 rounded hover:bg-gray-100 dark:hover:bg-dark-border text-gray-700 dark:text-gray-200 disabled:opacity-30"
            title="Nach unten verschieben"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
          </button>
          <button 
            type="button"
            @click.stop="deleteBox(box)"
            class="p-1 rounded hover:bg-red-500/10 text-red-500"
            title="Zarge löschen"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
          </button>
        </div>

      </div>
    </div>

    <!-- Legend Indicator -->
    <p v-if="boxes.length > 1" class="mt-5 text-[10px] font-semibold uppercase tracking-widest text-gray-500 dark:text-gray-400 text-center">
      Zargen per Drag and Drop umsortieren
    </p>

    <div class="flex space-x-4 mt-4 text-xs font-bold text-gray-600 dark:text-gray-300 uppercase tracking-wider">
      <div class="flex items-center space-x-1">
        <div class="w-3.5 h-3.5 bg-gradient-to-r from-amber-600 to-amber-700 border border-amber-800 rounded-sm"></div>
        <span>Brutraum</span>
      </div>
      <div class="flex items-center space-x-1">
        <div class="w-3.5 h-3.5 bg-gradient-to-r from-yellow-500 to-yellow-600 border border-yellow-700 rounded-sm"></div>
        <span>Honigraum</span>
      </div>
    </div>

  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useConfirmStore } from '../stores/confirm'

const confirmStore = useConfirmStore()

const props = defineProps({
  boxes: {
    type: Array,
    required: true,
    default: () => []
  },
  selectedBoxId: {
    type: String,
    default: null
  }
})

const emit = defineEmits(['select-box', 'update-boxes'])

// Drag & drop reactive states
const draggedIdx = ref(null)
const dragOverIdx = ref(null)

const sortedBoxes = computed(() => {
  // Sort boxes descending by their order so they render from top to bottom in normal flex-col
  return [...props.boxes].sort((a, b) => b.order - a.order)
})

function selectBox(box) {
  emit('select-box', box.id)
}

function onDragStart(event, idx) {
  draggedIdx.value = idx
  event.dataTransfer.effectAllowed = 'move'
  // Support Firefox and other standards-compliant drag engines
  event.dataTransfer.setData('text/plain', idx)
}

function onDragEnter(idx) {
  dragOverIdx.value = idx
}

function onDragLeave(idx) {
  if (dragOverIdx.value === idx) {
    dragOverIdx.value = null
  }
}

function onDragEnd() {
  draggedIdx.value = null
  dragOverIdx.value = null
}

function onDrop(dropIdx) {
  if (draggedIdx.value === null || draggedIdx.value === dropIdx) {
    draggedIdx.value = null
    dragOverIdx.value = null
    return
  }

  // Clone sortedBoxes
  const list = [...sortedBoxes.value]
  
  // Remove dragged box from its current position
  const [draggedBox] = list.splice(draggedIdx.value, 1)
  
  // Insert at new drop position
  list.splice(dropIdx, 0, draggedBox)
  
  // Re-map the 'order' property to match the new visual order (1..N descending)
  const updatedBoxes = list.map((box, index) => ({
    ...box,
    order: list.length - index
  }))
  
  emit('update-boxes', updatedBoxes)
  
  draggedIdx.value = null
  dragOverIdx.value = null
}

function moveUp(box) {
  const sorted = [...props.boxes].sort((a, b) => a.order - b.order)
  const currentIdx = sorted.findIndex(b => b.id === box.id)
  
  if (currentIdx < sorted.length - 1) {
    const nextBox = sorted[currentIdx + 1]
    
    // Swap order
    const oldOrder = box.order
    box.order = nextBox.order
    nextBox.order = oldOrder
    
    emit('update-boxes', [...props.boxes])
  }
}

function moveDown(box) {
  const sorted = [...props.boxes].sort((a, b) => a.order - b.order)
  const currentIdx = sorted.findIndex(b => b.id === box.id)
  
  if (currentIdx > 0) {
    const prevBox = sorted[currentIdx - 1]
    
    // Swap order
    const oldOrder = box.order
    box.order = prevBox.order
    prevBox.order = oldOrder
    
    emit('update-boxes', [...props.boxes])
  }
}

async function deleteBox(box) {
  const confirmed = await confirmStore.ask({
    title: 'Zarge entfernen',
    message: 'Möchtest du diese Zarge wirklich aus der Beute entfernen?',
    type: 'danger',
    confirmText: 'Ja, entfernen'
  })
  if (!confirmed) return
  
  // Filter out deleted box
  let remaining = props.boxes.filter(b => b.id !== box.id)
  
  // Recalculate order indices (ensure continuous 1..N order)
  remaining = remaining
    .sort((a, b) => a.order - b.order)
    .map((b, index) => {
      b.order = index + 1
      return b
    })
    
  emit('update-boxes', remaining)
  emit('select-box', null)
}
</script>

<style scoped>
.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: .7; }
}

.cursor-grab {
  cursor: grab;
}
.cursor-grabbing {
  cursor: grabbing;
}
</style>
