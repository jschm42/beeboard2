import { defineStore } from 'pinia'
import axios from 'axios'

export const useApiaryStore = defineStore('apiary', {
  state: () => ({
    apiaries: [], // List of memberships/apiaries
    activeApiaryId: localStorage.getItem('activeApiaryId') || null,
    loading: false,
    error: null
  }),
  getters: {
    activeApiary: (state) => {
      if (!state.activeApiaryId) return null
      return state.apiaries.find(a => a.id === state.activeApiaryId) || null
    },
    hasApiaries: (state) => state.apiaries.length > 0
  },
  actions: {
    initApiaryHeader() {
      if (this.activeApiaryId) {
        axios.defaults.headers.common['X-Apiary-ID'] = this.activeApiaryId
      } else {
        delete axios.defaults.headers.common['X-Apiary-ID']
      }
    },
    async fetchApiaries() {
      this.loading = true
      this.error = null
      try {
        const response = await axios.get('/api/apiaries')
        this.apiaries = response.data
        
        // If there's no active apiary selected, default to the first one available
        if (this.apiaries.length > 0 && !this.activeApiaryId) {
          this.selectApiary(this.apiaries[0].id)
        } else if (this.apiaries.length === 0) {
          this.activeApiaryId = null
          localStorage.removeItem('activeApiaryId')
          this.initApiaryHeader()
        } else {
          // Re-validate and select current active apiary
          this.initApiaryHeader()
        }
      } catch (err) {
        console.error('Fetch apiaries error:', err)
        this.error = err.response?.data?.detail || 'Fehler beim Laden der Imkereien.'
      } finally {
        this.loading = false
      }
    },
    selectApiary(apiaryId) {
      this.activeApiaryId = apiaryId
      localStorage.setItem('activeApiaryId', apiaryId)
      this.initApiaryHeader()
    },
    async createApiary(name, notes = '') {
      this.loading = true
      this.error = null
      try {
        const response = await axios.post('/api/apiaries', { name, notes })
        await this.fetchApiaries()
        // Select the newly created apiary
        if (response.data?.id) {
          this.selectApiary(response.data.id)
        }
        return response.data
      } catch (err) {
        console.error('Create apiary error:', err)
        this.error = err.response?.data?.detail || 'Fehler beim Erstellen der Imkerei.'
        throw err
      } finally {
        this.loading = false
      }
    },
    async addMember(usernameOrEmail, role = 'USER') {
      if (!this.activeApiaryId) throw new Error('Keine aktive Imkerei ausgewählt.')
      this.loading = true
      this.error = null
      try {
        const response = await axios.post(`/api/apiaries/${this.activeApiaryId}/members`, {
          username_or_email: usernameOrEmail,
          role: role
        })
        await this.fetchApiaries()
        return response.data
      } catch (err) {
        console.error('Add member error:', err)
        this.error = err.response?.data?.detail || 'Fehler beim Hinzufügen des Mitglieds.'
        throw err
      } finally {
        this.loading = false
      }
    }
  }
})
