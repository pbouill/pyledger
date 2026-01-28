<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="10" md="8">
        <v-card elevation="2">
          <v-card-title class="text-h5">Company Settings</v-card-title>
          <v-card-text>
            <!-- TODO: Company settings form fields -->
            <v-form @submit.prevent="onSave">
              <!-- Example setting -->
              <v-text-field v-model="exampleSetting" label="Example Setting" />
              <v-btn type="submit" color="primary" block class="mt-4">Save</v-btn>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref } from 'vue'
const exampleSetting = ref('')
function onSave() {
  // TODO: Implement settings save logic
}
</script>
