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
  <div class="hero min-h-[calc(100vh-68px-40px)] py-8 pb-16 overflow-auto relative flex flex-col items-center justify-center">

    <div class="hero-content flex-col lg:flex-row-reverse lg:items-stretch gap-8 relative z-10">

      <!-- Info -->
      <div class="bg-base-300/30 backdrop-blur-md border border-white/10 rounded-2xl text-center lg:text-left w-full max-w-md flex flex-col justify-start overflow-hidden">
        <!-- Header -->
        <div class="bg-gradient-to-r from-secondary/20 to-primary/20 px-8 py-5 border-b border-white/10">
          <h1 class="text-4xl font-semibold bg-clip-text text-transparent title-shimmer" style="font-family: 'Fredoka', sans-serif;">
            Playroom Diet
          </h1>
          <p class="text-sm opacity-60 mt-1">Because play needs balance, just like a diet</p>
        </div>

        <div class="p-6">
          <div class="mb-5">
            <div class="overflow-hidden relative min-h-24">
              <transition name="slide-fade" mode="out-in">
                <p class="text-base" :key="currentSlide" v-html="slides[currentSlide]"></p>
              </transition>
            </div>
            <div class="flex gap-1 mt-3">
              <button
                v-for="(_, i) in slides"
                :key="i"
                @click="goToSlide(i)"
                class="h-1 flex-1 rounded-full bg-white/10 overflow-hidden cursor-pointer"
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

          <!-- Tech stack -->
          <p class="text-xs opacity-50 mb-3">Built with:</p>
          <div class="flex flex-wrap justify-center gap-1.5 mb-5">
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

          <!-- Links -->
          <div class="border-t border-white/10 pt-5">
            <p class="text-xs opacity-50 mb-3">Explore more:</p>
            <div class="flex gap-2 flex-wrap justify-center lg:justify-start">
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
          </div>
        </div>
      </div>

      <!-- Form -->
      <div class="card w-full max-w-md bg-base-300/30 backdrop-blur-md border border-white/10 rounded-2xl overflow-hidden">
        <!-- Header -->
        <div class="bg-gradient-to-r from-primary/20 to-secondary/20 px-6 py-4 border-b border-white/10">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <div>
              <h2 class="font-bold text-lg">Start Your Analysis</h2>
              <p class="text-xs opacity-60">2 steps to boost your child's development</p>
            </div>
          </div>
        </div>

        <form class="card-body pt-4" @submit.prevent="handleSubmit">

          <!-- Age -->
          <div class="form-control">
            <label class="label pb-3">
              <span class="label-text font-semibold flex items-center gap-2">
                <span class="w-5 h-5 rounded-full bg-primary text-primary-content text-xs flex items-center justify-center font-bold">1</span>
                Child's Age
              </span>
              <span class="label-text-alt text-primary font-bold w-20 text-right">
                {{ age }} Years
              </span>
            </label>
            <div class="flex items-end gap-3">
              <div class="flex-1">
                <input
                  type="range"
                  min="1"
                  max="12"
                  v-model="age"
                  class="range range-primary w-full"
                />
                <div class="w-full flex justify-between text-xs px-2 mt-2 opacity-50">
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
          <div class="form-control mt-4">
            <label class="label pb-3">
              <span class="label-text font-semibold flex items-center gap-2">
                <span class="w-5 h-5 rounded-full bg-secondary text-secondary-content text-xs flex items-center justify-center font-bold">2</span>
                Playroom Photo
              </span>
            </label>

            <!-- Upload -->
            <div class="flex flex-col items-center justify-center w-full">
                <label for="dropzone-file" class="flex flex-col items-center justify-center w-full h-36 border-2 border-dashed rounded-lg cursor-pointer bg-base-200/50 hover:bg-base-300/50 border-base-content/20 hover:border-primary/50 transition-all relative overflow-hidden group">

                    <!-- Preview -->
                    <img v-if="previewUrl" :src="previewUrl" class="absolute inset-0 w-full h-full object-cover opacity-90 group-hover:scale-105 transition-transform" />

                    <!-- Placeholder -->
                    <div v-else class="flex flex-col items-center justify-center pt-5 pb-6 text-base-content/50">
                        <svg class="w-8 h-8 mb-3 text-primary/50" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 20 16">
                            <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 13h3a3 3 0 0 0 0-6h-.025A5.56 5.56 0 0 0 16 6.5 5.5 5.5 0 0 0 5.207 5.021C5.137 5.017 5.071 5 5 5a4 4 0 0 0 0 8h2.167M10 15V6m0 0L8 8m2-2 2 2"/>
                        </svg>
                        <p class="mb-1 text-sm"><span class="font-bold text-primary">Click to upload</span></p>
                        <p class="text-xs">PNG, JPG or take a photo</p>
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
          <div class="form-control mt-5">
            <button class="btn btn-primary gap-2 w-full" :disabled="isSubmitting || isCompressing">
              <span v-if="isSubmitting || isCompressing" class="loading loading-spinner loading-sm"></span>
              <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              {{ isCompressing ? 'Optimizing...' : isSubmitting ? 'Analyzing...' : 'Analyze Playroom' }}
            </button>
          </div>

          <!-- Preview -->
          <div class="mt-4 pt-4 border-t border-white/10">
            <p class="text-xs text-center opacity-50 mb-2">You'll receive:</p>
            <div class="flex justify-center gap-4 text-xs">
              <div class="flex items-center gap-1 opacity-70">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                Skill Radar
              </div>
              <div class="flex items-center gap-1 opacity-70">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-secondary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
                </svg>
                Roadmap
              </div>
              <div class="flex items-center gap-1 opacity-70">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v13m0-13V6a2 2 0 112 2h-2zm0 0V5.5A2.5 2.5 0 109.5 8H12zm-7 4h14M5 12a2 2 0 110-4h14a2 2 0 110 4M5 12v7a2 2 0 002 2h10a2 2 0 002-2v-7" />
                </svg>
                Career Skills
              </div>
            </div>
          </div>
        </form>
      </div>
    </div>

    <!-- Gemini Hackathon Badge -->
    <a
      href="https://gemini3.devpost.com/"
      target="_blank"
      class="gemini-badge inline-flex items-center gap-2 px-4 py-2 rounded-full bg-base-300/30 backdrop-blur-md border border-white/10 hover:border-white/25 transition-all relative z-10 mt-4 mb-8"
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

.title-shimmer {
  background-image: linear-gradient(
    90deg,
    var(--color-primary) 0%,
    var(--color-secondary) 50%,
    var(--color-primary) 100%
  );
  background-size: 200% 100%;
  animation: shimmer 8s ease-in-out infinite;
}

@keyframes shimmer {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
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
