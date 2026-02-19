# Documento de Diseño

## Overview

Sistema web full-stack para generación automática de recursos publicitarios evangelísticos. La arquitectura sigue un patrón cliente-servidor con separación clara de responsabilidades: el backend FastAPI maneja la lógica de negocio, procesamiento de plantillas Word y generación de PDFs, mientras el frontend Vue.js 3 proporciona una interfaz de usuario guiada y responsiva.

### Tecnologías Clave

**Backend:**
- FastAPI: Framework web asíncrono de alto rendimiento
- python-docx: Manipulación de archivos Word (.docx)
- docx2pdf o LibreOffice: Conversión de Word a PDF
- Pillow: Procesamiento de imágenes y conversión CMYK
- PyPDF2 o reportlab: Manipulación de PDFs y ajuste de dimensiones

**Frontend:**
- Vue.js 3 (Composition API): Framework reactivo
- Vue Router: Navegación entre vistas
- Axios: Cliente HTTP para comunicación con API
- Tailwind CSS: Framework de utilidades CSS
- Pinia: Gestión de estado (para Session_ID y datos de sesión)

**Justificación de Elecciones:**
- python-docx permite leer y modificar archivos .docx de forma programática
- FastAPI proporciona validación automática de datos y documentación OpenAPI
- Vue 3 Composition API ofrece mejor organización del código y reutilización
- Tailwind CSS facilita el diseño responsivo y personalización de colores

## Architecture

### Arquitectura General

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND (Vue.js 3)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Welcome    │  │    Login     │  │  Generator   │      │
│  │     View     │→ │     View     │→ │     View     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                           ↓                  ↓               │
│                    ┌──────────────────────────┐             │
│                    │   API Service (Axios)    │             │
│                    └──────────────────────────┘             │
└─────────────────────────────┬───────────────────────────────┘
                              │ HTTP/REST
