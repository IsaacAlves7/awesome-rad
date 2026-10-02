<script setup lang="ts">
// Import explícito (em vez de depender do auto-import do Nuxt) para que
// este componente permaneça testável isoladamente com @vue/test-utils/Vitest,
// fora do runtime do Nuxt.
import { useTypeColor } from '../composables/useTypeColor'

defineProps<{
  pokemon: {
    id: number
    name: string
    sprite: string | null
    types: string[]
    height_cm: number
    weight_kg: number
  }
}>()
</script>

<template>
  <div class="pokemon-card" data-testid="pokemon-card">
    <div class="pokemon-name-badge" data-testid="pokemon-name">{{ pokemon.name }}</div>

    <img
      v-if="pokemon.sprite"
      :src="pokemon.sprite"
      :alt="pokemon.name"
      class="pokemon-sprite"
      data-testid="pokemon-sprite"
    />
    <div v-else class="state-msg" data-testid="pokemon-sprite-fallback">sem imagem</div>

    <div class="pokemon-meta">
      <strong>numero:</strong>
      <span data-testid="pokemon-number">#{{ pokemon.id }}</span>
    </div>

    <div class="pokemon-meta">
      <strong>tipo:</strong>
    </div>
    <div class="types-row" data-testid="pokemon-types">
      <span
        v-for="t in pokemon.types"
        :key="t"
        class="type-badge"
        :data-testid="`type-badge-${t}`"
        :style="{ background: useTypeColor(t) }"
      >
        {{ t }}
      </span>
    </div>

    <div class="stats-row">
      <div>
        <strong>Altura:</strong><br />
        <span data-testid="pokemon-height">{{ pokemon.height_cm }} cm</span>
      </div>
      <div>
        <strong>peso:</strong><br />
        <span data-testid="pokemon-weight">{{ pokemon.weight_kg }} kg</span>
      </div>
    </div>
  </div>
</template>
