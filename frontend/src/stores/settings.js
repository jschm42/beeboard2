import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

export const useSettingsStore = defineStore('settings', () => {
  const currency = ref('EUR')
  const taxRates = ref([0.0, 7.0, 19.0])
  const calculateTaxes = ref(true)

  async function fetchSettings() {
    try {
      const res = await axios.get('/api/sales/tax-settings')
      currency.value = res.data.currency ?? 'EUR'
      taxRates.value = Array.isArray(res.data.tax_rates) ? res.data.tax_rates : [0.0, 7.0, 19.0]
      calculateTaxes.value = res.data.calculate_taxes ?? true
    } catch (err) {
      console.error('Failed to load settings:', err)
    }
  }

  return { currency, taxRates, calculateTaxes, fetchSettings }
})
