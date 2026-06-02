<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 font-sans">
    
    <!-- Back to Dashboard Link -->
    <router-link to="/dashboard" class="inline-flex items-center text-sm font-semibold text-primary hover:text-primary-hover mb-4 transition-colors duration-200">
      <svg class="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"/></svg>
      {{ $t('common.back_to_dashboard') }}
    </router-link>

    <!-- Header Area -->
    <div class="mb-8 flex flex-col md:flex-row md:justify-between md:items-center space-y-4 md:space-y-0">
      <div>
        <h1 class="text-3xl font-extrabold text-gray-900 dark:text-white tracking-tight">💰 {{ $t('sales.title') }}</h1>
        <p class="text-gray-500 dark:text-gray-400 mt-1">{{ $t('sales.subtitle') }}</p>
      </div>
      
      <div class="flex items-center space-x-3" v-if="activeTab === 'sales'">
        <button 
          @click="exportCSV" 
          :disabled="sales.length === 0"
          class="px-4 py-2.5 bg-gray-100 hover:bg-gray-200 dark:bg-dark-card dark:hover:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-200 font-extrabold text-sm rounded-xl transition-all duration-200 hover-scale flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
          <span>{{ $t('sales.export_tax_csv_btn') }}</span>
        </button>
        <button 
          @click="openCreateSaleModal" 
          class="px-5 py-2.5 bg-primary hover:bg-primary-hover text-white font-extrabold text-sm rounded-xl shadow-md shadow-primary/20 hover-scale flex items-center justify-center space-x-2"
        >
          <span>{{ $t('sales.new_sale_btn') }}</span>
        </button>
      </div>
      
      <div v-else-if="activeTab === 'products'">
        <button 
          @click="openCreateProductModal" 
          class="px-5 py-2.5 bg-primary hover:bg-primary-hover text-white font-extrabold text-sm rounded-xl shadow-md shadow-primary/20 hover-scale flex items-center justify-center space-x-2"
        >
          <span>{{ $t('sales.new_product_btn') }}</span>
        </button>
      </div>
    </div>

    <!-- Alert Message -->
    <div v-if="alertMessage" class="mb-6 p-4 rounded-xl text-sm flex items-start space-x-2" :class="alertClass">
      <svg class="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
      <span>{{ alertMessage }}</span>
    </div>

    <!-- Tax Calculation Info Alert -->
    <div v-if="!taxSettings.calculate_taxes" class="mb-6 p-4 bg-amber-500/10 border border-amber-500/20 text-amber-800 dark:text-amber-300 rounded-2xl text-xs flex items-center space-x-2">
      <span class="text-base">💼</span>
      <span><strong>{{ $t('sales.tax_disabled_label') }}</strong> {{ $t('sales.tax_disabled_desc') }}</span>
    </div>

    <!-- Tabs Dock -->
    <div class="flex border-b border-gray-200 dark:border-dark-border mb-8 space-x-6">
      <button 
        @click="activeTab = 'sales'"
        class="pb-4 text-sm font-bold tracking-wide border-b-2 transition-all duration-200"
        :class="[
          activeTab === 'sales' 
            ? 'border-primary text-primary' 
            : 'border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
        ]"
      >
        📊 {{ $t('sales.tab_sales') }}
      </button>
      <button 
        @click="activeTab = 'products'"
        class="pb-4 text-sm font-bold tracking-wide border-b-2 transition-all duration-200"
        :class="[
          activeTab === 'products' 
            ? 'border-primary text-primary' 
            : 'border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
        ]"
      >
        🍯 {{ $t('sales.tab_products') }}
      </button>
      <button 
        @click="activeTab = 'inventory'"
        class="pb-4 text-sm font-bold tracking-wide border-b-2 transition-all duration-200"
        :class="[
          activeTab === 'inventory' 
            ? 'border-primary text-primary' 
            : 'border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
        ]"
      >
        📦 {{ $t('sales.tab_inventory') }}
      </button>
    </div>

    <!-- TAB 1: SALES LEDGER -->
    <div v-if="activeTab === 'sales'" class="space-y-6">
      
      <!-- Date Filters Card -->
      <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-6 shadow-sm flex flex-col md:flex-row gap-4 items-end animate-scale">
        <div class="flex-1 w-full">
          <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('sales.filter_start_date') }}</label>
          <input 
            v-model="filters.startDate" 
            type="date" 
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-sm font-mono focus:outline-none focus:ring-2 focus:ring-primary"
            @change="fetchSales"
          />
        </div>
        <div class="flex-1 w-full">
          <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('sales.filter_end_date') }}</label>
          <input 
            v-model="filters.endDate" 
            type="date" 
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-sm font-mono focus:outline-none focus:ring-2 focus:ring-primary"
            @change="fetchSales"
          />
        </div>
        <button 
          @click="resetFilters" 
          class="px-4 py-2 bg-gray-100 hover:bg-gray-200 dark:bg-gray-800 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-200 text-xs font-bold rounded-xl transition duration-150 border border-gray-200 dark:border-gray-700 w-full md:w-auto h-[38px] flex items-center justify-center hover-scale"
        >
          {{ $t('sales.filter_reset') }}
        </button>
      </div>

      <!-- Ledger Table -->
      <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl overflow-hidden shadow-sm">
        <div v-if="loadingSales" class="flex flex-col items-center justify-center py-20">
          <svg class="animate-spin h-8 w-8 text-primary mb-3" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
          <span class="text-xs text-gray-400 font-bold">{{ $t('sales.loading_sales') }}</span>
        </div>

        <div v-else-if="sales.length === 0" class="flex flex-col items-center justify-center py-20 text-center px-4">
          <span class="text-4xl mb-3">💸</span>
          <h3 class="text-base font-bold text-gray-900 dark:text-white">{{ $t('sales.empty_sales_title') }}</h3>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1 max-w-sm">{{ $t('sales.empty_sales_desc') }}</p>
        </div>

        <div v-else class="overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="bg-gray-50 dark:bg-dark-bg text-gray-500 dark:text-gray-400 text-[10px] font-bold uppercase tracking-wider border-b border-gray-100 dark:border-dark-border">
                <th class="px-6 py-4">{{ $t('sales.table_date') }}</th>
                <th class="px-6 py-4">{{ $t('sales.table_product') }}</th>
                <th class="px-6 py-4 text-center">{{ $t('sales.table_quantity') }}</th>
                <th class="px-6 py-4 text-right">{{ $t('sales.table_total_price') }}</th>
                <th class="px-6 py-4 text-center">{{ $t('sales.table_tax') }}</th>
                <th class="px-6 py-4">{{ $t('sales.table_channel') }}</th>
                <th class="px-6 py-4">{{ $t('sales.table_batch') }}</th>
                <th class="px-6 py-4">{{ $t('sales.table_buyer') }}</th>
                <th class="px-6 py-4">{{ $t('sales.table_notes') }}</th>
                <th class="px-6 py-4 text-right">{{ $t('common.actions') }}</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100 dark:divide-dark-border text-sm">
              <tr 
                v-for="s in sales" 
                :key="s.id" 
                class="hover:bg-gray-50/50 dark:hover:bg-dark-bg/30 transition-colors duration-150"
              >
                <!-- Date -->
                <td class="px-6 py-4 font-mono text-xs text-gray-600 dark:text-gray-300">
                  {{ formatDateTime(s.sale_date) }}
                </td>
                
                <!-- Product Name -->
                <td class="px-6 py-4 font-bold text-gray-800 dark:text-gray-200">
                  {{ s.product?.name || $t('sales.deleted_product') }}
                </td>
                
                <!-- Quantity -->
                <td class="px-6 py-4 text-center text-gray-600 dark:text-gray-300">
                  {{ s.quantity }}
                </td>
                
                <!-- Total Price -->
                <td class="px-6 py-4 text-right font-bold text-gray-800 dark:text-gray-200">
                  {{ formatCurrency(s.total_price) }}
                </td>
                
                <!-- Tax -->
                <td class="px-6 py-4 text-center">
                  <span v-if="!taxSettings.calculate_taxes" class="text-xs text-gray-400">
                    0%
                  </span>
                  <span v-else class="text-xs text-gray-600 dark:text-gray-400">
                    {{ s.product?.tax_rate || 0 }}% <span class="text-[10px] text-gray-400">({{ formatCurrency(calculateVAT(s.total_price, s.product?.tax_rate)) }})</span>
                  </span>
                </td>

                <!-- Sales Channel -->
                <td class="px-6 py-4">
                  <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-primary/10 text-primary uppercase">
                    {{ formatChannel(s.sales_channel) }}
                  </span>
                </td>

                <!-- Honey Batch -->
                <td class="px-6 py-4 font-mono text-xs text-amber-600 dark:text-amber-400">
                  {{ s.batch?.batch_number || '-' }}
                </td>

                <!-- Buyer -->
                <td class="px-6 py-4 text-xs text-gray-600 dark:text-gray-300 max-w-[150px] truncate" :title="s.buyer">
                  {{ s.buyer || '-' }}
                </td>

                <!-- Notes -->
                <td class="px-6 py-4 text-gray-500 dark:text-gray-400 max-w-[200px] truncate" :title="s.notes">
                  {{ s.notes || '-' }}
                </td>

                <!-- Actions -->
                <td class="px-6 py-4 text-right space-x-2">
                  <button 
                    @click="openEditSaleModal(s)" 
                    class="p-1.5 text-gray-500 hover:text-primary hover:bg-gray-100 dark:hover:bg-dark-border rounded-lg transition-all duration-150 inline-flex hover-scale"
                    :title="$t('common.edit')"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/></svg>
                  </button>
                  <button 
                    @click="deleteSale(s)" 
                    class="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-500/10 rounded-lg transition-all duration-150 inline-flex hover-scale"
                    :title="$t('common.delete')"
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

    <!-- TAB 2: PRODUCT MANAGEMENT -->
    <div v-else-if="activeTab === 'products'" class="space-y-6">
      
      <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl overflow-hidden shadow-sm">
        <div v-if="loadingProducts" class="flex flex-col items-center justify-center py-20">
          <svg class="animate-spin h-8 w-8 text-primary mb-3" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
          <span class="text-xs text-gray-400 font-bold">{{ $t('sales.loading_products') }}</span>
        </div>

        <div v-else-if="products.length === 0" class="flex flex-col items-center justify-center py-20 text-center px-4">
          <span class="text-4xl mb-3">🍯</span>
          <h3 class="text-base font-bold text-gray-900 dark:text-white">{{ $t('sales.empty_products_title') }}</h3>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1 max-w-sm">{{ $t('sales.empty_products_desc') }}</p>
        </div>

        <div v-else class="overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="bg-gray-50 dark:bg-dark-bg text-gray-500 dark:text-gray-400 text-[10px] font-bold uppercase tracking-wider border-b border-gray-100 dark:border-dark-border">
                <th class="px-6 py-4">{{ $t('sales.table_name') }}</th>
                <th class="px-6 py-4">{{ $t('sales.table_honey_type') }}</th>
                <th class="px-6 py-4 text-right">{{ $t('sales.table_default_price') }}</th>
                <th class="px-6 py-4 text-center">{{ $t('sales.table_tax_rate') }}</th>
                <th class="px-6 py-4 text-center">{{ $t('sales.table_requires_batch') }}</th>
                <th class="px-6 py-4 text-center">{{ $t('sales.table_stock') }}</th>
                <th class="px-6 py-4 text-center">{{ $t('common.status') }}</th>
                <th class="px-6 py-4 text-right">{{ $t('common.actions') }}</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100 dark:divide-dark-border text-sm">
              <tr 
                v-for="p in products" 
                :key="p.id" 
                class="hover:bg-gray-50/50 dark:hover:bg-dark-bg/30 transition-colors duration-150"
              >
                <!-- Name -->
                <td class="px-6 py-4 font-bold text-gray-800 dark:text-gray-200">
                  {{ p.name }}
                </td>
                
                <!-- Honey Type -->
                <td class="px-6 py-4 text-gray-600 dark:text-gray-300">
                  {{ p.honey_type || '-' }}
                </td>
                
                <!-- Price -->
                <td class="px-6 py-4 text-right font-bold text-gray-800 dark:text-gray-200">
                  {{ formatCurrency(p.price) }}
                </td>
                
                <!-- Tax Rate -->
                <td class="px-6 py-4 text-center">
                  <span v-if="!taxSettings.calculate_taxes" class="text-xs text-gray-400 italic">
                    0%
                  </span>
                  <span v-else class="text-xs text-gray-600 dark:text-gray-300">
                    {{ p.tax_rate }}%
                  </span>
                </td>

                <!-- Requires Batch -->
                <td class="px-6 py-4 text-center">
                  <span
                    class="px-2 py-0.5 rounded-full text-[10px] font-bold"
                    :class="p.requires_batch_selection ? 'bg-amber-500/10 text-amber-600 dark:text-amber-400' : 'bg-gray-100 text-gray-400 dark:bg-gray-800'"
                  >
                    {{ p.requires_batch_selection ? '🔗 ' + $t('sales.requires_batch_badge') : $t('sales.optional_badge') }}
                  </span>
                </td>

                <!-- Stock -->
                <td class="px-6 py-4 text-center">
                  <span v-if="!p.manage_stock" class="text-xs text-gray-400 dark:text-gray-600">
                    -
                  </span>
                  <span v-else-if="p.stock <= 0" class="px-2.5 py-1 rounded-full text-[10px] font-bold bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/20">
                    🔴 0 ({{ $t('sales.stock_none_badge') }})
                  </span>
                  <span v-else-if="p.stock <= p.min_stock" class="px-2.5 py-1 rounded-full text-[10px] font-bold bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20" :title="`${$t('sales.table_min_stock')}: ${p.min_stock}`">
                    ⚠️ {{ p.stock }} ({{ $t('sales.stock_alert_badge') }})
                  </span>
                  <span v-else class="px-2.5 py-1 rounded-full text-[10px] font-bold bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
                    📦 {{ p.stock }}
                  </span>
                </td>

                <!-- Status -->
                <td class="px-6 py-4 text-center">
                  <span 
                    class="px-2 py-0.5 rounded-full text-[10px] font-bold"
                    :class="p.is_active ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400' : 'bg-rose-500/10 text-rose-600 dark:text-rose-400'"
                  >
                    {{ p.is_active ? $t('common.active') : $t('common.inactive') }}
                  </span>
                </td>

                <!-- Actions -->
                <td class="px-6 py-4 text-right space-x-2">
                  <button 
                    @click="openEditProductModal(p)" 
                    class="p-1.5 text-gray-500 hover:text-primary hover:bg-gray-100 dark:hover:bg-dark-border rounded-lg transition-all duration-150 inline-flex hover-scale"
                    :title="$t('common.edit')"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/></svg>
                  </button>
                  <button 
                    @click="deleteProduct(p)" 
                    class="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-500/10 rounded-lg transition-all duration-150 inline-flex hover-scale"
                    :title="$t('common.delete')"
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

    <!-- TAB 3: INVENTORY MANAGEMENT -->
    <div v-else-if="activeTab === 'inventory'" class="space-y-6">
      <!-- Inventory Filters Card -->
      <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-6 shadow-sm flex flex-col md:flex-row gap-4 items-end animate-scale">
        <div class="flex-1 w-full">
          <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('sales.table_name') }} / {{ $t('sales.table_honey_type') }}</label>
          <input 
            v-model="inventoryFilters.searchQuery" 
            type="text" 
            :placeholder="$t('sales.product_name_placeholder')"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>
        <div class="flex-1 w-full">
          <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('sales.filter_stock_status') }}</label>
          <select 
            v-model="inventoryFilters.status" 
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary"
          >
            <option value="all">{{ $t('sales.stock_filter_all') }}</option>
            <option value="low">{{ $t('sales.stock_filter_low') }}</option>
            <option value="empty">{{ $t('sales.stock_filter_empty') }}</option>
            <option value="ok">{{ $t('sales.stock_filter_ok') }}</option>
          </select>
        </div>
        <div class="flex items-center space-x-2 pb-2 h-[38px]">
          <label class="flex items-center space-x-2 cursor-pointer">
            <input
              v-model="inventoryFilters.showUnmanaged"
              type="checkbox"
              class="rounded text-primary focus:ring-primary h-4 w-4"
            />
            <span class="text-xs font-bold text-gray-700 dark:text-gray-300">{{ $t('sales.filter_show_unmanaged') }}</span>
          </label>
        </div>
      </div>

      <!-- Inventory Table -->
      <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl overflow-hidden shadow-sm">
        <div v-if="loadingProducts" class="flex flex-col items-center justify-center py-20">
          <svg class="animate-spin h-8 w-8 text-primary mb-3" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
          <span class="text-xs text-gray-400 font-bold">{{ $t('sales.loading_products') }}</span>
        </div>

        <div v-else-if="filteredInventory.length === 0" class="flex flex-col items-center justify-center py-20 text-center px-4">
          <span class="text-4xl mb-3">📦</span>
          <h3 class="text-base font-bold text-gray-900 dark:text-white">{{ $t('sales.empty_products_title') }}</h3>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1 max-w-sm">{{ $t('sales.empty_products_desc') }}</p>
        </div>

        <div v-else class="overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="bg-gray-50 dark:bg-dark-bg text-gray-500 dark:text-gray-400 text-[10px] font-bold uppercase tracking-wider border-b border-gray-100 dark:border-dark-border">
                <th class="px-6 py-4">{{ $t('sales.table_name') }}</th>
                <th class="px-6 py-4">{{ $t('sales.table_honey_type') }}</th>
                <th class="px-6 py-4 text-right">{{ $t('sales.table_default_price') }}</th>
                <th class="px-6 py-4 text-center">{{ $t('sales.table_stock') }}</th>
                <th class="px-6 py-4 text-center">{{ $t('sales.table_min_stock') }}</th>
                <th class="px-6 py-4 text-right">{{ $t('common.actions') }}</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100 dark:divide-dark-border text-sm">
              <tr 
                v-for="p in filteredInventory" 
                :key="p.id" 
                class="hover:bg-gray-50/50 dark:hover:bg-dark-bg/30 transition-colors duration-150"
              >
                <!-- Name -->
                <td class="px-6 py-4 font-bold text-gray-800 dark:text-gray-200">
                  {{ p.name }}
                </td>
                
                <!-- Honey Type -->
                <td class="px-6 py-4 text-gray-600 dark:text-gray-300">
                  {{ p.honey_type || '-' }}
                </td>
                
                <!-- Price -->
                <td class="px-6 py-4 text-right font-bold text-gray-800 dark:text-gray-200">
                  {{ formatCurrency(p.price) }}
                </td>
                
                <!-- Stock -->
                <td class="px-6 py-4 text-center">
                  <span v-if="!p.manage_stock" class="text-xs text-gray-400 dark:text-gray-600">
                    -
                  </span>
                  <span v-else-if="p.stock <= 0" class="px-2.5 py-1 rounded-full text-[10px] font-bold bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/20">
                    🔴 0 ({{ $t('sales.stock_none_badge') }})
                  </span>
                  <span v-else-if="p.stock <= p.min_stock" class="px-2.5 py-1 rounded-full text-[10px] font-bold bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20" :title="`${$t('sales.table_min_stock')}: ${p.min_stock}`">
                    ⚠️ {{ p.stock }} ({{ $t('sales.stock_alert_badge') }})
                  </span>
                  <span v-else class="px-2.5 py-1 rounded-full text-[10px] font-bold bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
                    📦 {{ p.stock }}
                  </span>
                </td>

                <!-- Min Stock -->
                <td class="px-6 py-4 text-center text-gray-600 dark:text-gray-300">
                  {{ p.manage_stock ? p.min_stock : '-' }}
                </td>

                <!-- Actions -->
                <td class="px-6 py-4 text-right space-x-2">
                  <button 
                    v-if="p.manage_stock"
                    @click="openAdjustStockModal(p)" 
                    class="px-2.5 py-1.5 bg-primary/10 hover:bg-primary/20 dark:bg-primary/20 dark:hover:bg-primary/30 text-primary text-xs font-bold rounded-lg transition-all duration-150 hover-scale inline-flex items-center space-x-1"
                    :title="$t('sales.adjust_stock_btn')"
                  >
                    <span>🔄</span>
                    <span class="hidden md:inline">{{ $t('sales.adjust_stock_btn') }}</span>
                  </button>
                  <button 
                    @click="openStockConfigModal(p)" 
                    class="p-1.5 text-gray-500 hover:text-primary hover:bg-gray-100 dark:hover:bg-dark-border rounded-lg transition-all duration-150 inline-flex hover-scale"
                    :title="$t('common.edit')"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/></svg>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- SALES MODAL -->
    <div v-if="showSaleModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl shadow-xl w-full max-w-xl p-6 animate-scale">
        <div class="flex justify-between items-center mb-6 pb-4 border-b border-gray-100 dark:border-dark-border">
          <h3 class="text-xl font-bold text-gray-900 dark:text-white">
            {{ isEditMode ? $t('sales.edit_sale_title') : $t('sales.create_sale_title') }}
          </h3>
          <button @click="closeSaleModal" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>

        <form @submit.prevent="submitSaleForm">
          <div class="space-y-4">
            <!-- Product Select -->
            <div>
              <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('sales.product_label') }}</label>
              <select 
                v-model="saleForm.product_id" 
                required
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm"
                @change="onProductChange"
              >
                <option value="" disabled>{{ $t('sales.select_product_placeholder') }}</option>
                <option v-for="p in activeProducts" :key="p.id" :value="p.id">
                  {{ p.name }} ({{ formatCurrency(p.price) }})
                </option>
              </select>
              <p v-if="activeProducts.length === 0" class="text-[11px] text-red-500 font-bold mt-1">
                ⚠️ {{ $t('sales.no_active_products_warning') }}
              </p>
              
              <!-- Stock Info Banner -->
              <div v-if="selectedProduct && selectedProduct.manage_stock" class="mt-2 text-xs animate-scale">
                <span v-if="selectedProduct.stock <= 0" class="inline-flex items-center px-2.5 py-1 rounded-xl bg-rose-500/10 text-rose-600 dark:text-rose-400 font-bold border border-rose-500/20">
                  🔴 {{ $t('sales.stock_none_badge') }} (0 Stk. verfügbar)
                </span>
                <span v-else-if="selectedProduct.stock <= selectedProduct.min_stock" class="inline-flex items-center px-2.5 py-1 rounded-xl bg-amber-500/10 text-amber-600 dark:text-amber-400 font-bold border border-amber-500/20">
                  ⚠️ {{ $t('sales.stock_alert_badge') }}: {{ selectedProduct.stock }} Stk. verfügbar (Mindestbestand: {{ selectedProduct.min_stock }} Stk.)
                </span>
                <span v-else class="inline-flex items-center px-2.5 py-1 rounded-xl bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 font-bold border border-emerald-500/20">
                  📦 {{ $t('sales.stock_ok_badge') }}: {{ selectedProduct.stock }} Stk. verfügbar
                </span>
              </div>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <!-- Quantity -->
              <div>
                <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('sales.quantity_label') }}</label>
                <input 
                  v-model.number="saleForm.quantity" 
                  type="number" 
                  min="1"
                  required
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm font-mono"
                  @input="recalculateTotalPrice"
                />
                
                <!-- Stock warnings -->
                <div v-if="selectedProduct && selectedProduct.manage_stock" class="mt-1.5 text-[11px] font-bold animate-scale">
                  <p v-if="saleForm.quantity > selectedProduct.stock" class="text-rose-600 dark:text-rose-400">
                    ⚠️ {{ $t('sales.warning_insufficient_stock', { qty: saleForm.quantity, stock: selectedProduct.stock }) }}
                  </p>
                  <p v-else-if="selectedProduct.stock - saleForm.quantity < selectedProduct.min_stock" class="text-amber-600 dark:text-amber-400">
                    ⚠️ {{ $t('sales.warning_low_stock', { min: selectedProduct.min_stock }) }}
                  </p>
                </div>
              </div>

              <!-- Total Price -->
              <div>
                <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('sales.total_price_label') }}</label>
                <input 
                  v-model.number="saleForm.total_price" 
                  type="number" 
                  step="0.01"
                  min="0.01"
                  required
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm font-mono"
                />
              </div>
            </div>

            <!-- Sales Channel -->
            <div>
              <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('sales.channel_label') }}</label>
              <select 
                v-model="saleForm.sales_channel" 
                required
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm"
              >
                <option value="direktverkauf">{{ formatChannel('direktverkauf') }}</option>
                <option value="online">{{ formatChannel('online') }}</option>
                <option value="email">{{ formatChannel('email') }}</option>
                <option value="verkaufsstand">{{ formatChannel('verkaufsstand') }}</option>
              </select>
            </div>

            <!-- Honey Batch (optional / required) -->
            <div>
              <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">
                {{ $t('sales.honey_batch_label') }}
                <span v-if="selectedProductRequiresBatch" class="text-red-500">*</span>
                <span v-else class="text-gray-400 font-normal">({{ $t('sales.optional_badge') }})</span>
              </label>
              <select
                v-model="saleForm.batch_id"
                :required="selectedProductRequiresBatch"
                class="w-full px-3 py-2 border rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm font-mono transition-colors"
                :class="selectedProductRequiresBatch && !saleForm.batch_id
                  ? 'border-amber-400 dark:border-amber-500 dark:bg-dark-bg dark:text-white'
                  : 'border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white'"
              >
                <option :value="null">{{ $t('sales.no_batch_link') }}</option>
                <option v-for="b in batches" :key="b.id" :value="b.id">
                  {{ b.batch_number || `MHD: ${formatDate(b.best_before_date)}` }} - {{ b.honey_type }} ({{ b.quantity_kg }} kg)
                </option>
              </select>
              <p v-if="selectedProductRequiresBatch && !saleForm.batch_id" class="text-[11px] text-amber-600 dark:text-amber-400 font-bold mt-1">
                ⚠️ {{ $t('sales.requires_batch_warning') }}
              </p>
            </div>

            <!-- Sale Date -->
            <div>
              <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('sales.sale_date_label') }}</label>
              <input 
                v-model="saleForm.sale_date" 
                type="datetime-local" 
                required
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm font-mono"
              />
            </div>

            <!-- Buyer (optional) -->
            <div>
              <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('sales.buyer_label') }} <span class="text-gray-400 font-normal">({{ $t('sales.optional_badge') }})</span></label>
              <input
                v-model="saleForm.buyer"
                type="text"
                :placeholder="$t('sales.buyer_placeholder')"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm"
              />
            </div>

            <!-- Notes -->
            <div>
              <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('sales.notes_label') }}</label>
              <textarea
                v-model="saleForm.notes"
                rows="2"
                :placeholder="$t('sales.notes_placeholder')"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm"
              ></textarea>
            </div>
          </div>

          <div class="flex justify-end space-x-3 pt-6 border-t border-gray-100 dark:border-dark-border mt-6">
            <button 
              type="button" 
              @click="closeSaleModal" 
              class="px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-xl text-xs font-semibold hover:bg-gray-100 dark:hover:bg-dark-border text-gray-700 dark:text-gray-300"
            >
              {{ $t('common.cancel') }}
            </button>
            <button 
              type="submit" 
              class="px-5 py-2 bg-primary hover:bg-primary-hover text-white text-xs font-bold rounded-xl shadow-md hover-scale"
            >
              {{ $t('common.save') }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- PRODUCT MODAL -->
    <div v-if="showProductModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl shadow-xl w-full max-w-md p-6 animate-scale">
        <div class="flex justify-between items-center mb-6 pb-4 border-b border-gray-100 dark:border-dark-border">
          <h3 class="text-xl font-bold text-gray-900 dark:text-white">
            {{ isEditMode ? $t('sales.edit_product_title') : $t('sales.create_product_title') }}
          </h3>
          <button @click="closeProductModal" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>

        <form @submit.prevent="submitProductForm">
          <div class="space-y-4">
            <!-- Name -->
            <div>
              <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('sales.product_name_label') }} *</label>
              <input 
                v-model="productForm.name" 
                type="text" 
                required
                :placeholder="$t('sales.product_name_placeholder')"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm"
              />
            </div>

            <!-- Honey Type -->
            <div>
              <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('sales.product_honey_type_label') }}</label>
              <input 
                v-model="productForm.honey_type" 
                type="text" 
                :placeholder="$t('sales.product_honey_type_placeholder')"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm"
              />
            </div>

            <!-- Price -->
            <div>
              <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('sales.product_default_price_label') }} *</label>
              <input 
                v-model.number="productForm.price" 
                type="number" 
                step="0.01"
                min="0.01"
                required
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm font-mono"
              />
            </div>

            <!-- Tax Rate -->
            <div v-if="taxSettings.calculate_taxes">
              <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('sales.product_tax_rate_label') }} *</label>
              <select 
                v-model.number="productForm.tax_rate" 
                required
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm font-mono"
              >
                <option v-for="rate in settingsStore.taxRates" :key="rate" :value="rate">{{ rate }} %</option>
              </select>
            </div>
            <div v-else class="p-3 bg-gray-50 dark:bg-dark-bg border border-gray-100 dark:border-dark-border rounded-xl">
              <span class="text-xs text-gray-500 dark:text-gray-400 font-bold block mb-1">{{ $t('sales.product_tax_rate_label') }}</span>
              <span class="text-xs text-gray-600 dark:text-gray-300">0.0 % ({{ $t('sales.tax_disabled_short') }})</span>
            </div>

            <!-- Requires Batch Selection -->
            <div class="flex items-center pt-1">
              <label class="flex items-center space-x-2 cursor-pointer">
                <input
                  v-model="productForm.requires_batch_selection"
                  type="checkbox"
                  class="rounded text-primary focus:ring-primary h-4 w-4"
                />
                <span class="text-xs font-bold text-gray-700 dark:text-gray-300">{{ $t('sales.product_requires_batch_checkbox') }}</span>
              </label>
            </div>

            <!-- Manage Stock -->
            <div class="flex items-center pt-1">
              <label class="flex items-center space-x-2 cursor-pointer">
                <input
                  v-model="productForm.manage_stock"
                  type="checkbox"
                  class="rounded text-primary focus:ring-primary h-4 w-4"
                />
                <span class="text-xs font-bold text-gray-700 dark:text-gray-300">{{ $t('sales.product_manage_stock_checkbox') }}</span>
              </label>
            </div>

            <!-- Stock Details -->
            <div v-if="productForm.manage_stock" class="grid grid-cols-2 gap-4 pt-1 animate-scale">
              <div>
                <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('sales.product_stock_label') }}</label>
                <input 
                  v-model.number="productForm.stock" 
                  type="number" 
                  step="any"
                  min="0"
                  required
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm font-mono"
                />
              </div>
              <div>
                <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('sales.product_min_stock_label') }}</label>
                <input 
                  v-model.number="productForm.min_stock" 
                  type="number" 
                  step="any"
                  min="0"
                  required
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm font-mono"
                />
              </div>
            </div>

            <!-- Is Active -->
            <div class="flex items-center pt-1">
              <label class="flex items-center space-x-2 cursor-pointer">
                <input
                  v-model="productForm.is_active"
                  type="checkbox"
                  class="rounded text-primary focus:ring-primary h-4 w-4"
                />
                <span class="text-xs font-bold text-gray-700 dark:text-gray-300">{{ $t('sales.product_is_active_checkbox') }}</span>
              </label>
            </div>
          </div>

          <div class="flex justify-end space-x-3 pt-6 border-t border-gray-100 dark:border-dark-border mt-6">
            <button 
              type="button" 
              @click="closeProductModal" 
              class="px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-xl text-xs font-semibold hover:bg-gray-100 dark:hover:bg-dark-border text-gray-700 dark:text-gray-300"
            >
              {{ $t('common.cancel') }}
            </button>
            <button 
              type="submit" 
              class="px-5 py-2 bg-primary hover:bg-primary-hover text-white text-xs font-bold rounded-xl shadow-md hover-scale"
            >
              {{ $t('common.save') }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- STOCK ADJUSTMENT MODAL -->
    <div v-if="showAdjustStockModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl shadow-xl w-full max-w-md p-6 animate-scale">
        <div class="flex justify-between items-center mb-6 pb-4 border-b border-gray-100 dark:border-dark-border">
          <h3 class="text-xl font-bold text-gray-900 dark:text-white">
            🔄 {{ $t('sales.adjust_stock_title') }}
          </h3>
          <button @click="closeAdjustStockModal" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>

        <div v-if="adjustingProduct" class="mb-4 p-3 bg-gray-50 dark:bg-dark-bg border border-gray-100 dark:border-dark-border rounded-2xl text-xs">
          <span class="font-bold text-gray-800 dark:text-gray-200 block mb-1">{{ adjustingProduct.name }}</span>
          <span class="text-gray-500 dark:text-gray-400">Aktueller Bestand: <strong>{{ adjustingProduct.stock }} Stk.</strong> (Min: {{ adjustingProduct.min_stock }} Stk.)</span>
        </div>

        <form @submit.prevent="submitAdjustStockForm">
          <div class="space-y-4">
            <!-- Action selection -->
            <div>
              <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-2">{{ $t('sales.adjust_type_label') }}</label>
              <div class="grid grid-cols-3 gap-2">
                <label 
                  class="flex flex-col items-center justify-center p-3 border rounded-xl cursor-pointer text-center select-none transition-all duration-150 hover:bg-gray-50 dark:hover:bg-dark-bg"
                  :class="adjustStockForm.type === 'add' ? 'border-primary bg-primary/5 text-primary' : 'border-gray-200 dark:border-gray-700'"
                >
                  <input type="radio" v-model="adjustStockForm.type" value="add" class="sr-only" />
                  <span class="text-lg mb-1">📈</span>
                  <span class="text-[10px] font-bold uppercase tracking-wider">{{ $t('sales.adjust_type_add') }}</span>
                </label>
                <label 
                  class="flex flex-col items-center justify-center p-3 border rounded-xl cursor-pointer text-center select-none transition-all duration-150 hover:bg-gray-50 dark:hover:bg-dark-bg"
                  :class="adjustStockForm.type === 'sub' ? 'border-primary bg-primary/5 text-primary' : 'border-gray-200 dark:border-gray-700'"
                >
                  <input type="radio" v-model="adjustStockForm.type" value="sub" class="sr-only" />
                  <span class="text-lg mb-1">📉</span>
                  <span class="text-[10px] font-bold uppercase tracking-wider">{{ $t('sales.adjust_type_sub') }}</span>
                </label>
                <label 
                  class="flex flex-col items-center justify-center p-3 border rounded-xl cursor-pointer text-center select-none transition-all duration-150 hover:bg-gray-50 dark:hover:bg-dark-bg"
                  :class="adjustStockForm.type === 'set' ? 'border-primary bg-primary/5 text-primary' : 'border-gray-200 dark:border-gray-700'"
                >
                  <input type="radio" v-model="adjustStockForm.type" value="set" class="sr-only" />
                  <span class="text-lg mb-1">🎯</span>
                  <span class="text-[10px] font-bold uppercase tracking-wider">{{ $t('sales.adjust_type_set') }}</span>
                </label>
              </div>
            </div>

            <!-- Amount Input -->
            <div>
              <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('sales.adjust_amount_label') }}</label>
              <input 
                v-model.number="adjustStockForm.amount" 
                type="number" 
                step="any"
                min="0"
                required
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm font-mono"
              />
            </div>

            <!-- Resulting Stock Preview -->
            <div v-if="adjustingProduct" class="p-3 bg-primary/5 border border-primary/10 rounded-2xl text-xs flex justify-between items-center">
              <span class="font-bold text-gray-600 dark:text-gray-400">Neuer berechneter Bestand:</span>
              <span class="text-base font-extrabold" :class="resultingStockClass">
                {{ resultingStock }} Stk.
              </span>
            </div>

            <!-- Warning if resulting stock is low -->
            <div v-if="resultingStockWarning" class="p-3 bg-amber-500/10 border border-amber-500/20 text-amber-800 dark:text-amber-300 rounded-2xl text-[11px] font-bold flex items-center space-x-1.5 animate-scale">
              <span>⚠️</span>
              <span>{{ resultingStockWarning }}</span>
            </div>
          </div>

          <div class="flex justify-end space-x-3 pt-6 border-t border-gray-100 dark:border-dark-border mt-6">
            <button 
              type="button" 
              @click="closeAdjustStockModal" 
              class="px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-xl text-xs font-semibold hover:bg-gray-100 dark:hover:bg-dark-border text-gray-700 dark:text-gray-300"
            >
              {{ $t('common.cancel') }}
            </button>
            <button 
              type="submit" 
              class="px-5 py-2 bg-primary hover:bg-primary-hover text-white text-xs font-bold rounded-xl shadow-md hover-scale"
            >
              {{ $t('common.save') }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- STOCK CONFIGURATION MODAL -->
    <div v-if="showStockConfigModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl shadow-xl w-full max-w-md p-6 animate-scale">
        <div class="flex justify-between items-center mb-6 pb-4 border-b border-gray-100 dark:border-dark-border">
          <h3 class="text-xl font-bold text-gray-900 dark:text-white">
            ⚙️ {{ $t('sales.edit_stock_config_title') }}
          </h3>
          <button @click="closeStockConfigModal" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>

        <div v-if="configuringProduct" class="mb-4 p-3 bg-gray-50 dark:bg-dark-bg border border-gray-100 dark:border-dark-border rounded-2xl text-xs">
          <span class="font-bold text-gray-800 dark:text-gray-200 block mb-1">{{ configuringProduct.name }}</span>
          <span class="text-gray-500 dark:text-gray-400" v-if="configuringProduct.honey_type">{{ configuringProduct.honey_type }}</span>
        </div>

        <form @submit.prevent="submitStockConfigForm">
          <div class="space-y-4">
            <!-- Manage Stock Toggle -->
            <div class="flex items-center pt-1">
              <label class="flex items-center space-x-2 cursor-pointer">
                <input
                  v-model="stockConfigForm.manage_stock"
                  type="checkbox"
                  class="rounded text-primary focus:ring-primary h-4 w-4"
                />
                <span class="text-xs font-bold text-gray-700 dark:text-gray-300">{{ $t('sales.product_manage_stock_checkbox') }}</span>
              </label>
            </div>

            <!-- Stock Details (Visible only when managing stock) -->
            <div v-if="stockConfigForm.manage_stock" class="grid grid-cols-2 gap-4 pt-1 animate-scale">
              <div>
                <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('sales.product_stock_label') }}</label>
                <input 
                  v-model.number="stockConfigForm.stock" 
                  type="number" 
                  step="any"
                  min="0"
                  required
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm font-mono"
                />
              </div>
              <div>
                <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">{{ $t('sales.product_min_stock_label') }}</label>
                <input 
                  v-model.number="stockConfigForm.min_stock" 
                  type="number" 
                  step="any"
                  min="0"
                  required
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm font-mono"
                />
              </div>
            </div>
          </div>

          <div class="flex justify-end space-x-3 pt-6 border-t border-gray-100 dark:border-dark-border mt-6">
            <button 
              type="button" 
              @click="closeStockConfigModal" 
              class="px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-xl text-xs font-semibold hover:bg-gray-100 dark:hover:bg-dark-border text-gray-700 dark:text-gray-300"
            >
              {{ $t('common.cancel') }}
            </button>
            <button 
              type="submit" 
              class="px-5 py-2 bg-primary hover:bg-primary-hover text-white text-xs font-bold rounded-xl shadow-md hover-scale"
            >
              {{ $t('common.save') }}
            </button>
          </div>
        </form>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import axios from 'axios'
