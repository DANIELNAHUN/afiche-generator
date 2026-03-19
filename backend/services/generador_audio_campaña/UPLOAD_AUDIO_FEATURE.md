# Funcionalidad de Subida de Audio para Campaña

## Descripción

Esta funcionalidad permite a los usuarios subir un archivo MP3 personalizado que será utilizado como el audio de "Hora y lugar del evento" en la generación del audio de campaña completo.

## Flujo de Trabajo

1. **Usuario hace clic en "Generar Audio"** en el frontend
2. **Se abre un modal** donde el usuario puede:
   - Arrastrar y soltar un archivo MP3
   - Seleccionar un archivo MP3 desde su computadora
3. **El archivo se sube al servidor** y reemplaza temporalmente el archivo `Gran Campaña - Hora y lugar del evento.mp3`
4. **Se procesa el audio de campaña** combinando todos los archivos de audio
5. **Se genera el audio final** listo para descargar

## Endpoints Nuevos

### POST `/api/audio/upload-event-audio`

Sube un archivo MP3 para el audio del evento.

**Request:**
- `session_id` (form): ID de sesión autenticada
- `file` (file): Archivo MP3 a subir

**Response:**
```json
{
  "success": true,
  "filename": "Gran Campaña - Hora y lugar del evento.mp3",
  "message": "Archivo de audio subido exitosamente"
}
```

### POST `/api/audio/process-campaign`

Procesa el audio de campaña completo usando el archivo subido.

**Request:**
```json
{
  "session_id": "session-id-here"
}
```

**Response:**
```json
{
  "success": true,
  "output_file": "temp_files/Gran_Campana_Final.mp3",
  "duration_seconds": 45.5,
  "warnings": []
}
```

## Cambios en el Backend

### `backend/audio_endpoints.py`
- Agregado endpoint `upload_event_audio` para subir archivos MP3
- Importado `Form` de FastAPI para manejar form data
- Agregado modelo `UploadEventAudioResponse`

### `backend/services/audio_campaign_service.py`
- Agregado método `save_event_audio()` para guardar archivos subidos
- Agregado atributo `uploaded_event_audio_filename` para el nombre del archivo
- El archivo subido reemplaza el archivo existente en la carpeta de audio

## Cambios en el Frontend

### `frontend/src/views/GeneratorView.vue`
- Agregado botón "Generar Audio" debajo del botón "Generar"
- Agregado modal con área de drag & drop para subir archivos MP3
- Agregadas funciones para manejar la subida y procesamiento de audio
- Agregados estados para controlar el modal y el progreso

### `frontend/src/services/api.js`
- Agregado método `uploadEventAudio()` para subir archivos
- Agregado método `processCampaignAudio()` para procesar el audio

## Uso

1. Completa el formulario con los datos del evento
2. Haz clic en "Generar Audio"
3. Sube tu archivo MP3 con la información de hora y lugar
4. Espera a que se procese el audio
5. El audio final se guardará en `temp_files/Gran_Campana_Final.mp3`

## Notas Técnicas

- El archivo subido reemplaza el archivo existente cada vez
- Los archivos se almacenan en `backend/services/generador_audio_campaña/files/`
- El procesamiento combina el archivo subido con los otros archivos de audio predefinidos
- El audio final se exporta a la carpeta `temp_files`
