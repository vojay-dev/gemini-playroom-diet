<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { event as gtagEvent } from 'vue-gtag'
import { useToast } from '../composables/useToast'
import { compressImage } from '../composables/useImageCompressor'

const router = useRouter()
const toast = useToast()
const age = ref(4)
const file = ref(null)
const previewUrl = ref(null)
const isSubmitting = ref(false)
const isCompressing = ref(false)

// Info slides
const slides = [
  'Turn toy chaos into a <span class="font-bold text-primary">science-backed</span> growth plan. 4 AI agents map your toys to the O*NET framework, forecast future career skills, and create a 6-month roadmap.',
  'Upload a photo of your playroom and get a <span class="font-bold text-primary">personalized skill radar</span> showing your child\'s development across 6 key areas.',
  'Each recommendation is <span class="font-bold text-primary">safety-validated</span> against CPSC guidelines for your child\'s age. Unsafe suggestions are automatically replaced.',
  'Get a <span class="font-bold text-primary">Play Quest</span>! A fun, structured activity using toys you already own, designed to target a specific development skill.',
]
const currentSlide = ref(0)
const SLIDE_DURATION = 6000
let slideTimer = null

const goToSlide = (i) => {
  currentSlide.value = i
  resetTimer()
}

const resetTimer = () => {
  clearInterval(slideTimer)
  slideTimer = setInterval(() => {
    currentSlide.value = (currentSlide.value + 1) % slides.length
  }, SLIDE_DURATION)
}

onMounted(() => resetTimer())
onUnmounted(() => clearInterval(slideTimer))

// Stick figure
const figure = computed(() => {
  const t = (age.value - 1) / 11 // 0 to 1
  const headR = 9 - t * 3        // 9 → 6
  const bodyLen = 10 + t * 14     // 10 → 24
  const legLen = 8 + t * 10       // 8 → 18
  const armLen = 6 + t * 7        // 6 → 13
  const armY = 0.3                // arms at 30% down body

  // Build from bottom up within viewBox 0 0 40 70
  const bottom = 68
  const legEnd = bottom
  const bodyEnd = bottom - legLen
  const bodyStart = bodyEnd - bodyLen
  const headCY = bodyStart - headR
  const armAttach = bodyStart + bodyLen * armY

  return { headR, bodyStart, bodyEnd, legEnd, armLen, armAttach, headCY }
})

const handleFileChange = async (event) => {
  const selected = event.target.files[0]
  if (!selected) return

  // Show preview immediately with original
  previewUrl.value = URL.createObjectURL(selected)

  // Compress if needed
  isCompressing.value = true
  try {
    const compressed = await compressImage(selected)
    file.value = compressed

    if (compressed.size < selected.size) {
      const savedMB = ((selected.size - compressed.size) / (1024 * 1024)).toFixed(1)
      toast.success(`Image optimized (saved ${savedMB} MB)`)
    }
  } catch (e) {
    console.error('Compression failed:', e)
    file.value = selected // Use original on failure
  } finally {
    isCompressing.value = false
  }
}

const exampleImages = [
  { src: '/examples/playroom1.jpg', label: 'Example 1' },
  { src: '/examples/playroom2.jpg', label: 'Example 2' }
]

const selectExample = async (exampleSrc) => {
  try {
    const response = await fetch(exampleSrc)
    const blob = await response.blob()
    const filename = exampleSrc.split('/').pop()
    const exampleFile = new File([blob], filename, { type: blob.type })

    previewUrl.value = URL.createObjectURL(blob)

    // Compress example if needed
    isCompressing.value = true
    try {
      file.value = await compressImage(exampleFile)
    } catch (e) {
      file.value = exampleFile
    } finally {
      isCompressing.value = false
    }
  } catch (e) {
    console.error('Failed to load example:', e)
  }
}

