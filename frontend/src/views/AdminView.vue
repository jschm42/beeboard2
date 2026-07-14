<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 font-sans">
    
    <!-- Back to Dashboard Link -->
    <router-link to="/dashboard" class="inline-flex items-center text-sm font-semibold text-primary hover:text-primary-hover mb-4 transition-colors duration-200">
      <svg class="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"/></svg>
      {{ $t('admin.back_to_dashboard') }}
    </router-link>

    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-extrabold text-gray-900 dark:text-white tracking-tight">{{ $t('admin.title') }}</h1>
      <p class="text-gray-500 dark:text-gray-400 mt-1">{{ $t('admin.subtitle') }}</p>
    </div>

    <!-- Toast Notifications -->
    <TransitionGroup 
      name="list" 
      tag="div" 
      class="fixed bottom-5 right-5 z-50 space-y-2 pointer-events-none"
    >
      <div 
        v-for="t in toasts" 
        :key="t.id" 
        class="flex items-center space-x-3 px-4 py-3 rounded-xl shadow-lg border text-sm font-semibold pointer-events-auto backdrop-blur-md"
        :class="[
          t.type === 'success' 
            ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-600 dark:text-emerald-400' 
            : 'bg-rose-500/10 border-rose-500/20 text-rose-600 dark:text-rose-400'
        ]"
      >
        <span>{{ t.type === 'success' ? '✅' : '⚠️' }}</span>
        <span>{{ t.message }}</span>
      </div>
    </TransitionGroup>

    <!-- Tabs Dock -->
    <div class="flex border-b border-gray-200 dark:border-dark-border mb-8 space-x-6">
      <button 
        @click="activeTab = 'users'"
        class="pb-4 text-sm font-bold tracking-wide border-b-2 transition-all duration-200"
        :class="[
          activeTab === 'users' 
            ? 'border-primary text-primary' 
            : 'border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
        ]"
      >
        {{ $t('admin.tab_users') }}
      </button>
      <button 
        @click="activeTab = 'llm'"
        class="pb-4 text-sm font-bold tracking-wide border-b-2 transition-all duration-200"
        :class="[
          activeTab === 'llm' 
            ? 'border-primary text-primary' 
            : 'border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
        ]"
      >
        {{ $t('admin.tab_llm') }}
      </button>
      <button 
        @click="activeTab = 'finance'"
        class="pb-4 text-sm font-bold tracking-wide border-b-2 transition-all duration-200"
        :class="[
          activeTab === 'finance' 
            ? 'border-primary text-primary' 
            : 'border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
        ]"
      >
        {{ $t('admin.tab_finance') }}
      </button>
      <button 
        @click="activeTab = 'frame-types'"
        class="pb-4 text-sm font-bold tracking-wide border-b-2 transition-all duration-200"
        :class="[
          activeTab === 'frame-types' 
            ? 'border-primary text-primary' 
            : 'border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
        ]"
      >
        {{ $t('admin.tab_frame_types') }}
      </button>
      <button 
        @click="activeTab = 'number-ranges'"
        class="pb-4 text-sm font-bold tracking-wide border-b-2 transition-all duration-200"
        :class="[
          activeTab === 'number-ranges' 
            ? 'border-primary text-primary' 
            : 'border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
        ]"
      >
        {{ $t('admin.tab_number_ranges') }}
      </button>
      <button 
        @click="activeTab = 'treatment-methods'"
        class="pb-4 text-sm font-bold tracking-wide border-b-2 transition-all duration-200"
        :class="[
          activeTab === 'treatment-methods' 
            ? 'border-primary text-primary' 
            : 'border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
        ]"
      >
        {{ $t('admin.tab_treatment_methods') }}
      </button>
      <button 
        @click="activeTab = 'treatment-application-types'"
        class="pb-4 text-sm font-bold tracking-wide border-b-2 transition-all duration-200"
        :class="[
          activeTab === 'treatment-application-types' 
            ? 'border-primary text-primary' 
            : 'border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
        ]"
      >
        {{ $t('admin.tab_treatment_application_types') }}
      </button>
    </div>

    <!-- Tab Content: User Management -->
    <div v-if="activeTab === 'users'" class="space-y-6">
      <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-6 shadow-sm">
        <h2 class="text-lg font-bold text-gray-900 dark:text-white">{{ $t('admin.create_user_title') }}</h2>
        <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">{{ $t('admin.create_user_desc') }}</p>

        <form @submit.prevent="createUser" class="mt-5 grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('admin.username_label') }}</label>
            <input v-model="newUserForm.username" type="text" required class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary" />
          </div>
          <div>
            <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('admin.email_label') }}</label>
            <input v-model="newUserForm.email" type="email" required class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary" />
          </div>
          <div>
            <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('admin.first_name_label') }}</label>
            <input v-model="newUserForm.first_name" type="text" class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary" />
          </div>
          <div>
            <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('admin.last_name_label') }}</label>
            <input v-model="newUserForm.last_name" type="text" class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary" />
          </div>
          <div>
            <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('admin.password_label') }}</label>
            <input v-model="newUserForm.password" type="password" minlength="8" required class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary" />
          </div>
          <div>
            <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('admin.role_label') }}</label>
            <select v-model="newUserForm.role" class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary">
              <option value="USER">USER</option>
              <option value="SYSTEM_ADMIN">SYSTEM_ADMIN</option>
            </select>
          </div>
          <div class="md:col-span-2 flex justify-end">
            <button type="submit" :disabled="creatingUser" class="px-5 py-2.5 bg-primary hover:bg-primary-hover text-white text-sm font-bold rounded-xl transition duration-200 disabled:opacity-60">
              {{ creatingUser ? $t('admin.creating_user_loading') : $t('admin.create_user_btn') }}
            </button>
          </div>
        </form>
      </div>

      <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl overflow-hidden shadow-sm">
        <div class="px-6 py-5 border-b border-gray-100 dark:border-dark-border">
          <h2 class="text-lg font-bold text-gray-900 dark:text-white">{{ $t('admin.registered_users_title') }}</h2>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">{{ $t('admin.registered_users_desc') }}</p>
        </div>

        <div v-if="loadingUsers" class="flex flex-col items-center justify-center py-20">
          <svg class="animate-spin h-8 w-8 text-primary mb-3" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
          <span class="text-xs text-gray-400 font-bold">{{ $t('admin.loading_users') }}</span>
        </div>

        <div v-else class="overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="bg-gray-50 dark:bg-dark-bg text-gray-500 dark:text-gray-400 text-[10px] font-bold uppercase tracking-wider border-b border-gray-100 dark:border-dark-border">
                <th class="px-6 py-4">{{ $t('admin.table_username') }}</th>
                <th class="px-6 py-4">{{ $t('admin.table_name') }}</th>
                <th class="px-6 py-4">{{ $t('admin.table_email') }}</th>
                <th class="px-6 py-4 text-center">{{ $t('admin.table_status') }}</th>
                <th class="px-6 py-4 text-center">{{ $t('admin.table_role') }}</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100 dark:divide-dark-border text-sm">
              <tr 
                v-for="u in sortedUsers" 
                :key="u.id" 
                class="hover:bg-gray-50/50 dark:hover:bg-dark-bg/30 transition-colors duration-150"
              >
                <!-- Username -->
                <td class="px-6 py-4 font-bold text-gray-800 dark:text-gray-200">
                  <div class="flex items-center space-x-2">
                    <span>{{ u.username }}</span>
                    <span 
                      v-if="u.id === authStore.user?.id" 
                      class="text-[9px] bg-primary/10 text-primary px-1.5 py-0.5 rounded font-black tracking-wide uppercase"
                    >
                      {{ $t('admin.you_badge') }}
                    </span>
                  </div>
                </td>
                
                <!-- Name -->
                <td class="px-6 py-4 text-gray-600 dark:text-gray-300">
                  {{ u.first_name || '-' }} {{ u.last_name || '' }}
                </td>
                
                <!-- Email -->
                <td class="px-6 py-4 text-gray-500 dark:text-gray-400">
                  {{ u.email }}
                </td>
                
                <!-- Active Toggle -->
                <td class="px-6 py-4">
                  <div class="flex items-center justify-center">
                    <button 
                      @click="toggleUserActive(u)" 
                      :disabled="u.id === authStore.user?.id || togglingUser === u.id"
                      class="relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none"
                      :class="[
                        u.is_active ? 'bg-emerald-500' : 'bg-gray-300 dark:bg-gray-700',
                        (u.id === authStore.user?.id) ? 'opacity-40 cursor-not-allowed' : ''
                      ]"
                    >
                      <span class="sr-only">{{ $t('admin.toggle_status_title') }}</span>
                      <span 
                        class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out"
                        :class="u.is_active ? 'translate-x-5' : 'translate-x-0'"
                      />
                    </button>
                    <span 
                      v-if="u.id === authStore.user?.id" 
                      class="ml-2 text-gray-400 text-xs cursor-help" 
                      :title="$t('admin.cannot_deactivate_self')"
                    >
                      🔒
                    </span>
                  </div>
                </td>
                
                <!-- Role Toggle -->
                <td class="px-6 py-4">
                  <div class="flex items-center justify-center">
                    <select 
                      v-model="u.role" 
                      @change="changeUserRole(u)"
                      :disabled="u.id === authStore.user?.id || togglingUser === u.id"
                      class="px-2 py-1 bg-white dark:bg-dark-bg border border-gray-300 dark:border-gray-700 rounded-lg text-xs font-semibold focus:outline-none focus:ring-1 focus:ring-primary cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed text-gray-800 dark:text-gray-200"
                    >
                      <option value="USER">USER</option>
                      <option value="SYSTEM_ADMIN">SYSTEM_ADMIN</option>
                    </select>
                    <span 
                      v-if="u.id === authStore.user?.id" 
                      class="ml-2 text-gray-400 text-xs cursor-help" 
                      :title="$t('admin.cannot_demote_self')"
                    >
                      🔒
                    </span>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Tab Content: LLM & Weather Configuration -->
    <div v-if="activeTab === 'llm'" class="space-y-6">
      
      <div v-if="loadingLLM" class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-16 flex flex-col items-center justify-center shadow-sm">
        <svg class="animate-spin h-10 w-10 text-primary mb-4" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
        <span class="text-sm text-gray-400 font-bold">{{ $t('admin.loading_config') }}</span>
      </div>

      <div v-else class="grid grid-cols-1 gap-8">
        
        <!-- Live Weather API Switch -->
        <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-6 shadow-sm space-y-4">
          <div class="flex items-start justify-between">
            <div class="space-y-1">
              <h3 class="text-base font-bold text-gray-900 dark:text-white flex items-center">
                <span>{{ $t('admin.weather_title') }}</span>
                <span class="ml-2 text-[10px] bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 px-1.5 py-0.5 rounded uppercase font-black">OpenWeatherMap API</span>
              </h3>
              <p class="text-xs text-gray-500 dark:text-gray-400 max-w-2xl">
                {{ $t('admin.weather_desc') }}
              </p>
            </div>
            
            <button 
              @click="llmConfig.enable_weather_api = !llmConfig.enable_weather_api" 
              class="relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none"
              :class="llmConfig.enable_weather_api ? 'bg-emerald-500' : 'bg-gray-300 dark:bg-gray-700'"
            >
              <span class="sr-only">{{ $t('admin.weather_title') }}</span>
              <span 
                class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out"
                :class="llmConfig.enable_weather_api ? 'translate-x-5' : 'translate-x-0'"
              />
            </button>
          </div>
        </div>

        <!-- AI Insights Cron Jobs -->
        <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-6 shadow-sm space-y-4">
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-base font-bold text-gray-900 dark:text-white">{{ $t('admin.cron_jobs_title') }}</h3>
              <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">{{ $t('admin.cron_jobs_subtitle') }}</p>
            </div>
            <button
              @click="openCreateAIInsightJob"
              class="px-3 py-2 bg-primary hover:bg-primary-hover text-white rounded-xl text-xs font-bold"
            >
              {{ $t('admin.new_cron_job_btn') }}
            </button>
          </div>

          <div v-if="loadingAIInsightJobs" class="text-xs text-gray-400 font-bold">{{ $t('admin.loading_cron_jobs') }}</div>
          <div v-else-if="aiInsightJobs.length === 0" class="text-xs text-gray-500 dark:text-gray-400">{{ $t('admin.no_cron_jobs') }}</div>
          <div v-else class="space-y-2">
            <div
              v-for="job in aiInsightJobs"
              :key="job.id"
              class="border border-gray-200 dark:border-dark-border rounded-xl p-3 flex items-center justify-between gap-3"
            >
              <div class="min-w-0">
                <div class="text-sm font-bold text-gray-900 dark:text-white truncate">{{ job.name }}</div>
                <div class="text-xs font-mono text-gray-500 dark:text-gray-400">{{ job.cron_expression }}</div>
                <div class="mt-1 flex flex-wrap gap-1">
                  <span v-if="job.inject_weather" class="px-1.5 py-0.5 rounded bg-sky-500/10 text-sky-700 dark:text-sky-300 text-[10px] font-bold">{{ $t('admin.weather_badge') }}</span>
                  <span v-if="job.inject_apiary" class="px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-700 dark:text-amber-300 text-[10px] font-bold">{{ $t('admin.apiary_badge') }}</span>
                  <span v-if="job.inject_locations" class="px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-700 dark:text-emerald-300 text-[10px] font-bold">{{ $t('admin.locations_badge') }}</span>
                  <span v-if="job.inject_hives" class="px-1.5 py-0.5 rounded bg-indigo-500/10 text-indigo-700 dark:text-indigo-300 text-[10px] font-bold">{{ $t('admin.hives_badge') }}</span>
                  <span v-if="job.inject_log_entries" class="px-1.5 py-0.5 rounded bg-rose-500/10 text-rose-700 dark:text-rose-300 text-[10px] font-bold">{{ $t('admin.logs_badge', { scope: job.log_scope, max: job.max_log_entries }) }}</span>
                </div>
              </div>
              <div class="flex items-center gap-2">
                <span
                  class="px-2 py-0.5 rounded-full text-[10px] font-bold"
                  :class="job.is_active ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400' : 'bg-gray-200 dark:bg-gray-700 text-gray-500'"
                >
                  {{ job.is_active ? $t('common.active') : $t('common.inactive') }}
                </span>
                <button @click="openEditAIInsightJob(job)" class="px-2 py-1 text-xs font-bold border border-gray-300 dark:border-gray-700 rounded-lg">{{ $t('common.edit') }}</button>
                <button @click="deleteAIInsightJob(job)" class="px-2 py-1 text-xs font-bold border border-red-300 dark:border-red-900/60 text-red-600 dark:text-red-300 rounded-lg">{{ $t('common.delete') }}</button>
              </div>
            </div>
          </div>

          <div v-if="showAIInsightJobForm" class="border border-gray-200 dark:border-dark-border rounded-2xl p-4 space-y-3">
            <div class="text-sm font-bold text-gray-900 dark:text-white">{{ editingAIInsightJobId ? $t('admin.edit_cron_job_title') : $t('admin.create_cron_job_title') }}</div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div>
                <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('admin.cron_name_label') }}</label>
                <input v-model="aiInsightJobForm.name" type="text" class="w-full px-3 py-2 border border-gray-300 dark:border-dark-border dark:bg-dark-bg dark:text-white rounded-xl text-sm" />
              </div>
              <div>
                <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('admin.cron_expression_label') }}</label>
                <input v-model="aiInsightJobForm.cron_expression" type="text" placeholder="0 */12 * * *" class="w-full px-3 py-2 border border-gray-300 dark:border-dark-border dark:bg-dark-bg dark:text-white rounded-xl text-sm font-mono" />
                <p class="text-[11px] text-gray-500 dark:text-gray-400 mt-1">{{ $t('admin.cron_format_hint') }}</p>
                <p v-if="aiInsightJobForm.cron_expression.trim() && !isAIInsightCronValid" class="text-[11px] text-rose-600 dark:text-rose-400 mt-1">
                  {{ $t('admin.cron_format_error') }}
                </p>
              </div>
            </div>
            <div>
              <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('admin.cron_prompt_label') }}</label>
              <textarea
                v-model="aiInsightJobForm.prompt"
                rows="4"
                class="w-full px-3 py-2 border border-gray-300 dark:border-dark-border dark:bg-dark-bg dark:text-white rounded-xl text-sm"
                :placeholder="$t('admin.cron_prompt_placeholder')"
              />
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <label class="flex items-center gap-2 text-xs font-semibold text-gray-700 dark:text-gray-300">
                <input v-model="aiInsightJobForm.inject_weather" type="checkbox" class="rounded" />
                {{ $t('admin.inject_weather') }}
              </label>
              <label class="flex items-center gap-2 text-xs font-semibold text-gray-700 dark:text-gray-300">
                <input v-model="aiInsightJobForm.inject_apiary" type="checkbox" class="rounded" />
                {{ $t('admin.inject_apiary') }}
              </label>
              <label class="flex items-center gap-2 text-xs font-semibold text-gray-700 dark:text-gray-300">
                <input v-model="aiInsightJobForm.inject_locations" type="checkbox" class="rounded" />
                {{ $t('admin.inject_locations') }}
              </label>
              <label class="flex items-center gap-2 text-xs font-semibold text-gray-700 dark:text-gray-300">
                <input v-model="aiInsightJobForm.inject_hives" type="checkbox" class="rounded" />
                {{ $t('admin.inject_hives') }}
              </label>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
              <label class="flex items-center gap-2 text-xs font-semibold text-gray-700 dark:text-gray-300 md:col-span-1">
                <input v-model="aiInsightJobForm.inject_log_entries" type="checkbox" class="rounded" />
                {{ $t('admin.inject_log_entries') }}
              </label>
              <div class="md:col-span-1" v-if="aiInsightJobForm.inject_log_entries">
                <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('admin.log_scope_label') }}</label>
                <select v-model="aiInsightJobForm.log_scope" class="w-full px-3 py-2 border border-gray-300 dark:border-dark-border dark:bg-dark-bg dark:text-white rounded-xl text-sm">
                  <option value="IMKEREI">{{ $t('beeAgent.scope_apiary') }}</option>
                  <option value="STANDORT">{{ $t('beeAgent.scope_location') }}</option>
                  <option value="VOLK">{{ $t('beeAgent.scope_hive') }}</option>
                </select>
              </div>
              <div class="md:col-span-1" v-if="aiInsightJobForm.inject_log_entries">
                <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('admin.max_logs_label') }}</label>
                <input v-model.number="aiInsightJobForm.max_log_entries" type="number" min="1" max="500" class="w-full px-3 py-2 border border-gray-300 dark:border-dark-border dark:bg-dark-bg dark:text-white rounded-xl text-sm" />
              </div>
            </div>
            <label class="flex items-center gap-2 text-xs font-semibold text-gray-700 dark:text-gray-300">
              <input v-model="aiInsightJobForm.is_active" type="checkbox" class="rounded" />
              {{ $t('admin.cron_job_active') }}
            </label>
            <div class="flex justify-end gap-2">
              <button @click="cancelAIInsightJobForm" class="px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-xl text-xs font-semibold">{{ $t('common.cancel') }}</button>
              <button @click="saveAIInsightJob" :disabled="savingAIInsightJob || !isAIInsightCronValid || !aiInsightJobForm.prompt.trim() || aiInsightJobForm.max_log_entries < 1 || aiInsightJobForm.max_log_entries > 500" class="px-3 py-2 bg-primary hover:bg-primary-hover text-white rounded-xl text-xs font-bold disabled:opacity-60">
                {{ savingAIInsightJob ? $t('admin.saving_changes_loading') : $t('common.save') }}
              </button>
            </div>
          </div>
        </div>

        <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-6 shadow-sm space-y-2">
          <h3 class="text-base font-bold text-gray-900 dark:text-white">{{ $t('admin.prompt_template_title') }}</h3>
          <p class="text-xs text-gray-500 dark:text-gray-400 max-w-2xl">
            {{ $t('admin.prompt_template_desc') }}
          </p>
        </div>

        <!-- Save Button Section -->
        <div class="flex items-center justify-end space-x-4">
          <button 
            @click="resetBeeAgentConfigToDefault"
            class="px-5 py-3 border border-gray-300 dark:border-gray-700 rounded-xl text-sm font-semibold hover:bg-gray-100 dark:hover:bg-dark-border text-gray-700 dark:text-gray-300 transition duration-200"
            :disabled="savingLLM"
          >
            {{ $t('admin.reset_to_default_btn') }}
          </button>
          
          <button 
            @click="saveBeeAgentConfig"
            class="px-6 py-3 bg-primary hover:bg-primary-hover text-white rounded-xl text-sm font-bold transition duration-200 flex items-center space-x-2 shadow-lg shadow-primary/20 hover-scale disabled:opacity-50 disabled:cursor-not-allowed"
            :disabled="savingLLM"
          >
            <svg v-if="savingLLM" class="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
            <span>{{ savingLLM ? $t('admin.saving_changes_loading') : $t('admin.save_changes_btn') }}</span>
          </button>
        </div>

      </div>
    </div>

    <!-- Tab Content: Finance & Taxes -->
    <div v-if="activeTab === 'finance'" class="space-y-6">
      <div v-if="loadingLLM" class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-16 flex flex-col items-center justify-center shadow-sm">
        <svg class="animate-spin h-10 w-10 text-primary mb-4" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
        <span class="text-sm text-gray-400 font-bold">{{ $t('admin.loading_config') }}</span>
      </div>

      <div v-else class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-6 shadow-sm space-y-4">
        <div>
          <h3 class="text-base font-bold text-gray-900 dark:text-white flex items-center">
            <span>{{ $t('admin.finance_title') }}</span>
          </h3>
          <p class="text-xs text-gray-500 dark:text-gray-400 max-w-2xl mt-1">
            {{ $t('admin.finance_desc') }}
          </p>
        </div>

        <div class="flex items-center justify-between pt-2 border-t border-gray-100 dark:border-dark-border/60">
          <div class="space-y-0.5">
            <p class="text-sm font-semibold text-gray-700 dark:text-gray-200">{{ $t('admin.calculate_taxes') }}</p>
            <p class="text-xs text-gray-500 dark:text-gray-400">
              {{ $t('admin.calculate_taxes_desc') }}
            </p>
          </div>
          <button
            @click="llmConfig.calculate_taxes = !llmConfig.calculate_taxes"
            class="relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ml-4"
            :class="llmConfig.calculate_taxes ? 'bg-emerald-500' : 'bg-gray-300 dark:bg-gray-700'"
          >
            <span class="sr-only">{{ $t('admin.calculate_taxes') }}</span>
            <span
              class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out"
              :class="llmConfig.calculate_taxes ? 'translate-x-5' : 'translate-x-0'"
            />
          </button>
        </div>

        <div class="pt-2 border-t border-gray-100 dark:border-dark-border/60">
          <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('admin.currency_label') }}</label>
          <p class="text-xs text-gray-500 dark:text-gray-400 mb-2">{{ $t('admin.currency_desc') }}</p>
          <div class="flex gap-2">
            <select
              v-model="llmConfig.currency"
              class="px-3 py-2 border border-gray-300 dark:border-dark-border dark:bg-dark-bg dark:text-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="EUR">EUR – Euro</option>
              <option value="USD">USD – US Dollar</option>
              <option value="CHF">CHF – Schweizer Franken</option>
              <option value="GBP">GBP – Britisches Pfund</option>
              <option value="custom">{{ $t('admin.currency_other') }}</option>
            </select>
            <input
              v-if="llmConfig.currency === 'custom' || !['EUR','USD','CHF','GBP'].includes(llmConfig.currency)"
              v-model="llmConfig.currency"
              type="text"
              maxlength="10"
              placeholder="z.B. JPY"
              class="flex-1 px-3 py-2 border border-gray-300 dark:border-dark-border dark:bg-dark-bg dark:text-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary font-mono"
            />
          </div>
        </div>

        <div class="pt-2 border-t border-gray-100 dark:border-dark-border/60">
          <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('admin.tax_rates_label') }}</label>
          <p class="text-xs text-gray-500 dark:text-gray-400 mb-2">{{ $t('admin.tax_rates_desc') }}</p>
          <input
            v-model="llmConfig.tax_rates"
            type="text"
            placeholder="z.B. 0.0,7.0,19.0"
            class="w-full px-3 py-2 border border-gray-300 dark:border-dark-border dark:bg-dark-bg dark:text-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary font-mono"
          />
        </div>

        <div class="flex items-center justify-end space-x-4 pt-2">
          <button
            @click="resetConfigToDefault"
            class="px-5 py-3 border border-gray-300 dark:border-gray-700 rounded-xl text-sm font-semibold hover:bg-gray-100 dark:hover:bg-dark-border text-gray-700 dark:text-gray-300 transition duration-200"
            :disabled="savingLLM"
          >
            {{ $t('admin.reset_to_default_btn') }}
          </button>

          <button
            @click="saveLLMConfig"
            class="px-6 py-3 bg-primary hover:bg-primary-hover text-white rounded-xl text-sm font-bold transition duration-200 flex items-center space-x-2 shadow-lg shadow-primary/20 hover-scale disabled:opacity-50 disabled:cursor-not-allowed"
            :disabled="savingLLM"
          >
            <svg v-if="savingLLM" class="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
            <span>{{ savingLLM ? $t('admin.saving_changes_loading') : $t('admin.save_changes_btn') }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Tab Content: Frame Types Management -->
    <div v-if="activeTab === 'frame-types'" class="space-y-6">
      <div class="flex justify-between items-center bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-6 shadow-sm animate-scale">
        <div>
          <h2 class="text-lg font-bold text-gray-900 dark:text-white">{{ $t('admin.frame_types_title') }}</h2>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">{{ $t('admin.frame_types_subtitle') }}</p>
        </div>
        <button 
          @click="openCreateFrameType" 
          class="px-4 py-2 bg-primary hover:bg-primary-hover text-white text-xs font-bold rounded-xl shadow-md flex items-center space-x-1 hover-scale"
        >
          <span>{{ $t('admin.new_frame_type_btn') }}</span>
        </button>
      </div>

      <!-- Frame Type Form (embedded/inline) -->
      <div v-if="showFrameTypeForm" class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-6 shadow-sm">
        <h3 class="text-sm font-bold text-gray-900 dark:text-white mb-4">
          {{ isEditFrameType ? $t('admin.edit_frame_type_title') : $t('admin.create_frame_type_title') }}
        </h3>
        <form @submit.prevent="submitFrameTypeForm" class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('admin.frame_name_label') }}</label>
              <input 
                v-model="formFrameType.name" 
                type="text" 
                required 
                :placeholder="$t('admin.frame_name_placeholder')" 
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
            <div class="flex items-center pt-5">
              <label class="flex items-center space-x-2 cursor-pointer">
                <input 
                  v-model="formFrameType.is_default" 
                  type="checkbox" 
                  class="rounded text-primary focus:ring-primary h-4 w-4"
                />
                <span class="text-xs font-bold text-gray-700 dark:text-gray-300">{{ $t('admin.frame_default_checkbox') }}</span>
              </label>
            </div>
          </div>

          <div class="grid grid-cols-2 md:grid-cols-6 gap-4">
            <div>
              <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('admin.brood_mult_label') }}</label>
              <input 
                v-model.number="formFrameType.brood_multiplier" 
                type="number" 
                step="0.01" 
                min="0.1" 
                required 
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary font-mono"
              />
            </div>
            <div>
              <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('admin.food_mult_label') }}</label>
              <input 
                v-model.number="formFrameType.food_multiplier" 
                type="number" 
                step="0.01" 
                min="0.1" 
                required 
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary font-mono"
              />
            </div>
            <div>
              <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('admin.bee_mult_label') }}</label>
              <input 
                v-model.number="formFrameType.bee_multiplier" 
                type="number" 
                step="0.01" 
                min="0.1" 
                required 
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary font-mono"
              />
            </div>
            <div>
              <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('admin.drone_mult_label') }}</label>
              <input 
                v-model.number="formFrameType.drone_multiplier" 
                type="number" 
                step="0.01" 
                min="0.1" 
                required 
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary font-mono"
              />
            </div>
            <div>
              <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('admin.drone_brood_mult_label') }}</label>
              <input 
                v-model.number="formFrameType.drone_brood_multiplier" 
                type="number" 
                step="0.01" 
                min="0.1" 
                required 
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary font-mono"
              />
            </div>
            <div>
              <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('admin.pollen_mult_label') }}</label>
              <input 
                v-model.number="formFrameType.pollen_multiplier" 
                type="number" 
                step="0.01" 
                min="0.1" 
                required 
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary font-mono"
              />
            </div>
          </div>

          <div class="flex justify-end space-x-3 pt-2">
            <button 
              type="button" 
              @click="showFrameTypeForm = false" 
              class="px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-xl text-xs font-semibold hover:bg-gray-100 dark:hover:bg-dark-border text-gray-700 dark:text-gray-300"
            >
              {{ $t('common.cancel') }}
            </button>
            <button 
              type="submit" 
              class="px-4 py-2 bg-primary hover:bg-primary-hover text-white text-xs font-bold rounded-xl shadow-md hover-scale"
              :disabled="savingFrameType"
            >
              {{ $t('common.save') }}
            </button>
          </div>
        </form>
      </div>

      <!-- Frame Types Table -->
      <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl overflow-hidden shadow-sm">
        <div v-if="loadingFrameTypes" class="flex flex-col items-center justify-center py-20">
          <svg class="animate-spin h-8 w-8 text-primary mb-3" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
          <span class="text-xs text-gray-400 font-bold">{{ $t('admin.loading_frame_types') }}</span>
        </div>

        <div v-else class="overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="bg-gray-50 dark:bg-dark-bg text-gray-500 dark:text-gray-400 text-[10px] font-bold uppercase tracking-wider border-b border-gray-100 dark:border-dark-border">
                <th class="px-6 py-4">{{ $t('admin.table_frame_name') }}</th>
                <th class="px-6 py-4 text-center">{{ $t('admin.table_brood_factor') }}</th>
                <th class="px-6 py-4 text-center">{{ $t('admin.table_food_factor') }}</th>
                <th class="px-6 py-4 text-center">{{ $t('admin.table_bee_factor') }}</th>
                <th class="px-6 py-4 text-center">{{ $t('admin.table_drone_factor') }}</th>
                <th class="px-6 py-4 text-center">{{ $t('admin.table_drone_brood_factor') }}</th>
                <th class="px-6 py-4 text-center">{{ $t('admin.table_pollen_factor') }}</th>
                <th class="px-6 py-4 text-center">{{ $t('admin.table_default') }}</th>
                <th class="px-6 py-4 text-right">{{ $t('common.actions') }}</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100 dark:divide-dark-border text-sm">
              <tr 
                v-for="ft in frameTypes" 
                :key="ft.id" 
                class="hover:bg-gray-50/50 dark:hover:bg-dark-bg/30 transition-colors duration-150"
              >
                <td class="px-6 py-4 font-bold text-gray-800 dark:text-gray-200">
                  {{ ft.name }}
                </td>
                <td class="px-6 py-4 text-center font-mono text-xs text-gray-600 dark:text-gray-300">
                  x{{ ft.brood_multiplier.toFixed(2) }}
                </td>
                <td class="px-6 py-4 text-center font-mono text-xs text-gray-600 dark:text-gray-300">
                  x{{ ft.food_multiplier.toFixed(2) }}
                </td>
                <td class="px-6 py-4 text-center font-mono text-xs text-gray-600 dark:text-gray-300">
                  x{{ ft.bee_multiplier.toFixed(2) }}
                </td>
                <td class="px-6 py-4 text-center font-mono text-xs text-gray-600 dark:text-gray-300">
                  x{{ (ft.drone_multiplier || 1.0).toFixed(2) }}
                </td>
                <td class="px-6 py-4 text-center font-mono text-xs text-gray-600 dark:text-gray-300">
                  x{{ (ft.drone_brood_multiplier || 1.0).toFixed(2) }}
                </td>
                <td class="px-6 py-4 text-center font-mono text-xs text-gray-600 dark:text-gray-300">
                  x{{ (ft.pollen_multiplier || 1.0).toFixed(2) }}
                </td>
                <td class="px-6 py-4 text-center">
                  <span v-if="ft.is_default" class="text-amber-500 font-bold text-lg" :title="$t('admin.table_default')">★</span>
                  <span v-else class="text-gray-300 dark:text-gray-700">-</span>
                </td>
                <td class="px-6 py-4 text-right space-x-2">
                  <button 
                    @click="openEditFrameType(ft)" 
                    class="p-1.5 text-gray-500 hover:text-primary hover:bg-gray-100 dark:hover:bg-dark-border rounded-lg transition-all duration-150 inline-flex"
                    :title="$t('admin.edit_tooltip')"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/></svg>
                  </button>
                  <button 
                    @click="deleteFrameType(ft)" 
                    class="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-500/10 rounded-lg transition-all duration-150 inline-flex"
                    :title="$t('admin.delete_tooltip')"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Tab Content: Number Ranges Management -->
    <div v-if="activeTab === 'number-ranges'" class="space-y-6">
      <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-6 shadow-sm animate-scale flex flex-col md:flex-row justify-between items-start md:items-center space-y-4 md:space-y-0">
        <div>
          <h2 class="text-lg font-bold text-gray-900 dark:text-white">{{ $t('admin.number_ranges_title') }}</h2>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
            {{ $t('admin.number_ranges_subtitle') }}
          </p>
        </div>
      </div>

      <!-- Edit Number Range Form (embedded/inline) -->
      <div v-if="showNumberRangeForm" class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-6 shadow-sm animate-scale">
        <h3 class="text-sm font-bold text-gray-900 dark:text-white mb-4">
          {{ $t('admin.edit_number_range_title', { name: formNumberRange.name }) }}
        </h3>
        <form @submit.prevent="submitNumberRangeForm" class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('admin.nr_prefix_label') }}</label>
              <input 
                v-model="formNumberRange.prefix" 
                type="text" 
                :placeholder="$t('admin.nr_prefix_placeholder')" 
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary font-mono"
              />
            </div>
            <div>
              <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('admin.nr_current_val_label') }}</label>
              <input 
                v-model.number="formNumberRange.current_value" 
                type="number" 
                min="1" 
                required 
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary font-mono"
              />
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('admin.nr_digits_label') }}</label>
              <input 
                v-model.number="formNumberRange.digits" 
                type="number" 
                min="1" 
                max="10" 
                required 
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary font-mono"
              />
            </div>
            <div class="flex items-center pt-5">
              <label class="flex items-center space-x-2 cursor-pointer">
                <input 
                  v-model="formNumberRange.is_active" 
                  type="checkbox" 
                  class="rounded text-primary focus:ring-primary h-4 w-4"
                />
                <span class="text-xs font-bold text-gray-700 dark:text-gray-300">{{ $t('admin.nr_active_checkbox') }}</span>
              </label>
            </div>
          </div>

          <!-- Preview -->
          <div class="p-3 bg-gray-50 dark:bg-dark-bg border border-gray-100 dark:border-dark-border rounded-xl">
            <span class="text-xs text-gray-500 dark:text-gray-400 font-bold block mb-1">{{ $t('admin.nr_preview_label') }}</span>
            <span class="font-mono text-sm font-bold text-amber-500">{{ previewNextNumber }}</span>
          </div>

          <div class="flex justify-end space-x-3 pt-2">
            <button 
              type="button" 
              @click="showNumberRangeForm = false" 
              class="px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-xl text-xs font-semibold hover:bg-gray-100 dark:hover:bg-dark-border text-gray-700 dark:text-gray-300"
            >
              {{ $t('common.cancel') }}
            </button>
            <button 
              type="submit" 
              class="px-5 py-2 bg-primary hover:bg-primary-hover text-white text-xs font-bold rounded-xl shadow-md hover-scale"
              :disabled="savingNumberRange"
            >
              {{ $t('common.save') }}
            </button>
          </div>
        </form>
      </div>

      <!-- Number Ranges Table -->
      <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl overflow-hidden shadow-sm">
        <div v-if="loadingNumberRanges" class="flex flex-col items-center justify-center py-20">
          <svg class="animate-spin h-8 w-8 text-primary mb-3" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
          <span class="text-xs text-gray-400 font-bold">{{ $t('admin.loading_number_ranges') }}</span>
        </div>

        <div v-else class="overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="bg-gray-50 dark:bg-dark-bg text-gray-500 dark:text-gray-400 text-[10px] font-bold uppercase tracking-wider border-b border-gray-100 dark:border-dark-border">
                <th class="px-6 py-4">{{ $t('admin.table_nr_name') }}</th>
                <th class="px-6 py-4">{{ $t('admin.table_nr_prefix') }}</th>
                <th class="px-6 py-4 text-center">{{ $t('admin.table_nr_current') }}</th>
                <th class="px-6 py-4 text-center">{{ $t('admin.table_nr_digits') }}</th>
                <th class="px-6 py-4 text-center">{{ $t('admin.table_nr_next') }}</th>
                <th class="px-6 py-4 text-center">{{ $t('admin.table_status') }}</th>
                <th class="px-6 py-4 text-right">{{ $t('common.actions') }}</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100 dark:divide-dark-border text-sm">
              <tr 
                v-for="nr in numberRanges" 
                :key="nr.id" 
                class="hover:bg-gray-50/50 dark:hover:bg-dark-bg/30 transition-colors duration-150"
              >
                <td class="px-6 py-4 font-bold text-gray-800 dark:text-gray-200">
                  {{ nr.name }}
                </td>
                <td class="px-6 py-4 font-mono text-gray-600 dark:text-gray-300">
                  {{ nr.prefix || '-' }}
                </td>
                <td class="px-6 py-4 text-center font-mono text-gray-600 dark:text-gray-300">
                  {{ nr.current_value }}
                </td>
                <td class="px-6 py-4 text-center font-mono text-gray-600 dark:text-gray-300">
                  {{ nr.digits }}
                </td>
                <td class="px-6 py-4 text-center font-mono font-bold text-amber-500">
                  {{ nr.prefix || '' }}{{ String(nr.current_value).padStart(nr.digits, '0') }}
                </td>
                <td class="px-6 py-4 text-center">
                  <span 
                    class="px-2 py-0.5 rounded-full text-[10px] font-bold"
                    :class="nr.is_active ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400' : 'bg-rose-500/10 text-rose-600 dark:text-rose-400'"
                  >
                    {{ nr.is_active ? $t('common.active') : $t('common.inactive') }}
                  </span>
                </td>
                <td class="px-6 py-4 text-right">
                  <button 
                    @click="openEditNumberRange(nr)" 
                    class="p-1.5 text-gray-500 hover:text-primary hover:bg-gray-100 dark:hover:bg-dark-border rounded-lg transition-all duration-150 inline-flex hover-scale"
                    :title="$t('admin.edit_tooltip')"
                  >
                    <svg class="w-4.5 h-4.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/></svg>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Tab Content: Treatment Methods Management -->
    <div v-if="activeTab === 'treatment-methods'" class="space-y-6">
      <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-6 shadow-sm animate-scale flex flex-col md:flex-row justify-between items-start md:items-center space-y-4 md:space-y-0">
        <div>
          <h2 class="text-lg font-bold text-gray-900 dark:text-white">{{ $t('admin.treatment_methods_title') }}</h2>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
            {{ $t('admin.treatment_methods_subtitle') }}
          </p>
        </div>
        <button 
          @click="openCreateTreatmentMethod" 
          class="px-4 py-2 bg-primary hover:bg-primary-hover text-white text-xs font-bold rounded-xl shadow-md hover-scale flex items-center gap-1.5"
        >
          <span>{{ $t('admin.new_treatment_method') }}</span>
        </button>
      </div>

      <!-- Create/Edit Form (inline/embedded) -->
      <div v-if="showTreatmentMethodForm" class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-6 shadow-sm animate-scale">
        <h3 class="text-sm font-bold text-gray-900 dark:text-white mb-4">
          {{ isEditTreatmentMethod ? $t('admin.edit_treatment_method', { name: formTreatmentMethod.name }) : $t('admin.new_treatment_method') }}
        </h3>
        <form @submit.prevent="submitTreatmentMethodForm" class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('admin.form_method_name') }}</label>
              <input 
                v-model="formTreatmentMethod.name" 
                type="text" 
                required 
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
            <div>
              <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('admin.form_method_unit') }}</label>
              <input 
                v-model="formTreatmentMethod.unit" 
                type="text" 
                required 
                :placeholder="$t('admin.form_method_unit_placeholder')"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
          </div>

          <div class="flex items-center pt-2">
            <label class="flex items-center space-x-2 cursor-pointer">
              <input 
                v-model="formTreatmentMethod.is_active" 
                type="checkbox" 
                class="rounded text-primary focus:ring-primary h-4 w-4"
              />
              <span class="text-xs font-bold text-gray-700 dark:text-gray-300">{{ $t('admin.form_method_active') }}</span>
            </label>
          </div>

          <div class="flex justify-end space-x-3 pt-2">
            <button 
              type="button" 
              @click="showTreatmentMethodForm = false" 
              class="px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-xl text-xs font-semibold hover:bg-gray-100 dark:hover:bg-dark-border text-gray-700 dark:text-gray-300"
            >
              {{ $t('common.cancel') }}
            </button>
            <button 
              type="submit" 
              class="px-5 py-2 bg-primary hover:bg-primary-hover text-white text-xs font-bold rounded-xl shadow-md hover-scale"
              :disabled="savingTreatmentMethod"
            >
              {{ $t('common.save') }}
            </button>
          </div>
        </form>
      </div>

      <!-- Table -->
      <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl overflow-hidden shadow-sm">
        <div v-if="loadingTreatmentMethods" class="flex flex-col items-center justify-center py-20">
          <svg class="animate-spin h-8 w-8 text-primary mb-3" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
          <span class="text-xs text-gray-400 font-bold">{{ $t('admin.loading_frame_types') }}</span>
        </div>

        <div v-else class="overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="bg-gray-50 dark:bg-dark-bg text-gray-500 dark:text-gray-400 text-[10px] font-bold uppercase tracking-wider border-b border-gray-100 dark:border-dark-border">
                <th class="px-6 py-4">{{ $t('admin.table_method_name') }}</th>
                <th class="px-6 py-4">{{ $t('admin.table_method_unit') }}</th>
                <th class="px-6 py-4 text-center">{{ $t('admin.table_method_status') }}</th>
                <th class="px-6 py-4 text-right">{{ $t('common.actions') }}</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100 dark:divide-dark-border text-sm">
              <tr 
                v-for="m in treatmentMethods" 
                :key="m.id" 
                class="hover:bg-gray-50/50 dark:hover:bg-dark-bg/30 transition-colors duration-150"
              >
                <td class="px-6 py-4 font-bold text-gray-800 dark:text-gray-200">
                  {{ m.name }}
                </td>
                <td class="px-6 py-4 font-mono text-gray-600 dark:text-gray-300">
                  {{ m.unit }}
                </td>
                <td class="px-6 py-4 text-center">
                  <span 
                    class="px-2 py-0.5 rounded-full text-[10px] font-bold"
                    :class="m.is_active ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400' : 'bg-rose-500/10 text-rose-600 dark:text-rose-400'"
                  >
                    {{ m.is_active ? $t('common.active') : $t('common.inactive') }}
                  </span>
                </td>
                <td class="px-6 py-4 text-right space-x-2">
                  <button 
                    @click="openEditTreatmentMethod(m)" 
                    class="p-1.5 text-gray-500 hover:text-primary hover:bg-gray-100 dark:hover:bg-dark-border rounded-lg transition-all duration-150 inline-flex hover-scale"
                    :title="$t('admin.edit_tooltip')"
                  >
                    <svg class="w-4.5 h-4.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/></svg>
                  </button>
                  <button 
                    @click="deleteTreatmentMethod(m)" 
                    class="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-500/10 rounded-lg transition-all duration-150 inline-flex hover-scale"
                    :title="$t('admin.delete_tooltip')"
                  >
                    <svg class="w-4.5 h-4.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Tab Content: Treatment Application Types Management -->
    <div v-if="activeTab === 'treatment-application-types'" class="space-y-6">
      <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-6 shadow-sm animate-scale flex flex-col md:flex-row justify-between items-start md:items-center space-y-4 md:space-y-0">
        <div>
          <h2 class="text-lg font-bold text-gray-900 dark:text-white">{{ $t('admin.treatment_apps_title') }}</h2>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
            {{ $t('admin.treatment_apps_subtitle') }}
          </p>
        </div>
        <button 
          @click="openCreateTreatmentApp" 
          class="px-4 py-2 bg-primary hover:bg-primary-hover text-white text-xs font-bold rounded-xl shadow-md hover-scale flex items-center gap-1.5"
        >
          <span>{{ $t('admin.new_treatment_app') }}</span>
        </button>
      </div>

      <!-- Create/Edit Form (inline/embedded) -->
      <div v-if="showTreatmentAppForm" class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-6 shadow-sm animate-scale">
        <h3 class="text-sm font-bold text-gray-900 dark:text-white mb-4">
          {{ isEditTreatmentApp ? $t('admin.edit_treatment_app', { name: formTreatmentApp.name }) : $t('admin.new_treatment_app') }}
        </h3>
        <form @submit.prevent="submitTreatmentAppForm" class="space-y-4">
          <div>
            <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('admin.form_app_name') }}</label>
            <input 
              v-model="formTreatmentApp.name" 
              type="text" 
              required 
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>

          <div class="flex items-center pt-2">
            <label class="flex items-center space-x-2 cursor-pointer">
              <input 
                v-model="formTreatmentApp.is_active" 
                type="checkbox" 
                class="rounded text-primary focus:ring-primary h-4 w-4"
              />
              <span class="text-xs font-bold text-gray-700 dark:text-gray-300">{{ $t('admin.form_app_active') }}</span>
            </label>
          </div>

          <div class="flex justify-end space-x-3 pt-2">
            <button 
              type="button" 
              @click="showTreatmentAppForm = false" 
              class="px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-xl text-xs font-semibold hover:bg-gray-100 dark:hover:bg-dark-border text-gray-700 dark:text-gray-300"
            >
              {{ $t('common.cancel') }}
            </button>
            <button 
              type="submit" 
              class="px-5 py-2 bg-primary hover:bg-primary-hover text-white text-xs font-bold rounded-xl shadow-md hover-scale"
              :disabled="savingTreatmentApp"
            >
              {{ $t('common.save') }}
            </button>
          </div>
        </form>
      </div>

      <!-- Table -->
      <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl overflow-hidden shadow-sm">
        <div v-if="loadingTreatmentApps" class="flex flex-col items-center justify-center py-20">
          <svg class="animate-spin h-8 w-8 text-primary mb-3" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
          <span class="text-xs text-gray-400 font-bold">{{ $t('admin.loading_frame_types') }}</span>
        </div>

        <div v-else class="overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="bg-gray-50 dark:bg-dark-bg text-gray-500 dark:text-gray-400 text-[10px] font-bold uppercase tracking-wider border-b border-gray-100 dark:border-dark-border">
                <th class="px-6 py-4">{{ $t('admin.table_app_name') }}</th>
                <th class="px-6 py-4 text-center">{{ $t('admin.table_method_status') }}</th>
                <th class="px-6 py-4 text-right">{{ $t('common.actions') }}</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100 dark:divide-dark-border text-sm">
              <tr 
                v-for="app in treatmentApps" 
                :key="app.id" 
                class="hover:bg-gray-50/50 dark:hover:bg-dark-bg/30 transition-colors duration-150"
              >
                <td class="px-6 py-4 font-bold text-gray-800 dark:text-gray-200">
                  {{ app.name }}
                </td>
                <td class="px-6 py-4 text-center">
                  <span 
                    class="px-2 py-0.5 rounded-full text-[10px] font-bold"
                    :class="app.is_active ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400' : 'bg-rose-500/10 text-rose-600 dark:text-rose-400'"
                  >
                    {{ app.is_active ? $t('common.active') : $t('common.inactive') }}
                  </span>
                </td>
                <td class="px-6 py-4 text-right space-x-2">
                  <button 
                    @click="openEditTreatmentApp(app)" 
                    class="p-1.5 text-gray-500 hover:text-primary hover:bg-gray-100 dark:hover:bg-dark-border rounded-lg transition-all duration-150 inline-flex hover-scale"
                    :title="$t('admin.edit_tooltip')"
                  >
                    <svg class="w-4.5 h-4.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/></svg>
                  </button>
                  <button 
                    @click="deleteTreatmentApp(app)" 
                    class="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-500/10 rounded-lg transition-all duration-150 inline-flex hover-scale"
                    :title="$t('admin.delete_tooltip')"
                  >
                    <svg class="w-4.5 h-4.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '../stores/auth'
