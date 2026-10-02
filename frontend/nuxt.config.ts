// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2026-01-01',
  devtools: { enabled: true },

  css: ['~/assets/css/main.css'],

  runtimeConfig: {
    public: {
      // URL do backend FastAPI. Em produção, aponte para o domínio do BFF.
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000',
    },
  },

  // ---- SSG + ISR ----
  // Nitro decide, por rota, se a página é:
  //  - prerenderizada em build time (SSG puro)
  //  - servida via ISR (gerada sob demanda e cacheada na borda por `isr` segundos)
  //  - sempre dinâmica (swr: false)
  // O deploy em uma plataforma com CDN (Vercel, Netlify, Cloudflare Pages) é o
  // que efetivamente transforma esse `isr`/`swr` em cache de borda real.
  routeRules: {
    // Home: lista de pokémons — gerada estaticamente no build (SSG)
    '/': { prerender: true },

    // Páginas de detalhe: ISR de 1h. Primeira visita gera e cacheia na CDN;
    // requisições seguintes (dentro da janela) são servidas do edge, sem
    // tocar no Nuxt server nem no FastAPI.
    '/pokemon/**': { isr: 60 * 60 },

    // API do próprio Nuxt (se usada) fica fora de cache agressivo
    '/api/**': { swr: 60 },
  },

  nitro: {
    // 'vercel' ou 'netlify' habilitam ISR nativo de borda nesses providers.
    // Para self-host, o preset 'node-server' + um CDN na frente (Cloudflare)
    // também respeita os headers Cache-Control emitidos pelo FastAPI.
    preset: process.env.NITRO_PRESET || 'node-server',
  },
})
