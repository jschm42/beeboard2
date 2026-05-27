import { defineStore } from 'pinia'
import axios from 'axios'

export const useAuthStore = defineStore('auth', {
  state: () => {
    const token = localStorage.getItem('token') || null
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
    }
    return {
      token,
      user: null,
      loading: false,
      error: null,
    }
  },
  getters: {
    isAuthenticated: (state) => !!state.token,
    isAdmin: (state) => state.user?.role === 'SYSTEM_ADMIN' || state.user?.is_superuser,
  },
  actions: {
    initAxiosHeaders() {
      if (this.token) {
        axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
      } else {
        delete axios.defaults.headers.common['Authorization']
      }
    },
    async login(username, password) {
      this.loading = true
      this.error = null
      try {
        const params = new URLSearchParams()
        params.append('username', username)
        params.append('password', password)

        const response = await axios.post('/api/auth/login', params, {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          }
        })

        this.token = response.data.access_token
        localStorage.setItem('token', this.token)
        this.initAxiosHeaders()
        
        await this.fetchMe()
        return true
      } catch (err) {
        console.error('Login error:', err)
        this.error = err.response?.data?.detail || 'Login fehlgeschlagen. Bitte überprüfe deine Anmeldedaten.'
        throw err
      } finally {
        this.loading = false
      }
    },
    async register(userData) {
      this.loading = true
      this.error = null
      try {
        await axios.post('/api/auth/register', {
          username: userData.username,
          email: userData.email,
          password: userData.password,
          first_name: userData.firstName || null,
          last_name: userData.lastName || null,
        })
        return true
      } catch (err) {
        console.error('Registration error:', err)
        this.error = err.response?.data?.detail || 'Registrierung fehlgeschlagen.'
        throw err
      } finally {
        this.loading = false
      }
    },
    async fetchMe() {
      if (!this.token) return
      this.initAxiosHeaders()
      try {
        const response = await axios.get('/api/auth/me')
        this.user = response.data
      } catch (err) {
        console.error('Fetch user profile failed:', err)
        if (err.response?.status === 401) {
          console.warn('Unauthorized token, logging out...')
          this.logout()
          // Also clear stale apiary selection so components don't fire authenticated
          // requests with an invalid apiary ID after a fresh DB creation
          localStorage.removeItem('activeApiaryId')
        }
      }
    },
    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem('token')
      this.initAxiosHeaders()
    }
  }
})
