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
