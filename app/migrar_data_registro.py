import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
db_path = os.path.join(BASE_DIR, "bonificacao.db")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE lancamentos_semanais ADD COLUMN data_registro DATE")
    print("Coluna data_registro criada com sucesso!")
except sqlite3.OperationalError as e:
    print("Aviso:", e)

conn.commit()
conn.close()