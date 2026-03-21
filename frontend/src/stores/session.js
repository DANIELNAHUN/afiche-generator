import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

const SESSION_KEY = 'app_session'
const FORM_KEY = 'app_form_data'
const RESULTS_KEY = 'app_results'
const SESSION_DURATION_MS = 5 * 60 * 1000 // 5 minutos

function saveToStorage(sessionId) {
  const data = {
    sessionId,
    expiresAt: Date.now() + SESSION_DURATION_MS
  }
  localStorage.setItem(SESSION_KEY, JSON.stringify(data))
}

function loadFromStorage() {
  try {
    const raw = localStorage.getItem(SESSION_KEY)
    if (!raw) return null
    const data = JSON.parse(raw)
    if (Date.now() > data.expiresAt) {
      localStorage.removeItem(SESSION_KEY)
      localStorage.removeItem(FORM_KEY)
      localStorage.removeItem(RESULTS_KEY)
      return null
    }
    return data
  } catch {
    localStorage.removeItem(SESSION_KEY)
    localStorage.removeItem(FORM_KEY)
    localStorage.removeItem(RESULTS_KEY)
    return null
  }
}

function clearStorage() {
  localStorage.removeItem(SESSION_KEY)
  localStorage.removeItem(FORM_KEY)
  localStorage.removeItem(RESULTS_KEY)
}

export function saveFormData(formData, timeComponents, rawDate = '') {
  localStorage.setItem(FORM_KEY, JSON.stringify({ formData, timeComponents, rawDate }))
}

export function loadFormData() {
  try {
    const raw = localStorage.getItem(FORM_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

export function saveResults(documents, audioFiles, selectedPreviewType) {
  localStorage.setItem(RESULTS_KEY, JSON.stringify({ documents, audioFiles, selectedPreviewType }))
}

export function loadResults() {
  try {
    const raw = localStorage.getItem(RESULTS_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

export const useSessionStore = defineStore('session', () => {
  const stored = loadFromStorage()

  const sessionId = ref(stored?.sessionId ?? null)
  const authenticated = ref(stored !== null)

  const isAuthenticated = computed(() => {
    if (!authenticated.value || !sessionId.value) return false
    const data = loadFromStorage()
    if (!data) {
      sessionId.value = null
      authenticated.value = false
      return false
    }
    return true
  })

  function setSession(id) {
    sessionId.value = id
  }

  function setAuthenticated(value) {
    authenticated.value = value
    if (value && sessionId.value) {
      saveToStorage(sessionId.value)
    } else if (!value) {
      clearStorage()
    }
  }

  function clearSession() {
    sessionId.value = null
    authenticated.value = false
    clearStorage()
  }

  return {
    sessionId,
    authenticated,
    isAuthenticated,
    setSession,
    setAuthenticated,
    clearSession
  }
})
