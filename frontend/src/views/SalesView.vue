<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 font-sans">
    
    <!-- Back to Dashboard Link -->
    <router-link to="/dashboard" class="inline-flex items-center text-sm font-semibold text-primary hover:text-primary-hover mb-4 transition-colors duration-200">
      <svg class="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"/></svg>
      Zurück zum Dashboard
    </router-link>

    <!-- Header Area -->
    <div class="mb-8 flex flex-col md:flex-row md:justify-between md:items-center space-y-4 md:space-y-0">
      <div>
        <h1 class="text-3xl font-extrabold text-gray-900 dark:text-white tracking-tight">💰 Verkäufe & Umsatz</h1>
        <p class="text-gray-500 dark:text-gray-400 mt-1">Erfasse deine Honigverkäufe, verwalte Produkte und exportiere Daten für die Steuererklärung.</p>
      </div>
      
      <div class="flex items-center space-x-3" v-if="activeTab === 'sales'">
        <button 
          @click="exportCSV" 
          :disabled="sales.length === 0"
          class="px-4 py-2.5 bg-gray-100 hover:bg-gray-200 dark:bg-dark-card dark:hover:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-200 font-extrabold text-sm rounded-xl transition-all duration-200 hover-scale flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
          <span>Steuerexport (CSV)</span>
        </button>
        <button 
          @click="openCreateSaleModal" 
          class="px-5 py-2.5 bg-primary hover:bg-primary-hover text-white font-extrabold text-sm rounded-xl shadow-md shadow-primary/20 hover-scale flex items-center justify-center space-x-2"
        >
          <span>+ Verkauf buchen</span>
        </button>
      </div>
      
      <div v-else-if="activeTab === 'products'">
        <button 
          @click="openCreateProductModal" 
          class="px-5 py-2.5 bg-primary hover:bg-primary-hover text-white font-extrabold text-sm rounded-xl shadow-md shadow-primary/20 hover-scale flex items-center justify-center space-x-2"
        >
          <span>+ Neues Produkt</span>
        </button>
      </div>
    </div>

    <!-- Alert Message -->
    <div v-if="alertMessage" class="mb-6 p-4 rounded-xl text-sm flex items-start space-x-2" :class="alertClass">
      <svg class="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
      <span>{{ alertMessage }}</span>
    </div>

    <!-- Kleinunternehmer Info Alert -->
    <div v-if="taxSettings.kleinunternehmer_regelung" class="mb-6 p-4 bg-amber-500/10 border border-amber-500/20 text-amber-800 dark:text-amber-300 rounded-2xl text-xs flex items-center space-x-2">
      <span class="text-base">💼</span>
      <span><strong>Kleinunternehmer-Regelung (§ 19 UStG) ist aktiv:</strong> In Rechnungen und Steuerexporten wird keine Umsatzsteuer ausgewiesen oder berechnet. Die Steuersätze deiner Produkte werden im Buchungs- und Steuersystem ignoriert.</span>
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
        📊 Verkäufe
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
        🍯 Produkte & Preise
      </button>
    </div>

    <!-- TAB 1: SALES LEDGER -->
    <div v-if="activeTab === 'sales'" class="space-y-6">
      
      <!-- Date Filters Card -->
      <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl p-6 shadow-sm flex flex-col md:flex-row gap-4 items-end animate-scale">
        <div class="flex-1 w-full">
          <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">Startdatum</label>
          <input 
            v-model="filters.startDate" 
            type="date" 
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl text-sm font-mono focus:outline-none focus:ring-2 focus:ring-primary"
            @change="fetchSales"
          />
        </div>
        <div class="flex-1 w-full">
          <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">Enddatum</label>
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
          Zurücksetzen
        </button>
      </div>

      <!-- Ledger Table -->
      <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl overflow-hidden shadow-sm">
        <div v-if="loadingSales" class="flex flex-col items-center justify-center py-20">
          <svg class="animate-spin h-8 w-8 text-primary mb-3" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
          <span class="text-xs text-gray-400 font-bold">Lade Verkaufstransaktionen...</span>
        </div>

        <div v-else-if="sales.length === 0" class="flex flex-col items-center justify-center py-20 text-center px-4">
          <span class="text-4xl mb-3">💸</span>
          <h3 class="text-base font-bold text-gray-900 dark:text-white">Keine Verkäufe erfasst</h3>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1 max-w-sm">Bisher wurden im ausgewählten Zeitraum keine Verkäufe eingetragen. Klicke auf "+ Verkauf buchen" um zu starten.</p>
        </div>

        <div v-else class="overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="bg-gray-50 dark:bg-dark-bg text-gray-500 dark:text-gray-400 text-[10px] font-bold uppercase tracking-wider border-b border-gray-100 dark:border-dark-border">
                <th class="px-6 py-4">Datum</th>
                <th class="px-6 py-4">Produkt</th>
                <th class="px-6 py-4 text-center">Menge</th>
                <th class="px-6 py-4 text-right">Gesamtpreis</th>
                <th class="px-6 py-4 text-center">USt. / MwSt.</th>
                <th class="px-6 py-4">Kanal</th>
                <th class="px-6 py-4">Charge</th>
                <th class="px-6 py-4">Notizen</th>
                <th class="px-6 py-4 text-right">Aktionen</th>
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
                  {{ s.product?.name || 'Gelöschtes Produkt' }}
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
                  <span v-if="taxSettings.kleinunternehmer_regelung" class="text-xs text-gray-400">
                    0% (§ 19)
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

                <!-- Notes -->
                <td class="px-6 py-4 text-gray-500 dark:text-gray-400 max-w-[200px] truncate" :title="s.notes">
                  {{ s.notes || '-' }}
                </td>

                <!-- Actions -->
                <td class="px-6 py-4 text-right space-x-2">
                  <button 
                    @click="openEditSaleModal(s)" 
                    class="p-1.5 text-gray-500 hover:text-primary hover:bg-gray-100 dark:hover:bg-dark-border rounded-lg transition-all duration-150 inline-flex hover-scale"
                    title="Bearbeiten"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/></svg>
                  </button>
                  <button 
                    @click="deleteSale(s)" 
                    class="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-500/10 rounded-lg transition-all duration-150 inline-flex hover-scale"
                    title="Löschen"
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
          <span class="text-xs text-gray-400 font-bold">Lade Produktkonfigurationen...</span>
        </div>

        <div v-else-if="products.length === 0" class="flex flex-col items-center justify-center py-20 text-center px-4">
          <span class="text-4xl mb-3">🍯</span>
          <h3 class="text-base font-bold text-gray-900 dark:text-white">Keine Produkte eingerichtet</h3>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1 max-w-sm">Richte zuerst Produkte wie "Blütenhonig 500g" ein, um dafür Verkäufe verbuchen zu können.</p>
        </div>

        <div v-else class="overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="bg-gray-50 dark:bg-dark-bg text-gray-500 dark:text-gray-400 text-[10px] font-bold uppercase tracking-wider border-b border-gray-100 dark:border-dark-border">
                <th class="px-6 py-4">Bezeichnung</th>
                <th class="px-6 py-4">Honigsorte</th>
                <th class="px-6 py-4 text-right">Standardpreis</th>
                <th class="px-6 py-4 text-center">Steuersatz</th>
                <th class="px-6 py-4 text-center">Status</th>
                <th class="px-6 py-4 text-right">Aktionen</th>
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
                  <span v-if="taxSettings.kleinunternehmer_regelung" class="text-xs text-gray-400 italic">
                    0% (§ 19)
                  </span>
                  <span v-else class="text-xs text-gray-600 dark:text-gray-300">
                    {{ p.tax_rate }}%
                  </span>
                </td>

                <!-- Status -->
                <td class="px-6 py-4 text-center">
                  <span 
                    class="px-2 py-0.5 rounded-full text-[10px] font-bold"
                    :class="p.is_active ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400' : 'bg-rose-500/10 text-rose-600 dark:text-rose-400'"
                  >
                    {{ p.is_active ? 'Aktiv' : 'Inaktiv' }}
                  </span>
                </td>

                <!-- Actions -->
                <td class="px-6 py-4 text-right space-x-2">
                  <button 
                    @click="openEditProductModal(p)" 
                    class="p-1.5 text-gray-500 hover:text-primary hover:bg-gray-100 dark:hover:bg-dark-border rounded-lg transition-all duration-150 inline-flex hover-scale"
                    title="Bearbeiten"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/></svg>
                  </button>
                  <button 
                    @click="deleteProduct(p)" 
                    class="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-500/10 rounded-lg transition-all duration-150 inline-flex hover-scale"
                    title="Löschen"
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

    <!-- SALES MODAL -->
    <div v-if="showSaleModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div class="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-3xl shadow-xl w-full max-w-xl p-6 animate-scale">
        <div class="flex justify-between items-center mb-6 pb-4 border-b border-gray-100 dark:border-dark-border">
          <h3 class="text-xl font-bold text-gray-900 dark:text-white">
            {{ isEditMode ? '📝 Verkauf bearbeiten' : '💸 Verkauf erfassen' }}
          </h3>
          <button @click="closeSaleModal" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>

        <form @submit.prevent="submitSaleForm">
          <div class="space-y-4">
            <!-- Product Select -->
            <div>
              <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">Produkt *</label>
              <select 
                v-model="saleForm.product_id" 
                required
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm"
                @change="onProductChange"
              >
                <option value="" disabled>Bitte Produkt auswählen...</option>
                <option v-for="p in activeProducts" :key="p.id" :value="p.id">
                  {{ p.name }} ({{ formatCurrency(p.price) }})
                </option>
              </select>
              <p v-if="activeProducts.length === 0" class="text-[11px] text-red-500 font-bold mt-1">
                ⚠️ Du hast noch keine aktiven Produkte eingerichtet. Bitte im Tab "Produkte & Preise" anlegen!
              </p>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <!-- Quantity -->
              <div>
                <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">Menge *</label>
                <input 
                  v-model.number="saleForm.quantity" 
                  type="number" 
                  min="1"
                  required
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm font-mono"
                  @input="recalculateTotalPrice"
                />
              </div>

              <!-- Total Price -->
              <div>
                <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">Gesamtpreis (€) *</label>
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
              <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">Verkaufskanal *</label>
              <select 
                v-model="saleForm.sales_channel" 
                required
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm"
              >
                <option value="direktverkauf">Direktverkauf</option>
                <option value="online">Online</option>
                <option value="email">E-Mail</option>
                <option value="verkaufsstand">Verkaufsstand</option>
              </select>
            </div>

            <!-- Honey Batch (optional) -->
            <div>
              <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">Honig-Charge (Optional)</label>
              <select 
                v-model="saleForm.batch_id" 
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm font-mono"
              >
                <option :value="null">Keine Verknüpfung</option>
                <option v-for="b in batches" :key="b.id" :value="b.id">
                  {{ b.batch_number || `MHD: ${formatDate(b.best_before_date)}` }} - {{ b.honey_type }} ({{ b.quantity_kg }} kg)
                </option>
              </select>
            </div>

            <!-- Sale Date -->
            <div>
              <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">Verkaufsdatum *</label>
              <input 
                v-model="saleForm.sale_date" 
                type="datetime-local" 
                required
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm font-mono"
              />
            </div>

            <!-- Notes -->
            <div>
              <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">Notizen</label>
              <textarea 
                v-model="saleForm.notes" 
                rows="2"
                placeholder="Optionale Notizen zum Verkauf..."
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
              Abbrechen
            </button>
            <button 
              type="submit" 
              class="px-5 py-2 bg-primary hover:bg-primary-hover text-white text-xs font-bold rounded-xl shadow-md hover-scale"
            >
              Speichern
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
            {{ isEditMode ? '📝 Produkt bearbeiten' : '🍯 Neues Produkt anlegen' }}
          </h3>
          <button @click="closeProductModal" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>

        <form @submit.prevent="submitProductForm">
          <div class="space-y-4">
            <!-- Name -->
            <div>
              <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">Bezeichnung *</label>
              <input 
                v-model="productForm.name" 
                type="text" 
                required
                placeholder="z.B. Sommertracht 500g D.I.B."
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm"
              />
            </div>

            <!-- Honey Type -->
            <div>
              <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">Honigsorte (Optional)</label>
              <input 
                v-model="productForm.honey_type" 
                type="text" 
                placeholder="z.B. Blütenhonig"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm"
              />
            </div>

            <!-- Price -->
            <div>
              <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">Standardpreis (€) *</label>
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
            <div v-if="!taxSettings.kleinunternehmer_regelung">
              <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">Steuersatz *</label>
              <select 
                v-model.number="productForm.tax_rate" 
                required
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 dark:bg-dark-bg dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm font-mono"
              >
                <option :value="7.0">7.0 % (Honig)</option>
                <option :value="19.0">19.0 % (z.B. Met / Kerzen)</option>
                <option :value="0.0">0.0 % (Steuerfrei)</option>
              </select>
            </div>
            <div v-else class="p-3 bg-gray-50 dark:bg-dark-bg border border-gray-100 dark:border-dark-border rounded-xl">
              <span class="text-xs text-gray-500 dark:text-gray-400 font-bold block mb-1">Steuersatz:</span>
              <span class="text-xs text-gray-600 dark:text-gray-300">0.0 % (Kleinunternehmer-Regelung § 19 UStG)</span>
            </div>

            <!-- Is Active -->
            <div class="flex items-center pt-2">
              <label class="flex items-center space-x-2 cursor-pointer">
                <input 
                  v-model="productForm.is_active" 
                  type="checkbox" 
                  class="rounded text-primary focus:ring-primary h-4 w-4"
                />
                <span class="text-xs font-bold text-gray-700 dark:text-gray-300">Produkt aktiv</span>
              </label>
            </div>
          </div>

          <div class="flex justify-end space-x-3 pt-6 border-t border-gray-100 dark:border-dark-border mt-6">
            <button 
              type="button" 
              @click="closeProductModal" 
              class="px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-xl text-xs font-semibold hover:bg-gray-100 dark:hover:bg-dark-border text-gray-700 dark:text-gray-300"
            >
              Abbrechen
            </button>
            <button 
              type="submit" 
              class="px-5 py-2 bg-primary hover:bg-primary-hover text-white text-xs font-bold rounded-xl shadow-md hover-scale"
            >
              Speichern
            </button>
          </div>
        </form>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive, watch } from 'vue'
