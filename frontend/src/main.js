import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import { router } from './router.js'
import { createGtag } from 'vue-gtag'

const app = createApp(App)

app.use(createGtag({
  config: { id: "G-SNNQEEFJLK" }
}, router))

app.use(router).mount('#app')
