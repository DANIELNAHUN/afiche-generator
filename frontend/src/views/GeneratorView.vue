<template>
  <div class="min-h-screen bg-background px-4 py-12">
    <div class="max-w-6xl mx-auto">

      <!-- Page header -->
      <div class="text-center mb-10">
        <p class="text-xs tracking-[0.2em] uppercase text-muted-foreground mb-1">Herramienta</p>
        <h1 class="text-2xl font-medium text-foreground">Generador de Recursos para la campaña</h1>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">

        <!-- Form -->
        <div class="bg-card border border-border rounded-2xl p-6 space-y-5">
          <h2 class="text-sm font-semibold tracking-[0.15em] uppercase text-muted-foreground">
            Datos de la Campaña
          </h2>

          <form @submit.prevent="handleGenerate" class="space-y-5">

            <!-- Fecha -->
            <div>
              <label class="block text-sm text-muted-foreground mb-2">Fecha de la Campaña *</label>
              <input
                v-model="selectedDateDisplay"
                type="date"
                @change="handleDateChange"
                class="w-full px-4 py-2.5 bg-background border border-border rounded-lg text-foreground
                       focus:outline-none focus:ring-1 focus:ring-ring transition-colors"
                required
              />
              <div v-if="formData.fecha_evento" class="mt-2 px-3 py-2 bg-muted rounded-lg">
                <p class="text-xs text-muted-foreground mb-0.5">Formato documento</p>
                <p class="text-sm font-medium text-foreground">{{ formData.fecha_evento }}</p>
              </div>
            </div>

            <!-- Hora -->
            <div>
              <label class="block text-sm text-muted-foreground mb-2">Hora de la Campaña *</label>
              <div class="flex gap-2">
                <select
                  v-model="timeComponents.hour"
                  @change="updateTimeString"
                  class="flex-1 px-3 py-2.5 bg-background border border-border rounded-lg text-foreground
                         focus:outline-none focus:ring-1 focus:ring-ring transition-colors"
                  required
                >
                  <option value="" disabled>Hora</option>
                  <option v-for="h in 12" :key="h" :value="h">{{ h }}</option>
                </select>

                <span class="flex items-center text-muted-foreground font-medium">:</span>

                <select
                  v-model="timeComponents.minute"
                  @change="updateTimeString"
                  class="flex-1 px-3 py-2.5 bg-background border border-border rounded-lg text-foreground
                         focus:outline-none focus:ring-1 focus:ring-ring transition-colors"
                  required
                >
                  <option value="" disabled>Min</option>
                  <option v-for="m in [1,16,31,46]" :key="m-1" :value="String(m-1).padStart(2, '0')">
                    {{ String(m-1).padStart(2, '0') }}
                  </option>
                </select>

                <select
                  v-model="timeComponents.period"
                  @change="updateTimeString"
                  class="px-3 py-2.5 bg-background border border-border rounded-lg text-foreground
                         focus:outline-none focus:ring-1 focus:ring-ring transition-colors"
                  required
                >
                  <option value="" disabled>AM/PM</option>
                  <option value="AM">AM</option>
                  <option value="PM">PM</option>
                </select>
              </div>
              <div v-if="formData.hora_evento" class="mt-2 px-3 py-2 bg-muted rounded-lg">
                <p class="text-xs text-muted-foreground mb-0.5">Hora seleccionada</p>
                <p class="text-sm font-medium text-foreground">{{ formData.hora_evento }}</p>
              </div>
            </div>

            <!-- Lugar -->
            <div>
              <label class="block text-sm text-muted-foreground mb-2">Lugar de la Campaña *</label>
              <input
                v-model="formData.lugar_evento"
                type="text"
                placeholder="Ej: Auditorio Central"
                class="w-full px-4 py-2.5 bg-background border border-border rounded-lg text-foreground
                       placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring
                       transition-colors uppercase"
                @input="handleLugarInput($event)"
                required
              />
            </div>

            <!-- Referencia -->
            <div>
              <label class="block text-sm text-muted-foreground mb-2">Referencia (Opcional)</label>
              <input
                v-model="formData.referencia_evento"
                type="text"
                placeholder="Ej: Calle Principal #123"
                class="w-full px-4 py-2.5 bg-background border border-border rounded-lg text-foreground
                       placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring
                       transition-colors"
              />
            </div>

            <!-- Nombre proyecto -->
            <div>
              <label class="block text-sm text-muted-foreground mb-2">Nombre del Proyecto *</label>
              <input
                v-model="formData.nombre_proyecto"
                type="text"
                placeholder="Ej: Campaña_Ovalo_2026"
                class="w-full px-4 py-2.5 bg-background border border-border rounded-lg text-foreground
                       placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring
                       transition-colors"
                required
              />
            </div>

            <div class="flex flex-col gap-3 pt-1">
              <button
                type="submit"
                :disabled="generating"
                class="w-full px-8 py-3 bg-primary text-primary-foreground rounded-full text-sm font-semibold
                       tracking-wide transition-all duration-300 hover:bg-primary/90 hover:-translate-y-0.5
                       active:scale-95 disabled:opacity-40 disabled:cursor-not-allowed disabled:translate-y-0"
              >
                {{ generating ? 'Generando...' : 'Generar Afiche' }}
              </button>

              <button
                type="button"
                @click="openAudioModal"
                :disabled="generating"
                class="w-full px-8 py-3 bg-secondary text-secondary-foreground border border-border rounded-full
                       text-sm font-semibold tracking-wide transition-all duration-300 hover:bg-border
                       hover:-translate-y-0.5 active:scale-95 disabled:opacity-40 disabled:cursor-not-allowed
                       disabled:translate-y-0"
              >
                Generar Audio
              </button>
            </div>
          </form>
        </div>

        <!-- Preview -->
        <div class="bg-card border border-border rounded-2xl p-6">
          <div class="flex justify-between items-center mb-5">
            <h2 class="text-sm font-semibold tracking-[0.15em] uppercase text-muted-foreground">
              Previsualización
            </h2>
            <select
              v-if="generatedDocuments.length > 0"
              v-model="selectedPreviewType"
              @change="updatePreview"
              class="px-3 py-1.5 bg-background border border-border rounded-lg text-sm text-foreground
                     focus:outline-none focus:ring-1 focus:ring-ring transition-colors"
            >
              <option value="a4">A4</option>
              <option value="4x1">4x1</option>
              <option value="gigantografia">Gigantografía</option>
            </select>
          </div>

          <!-- Empty state -->
          <div
            v-if="!previewUrl && !generating && generatedAudioFiles.length === 0"
            class="flex flex-col items-center justify-center h-96 bg-muted rounded-xl"
          >
            <svg class="h-10 w-10 text-muted-foreground/40" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                    d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
            </svg>
            <p class="mt-3 text-sm text-muted-foreground">
              La previsualización aparecerá aquí
            </p>
          </div>

          <!-- Loading state -->
          <div v-else-if="generating" class="flex flex-col items-center justify-center h-96 bg-muted rounded-xl">
            <svg class="animate-spin h-8 w-8 text-primary" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <p class="mt-4 text-sm text-muted-foreground">Generando documentos...</p>
          </div>

          <!-- Results -->
          <div v-else class="space-y-4">
            <!-- PDF viewer -->
            <div v-if="previewUrl" class="border border-border rounded-xl overflow-hidden">
              <iframe :src="previewUrl" class="w-full h-[460px]" frameborder="0"></iframe>
            </div>

            <!-- Document downloads -->
            <div v-if="generatedDocuments.length > 0">
              <p class="text-xs tracking-[0.15em] uppercase text-muted-foreground mb-2">Documentos</p>
              <div class="grid grid-cols-1 gap-2">
                <button
                  v-for="doc in generatedDocuments"
                  :key="doc.type"
                  @click="handleDownload(doc.filename)"
                  :disabled="doc.status !== 'success'"
                  class="w-full py-2.5 rounded-full text-sm font-semibold tracking-wide transition-all duration-200
                         hover:-translate-y-0.5 active:scale-95 disabled:opacity-40 disabled:cursor-not-allowed
                         disabled:translate-y-0"
                  :class="doc.status === 'success'
                    ? 'bg-primary text-primary-foreground hover:bg-primary/90'
                    : 'bg-muted text-muted-foreground'"
                >
                  {{ doc.status === 'success' ? getDownloadButtonText(doc.type) : `${getDownloadButtonText(doc.type)} — Error` }}
                </button>
              </div>
            </div>

            <!-- Audio downloads -->
            <div v-if="generatedAudioFiles.length > 0">
              <p class="text-xs tracking-[0.15em] uppercase text-muted-foreground mb-2">Audios</p>
              <div class="grid grid-cols-1 gap-2">
                <button
                  v-for="audioFile in generatedAudioFiles"
                  :key="audioFile"
                  @click="downloadAudio(audioFile)"
                  class="w-full py-2.5 bg-secondary text-secondary-foreground border border-border rounded-full
                         text-sm font-semibold tracking-wide transition-all duration-200 hover:bg-border
                         hover:-translate-y-0.5 active:scale-95"
                >
                  Descargar Versión {{ audioFile.includes('HOY') ? 'HOY' : 'ESTE' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Audio Modal -->
    <div
      v-if="showAudioModal"
      class="fixed inset-0 bg-foreground/20 backdrop-blur-sm flex items-center justify-center z-50 p-4"
      @click.self="closeAudioModal"
    >
      <div class="bg-background border border-border rounded-2xl shadow-xl max-w-3xl w-full p-6 max-h-[90vh] overflow-y-auto">

        <!-- Modal header -->
        <div class="flex justify-between items-center mb-6">
          <div>
            <p class="text-xs tracking-[0.2em] uppercase text-muted-foreground mb-0.5">Campaña</p>
            <h2 class="text-xl font-medium text-foreground">Generar Audio</h2>
          </div>
          <button
            @click="closeAudioModal"
            class="p-2 rounded-full text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <p class="text-sm text-muted-foreground mb-5">
          Sube los archivos MP3 con la información de hora y lugar del evento para ambas versiones.
        </p>

        <!-- IA notice -->
        <div v-if="showIAMessage" class="mb-5 p-4 bg-muted border border-border rounded-xl">
          <div class="flex items-start gap-3">
            <svg class="w-4 h-4 text-primary mt-0.5 shrink-0 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <p class="text-sm text-foreground/70">
              Regístrate con Google en ElevenLabs, pega el texto y selecciona la voz
              <span class="font-semibold text-foreground">Cesar Rodriguez</span>. Se abrirá en 5 segundos...
              <a href="https://elevenlabs.io/app/speech-synthesis/text-to-speech" target="_blank"
                 class="underline text-foreground hover:text-primary transition-colors ml-1">
                Abrir manualmente
              </a>
            </p>
          </div>
        </div>

        <!-- Two columns: HOY / ESTE -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-5 mb-6">

          <!-- HOY -->
          <div class="flex flex-col gap-3">
            <div class="bg-muted border border-border rounded-xl p-4">
              <div class="flex justify-between items-center mb-2">
                <label class="text-xs font-semibold tracking-wide uppercase text-muted-foreground">Guión HOY</label>
                <div class="flex gap-3">
                  <button @click="copyTextAndRedirectToIA(textHoy)"
                    class="text-xs text-foreground/60 hover:text-primary transition-colors flex items-center gap-1">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
                    </svg>
                    Copiar en IA
                  </button>
                  <button @click="copyTextHoy"
                    class="text-xs transition-colors flex items-center gap-1"
                    :class="copiedHoy ? 'text-primary' : 'text-foreground/60 hover:text-foreground'">
                    <svg v-if="!copiedHoy" class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
                    </svg>
                    <svg v-else class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                    </svg>
                    {{ copiedHoy ? 'Copiado' : 'Copiar' }}
                  </button>
                </div>
              </div>
              <textarea v-model="textHoy"
                class="w-full text-sm text-foreground bg-background border border-border rounded-lg
                       focus:outline-none focus:ring-1 focus:ring-ring min-h-[100px] p-2.5 resize-none
                       transition-colors">
              </textarea>
            </div>

            <!-- Drop zone HOY -->
            <div
              @dragover.prevent="dragOverHoy = true"
              @dragleave.prevent="dragOverHoy = false"
              @drop.prevent="handleFileDropHoy"
              class="border-2 border-dashed rounded-xl p-5 text-center transition-colors flex flex-col items-center justify-center min-h-[140px]"
              :class="dragOverHoy ? 'border-primary bg-primary/5' : 'border-border bg-muted'"
            >
              <input ref="fileInputHoy" type="file" accept=".mp3" @change="handleFileSelectHoy" class="hidden" />

              <div v-if="!selectedAudioHoy" class="flex flex-col items-center gap-2">
                <svg class="h-7 w-7 text-muted-foreground/50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                        d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
                </svg>
                <p class="text-xs text-muted-foreground">Audio Versión HOY</p>
                <button type="button" @click="$refs.fileInputHoy.click()"
                  class="px-4 py-1.5 bg-primary text-primary-foreground rounded-full text-xs font-semibold
                         transition-all hover:bg-primary/90 active:scale-95">
                  Seleccionar
                </button>
              </div>

              <div v-else class="flex flex-col items-center gap-1.5">
                <svg class="h-7 w-7 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                <p class="text-sm font-medium text-foreground truncate w-full px-2 text-center" :title="selectedAudioHoy.name">
                  {{ selectedAudioHoy.name }}
                </p>
                <p class="text-xs text-muted-foreground">{{ formatFileSize(selectedAudioHoy.size) }}</p>
                <button type="button" @click="clearSelectedFileHoy"
                  class="text-xs text-muted-foreground hover:text-foreground transition-colors">
                  Cambiar
                </button>
              </div>
            </div>
          </div>

          <!-- ESTE -->
          <div class="flex flex-col gap-3">
            <div class="bg-muted border border-border rounded-xl p-4">
              <div class="flex justify-between items-center mb-2">
                <label class="text-xs font-semibold tracking-wide uppercase text-muted-foreground">Guión ESTE</label>
                <div class="flex gap-3">
                  <button @click="copyTextAndRedirectToIA(textEste)"
                    class="text-xs text-foreground/60 hover:text-primary transition-colors flex items-center gap-1">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
                    </svg>
                    Copiar en IA
                  </button>
                  <button @click="copyTextEste"
                    class="text-xs transition-colors flex items-center gap-1"
                    :class="copiedEste ? 'text-primary' : 'text-foreground/60 hover:text-foreground'">
                    <svg v-if="!copiedEste" class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
                    </svg>
                    <svg v-else class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                    </svg>
                    {{ copiedEste ? 'Copiado' : 'Copiar' }}
                  </button>
                </div>
              </div>
              <textarea v-model="textEste"
                class="w-full text-sm text-foreground bg-background border border-border rounded-lg
                       focus:outline-none focus:ring-1 focus:ring-ring min-h-[100px] p-2.5 resize-none
                       transition-colors">
              </textarea>
            </div>

            <!-- Drop zone ESTE -->
            <div
              @dragover.prevent="dragOverEste = true"
              @dragleave.prevent="dragOverEste = false"
              @drop.prevent="handleFileDropEste"
              class="border-2 border-dashed rounded-xl p-5 text-center transition-colors flex flex-col items-center justify-center min-h-[140px]"
              :class="dragOverEste ? 'border-primary bg-primary/5' : 'border-border bg-muted'"
            >
              <input ref="fileInputEste" type="file" accept=".mp3" @change="handleFileSelectEste" class="hidden" />

              <div v-if="!selectedAudioEste" class="flex flex-col items-center gap-2">
                <svg class="h-7 w-7 text-muted-foreground/50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                        d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
                </svg>
                <p class="text-xs text-muted-foreground">Audio Versión ESTE</p>
                <button type="button" @click="$refs.fileInputEste.click()"
                  class="px-4 py-1.5 bg-primary text-primary-foreground rounded-full text-xs font-semibold
                         transition-all hover:bg-primary/90 active:scale-95">
                  Seleccionar
                </button>
              </div>

              <div v-else class="flex flex-col items-center gap-1.5">
                <svg class="h-7 w-7 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                <p class="text-sm font-medium text-foreground truncate w-full px-2 text-center" :title="selectedAudioEste.name">
                  {{ selectedAudioEste.name }}
                </p>
                <p class="text-xs text-muted-foreground">{{ formatFileSize(selectedAudioEste.size) }}</p>
                <button type="button" @click="clearSelectedFileEste"
                  class="text-xs text-muted-foreground hover:text-foreground transition-colors">
                  Cambiar
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Modal actions -->
        <div class="flex gap-3">
          <button
            type="button"
            @click="closeAudioModal"
            :disabled="generatingAudio"
            class="flex-1 px-4 py-2.5 border border-border text-foreground rounded-full text-sm font-semibold
                   hover:bg-muted transition-all disabled:opacity-40 disabled:cursor-not-allowed"
          >
            Cancelar
          </button>
          <button
            type="button"
            @click="handleGenerateAudio"
            :disabled="!selectedAudioHoy || !selectedAudioEste || generatingAudio"
            class="flex-1 px-4 py-2.5 bg-primary text-primary-foreground rounded-full text-sm font-semibold
                   tracking-wide transition-all hover:bg-primary/90 hover:-translate-y-0.5 active:scale-95
                   disabled:opacity-40 disabled:cursor-not-allowed disabled:translate-y-0"
          >
            {{ generatingAudio ? 'Generando...' : 'Generar Audio' }}
          </button>
        </div>

        <!-- Progress message -->
        <div v-if="audioGenerationMessage" class="mt-4 p-4 rounded-xl border"
          :class="audioGenerationSuccess ? 'bg-muted border-border' : 'bg-muted border-border'">
          <p class="text-sm" :class="audioGenerationSuccess ? 'text-foreground' : 'text-destructive'">
            {{ audioGenerationMessage }}
          </p>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useSessionStore, saveFormData, loadFormData, saveResults, loadResults } from '../stores/session'
import api from '../services/api'

const sessionStore = useSessionStore()
const router = useRouter()

// Restaurar datos del formulario si la sesión sigue activa
const savedForm = loadFormData()

const formData = ref(savedForm?.formData ?? {
  fecha_evento: '',
  hora_evento: '5:30 PM',
  lugar_evento: '',
  referencia_evento: '',
  nombre_proyecto: ''
})

const timeComponents = ref(savedForm?.timeComponents ?? { hour: '5', minute: '30', period: 'PM' })

// Restaurar la fecha en el input date (formato YYYY-MM-DD)
const selectedDateDisplay = ref(savedForm?.rawDate ?? '')

// Persistir formulario en localStorage mientras la sesión esté activa
watch(
  [formData, timeComponents],
  () => {
    if (sessionStore.isAuthenticated) {
      saveFormData(formData.value, timeComponents.value, selectedDateDisplay.value)
    }
  },
  { deep: true }
)

// Verificar expiración de sesión periódicamente
let sessionCheckInterval = null
onMounted(() => {
  sessionCheckInterval = setInterval(() => {
    if (!sessionStore.isAuthenticated) {
      router.push({ name: 'login' })
    }
  }, 15000) // cada 15 segundos
})
onUnmounted(() => {
  clearInterval(sessionCheckInterval)
})
const generating = ref(false)
const previewUrl = ref(null)

// Restaurar resultados previos si la sesión sigue activa
const savedResults = loadResults()
const generatedDocuments = ref(savedResults?.documents ?? [])
const generatedAudioFiles = ref(savedResults?.audioFiles ?? [])
const selectedPreviewType = ref(savedResults?.selectedPreviewType ?? 'a4')

// Restaurar previewUrl si había documentos guardados
if (savedResults?.documents?.length) {
  const doc = savedResults.documents.find(d => d.type === savedResults.selectedPreviewType && d.status === 'success')
  if (doc) previewUrl.value = `${api.getPreviewUrl(doc.filename)}?t=${Date.now()}`
}

const showAudioModal = ref(false)
const selectedAudioHoy = ref(null)
const selectedAudioEste = ref(null)
const generatingAudio = ref(false)
const audioGenerationMessage = ref('')
const audioGenerationSuccess = ref(false)
const dragOverHoy = ref(false)
const dragOverEste = ref(false)

const textHoy = ref('')
const textEste = ref('')
const copiedHoy = ref(false)
const copiedEste = ref(false)
const showIAMessage = ref(false)

const copyTextAndRedirectToIA = async (text) => {
  try {
    await navigator.clipboard.writeText(text)
    showIAMessage.value = true
    setTimeout(() => {
      showIAMessage.value = false
      window.open('https://elevenlabs.io/app/speech-synthesis/text-to-speech', '_blank')
    }, 5000)
  } catch (err) {
    console.error('Error al copiar:', err)
  }
}

const openAudioModal = () => {
  const { hour, minute, period } = timeComponents.value
  let timeText = formData.value.hora_evento || '[HORA]'

  if (hour && minute && period) {
    const hourNum = parseInt(hour, 10)
    let suffix = 'DE LA MAÑANA'
    if (period === 'PM') {
      suffix = (hourNum === 12 || hourNum < 7) ? 'DE LA TARDE' : 'DE LA NOCHE'
    }
    const hourToWord = {
      '1': 'UNA', '2': 'DOS', '3': 'TRES', '4': 'CUATRO', '5': 'CINCO', '6': 'SEIS',
      '7': 'SIETE', '8': 'OCHO', '9': 'NUEVE', '10': 'DIEZ', '11': 'ONCE', '12': 'DOCE'
    }
    const minToWord = { '00': 'EN PUNTO', '15': 'Y QUINCE', '30': 'Y TREINTA', '45': 'Y CUARENTA Y CINCO' }
    const hStr = hour.toString()
    const mStr = minute.toString().padStart(2, '0')
    timeText = `${hourToWord[hStr] || hStr} ${minToWord[mStr] || `Y ${mStr}`} ${suffix}`
  }

  let baseText = `${formData.value.fecha_evento || '[FECHA]'}.. DESDE LAS ${timeText}.. EN LA ${formData.value.lugar_evento || '[LUGAR]'}`
  if (formData.value.referencia_evento) baseText += `.. AL COSTADO DE ${formData.value.referencia_evento}`
  baseText = baseText.toUpperCase() + '...'

  textHoy.value = `HOY ${baseText}`
  textEste.value = `ESTE ${baseText}`
  showAudioModal.value = true
}

const copyTextHoy = async () => {
  try {
    await navigator.clipboard.writeText(textHoy.value)
    copiedHoy.value = true
    setTimeout(() => { copiedHoy.value = false }, 2000)
  } catch (err) { console.error(err) }
}

const copyTextEste = async () => {
  try {
    await navigator.clipboard.writeText(textEste.value)
    copiedEste.value = true
    setTimeout(() => { copiedEste.value = false }, 2000)
  } catch (err) { console.error(err) }
}

const handleLugarInput = (event) => {
  const upper = event.target.value.toUpperCase()
  formData.value.lugar_evento = upper
  const timestamp = Date.now()
  formData.value.nombre_proyecto = upper.trim().replace(/\s+/g, '_') + '_' + timestamp
}

const handleDateChange = (event) => {
  const dateValue = event.target.value
  selectedDateDisplay.value = dateValue
  if (!dateValue) { formData.value.fecha_evento = ''; return }
  const [year, month, day] = dateValue.split('-')
  const date = new Date(year, month - 1, day)
  const dias = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado']
  const meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
  formData.value.fecha_evento = `${dias[date.getDay()]} ${parseInt(day, 10)} de ${meses[date.getMonth()]}`.toUpperCase()
  if (sessionStore.isAuthenticated) {
    saveFormData(formData.value, timeComponents.value, dateValue)
  }
}

const updateTimeString = () => {
  const { hour, minute, period } = timeComponents.value
  formData.value.hora_evento = (hour && minute && period) ? `${hour}:${minute} ${period}` : ''
}

const handleGenerate = async () => {
  generating.value = true
  previewUrl.value = null
  generatedDocuments.value = []
  generatedAudioFiles.value = []
  try {
    const response = await api.generateDocuments(sessionStore.sessionId, formData.value)
    if (response.success) {
      generatedDocuments.value = response.documents
      updatePreview()
      saveResults(response.documents, generatedAudioFiles.value, selectedPreviewType.value)
    }
  } catch (error) {
    alert(error.message || 'Error al generar documentos. Por favor, intenta de nuevo.')
  } finally {
    generating.value = false
  }
}

const updatePreview = () => {
  const selectedDoc = generatedDocuments.value.find(doc => doc.type === selectedPreviewType.value)
  if (selectedDoc && selectedDoc.status === 'success') {
    previewUrl.value = `${api.getPreviewUrl(selectedDoc.filename)}?t=${Date.now()}`
  } else {
    previewUrl.value = null
  }
  if (sessionStore.isAuthenticated && generatedDocuments.value.length) {
    saveResults(generatedDocuments.value, generatedAudioFiles.value, selectedPreviewType.value)
  }
}

const handleDownload = (filename) => window.open(api.getDownloadUrl(filename), '_blank')
const downloadAudio = (filename) => window.open(api.getDownloadUrl(filename), '_blank')

const getDownloadButtonText = (type) => ({
  'a4': 'Descargar A4', '4x1': 'Descargar 4x1', 'gigantografia': 'Descargar Gigantografía'
}[type] || 'Descargar')

const closeAudioModal = () => {
  showAudioModal.value = false
  audioGenerationMessage.value = ''
  audioGenerationSuccess.value = false
  showIAMessage.value = false
}

const handleFileSelectHoy = (event) => {
  const file = event.target.files[0]
  if (file?.name.endsWith('.mp3')) selectedAudioHoy.value = file
  else alert('Por favor selecciona un archivo MP3 válido para HOY')
}
const handleFileDropHoy = (event) => {
  dragOverHoy.value = false
  const file = event.dataTransfer.files[0]
  if (file?.name.endsWith('.mp3')) selectedAudioHoy.value = file
  else alert('Por favor selecciona un archivo MP3 válido para HOY')
}
const clearSelectedFileHoy = () => { selectedAudioHoy.value = null }

const handleFileSelectEste = (event) => {
  const file = event.target.files[0]
  if (file?.name.endsWith('.mp3')) selectedAudioEste.value = file
  else alert('Por favor selecciona un archivo MP3 válido para ESTE')
}
const handleFileDropEste = (event) => {
  dragOverEste.value = false
  const file = event.dataTransfer.files[0]
  if (file?.name.endsWith('.mp3')) selectedAudioEste.value = file
  else alert('Por favor selecciona un archivo MP3 válido para ESTE')
}
const clearSelectedFileEste = () => { selectedAudioEste.value = null }

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
    audioGenerationMessage.value = 'Subiendo archivos de audio...'
    await api.uploadEventAudio(sessionStore.sessionId, selectedAudioHoy.value, selectedAudioEste.value)
    audioGenerationMessage.value = 'Procesando audio de campaña...'
    const result = await api.processCampaignAudio(sessionStore.sessionId)
    if (result.success) {
      audioGenerationSuccess.value = true
      audioGenerationMessage.value = `¡Audio generado! Duración: ${result.duration_seconds.toFixed(2)}s`
      generatedAudioFiles.value = result.output_files
      saveResults(generatedDocuments.value, result.output_files, selectedPreviewType.value)
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
