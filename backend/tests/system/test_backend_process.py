"""
Teste de SISTEMA (backend)
============================
Diferença para os testes de integração: aqui não usamos `TestClient`
(que chama a app in-process). Subimos o `uvicorn` de verdade, como um
processo de sistema operacional, e batemos nele via HTTP puro — validando
o sistema como ele roda em produção (bind de porta, servidor ASGI real,
serialização JSON na borda). A PokeAPI upstream é substituída por um
servidor HTTP fake local, para o teste ser hermético (sem internet).

Requer que a porta 8000/8010 estejam livres. Roda separado da suíte
principal por ser mais lento/pesado:

    pytest tests/system -v
"""
import json
import socket
import subprocess
import sys
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from threading import Thread

import pytest
import requests

BACKEND_DIR = Path(__file__).resolve().parents[2]


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class FakePokeApiHandler(BaseHTTPRequestHandler):
    """Servidor HTTP mínimo que finge ser a PokeAPI, para o teste de
    sistema não depender de internet nem do uptime da API real."""

    def do_GET(self):  # noqa: N802 (nome exigido pela stdlib)
        if self.path.startswith("/api/v2/pokemon/venusaur"):
            payload = {
                "id": 3, "name": "venusaur", "height": 20, "weight": 1000,
                "types": [{"type": {"name": "grass"}}, {"type": {"name": "poison"}}],
                "sprites": {"front_default": "https://x/3.png",
                            "other": {"official-artwork": {"front_default": "https://x/3-art.png"}}},
            }
            self._send_json(200, payload)
        else:
            self._send_json(404, {"detail": "not found"})

    def _send_json(self, status: int, payload: dict):
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):  # silencia logs do http.server no output do pytest
        pass


@pytest.fixture(scope="module")
def fake_pokeapi():
    port = _free_port()
    server = HTTPServer(("127.0.0.1", port), FakePokeApiHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{port}/api/v2"
    server.shutdown()


@pytest.fixture(scope="module")
def running_backend(fake_pokeapi):
    """Sobe `uvicorn main:app` como subprocesso real (bind de porta de
    verdade, servidor ASGI de verdade), apontando POKEAPI_BASE para o
    fake server HTTP local — assim o teste de sistema é hermético
    (não depende de internet nem do uptime da PokeAPI real)."""
    port = _free_port()
    env = {
        "PYTHONPATH": str(BACKEND_DIR),
        "PATH": "/usr/bin:/bin:/usr/local/bin",
        "POKEAPI_BASE": fake_pokeapi,
    }
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--port", str(port), "--host", "127.0.0.1"],
        cwd=str(BACKEND_DIR),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    base_url = f"http://127.0.0.1:{port}"
    for _ in range(50):
        try:
            r = requests.get(f"{base_url}/api/health", timeout=0.5)
            if r.status_code == 200:
                break
        except requests.exceptions.ConnectionError:
            time.sleep(0.1)
    else:
        proc.terminate()
        raise RuntimeError("Backend não subiu a tempo para o teste de sistema")

    yield base_url

    proc.terminate()
    proc.wait(timeout=5)


def test_system_health_check_over_real_http(running_backend):
    r = requests.get(f"{running_backend}/api/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_system_process_exposes_openapi_docs(running_backend):
    """Valida que o processo real do FastAPI está servindo o app inteiro
    (schema OpenAPI), não só uma rota isolada."""
    r = requests.get(f"{running_backend}/openapi.json")
    assert r.status_code == 200
    schema = r.json()
    assert "/api/pokemon/{identifier}" in schema["paths"]


def test_system_full_request_path_hits_fake_upstream_end_to_end(running_backend):
    """Percurso completo do sistema real: cliente HTTP -> processo uvicorn
    -> handler FastAPI -> cliente httpx -> servidor fake da PokeAPI -> volta
    serializado como PokemonDetail. Nenhuma peça é mockada in-process aqui,
    diferente dos testes de integração (que usam TestClient + respx)."""
    r = requests.get(f"{running_backend}/api/pokemon/venusaur")

    assert r.status_code == 200
    body = r.json()
    assert body["name"] == "venusaur"
    assert body["types"] == ["grass", "poison"]
    assert body["height_cm"] == 200
    assert "cache-control" in {k.lower(): v for k, v in r.headers.items()}


def test_system_404_propagates_through_real_process(running_backend):
    r = requests.get(f"{running_backend}/api/pokemon/nao-existe")
    assert r.status_code == 404
