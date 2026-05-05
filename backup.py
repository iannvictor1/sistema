import os
import shutil
from datetime import datetime
from datetime import timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

db_path = os.path.join(BASE_DIR, "bonificacao.db")

backup_dir = os.path.join(BASE_DIR, "backups")

os.makedirs(backup_dir, exist_ok=True)

data_hoje = datetime.now().strftime("%Y-%m-%d")

backup_path = os.path.join(backup_dir, f"backup_{data_hoje}.db")

try:
    shutil.copy2(db_path, backup_path)
    print(f"Backup criado: {backup_path}")
except Exception as e:
    print("Erro ao fazer backup:", e)
    
limite = datetime.now() - timedelta(days=7)

for arquivo in os.listdir(backup_dir):
    caminho = os.path.join(backup_dir, arquivo)
    if os.path.isfile(caminho):
        data_arquivo = datetime.fromtimestamp(os.path.getmtime(caminho))
        if data_arquivo < limite:
            os.remove(caminho)