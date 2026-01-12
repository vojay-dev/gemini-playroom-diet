import { createMemoryHistory, createRouter } from 'vue-router'

import Home from './components/Home.vue'
import About from './components/About.vue'

const routes = [
  { path: '/', component: Home },
  { path: '/about', component: About },
]

export const router = createRouter({
  history: createMemoryHistory(),
  routes,
})
