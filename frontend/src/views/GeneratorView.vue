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
              <div class="relative">
                <input
                  v-model="selectedDateDisplay"
                  type="date"
                  @change="handleDateChange"
                  class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 
                         focus:ring-blue-500 focus:border-transparent"
                  required
                />
                <div v-if="formData.fecha_evento" class="mt-2 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                  <p class="text-sm text-gray-600">Formato para el documento:</p>
                  <p class="text-lg font-semibold text-blue-700">{{ formData.fecha_evento }}</p>
                </div>
              </div>
            </div>
            
            <div>
              <label class="block text-gray-700 font-medium mb-2">
                Hora del Evento *
              </label>
              <div class="flex gap-2">
                <!-- Selector de Hora -->
                <select
                  v-model="timeComponents.hour"
                  @change="updateTimeString"
                  class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 
                         focus:ring-blue-500 focus:border-transparent"
                  required
                >
                  <option value="" disabled>Hora</option>
                  <option v-for="h in 12" :key="h" :value="h">{{ h }}</option>
                </select>
                
                <span class="flex items-center text-gray-600 font-bold text-xl">:</span>
                
                <!-- Selector de Minutos -->
                <select
                  v-model="timeComponents.minute"
                  @change="updateTimeString"
                  class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 
                         focus:ring-blue-500 focus:border-transparent"
                  required
                >
                  <option value="" disabled>Min</option>
                  <option v-for="m in [1,16,31,46]" :key="m-1" :value="String(m-1).padStart(2, '0')">
                    {{ String(m-1).padStart(2, '0') }}
                  </option>
                </select>
                
                <!-- Selector AM/PM -->
                <select
                  v-model="timeComponents.period"
                  @change="updateTimeString"
                  class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 
                         focus:ring-blue-500 focus:border-transparent"
                  required
                >
                  <option value="" disabled>AM/PM</option>
                  <option value="AM">AM</option>
                  <option value="PM">PM</option>
                </select>
              </div>
              
              <!-- Vista previa de la hora formateada -->
              <div v-if="formData.hora_evento" class="mt-2 p-3 bg-purple-50 border border-purple-200 rounded-lg">
                <p class="text-sm text-gray-600">Hora seleccionada:</p>
                <p class="text-lg font-semibold text-purple-700">{{ formData.hora_evento }}</p>
              </div>
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
                       focus:ring-blue-500 focus:border-transparent uppercase"
                style="text-transform: uppercase"
                @input="formData.lugar_evento = $event.target.value.toUpperCase()"
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
                placeholder="Ej: Campaña_Ovalo_2026"
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
            
            <button
              type="button"
              @click="showAudioModal = true"
              :disabled="generating"
              class="w-full bg-purple-600 hover:bg-purple-700 text-white font-semibold py-3 rounded-lg 
                     transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Generar Audio
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
          
          <div v-if="!previewUrl && !generating && generatedAudioFiles.length === 0" class="flex items-center justify-center h-96 bg-gray-100 rounded-lg">
            <div class="text-center">
              <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
              </svg>
              <p class="mt-2 text-gray-500">
                La previsualización o tus descargas aparecerán aquí
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
            <div v-if="previewUrl" class="border border-gray-300 rounded-lg overflow-hidden bg-gray-50">
              <iframe
                :src="previewUrl"
                class="w-full h-[500px]"
                frameborder="0"
              ></iframe>
            </div>
            
            <!-- Sección de Descarga -->
            <div class="space-y-4">
              <div v-if="generatedDocuments.length > 0">
                <h3 class="text-lg font-semibold text-gray-800 mb-2">Documentos Generados</h3>
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

              <!-- Audios Generados -->
              <div v-if="generatedAudioFiles.length > 0">
                <h3 class="text-lg font-semibold text-gray-800 mb-2">Audios de Campaña</h3>
                <div class="grid grid-cols-1 gap-2">
                  <button
                    v-for="audioFile in generatedAudioFiles"
                    :key="audioFile"
                    @click="downloadAudio(audioFile)"
                    class="w-full font-semibold py-2 rounded-lg transition duration-200 bg-purple-600 hover:bg-purple-700 text-white shadow-sm"
                  >
                    Descargar Versión {{ audioFile.includes('HOY') ? 'HOY' : 'ESTE' }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Modal para Generar Audio -->
    <div
      v-if="showAudioModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      @click.self="closeAudioModal"
    >
      <div class="bg-white rounded-2xl shadow-2xl max-w-xl w-full p-6">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-2xl font-bold text-gray-800">Generar Audio de Campaña</h2>
          <button
            @click="closeAudioModal"
            class="text-gray-500 hover:text-gray-700 transition"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <div class="space-y-4">
          <div>
            <p class="text-gray-600 mb-4">
              Sube los archivos MP3 con la información de hora y lugar del evento para ambas versiones.
            </p>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <!-- Área de subida HOY -->
              <div
                @dragover.prevent="dragOverHoy = true"
                @dragleave.prevent="dragOverHoy = false"
                @drop.prevent="handleFileDropHoy"
                :class="[
                  'border-2 border-dashed rounded-lg p-4 text-center transition flex flex-col justify-center min-h-[160px]',
                  dragOverHoy ? 'border-purple-500 bg-purple-50' : 'border-gray-300 bg-gray-50'
                ]"
              >
                <input
                  ref="fileInputHoy"
                  type="file"
                  accept=".mp3"
                  @change="handleFileSelectHoy"
                  class="hidden"
                />
                
                <h3 class="font-bold text-gray-700 mb-2">Versión HOY</h3>

                <div v-if="!selectedAudioHoy" class="flex flex-col items-center justify-center">
                  <svg class="h-8 w-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                          d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
                  </svg>
                  <p class="mt-2 text-sm text-gray-600">
                    Arrastra aquí o
                  </p>
                  <button
                    type="button"
                    @click="$refs.fileInputHoy.click()"
                    class="mt-2 px-3 py-1.5 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition text-sm font-medium w-full max-w-[120px]"
                  >
                    Seleccionar
                  </button>
                </div>
                
                <div v-else class="flex flex-col items-center justify-center space-y-1">
                  <svg class="h-8 w-8 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                  <p class="text-gray-800 font-medium text-sm truncate w-full px-2" :title="selectedAudioHoy.name">{{ selectedAudioHoy.name }}</p>
                  <p class="text-xs text-gray-500">{{ formatFileSize(selectedAudioHoy.size) }}</p>
                  <button
                    type="button"
                    @click="clearSelectedFileHoy"
                    class="text-red-600 hover:text-red-700 text-sm font-medium"
                  >
                    Cambiar
                  </button>
                </div>
              </div>

              <!-- Área de subida ESTE -->
              <div
                @dragover.prevent="dragOverEste = true"
                @dragleave.prevent="dragOverEste = false"
                @drop.prevent="handleFileDropEste"
                :class="[
                  'border-2 border-dashed rounded-lg p-4 text-center transition flex flex-col justify-center min-h-[160px]',
                  dragOverEste ? 'border-purple-500 bg-purple-50' : 'border-gray-300 bg-gray-50'
                ]"
              >
                <input
                  ref="fileInputEste"
                  type="file"
                  accept=".mp3"
                  @change="handleFileSelectEste"
                  class="hidden"
                />

                <h3 class="font-bold text-gray-700 mb-2">Versión ESTE</h3>
                
                <div v-if="!selectedAudioEste" class="flex flex-col items-center justify-center">
                  <svg class="h-8 w-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                          d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
                  </svg>
                  <p class="mt-2 text-sm text-gray-600">
                    Arrastra aquí o
                  </p>
                  <button
                    type="button"
                    @click="$refs.fileInputEste.click()"
                    class="mt-2 px-3 py-1.5 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition text-sm font-medium w-full max-w-[120px]"
                  >
                    Seleccionar
                  </button>
                </div>
                
                <div v-else class="flex flex-col items-center justify-center space-y-1">
                  <svg class="h-8 w-8 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                  <p class="text-gray-800 font-medium text-sm truncate w-full px-2" :title="selectedAudioEste.name">{{ selectedAudioEste.name }}</p>
                  <p class="text-xs text-gray-500">{{ formatFileSize(selectedAudioEste.size) }}</p>
                  <button
                    type="button"
                    @click="clearSelectedFileEste"
                    class="text-red-600 hover:text-red-700 text-sm font-medium"
                  >
                    Cambiar
                  </button>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Botones de acción -->
          <div class="flex gap-3">
            <button
              type="button"
              @click="closeAudioModal"
              :disabled="generatingAudio"
              class="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 
                     transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Cancelar
            </button>
            <button
              type="button"
              @click="handleGenerateAudio"
              :disabled="!selectedAudioHoy || !selectedAudioEste || generatingAudio"
              class="flex-1 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg 
                     transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {{ generatingAudio ? 'Generando...' : 'Generar Audio' }}
            </button>
          </div>
          
          <!-- Mensaje de progreso -->
          <div v-if="audioGenerationMessage" class="mt-4 p-3 rounded-lg" :class="audioGenerationSuccess ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'">
            <p :class="audioGenerationSuccess ? 'text-green-700' : 'text-red-700'">
              {{ audioGenerationMessage }}
            </p>
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
  hora_evento: '5:30 PM',
  lugar_evento: '',
  referencia_evento: '',
  nombre_proyecto: ''
})

