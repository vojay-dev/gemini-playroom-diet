import { createMemoryHistory, createRouter } from 'vue-router'

import Home from './components/Home.vue'
import About from './components/About.vue'
import ScanResult from './components/ScanResult.vue'
import SystemOverview from './components/SystemOverview.vue'

const routes = [
  { path: '/', component: Home },
  { path: '/about', component: About },
  { path: '/scan/:id', component: ScanResult },
  { path: '/system', component: SystemOverview },
]

export const router = createRouter({
  history: createMemoryHistory(),
  routes,
})
