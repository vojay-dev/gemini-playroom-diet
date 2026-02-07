<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute } from 'vue-router'
let confetti = null
import SkillRadar from './SkillRadar.vue'
import ShareCard from './ShareCard.vue'

const route = useRoute()
const scanId = route.params.id
const isCached = computed(() => route.query.cached === '1')

const status = ref('loading')
const result = ref(null)
const error = ref(null)
const imageUrl = ref(null)
const childAge = ref(null)
const expandedItem = ref(0)
const showShareModal = ref(false)
const hasShownConfetti = ref(false)
let pollInterval = null
let messageInterval = null

const loadingMessages = [
  { text: "Wrangling neural networks...", icon: "🧠" },
  { text: "Building a LEGO castle...", icon: "🏰" },
  { text: "Teaching robots to play...", icon: "🤖" },
  { text: "Consulting the toy experts...", icon: "🧸" },
  { text: "Counting building blocks...", icon: "🧱" },
  { text: "Analyzing play patterns...", icon: "🔬" },
  { text: "Mapping skills to careers...", icon: "💼" },
  { text: "Checking safety guidelines...", icon: "🛡️" },
  { text: "Crafting your Play Quest...", icon: "🎮" },
  { text: "Connecting the dots...", icon: "✨" },
  { text: "Thinking like a 5-year-old...", icon: "🎨" },
  { text: "Calibrating fun detectors...", icon: "📡" },
]
const currentMessageIndex = ref(0)
const currentMessage = computed(() => loadingMessages[currentMessageIndex.value])

// Which agent is currently "active" (0-3) based on message rotation
const activeAgentIndex = computed(() => Math.floor(currentMessageIndex.value / 3) % 4)

const roadmap = computed(() => result.value?.roadmap || [])
const skillScores = computed(() => result.value?.skill_scores || {})
const statusQuo = computed(() => result.value?.status_quo || '')
const toyInventory = computed(() => result.value?.toy_inventory || [])
const playQuest = computed(() => result.value?.play_quest || null)
const activeTab = ref('roadmap')
const hoveredToyIndex = ref(null)

// Typewriter effect for analysis text
const typedStatusQuo = ref('')
let typewriterTimeout = null
watch(statusQuo, (text) => {
  if (!text) return
  typedStatusQuo.value = ''
  let i = 0
  function type() {
    if (i < text.length) {
      typedStatusQuo.value += text[i]
      i++
      typewriterTimeout = setTimeout(type, 12)
    }
  }
  type()
})

// Animated counters
const animatedToyCount = ref(0)
const animatedSafetyCount = ref(0)
function animateCounter(target, setter, duration = 1000) {
  const start = performance.now()
  function step(now) {
    const progress = Math.min((now - start) / duration, 1)
    const eased = 1 - Math.pow(1 - progress, 3)
    setter(Math.round(eased * target))
    if (progress < 1) requestAnimationFrame(step)
  }
  requestAnimationFrame(step)
}
watch(roadmap, (items) => {
  if (!items.length) return
  animateCounter(items.length, v => { animatedToyCount.value = v })
  animateCounter(items.filter(r => r.decision === 'APPROVED').length, v => { animatedSafetyCount.value = v })
})

const toggleToy = (index) => {
  hoveredToyIndex.value = hoveredToyIndex.value === index ? null : index
}

const projectedScores = computed(() => {
  if (!skillScores.value || !roadmap.value.length) return null
  const projected = { ...skillScores.value }
  roadmap.value.forEach((item, i) => {
    const category = item.skill_category
    if (category && projected[category] !== undefined) {
      projected[category] = Math.min(95, projected[category] + 15 + (i * 7 % 5))
    }
  })
  return projected
})

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
    { name: 'Google', url: `https://www.google.com/search?tbm=shop&q=${query}`, color: 'btn-neutral' },
  ]
}

