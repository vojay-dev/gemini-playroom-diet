<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import PlayroomScene from './components/PlayroomScene.vue'

const isNightTheme = ref(true)
const scansToday = ref(0)
const dailyLimit = ref(20)
const dropdownRef = ref(null)
let limitsInterval = null

const closeMenu = () => {
  // Blur the active element to close the dropdown
  document.activeElement?.blur()
}

const usagePercent = computed(() => Math.min(100, (scansToday.value / dailyLimit.value) * 100))

const fetchLimits = async () => {
  try {
    const apiUrl = import.meta.env.GPD_API_URL || 'http://localhost:8000'
    const response = await fetch(`${apiUrl}/api/limits`)
    if (response.ok) {
      const data = await response.json()
      scansToday.value = data.scans_today
      dailyLimit.value = data.daily_scan_limit
    }
  } catch (e) {
    // silently fail - limits display is non-critical
  }
}

const toggleTheme = () => {
  isNightTheme.value = !isNightTheme.value
  const newTheme = isNightTheme.value ? 'night' : 'dracula'
  document.documentElement.setAttribute('data-theme', newTheme)
  localStorage.setItem('theme', newTheme)
}

onMounted(() => {
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme === 'dracula') {
    isNightTheme.value = false
    document.documentElement.setAttribute('data-theme', 'dracula')
  }

  fetchLimits()
  limitsInterval = setInterval(fetchLimits, 30000)
})

onUnmounted(() => {
  if (limitsInterval) clearInterval(limitsInterval)
})
</script>

