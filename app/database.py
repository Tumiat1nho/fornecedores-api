import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "fornecedores.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS fornecedores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cnpj TEXT NOT NULL UNIQUE,
            razao_social TEXT,
            situacao_cadastral TEXT,
            cnae_principal TEXT,
            capital_social REAL,
            nivel_risco TEXT,
            data_cadastro TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()
