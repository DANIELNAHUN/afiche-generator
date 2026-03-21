# Generador de Recursos Evangelísticos

Sistema web full-stack para la generación automática de recursos publicitarios (afiches, gigantografías y audios) para campañas evangelísticas.

## Características

- ✅ Autenticación mediante cuestionario de seguridad
- ✅ Generación de afiches en formato A4 y 4x1
- ✅ Creación de gigantografías de 1x1.5 metros en modo CMYK
- ✅ Personalización con datos del evento
- ✅ Descarga individual de documentos PDF
- ✅ Generación de audio de campaña con dos versiones: **HOY** y **ESTE**
- ✅ Guiones de locutor generados automáticamente desde los datos del evento
- ✅ Subida de archivos MP3 del locutor (versión HOY y ESTE) vía drag & drop
- ✅ Combinación de audio locutor con música de fondo usando FFmpeg/pydub
- ✅ Integración con ElevenLabs TTS (opcional)
- ✅ Limpieza automática de archivos temporales (diaria a las 2:00 AM)
- ✅ Persistencia de sesión y formulario en localStorage

## Requisitos del Sistema

### Backend
- Python 3.10 o superior
- LibreOffice (para conversión de DOCX a PDF)
- FFmpeg (para procesamiento de audio)
- pip (gestor de paquetes de Python)

### Frontend
- Node.js 18 o superior
- npm (incluido con Node.js)

### Instalación de LibreOffice

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install libreoffice
```

**macOS:**
```bash
brew install --cask libreoffice
```

**Windows:**
Descargar e instalar desde [https://www.libreoffice.org/download/download/](https://www.libreoffice.org/download/download/)

### Instalación de FFmpeg

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
Descargar desde [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html) y agregar al PATH del sistema.

## Instalación

### Inicio Rápido (Quick Start)

**Linux/macOS:**
```bash
chmod +x setup.sh
./setup.sh
```

**Windows:**
```bash
setup.bat
```

### Instalación Manual

```bash
git clone <repository-url>
cd generador-recursos-evangelisticos
```

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

**Frontend:**
```bash
cd frontend
npm install
cp .env.example .env
```

## Ejecución

```bash
# Backend
cd backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Frontend (otra terminal)
cd frontend
npm run dev
```

- Backend: `http://localhost:8000`
- Frontend: `http://localhost:5173`

## Estructura del Proyecto

```
.
├── backend/
│   ├── services/
│   │   ├── generador_audio_campaña/   # Motor de generación de audio
│   │   │   ├── src/                   # Módulos de procesamiento
│   │   │   │   ├── audio_processor.py
│   │   │   │   ├── audio_combiner.py
│   │   │   │   ├── elevenlabs_generator.py
│   │   │   │   ├── locutor_processor.py
│   │   │   │   ├── background_music_processor.py
│   │   │   │   └── models.py
│   │   │   └── files/                 # Archivos de audio base (música, intro, cierre)
│   │   ├── audio_campaign_service.py  # Servicio de audio integrado al backend
│   │   ├── auth_service.py
│   │   ├── document_generator.py
│   │   ├── file_service.py
│   │   └── template_processor.py
│   ├── audio_endpoints.py             # Endpoints de audio (FastAPI)
│   ├── templates/                     # Plantillas Word (.docx)
│   ├── tests/
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── views/
│       │   ├── GeneratorView.vue      # Vista principal con modal de audio
│       │   ├── LoginView.vue
│       │   └── WelcomeView.vue
│       ├── stores/session.js
│       ├── services/api.js
│       └── router/
└── temp_files/                        # Archivos generados temporalmente
```

## Uso de la Aplicación

### Flujo Completo

1. **Bienvenida**: Clic en "Iniciar"

2. **Autenticación**: Responder 3 preguntas de seguridad secuencialmente. Si una respuesta es incorrecta, el cuestionario se reinicia desde la pregunta 1.

3. **Generación de Afiches**:
   - Ingresar fecha, hora, lugar, referencia (opcional) y nombre del proyecto
   - Clic en "Generar Afiche"
   - Descargar A4, 4x1 o Gigantografía

4. **Generación de Audio** (nuevo flujo):
   - Clic en "Generar Audio" (mismo formulario)
   - El modal muestra los guiones **HOY** y **ESTE** generados automáticamente con los datos del evento
   - Copiar el guión y grabarlo con ElevenLabs (voz recomendada: *Cesar Rodriguez*)
   - Subir los dos MP3 resultantes (versión HOY y versión ESTE) vía drag & drop o selector
   - Clic en "Generar Audio" para combinar con la música de fondo
   - Descargar los audios finales desde la sección de resultados

### Formato de los guiones de audio

