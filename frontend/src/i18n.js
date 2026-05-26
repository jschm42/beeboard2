import { createI18n } from 'vue-i18n'
import de from './locales/de.json'
import en from './locales/en.json'

const savedLocale = localStorage.getItem('locale') || 'de'

const i18n = createI18n({
  legacy: false,
  locale: savedLocale,
  fallbackLocale: 'de',
  messages: { de, en },
})

export default i18n