import { useConfirmStore } from '../stores/confirm'
import axios from 'axios'

const { t, locale } = useI18n()
const authStore = useAuthStore()
const confirmStore = useConfirmStore()

const activeTab = ref('users')

// Users States
const users = ref([])
const loadingUsers = ref(false)
const togglingUser = ref(null)
const creatingUser = ref(false)
const newUserForm = reactive({
  username: '',
  email: '',
  password: '',
  first_name: '',
  last_name: '',
  role: 'USER'
})

// LLM States
const llmConfig = ref({
  enable_weather_api: false,
  calculate_taxes: true,
  currency: 'EUR',
  tax_rates: '0.0,7.0,19.0'
})
const loadingLLM = ref(false)
const savingLLM = ref(false)

const aiInsightJobs = ref([])
const loadingAIInsightJobs = ref(false)
const savingAIInsightJob = ref(false)
const showAIInsightJobForm = ref(false)
const editingAIInsightJobId = ref(null)
const aiInsightJobForm = reactive({
  name: '',
  prompt: '',
  cron_expression: '0 */12 * * *',
  inject_weather: false,
  inject_locations: true,
  inject_apiary: true,
  inject_hives: true,
  inject_log_entries: true,
  log_scope: 'IMKEREI',
  max_log_entries: 20,
  is_active: true
})

