<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

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
  <div class="hero h-[calc(100vh-68px)] overflow-hidden relative">

    <div class="hero-content flex-col lg:flex-row-reverse lg:items-stretch gap-8 relative z-10">

      <!-- Text Section with glass card -->
      <div class="bg-base-300/30 backdrop-blur-md border border-white/10 p-8 rounded-2xl text-center lg:text-left w-full max-w-md flex flex-col justify-start">
        <h1 class="text-5xl font-semibold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent" style="font-family: 'Fredoka', sans-serif;">
          Playroom Diet
        </h1>
        <p class="py-6 text-lg">
          Turn your chaotic toy pile into a
          <span class="font-bold text-primary">science-backed</span>
          development plan. We use AI to audit your toys and find the missing skills.
        </p>

        <!-- Trust Indicators -->
        <div class="flex gap-4 flex-wrap justify-center lg:justify-start">
          <div class="badge badge-outline">🧠 Gemini 3</div>
          <div class="badge badge-outline">✨ Gemini 3 Vision</div>
          <div class="badge badge-outline">🧬 O*NET Data</div>
        </div>
      </div>

      <!-- The Form Card (glassmorphism) -->
      <div class="card w-full max-w-md bg-base-300/30 backdrop-blur-md border border-white/10 rounded-2xl">
        <form class="card-body" @submit.prevent="handleSubmit">

          <!-- Age Input -->
          <div class="form-control">
            <label class="label">
              <span class="label-text font-semibold">Child's Age</span>
              <span class="label-text-alt text-primary font-bold w-20 text-right">
                {{ age }} Years
              </span>
            </label>
            <input
              type="range"
              min="1"
              max="12"
              v-model="age"
              class="range range-primary range-sm"
            />
            <div class="w-full flex justify-between text-xs px-2 mt-2 opacity-50">
              <span>1</span><span>6</span><span>12</span>
            </div>
          </div>

          <!-- File Input -->
          <div class="form-control mt-4">
            <label class="label">
              <span class="label-text font-semibold">Playroom Photo</span>
            </label>

            <!-- Custom File Area -->
            <div class="flex flex-col items-center justify-center w-full">
                <label for="dropzone-file" class="flex flex-col items-center justify-center w-full h-40 border-2 border-dashed rounded-lg cursor-pointer bg-base-200 hover:bg-base-300 border-base-content/20 transition-all relative overflow-hidden group">

                    <!-- Preview Image (If exists) -->
                    <img v-if="previewUrl" :src="previewUrl" class="absolute inset-0 w-full h-full object-cover opacity-90 group-hover:scale-105 transition-transform" />

                    <!-- Placeholder UI -->
                    <div v-else class="flex flex-col items-center justify-center pt-5 pb-6 text-base-content/50">
                        <svg class="w-8 h-8 mb-4" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 20 16">
                            <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 13h3a3 3 0 0 0 0-6h-.025A5.56 5.56 0 0 0 16 6.5 5.5 5.5 0 0 0 5.207 5.021C5.137 5.017 5.071 5 5 5a4 4 0 0 0 0 8h2.167M10 15V6m0 0L8 8m2-2 2 2"/>
                        </svg>
                        <p class="mb-2 text-sm"><span class="font-bold">Click to upload</span></p>
                        <p class="text-xs">or take a photo</p>
                    </div>

                    <!-- Actual Input (Hidden) -->
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
          </div>

          <!-- Submit Button -->
          <div class="form-control mt-6">
            <button class="btn btn-primary" :disabled="isSubmitting">
              <span v-if="isSubmitting" class="loading loading-spinner"></span>
              {{ isSubmitting ? 'Analyzing...' : 'Audit My Room' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
</style>