import axios from 'axios'
import { useApiaryStore } from '../stores/apiary'

const apiaryStore = useApiaryStore()

const activeTab = ref('sales')
const sales = ref([])
const products = ref([])
const batches = ref([])
const taxSettings = ref({ kleinunternehmer_regelung: false })

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
  notes: ''
})

const productForm = reactive({
  name: '',
  honey_type: '',
  price: 0,
  tax_rate: 7.0,
  is_active: true
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
  if (val === null || val === undefined) return '0,00 €'
  return new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(val)
}

function formatChannel(val) {
  const map = {
    'direktverkauf': 'Direktverkauf',
    'online': 'Online',
    'email': 'E-Mail',
    'verkaufsstand': 'Verkaufsstand'
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
    showAlert('Fehler beim Laden der Verkaufstransaktionen.', 'error')
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
    showAlert('Fehler beim Laden der Produkte.', 'error')
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
  try {
    const payload = {
      product_id: saleForm.product_id,
      quantity: Number(saleForm.quantity),
      total_price: Number(saleForm.total_price),
      sales_channel: saleForm.sales_channel,
      batch_id: saleForm.batch_id || null,
      sale_date: saleForm.sale_date ? new Date(saleForm.sale_date).toISOString() : null,
      notes: saleForm.notes.trim() || null
    }

    if (isEditMode.value) {
      await axios.put(`/api/sales/${editingId.value}`, payload)
      showAlert('Verkaufstransaktion erfolgreich aktualisiert!', 'success')
    } else {
      await axios.post('/api/sales', payload)
      showAlert('Verkaufstransaktion erfolgreich erfasst!', 'success')
    }
    
    showSaleModal.value = false
    await fetchSales()
  } catch (err) {
    console.error('Submit sale error:', err)
    showAlert(err.response?.data?.detail || 'Fehler beim Speichern der Transaktion.', 'error')
  }
}

async function deleteSale(s) {
  if (!confirm('Möchtest du diese Verkaufstransaktion wirklich löschen?')) return
  try {
    await axios.delete(`/api/sales/${s.id}`)
    showAlert('Verkaufstransaktion erfolgreich gelöscht.', 'success')
    await fetchSales()
  } catch (err) {
    console.error('Delete sale error:', err)
    showAlert(err.response?.data?.detail || 'Fehler beim Löschen der Transaktion.', 'error')
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
      tax_rate: taxSettings.value.kleinunternehmer_regelung ? 0.0 : Number(productForm.tax_rate),
      is_active: productForm.is_active
    }

    if (isEditMode.value) {
      await axios.put(`/api/sales/products/${editingId.value}`, payload)
      showAlert('Produktkonfiguration erfolgreich aktualisiert!', 'success')
    } else {
      await axios.post('/api/sales/products', payload)
      showAlert('Produktkonfiguration erfolgreich erstellt!', 'success')
    }
    
    showProductModal.value = false
    await fetchProducts()
  } catch (err) {
    console.error('Submit product error:', err)
    showAlert(err.response?.data?.detail || 'Fehler beim Speichern des Produkts.', 'error')
  }
}

async function deleteProduct(p) {
  if (!confirm(`Möchtest du das Produkt "${p.name}" wirklich löschen?`)) return
  try {
    await axios.delete(`/api/sales/products/${p.id}`)
    showAlert('Produktkonfiguration erfolgreich gelöscht.', 'success')
    await fetchProducts()
  } catch (err) {
    console.error('Delete product error:', err)
    showAlert(err.response?.data?.detail || 'Fehler beim Löschen des Produkts.', 'error')
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
    showAlert('Fehler beim Exportieren des Honigbuchs.', 'error')
  }
}

onMounted(async () => {
  await fetchTaxSettings()
  await fetchSales()
  await fetchProducts()
  await fetchBatches()
})
</script>