<template>
  <!-- Playroom Wall Pattern Background -->
  <div class="playroom-wall fixed inset-0 z-0"></div>

  <!-- Global 3D Background -->
  <PlayroomScene class="!fixed inset-0 z-[1] pointer-events-none" />

  <header class="relative z-20">
    <div class="navbar bg-base-300/30 backdrop-blur-md border-b border-white/10">
      <div class="navbar-start">
        <div class="dropdown" ref="dropdownRef">
          <div tabindex="0" role="button" class="btn btn-ghost btn-circle">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"> <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h7" /> </svg>
          </div>
          <ul
            tabindex="-1"
            class="menu menu-md dropdown-content bg-base-100 rounded-box z-50 mt-3 w-52 p-2 shadow">
            <li><RouterLink to="/" @click="closeMenu" v-bind:class="{ 'menu-active': $route.fullPath === '/' }"><svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" /></svg> Home</RouterLink></li>
            <li><RouterLink to="/system" @click="closeMenu" v-bind:class="{ 'menu-active': $route.fullPath === '/system' }"><svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-warning" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" /></svg> System</RouterLink></li>
            <li><RouterLink to="/about" @click="closeMenu" v-bind:class="{ 'menu-active': $route.fullPath === '/about' }"><svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg> About</RouterLink></li>
          </ul>
        </div>
      </div>
      <div class="navbar-center">
        <a class="btn btn-ghost text-xl">Gemini Playroom Diet</a>
      </div>
      <div class="navbar-end gap-2">
        <!-- Usage Display -->
        <div class="flex items-center gap-1.5 px-3 py-1 rounded-full bg-base-100/50 border border-white/10 text-sm">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 opacity-70" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          <span class="font-mono" :class="usagePercent >= 90 ? 'text-error' : usagePercent >= 70 ? 'text-warning' : 'text-success'">
            {{ scansToday }}/{{ dailyLimit }}
          </span>
        </div>
        <!-- Theme Toggle: Boy (night) / Girl (dracula) -->
        <label class="swap swap-rotate btn btn-ghost btn-circle" @click="toggleTheme">
          <!-- Boy icon (night theme) -->
          <svg
            :class="isNightTheme ? 'swap-off' : 'swap-on'"
            class="h-6 w-6 fill-current"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24">
            <path d="M12 2C9.24 2 7 4.24 7 7s2.24 5 5 5 5-2.24 5-5-2.24-5-5-5zm0 8c-1.65 0-3-1.35-3-3s1.35-3 3-3 3 1.35 3 3-1.35 3-3 3zm0 4c-4.42 0-8 1.79-8 4v2h16v-2c0-2.21-3.58-4-8-4z"/>
          </svg>
          <!-- Girl icon (dracula theme) -->
          <svg
            :class="isNightTheme ? 'swap-on' : 'swap-off'"
            class="h-6 w-6 fill-current"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24">
            <path d="M12 2C9.24 2 7 4.24 7 7c0 1.64.8 3.09 2.03 4H7l-1 8h2l.5-4h7l.5 4h2l-1-8h-2.03c1.23-.91 2.03-2.36 2.03-4 0-2.76-2.24-5-5-5zm0 2c1.65 0 3 1.35 3 3s-1.35 3-3 3-3-1.35-3-3 1.35-3 3-3zm-2.5 9h5l.25 2h-5.5l.25-2z"/>
          </svg>
        </label>
      </div>
    </div>
  </header>
  <main class="relative z-10">
    <RouterView />
  </main>
  <footer class="footer footer-center p-1 px-2 text-neutral-content fixed bottom-0 z-50 bg-base-300/30 backdrop-blur-md border-t border-white/10">
    <aside class="items-center grid-flow-col">
      <p>© 2026 Volker Janz</p>
      <nav class="grid-flow-col gap-1 md:place-self-center md:justify-self-end">
        <a class="btn btn-ghost text-xl" href="https://www.vojay.io/" target="_blank">
          <svg xmlns="http://www.w3.org/2000/svg" width=".8em" height=".8em" viewBox="0 0 24 24"><g fill="none"><path d="M24 0v24H0V0zM12.593 23.258l-.011.002l-.071.035l-.02.004l-.014-.004l-.071-.035c-.01-.004-.019-.001-.024.005l-.004.01l-.017.428l.005.02l.01.013l.104.074l.015.004l.012-.004l.104-.074l.012-.016l.004-.017l-.017-.427c-.002-.01-.009-.017-.017-.018m.265-.113l-.013.002l-.185.093l-.01.01l-.003.011l.018.43l.005.012l.008.007l.201.093c.012.004.023 0 .029-.008l.004-.014l-.034-.614c-.003-.012-.01-.02-.02-.022m-.715.002a.023.023 0 0 0-.027.006l-.006.014l-.034.614c0 .012.007.02.017.024l.015-.002l.201-.093l.01-.008l.004-.011l.017-.43l-.003-.012l-.01-.01z"/><path fill="currentColor" d="M19 4a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2zm0 6H5v7a1 1 0 0 0 .883.993L6 18h12a1 1 0 0 0 .993-.883L19 17zM6 6a1 1 0 1 0 0 2a1 1 0 0 0 0-2m3 0a1 1 0 1 0 0 2a1 1 0 0 0 0-2m3 0a1 1 0 1 0 0 2a1 1 0 0 0 0-2"/></g></svg>
        </a>
        <a class="btn btn-ghost text-xl" href="https://github.com/vojay-dev" target="_blank">
          <svg xmlns="http://www.w3.org/2000/svg" width=".8em" height=".8em" viewBox="-2 -2 24 24"><path fill="currentColor" d="M18.88 1.099C18.147.366 17.265 0 16.233 0H3.746C2.714 0 1.832.366 1.099 1.099C.366 1.832 0 2.714 0 3.746v12.487c0 1.032.366 1.914 1.099 2.647c.733.733 1.615 1.099 2.647 1.099H6.66c.19 0 .333-.007.429-.02a.504.504 0 0 0 .286-.169c.095-.1.143-.245.143-.435l-.007-.885c-.004-.564-.006-1.01-.006-1.34l-.3.052c-.19.035-.43.05-.721.046a5.555 5.555 0 0 1-.904-.091a2.026 2.026 0 0 1-.872-.39a1.651 1.651 0 0 1-.572-.8l-.13-.3a3.25 3.25 0 0 0-.41-.663c-.186-.243-.375-.407-.566-.494l-.09-.065a.956.956 0 0 1-.17-.156a.723.723 0 0 1-.117-.182c-.026-.061-.004-.111.065-.15c.07-.04.195-.059.378-.059l.26.04c.173.034.388.138.643.311a2.1 2.1 0 0 1 .631.677c.2.355.44.626.722.813c.282.186.566.28.852.28c.286 0 .533-.022.742-.065a2.59 2.59 0 0 0 .585-.196c.078-.58.29-1.028.637-1.34a8.907 8.907 0 0 1-1.333-.234a5.314 5.314 0 0 1-1.223-.507a3.5 3.5 0 0 1-1.047-.872c-.277-.347-.505-.802-.683-1.365c-.177-.564-.266-1.215-.266-1.952c0-1.049.342-1.942 1.027-2.68c-.32-.788-.29-1.673.091-2.652c.252-.079.625-.02 1.119.175c.494.195.856.362 1.086.5c.23.14.414.257.553.352a9.233 9.233 0 0 1 2.497-.338c.859 0 1.691.113 2.498.338l.494-.312a6.997 6.997 0 0 1 1.197-.572c.46-.174.81-.221 1.054-.143c.39.98.424 1.864.103 2.653c.685.737 1.028 1.63 1.028 2.68c0 .737-.089 1.39-.267 1.957c-.177.568-.407 1.023-.689 1.366a3.65 3.65 0 0 1-1.053.865c-.42.234-.828.403-1.223.507a8.9 8.9 0 0 1-1.333.235c.45.39.676 1.005.676 1.846v3.11c0 .147.021.266.065.357a.36.36 0 0 0 .208.189c.096.034.18.056.254.064c.074.01.18.013.318.013h2.914c1.032 0 1.914-.366 2.647-1.099c.732-.732 1.099-1.615 1.099-2.647V3.746c0-1.032-.367-1.914-1.1-2.647z"/></svg>
        </a>
        <a class="btn btn-ghost text-xl" href="https://www.linkedin.com/in/vjanz/" target="_blank">
          <svg xmlns="http://www.w3.org/2000/svg" width=".8em" height=".8em" viewBox="0 0 16 16"><path fill="currentColor" fill-rule="evenodd" d="M3 1a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V3a2 2 0 0 0-2-2zm1.102 4.297a1.195 1.195 0 1 0 0-2.39a1.195 1.195 0 0 0 0 2.39m1 7.516V6.234h-2v6.579zM6.43 6.234h2v.881c.295-.462.943-1.084 2.148-1.084c1.438 0 2.219.953 2.219 2.766c0 .087.008.484.008.484v3.531h-2v-3.53c0-.485-.102-1.438-1.18-1.438c-1.079 0-1.17 1.198-1.195 1.982v2.986h-2z" clip-rule="evenodd"/></svg>
        </a>
      </nav>
    </aside>
  </footer>
