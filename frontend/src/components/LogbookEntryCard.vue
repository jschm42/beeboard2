<template>
  <article class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-2xl p-4 sm:p-5 shadow-sm">
    <header class="flex items-start gap-3">
      <div class="flex-1 min-w-0">
        <div class="flex flex-wrap items-center gap-x-2 gap-y-1">
          <h4 class="text-sm font-bold text-gray-900 dark:text-white">{{ typeLabel }}</h4>
          <span v-if="entry.hive" class="px-2 py-0.5 rounded-md bg-primary/10 text-primary text-xs font-semibold">
            🐝 {{ entry.hive.name }}
          </span>
          <span
            v-if="entry.created_via_mcp"
            class="px-1.5 py-0.5 rounded-md bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400 text-[11px] font-semibold"
            :title="$t('logbook.mcp_badge_title')"
          >
            🤖 MCP
          </span>
        </div>
        <p class="text-xs text-gray-400 mt-0.5">
          {{ formatDate(entry.date) }}<template v-if="entry.created_by"> · {{ entry.created_by.username }}</template>
        </p>
      </div>

      <div class="flex items-center gap-0.5 flex-shrink-0">
        <template v-if="canAddImage">
          <label
            class="p-1.5 text-gray-400 hover:text-primary hover:bg-gray-100 dark:hover:bg-dark-bg rounded-lg transition-colors cursor-pointer"
            :title="$t('logbook.add_image')"
          >
            <ImagePlus class="w-4 h-4" />
            <input type="file" accept="image/*" class="hidden" @change="onFile" />
          </label>
          <label
            class="p-1.5 text-gray-400 hover:text-primary hover:bg-gray-100 dark:hover:bg-dark-bg rounded-lg transition-colors cursor-pointer sm:hidden"
            :title="$t('logbook.take_photo')"
          >
            <Camera class="w-4 h-4" />
            <input type="file" accept="image/*" capture="environment" class="hidden" @change="onFile" />
          </label>
        </template>
        <button
          type="button"
          class="p-1.5 text-gray-400 hover:text-primary hover:bg-gray-100 dark:hover:bg-dark-bg rounded-lg transition-colors"
          :title="$t('common.edit')"
          :aria-label="$t('common.edit')"
          @click="$emit('edit', entry)"
        >
          <Pencil class="w-4 h-4" />
        </button>
        <button
          type="button"
          class="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-500/10 rounded-lg transition-colors"
          :title="$t('common.delete')"
          :aria-label="$t('common.delete')"
          @click="$emit('delete', entry)"
        >
          <Trash2 class="w-4 h-4" />
        </button>
      </div>
    </header>

    <div v-if="hasBody" class="mt-3 space-y-3">
      <p v-if="entry.notes" class="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-line">{{ entry.notes }}</p>

      <LogbookInspectionSummary
        v-if="entry.entry_type === 'INSPECTION' && entry.inspection_detail"
        :inspection-detail="entry.inspection_detail"
      />

      <div v-if="entry.entry_type === 'VARROA_COUNT' && entry.varroa_count_detail" class="grid grid-cols-2 gap-3">
        <div class="p-3 rounded-xl bg-gray-50 dark:bg-dark-bg/60">
          <span class="block text-[11px] font-semibold text-gray-500">{{ $t('logbook.measured_mites_raw') }}</span>
          <span class="text-lg font-bold text-gray-900 dark:text-white">{{ $t('logbook.measured_mites_raw_val', { count: entry.varroa_count_detail.raw_count }) }}</span>
        </div>
        <div class="p-3 rounded-xl bg-red-500/5 dark:bg-red-500/10">
          <span class="block text-[11px] font-semibold text-gray-500">{{ $t('logbook.estimated_mites') }}</span>
          <span class="text-lg font-bold text-red-600 dark:text-red-400">{{ $t('logbook.estimated_mites_val', { count: Math.round(entry.varroa_count_detail.estimated_total).toLocaleString() }) }}</span>
        </div>
      </div>

      <div v-if="entry.entry_type === 'VARROA_TREATMENT' && entry.varroa_treatment_detail" class="p-3 rounded-xl bg-green-500/5 dark:bg-green-500/10 text-sm">
        <p class="font-semibold text-green-700 dark:text-green-400">
          {{ entry.varroa_treatment_detail.product }}<template v-if="entry.varroa_treatment_detail.dosage"> · {{ entry.varroa_treatment_detail.dosage }}</template>
        </p>
        <p v-if="entry.varroa_treatment_detail.treatment_notes" class="text-xs text-gray-500 mt-1">{{ entry.varroa_treatment_detail.treatment_notes }}</p>
      </div>

      <!-- Photos -->
      <div v-if="entry.images?.length" class="flex flex-wrap items-center gap-2">
        <div
          v-for="img in entry.images || []"
          :key="img.id"
          class="relative w-16 h-16 rounded-xl overflow-hidden border border-gray-100 dark:border-dark-border group"
        >
          <img
            :src="`/uploads/${img.thumbnail_path || img.image_path}`"
            :alt="$t('logbook.table_images')"
            class="w-full h-full object-cover cursor-pointer"
            @click="$emit('open-image', `/uploads/${img.image_path}`)"
          />
          <button
            type="button"
            class="absolute top-0.5 right-0.5 p-0.5 bg-red-500 text-white rounded-md shadow sm:opacity-0 sm:group-hover:opacity-100 transition-opacity"
            :title="$t('logbook.delete_image')"
            :aria-label="$t('logbook.delete_image')"
            @click="$emit('delete-image', img.id)"
          >
            <X class="w-3 h-3" />
          </button>
        </div>
      </div>
    </div>
  </article>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Camera, ImagePlus, Pencil, Trash2, X } from 'lucide-vue-next'
import LogbookInspectionSummary from './LogbookInspectionSummary.vue'
import { entryTypeLabel, formatLogDate } from '../utils/logbook'

const props = defineProps({
  entry: { type: Object, required: true },
})

const emit = defineEmits(['edit', 'delete', 'upload-image', 'delete-image', 'open-image'])

const MAX_IMAGES = 5

const { t, locale } = useI18n()

const typeLabel = computed(() => entryTypeLabel(props.entry, t))
const canAddImage = computed(() => (props.entry.images?.length || 0) < MAX_IMAGES)
const hasBody = computed(() => {
  const e = props.entry
  return Boolean(
    e.notes ||
    e.images?.length ||
    (e.entry_type === 'INSPECTION' && e.inspection_detail) ||
    (e.entry_type === 'VARROA_COUNT' && e.varroa_count_detail) ||
    (e.entry_type === 'VARROA_TREATMENT' && e.varroa_treatment_detail),
  )
})

function formatDate(value) {
  return formatLogDate(value, locale.value)
}

function onFile(event) {
  const file = event.target.files?.[0]
  event.target.value = ''
  if (file) emit('upload-image', props.entry.id, file)
}
</script>