const getCalendarUrl = (item) => {
  const toyName = item.final_toy || item.recommended_toy
  const title = encodeURIComponent(`Get toy: ${toyName}`)
  const details = encodeURIComponent(`Playroom Diet recommendation for your child's development.\n\nToy: ${toyName}\nSkill: ${item.missing_skill}\nReason: ${item.reasoning}`)

  // Calculate target date based on timeframe
  const now = new Date()
  let targetDate = new Date(now)
  if (item.timeframe === '3_months') {
    targetDate.setMonth(targetDate.getMonth() + 3)
  } else if (item.timeframe === '6_months') {
    targetDate.setMonth(targetDate.getMonth() + 6)
  }

  // Format as YYYYMMDD for Google Calendar (all-day event)
  const dateStr = targetDate.toISOString().split('T')[0].replace(/-/g, '')

  return `https://calendar.google.com/calendar/render?action=TEMPLATE&text=${title}&details=${details}&dates=${dateStr}/${dateStr}`
}

const copyLinkSuccess = ref(false)
const copyLink = async () => {
  try {
    await navigator.clipboard.writeText(window.location.href)
    copyLinkSuccess.value = true
    setTimeout(() => { copyLinkSuccess.value = false }, 2000)
  } catch (e) {
    console.error('Failed to copy link:', e)
  }
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
    imageUrl.value = data.image_url
    childAge.value = data.child_age

    if (data.status === 'done') {
      result.value = data.result
      stopPolling()
      if (!hasShownConfetti.value) {
        hasShownConfetti.value = true
        import('canvas-confetti').then(m => {
          confetti = m.default
          confetti({ particleCount: 100, spread: 70, origin: { y: 0.6 } })
        })
      }
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
  messageInterval = setInterval(() => {
    currentMessageIndex.value = (currentMessageIndex.value + 1) % loadingMessages.length
  }, 3000)
})

onUnmounted(() => {
  stopPolling()
  if (messageInterval) clearInterval(messageInterval)
  if (typewriterTimeout) clearTimeout(typewriterTimeout)
})
</script>

