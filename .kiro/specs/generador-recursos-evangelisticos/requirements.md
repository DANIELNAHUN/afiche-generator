# Documento de Requisitos

## Introducción

Sistema web full-stack para la generación automática de recursos publicitarios (afiches y gigantografías) en formato PDF para campañas evangelísticas. La aplicación procesa plantillas Word editables y genera documentos personalizados con información de eventos, permitiendo a los usuarios descargar materiales listos para impresión profesional.

## Glosario

- **Sistema**: La aplicación web completa (backend + frontend)
- **Backend**: Servidor FastAPI que procesa plantillas y genera PDFs
- **Frontend**: Interfaz de usuario Vue.js 3 con Tailwind CSS
- **Sesión**: Proceso completo de autenticación desde el inicio hasta la validación exitosa de las 3 preguntas
- **Session_ID**: Identificador único generado para cada sesión de autenticación
- **Plantilla_Word**: Archivo .docx con campos editables ubicado en la raíz del proyecto
- **Afiche**: Documento publicitario en formato PDF generado a partir de plantillas
- **Gigantografía**: Documento de gran formato (1x1.5 metros) en modo CMYK para impresión profesional
- **Usuario**: Persona que utiliza el sistema para generar recursos publicitarios
- **Pregunta_Seguridad**: Una de las 3 preguntas utilizadas para autenticación
- **Respuesta_Predefinida**: Valor correcto almacenado en el backend para cada pregunta de seguridad
- **Parámetros_Evento**: Datos del evento (fecha, hora, lugar, referencia opcional)

## Requisitos

### Requisito 1: Autenticación por Cuestionario

**User Story:** Como usuario, quiero autenticarme mediante un cuestionario de 3 preguntas de seguridad, para que pueda acceder al sistema de generación de recursos.

#### Acceptance Criteria

1. WHEN un usuario inicia el proceso de autenticación, THE Sistema SHALL generar un Session_ID único
2. THE Sistema SHALL presentar exactamente 3 Preguntas_Seguridad de forma secuencial
3. WHEN un usuario envía una respuesta, THE Backend SHALL normalizar el texto eliminando espacios extras, convirtiendo a minúsculas y removiendo puntuación adicional
4. WHEN una respuesta normalizada coincide con la Respuesta_Predefinida, THE Sistema SHALL avanzar a la siguiente pregunta
5. IF una respuesta no coincide con la Respuesta_Predefinida, THEN THE Sistema SHALL reiniciar el cuestionario desde la pregunta 1
6. WHEN las 3 preguntas son respondidas correctamente, THE Sistema SHALL marcar la sesión como autenticada
7. THE Backend SHALL almacenar las Respuestas_Predefinidas de forma segura

### Requisito 2: Gestión de Sesiones

**User Story:** Como sistema, quiero gestionar sesiones de usuario con identificadores únicos, para que pueda rastrear el estado de autenticación y las operaciones de cada usuario.

#### Acceptance Criteria

1. WHEN se inicia una nueva sesión, THE Sistema SHALL generar un Session_ID único y aleatorio
2. THE Backend SHALL asociar cada Session_ID con el estado de autenticación del usuario
3. WHEN se valida una respuesta, THE Backend SHALL verificar que el Session_ID existe y es válido
4. WHEN se solicita generar PDFs, THE Backend SHALL verificar que el Session_ID corresponde a una sesión autenticada
5. THE Sistema SHALL mantener el estado de la sesión durante todo el proceso de generación

### Requisito 3: Procesamiento de Plantillas Word

**User Story:** Como sistema, quiero procesar plantillas Word con campos editables, para que pueda generar documentos personalizados con los datos del evento.

#### Acceptance Criteria

