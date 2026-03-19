<template>
  <main class="min-h-screen bg-background flex flex-col items-center justify-between py-16 md:py-24 px-6 text-center selection:bg-primary/10 transition-colors duration-300">
    <!-- Logo & Title -->
    <transition appear name="fade-in">
      <header class="space-y-4">
        <div class="flex justify-center text-foreground/70">
          <!-- A placeholder elegant dove icon -->
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="56"
            height="56"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="1.5"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="w-14 h-14"
          >
            <path d="M4 12c-1.333-2-2-4.667-2-8 3.333 0 6 1.333 8 4 2-2.667 4.667-4 8-4 0 3.333-.667 6-2 8" />
            <path d="M11.9 19.3c5-1.5 8.1-6.1 8.1-11.3" />
            <path d="M4 8c0 3.5 1.7 6.6 4.4 8.5" />
            <circle cx="15.5" cy="8.5" r=".5" fill="currentColor"/>
          </svg>
        </div>
        <h1 class="text-[13px] font-medium tracking-[0.2em] uppercase text-muted-foreground">
          Grace Community Church
        </h1>
      </header>
    </transition>

    <!-- The Message -->
    <transition appear name="slide-up">
      <section class="max-w-2xl style-delay-1">
        <p class="font-serif-display italic text-[clamp(2rem,5vw,3.5rem)] leading-[1.1] text-foreground text-balance">
          "Peace I leave with you; my peace I give to you."
        </p>
        <p class="mt-6 text-[13px] tracking-[0.15em] uppercase text-muted-foreground">
          — John 14:27
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
          Generate poster and audio
        </button>

        <div class="space-y-1">
          <p class="text-sm text-foreground/60">122 Sanctuary Lane, East River</p>
          <p class="text-xs text-muted-foreground tracking-wide">
            Sunday Service · 10:00 AM
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
