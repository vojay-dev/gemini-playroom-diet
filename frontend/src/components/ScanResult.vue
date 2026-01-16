<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const scanId = route.params.id

const status = ref('loading')
const result = ref(null)
const error = ref(null)
let pollInterval = null

const parsedResult = computed(() => {
  if (!result.value) return null
  try {
    const analysis = JSON.parse(result.value.analysis_result)
    const recommendation = JSON.parse(result.value.toy_recommendation)
    return { analysis, recommendation }
  } catch (e) {
    console.error('Failed to parse result:', e)
    return null
  }
})

const searchQuery = computed(() => {
  if (!parsedResult.value?.recommendation?.amazon_search) return null
  return encodeURIComponent(parsedResult.value.recommendation.amazon_search)
})

const retailers = computed(() => {
  if (!searchQuery.value) return []
  return [
    { name: 'Amazon', url: `https://www.amazon.com/s?k=${searchQuery.value}`, color: 'btn-warning' },
    { name: 'Target', url: `https://www.target.com/s?searchTerm=${searchQuery.value}`, color: 'btn-error' },
    { name: 'Walmart', url: `https://www.walmart.com/search?q=${searchQuery.value}`, color: 'btn-info' },
  ]
})

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
  <div class="min-h-[calc(100vh-68px)] flex items-start justify-center p-4 py-8">
    <div class="w-full max-w-2xl space-y-4">

      <!-- Loading State -->
      <div v-if="status === 'loading'" class="card bg-base-300/30 backdrop-blur-md border border-white/10 rounded-2xl">
        <div class="card-body text-center py-12">
          <span class="loading loading-spinner loading-lg text-primary"></span>
          <p class="mt-4 text-lg">Loading scan...</p>
        </div>
      </div>

      <!-- Processing State -->
      <div v-else-if="status === 'processing'" class="card bg-base-300/30 backdrop-blur-md border border-white/10 rounded-2xl">
        <div class="card-body text-center py-12">
          <span class="loading loading-dots loading-lg text-primary"></span>
          <h2 class="text-2xl font-semibold mt-4">Analyzing your playroom...</h2>
          <p class="mt-2 opacity-70">This may take a minute. We're using AI to analyze the toys.</p>
          <div class="flex flex-col items-center mt-6 gap-2">
            <div class="flex items-center gap-2 text-sm opacity-50">
              <span class="loading loading-ring loading-xs"></span>
              Checking again in 30 seconds...
            </div>
            <p class="font-mono text-xs opacity-40">ID: {{ scanId }}</p>
          </div>
        </div>
      </div>

      <!-- Done State -->
      <template v-else-if="status === 'done' && parsedResult">

        <!-- Hero Card: Recommendation -->
        <div class="card bg-gradient-to-br from-primary/20 to-secondary/20 backdrop-blur-md border border-white/10 rounded-2xl">
          <div class="card-body text-center">
            <div class="text-5xl mb-2">🧩</div>
            <h2 class="text-xl font-semibold opacity-70">We recommend</h2>
            <h1 class="text-2xl md:text-3xl font-bold text-primary" style="font-family: 'Fredoka', sans-serif;">
              {{ parsedResult.recommendation.recommended_toy }}
            </h1>

            <!-- Retailer Buttons -->
            <div v-if="retailers.length" class="flex flex-wrap justify-center gap-2 mt-4">
              <a
                v-for="retailer in retailers"
                :key="retailer.name"
                :href="retailer.url"
                target="_blank"
                rel="noopener noreferrer"
                :class="['btn gap-2', retailer.color]"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
                {{ retailer.name }}
              </a>
            </div>
          </div>
        </div>

        <!-- Missing Skill Badge -->
        <div class="card bg-base-300/30 backdrop-blur-md border border-white/10 rounded-2xl">
          <div class="card-body">
            <div class="flex items-center gap-3">
              <div class="text-3xl">🎯</div>
              <div>
                <h3 class="text-sm font-semibold opacity-70">Missing Skill Identified</h3>
                <p class="text-lg font-bold text-secondary">{{ parsedResult.analysis.missing_skill }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Analysis Section -->
        <div class="collapse collapse-arrow bg-base-300/30 backdrop-blur-md border border-white/10 rounded-2xl">
          <input type="checkbox" checked />
          <div class="collapse-title text-lg font-semibold flex items-center gap-2">
            <span>🧠</span> Why This Toy?
          </div>
          <div class="collapse-content">
            <p class="text-base-content/80 leading-relaxed">{{ parsedResult.analysis.reasoning }}</p>
          </div>
        </div>

        <!-- Current Status Section -->
        <div class="collapse collapse-arrow bg-base-300/30 backdrop-blur-md border border-white/10 rounded-2xl">
          <input type="checkbox" />
          <div class="collapse-title text-lg font-semibold flex items-center gap-2">
            <span>📊</span> Current Playroom Analysis
          </div>
          <div class="collapse-content">
            <p class="text-base-content/80 leading-relaxed">{{ parsedResult.analysis.status_quo }}</p>
          </div>
        </div>

        <!-- Safety Section -->
        <div class="collapse collapse-arrow bg-base-300/30 backdrop-blur-md border border-white/10 rounded-2xl">
          <input type="checkbox" />
          <div class="collapse-title text-lg font-semibold flex items-center gap-2">
            <span>🛡️</span> Safety Information
          </div>
          <div class="collapse-content">
            <div class="flex items-start gap-2">
              <span class="badge badge-success badge-sm mt-1">{{ parsedResult.recommendation.decision }}</span>
              <p class="text-base-content/80 leading-relaxed text-sm">{{ parsedResult.recommendation.safety_context }}</p>
            </div>
          </div>
        </div>

        <!-- Scan Again -->
        <div class="text-center pt-4">
          <RouterLink to="/" class="btn btn-ghost btn-sm opacity-70">
            ← Scan Another Room
          </RouterLink>
          <p class="font-mono text-xs opacity-30 mt-2">ID: {{ scanId }}</p>
        </div>

      </template>

      <!-- Fallback: Raw JSON if parsing failed -->
      <div v-else-if="status === 'done' && !parsedResult" class="card bg-base-300/30 backdrop-blur-md border border-white/10 rounded-2xl">
        <div class="card-body">
          <h2 class="text-2xl font-semibold text-success mb-4">Analysis Complete</h2>
          <div class="bg-base-100/50 rounded-lg p-4 overflow-auto max-h-96">
            <pre class="text-sm whitespace-pre-wrap">{{ JSON.stringify(result, null, 2) }}</pre>
          </div>
        </div>
      </div>

      <!-- Not Found State -->
      <div v-else-if="status === 'not_found'" class="card bg-base-300/30 backdrop-blur-md border border-white/10 rounded-2xl">
        <div class="card-body text-center py-12">
          <div class="text-6xl mb-4">🔍</div>
          <h2 class="text-2xl font-semibold text-error">Scan Not Found</h2>
          <p class="mt-2 opacity-70">The scan ID doesn't exist or has expired.</p>
          <p class="mt-4 font-mono text-xs opacity-40">ID: {{ scanId }}</p>
          <RouterLink to="/" class="btn btn-primary mt-6">Back to Home</RouterLink>
        </div>
      </div>

      <!-- Error State -->
      <div v-else-if="status === 'error'" class="card bg-base-300/30 backdrop-blur-md border border-white/10 rounded-2xl">
        <div class="card-body text-center py-12">
          <div class="text-6xl mb-4">⚠️</div>
          <h2 class="text-2xl font-semibold text-error">Something went wrong</h2>
          <p class="mt-2 opacity-70">{{ error }}</p>
          <RouterLink to="/" class="btn btn-primary mt-6">Back to Home</RouterLink>
        </div>
      </div>

    </div>
  </div>
</template>