const timeComponents = ref({
  hour: '5',
  minute: '30',
  period: 'PM'
})

const generating = ref(false)
const previewUrl = ref(null)
const generatedDocuments = ref([])
const generatedAudioFiles = ref([])
const selectedPreviewType = ref('a4')
const selectedDateDisplay = ref('')

// Audio generation state
const showAudioModal = ref(false)
const selectedAudioHoy = ref(null)
const selectedAudioEste = ref(null)
const generatingAudio = ref(false)
const audioGenerationMessage = ref('')
const audioGenerationSuccess = ref(false)
const dragOverHoy = ref(false)
const dragOverEste = ref(false)

// Función para convertir fecha a formato español
const handleDateChange = (event) => {
  const dateValue = event.target.value // Formato: YYYY-MM-DD
  
  if (!dateValue) {
    formData.value.fecha_evento = ''
    return
  }
  
  const [year, month, day] = dateValue.split('-')
  const date = new Date(year, month - 1, day)
  
  // Nombres de días en español
  const diasSemana = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado']
  
  // Nombres de meses en español
  const meses = [
    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
  ]
  
  const nombreDia = diasSemana[date.getDay()]
  const numeroDia = parseInt(day, 10)
  const nombreMes = meses[date.getMonth()]
  
  // Formato: "{nombre_dia} {dia} de {nombre_mes}" en MAYÚSCULAS
  formData.value.fecha_evento = `${nombreDia} ${numeroDia} de ${nombreMes}`.toUpperCase()
}

