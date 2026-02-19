# Plan de Implementación: Generador de Recursos Evangelísticos

## Overview

Implementación de una aplicación web full-stack para generación automática de recursos publicitarios evangelísticos. El backend FastAPI procesará plantillas Word y generará PDFs, mientras el frontend Vue.js 3 proporcionará una interfaz guiada paso a paso.

## Tasks

- [x] 1. Configurar estructura del proyecto y dependencias
  - Crear estructura de directorios para backend (services/, tests/) y frontend (src/views/, src/stores/, src/services/)
  - Configurar requirements.txt con FastAPI, python-docx, Pillow, pdf2image, reportlab, hypothesis, pytest
  - Configurar package.json con Vue 3, Vue Router, Pinia, Axios, Tailwind CSS, Vitest
  - Configurar archivos de configuración (vite.config.js, tailwind.config.js, pytest.ini)
  - _Requirements: Todos los requisitos del sistema_

- [ ] 2. Implementar servicio de autenticación (Backend)
  - [x] 2.1 Crear AuthService con gestión de sesiones
    - Implementar clase AuthService con diccionario de sesiones
    - Implementar create_session() que genera UUID y retorna primera pregunta
    - Implementar _normalize_text() para normalización de respuestas
    - Implementar validate_answer() con lógica de validación y reinicio
    - Implementar is_authenticated() para verificar estado de sesión
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 2.1, 2.2, 2.3_
  
  - [ ]* 2.2 Escribir prueba de propiedad para unicidad de Session_ID
    - **Property 1: Session ID Uniqueness**
    - **Validates: Requirements 1.1, 2.1**
  
  - [ ]* 2.3 Escribir prueba de propiedad para normalización de texto
    - **Property 2: Text Normalization Consistency**
    - **Validates: Requirements 1.3**
  
  - [ ]* 2.4 Escribir prueba de propiedad para progresión con respuesta correcta
    - **Property 3: Correct Answer Progression**
    - **Validates: Requirements 1.4**
  
  - [ ]* 2.5 Escribir prueba de propiedad para reinicio con respuesta incorrecta
    - **Property 4: Incorrect Answer Reset**
    - **Validates: Requirements 1.5**
  
  - [ ]* 2.6 Escribir prueba de propiedad para completitud de autenticación
    - **Property 5: Authentication Completion**
    - **Validates: Requirements 1.6**
  
  - [ ]* 2.7 Escribir pruebas unitarias para casos edge de autenticación
    - Probar sesión inválida
    - Probar normalización con caracteres especiales
    - Probar respuestas con espacios extras

- [ ] 3. Implementar procesador de plantillas (Backend)
  - [x] 3.1 Crear TemplateProcessor
    - Implementar clase TemplateProcessor con configuración de plantillas
    - Implementar process_template() que lee plantilla Word
    - Implementar _replace_in_runs() para reemplazar marcadores
    - Manejar reemplazo en párrafos y tablas
    - _Requirements: 3.1, 3.2, 3.4_
  
  - [ ]* 3.2 Escribir prueba de propiedad para reemplazo de campos
    - **Property 9: Template Field Replacement**
    - **Validates: Requirements 3.2**
  
  - [ ]* 3.3 Escribir prueba de propiedad para manejo de campos opcionales
    - **Property 10: Optional Field Handling**
    - **Validates: Requirements 3.4**
  
  - [ ]* 3.4 Escribir pruebas unitarias para procesamiento de plantillas
    - Probar lectura de plantilla existente
    - Probar error con plantilla inexistente
    - Probar reemplazo en tablas

