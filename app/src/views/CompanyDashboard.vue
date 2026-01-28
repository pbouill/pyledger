<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="10" md="8">
        <v-card elevation="2">
          <v-card-title class="text-h5">Your Companies</v-card-title>
          <v-card-text>
            <v-list>
              <v-list-item v-for="company in companies" :key="company.id">
                <v-list-item-title>{{ company.name }}</v-list-item-title>
                <v-list-item-subtitle>{{ company.legal_name }}</v-list-item-subtitle>
              </v-list-item>
            </v-list>
            <v-btn color="primary" to="/company/create">Create New Company</v-btn>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '../api'
const companies = ref([])
onMounted(async () => {
  try {
    const { data } = await api.get('/company/')
    companies.value = data
  } catch (err) {
    companies.value = []
  }
})
</script>
