"""
Testes UNITÁRIOS
=================
Escopo: uma única função, isolada, sem rede e sem subir a aplicação inteira.
Aqui testamos `_set_cdn_cache`, que decide o header de cache que a CDN vai
respeitar — a peça central da estratégia de ISR/SSG deste projeto.
"""
from fastapi import Response

from main import CACHE_S_MAXAGE, CACHE_SWR, _set_cdn_cache


def test_default_cache_header_uses_module_constants():
    response = Response()
    _set_cdn_cache(response)

    header = response.headers["cache-control"]
    assert "public" in header
    assert f"s-maxage={CACHE_S_MAXAGE}" in header
    assert f"stale-while-revalidate={CACHE_SWR}" in header


def test_custom_ttl_overrides_defaults():
    response = Response()
    _set_cdn_cache(response, s_maxage=120, swr=30)

    header = response.headers["cache-control"]
    assert "s-maxage=120" in header
    assert "stale-while-revalidate=30" in header
    # garante que não vazou o valor default junto
    assert f"s-maxage={CACHE_S_MAXAGE}" not in header


def test_header_is_marked_public_for_cdn_sharing():
    """Sem `public`, algumas CDNs tratam a resposta como privada e não cacheiam."""
    response = Response()
    _set_cdn_cache(response)

    assert response.headers["cache-control"].startswith("public,")
