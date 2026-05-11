<script setup>
import { ref, onMounted, onUnmounted, computed, nextTick } from 'vue'
import PlayroomScene from './components/PlayroomScene.vue'
import { useToast } from './composables/useToast'

const { toasts } = useToast()

const isNightTheme = ref(true)
const scansToday = ref(null)
const dailyLimit = ref(20)
const dropdownRef = ref(null)
const ottoOpen = ref(false)
const ottoCmd = ref('')
const ottoLines = ref([])
const ottoInput = ref(null)
let limitsInterval = null

const ottoToggle = async () => {
  ottoOpen.value = !ottoOpen.value
  if (ottoOpen.value) {
    await nextTick()
    ottoInput.value?.focus()
  }
}

const ottoClose = () => {
  ottoOpen.value = false
}

const escapeHtml = (s) => s.replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]))

const ottoExec = () => {
  const raw = ottoCmd.value.trim()
  if (!raw) return
  const cmd = raw.toLowerCase()
  ottoLines.value.push({ type: 'echo', text: raw })

  if (cmd === '/otto' || cmd === 'otto') {
    ottoLines.value.push({ type: 'ok', text: 'opening astronomer.io/product/otto →' })
    window.open('https://www.astronomer.io/product/otto/', '_blank', 'noopener')
  } else if (cmd === '/help' || cmd === 'help') {
    ottoLines.value.push({ type: 'info', text: 'available: /otto · /help · /clear' })
  } else if (cmd === '/clear' || cmd === 'clear') {
    ottoLines.value = []
  } else {
    ottoLines.value.push({ type: 'err', text: `command not found: ${escapeHtml(raw)}. try /otto` })
  }
  ottoCmd.value = ''
}

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
    // Silently fail - limits display is non-critical
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

  setTimeout(() => { ottoOpen.value = true }, 2200)
})

onUnmounted(() => {
  if (limitsInterval) clearInterval(limitsInterval)
})
</script>