</template>

<style scoped>
/* Playroom - soft colorful confetti/sprinkles pattern */
.playroom-wall {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #1a1a2e 100%);
  background-attachment: fixed;
}

.playroom-wall::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image:
    /* Yellow stars */
    radial-gradient(circle at 10% 20%, #f1c40f 3px, transparent 3px),
    radial-gradient(circle at 85% 15%, #f1c40f 2px, transparent 2px),
    radial-gradient(circle at 45% 80%, #f1c40f 2.5px, transparent 2.5px),
    radial-gradient(circle at 70% 60%, #f1c40f 2px, transparent 2px),
    /* Pink circles */
    radial-gradient(circle at 20% 70%, #e91e63 4px, transparent 4px),
    radial-gradient(circle at 90% 45%, #e91e63 3px, transparent 3px),
    radial-gradient(circle at 55% 25%, #e91e63 2.5px, transparent 2.5px),
    /* Cyan dots */
    radial-gradient(circle at 30% 40%, #00bcd4 3px, transparent 3px),
    radial-gradient(circle at 75% 85%, #00bcd4 2.5px, transparent 2.5px),
    radial-gradient(circle at 15% 90%, #00bcd4 2px, transparent 2px),
    /* Green dots */
    radial-gradient(circle at 60% 50%, #2ecc71 3px, transparent 3px),
    radial-gradient(circle at 5% 55%, #2ecc71 2px, transparent 2px),
    radial-gradient(circle at 95% 75%, #2ecc71 2.5px, transparent 2.5px),
    /* Orange dots */
    radial-gradient(circle at 40% 10%, #e67e22 2.5px, transparent 2.5px),
    radial-gradient(circle at 80% 30%, #e67e22 3px, transparent 3px),
    radial-gradient(circle at 25% 95%, #e67e22 2px, transparent 2px),
    /* Purple dots */
    radial-gradient(circle at 50% 65%, #9b59b6 2.5px, transparent 2.5px),
    radial-gradient(circle at 65% 5%, #9b59b6 2px, transparent 2px),
    radial-gradient(circle at 35% 55%, #9b59b6 3px, transparent 3px);
  background-size: 400px 400px;
  opacity: 0.6;
}
</style>
