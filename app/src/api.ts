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

export default api