<template>
  <!-- Background -->
  <div class="playroom-wall fixed inset-0 z-0"></div>

  <!-- Playroom background -->
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
            class="menu menu-lg dropdown-content bg-base-300/85 backdrop-blur-xl saturate-150 border border-white/10 rounded-2xl z-50 mt-5 w-64 p-3 shadow-2xl">
            <li>
              <RouterLink to="/" @click="closeMenu" v-bind:class="{ 'menu-active': $route.fullPath === '/' }">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                </svg>
                Home
              </RouterLink>
            </li>
            <li>
              <RouterLink to="/system" @click="closeMenu" v-bind:class="{ 'menu-active': $route.fullPath === '/system' }">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-warning" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
                </svg>
                  System
                </RouterLink>
              </li>
            <li>
              <RouterLink to="/about" @click="closeMenu" v-bind:class="{ 'menu-active': $route.fullPath === '/about' }">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                About
              </RouterLink>
            </li>
            <li>
              <a href="https://github.com/vojay-dev/gemini-playroom-diet" target="_blank">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-info" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
                GitHub
              </a>
            </li>
          </ul>
        </div>
      </div>
      <div class="navbar-center hidden sm:flex">
        <RouterLink to="/" class="nav-stack" aria-label="AI project using Apache Airflow on Astronomer">
          <span class="nav-stack-label">AI project using</span>
          <span class="nav-stack-logo nav-stack-logo--airflow">
            <img src="/airflow.svg" alt="Apache Airflow" />
          </span>
          <span class="nav-stack-flow" aria-hidden="true">
            <span class="nav-stack-flow-line"></span>
            <span class="nav-stack-flow-dot"></span>
            <span class="nav-stack-flow-dot"></span>
            <span class="nav-stack-flow-dot"></span>
          </span>
          <span class="nav-stack-logo nav-stack-logo--astro">
            <img src="/astronomer.svg" alt="Astronomer" />
          </span>
        </RouterLink>
      </div>
      <div class="navbar-end gap-2">
        <!-- Usage display -->
        <div class="flex items-center gap-1.5 px-3 py-1 rounded-full bg-base-100/50 border border-white/10 text-sm">
          <template v-if="scansToday === null">
            <span class="loading loading-spinner loading-xs"></span>
            <span class="text-xs opacity-70">Connecting...</span>
          </template>
          <template v-else>
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 opacity-70" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            <span class="font-mono" :class="usagePercent >= 90 ? 'text-error' : usagePercent >= 70 ? 'text-warning' : 'text-success'">
              {{ scansToday }}/{{ dailyLimit }}
            </span>
          </template>
        </div>
        <!-- Theme toggle -->
        <label class="swap swap-rotate btn btn-ghost btn-circle" @click="toggleTheme">
          <!-- Boy icon -->
          <svg
            :class="isNightTheme ? 'swap-off' : 'swap-on'"
            class="h-6 w-6 fill-current"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24">
            <path d="M12 2C9.24 2 7 4.24 7 7s2.24 5 5 5 5-2.24 5-5-2.24-5-5-5zm0 8c-1.65 0-3-1.35-3-3s1.35-3 3-3 3 1.35 3 3-1.35 3-3 3zm0 4c-4.42 0-8 1.79-8 4v2h16v-2c0-2.21-3.58-4-8-4z"/>
          </svg>
          <!-- Girl icon -->
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

  <!-- Otto overlay: terminal window + toggle character -->
  <aside class="otto-overlay" aria-label="Otto from Astronomer">
    <Transition name="otto-win">
      <div v-if="ottoOpen" class="otto-win" role="dialog" aria-label="otto">
        <!-- Title bar -->
        <div class="otto-titlebar">
          <span class="otto-traffic">
            <button class="otto-light otto-light--red" @click="ottoClose" aria-label="Close"></button>
            <span class="otto-light otto-light--amber"></span>
            <span class="otto-light otto-light--green"></span>
          </span>
          <span class="otto-titlebar-name">otto</span>
          <span class="otto-titlebar-spacer"></span>
        </div>

        <!-- Body -->
        <div class="otto-body">
          <p class="otto-line otto-line--intro">
            <span class="otto-prompt">$</span> Hi, I'm <span class="otto-name">Otto</span>
          </p>
          <p class="otto-line otto-line--dim">
            This Airflow project uses modern orchestration patterns. I can help you build cool stuff like this! Also debugging, optimizing, or upgrading your Airflow Dags.
          </p>
          <p v-for="(line, i) in ottoLines" :key="i" class="otto-line" :class="`otto-line--${line.type}`">
            <template v-if="line.type === 'echo'"><span class="otto-prompt">$</span> {{ line.text }}</template>
            <template v-else><span v-html="line.text"></span></template>
          </p>
        </div>

        <!-- Prompt input -->
        <form @submit.prevent="ottoExec" class="otto-promptbar">
          <span class="otto-prompt">$</span>
          <input
            ref="ottoInput"
            v-model="ottoCmd"
            type="text"
            autocomplete="off"
            autocorrect="off"
            autocapitalize="off"
            spellcheck="false"
            placeholder="Type /otto"
            class="otto-input"
            aria-label="Otto command"
          />
          <a href="https://www.astronomer.io/product/otto/" target="_blank" rel="noopener" class="otto-taplink" aria-label="Open Otto">
            Tap to open →
          </a>
        </form>
      </div>
    </Transition>

    <!-- Character (always visible, toggles window) -->
    <button class="otto-character" @click="ottoToggle" :aria-expanded="ottoOpen" aria-label="Toggle Otto">
      <img src="/otto.svg" alt="Otto" />
    </button>
  </aside>

  <!-- Toast container -->
  <div class="toast toast-bottom toast-end z-50 mb-12">
    <div
      v-for="t in toasts"
      :key="t.id"
      class="alert shadow-lg"
      :class="{
        'bg-error text-error-content': t.type === 'error',
        'bg-success text-success-content': t.type === 'success',
        'bg-warning text-warning-content': t.type === 'warning'
      }"
    >
      <span>{{ t.message }}</span>
    </div>
  </div>
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
.nav-stack {
  display: inline-flex;
  align-items: center;
  gap: 0.625rem;
  text-decoration: none;
  white-space: nowrap;
  transition: opacity 0.2s ease;
}