import { useI18n } from 'vue-i18n'
import { useApiaryStore } from '../stores/apiary'
import { useConfirmStore } from '../stores/confirm'
import { useSettingsStore } from '../stores/settings'

const apiaryStore = useApiaryStore()
const confirmStore = useConfirmStore()
const settingsStore = useSettingsStore()
const { t, locale } = useI18n()

const activeTab = ref('sales')
const sales = ref([])
const products = ref([])
const batches = ref([])
const taxSettings = ref({ calculate_taxes: true })

const loadingSales = ref(false)
const loadingProducts = ref(false)
const isEditMode = ref(false)
const editingId = ref(null)

const showSaleModal = ref(false)
const showProductModal = ref(false)

const alertMessage = ref('')
const alertClass = ref('')

const filters = reactive({
  startDate: '',
  endDate: ''
})

const saleForm = reactive({
  product_id: '',
  quantity: 1,
  total_price: 0,
  sales_channel: 'direktverkauf',
  batch_id: null,
  sale_date: '',
  notes: '',
  buyer: ''
})

const productForm = reactive({
  name: '',
  honey_type: '',
  price: 0,
  tax_rate: 7.0,
  is_active: true,
  requires_batch_selection: false,
  manage_stock: false,
  stock: 0,
  min_stock: 0
})

