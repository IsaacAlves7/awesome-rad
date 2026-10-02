# Estratégia de Testes — PokeVue

Seis tipos de teste foram pedidos. Este documento mapeia cada um para onde
ele vive no repo, o que exatamente ele verifica, e como rodar. No final há
uma nota de transparência sobre o que foi **executado de verdade** ao gerar
este projeto vs. o que foi escrito e revisado mas não pôde ser executado
neste ambiente (sandbox sem acesso a determinados domínios de rede).

```
                    ▲  poucos, lentos, caros
        E2E / Sistema / Usabilidade   (Playwright, navegador real)
       ─────────────────────────────
        Integração / Funcional        (pytest + TestClient, respx)
       ─────────────────────────────
        Unitário                      (pytest / Vitest)
                    ▼  muitos, rápidos, baratos
```

## 1. Testes Unitários

**O quê:** uma função/classe isolada, sem I/O, sem framework web de pé.

| Onde | O que testa |
|---|---|
| `backend/tests/unit/test_cache_headers.py` | função `_set_cdn_cache` (monta o header `Cache-Control`) |
| `backend/tests/unit/test_models.py` | validação dos modelos Pydantic (`PokemonSummary`, `PokemonDetail`) |
| `frontend/tests/unit/useTypeColor.spec.ts` | composable puro `useTypeColor` (mapa tipo → cor) |

```bash
# backend
cd backend && pytest tests/unit -v
# frontend
cd frontend && npm run test:unit
```

## 2. Testes de Integração

**O quê:** a aplicação real (roteamento, DI, serialização) rodando
in-process, com a única dependência externa (PokeAPI) substituída por um
mock determinístico (`respx`), para não depender de rede.

| Onde | O que testa |
|---|---|
| `backend/tests/integration/test_pokemon_endpoints.py` | rotas `/api/health`, `/api/pokemon`, `/api/pokemon/{id}`, CORS, propagação de erros (404 vs 502) |

```bash
cd backend && pytest tests/integration -v
```

## 3. Testes Funcionais

**O quê:** requisitos de **produto**, descritos como comportamento
observável (não implementação). Cada teste referencia um "RFxx" documentado
no cabeçalho do arquivo.

| Onde | O que testa |
|---|---|
| `backend/tests/functional/test_business_requirements.py` | conversão de unidades (dm/hg → cm/kg), ordem dos tipos, paginação, TTL de cache ≥ 1h, diferenciação 404/502 |
| `frontend/tests/component/PokemonCard.spec.ts` | requisitos de UI: nome, número, badges por tipo, fallback sem sprite — funcional na camada de componente |

```bash
cd backend && pytest tests/functional -v
cd frontend && npm run test:component
```

## 4. Testes de Sistema

**O quê:** os serviços reais rodando como processos de verdade (não
in-process), se comunicando por HTTP de verdade. Testa o sistema como ele
roda em produção, não a aplicação Python/JS isolada.

| Onde | O que testa |
|---|---|
| `backend/tests/system/test_backend_process.py` | sobe `uvicorn` como subprocesso real, bate HTTP nele de fora, valida bind de porta / OpenAPI / percurso completo até um servidor fake da PokeAPI |
| `frontend/tests/e2e/system.spec.ts` | Nuxt real + FastAPI real rodando juntos (via `webServer` do Playwright); valida que o header de cache chega íntegro até o navegador, que a home não faz fetch client-side, idempotência |

```bash
cd backend && pytest tests/system -v
cd frontend && npm run test:system   # sobe os 2 serviços automaticamente
```

## 5. Testes End-to-End (E2E)

**O quê:** navegador real, jornada completa do usuário, sistema real de
ponta a ponta (frontend → backend → PokeAPI real).

| Onde | O que testa |
|---|---|
| `frontend/tests/e2e/user-journey.spec.ts` | home → clicar num card → ver detalhe correto; Pokémon inexistente mostra erro amigável; navegação de volta |

```bash
cd frontend && npm run test:e2e
```

## 6. Testes de Usabilidade

**O quê:** a parte automatizável de usabilidade — acessibilidade,
responsividade, navegação por teclado, tempo até o conteúdo aparecer.
Usabilidade "completa" também inclui testes com usuários reais, que não
são automatizáveis (checklist manual abaixo).

| Onde | O que testa |
|---|---|
| `frontend/tests/e2e/usability.spec.ts` | violações de acessibilidade via `axe-core` (WCAG 2 A/AA), ausência de scroll horizontal em mobile, grid responsivo, navegação 100% por teclado, orçamento de performance (<2s até conteúdo principal) |

```bash
cd frontend && npm run test:usability
```

### Checklist manual complementar (não automatizável)
- [ ] Um usuário que nunca viu o app entende em <10s que pode clicar num Pokémon?
- [ ] O texto dos badges de tipo é legível para daltônicos (não depender só da cor)?
- [ ] A jornada é confortável em conexão 3G simulada (Chrome DevTools throttling)?
- [ ] Usuário de leitor de tela (NVDA/VoiceOver) consegue navegar sem se perder?

---

## Rodando tudo de uma vez

```bash
# backend — unit + integration + functional + system
cd backend
pip install -r requirements.txt -r tests/requirements-test.txt
pytest

# frontend — unit + component
cd frontend
npm install
npm run test:unit
npm run test:component

# frontend — e2e + sistema + usabilidade (sobe backend+frontend sozinho)
npx playwright install --with-deps
npm run test:e2e
npm run test:system
npm run test:usability
```

O workflow `.github/workflows/tests.yml` roda todas as seis camadas em CI
a cada push/PR.

---

## Nota de transparência

Ao construir este projeto, as seguintes suítes foram **efetivamente
executadas e passaram**, neste ambiente de geração:

- ✅ Backend unitário — 8 testes
- ✅ Backend integração — 9 testes
- ✅ Backend funcional — 6 testes
- ✅ Backend sistema (subprocesso `uvicorn` real + servidor HTTP fake local) — 4 testes
- ✅ Frontend unitário (Vitest) — 4 testes
- ✅ Frontend componente (Vue Test Utils) — 6 testes

**Total executado e verificado: 37 testes, 37 passando.**

Os arquivos de **E2E, Sistema (frontend) e Usabilidade** baseados em
Playwright foram escritos e revisados com o mesmo cuidado, mas não puderam
ser *executados* neste ambiente porque o download do binário do navegador
Chromium (`cdn.playwright.dev`) é bloqueado pela política de rede do
sandbox de geração. Eles vão rodar normalmente em uma máquina/CI com acesso
de rede padrão — o workflow em `.github/workflows/tests.yml` já está
configurado para isso. Recomendo rodar `npx playwright test` localmente
antes do primeiro merge para confirmar comportamento no seu ambiente.
