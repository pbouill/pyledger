import { defineStore } from 'pinia'
import { ref } from 'vue'

export type ToastLevel = 'info' | 'success' | 'warning' | 'error'

export const useToastStore = defineStore('toasts', () => {
  const toasts = ref<Array<{ id: number; text: string; level: ToastLevel }>>([])
  let counter = 1

  function addToast(text: string, level: ToastLevel = 'info') {
    const id = counter++
    toasts.value.push({ id, text, level })
    // auto-remove after 5s
    setTimeout(() => removeToast(id), 5000)
  }

  function removeToast(id: number) {
    toasts.value = toasts.value.filter((t) => t.id !== id)
  }

  return { toasts, addToast, removeToast }
})
