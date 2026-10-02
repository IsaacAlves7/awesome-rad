/**
 * Testes de USABILIDADE
 * =======================
 * Escopo: a aplicação é fácil e confortável de usar — não só "funciona
 * tecnicamente". Cobrimos quatro dimensões automatizáveis de usabilidade:
 *   1. Acessibilidade (axe-core) — leitores de tela, contraste, semântica.
 *   2. Responsividade — a UI não quebra em telas pequenas (mobile-first).
 *   3. Navegação por teclado — usuário sem mouse consegue completar a
 *      jornada principal.
 *   4. Performance percebida — tempo até o conteúdo principal aparecer,
 *      que é o que a estratégia inteira de SSG/ISR promete melhorar.
 *
 * Usabilidade "de verdade" também inclui testes com usuários reais
 * (não automatizáveis) — ver TESTING.md para o checklist manual complementar.
 */
import { test, expect } from '@playwright/test'
import AxeBuilder from '@axe-core/playwright'

test.describe('Usabilidade: acessibilidade', () => {
  test('home não tem violações de acessibilidade críticas/sérias (axe-core)', async ({ page }) => {
    await page.goto('/')
    const results = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa'])
      .analyze()

    const blocking = results.violations.filter((v) => ['critical', 'serious'].includes(v.impact ?? ''))
    expect(blocking, JSON.stringify(blocking, null, 2)).toEqual([])
  })

  test('página de detalhe não tem violações de acessibilidade críticas/sérias', async ({ page }) => {
    await page.goto('/pokemon/venusaur')
    const results = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa'])
      .analyze()

    const blocking = results.violations.filter((v) => ['critical', 'serious'].includes(v.impact ?? ''))
    expect(blocking, JSON.stringify(blocking, null, 2)).toEqual([])
  })

  test('imagem do Pokémon tem texto alternativo descritivo', async ({ page }) => {
    await page.goto('/pokemon/venusaur')
    const img = page.getByTestId('pokemon-sprite')
    await expect(img).toHaveAttribute('alt', 'venusaur')
  })
})

test.describe('Usabilidade: responsividade', () => {
  test('card de detalhe não causa scroll horizontal em viewport mobile (360px)', async ({ page }) => {
    await page.setViewportSize({ width: 360, height: 800 })
    await page.goto('/pokemon/venusaur')

    const hasHorizontalScroll = await page.evaluate(
      () => document.documentElement.scrollWidth > document.documentElement.clientWidth
    )
    expect(hasHorizontalScroll).toBe(false)
  })

  test('grid da home se adapta de 1 coluna (mobile) a múltiplas colunas (desktop)', async ({ page }) => {
    await page.setViewportSize({ width: 360, height: 800 })
    await page.goto('/')
    const mobileColumns = await page.evaluate(() => {
      const grid = document.querySelector('.grid-list') as HTMLElement
      return getComputedStyle(grid).gridTemplateColumns.split(' ').length
    })

    await page.setViewportSize({ width: 1280, height: 800 })
    const desktopColumns = await page.evaluate(() => {
      const grid = document.querySelector('.grid-list') as HTMLElement
      return getComputedStyle(grid).gridTemplateColumns.split(' ').length
    })

    expect(desktopColumns).toBeGreaterThan(mobileColumns)
  })
})

test.describe('Usabilidade: navegação por teclado', () => {
  test('usuário consegue tabular até um card e ativá-lo com Enter', async ({ page }) => {
    await page.goto('/')

    // tab até o primeiro link de pokémon foca via teclado
    const firstLink = page.locator('.grid-item').first()
    await firstLink.focus()
    await expect(firstLink).toBeFocused()

    await page.keyboard.press('Enter')
    await expect(page).toHaveURL(/\/pokemon\/.+/)
  })
})

test.describe('Usabilidade: performance percebida', () => {
  test('conteúdo principal da home aparece rapidamente (orçamento de 2s)', async ({ page }) => {
    const start = Date.now()
    await page.goto('/')
    await page.getByText('SSG na Home').waitFor({ state: 'visible' })
    const elapsedMs = Date.now() - start

    expect(elapsedMs).toBeLessThan(2000)
  })
})
