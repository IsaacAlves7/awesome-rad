"""
Testes UNITÁRIOS — modelos Pydantic.
Garantem que o "contrato de dados" da API é validado corretamente,
independente de qualquer chamada HTTP.
"""
import pytest
from pydantic import ValidationError

from main import PokemonDetail, PokemonSummary


def test_pokemon_summary_accepts_valid_data():
    p = PokemonSummary(id=3, name="venusaur", sprite="https://x/3.png")
    assert p.id == 3
    assert p.name == "venusaur"


def test_pokemon_summary_allows_missing_sprite():
    p = PokemonSummary(id=3, name="venusaur", sprite=None)
    assert p.sprite is None


def test_pokemon_summary_rejects_missing_required_field():
    with pytest.raises(ValidationError):
        PokemonSummary(name="venusaur", sprite=None)  # falta `id`


def test_pokemon_detail_conversion_from_pokeapi_units():
    """PokeAPI retorna altura em decímetros e peso em hectogramas — a API
    deve expor em cm e kg (ver main.get_pokemon: height*10, weight/10)."""
    detail = PokemonDetail(
        id=3,
        name="venusaur",
        sprite="https://x/3.png",
        types=["grass", "poison"],
        height_cm=200,
        weight_kg=100.0,
        generated_at=0.0,
    )
    assert detail.height_cm == 200
    assert detail.weight_kg == 100.0
    assert detail.types == ["grass", "poison"]


def test_pokemon_detail_rejects_wrong_type_for_types_field():
    with pytest.raises(ValidationError):
        PokemonDetail(
            id=3,
            name="venusaur",
            sprite=None,
            types="grass",  # deveria ser list[str], não str
            height_cm=200,
            weight_kg=100.0,
            generated_at=0.0,
        )