const inventoryFilters = reactive({
  searchQuery: '',
  status: 'all',
  showUnmanaged: false
})

const showAdjustStockModal = ref(false)
const adjustingProduct = ref(null)
const adjustStockForm = reactive({
  type: 'add',
  amount: 0
})

const showStockConfigModal = ref(false)
const configuringProduct = ref(null)
const stockConfigForm = reactive({
  manage_stock: false,
  stock: 0,
  min_stock: 0
})

function showAlert(message, type = 'success') {
  alertMessage.value = message
  alertClass.value = type === 'success' 
    ? 'bg-emerald-500/10 border border-emerald-500/20 text-emerald-600 dark:text-emerald-400' 
    : 'bg-rose-500/10 border border-rose-500/20 text-rose-600 dark:text-rose-400'
  setTimeout(() => {
    alertMessage.value = ''
  }, 4000)
}

const activeProducts = computed(() => {
  return products.value.filter(p => p.is_active)
})

const selectedProduct = computed(() => {
  if (!saleForm.product_id) return null
  return products.value.find(p => p.id === saleForm.product_id) || null
})

const filteredInventory = computed(() => {
  return products.value.filter(p => {
    // 1. Filter by showUnmanaged
    if (!inventoryFilters.showUnmanaged && !p.manage_stock) {
      return false
    }

    // 2. Filter by searchQuery (product name or honey type)
    if (inventoryFilters.searchQuery) {
      const q = inventoryFilters.searchQuery.toLowerCase()
      const nameMatch = p.name.toLowerCase().includes(q)
      const typeMatch = p.honey_type ? p.honey_type.toLowerCase().includes(q) : false
      if (!nameMatch && !typeMatch) return false
    }

    // 3. Filter by stock status
    if (p.manage_stock) {
      if (inventoryFilters.status === 'low') {
        return p.stock <= p.min_stock && p.stock > 0
      }
      if (inventoryFilters.status === 'empty') {
        return p.stock <= 0
      }
      if (inventoryFilters.status === 'ok') {
        return p.stock > p.min_stock
      }
    } else {
      if (inventoryFilters.status !== 'all') return false
    }

    return true
  })
})

