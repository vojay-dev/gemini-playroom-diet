<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const scanId = route.params.id

const status = ref('loading')
const result = ref(null)
const error = ref(null)
let pollInterval = null

const fetchScan = async () => {
  try {
    const apiUrl = import.meta.env.GPD_API_URL || 'http://localhost:8000'
    const response = await fetch(`${apiUrl}/api/scan/${scanId}`)

    if (response.status === 404) {
      status.value = 'not_found'
      stopPolling()
      return
    }

    if (!response.ok) {
      throw new Error(`Failed to fetch scan: ${response.statusText}`)
    }

    const data = await response.json()
    status.value = data.status

    if (data.status === 'done') {
      result.value = data.result
      stopPolling()
    }
  } catch (e) {
    console.error(e)
    error.value = e.message
    status.value = 'error'
    stopPolling()
  }
}

const stopPolling = () => {
  if (pollInterval) {
    clearInterval(pollInterval)
    pollInterval = null
  }
}

onMounted(() => {
  fetchScan()
  pollInterval = setInterval(fetchScan, 30000)
})

onUnmounted(() => {
  stopPolling()
})
</script>

<template>
  <div class="min-h-[calc(100vh-68px)] flex items-center justify-center p-4">
    <div class="card w-full max-w-2xl bg-base-300/30 backdrop-blur-md border border-white/10 rounded-2xl">
      <div class="card-body">

        <!-- Loading State -->
        <div v-if="status === 'loading'" class="text-center py-8">
          <span class="loading loading-spinner loading-lg text-primary"></span>
          <p class="mt-4 text-lg">Loading scan...</p>
        </div>

        <!-- Processing State -->
        <div v-else-if="status === 'processing'" class="text-center py-8">
          <span class="loading loading-dots loading-lg text-primary"></span>
          <h2 class="text-2xl font-semibold mt-4">Analyzing your playroom...</h2>
          <p class="mt-2 opacity-70">This may take a minute. We're using AI to analyze the toys.</p>
          <p class="mt-4 text-sm opacity-50">Checking again in 30 seconds...</p>
          <p class="mt-2 font-mono text-xs opacity-40">Scan ID: {{ scanId }}</p>
        </div>

        <!-- Done State -->
        <div v-else-if="status === 'done'" class="py-4">
          <h2 class="text-2xl font-semibold text-success mb-4">Analysis Complete</h2>
          <div class="bg-base-100/50 rounded-lg p-4 overflow-auto max-h-96">
            <pre class="text-sm whitespace-pre-wrap">{{ JSON.stringify(result, null, 2) }}</pre>
          </div>
          <p class="mt-4 font-mono text-xs opacity-40">Scan ID: {{ scanId }}</p>
        </div>

        <!-- Not Found State -->
        <div v-else-if="status === 'not_found'" class="text-center py-8">
          <div class="text-6xl mb-4">🔍</div>
          <h2 class="text-2xl font-semibold text-error">Scan Not Found</h2>
          <p class="mt-2 opacity-70">The scan ID doesn't exist or has expired.</p>
          <p class="mt-4 font-mono text-xs opacity-40">Scan ID: {{ scanId }}</p>
          <RouterLink to="/" class="btn btn-primary mt-6">Back to Home</RouterLink>
        </div>

        <!-- Error State -->
        <div v-else-if="status === 'error'" class="text-center py-8">
          <div class="text-6xl mb-4">⚠️</div>
          <h2 class="text-2xl font-semibold text-error">Something went wrong</h2>
          <p class="mt-2 opacity-70">{{ error }}</p>
          <RouterLink to="/" class="btn btn-primary mt-6">Back to Home</RouterLink>
        </div>

      </div>
    </div>
  </div>
</template>
