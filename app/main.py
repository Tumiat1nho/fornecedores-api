from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query

from app import database, external_api, risco_client, schemas

app = FastAPI(
    title="Fornecedores API",
    description=(
        "Cadastro e avaliação de risco de fornecedores/terceiros, com enriquecimento "
        "automático de dados via consulta pública de CNPJ (BrasilAPI)."
    ),
    version="1.0.0",
)


@app.on_event("startup")
def startup() -> None:
    database.init_db()


@app.post("/fornecedores", response_model=schemas.Fornecedor, status_code=201)
def criar_fornecedor(payload: schemas.FornecedorCreate):
    conn = database.get_connection()

    existente = conn.execute(
        "SELECT id FROM fornecedores WHERE cnpj = ?", (payload.cnpj,)
    ).fetchone()
    if existente:
        conn.close()
        raise HTTPException(status_code=409, detail="Fornecedor já cadastrado")

    try:
        dados_cnpj = external_api.consultar_cnpj(payload.cnpj)
    except ValueError as erro:
        conn.close()
        raise HTTPException(status_code=400, detail=str(erro))

    razao_social = dados_cnpj.get("razao_social")
    situacao_cadastral = dados_cnpj.get("descricao_situacao_cadastral")
    cnae_principal = str(dados_cnpj.get("cnae_fiscal", ""))
    capital_social = dados_cnpj.get("capital_social", 0)
    data_inicio_atividade = dados_cnpj.get("data_inicio_atividade", "")

    nivel_risco = risco_client.calcular_risco(
        {
            "situacao_cadastral": situacao_cadastral,
            "capital_social": capital_social,
            "data_inicio_atividade": data_inicio_atividade,
        }
    )

    cursor = conn.execute(
        """INSERT INTO fornecedores
           (cnpj, razao_social, situacao_cadastral, cnae_principal, capital_social, nivel_risco)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (
            payload.cnpj,
            razao_social,
            situacao_cadastral,
            cnae_principal,
            capital_social,
            nivel_risco,
        ),
    )
    conn.commit()
    novo_id = cursor.lastrowid

    row = conn.execute("SELECT * FROM fornecedores WHERE id = ?", (novo_id,)).fetchone()
    conn.close()
    return dict(row)


@app.get("/fornecedores", response_model=List[schemas.Fornecedor])
def listar_fornecedores(
    situacao_cadastral: Optional[str] = None,
    nivel_risco: Optional[str] = None,
    order_by: str = Query("id", enum=["id", "razao_social", "capital_social", "data_cadastro"]),
    order_dir: str = Query("asc", enum=["asc", "desc"]),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    conn = database.get_connection()

    query = "SELECT * FROM fornecedores WHERE 1=1"
    params: list = []

    if situacao_cadastral:
        query += " AND situacao_cadastral = ?"
        params.append(situacao_cadastral)

    if nivel_risco:
        query += " AND nivel_risco = ?"
        params.append(nivel_risco)

    query += f" ORDER BY {order_by} {order_dir.upper()} LIMIT ? OFFSET ?"
    params.extend([limit, skip])

    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/fornecedores/{fornecedor_id}", response_model=schemas.Fornecedor)
def obter_fornecedor(fornecedor_id: int):
    conn = database.get_connection()
    row = conn.execute("SELECT * FROM fornecedores WHERE id = ?", (fornecedor_id,)).fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado")
    return dict(row)


@app.put("/fornecedores/{fornecedor_id}", response_model=schemas.Fornecedor)
def atualizar_fornecedor(fornecedor_id: int, payload: schemas.FornecedorUpdate):
    conn = database.get_connection()

    row = conn.execute("SELECT * FROM fornecedores WHERE id = ?", (fornecedor_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado")

    campos = payload.dict(exclude_unset=True)
    if campos:
        set_clause = ", ".join(f"{campo} = ?" for campo in campos)
        valores = list(campos.values()) + [fornecedor_id]
        conn.execute(f"UPDATE fornecedores SET {set_clause} WHERE id = ?", valores)
        conn.commit()

    row = conn.execute("SELECT * FROM fornecedores WHERE id = ?", (fornecedor_id,)).fetchone()
    conn.close()
    return dict(row)


@app.delete("/fornecedores/{fornecedor_id}", status_code=204)
def remover_fornecedor(fornecedor_id: int):
    conn = database.get_connection()

    row = conn.execute("SELECT id FROM fornecedores WHERE id = ?", (fornecedor_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado")

    conn.execute("DELETE FROM fornecedores WHERE id = ?", (fornecedor_id,))
    conn.commit()
    conn.close()
    return None
