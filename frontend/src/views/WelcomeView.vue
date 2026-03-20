<template>
  <main class="min-h-screen bg-background flex flex-col items-center justify-between py-16 md:py-24 px-6 text-center selection:bg-primary/10 transition-colors duration-300">
    <!-- Logo & Title -->
    <transition appear name="fade-in">
      <header class="space-y-4">
        <div class="flex justify-center text-foreground/70">
          <!-- A placeholder elegant dove icon -->
          <svg width="72" height="72" xmlns="http://www.w3.org/2000/svg" version="1.1" xmlns:bx="https://boxy-svg.com">
            <g transform="matrix(1, 0, 0, 1, -4.10958, 9.011007)" style="">
              <bx:title>Espiritu Santo</bx:title>
              <g transform="matrix(1, 0, 0, 1, -54.608284, -19.205931)">
                <path stroke="#957850ff" id="svg_9" d="M 83.762 35.803 C 78.944 40.782 76.085 45.709 76.1 47.387 C 76.115 49.065 83.872 54.346 83.872 54.346 L 97.854 43.125 C 98.201 34.663 93.41 11.763 89.844 21.468 C 85.79 32.497 83.762 35.803 83.762 35.803 Z" stroke-width="2" stroke-miterlimit="10" stroke-linejoin="round" stroke-linecap="round" style="stroke-width: 2; fill: rgb(255, 255, 255);"></path>
                <path id="svg_8" d="M 94.947 56.715 C 123.307 55.8 113.247 19.205 112.327 23.785 C 111.407 28.365 84.887 54.885 82.137 51.225 C 79.393 47.566 75.733 46.651 73.904 49.395 C 72.074 52.139 71.16 53.054 71.16 53.054 C 71.16 53.054 76.649 52.139 77.564 53.968 C 78.479 55.798 81.38 61.801 86.712 62.201 C 86.712 62.201 88.533 62.823 92.201 70.434 C 96.478 79.31 114.161 70.434 108.671 65.86 C 103.182 61.286 99.523 63.116 96.781 61.286 C 94.037 59.456 94.951 56.712 94.951 56.712 L 94.947 56.715 L 94.947 56.715 Z" stroke-width="2" stroke-miterlimit="10" stroke-linejoin="round" stroke-linecap="round" stroke="#957850ff" style="stroke-width: 2; fill: rgb(255, 255, 255);"></path>
              </g>
            </g>
          </svg>
        </div>
        <h1 class="text-lg font-medium tracking-[0.2em] uppercase text-muted-foreground">
          Iglesia del Verbo de Dios en Ilo
        </h1>
      </header>
    </transition>

    <!-- The Message -->
    <transition appear name="slide-up">
      <section class="max-w-2xl style-delay-1">
        <p class="font-serif-display italic text-[clamp(2rem,5vw,3.5rem)] leading-[1.1] text-foreground text-balance">
          "Si puedes creer, al que cree todo le es posible."
        </p>
        <p class="mt-6 text-[13px] tracking-[0.15em] uppercase text-muted-foreground">
          — Marcos 9:23
        </p>
      </section>
    </transition>

    <!-- Action & Location -->
    <transition appear name="fade-in">
      <footer class="flex flex-col items-center gap-12 style-delay-2">
        <button
          @click="handleStart"
          class="px-8 py-4 bg-primary text-primary-foreground rounded-full text-sm font-semibold tracking-wide shadow-[0_10px_15px_-3px_rgba(0,0,0,0.05),0_4px_6px_-2px_rgba(0,0,0,0.02)] transition-all duration-300 hover:bg-primary/90 hover:-translate-y-0.5 hover:shadow-[0_20px_25px_-5px_rgba(0,0,0,0.08),0_8px_10px_-6px_rgba(0,0,0,0.04)] active:scale-95"
        >
          Generar afiche y audio
        </button>

        <div class="space-y-1">
          <p class="text-md text-foreground/60">
          <a href="https://maps.app.goo.gl/uyME8FpoYWg2fQzz8" target="_blank">
            Ilo, Urb José Olaya D-28
          </a>
          </p>
          <p class="text-sm text-muted-foreground tracking-wide">
            Estudios Biblicos Diarios · 06:30 PM - 08:00 PM
            <br>
            Ayuno Dominical · 09:00 AM - 12:00 PM
          </p>
        </div>
      </footer>
    </transition>
  </main>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const handleStart = () => {
  router.push({ name: 'login' })
}
</script>

<style scoped>
/* Vue Transitions to replicate framer-motion */
.fade-in-enter-active {
  transition: opacity 0.8s ease;
}
.fade-in-enter-from {
  opacity: 0;
}
.fade-in-enter-to {
  opacity: 1;
}

.slide-up-enter-active {
  transition: opacity 0.6s cubic-bezier(0.25, 0.1, 0.25, 1), transform 0.6s cubic-bezier(0.25, 0.1, 0.25, 1);
}
.slide-up-enter-from {
  opacity: 0;
  transform: translateY(8px);
}
.slide-up-enter-to {
  opacity: 1;
  transform: translateY(0);
}

.style-delay-1.slide-up-enter-active, .style-delay-1.fade-in-enter-active {
  transition-delay: 0.3s;
}

.style-delay-2.fade-in-enter-active {
  transition-delay: 0.6s;
}

.text-balance {
  text-wrap: balance;
}
</style>
