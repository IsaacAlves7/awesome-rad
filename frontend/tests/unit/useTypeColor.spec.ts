/**
 * Teste UNITÁRIO (frontend)
 * ==========================
 * `useTypeColor` é uma função pura (sem reatividade Vue, sem DOM), então
 * testamos como qualquer função JS — sem montar componente, sem Nuxt.
 */
import { describe, it, expect } from 'vitest'
import { useTypeColor } from '../../composables/useTypeColor'

describe('useTypeColor', () => {
  it('retorna a cor oficial para um tipo conhecido', () => {
    expect(useTypeColor('grass')).toBe('#78C850')
    expect(useTypeColor('poison')).toBe('#A040A0')
    expect(useTypeColor('fire')).toBe('#F08030')
  })

  it('retorna uma cor de fallback para tipo desconhecido', () => {
    expect(useTypeColor('tipo-que-nao-existe')).toBe('#777777')
  })

  it('é case-sensitive (tipos vêm sempre em lowercase da API)', () => {
    // Documenta o contrato: quem chamar com 'Grass' cai no fallback.
    expect(useTypeColor('Grass')).toBe('#777777')
  })

  it('cobre todos os 18 tipos oficiais de Pokémon', () => {
    const officialTypes = [
      'normal', 'fire', 'water', 'electric', 'grass', 'ice', 'fighting',
      'poison', 'ground', 'flying', 'psychic', 'bug', 'rock', 'ghost',
      'dragon', 'dark', 'steel', 'fairy',
    ]
    for (const type of officialTypes) {
      expect(useTypeColor(type)).not.toBe('#777777')
    }
  })
})
