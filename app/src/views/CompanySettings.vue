<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="10" md="8">
        <v-card elevation="2">
          <v-card-title class="text-h5">Company Settings</v-card-title>
          <v-card-text>
              <v-form @submit.prevent="onSave">
                <v-text-field v-model="name" label="Company Name" required />
                <v-text-field v-model="legalName" label="Legal Name" />
                <v-text-field v-model="taxNumber" label="Tax Number" />
                <CurrencySelect v-model="currencyCode" label="Currency Code" />
                <v-alert v-if="error" type="error" class="mb-4" text>{{ error }}</v-alert>
              <v-btn type="submit" color="primary" block class="mt-4">Save</v-btn>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../api'
import CurrencySelect from '../components/CurrencySelect.vue'

const route = useRoute()
const router = useRouter()
const companyId = route.params.id ? Number(route.params.id) : null

const name = ref('')
const legalName = ref('')
const taxNumber = ref('')
const currencyCode = ref('')
const error = ref('')

onMounted(async () => {
  if (companyId) {
    await loadCompany()
  } else {
    // try to load first company from list
    try {
      const { data } = await api.get('/company/')
      if (data && data.length > 0) {
        const c = data[0]
        router.replace(`/company/${c.id}/settings`)
      }
    } catch (e) {
      // ignore
    }
  }
})

async function loadCompany() {
  try {
    const { data } = await api.get(`/company/${companyId}/`)
    name.value = data.name
    legalName.value = data.legal_name || ''
    taxNumber.value = data.tax_number || ''
    currencyCode.value = data.currency_code || ''
  } catch (err) {
    error.value = 'Could not load company'
  }
}

async function onSave() {
  error.value = ''
  try {
    const payload: any = {
      name: name.value,
      legal_name: legalName.value,
      tax_number: taxNumber.value,
      currency_code: currencyCode.value,
    }
    await api.patch(`/company/${companyId}/`, payload)
    // reload
    await loadCompany()
  } catch (err: any) {
    error.value = err?.response?.data?.detail || 'Save failed'
  }
}
</script>
