<template>
  <div class="min-h-screen bg-background flex items-center justify-center p-6">
    <div class="w-full max-w-sm">

      <!-- Header -->
      <div class="text-center mb-10">
        <p class="text-xs tracking-[0.2em] uppercase text-muted-foreground mb-1">Acceso</p>
        <h1 class="text-2xl font-medium text-foreground">Verificación</h1>
      </div>

      <!-- Progress -->
      <div class="mb-8">
        <div class="flex justify-between mb-2">
          <span class="text-xs text-muted-foreground tracking-wide">
            Pregunta {{ currentQuestion }} de {{ totalQuestions }}
          </span>
          <span class="text-xs text-muted-foreground">
            {{ Math.round((currentQuestion / totalQuestions) * 100) }}%
          </span>
        </div>
        <div class="w-full bg-border rounded-full h-px">
          <div
            class="bg-primary h-px rounded-full transition-all duration-500"
            :style="{ width: `${(currentQuestion / totalQuestions) * 100}%` }"
          ></div>
        </div>
      </div>

      <!-- Error -->
      <div v-if="errorMessage" class="mb-6 p-4 bg-muted rounded-lg border border-border">
        <p class="text-sm text-foreground/70">{{ errorMessage }}</p>
      </div>

      <!-- Form -->
      <form @submit.prevent="handleSubmit" class="space-y-6">
        <div>
          <label class="block text-sm text-muted-foreground mb-2 tracking-wide">
            {{ questionText }}
          </label>
          <input
            ref="inputRef"
            v-model="answer"
            type="text"
            class="w-full px-4 py-3 bg-background border border-border rounded-lg text-foreground
                   placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring
                   transition-colors duration-200"
            :disabled="loading"
            required
          />
        </div>

        <button
          type="submit"
          :disabled="loading"
          class="w-full px-8 py-3 bg-primary text-primary-foreground rounded-full text-sm font-semibold
                 tracking-wide transition-all duration-300 hover:bg-primary/90 hover:-translate-y-0.5
                 active:scale-95 disabled:opacity-40 disabled:cursor-not-allowed disabled:translate-y-0"
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
        currentQuestion.value = response.next_question
        questionText.value = response.question_text
        answer.value = ''
        loading.value = false
        await nextTick()
        inputRef.value?.focus()
      } else {
        sessionStore.setAuthenticated(true)
        router.push({ name: 'generator' })
      }
    } else {
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
