

<template>
  <v-app>
    <v-main>
      <div class="app">
        <img alt="CanonLedger Logo" src="/logo.png" class="logo" />
        <h1>CanonLedger</h1>
        <router-view />
        <ToastContainer />
      </div>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import ToastContainer from './components/ToastContainer.vue'
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
</style>
