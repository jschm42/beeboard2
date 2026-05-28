import { createApp } from 'vue'
import { createPinia } from 'pinia'
import VCalendar from 'v-calendar'
import router from './router'
import App from './App.vue'
import i18n from './i18n'
import './style.css'
import 'v-calendar/style.css'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(i18n)
app.use(VCalendar, {})

app.mount('#app')
