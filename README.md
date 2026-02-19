# Generador de Recursos Evangelísticos

Sistema web full-stack para la generación automática de recursos publicitarios (afiches y gigantografías) en formato PDF para campañas evangelísticas.

## Características

- ✅ Autenticación mediante cuestionario de seguridad
- ✅ Generación de afiches en formato A4 y 4x1
- ✅ Creación de gigantografías de 1x1.5 metros en modo CMYK
- ✅ Personalización con datos del evento
- ✅ Descarga individual de documentos PDF

## Requisitos del Sistema

### Backend
- Python 3.10 o superior
- LibreOffice (para conversión de DOCX a PDF)
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

## Instalación

### Inicio Rápido (Quick Start)

Para usuarios que quieren comenzar rápidamente, hay scripts de configuración automática:

**Linux/macOS:**
```bash
chmod +x setup.sh
./setup.sh
```

**Windows:**
```bash
setup.bat
```

Estos scripts instalarán automáticamente todas las dependencias del backend y frontend.

### Instalación Manual

### 1. Clonar el repositorio

```bash
git clone <repository-url>
cd generador-recursos-evangelisticos
```

### 2. Configurar Backend

```bash
cd backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Linux/macOS:
source venv/bin/activate
# En Windows:
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Copiar archivo de configuración
cp .env.example .env
```

### 3. Configurar Frontend

```bash
cd frontend

# Instalar dependencias
npm install

# Copiar archivo de configuración
cp .env.example .env
```

## Ejecución

### Iniciar Backend

```bash
cd backend
source venv/bin/activate  # En Windows: venv\Scripts\activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

El backend estará disponible en: `http://localhost:8000`

### Iniciar Frontend

En otra terminal:

```bash
cd frontend
npm run dev
```

El frontend estará disponible en: `http://localhost:5173`

## Ejecutar Tests

### Tests del Backend

El backend utiliza pytest con dos tipos de tests:
- **Tests unitarios**: Verifican casos específicos y condiciones de error
- **Tests de propiedades**: Verifican comportamiento universal con múltiples entradas generadas (usando Hypothesis)

```bash
cd backend
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Ejecutar todos los tests
pytest

# Ejecutar con cobertura
pytest --cov=services --cov=main --cov-report=html

# Ver reporte de cobertura en el navegador
# El reporte se genera en backend/htmlcov/index.html

# Ejecutar solo tests de propiedades
pytest -m property

# Ejecutar solo tests unitarios
pytest -m unit

# Ejecutar tests de un módulo específico
pytest tests/test_auth_service.py

# Ejecutar con salida detallada
pytest -v
```

### Tests del Frontend

El frontend utiliza Vitest con Vue Test Utils:

```bash
cd frontend

# Ejecutar tests una vez
npm run test:unit

# Ejecutar tests en modo watch (útil durante desarrollo)
npm run test:watch

# Ejecutar con cobertura
npm run test:coverage
```

### Tests de Integración

Para ejecutar los tests de integración completos:

```bash
# Desde la raíz del proyecto
python test_integration.py
```

## Estructura del Proyecto

```
.
├── backend/
│   ├── services/          # Servicios de lógica de negocio
│   ├── templates/         # Plantillas Word (.docx)
│   ├── tests/             # Tests del backend
│   ├── main.py            # Aplicación FastAPI principal
│   ├── requirements.txt   # Dependencias de Python
│   └── pytest.ini         # Configuración de pytest
├── frontend/
│   ├── src/
│   │   ├── views/         # Componentes de vistas
│   │   ├── stores/        # Stores de Pinia
│   │   ├── services/      # Servicios de API
│   │   ├── router/        # Configuración de rutas
│   │   └── main.js        # Punto de entrada
│   ├── package.json       # Dependencias de Node.js
│   └── vite.config.js     # Configuración de Vite
└── temp_files/            # Archivos PDF generados temporalmente
```

## Plantillas Word

Las plantillas Word se encuentran en `backend/templates/` y deben contener los siguientes marcadores que serán reemplazados:

- `{{fecha_evento}}` - Fecha del evento
- `{{hora_evento}}` - Hora del evento
- `{{lugar_evento}}` - Lugar del evento
- `{{referencia_evento}}` - Referencia opcional del evento

## Uso de la Aplicación

### Flujo Completo

1. **Bienvenida**: Pantalla inicial con descripción de la aplicación
   - Haz clic en el botón "Iniciar" para comenzar

2. **Autenticación**: Responder 3 preguntas de seguridad secuencialmente
   - Pregunta 1: ¿Cuál es el nombre de tu iglesia?
   - Pregunta 2: ¿En qué ciudad se realizará el evento?
   - Pregunta 3: ¿Cuál es el tema de la campaña?
   - **Nota**: Si una respuesta es incorrecta, el cuestionario se reinicia desde la pregunta 1

3. **Generación**: Ingresar datos del evento y generar documentos
   - **Fecha del evento** (requerido): Ej. "15 de Diciembre, 2024"
   - **Hora del evento** (requerido): Ej. "7:00 PM"
   - **Lugar del evento** (requerido): Ej. "Auditorio Central"
   - **Referencia del evento** (opcional): Ej. "Calle Principal #123"
   - **Nombre del proyecto** (requerido): Ej. "Campaña_Navidad_2024"
   - Haz clic en "Generar" para crear los documentos
   - Verás una previsualización del documento A4 generado

