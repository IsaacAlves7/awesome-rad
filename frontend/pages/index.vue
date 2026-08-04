<script setup lang="ts">
const config = useRuntimeConfig()

// useFetch aqui roda em build time (nuxt generate) -> vira SSG puro na home,
// conforme routeRules['/'].prerender = true em nuxt.config.ts
const { data: pokemons, error } = await useFetch<Array<{ id: number; name: string; sprite: string | null }>>(
  `${config.public.apiBase}/api/pokemon`,
  { query: { limit: 24, offset: 0 } }
)
</script>

<template>
  <div class="page">
    <div class="title-badge">PokeVue — SSG na Home</div>

    <p v-if="error" class="state-msg">Não foi possível carregar a lista de Pokémon.</p>

    <div v-else class="grid-list">
      <NuxtLink
        v-for="p in pokemons"
        :key="p.id"
        :to="`/pokemon/${p.name}`"
        class="grid-item"
      >
        <img v-if="p.sprite" :src="p.sprite" :alt="p.name" />
        <div>#{{ p.id }} {{ p.name }}</div>
      </NuxtLink>
    </div>
  </div>
</template>
