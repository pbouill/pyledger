<template>
  <v-autocomplete
    :items="items"
    :loading="loading"
    :label="label"
    v-model="selected"
    item-text="text"
    item-value="value"
    clearable
    :required="required"
    autocomplete="off"
  />
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import api from '../api'

interface Item {
  text: string
  value: string
}

const props = defineProps<{
  modelValue?: string
  label?: string
  required?: boolean
}>()

const emit = defineEmits(['update:modelValue'])

const label = props.label ?? 'Currency Code'
const required = props.required ?? false

const items = ref<Item[]>([])
const loading = ref(false)
const selected = ref<string | null>(props.modelValue ?? null)

onMounted(async () => {
  loading.value = true
  try {
    const res = await api.get('/currency')
    // API returns dict mapping code => name
    items.value = Object.entries(res.data).map(([code, name]) => ({
      text: `${code} - ${name}`,
      value: code,
    }))
  } catch (e) {
    // swallow; calling views can show errors if needed
  } finally {
    loading.value = false
  }
})

// Sync incoming changes to modelValue
watch(
  () => props.modelValue,
  (nv) => {
    selected.value = nv ?? null
  }
)

// Emit changes outward
watch(selected, (nv) => {
  emit('update:modelValue', nv)
})
</script>