<template>
  <div class="min-h-[calc(100vh-68px)] flex items-start justify-center p-4 py-8">
    <!-- Loading/error states -->
    <div v-if="status !== 'done' || !roadmap.length" class="w-full max-w-2xl space-y-4">

      <!-- Loading -->
      <div v-if="status === 'loading'" class="card bg-base-300/30 backdrop-blur-md border border-white/10 rounded-2xl">
        <div class="card-body text-center py-12">
          <span class="loading loading-spinner loading-lg text-primary"></span>
          <p class="mt-4 text-lg">Loading scan...</p>
        </div>
      </div>

      <!-- Processing (includes 'in_flight' status from Airflow) -->
      <div v-else-if="status === 'processing' || status === 'in_flight'" class="card bg-base-300/30 backdrop-blur-md border border-white/10 rounded-2xl">
        <div class="card-body flex flex-col items-center text-center py-12">
          <h2 class="text-2xl font-semibold">Analyzing your playroom...</h2>

          <!-- Scanning image -->
          <div v-if="imageUrl" class="relative rounded-xl overflow-hidden my-6 shadow-lg">
            <img :src="imageUrl" alt="Your playroom" class="w-72 h-52 object-cover" />

            <!-- Overlay -->
            <div class="absolute inset-0 bg-black/40"></div>

            <!-- Sparkles -->
            <div class="sparkle s1"></div>
            <div class="sparkle s2"></div>
            <div class="sparkle s3"></div>
            <div class="sparkle s4"></div>
            <div class="sparkle s5"></div>
          </div>

          <!-- Rotating loading message -->
          <div class="my-4 h-12 flex flex-col items-center justify-center">
            <div
              :key="currentMessageIndex"
              class="loading-message flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-primary/20 to-secondary/20 border border-white/10"
            >
              <span class="text-lg animate-bounce">{{ currentMessage.icon }}</span>
              <span class="text-sm font-medium bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
                {{ currentMessage.text }}
              </span>
            </div>
          </div>

          <p class="text-sm opacity-50 mb-4">This may take a couple of minutes.</p>

          <div class="flex flex-wrap justify-center gap-2 max-w-sm">
            <div :class="['agent-badge badge gap-1.5 py-3 transition-all duration-500', activeAgentIndex === 0 ? 'badge-primary shadow-glow' : 'badge-ghost opacity-50']">
              <span>👁️</span> Detecting toys
            </div>
            <div :class="['agent-badge badge gap-1.5 py-3 transition-all duration-500', activeAgentIndex === 1 ? 'badge-secondary shadow-glow' : 'badge-ghost opacity-50']">
              <span>🧠</span> Mapping skills
            </div>
            <div :class="['agent-badge badge gap-1.5 py-3 transition-all duration-500', activeAgentIndex === 2 ? 'badge-warning shadow-glow' : 'badge-ghost opacity-50']">
              <span>🛡️</span> Safety check
            </div>
            <div :class="['agent-badge badge gap-1.5 py-3 transition-all duration-500', activeAgentIndex === 3 ? 'badge-accent shadow-glow' : 'badge-ghost opacity-50']">
              <span>🎮</span> Play Quest
            </div>
          </div>

          <div class="flex flex-col items-center mt-6 gap-2">
            <div class="flex items-center gap-2 text-xs opacity-50">
              <span class="loading loading-ring loading-xs text-primary"></span>
              Auto-refresh in 30s
            </div>
            <p class="font-mono text-xs opacity-30">{{ scanId }}</p>
          </div>
        </div>
      </div>

      <!-- Fallback -->
      <div v-else-if="status === 'done'" class="card bg-base-300/30 backdrop-blur-md border border-white/10 rounded-2xl">
        <div class="card-body">
          <h2 class="text-2xl font-semibold text-success mb-4">Analysis Complete</h2>
          <div class="bg-base-100/50 rounded-lg p-4 overflow-auto max-h-96">
            <pre class="text-sm whitespace-pre-wrap">{{ JSON.stringify(result, null, 2) }}</pre>
          </div>
          <RouterLink to="/" class="btn btn-primary mt-4">Back to Home</RouterLink>
        </div>
      </div>

      <!-- Not found -->
      <div v-else-if="status === 'not_found'" class="card bg-base-300/30 backdrop-blur-md border border-white/10 rounded-2xl">
        <div class="card-body text-center py-12">
          <div class="text-6xl mb-4">🔍</div>
          <h2 class="text-2xl font-semibold text-error">Scan Not Found</h2>
          <p class="mt-2 opacity-70">The scan ID doesn't exist or has expired.</p>
          <p class="mt-4 font-mono text-xs opacity-40">ID: {{ scanId }}</p>
          <RouterLink to="/" class="btn btn-primary mt-6">Back to Home</RouterLink>
        </div>
      </div>

      <!-- Error -->
      <div v-else-if="status === 'error'" class="card bg-base-300/30 backdrop-blur-md border border-white/10 rounded-2xl">
        <div class="card-body text-center py-12">
          <div class="text-6xl mb-4">⚠️</div>
          <h2 class="text-2xl font-semibold text-error">Something went wrong</h2>
          <p class="mt-2 opacity-70">{{ error }}</p>
          <RouterLink to="/" class="btn btn-primary mt-6">Back to Home</RouterLink>
        </div>
      </div>

    </div>

    <!-- Results -->
    <div v-else class="w-full max-w-6xl">
      <!-- Header -->
      <div class="result-header relative z-10 rounded-2xl mb-6 p-[1px] stagger-in overflow-visible" style="animation-delay: 0ms">
        <div class="absolute inset-0 rounded-2xl rotating-border"></div>
        <div class="relative card bg-base-300/80 rounded-2xl overflow-visible">
          <div class="card-body text-center py-5">
            <h1 class="text-2xl md:text-3xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent" style="font-family: 'Fredoka', sans-serif;">
              Your Development Roadmap
            </h1>
            <p class="opacity-60 text-sm mt-1">
              A personalized 6-month plan for your
              <span v-if="childAge" class="font-semibold text-primary">{{ childAge }}-year-old</span>
              <span v-else>child</span>'s growth
            </p>
            <div v-if="isCached" class="tooltip tooltip-bottom mt-1" data-tip="Results loaded from cache. The cache is based on the image hash. In case of a cache hit, the child's age from the cached run is used. It is automatically cleaned after a few days.">
              <span class="badge badge-ghost gap-1 cursor-help text-xs opacity-40">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Cached result
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Tabs -->
      <div class="relative p-1 rounded-2xl bg-base-300/30 backdrop-blur-md border border-white/10 mb-6 stagger-in" style="animation-delay: 150ms">
        <div
          class="tab-indicator absolute top-1 bottom-1 rounded-xl transition-all duration-300 ease-out"
          :class="activeTab === 'roadmap' ? 'bg-primary/20 shadow-[0_0_12px_var(--color-primary)]' : 'bg-accent/20 shadow-[0_0_12px_var(--color-accent)]'"
          :style="{ left: activeTab === 'roadmap' ? '4px' : playQuest ? '50%' : '4px', width: playQuest ? 'calc(50% - 4px)' : 'calc(100% - 8px)' }"
        />
        <div class="relative grid" :class="playQuest ? 'grid-cols-2' : 'grid-cols-1'">
          <button
            @click="activeTab = 'roadmap'"
            :class="[
              'flex items-center justify-center gap-2 py-3 px-4 rounded-xl transition-all duration-300 z-10 cursor-pointer',
              activeTab === 'roadmap' ? 'text-primary' : 'text-white/40 hover:text-white/70'
            ]"
          >
            <span>🗺️</span>
            <span class="font-semibold text-sm">6-Month Roadmap</span>
          </button>
          <button
            v-if="playQuest"
            @click="activeTab = 'quest'"
            :class="[
              'flex items-center justify-center gap-2 py-3 px-4 rounded-xl transition-all duration-300 z-10 cursor-pointer',
              activeTab === 'quest' ? 'text-accent' : 'text-white/40 hover:text-white/70'
            ]"
          >
            <span>🎮</span>
            <span class="font-semibold text-sm">Play Quest</span>
          </button>
        </div>
      </div>

      <!-- Grid -->
      <div v-if="activeTab === 'roadmap'" class="grid grid-cols-1 lg:grid-cols-5 gap-6">

        <!-- Roadmap -->
        <div class="lg:col-span-3 space-y-4">
          <div
            v-for="(item, index) in roadmap"
            :key="item.timeframe"
            class="card bg-base-300/30 backdrop-blur-md border border-white/10 rounded-2xl overflow-hidden"
          >
            <!-- Header -->
            <div
              class="card-body cursor-pointer"
              @click="expandedItem = expandedItem === index ? -1 : index"
            >
              <div class="flex items-start gap-4">
                <!-- Indicator -->
                <div class="flex flex-col items-center">
                  <div :class="[
                    'w-12 h-12 rounded-full flex items-center justify-center text-2xl',
                    `bg-${timeframeLabels[item.timeframe]?.color || 'primary'}/20`
                  ]">
                    {{ timeframeLabels[item.timeframe]?.icon || '📦' }}
                  </div>
                  <div v-if="index < roadmap.length - 1" class="w-0.5 h-8 bg-base-content/20 mt-2"></div>
                </div>

                <!-- Body -->
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

                  <h3 class="text-xl font-bold mt-2 bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent" style="font-family: 'Fredoka', sans-serif;">
                    {{ item.final_toy || item.recommended_toy }}
                  </h3>

                  <p class="text-sm opacity-70 mt-1">
                    Develops: <span class="font-semibold text-secondary">{{ item.missing_skill }}</span>
                  </p>

                  <!-- Expand -->
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

            <!-- Details -->
            <Transition name="expand">
            <div v-if="expandedItem === index" class="details-content px-6 pb-6 space-y-4">
              <div class="divider my-0"></div>

              <!-- Why -->
              <div>
                <h4 class="font-semibold flex items-center gap-2 mb-2">
                  <span>🧠</span> Why This Toy?
                </h4>
                <p class="text-sm text-base-content/80 leading-relaxed">{{ item.reasoning }}</p>
              </div>

              <!-- Safety -->
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

              <!-- Reference -->
              <div class="text-xs opacity-50">
                O*NET Skill: {{ item.missing_skill }} ({{ item.skill_id }}) • Category: {{ item.skill_category }}
              </div>

              <!-- Shop links -->
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
                <a
                  v-if="item.timeframe !== 'now'"
                  :href="getCalendarUrl(item)"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="btn btn-sm btn-outline btn-secondary gap-2"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  Add to Calendar
                </a>
              </div>
            </div>
            </Transition>
          </div>

          <!-- Analysis -->
          <div class="collapse collapse-arrow bg-base-300/30 backdrop-blur-md border border-white/10 rounded-2xl">
            <input type="checkbox" checked />
            <div class="collapse-title text-lg font-semibold flex items-center gap-2">
              <span>📊</span> Current Playroom Analysis
            </div>
            <div class="collapse-content">
              <!-- Heatmap -->
              <div v-if="imageUrl && toyInventory.length" class="relative rounded-xl overflow-hidden mb-4">
                <img :src="imageUrl" alt="Your playroom" class="w-full h-auto brightness-50" />

                <!-- Grid -->
                <div class="absolute inset-0 ai-grid"></div>

                <!-- Detection boxes -->
                <div
                  v-for="(toy, index) in toyInventory"
                  :key="index"
                  class="toy-box absolute cursor-pointer"
                  :class="{ 'is-active': hoveredToyIndex === index }"
                  :style="{
                    left: `${toy.bbox.x * 100}%`,
                    top: `${toy.bbox.y * 100}%`,
                    width: `${toy.bbox.w * 100}%`,
                    height: `${toy.bbox.h * 100}%`,
                    animationDelay: `${index * 0.15}s`
                  }"
                  @mouseenter="hoveredToyIndex = index"
                  @mouseleave="hoveredToyIndex = null"
                  @click.stop="toggleToy(index)"
                >
                  <!-- Tooltip -->
                  <div
                    class="toy-tooltip"
                    :class="{ 'is-visible': hoveredToyIndex === index }"
                  >
                    <span class="font-medium">{{ toy.item_name }}</span>
                    <span class="opacity-70 text-[10px]">{{ toy.play_mode }} · x{{ toy.count }}</span>
                  </div>

                  <!-- Corner accents -->
                  <div class="corner-accent top-0 left-0 border-t-2 border-l-2"></div>
                  <div class="corner-accent top-0 right-0 border-t-2 border-r-2"></div>
                  <div class="corner-accent bottom-0 left-0 border-b-2 border-l-2"></div>
                  <div class="corner-accent bottom-0 right-0 border-b-2 border-r-2"></div>
                </div>
              </div>
              <p class="text-base-content/80 leading-relaxed">{{ typedStatusQuo }}<span v-if="typedStatusQuo.length < statusQuo.length" class="typewriter-cursor">|</span></p>
              <!-- Legend -->
              <div v-if="toyInventory.length" class="mt-4 pt-4 border-t border-white/10">
                <p class="text-sm font-semibold mb-2">Detected Items:</p>
                <div class="flex flex-wrap gap-2">
                  <span
                    v-for="(toy, index) in toyInventory"
                    :key="index"
                    class="badge badge-dash badge-info"
                  >
                    {{ toy.item_name }} ({{ toy.count }})
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Sidebar -->
        <div class="lg:col-span-2 space-y-4">
          <!-- Radar -->
          <div class="card bg-base-300/30 backdrop-blur-md border border-white/10 rounded-2xl">
            <div class="card-body">
              <h2 class="text-lg font-semibold flex items-center gap-2 mb-2">
                <span>📈</span> Skill Development
              </h2>
              <SkillRadar
                :scores="skillScores"
                :projected-scores="projectedScores"
              />
              <p class="text-xs text-center opacity-50 mt-2">
                Dashed line shows projected improvement after completing the roadmap
              </p>
            </div>
          </div>

          <!-- Stats -->
          <div class="card bg-base-300/30 backdrop-blur-md border border-white/10 rounded-2xl">
            <div class="card-body">
              <h2 class="text-lg font-semibold flex items-center gap-2 mb-4">
                <span>✨</span> Quick Stats
              </h2>
              <div class="grid grid-cols-2 gap-3">
                <div class="text-center p-3 rounded-xl bg-base-100/30">
                  <div class="text-2xl font-bold text-primary">{{ animatedToyCount }}</div>
                  <div class="text-xs opacity-70">Toys Recommended</div>
                </div>
                <div class="text-center p-3 rounded-xl bg-base-100/30">
                  <div class="text-2xl font-bold text-secondary">6</div>
                  <div class="text-xs opacity-70">Skills Analyzed</div>
                </div>
                <div class="text-center p-3 rounded-xl bg-base-100/30">
                  <div class="text-2xl font-bold text-accent">6mo</div>
                  <div class="text-xs opacity-70">Roadmap Duration</div>
                </div>
                <div class="text-center p-3 rounded-xl bg-base-100/30">
                  <div class="text-2xl font-bold text-success">
                    {{ animatedSafetyCount }}/{{ animatedToyCount }}
                  </div>
                  <div class="text-xs opacity-70">Safety Approved</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Share -->
          <div class="card bg-gradient-to-br from-secondary/20 to-accent/20 backdrop-blur-md border border-white/10 rounded-2xl">
            <div class="card-body text-center">
              <h2 class="text-lg font-semibold">Share Your Results</h2>
              <p class="text-sm opacity-70 mb-4">Generate a shareable image of your roadmap!</p>
              <button @click="showShareModal = true" class="btn btn-secondary gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
                </svg>
                Share Results
              </button>
            </div>
          </div>
        </div>

      </div>

      <!-- Quest -->
      <div v-else-if="activeTab === 'quest' && playQuest" class="max-w-2xl mx-auto">
        <div class="card bg-gradient-to-br from-accent/20 to-secondary/20 backdrop-blur-md border border-white/10 rounded-2xl">
          <div class="card-body">
            <div class="flex items-center gap-3 mb-4">
              <div class="text-4xl">🎮</div>
              <div>
                <h2 class="text-2xl font-bold" style="font-family: 'Fredoka', sans-serif;">
                  {{ playQuest.title }}
                </h2>
                <p class="text-sm opacity-70">
                  Develops: <span class="font-semibold text-secondary">{{ playQuest.target_skill }}</span>
                </p>
              </div>
            </div>

            <div class="flex flex-wrap gap-2 mb-4">
              <div class="badge badge-outline gap-1">
                <span>⏱️</span> {{ playQuest.duration_minutes }} min
              </div>
              <div class="badge badge-outline gap-1">
                <span>🧠</span> {{ playQuest.skill_id }}
              </div>
            </div>

            <div class="space-y-4">
              <div>
                <h3 class="font-semibold flex items-center gap-2 mb-2">
                  <span>🧸</span> Toys Needed
                </h3>
                <div class="flex flex-wrap gap-2">
                  <span v-for="toy in playQuest.toys_needed" :key="toy" class="badge badge-primary">
                    {{ toy }}
                  </span>
                </div>
              </div>

              <div>
                <h3 class="font-semibold flex items-center gap-2 mb-2">
                  <span>📋</span> Setup
                </h3>
                <p class="text-base-content/80">{{ playQuest.setup }}</p>
              </div>

              <div>
                <h3 class="font-semibold flex items-center gap-2 mb-2">
                  <span>🎯</span> Instructions
                </h3>
                <ol class="list-decimal list-inside space-y-2 text-base-content/80">
                  <li v-for="(step, i) in playQuest.instructions" :key="i">{{ step }}</li>
                </ol>
              </div>

              <div class="bg-base-100/30 rounded-lg p-4 mt-4">
                <p class="text-sm">
                  <span class="font-semibold">💡 Parent Tip:</span>
                  {{ playQuest.parent_tip }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="mt-6 flex flex-col sm:flex-row items-center justify-between gap-4 p-4 rounded-2xl bg-base-300/20 backdrop-blur-sm border border-white/5">
        <p class="font-mono text-xs opacity-40">Scan ID: {{ scanId }}</p>
        <div class="flex gap-2">
          <button @click="copyLink" class="btn btn-secondary gap-2">
            <svg v-if="!copyLinkSuccess" xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            {{ copyLinkSuccess ? 'Copied!' : 'Copy Link' }}
          </button>
          <RouterLink to="/" class="btn btn-primary gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            Scan Another Room
          </RouterLink>
        </div>
      </div>

      <!-- Gemini Badge -->
      <div class="flex justify-center mt-6 mb-16">
        <a
          href="https://gemini3.devpost.com/"
          target="_blank"
          class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-base-300/30 backdrop-blur-md border border-white/10 hover:border-white/25 transition-all"
        >
          <img src="/gemini-color.png" alt="Gemini" class="w-5 h-5 gemini-spin" />
          <span class="text-xs opacity-60">Powered by</span>
          <span class="text-xs font-semibold">Gemini 3</span>
        </a>
      </div>

      <!-- Modal -->
      <ShareCard
        v-if="showShareModal"
        :roadmap="roadmap"
        :skill-scores="skillScores"
        @close="showShareModal = false"
      />
    </div>
  </div>
</template>

<style scoped>
/* sparkle */
.sparkle {
  position: absolute;
  width: 4px;
  height: 4px;
  background: white;
  border-radius: 50%;
  animation: sparkle-pop 2s ease-in-out infinite;
}

.sparkle::before,
.sparkle::after {
  content: '';
  position: absolute;
  background: white;
  border-radius: 2px;
}

.sparkle::before {
  width: 2px;
  height: 12px;
  left: 1px;
  top: -4px;
}

.sparkle::after {
  width: 12px;
  height: 2px;
  left: -4px;
  top: 1px;
}

/* positions */
.s1 { top: 20%; left: 15%; animation-delay: 0s; }
.s2 { top: 60%; left: 75%; animation-delay: 0.4s; }
.s3 { top: 35%; left: 55%; animation-delay: 0.8s; }
.s4 { top: 75%; left: 25%; animation-delay: 1.2s; }
.s5 { top: 45%; left: 85%; animation-delay: 1.6s; }

@keyframes sparkle-pop {
  0%, 100% {
    opacity: 0;
    transform: scale(0) rotate(0deg);
  }
  50% {
    opacity: 1;
    transform: scale(1) rotate(180deg);
  }
}

/* grid - base layer */
.ai-grid {
  background-image:
    linear-gradient(rgba(34, 211, 238, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(34, 211, 238, 0.05) 1px, transparent 1px);
  background-size: 24px 24px;
  mask-image: radial-gradient(ellipse at center, black 50%, transparent 90%);
  -webkit-mask-image: radial-gradient(ellipse at center, black 50%, transparent 90%);
}

/* grid - bright scan sweep */
.ai-grid::after {
  content: '';
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(34, 211, 238, 0.25) 1px, transparent 1px),
    linear-gradient(90deg, rgba(34, 211, 238, 0.25) 1px, transparent 1px);
  background-size: 24px 24px;
  mask-image:
    radial-gradient(ellipse at center, black 50%, transparent 90%),
    linear-gradient(to bottom, transparent 0%, rgba(0,0,0,0.8) 40%, black 50%, rgba(0,0,0,0.8) 60%, transparent 100%);
  mask-composite: intersect;
  -webkit-mask-image:
    linear-gradient(to bottom, transparent 0%, rgba(0,0,0,0.8) 40%, black 50%, rgba(0,0,0,0.8) 60%, transparent 100%);
  -webkit-mask-size: 100% 40%;
  -webkit-mask-repeat: no-repeat;
  mask-size: 100% 40%;
  mask-repeat: no-repeat;
  animation: grid-scan 4s ease-in-out infinite;
}

@keyframes grid-scan {
  0% { mask-position: 0 -40%; -webkit-mask-position: 0 -40%; }
  100% { mask-position: 0 140%; -webkit-mask-position: 0 140%; }
}

/* detection boxes */
.toy-box {
  background: linear-gradient(135deg, rgba(34, 211, 238, 0.22), rgba(168, 85, 247, 0.22));
  border: 1px solid rgba(34, 211, 238, 0.55);
  transition: all 0.3s ease;
  animation: box-appear 0.5s ease-out both;
}

.toy-box:hover,
.toy-box.is-active {
  background: linear-gradient(135deg, rgba(34, 211, 238, 0.2), rgba(168, 85, 247, 0.2));
  border-color: rgba(34, 211, 238, 0.8);
  box-shadow: 0 0 12px rgba(34, 211, 238, 0.3), inset 0 0 12px rgba(34, 211, 238, 0.1);
}

@keyframes box-appear {
  0% {
    opacity: 0;
    border-color: transparent;
  }
  100% {
    opacity: 1;
  }
}

/* corner accents */
.corner-accent {
  position: absolute;
  width: 8px;
  height: 8px;
  border-color: rgba(34, 211, 238, 0.6);
  transition: all 0.3s ease;
}

.toy-box:hover .corner-accent,
.toy-box.is-active .corner-accent {
  width: 12px;
  height: 12px;
  border-color: rgba(34, 211, 238, 1);
}

/* tooltip */
.toy-tooltip {
  position: absolute;
  bottom: calc(100% + 6px);
  left: 50%;
  transform: translateX(-50%) translateY(4px);
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(34, 211, 238, 0.3);
  border-radius: 8px;
  padding: 4px 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  white-space: nowrap;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.9);
  opacity: 0;
  pointer-events: none;
  transition: all 0.2s ease;
}