4. **Descarga**: Descargar individualmente cada tipo de documento
   - **Descargar A4**: Afiche en formato A4 vertical
   - **Descargar 4x1**: Afiche en formato 4x1 vertical
   - **Descargar Gigantografía**: Documento de 1x1.5 metros en modo CMYK para impresión profesional

### Ejemplo de Uso

```bash
# 1. Iniciar el backend
cd backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 2. En otra terminal, iniciar el frontend
cd frontend
npm run dev

# 3. Abrir el navegador en http://localhost:5173

# 4. Seguir el flujo de la aplicación:
#    - Clic en "Iniciar"
#    - Responder las 3 preguntas de seguridad
#    - Ingresar datos del evento
#    - Generar documentos
#    - Descargar los PDFs generados
```

## Variables de Entorno

### Backend (.env)

El archivo `.env` del backend debe configurarse copiando `.env.example`:

```bash
cd backend
cp .env.example .env
```

Variables principales:

```
# Configuración del servidor
PORT=8000
HOST=0.0.0.0

# Almacenamiento de archivos
TEMP_STORAGE_PATH=../temp_files
CLEANUP_HOURS=24

# CORS
FRONTEND_URL=http://localhost:5173

# Logging
LOG_LEVEL=INFO

# Plantillas (ubicadas en backend/templates/)
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
```

### Frontend (.env)

El archivo `.env` del frontend debe configurarse copiando `.env.example`:

```bash
cd frontend
cp .env.example .env
```

Variables principales:

```
# URL del backend API
VITE_API_BASE_URL=http://localhost:8000

# Configuración opcional
VITE_APP_TITLE=Generador de Recursos Evangelísticos
VITE_API_TIMEOUT=30000
VITE_DEBUG_MODE=false
VITE_ENABLE_CONSOLE_LOGS=false
```

## API Endpoints

- `POST /api/auth/start-session` - Iniciar sesión de autenticación
- `POST /api/auth/validate-answer` - Validar respuesta de pregunta
- `POST /api/generate` - Generar documentos PDF
- `GET /api/download/{filename}` - Descargar archivo PDF

## Tecnologías Utilizadas

### Backend
- FastAPI - Framework web asíncrono
- python-docx - Manipulación de archivos Word
- Pillow - Procesamiento de imágenes
- pdf2image - Conversión de PDF a imagen
- reportlab - Generación de PDFs
- Hypothesis - Property-based testing
- pytest - Framework de testing

### Frontend
- Vue.js 3 - Framework reactivo
- Vue Router - Navegación
- Pinia - Gestión de estado
- Axios - Cliente HTTP
- Tailwind CSS - Framework CSS
- Vitest - Framework de testing

## Solución de Problemas

### Error: LibreOffice no encontrado

Asegúrate de que LibreOffice esté instalado y disponible en el PATH del sistema.

**Verificar instalación:**
```bash
# Linux/macOS
which libreoffice

# Windows (PowerShell)
where.exe libreoffice
```

Si no está en el PATH, agrega la ruta de instalación:
- **Linux**: `/usr/bin/libreoffice`
- **macOS**: `/Applications/LibreOffice.app/Contents/MacOS/soffice`
- **Windows**: `C:\Program Files\LibreOffice\program\soffice.exe`

### Error: Puerto ya en uso

Si el puerto 8000 o 5173 ya está en uso, puedes cambiarlos:

```bash
# Backend con puerto diferente
uvicorn main:app --reload --port 8001

# Frontend con puerto diferente
npm run dev -- --port 5174
```

**Nota**: Si cambias el puerto del backend, actualiza `VITE_API_BASE_URL` en `frontend/.env`

### Error: Módulo no encontrado

Asegúrate de haber instalado todas las dependencias:

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### Error: Plantillas Word no encontradas

Verifica que los archivos `Formato a4.docx` y `Formato 4x1.docx` estén en el directorio `backend/templates/`. Si están en otra ubicación, actualiza las variables `TEMPLATE_DIR`, `TEMPLATE_A4` y `TEMPLATE_4X1` en `backend/.env`.

### Error: Archivos PDF no se generan correctamente

1. Verifica que LibreOffice esté instalado correctamente
2. Asegúrate de que las plantillas Word contengan los marcadores correctos: `{{fecha_evento}}`, `{{hora_evento}}`, `{{lugar_evento}}`, `{{referencia_evento}}`
3. Revisa los logs del backend para ver mensajes de error detallados
4. Verifica que el directorio `temp_files` exista y tenga permisos de escritura

### Error: CORS en el navegador

Si ves errores de CORS en la consola del navegador:

1. Verifica que `FRONTEND_URL` en `backend/.env` coincida con la URL del frontend
2. Asegúrate de que el backend esté ejecutándose antes de abrir el frontend
3. Limpia la caché del navegador y recarga la página

### Error: Tests fallan

```bash
# Backend: Limpiar caché de pytest
cd backend
rm -rf .pytest_cache __pycache__ **/__pycache__
pytest

# Frontend: Limpiar node_modules y reinstalar
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run test:unit
```

## Licencia

Este proyecto es de uso interno para campañas evangelísticas.

## Soporte

Para reportar problemas o solicitar nuevas características, por favor contacta al equipo de desarrollo.
