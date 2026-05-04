import sqlite3
from pathlib import Path
import os

DB_PATH = Path("bonificacao.db")

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
db_path = os.path.join(BASE_DIR, "bonificacao.db")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

colunas = [row[1] for row in cursor.execute("PRAGMA table_info(lancamentos_semanais)").fetchall()]

if "tipo_lancamento" not in colunas:
    cursor.execute("ALTER TABLE lancamentos_semanais ADD COLUMN tipo_lancamento TEXT DEFAULT 'semanal'")

if "data_lancamento" not in colunas:
    cursor.execute("ALTER TABLE lancamentos_semanais ADD COLUMN data_lancamento DATE")

if "usuario_lancamento" not in colunas:
    cursor.execute("ALTER TABLE lancamentos_semanais ADD COLUMN usuario_lancamento TEXT")

conn.commit()
conn.close()

print("Migração concluída com sucesso!")