const handleSubmit = async () => {
  if (!file.value) return toast.error("Please select a photo first!")

  isSubmitting.value = true

  try {
    const formData = new FormData()
    formData.append('file', file.value)
    formData.append('age', age.value.toString())

    const apiUrl = import.meta.env.GPD_API_URL || 'http://localhost:8000'
    const response = await fetch(`${apiUrl}/api/scan`, {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      throw new Error(`Upload failed: ${response.statusText}`)
    }

    const data = await response.json()
    try { gtagEvent('scan_created', { child_age: age.value, cached: data.cached || false }) } catch {}
    router.push({ path: `/scan/${data.scan_id}`, query: data.cached ? { cached: '1' } : {} })

  } catch (e) {
    console.error(e)
    toast.error("Error uploading scan. Please try again.")
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="hero-page min-h-[calc(100vh-68px-40px)] py-6 lg:py-10 px-6 overflow-auto relative flex flex-col items-center">

    <!-- HERO: title + subtitle + rotating tagline -->
    <section class="hero-block w-full max-w-2xl relative z-10 text-center">
      <h1 class="logo-text" style="font-family: 'Fredoka', sans-serif;">
        <span class="logo-orb logo-orb-1" aria-hidden="true"></span>
        <span class="logo-orb logo-orb-2" aria-hidden="true"></span>
        <span class="spark spark-1" aria-hidden="true"></span>
        <span class="spark spark-2" aria-hidden="true"></span>
        <span class="spark spark-3" aria-hidden="true"></span>
        <span class="spark spark-4" aria-hidden="true"></span>
        <span class="spark spark-5" aria-hidden="true"></span>
        <span class="spark spark-6" aria-hidden="true"></span>
        <span class="logo-main">Playroom</span> <span class="logo-accent">Diet<svg class="logo-squiggle" viewBox="0 0 200 14" preserveAspectRatio="none" aria-hidden="true"><defs><linearGradient id="squiggleGrad" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" stop-color="var(--color-primary)"/><stop offset="100%" stop-color="var(--color-secondary)"/></linearGradient></defs><path d="M 4 8 C 50 14, 150 1, 196 8" class="squiggle-path" vector-effect="non-scaling-stroke" fill="none" stroke="url(#squiggleGrad)" stroke-width="2.5" stroke-linecap="round"/></svg></span>
      </h1>

      <p class="hero-subtitle mt-8">Because play needs balance, just like a diet.</p>

      <div class="hero-rotator mt-8">
        <div class="relative min-h-20">
          <transition name="slide-fade" mode="out-in">
            <p class="text-base lg:text-lg opacity-80 leading-relaxed" :key="currentSlide" v-html="slides[currentSlide]"></p>
          </transition>
        </div>
        <div class="flex gap-1.5 mt-4 max-w-xs mx-auto">
          <button
            v-for="(_, i) in slides"
            :key="i"
            @click="goToSlide(i)"
            class="h-0.5 flex-1 rounded-full bg-white/10 overflow-hidden cursor-pointer"
          >
            <div
              :class="[
                'h-full rounded-full',
                currentSlide === i ? 'slide-progress bg-primary' : i < currentSlide ? 'w-full bg-primary/40' : 'w-0'
              ]"
            />
          </button>
        </div>
      </div>
    </section>

    <!-- FORM CARD -->
    <div class="form-card w-full max-w-xl mt-12 relative z-10">
      <form class="p-8 lg:p-10" @submit.prevent="handleSubmit">

          <!-- Age -->
          <div class="form-step">
            <div class="flex items-center justify-between mb-4">
              <span class="step-label">
                <span class="step-num">1</span>
                Child's Age
              </span>
              <span class="step-value">
                {{ age }} <span class="opacity-60 font-normal">years</span>
              </span>
            </div>
            <div class="flex items-end gap-4">
              <div class="flex-1">
                <input
                  type="range"
                  min="1"
                  max="12"
                  v-model="age"
                  class="range-aura"
                  :style="{ '--progress': `${((age - 1) / 11) * 100}%` }"
                />
                <div class="w-full flex justify-between text-xs px-1 mt-3 opacity-40">
                  <span>1</span>
                  <span>3</span>
                  <span>6</span>
                  <span>9</span>
                  <span>12</span>
                </div>
              </div>
              <svg viewBox="0 0 40 70" class="w-8 h-14 shrink-0 mb-1 figure-transition figure-entrance">
                <!-- head -->
                <circle
                  cx="20" :cy="figure.headCY" :r="figure.headR"
                  fill="none" class="stroke-primary" stroke-width="2.5" stroke-linecap="round" opacity="0.7"
                />
                <!-- smile -->
                <path
                  :d="`M ${17} ${figure.headCY + 2} Q 20 ${figure.headCY + 5} ${23} ${figure.headCY + 2}`"
                  fill="none" class="stroke-primary" stroke-width="2" stroke-linecap="round" opacity="0.6"
                />
                <!-- body -->
                <line
                  x1="20" :y1="figure.bodyStart" x2="20" :y2="figure.bodyEnd"
                  class="stroke-primary" stroke-width="2.5" stroke-linecap="round" opacity="0.7"
                />
                <!-- left arm -->
                <line
                  x1="20" :y1="figure.armAttach" :x2="20 - figure.armLen" :y2="figure.armAttach + figure.armLen * 0.7"
                  class="stroke-primary" stroke-width="2.5" stroke-linecap="round" opacity="0.7"
                />
                <!-- right arm -->
                <line
                  x1="20" :y1="figure.armAttach" :x2="20 + figure.armLen" :y2="figure.armAttach + figure.armLen * 0.7"
                  class="stroke-primary" stroke-width="2.5" stroke-linecap="round" opacity="0.7"
                />
                <!-- left leg -->
                <line
                  x1="20" :y1="figure.bodyEnd" :x2="13" :y2="figure.legEnd"
                  class="stroke-primary" stroke-width="2.5" stroke-linecap="round" opacity="0.7"
                />
                <!-- right leg -->
                <line
                  x1="20" :y1="figure.bodyEnd" :x2="27" :y2="figure.legEnd"
                  class="stroke-primary" stroke-width="2.5" stroke-linecap="round" opacity="0.7"
                />
              </svg>
            </div>
          </div>

          <!-- Photo -->
          <div class="form-step mt-7">
            <div class="flex items-center mb-4">
              <span class="step-label">
                <span class="step-num step-num-secondary">2</span>
                Playroom Photo
              </span>
            </div>

            <!-- Upload -->
            <div class="flex flex-col items-center justify-center w-full">
                <label for="dropzone-file" class="dropzone flex flex-col items-center justify-center w-full h-36 rounded-xl cursor-pointer relative overflow-hidden group" :class="{ 'dropzone-filled': previewUrl }">

                    <!-- Preview -->
                    <img v-if="previewUrl" :src="previewUrl" class="absolute inset-0 w-full h-full object-cover opacity-90 group-hover:scale-105 transition-transform" />

                    <!-- Placeholder -->
                    <div v-else class="flex flex-col items-center justify-center pt-5 pb-6 text-base-content/60 relative">
                        <div class="dropzone-icon mb-3">
                          <svg class="w-5 h-5 text-primary" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 20 16">
                              <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 13h3a3 3 0 0 0 0-6h-.025A5.56 5.56 0 0 0 16 6.5 5.5 5.5 0 0 0 5.207 5.021C5.137 5.017 5.071 5 5 5a4 4 0 0 0 0 8h2.167M10 15V6m0 0L8 8m2-2 2 2"/>
                          </svg>
                        </div>
                        <p class="mb-0.5 text-sm font-medium">Click to upload</p>
                        <p class="text-xs opacity-70">PNG, JPG or take a photo</p>
                    </div>

                    <!-- Input -->
                    <input
                      id="dropzone-file"
                      type="file"
                      accept="image/*"
                      class="hidden"
                      @change="handleFileChange"
                    />
                </label>
            </div>

            <!-- Examples -->
            <div class="mt-3">
              <div class="flex items-center gap-2 mb-2">
                <div class="flex-1 h-px bg-base-content/20"></div>
                <span class="text-xs text-base-content/50">or try an example</span>
                <div class="flex-1 h-px bg-base-content/20"></div>
              </div>
              <div class="flex gap-2 justify-center">
                <button
                  v-for="(example, index) in exampleImages"
                  :key="index"
                  type="button"
                  @click="selectExample(example.src)"
                  class="relative w-14 h-14 rounded-lg overflow-hidden border-2 border-transparent hover:border-primary transition-all hover:scale-105 shadow-md"
                >
                  <img
                    :src="example.src"
                    :alt="example.label"
                    class="w-full h-full object-cover"
                  />
                </button>
              </div>
            </div>
          </div>

          <!-- Submit -->
          <div class="mt-8">
            <button class="btn-aura w-full" :disabled="isSubmitting || isCompressing">
              <span v-if="isSubmitting || isCompressing" class="loading loading-spinner loading-sm"></span>
              <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <span>{{ isCompressing ? 'Optimizing...' : isSubmitting ? 'Analyzing...' : 'Analyze Playroom' }}</span>
              <svg v-if="!(isSubmitting || isCompressing)" xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5 btn-aura-arrow" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>

          <!-- Preview -->
          <div class="mt-6 pt-5 border-t border-white/8">
            <p class="text-xs text-center opacity-50 mb-3">You'll receive</p>
            <div class="flex justify-center gap-5 text-xs">
              <div class="flex items-center gap-1.5 opacity-70">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                Skill Radar
              </div>
              <div class="flex items-center gap-1.5 opacity-70">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5 text-secondary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
                </svg>
                Roadmap
              </div>
              <div class="flex items-center gap-1.5 opacity-70">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v13m0-13V6a2 2 0 112 2h-2zm0 0V5.5A2.5 2.5 0 109.5 8H12zm-7 4h14M5 12a2 2 0 110-4h14a2 2 0 110 4M5 12v7a2 2 0 002 2h10a2 2 0 002-2v-7" />
                </svg>
                Career Skills
              </div>
            </div>
          </div>
        </form>
    </div>

    <!-- Tech stack + nav -->
    <section class="secondary-block w-full max-w-2xl mt-16 mb-4 relative z-10 text-center">
      <p class="text-xs opacity-40 mb-4 tracking-wider uppercase">Built with</p>
      <div class="flex flex-wrap justify-center gap-1.5 mb-8">
        <a href="https://github.com/astronomer/airflow-ai-sdk" target="_blank" class="badge badge-md badge-soft badge-primary gap-1 p-2 tech-badge pill-in" style="animation-delay: 0.1s">
          <span>🧠</span> AI Agents
        </a>
        <a href="https://ai.google.dev/gemini-api/docs" target="_blank" class="badge badge-md badge-soft badge-primary gap-1 p-2 tech-badge pill-in" style="animation-delay: 0.17s">
          <span>🤖</span> Gemini 3
        </a>
        <a href="https://airflow.apache.org/" target="_blank" class="badge badge-md badge-soft badge-primary gap-1 p-2 tech-badge pill-in" style="animation-delay: 0.24s">
          <span>🌀</span> Apache Airflow
        </a>
        <a href="https://fastapi.tiangolo.com/" target="_blank" class="badge badge-md badge-soft badge-primary gap-1 p-2 tech-badge pill-in" style="animation-delay: 0.31s">
          <span>⚡</span> FastAPI
        </a>
        <a href="https://vuejs.org/" target="_blank" class="badge badge-md badge-soft badge-primary gap-1 p-2 tech-badge pill-in" style="animation-delay: 0.38s">
          <span>💚</span> Vue.js 3
        </a>
        <a href="https://tailwindcss.com/" target="_blank" class="badge badge-md badge-soft badge-primary gap-1 p-2 tech-badge pill-in" style="animation-delay: 0.45s">
          <span>🎨</span> Tailwind CSS
        </a>
        <a href="https://daisyui.com/" target="_blank" class="badge badge-md badge-soft badge-primary gap-1 p-2 tech-badge pill-in" style="animation-delay: 0.52s">
          <span>🌼</span> daisyUI 5
        </a>
        <a href="https://www.postgresql.org/" target="_blank" class="badge badge-md badge-soft badge-primary gap-1 p-2 tech-badge pill-in" style="animation-delay: 0.59s">
          <span>🗄️</span> Postgres
        </a>
        <a href="https://www.python.org/" target="_blank" class="badge badge-md badge-soft badge-primary gap-1 p-2 tech-badge pill-in" style="animation-delay: 0.66s">
          <span>🐍</span> Python
        </a>
        <a href="https://www.onetcenter.org/" target="_blank" class="badge badge-md badge-soft badge-primary gap-1 p-2 tech-badge pill-in" style="animation-delay: 0.73s">
          <span>📊</span> O*NET Data
        </a>
      </div>
      <div class="flex gap-2 flex-wrap justify-center">
        <RouterLink to="/system" class="btn btn-sm btn-ghost gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-warning" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
          </svg>
          System
        </RouterLink>
        <RouterLink to="/about" class="btn btn-sm btn-ghost gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          About
        </RouterLink>
        <a href="https://github.com/vojay-dev/gemini-playroom-diet" target="_blank" class="btn btn-sm btn-ghost gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-info" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
          </svg>
          GitHub
        </a>
      </div>
    </section>

    <!-- Gemini Hackathon Badge -->
    <a
      href="https://gemini3.devpost.com/"
      target="_blank"
      class="gemini-badge inline-flex items-center gap-2 px-4 py-2 rounded-full bg-base-300/30 backdrop-blur-md border border-white/10 hover:border-white/25 transition-all relative z-10 mt-8 mb-8"
    >
      <img src="/gemini-color.png" alt="Gemini" class="w-5 h-5 gemini-spin" />
      <span class="text-xs opacity-60">Built for the</span>
      <span class="text-xs font-semibold">Gemini 3 Hackathon</span>
    </a>
  </div>
</template>

<style scoped>
.tech-badge {
  transition: all 0.3s ease;
  cursor: pointer;
  text-decoration: none;
}

.figure-transition circle,
.figure-transition line,
.figure-transition path {
  transition: all 0.4s ease-out;
}

.figure-entrance {
  animation: figure-pop 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) 0.3s both;
}

@keyframes figure-pop {
  0% {
    opacity: 0;
    transform: translateY(10px) scale(0.3) rotate(-15deg);
  }
  60% {
    opacity: 1;
    transform: translateY(-3px) scale(1.1) rotate(3deg);
  }
  100% {
    opacity: 1;
    transform: translateY(0) scale(1) rotate(0deg);
  }
}

/* Hero layout */
.hero-page {
  isolation: isolate;
}

.hero-subtitle {
  font-size: clamp(1rem, 1.6vw, 1.125rem);
  color: rgba(255, 255, 255, 0.55);
  max-width: 32rem;
  margin-left: auto;
  margin-right: auto;
}

/* Form card */
.form-card {
  background: linear-gradient(
    to bottom,
    color-mix(in oklch, var(--color-base-300) 82%, transparent) 0%,
    color-mix(in oklch, var(--color-base-300) 76%, transparent) 100%
  );
  backdrop-filter: blur(24px) saturate(140%);
  -webkit-backdrop-filter: blur(24px) saturate(140%);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 1.25rem;
  box-shadow:
    0 1px 0 rgba(255, 255, 255, 0.05) inset,
    0 20px 60px -20px rgba(0, 0, 0, 0.5);
}

.form-step + .form-step {
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  padding-top: 1.75rem;
}

.step-label {
  display: inline-flex;
  align-items: center;
  gap: 0.625rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
}

.step-num {
  width: 1.25rem;
  height: 1.25rem;
  border-radius: 50%;
  background: color-mix(in oklch, var(--color-primary) 18%, transparent);
  border: 1px solid color-mix(in oklch, var(--color-primary) 45%, transparent);
  color: var(--color-primary);
  font-size: 0.7rem;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.step-num-secondary {
  background: color-mix(in oklch, var(--color-secondary) 18%, transparent);
  border-color: color-mix(in oklch, var(--color-secondary) 45%, transparent);
  color: var(--color-secondary);
}

.step-value {
  font-size: 0.95rem;
  font-weight: 600;
  color: white;
  font-variant-numeric: tabular-nums;
}

/* Title: white with one accent word in gradient */
.logo-text {
  font-size: clamp(2.25rem, 7vw, 4.75rem);
  font-weight: 600;
  letter-spacing: -0.03em;
  line-height: 1;
  color: white;
  position: relative;
  display: inline-block;
  max-width: 100%;
}

.logo-accent {
  position: relative;
  background-image: linear-gradient(
    100deg,
    var(--color-primary) 0%,
    var(--color-secondary) 100%
  );
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

/* Subtle chromatic-aberration breathing on the "Playroom" word */
.logo-main {
  animation: chromatic-breathe 6s ease-in-out infinite;
}

@keyframes chromatic-breathe {
  0%, 100% {
    text-shadow:
      -0.8px 0 1px rgba(255, 60, 130, 0.35),
       0.8px 0 1px rgba(60, 200, 255, 0.35);
  }
  50% {
    text-shadow:
      -2px 0 1.5px rgba(255, 60, 130, 0.5),
       2px 0 1.5px rgba(60, 200, 255, 0.5);
  }
}

/* Hand-drawn squiggle under "Diet" */
.logo-squiggle {
  position: absolute;
  left: 0;
  right: 0;
  bottom: -0.05em;
  width: 100%;
  height: 0.18em;
  pointer-events: none;
  overflow: visible;
}

.squiggle-path {
  stroke-dasharray: 260;
  stroke-dashoffset: 260;
  animation: squiggle-draw 1.4s cubic-bezier(0.4, 0, 0.2, 1) 0.7s forwards;
  filter: drop-shadow(0 0 6px color-mix(in oklch, var(--color-primary) 60%, transparent));
}

@keyframes squiggle-draw {
  to { stroke-dashoffset: 0; }
}

/* Subtle ambient orbs behind the title — barely-there atmosphere */
.logo-orb {
  position: absolute;
  border-radius: 50%;
  pointer-events: none;
  filter: blur(36px);
  z-index: -1;
  will-change: transform, opacity;
}

.logo-orb-1 {
  top: -0.2em;
  left: -0.2em;
  width: 1.1em;
  height: 1.1em;
  background: color-mix(in oklch, var(--color-primary) 60%, transparent);
  animation: orb-drift-a 9s ease-in-out infinite;
}

.logo-orb-2 {
  bottom: -0.3em;
  right: -0.1em;
  width: 1.3em;
  height: 1.3em;
  background: color-mix(in oklch, var(--color-secondary) 50%, transparent);
  animation: orb-drift-b 11s ease-in-out infinite;
}

@keyframes orb-drift-a {
  0%, 100% { opacity: 0.2; transform: translate(0, 0) scale(1); }
  50%      { opacity: 0.35; transform: translate(15%, 8%) scale(1.1); }
}

@keyframes orb-drift-b {
  0%, 100% { opacity: 0.18; transform: translate(0, 0) scale(1); }
  50%      { opacity: 0.32; transform: translate(-12%, -10%) scale(1.08); }
}

/* Chromatic-aberration sparks — small white pixels with RGB ghost */
.spark {
  position: absolute;
  width: 3px;
  height: 3px;
  background: white;
  border-radius: 50%;
  pointer-events: none;
  opacity: 0;
  box-shadow:
    -1.5px 0 0 0 rgba(255, 50, 130, 0.75),
     1.5px 0 0 0 rgba(50, 200, 255, 0.75),
     0 0 6px 0 rgba(255, 255, 255, 0.4);
  animation: spark-twinkle 5s ease-in-out infinite;
}

.spark-1 { top: -8%; left: 6%;   width: 3px; height: 3px; animation-delay: 0.4s; }
.spark-2 { top: 18%;  right: 4%; width: 4px; height: 4px; animation-delay: 1.3s; }
.spark-3 { bottom: -8%; left: 28%; width: 2px; height: 2px; animation-delay: 2.2s; }
.spark-4 { top: -4%;  right: 22%; width: 3px; height: 3px; animation-delay: 3.0s; }
.spark-5 { top: 48%;  left: -2%; width: 2px; height: 2px; animation-delay: 3.8s; }
.spark-6 { bottom: -2%; right: 38%; width: 4px; height: 4px; animation-delay: 0.9s; }

@keyframes spark-twinkle {
  0%, 100% { opacity: 0; transform: scale(0.4); }
  20%, 70% { opacity: 0.95; transform: scale(1); }
}

/* Small pill above title */
.logo-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.75rem;
  margin-bottom: 0.75rem;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  font-size: 0.7rem;
  letter-spacing: 0.02em;
  color: rgba(255, 255, 255, 0.7);
}

.logo-pill-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--color-primary);
  box-shadow: 0 0 8px var(--color-primary);
  animation: logo-pill-pulse 2.4s ease-in-out infinite;
}

@keyframes logo-pill-pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.6; transform: scale(0.85); }
}

