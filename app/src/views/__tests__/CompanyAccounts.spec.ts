/// <reference types="vitest" />
/// <reference types="node" />
import { render, screen, fireEvent } from '@testing-library/vue'
import { vi } from 'vitest'

vi.mock('vue-router', () => ({ useRoute: () => ({ params: { id: '1' } }) }))

const REAL_BACKEND = Boolean(process.env.TEST_API_URL)

import CompanyAccounts from '../CompanyAccounts.vue'
import api, { setApiBaseUrl } from '../../api'

async function createTestUserAndLogin(base: string) {
  const username = `vitestuser_${Date.now()}`
  const email = `${username}@example.com`
  const password = 'TestPassw0rd!'
  await api.post(`${base}/auth/register`, { username, email, password })
  // login endpoint expects form-encoded
  const form = new URLSearchParams()
  form.append('username', username)
  form.append('password', password)
  const res = await api.post(`${base}/auth/login`, form, { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } })
  const token = res.data.access_token
  api.defaults.headers['Authorization'] = `Bearer ${token}`
  return { username, email }
}

describe('CompanyAccounts view', () => {
  beforeEach(() => {
    if (!REAL_BACKEND) {
      ;(api as any).get = vi.fn()
      ;(api as any).post = vi.fn()
    }
  })

  test('renders accounts from API', async () => {
    if (!REAL_BACKEND) {
      // api.get is mocked; provide responses for company then accounts
      ;(api as any).get.mockResolvedValueOnce({ data: { id: 1, name: 'Company' } })
      ;(api as any).get.mockResolvedValueOnce({ data: [{ id: 1, name: 'Main', institution: 'Bank', account_type: 'chequing' }] })
      ;(api as any).get.mockResolvedValueOnce({ data: ['chequing','savings','credit_card'] })
      const { findByText } = render(CompanyAccounts)
      expect(await findByText('Main')).toBeTruthy()
      expect(await findByText('Bank')).toBeTruthy()
    } else {
      // integration: point api at test backend
      const base = process.env.TEST_API_URL!.replace(/\/$/, '') + '/api'
      setApiBaseUrl(base)
      await createTestUserAndLogin(base)

      // create a company
      const comp = await api.post(`${base}/company/`, { name: `testco_${Date.now()}`, legal_name: 'Test Co' })
      const id = comp.data.id

      // create an account
      const acct = await api.post(`${base}/company/${id}/accounts/`, { name: 'Main', institution: 'Bank', currency_code: 'USD', account_type: 'chequing' })

      // render and assert it loads
      const { findByText } = render(CompanyAccounts, { global: { mocks: { $route: { params: { id } } } } })
      expect(await findByText('Main')).toBeTruthy()
      expect(await findByText('Bank')).toBeTruthy()
    }
  })

  test('creates account and adds to list', async () => {
    if (!REAL_BACKEND) {
      ;(api as any).get.mockResolvedValueOnce({ data: [] })
      ;(api as any).get.mockResolvedValueOnce({ data: ['chequing','savings','credit_card'] })
      ;(api as any).post.mockResolvedValueOnce({ data: { id: 2, name: 'New', institution: 'Bank', account_type: 'savings' } })

      const { getByRole, getAllByRole, getByLabelText, findByText } = render(CompanyAccounts)

    // open create dialog (use button role to avoid ambiguous matches)
    await fireEvent.click(getByRole('button', { name: /Create Account/i }))

    // fill form (stubbed inputs are rendered with labels)
    const nameInput = getByLabelText('Name') as HTMLInputElement
    await fireEvent.update(nameInput, 'New')

    const instInput = getByLabelText('Institution') as HTMLInputElement
    await fireEvent.update(instInput, 'Bank')

    // pick the 'Create' button inside the Create Account dialog specifically
    const createButtons = getAllByRole('button', { name: /^Create$/i })
    const dialogTitle = await findByText('Create Account')
    const createBtn = createButtons.find((b: any) => b.closest('section')?.textContent?.includes(dialogTitle.textContent || ''))!
      await fireEvent.click(createBtn)

      expect((api as any).post).toHaveBeenCalled()
      expect(await screen.findByText('New')).toBeTruthy()
    } else {
      const base = process.env.TEST_API_URL!.replace(/\/$/, '') + '/api'
      setApiBaseUrl(base)
      await createTestUserAndLogin(base)

      // create company
      const comp = await api.post(`${base}/company/`, { name: `testco_${Date.now()}`, legal_name: 'Test Co 2' })
      const id = comp.data.id

      const { getByText, getByLabelText } = render(CompanyAccounts, { global: { mocks: { $route: { params: { id } } } } })

      // open create dialog
      await fireEvent.click(getByText('Create Account'))

      // fill form
      const nameInput = getByLabelText('Name') as HTMLInputElement
      await fireEvent.update(nameInput, 'New')

      const instInput = getByLabelText('Institution') as HTMLInputElement
      await fireEvent.update(instInput, 'Bank')

      const createBtn = getByText('Create')
      await fireEvent.click(createBtn)

      // verify via API that it exists
      const { data } = await api.get(`${base}/company/${id}/accounts/`)
      expect(data.some((a: any) => a.name === 'New')).toBeTruthy()
    }
  })
})
