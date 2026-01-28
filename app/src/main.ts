

import { createApp } from 'vue'
import App from './App.vue'
import { createVuetify } from 'vuetify'
import 'vuetify/styles'
import { aliases, mdi } from 'vuetify/iconsets/mdi'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

import { router } from './router'
import { createPinia } from 'pinia'

const pinia = createPinia()
const vuetify = createVuetify({
	components,
	directives,
	icons: {
		defaultSet: 'mdi',
		aliases,
		sets: { mdi },
	},
})

createApp(App)
	.use(pinia)
	.use(vuetify)
	.use(router)
	.mount('#app')
