import '@testing-library/jest-dom'
import { config, shallowMount } from '@vue/test-utils'
import { defineComponent, h } from 'vue'

// Lightweight Vuetify stubs for tests — render accessible HTML so tests can interact
const passthrough = (tag = 'div') =>
  defineComponent({
    props: ['modelValue', 'label', 'items'],
    setup(_props, { slots }) {
      return () => h(tag, {}, slots.default && slots.default())
    },
  })

const VBtn = defineComponent({
  setup(_, { slots }) {
    return () => h('button', {}, slots.default && slots.default())
  },
})

const VTextField = defineComponent({
  props: ['label', 'modelValue'],
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    const id = `vtf-${Math.random().toString(36).slice(2, 8)}`
    return () =>
      h('label', { for: id }, [
        props.label,
        h('input', {
          id,
          value: (props as any).modelValue,
          onInput: (e: Event) => emit('update:modelValue', (e.target as HTMLInputElement).value),
        }),
      ])
  },
})

const VSelect = defineComponent({
  props: ['label', 'items', 'modelValue'],
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    const id = `vs-${Math.random().toString(36).slice(2, 8)}`
    return () =>
      h('label', { for: id }, [
        props.label,
        h(
          'select',
          {
            id,
            value: (props as any).modelValue,
            onChange: (e: Event) => emit('update:modelValue', (e.target as HTMLSelectElement).value),
          },
          (props.items || []).map((it: any) => h('option', {}, String(it)))
        ),
      ])
  },
})

import { createPinia, setActivePinia } from 'pinia'

// Register stubs globally
config.global.components = config.global.components || {}
// Install Pinia so modules accessed by `api` work in tests
config.global.plugins = config.global.plugins || []
const pinia = createPinia()
setActivePinia(pinia)
config.global.plugins.push(pinia)
config.global.components['v-btn'] = VBtn
config.global.components['v-text-field'] = VTextField
config.global.components['v-select'] = VSelect
config.global.components['v-list'] = passthrough('ul')
config.global.components['v-list-item'] = passthrough('li')
config.global.components['v-list-item-content'] = passthrough('div')
config.global.components['v-list-item-title'] = passthrough('div')
config.global.components['v-list-item-subtitle'] = passthrough('div')
config.global.components['v-list-item-action'] = passthrough('div')
config.global.components['v-card'] = passthrough('section')
config.global.components['v-card-title'] = passthrough('h3')
config.global.components['v-card-text'] = passthrough('div')
config.global.components['v-card-actions'] = passthrough('div')
config.global.components['v-dialog'] = passthrough('div')
config.global.components['v-container'] = passthrough('div')
config.global.components['v-row'] = passthrough('div')
config.global.components['v-col'] = passthrough('div')
config.global.components['v-chip'] = passthrough('span')
config.global.components['v-spacer'] = passthrough('div')

// keep any existing config
config.global.stubs = config.global.stubs || {}
