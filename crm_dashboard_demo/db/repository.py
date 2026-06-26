from __future__ import annotations

from pathlib import Path
from typing import Any

from .connection import connect_readonly


def run_select_query(sql: str, *, db_path: str | Path | None = None) -> dict[str, Any]:
    with connect_readonly(db_path) as conn:
        cursor = conn.execute(sql)
        rows = [dict(row) for row in cursor.fetchall()]
        columns = [description[0] for description in cursor.description or []]
    return {"columns": columns, "rows": rows, "row_count": len(rows)}
