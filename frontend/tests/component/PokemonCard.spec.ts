/**
 * Testes de COMPONENTE (também chamados de "funcionais" na camada de UI)
 * ==========================================================================
 * Escopo: um componente Vue montado de verdade (via @vue/test-utils),
 * verificando o que o USUÁRIO veria — texto renderizado, badges, atributos
 * de imagem — a partir de props controladas. Sem chamar useFetch, sem
 * subir o Nuxt: por isso não é E2E, é um degrau abaixo.
 */
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import PokemonCard from '../../components/PokemonCard.vue'

const venusaur = {
  id: 3,
  name: 'venusaur',
  sprite: 'https://example.com/venusaur.png',
  types: ['grass', 'poison'],
  height_cm: 200,
  weight_kg: 100,
}

describe('PokemonCard', () => {
  it('renderiza nome, número, altura e peso corretamente', () => {
    const wrapper = mount(PokemonCard, { props: { pokemon: venusaur } })

    expect(wrapper.get('[data-testid="pokemon-name"]').text()).toBe('venusaur')
    expect(wrapper.get('[data-testid="pokemon-number"]').text()).toBe('#3')
    expect(wrapper.get('[data-testid="pokemon-height"]').text()).toBe('200 cm')
    expect(wrapper.get('[data-testid="pokemon-weight"]').text()).toBe('100 kg')
  })

  it('renderiza um badge para cada tipo, na ordem recebida', () => {
    const wrapper = mount(PokemonCard, { props: { pokemon: venusaur } })

    const badges = wrapper.findAll('[data-testid^="type-badge-"]')
    expect(badges).toHaveLength(2)
    expect(badges[0].text()).toBe('grass')
    expect(badges[1].text()).toBe('poison')
  })

  it('aplica a cor correta de fundo em cada badge de tipo', () => {
    const wrapper = mount(PokemonCard, { props: { pokemon: venusaur } })

    const grassBadge = wrapper.get('[data-testid="type-badge-grass"]')
    expect(grassBadge.attributes('style')).toContain('background: rgb(120, 200, 80)')
  })

  it('exibe a sprite com o alt text correto para acessibilidade', () => {
    const wrapper = mount(PokemonCard, { props: { pokemon: venusaur } })

    const img = wrapper.get('[data-testid="pokemon-sprite"]')
    expect(img.attributes('src')).toBe(venusaur.sprite)
    expect(img.attributes('alt')).toBe('venusaur')
  })

  it('mostra um fallback textual quando não há sprite', () => {
    const noSprite = { ...venusaur, sprite: null }
    const wrapper = mount(PokemonCard, { props: { pokemon: noSprite } })

    expect(wrapper.find('[data-testid="pokemon-sprite"]').exists()).toBe(false)
    expect(wrapper.get('[data-testid="pokemon-sprite-fallback"]').text()).toBe('sem imagem')
  })

  it('renderiza apenas um badge para Pokémon de tipo único', () => {
    const singleType = { ...venusaur, types: ['grass'] }
    const wrapper = mount(PokemonCard, { props: { pokemon: singleType } })

    expect(wrapper.findAll('[data-testid^="type-badge-"]')).toHaveLength(1)
  })
})
