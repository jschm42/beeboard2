<template>
  <div class="flex flex-col items-center justify-center p-6 border border-gray-100 dark:border-dark-border rounded-3xl bg-gray-50/50 dark:bg-dark-card/30 backdrop-blur-sm relative overflow-hidden">
    
    <!-- Decorative wooden cover banner -->
    <div class="w-36 h-3.5 bg-amber-700/80 rounded-t-lg shadow-sm"></div>
    <div class="w-32 h-1 bg-amber-800 rounded-b-sm mb-2"></div>

    <!-- Empty stack helper -->
    <div v-if="boxes.length === 0" class="py-8 text-center text-gray-400 text-xs italic">
      Keine Zargen definiert. Klicke auf "+ Zarge hinzufügen", um den Stapel aufzubauen!
    </div>

    <!-- SVG Box Stack Container -->
    <div v-else class="space-y-1 w-full max-w-[240px] flex flex-col-reverse">
      <div 
        v-for="(box, idx) in sortedBoxes" 
        :key="box.id || idx"
        class="relative transition-all duration-300 transform"
        :class="[
          selectedBoxId === box.id ? 'scale-[1.03] z-10' : 'hover:scale-[1.01]',
        ]"
      >
        <!-- Box Shape representation -->
        <div 
          @click="selectBox(box)"
          class="w-full h-14 rounded-md border-2 cursor-pointer transition-all duration-200 flex flex-col justify-center items-center shadow-sm relative"
          :class="[
            selectedBoxId === box.id 
              ? 'border-primary ring-2 ring-primary/20 shadow-md' 
              : 'border-amber-900/40 dark:border-amber-950/70',
            box.box_type === 'BROOD'
              ? 'bg-gradient-to-r from-amber-600/90 to-amber-700/90 text-white'
              : 'bg-gradient-to-r from-yellow-500/90 to-yellow-600/90 text-gray-900'
          ]"
        >
          <!-- Wooden handle indentation in the middle -->
          <div 
            class="w-12 h-3.5 rounded-sm absolute left-1/2 -translate-x-1/2 opacity-70"
            :class="box.box_type === 'BROOD' ? 'bg-amber-800' : 'bg-yellow-700/30'"
          ></div>

          <!-- Text content overlay -->
          <span class="text-xs font-black tracking-wide z-10 uppercase">
            {{ box.box_type === 'BROOD' ? 'Brutraum' : 'Honigraum' }}
          </span>
          <span class="text-[10px] font-bold opacity-80 z-10">
            {{ box.frame_count }} Waben ({{ box.frame_type_name || 'Standard' }})
          </span>

          <!-- Left Side: Order Indicator -->
          <span class="absolute left-3 text-[10px] font-black opacity-40">
            #{{ box.order }}
          </span>
        </div>

        <!-- Float Control Arrows displayed on hover / select -->
        <div 
          v-if="selectedBoxId === box.id" 
          class="absolute -right-12 top-1/2 -translate-y-1/2 flex flex-col space-y-1 z-20 bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border p-1 rounded-lg shadow-lg"
        >
          <button 
            type="button"
            @click.stop="moveUp(box)" 
            :disabled="box.order === boxes.length"
            class="p-1 rounded hover:bg-gray-100 dark:hover:bg-dark-border text-gray-600 dark:text-gray-300 disabled:opacity-30"
            title="Nach oben verschieben"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7"/></svg>
          </button>
          <button 
            type="button"
            @click.stop="moveDown(box)" 
            :disabled="box.order === 1"
            class="p-1 rounded hover:bg-gray-100 dark:hover:bg-dark-border text-gray-600 dark:text-gray-300 disabled:opacity-30"
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

    <!-- Entrance flight board design at the bottom -->
    <div class="w-40 h-2 bg-amber-800 rounded-sm mt-3 relative flex justify-center shadow-sm">
      <!-- Flight hole gate -->
      <div class="w-14 h-1.5 bg-black rounded-t-sm absolute -top-1.5"></div>
      <div class="w-24 h-3 bg-amber-700/60 rounded-b-md skew-x-12 translate-y-1 shadow-md"></div>
    </div>

    <!-- Legend Indicator -->
    <div class="flex space-x-4 mt-8 text-[10px] font-bold text-gray-500 uppercase tracking-wider">
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
import { computed } from 'vue'

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

const sortedBoxes = computed(() => {
  // Sort boxes ascending by their order (so higher order boxes appear higher up in flex-reverse rendering)
  return [...props.boxes].sort((a, b) => a.order - b.order)
})

function selectBox(box) {
  emit('select-box', box.id)
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

function deleteBox(box) {
  if (!confirm('Möchtest du diese Zarge wirklich aus der Beute entfernen?')) return
  
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
</style>