function validateCronExpression(value) {
  const parts = value.trim().split(/\s+/)
  return parts.length === 5 && parts.every(p => p.length > 0)
}

const isAIInsightCronValid = computed(() => validateCronExpression(aiInsightJobForm.cron_expression || ''))

// Toast Notifications System
const toasts = ref([])
let toastId = 0

function showToast(message, type = 'success') {
  const id = toastId++
  toasts.value.push({ id, message, type })
  setTimeout(() => {
    toasts.value = toasts.value.filter(t => t.id !== id)
  }, 3500)
}

// Fetch Users List
async function fetchUsers() {
  loadingUsers.value = true
  try {
    const res = await axios.get('/api/admin/users')
    users.value = res.data
  } catch (err) {
    console.error('Fetch users error:', err)
    showToast(t('admin.toast_users_load_error'), 'error')
  } finally {
    loadingUsers.value = false
  }
}

async function createUser() {
  creatingUser.value = true
  try {
    await axios.post('/api/admin/users', {
      username: newUserForm.username.trim(),
      email: newUserForm.email.trim(),
      password: newUserForm.password,
      first_name: newUserForm.first_name?.trim() || null,
      last_name: newUserForm.last_name?.trim() || null,
      role: newUserForm.role
    })
    showToast(t('admin.toast_user_created', { username: newUserForm.username }))
    newUserForm.username = ''
    newUserForm.email = ''
    newUserForm.password = ''
    newUserForm.first_name = ''
    newUserForm.last_name = ''
    newUserForm.role = 'USER'
    await fetchUsers()
  } catch (err) {
    console.error('Create user error:', err)
    const errDetail = err.response?.data?.detail || t('admin.toast_users_create_error')
    showToast(errDetail, 'error')
  } finally {
    creatingUser.value = false
  }
}

