import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useSessionStore = defineStore('session', () => {
  const sessionId = ref(null)
  const authenticated = ref(false)
  
  const isAuthenticated = computed(() => authenticated.value && sessionId.value !== null)
  
  function setSession(id) {
    sessionId.value = id
  }
  
  function setAuthenticated(value) {
    authenticated.value = value
  }
  
  function clearSession() {
    sessionId.value = null
    authenticated.value = false
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
