<template>
  <transition name="fade">
    <div
      v-if="modelValue"
      class="fixed inset-0 z-[90] flex items-center justify-center bg-black/50 backdrop-blur-sm p-4"
      @click.self="close"
    >
      <div class="w-full max-w-3xl max-h-[90vh] overflow-hidden rounded-2xl bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border shadow-2xl">
        <div class="px-6 py-4 border-b border-gray-200 dark:border-dark-border flex items-start justify-between gap-4">
          <div>
            <h2 class="text-lg font-extrabold text-gray-900 dark:text-white">About BeeBoard 2</h2>
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
              Third-party attributions and dependency acknowledgements.
            </p>
          </div>
          <button
            class="px-3 py-1.5 text-xs font-bold rounded-lg border border-gray-300 dark:border-dark-border text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-dark-bg"
            @click="close"
          >
            Close
          </button>
        </div>

        <div class="px-6 py-5 space-y-5 overflow-y-auto max-h-[calc(90vh-72px)] text-sm">
          <section class="space-y-2">
            <h3 class="font-bold text-gray-900 dark:text-white">APIs and services</h3>
            <ul class="list-disc pl-5 text-gray-700 dark:text-gray-300 space-y-1">
              <li>OpenWeatherMap API (optional weather and geocoding data).</li>
              <li>OpenStreetMap Nominatim fallback geocoding with OSM attribution requirements.</li>
              <li>LiteLLM routing for configured model providers (for example Gemini/OpenAI).</li>
            </ul>
          </section>

          <section class="space-y-2">
            <h3 class="font-bold text-gray-900 dark:text-white">Icons and brand assets</h3>
            <ul class="list-disc pl-5 text-gray-700 dark:text-gray-300 space-y-1">
              <li>Lucide icons via <span class="font-mono">lucide-vue-next</span> (ISC).</li>
              <li>Social logos in <span class="font-mono">frontend/public/icons.svg</span> follow brand/trademark rules of the respective platforms.</li>
              <li>Custom SVG assets in <span class="font-mono">assets/public</span> were generated with Recraft using paid credits.</li>
            </ul>
          </section>

          <section class="space-y-2">
            <h3 class="font-bold text-gray-900 dark:text-white">Fonts</h3>
            <ul class="list-disc pl-5 text-gray-700 dark:text-gray-300 space-y-1">
              <li>UI font stack: Outfit, Inter, then system fonts.</li>
              <li>No webfont files are bundled in this repository by default.</li>
            </ul>
          </section>

          <section class="space-y-2">
            <h3 class="font-bold text-gray-900 dark:text-white">Core frontend dependencies</h3>
            <p class="text-gray-700 dark:text-gray-300 leading-relaxed">
              vue (MIT), vue-router (MIT), pinia (MIT), axios (MIT), chart.js (MIT),
              dompurify (MPL-2.0 OR Apache-2.0), marked (MIT), tailwindcss (MIT),
              vite (MIT), lucide-vue-next (ISC),
              @vitejs/plugin-vue (MIT), @tailwindcss/vite (MIT), eslint ecosystem (MIT).
            </p>
          </section>

          <section class="space-y-2">
            <h3 class="font-bold text-gray-900 dark:text-white">Core backend dependencies</h3>
            <p class="text-gray-700 dark:text-gray-300 leading-relaxed">
              fastapi (MIT), uvicorn (BSD), sqlalchemy (MIT), pydantic (MIT),
              pydantic-settings (MIT), python-jose (MIT), bcrypt (Apache-2.0),
              python-multipart (Apache), litellm (MIT), pillow, pytest,
              httpx (BSD-3-Clause), pytest-asyncio, email-validator (Unlicense),
              apscheduler (MIT), alembic.
            </p>
          </section>

          <section class="space-y-2">
            <h3 class="font-bold text-gray-900 dark:text-white">Full notices</h3>
            <p class="text-gray-700 dark:text-gray-300 leading-relaxed">
              Please review <span class="font-mono">THIRD_PARTY_NOTICES.md</span> in the repository root for a detailed inventory and links to upstream terms.
            </p>
            <p class="text-gray-700 dark:text-gray-300 leading-relaxed">
              Thank you to all maintainers and contributors of the open-source projects and data services that make BeeBoard possible.
            </p>
          </section>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup>
defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:modelValue'])

function close() {
  emit('update:modelValue', false)
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