.nav-stack:hover .nav-stack-label {
  color: rgba(255, 255, 255, 0.75);
}

.nav-stack-label {
  font-size: 0.7rem;
  letter-spacing: 0.04em;
  color: rgba(255, 255, 255, 0.5);
  font-weight: 500;
}

.nav-stack-logo {
  display: inline-flex;
  align-items: center;
  transition: filter 0.3s ease;
}

.nav-stack-logo img {
  display: block;
}

.nav-stack-logo--airflow img {
  height: 18px;
  width: 18px;
  filter: drop-shadow(0 0 6px rgba(17, 225, 238, 0.35));
  animation: airflow-pulse 4s ease-in-out infinite;
}

.nav-stack-logo--astro img {
  height: 11px;
  width: auto;
  opacity: 0.9;
}

@keyframes airflow-pulse {
  0%, 100% {
    filter: drop-shadow(0 0 4px rgba(17, 225, 238, 0.25));
  }
  50% {
    filter: drop-shadow(0 0 10px rgba(17, 225, 238, 0.55));
  }
}

/* Flow dots traveling Airflow → Astronomer */
.nav-stack-flow {
  position: relative;
  display: inline-block;
  width: 32px;
  height: 10px;
  flex-shrink: 0;
}

.nav-stack-flow-line {
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(
    to right,
    transparent,
    rgba(255, 255, 255, 0.18) 30%,
    rgba(255, 255, 255, 0.18) 70%,
    transparent
  );
  transform: translateY(-50%);
}

.nav-stack-flow-dot {
  position: absolute;
  top: 50%;
  width: 3px;
  height: 3px;
  border-radius: 50%;
  background: white;
  box-shadow: 0 0 6px rgba(255, 255, 255, 0.7);
  transform: translate(-50%, -50%);
  animation: flow-travel 2.4s linear infinite;
  opacity: 0;
}

.nav-stack-flow-dot:nth-child(2) { animation-delay: 0s; }
.nav-stack-flow-dot:nth-child(3) { animation-delay: 0.8s; }
.nav-stack-flow-dot:nth-child(4) { animation-delay: 1.6s; }

@keyframes flow-travel {
  0%   { left: 0%;   opacity: 0; }
  15%  { opacity: 1; }
  85%  { opacity: 1; }
  100% { left: 100%; opacity: 0; }
}

/* Otto overlay: terminal window + toggle character */
.otto-overlay {
  position: fixed;
  bottom: 4.25rem;
  right: 1.25rem;
  display: flex;
  align-items: flex-end;
  gap: 0.6rem;
  z-index: 40;
  max-width: calc(100vw - 2.5rem);
}

/* Otto character: minimal — one subtle amber pulse, that's it */
.otto-character {
  position: relative;
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background:
    radial-gradient(circle at 30% 30%, rgba(255, 179, 45, 0.18), rgba(20, 22, 30, 0.92) 70%);
  border: 1px solid rgba(255, 179, 45, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  cursor: pointer;
  padding: 0;
  box-shadow: 0 6px 18px -6px rgba(255, 179, 45, 0.3);
  transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
}

.otto-character:hover {
  transform: translateY(-2px);
  border-color: rgba(255, 179, 45, 0.55);
  box-shadow: 0 8px 24px -6px rgba(255, 179, 45, 0.45);
}

.otto-character img {
  width: 30px;
  height: 30px;
  animation: otto-pulse 4s ease-in-out infinite;
}

@keyframes otto-pulse {
  0%, 100% { filter: drop-shadow(0 0 4px rgba(255, 179, 45, 0.4)); }
  50%      { filter: drop-shadow(0 0 12px rgba(255, 179, 45, 0.85)); }
}

/* Terminal window */
.otto-win {
  width: 320px;
  background: rgba(12, 14, 20, 0.94);
  backdrop-filter: blur(18px) saturate(140%);
  border: 1px solid rgba(255, 179, 45, 0.18);
  border-radius: 0.6rem;
  overflow: hidden;
  font-family: 'JetBrains Mono', 'Fira Code', ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.85);
  box-shadow:
    0 16px 50px -12px rgba(0, 0, 0, 0.6),
    0 0 20px -10px rgba(255, 179, 45, 0.25);
}