El modal genera automáticamente los textos para locutor basándose en los datos del formulario:

- **HOY**: `HOY [FECHA].. DESDE LAS [HORA EN PALABRAS].. EN LA [LUGAR].. AL COSTADO DE [REFERENCIA]...`
- **ESTE**: `ESTE [FECHA].. DESDE LAS [HORA EN PALABRAS].. EN LA [LUGAR].. AL COSTADO DE [REFERENCIA]...`

La hora se convierte automáticamente a palabras (ej: `5:30 PM` → `CINCO Y TREINTA DE LA TARDE`).

## Variables de Entorno

### Backend (`backend/.env`)

```env
PORT=8000
HOST=0.0.0.0
TEMP_STORAGE_PATH=../temp_files
CLEANUP_HOURS=24
FRONTEND_URL=http://localhost:5173
LOG_LEVEL=INFO
TEMPLATE_DIR=templates
TEMPLATE_A4=Formato a4.docx
TEMPLATE_4X1=Formato 4x1.docx

# Preguntas de seguridad (cambiar en producción)
SECURITY_QUESTION_1=¿Cuál es el nombre de tu iglesia?
SECURITY_ANSWER_1=iglesia central
SECURITY_QUESTION_2=¿En qué ciudad se realizará el evento?
SECURITY_ANSWER_2=lima
SECURITY_QUESTION_3=¿Cuál es el tema de la campaña?
SECURITY_ANSWER_3=esperanza viva

# ElevenLabs (opcional, para TTS automático)
ELEVEN_API_KEY=your_api_key_here
ELEVEN_VOICE_ID=JBFqnCBsd6RMkjVDRZzb
```

### Frontend (`frontend/.env`)

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_TITLE=Generador de Recursos Evangelísticos
VITE_API_TIMEOUT=30000
```

## API Endpoints

### Autenticación
- `POST /api/auth/start-session` — Iniciar sesión
- `POST /api/auth/validate-answer` — Validar respuesta de pregunta

### Documentos
- `POST /api/generate` — Generar PDFs
- `GET /api/preview/{filename}` — Previsualizar PDF en el navegador
- `GET /api/download/{filename}` — Descargar archivo

### Audio
- `POST /api/audio/upload-event-audio` — Subir MP3 del locutor (HOY + ESTE)
- `POST /api/audio/process-campaign` — Combinar locutor con música de fondo → genera `Gran_Campana_Final_HOY.mp3` y `Gran_Campana_Final_ESTE.mp3`
- `POST /api/audio/generate-tts` — Generar TTS automático con ElevenLabs (requiere API key)
- `GET /api/audio/test-connection` — Verificar conexión con ElevenLabs

## Plantillas Word

Las plantillas en `backend/templates/` deben contener los marcadores:

- `{{fecha_evento}}` — Fecha del evento
- `{{hora_evento}}` — Hora del evento
- `{{lugar_evento}}` — Lugar del evento
- `{{referencia_evento}}` — Referencia opcional

## Ejecutar Tests

```bash
# Backend
cd backend
source venv/bin/activate
pytest

# Con cobertura
pytest --cov=services --cov=main --cov-report=html

# Por tipo
pytest -m unit
pytest -m property

# Integración (desde raíz)
python test_integration.py
```

## Tecnologías Utilizadas

### Backend
- FastAPI — Framework web asíncrono
- python-docx — Manipulación de archivos Word
- pydub + FFmpeg — Procesamiento y combinación de audio
- elevenlabs — Cliente API TTS (opcional)
- APScheduler — Limpieza automática de archivos temporales
- Pillow, pdf2image, reportlab — Procesamiento de imágenes y PDFs
- pytest + Hypothesis — Testing unitario y de propiedades

### Frontend
- Vue.js 3 — Framework reactivo
- Vue Router + Pinia — Navegación y estado
- Axios — Cliente HTTP
- Tailwind CSS — Estilos

## Solución de Problemas

**LibreOffice no encontrado:**
```bash
which libreoffice  # Linux/macOS
```
Agregar al PATH si es necesario: `/usr/bin/libreoffice` (Linux), `/Applications/LibreOffice.app/Contents/MacOS/soffice` (macOS)

**Puerto ya en uso:**
```bash
uvicorn main:app --reload --port 8001
npm run dev -- --port 5174
```

**Error al procesar audio:**
- Verificar que FFmpeg esté instalado: `ffmpeg -version`
- Confirmar que los archivos base existen en `backend/services/generador_audio_campaña/files/`
- Los MP3 subidos deben ser archivos válidos

**Error de CORS:**
- Verificar que `FRONTEND_URL` en `backend/.env` coincida con la URL del frontend

## Licencia

Uso interno para campañas evangelísticas.