// Fetch LLM and Weather configs
async function fetchLLMConfig() {
  loadingLLM.value = true
  try {
    const res = await axios.get('/api/admin/llm-config')
    llmConfig.value = res.data
  } catch (err) {
    console.error('Fetch LLM config error:', err)
    showToast(t('admin.toast_config_load_error'), 'error')
  } finally {
    loadingLLM.value = false
  }
}

async function fetchAIInsightJobs() {
  loadingAIInsightJobs.value = true
  try {
    const res = await axios.get('/api/admin/ai-insight-jobs')
    aiInsightJobs.value = res.data
  } catch (err) {
    console.error('Fetch AI insight jobs error:', err)
    showToast(t('admin.toast_cron_jobs_load_error'), 'error')
  } finally {
    loadingAIInsightJobs.value = false
  }
}

function openCreateAIInsightJob() {
  editingAIInsightJobId.value = null
  aiInsightJobForm.name = ''
  aiInsightJobForm.prompt = ''
  aiInsightJobForm.cron_expression = '0 */12 * * *'
  aiInsightJobForm.inject_weather = false
  aiInsightJobForm.inject_locations = true
  aiInsightJobForm.inject_apiary = true
  aiInsightJobForm.inject_hives = true
  aiInsightJobForm.inject_log_entries = true
  aiInsightJobForm.log_scope = 'IMKEREI'
  aiInsightJobForm.max_log_entries = 20
  aiInsightJobForm.is_active = true
  showAIInsightJobForm.value = true
}

