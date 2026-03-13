# Integración del Generador de Audio de Campaña

## Resumen de Cambios

El generador de audio de campaña ha sido integrado al backend principal con las siguientes adaptaciones:

### 1. Estructura de Archivos

- **Archivos de entrada**: `backend/services/generador_audio_campaña/files/`
  - Archivos de locutor (Gran Campaña - *.mp3/wav)
  - Fondos musicales (Yo tengo un amigo que me ama.mp3, Eres todo poderoso.mp3)

- **Archivos de salida**: `temp_files/` (carpeta compartida con el resto del backend)
  - Audios TTS generados
  - Audios procesados finales

### 2. Nuevos Servicios

#### AudioCampaignService (`backend/services/audio_campaign_service.py`)
Servicio wrapper que integra la funcionalidad de generación de audio con el backend:
- `generate_tts_audio()`: Genera audio TTS usando ElevenLabs
- `process_campaign_audio()`: Procesa y combina archivos de audio
- `test_elevenlabs_connection()`: Prueba la conexión con la API

### 3. Nuevos Endpoints

Los endpoints están definidos en `backend/audio_endpoints.py`:

#### POST `/api/audio/generate-tts`
Genera audio TTS para anuncios de campaña.

**Request:**
```json
{
  "session_id": "string",
  "fecha": "DOMINGO 15 DE MARZO",
  "hora": "5:30 PM",
  "lugar": "PLAZA DE LA BANDERA",
  "referencia": "CERCA AL OVALO",
  "version": "both"  // "este", "hoy", o "both"
}
```

**Response:**
```json
{
  "success": true,
  "files": {
    "este": "temp_files/campaign_este_domingo_15_de_marzo.mp3",
    "hoy": "temp_files/campaign_today_domingo_15_de_marzo.mp3"
  },
  "message": "Audio TTS generado exitosamente"
}
```

#### POST `/api/audio/process-campaign`
Procesa audio de campaña combinando archivos de locutor con música de fondo.

**Request:**
```json
{
  "session_id": "string"
}
```

**Response:**
```json
{
  "success": true,
  "output_file": "temp_files/Gran_Campana_Final.mp3",
  "duration_seconds": 120.5,
  "warnings": []
}
```

#### GET `/api/audio/test-connection`
Prueba la conexión con ElevenLabs API (no requiere autenticación).

**Response:**
```json
{
  "success": true,
  "message": "Conexión exitosa con ElevenLabs API"
}
```

### 4. Variables de Entorno

Agregar al archivo `.env`:

```env
# ElevenLabs API Configuration
ELEVEN_API_KEY=your_elevenlabs_api_key_here
ELEVEN_VOICE_ID=JBFqnCBsd6RMkjVDRZzb
```

### 5. Dependencias Nuevas

Agregadas a `requirements.txt`:
- `pydub`: Procesamiento de audio
- `elevenlabs`: Cliente de la API de ElevenLabs

**Nota**: También requiere FFmpeg instalado en el sistema.

### 6. Uso desde CLI

Los scripts originales siguen funcionando:

```bash
# Generar audio TTS
cd backend/services/generador_audio_campaña
python generate_campaign_audio.py -f "DOMINGO 15 DE MARZO" -t "5:30 PM" -l "PLAZA" -r "CERCA AL OVALO"

# Procesar audio completo
python main.py
```

### 7. Autenticación

Todos los endpoints de generación requieren un `session_id` autenticado, igual que los endpoints de generación de documentos.

## Instalación

1. Instalar dependencias:
```bash
cd backend
pip install -r requirements.txt
```

2. Instalar FFmpeg:
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg
```

3. Configurar variables de entorno en `.env`

4. Reiniciar el servidor FastAPI
