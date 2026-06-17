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
    end_date: endDate,
    is_recurring: !!input.is_recurring,
    recurrence_interval_type: input.recurrence_interval_type || 'WEEKLY',
    recurrence_interval_value: parseInt(input.recurrence_interval_value) || 1,
    recurrence_weekdays: input.recurrence_weekdays !== undefined ? String(input.recurrence_weekdays) : '',
    recurrence_end_date: input.recurrence_end_date ? normalizeDateString(input.recurrence_end_date) : '',
    is_all_day: input.is_all_day !== false,
    start_time: input.start_time || '',
    end_time: input.end_time || ''
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

export function getOccurrences(item, rangeStartStr, rangeEndStr) {
  const occurrences = []
  const startStr = item.start_date || item.due_date
  if (!startStr) return occurrences

  const isRecurring = item.is_recurring
  if (!isRecurring) {
    if (startStr >= rangeStartStr && startStr <= rangeEndStr) {
      occurrences.push(startStr)
    }
    return occurrences
  }

  const intervalType = (item.recurrence_interval_type || 'WEEKLY').toUpperCase()
  const intervalVal = parseInt(item.recurrence_interval_value) || 1
  const endStr = item.recurrence_end_date || ''
  
  let activeDays = []
  if (item.recurrence_weekdays) {
    activeDays = String(item.recurrence_weekdays)
      .split(',')
      .map(d => parseInt(d.trim()))
      .filter(d => !isNaN(d))
  }

  const startDate = new Date(`${startStr}T00:00:00`)
  const limitDate = new Date(`${rangeEndStr}T00:00:00`)
  const maxEndDate = endStr ? new Date(`${endStr}T00:00:00`) : null
  
  const capDate = new Date(startDate.getTime())
  capDate.setFullYear(capDate.getFullYear() + 2)
  const actualLimit = maxEndDate && maxEndDate < capDate ? maxEndDate : capDate

  let current = new Date(startDate.getTime())

  if (intervalType === 'DAILY') {
    while (current <= actualLimit && current <= limitDate) {
      const curStr = current.toISOString().split('T')[0]
      if (curStr >= rangeStartStr) {
        occurrences.push(curStr)
      }
      current.setDate(current.getDate() + intervalVal)
    }
  }
  else if (intervalType === 'WEEKLY') {
    if (activeDays.length > 0) {
      const startWeekTime = getStartOfWeek(startDate).getTime()
      while (current <= actualLimit && current <= limitDate) {
        const currentWeekTime = getStartOfWeek(current).getTime()
        const weekDiff = Math.round((currentWeekTime - startWeekTime) / (7 * 24 * 60 * 60 * 1000))
        
        if (weekDiff % intervalVal === 0) {
          const jsDay = current.getDay()
          const isoDay = jsDay === 0 ? 6 : jsDay - 1
          if (activeDays.includes(isoDay)) {
            const curStr = current.toISOString().split('T')[0]
            if (curStr >= startStr && curStr >= rangeStartStr) {
              occurrences.push(curStr)
            }
          }
        }
        current.setDate(current.getDate() + 1)
      }
    } else {
      while (current <= actualLimit && current <= limitDate) {
        const curStr = current.toISOString().split('T')[0]
        if (curStr >= rangeStartStr) {
          occurrences.push(curStr)
        }
        current.setDate(current.getDate() + (7 * intervalVal))
      }
    }
  }
  else if (intervalType === 'MONTHLY') {
    while (current <= actualLimit && current <= limitDate) {
      const curStr = current.toISOString().split('T')[0]
      if (curStr >= rangeStartStr) {
        occurrences.push(curStr)
      }
      current.setMonth(current.getMonth() + intervalVal)
    }
  }
  else if (intervalType === 'YEARLY') {
    while (current <= actualLimit && current <= limitDate) {
      const curStr = current.toISOString().split('T')[0]
      if (curStr >= rangeStartStr) {
        occurrences.push(curStr)
      }
      current.setFullYear(current.getFullYear() + intervalVal)
    }
  }

  return occurrences
}

function getStartOfWeek(d) {
  const date = new Date(d.getTime())
  const day = date.getDay()
  const diff = date.getDate() - day + (day === 0 ? -6 : 1)
  date.setDate(diff)
  date.setHours(0, 0, 0, 0)
  return date
}
