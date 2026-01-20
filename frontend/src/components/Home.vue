<script setup>
import { ref } from 'vue'
import { useRouter, RouterLink } from 'vue-router'

const router = useRouter()
const age = ref(4)
const file = ref(null)
const previewUrl = ref(null)
const isSubmitting = ref(false)

const handleFileChange = (event) => {
  const selected = event.target.files[0]
  if (!selected) return
  file.value = selected
  previewUrl.value = URL.createObjectURL(selected)
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

    file.value = exampleFile
    previewUrl.value = URL.createObjectURL(blob)
  } catch (e) {
    console.error('Failed to load example:', e)
  }
}

const handleSubmit = async () => {
  if (!file.value) return alert("Please select a photo first!")

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
    router.push(`/scan/${data.scan_id}`)

  } catch (e) {
    console.error(e)
    alert("Error uploading scan. Is the backend running?")
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="hero min-h-[calc(100vh-68px-40px)] py-8 pb-16 overflow-auto relative">

    <div class="hero-content flex-col lg:flex-row-reverse lg:items-stretch gap-8 relative z-10">

      <!-- Info -->
      <div class="bg-base-300/30 backdrop-blur-md border border-white/10 rounded-2xl text-center lg:text-left w-full max-w-md flex flex-col justify-start overflow-hidden">
        <!-- Header -->
        <div class="bg-gradient-to-r from-secondary/20 to-primary/20 px-8 py-5 border-b border-white/10">
          <h1 class="text-4xl font-semibold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent" style="font-family: 'Fredoka', sans-serif;">
            Playroom Diet
          </h1>
          <p class="text-sm opacity-60 mt-1">AI-powered child development analysis</p>
        </div>

        <div class="p-6">
          <p class="text-base mb-6">
            Turn toy chaos into a
            <span class="font-bold text-primary">science-backed</span>
            growth plan. Get a 6-month roadmap, plus a Play Quest to start today with what you have.
          </p>

          <!-- Tech stack -->
          <p class="text-xs opacity-50 mb-3">Built with:</p>
          <div class="flex flex-wrap justify-center gap-3 mb-5">
            <div class="badge badge-md badge-soft badge-primary gap-1 p-2">
              <span>🤖</span> Gemini 3 Flash
            </div>
            <div class="badge badge-md badge-soft badge-primary gap-1 p-2">
              <span>🌀</span> Apache Airflow
            </div>
            <div class="badge badge-md badge-soft badge-primary gap-1 p-2">
              <span>⚡</span> FastAPI
            </div>
            <div class="badge badge-md badge-soft badge-primary gap-1 p-2">
              <span>💚</span> Vue.js 3
            </div>
            <div class="badge badge-md badge-soft badge-primary gap-1 p-2">
              <span>🎨</span> Tailwind CSS
            </div>
            <div class="badge badge-md badge-soft badge-primary gap-1 p-2">
              <span>🗄️</span> Postgres
            </div>
            <div class="badge badge-md badge-soft badge-primary gap-1 p-2">
              <span>🐍</span> Python
            </div>
            <div class="badge badge-md badge-soft badge-primary gap-1 p-2">
              <span>📊</span> O*NET Data
            </div>
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
              <p class="text-xs opacity-60">Just 2 steps to optimize your playroom</p>
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
            <div class="w-full">
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
                      capture="environment"
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
            <button class="btn btn-primary gap-2" :disabled="isSubmitting">
              <span v-if="isSubmitting" class="loading loading-spinner loading-sm"></span>
              <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              {{ isSubmitting ? 'Analyzing...' : 'Analyze Playroom' }}
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
                Toy Picks
              </div>
            </div>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
