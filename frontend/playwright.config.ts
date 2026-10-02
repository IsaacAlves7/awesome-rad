import { defineConfig, devices } from '@playwright/test'
import path from 'node:path'

const FRONTEND_URL = 'http://127.0.0.1:3000'
const BACKEND_URL = 'http://127.0.0.1:8000'

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: false, // os specs de sistema dependem de estado de rede/servidor; evita flakiness
  retries: process.env.CI ? 1 : 0,
  reporter: [['html', { open: 'never' }], ['list']],

  use: {
    baseURL: FRONTEND_URL,
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },

  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'mobile-webkit', use: { ...devices['iPhone 13'] } }, // cobre teste de usabilidade responsiva
  ],

  // Sobe os dois serviços reais (backend + frontend) antes da suíte, e
  // derruba ao final — é isso que torna esses testes "de sistema" e não
  // apenas "de UI com mocks".
  webServer: [
    {
      command: 'python -m uvicorn main:app --port 8000',
      cwd: path.resolve(__dirname, '../backend'),
      url: `${BACKEND_URL}/api/health`,
      reuseExistingServer: !process.env.CI,
      timeout: 30_000,
    },
    {
      command: 'npm run dev',
      cwd: __dirname,
      url: FRONTEND_URL,
      env: { NUXT_PUBLIC_API_BASE: BACKEND_URL },
      reuseExistingServer: !process.env.CI,
      timeout: 60_000,
    },
  ],
})
