import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import { router } from './router.js'
import { createGtag } from 'vue-gtag'

const app = createApp(App)
const gtag = createGtag({
  tagId: 'G-SNNQEEFJLK'
})

app.use(router).use(gtag).mount('#app')
