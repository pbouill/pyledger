<template>
  <div class="toast-area">
    <v-snackbar
      v-for="toast in toasts"
      :key="toast.id"
      v-model="visible[toast.id]"
      :timeout="5000"
      :color="colorForLevel(toast.level)"
      bottom
      right
      rounded
      elevation="6"
      class="toast"
    >
      {{ toast.text }}
      <template #actions>
        <v-btn icon @click="dismiss(toast.id)">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </template>
    </v-snackbar>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, watch } from 'vue'
import { useToastStore } from '../stores/toasts'

const toastStore = useToastStore()
const toasts = computed(() => toastStore.toasts)
const visible = reactive<Record<number, boolean>>({})

watch(toasts, (next) => {
  next.forEach((t) => {
    visible[t.id] = true
  })
})

function dismiss(id: number) {
  visible[id] = false
  setTimeout(() => toastStore.removeToast(id), 200)
}

function colorForLevel(level: string) {
  switch (level) {
    case 'success':
      return 'green'
    case 'warning':
      return 'orange'
    case 'error':
      return 'red'
    default:
      return 'primary'
  }
}
</script>

<style scoped>
.toast-area {
  position: fixed;
  right: 1rem;
  bottom: 1rem;
  z-index: 9999;
}
.toast {
  margin-top: 0.5rem;
  min-width: 240px;
}
</style>