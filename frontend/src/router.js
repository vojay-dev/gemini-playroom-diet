import { createWebHistory, createRouter } from 'vue-router'

const routes = [
  { path: '/', component: () => import('./components/Home.vue') },
  { path: '/about', component: () => import('./components/About.vue') },
  { path: '/scan/:id', component: () => import('./components/ScanResult.vue') },
  { path: '/system', component: () => import('./components/SystemOverview.vue') },
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
})
