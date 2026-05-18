import { defineStore } from 'pinia'

export const useErrorStore = defineStore('error', {
  state: () => ({
    show: false,
    title: 'Fehler aufgetreten',
    message: '',
    details: null
  }),
  actions: {
    showError(message, details = null, title = 'Fehler') {
      this.title = title
      this.message = message
      
      if (details) {
        if (typeof details === 'object') {
          if (details.response) {
            // It's an Axios response error
            this.details = {
              status: details.response.status,
              statusText: details.response.statusText,
              detail: details.response.data?.detail || 'Keine Detailbeschreibung vom Server.',
              method: details.config?.method?.toUpperCase() || 'UNKNOWN',
              url: details.config?.url || 'UNKNOWN'
            }
          } else if (details.request) {
            // Request was made but no response received
            this.details = {
              status: 'Keine Antwort',
              statusText: 'Der Server antwortet nicht. Bitte prüfen Sie Ihre Verbindung.',
              detail: 'Netzwerkfehler oder Server offline.',
              method: details.config?.method?.toUpperCase() || 'UNKNOWN',
              url: details.config?.url || 'UNKNOWN'
            }
          } else {
            // Standard Error object or other object
            this.details = {
              detail: details.message || JSON.stringify(details)
            }
          }
        } else {
          this.details = {
            detail: String(details)
          }
        }
      } else {
        this.details = null
      }
      
      this.show = true
    },
    clearError() {
      this.show = false
      this.title = 'Fehler aufgetreten'
      this.message = ''
      this.details = null
    }
  }
})
