# PokeVue — SSG/ISR com CDN (Vue/Nuxt + FastAPI)

Réplica funcional do conceito da imagem (PokeNext, em Next.js), mas com
**Vue.js (via Nuxt 3)** no front e **FastAPI** no back.

## Arquitetura

```
Usuário → CDN (edge) → Nuxt Server (Nitro) → FastAPI (BFF) → PokeAPI
              ↑ cache ISR                        ↑ cache s-maxage
```

- **Home (`/`)** — `prerender: true` → gerada 100% em build time (SSG puro).
  Nenhuma requisição ao backend acontece em runtime para essa rota.
- **Detalhe (`/pokemon/[id]`)** — `isr: 3600` (1h). Vue.js puro não tem
  conceito de ISR (isso é feature de meta-framework), por isso o front usa
  **Nuxt 3**, que implementa SSG/ISR sobre Vue do mesmo jeito que Next.js faz
  sobre React. Na primeira visita depois do cache expirar, a CDN deixa passar
  a requisição, o Nitro (servidor do Nuxt) renderiza a página chamando o
  FastAPI, e a resposta fica cacheada na borda pelo tempo configurado.
- **FastAPI (BFF)** — não é só um proxy: adiciona os headers
  `Cache-Control: public, s-maxage=86400, stale-while-revalidate=3600` em
  cada resposta. Isso significa que, mesmo se você chamar o FastAPI
  diretamente por trás de uma CDN (Cloudflare, Fastly), ele já cacheia
  corretamente — o ISR do Nuxt é uma segunda camada de cache, não a única.

## Rodando localmente

### Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Configure a URL do backend via variável de ambiente, se necessário:
```bash
NUXT_PUBLIC_API_BASE=http://localhost:8000 npm run dev
```

## Deploy com CDN real (ISR de verdade)

O ISR só produz efeito de cache de borda de fato quando hospedado em uma
plataforma com CDN integrada ao Nitro:

- **Vercel**: `nitro.preset = 'vercel'` → cada rota `isr` vira uma Edge/Serverless
  Function com cache automático na Vercel CDN.
- **Netlify**: `nitro.preset = 'netlify'` → equivalente via Netlify Edge.
- **Self-host + Cloudflare**: `nitro.preset = 'node-server'` atrás do Cloudflare
  como proxy reverso; o Cloudflare respeita os headers `Cache-Control` tanto
  do Nuxt quanto do FastAPI.

Para gerar o build estático (páginas prerenderizadas + rotas ISR):
```bash
npm run generate
```

## Por que Nuxt e não "Vue puro"?

Vue.js (o framework em si) não faz build-time rendering nem ISR — isso é
responsabilidade de um meta-framework, do mesmo jeito que React sozinho não
faz SSG/ISR, só o Next.js faz. Nuxt 3 está para Vue assim como Next.js está
para React: fornece SSG, SSR, ISR e `routeRules` por rota em cima do Vue.