- [ ] 4. Implementar generador de documentos (Backend)
  - [x] 4.1 Crear DocumentGenerator
    - Implementar clase DocumentGenerator con referencia a TemplateProcessor
    - Implementar generate_all() que orquesta generación de 3 documentos
    - Implementar _generate_a4() para PDF A4
    - Implementar _generate_4x1() para PDF 4x1
    - Implementar _generate_gigantografia() con conversión CMYK y redimensionamiento
    - Implementar _convert_docx_to_pdf() usando LibreOffice
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7_
  
  - [ ]* 4.2 Escribir prueba de propiedad para generación de 3 documentos
    - **Property 12: Three Document Generation**
    - **Validates: Requirements 4.1, 4.2, 4.3**
  
  - [ ]* 4.3 Escribir prueba de propiedad para modo de color CMYK
    - **Property 13: CMYK Color Mode**
    - **Validates: Requirements 4.4**
  
  - [ ]* 4.4 Escribir prueba de propiedad para convención de nombres
    - **Property 14: Filename Convention**
    - **Validates: Requirements 4.5**
  
  - [ ]* 4.5 Escribir prueba de propiedad para completitud de respuesta
    - **Property 15: Generation Response Completeness**
    - **Validates: Requirements 4.6**
  
  - [ ]* 4.6 Escribir pruebas unitarias para generación de documentos
    - Probar generación individual de cada tipo
    - Probar manejo de errores en generación
    - Probar que errores individuales no fallan toda la operación

- [ ] 5. Implementar servicio de archivos (Backend)
  - [x] 5.1 Crear FileService
    - Implementar clase FileService con configuración de almacenamiento
    - Implementar get_file_path() para verificar existencia de archivos
    - Implementar cleanup_old_files() para limpieza automática
    - _Requirements: 12.1, 12.3, 12.5_
  
  - [ ]* 5.2 Escribir prueba de propiedad para almacenamiento temporal
    - **Property 35: Temporary Directory Storage**
    - **Validates: Requirements 12.1**
  
  - [ ]* 5.3 Escribir prueba de propiedad para limpieza de archivos antiguos
    - **Property 36: Old File Cleanup**
    - **Validates: Requirements 12.3**
  
  - [ ]* 5.4 Escribir pruebas unitarias para servicio de archivos
    - Probar get_file_path con archivo existente e inexistente
    - Probar cleanup con diferentes antigüedades de archivos

- [x] 6. Checkpoint - Verificar servicios del backend
  - Asegurar que todos los tests pasen, preguntar al usuario si surgen dudas.

- [ ] 7. Implementar endpoints de la API (Backend)
  - [x] 7.1 Crear aplicación FastAPI con endpoints
    - Configurar FastAPI con CORS
    - Implementar modelos Pydantic (SessionResponse, ValidateAnswerRequest, etc.)
    - Implementar POST /api/auth/start-session
    - Implementar POST /api/auth/validate-answer
    - Implementar POST /api/generate con validación de autenticación
    - Implementar GET /api/download/{filename}
    - Agregar manejo de errores con HTTPException
    - _Requirements: 2.4, 5.1, 5.2, 5.3, 5.4, 5.5, 6.1, 6.2, 6.3, 6.4, 6.5, 6.6_
  
  - [ ]* 7.2 Escribir prueba de propiedad para rechazo de sesión no autenticada
    - **Property 8: Unauthenticated Generation Rejection**
    - **Validates: Requirements 2.4**
  
  - [ ]* 7.3 Escribir prueba de propiedad para validación de campos requeridos
    - **Property 11: Required Fields Validation**
    - **Validates: Requirements 3.5**
  
  - [ ]* 7.4 Escribir prueba de propiedad para error de archivo no encontrado
    - **Property 17: Nonexistent File Error**
    - **Validates: Requirements 5.2, 5.5**
  
  - [ ]* 7.5 Escribir prueba de propiedad para Content-Type de PDF
    - **Property 18: PDF Content Type**
    - **Validates: Requirements 5.3, 5.4**
  
  - [ ]* 7.6 Escribir prueba de propiedad para códigos de error HTTP
    - **Property 19: HTTP Error Codes**
    - **Validates: Requirements 6.5**
  
  - [ ]* 7.7 Escribir prueba de propiedad para formato de respuesta JSON
    - **Property 20: JSON Response Format**
    - **Validates: Requirements 6.6**
  
  - [ ]* 7.8 Escribir pruebas de integración para flujo completo
    - Probar flujo de autenticación completo
    - Probar generación con sesión autenticada
    - Probar descarga de archivos generados

