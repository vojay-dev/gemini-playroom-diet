<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const scanId = route.params.id

const status = ref('loading')
const result = ref(null)
const error = ref(null)
const expandedItem = ref(0) // Which roadmap item is expanded
let pollInterval = null

// New structure: result is already parsed, no nested JSON
const roadmap = computed(() => result.value?.roadmap || [])
const skillScores = computed(() => result.value?.skill_scores || {})
const statusQuo = computed(() => result.value?.status_quo || '')

const timeframeLabels = {
  'now': { label: 'Start Now', icon: '🎯', color: 'primary' },
  '3_months': { label: 'In 3 Months', icon: '📅', color: 'secondary' },
  '6_months': { label: 'In 6 Months', icon: '🌟', color: 'accent' }
}

const getRetailers = (amazonSearch) => {
  if (!amazonSearch) return []
  const query = encodeURIComponent(amazonSearch)
  return [
    { name: 'Amazon', url: `https://www.amazon.com/s?k=${query}`, color: 'btn-warning' },
    { name: 'Target', url: `https://www.target.com/s?searchTerm=${query}`, color: 'btn-error' },
    { name: 'Walmart', url: `https://www.walmart.com/search?q=${query}`, color: 'btn-info' },
  ]
}

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
        <div class="card-body flex flex-col items-center text-center py-12">
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
      <template v-else-if="status === 'done' && roadmap.length">

        <!-- Header Card -->
        <div class="card bg-gradient-to-br from-primary/20 to-secondary/20 backdrop-blur-md border border-white/10 rounded-2xl">
          <div class="card-body text-center">
            <div class="text-5xl mb-2">🗺️</div>
            <h1 class="text-2xl md:text-3xl font-bold" style="font-family: 'Fredoka', sans-serif;">
              Your Development Roadmap
            </h1>
            <p class="opacity-70 mt-2">A personalized 6-month plan for your child's growth</p>
          </div>
        </div>

        <!-- Roadmap Timeline -->
        <div class="space-y-4">
          <div
            v-for="(item, index) in roadmap"
            :key="item.timeframe"
            class="card bg-base-300/30 backdrop-blur-md border border-white/10 rounded-2xl overflow-hidden"
          >
            <!-- Timeline Header (always visible) -->
            <div
              class="card-body cursor-pointer"
              @click="expandedItem = expandedItem === index ? -1 : index"
            >
              <div class="flex items-start gap-4">
                <!-- Timeline indicator -->
                <div class="flex flex-col items-center">
                  <div :class="[
                    'w-12 h-12 rounded-full flex items-center justify-center text-2xl',
                    `bg-${timeframeLabels[item.timeframe]?.color || 'primary'}/20`
                  ]">
                    {{ timeframeLabels[item.timeframe]?.icon || '📦' }}
                  </div>
                  <div v-if="index < roadmap.length - 1" class="w-0.5 h-8 bg-base-content/20 mt-2"></div>
                </div>

                <!-- Content -->
                <div class="flex-1">
                  <div class="flex items-center gap-2 flex-wrap">
                    <span :class="[
                      'badge',
                      `badge-${timeframeLabels[item.timeframe]?.color || 'primary'}`
                    ]">
                      {{ timeframeLabels[item.timeframe]?.label || item.timeframe }}
                    </span>
                    <span
                      v-if="item.decision === 'SUBSTITUTED'"
                      class="badge badge-warning badge-sm"
                    >
                      Safety Adjusted
                    </span>
                  </div>

                  <h3 class="text-xl font-bold mt-2" style="font-family: 'Fredoka', sans-serif;">
                    {{ item.final_toy || item.recommended_toy }}
                  </h3>

                  <p class="text-sm opacity-70 mt-1">
                    Develops: <span class="font-semibold text-secondary">{{ item.missing_skill }}</span>
                  </p>

                  <!-- Expand indicator -->
                  <div class="flex items-center gap-1 mt-2 text-xs opacity-50">
                    <svg
                      :class="['w-4 h-4 transition-transform', expandedItem === index ? 'rotate-180' : '']"
                      fill="none" viewBox="0 0 24 24" stroke="currentColor"
                    >
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                    </svg>
                    {{ expandedItem === index ? 'Less details' : 'More details' }}
                  </div>
                </div>
              </div>
            </div>

            <!-- Expanded Content -->
            <div v-if="expandedItem === index" class="px-6 pb-6 space-y-4">
              <div class="divider my-0"></div>

              <!-- Reasoning -->
              <div>
                <h4 class="font-semibold flex items-center gap-2 mb-2">
                  <span>🧠</span> Why This Toy?
                </h4>
                <p class="text-sm text-base-content/80 leading-relaxed">{{ item.reasoning }}</p>
              </div>

              <!-- Safety Context -->
              <div v-if="item.safety_context">
                <h4 class="font-semibold flex items-center gap-2 mb-2">
                  <span>🛡️</span> Safety Check
                  <span :class="[
                    'badge badge-sm',
                    item.decision === 'APPROVED' ? 'badge-success' : 'badge-warning'
                  ]">
                    {{ item.decision }}
                  </span>
                </h4>
                <p class="text-sm text-base-content/80 leading-relaxed">{{ item.safety_context }}</p>
              </div>

              <!-- O*NET Reference -->
              <div class="text-xs opacity-50">
                O*NET Skill: {{ item.missing_skill }} ({{ item.skill_id }}) • Category: {{ item.skill_category }}
              </div>

              <!-- Retailer Buttons -->
              <div class="flex flex-wrap gap-2 pt-2">
                <a
                  v-for="retailer in getRetailers(item.amazon_search)"
                  :key="retailer.name"
                  :href="retailer.url"
                  target="_blank"
                  rel="noopener noreferrer"
                  :class="['btn btn-sm gap-2', retailer.color]"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                  {{ retailer.name }}
                </a>
              </div>
            </div>
          </div>
        </div>

        <!-- Current Status Section -->
        <div class="collapse collapse-arrow bg-base-300/30 backdrop-blur-md border border-white/10 rounded-2xl">
          <input type="checkbox" />
          <div class="collapse-title text-lg font-semibold flex items-center gap-2">
            <span>📊</span> Current Playroom Analysis
          </div>
          <div class="collapse-content">
            <p class="text-base-content/80 leading-relaxed">{{ statusQuo }}</p>
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

      <!-- Fallback: Raw JSON if structure is unexpected -->
      <div v-else-if="status === 'done'" class="card bg-base-300/30 backdrop-blur-md border border-white/10 rounded-2xl">
        <div class="card-body">
          <h2 class="text-2xl font-semibold text-success mb-4">Analysis Complete</h2>
          <div class="bg-base-100/50 rounded-lg p-4 overflow-auto max-h-96">
            <pre class="text-sm whitespace-pre-wrap">{{ JSON.stringify(result, null, 2) }}</pre>
          </div>
          <RouterLink to="/" class="btn btn-primary mt-4">Back to Home</RouterLink>
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
