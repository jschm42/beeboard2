<template>
  <header class="mb-6 sm:mb-8 flex flex-col md:flex-row md:justify-between md:items-end gap-4">
    <div class="min-w-0">
      <h1 class="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white tracking-tight flex items-center gap-2.5">
        <span v-if="icon" aria-hidden="true">{{ icon }}</span>
        <slot name="title">{{ title }}</slot>
      </h1>
      <p v-if="subtitle || $slots.subtitle" class="text-sm sm:text-base text-gray-500 dark:text-gray-400 mt-1">
        <slot name="subtitle">{{ subtitle }}</slot>
      </p>
    </div>
    <div v-if="$slots.actions" class="flex flex-wrap items-center gap-2 md:justify-end shrink-0">
      <slot name="actions" />
    </div>
  </header>
</template>

<script setup>
defineProps({
  title: { type: String, default: '' },
  subtitle: { type: String, default: '' },
  icon: { type: String, default: '' },
})
</script>