- [ ] 8. Configurar proyecto Vue.js (Frontend)
  - [x] 8.1 Crear estructura de proyecto Vue
    - Inicializar proyecto Vue 3 con Vite
    - Configurar Tailwind CSS
    - Crear estructura de carpetas (views/, stores/, services/)
    - Configurar Vue Router con rutas
    - Configurar Pinia para gestión de estado
    - _Requirements: 11.3_
  
  - [x] 8.2 Crear Session Store con Pinia
    - Implementar store con sessionId y authenticated
    - Implementar computed isAuthenticated
    - Implementar acciones setSession, setAuthenticated, clearSession
    - _Requirements: 2.2, 2.5_

- [ ] 9. Implementar servicio de API (Frontend)
  - [x] 9.1 Crear API service con Axios
    - Configurar cliente Axios con baseURL
    - Implementar startSession()
    - Implementar validateAnswer()
    - Implementar generateDocuments()
    - Implementar getDownloadUrl()
    - Agregar interceptor para manejo de errores
    - _Requirements: 6.1, 6.2, 6.3, 6.4_
  
  - [ ]* 9.2 Escribir pruebas unitarias para API service
    - Probar construcción correcta de URLs
    - Probar manejo de errores de red
    - Probar transformación de respuestas

- [ ] 10. Implementar vista de bienvenida (Frontend)
  - [x] 10.1 Crear WelcomeView.vue
    - Diseñar layout con colores claros y acogedores
    - Agregar título y descripción de la aplicación
    - Agregar lista de funcionalidades
    - Agregar botón "Iniciar" con navegación a /login
    - _Requirements: 7.1, 7.2, 7.3, 7.4_
  
  - [ ]* 10.2 Escribir prueba de propiedad para navegación a login
    - **Property 21: Welcome to Login Navigation**
    - **Validates: Requirements 7.4**
  
  - [ ]* 10.3 Escribir pruebas unitarias para WelcomeView
    - Probar que el botón "Iniciar" existe
    - Probar que la descripción es visible

- [ ] 11. Implementar vista de login (Frontend)
  - [x] 11.1 Crear LoginView.vue
    - Implementar onMounted para iniciar sesión
    - Crear formulario con input de respuesta
    - Agregar indicador de progreso (pregunta X de 3)
    - Implementar handleSubmit para validar respuestas
    - Agregar manejo de errores con mensaje visible
    - Implementar navegación a /generator tras autenticación exitosa
    - Implementar reinicio visual cuando respuesta es incorrecta
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7_
  
  - [ ]* 11.2 Escribir prueba de propiedad para inicialización de sesión
    - **Property 22: Session Initialization on Login**
    - **Validates: Requirements 8.1**
  
  - [ ]* 11.3 Escribir prueba de propiedad para display secuencial de preguntas
    - **Property 23: Sequential Question Display**
    - **Validates: Requirements 8.2**
  
  - [ ]* 11.4 Escribir prueba de propiedad para llamada de validación
    - **Property 24: Answer Validation API Call**
    - **Validates: Requirements 8.3**
  
  - [ ]* 11.5 Escribir prueba de propiedad para progresión de UI con respuesta correcta
    - **Property 25: Correct Answer UI Progression**
    - **Validates: Requirements 8.4**
  
  - [ ]* 11.6 Escribir prueba de propiedad para reinicio de UI con respuesta incorrecta
    - **Property 26: Incorrect Answer UI Reset**
    - **Validates: Requirements 8.5**
  
  - [ ]* 11.7 Escribir prueba de propiedad para navegación a generator
    - **Property 27: Login to Generator Navigation**
    - **Validates: Requirements 8.6**
  
  - [ ]* 11.8 Escribir pruebas unitarias para LoginView
    - Probar display de texto de pregunta
    - Probar llamada a API en submit
    - Probar display de mensaje de error

