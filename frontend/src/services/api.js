import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Response interceptor for error handling
apiClient.interceptors.response.use(
  response => response,
  error => {
    if (error.response) {
      // El servidor respondió con un código de error
      const status = error.response.status
      const message = error.response.data.detail || 'Error desconocido'
      
      switch (status) {
        case 400:
          throw new Error(`Datos inválidos: ${message}`)
        case 401:
          throw new Error(`No autorizado: ${message}`)
        case 404:
          throw new Error(`No encontrado: ${message}`)
        case 500:
          throw new Error(`Error del servidor: ${message}`)
        default:
          throw new Error(`Error: ${message}`)
      }
    } else if (error.request) {
      // La petición se hizo pero no hubo respuesta
      throw new Error('No se pudo conectar con el servidor')
    } else {
      // Algo pasó al configurar la petición
      throw new Error('Error al realizar la petición')
    }
  }
)

export default {
  // Auth endpoints
  async startSession() {
    const response = await apiClient.post('/api/auth/start-session')
    return response.data
  },
  
  async validateAnswer(sessionId, questionNumber, answer) {
    const response = await apiClient.post('/api/auth/validate-answer', {
      session_id: sessionId,
      question_number: questionNumber,
      answer: answer
    })
    return response.data
  },
  
  // Generation endpoint
  async generateDocuments(sessionId, eventData) {
    const response = await apiClient.post('/api/generate', {
      session_id: sessionId,
      ...eventData
    })
    return response.data
  },
  
  // Download endpoint
  getDownloadUrl(filename) {
    return `${API_BASE_URL}/api/download/${filename}`
  }
}
