<script setup lang="ts">
const route = useRoute()
const config = useRuntimeConfig()

interface PokemonDetail {
  id: number
  name: string
  sprite: string | null
  types: string[]
  height_cm: number
  weight_kg: number
  generated_at: number
}

// Em produção (nuxt generate + ISR), essa página é gerada sob demanda na
// primeira requisição e depois servida direto da CDN por até 1h
// (routeRules['/pokemon/**'].isr em nuxt.config.ts), sem re-executar este
// código nem chamar o FastAPI de novo até expirar o cache.
const { data: pokemon, error } = await useFetch<PokemonDetail>(
  `${config.public.apiBase}/api/pokemon/${route.params.id}`
)
</script>

<template>
  <div class="page">
    <div class="browser-frame">
      <div class="browser-topbar">
        pokevue.vercel.app/pokemon/{{ route.params.id }}
      </div>

      <div class="pokemon-card">
        <p v-if="error" class="state-msg" style="color:#900">
          Pokémon não encontrado.
        </p>

        <template v-else-if="pokemon">
          <div class="pokemon-name-badge">{{ pokemon.name }}</div>

          <img
            v-if="pokemon.sprite"
            :src="pokemon.sprite"
            :alt="pokemon.name"
            class="pokemon-sprite"
          />

          <div class="pokemon-meta">
            <strong>numero:</strong>
            <span>#{{ pokemon.id }}</span>
          </div>

          <div class="pokemon-meta">
            <strong>tipo:</strong>
          </div>
          <div class="types-row">
            <span
              v-for="t in pokemon.types"
              :key="t"
              class="type-badge"
              :style="{ background: useTypeColor(t) }"
            >
              {{ t }}
            </span>
          </div>

          <div class="stats-row">
            <div>
              <strong>Altura:</strong><br />
              {{ pokemon.height_cm }} cm
            </div>
            <div>
              <strong>peso:</strong><br />
              {{ pokemon.weight_kg }} kg
            </div>
          </div>
        </template>
      </div>
    </div>

    <div style="text-align:center">
      <div class="footer-badge">Experiência fica super rápida e fluida</div>
    </div>
  </div>
</template>
