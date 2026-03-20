import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

const SESSION_KEY = 'app_session'
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
      return null
    }
    return data
  } catch {
    localStorage.removeItem(SESSION_KEY)
    return null
  }
}

function clearStorage() {
  localStorage.removeItem(SESSION_KEY)
}

export const useSessionStore = defineStore('session', () => {
  // Intentar restaurar sesión persistida al inicializar
  const stored = loadFromStorage()

  const sessionId = ref(stored?.sessionId ?? null)
  const authenticated = ref(stored !== null)

  const isAuthenticated = computed(() => {
    if (!authenticated.value || !sessionId.value) return false
    // Verificar que la sesión en localStorage no haya expirado
    const data = loadFromStorage()
    if (!data) {
      // Expiró mientras la app estaba abierta
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