const resultingStock = computed(() => {
  if (!adjustingProduct.value) return 0
  const current = Number(adjustingProduct.value.stock) || 0
  const amount = Number(adjustStockForm.amount) || 0
  if (adjustStockForm.type === 'add') {
    return current + amount
  } else if (adjustStockForm.type === 'sub') {
    return Math.max(0, current - amount)
  } else {
    return amount
  }
})

const resultingStockClass = computed(() => {
  if (!adjustingProduct.value) return 'text-gray-800 dark:text-white'
  const finalStock = resultingStock.value
  const minStock = adjustingProduct.value.min_stock || 0
  if (finalStock <= 0) {
    return 'text-rose-600 dark:text-rose-400'
  } else if (finalStock <= minStock) {
    return 'text-amber-600 dark:text-amber-400'
  } else {
    return 'text-emerald-600 dark:text-emerald-400'
  }
})

const resultingStockWarning = computed(() => {
  if (!adjustingProduct.value) return ''
  const finalStock = resultingStock.value
  const minStock = adjustingProduct.value.min_stock || 0
  
  if (adjustStockForm.type === 'sub' && adjustStockForm.amount > adjustingProduct.value.stock) {
    return t('sales.warning_insufficient_stock', { qty: adjustStockForm.amount, stock: adjustingProduct.value.stock })
  } else if (finalStock <= minStock) {
    return t('sales.warning_low_stock', { min: minStock })
  }
  return ''
})