function openEditAIInsightJob(job) {
  editingAIInsightJobId.value = job.id
  aiInsightJobForm.name = job.name
  aiInsightJobForm.prompt = job.prompt || ''
  aiInsightJobForm.cron_expression = job.cron_expression
  aiInsightJobForm.inject_weather = !!job.inject_weather
  aiInsightJobForm.inject_locations = !!job.inject_locations
  aiInsightJobForm.inject_apiary = !!job.inject_apiary
  aiInsightJobForm.inject_hives = !!job.inject_hives
  aiInsightJobForm.inject_log_entries = !!job.inject_log_entries
  aiInsightJobForm.log_scope = job.log_scope || 'IMKEREI'
  aiInsightJobForm.max_log_entries = Number(job.max_log_entries || 20)
  aiInsightJobForm.is_active = job.is_active
  showAIInsightJobForm.value = true
}

function cancelAIInsightJobForm() {
  showAIInsightJobForm.value = false
  editingAIInsightJobId.value = null
}

async function saveAIInsightJob() {
  if (!aiInsightJobForm.name.trim()) {
    showToast(t('admin.toast_cron_job_save_error'), 'error')
    return
  }
  if (!aiInsightJobForm.cron_expression.trim()) {
    showToast(t('admin.toast_cron_job_save_error'), 'error')
    return
  }
  if (!aiInsightJobForm.prompt.trim()) {
    showToast(t('admin.toast_cron_job_save_error'), 'error')
    return
  }
  if (!validateCronExpression(aiInsightJobForm.cron_expression)) {
    showToast(t('admin.cron_format_error'), 'error')
    return
  }
  if (aiInsightJobForm.max_log_entries < 1 || aiInsightJobForm.max_log_entries > 500) {
    showToast(t('admin.max_logs_error'), 'error')
    return
  }

  savingAIInsightJob.value = true
  try {
    const payload = {
      name: aiInsightJobForm.name.trim(),
      prompt: aiInsightJobForm.prompt.trim(),
      cron_expression: aiInsightJobForm.cron_expression.trim(),
      inject_weather: aiInsightJobForm.inject_weather,
      inject_locations: aiInsightJobForm.inject_locations,
      inject_apiary: aiInsightJobForm.inject_apiary,
      inject_hives: aiInsightJobForm.inject_hives,
      inject_log_entries: aiInsightJobForm.inject_log_entries,
      log_scope: aiInsightJobForm.log_scope,
      max_log_entries: aiInsightJobForm.max_log_entries,
      is_active: aiInsightJobForm.is_active
    }
    if (editingAIInsightJobId.value) {
      await axios.put(`/api/admin/ai-insight-jobs/${editingAIInsightJobId.value}`, payload)
      showToast(t('admin.toast_cron_job_updated'))
    } else {
      await axios.post('/api/admin/ai-insight-jobs', payload)
      showToast(t('admin.toast_cron_job_created'))
    }
    cancelAIInsightJobForm()
    await fetchAIInsightJobs()
  } catch (err) {
    console.error('Save AI insight job error:', err)
    const msg = err.response?.data?.detail || t('admin.toast_cron_job_save_error')
    showToast(msg, 'error')
  } finally {
    savingAIInsightJob.value = false
  }
}