- [ ] 12. Implementar vista de generación (Frontend)
  - [x] 12.1 Crear GeneratorView.vue
    - Crear layout dividido (formulario izquierda, previsualización derecha)
    - Implementar formulario con campos: fecha_evento, hora_evento, lugar_evento, referencia_evento, nombre_proyecto
    - Agregar validación de campos obligatorios
    - Implementar handleGenerate para enviar datos al backend
    - Implementar display de previsualización con embed de PDF A4
    - Ocultar previsualización inicialmente
    - Agregar indicador de carga durante generación
    - Crear sección de descarga con 3 botones
    - Implementar handleDownload para abrir URLs de descarga
    - Deshabilitar botones de descarga hasta que generación complete
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7, 10.1, 10.2, 10.3, 10.4, 10.5_
  
  - [ ]* 12.2 Escribir prueba de propiedad para validación de campos requeridos
    - **Property 28: Required Fields Validation**
    - **Validates: Requirements 9.3**
  
  - [ ]* 12.3 Escribir prueba de propiedad para llamada de generación
    - **Property 29: Generation API Call**
    - **Validates: Requirements 9.4**
  
  - [ ]* 12.4 Escribir prueba de propiedad para display de previsualización
    - **Property 30: Preview Display on Success**
    - **Validates: Requirements 9.5**
  
  - [ ]* 12.5 Escribir prueba de propiedad para previsualización oculta inicialmente
    - **Property 31: Initial Preview Hidden**
    - **Validates: Requirements 9.6**
  
  - [ ]* 12.6 Escribir prueba de propiedad para indicador de carga
    - **Property 32: Loading Indicator Display**
    - **Validates: Requirements 9.7**
  
  - [ ]* 12.7 Escribir prueba de propiedad para clic en botón de descarga
    - **Property 33: Download Button Click**
    - **Validates: Requirements 10.3**
  
  - [ ]* 12.8 Escribir prueba de propiedad para botones deshabilitados inicialmente
    - **Property 34: Initial Download Buttons Disabled**
    - **Validates: Requirements 10.5**
  
  - [ ]* 12.9 Escribir pruebas unitarias para GeneratorView
    - Probar que formulario tiene todos los campos
    - Probar que previsualización está oculta inicialmente
    - Probar que botones de descarga existen

- [ ] 13. Configurar router con guard de autenticación (Frontend)
  - [x] 13.1 Implementar router con protección de rutas
    - Configurar rutas para /, /login, /generator
    - Implementar beforeEach guard para verificar autenticación
    - Redirigir a /login si ruta requiere autenticación y usuario no está autenticado
    - _Requirements: 7.4, 8.6_

- [x] 14. Checkpoint - Verificar integración frontend-backend
  - Asegurar que todos los tests pasen, preguntar al usuario si surgen dudas.

- [ ] 15. Implementar diseño responsivo y estilos finales (Frontend)
  - [x] 15.1 Aplicar estilos Tailwind CSS
    - Configurar paleta de colores claros (azules, morados suaves)
    - Aplicar estilos responsivos con breakpoints
    - Agregar transiciones y efectos hover
    - Asegurar consistencia visual entre vistas
    - _Requirements: 7.3, 11.1, 11.4_

- [ ] 16. Configurar variables de entorno y deployment
  - [x] 16.1 Crear archivos de configuración
    - Crear .env.example para backend con configuración de puertos y paths
    - Crear .env.example para frontend con VITE_API_BASE_URL
    - Documentar variables de entorno necesarias
    - _Requirements: Todos los requisitos del sistema_

- [ ] 17. Crear documentación de setup y ejecución
  - [x] 17.1 Crear README.md
    - Documentar requisitos del sistema (Python 3.10+, Node 18+, LibreOffice)
    - Documentar instalación de dependencias
    - Documentar comandos para ejecutar backend y frontend
    - Documentar comandos para ejecutar tests
    - Incluir ejemplos de uso
    - _Requirements: Todos los requisitos del sistema_

- [x] 18. Checkpoint final - Verificar sistema completo
  - Ejecutar todos los tests (backend y frontend)
  - Verificar flujo completo de usuario manualmente
  - Asegurar que todos los documentos se generan correctamente
  - Preguntar al usuario si hay ajustes finales necesarios

## Notes

- Las tareas marcadas con `*` son opcionales y pueden omitirse para un MVP más rápido
- Cada tarea referencia requisitos específicos para trazabilidad
- Los checkpoints aseguran validación incremental
- Las pruebas de propiedad validan corrección universal
- Las pruebas unitarias validan ejemplos específicos y casos edge
- Se requiere LibreOffice instalado en el sistema para conversión de DOCX a PDF
