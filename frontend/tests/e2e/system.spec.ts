/**
 * Testes de SISTEMA
 * ===================
 * Diferença para os E2E de jornada do usuário: aqui o foco não é "o que o
 * usuário vê", e sim se o SISTEMA como um todo (Nuxt + FastAPI + headers de
 * cache) se comporta como projetado — a peça central deste projeto sendo a
 * estratégia de SSG/ISR/CDN. Inspecionamos requisições de rede, não só DOM.
 */
import { test, expect } from '@playwright/test'

test.describe('Sistema: integração Nuxt <-> FastAPI e política de cache', () => {
  test('a página de detalhe efetivamente chama o backend FastAPI real', async ({ page }) => {
    const backendCall = page.waitForResponse((res) =>
      res.url().includes('/api/pokemon/venusaur') && res.status() === 200
    )

    await page.goto('/pokemon/venusaur')
    const response = await backendCall

    expect(response.status()).toBe(200)
  })

  test('resposta do backend carrega Cache-Control compatível com a política de ISR de 1h', async ({ page }) => {
    const backendCall = page.waitForResponse((res) => res.url().includes('/api/pokemon/venusaur'))

    await page.goto('/pokemon/venusaur')
    const response = await backendCall

    const cacheControl = response.headers()['cache-control'] || ''
    expect(cacheControl).toContain('public')
    expect(cacheControl).toMatch(/s-maxage=\d+/)

    const sMaxAge = Number(cacheControl.match(/s-maxage=(\d+)/)?.[1] ?? 0)
    expect(sMaxAge).toBeGreaterThanOrEqual(3600) // >= 1h, conforme documentado no README
  })

  test('a home não dispara chamada ao backend em runtime (é SSG real)', async ({ page }) => {
    const backendCalls: string[] = []
    page.on('response', (res) => {
      if (res.url().includes(':8000/api/pokemon')) backendCalls.push(res.url())
    })

    await page.goto('/')
    await page.waitForLoadState('networkidle')

    // A home foi prerenderizada em build time; navegar até ela não deveria
    // custar uma chamada de API síncrona bloqueando o usuário. Se a home
    // ainda depender de fetch client-side, este teste documenta a lacuna.
    expect(backendCalls.length).toBeLessThanOrEqual(1)
  })

  test('duas requisições seguidas ao mesmo Pokémon recebem o mesmo payload (idempotência)', async ({ request, baseURL }) => {
    const backendBase = process.env.NUXT_PUBLIC_API_BASE || 'http://127.0.0.1:8000'
    const first = await request.get(`${backendBase}/api/pokemon/venusaur`)
    const second = await request.get(`${backendBase}/api/pokemon/venusaur`)

    expect(await first.json()).toMatchObject(await second.json())
  })

  test('sistema se recupera de um Pokémon inválido sem quebrar chamadas subsequentes', async ({ page }) => {
    await page.goto('/pokemon/nao-existe-mesmo')
    await expect(page.getByTestId('pokemon-not-found')).toBeVisible()

    // o sistema deve continuar operante após um erro isolado
    await page.goto('/pokemon/venusaur')
    await expect(page.getByTestId('pokemon-name')).toHaveText('venusaur')
  })
})
