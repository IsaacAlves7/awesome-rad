import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# permite `import main` a partir de backend/tests/
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from main import app  # noqa: E402


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def venusaur_payload():
    """Payload reduzido, mas estruturalmente fiel ao retorno real da PokeAPI."""
    return {
        "id": 3,
        "name": "venusaur",
        "height": 20,   # decímetros -> 200 cm
        "weight": 1000, # hectogramas -> 100 kg
        "types": [
            {"slot": 1, "type": {"name": "grass", "url": "https://pokeapi.co/api/v2/type/12/"}},
            {"slot": 2, "type": {"name": "poison", "url": "https://pokeapi.co/api/v2/type/4/"}},
        ],
        "sprites": {
            "front_default": "https://raw.githubusercontent.com/pokeapi/sprites/master/sprites/pokemon/3.png",
            "other": {
                "official-artwork": {
                    "front_default": "https://raw.githubusercontent.com/pokeapi/sprites/master/sprites/pokemon/other/official-artwork/3.png"
                }
            },
        },
    }


@pytest.fixture
def pokemon_list_page():
    return {
        "count": 1302,
        "next": "https://pokeapi.co/api/v2/pokemon?offset=2&limit=2",
        "previous": None,
        "results": [
            {"name": "bulbasaur", "url": "https://pokeapi.co/api/v2/pokemon/1/"},
            {"name": "ivysaur", "url": "https://pokeapi.co/api/v2/pokemon/2/"},
        ],
    }


@pytest.fixture
def bulbasaur_min():
    return {
        "id": 1,
        "name": "bulbasaur",
        "sprites": {"front_default": "https://.../1.png", "other": {"official-artwork": {"front_default": None}}},
        "height": 7,
        "weight": 69,
        "types": [{"slot": 1, "type": {"name": "grass", "url": "x"}}],
    }


@pytest.fixture
def ivysaur_min():
    return {
        "id": 2,
        "name": "ivysaur",
        "sprites": {"front_default": "https://.../2.png", "other": {"official-artwork": {"front_default": None}}},
        "height": 10,
        "weight": 130,
        "types": [{"slot": 1, "type": {"name": "grass", "url": "x"}}],
    }
