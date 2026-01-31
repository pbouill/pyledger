

<template>
  <v-app>
    <v-main>
      <div class="app">
        <img alt="CanonLedger Logo" src="/logo.png" class="logo" />
        <h1>CanonLedger</h1>
        <div class="nav">
          <template v-if="!auth.isAuthenticated">
            <router-link to="/login"><v-btn color="primary" class="mx-2">Login</v-btn></router-link>
            <router-link to="/register"><v-btn color="secondary">Register</v-btn></router-link>
          </template>
          <template v-else>
            <v-btn text :to="'/company'">Companies</v-btn>
            <v-btn text :to="'/company/create'">Create Company</v-btn>
            <v-btn text @click="onLogout">Logout</v-btn>
          </template>
        </div>
        <router-view />
        <ToastContainer />
      </div>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import ToastContainer from './components/ToastContainer.vue'
import { useAuthStore } from './stores/auth'
import { useRouter } from 'vue-router'
const auth = useAuthStore()
const router = useRouter()

function onLogout() {
  auth.logout()
  router.push('/login')
}
</script>

<style>
body { font-family: 'Nunito', system-ui, sans-serif; padding: 2rem; }
.app { max-width: 800px; margin: 0 auto; text-align: center; }
.logo {
  width: 120px;
  margin-bottom: 1.5rem;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
.nav { margin-bottom: 1rem; }
.nav .v-btn { font-weight: 600; }
</style>
