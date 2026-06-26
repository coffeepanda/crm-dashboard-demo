from __future__ import annotations

import sqlite3
from pathlib import Path

from crm_dashboard_demo.data.seed import seed_database

DEFAULT_DB_PATH = Path(__file__).resolve().parents[1] / "data" / "crm.sqlite"


def ensure_database(db_path: str | Path | None = None) -> Path:
    path = Path(db_path) if db_path else DEFAULT_DB_PATH
    if not path.exists():
        seed_database(path)
    return path


def connect_readonly(db_path: str | Path | None = None) -> sqlite3.Connection:
    path = ensure_database(db_path)
    uri = f"file:{path.as_posix()}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    return conn
