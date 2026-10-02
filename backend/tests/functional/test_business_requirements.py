"""
Testes FUNCIONAIS
===================
Diferença para os de integração: os de integração validam "o código
funciona tecnicamente" (rotas, status codes, contratos). Os funcionais
validam requisitos de PRODUTO — o que foi combinado que a aplicação faz,
descrito em termos de comportamento observável, não de implementação.

Requisitos cobertos aqui (derivados do escopo do projeto):
  RF01 — Unidades de altura/peso devem ser convertidas para cm/kg (não
         expor decímetros/hectogramas da PokeAPI cru).
  RF02 — Cada Pokémon pode ter 1 ou 2 tipos, e a ordem retornada pela
         PokeAPI deve ser preservada (afeta qual badge aparece primeiro).
  RF03 — A listagem respeita paginação via `limit`/`offset`.
  RF04 — Toda resposta cacheável carrega uma política de cache compatível
         com ISR de 1h+ (long TTL), conforme documentado no README.
  RF05 — Erros de "não encontrado" devem ser diferenciáveis de erros de
         infraestrutura (404 vs 502), para o frontend decidir a UI certa.
"""
import httpx
import respx

POKEAPI_BASE = "https://pokeapi.co/api/v2"


@respx.mock
def test_rf01_units_are_converted_to_cm_and_kg(client, venusaur_payload):
    respx.get(f"{POKEAPI_BASE}/pokemon/venusaur").mock(
        return_value=httpx.Response(200, json=venusaur_payload)
    )
    body = client.get("/api/pokemon/venusaur").json()

    # payload de origem: height=20 (dm), weight=1000 (hg)
    assert body["height_cm"] == 200
    assert body["weight_kg"] == 100.0


@respx.mock
def test_rf02_type_order_is_preserved_for_dual_type_pokemon(client, venusaur_payload):
    respx.get(f"{POKEAPI_BASE}/pokemon/venusaur").mock(
        return_value=httpx.Response(200, json=venusaur_payload)
    )
    body = client.get("/api/pokemon/venusaur").json()

    assert body["types"] == ["grass", "poison"]  # grass é slot 1, poison é slot 2


@respx.mock
def test_rf02_single_type_pokemon_returns_one_type(client, bulbasaur_min):
    respx.get(f"{POKEAPI_BASE}/pokemon/bulbasaur").mock(
        return_value=httpx.Response(200, json=bulbasaur_min)
    )
    body = client.get("/api/pokemon/bulbasaur").json()

    assert body["types"] == ["grass"]


@respx.mock
def test_rf03_listing_forwards_limit_and_offset_to_upstream(client, pokemon_list_page):
    route = respx.get(f"{POKEAPI_BASE}/pokemon", params={"limit": "2", "offset": "10"}).mock(
        return_value=httpx.Response(200, json={**pokemon_list_page, "results": []})
    )

    client.get("/api/pokemon", params={"limit": 2, "offset": 10})

    assert route.called


@respx.mock
def test_rf04_detail_cache_ttl_supports_hourly_isr_or_longer(client, venusaur_payload):
    """O README promete ISR de 1h no frontend; o backend não pode emitir
    um TTL menor que isso, ou a CDN revalidaria mais rápido do que o Nuxt
    espera, anulando o ganho de performance."""
    respx.get(f"{POKEAPI_BASE}/pokemon/venusaur").mock(
        return_value=httpx.Response(200, json=venusaur_payload)
    )
    resp = client.get("/api/pokemon/venusaur")

    cache_control = resp.headers["cache-control"]
    s_maxage = int(cache_control.split("s-maxage=")[1].split(",")[0])
    ONE_HOUR = 3600
    assert s_maxage >= ONE_HOUR


@respx.mock
def test_rf05_not_found_and_upstream_error_are_distinguishable(client):
    respx.get(f"{POKEAPI_BASE}/pokemon/ghost-mon").mock(return_value=httpx.Response(404))
    respx.get(f"{POKEAPI_BASE}/pokemon/broken-mon").mock(return_value=httpx.Response(500))

    not_found = client.get("/api/pokemon/ghost-mon")
    upstream_error = client.get("/api/pokemon/broken-mon")

    assert not_found.status_code == 404
    assert upstream_error.status_code == 502
    assert not_found.status_code != upstream_error.status_code
