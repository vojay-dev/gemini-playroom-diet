import { ref } from 'vue'

const toasts = ref([])

export function useToast() {
  const show = (message, type = 'error', duration = 4000) => {
    const id = Date.now()
    toasts.value.push({ id, message, type })
    setTimeout(() => {
      toasts.value = toasts.value.filter(t => t.id !== id)
    }, duration)
  }

  const error = (message) => show(message, 'error')
  const success = (message) => show(message, 'success')
  const warning = (message) => show(message, 'warning')

  return { toasts, show, error, success, warning }
}
