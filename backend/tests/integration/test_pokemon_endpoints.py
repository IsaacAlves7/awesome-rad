"""
Testes de INTEGRAÇÃO
=====================
Escopo: a pilha real do FastAPI (roteamento, DI, serialização Pydantic,
middleware de CORS, cliente httpx) funcionando junta. A única coisa
substituída é a borda externa (PokeAPI), via respx — assim o teste é
determinístico e não depende de rede/uptime de terceiros.
"""
import respx
import httpx
import pytest

POKEAPI_BASE = "https://pokeapi.co/api/v2"


def test_health_endpoint(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


@respx.mock
def test_get_pokemon_success_integrates_route_client_and_serialization(client, venusaur_payload):
    respx.get(f"{POKEAPI_BASE}/pokemon/venusaur").mock(
        return_value=httpx.Response(200, json=venusaur_payload)
    )

    resp = client.get("/api/pokemon/venusaur")

    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == 3
    assert body["name"] == "venusaur"
    assert body["types"] == ["grass", "poison"]
    assert body["height_cm"] == 200   # 20 dm -> 200 cm
    assert body["weight_kg"] == 100.0  # 1000 hg -> 100 kg


@respx.mock
def test_get_pokemon_is_case_insensitive(client, venusaur_payload):
    """A rota normaliza para lowercase antes de consultar a PokeAPI."""
    route = respx.get(f"{POKEAPI_BASE}/pokemon/venusaur").mock(
        return_value=httpx.Response(200, json=venusaur_payload)
    )

    resp = client.get("/api/pokemon/VENUSAUR")

    assert resp.status_code == 200
    assert route.called


@respx.mock
def test_get_pokemon_not_found_returns_404(client):
    respx.get(f"{POKEAPI_BASE}/pokemon/inexistente").mock(
        return_value=httpx.Response(404, json={"detail": "Not found"})
    )

    resp = client.get("/api/pokemon/inexistente")

    assert resp.status_code == 404
    assert "não encontrado" in resp.json()["detail"].lower()


@respx.mock
def test_get_pokemon_upstream_failure_returns_502(client):
    """Se a PokeAPI cair ou responder erro inesperado, expomos 502 (bad gateway),
    nunca deixamos o erro cru do upstream vazar para o cliente."""
    respx.get(f"{POKEAPI_BASE}/pokemon/venusaur").mock(
        return_value=httpx.Response(500)
    )

    resp = client.get("/api/pokemon/venusaur")

    assert resp.status_code == 502


@respx.mock
def test_get_pokemon_sets_cdn_cache_header(client, venusaur_payload):
    respx.get(f"{POKEAPI_BASE}/pokemon/venusaur").mock(
        return_value=httpx.Response(200, json=venusaur_payload)
    )

    resp = client.get("/api/pokemon/venusaur")

    assert "cache-control" in resp.headers
    assert "s-maxage" in resp.headers["cache-control"]


@respx.mock
def test_list_pokemon_fans_out_and_aggregates_details(
    client, pokemon_list_page, bulbasaur_min, ivysaur_min
):
    """Verifica a integração entre a chamada de listagem e o fan-out
    assíncrono para cada detalhe (asyncio.gather em list_pokemon)."""
    respx.get(f"{POKEAPI_BASE}/pokemon", params={"limit": "2", "offset": "0"}).mock(
        return_value=httpx.Response(200, json=pokemon_list_page)
    )
    respx.get("https://pokeapi.co/api/v2/pokemon/1/").mock(
        return_value=httpx.Response(200, json=bulbasaur_min)
    )
    respx.get("https://pokeapi.co/api/v2/pokemon/2/").mock(
        return_value=httpx.Response(200, json=ivysaur_min)
    )

    resp = client.get("/api/pokemon", params={"limit": 2, "offset": 0})

    assert resp.status_code == 200
    body = resp.json()
    assert [p["name"] for p in body] == ["bulbasaur", "ivysaur"]


@respx.mock
def test_list_pokemon_upstream_failure_returns_502(client):
    respx.get(f"{POKEAPI_BASE}/pokemon", params={"limit": "2", "offset": "0"}).mock(
        return_value=httpx.Response(503)
    )

    resp = client.get("/api/pokemon", params={"limit": 2, "offset": 0})

    assert resp.status_code == 502


def test_cors_allows_get_from_any_origin(client):
    resp = client.options(
        "/api/health",
        headers={
            "Origin": "https://pokevue.vercel.app",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert resp.headers.get("access-control-allow-origin") == "*"
