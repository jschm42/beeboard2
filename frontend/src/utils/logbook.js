const EIGHTH_FIELDS = [
  'brood_eighths',
  'bee_eighths',
  'food_eighths',
  'drone_eighths',
  'drone_brood_eighths',
  'pollen_eighths',
]

const TYPE_LABEL_KEYS = {
  INSPECTION: 'logbook.type_inspection',
  VARROA_COUNT: 'logbook.type_varroa_count',
  VARROA_TREATMENT: 'logbook.type_varroa_treatment',
  GENERAL: 'logbook.type_general',
}

function dateLocale(locale) {
  return locale === 'de' ? 'de-DE' : 'en-US'
}

export function isEighthsInspection(inspectionDetail) {
  return (inspectionDetail?.boxes || []).some(box =>
    EIGHTH_FIELDS.some(field => box[field] != null && box[field] !== -1),
  )
}

export function entryTypeLabel(entry, t) {
  if (entry.entry_type === 'INSPECTION' && entry.inspection_detail) {
    return isEighthsInspection(entry.inspection_detail)
      ? t('logbook.type_inspection_eighths')
      : t('logbook.type_inspection_exact')
  }
  const key = TYPE_LABEL_KEYS[entry.entry_type]
  return key ? t(key) : entry.entry_type
}

// Log dates are plain "YYYY-MM-DD" values; parse them as local dates so they do not shift by timezone.
export function parseLogDate(value) {
  if (!value) return null
  const [year, month, day] = String(value).slice(0, 10).split('-').map(Number)
  return new Date(year, month - 1, day)
}

export function formatLogDate(value, locale, options = { day: '2-digit', month: '2-digit', year: 'numeric' }) {
  const date = parseLogDate(value)
  return date ? date.toLocaleDateString(dateLocale(locale), options) : ''
}

export function formatLogDateTime(value, locale) {
  if (!value) return ''
  return new Date(value).toLocaleString(dateLocale(locale), {
    day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit',
  })
}

export function todayIsoDate() {
  const now = new Date()
  const pad = n => String(n).padStart(2, '0')
  return `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`
}