┌─────────────────────────────┴───────────────────────────────┐
│                      BACKEND (FastAPI)                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                    API Endpoints                      │   │
│  │  /api/auth/*  │  /api/generate  │  /api/download/*  │   │
│  └───────┬──────────────────┬──────────────────┬────────┘   │
│          ↓                  ↓                  ↓             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │    Auth      │  │   Document   │  │    File      │      │
│  │   Service    │  │  Generator   │  │   Service    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│          ↓                  ↓                  ↓             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Session    │  │   Template   │  │    Temp      │      │
│  │   Manager    │  │  Processor   │  │   Storage    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└──────────────────────────────────────────────────────────────┘
```

### Flujo de Datos Principal

1. **Autenticación:**
   - Frontend solicita Session_ID → Backend genera UUID
   - Usuario responde preguntas → Backend normaliza y valida
   - Sesión autenticada → Frontend almacena Session_ID

2. **Generación:**
   - Usuario ingresa datos → Frontend valida y envía
   - Backend procesa plantillas Word → Reemplaza campos
   - Backend genera 3 PDFs → Almacena temporalmente
   - Backend retorna metadatos → Frontend muestra previsualización

3. **Descarga:**
   - Usuario solicita archivo → Frontend llama endpoint
   - Backend verifica existencia → Envía archivo con FileResponse


## Components and Interfaces

### Backend Components

#### 1. API Endpoints (main.py)

Expone los endpoints REST y maneja las peticiones HTTP.

```python
from fastapi import FastAPI, HTTPException, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configuración CORS para desarrollo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Puerto de Vite
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/auth/start-session")
async def start_session() -> SessionResponse

@app.post("/api/auth/validate-answer")
async def validate_answer(request: ValidateAnswerRequest) -> ValidationResponse

@app.post("/api/generate")
async def generate_documents(request: GenerateRequest) -> GenerateResponse

@app.get("/api/download/{filename}")
async def download_file(filename: str) -> FileResponse
```

**Modelos de Datos (Pydantic):**

```python
from pydantic import BaseModel, Field
from typing import Optional

class SessionResponse(BaseModel):
    session_id: str
    question_number: int
    question_text: str

class ValidateAnswerRequest(BaseModel):
    session_id: str
    question_number: int
    answer: str

class ValidationResponse(BaseModel):
    success: bool
    message: str
    next_question: Optional[int] = None
    question_text: Optional[str] = None

class GenerateRequest(BaseModel):
    session_id: str
    fecha_evento: str
    hora_evento: str
    lugar_evento: str
    referencia_evento: Optional[str] = ""
    nombre_proyecto: str

class DocumentInfo(BaseModel):
    type: str  # "a4", "4x1", "gigantografia"
    filename: str
    status: str  # "success", "error"
    message: Optional[str] = None

class GenerateResponse(BaseModel):
    success: bool
    documents: list[DocumentInfo]
```

#### 2. Auth Service (services/auth_service.py)

Maneja la lógica de autenticación y validación de respuestas.

```python
import uuid
from typing import Dict, Optional

class AuthService:
    def __init__(self):
        self.sessions: Dict[str, SessionData] = {}
        self.security_questions = [
            {"number": 1, "text": "¿Cuál es el nombre de tu iglesia?", "answer": "iglesia central"},
            {"number": 2, "text": "¿En qué ciudad se realizará el evento?", "answer": "lima"},
            {"number": 3, "text": "¿Cuál es el tema de la campaña?", "answer": "esperanza viva"}
        ]
    
    def create_session(self) -> tuple[str, dict]:
        """Genera un nuevo Session_ID y retorna la primera pregunta"""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = SessionData(
            session_id=session_id,
            current_question=1,
            authenticated=False
        )
        return session_id, self.security_questions[0]
    
    def validate_answer(self, session_id: str, question_number: int, answer: str) -> dict:
        """Valida una respuesta y retorna el resultado"""
        if session_id not in self.sessions:
            raise ValueError("Sesión inválida")
        
        normalized_answer = self._normalize_text(answer)
        expected_answer = self.security_questions[question_number - 1]["answer"]
        
        if normalized_answer == expected_answer:
            if question_number == 3:
                self.sessions[session_id].authenticated = True
                return {"success": True, "message": "Autenticación exitosa"}
            else:
                self.sessions[session_id].current_question = question_number + 1
                next_q = self.security_questions[question_number]
                return {
                    "success": True,
                    "next_question": next_q["number"],
                    "question_text": next_q["text"]
                }
        else:
            # Reiniciar a pregunta 1
            self.sessions[session_id].current_question = 1
            return {
                "success": False,
                "message": "Respuesta incorrecta. Reiniciando...",
                "next_question": 1,
                "question_text": self.security_questions[0]["text"]
            }
    
    def is_authenticated(self, session_id: str) -> bool:
        """Verifica si una sesión está autenticada"""
        return session_id in self.sessions and self.sessions[session_id].authenticated
    
    def _normalize_text(self, text: str) -> str:
        """Normaliza texto: lowercase, trim, remover puntuación extra"""
        import re
        text = text.strip().lower()
        text = re.sub(r'[^\w\s]', '', text)  # Remover puntuación
        text = re.sub(r'\s+', ' ', text)  # Normalizar espacios
        return text

class SessionData:
    def __init__(self, session_id: str, current_question: int, authenticated: bool):
        self.session_id = session_id
        self.current_question = current_question
        self.authenticated = authenticated
```

#### 3. Template Processor (services/template_processor.py)

Procesa plantillas Word y reemplaza campos editables.

```python
from docx import Document
from typing import Dict
import os

class TemplateProcessor:
    def __init__(self):
        self.template_dir = "."  # Raíz del proyecto
        self.templates = {
            "a4": "Formato a4.docx",
            "4x1": "Formato 4x1.docx"
        }
    
    def process_template(self, template_type: str, data: Dict[str, str], output_path: str) -> str:
        """
        Procesa una plantilla Word reemplazando campos con datos
        
        Args:
            template_type: "a4" o "4x1"
            data: Diccionario con fecha_evento, hora_evento, lugar_evento, referencia_evento
            output_path: Ruta donde guardar el documento procesado
        
        Returns:
            Ruta del archivo procesado
        """
        template_path = os.path.join(self.template_dir, self.templates[template_type])
        
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Plantilla no encontrada: {template_path}")
        
        doc = Document(template_path)
        
        # Reemplazar en párrafos
        for paragraph in doc.paragraphs:
            self._replace_in_runs(paragraph.runs, data)
        
        # Reemplazar en tablas
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        self._replace_in_runs(paragraph.runs, data)
        
        doc.save(output_path)
        return output_path
    
    def _replace_in_runs(self, runs, data: Dict[str, str]):
        """Reemplaza marcadores en runs de texto"""
        # Marcadores esperados: {{fecha_evento}}, {{hora_evento}}, {{lugar_evento}}, {{referencia_evento}}
        replacements = {
            "{{fecha_evento}}": data.get("fecha_evento", ""),
            "{{hora_evento}}": data.get("hora_evento", ""),
            "{{lugar_evento}}": data.get("lugar_evento", ""),
            "{{referencia_evento}}": data.get("referencia_evento", "")
        }
        
        for run in runs:
            for marker, value in replacements.items():
                if marker in run.text:
                    run.text = run.text.replace(marker, value)
```

#### 4. Document Generator (services/document_generator.py)

Genera los 3 tipos de PDFs a partir de plantillas procesadas.

```python
import os
import subprocess
from typing import Dict, List
from PIL import Image
from pdf2image import convert_from_path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader

class DocumentGenerator:
    def __init__(self, template_processor, temp_storage_path: str):
        self.template_processor = template_processor
        self.temp_storage = temp_storage_path
        os.makedirs(temp_storage_path, exist_ok=True)
    
    def generate_all(self, data: Dict[str, str], project_name: str) -> List[Dict]:
        """
        Genera los 3 tipos de documentos PDF
        
        Returns:
            Lista de diccionarios con información de cada documento generado
        """
        results = []
        
        # 1. Generar A4
        try:
            a4_filename = self._generate_a4(data, project_name)
            results.append({
                "type": "a4",
                "filename": a4_filename,
                "status": "success"
            })
        except Exception as e:
            results.append({
                "type": "a4",
                "filename": "",
                "status": "error",
                "message": str(e)
            })
        
        # 2. Generar 4x1
        try:
            format_4x1_filename = self._generate_4x1(data, project_name)
            results.append({
                "type": "4x1",
                "filename": format_4x1_filename,
                "status": "success"
            })
        except Exception as e:
            results.append({
                "type": "4x1",
                "filename": "",
                "status": "error",
                "message": str(e)
            })
        
        # 3. Generar Gigantografía
        try:
            giga_filename = self._generate_gigantografia(data, project_name)
            results.append({
                "type": "gigantografia",
                "filename": giga_filename,
                "status": "success"
            })
        except Exception as e:
            results.append({
                "type": "gigantografia",
                "filename": "",
                "status": "error",
                "message": str(e)
            })
        
        return results
    
    def _generate_a4(self, data: Dict[str, str], project_name: str) -> str:
        """Genera PDF en formato A4"""
        docx_path = os.path.join(self.temp_storage, f"{project_name}_a4.docx")
        pdf_path = os.path.join(self.temp_storage, f"{project_name}_a4.pdf")
        
        # Procesar plantilla
        self.template_processor.process_template("a4", data, docx_path)
        
        # Convertir a PDF usando LibreOffice
        self._convert_docx_to_pdf(docx_path, pdf_path)
        
        return f"{project_name}_a4.pdf"
    
    def _generate_4x1(self, data: Dict[str, str], project_name: str) -> str:
        """Genera PDF en formato 4x1"""
        docx_path = os.path.join(self.temp_storage, f"{project_name}_4x1.docx")
        pdf_path = os.path.join(self.temp_storage, f"{project_name}_4x1.pdf")
        
        # Procesar plantilla
        self.template_processor.process_template("4x1", data, docx_path)
        
        # Convertir a PDF
        self._convert_docx_to_pdf(docx_path, pdf_path)
        
        return f"{project_name}_4x1.pdf"
    
    def _generate_gigantografia(self, data: Dict[str, str], project_name: str) -> str:
        """Genera gigantografía 1x1.5m en CMYK"""
        # Primero generar el A4 base
        docx_path = os.path.join(self.temp_storage, f"{project_name}_giga_temp.docx")
        pdf_temp_path = os.path.join(self.temp_storage, f"{project_name}_giga_temp.pdf")
        pdf_final_path = os.path.join(self.temp_storage, f"{project_name}_gigantografia.pdf")
        
        # Procesar plantilla A4
        self.template_processor.process_template("a4", data, docx_path)
        self._convert_docx_to_pdf(docx_path, pdf_temp_path)
        
        # Convertir PDF a imagen
        images = convert_from_path(pdf_temp_path, dpi=300)
        img = images[0]
        
        # Convertir a CMYK
        if img.mode != 'CMYK':
            img = img.convert('CMYK')
        
        # Redimensionar a 1x1.5 metros (100x150 cm) a 300 DPI
        # 100cm = 39.37 inches, 150cm = 59.06 inches
        # A 300 DPI: 11811 x 17717 pixels
        target_size = (11811, 17717)
        img_resized = img.resize(target_size, Image.Resampling.LANCZOS)
        
        # Guardar como PDF usando reportlab
        c = canvas.Canvas(pdf_final_path, pagesize=(11811, 17717))
        
        # Guardar imagen temporalmente
        temp_img_path = os.path.join(self.temp_storage, f"{project_name}_temp.tiff")
        img_resized.save(temp_img_path, 'TIFF')
        
        # Dibujar en PDF
        c.drawImage(temp_img_path, 0, 0, width=11811, height=17717)
        c.save()
        
        # Limpiar archivos temporales
        os.remove(temp_img_path)
        os.remove(pdf_temp_path)
        os.remove(docx_path)
        
        return f"{project_name}_gigantografia.pdf"
    
    def _convert_docx_to_pdf(self, docx_path: str, pdf_path: str):
        """Convierte DOCX a PDF usando LibreOffice"""
        # Comando para LibreOffice en modo headless
        cmd = [
            'libreoffice',
            '--headless',
            '--convert-to', 'pdf',
            '--outdir', os.path.dirname(pdf_path),
            docx_path
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        
        # LibreOffice genera el PDF con el mismo nombre base
        generated_pdf = docx_path.replace('.docx', '.pdf')
        if generated_pdf != pdf_path:
            os.rename(generated_pdf, pdf_path)
```

#### 5. File Service (services/file_service.py)

Maneja almacenamiento temporal y limpieza de archivos.

```python
import os
import time
from typing import Optional
from datetime import datetime, timedelta

class FileService:
    def __init__(self, storage_path: str, cleanup_hours: int = 24):
        self.storage_path = storage_path
        self.cleanup_hours = cleanup_hours
        os.makedirs(storage_path, exist_ok=True)
    
    def get_file_path(self, filename: str) -> Optional[str]:
        """Retorna la ruta completa de un archivo si existe"""
        file_path = os.path.join(self.storage_path, filename)
        if os.path.exists(file_path):
            return file_path
        return None
    
    def cleanup_old_files(self):
        """Elimina archivos más antiguos que cleanup_hours"""
        now = time.time()
        cutoff = now - (self.cleanup_hours * 3600)
        
        for filename in os.listdir(self.storage_path):
            file_path = os.path.join(self.storage_path, filename)
            if os.path.isfile(file_path):
                file_age = os.path.getmtime(file_path)
                if file_age < cutoff:
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        print(f"Error eliminando {filename}: {e}")
```


### Frontend Components

#### 1. Router Configuration (router/index.js)

```javascript
import { createRouter, createWebHistory } from 'vue-router'
import WelcomeView from '../views/WelcomeView.vue'
import LoginView from '../views/LoginView.vue'
import GeneratorView from '../views/GeneratorView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'welcome',
      component: WelcomeView
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/generator',
      name: 'generator',
      component: GeneratorView,
      meta: { requiresAuth: true }
    }
  ]
})

// Guard para verificar autenticación
router.beforeEach((to, from, next) => {
  const sessionStore = useSessionStore()
  if (to.meta.requiresAuth && !sessionStore.isAuthenticated) {
    next({ name: 'login' })
  } else {
    next()
  }
})

export default router
```

#### 2. Session Store (stores/session.js)

```javascript
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
```

#### 3. API Service (services/api.js)

```javascript
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

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
```

#### 4. Welcome View (views/WelcomeView.vue)

```vue
<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 flex items-center justify-center p-4">
    <div class="max-w-2xl w-full bg-white rounded-2xl shadow-xl p-8 text-center">
      <div class="mb-6">
        <h1 class="text-4xl font-bold text-gray-800 mb-4">
          Generador de Recursos Evangelísticos
        </h1>
        <p class="text-lg text-gray-600 mb-6">
          Crea afiches y gigantografías profesionales para tus campañas evangelísticas
          de forma rápida y sencilla.
        </p>
        <div class="bg-blue-50 rounded-lg p-6 mb-6 text-left">
          <h2 class="text-xl font-semibold text-gray-800 mb-3">¿Qué puedes hacer?</h2>
          <ul class="space-y-2 text-gray-700">
            <li class="flex items-start">
              <span class="text-blue-500 mr-2">✓</span>
              Generar afiches en formato A4 y 4x1
            </li>
            <li class="flex items-start">
              <span class="text-blue-500 mr-2">✓</span>
              Crear gigantografías de 1x1.5 metros listas para impresión
            </li>
            <li class="flex items-start">
              <span class="text-blue-500 mr-2">✓</span>
              Personalizar con fecha, hora, lugar y referencia del evento
            </li>
            <li class="flex items-start">
              <span class="text-blue-500 mr-2">✓</span>
              Descargar archivos PDF de alta calidad
            </li>
          </ul>
        </div>
      </div>
      
      <button
        @click="handleStart"
        class="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-8 rounded-lg 
               transition duration-200 transform hover:scale-105"
      >
        Iniciar
      </button>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const handleStart = () => {
  router.push({ name: 'login' })
}
</script>
```

#### 5. Login View (views/LoginView.vue)

```vue
<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 flex items-center justify-center p-4">
    <div class="max-w-md w-full bg-white rounded-2xl shadow-xl p-8">
      <h2 class="text-2xl font-bold text-gray-800 mb-6 text-center">
        Verificación de Seguridad
      </h2>
      
      <!-- Progress indicator -->
      <div class="mb-6">
        <div class="flex justify-between mb-2">
          <span class="text-sm text-gray-600">Pregunta {{ currentQuestion }} de 3</span>
        </div>
        <div class="w-full bg-gray-200 rounded-full h-2">
          <div 
            class="bg-blue-600 h-2 rounded-full transition-all duration-300"
            :style="{ width: `${(currentQuestion / 3) * 100}%` }"
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
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useSessionStore } from '../stores/session'
import api from '../services/api'

const router = useRouter()
const sessionStore = useSessionStore()

const currentQuestion = ref(1)
const questionText = ref('')
const answer = ref('')
const loading = ref(false)
const errorMessage = ref('')

onMounted(async () => {
  try {
    const response = await api.startSession()
    sessionStore.setSession(response.session_id)
    currentQuestion.value = response.question_number
    questionText.value = response.question_text
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
    }
  } catch (error) {
    errorMessage.value = 'Error al validar respuesta. Por favor, intenta de nuevo.'
  } finally {
    loading.value = false
  }
}
</script>
```

#### 6. Generator View (views/GeneratorView.vue)

```vue
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
    alert('Error al generar documentos. Por favor, intenta de nuevo.')
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
```


## Data Models

### Backend Data Models

#### Session Data

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class SessionData:
    """Representa el estado de una sesión de usuario"""
    session_id: str
    current_question: int  # 1, 2, o 3
    authenticated: bool
    created_at: float  # timestamp
```

#### Event Data

```python
from pydantic import BaseModel, Field

class EventData(BaseModel):
    """Datos del evento para generar documentos"""
    fecha_evento: str = Field(..., min_length=1, description="Fecha del evento")
    hora_evento: str = Field(..., min_length=1, description="Hora del evento")
    lugar_evento: str = Field(..., min_length=1, description="Lugar del evento")
    referencia_evento: str = Field(default="", description="Referencia opcional del evento")
    nombre_proyecto: str = Field(..., min_length=1, description="Nombre del proyecto para archivos")
```

#### Document Metadata

```python
from enum import Enum

class DocumentType(str, Enum):
    A4 = "a4"
    FORMAT_4X1 = "4x1"
    GIGANTOGRAFIA = "gigantografia"

class DocumentStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"

@dataclass
class DocumentMetadata:
    """Metadatos de un documento generado"""
    type: DocumentType
    filename: str
    status: DocumentStatus
    message: Optional[str] = None
    file_size: Optional[int] = None
    created_at: float = None
```

### Frontend Data Models

#### Form State

```typescript
interface EventFormData {
  fecha_evento: string
  hora_evento: string
  lugar_evento: string
  referencia_evento: string
  nombre_proyecto: string
}
```

#### Session State

```typescript
interface SessionState {
  sessionId: string | null
  authenticated: boolean
}
```

#### Generated Document

```typescript
interface GeneratedDocument {
  type: 'a4' | '4x1' | 'gigantografia'
  filename: string
  status: 'success' | 'error'
  message?: string
}
```

### Database Schema

Para esta aplicación, no se requiere una base de datos persistente. Los datos de sesión se mantienen en memoria en el backend (diccionario Python). Para una implementación en producción, se podría considerar:

- Redis para almacenamiento de sesiones
- PostgreSQL para logs de generación y auditoría
- S3 o almacenamiento en nube para archivos generados

### File Naming Convention

Los archivos generados siguen esta convención:

```
{nombre_proyecto}_{tipo}.{extension}

Ejemplos:
- Campaña_Navidad_2024_a4.pdf
- Campaña_Navidad_2024_4x1.pdf
- Campaña_Navidad_2024_gigantografia.pdf
```

### Template Field Markers

Las plantillas Word deben contener estos marcadores:

```
{{fecha_evento}}      - Reemplazado con la fecha del evento
{{hora_evento}}       - Reemplazado con la hora del evento
{{lugar_evento}}      - Reemplazado con el lugar del evento
{{referencia_evento}} - Reemplazado con la referencia (o vacío si no se proporciona)
```


## Correctness Properties

*Una propiedad es una característica o comportamiento que debe mantenerse verdadero en todas las ejecuciones válidas de un sistema - esencialmente, una declaración formal sobre lo que el sistema debe hacer. Las propiedades sirven como puente entre las especificaciones legibles por humanos y las garantías de corrección verificables por máquina.*

### Authentication Properties

Property 1: Session ID Uniqueness
*For any* número de sesiones iniciadas, todos los Session_IDs generados deben ser únicos entre sí
**Validates: Requirements 1.1, 2.1**

Property 2: Text Normalization Consistency
*For any* string de entrada, la normalización debe producir un resultado en minúsculas, sin espacios extras al inicio/final, sin espacios múltiples consecutivos, y sin caracteres de puntuación
**Validates: Requirements 1.3**

Property 3: Correct Answer Progression
*For any* sesión válida y respuesta correcta en las preguntas 1 o 2, el sistema debe avanzar al siguiente número de pregunta
**Validates: Requirements 1.4**

Property 4: Incorrect Answer Reset
*For any* sesión válida y respuesta incorrecta en cualquier pregunta, el sistema debe reiniciar a la pregunta 1
**Validates: Requirements 1.5**

Property 5: Authentication Completion
*For any* sesión que ha respondido correctamente las 3 preguntas en secuencia, el estado de autenticación debe ser True
**Validates: Requirements 1.6**

Property 6: Session State Persistence
*For any* Session_ID válido, debe ser posible recuperar su estado de autenticación y pregunta actual
**Validates: Requirements 2.2**

Property 7: Invalid Session Rejection
*For any* Session_ID que no existe en el sistema, intentar validar una respuesta debe producir un error
**Validates: Requirements 2.3**

Property 8: Unauthenticated Generation Rejection
*For any* Session_ID que no está autenticado, intentar generar documentos debe producir un error de autorización
**Validates: Requirements 2.4**

### Template Processing Properties

Property 9: Template Field Replacement
*For any* conjunto de parámetros de evento válidos, todos los marcadores ({{fecha_evento}}, {{hora_evento}}, {{lugar_evento}}, {{referencia_evento}}) en el documento procesado deben ser reemplazados con los valores correspondientes
**Validates: Requirements 3.2**

Property 10: Optional Field Handling
*For any* documento procesado donde referencia_evento es una cadena vacía, el marcador {{referencia_evento}} debe ser reemplazado con una cadena vacía sin producir errores
**Validates: Requirements 3.4**

Property 11: Required Fields Validation
*For any* solicitud de generación que omite uno o más campos obligatorios (fecha_evento, hora_evento, lugar_evento), el sistema debe rechazar la solicitud con un error de validación
**Validates: Requirements 3.5**

### Document Generation Properties

Property 12: Three Document Generation
*For any* solicitud de generación válida, el sistema debe crear exactamente 3 archivos PDF: uno tipo A4, uno tipo 4x1, y uno tipo gigantografía
**Validates: Requirements 4.1, 4.2, 4.3**

Property 13: CMYK Color Mode
*For any* gigantografía generada, el archivo PDF debe estar en modo de color CMYK
**Validates: Requirements 4.4**

Property 14: Filename Convention
*For any* documento generado con nombre_proyecto "X" y tipo "T", el nombre del archivo debe seguir el patrón "X_T.pdf"
**Validates: Requirements 4.5**

Property 15: Generation Response Completeness
*For any* respuesta de generación exitosa, debe contener exactamente 3 objetos DocumentInfo con sus campos type, filename y status poblados
**Validates: Requirements 4.6**

Property 16: Temporary Storage
*For any* conjunto de documentos generados, todos los archivos deben existir en el directorio temporal inmediatamente después de la generación
**Validates: Requirements 4.7**

### Download Properties

Property 17: Nonexistent File Error
*For any* nombre de archivo que no existe en el almacenamiento temporal, solicitar su descarga debe retornar un error 404
**Validates: Requirements 5.2, 5.5**

Property 18: PDF Content Type
*For any* archivo PDF existente solicitado para descarga, la respuesta HTTP debe tener Content-Type "application/pdf"
**Validates: Requirements 5.3, 5.4**

### API Properties

Property 19: HTTP Error Codes
*For any* tipo de error (validación, autenticación, no encontrado, servidor), el sistema debe retornar el código de estado HTTP apropiado (400, 401, 404, 500 respectivamente)
**Validates: Requirements 6.5**

Property 20: JSON Response Format
*For any* endpoint excepto /api/download/*, la respuesta debe tener Content-Type "application/json"
**Validates: Requirements 6.6**

### Frontend Navigation Properties

Property 21: Welcome to Login Navigation
*For any* estado inicial en la vista de bienvenida, hacer clic en el botón "Iniciar" debe cambiar la ruta a /login
**Validates: Requirements 7.4**

Property 22: Session Initialization on Login
*For any* carga de la vista de login, debe realizarse una llamada al endpoint /api/auth/start-session
**Validates: Requirements 8.1**

Property 23: Sequential Question Display
*For any* estado de la vista de login, solo debe ser visible un campo de pregunta a la vez
**Validates: Requirements 8.2**

Property 24: Answer Validation API Call
*For any* envío de respuesta en la vista de login, debe realizarse una llamada al endpoint /api/auth/validate-answer con los parámetros correctos
**Validates: Requirements 8.3**

Property 25: Correct Answer UI Progression
*For any* respuesta correcta en las preguntas 1 o 2, el número de pregunta mostrado en la UI debe incrementar
**Validates: Requirements 8.4**

Property 26: Incorrect Answer UI Reset
*For any* respuesta incorrecta, la UI debe mostrar un mensaje de error y reiniciar a la pregunta 1
**Validates: Requirements 8.5**

Property 27: Login to Generator Navigation
*For any* estado donde las 3 preguntas han sido respondidas correctamente, la aplicación debe navegar a la ruta /generator
**Validates: Requirements 8.6**

### Generator View Properties

Property 28: Required Fields Validation
*For any* estado del formulario donde uno o más campos obligatorios están vacíos, el botón de generar debe estar deshabilitado o la validación debe prevenir el envío
**Validates: Requirements 9.3**

Property 29: Generation API Call
*For any* clic en el botón "Generar" con formulario válido, debe realizarse una llamada al endpoint /api/generate con todos los parámetros del formulario
**Validates: Requirements 9.4**

Property 30: Preview Display on Success
*For any* respuesta exitosa de generación, el elemento de previsualización debe volverse visible y mostrar el PDF A4
**Validates: Requirements 9.5**

Property 31: Initial Preview Hidden
*For any* estado inicial de la vista de generación (antes de generar), el área de previsualización debe estar oculta
**Validates: Requirements 9.6**

Property 32: Loading Indicator Display
*For any* operación de generación en curso, debe ser visible un indicador de carga en la UI
**Validates: Requirements 9.7**

Property 33: Download Button Click
*For any* clic en un botón de descarga con un filename válido, debe abrirse la URL /api/download/{filename}
**Validates: Requirements 10.3**

Property 34: Initial Download Buttons Disabled
*For any* estado inicial de la vista de generación (antes de generar), los botones de descarga deben estar deshabilitados
**Validates: Requirements 10.5**

### File Management Properties

Property 35: Temporary Directory Storage
*For any* archivo generado, debe ser almacenado en el directorio temporal configurado
**Validates: Requirements 12.1**

Property 36: Old File Cleanup
*For any* archivo en el directorio temporal con antigüedad mayor al threshold configurado, debe ser eliminado por el mecanismo de limpieza
**Validates: Requirements 12.3**

Property 37: File I/O Error Handling
*For any* error de lectura o escritura de archivos, el sistema debe capturar la excepción y retornar una respuesta de error apropiada sin crashear
**Validates: Requirements 12.5**


## Error Handling

### Backend Error Handling Strategy

#### 1. Authentication Errors

```python
class AuthenticationError(Exception):
    """Raised when authentication fails"""
    pass

class InvalidSessionError(Exception):
    """Raised when session ID is invalid"""
    pass

# Manejo en endpoints
@app.post("/api/auth/validate-answer")
async def validate_answer(request: ValidateAnswerRequest):
    try:
        result = auth_service.validate_answer(
            request.session_id,
            request.question_number,
            request.answer
        )
        return ValidationResponse(**result)
    except InvalidSessionError:
        raise HTTPException(status_code=401, detail="Sesión inválida")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error interno del servidor")
```

#### 2. Validation Errors

FastAPI maneja automáticamente la validación de Pydantic models y retorna 422 para datos inválidos. Para validaciones personalizadas:

```python
@app.post("/api/generate")
async def generate_documents(request: GenerateRequest):
    # Verificar autenticación
    if not auth_service.is_authenticated(request.session_id):
        raise HTTPException(status_code=401, detail="Sesión no autenticada")
    
    # Validar campos obligatorios (Pydantic ya lo hace, pero ejemplo adicional)
    if not request.nombre_proyecto.strip():
        raise HTTPException(status_code=400, detail="nombre_proyecto no puede estar vacío")
    
    try:
        results = document_generator.generate_all(
            {
                "fecha_evento": request.fecha_evento,
                "hora_evento": request.hora_evento,
                "lugar_evento": request.lugar_evento,
                "referencia_evento": request.referencia_evento
            },
            request.nombre_proyecto
        )
        return GenerateResponse(success=True, documents=results)
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=f"Plantilla no encontrada: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando documentos: {str(e)}")
```

#### 3. File Not Found Errors

```python
@app.get("/api/download/{filename}")
async def download_file(filename: str):
    file_path = file_service.get_file_path(filename)
    
    if not file_path:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    
    try:
        return FileResponse(
            path=file_path,
            media_type="application/pdf",
            filename=filename
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al descargar archivo")
```

#### 4. Document Generation Errors

Los errores en generación individual de documentos no deben fallar toda la operación:

```python
def generate_all(self, data: Dict[str, str], project_name: str) -> List[Dict]:
    results = []
    
    # Cada tipo de documento se genera independientemente
    for doc_type, generator_method in [
        ("a4", self._generate_a4),
        ("4x1", self._generate_4x1),
        ("gigantografia", self._generate_gigantografia)
    ]:
        try:
            filename = generator_method(data, project_name)
            results.append({
                "type": doc_type,
                "filename": filename,
                "status": "success"
            })
        except Exception as e:
            results.append({
                "type": doc_type,
                "filename": "",
                "status": "error",
                "message": str(e)
            })
    
    return results
```

### Frontend Error Handling Strategy

#### 1. API Call Errors

```javascript
// En api.js
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
```

#### 2. Component Error Handling

```javascript
// En LoginView.vue
const handleSubmit = async () => {
  loading.value = true
  errorMessage.value = ''
  
  try {
    const response = await api.validateAnswer(
      sessionStore.sessionId,
      currentQuestion.value,
      answer.value
    )
    
    // Manejar respuesta exitosa...
  } catch (error) {
    errorMessage.value = error.message || 'Error al validar respuesta. Por favor, intenta de nuevo.'
  } finally {
    loading.value = false
  }
}
```

#### 3. Network Errors

```javascript
// En GeneratorView.vue
const handleGenerate = async () => {
  generating.value = true
  
  try {
    const response = await api.generateDocuments(
      sessionStore.sessionId,
      formData.value
    )
    
    if (response.success) {
      // Verificar si algún documento falló
      const failedDocs = response.documents.filter(doc => doc.status === 'error')
      if (failedDocs.length > 0) {
        const failedTypes = failedDocs.map(doc => doc.type).join(', ')
        alert(`Advertencia: No se pudieron generar algunos documentos: ${failedTypes}`)
      }
      
      generatedDocuments.value = response.documents
      // Mostrar previsualización...
    }
  } catch (error) {
    alert(error.message || 'Error al generar documentos. Por favor, intenta de nuevo.')
  } finally {
    generating.value = false
  }
}
```

### Error Response Format

Todos los errores del backend siguen este formato JSON:

```json
{
  "detail": "Mensaje de error descriptivo"
}
```

### Logging Strategy

```python
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Usar en el código
try:
    doc.save(output_path)
    logger.info(f"Documento guardado exitosamente: {output_path}")
except Exception as e:
    logger.error(f"Error guardando documento: {str(e)}", exc_info=True)
    raise
```

## Testing Strategy

### Dual Testing Approach

Este proyecto requiere tanto pruebas unitarias como pruebas basadas en propiedades para garantizar corrección completa:

- **Pruebas unitarias**: Verifican ejemplos específicos, casos edge y condiciones de error
- **Pruebas de propiedades**: Verifican propiedades universales a través de múltiples entradas generadas

Ambos tipos de pruebas son complementarios y necesarios para cobertura integral.

### Backend Testing

#### Property-Based Testing Library

Usaremos **Hypothesis** para Python, la biblioteca estándar para property-based testing.

```bash
pip install hypothesis pytest
```

#### Test Configuration

Cada prueba de propiedad debe ejecutarse con mínimo 100 iteraciones:

```python
from hypothesis import given, settings
import hypothesis.strategies as st

@settings(max_examples=100)
@given(st.text())
def test_property(input_text):
    # Feature: generador-recursos-evangelisticos, Property 2: Text Normalization Consistency
    result = normalize_text(input_text)
    assert result == result.lower()
    assert result == result.strip()
```

#### Unit Tests Structure

```
tests/
├── test_auth_service.py
├── test_template_processor.py
├── test_document_generator.py
├── test_file_service.py
└── test_api_endpoints.py
```

#### Example Unit Tests

```python
# tests/test_auth_service.py
import pytest
from services.auth_service import AuthService

def test_create_session_returns_unique_id():
    """Ejemplo específico de creación de sesión"""
    auth_service = AuthService()
    session_id, question = auth_service.create_session()
    
    assert session_id is not None
    assert len(session_id) > 0
    assert question["number"] == 1

def test_normalize_text_removes_punctuation():
    """Caso edge: texto con puntuación"""
    auth_service = AuthService()
    result = auth_service._normalize_text("¡Hola, Mundo!")
    assert result == "hola mundo"

def test_validate_answer_with_invalid_session():
    """Condición de error: sesión inválida"""
    auth_service = AuthService()
    
    with pytest.raises(ValueError, match="Sesión inválida"):
        auth_service.validate_answer("invalid-id", 1, "answer")
```

#### Example Property Tests

```python
# tests/test_auth_properties.py
from hypothesis import given, settings
import hypothesis.strategies as st
from services.auth_service import AuthService

@settings(max_examples=100)
@given(st.integers(min_value=1, max_value=10))
def test_session_id_uniqueness(num_sessions):
    """
    Feature: generador-recursos-evangelisticos, Property 1: Session ID Uniqueness
    For any número de sesiones iniciadas, todos los Session_IDs generados deben ser únicos
    """
    auth_service = AuthService()
    session_ids = set()
    
    for _ in range(num_sessions):
        session_id, _ = auth_service.create_session()
        session_ids.add(session_id)
    
    assert len(session_ids) == num_sessions

@settings(max_examples=100)
@given(st.text())
def test_text_normalization_consistency(input_text):
    """
    Feature: generador-recursos-evangelisticos, Property 2: Text Normalization Consistency
    For any string de entrada, la normalización debe producir resultado consistente
    """
    auth_service = AuthService()
    result = auth_service._normalize_text(input_text)
    
    # Verificar lowercase
    assert result == result.lower()
    # Verificar sin espacios al inicio/final
    assert result == result.strip()
    # Verificar sin espacios múltiples
    assert '  ' not in result
    # Verificar sin puntuación
    import re
    assert not re.search(r'[^\w\s]', result)

@settings(max_examples=100)
@given(
    st.integers(min_value=1, max_value=2),
    st.text(min_size=1)
)
def test_correct_answer_progression(question_num, answer):
    """
    Feature: generador-recursos-evangelisticos, Property 3: Correct Answer Progression
    For any sesión válida y respuesta correcta en preguntas 1 o 2, debe avanzar
    """
    auth_service = AuthService()
    session_id, _ = auth_service.create_session()
    
    # Configurar respuesta correcta
    correct_answer = auth_service.security_questions[question_num - 1]["answer"]
    
    # Avanzar a la pregunta deseada
    for i in range(1, question_num):
        auth_service.sessions[session_id].current_question = i
        auth_service.validate_answer(
            session_id, 
            i, 
            auth_service.security_questions[i - 1]["answer"]
        )
    
    # Validar respuesta correcta
    result = auth_service.validate_answer(session_id, question_num, correct_answer)
    
    assert result["success"] == True
    if question_num < 3:
        assert result["next_question"] == question_num + 1
```

#### Integration Tests

```python
# tests/test_integration.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_full_authentication_flow():
    """Prueba de integración: flujo completo de autenticación"""
    # Iniciar sesión
    response = client.post("/api/auth/start-session")
    assert response.status_code == 200
    session_id = response.json()["session_id"]
    
    # Responder preguntas correctamente
    questions_answers = [
        (1, "iglesia central"),
        (2, "lima"),
        (3, "esperanza viva")
    ]
    
    for q_num, answer in questions_answers:
        response = client.post("/api/auth/validate-answer", json={
            "session_id": session_id,
            "question_number": q_num,
            "answer": answer
        })
        assert response.status_code == 200
        result = response.json()
        assert result["success"] == True
    
    # Verificar que puede generar documentos
    response = client.post("/api/generate", json={
        "session_id": session_id,
        "fecha_evento": "15 de Diciembre",
        "hora_evento": "7:00 PM",
        "lugar_evento": "Auditorio Central",
        "referencia_evento": "",
        "nombre_proyecto": "test_project"
    })
    assert response.status_code == 200
    assert response.json()["success"] == True
```

### Frontend Testing

#### Testing Library

Usaremos **Vitest** y **Vue Test Utils** para testing de componentes Vue.

```bash
npm install -D vitest @vue/test-utils jsdom
```

#### Test Configuration

```javascript
// vitest.config.js
import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  test: {
    environment: 'jsdom',
    globals: true
  }
})
```

#### Component Tests Structure

```
tests/
├── unit/
│   ├── WelcomeView.spec.js
│   ├── LoginView.spec.js
│   └── GeneratorView.spec.js
└── integration/
    └── navigation.spec.js
```

#### Example Component Tests

```javascript
// tests/unit/LoginView.spec.js
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import LoginView from '@/views/LoginView.vue'
import api from '@/services/api'

vi.mock('@/services/api')

describe('LoginView', () => {
  let wrapper
  let pinia
  
  beforeEach(() => {
    pinia = createPinia()
    api.startSession.mockResolvedValue({
      session_id: 'test-session-id',
      question_number: 1,
      question_text: '¿Cuál es el nombre de tu iglesia?'
    })
    
    wrapper = mount(LoginView, {
      global: {
        plugins: [pinia]
      }
    })
  })
  
  it('should display question text', async () => {
    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('¿Cuál es el nombre de tu iglesia?')
  })
  
  it('should call API on submit', async () => {
    api.validateAnswer.mockResolvedValue({
      success: true,
      next_question: 2,
      question_text: '¿En qué ciudad se realizará el evento?'
    })
    
    await wrapper.vm.$nextTick()
    const input = wrapper.find('input[type="text"]')
    await input.setValue('iglesia central')
    
    const form = wrapper.find('form')
    await form.trigger('submit')
    
    expect(api.validateAnswer).toHaveBeenCalledWith(
      'test-session-id',
      1,
      'iglesia central'
    )
  })
})
```

### Test Coverage Goals

- Backend: Mínimo 80% de cobertura de código
- Frontend: Mínimo 70% de cobertura de componentes
- Todas las propiedades de corrección deben tener pruebas de propiedad correspondientes
- Todos los casos edge identificados deben tener pruebas unitarias

### Running Tests

```bash
# Backend
pytest tests/ -v --cov=services --cov=main

# Frontend
npm run test:unit
npm run test:coverage
```

### Continuous Integration

Los tests deben ejecutarse automáticamente en CI/CD:

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest hypothesis pytest-cov
      - name: Run tests
        run: pytest tests/ -v --cov=services --cov=main
  
  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Node
        uses: actions/setup-node@v2
        with:
          node-version: '18'
      - name: Install dependencies
        run: npm ci
      - name: Run tests
        run: npm run test:unit
```