1. THE Sistema SHALL leer las plantillas "Formato a4.docx" y "Formato 4x1.docx" desde la raíz del proyecto
2. WHEN se reciben Parámetros_Evento, THE Backend SHALL reemplazar los campos editables en las Plantillas_Word con los valores proporcionados
3. THE Backend SHALL preservar el formato original de las plantillas durante el procesamiento
4. WHEN el campo referencia_evento está vacío, THE Backend SHALL manejar el campo opcional apropiadamente
5. THE Backend SHALL validar que los campos obligatorios (fecha_evento, hora_evento, lugar_evento) estén presentes

### Requisito 4: Generación de PDFs

**User Story:** Como usuario, quiero generar automáticamente 3 tipos de documentos PDF, para que pueda obtener materiales publicitarios en diferentes formatos.

#### Acceptance Criteria

1. WHEN se solicita la generación, THE Sistema SHALL crear un PDF en formato A4 vertical basado en "Formato a4.docx"
2. WHEN se solicita la generación, THE Sistema SHALL crear un PDF en formato 4x1 vertical basado en "Formato 4x1.docx"
3. WHEN se solicita la generación, THE Sistema SHALL crear una Gigantografía en formato PDF vertical de 1x1.5 metros basada en "Formato a4.docx"
4. THE Sistema SHALL convertir la Gigantografía a modo de color CMYK para impresión profesional
5. THE Backend SHALL generar nombres de archivo únicos para cada documento usando el nombre_proyecto proporcionado
6. WHEN la generación finaliza, THE Backend SHALL retornar el estado de generación y nombre de archivo para cada uno de los 3 documentos
7. THE Sistema SHALL almacenar temporalmente los archivos generados para descarga

### Requisito 5: Sistema de Descarga de Archivos

**User Story:** Como usuario, quiero descargar los PDFs generados individualmente, para que pueda obtener cada formato según mis necesidades.

#### Acceptance Criteria

1. THE Backend SHALL exponer un endpoint de descarga que acepte el nombre del archivo
2. WHEN un usuario solicita descargar un archivo, THE Backend SHALL verificar que el archivo existe
3. WHEN un archivo existe, THE Backend SHALL enviarlo usando FileResponse con los headers apropiados
4. THE Backend SHALL establecer el tipo de contenido como "application/pdf"
5. IF un archivo no existe, THEN THE Backend SHALL retornar un error 404

### Requisito 6: API REST del Backend

**User Story:** Como frontend, quiero comunicarme con el backend mediante una API REST bien definida, para que pueda realizar operaciones de autenticación, generación y descarga.

#### Acceptance Criteria

1. THE Backend SHALL exponer el endpoint POST /api/auth/start-session que retorna un Session_ID
2. THE Backend SHALL exponer el endpoint POST /api/auth/validate-answer que acepta session_id, question_number y answer
3. THE Backend SHALL exponer el endpoint POST /api/generate que acepta session_id, Parámetros_Evento y nombre_proyecto
4. THE Backend SHALL exponer el endpoint GET /api/download/{filename} para descargar archivos
5. WHEN se recibe una petición inválida, THE Backend SHALL retornar códigos de estado HTTP apropiados (400, 401, 404, 500)
6. THE Backend SHALL retornar respuestas en formato JSON para todos los endpoints excepto descarga

### Requisito 7: Vista de Bienvenida

**User Story:** Como usuario, quiero ver una pantalla de bienvenida atractiva, para que pueda entender el propósito de la aplicación e iniciar el proceso.

#### Acceptance Criteria

1. THE Frontend SHALL mostrar una descripción clara de la funcionalidad de la aplicación
2. THE Frontend SHALL incluir un botón "Iniciar" prominente
3. THE Frontend SHALL utilizar una paleta de colores claros y acogedores apropiados para el tema cristiano/evangelístico
4. WHEN el usuario hace clic en "Iniciar", THE Frontend SHALL navegar a la vista de login

### Requisito 8: Vista de Login (Formulario Secuencial)

**User Story:** Como usuario, quiero responder las preguntas de seguridad de forma secuencial, para que pueda autenticarme en el sistema.

