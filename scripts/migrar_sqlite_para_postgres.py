import argparse
import os
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from app.database import Base
from app.models import Funcionario, FrequenciaMensal, LancamentoSemanal


DEFAULT_SQLITE = ROOT_DIR / "bonificacao.db"


TABLES = [
    {
        "name": "funcionarios",
        "model": Funcionario,
        "columns": ["id", "nome", "cargo", "ativo", "tipo_entrega", "turno"],
    },
    {
        "name": "lancamentos_semanais",
        "model": LancamentoSemanal,
        "columns": [
            "id",
            "funcionario_id",
            "semana",
            "tipo_lancamento",
            "data_lancamento",
            "data_registro",
            "usuario_lancamento",
            "pedidos_separados",
            "pedidos_carregados",
            "toneladas",
            "entregas",
            "retornos",
            "nota",
            "penalidade",
            "motivo_penalidade",
            "bonus_calculado",
        ],
    },
    {
        "name": "frequencias_mensais",
        "model": FrequenciaMensal,
        "columns": ["id", "funcionario_id", "mes", "ausencias", "data_falta", "tipo_falta", "status_mes"],
    },
]


def normalize_database_url(url: str) -> str:
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


def sqlite_columns(conn: sqlite3.Connection, table: str) -> set[str]:
    return {row["name"] for row in conn.execute(f"PRAGMA table_info({table})")}


def read_sqlite_rows(conn: sqlite3.Connection, table: str, columns: list[str]) -> list[dict]:
    available = sqlite_columns(conn, table)
    selected = [column for column in columns if column in available]

    if not selected:
        return []

    rows = conn.execute(f"SELECT {', '.join(selected)} FROM {table} ORDER BY id").fetchall()
    result = []

    for row in rows:
        item = {column: row[column] if column in selected else None for column in columns}
        result.append(item)

    return result


def backup_sqlite(sqlite_path: Path) -> Path:
    backup_dir = ROOT_DIR / "backups"
    backup_dir.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"{sqlite_path.stem}_antes_migracao_{stamp}{sqlite_path.suffix}"
    shutil.copy2(sqlite_path, backup_path)
    return backup_path


def reset_postgres(session, engine) -> None:
    for table in reversed(TABLES):
        session.execute(text(f"DELETE FROM {table['name']}"))

    session.commit()

    if engine.dialect.name == "postgresql":
        sequence_tables = ", ".join(table["name"] for table in TABLES)
        session.execute(text(f"TRUNCATE TABLE {sequence_tables} RESTART IDENTITY CASCADE"))
        session.commit()


def sync_sequences(session, engine) -> None:
    if engine.dialect.name != "postgresql":
        return

    for table in TABLES:
        session.execute(
            text(
                f"""
                SELECT setval(
                    pg_get_serial_sequence('{table["name"]}', 'id'),
                    COALESCE((SELECT MAX(id) FROM {table["name"]}), 1),
                    (SELECT COUNT(*) FROM {table["name"]}) > 0
                )
                """
            )
        )

    session.commit()


def migrate(sqlite_path: Path, database_url: str, replace: bool, no_backup: bool) -> None:
    if not sqlite_path.exists():
        raise FileNotFoundError(f"SQLite nao encontrado: {sqlite_path}")

    if not database_url:
        raise RuntimeError("Informe DATABASE_URL apontando para PostgreSQL.")

    database_url = normalize_database_url(database_url)

    if "sqlite" in database_url:
        raise RuntimeError("DATABASE_URL esta apontando para SQLite. Aponte para PostgreSQL antes de migrar.")

    backup_path = None if no_backup else backup_sqlite(sqlite_path)

    engine = create_engine(database_url)
    if engine.dialect.name != "postgresql":
        raise RuntimeError(f"Este script deve gravar em PostgreSQL, mas encontrou: {engine.dialect.name}")

    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)

    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_conn.row_factory = sqlite3.Row

    session = Session()

    try:
        if replace:
            reset_postgres(session, engine)

        totals = {}

        for table in TABLES:
            rows = read_sqlite_rows(sqlite_conn, table["name"], table["columns"])
            totals[table["name"]] = len(rows)

            for row in rows:
                session.merge(table["model"](**row))

            session.commit()

        sync_sequences(session, engine)

        print("Migracao concluida.")
        if backup_path:
            print(f"Backup SQLite: {backup_path}")
        for table_name, count in totals.items():
            print(f"{table_name}: {count} registro(s)")

    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
        sqlite_conn.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Migra dados do SQLite local para PostgreSQL.")
    parser.add_argument("--sqlite", default=str(DEFAULT_SQLITE), help="Caminho do banco SQLite de origem.")
    parser.add_argument("--database-url", default=os.getenv("DATABASE_URL", ""), help="URL PostgreSQL de destino.")
    parser.add_argument("--replace", action="store_true", help="Apaga os dados atuais do PostgreSQL antes de importar.")
    parser.add_argument("--no-backup", action="store_true", help="Nao cria backup do SQLite antes da migracao.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    migrate(Path(args.sqlite), args.database_url, args.replace, args.no_backup)