async function deleteAIInsightJob(job) {
  const confirmed = await confirmStore.ask({
    title: t('admin.toast_cron_job_delete_title'),
    message: t('admin.toast_cron_job_delete_msg', { name: job.name }),
    type: 'danger',
    confirmText: t('common.delete')
  })
  if (!confirmed) return

  try {
    await axios.delete(`/api/admin/ai-insight-jobs/${job.id}`)
    showToast(t('admin.toast_cron_job_deleted'))
    await fetchAIInsightJobs()
  } catch (err) {
    console.error('Delete AI insight job error:', err)
    const msg = err.response?.data?.detail || t('admin.toast_cron_job_delete_error')
    showToast(msg, 'error')
  }
}

// Update active status for user
async function toggleUserActive(user) {
  togglingUser.value = user.id
  const originalStatus = user.is_active
  const targetStatus = !originalStatus
  try {
    const res = await axios.put(`/api/admin/users/${user.id}`, {
      is_active: targetStatus
    })
    user.is_active = res.data.is_active
    const statusVal = user.is_active
      ? (locale.value === 'de' ? 'aktiviert' : 'activated')
      : (locale.value === 'de' ? 'deaktiviert' : 'deactivated')
    showToast(t('admin.toast_user_status_updated', { username: user.username, status: statusVal }))
  } catch (err) {
    console.error('Toggle active error:', err)
    const errDetail = err.response?.data?.detail || t('admin.toast_user_status_error')
    showToast(errDetail, 'error')
    user.is_active = originalStatus // Rollback visual
  } finally {
    togglingUser.value = null
  }
}

