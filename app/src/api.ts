import axios from 'axios'
import { useAuthStore } from './stores/auth'

const api = axios.create({
  baseURL: '/api',
  withCredentials: true,
})

api.interceptors.request.use((config) => {
  const auth = useAuthStore()
  if (auth.token) {
    config.headers = config.headers || {}
    config.headers['Authorization'] = `Bearer ${auth.token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => {
    try {
      const msg = response.headers['x-app-message'] || response.data?.message?.text || response.data?.detail
      const lvl = response.headers['x-app-message-level'] || (response.status >= 400 ? 'error' : 'info')
      if (msg) {
        const toasts = useToastStore()
        toasts.addToast(String(msg), (lvl as any))
      }
    } catch (err) {
      // swallow errors in interceptor
    }
    return response
  },
  (error) => {
    try {
      const resp = error.response
      if (resp) {
        const msg = resp.headers['x-app-message'] || resp.data?.message?.text || resp.data?.detail
        const lvl = resp.headers['x-app-message-level'] || 'error'
        if (msg) {
          const toasts = useToastStore()
          toasts.addToast(String(msg), (lvl as any))
        }
      }
    } catch (err) {
      // ignore
    }
    return Promise.reject(error)
  },
)

export default api
