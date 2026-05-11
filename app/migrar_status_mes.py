import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
db_path = os.path.join(BASE_DIR, "bonificacao.db")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("""
        ALTER TABLE frequencias_mensais
        ADD COLUMN status_mes TEXT DEFAULT 'Normal'
    """)
    print("Coluna status_mes criada com sucesso!")
except sqlite3.OperationalError as e:
    print("Aviso:", e)

conn.commit()
conn.close()