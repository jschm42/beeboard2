import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

const SIDEBAR_COLLAPSED_KEY = 'sidebarCollapsed'
const SIDEBAR_PREFERENCE_KEY = 'sidebarPreferenceSet'
const AUTO_COLLAPSE_QUERY = '(max-width: 1023px)'

export const useSettingsStore = defineStore('settings', () => {
  const currency = ref('EUR')
  const taxRates = ref([0.0, 7.0, 19.0])
  const calculateTaxes = ref(true)

  const sidebarCollapsed = ref(false)
  const userHasSidebarPreference = ref(false)

  const sidebarExpanded = computed(() => !sidebarCollapsed.value)

  function readInitialCollapsed() {
    try {
      const hasPreference = localStorage.getItem(SIDEBAR_PREFERENCE_KEY) === '1'
      userHasSidebarPreference.value = hasPreference
      if (hasPreference) {
        return localStorage.getItem(SIDEBAR_COLLAPSED_KEY) === '1'
      }
    } catch {
      // localStorage unavailable, fall through to width check
    }
    if (typeof window !== 'undefined' && typeof window.matchMedia === 'function') {
      return window.matchMedia(AUTO_COLLAPSE_QUERY).matches
    }
    return false
  }

  function applyAutoCollapse() {
    if (typeof window === 'undefined' || typeof window.matchMedia !== 'function') return
    if (userHasSidebarPreference.value) return
    sidebarCollapsed.value = window.matchMedia(AUTO_COLLAPSE_QUERY).matches
  }

  function setSidebarCollapsed(value) {
    sidebarCollapsed.value = !!value
    userHasSidebarPreference.value = true
    try {
      localStorage.setItem(SIDEBAR_COLLAPSED_KEY, sidebarCollapsed.value ? '1' : '0')
      localStorage.setItem(SIDEBAR_PREFERENCE_KEY, '1')
    } catch {
      // Ignore storage errors (private mode, quota, etc.)
    }
  }

  function toggleSidebar() {
    setSidebarCollapsed(!sidebarCollapsed.value)
  }

  let autoCollapseUnbind = null

  function bindAutoCollapseListener() {
    if (autoCollapseUnbind) return autoCollapseUnbind
    if (typeof window === 'undefined' || typeof window.matchMedia !== 'function') return () => {}
    const mql = window.matchMedia(AUTO_COLLAPSE_QUERY)
    mql.addEventListener('change', applyAutoCollapse)
    autoCollapseUnbind = () => {
      mql.removeEventListener('change', applyAutoCollapse)
      autoCollapseUnbind = null
    }
    return autoCollapseUnbind
  }

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

  return {
    currency,
    taxRates,
    calculateTaxes,
    fetchSettings,
    sidebarCollapsed,
    sidebarExpanded,
    userHasSidebarPreference,
    readInitialCollapsed,
    setSidebarCollapsed,
    toggleSidebar,
    applyAutoCollapse,
    bindAutoCollapseListener,
  }
})
