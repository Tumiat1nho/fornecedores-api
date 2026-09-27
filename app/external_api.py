import requests

# API externa pública e gratuita, sem necessidade de cadastro ou chave de acesso.
# Documentação: https://brasilapi.com.br/docs#tag/CNPJ
BRASILAPI_URL = "https://brasilapi.com.br/api/cnpj/v1/{cnpj}"


def consultar_cnpj(cnpj: str) -> dict:
    """Consulta os dados públicos de uma empresa a partir do CNPJ."""
    cnpj_limpo = "".join(filter(str.isdigit, cnpj))

    if len(cnpj_limpo) != 14:
        raise ValueError("CNPJ deve conter 14 dígitos numéricos")

    resp = requests.get(BRASILAPI_URL.format(cnpj=cnpj_limpo), timeout=10)

    if resp.status_code != 200:
        raise ValueError(f"CNPJ não encontrado ou inválido: {cnpj}")

    return resp.json()
