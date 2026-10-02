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

      <p v-if="error" class="state-msg" style="color:#900" data-testid="pokemon-not-found">
        Pokémon não encontrado.
      </p>

      <PokemonCard v-else-if="pokemon" :pokemon="pokemon" />
    </div>

    <div style="text-align:center">
      <div class="footer-badge">Experiência fica super rápida e fluida</div>
    </div>
  </div>
</template>
