from pydantic import BaseModel
from typing import Optional


class FornecedorCreate(BaseModel):
    cnpj: str


class FornecedorUpdate(BaseModel):
    razao_social: Optional[str] = None
    situacao_cadastral: Optional[str] = None
    capital_social: Optional[float] = None


class Fornecedor(BaseModel):
    id: int
    cnpj: str
    razao_social: Optional[str] = None
    situacao_cadastral: Optional[str] = None
    cnae_principal: Optional[str] = None
    capital_social: Optional[float] = None
    nivel_risco: Optional[str] = None
    data_cadastro: str
