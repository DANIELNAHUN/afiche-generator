<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 flex items-center justify-center p-4">
    <div class="max-w-md w-full bg-white rounded-2xl shadow-xl p-8">
      <h2 class="text-2xl font-bold text-gray-800 mb-6 text-center">
        Verificación de Seguridad
      </h2>
      
      <!-- Progress indicator -->
      <div class="mb-6">
        <div class="flex justify-between mb-2">
          <span class="text-sm text-gray-600">Pregunta {{ currentQuestion }} de {{ totalQuestions }}</span>
        </div>
        <div class="w-full bg-gray-200 rounded-full h-2">
          <div 
            class="bg-blue-600 h-2 rounded-full transition-all duration-300"
            :style="{ width: `${(currentQuestion / totalQuestions) * 100}%` }"
          ></div>
        </div>
      </div>
      
      <!-- Error message -->
      <div v-if="errorMessage" class="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
        <p class="text-red-700 text-sm">{{ errorMessage }}</p>
      </div>
      
      <!-- Question form -->
      <form @submit.prevent="handleSubmit">
        <div class="mb-6">
          <label class="block text-gray-700 font-medium mb-2">
            {{ questionText }}
          </label>
          <input
            ref="inputRef"
            v-model="answer"
            type="text"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 
                   focus:ring-blue-500 focus:border-transparent"
            :disabled="loading"
            required
          />
        </div>
        
        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 rounded-lg 
                 transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {{ loading ? 'Validando...' : 'Continuar' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useSessionStore } from '../stores/session'
import api from '../services/api'

const router = useRouter()
const sessionStore = useSessionStore()

const currentQuestion = ref(1)
const totalQuestions = ref(3)
const questionText = ref('')
const answer = ref('')
const loading = ref(false)
const errorMessage = ref('')
const inputRef = ref(null)

onMounted(async () => {
  try {
    const response = await api.startSession()
    sessionStore.setSession(response.session_id)
    currentQuestion.value = response.question_number
    totalQuestions.value = response.total_questions
    questionText.value = response.question_text
    await nextTick()
    inputRef.value?.focus()
  } catch (error) {
    errorMessage.value = 'Error al iniciar sesión. Por favor, intenta de nuevo.'
  }
})

const handleSubmit = async () => {
  loading.value = true
  errorMessage.value = ''
  
  try {
    const response = await api.validateAnswer(
      sessionStore.sessionId,
      currentQuestion.value,
      answer.value
    )
    
    if (response.success) {
      if (response.next_question) {
        // Avanzar a siguiente pregunta
        currentQuestion.value = response.next_question
        questionText.value = response.question_text
        answer.value = ''
        loading.value = false
        await nextTick()
        inputRef.value?.focus()
      } else {
        // Autenticación completa
        sessionStore.setAuthenticated(true)
        router.push({ name: 'generator' })
      }
    } else {
      // Respuesta incorrecta - reiniciar
      errorMessage.value = response.message
      currentQuestion.value = response.next_question
      questionText.value = response.question_text
      answer.value = ''
      loading.value = false
      await nextTick()
      inputRef.value?.focus()
    }
  } catch (error) {
    errorMessage.value = error.message || 'Error al validar respuesta. Por favor, intenta de nuevo.'
    loading.value = false
  }
}
</script>