const selectedProductRequiresBatch = computed(() => {
  if (!saleForm.product_id) return false
  const prod = products.value.find(p => p.id === saleForm.product_id)
  return prod?.requires_batch_selection ?? false
})

function formatDateTime(val) {
  if (!val) return '-'
  const d = new Date(val)
  return d.toLocaleString('de-DE', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function formatDate(val) {
  if (!val) return '-'
  const d = new Date(val)
  return d.toLocaleDateString('de-DE', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  })
}

function formatCurrency(val) {
  if (val === null || val === undefined) val = 0
  const activeCurrency = settingsStore.currency || 'EUR'
  const activeLocale = locale.value === 'de' ? 'de-DE' : 'en-US'
  return new Intl.NumberFormat(activeLocale, { style: 'currency', currency: activeCurrency }).format(val)
}

function formatChannel(val) {
  const map = {
    'direktverkauf': t('sales.channel_direct'),
    'online': t('sales.channel_online'),
    'email': t('sales.channel_email'),
    'verkaufsstand': t('sales.channel_booth')
  }
  return map[val] || val
}

function calculateVAT(total, rate) {
  if (!total || !rate) return 0
  // Gross price contains VAT: VAT = Gross * (Rate / (100 + Rate))
  return total * (rate / (100 + rate))
}

async function fetchTaxSettings() {
  try {
    const res = await axios.get('/api/sales/tax-settings')
    taxSettings.value = res.data
    // Sync into global settings store so other components can use currency/taxRates
    settingsStore.currency = res.data.currency ?? settingsStore.currency
    settingsStore.taxRates = Array.isArray(res.data.tax_rates) ? res.data.tax_rates : settingsStore.taxRates
    settingsStore.calculateTaxes = res.data.calculate_taxes ?? settingsStore.calculateTaxes
  } catch (err) {
    console.error('Fetch tax settings error:', err)
  }
}

async function fetchSales() {
  loadingSales.value = true
  try {
    const params = {}
    if (filters.startDate) {
      params.start_date = new Date(filters.startDate).toISOString()
    }
    if (filters.endDate) {
      params.end_date = new Date(filters.endDate).toISOString()
    }
    const res = await axios.get('/api/sales', { params })
    sales.value = res.data
  } catch (err) {
    console.error('Fetch sales error:', err)
    showAlert(t('sales.error_fetch'), 'error')
  } finally {
    loadingSales.value = false
  }
}

async function fetchProducts() {
  loadingProducts.value = true
  try {
    const res = await axios.get('/api/sales/products')
    products.value = res.data
  } catch (err) {
    console.error('Fetch products error:', err)
    showAlert(t('sales.error_products_fetch'), 'error')
  } finally {
    loadingProducts.value = false
  }
}

async function fetchBatches() {
  batches.value = []
  // We need apiaries list loaded to fetch batches for each
  if (apiaryStore.apiaries.length === 0) {
    await apiaryStore.fetchApiaries()
  }
  for (const apiary of apiaryStore.apiaries) {
    try {
      const response = await axios.get('/api/honey-batches', {
        params: { apiary_id: apiary.id }
      })
      batches.value.push(...response.data)
    } catch (err) {
      console.error(`Error fetching batches for apiary ${apiary.id}:`, err)
    }
  }
}

function resetFilters() {
  filters.startDate = ''
  filters.endDate = ''
  fetchSales()
}

// SALES MODAL ACTIONS
function openCreateSaleModal() {
  isEditMode.value = false
  editingId.value = null
  
  saleForm.product_id = activeProducts.value.length > 0 ? activeProducts.value[0].id : ''
  saleForm.quantity = 1
  saleForm.total_price = 0
  saleForm.sales_channel = 'direktverkauf'
  saleForm.batch_id = null
  // Format current date/time to local ISO format for datetime-local input
  const now = new Date()
  const offset = now.getTimezoneOffset() * 60000
  const localISOTime = new Date(now.getTime() - offset).toISOString().slice(0, 16)
  saleForm.sale_date = localISOTime
  saleForm.notes = ''
  saleForm.buyer = ''
  
  recalculateTotalPrice()
  showSaleModal.value = true
}

function openEditSaleModal(s) {
  isEditMode.value = true
  editingId.value = s.id
  
  saleForm.product_id = s.product_id
  saleForm.quantity = s.quantity
  saleForm.total_price = s.total_price
  saleForm.sales_channel = s.sales_channel
  saleForm.batch_id = s.batch_id
  
  // Format to local ISO format for datetime-local input
  if (s.sale_date) {
    const d = new Date(s.sale_date)
    const offset = d.getTimezoneOffset() * 60000
    saleForm.sale_date = new Date(d.getTime() - offset).toISOString().slice(0, 16)
  } else {
    saleForm.sale_date = ''
  }
  saleForm.notes = s.notes || ''
  saleForm.buyer = s.buyer || ''
  
  showSaleModal.value = true
}

function closeSaleModal() {
  showSaleModal.value = false
}

function onProductChange() {
  recalculateTotalPrice()
}

function recalculateTotalPrice() {
  const prod = products.value.find(p => p.id === saleForm.product_id)
  if (prod && saleForm.quantity) {
    saleForm.total_price = Math.round(prod.price * saleForm.quantity * 100) / 100
  } else {
    saleForm.total_price = 0
  }
}

async function submitSaleForm() {
  if (!saleForm.product_id) return

  // Client-side: enforce batch if required by product
  if (selectedProductRequiresBatch.value && !saleForm.batch_id) {
    showAlert(t('sales.error_batch_required'), 'error')
    return
  }

  try {
    const payload = {
      product_id: saleForm.product_id,
      quantity: Number(saleForm.quantity),
      total_price: Number(saleForm.total_price),
      sales_channel: saleForm.sales_channel,
      batch_id: saleForm.batch_id || null,
      sale_date: saleForm.sale_date ? new Date(saleForm.sale_date).toISOString() : null,
      notes: saleForm.notes.trim() || null,
      buyer: saleForm.buyer?.trim() || null
    }

    if (isEditMode.value) {
      await axios.put(`/api/sales/${editingId.value}`, payload)
      showAlert(t('sales.success_sale_update'), 'success')
    } else {
      await axios.post('/api/sales', payload)
      showAlert(t('sales.success_sale_create'), 'success')
    }
    
    showSaleModal.value = false
    await fetchSales()
  } catch (err) {
    console.error('Submit sale error:', err)
    showAlert(err.response?.data?.detail || t('sales.error_sale_save'), 'error')
  }
}

async function deleteSale(s) {
  const confirmed = await confirmStore.ask({
    title: t('sales.delete_sale_title'),
    message: t('sales.delete_sale_confirm'),
    type: 'danger',
    confirmText: t('sales.confirm_delete_btn')
  })
  if (!confirmed) return
  try {
    await axios.delete(`/api/sales/${s.id}`)
    showAlert(t('sales.success_sale_delete'), 'success')
    await fetchSales()
  } catch (err) {
    console.error('Delete sale error:', err)
    showAlert(err.response?.data?.detail || t('sales.error_sale_delete'), 'error')
  }
}

// PRODUCT MODAL ACTIONS
function openCreateProductModal() {
  isEditMode.value = false
  editingId.value = null

  productForm.name = ''
  productForm.honey_type = ''
  productForm.price = 0
  productForm.tax_rate = 7.0
  productForm.is_active = true
  productForm.requires_batch_selection = false
  productForm.manage_stock = false
  productForm.stock = 0
  productForm.min_stock = 0

  showProductModal.value = true
}

function openEditProductModal(p) {
  isEditMode.value = true
  editingId.value = p.id
  
  productForm.name = p.name
  productForm.honey_type = p.honey_type || ''
  productForm.price = p.price
  productForm.tax_rate = p.tax_rate
  productForm.is_active = p.is_active
  productForm.requires_batch_selection = p.requires_batch_selection ?? false
  productForm.manage_stock = p.manage_stock ?? false
  productForm.stock = p.stock ?? 0
  productForm.min_stock = p.min_stock ?? 0
  
  showProductModal.value = true
}

function closeProductModal() {
  showProductModal.value = false
}

async function submitProductForm() {
  if (!productForm.name.trim()) return
  try {
    const payload = {
      name: productForm.name.trim(),
      honey_type: productForm.honey_type.trim() || null,
      price: Number(productForm.price),
      tax_rate: taxSettings.value.calculate_taxes ? Number(productForm.tax_rate) : 0.0,
      is_active: productForm.is_active,
      requires_batch_selection: productForm.requires_batch_selection,
      manage_stock: productForm.manage_stock,
      stock: productForm.manage_stock ? Number(productForm.stock) : 0.0,
      min_stock: productForm.manage_stock ? Number(productForm.min_stock) : 0.0
    }

    if (isEditMode.value) {
      await axios.put(`/api/sales/products/${editingId.value}`, payload)
      showAlert(t('sales.success_product_update'), 'success')
    } else {
      await axios.post('/api/sales/products', payload)
      showAlert(t('sales.success_product_create'), 'success')
    }
    
    showProductModal.value = false
    await fetchProducts()
  } catch (err) {
    console.error('Submit product error:', err)
    showAlert(err.response?.data?.detail || t('sales.error_product_save'), 'error')
  }
}

async function deleteProduct(p) {
  const confirmed = await confirmStore.ask({
    title: t('sales.delete_product_title'),
    message: t('sales.delete_product_confirm', { name: p.name }),
    type: 'danger',
    confirmText: t('sales.confirm_delete_btn')
  })
  if (!confirmed) return
  try {
    await axios.delete(`/api/sales/products/${p.id}`)
    showAlert(t('sales.success_product_delete'), 'success')
    await fetchProducts()
  } catch (err) {
    console.error('Delete product error:', err)
    showAlert(err.response?.data?.detail || t('sales.error_product_delete'), 'error')
  }
}

function openAdjustStockModal(p) {
  adjustingProduct.value = p
  adjustStockForm.type = 'add'
  adjustStockForm.amount = 0
  showAdjustStockModal.value = true
}

function closeAdjustStockModal() {
  showAdjustStockModal.value = false
  adjustingProduct.value = null
}

async function submitAdjustStockForm() {
  if (!adjustingProduct.value) return
  try {
    const finalVal = resultingStock.value
    const payload = {
      stock: Number(finalVal)
    }
    await axios.put(`/api/sales/products/${adjustingProduct.value.id}`, payload)
    showAlert(t('sales.success_stock_adjust'), 'success')
    showAdjustStockModal.value = false
    await fetchProducts()
  } catch (err) {
    console.error('Adjust stock error:', err)
    showAlert(err.response?.data?.detail || t('sales.error_product_save'), 'error')
  }
}

function openStockConfigModal(p) {
  configuringProduct.value = p
  stockConfigForm.manage_stock = p.manage_stock ?? false
  stockConfigForm.stock = p.stock ?? 0
  stockConfigForm.min_stock = p.min_stock ?? 0
  showStockConfigModal.value = true
}

function closeStockConfigModal() {
  showStockConfigModal.value = false
  configuringProduct.value = null
}

async function submitStockConfigForm() {
  if (!configuringProduct.value) return
  try {
    const payload = {
      manage_stock: stockConfigForm.manage_stock,
      stock: stockConfigForm.manage_stock ? Number(stockConfigForm.stock) : 0.0,
      min_stock: stockConfigForm.manage_stock ? Number(stockConfigForm.min_stock) : 0.0
    }
    await axios.put(`/api/sales/products/${configuringProduct.value.id}`, payload)
    showAlert(t('sales.success_stock_config_update'), 'success')
    showStockConfigModal.value = false
    await fetchProducts()
  } catch (err) {
    console.error('Submit stock config error:', err)
    showAlert(err.response?.data?.detail || t('sales.error_product_save'), 'error')
  }
}

async function exportCSV() {
  try {
    let url = '/api/sales/export/csv'
    const queryParts = []
    if (filters.startDate) {
      queryParts.push(`start_date=${encodeURIComponent(new Date(filters.startDate).toISOString())}`)
    }
    if (filters.endDate) {
      queryParts.push(`end_date=${encodeURIComponent(new Date(filters.endDate).toISOString())}`)
    }
    if (queryParts.length > 0) {
      url += '?' + queryParts.join('&')
    }
    
    const response = await axios.get(url, { responseType: 'blob' })
    const blob = new Blob([response.data], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const urlBlob = URL.createObjectURL(blob)
    
    let filename = `honigverkaeufe_${new Date().toISOString().slice(0,10)}.csv`
    const disposition = response.headers['content-disposition']
    if (disposition && disposition.indexOf('attachment') !== -1) {
      const filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/
      const matches = filenameRegex.exec(disposition)
      if (matches != null && matches[1]) {
        filename = matches[1].replace(/['"]/g, '')
      }
    }
    
    link.setAttribute('href', urlBlob)
    link.setAttribute('download', filename)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } catch (err) {
    console.error('CSV export error:', err)
    showAlert(t('sales.error_export'), 'error')
  }
}

onMounted(async () => {
  await fetchTaxSettings()
  await fetchSales()
  await fetchProducts()
  await fetchBatches()
})
</script>