// Change role for user
async function changeUserRole(user) {
  togglingUser.value = user.id
  const originalRole = user.role
  try {
    const res = await axios.put(`/api/admin/users/${user.id}`, {
      role: user.role
    })
    user.role = res.data.role
    showToast(t('admin.toast_user_role_updated', { username: user.username, role: user.role }))
  } catch (err) {
    console.error('Change role error:', err)
    const errDetail = err.response?.data?.detail || t('admin.toast_user_role_error')
    showToast(errDetail, 'error')
    user.role = originalRole // Rollback visual
  } finally {
    togglingUser.value = null
  }
}

// Save dynamic system prompts and weather api switch
async function saveLLMConfig() {
  savingLLM.value = true
  try {
    const res = await axios.put('/api/admin/llm-config', {
      enable_weather_api: llmConfig.value.enable_weather_api,
      calculate_taxes: llmConfig.value.calculate_taxes,
      currency: llmConfig.value.currency,
      tax_rates: llmConfig.value.tax_rates
    })
    llmConfig.value = res.data
    showToast(t('admin.toast_config_updated'))
  } catch (err) {
    console.error('Save config error:', err)
    const msg = err.response?.data?.detail || t('admin.toast_config_save_error')
    showToast(msg, 'error')
  } finally {
    savingLLM.value = false
  }
}

async function saveBeeAgentConfig() {
  savingLLM.value = true
  try {
    const res = await axios.put('/api/admin/llm-config', {
      enable_weather_api: llmConfig.value.enable_weather_api
    })
    llmConfig.value = res.data
    showToast(t('admin.toast_beeagent_config_updated'))
  } catch (err) {
    console.error('Save bee-agent config error:', err)
    const msg = err.response?.data?.detail || t('admin.toast_beeagent_config_save_error')
    showToast(msg, 'error')
  } finally {
    savingLLM.value = false
  }
}

function resetBeeAgentConfigToDefault() {
  llmConfig.value.enable_weather_api = false
  showToast(t('admin.reset_defaults_toast'), 'success')
}

// Restore editable admin settings to defaults
function resetConfigToDefault() {
  llmConfig.value.enable_weather_api = false
  llmConfig.value.calculate_taxes = true
  llmConfig.value.currency = 'EUR'
  llmConfig.value.tax_rates = '0.0,7.0,19.0'

  showToast(t('admin.reset_defaults_toast'), 'success')
}

// Order users: admins first, then by username
const sortedUsers = computed(() => {
  return [...users.value].sort((a, b) => {
    if (a.role === 'SYSTEM_ADMIN' && b.role !== 'SYSTEM_ADMIN') return -1
    if (a.role !== 'SYSTEM_ADMIN' && b.role === 'SYSTEM_ADMIN') return 1
    return a.username.localeCompare(b.username)
  })
})

// Frame Types States
const frameTypes = ref([])
const loadingFrameTypes = ref(false)
const savingFrameType = ref(false)
const showFrameTypeForm = ref(false)
const isEditFrameType = ref(false)
const editingFrameTypeId = ref(null)

const formFrameType = reactive({
  name: '',
  is_default: false,
  brood_multiplier: 1.0,
  food_multiplier: 1.0,
  bee_multiplier: 1.0,
  drone_multiplier: 1.0,
  drone_brood_multiplier: 1.0,
  pollen_multiplier: 1.0
})

async function fetchFrameTypes() {
  loadingFrameTypes.value = true
  try {
    const res = await axios.get('/api/admin/frame-types')
    frameTypes.value = res.data
  } catch (err) {
    console.error('Fetch frame types error:', err)
    showToast(t('admin.toast_frame_types_load_error'), 'error')
  } finally {
    loadingFrameTypes.value = false
  }
}

function openCreateFrameType() {
  isEditFrameType.value = false
  editingFrameTypeId.value = null
  formFrameType.name = ''
  formFrameType.is_default = false
  formFrameType.brood_multiplier = 1.0
  formFrameType.food_multiplier = 1.0
  formFrameType.bee_multiplier = 1.0
  formFrameType.drone_multiplier = 1.0
  formFrameType.drone_brood_multiplier = 1.0
  formFrameType.pollen_multiplier = 1.0
  showFrameTypeForm.value = true
}

function openEditFrameType(ft) {
  isEditFrameType.value = true
  editingFrameTypeId.value = ft.id
  formFrameType.name = ft.name
  formFrameType.is_default = ft.is_default
  formFrameType.brood_multiplier = ft.brood_multiplier
  formFrameType.food_multiplier = ft.food_multiplier
  formFrameType.bee_multiplier = ft.bee_multiplier
  formFrameType.drone_multiplier = ft.drone_multiplier || 1.0
  formFrameType.drone_brood_multiplier = ft.drone_brood_multiplier || 1.0
  formFrameType.pollen_multiplier = ft.pollen_multiplier || 1.0
  showFrameTypeForm.value = true
}

async function submitFrameTypeForm() {
  savingFrameType.value = true
  try {
    const payload = {
      name: formFrameType.name,
      is_default: formFrameType.is_default,
      brood_multiplier: Number(formFrameType.brood_multiplier),
      food_multiplier: Number(formFrameType.food_multiplier),
      bee_multiplier: Number(formFrameType.bee_multiplier),
      drone_multiplier: Number(formFrameType.drone_multiplier),
      drone_brood_multiplier: Number(formFrameType.drone_brood_multiplier),
      pollen_multiplier: Number(formFrameType.pollen_multiplier)
    }
    if (isEditFrameType.value) {
      await axios.put(`/api/admin/frame-types/${editingFrameTypeId.value}`, payload)
      showToast(t('admin.toast_frame_type_updated', { name: payload.name }))
    } else {
      await axios.post('/api/admin/frame-types', payload)
      showToast(t('admin.toast_frame_type_created', { name: payload.name }))
    }
    showFrameTypeForm.value = false
    await fetchFrameTypes()
  } catch (err) {
    console.error('Save frame type error:', err)
    const errDetail = err.response?.data?.detail || t('admin.toast_frame_type_save_error')
    showToast(errDetail, 'error')
  } finally {
    savingFrameType.value = false
  }
}

