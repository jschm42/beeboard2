const STORAGE_KEY = 'bb_custom_calendar_events_v1'

function loadEvents() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return []
    const parsed = JSON.parse(raw)
    return Array.isArray(parsed) ? parsed : []
  } catch {
    return []
  }
}

function saveEvents(events) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(events))
}

function normalizeDateString(value) {
  if (!value) return ''
  return String(value).slice(0, 10)
}

export function getCustomCalendarEvents(apiaryId) {
  if (!apiaryId) return []
  return loadEvents()
    .filter(event => event.apiary_id === apiaryId)
    .sort((a, b) => a.start_date.localeCompare(b.start_date))
}

export function upsertCustomCalendarEvent(apiaryId, input) {
  if (!apiaryId) {
    throw new Error('apiaryId is required')
  }

  const startDate = normalizeDateString(input.start_date)
  const endDate = normalizeDateString(input.end_date || input.start_date)
  if (!startDate) {
    throw new Error('start_date is required')
  }
  if (endDate < startDate) {
    throw new Error('end_date must be on or after start_date')
  }

  const allEvents = loadEvents()
  const eventId = input.id || (typeof crypto !== 'undefined' && crypto.randomUUID ? crypto.randomUUID() : `${Date.now()}-${Math.random()}`)

  const normalized = {
    id: eventId,
    apiary_id: apiaryId,
    title: (input.title || '').trim(),
    notes: (input.notes || '').trim(),
    color: input.color || '#2563eb',
    start_date: startDate,
    end_date: endDate
  }

  const idx = allEvents.findIndex(event => event.id === eventId && event.apiary_id === apiaryId)
  if (idx >= 0) {
    allEvents[idx] = normalized
  } else {
    allEvents.push(normalized)
  }
  saveEvents(allEvents)

  return normalized
}

export function deleteCustomCalendarEvent(apiaryId, eventId) {
  if (!apiaryId || !eventId) return
  const filtered = loadEvents().filter(event => !(event.apiary_id === apiaryId && event.id === eventId))
  saveEvents(filtered)
}

export function isDateInRange(day, startDate, endDate) {
  const dayStr = normalizeDateString(day)
  const start = normalizeDateString(startDate)
  const end = normalizeDateString(endDate || startDate)
  if (!dayStr || !start || !end) return false
  return dayStr >= start && dayStr <= end
}

export function classifyDueStatus(dueDate, todayStr) {
  if (!dueDate) return 'open'
  if (dueDate < todayStr) return 'overdue'
  if (dueDate === todayStr) return 'today'
  return 'upcoming'
}
