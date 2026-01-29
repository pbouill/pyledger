<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="4">
        <v-card elevation="2">
          <v-card-title class="text-h5">Register</v-card-title>
          <v-card-text>
            <v-form @submit.prevent="onRegister">
              <v-text-field v-model="username" label="Username" autocomplete="username" required />
              <v-text-field v-model="email" label="Email" type="email" autocomplete="email" required />
              <v-text-field v-model="password" label="Password" type="password" autocomplete="new-password" required />
              <v-text-field v-model="confirmPassword" label="Confirm Password" type="password" autocomplete="new-password" :error="passwordsMismatch" :error-messages="passwordsMismatch ? ['Passwords do not match'] : []" required />
              <v-alert v-if="error" type="error" class="mt-2">{{ error }}</v-alert>
              <v-btn type="submit" color="primary" block class="mt-4">Register</v-btn>
            </v-form>
            <div class="mt-2 text-center">
              <router-link to="/login">Already have an account? Login</router-link>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import api from '../api'
const username = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const router = useRouter()
const auth = useAuthStore()
const error = ref('')
const passwordsMismatch = computed(() => password.value !== '' && confirmPassword.value !== '' && password.value !== confirmPassword.value)
async function onRegister() {
  error.value = ''
  if (passwordsMismatch.value) {
    error.value = 'Passwords do not match'
    return
  }
  try {
    await api.post('/auth/register', { username: username.value, email: email.value, password: password.value })
    // Auto-login after registration
    const params = new URLSearchParams()
    params.append('username', username.value)
    params.append('password', password.value)
    const { data } = await api.post('/auth/login', params)
    auth.token = data.access_token
    auth.isAuthenticated = true
    // Fetch user info
    const me = await api.get('/auth/me')
    auth.user = me.data
    router.push('/company')
  } catch (err: any) {
    error.value = err?.response?.data?.detail || 'Registration failed'
  }
}
</script>
