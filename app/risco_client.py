import os
import requests

# Em Docker Compose, "risco_api" é o nome do serviço/host na rede interna.
# Em execução local (fora de container), use http://localhost:8001.
RISCO_API_URL = os.getenv("RISCO_API_URL", "http://localhost:8001")


def calcular_risco(dados: dict) -> str:
    """Envia os dados do fornecedor para a API secundária e retorna o nível de risco."""
    try:
        resp = requests.post(f"{RISCO_API_URL}/risco/calcular", json=dados, timeout=5)
        resp.raise_for_status()
        return resp.json().get("nivel_risco", "desconhecido")
    except requests.RequestException:
        # Se a API de risco estiver fora do ar, o cadastro não deve falhar por completo.
        return "indisponivel"
