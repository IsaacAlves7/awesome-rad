> Versículo chave: "Consagre ao Senhor tudo o que você faz, e os seus planos serão bem-sucedidos." - Provérbios 16:3

# 🏃🏾💨 awesome-rad
Esse repositório une os melhores dos mundos, com alta performance em aplicações web e consumo de APIs + Deploy rápido passando pelos testes com CI/CD Pipeline com o ciclo de desenvolvimento RAD - Rapid Application Development.

Um stack com **Vue.js no frontend** e **FastAPI no backend** é uma combinação extremamente poderosa quando a meta é **alta performance**, tanto em tempo de resposta quanto em produtividade do time. E converter muitos arquivos em um curto período de tempo é muito útil, pois ajudará bastante na agilidade da equipe em fazer projetos eficientes.

* **FastAPI**: assíncrono por padrão, validação automática, escalabilidade, ideal para APIs críticas em baixa latência.
* **Vue.js**: leve, rápido de renderizar, curva de aprendizado menor que Angular/React.
* **Integração**: comunicação limpa via JSON, usando Axios/fetch ou GraphQL.
* **Escalabilidade**: cada parte pode escalar de forma independente (micro frontends com Vue, microsserviços com FastAPI).

Estrutura geral da aplicação:
* **Frontend (Vue.js)**: SPA (Single Page Application) reativa, com rotas no cliente, componentes reutilizáveis e integração via Axios ou Fetch para consumir as APIs.
* **Backend (FastAPI)**: expõe endpoints REST ou GraphQL, com tipagem forte (pydantic), validação automática, suporte nativo a WebSockets e performance comparável ao Node.js graças ao Starlette + Uvicorn.
* **Banco de Dados**: pode ser SQL (PostgreSQL, MySQL) via SQLAlchemy/Tortoise ORM ou NoSQL (MongoDB, Redis).
* **Deploy**: Docker + Kubernetes, com escalabilidade horizontal (FastAPI é ótimo para rodar em workers assíncronos).

Casos de uso de alta performance:

<table>
  <tr>
    <td><img width="452" height="669" alt="Captura de tela 2025-10-31 110519" src="https://github.com/user-attachments/assets/6fbe6335-447e-44bf-a00c-506c1718c344" /></td>
    <td><img src="https://github.com/user-attachments/assets/a92f4e21-c43c-49b9-a61d-b4df22397ed0"></td>
  </tr>
</table>

Confira estas 8 dicas para melhorar o desempenho do frontend:

- **Compression**: Comprima arquivos e minimize o tamanho dos dados antes da transmissão para reduzir a carga da rede.

- **Selective Rendering/Windowing** - Exibe apenas elementos visíveis para otimizar o desempenho da renderização. Por exemplo, em uma lista dinâmica, apenas renderize itens visíveis.

- **Modular Architecture with Code Splitting** - um pacote de aplicações maior em vários pacotes menores para carregamento eficiente.

- **Priority-Based Loading** - Priorize recursos essenciais e conteúdos visíveis (ou acima da dobra) para uma melhor experiência do usuário.

- **Pre-loading** os recursos do Fetch com antecedência antes de serem solicitados para melhorar a velocidade de carregamento.

- **Tree Shaking or Dead Code Removal** - Otimize o pacote JS final removendo código morto que nunca será usado.

- **Pre-fetching** ou cachear proativamente recursos que provavelmente serão necessários em breve.

- **Dynamic Imports** - Carreguem módulos de código dinamicamente baseados nas ações do usuário para otimizar os tempos iniciais de carregamento.

1. **Plataformas em tempo real** 🚀

   * **Exemplo**: dashboards de monitoramento, chats, multiplayer games, trading de ações, telemedicina.
   * **Por quê?** FastAPI suporta **WebSockets** e tarefas assíncronas (via asyncio, Celery ou Redis), enquanto Vue.js pode atualizar a UI em tempo real com Vuex/Pinia.

2. **APIs de Machine Learning / Data Science**

   * **Exemplo**: sistema que recebe uma imagem e retorna classificação, ou processamento de linguagem natural.
   * **Por quê?** FastAPI é muito usado para expor modelos de ML treinados (TensorFlow, PyTorch, Scikit-learn) em endpoints REST. Vue.js fica responsável pela interface intuitiva.

3. **Sistemas de e-commerce e marketplace escaláveis**

   * **Exemplo**: lojas online com carrinho em tempo real, integração de pagamentos, estoque distribuído.
   * **Por quê?** Vue.js garante UX fluida (checkout sem recarregar página), enquanto FastAPI dá conta de APIs de alta concorrência com resposta rápida.

4. **Aplicativos de streaming e multimídia**

   * **Exemplo**: plataformas de vídeo/aúdio sob demanda, como Netflix-like ou Spotify-like.
   * **Por quê?** FastAPI gerencia a API de metadados, autenticação e filas de processamento, e Vue.js cuida do player responsivo e UI rica.

5. **SaaS (Software as a Service) multi-tenant**

   * **Exemplo**: CRM, ERP leve, ferramentas de produtividade (como Notion ou Trello-like).
   * **Por quê?** Vue.js entrega interatividade de nível desktop, e FastAPI suporta autenticação JWT/OAuth2 + performance para múltiplos clientes simultâneos.

6. **Plataformas de observabilidade / IoT**

   * **Exemplo**: dashboards que coletam métricas de sensores ou logs de sistemas em tempo real.
   * **Por quê?** FastAPI processa milhões de eventos concorrentes, e Vue.js mostra os dados em gráficos reativos (via D3.js, Chart.js, ECharts).

# PokeVue — SSG/ISR com CDN (Vue/Nuxt + FastAPI)
Exemplo: Réplica funcional do conceito da imagem (PokeNext, em Next.js), mas com **Vue.js (via Nuxt 3)** no front e **FastAPI** no back.

Arquitetura:

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

## (Desenvolvimento) Rodando localmente
Backend:

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Configure a URL do backend via variável de ambiente, se necessário:
```bash
NUXT_PUBLIC_API_BASE=http://localhost:8000 npm run dev
```

## (Produção) Deploy com CDN real - ISR de verdade
O ISR só produz efeito de cache de borda de fato quando hospedado em uma plataforma com CDN integrada ao Nitro:

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

Por que Nuxt e não "Vue puro"? Vue.js (o framework em si) não faz build-time rendering nem ISR — isso é
responsabilidade de um meta-framework, do mesmo jeito que React sozinho não faz SSG/ISR, só o Next.js faz. Nuxt 3 está para Vue assim como Next.js está para React: fornece SSG, SSR, ISR e `routeRules` por rota em cima do Vue.