async function deleteFrameType(ft) {
  const confirmed = await confirmStore.ask({
    title: t('admin.toast_frame_type_delete_title'),
    message: t('admin.toast_frame_type_delete_msg', { name: ft.name }),
    type: 'danger',
    confirmText: t('common.delete')
  })
  if (!confirmed) {
    return
  }
  try {
    await axios.delete(`/api/admin/frame-types/${ft.id}`)
    showToast(t('admin.toast_frame_type_deleted', { name: ft.name }))
    await fetchFrameTypes()
  } catch (err) {
    console.error('Delete frame type error:', err)
    const errDetail = err.response?.data?.detail || t('admin.toast_frame_type_delete_error')
    showToast(errDetail, 'error')
  }
}

// Number Ranges States
const numberRanges = ref([])
const loadingNumberRanges = ref(false)
const savingNumberRange = ref(false)
const showNumberRangeForm = ref(false)
const formNumberRange = reactive({
  id: '',
  name: '',
  prefix: '',
  current_value: 1,
  digits: 4,
  is_active: true
})

const previewNextNumber = computed(() => {
  const prefix = formNumberRange.prefix || ''
  const current = String(formNumberRange.current_value || 0)
  const digits = formNumberRange.digits || 4
  return prefix + current.padStart(digits, '0')
})

async function fetchNumberRanges() {
  loadingNumberRanges.value = true
  try {
    const res = await axios.get('/api/admin/number-ranges')
    numberRanges.value = res.data
  } catch (err) {
    console.error('Fetch number ranges error:', err)
    showToast(t('admin.toast_number_ranges_load_error'), 'error')
  } finally {
    loadingNumberRanges.value = false
  }
}

function openEditNumberRange(nr) {
  formNumberRange.id = nr.id
  formNumberRange.name = nr.name
  formNumberRange.prefix = nr.prefix || ''
  formNumberRange.current_value = nr.current_value
  formNumberRange.digits = nr.digits
  formNumberRange.is_active = nr.is_active
  showNumberRangeForm.value = true
}

async function submitNumberRangeForm() {
  savingNumberRange.value = true
  try {
    const payload = {
      name: formNumberRange.name,
      prefix: formNumberRange.prefix || null,
      current_value: Number(formNumberRange.current_value),
      digits: Number(formNumberRange.digits),
      is_active: formNumberRange.is_active
    }
    await axios.put(`/api/admin/number-ranges/${formNumberRange.id}`, payload)
    showToast(t('admin.toast_number_range_updated', { name: payload.name }))
    showNumberRangeForm.value = false
    await fetchNumberRanges()
  } catch (err) {
    console.error('Save number range error:', err)
    const errDetail = err.response?.data?.detail || t('admin.toast_number_range_save_error')
    showToast(errDetail, 'error')
  } finally {
    savingNumberRange.value = false
  }
}

// Treatment Methods States
const treatmentMethods = ref([])
const loadingTreatmentMethods = ref(false)
const savingTreatmentMethod = ref(false)
const showTreatmentMethodForm = ref(false)
const isEditTreatmentMethod = ref(false)
const editingTreatmentMethodId = ref(null)

const formTreatmentMethod = reactive({
  name: '',
  unit: 'ml',
  is_active: true
})

async function fetchTreatmentMethods() {
  loadingTreatmentMethods.value = true
  try {
    const res = await axios.get('/api/admin/treatment-methods')
    treatmentMethods.value = res.data
  } catch (err) {
    console.error('Fetch treatment methods error:', err)
    showToast(t('admin.toast_methods_load_error'), 'error')
  } finally {
    loadingTreatmentMethods.value = false
  }
}

function openCreateTreatmentMethod() {
  isEditTreatmentMethod.value = false
  editingTreatmentMethodId.value = null
  formTreatmentMethod.name = ''
  formTreatmentMethod.unit = 'ml'
  formTreatmentMethod.is_active = true
  showTreatmentMethodForm.value = true
}

function openEditTreatmentMethod(m) {
  isEditTreatmentMethod.value = true
  editingTreatmentMethodId.value = m.id
  formTreatmentMethod.name = m.name
  formTreatmentMethod.unit = m.unit
  formTreatmentMethod.is_active = m.is_active
  showTreatmentMethodForm.value = true
}

async function submitTreatmentMethodForm() {
  if (!formTreatmentMethod.name.trim() || !formTreatmentMethod.unit.trim()) return
  savingTreatmentMethod.value = true
  try {
    const payload = {
      name: formTreatmentMethod.name.trim(),
      unit: formTreatmentMethod.unit.trim(),
      is_active: formTreatmentMethod.is_active
    }
    if (isEditTreatmentMethod.value) {
      await axios.put(`/api/admin/treatment-methods/${editingTreatmentMethodId.value}`, payload)
      showToast(t('admin.toast_method_updated', { name: payload.name }))
    } else {
      await axios.post('/api/admin/treatment-methods', payload)
      showToast(t('admin.toast_method_created', { name: payload.name }))
    }
    showTreatmentMethodForm.value = false
    await fetchTreatmentMethods()
  } catch (err) {
    console.error('Save treatment method error:', err)
    const errDetail = err.response?.data?.detail || t('admin.toast_method_save_error')
    showToast(errDetail, 'error')
  } finally {
    savingTreatmentMethod.value = false
  }
}

async function deleteTreatmentMethod(m) {
  const confirmed = await confirmStore.ask({
    title: t('admin.toast_method_delete_title'),
    message: t('admin.toast_method_delete_msg', { name: m.name }),
    type: 'danger',
    confirmText: t('common.delete')
  })
  if (!confirmed) return
  try {
    await axios.delete(`/api/admin/treatment-methods/${m.id}`)
    showToast(t('admin.toast_method_deleted', { name: m.name }))
    await fetchTreatmentMethods()
  } catch (err) {
    console.error('Delete treatment method error:', err)
    const errDetail = err.response?.data?.detail || t('admin.toast_method_delete_error')
    showToast(errDetail, 'error')
  }
}

// Treatment Application Types States
const treatmentApps = ref([])
const loadingTreatmentApps = ref(false)
const savingTreatmentApp = ref(false)
const showTreatmentAppForm = ref(false)
const isEditTreatmentApp = ref(false)
const editingTreatmentAppId = ref(null)

const formTreatmentApp = reactive({
  name: '',
  is_active: true
})

async function fetchTreatmentApps() {
  loadingTreatmentApps.value = true
  try {
    const res = await axios.get('/api/admin/treatment-application-types')
    treatmentApps.value = res.data
  } catch (err) {
    console.error('Fetch treatment application types error:', err)
    showToast(t('admin.toast_apps_load_error'), 'error')
  } finally {
    loadingTreatmentApps.value = false
  }
}

function openCreateTreatmentApp() {
  isEditTreatmentApp.value = false
  editingTreatmentAppId.value = null
  formTreatmentApp.name = ''
  formTreatmentApp.is_active = true
  showTreatmentAppForm.value = true
}

function openEditTreatmentApp(app) {
  isEditTreatmentApp.value = true
  editingTreatmentAppId.value = app.id
  formTreatmentApp.name = app.name
  formTreatmentApp.is_active = app.is_active
  showTreatmentAppForm.value = true
}

async function submitTreatmentAppForm() {
  if (!formTreatmentApp.name.trim()) return
  savingTreatmentApp.value = true
  try {
    const payload = {
      name: formTreatmentApp.name.trim(),
      is_active: formTreatmentApp.is_active
    }
    if (isEditTreatmentApp.value) {
      await axios.put(`/api/admin/treatment-application-types/${editingTreatmentAppId.value}`, payload)
      showToast(t('admin.toast_app_updated', { name: payload.name }))
    } else {
      await axios.post('/api/admin/treatment-application-types', payload)
      showToast(t('admin.toast_app_created', { name: payload.name }))
    }
    showTreatmentAppForm.value = false
    await fetchTreatmentApps()
  } catch (err) {
    console.error('Save treatment application type error:', err)
    const errDetail = err.response?.data?.detail || t('admin.toast_app_save_error')
    showToast(errDetail, 'error')
  } finally {
    savingTreatmentApp.value = false
  }
}

async function deleteTreatmentApp(app) {
  const confirmed = await confirmStore.ask({
    title: t('admin.toast_app_delete_title'),
    message: t('admin.toast_app_delete_msg', { name: app.name }),
    type: 'danger',
    confirmText: t('common.delete')
  })
  if (!confirmed) return
  try {
    await axios.delete(`/api/admin/treatment-application-types/${app.id}`)
    showToast(t('admin.toast_app_deleted', { name: app.name }))
    await fetchTreatmentApps()
  } catch (err) {
    console.error('Delete treatment application type error:', err)
    const errDetail = err.response?.data?.detail || t('admin.toast_app_delete_error')
    showToast(errDetail, 'error')
  }
}

onMounted(() => {
  fetchUsers()
  fetchLLMConfig()
  fetchAIInsightJobs()
  fetchFrameTypes()
  fetchNumberRanges()
  fetchTreatmentMethods()
  fetchTreatmentApps()
})
</script>

<style scoped>
/* List Transitions for Toasts */
.list-enter-active,
.list-leave-active {
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
.list-enter-from {
  opacity: 0;
  transform: translateY(30px) scale(0.9);
}
.list-leave-to {
  opacity: 0;
  transform: scale(0.9);
}
</style>