// Función para actualizar el string de hora desde los componentes
const updateTimeString = () => {
  const { hour, minute, period } = timeComponents.value
  
  if (hour && minute && period) {
    formData.value.hora_evento = `${hour}:${minute} ${period}`
  } else {
    formData.value.hora_evento = ''
  }
}

const handleGenerate = async () => {
  generating.value = true
  
  // Limpiar previsualización anterior
  previewUrl.value = null
  generatedDocuments.value = []
  generatedAudioFiles.value = []
  
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

const downloadAudio = (filename) => {
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

// Audio modal functions
const closeAudioModal = () => {
  showAudioModal.value = false
  audioGenerationMessage.value = ''
  audioGenerationSuccess.value = false
}

const handleFileSelectHoy = (event) => {
  const file = event.target.files[0]
  if (file && file.name.endsWith('.mp3')) {
    selectedAudioHoy.value = file
  } else {
    alert('Por favor selecciona un archivo MP3 válido para HOY')
  }
}

const handleFileDropHoy = (event) => {
  dragOverHoy.value = false
  const file = event.dataTransfer.files[0]
  if (file && file.name.endsWith('.mp3')) {
    selectedAudioHoy.value = file
  } else {
    alert('Por favor selecciona un archivo MP3 válido para HOY')
  }
}

const clearSelectedFileHoy = () => {
  selectedAudioHoy.value = null
}

const handleFileSelectEste = (event) => {
  const file = event.target.files[0]
  if (file && file.name.endsWith('.mp3')) {
    selectedAudioEste.value = file
  } else {
    alert('Por favor selecciona un archivo MP3 válido para ESTE')
  }
}

const handleFileDropEste = (event) => {
  dragOverEste.value = false
  const file = event.dataTransfer.files[0]
  if (file && file.name.endsWith('.mp3')) {
    selectedAudioEste.value = file
  } else {
    alert('Por favor selecciona un archivo MP3 válido para ESTE')
  }
}

const clearSelectedFileEste = () => {
  selectedAudioEste.value = null
}

const formatFileSize = (bytes) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
}

const handleGenerateAudio = async () => {
  if (!selectedAudioHoy.value || !selectedAudioEste.value) {
    alert('Por favor selecciona ambos archivos MP3 (HOY y ESTE)')
    return
  }
  
  generatingAudio.value = true
  audioGenerationMessage.value = ''
  audioGenerationSuccess.value = false
  
  try {
    // Step 1: Upload the MP3 files
    audioGenerationMessage.value = 'Subiendo archivos de audio...'
    await api.uploadEventAudio(sessionStore.sessionId, selectedAudioHoy.value, selectedAudioEste.value)
    
    // Step 2: Process campaign audio
    audioGenerationMessage.value = 'Procesando audio de campaña...'
    const result = await api.processCampaignAudio(sessionStore.sessionId)
    
    if (result.success) {
      audioGenerationSuccess.value = true
      audioGenerationMessage.value = `¡Audio generado exitosamente! Duración combinada: ${result.duration_seconds.toFixed(2)}s`
      generatedAudioFiles.value = result.output_files
      
      // Auto-close modal after 2 seconds
      setTimeout(() => {
        closeAudioModal()
        clearSelectedFileHoy()
        clearSelectedFileEste()
      }, 2000)
    }
  } catch (error) {
    audioGenerationSuccess.value = false
    audioGenerationMessage.value = error.message || 'Error al generar audio. Por favor, intenta de nuevo.'
  } finally {
    generatingAudio.value = false
  }
}

</script>