/* Range slider - pure custom, no daisyUI inheritance */
.range-aura {
  -webkit-appearance: none;
  appearance: none;
  width: 100%;
  height: 24px;
  background: transparent;
  cursor: pointer;
  padding: 0;
  margin: 0;
  border: none;
  outline: none;
  overflow: visible;
}

.range-aura:focus { outline: none; }

.range-aura::-webkit-slider-runnable-track {
  height: 6px;
  border-radius: 999px;
  background: linear-gradient(
    to right,
    var(--color-primary) 0%,
    var(--color-secondary) var(--progress, 0%),
    rgba(255, 255, 255, 0.08) var(--progress, 0%),
    rgba(255, 255, 255, 0.08) 100%
  );
}

.range-aura::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: white;
  margin-top: -7px;
  box-shadow:
    0 0 0 4px rgba(255, 255, 255, 0.06),
    0 2px 12px color-mix(in oklch, var(--color-primary) 60%, transparent);
  cursor: grab;
  transition: transform 0.15s ease;
  border: none;
}

.range-aura:active::-webkit-slider-thumb {
  transform: scale(1.12);
  cursor: grabbing;
  box-shadow:
    0 0 0 6px rgba(255, 255, 255, 0.08),
    0 2px 16px color-mix(in oklch, var(--color-primary) 70%, transparent);
}