.toy-tooltip.is-visible {
  opacity: 1;
  transform: translateX(-50%) translateY(0);
}

/* loading message animation */
.loading-message {
  animation: message-pop 0.4s ease-out;
}

@keyframes message-pop {
  0% {
    opacity: 0;
    transform: scale(0.9) translateY(10px);
  }
  100% {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

/* result header */
.rotating-border {
  background: conic-gradient(
    from var(--border-angle, 0deg),
    var(--color-primary),
    var(--color-secondary),
    var(--color-accent),
    var(--color-primary)
  );
  animation: rotate-border 4s linear infinite;
  opacity: 0.5;
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  padding: 1.5px;
}

@keyframes rotate-border {
  to { --border-angle: 360deg; }
}

@property --border-angle {
  syntax: "<angle>";
  initial-value: 0deg;
  inherits: false;
}


.gemini-spin {
  animation: gemini-spin 8s linear infinite;
}

@keyframes gemini-spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* staggered entrance animation */
@keyframes fade-in-up {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.stagger-in {
  animation: fade-in-up 0.5s ease-out both;
}


/* agent badge glow */
.shadow-glow {
  box-shadow: 0 0 12px currentColor, 0 0 24px currentColor;
  animation: pulse-glow 1.5s ease-in-out infinite;
}

@keyframes pulse-glow {
  0%, 100% { box-shadow: 0 0 8px currentColor, 0 0 16px currentColor; }
  50% { box-shadow: 0 0 16px currentColor, 0 0 32px currentColor; }
}

/* expand transition for roadmap details */
.expand-enter-active,
.expand-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}

.expand-enter-from,
.expand-leave-to {
  opacity: 0;
  transform: translateY(-10px);
  max-height: 0;
  padding-top: 0;
  padding-bottom: 0;
}

.expand-enter-to,
.expand-leave-from {
  opacity: 1;
  transform: translateY(0);
  max-height: 500px;
}

/* typewriter cursor */
.typewriter-cursor {
  animation: blink 0.7s step-end infinite;
  color: var(--color-primary);
  font-weight: 300;
}

@keyframes blink {
  50% { opacity: 0; }
}
</style>