#### Acceptance Criteria

1. WHEN la vista se carga, THE Frontend SHALL solicitar un Session_ID al backend
2. THE Frontend SHALL mostrar una pregunta a la vez en orden secuencial
3. WHEN el usuario envía una respuesta, THE Frontend SHALL validarla con el backend
4. WHEN una respuesta es correcta, THE Frontend SHALL avanzar a la siguiente pregunta
5. IF una respuesta es incorrecta, THEN THE Frontend SHALL mostrar un mensaje de error y reiniciar desde la pregunta 1
6. WHEN las 3 preguntas son respondidas correctamente, THE Frontend SHALL navegar a la vista de generación
7. THE Frontend SHALL proporcionar retroalimentación visual durante la validación

### Requisito 9: Vista de Generación con Formulario y Previsualización

**User Story:** Como usuario, quiero ingresar los datos del evento y ver una previsualización de los documentos generados, para que pueda verificar la información antes de descargar.

#### Acceptance Criteria

1. THE Frontend SHALL mostrar un layout dividido con el formulario a la izquierda y el área de previsualización a la derecha
2. THE Frontend SHALL incluir campos para fecha_evento, hora_evento, lugar_evento, referencia_evento (opcional) y nombre_proyecto
3. THE Frontend SHALL validar que los campos obligatorios estén completos antes de permitir la generación
4. WHEN el usuario hace clic en "Generar", THE Frontend SHALL enviar los datos al backend
5. WHEN la generación es exitosa, THE Frontend SHALL mostrar la previsualización del documento en formato A4
6. THE Frontend SHALL ocultar la previsualización hasta que se complete la generación
7. THE Frontend SHALL mostrar indicadores de carga durante el proceso de generación

### Requisito 10: Sección de Descarga

**User Story:** Como usuario, quiero descargar cada tipo de documento individualmente, para que pueda obtener solo los formatos que necesito.

#### Acceptance Criteria

1. THE Frontend SHALL mostrar la sección de descarga debajo del área de previsualización
2. THE Frontend SHALL incluir 3 botones: "Descargar A4", "Descargar 4x1" y "Descargar Gigantografía"
3. WHEN el usuario hace clic en un botón de descarga, THE Frontend SHALL solicitar el archivo correspondiente al backend
4. THE Frontend SHALL iniciar la descarga del archivo en el navegador del usuario
5. THE Frontend SHALL deshabilitar los botones de descarga hasta que la generación esté completa

### Requisito 11: Diseño Responsivo y Experiencia de Usuario

**User Story:** Como usuario, quiero una interfaz simple y guiada, para que pueda completar el proceso sin confusión.

#### Acceptance Criteria

1. THE Frontend SHALL implementar un diseño responsivo que funcione en dispositivos móviles y de escritorio
2. THE Frontend SHALL guiar al usuario paso a paso a través del proceso completo
3. THE Frontend SHALL utilizar Tailwind CSS para el estilado
4. THE Frontend SHALL mantener una paleta de colores consistente en todas las vistas
5. THE Frontend SHALL proporcionar mensajes de error claros y útiles
6. THE Frontend SHALL mostrar el estado de las operaciones en curso

### Requisito 12: Manejo de Archivos Temporales

**User Story:** Como sistema, quiero gestionar archivos temporales de forma eficiente, para que no se acumulen archivos innecesarios en el servidor.

#### Acceptance Criteria

1. THE Backend SHALL almacenar los archivos generados en un directorio temporal
2. THE Backend SHALL generar nombres de archivo únicos para evitar colisiones
3. THE Backend SHALL implementar un mecanismo de limpieza de archivos antiguos
4. WHEN un archivo es descargado, THE Backend SHALL mantenerlo disponible por un período razonable
5. THE Backend SHALL manejar errores de escritura y lectura de archivos apropiadamente
