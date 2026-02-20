<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 p-4">
    <div class="max-w-7xl mx-auto">
      <h1 class="text-3xl font-bold text-gray-800 mb-8 text-center">
        Generador de Recursos
      </h1>
      
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Formulario (Izquierda) -->
        <div class="bg-white rounded-2xl shadow-xl p-6">
          <h2 class="text-xl font-semibold text-gray-800 mb-4">
            Datos del Evento
          </h2>
          
          <form @submit.prevent="handleGenerate" class="space-y-4">
            <div>
              <label class="block text-gray-700 font-medium mb-2">
                Fecha del Evento *
              </label>
              <input
                v-model="formData.fecha_evento"
                type="text"
                placeholder="Ej: 15 de Diciembre, 2024"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 
                       focus:ring-blue-500 focus:border-transparent"
                required
              />
            </div>
            
            <div>
              <label class="block text-gray-700 font-medium mb-2">
                Hora del Evento *
              </label>
              <input
                v-model="formData.hora_evento"
                type="text"
                placeholder="Ej: 7:00 PM"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 
                       focus:ring-blue-500 focus:border-transparent"
                required
              />
            </div>
            
            <div>
              <label class="block text-gray-700 font-medium mb-2">
                Lugar del Evento *
              </label>
              <input
                v-model="formData.lugar_evento"
                type="text"
                placeholder="Ej: Auditorio Central"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 
                       focus:ring-blue-500 focus:border-transparent"
                required
              />
            </div>
            
            <div>
              <label class="block text-gray-700 font-medium mb-2">
                Referencia del Evento (Opcional)
              </label>
              <input
                v-model="formData.referencia_evento"
                type="text"
                placeholder="Ej: Calle Principal #123"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 
                       focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            
            <div>
              <label class="block text-gray-700 font-medium mb-2">
                Nombre del Proyecto *
              </label>
              <input
                v-model="formData.nombre_proyecto"
                type="text"
                placeholder="Ej: Campaña_Navidad_2024"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 
                       focus:ring-blue-500 focus:border-transparent"
                required
              />
            </div>
            
            <button
              type="submit"
              :disabled="generating"
              class="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 rounded-lg 
                     transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {{ generating ? 'Generando...' : 'Generar' }}
            </button>
          </form>
        </div>
        
        <!-- Previsualización (Derecha) -->
        <div class="bg-white rounded-2xl shadow-xl p-6">
          <div class="flex justify-between items-center mb-4">
            <h2 class="text-xl font-semibold text-gray-800">
              Previsualización
            </h2>
            
            <!-- Selector de documento para previsualizar -->
            <select
              v-if="generatedDocuments.length > 0"
              v-model="selectedPreviewType"
              @change="updatePreview"
              class="px-3 py-1 border border-gray-300 rounded-lg text-sm focus:ring-2 
                     focus:ring-blue-500 focus:border-transparent"
            >
              <option value="a4">A4</option>
              <option value="4x1">4x1</option>
              <option value="gigantografia">Gigantografía</option>
            </select>
          </div>
          
          <div v-if="!previewUrl && !generating" class="flex items-center justify-center h-96 bg-gray-100 rounded-lg">
            <div class="text-center">
              <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
              </svg>
              <p class="mt-2 text-gray-500">
                La previsualización aparecerá aquí después de generar
              </p>
            </div>
          </div>
          
          <!-- Estado de carga -->
          <div v-else-if="generating" class="flex items-center justify-center h-96 bg-gray-100 rounded-lg">
            <div class="text-center">
              <svg class="animate-spin h-12 w-12 text-blue-600 mx-auto" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <p class="mt-4 text-gray-600 font-medium">
                Generando documentos...
              </p>
              <p class="mt-1 text-sm text-gray-500">
                Esto puede tomar unos segundos
              </p>
            </div>
          </div>
          
          <div v-else class="space-y-4">
            <!-- Indicador de regeneración -->
            <div v-if="generating" class="bg-blue-50 border border-blue-200 rounded-lg p-3 flex items-center gap-2">
              <svg class="animate-spin h-5 w-5 text-blue-600" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span class="text-blue-700 font-medium">Regenerando documentos...</span>
            </div>
            
            <!-- Visor de PDF -->
            <div class="border border-gray-300 rounded-lg overflow-hidden bg-gray-50">
              <iframe
                :src="previewUrl"
                class="w-full h-[500px]"
                frameborder="0"
              ></iframe>
            </div>
            
            <!-- Sección de Descarga -->
            <div class="space-y-2">
              <h3 class="text-lg font-semibold text-gray-800">Descargar Archivos</h3>
              
              <div class="grid grid-cols-1 gap-2">
                <button
                  v-for="doc in generatedDocuments"
                  :key="doc.type"
                  @click="handleDownload(doc.filename)"
                  :disabled="doc.status !== 'success'"
                  :class="[
                    'w-full font-semibold py-2 rounded-lg transition duration-200',
                    doc.status === 'success' 
                      ? 'bg-green-600 hover:bg-green-700 text-white' 
                      : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  ]"
                >
                  <span v-if="doc.status === 'success'">
                    {{ getDownloadButtonText(doc.type) }}
                  </span>
                  <span v-else>
                    {{ getDownloadButtonText(doc.type) }} - Error
                  </span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useSessionStore } from '../stores/session'
import api from '../services/api'

const sessionStore = useSessionStore()

const formData = ref({
  fecha_evento: '',
  hora_evento: '',
  lugar_evento: '',
  referencia_evento: '',
  nombre_proyecto: ''
})

const generating = ref(false)
const previewUrl = ref(null)
const generatedDocuments = ref([])
const selectedPreviewType = ref('a4')

const handleGenerate = async () => {
  generating.value = true
  
  // Limpiar previsualización anterior
  previewUrl.value = null
  generatedDocuments.value = []
  
  try {
    const response = await api.generateDocuments(
      sessionStore.sessionId,
      formData.value
    )
    
    if (response.success) {
      generatedDocuments.value = response.documents
      
      // Forzar actualización de previsualización con timestamp para evitar caché
      updatePreview()
    }
  } catch (error) {
    alert(error.message || 'Error al generar documentos. Por favor, intenta de nuevo.')
  } finally {
    generating.value = false
  }
}

const updatePreview = () => {
  const selectedDoc = generatedDocuments.value.find(
    doc => doc.type === selectedPreviewType.value
  )
  
  if (selectedDoc && selectedDoc.status === 'success') {
    // Agregar timestamp para evitar caché del navegador y forzar recarga
    const timestamp = new Date().getTime()
    previewUrl.value = `${api.getPreviewUrl(selectedDoc.filename)}?t=${timestamp}`
  } else {
    previewUrl.value = null
  }
}

const handleDownload = (filename) => {
  const url = api.getDownloadUrl(filename)
  window.open(url, '_blank')
}

const getDownloadButtonText = (type) => {
  const labels = {
    'a4': 'Descargar A4',
    '4x1': 'Descargar 4x1',
    'gigantografia': 'Descargar Gigantografía'
  }
  return labels[type] || 'Descargar'
}
</script>
