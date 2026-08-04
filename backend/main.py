"""
PokeNext-Vue Backend
=====================
API FastAPI que atua como camada intermediária (BFF) entre o frontend Nuxt
e a PokeAPI pública, com foco em cacheabilidade por CDN.

Estratégia de cache:
- Cada resposta carrega `Cache-Control: public, s-maxage=X, stale-while-revalidate=Y`.
- `s-maxage` é respeitado por CDNs (Vercel Edge, Cloudflare, Fastly, Netlify Edge),
  mas ignorado por navegadores comuns -> o browser sempre revalida, a CDN não.
- `stale-while-revalidate` permite servir uma resposta "velha" instantaneamente
  enquanto a CDN busca uma nova versão em background (ISR na prática).
- Dados de Pokémon raramente mudam, então usamos TTL longo (24h) com SWR de 1h.
"""

import time
from typing import Optional

import httpx
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

POKEAPI_BASE = "https://pokeapi.co/api/v2"

# TTLs de cache (em segundos) — ajustáveis conforme a política de ISR desejada
CACHE_S_MAXAGE = 60 * 60 * 24       # 24h "fresco" na borda da CDN
CACHE_SWR = 60 * 60                  # 1h servindo stale enquanto revalida

app = FastAPI(
    title="PokeNext-Vue API",
    description="BFF cacheável para consumo da PokeAPI, otimizado para SSG/ISR via CDN.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # em produção: restringir ao domínio do frontend
    allow_methods=["GET"],
    allow_headers=["*"],
)


class PokemonSummary(BaseModel):
    id: int
    name: str
    sprite: Optional[str]


class PokemonDetail(BaseModel):
    id: int
    name: str
    sprite: Optional[str]
    types: list[str]
    height_cm: int
    weight_kg: float
    generated_at: float  # timestamp de quando essa resposta foi montada (debug de cache)


def _set_cdn_cache(response: Response, s_maxage: int = CACHE_S_MAXAGE, swr: int = CACHE_SWR) -> None:
    response.headers["Cache-Control"] = (
        f"public, s-maxage={s_maxage}, stale-while-revalidate={swr}"
    )
    # CDN Vary opcional: aqui não variamos por header, então omitido de propósito


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/pokemon", response_model=list[PokemonSummary])
async def list_pokemon(response: Response, limit: int = 24, offset: int = 0):
    """Lista paginada, usada para gerar a home (SSG) e os links de detalhe."""
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(f"{POKEAPI_BASE}/pokemon", params={"limit": limit, "offset": offset})
        if r.status_code != 200:
            raise HTTPException(status_code=502, detail="Falha ao consultar PokeAPI")
        data = r.json()

        results = []
        # busca em paralelo os sprites de cada item da página
        async def fetch_one(entry):
            detail = await client.get(entry["url"])
            d = detail.json()
            return PokemonSummary(
                id=d["id"],
                name=d["name"],
                sprite=d["sprites"]["front_default"],
            )

        import asyncio
        results = await asyncio.gather(*(fetch_one(e) for e in data["results"]))

    _set_cdn_cache(response)
    return results


@app.get("/api/pokemon/{identifier}", response_model=PokemonDetail)
async def get_pokemon(identifier: str, response: Response):
    """Detalhe de um Pokémon por nome ou id, formatado como no mock (numero/tipo/altura/peso)."""
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(f"{POKEAPI_BASE}/pokemon/{identifier.lower()}")
        if r.status_code == 404:
            raise HTTPException(status_code=404, detail="Pokémon não encontrado")
        if r.status_code != 200:
            raise HTTPException(status_code=502, detail="Falha ao consultar PokeAPI")
        d = r.json()

    detail = PokemonDetail(
        id=d["id"],
        name=d["name"],
        sprite=d["sprites"]["other"]["official-artwork"]["front_default"] or d["sprites"]["front_default"],
        types=[t["type"]["name"] for t in d["types"]],
        height_cm=d["height"] * 10,   # PokeAPI retorna decímetros
        weight_kg=d["weight"] / 10,   # PokeAPI retorna hectogramas
        generated_at=time.time(),
    )

    _set_cdn_cache(response)
    return detail
