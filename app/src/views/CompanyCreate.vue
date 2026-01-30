<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="10" md="8">
        <v-card elevation="2">
          <v-card-title class="text-h5">Create Company</v-card-title>
          <v-card-text>
            <v-form @submit.prevent="onCreate">
              <v-text-field
                v-model="name"
                label="Company Name"
                required
                autocomplete="organization"
              />
              <v-text-field
                v-model="legalName"
                label="Legal Name"
                autocomplete="organization"
              />
              <v-text-field v-model="taxNumber" label="Tax Number" autocomplete="off" />

              <CurrencySelect v-model="currencyCode" label="Currency Code" />

              <!-- TODO: Address, settings, logo upload -->
              <v-btn type="submit" color="primary" block class="mt-4">Create</v-btn>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import CurrencySelect from '../components/CurrencySelect.vue'
const name = ref('')
const legalName = ref('')
const taxNumber = ref('')
const currencyCode = ref('')
const error = ref('')
const router = useRouter()

async function onCreate() {
  error.value = ''
  try {
    await api.post('/company/', {
      name: name.value,
      legal_name: legalName.value,
      tax_number: taxNumber.value,
      currency_code: currencyCode.value,
    })
    router.push('/company')
  } catch (err: any) {
    error.value = err?.response?.data?.detail || 'Company creation failed'
  }
}
</script>