.otto-titlebar {
  display: flex;
  align-items: center;
  padding: 0.45rem 0.65rem;
  background: rgba(255, 255, 255, 0.03);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.otto-traffic {
  display: inline-flex;
  gap: 6px;
}

.otto-light {
  width: 11px;
  height: 11px;
  border-radius: 50%;
  border: none;
  padding: 0;
  cursor: default;
}

.otto-light--red    { background: #ff5f57; cursor: pointer; }
.otto-light--amber  { background: #ffbd2e; }
.otto-light--green  { background: #28c941; }

.otto-light--red:hover { background: #ff8079; }

.otto-titlebar-name {
  flex: 1;
  text-align: center;
  font-size: 0.7rem;
  color: rgba(255, 255, 255, 0.5);
  letter-spacing: 0.02em;
}

.otto-titlebar-spacer {
  width: 39px;
}

/* Body */
.otto-body {
  padding: 0.7rem 0.85rem 0.55rem;
  line-height: 1.55;
  max-height: 200px;
  overflow-y: auto;
}

.otto-line {
  margin: 0;
}

.otto-line + .otto-line {
  margin-top: 0.25rem;
}

.otto-line--dim {
  color: rgba(255, 255, 255, 0.55);
}

.otto-line--echo {
  color: rgba(255, 255, 255, 0.9);
}

.otto-line--ok  { color: #6dd97e; }
.otto-line--err { color: #ff7a6b; }
.otto-line--info { color: rgba(255, 255, 255, 0.7); }

.otto-prompt {
  color: #ffb32d;
  margin-right: 0.4rem;
  user-select: none;
}

.otto-name {
  color: #ffb32d;
  font-weight: 600;
}

/* Prompt input row */
.otto-promptbar {
  display: flex;
  align-items: center;
  padding: 0.55rem 0.85rem 0.75rem;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  gap: 0.4rem;
}

.otto-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: rgba(255, 255, 255, 0.95);
  font-family: inherit;
  font-size: inherit;
  caret-color: #ffb32d;
  padding: 0;
  min-width: 0;
}

.otto-input::placeholder {
  color: rgba(255, 255, 255, 0.25);
}

.otto-taplink {
  display: none;
  font-size: 0.7rem;
  color: #ffb32d;
  text-decoration: none;
  white-space: nowrap;
  border: 1px solid rgba(255, 179, 45, 0.3);
  padding: 0.2rem 0.55rem;
  border-radius: 999px;
}

.otto-taplink:hover { color: #ffd57a; border-color: rgba(255, 179, 45, 0.5); }

/* Transitions */
.otto-win-enter-active {
  transition: opacity 0.35s ease-out, transform 0.4s cubic-bezier(0.34, 1.4, 0.64, 1);
}
.otto-win-enter-from {
  opacity: 0;
  transform: translate(8px, 12px) scale(0.96);
}
.otto-win-leave-active {
  transition: opacity 0.2s ease-in, transform 0.2s ease-in;
}
.otto-win-leave-to {
  opacity: 0;
  transform: translate(4px, 4px) scale(0.98);
}

/* Mobile: replace prompt input with tap link */
@media (max-width: 640px) {
  .otto-overlay {
    bottom: 3.75rem;
    right: 0.75rem;
    gap: 0.5rem;
  }
  .otto-character {
    width: 44px;
    height: 44px;
  }
  .otto-character img {
    width: 24px;
    height: 24px;
  }
  .otto-win {
    width: 240px;
    font-size: 0.7rem;
  }
  .otto-input { display: none; }
  .otto-taplink { display: inline-flex; align-items: center; }
  .otto-promptbar > .otto-prompt { display: none; }
}

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
