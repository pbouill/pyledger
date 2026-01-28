import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import Login from './views/Login.vue'
import Register from './views/Register.vue'
import CompanyDashboard from './views/CompanyDashboard.vue'
import CompanyCreate from './views/CompanyCreate.vue'
import CompanySettings from './views/CompanySettings.vue'

const routes: RouteRecordRaw[] = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: Login },
  { path: '/register', component: Register },
  { path: '/company', component: CompanyDashboard, meta: { requiresAuth: true } },
  { path: '/company/create', component: CompanyCreate, meta: { requiresAuth: true } },
  { path: '/company/settings', component: CompanySettings, meta: { requiresAuth: true } },
]


import { useAuthStore } from './stores/auth'

export const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    next('/login')
  } else {
    next()
  }
})