.range-aura::-moz-range-track {
  height: 6px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.08);
  border: none;
}

.range-aura::-moz-range-progress {
  height: 6px;
  border-radius: 999px;
  background: linear-gradient(to right, var(--color-primary), var(--color-secondary));
}

.range-aura::-moz-range-thumb {
  width: 20px;
  height: 20px;
  border: none;
  border-radius: 50%;
  background: white;
  box-shadow:
    0 0 0 4px rgba(255, 255, 255, 0.06),
    0 2px 12px color-mix(in oklch, var(--color-primary) 60%, transparent);
  cursor: grab;
}

/* Dropzone - clean dashed, soft hover glow */
.dropzone {
  background: rgba(255, 255, 255, 0.02);
  border: 1px dashed rgba(255, 255, 255, 0.15);
  transition: all 0.25s ease;
}

.dropzone:hover {
  background: rgba(255, 255, 255, 0.04);
  border-color: color-mix(in oklch, var(--color-primary) 50%, transparent);
  box-shadow: 0 0 0 4px color-mix(in oklch, var(--color-primary) 10%, transparent);
}

.dropzone-filled {
  border-style: solid;
  border-color: color-mix(in oklch, var(--color-primary) 40%, transparent);
}

.dropzone-icon {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 0.75rem;
  background: color-mix(in oklch, var(--color-primary) 12%, transparent);
  border: 1px solid color-mix(in oklch, var(--color-primary) 25%, transparent);
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Submit button - calm gradient, no shine */
.btn-aura {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  border-radius: 999px;
  font-weight: 600;
  font-size: 0.95rem;
  color: white;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-secondary) 100%);
  border: 1px solid color-mix(in oklch, var(--color-primary) 60%, transparent);
  box-shadow:
    0 4px 16px color-mix(in oklch, var(--color-primary) 30%, transparent),
    inset 0 1px 0 rgba(255, 255, 255, 0.15);
  transition: transform 0.15s ease, box-shadow 0.2s ease, opacity 0.2s ease;
  cursor: pointer;
}

