<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12" md="8">
        <v-card>
          <v-card-title class="text-h6">Accounts for {{ company?.name || 'Company' }}</v-card-title>
          <v-card-text>
            <v-list>
              <v-list-item v-for="acct in accounts" :key="acct.id" @click="selectAccount(acct)">
                <v-list-item-content>
                  <v-list-item-title>{{ acct.name }}</v-list-item-title>
                  <v-list-item-subtitle>{{ acct.institution }}</v-list-item-subtitle>
                </v-list-item-content>
                <v-list-item-action>
                  <div class="text-right">
                    <div v-if="acct.account_type"><v-chip>{{ acct.account_type }}</v-chip></div>
                    <div class="mt-1">Balance: {{ acct.current_balance ?? acct.opening_balance ?? 0.0 }} {{ acct.currency_code || '' }}</div>
                  </div>
                </v-list-item-action>
              </v-list-item>
            </v-list>
            <v-btn color="primary" @click="openCreate">Create Account</v-btn>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="4" v-if="selected">
        <v-card>
          <v-card-title class="text-h6">Transactions for {{ selected.name }}</v-card-title>
          <v-card-text>
            <v-list>
              <v-list-item v-for="tx in transactions" :key="tx.id">
                <v-list-item-content>
                  <v-list-item-title>{{ tx.amount }} {{ tx.currency_code || '' }}</v-list-item-title>
                  <v-list-item-subtitle>{{ tx.description }}</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
            </v-list>
            <v-btn color="primary" @click="openCreateTx">Create Transaction</v-btn>
            <v-btn text @click="openEditAccount">Edit Account</v-btn>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-dialog v-model="showCreate" width="500">
      <template #activator>
      </template>
      <v-card>
        <v-card-title>Create Account</v-card-title>
        <v-card-text>
          <v-text-field v-model="newAcct.name" label="Name" />
          <v-text-field v-model="newAcct.institution" label="Institution" />
          <CurrencySelect v-model="newAcct.currency_code" label="Currency Code" />
          <v-select :items="accountTypeItems" v-model="newAcct.account_type" label="Type" />
          <v-text-field v-model.number="newAcct.opening_balance" type="number" label="Opening Balance" />
        </v-card-text>
        <v-card-actions>
          <v-btn text @click="showCreate = false">Cancel</v-btn>
          <v-btn color="primary" @click="createAccount">Create</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="showCreateTx" width="500">
      <v-card>
        <v-card-title>Create Transaction</v-card-title>
        <v-card-text>
          <v-text-field v-model="newTx.amount" type="number" label="Amount" />
          <div class="mb-2">Currency: {{ selected.currency_code || '' }}</div>
          <v-text-field v-model="newTx.description" label="Description" />
        </v-card-text>
        <v-card-actions>
          <v-btn text @click="showCreateTx = false">Cancel</v-btn>
          <v-btn color="primary" @click="createTransaction">Create</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="showEditAcct" width="500">
      <v-card>
        <v-card-title>Edit Account</v-card-title>
        <v-card-text>
          <v-text-field v-model="editAcct.name" label="Name" />
          <v-text-field v-model="editAcct.institution" label="Institution" />
          <CurrencySelect v-model="editAcct.currency_code" label="Currency Code" />
          <v-select :items="accountTypeItems" v-model="editAcct.account_type" label="Type" />
          <v-text-field v-model.number="editAcct.opening_balance" type="number" label="Opening Balance" />
        </v-card-text>
        <v-card-actions>
          <v-btn text @click="showEditAcct = false">Cancel</v-btn>
          <v-btn color="primary" @click="updateAccount">Save</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api'
import CurrencySelect from '../components/CurrencySelect.vue'

const route = useRoute()
const companyId = Number(route.params.id)
const company = ref(null as any)
const accounts = ref([] as any[])
const transactions = ref([] as any[])
const selected = ref(null as any)

const showCreate = ref(false)
const showCreateTx = ref(false)
const showEditAcct = ref(false)
const newAcct = ref({ name: '', institution: '', currency_code: '', account_type: 'chequing', opening_balance: 0.0 })
const editAcct = ref({ id: null as number | null, name: '', institution: '', currency_code: '', account_type: 'chequing', opening_balance: 0.0 })
const newTx = ref({ amount: 0, description: '' })

onMounted(async () => {
  await loadCompany()
  await loadAccounts()
  await loadAccountTypes()
})

const accountTypeItems = ref<string[]>([])

async function loadAccountTypes() {
  try {
    const { data } = await api.get(`/company/${companyId}/accounts/types`)
    accountTypeItems.value = data || []
  } catch (err) {
    accountTypeItems.value = ['chequing','savings','credit_card']
  }
}

async function loadCompany() {
  try {
    const { data } = await api.get(`/company/${companyId}/`)
    company.value = data
    // default new account currency to company currency
    if (company.value && company.value.currency_code) {
      newAcct.value.currency_code = company.value.currency_code
    }
  } catch (err) {
    company.value = null
  }
}

async function loadAccounts() {
  try {
    const { data } = await api.get(`/company/${companyId}/accounts/`)
    accounts.value = data
    await loadAccountSummary()
  } catch (err) {
    accounts.value = []
  }
}

async function loadAccountSummary() {
  try {
    const { data } = await api.get(`/company/${companyId}/accounts/summary`)
    const map = new Map<number, number>()
    ;(data || []).forEach((r: any) => map.set(r.account_id, r.current_balance))
    accounts.value = accounts.value.map((a: any) => ({ ...a, current_balance: map.get(a.id) ?? 0.0 }))
  } catch (err) {
    // best-effort; ignore
  }
}

async function selectAccount(acct: any) {
  selected.value = acct
  await loadTransactions(acct.id)
}

async function loadTransactions(accountId: number) {
  try {
    const { data } = await api.get(`/company/${companyId}/accounts/${accountId}/transactions`)
    transactions.value = data
  } catch (err) {
    transactions.value = []
  }
}

function openCreate() {
  showCreate.value = true
}

async function createAccount() {
  try {
      const { data } = await api.post(`/company/${companyId}/accounts/`, newAcct.value)
    accounts.value.push(data)
    showCreate.value = false
  } catch (err) {
    // error handled by interceptor
  }
}

function openCreateTx() {
  showCreateTx.value = true
}

function openEditAccount() {
  if (!selected.value) return
  editAcct.value = { ...selected.value }
  showEditAcct.value = true
}

async function updateAccount() {
  try {
    if (!editAcct.value?.id) return
    const payload = {
      name: editAcct.value.name,
      institution: editAcct.value.institution,
      currency_code: editAcct.value.currency_code,
      account_type: editAcct.value.account_type,
    }
    const { data } = await api.patch(`/company/${companyId}/accounts/${editAcct.value.id}/`, payload)
    // Update local lists
    const idx = accounts.value.findIndex((a: any) => a.id === data.id)
    if (idx !== -1) accounts.value.splice(idx, 1, data)
    if (selected.value && selected.value.id === data.id) selected.value = data
    showEditAcct.value = false
  } catch (err) {
    // error handled by interceptor
  }
}

async function createTransaction() {
  try {
    if (!selected.value) return
    const payload = { amount: newTx.value.amount, description: newTx.value.description }
    const { data } = await api.post(`/company/${companyId}/accounts/${selected.value.id}/transactions`, payload)
    transactions.value.push(data)
    // update accounting totals for the account locally
    await loadAccountSummary()
    showCreateTx.value = false
  } catch (err) {
    // error handled by interceptor
  }
}
</script>
