<template>
  <div v-if="summary">
    <!-- Compact: totals only, as chips (table view) -->
    <div v-if="compact" class="flex flex-wrap gap-1.5">
      <span
        v-for="cat in visibleCategories"
        :key="cat.key"
        class="inline-flex items-center gap-1 px-2 py-0.5 rounded-lg text-[11px] font-semibold"
        :class="cat.chipClass"
      >
        {{ $t(cat.label) }}
        <span class="font-mono font-bold">{{ format(summary.total[cat.key], cat.unit) }}</span>
      </span>
    </div>

    <!-- Full: categories x boxes matrix with colony total -->
    <div v-else class="overflow-x-auto rounded-2xl border border-gray-100 dark:border-dark-border">
      <table class="w-full text-xs">
        <thead>
          <tr class="bg-gray-50 dark:bg-dark-bg/60 text-gray-500 dark:text-gray-400">
            <th class="px-3 py-2 text-left font-semibold" />
            <th
              v-for="box in summary.boxes"
              :key="box.key"
              class="px-3 py-2 text-right font-semibold whitespace-nowrap"
            >
              {{ $t('logbook.box_short', { order: box.order }) }}
            </th>
            <th v-if="summary.boxes.length > 1" class="px-3 py-2 text-right font-bold text-gray-700 dark:text-gray-200 whitespace-nowrap">
              {{ $t('logbook.colony_total') }}
            </th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100 dark:divide-dark-border">
          <tr v-for="cat in visibleCategories" :key="cat.key">
            <td class="px-3 py-1.5 font-semibold whitespace-nowrap" :class="cat.textClass">
              {{ $t(cat.label) }}
            </td>
            <td
              v-for="box in summary.boxes"
              :key="box.key"
              class="px-3 py-1.5 text-right font-mono text-gray-700 dark:text-gray-300"
            >
              {{ format(box.values[cat.key], cat.unit) }}
            </td>
            <td v-if="summary.boxes.length > 1" class="px-3 py-1.5 text-right font-mono font-bold text-gray-900 dark:text-white">
              {{ format(summary.total[cat.key], cat.unit) }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
  <p v-else class="text-xs text-gray-400 italic">{{ $t('logbook.box_calc_error') }}</p>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  inspectionDetail: { type: Object, default: null },
  compact: { type: Boolean, default: false },
})

const CATEGORIES = [
  { key: 'brood', field: 'brood_total', label: 'logbook.brood', unit: '', textClass: 'text-amber-600 dark:text-amber-400', chipClass: 'bg-amber-500/10 text-amber-700 dark:text-amber-400' },
  { key: 'bees', field: 'bee_total', label: 'logbook.bees', unit: '', textClass: 'text-green-600 dark:text-green-400', chipClass: 'bg-green-500/10 text-green-700 dark:text-green-400' },
  { key: 'drones', field: 'drone_total', label: 'logbook.drones', unit: '', textClass: 'text-sky-600 dark:text-sky-400', chipClass: 'bg-sky-500/10 text-sky-700 dark:text-sky-400' },
  { key: 'drone_brood', field: 'drone_brood_total', label: 'logbook.drone_brood', unit: '', textClass: 'text-orange-600 dark:text-orange-400', chipClass: 'bg-orange-500/10 text-orange-700 dark:text-orange-400' },
  { key: 'pollen', field: 'pollen_total', label: 'logbook.pollen', unit: 'g', textClass: 'text-purple-600 dark:text-purple-400', chipClass: 'bg-purple-500/10 text-purple-700 dark:text-purple-400' },
  { key: 'food', field: 'food_total', label: 'logbook.food', unit: 'g', textClass: 'text-yellow-600 dark:text-yellow-400', chipClass: 'bg-yellow-500/10 text-yellow-700 dark:text-yellow-400' },
]

// -1 / null mean "category not recorded"
function recorded(value) {
  return value !== null && value !== undefined && value !== -1
}

const summary = computed(() => {
  const rawBoxes = props.inspectionDetail?.boxes
  if (!rawBoxes || rawBoxes.length === 0) return null

  const boxes = [...rawBoxes]
    .sort((a, b) => (a.box_index ?? 0) - (b.box_index ?? 0))
    .map((b, idx) => ({
      key: b.id || `box-${idx}`,
      order: (b.box_index ?? idx) + 1,
      values: Object.fromEntries(CATEGORIES.map(c => [c.key, recorded(b[c.field]) ? b[c.field] : null])),
    }))

  const total = Object.fromEntries(CATEGORIES.map(c => {
    const values = boxes.map(b => b.values[c.key]).filter(v => v !== null)
    return [c.key, values.length ? values.reduce((sum, v) => sum + v, 0) : null]
  }))

  return { boxes, total }
})

const visibleCategories = computed(() =>
  summary.value ? CATEGORIES.filter(c => summary.value.total[c.key] !== null) : [],
)

function format(value, unit) {
  if (value === null || value === undefined) return '–'
  const rounded = Math.round(Number(value)).toLocaleString()
  return unit ? `${rounded} ${unit}` : rounded
}
</script>