.btn-aura:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow:
    0 6px 20px color-mix(in oklch, var(--color-primary) 40%, transparent),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.btn-aura:active:not(:disabled) {
  transform: translateY(0);
}

.btn-aura:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-aura-arrow {
  transition: transform 0.2s ease;
}

.btn-aura:hover:not(:disabled) .btn-aura-arrow {
  transform: translateX(2px);
}

.pill-in {
  animation: pill-drop 0.4s cubic-bezier(0.34, 1.56, 0.64, 1) both;
}

@keyframes pill-drop {
  0% {
    opacity: 0;
    transform: translateY(-8px) scale(0.8);
  }
  100% {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.slide-fade-enter-active {
  transition: all 0.4s ease-out;
}
.slide-fade-leave-active {
  transition: all 0.2s ease-in;
}
.slide-fade-enter-from {
  opacity: 0;
  filter: blur(4px);
  transform: translateY(6px);
}
.slide-fade-leave-to {
  opacity: 0;
  filter: blur(2px);
}

.slide-progress {
  animation: progress-fill 6s linear;
}

@keyframes progress-fill {
  from { width: 0%; }
  to { width: 100%; }
}

.tech-badge:hover {
  box-shadow: 0 0 6px currentColor, 0 0 12px currentColor;
}

.gemini-badge {
  animation: fade-in-up 0.5s ease-out 1s both;
}

.gemini-spin {
  animation: gentle-spin 8s linear infinite;
}

@keyframes gentle-spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes fade-in-up {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
