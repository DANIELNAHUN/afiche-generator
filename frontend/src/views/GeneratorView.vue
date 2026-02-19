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
          <h2 class="text-xl font-semibold text-gray-800 mb-4">
            Previsualización
          </h2>
          
          <div v-if="!previewUrl" class="flex items-center justify-center h-96 bg-gray-100 rounded-lg">
            <p class="text-gray-500">
              La previsualización aparecerá aquí después de generar
            </p>
          </div>
          
          <div v-else class="space-y-4">
            <div class="border border-gray-300 rounded-lg overflow-hidden">
              <embed
                :src="previewUrl"
                type="application/pdf"
                class="w-full h-96"
              />
            </div>
            
            <!-- Sección de Descarga -->
            <div class="space-y-2">
              <h3 class="text-lg font-semibold text-gray-800">Descargar Archivos</h3>
              
              <button
                v-for="doc in generatedDocuments"
                :key="doc.type"
                @click="handleDownload(doc.filename)"
                :disabled="doc.status !== 'success'"
                class="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-2 rounded-lg 
                       transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {{ getDownloadButtonText(doc.type) }}
              </button>
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

const handleGenerate = async () => {
  generating.value = true
  
  try {
    const response = await api.generateDocuments(
      sessionStore.sessionId,
      formData.value
    )
    
    if (response.success) {
      generatedDocuments.value = response.documents
      
      // Mostrar previsualización del A4
      const a4Doc = response.documents.find(doc => doc.type === 'a4')
      if (a4Doc && a4Doc.status === 'success') {
        previewUrl.value = api.getDownloadUrl(a4Doc.filename)
      }
    }
  } catch (error) {
    alert(error.message || 'Error al generar documentos. Por favor, intenta de nuevo.')
  } finally {
    generating.value = false
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
