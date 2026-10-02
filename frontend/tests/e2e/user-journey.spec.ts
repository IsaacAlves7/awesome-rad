/**
 * Testes END-TO-END (E2E)
 * =========================
 * Escopo: navegador real (via Playwright) contra a aplicação real de ponta
 * a ponta — frontend Nuxt servindo HTML, chamando o backend FastAPI real,
 * que por sua vez chama a PokeAPI real. Nada é mockado aqui: se a PokeAPI
 * estiver fora do ar, este teste também falha (isso é esperado — é o
 * preço de testar o sistema completo tal como o usuário o vive).
 */
import { test, expect } from '@playwright/test'

test.describe('Jornada do usuário: descobrir e ver detalhes de um Pokémon', () => {
  test('usuário abre a home, vê a lista e navega para um detalhe', async ({ page }) => {
    await page.goto('/')

    // A home é SSG: o conteúdo já deve estar no HTML inicial, sem spinner.
    await expect(page.getByText('SSG na Home')).toBeVisible()

    const firstCard = page.locator('.grid-item').first()
    await expect(firstCard).toBeVisible()
    const pokemonName = await firstCard.locator('div').last().innerText()

    await firstCard.click()

    await expect(page).toHaveURL(/\/pokemon\/.+/)
    await expect(page.getByTestId('pokemon-name')).toContainText(
      pokemonName.replace(/#\d+\s*/, '').trim()
    )
  })

  test('página de detalhe mostra número, tipos, altura e peso consistentes', async ({ page }) => {
    await page.goto('/pokemon/venusaur')

    await expect(page.getByTestId('pokemon-name')).toHaveText('venusaur')
    await expect(page.getByTestId('pokemon-number')).toHaveText('#3')
    await expect(page.getByTestId('type-badge-grass')).toBeVisible()
    await expect(page.getByTestId('type-badge-poison')).toBeVisible()
    await expect(page.getByTestId('pokemon-height')).toHaveText('200 cm')
    await expect(page.getByTestId('pokemon-weight')).toHaveText('100 kg')
  })

  test('Pokémon inexistente mostra mensagem de erro amigável, não uma tela quebrada', async ({ page }) => {
    await page.goto('/pokemon/pokemon-que-nao-existe-123')

    await expect(page.getByTestId('pokemon-not-found')).toBeVisible()
    await expect(page.getByTestId('pokemon-card')).not.toBeVisible()
  })

  test('navegação de volta para a home a partir do detalhe preserva a lista', async ({ page }) => {
    await page.goto('/pokemon/venusaur')
    await page.goBack()

    await expect(page).toHaveURL('/')
    await expect(page.locator('.grid-item').first()).toBeVisible()
  })
})
